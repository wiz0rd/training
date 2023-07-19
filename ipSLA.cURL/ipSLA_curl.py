import subprocess
import time
from prometheus_client import start_http_server, Gauge

# Define the Metrics
NAME_LOOKUP_TIME = Gauge('curl_namelookup_time_seconds', 'Time spent in name lookup.')
CONNECT_TIME = Gauge('curl_connect_time_seconds', 'Time spent in connection.')
APP_CONNECT_TIME = Gauge('curl_appconnect_time_seconds', 'Time spent in app connection.')
PRETRANSFER_TIME = Gauge('curl_pretransfer_time_seconds', 'Time spent in pretransfer.')
STARTTRANSFER_TIME = Gauge('curl_starttransfer_time_seconds', 'Time spent in starttransfer.')
TOTAL_TIME = Gauge('curl_total_time_seconds', 'Total time spent in request.')

def measure(url):
    # Execute curl command
    curl_cmd = 'curl -s -w "%{time_namelookup},%{time_connect},%{time_appconnect},%{time_pretransfer},%{time_starttransfer},%{time_total}" -o /dev/null ' + url
    output = subprocess.check_output(curl_cmd, shell=True).decode('utf-8')

    # Parse curl output
    time_namelookup, time_connect, time_appconnect, time_pretransfer, time_starttransfer, time_total = map(float, output.split(','))

    # Export metrics
    NAME_LOOKUP_TIME.set(time_namelookup)
    CONNECT_TIME.set(time_connect)
    APP_CONNECT_TIME.set(time_appconnect)
    PRETRANSFER_TIME.set(time_pretransfer)
    STARTTRANSFER_TIME.set(time_starttransfer)
    TOTAL_TIME.set(time_total)

if __name__ == "__main__":
    # Start up the server to expose the metrics.
    start_http_server(8001)
    
    # measure every second
    while True:
        measure('http://www.cnn.com')
        time.sleep(20)
