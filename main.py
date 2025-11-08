#!/usr/bin/env python3
import asyncio
import json
import logging
import time
import os
#import platform
#import ssl
#import numpy as np
from aiortc import VideoStreamTrack
from av import VideoFrame
import cv2
import threading
from multiprocessing import Process,Queue
#import queue
from aiohttp import web
from aiortc import RTCPeerConnection, RTCSessionDescription
from aiortc.contrib.media import MediaPlayer, MediaRelay
from aiortc.rtcrtpsender import RTCRtpSender
from urllib.parse import urlparse
import yolo_detecting
from yolo_detecting import *
from face_recognition import *
from metering_time import *
from lib.socket import *
from lib.YOLO_modified import conv_replace

os.environ["QT_QPA_PLATFORM_PLUGIN_PATH"]="C:\\Users\\Дмитрий\\work_env\\Lib\\site-packages\\PyQt5\\Qt5\\plugins\\platforms"
#import torch_directml
#dml = torch_directml.device()
ROOT = os.path.dirname(__file__)
t=Metric_time()
t.add()
#logging.basicConfig(level=logging.INFO, filename="py_log.log",filemode="w")
def video_get(q,link):
    cap=cv2.VideoCapture(link)
    i=0
    while True:
        rat,frame=cap.read()
        q.put((i,frame))
        i+=1
def predict_get(q,q_result,result_images,key_frame=0):
    model=YOLO("models/yolo_best.pt",task="detect")
    model=conv_replace(model)
    while True:
        i,frame=q.get()
        #coordinates=predict(model,frame)      
        #q_result.put((i,recognate(coordinates,frame)))
        #frame=cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        if key_frame!=0:
            if i % key_frame>0:
                q_result.put((i,frame))
            else:
                q_result.put((i,predict(model,frame,result_images)))
        else:
            q_result.put((i,predict(model,frame,result_images)))
class Capture_cv2(VideoStreamTrack):
    def __init__(self,capture=0):
        super().__init__()
        self.result=None
        self.count=0
        self.buffer={}
        '''
        if not self.cap.isOpened():
            raise IOError("Cannot open webcam")
        '''
    async def recv(self):
        global q_result
        pts, time_base = await self.next_timestamp()
        T=time.time()
        t.mark()
        i,frame=q_result.get()
        while True:
            #logging.info(f'Frame: {frame}')
            if i==self.count:
                self.count+=1
                break
            elif i in self.buffer.keys():
                frame=self.buffer.pop(i)
                self.count+=1
                break
            else:
                self.buffer[i]=frame
        T=time.time()-T
        f=1/T
        font=cv2.FONT_HERSHEY_DUPLEX
        frame=cv2.putText(frame,str(round(f)),(200,200),font,4.0,(0,255,0),4)
        result=VideoFrame.from_ndarray(frame,format="bgr24")
        result.pts=pts
        if i==500:
            t.view(save=True)
        result.time_base=time_base
        return result
def create_local_tracks(play, decode,options):
    global relay, webcam
    player = MediaPlayer(play, decode=decode,options=options)
    return player.audio, player.video
    
def force_codec(pc, sender, forced_codec):
    kind = forced_codec.split("/")[0]
    codecs = RTCRtpSender.getCapabilities(kind).codecs
    transceiver = next(t for t in pc.getTransceivers() if t.sender == sender)
    transceiver.setCodecPreferences(
        [codec for codec in codecs if codec.mimeType == forced_codec]
    )
    
async def index(request):
    content = open(os.path.join(ROOT, "index.html"), "r").read()
    return web.Response(content_type="text/html", text=content)


async def javascript(request):
    content = open(os.path.join(ROOT, "client.js"), "r").read()
    return web.Response(content_type="application/javascript", text=content)
    
async def get_image(request):
    url=urlparse(str(request.url)).path
    url=url[1:len(url)]
    return web.FileResponse(url)
    
async def offer(request):
    params = await request.json()
    offer = RTCSessionDescription(sdp=params["sdp"], type=params["type"])

    pc = RTCPeerConnection()
    pcs.add(pc)
    @pc.on("connectionstatechange")
    async def on_connectionstatechange():
        print("Connection state is %s" % pc.connectionState)
        if pc.connectionState == "failed":
            await pc.close()
            pcs.discard(pc)
    #play="on-the-street-remast.mp4"
    play="video/vlc-record-2025-05-05-13h12m51s-rtsp___192.168.6.41_554_1-.avi"
    #play="rtsp://admin:admin@192.168.6.38:554/1"
    video = Capture_cv2(capture=play)
    if video:
        video_sender = pc.addTrack(video)
    await pc.setRemoteDescription(offer)

    answer = await pc.createAnswer()
    await pc.setLocalDescription(answer)

    return web.Response(
        content_type="application/json",
        text=json.dumps(
            {"sdp": pc.localDescription.sdp, "type": pc.localDescription.type}
        ),
    )


pcs = set()
async def on_shutdown(app):
    # close peer connections
    coros = [pc.close() for pc in pcs]
    await asyncio.gather(*coros)
    pcs.clear()
    
if __name__ == "__main__":
    host="0.0.0.0"
    port=8088
    q_result=Queue()
    q=Queue()
    result_images=Queue()
    #threading.Thread(target=video_get,args=(q,"video/vlc-record-2025-05-05-13h12m51s-rtsp___192.168.6.41_554_1-.avi")).start()
    #threading.Thread(target=video_get,args=(q,"rtsp://admin:admin@192.168.6.38:554/1")).start()
    threading.Thread(target=video_get,args=(q,"video/test.mp4")).start()
    threading.Thread(target=lambda:asyncio.run(socket_start(result_images)),args=()).start()    
    th_count=28
    count=0
    while count<th_count:
        Process(target=predict_get,args=(q,q_result,result_images)).start()
        count+=1
    ssl_context=None
    app = web.Application()
    app.on_shutdown.append(on_shutdown)
    app.router.add_get("/", index)
    app.router.add_get("/client.js", javascript)
    app.router.add_post("/offer", offer)
    pathes=os.listdir("imgs/")
    for img in pathes:
        app.router.add_get(f"/imgs/{img}",get_image)
    web.run_app(app, host=host, port=port, ssl_context=ssl_context)