#! /usr/bin/env python

from rule_book import RuleBook

import argparse
import sys


def parse_args():
    '''
    Define the CLI and parse the arguments.
    '''

    parser = argparse.ArgumentParser(
        description="Docker anomaly detection."
    )

    parser.add_argument(
        '--rules',
        type=str,
        required=True,
        help='A yaml file containing the monitor rules.'
    )

    return parser.parse_args()


if __name__ == "__main__":

    args = parse_args()

    rule_book = RuleBook(args.rules)

    # Get a map of filters, each loaded with the user-defined rules.
    data_filters = rule_book.filters

    # TODO: Now it should initialize the data collectors.
