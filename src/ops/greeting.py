"""
开场白配置模块
管理客服开场白、欢迎语等
"""
import logging
import random
from typing import Dict, Any, List, Optional
from datetime import datetime, time

from src.config.operation_config import get_operation_config

logger = logging.getLogger(__name__)


class GreetingManager:
    """开场白管理器"""

    def __init__(self):
        self.config = get_operation_config()

    def should_send_greeting(self, context: Dict[str, Any]) -> bool:
        """
        判断是否应该发送开场白

        Args:
            context: 对话上下文
                - is_first_message: 是否首条消息
                - time: 当前时间
                - is_new_user: 是否新用户

        Returns:
            是否发送
        """
        # 检查是否启用
        if not self.config.get("greeting.enabled", False):
            return False

        # 检查是否首条消息
        if not context.get("is_first_message", False):
            return False

        return True

    def get_greeting(self, context: Dict[str, Any]) -> str:
        """
        获取开场白

        Args:
            context: 对话上下文

        Returns:
            开场白文本
        """
        messages = self.config.get("greeting.messages", [])

        if not messages:
            return "您好，我是智能客服助手，有什么可以帮您的吗？"

        # 根据时间选择开场白
        if self._should_use_time_based_greeting(context):
            return self._get_time_based_greeting(context)

        # 随机选择
        return random.choice(messages)

    def _should_use_time_based_greeting(self, context: Dict[str, Any]) -> bool:
        """判断是否应该使用基于时间的开场白"""
        current_time = context.get("current_time", datetime.now().time())

        # 早上
        if time(6, 0) <= current_time < time(12, 0):
            return True
        # 下午
        elif time(12, 0) <= current_time < time(18, 0):
            return True
        # 晚上
        elif time(18, 0) <= current_time < time(22, 0):
            return True

        return False

    def _get_time_based_greeting(self, context: Dict[str, Any]) -> str:
        """获取基于时间的开场白"""
        current_time = context.get("current_time", datetime.now().time())

        if time(6, 0) <= current_time < time(9, 0):
            return "早上好！有什么可以帮您的吗？"
        elif time(9, 0) <= current_time < time(12, 0):
            return "上午好！我是智能客服助手，有什么可以帮您的吗？"
        elif time(12, 0) <= current_time < time(14, 0):
            return "中午好！有什么可以帮您的吗？"
        elif time(14, 0) <= current_time < time(18, 0):
            return "下午好！有什么可以帮您的吗？"
        elif time(18, 0) <= current_time < time(22, 0):
            return "晚上好！有什么可以帮您的吗？"
        else:
            return "您好！有什么可以帮您的吗？"

    def add_greeting(self, message: str):
        """添加开场白"""
        messages = self.config.get("greeting.messages", [])
        messages.append(message)
        self.config.set("greeting.messages", messages)

    def remove_greeting(self, message: str):
        """移除开场白"""
        messages = self.config.get("greeting.messages", [])
        messages = [m for m in messages if m != message]
        self.config.set("greeting.messages", messages)

    def get_greeting_delay(self) -> int:
        """获取开场白延迟时间（秒）"""
        return self.config.get("greeting.delay", 0)


class GreetingScenario:
    """开场白场景"""

    def __init__(self, scenario_id: str, name: str, conditions: Dict[str, Any], greetings: List[str]):
        self.scenario_id = scenario_id
        self.name = name
        self.conditions = conditions
        self.greetings = greetings

    def match(self, context: Dict[str, Any]) -> bool:
        """判断是否匹配场景"""
        for key, value in self.conditions.items():
            if context.get(key) != value:
                return False
        return True

    def get_greeting(self) -> str:
        """获取随机开场白"""
        return random.choice(self.greetings)


class ScenarioGreetingManager:
    """场景化开场白管理器"""

    def __init__(self):
        self.config = get_operation_config()
        self.scenarios: Dict[str, GreetingScenario] = {}
        self._init_default_scenarios()

    def _init_default_scenarios(self):
        """初始化默认场景"""
        # 新用户场景
        self.scenarios["new_user"] = GreetingScenario(
            scenario_id="new_user",
            name="新用户",
            conditions={"is_new_user": True},
            greetings=[
                "您好！欢迎来到我们的平台，我是您的专属智能客服，有什么可以帮您的吗？",
                "欢迎新用户！我是智能客服助手，很高兴为您服务~"
            ]
        )

        # 老用户场景
        self.scenarios["returning_user"] = GreetingScenario(
            scenario_id="returning_user",
            name="老用户",
            conditions={"is_new_user": False},
            greetings=[
                "欢迎回来！有什么可以帮您的吗？",
                "您好！很高兴再次为您服务"
            ]
        )

        # VIP用户场景
        self.scenarios["vip_user"] = GreetingScenario(
            scenario_id="vip_user",
            name="VIP用户",
            conditions={"is_vip": True},
            greetings=[
                "尊贵的VIP用户您好！有什么可以帮您的吗？",
                "欢迎VIP用户！我是您的专属客服，有什么可以帮您的吗？"
            ]
        )

    def get_scenario_greeting(self, context: Dict[str, Any]) -> Optional[str]:
        """获取场景化开场白"""
        for scenario in self.scenarios.values():
            if scenario.match(context):
                return scenario.get_greeting()

        return None

    def add_scenario(self, scenario: GreetingScenario):
        """添加场景"""
        self.scenarios[scenario.scenario_id] = scenario

    def remove_scenario(self, scenario_id: str):
        """移除场景"""
        if scenario_id in self.scenarios:
            del self.scenarios[scenario_id]

    def list_scenarios(self) -> List[GreetingScenario]:
        """列出所有场景"""
        return list(self.scenarios.values())


def get_greeting_message(context: Dict[str, Any]) -> str:
    """
    获取开场白（便捷函数）

    Args:
        context: 对话上下文

    Returns:
        开场白文本
    """
    manager = GreetingManager()

    # 首先检查场景化开场白
    scenario_manager = ScenarioGreetingManager()
    scenario_greeting = scenario_manager.get_scenario_greeting(context)

    if scenario_greeting:
        return scenario_greeting

    # 使用默认开场白
    if manager.should_send_greeting(context):
        return manager.get_greeting(context)

    return ""
