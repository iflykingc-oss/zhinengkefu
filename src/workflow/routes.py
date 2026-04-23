"""
工作流路由条件
定义节点之间的条件路由
"""
from typing import Literal
from workflow.state import WorkflowState


def should_search_web(state: WorkflowState) -> Literal["web_search", "answer_generation"]:
    """
    决定是否进行联网搜索
    """
    if state.get("knowledge_found", False):
        return "answer_generation"
    else:
        return "web_search"


def should_generate_risky_answer(state: WorkflowState) -> Literal["generate_risky_answer", "generate_safe_answer"]:
    """
    决定如何生成答案（基于风险评估）
    """
    if state.get("is_risky", False):
        return "generate_risky_answer"
    else:
        return "generate_safe_answer"


def should_send_feishu(state: WorkflowState) -> Literal["feishu_notification", "__end__"]:
    """
    决定是否发送飞书通知
    """
    if state.get("enable_feishu", False):
        return "feishu_notification"
    else:
        return "__end__"
