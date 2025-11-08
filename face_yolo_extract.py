#!/usr/bin/env python3
import os
import threading
from yolo_detecting import *
from face_recognition import *
from multiprocessing import Process,Queue
from PIL import Image
import numpy as np
path="faces/"
imgs=os.listdir(path)
pathes=Queue()
model=YOLO("models/yolo_distillation.pt",task="detect")
for img in imgs:
    pathes.put(img)
count_pipes=4
ob_names=[]
def crop_face(model,path,queue):
    while not queue.empty():
        img=queue.get()
        if img==None:
            break
        image=Image.open(f"{path}/{img}")
        coordinates=get_coordinates(model,image)
        if coordinates.shape[0]==1:
            coordinates=coordinates[0]
            #print(coordinates[0]/size[0],coordinates[1]/size[1],coordinates[2]/size[0],coordinates[3]/size[1])
            w,h=image.size
            if not img in ob_names:
                index_class=len(ob_names)+1
                ob_names.append(os.path.splitext(img)[0])
            x1,y1,x2,y2=coordinates[0]/w,coordinates[1]/h,coordinates[2]/w,coordinates[3]/h
            with open(f"{path}/yolo/labels/{os.path.splitext(img)[0]+'.txt'}",'w') as f:
                f.write(f'{index_class} {x1} {x2} {y1} {y2}')
            image.save(f"{path}/yolo/images/{img}")
            with open(f"{path}/yolo/for_yaml.txt",'w') as f:
                for key,value in enumerate(ob_names):
                    f.write(f'\t{key+1} : \'{value}\'\n')
if __name__=="__main__":
    for i in range(count_pipes):
        Process(target=crop_face,args=(model,path,pathes)).start()
    
    