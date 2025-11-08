import torch
import struct
import skimage.transform
from torchvision import transforms,models
from PIL import Image
import os
import numpy as np
import time
import random
import torch.nn.functional as F
from torchvision.transforms import v2
transform=transforms.Compose([transforms.Resize((224,224),interpolation=transforms.InterpolationMode.NEAREST),v2.RGB(),transforms.ToTensor()])
class SiameseNetwork(torch.nn.Module):

    def __init__(self,basemodel="resnet18"):
        super(SiameseNetwork, self).__init__()
        self.optimizer=None
        self.loss=None

        if basemodel not in models.__dict__:
            raise Exception(f"Model {basemodel} not found in torchvision.models")

        self.basenetwork = models.__dict__[basemodel](weights=True, progress=True)

        out_features = list(self.basenetwork.modules())[-1].out_features

        self.cls_layer = torch.nn.Sequential(
            torch.nn.Dropout(p=0.5),
            torch.nn.Linear(out_features, 512),
            torch.nn.BatchNorm1d(512),
            torch.nn.ReLU(),

            torch.nn.Dropout(p=0.5),
            torch.nn.Linear(512, 64),
            torch.nn.BatchNorm1d(64),
            torch.nn.Sigmoid(),
            torch.nn.Dropout(p=0.5),

            torch.nn.Linear(64, 1),
            torch.nn.Sigmoid(),
        )

    def forward(self, input1, input2):
        output1 = self.basenetwork(input1)
        output2 = self.basenetwork(input2)
        multiply_output=output1*output2
        output=self.cls_layer(multiply_output)
        return output

face_detect=SiameseNetwork()

device = torch.device('cuda:0' if torch.cuda.is_available() else 'cpu')
face_detect = face_detect.to(device)
face_detect.load_state_dict(torch.load('models/model_facedetect_with_resnet.pt',weights_only=True, map_location=torch.device('cpu')))
face_detect.eval()


def features_extract(image):
    features=face_detect.basenetwork(image)
    features=features.tolist()[0]
    bytes_data = b''.join(struct.pack('f', f) for f in features)
    return bytes_data
def save_binary(binary,file_name):
    with open(file_name,'wb') as file:
        file.write(binary)
def open_binary(file_name):
    with open(file_name,'rb') as file:
        bytes_data=file.read()
        float_list = [struct.unpack('f', bytes_data[i:i+4])[0] for i in range(0, len(bytes_data), 4)]
    return torch.FloatTensor(float_list)
def calculate_euclidian(features1,features2):
    multiply_output=features1*features2
    output=face_detect.cls_layer(multiply_output)
    return output
def found_faces(face,path_features,min=0.5):
    features=os.listdir(path_features)
    face=torch.unsqueeze(transform(face),0)
    face_feature=face_detect.basenetwork(face)
    for file_path in features:
        comparison=open_binary(f"{path_features}/{file_path}")
        if calculate_euclidian(face_feature,comparison)>=min:
            return file_path
    return None
'''
path1="faces/cropped"
path2="faces/features"
imgs=os.listdir(path1)
for file in imgs:
    img=Image.open(f"{path1}/{file}").convert("L")
    img=torch.unsqueeze(transform(img),0)
    feature=features_extract(img)
    rename=f"{file.split(".")[0]}.dat"
    save_binary(feature,f"{path2}/{rename}")
'''
        
  