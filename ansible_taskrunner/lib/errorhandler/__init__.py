ERR_ARGS_TASKF_OVERRIDE = '''
When specifying a task file override, you must do so like this:
{script} -f /path/to/mytasks.yaml
{script} --tasks-file /path/to/mytasks.yaml
Additionally, only task file overrides ending in .yml or .yaml are accepted
'''

# see https://stackoverflow.com/questions/6234405/logging-uncaught-exceptions-in-python


def catchException(logger, script_name, typ, value, traceback):
    """Log uncaught exception to python logger"""
    logger.critical("Program Crash")
    logger.critical("Type: %s" % typ)
    logger.critical("Value: %s" % value)
    logger.critical("Traceback: %s" % traceback)
    logger.info(
        "Run same command but with %s --debug to see full stack trace!" % script_name)
