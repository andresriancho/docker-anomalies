import threading
import logging
import optparse
import time

from docker import Client
from docker_anomalies.ptrace_wrapper import SyscallTracer
from docker_anomalies.event_queuer import queue_syscall

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
        thread.daemon = True
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

            if container_top is None:
                time.sleep(CONTAINER_MONITOR_TIMEOUT)
                continue

            for process_data in container_top['Processes']:
                pid = int(process_data[1])
                already_monitored = False

                for process_monitor_thread in PROCESS_MONITORS:
                    if process_monitor_thread.process_id == pid:
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
        self.debugger = None
        super(ProcessMonitorThread, self).__init__(name='ProcessMonitor')

    def run(self):
        logging.info('Monitoring process ID: %s' % self.process_id)

        self.debugger = SyscallTracer(options=optparse.Values({
                                          'fork': False,
                                          'enter': False,
                                          'show_ip': False,
                                          'trace_exec': True,
                                          'no_stdout': False,
                                          'pid': self.process_id,
                                          'show_pid': True,
                                      }),
                                      program=None,
                                      ignore_syscall_callback=self.ignore_syscall_callback,
                                      syscall_callback=self.syscall_callback,
                                      event_callback=self.event_callback,
                                      quit_callback=self.quit_callback)
        self.debugger.main()

    def syscall_callback(self, syscall):
        queue_syscall(syscall)

    def ignore_syscall_callback(self, *args):
        # TODO: Smarter decision here, we only want some of the syscalls
        #       sent to the queue/anomaly detection engine
        return False

    def event_callback(self, *args):
        pass

    def quit_callback(self):
        try:
            PROCESS_MONITORS.remove(self)
        except ValueError:
            pass
        else:
            logging.info('Finished monitoring process ID: %s' % self.process_id)


def process_monitor(pid):
    """
    Starts monitoring a process which is running inside a container and
    sends the events to the queue for anomaly detection engine to consume

    :param pid: The process ID to monitor
    """
    thread = ProcessMonitorThread(pid)
    thread.daemon = True
    thread.start()

    PROCESS_MONITORS.append(thread)
