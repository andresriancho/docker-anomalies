from docker import Client

import process_monitor

def event_stream(client, images=['redis1', ]):
    """
    
    """
    for event in  client.events():
        pass
    
