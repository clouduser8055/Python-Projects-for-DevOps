from pathlib import Path
from datetime import datetime
import shutil
import logging
import boto3
import os
import json

script_dir = Path(__file__).resolve().parent
config_file = script_dir / "config.json"

logging.basicConfig(
    filename=script_dir / "backup_01.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

def load_config():
    try:
        with open(config_file, "r") as file:
            config = json.load(file)
        required_keys = ["source", "bucket", "keep"]

        for key in required_keys:
            if key not in required_keys:
                raise ValueError(f"Missing Configuration Key: {key}")

        if not isinstance(config["keep"], int):
            raise ValueError("'keep' must be an integer")

        if config["keep"] < 1:
            raise ValueError("'keep' must be greater than 0")

        return config

    except FileNotFoundError:
        logging.error("config.json was not found")
        print("ERROR: config.json was not found")
        exit()

    except json.decoder.JSONDecodeError:
        logging.error("config.json contains invalid JSON")
        print("config.json contains invalid JSON")
        exit()

    except ValueError as e:
        logging.error(f"Invalid Configuration: {e}")
        print(f"ERROR: {e}")
        exit()

config = load_config()

source = Path(config["source"])
keep = config["keep"]
backup_dir = script_dir / "backups"

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
        print(f"Source directory doesn't exist: {source}")
        logging.error(f"Source directory doesn't exist: {source}")

        exit()
    
    logging.info("Archiving..........")
    shutil.make_archive(str(backup_name), 'zip', root_dir=source)
    logging.info(f"{backup_name}.zip is successfully created.")

    print(f"Source : {source}")
    print(f"Backup : {backup_name}.zip")
    print(f"Status : SUCCESS")

    bucket = config["bucket"]
    # my aws s3 bucket: 'automation-bucket-02'
    s3 = boto3.client("s3")
    local_file = f"{backup_name}.zip"
    s3_key = f"backups/{backup_name.name}.zip"
    logging.info(f"Uploading {local_file} to s3://{bucket}/{s3_key}")

    s3.upload_file(local_file, bucket, s3_key)
    
    logging.info("Successfully Uploaded.")
    print(f"Uploaded : s3://{bucket}/{s3_key}")

    print("Cleaning Local Backup Files....")
    logging.info("Cleaning Local Backup Files....")
    os.remove(f"{backup_name}.zip")
    print(f"{backup_name} is deleted.")
    logging.info(f"{backup_name} is deleted.")

    logging.info("Checking old backups on s3....")

    response = s3.list_objects_v2(
        Bucket=bucket,
        Prefix="backups/"
    )
    objects = response.get("Contents", [])

    print(f"Total backups found: {len(objects)}")
    logging.info(f"Total backups found: {len(objects)}")

    objects.sort(key=lambda obj:obj["LastModified"], reverse=True)

    # old_backups = objects[2:]
    # old_backups = objects[args.keep:]
    old_backups = objects[keep:]

    for obj in old_backups:
        # print(obj)
        key = obj["Key"]
        logging.info(f"Deleting Old Backups: {key}")

        s3.delete_object(
            Bucket=bucket,
            Key=key
        )

        print(f"Deleted Old Backups: {key}")
        
except Exception as e:
    print(f"Backup failed: {e}")
    logging.exception("Backup Failed")

