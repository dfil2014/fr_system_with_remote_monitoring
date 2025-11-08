class face_detect:
    def __init__(self,models,model_weights,detect_system):
        super(SiameseNetwork, self).__init__()
        self.models=models
        self.weights=model_weights
        self.detect_system=detect_system
        
    def convert_xywh(coordinates):
        assert len(coordinates), f"Координаты должны содержать 4 значения, а содержат {len(coordinates)}"
        w=coordinates[2]-coordinates[0]
        h=coordinates[3]-coordinates[1]
        x=coordinates[0]+w//2
        y=coordinates[1]+h//2
        return [x,y,w,h]
    
    def convert_xyxy(coordinates):
        assert len(coordinates), f"Координаты должны содержать 4 значения, а содержат {len(coordinates)}"
        x1=coordinates[0]-coordinates[2]//2
        x2=coordinates[0]+coordinates[2]//2
        y1=coordinates[1]-coordinates[3]//2
        y2=coordinates[1]+coordinates[3]//2
        return [x1,y1,x2,y2]
    
    def review(image,list_pos,list_famous,thick=5):
        image=np.array(image)
        for pos,famous in zip(list_pos,list_famous):
            #pos=convert_xyxy(pos)
            for i in range(thick):
                rr,cc=skimage.draw.rectangle_perimeter((pos[1]-i,pos[0]-i),extent=(pos[3]-pos[1]+i*2,pos[2]-pos[0]+i*2),shape=image.shape)
                if famous:
                    image[rr,cc]=[0,255,0]
                else:
                    image[rr,cc]=[255,0,0]
        return image
        
    def get_coordinates(model,frame):
        results=model(frame)
        return results[0].boxes.xyxy.cpu().numpy().astype(np.int32)
        
    def predict(model,frame,result_images):
        path="faces/features"
        bboxes=get_coordinates(model,frame)
        famous=[]
        for coordinate in bboxes:
            face=Image.fromarray(frame.astype('uint8'),'RGB')
            face=face.crop((coordinate[0],coordinate[1],coordinate[2],coordinate[3]))
            found_face=found_faces(face,path)
            if found_face is None:
                famous.append(False)
                result_images.put((face,False,""))
            else:
                famous.append(True)
                result_images.put((face,True,found_face))
        return review(frame,list(bboxes),famous,thick=10)

    