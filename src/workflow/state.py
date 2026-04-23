"""
工作流状态定义
"""
from typing import TypedDict, Annotated, Optional, List
from langchain_core.messages import AnyMessage, BaseMessage
from langgraph.graph.message import add_messages


class WorkflowState(TypedDict):
    """工作流状态"""
    # 消息历史
    messages: Annotated[List[BaseMessage], add_messages]

    # 用户输入
    user_input: str

    # 多模态信息
    has_image: bool
    image_url: Optional[str]

    # 知识库搜索结果
    knowledge_result: Optional[str]
    knowledge_found: bool

    # 联网搜索结果
    web_result: Optional[str]
    web_found: bool

    # 风险评估
    risk_assessment: Optional[str]
    is_risky: bool

    # 最终答案
    final_answer: Optional[str]
    answer_source: str  # knowledge_base, web_search, llm

    # 调试信息
    debug_mode: bool
    debug_info: List[str]
    current_step: str

    # 飞书通知
    enable_feishu: bool
    feishu_sent: bool

    # 配置
    config_id: Optional[str]
