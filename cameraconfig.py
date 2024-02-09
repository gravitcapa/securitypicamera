#AWS S3 cloud storage
#AWS API user what has permissions to write to S3

# open AWS Console, IAM -> Policies -> create new policy 'Cameras' using this JSON
#{
#    "Version": "2012-10-17",
#    "Statement": [
#        {
#            "Sid": "VisualEditor0",
#            "Effect": "Allow",
#            "Action": [
#                "s3:PutObject",
#                "s3:GetObject",
#                "s3:ListBucket",
#                "s3:GetBucketLocation"
#            ],
#            "Resource": "*"
#        }
#    ]
#}

# open AWS Console, IAM -> Users -> Create new user 'camuser'
# select User 'camuser' -> Permissions -> Permissions policies -> Add previously created policy 'Cameras' to this user
# User -> Security credentials -> Access Keys -> Create Access Key (key_id and secret) region is the S3 bucket region
# open AWS Console, open S3 -> create bucket, specify name and all settings by default, do not make it public
# open S3 bucket -> Management -> Lifecycle rules -> Create Lifecycle rule, specify name, check box expire current versions after X days, this will automaticaly delete old files after X days

#AWS API your user access key
aws_access_key_id = 'MYKEY-REPLACE'
#AWS API your user secret
aws_secret_access_key = 'MYSECRET-REPLACE'
#AWS region for example ca-central-1
aws_region = 'MYREGION-REPLACE'
#AWS S3 bucket, it's recomended to setup Lifecycle rules for a bucket with a automated cleanup after X days
aws_s3_bucket_name = 'homecameras'
#AWS bucket's folder for camera recordings, bucket can have many folders for all yours cameras, better to keep recordings in separate folders
aws_s3_bucket_folder = 'camera1'

#camera name
cam_name = 'cam1'

# application log folder
log_folder = 'log/'

# current video capture folder for incomplete videos
capture_folder = "capture/"

# recorded video folder but not uploaded
videos_folder = "videos/"

# archive folder for uploaded to S3 folder videos
archive_folder = "archive/"

# target disk free space percentage, keep low to use full disk for archive, default is 10%
target_free_space_percentage = 10

# video frames per second (will affect file size), 2 FPS means about 10Gb of data per day in (1920, 1080) resolution
framerate = 2.0

# main video resolution, (1920, 1080) max with HDR
main_resolution = (1920, 1080)

# max file rec time in seconds (will affect file size and number of files per hour) default is 5 minutes long video files
maxrectimeseconds = 300.0

# Motion detection
# Measure pixels differences between current and previous frame settings (mse)

# software motion detection resolution, should stay low about (320, 240) to prevent high sensitivity to noise
motion_detection_resolution = (320, 240)

# avgmse stat points, application collects statistics for dynamic mse adjustments based on stat points, mse for day around 1 and night around 7, it affects triggers
maxmseitems = 60

# motion detection trigger percentage above current avgmse
trigger_percentage = 50.0

# maximum mse in percent to avgmse to skip noise for avgmse calculation, if current mse is above this setting, application will ignore stat point
maxmse_percentage = 50.0 

# minimum trigger mse to reduce noise, default is 4.0 experemental for day light then mse around 1
minmse = 4.0

# maximum trigger mse to reduce noise, camera calibration causes spikes in mse 
maxmse = 20.0

# fan ON CPU temperature
startfantemp = 43.0

# fan OFF CPU temperature
stopfantemp = 40.0

# max CPU temperature to stop upload
maxcputemp = 45.0

# gpio fan pin
fanpin = 17

# gpio harware PIR sensor pin
pirpin = 4
