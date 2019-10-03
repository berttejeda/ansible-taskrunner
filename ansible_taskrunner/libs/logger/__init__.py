import logging
import logging.handlers
import sys

def init_logger():
	# Setup Logging
	logger = logging.getLogger()
	if '--debug run' in ' '.join(sys.argv):
	    logger.setLevel(logging.DEBUG)
	else:
	    logger.setLevel(logging.INFO)
	streamhandler = logging.StreamHandler()
	streamhandler.setFormatter(
	    logging.Formatter("%(asctime)s %(name)s [%(levelname)s]: %(message)s", datefmt='%Y-%m-%d %H:%M:%S')
	)
	logger.addHandler(streamhandler)
	return logger