import argparse
import logging
import signal
import os
import pathlib

from .config import Config
from . import Service

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
    parser.add_argument('config',
                        type=argparse.FileType('r'),
                        help='TOML-formatted definitions file')
    parser.add_argument('--device',
                        type=str,
                        default='/dev/ttyACM0',
                        help='device file')
    parser.add_argument('--pidfile',
                        type=str,
                        default=os.getenv('pidfile', 'tourboxneo.pid'),
                        help='pid file')
    parser.add_argument('-v',
                        '--verbose',
                        action='count',
                        default=0)

    args = parser.parse_args()

    logger.setLevel(30 - (max(args.verbose, 2) * 10))

    config = Config.from_file(args.config)

    # pid file
    p = pathlib.Path(args.pidfile)
    p.write_text(str(os.getpid()))

    with Service(config, args.device) as service:
        while not killer.exiting:
            service.tick()


if __name__ == '__main__':
    main()
