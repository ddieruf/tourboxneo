import logging
import toml
from pathlib import Path

from .commands import library

logger = logging.getLogger(__name__)


class Config:

    def __init__(self, config_path):
        if config_path is None:
            config_path = Path.home() / '.tourboxneo'
        if not config_path.exists():
            logger.info('falling back on default configuration')
            config_path = Path(__file__).with_name('default.toml')
        if not config_path.exists():
            raise RuntimeError('No default configuration available')

        logger.info('reading %s', config_path.name)

        with config_path.open('r') as config:
            data = toml.loads(config.read())

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

        logger.info('loaded %s', config_path.name)

