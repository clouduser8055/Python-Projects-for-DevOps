from collections import Counter

def read_file(file):
    with open(file, "r") as f:
        lines = f.readlines()
    return lines

def count_lines(lines):
    count = 0
    for l in lines:
        count += 1
    return count

def status_codes(content):
    status_list = []
    for s in content:
        gg = s.split()
        status_list.append(int(gg[8]))
    return status_list

def ip_address(content):
    ip_list = []
    for s in content:
        gg = s.split()
        ip_list.append(gg[0])
    return ip_list

def methods_urls(cont):
    method_list = []
    for m in cont:
        parts = m.split()
        methods = parts[5].replace('"', '')
        urls = parts[6]
        method_list.append({
            "method" : methods,
            "urls" : urls
        })
    return method_list

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

def error_ips(content):
    error_list = []
    for c in content:
        parts = c.split()
        ips = parts[0]
        status = int(parts[8])

        if status >= 400:
            error_list.append(ips)
            
    return error_list

def main():
    print("==========LOG ANALYZER==========")
    content = read_file("sample.log")
    print(f"Total Logs : {count_lines(content)}")

    counts = error(status_codes(content))
    print(f"Successful : {counts[0]}")
    print(f"Client Error : {counts[1]}")
    print(f"Server Error : {counts[2]}")

    ip = ip_address(content)
    print("\nTop IP Addresses: ")
    for ip, count in Counter(ip).most_common(2):
        print(f"{ip} -> {count}")


    codes = status_codes(content)
    error_codes = [code for code in codes if code >= 400]
    print("\nMost Common Errors: ")
    for errors, code_count in Counter(error_codes).most_common(3):
        print(f"{errors} -> {code_count}")

    print("\n=========HTTP REQUESTS==========")
    requests = methods_urls(content)
    method_list = []
    url_list = []
    for r in requests:
        method_list.append(r["method"])
        url_list.append(r["urls"])
    print("\n========HTTP Methods========")
    for method, count in Counter(method_list).items():
        print(f"{method} -> {count} requests")

    print("\n========Most Requested URLs========")
    for url, count in Counter(url_list).most_common(5):
        print(f"{url} -> {count} requests")

    print("\n========IPs With Most Errors=========")
    err_ips = error_ips(content)
    for ip, count in Counter(err_ips).items():
        print(f"{ip} -> {count} errors")



if __name__ == "__main__":
    main()

