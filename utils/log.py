def wt_log(func_name, levelname, msg):
    import logging
    import os
    from logging.handlers import RotatingFileHandler

    logger = logging.getLogger(func_name)
    logger.setLevel(logging.INFO)

    log_path = "log.txt"

    handler = RotatingFileHandler(log_path, maxBytes=102400, backupCount=3)
    handler.setLevel(logging.INFO)

    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)

    console = logging.StreamHandler()
    console.setLevel(logging.INFO)
    console.setFormatter(formatter)
    
    logger.addHandler(handler)
    logger.addHandler(console)

    if levelname == "info":
        logger.info(msg)
    elif levelname == "warning":
        logger.warning(msg)
    elif levelname == "debug":
        logger.debug(msg)
    elif levelname == "fatal":
        logger.fatal(msg)
    elif levelname == "error":
        logger.error(msg)
    else:
        logger.error(f"Unknown logging level: {levelname}")

    logger.propagate = False
    for handler in logger.handlers[:]:
        logger.removeHandler(handler)


