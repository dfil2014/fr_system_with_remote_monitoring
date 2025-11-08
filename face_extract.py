#!/usr/bin/env python3
import os
import threading
from yolo_detecting import *
from face_recognition import *
from multiprocessing import Process,Queue
from PIL import Image
path="faces/"
imgs=os.listdir(path)
pathes=Queue()
model=YOLO("models/yolo_distillation.pt",task="detect")
for img in imgs:
    pathes.put(img)
count_pipes=4
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
            image=image.crop((coordinates[0],coordinates[1],coordinates[2],coordinates[3]))
            image.save(f"{path}/cropped_{img}")
            return image
if __name__=="__main__":
    for i in range(count_pipes):
        Process(target=crop_face,args=(model,path,pathes)).start()
    
    