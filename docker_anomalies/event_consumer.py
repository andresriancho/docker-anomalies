import json

from docker import Client
from docker_anomalies.process_monitor import container_monitor


def event_stream(images=['redis1', ]):
    """

    """
    client = Client(base_url='unix://var/run/docker.sock')

    for event in client.events():
        event = json.loads(event)
        container_monitor(event)