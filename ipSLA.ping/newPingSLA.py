import os
import re
import time
import logging
from datetime import datetime
from subprocess import Popen, PIPE
from prometheus_client import start_http_server, Gauge

# Define the hosts to ping
hosts = ['8.8.4.4', '8.8.8.8']

# Set up logging
logging.basicConfig(filename='ping_logs.log', level=logging.INFO, format='%(message)s')

# Instantiate the Gauge metrics with the same name and parameters
ping_status = Gauge('host_ping_status', 'Ping status of the host', ['host'])
rtt_min = Gauge('host_ping_rtt_min', 'Minimum round trip time for the host', ['host'])
rtt_max = Gauge('host_ping_rtt_max', 'Maximum round trip time for the host', ['host'])

def ping_host(host):
    process = Popen(['ping', '-c', '1', host], stdout=PIPE, stderr=PIPE)
    stdout, stderr = process.communicate()
    stdout = stdout.decode()

    if "1 packets transmitted, 1 received" in stdout:
        logging.info(f'{datetime.now().isoformat()} {host} Reachable')
        ping_status.labels(host=host).set(1)  # Update the metric to '1' for reachable
        rtt_values = re.findall("rtt min/avg/max/mdev = (.*)/(.*)/(.*)/(.*) ms", stdout)
        if rtt_values:
            rtt_min_value, _, rtt_max_value, _ = map(float, rtt_values[0])
            rtt_min.labels(host=host).set(rtt_min_value)
            rtt_max.labels(host=host).set(rtt_max_value)
    else:
        logging.info(f'{datetime.now().isoformat()} {host} Unreachable')
        ping_status.labels(host=host).set(0)  # Update the metric to '0' for unreachable
        rtt_min.labels(host=host).set(float('inf'))  # Set to infinity if host is unreachable
        rtt_max.labels(host=host).set(float('inf'))  # Set to infinity if host is unreachable

if __name__ == '__main__':
    # Start the server to expose the metrics.
    start_http_server(8000)

    # Ping hosts and report indefinitely.
    while True:
        for host in hosts:
            ping_host(host)

        # Sleep some time
        time.sleep(1)
