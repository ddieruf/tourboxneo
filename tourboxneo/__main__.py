import argparse
import logging
import signal
import os
from pathlib import Path

from .config import Config
from .reader import Reader
from .driver import Driver

logger = logging.getLogger('tourboxneo')


class GracefulKiller:
    exiting = False

    def __init__(self):
        signal.signal(signal.SIGINT, self.exit_gracefully)
        signal.signal(signal.SIGTERM, self.exit_gracefully)

    def exit_gracefully(self, *args):
        self.exiting = True


def main():
    killer = GracefulKiller()

    parser = argparse.ArgumentParser(prog='tourboxneo',
                                     description='TourBox NEO Service')
    parser.add_argument('-c',
                        '--config',
                        type=Path,
                        help='TOML-formatted definitions file')
    parser.add_argument('-d',
                        '--device',
                        type=Path,
                        help='device file')
    parser.add_argument('-p',
                        '--pidfile',
                        type=str,
                        default=os.getenv('pidfile', 'tourboxneo.pid'),
                        help='pid file')
    parser.add_argument('-v', '--verbose', action='count', default=0)

    args = parser.parse_args()

    logger.setLevel(30 - (max(args.verbose, 2) * 10))

    config = Config(args.config)

    # pid file
    p = Path(args.pidfile)
    p.write_text(str(os.getpid()))

    with Driver(Reader(args.device), config) as driver:
        while not killer.exiting:
            driver.tick()


if __name__ == '__main__':
    main()
