import argparse
import docker
import sys
import logging
import json

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

    list_parser = subparsers.add_parser(
        "list",
        help="List all Docker Containers"
    )
    list_parser.add_argument(
        "--format",
        choices=["json", "text"],
        default="text",
        help="Output format"
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

    remove_parser = subparsers.add_parser(
        "remove",
        help="Remove a docker container"
    )
    remove_parser.add_argument(
        "container",
        help="Container name or ID"
    )

    inspect_parser = subparsers.add_parser(
        "inspect",
        help="Show detailed information about a docker container"
    )
    inspect_parser.add_argument(
        "container",
        help="Container name or Id"
    )

    stats_parser = subparsers.add_parser(
        "stats",
        help="Show CPU/Memory usage of a docker container"
    )
    stats_parser.add_argument(
        "container",
        help="Container name or Id"
    )

    stats_parser.add_argument(
        "--format",
        choices=["text", "json"],
        default="text",
        help="Output format"
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

def list_containers(client,args):
    try:
        containers = client.containers.list(all=True)
        container_data = []

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

        if args.format == "json":
            print(json.dumps(container_data, indent=4))
        else:
            print("listing Containers.....")
            logging.info("Listing all Docker Containers........")
            print(
                f"{'NAME':<26}"
                f"{'ID':<12}"
                f"{'STATUS':<12}"
                f"{'IMAGE':<35}"
                f"{'PORTS':<20}"
            )

            for container in container_data: 
                print(
                    f"{container['name']:<26}"
                    f"{container['id']:<12}"
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

def remove_container(client, args):
    try:
        container = client.containers.get(args.container)
        print(f"Removing {container.name} container.....")
        logging.info(f"Removing {args.container} container.....")
        status = container.status
        if status == "running":
            print(f"{container.name} is currently {status}.")
            logging.warning(f"{container.name} is currently {status}.")
            user_input = input("Stop it before removing? (y/N)").lower()
            if user_input != "y":
                print(f"You declined stopping request for {container.name} container.")
                logging.warning(f"You declined stopping request for {container.name} container.")
                return True
            
            print(f"Stopping {container.name}......")
            logging.info(f"Stopping {container.name}......")
            container.stop()
            print(f"{container.name} is successfully stopped!")
            logging.info(f"{container.name} is successfully stopped!")
        
        confirmation = input(f"You really want to delete {container.name} container? (y/N)").lower()
        if confirmation != "y":
            print(f"Operation Cancelled!")
            logging.info(f"Operation Cancelled!")
            return True

        container.remove()
        print(f"Container {container.name} is successfully removed.")
        logging.info(f"Container {container.name} is successfully removed.")

        return True
    except docker.errors.NotFound:
        print(f"ERROR: {args.container} was Not Found")
        logging.error(f"Container {args.container} was Not Found")

        return False
    except docker.errors.APIError as e:
        print(f"ERROR: Docker API error: {e}")
        logging.error(f"Docker API error: {e}")

        return False

def inspect_container(client, args):
    try:
        container = client.containers.get(args.container)
        print(f"Inspecting {container.name} container......")
        logging.info(f"Inspecting {container.name} container......")

        info = container.attrs

        print("--------Container Information---------")
        print(f"Name: {info['Name']}")
        print(f"ID: {info['Id']}")
        print(f"Status: {info['State']['Status']}")
        print(f"Image: {info['Config']['Image']}")
        print(f"Created: {info['Created']}")

        return True

    except docker.errors.NotFound:
        print(f"ERROR: {args.container} was Not Found")
        logging.error(f"Container {args.container} was Not Found")

        return False
    except docker.errors.APIError as e:
        print(f"ERROR: Docker API error: {e}")
        logging.error(f"Docker API error: {e}")

        return False

def bytes_to_mb(value):
    return value / (1024 * 1024)

def container_stats(client, args):
    try:
        container = client.containers.get(args.container)
        if container.status != "running":
            print(
                f"ERROR: Container '{container.name}' "
                f"is not running."
            )
            return False

        logging.info(f"Getting Stats of {container.name} container......")

        stats = container.stats(stream=False)
        # print(stats)

        cpu_stats = stats['cpu_stats']['cpu_usage']['total_usage']
        precpu_stats = stats['precpu_stats']['cpu_usage']['total_usage']
        system_cpu = stats['cpu_stats']['system_cpu_usage']
        precpu_system = stats['cpu_stats']['system_cpu_usage']
        online_cpus = stats['precpu_stats']['online_cpus']
        if online_cpus is None:
            online_cpus = len(
                stats["cpu_stats"]["cpu_usage"].get(
                    "percpu_usage", []
                )
            )

        cpu_delta = cpu_stats - precpu_stats
        system_delta = system_cpu - precpu_system

        cpu_percentage = 0.0
        if cpu_delta > 0 and system_delta > 0:
            cpu_percentage = (cpu_delta / system_delta) * online_cpus * 100.0
        
        memory_stats = stats['memory_stats']
        memory_usage = memory_stats.get('usage', 0)
        memory_details = memory_stats.get('stats', {})

        cache = memory_details.get(
            'inactive_file',
            memory_details.get(
                'total_inactive_file',
                memory_details.get('cache', 0)
            )
        )

        used_memory = memory_usage - cache
        if used_memory < 0:
            used_memory = 0

        memory_limit = memory_stats.get('limit', 0)


        memory_usage_mb = bytes_to_mb(used_memory)
        memory_limit_mb = bytes_to_mb(memory_limit)

        if memory_limit_mb > 0:
            memory_percentage = (used_memory / memory_limit) * 100
        else:
            memory_percentage = 0

       

        network_rx = 0
        network_tx = 0

        networks = stats.get('networks', {})

        for interface in networks.values():
            network_rx += interface.get('rx_bytes', 0)
            network_tx += interface.get('tx_bytes', 0)

        network_rx_mb = bytes_to_mb(network_rx)
        network_tx_mb = bytes_to_mb(network_tx)


        pids = stats.get('pids_stats', {}).get('current', 0)
        if pids is None:
            pids = "N/A"


        stats_data = {
            "name": container.name,
            "cpu_percentage": round(cpu_percentage, 2),
            "memory_usage_mb": round(memory_usage_mb, 2),
            "memory_limit_mb": round(memory_limit_mb, 2),
            "memory_percent": round(memory_percentage, 2),
            "network_rx_mb": round(network_rx_mb, 2),
            "network_tx_mb": round(network_tx_mb, 2),
            "pids": pids
        }

        if args.format == "json":
            print(json.dumps(stats_data, indent=4))
        else:
            print(f"--------Stats for {container.name}---------")
            print(f"CPU Usage: {cpu_percentage:.2f} %")
            print(f"Memory Usage: {memory_usage_mb:.2f} MB")
            print(f"Memory Limit: {memory_limit_mb:.2f} MB")
            print(f"Memory: {memory_percentage:.2f} %")
            print(f"Received: {network_rx_mb:.2f} MB")
            print(f"Sent: {network_tx_mb:.2f} MB")    
            print(f"PIDs: {pids}")


        return True

    except docker.errors.NotFound:
        print(f"ERROR: {args.container} was Not Found")
        logging.error(f"Container {args.container} was Not Found")

        return False
    except docker.errors.APIError as e:
        print(f"ERROR: Docker API error: {e}")
        logging.error(f"Docker API error: {e}")

        return False

def exit_status_helper(result):
    if result:
        logging.info("Operation completed successfully.")
        sys.exit(0)
    logging.error("Operation failed!!")
    sys.exit(1)

def main():
    args = get_arguments()

    try:
        client = docker.from_env()

    except docker.errors.DockerException as e:
        print(f"ERROR: Could not connect to Docker: {e}")
        logging.error(f"Could not connect to Docker: {e}")
        sys.exit(1)

    if args.action == "list":
        result = list_containers(client, args)
        exit_status_helper(result)

    elif args.action == "start":    
        result = start_container(client, args)
        exit_status_helper(result)

    elif args.action == "stop":
        result = stop_container(client, args)
        exit_status_helper(result)

    elif args.action == "restart":
        result = restart_container(client, args)
        exit_status_helper(result)

    elif args.action == "logs":
        logs = container_logs(client, args)

        if logs is not None:
            print(f"------ Logs for {args.container} ------")
            print(logs)
            sys.exit(0)
        else:
            print("Failed to retrieve logs.")
            sys.exit(1)

    elif args.action == "remove":
        result = remove_container(client, args)
        exit_status_helper(result)

    elif args.action == "inspect":
        result = inspect_container(client, args)
        exit_status_helper(result)

    elif args.action == "stats":
        result = container_stats(client, args)
        exit_status_helper(result)

if __name__ == "__main__":
    main()