

from rules import Rules

import argparse
import sys
import yaml



if __name__=="__main__":

    parser = argparse.ArgumentParser(
        description="Docker anomaly detection."
    )
    parser.add_argument(
        '--conf',
        type=str,
        help='A yaml file with the monitor settings.'
    )
    args = parser.parse_args()
    
    
    # Open the conf file.
    try:
        conf = yaml.load(open(args.conf))
    except IOError:
        sys.stderr.write('Error: configuration file does not exist.')
        sys.stderr.write(IOError)
        exit(1)
    
    rules = Rules(conf['rules'])
    print rules.ruleset
        

    
    
        
        
