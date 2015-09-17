

from rules import Rules

import argparse
import sys
import yaml

def load_rulebook(path):
    '''
    Load a rulebook file.
    '''
    
    try:
        rules = yaml.load(open(path))
    except IOError:
        # TODO -> Wrap it arround the log_handler
        sys.stderr.write('Error: Rulebook file does not exist\n.')
        sys.stderr.write(IOError)
        exit(1)
    
    return rules


def parse_args(args=sys.argv):
    '''
    Define the CLI and parse the arguments.
    '''
    
    
    parser = argparse.ArgumentParser(
        description="Docker anomaly detection."
    )
    
    
    parser.add_argument(
        '-r', '--rules',
        type=str,
        required=True,
        help='A yaml file containing the monitor rules.'
    )
    
    
    return parser.parse_args(argv)


if __name__=="__main__":
    
    
    args = parse_args(raw)
    
    rulebook = load_rulebook(args.rules)
    
    rules = Rules(rulebook)
    
        

    
    
        
        
