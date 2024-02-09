import os
import logging
from logging.handlers import TimedRotatingFileHandler
from logging import handlers
import traceback
from gpiozero import CPUTemperature
import cameraconfig
from gpiozero import OutputDevice
import time

if __name__ == "__main__":

    logging.basicConfig(format='%(asctime)s.%(msecs)03d %(levelname)s %(message)s', datefmt='%Y-%m-%d %H:%M:%S', encoding='utf-8', level=logging.INFO)
    handler = TimedRotatingFileHandler(f"{cameraconfig.log_folder}fanoff.log", when="d", interval=1)
    handler.setFormatter(logging.Formatter('%(asctime)s.%(msecs)03d %(levelname)s %(message)s', datefmt='%Y-%m-%d %H:%M:%S'))
    logging.getLogger().addHandler(handler)
    
    try:
        logging.info(f"fan application started.")
        
        fan = OutputDevice(cameraconfig.fanpin)
        
        logging.info(f"fan gpio pin: {cameraconfig.fanpin}")
        
        fan.off()
        
        logging.info(f"fan stopped")
  
        logging.info(f"fan application finished")
        
    except KeyboardInterrupt:
        pass
            
    except Exception as err:
        logging.error(f"Error {err=}, {type(err)=}, {traceback.format_exc()}")