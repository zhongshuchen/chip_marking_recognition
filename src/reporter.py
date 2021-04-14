import os
import imageio
import pandas as pd
import numpy as np
import base64
import cv2

class Reporter(object):

    def __init__(self):

        self.total = 0
        self.positive = 0
        self.times = list()
        self.negativeHooks = dict()
        self.instances = list()

    def record(self,instance):

        if instance.result is None:
            return None

        self.instances.append(instance)
        self.total += 1
        self.times.append(instance.time)

        if instance.result[0] == True:
            self.positive += 1
        else:
            hook = instance.result[1]
            if hook not in self.negativeHooks:
                self.negativeHooks[hook] = 0
            self.negativeHooks[hook] += 1

    def reportLatest(self):
        
        latest_ins = self.instances[-1]
        
        message = '%d files detected | current file: %s | result: %s'%(self.total, latest_ins.path, latest_ins.result[0])
        if latest_ins.result[2] is None:
            message += ' | recorded by %s'%latest_ins.result[1]
        else:
            message += ' | '+latest_ins.result[2]
        print(message)

    def reportTime(self):
        
        timeframe = pd.DataFrame(self.times)
        timeseries = timeframe.sum()
        print('%-30s\t%s'%('Component Class','Time Usage(s)'))
        print('-----------------------------------')
        for i,v in timeseries.iteritems():
            print('%-30s\t%f'%(i,v))
        print('%-30s\t%f'%('Total',timeseries.sum()))
        print('-----------------------------------')
        print('%-30s\t%f fps'%('Speed',self.total / timeseries.sum() ))

    def reportInseption(self):
        
        print('%d files detected'%(self.total))
        print('-----------------------------------')
        print('Positive Samples:')
        print('%-30s\t%d'%('Total',self.positive))
        print('-----------------------------------')
        print('Negative Samples:')
        for i,v in self.negativeHooks.items():
            print('%-30s\t%d'%(i,v))
        print('%-30s\t%d'%('Total',self.total - self.positive))
        print('-----------------------------------')
        print('%-30s\t%f'%('Accurate',self.positive / self.total))
    
    def _cv2base64(self,img):
        assert len(img.shape) == 2 or len(img.shape)== 3
        if str(img.dtype).find('float')>=0:
            img = np.clip(img*255,0,255)
            img = img.astype(np.uint8)
            
        if len(img.shape) == 2:
            img = cv2.cvtColor(img, cv2.COLOR_GRAY2BGR)
        base64_str = cv2.imencode('.jpg',img)[1].tostring()
        base64_str = b'data:image/jpeg;base64,'+base64.b64encode(base64_str)
        return base64_str.decode()
        
    def exportHTML(self, path, only_negative = False):
        
        real_dir = os.path.split(os.path.realpath(__file__))[0]
        base_path = os.path.splitext(path)[0]
        
        while os.path.exists(base_path + '.html'):
            base_path += '_1'
#             raise Exception('A directory or a file named '+base_path+'_files is already existed, please use another file name for the report.')
#             return None
        base_name = os.path.basename(base_path)

#         os.makedirs(base_path + '_files')

        samples_html = '<h2>%d files detected</h2>'%self.total
        for instance in self.instances:
            
            if only_negative and instance.result[0]:
                continue

            filename,ext = os.path.splitext(instance.path)
            filename = os.path.basename(filename)
            
            raw_img = self._cv2base64(instance.raw)
            final_img = self._cv2base64(instance.img)

            logs = ''
            img_logs = ''
            for log in instance.logs:
                logs+='<p>%s</p>'%log
            for img in instance.img_logs:
                img_logs += '<img src="%s">&nbsp;&nbsp;'%self._cv2base64(img)
            sample_class = 'positive' if instance.result[0] else 'negative'
            samples_html += '<div class="sample %s"><div class="img raw-img"><img src="%s" width="128" height="128"></div><div class="img final-img"><img src="%s" width="128" height="128"></div><div class="records"><span class="path">%s</span><br><span class="judge">Result: %s</span><br><span class="log"><strong>Logs:</strong> %s</span><br>%s</div></div>'%(sample_class,raw_img, final_img, instance.path, instance.result[0], logs, img_logs)

        time_html = '<table><tr><th>Component Class</th><th>Time Usage(s)</th></tr>'
        timeframe = pd.DataFrame(self.times)
        timeseries = timeframe.sum()
        for i,v in timeseries.iteritems():
            time_html += '<tr><td>%s</td><td>%f</td></tr>'%(i,v)
        time_html += '<tr><td>%s</td><td>%f</td></tr>'%('Total',timeseries.sum())
        time_html += '</table>'
        
        result_html = '<table><tr><th>Component Class</th><th>Time Usage(s)</th></tr>'
        result_html+= '<tr><td>%s</td><td>%d</td></tr>'%('Total Positive',self.positive)
        for i,v in self.negativeHooks.items():
            result_html+= '<tr><td>%s</td><td>%d</td></tr>'%(i,v)
        result_html+= '<tr><td>%s</td><td>%d</td></tr>'%('Total Negative',self.total - self.positive)
        result_html+= '<tr><td>%s</td><td>%.4f</td></tr>'%('Accurate', self.positive / self.total * 100)
        result_html += '</table>'

        with open(real_dir+'/html_report_template.html','r') as f:
            template = f.read() 
            template = template.replace('<!--samples-->', samples_html)
            template = template.replace('<!--time-->', time_html)
            template = template.replace('<!--result-->', result_html)

            out = open(base_path+'.html','w+')
            out.write(template)
            out.close()

            print('HTML report has been saved at '+ base_path +'.html')