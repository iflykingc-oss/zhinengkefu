"""
运营配置系统
支持知识库、SOP、转人工策略、开场白、闲聊等运营配置管理
"""
import json
import os
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime
from enum import Enum

logger = logging.getLogger(__name__)


class TransferStrategyType(str, Enum):
    """转人工策略类型"""
    KEYWORD = "keyword"  # 关键词触发
    INTENT = "intent"  # 意图识别
    ROUND_LIMIT = "round_limit"  # 轮次限制
    SENTIMENT = "sentiment"  # 情感分析
    MANUAL = "manual"  # 手动触发


class ChatType(str, Enum):
    """聊天类型"""
    FAQ = "faq"  # 问答
    CHITCHAT = "chitchat"  # 闲聊
    TASK = "task"  # 任务型对话


class OperationConfig:
    """运营配置"""

    def __init__(self, config_path: Optional[str] = None):
        self.workspace_path = os.getenv("COZE_WORKSPACE_PATH", "/workspace/projects")
        if config_path is None:
            config_path = os.path.join(self.workspace_path, "config/operation_config.json")
        self.config_path = config_path

        # 默认配置
        self.config = self._default_config()

        # 加载配置
        self.load_config()

    def _default_config(self) -> Dict[str, Any]:
        """默认配置"""
        return {
            "greeting": {
                "enabled": True,
                "messages": [
                    "您好，我是智能客服助手，有什么可以帮您的吗？",
                    "您好！请问有什么可以帮到您？"
                ],
                "delay": 0  # 延迟发送（秒）
            },
            "chitchat": {
                "enabled": True,
                "auto_detect": True,
                "intents": [
                    {
                        "intent": "greeting",
                        "keywords": ["你好", "嗨", "hello", "hi"],
                        "responses": ["你好！", "嗨！有什么可以帮您？"]
                    },
                    {
                        "intent": "thanks",
                        "keywords": ["谢谢", "感谢", "thanks"],
                        "responses": ["不客气！", "很高兴能帮到您！"]
                    },
                    {
                        "intent": "goodbye",
                        "keywords": ["再见", "拜拜", "bye"],
                        "responses": ["再见！祝您生活愉快！", "拜拜！"]
                    }
                ]
            },
            "transfer_to_human": {
                "enabled": True,
                "strategies": [
                    {
                        "type": TransferStrategyType.KEYWORD.value,
                        "name": "关键词转人工",
                        "enabled": True,
                        "config": {
                            "keywords": ["转人工", "找客服", "人工客服", "投诉", "投诉"],
                            "match_mode": "contains"  # contains/exact
                        }
                    },
                    {
                        "type": TransferStrategyType.ROUND_LIMIT.value,
                        "name": "轮次限制",
                        "enabled": True,
                        "config": {
                            "max_rounds": 5,
                            "no_solution_trigger": True  # 无解决方案时触发
                        }
                    },
                    {
                        "type": TransferStrategyType.SENTIMENT.value,
                        "name": "情感分析",
                        "enabled": True,
                        "config": {
                            "negative_threshold": 0.7,  # 消极情感阈值
                            "anger_threshold": 0.8  # 愤怒阈值
                        }
                    }
                ],
                "fallback_message": "正在为您转接人工客服，请稍候..."
            },
            "knowledge_base": {
                "enabled": True,
                "priority": 1,  # 优先级
                "rag_enabled": True,
                "retrieval_config": {
                    "top_k": 5,
                    "min_score": 0.5
                }
            },
            "sop_flow": {
                "enabled": True,
                "priority": 0,  # 最高优先级
                "canvas_nodes": []  # 画布节点配置
            },
            "human_handoff": {
                "enabled": True,
                "channels": ["feishu", "weixin", "email"],
                "default_channel": "feishu",
                "notification_message": "有新的人工转接请求："
            },
            "conversation_settings": {
                "max_rounds": 20,  # 最大对话轮次
                "timeout": 1800,  # 会话超时时间（秒）
                "remember_context": True  # 是否记住上下文
            },
            "response_settings": {
                "stream_response": True,  # 流式响应
                "show_thinking": False,  # 显示思考过程
                "typing_indicator": True  # 打字指示器
            }
        }

    def load_config(self):
        """加载配置"""
        if os.path.exists(self.config_path):
            try:
                with open(self.config_path, 'r', encoding='utf-8') as f:
                    loaded_config = json.load(f)
                    # 合并配置
                    self.config = self._merge_config(self.config, loaded_config)
                    logger.info(f"已加载运营配置: {self.config_path}")
            except Exception as e:
                logger.error(f"加载运营配置失败: {e}")
        else:
            # 创建默认配置
            self.save_config()

    def save_config(self):
        """保存配置"""
        os.makedirs(os.path.dirname(self.config_path), exist_ok=True)
        with open(self.config_path, 'w', encoding='utf-8') as f:
            json.dump(self.config, f, ensure_ascii=False, indent=2)
        logger.info(f"已保存运营配置: {self.config_path}")

    def _merge_config(self, default: Dict, loaded: Dict) -> Dict:
        """合并配置"""
        result = default.copy()
        for key, value in loaded.items():
            if key in result and isinstance(result[key], dict) and isinstance(value, dict):
                result[key] = self._merge_config(result[key], value)
            else:
                result[key] = value
        return result

    def get(self, key: str, default: Any = None) -> Any:
        """获取配置值"""
        keys = key.split(".")
        value = self.config
        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return default
        return value

    def set(self, key: str, value: Any):
        """设置配置值"""
        keys = key.split(".")
        config = self.config
        for k in keys[:-1]:
            if k not in config:
                config[k] = {}
            config = config[k]
        config[keys[-1]] = value
        self.save_config()

    def update_config(self, config: Dict[str, Any]):
        """更新配置"""
        self.config = self._merge_config(self.config, config)
        self.save_config()

    def get_full_config(self) -> Dict[str, Any]:
        """获取完整配置"""
        return self.config.copy()

    def add_chitchat_intent(self, intent: str, keywords: List[str], responses: List[str]):
        """添加闲聊意图"""
        chitchat_config = self.config.get("chitchat", {})
        intents = chitchat_config.get("intents", [])
        intents.append({
            "intent": intent,
            "keywords": keywords,
            "responses": responses
        })
        chitchat_config["intents"] = intents
        self.config["chitchat"] = chitchat_config
        self.save_config()

    def remove_chitchat_intent(self, intent: str):
        """移除闲聊意图"""
        chitchat_config = self.config.get("chitchat", {})
        intents = chitchat_config.get("intents", [])
        intents = [i for i in intents if i.get("intent") != intent]
        chitchat_config["intents"] = intents
        self.config["chitchat"] = chitchat_config
        self.save_config()

    def add_transfer_strategy(self, strategy: Dict[str, Any]):
        """添加转人工策略"""
        transfer_config = self.config.get("transfer_to_human", {})
        strategies = transfer_config.get("strategies", [])
        strategies.append(strategy)
        transfer_config["strategies"] = strategies
        self.config["transfer_to_human"] = transfer_config
        self.save_config()

    def update_transfer_strategy(self, strategy_type: str, config: Dict[str, Any]):
        """更新转人工策略"""
        transfer_config = self.config.get("transfer_to_human", {})
        strategies = transfer_config.get("strategies", [])
        for strategy in strategies:
            if strategy.get("type") == strategy_type:
                strategy["config"] = config
                break
        self.config["transfer_to_human"] = transfer_config
        self.save_config()


# 创建全局运营配置管理器
_operation_config: Optional[OperationConfig] = None


def get_operation_config() -> OperationConfig:
    """获取运营配置管理器"""
    global _operation_config
    if _operation_config is None:
        _operation_config = OperationConfig()
    return _operation_config
