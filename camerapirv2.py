#!/usr/bin/python3
import time
from datetime import datetime
import os
import sys
from picamera2 import Picamera2
from picamera2.encoders import H264Encoder, Quality
from picamera2.outputs import FfmpegOutput
import numpy as np
import shutil
import logging
from logging.handlers import TimedRotatingFileHandler
from logging import handlers
import cameraconfig
from gpiozero import MotionSensor

xtime = 0
encoding = False
currentfile = ''
strdatetime = ''

pir = MotionSensor(4)

if __name__ == "__main__":
    strdatetime = datetime.now().strftime("%Y%m%d%H%M%S")
    logging.basicConfig(format='%(asctime)s.%(msecs)03d %(levelname)s %(message)s', datefmt='%Y-%m-%d %H:%M:%S', encoding='utf-8', level=logging.INFO)
    handler = TimedRotatingFileHandler(f"{cameraconfig.log_folder}camerapirv2.log", when="d", interval=1)
    handler.setFormatter(logging.Formatter('%(asctime)s.%(msecs)03d %(levelname)s %(message)s', datefmt='%Y-%m-%d %H:%M:%S'))
    logging.getLogger().addHandler(handler)

    logging.info(f"camera application started")

    #enable os HDR
    os.system("v4l2-ctl --set-ctrl wide_dynamic_range=1 -d /dev/v4l-subdev0")

    with Picamera2() as picam2:
        try:    
            config = picam2.create_video_configuration(main={"size": cameraconfig.main_resolution})
            picam2.configure(config)

            encoder = H264Encoder()

            picam2.start()

            picam2.set_controls({"AeEnable": True, "AwbEnable": True, "FrameRate": cameraconfig.framerate})
            
            time.sleep(5)

            logging.info("cam init done")

            try:
                while True:
                    if not encoding and pir.motion_detected:
                        strdatetime = datetime.now().strftime("%Y%m%d%H%M%S")
                        xtime = time.time()
                        currentfile = f"{cameraconfig.capture_folder}{strdatetime}.mp4"
                        encoder.output = FfmpegOutput(currentfile)
                        picam2.start_encoder(encoder, quality=Quality.VERY_HIGH)
                        encoding = True
                        logging.info(f"recording started:{currentfile}")

                    if encoding and (time.time() - xtime > cameraconfig.maxrectimeseconds or not pir.motion_detected):
                        picam2.stop_encoder()
                        encoding = False
                        videofile = f"{cameraconfig.videos_folder}{strdatetime}-{cameraconfig.cam_name}.mp4"
                        shutil.move(currentfile, videofile)
                        logging.info(f"recording stopped, {currentfile} file moved to {videofile}")

                    time.sleep(1)
                
            except KeyboardInterrupt:
                pass
                
        #except Exception as err:
        #    logging.error(f"Error {err=}, {type(err)=}")
            
        finally:
            try:
                logging.info(f"closing camera")
                if encoding:
                    picam2.stop_encoder()
                picam2.stop()
                picam2.close()
                logging.info(f"camera closed")
            except Exception as err:
                logging.error(f"Camera closing Error {err=}, {type(err)=}")

    #disable os HDR     
    os.system("v4l2-ctl --set-ctrl wide_dynamic_range=0 -d /dev/v4l-subdev0")

    logging.info(f"camera application  finished")

