from pathlib import Path
from datetime import datetime
import shutil
import logging
import boto3
import argparse
import os

logging.basicConfig(
    filename="backup_01.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

def get_arguments():
    parser = argparse.ArgumentParser(description="Automated Backup Tool")

    parser.add_argument(
        "--source",
        required=True,
        help="Taking source file for Backup"
    )

    parser.add_argument(
        "--bucket",
        required=True,
        help="AWS S3 Bucket"
    )

    return parser.parse_args()

args = get_arguments()

source = Path(args.source)
backup_dir = Path("backups")

if not backup_dir.exists():
    print("Creating Directory....")
    logging.info("Creating Directory....")
    backup_dir.mkdir(parents=True, exist_ok=True)
    logging.info(f"{backup_dir} Created Successfully.")
else:
    print(f"{backup_dir} directory is already exists.")
    logging.info(f"{backup_dir} directory is already exists.")

timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
backup_name = backup_dir / f"backup_{timestamp}"
try:
    if not source.exists():
        print(f"Source directory does not exist: {source}")
        logging.error(f"Source directory does not exist: {source}")

        exit()
    
    logging.info("Archiving..........")
    shutil.make_archive(str(backup_name), 'zip', root_dir=source)
    logging.info(f"{backup_name}.zip is successfully created.")

    print(f"Source : {source}")
    print(f"Backup : {backup_name}.zip")
    print(f"Status : SUCCESS")

    bucket = args.bucket
    # bucket = automation-bucket-02

    s3 = boto3.client('s3')
    logging.info(f"Uploading {backup_name}.zip on AWS S3 {bucket} Bucket")
    s3.upload_file(f"{backup_name}.zip", bucket, f"{backup_name}.zip")
    logging.info("Successfully Uploaded.")
    print("Cleaning Local Backup Files....")
    logging.info("Cleaning Local Backup Files....")
    os.remove(f"{backup_name}.zip")
    print(f"{backup_name} is deleted.")
    logging.info(f"{backup_name} is deleted.")
except Exception as e:
    print(f"Upload failed: {e}")
    logging.exception(f"Upload Failed: {e}")
