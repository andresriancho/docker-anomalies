import sys
import logging

from docker_anomalies.event_consumer import monitor_event_stream
from docker_anomalies.log_handler import configure_logging
from docker_anomalies.start_redis import start_redis, stop_redis


def main():
    configure_logging()

    try:
        container_id, redis_port = start_redis()
    except Exception, e:
        logging.error('%s' % e)
        return 1

    try:
        monitor_event_stream(redis_port)
    except KeyboardInterrupt:
        return 0
    except Exception, e:
        raise
        logging.error('%s' % e)
        return 1
    finally:
        stop_redis(container_id)

    return 0

if __name__ == '__main__':
    sys.exit(main())