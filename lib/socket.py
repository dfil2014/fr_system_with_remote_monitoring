import asyncio
import pathlib
import base64
import json
import io

from functools import partial
from websockets.asyncio.server import serve

async def work(result_images,websocket):
    while True:
        #name = await websocket.recv()
        if result_images.empty():
            continue
        image,result,label=result_images.get()
        buffer = io.BytesIO()
        image.save(buffer,format="JPEG")
        bytesarray = buffer.getvalue()
        encoded_data = base64.b64encode(bytesarray)
        await websocket.send(json.dumps({'image':encoded_data.decode('ascii'),'defined':result,'label':label}))

async def socket_start(result_images):
    work_with_queue=partial(work,result_images)
    async with serve(work_with_queue, "0.0.0.0", 8765) as server:
        await server.serve_forever()

#if __name__ == "__main__":
#asyncio.run(socket_start())