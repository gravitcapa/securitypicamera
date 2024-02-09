import os
import psutil
import time
import logging
from logging.handlers import TimedRotatingFileHandler
from logging import handlers
import cameraconfig

def delete_oldest_files(folder, space_to_free):
    logging.info(f"Disk space cleanup started. folder:{folder}")
    files = [(f, os.path.getmtime(os.path.join(folder, f)), os.path.getsize(os.path.join(folder, f))) for f in os.listdir(folder)]
    files.sort(key=lambda x: x[1])

    for file in files:
        
        file_path = os.path.join(folder, file[0])
        os.remove(file_path)
        space_to_free -= file[2]
        if space_to_free <= 0:
            break

        logging.info(f"Deleted: {file_path} created dt: {time.ctime(file[1])} size: {file[2]}")
        
    logging.info(f"Disk space cleanup completed. folder:{folder}")

if __name__ == "__main__":

    logging.basicConfig(format='%(asctime)s.%(msecs)03d %(levelname)s %(message)s', datefmt='%Y-%m-%d %H:%M:%S', encoding='utf-8', level=logging.INFO)
    handler = TimedRotatingFileHandler(f"{cameraconfig.log_folder}cleanup.log", when="d", interval=1)
    handler.setFormatter(logging.Formatter('%(asctime)s.%(msecs)03d %(levelname)s %(message)s', datefmt='%Y-%m-%d %H:%M:%S'))
    logging.getLogger().addHandler(handler)

    try:
        
        logging.info(f"Application started")
     
        disk_usage = psutil.disk_usage(cameraconfig.archive_folder)
        total_space = disk_usage.total
        free_space = disk_usage.free
        used_space = total_space - free_space
        target_free_space = total_space * (cameraconfig.target_free_space_percentage / 100)
        space_to_free = target_free_space - free_space

        logging.info(f"Total disk space: {total_space / (1024 ** 3):.2f} GB")
        logging.info(f"Available disk space: {free_space / (1024 ** 3):.2f} GB")
        logging.info(f"Used disk space: {used_space / (1024 ** 3):.2f} GB")
        logging.info(f"Target free disk percent: {cameraconfig.target_free_space_percentage} space: {target_free_space / (1024 ** 3):.2f} GB")
        logging.info(f"Space_to_free: {space_to_free / (1024 ** 3):.2f} GB")
        
        if space_to_free > 0 :
            delete_oldest_files(cameraconfig.archive_folder, space_to_free)
            delete_oldest_files(cameraconfig.videos_folder, space_to_free)
            delete_oldest_files(cameraconfig.log_folder, space_to_free)
            logging.info("Disk space cleanup completed.")
        else:
            logging.info("No need to clean up disk space.")

        logging.info(f"Application finished")
        
    except KeyboardInterrupt:
        pass
            
    except Exception as err:
        logging.error(f"Error {err=}, {type(err)=}")