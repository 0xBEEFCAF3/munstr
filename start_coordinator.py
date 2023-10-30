#!/usr/bin/env python3
from src.coordinator.coordinator import run

import argparse

def main(show:bool, relays=None):
    run(show, relays)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-s", "--show", help="Display active relays", default=False, action='store_true')
    parser.add_argument("-a", "--add", help="Add new relays before running", default=None, nargs="+")
    args = parser.parse_args()

    main(args.show, args.add)
