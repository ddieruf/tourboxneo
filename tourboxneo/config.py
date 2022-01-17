import toml
import logging

logger = logging.getLogger(__name__)


class Config:

    def __init__(self, f):
        logger.info(f'reading {f.name}')

        data = toml.loads(f.read())

        self.name = data['name']
        self.layouts = data['layouts']

        if self.name is None:
            raise RuntimeError('no name')
        if self.layouts is None:
            raise RuntimeError('no layouts')
        if self.layouts['main'] is None:
            raise RuntimeError('no main layout')

        logger.info(f'loaded {f.name}')
