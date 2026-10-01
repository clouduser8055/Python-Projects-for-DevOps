import boto3
import argparse
import logging
from datetime import datetime, timezone
from botocore.exceptions import ClientError

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
        "--region",
        default="ap-south-1",
        help="Specify your AWS Region"
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Forcing AWS Resources to Delete."
    )
    mode_group = parser.add_mutually_exclusive_group()
    mode_group.add_argument(
        "--dry-run",
        action="store_true",
        help="Show resources without deleting them"
    )
    mode_group.add_argument(
        "--execute",
        action="store_true",
        help="Actually delete resources"
    )
    parser.add_argument(
    "--older-than",
    type=int,
    default=30,
    help="Only consider resources older than this many days"
    )

    return parser.parse_args()

def get_tags(resource):
    tags = {}

    for tag in resource.get('Tags', []):
        tags[tag["Key"]] = tag["Value"]

    return tags

def is_protected(resource):
    environment = resource["tags"].get("Environment")

    return environment == "production"

def get_cleanup_candidate(resources, resource_type, older_than):
    candidates = []
    protected_count = 0
    too_new_count = 0

    for resource in resources:
        if is_protected(resource):
            print(f"Skipping Protected Resource: {resource['id']}")
            logging.warning(f"Protected Resource Skipped: {resource['id']}")
            protected_count += 1
            continue

        age_days = calculate_age_days(
            resource,
            resource_type
        )

        if age_days < older_than:
            print(
                f"Skipping resource younger than "
                f"{older_than} days: {resource['id']}"
            )

            too_new_count += 1
            continue

        candidates.append(resource)
        

    return candidates, protected_count, too_new_count

def stopped_instances(ec2):
    paginator = ec2.get_paginator("describe_instances")
    pages = paginator.paginate(
        Filters = [
            {
                "Name": "instance-state-name",
                "Values": ["stopped"]
            }
        ]
    )
    response_list = []
    instances = 0
    for page in pages:
        for reservation in page["Reservations"]:
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
                        "type": instance["InstanceType"],
                        "launch_time": instance["LaunchTime"],
                        "tags": get_tags(instance)
                    }
                )
    print(f"Found: {instances} stopped EC2 instances\n")

    return response_list

