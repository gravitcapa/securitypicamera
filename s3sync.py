import os
import boto3
from botocore.exceptions import NoCredentialsError
import logging
from logging.handlers import TimedRotatingFileHandler
from logging import handlers
import cameraconfig

def upload_to_s3(local_folder, bucket_name, s3_folder, archive_folder):
    """
    Uploads files from a local folder to an AWS S3 bucket and moves uploaded files to an archive folder.

    Parameters:
    - local_folder: Local folder path containing files to be uploaded.
    - bucket_name: AWS S3 bucket name.
    - s3_folder: S3 folder path where files will be uploaded.
    - archive_folder: Local archive folder path.
    """
    s3 = boto3.client('s3')

    for root, dirs, files in os.walk(local_folder):
        for file in files:
            local_file_path = os.path.join(root, file)
            s3_key = os.path.join(s3_folder, file)

            try:
                # upload file to S3 cloud storage
                logging.info(f"File uploading: {local_file_path} to {bucket_name}/{s3_key}")
                s3.upload_file(local_file_path, bucket_name, s3_key)
                logging.info(f"File uploaded: {local_file_path} to {bucket_name}/{s3_key}")

                # Move the uploaded file to the specified archive folder
                os.makedirs(archive_folder, exist_ok=True)
                archive_file_path = os.path.join(archive_folder, file)
                os.rename(local_file_path, archive_file_path)
                logging.info(f"File moved to archive: {local_file_path} to {archive_file_path}")

            except NoCredentialsError:
                logging.error("Credentials not available")
            
            except Exception as err:
                logging.error(f"Error {err=}, {type(err)=}")

if __name__ == "__main__":

    logging.basicConfig(format='%(asctime)s.%(msecs)03d %(levelname)s %(message)s', datefmt='%Y-%m-%d %H:%M:%S', encoding='utf-8', level=logging.INFO)
    handler = TimedRotatingFileHandler(f"{cameraconfig.log_folder}s3sync.log", when="d", interval=1)
    handler.setFormatter(logging.Formatter('%(asctime)s.%(msecs)03d %(levelname)s %(message)s', datefmt='%Y-%m-%d %H:%M:%S'))
    logging.getLogger().addHandler(handler)
    
    try:
        logging.info(f"s3sync application started")

        # Configure AWS credentials and region
        boto3.setup_default_session(aws_access_key_id=cameraconfig.aws_access_key_id,  aws_secret_access_key=cameraconfig.aws_secret_access_key,  region_name=cameraconfig.aws_region)

        # Call the upload function
        upload_to_s3(cameraconfig.videos_folder, cameraconfig.aws_s3_bucket_name, cameraconfig.aws_s3_bucket_folder, cameraconfig.archive_folder)

        logging.info(f"s3sync application finished")
        
    except KeyboardInterrupt:
        pass
            
    except Exception as err:
        logging.error(f"Error {err=}, {type(err)=}")