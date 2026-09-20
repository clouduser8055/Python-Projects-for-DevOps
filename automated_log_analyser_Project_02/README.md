# Automated Log Analyzer

A Python-based log analysis tool that reads web-server access logs,
extracts useful information, analyzes errors and requests, and generates
a JSON report.

## Features

- Count total log entries
- Analyze successful requests (2xx)
- Analyze client errors (4xx)
- Analyze server errors (5xx)
- Find top IP addresses
- Find the most common error codes
- Analyze HTTP methods
- Find the most requested URLs
- Find IP addresses generating the most errors
- Export analysis results to JSON
- Accept input/output files through command-line arguments
- Handle missing files gracefully
- Skip malformed log entries

## Project Structure

```text
automated-log-analyzer/
├── log_analyzer.py
├── sample.log
├── log_report.json
├── README.md
└── .gitignore 
```

## Requirements
- Python 3
- No external Python packages required

The project uses Python's built-in modules:

- collections.Counter
- json
- argparse

## Usage
Run with default files
```bash
python log_analyzer.py
```

### This uses:
```bash
Input  : sample.log
Output : log_report.json
```
### Specify a custom input file
```bash
python log_analyzer.py --file production.log
```

### Specify a custom output file
```bash
python log_analyzer.py --file production.log --output report.json
```

## Example Output
```text
========== LOG ANALYZER ==========

Log Count : 15

Successful : 9
Client Error : 5
Server Error : 2

Top IP Addresses:
192.168.1.10 -> 6 requests
10.0.0.5 -> 3 requests

Most Common Errors:
404 -> 2
401 -> 2
500 -> 2

HTTP Methods:
GET -> 13 requests
POST -> 2 requests

Most Requested URLs:
/index.html -> 2 requests
/login -> 2 requests
/dashboard -> 2 requests

IPs With Most Errors:
10.0.0.5 -> 3 errors
192.168.1.12 -> 2 errors

Report saved to log_report.json

```

## JSON Report
The analyzer generates a JSON report containing information such as:
```json
{
    "total_logs": 15,
    "successful_requests": 9,
    "client_errors": 5,
    "server_errors": 2
}
```
The report can be consumed by other scripts, automation tools, APIs,
or monitoring systems.