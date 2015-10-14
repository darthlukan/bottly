import logging
import logging.handlers
import os

base_dir = os.path.dirname(os.path.abspath(__file__))


def log_setup(log_dir, log_file):
    logger = logging.getLogger("bottly")
    log_path = base_dir + "/" + log_dir + "/"
    log = log_path + log_file
    if not os.path.exists(log_path):
        os.makedirs(log_path)

    if not os.path.isfile(log):
        handler = logging.FileHandler(log, "w")

    handler = logging.FileHandler(log)
    formatter = logging.Formatter("%(levelname)s %(asctime)s %(message)s",
                                  "%H:%M:%S")
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    logger.setLevel(logging.INFO)

    return logger


def log(logger, user, msg_type, destination, command, arg):
    arg = " ".join(arg)
    message = command + " " + arg
    logger.info("%s %s: %s" % (destination, user, message))
