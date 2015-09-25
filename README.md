## docker-anomalies
Identify intrusion attempts in processes running inside docker containers using
anomaly detection.

## Installation
We recommend you install `docker-anomalies` inside a `virtualenv`:

```bash
sudo pip install --upgrade virtualenv
git clone git@github.com:andresriancho/docker-anomalies.git
cd docker-anomalies
virtualenv venv
. venv/bin/activate
pip install -r requirements.txt
```

## Detecting anomalies

In one console start the anomaly detection engine:
```console
$ sudo -s -H
$ . venv/bin/activate
$ python docker-anomalies.py
Listening for docker events...
```

In a second console run a docker container:
```console
$ docker run -it ubuntu /bin/bash
root@9957e6a9ceea:/# ls
...
```

In the first console you'll now see something like:
```text
Listening for docker events...
Monitoring container: 9957e6a
Monitoring process ID: 10410
New process ID detected 10410 detected in container 9957e6a
Attach process 10410
Attach process 10410
{'arguments': [{'type': 'int', 'name': 'fd', 'value': 0L}, ... 'name': 'read'}
{'arguments': [{'type': 'int', 'name': 'fd', 'value': 2L}, ... 'name': 'write'}
```

The last two lines are the captured process syscalls, which are serialized and
sent to the Redis queue for processing.

When the process or container finishes you'll see:
```
Finished monitoring process ID: 10410
Finished monitoring container: 9957e6a
```

## Architecture
`docker-anomalies` is a process that runs on the same box as your `docker` daemon
and monitors it's events. When an event indicates that a new container is started
`docker-anomalies` queries the daemon to find the process IDs which are running
inside the container.

Using the process IDs, root privileges, and `ptrace, `docker-anomalies` captures
the syscalls from all container processes and sends them to a Redis queue
(serialized using msgpack).

The event anomaly detection analyzes the process behaviour and if necessary
sends an email to the admins.

![docker anomaly detection](https://cloud.githubusercontent.com/assets/865200/10103473/90577d44-637a-11e5-95e1-6657678090ef.png)

## Disclaimer
This code is alpha state, we just wanted to explore Docker REST API and `ptrace`.
No performance/load testing was done and the anomaly detection engine is very basic.

## Project leaders
[Andrés Riancho](https://github.com/jpcenteno)

[Joaquín P. Centeno](https://github.com/jpcenteno)