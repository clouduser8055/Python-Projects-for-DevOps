# Automated Backup Tool

A Python-based DevOps automation tool that creates timestamped ZIP backups,
uploads them to AWS S3, applies backup retention, and automatically cleans
up local backup files.

## Features

- Timestamped ZIP backups
- AWS S3 upload using boto3
- Configurable backup retention
- Automatic deletion of old S3 backups
- Local backup cleanup
- Logging
- Configuration through JSON
- Error handling and validation
- Windows Task Scheduler support

## Architecture

Source Directory
        |
        v
   Python Script
        |
        v
   ZIP Backup
        |
        v
    AWS S3
        |
        v
 Retention Policy
        |
        v
Delete Old Backups
        |
        v
Local Cleanup

## Technologies

- Python
- boto3
- AWS S3
- JSON
- Windows Task Scheduler
- Git/GitHub

## Project Structure

automated-backup-tool/
├── backup.py
├── config.json
├── requirements.txt
├── README.md
├── .gitignore
└── source/

## Installation

Clone the repository:

```bash
git clone <your-repository-url>
cd automated-backup-tool
```

Install dependencies:
```bash
pip install -r requirements.txt
```

Configure AWS credentials using your normal AWS CLI/credential configuration.

## Configuration

Example:
```json
{
    "source": "path/to/source",
    "bucket": "your-s3-bucket",
    "keep": 5
}
```

## Usage
python backup.py

### The tool:

1. Creates a timestamped ZIP backup.
2. Uploads it to S3.
3. Keeps the configured number of recent backups.
4. Deletes older backups.
5. Deletes the local ZIP after successful upload.
6. Records operations in the log.

## Scheduling

The tool can be executed automatically using Windows Task Scheduler.

## Example Output

Source : source
Backup : backups/backup_2026-09-26_11-30-00.zip
Status : SUCCESS
Uploaded : s3://bucket/backups/backup_2026-09-26_11-30-00.zip

## What I Learned

- Python filesystem automation
- Exception handling
- Logging
- JSON configuration
- AWS boto3
- S3 object operations
- Backup retention
- Windows task scheduling
- Git/GitHub project organization