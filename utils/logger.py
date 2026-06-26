"""
日志系统
支持文件输出和GUI回调输出
"""
import os
import logging
from datetime import datetime
from typing import Callable, Optional


class AppLogger:
    """应用日志管理器（单例）"""
    _instance = None
    _initialized = False

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self, log_dir: str = "logs", gui_callback: Optional[Callable] = None):
        if self._initialized:
            if gui_callback:
                self._gui_callback = gui_callback
            return
        self._initialized = True
        self._gui_callback = gui_callback

        os.makedirs(log_dir, exist_ok=True)
        log_file = os.path.join(log_dir, f"taobao_{datetime.now().strftime('%Y-%m-%d')}.log")

        self._logger = logging.getLogger("taobao_app")
        self._logger.setLevel(logging.DEBUG)

        # 文件输出
        fh = logging.FileHandler(log_file, encoding="utf-8")
        fh.setLevel(logging.DEBUG)
        fh.setFormatter(logging.Formatter(
            "[%(asctime)s] [%(levelname)s] [%(module)s] %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S"
        ))
        self._logger.addHandler(fh)

        # 控制台输出
        ch = logging.StreamHandler()
        ch.setLevel(logging.INFO)
        ch.setFormatter(logging.Formatter(
            "[%(asctime)s] [%(levelname)s] %(message)s",
            datefmt="%H:%M:%S"
        ))
        self._logger.addHandler(ch)

    def set_gui_callback(self, callback: Callable):
        """设置GUI回调"""
        self._gui_callback = callback

    def _emit(self, level: str, message: str):
        """发送日志到文件和GUI"""
        if self._gui_callback:
            try:
                self._gui_callback(level, message)
            except Exception:
                pass

    def info(self, message: str):
        self._logger.info(message)
        self._emit("INFO", message)

    def warning(self, message: str):
        self._logger.warning(message)
        self._emit("WARNING", message)

    def error(self, message: str):
        self._logger.error(message)
        self._emit("ERROR", message)

    def debug(self, message: str):
        self._logger.debug(message)
        self._emit("DEBUG", message)


def get_logger(log_dir: str = "logs", gui_callback: Optional[Callable] = None) -> AppLogger:
    """获取日志实例"""
    return AppLogger(log_dir, gui_callback)
