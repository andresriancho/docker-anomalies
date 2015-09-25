import msgpack
import redis


def queue_syscall(container_id, process_id, syscall, redis_port):
    """
    :param syscall: Send the syscall to the queue
    :return: None
    """
    arguments = []

    for argument in syscall.arguments:
        arg_data = {'name': argument.name,
                    'type': argument.type,
                    'value': argument.value}
        arguments.append(arg_data)

    data = {'arguments': arguments,
            'name': syscall.name,
            'container_id': container_id,
            'process_id': process_id}

    r = redis.StrictRedis(host='localhost', port=redis_port, db=0)
    r.publish('docker-anomalies', msgpack.dumps(data))
