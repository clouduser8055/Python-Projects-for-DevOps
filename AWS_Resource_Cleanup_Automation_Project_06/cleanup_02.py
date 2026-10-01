import boto3
import argparse
from botocore.exceptions import ClientError
import logging

logging.basicConfig(
    filename="cleanup_03.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

def get_arguments():
    parser = argparse.ArgumentParser(description="AWS Cleanup Automation")

    parser.add_argument(
        "--resource",
        choices=["ec2", "volumes"],
        required=True,
        help="Unused Resources on AWS"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show resources without deleting them"
    )

    return parser.parse_args()

def stopped_instances(ec2):
    response = ec2.describe_instances(
        Filters = [
            {
                "Name": "instance-state-name",
                "Values": ["stopped"]
            }
        ]
    )
    response_list = []
    instances = 0
    for reservation in response["Reservations"]:
        for instance in reservation["Instances"]:
            instances += 1
            for key in instance.get('Tags', []):
                if key["Key"] == "Name":
                    name = key["Value"]

            response_list.append(
                {
                    "id": instance["InstanceId"],
                    "name": name,
                    "state": instance["State"]["Name"],
                    "type": instance["InstanceType"]
                }
            )
    print(f"Found: {instances} stopped EC2 instances\n")

    return response_list

def unused_volumes(ec2):
    response = ec2.describe_volumes(
        Filters = [
            {
                "Name": "status",
                "Values": ["available"]
            }
        ]
    )
    response_list = []
    volumes = 0
    l = 0
    for volume in response["Volumes"]:
        volumes += 1
        data = response["Volumes"][l]
        if 'Tags' in data:
            for key in volume.get('Tags', []):
                if key["Key"] == "Name":
                    name = key["Value"]
            response_list.append(
                {
                    "name":name,
                    "id": volume["VolumeId"],
                    "state": volume["State"],
                    "type": volume["VolumeType"]
                }
            )
        else:
            response_list.append(
                {
                    "id": volume["VolumeId"],
                    "state": volume["State"],
                    "type": volume["VolumeType"],
                    "name": ""
                }
            )
        l += 1
    print(f"Found: {volumes} unused EBS Volumes.\n")

    return response_list

def display_resources(resources):
    if not resources:
        print("No unused resources found")
        logging.info("No unused resources found.")
        return

    for resource in resources:
        print(f"Name: {resource["name"]}")
        print(f"ID: {resource["id"]}")
        print(f"STATE: {resource["state"]}")
        print(f"TYPE: {resource["type"]}")
        print("-" * 40)\

    print(f"\nResources Found: {len(resources)}")

    return len(resources)

def confirm_cleanup():
    answer = input("Are you sure you want to delete these resources? (y/N)")

    return answer.lower() == "y"

def terminate_instances(ec2, resources):
    for resource in resources:
        instance_id = resource["id"]
        try:
            print(f"Terminating EC2 instance: {resource["name"]}")

            ec2.terminate_instances(
                InstanceIds=[instance_id]
            )

            print(f"Termination requested: {instance_id}")
            logging.info(f"Termination requested: {instance_id}")

        except ClientError as error:
            error_code = error.response["Error"]["Code"]
            error_message = error.response["Error"]["Message"]

            print(
                f"Failed to terminate {instance_id}: "
                f"{error_code} - {error_message}"
            )

            logging.error(
                f"Failed to terminate EC2 instance "
                f"{instance_id}: {error_code} - {error_message}"
            )

def delete_volumes(ec2, resources):
    for resource in resources:
        volume_id = resource["id"]
        try:
            print(f"Deleting EBS Volume: {volume_id}")

            ec2.delete_volume(
                VolumeId = volume_id
            )

            print(f"Deletion Requested: {volume_id}")
            logging.info(f"Deletion Requested: {volume_id}")

        except ClientError as error:
            error_code = error.response["Error"]["Code"]
            error_message = error.response["Error"]["Message"]

            print(
                f"Failed to delete {volume_id}: "
                f"{error_code} - {error_message}"
            )

            logging.error(
                f"Failed to delete EBS volume "
                f"{volume_id}: {error_code} - {error_message}"
            )



def main():
    logging.info("AWS cleanup automation started")
    args = get_arguments()
    ec2 = boto3.client('ec2', region_name="ap-south-1")

    if args.resource == "ec2":
        print("\n===== STOPPED EC2 INSTANCES =====\n")
        logging.info("Fetching EC2 Stopped Instances....")
        response = stopped_instances(ec2)
        count = display_resources(response)

    elif args.resource == "volumes":
        print("\n===== UNATTACHED EBS VOLUMES =====\n")
        logging.info("Fetching Unused EBS Volumes....")
        response = unused_volumes(ec2)
        count = display_resources(response)

    else:
        print("Please Specify a resource.")
        logging.info("No Resource is specified")
        return

    if args.dry_run:
        print(f"\nDRY RUN: {count} resource(s) identified. "
              "No resources were deleted."
        )
        logging.info(f"DRY RUN completed. {count} {args.resource} resource(s) identified."
        )
        return

    if not response:
        print("\nNo resource found. Nothing to clean")
        logging.info("No resource found. Nothing to clean")
        return

    if confirm_cleanup():
        print("\nCleanup Approved")
        logging.info("Cleanup Approved")

        if args.resource == "ec2":
            terminate_instances(ec2, response)

        elif args.resource == "volumes":
            delete_volumes(ec2, response)

        print(f"Cleanup operation completed for {count} resource(s).")

    else:
        print("\nCleanup Cancelled")
        logging.info("Cleanup Cancelled")

    logging.info("AWS cleanup automation finished")

if __name__ == "__main__":
    main()