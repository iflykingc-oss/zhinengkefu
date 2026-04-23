"""
闲聊配置模块
管理闲聊意图识别和回复
"""
import logging
import random
from typing import Dict, Any, List, Optional, Tuple

from src.config.operation_config import get_operation_config

logger = logging.getLogger(__name__)


class ChitchatManager:
    """闲聊管理器"""

    def __init__(self):
        self.config = get_operation_config()

    def is_chitchat(self, user_input: str) -> bool:
        """
        判断是否为闲聊

        Args:
            user_input: 用户输入

        Returns:
            是否闲聊
        """
        if not self.config.get("chitchat.enabled", False):
            return False

        if not self.config.get("chitchat.auto_detect", False):
            return False

        intents = self.config.get("chitchat.intents", [])
        user_input_lower = user_input.lower().strip()

        for intent_config in intents:
            keywords = intent_config.get("keywords", [])
            for keyword in keywords:
                if keyword.lower() in user_input_lower:
                    return True

        return False

    def get_chitchat_response(self, user_input: str) -> Optional[str]:
        """
        获取闲聊回复

        Args:
            user_input: 用户输入

        Returns:
            闲聊回复
        """
        intents = self.config.get("chitchat.intents", [])
        user_input_lower = user_input.lower().strip()

        matched_intents = []

        for intent_config in intents:
            keywords = intent_config.get("keywords", [])
            responses = intent_config.get("responses", [])

            for keyword in keywords:
                if keyword.lower() in user_input_lower:
                    matched_intents.extend(responses)
                    break

        if matched_intents:
            # 随机选择一个回复
            return random.choice(matched_intents)

        return None

    def detect_intent(self, user_input: str) -> Optional[str]:
        """
        检测意图

        Args:
            user_input: 用户输入

        Returns:
            意图名称
        """
        intents = self.config.get("chitchat.intents", [])
        user_input_lower = user_input.lower().strip()

        for intent_config in intents:
            keywords = intent_config.get("keywords", [])
            for keyword in keywords:
                if keyword.lower() in user_input_lower:
                    return intent_config.get("intent")

        return None

    def add_intent(self, intent: str, keywords: List[str], responses: List[str]):
        """添加闲聊意图"""
        self.config.add_chitchat_intent(intent, keywords, responses)

    def remove_intent(self, intent: str):
        """移除闲聊意图"""
        self.config.remove_chitchat_intent(intent)

    def list_intents(self) -> List[Dict[str, Any]]:
        """列出所有意图"""
        return self.config.get("chitchat.intents", [])


class ChitchatTemplate:
    """闲聊模板"""

    def __init__(self, template_id: str, name: str, patterns: List[str], responses: List[str], variables: Optional[Dict[str, Any]] = None):
        self.template_id = template_id
        self.name = name
        self.patterns = patterns
        self.responses = responses
        self.variables = variables or {}

    def match(self, user_input: str) -> bool:
        """判断是否匹配"""
        user_input_lower = user_input.lower()
        for pattern in self.patterns:
            if pattern.lower() in user_input_lower:
                return True
        return False

    def generate_response(self, context: Dict[str, Any] = None) -> str:
        """生成回复"""
        response = random.choice(self.responses)

        # 替换变量
        if self.variables and context:
            for key, value in self.variables.items():
                placeholder = f"{{{key}}}"
                if placeholder in response:
                    response = response.replace(placeholder, str(value))

        return response


class TemplateChitchatManager:
    """模板化闲聊管理器"""

    def __init__(self):
        self.templates: Dict[str, ChitchatTemplate] = {}
        self._init_default_templates()

    def _init_default_templates(self):
        """初始化默认模板"""
        # 时间问候
        self.templates["time_greeting"] = ChitchatTemplate(
            template_id="time_greeting",
            name="时间问候",
            patterns=["几点了", "现在时间", "现在是几点"],
            responses=["现在是 {time}"],
            variables={"time": lambda: self._get_current_time()}
        )

        # 天气询问
        self.templates["weather"] = ChitchatTemplate(
            template_id="weather",
            name="天气询问",
            patterns=["天气怎么样", "今天天气"],
            responses=["抱歉，我无法获取实时天气信息，建议您查看天气APP哦~"]
        )

        # 身份询问
        self.templates["identity"] = ChitchatTemplate(
            template_id="identity",
            name="身份询问",
            patterns=["你是谁", "你叫什么", "你的名字"],
            responses=["我是智能客服助手，很高兴为您服务！", "我是您的AI助手，有什么可以帮您的吗？"]
        )

        # 能力询问
        self.templates["capability"] = ChitchatTemplate(
            template_id="capability",
            name="能力询问",
            patterns=["你能做什么", "你有什么功能", "你可以做什么"],
            responses=["我可以帮您解答问题、提供信息查询等服务。请问有什么可以帮您的吗？"]
        )

    def _get_current_time(self) -> str:
        """获取当前时间"""
        from datetime import datetime
        return datetime.now().strftime("%H:%M")

    def get_template_response(self, user_input: str, context: Dict[str, Any] = None) -> Optional[str]:
        """获取模板回复"""
        for template in self.templates.values():
            if template.match(user_input):
                return template.generate_response(context)
        return None

    def add_template(self, template: ChitchatTemplate):
        """添加模板"""
        self.templates[template.template_id] = template

    def remove_template(self, template_id: str):
        """移除模板"""
        if template_id in self.templates:
            del self.templates[template_id]

    def list_templates(self) -> List[ChitchatTemplate]:
        """列出所有模板"""
        return list(self.templates.values())


def handle_chitchat(user_input: str) -> Tuple[bool, Optional[str]]:
    """
    处理闲聊（便捷函数）

    Args:
        user_input: 用户输入

    Returns:
        (是否闲聊, 回复)
    """
    # 首先检查模板闲聊
    template_manager = TemplateChitchatManager()
    template_response = template_manager.get_template_response(user_input)

    if template_response:
        return True, template_response

    # 检查意图闲聊
    chitchat_manager = ChitchatManager()
    if chitchat_manager.is_chitchat(user_input):
        response = chitchat_manager.get_chitchat_response(user_input)
        return True, response

    return False, None
