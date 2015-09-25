import sys
import json
import logging

from docker import Client
from docker_anomalies.process_monitor import container_monitor


def event_stream(images=['redis1', ]):
    """
    Read events from docker's event stream and call the container monitor
    """
    client = Client(base_url='unix://var/run/docker.sock')

    logging.info('Listening for docker events...')

    try:
        for event in client.events():
            event = json.loads(event)
            container_monitor(event)
    except KeyboardInterrupt:
        sys.exit(0)