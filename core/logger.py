import logging
from pathlib import Path


def configure_logger():
    logger = logging.getLogger(
        'schedule_mvp')  # 调用 logging.getLogger 函数获取一个名为 'schedule_mvp'的logger。这样做可以在不同模块中共享同一个日志记录器。
    logger.setLevel(logging.DEBUG)  # 设置 logger 的日志级别为 DEBUG，这意味着所有级别在 DEBUG 及以上的日志信息都会被记录下来。

    # 文件handler
    log_file = Path(__file__).parent.parent / 'logs' / 'app.log'  # C:\Users\86159\Desktop\schedule_mvp\logs
    file_handler = logging.FileHandler(log_file)  # 创建文件处理器
    file_handler.setFormatter(logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'  # 时间戳-记录器名称（s_m)-日志级别-信息
    ))
    # 控制台handler，将日志信息输出到标准输出（控制台）
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(logging.Formatter(  # 只显示级别、信息
        '%(levelname)s - %(message)s'
    ))

    logger.addHandler(file_handler)  # 将文件处理器添加到 logger 中，这样 logger 的日志信息会被写入到文件中。
    logger.addHandler(console_handler)  # 将控制台处理器添加到 logger 中，使得日志信息同时在控制台上显示。
    return logger
