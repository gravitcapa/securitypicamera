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
from gpiozero import OutputDevice
from gpiozero import CPUTemperature

w, h = cameraconfig.motion_detection_resolution
prev = None
xtime = 0
encoding = False
mselist = []
avgmse = 0.0
triggeredmse = 0.0;

motionevents = 0
currentfile = ''
strdatetime = ''

pirdetected = 0

if __name__ == "__main__":
    strdatetime = datetime.now().strftime("%Y%m%d%H%M%S")
    logging.basicConfig(format='%(asctime)s.%(msecs)03d %(levelname)s %(message)s', datefmt='%Y-%m-%d %H:%M:%S', encoding='utf-8', level=logging.INFO)
    handler = TimedRotatingFileHandler(f"{cameraconfig.log_folder}camera.log", when="d", interval=1)
    handler.setFormatter(logging.Formatter('%(asctime)s.%(msecs)03d %(levelname)s %(message)s', datefmt='%Y-%m-%d %H:%M:%S'))
    logging.getLogger().addHandler(handler)
 
    logging.info(f"camera application started")
    
    # enable PIR
    pir = MotionSensor(cameraconfig.pirpin)
    
    logging.info(f"PIR gpio pin: {cameraconfig.pirpin}")
  
    # enable green LED
    led = OutputDevice(cameraconfig.ledpin)
    led.on()
        
    logging.info(f"LED gpio pin: {cameraconfig.ledpin} status: {led.value}")
    
    # delete temp files in capture folder
    for filename in os.listdir(cameraconfig.capture_folder):
        file_path = os.path.join(cameraconfig.capture_folder, filename)
        os.remove(file_path)
        logging.info(f"deleted temp file: {file_path}")

    #enable os HDR
    os.system("v4l2-ctl --set-ctrl wide_dynamic_range=1 -d /dev/v4l-subdev0")

    with Picamera2() as picam2:
        try:    
            config = picam2.create_video_configuration(main={"size": cameraconfig.main_resolution}, lores={"size": cameraconfig.motion_detection_resolution, "format": "YUV420"})
            picam2.configure(config)

            encoder = H264Encoder()

            picam2.start()

            picam2.set_controls({"AeEnable": True, "AwbEnable": True, "FrameRate": cameraconfig.framerate})
            
            time.sleep(5)

            logging.info("cam init done")

            try:
                while True:
                        
                    # start mp4 encodig
                    if not encoding:
                        strdatetime = datetime.now().strftime("%Y%m%d%H%M%S")
                        picam2.set_controls({"AeEnable": False, "AwbEnable": False, "FrameRate": cameraconfig.framerate})
                        motionevents = 0
                        xtime = time.time()
                        currentfile = f"{cameraconfig.capture_folder}{strdatetime}.mp4"
                        # MP4 encoder
                        encoder.output = FfmpegOutput(currentfile)
                        picam2.start_encoder(encoder, quality=Quality.VERY_HIGH)
                        encoding = True
                        logging.info(f"new recording started:{currentfile}")
                        cpu = CPUTemperature()
                        if cpu.temperature is not None:
                            logging.info(f"CPU t: {cpu.temperature}")
                        pirdetected = 0
                    else:
                        # stop mp4 encodig, motionevents represents the seconds count with motion detected
                        if time.time() - xtime > cameraconfig.maxrectimeseconds:
                            picam2.stop_encoder()
                            picam2.set_controls({"AeEnable": True, "AwbEnable": True, "FrameRate": cameraconfig.framerate})
                            encoding = False
                            videofile = f"{cameraconfig.videos_folder}{strdatetime}-{cameraconfig.cam_name}-{pirdetected}-{motionevents}.mp4"
                            shutil.move(currentfile, videofile)
                            logging.info(f"recording stopped, {currentfile} reached maxrectime:{cameraconfig.maxrectimeseconds} file moved to {videofile}")
           
                    
                    cur = picam2.capture_buffer("lores")
                    cur = cur[:w * h].reshape(h, w)
                    
                    # Motion detection
                    if prev is not None:
                        # Measure pixels differences between current and
                        # previous frame
                        mse = np.square(np.subtract(cur, prev)).mean()
                        
                        # add mse to the list
                        if avgmse == 0 or mse <= avgmse + avgmse * (cameraconfig.maxmse_percentage / 100.0):
                            mselist.append(mse)
                            
                        # remove last element if len exeeds maxmseitems
                        if (len(mselist) > cameraconfig.maxmseitems):
                            mselist.pop(0)

                        # average mse calculation
                        if len(mselist) >= cameraconfig.maxmseitems:
                            avgmse = np.mean(mselist)
                           
                        # calculate trigger mse
                        triggermse = cameraconfig.minmse
                        tolerancemse = avgmse + avgmse * (cameraconfig.trigger_percentage / 100.0) + 1.0
                        if tolerancemse > cameraconfig.minmse:
                            triggermse = tolerancemse
                            
                        # trigger then not collecting stats and reached trigger limit
                        if avgmse > 0.0 and mse >= triggermse and mse <= cameraconfig.maxmse:
                            motionevents += 1
                            logging.info(f"new movement detected. mse:{mse:.2f} avgmse: {avgmse:.2f} trmse:{triggermse:.2f} tlmse:{tolerancemse:.2f} events:{motionevents}")
                            
                    if pir.motion_detected:                        
                        pirdetected = 1
                        logging.info(f"new PIR movement detected")
                        
                    prev = cur
                    time.sleep(1)
                
            except KeyboardInterrupt:
                pass
                
        except Exception as err:
            logging.error(f"Error {err=}, {type(err)=}")
            
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

