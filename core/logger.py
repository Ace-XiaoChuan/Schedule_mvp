import logging
from pathlib import Path


def configure_logger():
    logger = logging.getLogger('schedule_mvp')
    logger.setLevel(logging.DEBUG)

    # 文件handler
    log_file = Path(__file__).parent.parent / 'logs' / 'app.log'
    file_handler = logging.FileHandler(log_file)
    file_handler.setFormatter(logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    ))
    # 控制台handler
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(logging.Formatter(
        '%(levelname)s - %(message)s'
    ))

    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
    return logger
