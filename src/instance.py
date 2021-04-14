import os
import imageio
import cv2
import time

__all__ = ["Instance"]

class Instance(object):

    def __init__(self, path):
        
        assert os.path.exists(path)
        img = imageio.imread(path)
        img = cv2.cvtColor(img, cv2.COLOR_RGB2BGR)

        self.img = img
        self.__dict__['meta'] = {
            'raw': self.img,
            'path': path,
            'logs':[],
            'img_logs':[],
            'result':None,
            'medium':dict(),
            'time':dict()
        }

    def __getattr__(self, name):

        if name == 'img':
            return self.img.copy()
        elif name in self.meta:
            return self.meta[name]

    def __setattr__(self, name, value):

        if name == 'img':
            self.__dict__['img'] = value
        elif name =='meta':
            pass
        else:
            self.__dict__['meta'][name] = value

    def show(self):

        cv2.imshow(self.path, self.img)
        cv2.waitKey()


    def inInfo(self, name):
        return name in self.__dict__['meta']