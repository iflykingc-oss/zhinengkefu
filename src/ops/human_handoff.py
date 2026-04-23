"""
转人工策略模块
管理各种转人工策略（关键词、意图、轮次限制、情感分析等）
"""
import logging
from typing import Dict, Any, List, Optional
from enum import Enum

from src.config.operation_config import get_operation_config, TransferStrategyType

logger = logging.getLogger(__name__)


class TransferReason(str, Enum):
    """转人工原因"""
    KEYWORD = "keyword"  # 关键词触发
    ROUND_LIMIT = "round_limit"  # 轮次超限
    NO_SOLUTION = "no_solution"  # 无解决方案
    NEGATIVE_SENTIMENT = "negative_sentiment"  # 负面情感
    ANGER = "anger"  # 愤怒
    INTENT = "intent"  # 意图识别
    MANUAL = "manual"  # 手动触发


class HumanHandoffManager:
    """人工转接管理器"""

    def __init__(self):
        self.config = get_operation_config()

    def should_transfer(self, context: Dict[str, Any]) -> tuple[bool, Optional[str], Optional[TransferReason]]:
        """
        判断是否需要转人工

        Args:
            context: 对话上下文
                - user_input: 用户输入
                - round: 当前轮次
                - conversation_history: 对话历史
                - has_solution: 是否有解决方案

        Returns:
            (是否转接, 消息, 原因)
        """
        user_input = context.get("user_input", "")
        round = context.get("round", 0)
        has_solution = context.get("has_solution", True)
        conversation_history = context.get("conversation_history", [])

        # 获取转人工策略配置
        strategies = self.config.get("transfer_to_human.strategies", [])

        # 检查每个策略
        for strategy in strategies:
            if not strategy.get("enabled", False):
                continue

            strategy_type = strategy.get("type")
            strategy_config = strategy.get("config", {})

            # 关键词策略
            if strategy_type == TransferStrategyType.KEYWORD.value:
                should, reason = self._check_keyword_strategy(user_input, strategy_config)
                if should:
                    message = self.config.get("transfer_to_human.fallback_message", "正在为您转接人工客服...")
                    return True, message, TransferReason.KEYWORD

            # 轮次限制策略
            elif strategy_type == TransferStrategyType.ROUND_LIMIT.value:
                should, reason = self._check_round_limit_strategy(round, has_solution, strategy_config)
                if should:
                    if reason == TransferReason.NO_SOLUTION:
                        message = self.config.get("transfer_to_human.fallback_message", "抱歉，我无法解决您的问题，正在为您转接人工客服...")
                    else:
                        message = self.config.get("transfer_to_human.fallback_message", "您的对话轮次较多，正在为您转接人工客服...")
                    return True, message, reason

            # 情感分析策略
            elif strategy_type == TransferStrategyType.SENTIMENT.value:
                should, reason = self._check_sentiment_strategy(user_input, strategy_config)
                if should:
                    message = self.config.get("transfer_to_human.fallback_message", "我理解您的情绪，正在为您转接人工客服...")
                    return True, message, reason

        return False, None, None

    def _check_keyword_strategy(self, user_input: str, config: Dict[str, Any]) -> tuple[bool, TransferReason]:
        """检查关键词策略"""
        keywords = config.get("keywords", [])
        match_mode = config.get("match_mode", "contains")

        user_input_lower = user_input.lower()

        for keyword in keywords:
            if match_mode == "exact":
                if keyword.lower() == user_input_lower:
                    return True, TransferReason.KEYWORD
            else:  # contains
                if keyword.lower() in user_input_lower:
                    return True, TransferReason.KEYWORD

        return False, TransferReason.KEYWORD

    def _check_round_limit_strategy(self, round: int, has_solution: bool, config: Dict[str, Any]) -> tuple[bool, TransferReason]:
        """检查轮次限制策略"""
        max_rounds = config.get("max_rounds", 5)
        no_solution_trigger = config.get("no_solution_trigger", True)

        # 检查轮次超限
        if round >= max_rounds:
            return True, TransferReason.ROUND_LIMIT

        # 检查无解决方案
        if no_solution_trigger and not has_solution and round >= 3:
            return True, TransferReason.NO_SOLUTION

        return False, TransferReason.ROUND_LIMIT

    def _check_sentiment_strategy(self, user_input: str, config: Dict[str, Any]) -> tuple[bool, TransferReason]:
        """检查情感分析策略"""
        # 这里应该调用情感分析API
        # 暂时使用简单的关键词匹配

        anger_keywords = ["愤怒", "生气", "骂", "滚", "垃圾", "笨蛋", "投诉"]
        negative_keywords = ["不满意", "糟糕", "差", "失望", "难过"]

        anger_threshold = config.get("anger_threshold", 0.8)
        negative_threshold = config.get("negative_threshold", 0.7)

        user_input_lower = user_input.lower()

        # 检查愤怒情绪
        anger_count = sum(1 for kw in anger_keywords if kw in user_input_lower)
        if anger_count > 0:
            return True, TransferReason.ANGER

        # 检查负面情绪
        negative_count = sum(1 for kw in negative_keywords if kw in user_input_lower)
        if negative_count > 0:
            return True, TransferReason.NEGATIVE_SENTIMENT

        return False, TransferReason.NEGATIVE_SENTIMENT

    def get_transfer_channels(self) -> List[str]:
        """获取转人工渠道"""
        return self.config.get("human_handoff.channels", ["feishu"])

    def get_default_channel(self) -> str:
        """获取默认渠道"""
        return self.config.get("human_handoff.default_channel", "feishu")

    def send_notification(self, channel: str, message: str, context: Dict[str, Any]):
        """发送转人工通知"""
        try:
            if channel == "feishu":
                self._send_feishu_notification(message, context)
            elif channel == "weixin":
                self._send_weixin_notification(message, context)
            elif channel == "email":
                self._send_email_notification(message, context)
            else:
                logger.warning(f"不支持的转人工渠道: {channel}")
        except Exception as e:
            logger.error(f"发送转人工通知失败: {e}")

    def _send_feishu_notification(self, message: str, context: Dict[str, Any]):
        """发送飞书通知"""
        try:
            from tools.feishu_notification_tool import send_feishu_text_message

            notification_message = self.config.get("human_handoff.notification_message", "有新的人工转接请求：")
            full_message = f"{notification_message}\n\n用户咨询: {context.get('user_input', '')}\n{message}"

            send_feishu_text_message(full_message)
            logger.info("已发送飞书转人工通知")
        except Exception as e:
            logger.error(f"发送飞书通知失败: {e}")

    def _send_weixin_notification(self, message: str, context: Dict[str, Any]):
        """发送微信通知"""
        # 实现微信通知逻辑
        logger.info(f"发送微信转人工通知: {message}")

    def _send_email_notification(self, message: str, context: Dict[str, Any]):
        """发送邮件通知"""
        # 实现邮件通知逻辑
        logger.info(f"发送邮件转人工通知: {message}")


def check_should_transfer_human(context: Dict[str, Any]) -> tuple[bool, Optional[str], Optional[TransferReason]]:
    """
    检查是否需要转人工（便捷函数）

    Args:
        context: 对话上下文

    Returns:
        (是否转接, 消息, 原因)
    """
    manager = HumanHandoffManager()
    return manager.should_transfer(context)
