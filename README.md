## docker-anomalies
Identify intrusion attempts in processes running inside docker containers using anomaly detection.

## Architecture
`docker-anomalies` is a process that runs on the same box as your `docker` daemon and monitors it's events. When an event indicates that a new container is started `docker-anomalies` queries the daemon to find the process IDs which are running inside the container.

Using the process IDs, root privileges, and `ptrace, `docker-anomalies` captures the syscalls from all container processes and sends them to a Redis queue (serialized using msgpack).

The event anomaly detection analyzes the process behaviour and if necessary sends an email to the admins.

![docker anomaly detection](https://cloud.githubusercontent.com/assets/865200/10103473/90577d44-637a-11e5-95e1-6657678090ef.png)

## Testing the code
TBD

## Disclaimer
This code is alpha state, we just wanted to explore Docker REST API and `ptrace`. No performance/load testing was done and the anomaly detection engine is very basic.

## Contributors
[Andrés Riancho](https://github.com/jpcenteno)
[Joaquín P. Centeno](https://github.com/jpcenteno)