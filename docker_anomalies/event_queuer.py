import msgpack


def queue_syscall(syscall):
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
            'name': syscall.name}
    print data