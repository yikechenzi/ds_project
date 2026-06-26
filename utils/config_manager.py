"""
配置管理器
加载config.json, 合并默认配置, 提供读写接口
"""
import json
import os
from typing import Any


class ConfigManager:
    """配置管理器"""

    def __init__(self, config_path: str = "config.json", default_path: str = "resources/default_config.json"):
        self._config_path = config_path
        self._default_path = default_path
        self._config = {}
        self._load()

    def _load(self):
        """加载配置"""
        # 先加载默认配置
        if os.path.exists(self._default_path):
            with open(self._default_path, "r", encoding="utf-8") as f:
                self._config = json.load(f)

        # 再加载用户配置覆盖
        if os.path.exists(self._config_path):
            with open(self._config_path, "r", encoding="utf-8") as f:
                user_config = json.load(f)
                self._deep_merge(self._config, user_config)

    def _deep_merge(self, base: dict, override: dict):
        """深度合并字典"""
        for key, value in override.items():
            if key in base and isinstance(base[key], dict) and isinstance(value, dict):
                self._deep_merge(base[key], value)
            else:
                base[key] = value

    def get(self, section: str, key: str = None, default: Any = None) -> Any:
        """获取配置值"""
        section_data = self._config.get(section, {})
        if key is None:
            return section_data if section_data else default
        return section_data.get(key, default)

    def set(self, section: str, key: str, value: Any):
        """设置配置值"""
        if section not in self._config:
            self._config[section] = {}
        self._config[section][key] = value
        self._save()

    def _save(self):
        """保存配置到文件"""
        with open(self._config_path, "w", encoding="utf-8") as f:
            json.dump(self._config, f, ensure_ascii=False, indent=2)

    def reload(self):
        """重新加载配置"""
        self._config = {}
        self._load()

    @property
    def raw(self) -> dict:
        """返回原始配置字典"""
        return self._config
