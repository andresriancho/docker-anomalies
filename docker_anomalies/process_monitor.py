import threading
import logging
import time

from docker import Client


CONTAINER_MONITORS = []
PROCESS_MONITORS = []
CONTAINER_MONITOR_TIMEOUT = 1


def container_monitor(event):
    """
    Receives a container event and starts/stops monitoring the processes
    started inside that container.

    Since the active container processes might change (new are created, some
    die) we need create a thread to monitor the container every N seconds.

    :param event: The docker event as received from the API
    """
    container_id = event['id']
    event_action = event['status']

    if event_action == 'start':
        thread = ContainerMonitorThread(container_id)
        thread.start()

        CONTAINER_MONITORS.append(thread)

    elif event_action == 'die':
        for monitor in CONTAINER_MONITORS:
            if monitor.container_id == container_id:
                monitor.should_run = False
                CONTAINER_MONITORS.remove(monitor)


class ContainerMonitorThread(threading.Thread):
    def __init__(self, container_id):
        self.container_id = container_id
        self.should_run = True
        self.client = Client(base_url='unix://var/run/docker.sock')
        super(ContainerMonitorThread, self).__init__(name='ContainerMonitor')

    def run(self):
        logging.info('Monitoring container: %s' % self.container_id[:7])

        while self.should_run:
            # >>> cli.top('sleeper')
            # {'Processes': [['952', 'root', '/bin/sleep 30']],
            #  'Titles': ['PID', 'USER', 'COMMAND']}
            container_top = self.client.top(self.container_id)

            for process_data in container_top['Processes']:
                pid = int(process_data[0])
                already_monitored = False

                for process_monitor_thread in PROCESS_MONITORS:
                    if process_monitor_thread.pid == pid:
                        already_monitored = True
                        break

                if not already_monitored:
                    process_monitor(pid)

                    msg = 'New process ID detected %s detected in container %s'
                    logging.info(msg % (pid, self.container_id[:7]))

            time.sleep(CONTAINER_MONITOR_TIMEOUT)

        logging.info('Finished monitoring container: %s' % self.container_id[:7])


class ProcessMonitorThread(threading.Thread):
    def __init__(self, process_id):
        self.process_id = process_id
        self.should_run = True
        super(ProcessMonitorThread, self).__init__(name='ProcessMonitor')

    def run(self):
        logging.info('Monitoring process ID: %s' % self.process_id)

        while self.should_run:
            raise NotImplementedError

    def cleanup(self):
        PROCESS_MONITORS.remove(self)
        logging.info('Finished monitoring process ID: %s' % self.process_id)


def process_monitor(pid):
    """
    Starts monitoring a process which is running inside a container and
    sends the events to the queue for anomaly detection engine to consume

    :param pid: The process ID to monitor
    """
    thread = ProcessMonitorThread(pid)
    thread.start()

    PROCESS_MONITORS.append(thread)
