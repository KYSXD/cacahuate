#!/usr/bin/env python3
from lib.loop import Loop
from lib.models import bind_models

from coralillo import Engine
from itacate import Config
import time
import os

if __name__ == '__main__':
    # Load the config
    config = Config(os.path.dirname(os.path.realpath(__file__)))
    config.from_pyfile('settings.py')
    config.from_envvar('PVM_SETTINGS', silent=False)

    # Set the timezone
    os.environ['TZ'] = config['TIMEZONE']
    time.tzset()

    # Logging stuff
    if not config['TESTING']:
        from lib.logger import init_logging

        init_logging(config)

    # Load the models
    eng = Engine(
        host = config['REDIS_HOST'],
        port = config['REDIS_PORT'],
        db = config['REDIS_DB'],
    )
    bind_models(eng)

    # start the loop
    loop = Loop(config)
    loop.start()
