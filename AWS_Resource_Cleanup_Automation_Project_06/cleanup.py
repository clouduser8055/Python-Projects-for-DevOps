import boto3
import logging

logging.basicConfig(
    filename="cleanup.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)
region = "ap-south-1"
ec2 = boto3.client('ec2', region_name=region)
logging.info(f"Region: {region}")
response = ec2.describe_volumes()
logging.info("Finding Unused Volumes.....")
unused_volumes = []
for volume in response["Volumes"]:

    if volume['State'] == "available":
        volume_id = volume["VolumeId"]
        unused_volumes.append(volume_id)

if len(unused_volumes) > 0:
    print(f"DRY RUN: Found {len(unused_volumes)} unused volumes:\n{unused_volumes}")
    logging.info(f"DRY RUN: Found {len(unused_volumes)} unused volumes:\n{unused_volumes}")
    confirm = input("Delete these volumes? (yes/no): ")
    if confirm.lower() == 'yes':
        for vol in unused_volumes:
            try:
                ec2.delete_volume(VolumeId = vol)
                print(f"Volume with {vol} is deleted!")
                logging.info(f"Volume with {vol} is deleted!")
            except Exception as e:
                print(f"ERROR: {e}")
                logging.error(e)
        logging.info("Unused Volumes Are Deleted Successfully.")
    else:
        print("Deletion Cancelled")
        logging.info("Deletion Cancelled")
else:
    print("Your Environment is Already Clean.")
    logging.info("Your Environment is Already Clean.")