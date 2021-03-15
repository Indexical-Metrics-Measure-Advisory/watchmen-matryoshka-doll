import logging
import logging.handlers
import sys


def init():
    logging.getLogger().setLevel(logging.NOTSET)

    # Add stdout handler, with level INFO
    console = logging.StreamHandler(sys.stdout)
    console.setLevel(logging.INFO)
    formatter = logging.Formatter('%(name)-13s: %(levelname)-8s %(message)s')
    console.setFormatter(formatter)
    logging.getLogger().addHandler(console)

    # Add file rotating handler, with level DEBUG
    # rotating_handler = logging.handlers.RotatingFileHandler(filename='temp/rotating.log', maxBytes=10242880,
    #                                                         backupCount=5)
    # rotating_handler.setLevel(logging.ERROR)
    # formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    # rotating_handler.setFormatter(formatter)
    # logging.getLogger().addHandler(rotating_handler)

    # return logging

# log = logging.getLogger("app." + __name__)
#
# log.debug('Debug message, should only appear in the file.')
# log.info('Info message, should appear in file and stdout.')
# log.warning('Warning message, should appear in file and stdout.   ')
# log.error('Error message, should appear in file and stdout.')
