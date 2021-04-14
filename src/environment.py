import torch

__all__ = ['Environment']

class Environment(object):

    def __init__(self, gpu, test = False):

        self.test = test
        self.use_parallel = False
        
        if gpu == -1:
            self.device = torch.device('cpu')
        
        elif torch.cuda.is_available() == False:
            raise Exception('CUDA is not available on this device')
       
        elif isinstance(gpu, int):
            self.device = torch.device('cuda:'+str(gpu))
        
        elif isinstance(gpu, list):
            gpu_count = torch.cuda.device_count()
            
            for i in gpu:
                if not isinstance(i,int):
                    raise Exception('All gpu numbers supposed to be integers')
                    break
                elif i<0 or i>=gpu_count:
                    raise Exception('GPU number mismatches the device envrionment')
                    break
           
            if len(gpu) == 1:
                self.device = torch.device('cuda:'+str(gpu[0]))
            
            else:
                gpu = [str(i) for i in gpu]
                os.environ["CUDA_VISIBLE_DEVICES"] = ','.join(gpu)
                self.device = torch.device('cuda:0')
                self.use_parallel = True
        
        else:
            raise Exception('Unsupported format for the parameter "gpu"')
