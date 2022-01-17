import argparse
import logging
import signal
import sys
import os
import pathlib

from .config import *
from .reader import *
from .writer import *

logger = logging.getLogger(__name__)

exiting = False


def exit_gracefully(self, *args):
    exiting = True


def main():
    parser = argparse.ArgumentParser(prog='tourboxneo',
                                     description='TourBox NEO Service')
    parser.add_argument('config',
                        type=argparse.FileType('r'),
                        help='TOML-formatted definitions file')

    args = parser.parse_args()

    config = Config(args.config)

    # pid file
    pidfile = os.getenv('pidfile') or "tourbox.pid"
    p = pathlib.Path(pidfile)
    p.write_text(str(os.getpid()))

    # signals
    signal.signal(signal.SIGINT, exit_gracefully)
    signal.signal(signal.SIGTERM, exit_gracefully)

    with Reader(dev_path=sys.argv[1]) as reader, Writer(config) as writer:
        while not exiting:
            btn = reader.tick()
            writer.process(btn)
        logger.debug('Exiting Tourbox Daemon')


if __name__ == '__main__':
    main()
