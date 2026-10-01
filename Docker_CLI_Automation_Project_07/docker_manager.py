import docker
import argparse
import logging

logging.basicConfig(
    filename="docker_manager.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

def get_arguments():
    parser = argparse.ArgumentParser(description="Docker CLI commands for automation")

    parser.add_argument(
        "action",
        choices=["list", "start", "stop", "restart", "logs"],
        help="To list containers"
    )
    parser.add_argument(
        "--container",
        help="Target container name and id"
    )

    return parser.parse_args()

client = docker.from_env()
args = get_arguments()

if args.action == "list":
    print("Listing Containers.....")
    logging.info("Listing Containers.....")
    try:
        containers = client.containers.list(all=True)
        for container in containers:
            print(f"Container: {container.name} | Status: {container.status}")

    except Exception as e:
        print(f"ERROR: {e}")
        logging.error(e)

elif args.action == "start":
    if not args.container:
        print("No container is specified")
        exit()

    print(f"Starting {args.container} container......")
    logging.info(f"Starting {args.container} container......")

    try:
        container = client.containers.get(args.container)
        container.start()
        print(f"Container {args.container} is successfully started.")
        logging.info(f"Container {args.container} is successfully started.")

    except docker.errors.NotFound as e:
        print(f"ERROR: Container Not Found")
        logging.error(e)

    except Exception as e:
        print(f"ERROR: {e}")
        logging.error(e)

elif args.action == "stop":
    if not args.container:
        print("No container is specified")
        exit()

    print(f"Stopping {args.container} container......")
    logging.info(f"Stopping {args.container} container......")

    try:    
        container = client.containers.get(args.container)
        container.stop()
        print(f"Container {args.container} is successfully stopped.")
        logging.info(f"Container {args.container} is successfully stopped.")

    except docker.errors.NotFound as e:
            print(f"ERROR: Container Not Found")
            logging.error(e)

    except Exception as e:
        print(f"ERROR: {e}")
        logging.error(e)

elif args.action == "restart":
    if not args.container:
        print("No container is specified")
        exit()

    print(f"Restarting {args.container} container......")
    logging.info(f"Restarting {args.container} container......")

    try:    
        container = client.containers.get(args.container)
        container.restart()
        print(f"Container {args.container} is successfully restarted.")
        logging.info(f"Container {args.container} is successfully restarted.")

    except docker.errors.NotFound as e:
            print(f"ERROR: Container Not Found")
            logging.error(e)

    except Exception as e:
        print(f"ERROR: {e}")
        logging.error(e)

elif args.action == "logs":
    if not args.container:
        print("No container is specified")
        exit()

    print(f"logging {args.container} container......")
    logging.info(f"logging {args.container} container......")

    try:    
        container = client.containers.get(args.container)
        logs = container.logs().decode('utf-8')
        print(f"-------Logs for {args.container} -----\n{logs}")
        logging.info(f"----- Logs for {args.container} -----\n{logs}")

    except docker.errors.NotFound as e:
            print(f"ERROR: Container Not Found")
            logging.error(e)

    except Exception as e:
        print(f"ERROR: {e}")
        logging.error(e)

