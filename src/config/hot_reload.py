"""
配置热更新功能
支持运行时更新配置，无需重启服务
"""
import json
import os
import time
import threading
from typing import Dict, Any, Optional, Callable
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class HotReloadConfig:
    """
    支持热更新的配置类
    """

    def __init__(self, config_path: str):
        self.config_path = config_path
        self._config: Dict[str, Any] = {}
        self._last_modified = 0
        self._callbacks: Dict[str, list] = {}
        self._lock = threading.Lock()
        self._watch_thread: Optional[threading.Thread] = None
        self._watching = False

        # 加载初始配置
        self.load_config()

    def load_config(self) -> Dict[str, Any]:
        """加载配置"""
        with self._lock:
            if os.path.exists(self.config_path):
                with open(self.config_path, 'r', encoding='utf-8') as f:
                    self._config = json.load(f)

                # 更新修改时间
                self._last_modified = os.path.getmtime(self.config_path)

                logger.info(f"配置已加载: {self.config_path}")

            return self._config.copy()

    def save_config(self) -> bool:
        """保存配置"""
        try:
            with self._lock:
                # 保存配置
                os.makedirs(os.path.dirname(self.config_path), exist_ok=True)
                with open(self.config_path, 'w', encoding='utf-8') as f:
                    json.dump(self._config, f, ensure_ascii=False, indent=2)

                # 更新修改时间
                self._last_modified = os.path.getmtime(self.config_path)

                logger.info(f"配置已保存: {self.config_path}")

                return True

        except Exception as e:
            logger.error(f"保存配置失败: {e}")
            return False

    def get_config(self) -> Dict[str, Any]:
        """获取配置"""
        with self._lock:
            return self._config.copy()

    def get(self, key: str, default: Any = None) -> Any:
        """获取配置项"""
        with self._lock:
            return self._config.get(key, default)

    def set(self, key: str, value: Any) -> bool:
        """设置配置项"""
        try:
            with self._lock:
                self._config[key] = value

                # 保存配置
                self.save_config()

                # 触发回调
                self._trigger_callbacks(key, value)

                logger.info(f"配置已更新: {key}")

                return True

        except Exception as e:
            logger.error(f"更新配置失败: {e}")
            return False

    def update(self, updates: Dict[str, Any]) -> bool:
        """批量更新配置"""
        try:
            with self._lock:
                for key, value in updates.items():
                    self._config[key] = value

                # 保存配置
                self.save_config()

                # 触发回调
                for key, value in updates.items():
                    self._trigger_callbacks(key, value)

                logger.info(f"配置已批量更新: {len(updates)} 项")

                return True

        except Exception as e:
            logger.error(f"批量更新配置失败: {e}")
            return False

    def register_callback(self, key: str, callback: Callable[[str, Any], None]):
        """注册配置变更回调"""
        if key not in self._callbacks:
            self._callbacks[key] = []
        self._callbacks[key].append(callback)
        logger.info(f"已注册回调: {key}")

    def _trigger_callbacks(self, key: str, value: Any):
        """触发回调"""
        if key in self._callbacks:
            for callback in self._callbacks[key]:
                try:
                    callback(key, value)
                except Exception as e:
                    logger.error(f"回调执行失败 ({key}): {e}")

    def start_watch(self, interval: float = 1.0):
        """开始监听配置文件变化"""
        if self._watching:
            logger.warning("配置监听已在运行")
            return

        self._watching = True
        self._watch_thread = threading.Thread(target=self._watch_config_file, daemon=True)
        self._watch_thread.start()
        logger.info(f"开始监听配置文件变化（间隔: {interval}s）")

    def stop_watch(self):
        """停止监听配置文件变化"""
        self._watching = False
        if self._watch_thread:
            self._watch_thread.join(timeout=2.0)
        logger.info("已停止监听配置文件变化")

    def _watch_config_file(self, interval: float = 1.0):
        """监听配置文件变化"""
        while self._watching:
            try:
                # 检查文件修改时间
                if os.path.exists(self.config_path):
                    current_mtime = os.path.getmtime(self.config_path)

                    if current_mtime > self._last_modified:
                        logger.info("检测到配置文件变化，重新加载...")
                        old_config = self._config.copy()
                        new_config = self.load_config()

                        # 触发变更回调
                        for key, value in new_config.items():
                            if key not in old_config or old_config[key] != value:
                                self._trigger_callbacks(key, value)

                        logger.info("配置重新加载完成")

            except Exception as e:
                logger.error(f"监听配置文件时出错: {e}")

            time.sleep(interval)

    def reload_config(self) -> bool:
        """手动重新加载配置"""
        try:
            old_config = self._config.copy()
            new_config = self.load_config()

            # 触发变更回调
            for key, value in new_config.items():
                if key not in old_config or old_config[key] != value:
                    self._trigger_callbacks(key, value)

            return True

        except Exception as e:
            logger.error(f"重新加载配置失败: {e}")
            return False


class ConfigManager:
    """
    配置管理器
    支持热更新和多配置文件管理
    """

    def __init__(self):
        self.workspace_path = os.getenv("COZE_WORKSPACE_PATH", "/workspace/projects")
        self._configs: Dict[str, HotReloadConfig] = {}

        # 加载默认配置
        self.load_default_configs()

    def load_default_configs(self):
        """加载默认配置"""
        # 工作流配置
        workflow_config_path = os.path.join(self.workspace_path, "config/workflow_config.json")
        self.register_config("workflow", workflow_config_path)

        # Agent 配置
        agent_config_path = os.path.join(self.workspace_path, "config/agent_llm_config.json")
        self.register_config("agent", agent_config_path)

        # 启动配置监听
        self.start_watch_all()

    def register_config(self, name: str, config_path: str) -> HotReloadConfig:
        """注册配置"""
        config = HotReloadConfig(config_path)
        self._configs[name] = config
        logger.info(f"已注册配置: {name} -> {config_path}")
        return config

    def get_config(self, name: str) -> Optional[HotReloadConfig]:
        """获取配置"""
        return self._configs.get(name)

    def update_config(self, name: str, updates: Dict[str, Any]) -> bool:
        """更新配置"""
        config = self.get_config(name)
        if config:
            return config.update(updates)
        return False

    def start_watch_all(self):
        """开始监听所有配置文件"""
        for name, config in self._configs.items():
            config.start_watch()
        logger.info(f"已开始监听 {len(self._configs)} 个配置文件")

    def stop_watch_all(self):
        """停止监听所有配置文件"""
        for name, config in self._configs.items():
            config.stop_watch()
        logger.info("已停止监听所有配置文件")


# 创建全局配置管理器实例
_config_manager: Optional[ConfigManager] = None


def get_config_manager() -> ConfigManager:
    """获取全局配置管理器"""
    global _config_manager
    if _config_manager is None:
        _config_manager = ConfigManager()
    return _config_manager


def reload_all_configs() -> bool:
    """重新加载所有配置"""
    manager = get_config_manager()
    success = True

    for name, config in manager._configs.items():
        if not config.reload_config():
            success = False
            logger.error(f"重新加载配置失败: {name}")

    return success
