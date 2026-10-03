import argparse
import docker
import sys
import logging

logging.basicConfig(
    filename="docker_manager_02.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

def get_arguments():
    parser = argparse.ArgumentParser(description="Docker container management tool")

    subparsers = parser.add_subparsers(
        dest="action",
        required=True
    )

    subparsers.add_parser(
        "list",
        help="List all Docker Containers"
    )

    start_parser = subparsers.add_parser(
        "start",
        help="Start a Docker Container"
    )
    start_parser.add_argument(
        "container",
        help="Container name or ID"
    )

    stop_parser = subparsers.add_parser(
        "stop",
        help="Stop a docker container"
    )
    stop_parser.add_argument(
        "container",
        help="Container name or ID"
    )

    restart_parser = subparsers.add_parser(
        "restart",
        help="Restart a docker container"
    )
    restart_parser.add_argument(
        "container",
        help="Container name or ID"
    )

    logs_parser = subparsers.add_parser(
        "logs",
        help="Show container Logs"
    )
    logs_parser.add_argument(
        "container",
        help="Container name or ID"
    )

    return parser.parse_args()

def format_ports(ports):
    if not ports:
        return "-"

    foramatted_ports = []

    for container_port, host_bindings in ports.items():
        if host_bindings:
            for binding in host_bindings:
                host_port = binding['HostPort']
                foramatted_ports.append(
                    f"{host_port}->{container_port}"
                )
        else:
            foramatted_ports.append(container_port)

    return ", ".join(foramatted_ports)

def list_containers(client):
    print("listing Containers.....")
    logging.info("Listing all Docker Containers........")
    try:
        containers = client.containers.list(all=True)
        container_data = []

        print(
            f"{'NAME':<26}"
            f"{'ID':<12}"
            f"{'STATUS':<12}"
            f"{'IMAGE':<35}"
            f"{'PORTS':<20}"
        )
    
        for container in containers:
            image = container.image.tags
            if image:
                image = image[0]
            else:
                image = "N/A"

            container_info = {
                "name": container.name,
                "id": container.short_id,
                "status": container.status,
                "image": image,
                "ports": format_ports(container.ports)
            }

            container_data.append(container_info)

        for container in container_data: 
            print(
                f"{container['name']:<20}"
                f"{container['id']:<19}"
                f"{container['status']:<12}"
                f"{container['image']:<35}"
                f"{container['ports']:<20}"
            )
            

        logging.info(f"Found {len(containers)} containers.")

        return True
    except docker.errors.APIError as e:
        print(f"ERROR: Docker API error: {e}")
        logging.error(f"Docker API error while listing containers: {e}")

        return False

def start_container(client, args):
    try:
        container = client.containers.get(args.container)
        print(f"Starting {container.name} container......")
        logging.info(f"Starting {args.container} container......")
        container.start()
        print(f"{container.name} is successfully started.")
        logging.info(f"{container.name} is successfully started.")

        return True

    except docker.errors.NotFound:
        print(f"ERROR: Container '{args.container}' was not found.")
        logging.error(f"Container '{args.container}' was not found.")

        return False
    except docker.errors.APIError as e:
        print(f"ERROR: Docker API error: {e}")
        logging.error(f"Docker API error: {e}")

        return False

def stop_container(client, args):
    try:
        container = client.containers.get(args.container)
        print(f"Stopping {container.name} container......")
        logging.info(f"Stopping {container.name} container......")
        container.stop()
        print(f"{container.name} is successfully stopped.")
        logging.info(f"{container.name} is successfully stopped.")

        return True

    except docker.errors.NotFound:
        print(f"ERROR: Container '{args.container}' was not found.")
        logging.error(f"Container '{args.container}' was not found.")

        return False
    except docker.errors.APIError as e:
        print(f"ERROR: Docker API error: {e}")
        logging.error(f"Docker API error: {e}")

        return False

def restart_container(client, args):
    try:
        container = client.containers.get(args.container)
        print(f"Restarting {container.name} container......")
        logging.info(f"Restarting {container.name} container......")
        container.restart()
        print(f"{container.name} is successfully Restarted.")
        logging.info(f"{container.name} is successfully Restarted.")

        return True

    except docker.errors.NotFound:
        print(f"ERROR: Container '{args.container}' was not found.")
        logging.error(f"Container '{args.container}' was not found.")

        return False
    except docker.errors.APIError as e:
        print(f"ERROR: Docker API error: {e}")
        logging.error(f"Docker API error: {e}")

        return False

def container_logs(client, args):
    try:
        container = client.containers.get(args.container)

        logging.info(f"Retrieving logs for container: {container.name}")

        logs = container.logs().decode('utf-8')

        return logs
    
    except docker.errors.NotFound:
        print(f"ERROR: Container '{args.container}' was not found.")
        logging.error(f"Container '{args.container}' was not found.")

        return None
    except docker.errors.APIError as e:
        print(f"ERROR: Docker API error: {e}")
        logging.error(f"Docker API error: {e}")

        return None


def main():
    args = get_arguments()

    try:
        client = docker.from_env()

    except docker.errors.DockerException as e:
        print(f"ERROR: Could not connect to Docker: {e}")
        logging.error(f"Could not connect to Docker: {e}")
        sys.exit(1)

    if args.action == "list":
        result = list_containers(client)
        if result:
            sys.exit(0)
        else:
            sys.exit(1)

    elif args.action == "start":    
        result = start_container(client, args)
        if result:
            sys.exit(0)
        else:
            sys.exit(1)

    elif args.action == "stop":
        result = stop_container(client, args)
        if result:
            sys.exit(0)
        else:
            sys.exit(1)

    elif args.action == "restart":
        result = restart_container(client, args)
        if result:
            sys.exit(0)
        else:
            sys.exit(1)

    elif args.action == "logs":
        logs = container_logs(client, args)

        if logs is not None:
            print(f"------ Logs for {args.container} ------")
            print(logs)
            sys.exit(0)
        else:
            print("Failed to retrieve logs.")
            sys.exit(1)

if __name__ == "__main__":
    main()