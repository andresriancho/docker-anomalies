import socket
import logging
import time

import docker
import docker.utils
import port_for

REDIS_REPO = 'redis'
REDIS_IMAGE_TAG = '2.8.22'
REDIS_IMAGE = '{}:{}'.format(REDIS_REPO, REDIS_IMAGE_TAG)
DEFAULT_REDIS_PORT = 6379


def download_image_if_missing(docker_client):
    """
    Ensures that the needed Redis Docker image is present.
    """
    redis_images = docker_client.images(name=REDIS_REPO)
    proper_image_exists = bool(
        [image for image in redis_images if REDIS_IMAGE in image['RepoTags']])
    if not proper_image_exists:
        logging.debug('Pulling redis image...')
        docker_client.pull(repository=REDIS_REPO, tag=REDIS_IMAGE_TAG)


def start_redis_container(docker_client):
    """
    Start a Redis Docker container.
    """
    logging.debug('Starting redis container')
    redis_port = port_for.select_random()
    host_config = docker.utils.create_host_config(port_bindings={
        DEFAULT_REDIS_PORT: redis_port,
    })

    container_id = docker_client.create_container(
        REDIS_IMAGE,
        host_config=host_config
    )['Id']

    docker_client.start(container_id)

    logging.info('Waiting for Redis to start...')
    success = False

    for _ in xrange(60):
        time.sleep(1)

        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            s.connect(('localhost', redis_port))
        except:
            continue
        else:
            s.close()
            success = True
            break

    if not success:
        raise Exception('Failed to start redis daemon inside docker container')

    return container_id, redis_port


def start_redis():
    """
    Start a Docker container with a Redis instance to be used as the
    event queue.
    """
    docker_client = docker.Client(version='auto')
    download_image_if_missing(docker_client)
    container_id, redis_port = start_redis_container(docker_client)
    return container_id, redis_port


def stop_redis(container_id):
    """
    Stop the container used for the event queue.
    """
    docker_client = docker.Client(version='auto')
    docker_client.remove_container(container_id, force=True)
