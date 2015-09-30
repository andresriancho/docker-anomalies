import sys
import logging
import argparse

from docker_anomalies.event_consumer import monitor_event_stream
from docker_anomalies.log_handler import configure_logging
from docker_anomalies.start_redis import start_redis, stop_redis


def cli():
    parser = argparse.ArgumentParser()

    parser.add_argument('-v', '--verbose',
                        action='store_true',
                        help='Turn on the verbose output.')

    parser.add_argument('--redis_docker_repo',
                        default='redis',
                        nargs=1,
                        help='''
Set the Docker repository for the Redis image that will be used as the
message queue.
''')

    parser.add_argument('--redis_docker_tag',
                        default='2.8.22',
                        nargs=1,
                        help='''
Set the tag of the docker container that will be used as the message
queue.
''')

    return parser.parse_args()


def main():

    args = cli()

    configure_logging(verbose=args.verbose)

    try:
        container_id, redis_port = start_redis(
            repository=args.redis_repo[0],
            tag=args.redis_docker_tag[0]
        )
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
