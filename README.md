# Linux System Monitor

A Python-based system monitoring tool that checks CPU, memory, disk usage,
and running processes. It generates warnings when configured resource
thresholds are exceeded and records monitoring events in a log file.

## Features

- Monitor CPU usage
- Monitor memory usage
- Monitor disk usage
- Display top CPU-consuming processes
- Configurable CPU, memory, and disk thresholds
- Warning messages for high resource usage
- System health status
- Logging to a file
- Command-line arguments

## Requirements

- Python 3
- psutil

## Installation

Clone the repository:

```bash
git clone <your-repository-url>
cd linux-system-monitor```

Install the dependency:

pip install psutil

Usage:

Run with default thresholds:

python system_monitor.py

Run with custom thresholds:

python system_monitor.py --cpu 80 --memory 75 --disk 90

Example:

    ======= SYSTEM MONITOR =======
    CPU usage is    : 7.4%
    Memory usage is : 59.4%
    Disk usage is   : 35.4%

    ======== RUNNING PROCESSES ========
    PID : 4 | NAME : System | CPU : 0.0%
    PID : 256 | NAME : Registry | CPU : 0.0%

    ========= THRESHOLDS =========
    CPU threshold    : 5.0%
    Memory threshold : 50.0%
    Disk threshold   : 30.0%

    Warning: CPU usage is high
    Warning: Memory usage is high
    Warning: Disk usage is high

    System status: Unhealthy