from collections import Counter
import json
import argparse

def get_arguments():
    parser = argparse.ArgumentParser(
        description="Taking log file and Creating JSON Report file"
    )
    parser.add_argument(
        "--file",
        default="sample.log",
        help="Input file"
    )

    parser.add_argument(
        "--output",
        default="log_report.json",
        help="Output file"
    )

    return parser.parse_args()

def save_report(report, filename):
    with open(filename, "w") as file:
        json.dump(report, file, indent=4)

def read_file(file):
    try:
        with open(file, "r") as f:
            lines = f.readlines()

        return lines
    except FileNotFoundError:
        print(f"Error : file \'{file}\' was not found!")
        return None
    except PermissionError:
        print(f"Error : Permission denied for file \'{file}\'")
        return None

def count_lines(lines):
    count = 0
    for l in lines:
        count += 1

    return count

def parse_log_line(line):
    try:
        parts = line.split()

        if len(parts)<9:
            return None

        ip = parts[0]
        method = parts[5].replace('"', '')
        url = parts[8]
        status = int(parts[8])

        return {
            "ip" : ip,
            "method" : method,
            "url" : url, 
            "status" : status
        }
    except (IndexError, ValueError):
        return None

def analyze_logs(content):
    parsed_logs = []

    for line in content:
        parsed = parse_log_line(line)

        if parsed is not None:
            parsed_logs.append(parsed)

    return parsed_logs

def status_codes(parsed_logs):
    return [log["status"] for log in parsed_logs]

def ip_address(parsed_logs):
    return [log["ip"] for log in parsed_logs]  

def methods_urls(parsed_logs):
    return[{
        "method" : log["method"],
        "urls" : log["url"]
        }
        for log in parsed_logs
    ]

def error_ips(parsed_logs):
    errors = [
        log["ip"]
        for log in parsed_logs
        if log["status"] >= 400
    ]
    return Counter(errors)

def error(lines):
    success = 0
    client_errors = 0
    server_errors = 0
    for item in lines:
        if 200 <= item < 300:
            success += 1
        elif 400 <= item < 500:
            client_errors += 1
        elif   500 <= item < 600:
            server_errors += 1
        else:
            continue
    return success, client_errors, server_errors


def all_ips(content):
    ips_list = []
    for i, c in Counter(content).items():
        ips_list.append({
            "ip" : i,
            "count" : c
        })
    l2 = []
    for f in ips_list:
        l1 = f"{f["ip"]} : {f["count"]}"
        l2.append(l1)

    return l2

def main():
    args = get_arguments()

    print("==========LOG ANALYZER==========")
    content = read_file(args.file)
    parsed_logs = analyze_logs(content)
    if content is None:
        return
    print(f"Total Logs : {count_lines(content)}")

    counts = error(status_codes(parsed_logs))
    print(f"Successful : {counts[0]}")
    print(f"Client Error : {counts[1]}")
    print(f"Server Error : {counts[2]}")

    ip = ip_address(parsed_logs)
    print("\nTop IP Addresses: ")
    for ip, count in Counter(ip).most_common(2):
        print(f"{ip} -> {count}")

    codes = status_codes(parsed_logs)
    status_code = [code for code in codes]
    error_codes = [code for code in codes if code >= 400]
    print("\nMost Common Errors: ")
    for errors, code_count in Counter(error_codes).most_common(3):
        print(f"{errors} -> {code_count}")

    print("\n=========HTTP REQUESTS==========")
    requests = methods_urls(parsed_logs)
    method_list = []
    url_list = []
    for r in requests:
        # print(f"Method : {r["method"]} | URL : {r["urls"]}")
        method_list.append(r["method"])
        url_list.append(r["urls"])

    print("\n========HTTP Methods========")
    for method, count in Counter(method_list).items():
        method_counts = f"{method} -> {count} requests"
        print(method_counts)

    new_list = []
    new_list2 = []
    for m, c in Counter(method_list).items():
        new_list.append({
            "method" : m,
            "count" : c
        })
    for n in new_list:
        new_list2.append(f"{n["method"]} : {n["count"]}")

    print("\n========Most Requested URLs========")
    for url, count in Counter(url_list).most_common(5):
        url_counts = f"{url} -> {count} requests"
        print(url_counts)

    print("\n========IPs With Most Errors=========")
    err_ips = error_ips(parsed_logs)
    for ip, count in Counter(err_ips).items():
        error_ip_counts = f"{ip} -> {count} errors"
        print(error_ip_counts)

    ip_add = ip_address(parsed_logs)
    ips = all_ips(ip_add)
    
    report = {
        "total_logs": count_lines(content),
        "successful_requests": counts[0],
        "client_errors": counts[1],
        "server_errors": counts[2],
        "top_ips": ips,
        "status_codes": dict(Counter(status_code)),
        "http_methods": new_list2,
        # "top_urls": dict(url_counts),
        # "error_ips": dict(error_ip_counts)
    }

    save_report(report, args.output)

    print("\nReport saved to log_report.json")


if __name__ == "__main__":
    main()

