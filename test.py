from docker_anomalies.event_consumer import event_stream
from docker_anomalies.log_handler import configure_logging

configure_logging()

event_stream()
