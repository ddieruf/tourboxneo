import logging
import toml

from .commands import library

logger = logging.getLogger(__name__)


class Config:

    def __init__(self, f):
        logger.info('reading %s', f.name)

        data = toml.loads(f.read())

        self.name = data['name']
        self.layouts = data['layouts']

        if self.name is None:
            raise RuntimeError('no name')
        if self.layouts is None:
            raise RuntimeError('no layouts')
        if self.layouts['main'] is None:
            raise RuntimeError('no main layout')

        for l_name, layout in self.layouts.items():
            for s_name, section in layout.items():
                for key, cmd_str in section.items():
                    section[key] = library.lookup(cmd_str)

        logger.info('loaded %s', f.name)