def unused_volumes(ec2):
    paginator = ec2.get_paginator("describe_volumes")
    pages = paginator.paginate(
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
    for page in pages:
        for volume in page["Volumes"]:
            volumes += 1
            data = page["Volumes"][l]
            if 'Tags' in data:
                for key in volume.get('Tags', []):
                    if key["Key"] == "Name":
                        name = key["Value"]
                response_list.append(
                    {
                        "name":name,
                        "id": volume["VolumeId"],
                        "state": volume["State"],
                        "type": volume["VolumeType"],
                        "create_time": volume["CreateTime"],
                        "tags": get_tags(volume)
                    }
                )
            else:
                response_list.append(
                    {
                        "name": "",
                        "id": volume["VolumeId"],
                        "state": volume["State"],
                        "type": volume["VolumeType"],
                        "create_time": volume["CreateTime"],
                        "tags": get_tags(volume)
                    }
                )
            l += 1
    print(f"Found: {volumes} unused EBS Volumes.\n")

    return response_list

def display_resources(resources, resource_type):
    if not resources:
        print("No unused resources found")
        logging.info("No unused resources found.")
        return 0

    for resource in resources:

        age_days = calculate_age_days(
            resource,
            resource_type
        )

        print(f"Name: {resource["name"]}")
        print(f"ID: {resource["id"]}")
        print(f"STATE: {resource["state"]}")
        print(f"TYPE: {resource["type"]}")
        if resource_type == "ec2":
            print(f"Launch age: {age_days} days")
        else:
            print(f"Creation age: {age_days} days")

        environment = resource["tags"].get(
            "Environment",
            "Not Specified"
        )
        print(f"Environment: {environment}")

        print("-" * 40)\

    print(f"\nResources Found: {len(resources)}")

    return len(resources)

def confirm_cleanup():
    answer = input("Are you sure you want to delete these resources? (y/N)")

    return answer.lower() == "y"

def terminate_instances(ec2, resources):
    successful = 0
    failed = 0
    for resource in resources:
        instance_id = resource["id"]
        try:
            print(f"Terminating EC2 instance: {resource["name"]}")

            ec2.terminate_instances(
                InstanceIds=[instance_id]
            )

            print(f"Termination requested: {instance_id}")
            logging.info(f"Termination requested: {instance_id}")

            successful += 1

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

            failed += 1

    return successful, failed

def delete_volumes(ec2, resources):
    successfull = 0
    failed = 0

    for resource in resources:
        volume_id = resource["id"]
        try:
            print(f"Deleting EBS Volume: {volume_id}")

            ec2.delete_volume(
                VolumeId = volume_id
            )

            print(f"Deletion Requested: {volume_id}")
            logging.info(f"Deletion Requested: {volume_id}")

            successfull += 1

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

            failed += 1

    return successfull, failed

def calculate_age_days(resource, resource_type):
    now = datetime.now(timezone.utc)

    if resource_type == "ec2":
        resource_time = resource["launch_time"]

    elif resource_type == "volumes":
        resource_time = resource["create_time"]

    else:
        return 0

    age = now - resource_time

    return age.days

def main():
    logging.info("AWS cleanup automation started")

    args = get_arguments()
    if args.execute:
        dry_run = False
    else:
        dry_run = True
    ec2 = boto3.client('ec2', region_name=args.region)

    print(f"\nAWS Region: {args.region}")
    if args.execute:
        dry_run = False
        print("Mode: EXECUTE")
    else:
        dry_run = True
        print("Mode: DRY RUN")

    logging.info(
    f"Starting cleanup: resource={args.resource}, "
    f"region={args.region}, "
    f"execute={args.execute}, "
    f"force={args.force}"
    )

    if args.resource == "ec2":
        print("\n===== STOPPED EC2 INSTANCES =====\n")
        logging.info("Fetching EC2 Stopped Instances....")
        response = stopped_instances(ec2)

    elif args.resource == "volumes":
        print("\n===== UNATTACHED EBS VOLUMES =====\n")
        logging.info("Fetching Unused EBS Volumes....")
        response = unused_volumes(ec2)
        
    else:
        print("Please Specify a resource.")
        logging.info("No Resource is specified")
        return

    found_count = display_resources(response, args.resource)
    cleanup_candidates, protected_count, too_new_count = get_cleanup_candidate(response, args.resource, args.older_than)
    candidate_count = len(cleanup_candidates)

    if dry_run:
        print("\n===== DRY RUN SUMMARY =====")
        print(f"Region: {args.region}")
        print(f"Age threshold: {args.older_than} days")
        print(f"Resources found: {found_count}")
        print(f"Protected resources: {protected_count}")
        print(f"Too recent: {too_new_count}")
        print(f"Cleanup candidates: {candidate_count}")
        print("No resources were deleted.")

        logging.info(
            f"Dry run: region={args.region}, "
            f"resource={args.resource}, "
            f"age_threshold={args.older_than}, "
            f"found={found_count}, "
            f"protected={protected_count}, "
            f"too_new={too_new_count}, "
            f"candidates={candidate_count}"
        )

        return

    if not cleanup_candidates:
        print("\nNo resources are eligible for cleanup.")
        return
    
    if not response:
        print("\nNo resource found. Nothing to clean")
        logging.info("No resource found. Nothing to clean")
        return

    if args.force and not args.execute:
        print("--force can only be used with --execute.")
        return

    if args.force or confirm_cleanup():
        print("\nCleanup Approved")
        logging.info("Cleanup Approved")
        if args.resource == "ec2":
            successful, failed = terminate_instances(ec2, cleanup_candidates)

        elif args.resource == "volumes":
            successful, failed = delete_volumes(ec2, cleanup_candidates)

        print("\n===== CLEANUP SUMMARY =====")
        print(f"Resources found: {found_count}")
        print(f"Protected resources: {protected_count}")
        print(f"Cleanup candidates: {candidate_count}")
        print(f"Successful requests: {successful}")
        print(f"Failed requests: {failed}")
        logging.info(
            f"Cleanup summary: found={found_count}, "
            f"protected={protected_count}, "
            f"candidates={candidate_count}, "
            f"successful={successful}, "
            f"failed={failed}"
        )
    else:
        print("\nCleanup Cancelled")
        logging.info("Cleanup Cancelled")

    logging.info("AWS cleanup automation finished")

if __name__ == "__main__":
    main()