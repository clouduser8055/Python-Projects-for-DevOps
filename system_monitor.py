import psutil
import logging
import argparse

def configure_logging():
    logging.basicConfig(
        filename="system_monitor.log",
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(message)s"
    )

def get_arguments():
    parser = argparse.ArgumentParser(
        description="Monitor CPU, memory, disk, and running processes."
    )
    parser.add_argument(
        "--cpu",
        type=float,
        default=80,
        help="CPU Usage Threshold"
    )
    parser.add_argument(
        "--memory",
        type=float,
        default=80,
        help="MEMORY Usage Threshold"
    )
    parser.add_argument(
        "--disk",
        type=float,
        default=80,
        help="DISK Usage Threshold"
    )

    return parser.parse_args()

def get_system_metrics():
    cpu_usage = psutil.cpu_percent(interval=1)
    memory_usage = psutil.virtual_memory().percent
    disk_usage = psutil.disk_usage("/").percent

    return cpu_usage, memory_usage, disk_usage

def get_top_processes(limit=5):
    processes = []

    for process in psutil.process_iter(["pid", "name", "cpu_percent"]):
        try:
            pid = process.info["pid"]
            name = process.info["name"]

            if not name or name == "System Idle Process":
                continue

            cpu = process.cpu_percent(interval=0.2)

            processes.append({
                "pid" : pid,
                "name" : name,
                "cpu" : cpu
            })
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            pass

    processes.sort(key=lambda process:process["cpu"], reverse=True)

    return processes[:limit]


def check_health(cpu_usage, memory_usage, disk_usage, args):
    if cpu_usage > args.cpu:
        print("Warning: CPU usage is high")
        logging.warning(f"CPU usage is high : {cpu_usage}%")

    if memory_usage > args.memory:
        print("Warning: Memory usage is high")
        logging.warning(f"MEMORY usage is high : {memory_usage}%")

    if disk_usage > args.disk:
        print("Warning: Disk usage is high")
        logging.warning(f"DISK usage is high : {disk_usage}%")

    if (cpu_usage > args.cpu
        or memory_usage > args.memory
        or disk_usage > args.disk):
        print("\nSystem status : Unhealthy")
        logging.error("System status : Unhealthy")
    else:
        print("\nSystem status : Healthy")
        logging.info("System status : Healthy")

def main():
    configure_logging()
    args = get_arguments()

    cpu_usage, memory_usage, disk_usage = get_system_metrics()

    print("=======system monitor=======")
    print(f"CPU usage is : {cpu_usage} %")
    print(f"MEMORY usage is : {memory_usage} %")
    print(f"DISK usage is : {disk_usage} %")

    print("\n========running processes=======")

    processes = get_top_processes()

    for process in processes[:5]:
        print(
            f"PID : {process['pid']} | "
            f"NAME : {process['name']} | "
            f"CPU : {process['cpu']}%"
        )

    print("\n=========THRESHOLDS=========")
    print(f"CPU Threshold : {args.cpu}%")
    print(f"MEMORY Threshold : {args.memory}%")
    print(f"DISK Threshold : {args.disk}%\n")

    logging.info(
        f"CPU = {cpu_usage}% | "
        f"MEMORY = {memory_usage}% | "
        f"DISK = {disk_usage}%"
    )

    check_health(
        cpu_usage,
        memory_usage,
        disk_usage,
        args
    )

if __name__ == "__main__":
    main()