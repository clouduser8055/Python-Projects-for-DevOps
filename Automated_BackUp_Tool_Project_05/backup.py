import argparse
import shutil
import boto3
import logging
import os

logging.basicConfig(
    filename="backup.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

def get_arguments():
    parser = argparse.ArgumentParser(description="Automated Backup Tool")

    parser.add_argument(
        "--source",
        required=True,
        help="Select from backup folder"
    )

    return parser.parse_args()

args = get_arguments()

print(args.source)
logging.info(f"Source folder you asked for : {args.source}")

archive_name = "my_backup"

shutil.make_archive(archive_name, 'zip', args.source)
print("Backup Created Successfully")
logging.info("Bakup Created Successfully")

bucket = "my-devops-backup-05"

s3 = boto3.client('s3')
try:
    s3.upload_file(f"{archive_name}.zip", bucket, f"{archive_name}.zip")
    os.remove(f"{archive_name}.zip")
    logging.info(f"{archive_name}.zip is uploaded to AWS S3 {bucket} Bucket")
except Exception as e:
    print(e)
    logging.error(e)