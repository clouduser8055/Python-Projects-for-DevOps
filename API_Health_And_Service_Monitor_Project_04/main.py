import requests
import logging
import time

logging.basicConfig(
    filename="api_monitor.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

urls = ["https://api.github.com",
        "https://jsonplaceholder.typicode.com/posts/1",
        "https://httpstat.us/404",
        "https://httpstat.us/500"
    ]

slow_threshold = 0.5
try:
    while True:
        for url in urls:
            try:
                response = requests.get(url, timeout=5)
                time_consumed = round(response.elapsed.total_seconds(), 2)
                if 200 <= response.status_code <= 299:
                    if time_consumed > slow_threshold:
                        status = "SLOW" 
                    else:
                        status = "UP"
                elif response.status_code >= 400:
                    status = "DOWN"
                print(f"{url} - {response.status_code} - {time_consumed}s - {status}")
                logging.info(f"{url} - {response.status_code} - {time_consumed}s - {status}")
            except (requests.exceptions.ConnectionError, requests.exceptions.Timeout):
                status = "DOWN"
                print(f"{status} - Connection failed!!!")
                logging.error(f"{url} - {status} - Connection Failed")

        time.sleep(10)

except KeyboardInterrupt:
    print("Terminal Response is Stopped by the User.")