"""
工作流节点定义
"""
import logging
from typing import Dict, Any
from langchain_core.messages import HumanMessage, AIMessage
from src.workflow.state import WorkflowState
from src.workflow.config import get_workflow_config, NodeStatus

logger = logging.getLogger(__name__)


def _add_debug_info(state: WorkflowState, step_name: str, info: str):
    """添加调试信息"""
    if state.get("debug_mode", False):
        debug_info = state.get("debug_info", [])
        debug_info.append(f"[{step_name}] {info}")
        state["debug_info"] = debug_info
    state["current_step"] = step_name
    logger.info(f"[{step_name}] {info}")


def input_parser_node(state: WorkflowState) -> WorkflowState:
    """
    输入解析节点
    解析用户输入，判断是否包含图片
    """
    _add_debug_info(state, "input_parser", "开始解析用户输入")

    user_input = state["user_input"]
    has_image = state.get("has_image", False)
    image_url = state.get("image_url")

    # 解析输入
    if has_image and image_url:
        _add_debug_info(state, "input_parser", f"检测到图片输入: {image_url}")
        # 构建多模态消息
        message = HumanMessage(content=[
            {"type": "text", "text": user_input},
            {"type": "image_url", "image_url": {"url": image_url}}
        ])
    else:
        _add_debug_info(state, "input_parser", f"纯文本输入: {user_input[:100]}...")
        message = HumanMessage(content=user_input)

    state["messages"] = [message]

    _add_debug_info(state, "input_parser", "输入解析完成")
    return state


def knowledge_search_node(state: WorkflowState) -> WorkflowState:
    """
    知识库搜索节点
    在知识库中搜索相关信息
    """
    config = get_workflow_config()
    node_config = config.get_node_config("knowledge_search")

    _add_debug_info(state, "knowledge_search", "开始知识库搜索")

    if node_config.get("status") == NodeStatus.DISABLED:
        _add_debug_info(state, "knowledge_search", "节点已禁用，跳过")
        state["knowledge_found"] = False
        return state

    try:
        from workflow.tool_helpers import call_knowledge_search

        # 从消息中提取用户问题
        messages = state.get("messages", [])
        user_input = messages[0].content if messages else state["user_input"]

        # 提取纯文本（处理多模态消息）
        if isinstance(user_input, list):
            text_parts = [item.get("text", "") for item in user_input if item.get("type") == "text"]
            query = " ".join(text_parts)
        else:
            query = user_input

        _add_debug_info(state, "knowledge_search", f"搜索查询: {query[:50]}...")

        # 调用知识库搜索
        result = call_knowledge_search(query)

        state["knowledge_result"] = result

        # 判断是否找到结果
        if result and "未找到相关信息" not in result:
            state["knowledge_found"] = True
            _add_debug_info(state, "knowledge_search", f"找到知识库结果，长度: {len(result)} 字符")
        else:
            state["knowledge_found"] = False
            _add_debug_info(state, "knowledge_search", "知识库中未找到相关信息")

    except Exception as e:
        logger.error(f"知识库搜索失败: {e}")
        state["knowledge_found"] = False
        _add_debug_info(state, "knowledge_search", f"搜索失败: {str(e)}")

    return state


def web_search_node(state: WorkflowState) -> WorkflowState:
    """
    联网搜索节点
    在互联网上搜索信息
    """
    config = get_workflow_config()
    node_config = config.get_node_config("web_search")

    _add_debug_info(state, "web_search", "开始联网搜索")

    if node_config.get("status") == NodeStatus.DISABLED:
        _add_debug_info(state, "web_search", "节点已禁用，跳过")
        state["web_found"] = False
        return state

    try:
        from workflow.tool_helpers import call_web_search

        # 从消息中提取用户问题
        messages = state.get("messages", [])
        user_input = messages[0].content if messages else state["user_input"]

        # 提取纯文本（处理多模态消息）
        if isinstance(user_input, list):
            text_parts = [item.get("text", "") for item in user_input if item.get("type") == "text"]
            query = " ".join(text_parts)
        else:
            query = user_input

        _add_debug_info(state, "web_search", f"搜索查询: {query[:50]}...")

        # 调用联网搜索
        result = call_web_search(query)

        state["web_result"] = result

        # 判断是否找到结果
        if result and "未找到相关信息" not in result:
            state["web_found"] = True
            _add_debug_info(state, "web_search", f"找到联网搜索结果，长度: {len(result)} 字符")
        else:
            state["web_found"] = False
            _add_debug_info(state, "web_search", "联网搜索未找到相关信息")

    except Exception as e:
        logger.error(f"联网搜索失败: {e}")
        state["web_found"] = False
        _add_debug_info(state, "web_search", f"搜索失败: {str(e)}")

    return state


def risk_assessment_node(state: WorkflowState) -> WorkflowState:
    """
    风险评估节点
    评估外部信息的风险
    """
    config = get_workflow_config()
    node_config = config.get_node_config("risk_assessment")

    _add_debug_info(state, "risk_assessment", "开始风险评估")

    if node_config.get("status") == NodeStatus.DISABLED:
        _add_debug_info(state, "risk_assessment", "节点已禁用，跳过")
        state["is_risky"] = False
        return state

    web_result = state.get("web_result", "")

    # 如果没有联网搜索结果，则不评估风险
    if not web_result:
        state["is_risky"] = False
        _add_debug_info(state, "risk_assessment", "无外部信息，跳过风险评估")
        return state

    # 简单风险评估逻辑
    risk_indicators = [
        "未知来源",
        "可疑",
        "不安全",
        "无法验证",
        "风险"
    ]

    is_risky = any(indicator in web_result for indicator in risk_indicators)

    if is_risky:
        state["is_risky"] = True
        state["risk_assessment"] = "检测到潜在风险，建议不采纳此信息"
        _add_debug_info(state, "risk_assessment", "检测到风险信息")
    else:
        state["is_risky"] = False
        state["risk_assessment"] = "信息风险评估通过，可以采纳"
        _add_debug_info(state, "risk_assessment", "风险评估通过")

    return state


def answer_generation_node(state: WorkflowState) -> WorkflowState:
    """
    答案生成节点
    生成最终答案
    """
    config = get_workflow_config()
    node_config = config.get_node_config("answer_generation")

    _add_debug_info(state, "answer_generation", "开始生成答案")

    try:
        from coze_coding_dev_sdk import LLMClient
        from langchain_core.messages import SystemMessage, HumanMessage
        from coze_coding_utils.log.write_log import request_context
        from coze_coding_utils.runtime_ctx.context import new_context

        # 获取上下文
        ctx = request_context.get() or new_context(method="answer_generation")

        # 初始化 LLM 客户端
        llm_client = LLMClient(ctx=ctx)

        # 构建提示词
        user_input = state["user_input"]
        knowledge_result = state.get("knowledge_result", "")
        web_result = state.get("web_result", "")
        is_risky = state.get("is_risky", False)
        knowledge_found = state.get("knowledge_found", False)

        # 根据搜索结果构建上下文
        context_parts = []

        if knowledge_found and knowledge_result:
            context_parts.append(f"【知识库参考】\n{knowledge_result}")
            source = "knowledge_base"

        elif web_result and not is_risky:
            context_parts.append(f"【网络搜索参考】\n{web_result}")
            source = "web_search"

        elif web_result and is_risky:
            context_parts.append("【信息风险提醒】搜索到的信息存在风险，无法提供答案")
            source = "llm"

        else:
            source = "llm"

        context = "\n\n".join(context_parts) if context_parts else ""

        # 系统提示词（不向用户展示来源信息）
        system_prompt = """你是一个专业的智能客服助手。

根据提供的参考信息回答用户问题。如果提供了参考信息，请优先基于参考信息回答。
如果没有参考信息或参考信息不可用，请基于你的知识回答。

回答要求：
1. 准确、简洁、友好
2. 直接回答用户问题，不要标注答案来源
3. 如果参考信息不足，可以说明需要更多信息
"""

        # 构建消息 - 使用 LangChain 的消息类型
        messages = [
            SystemMessage(content=system_prompt),
            HumanMessage(content=f"参考信息：\n{context}\n\n用户问题：{user_input}")
        ]

        # 调用LLM生成答案
        response = llm_client.invoke(
            messages=messages,
            model=node_config["config"].get("model", "doubao-seed-1-8-251228"),
            temperature=node_config["config"].get("temperature", 0.7)
        )

        # 安全地获取响应内容
        if hasattr(response, 'content'):
            content = response.content
        else:
            content = str(response)

        # 如果内容是列表，提取文本
        if isinstance(content, list):
            if content and isinstance(content[0], str):
                content = " ".join(content)
            else:
                text_parts = [item.get("text", "") for item in content if isinstance(item, dict)]
                content = " ".join(text_parts)

        answer = str(content)

        state["final_answer"] = answer
        state["answer_source"] = source

        _add_debug_info(state, "answer_generation", f"答案生成完成，来源: {source}")

    except Exception as e:
        import traceback
        logger.error(f"答案生成失败: {e}")
        logger.error(f"Traceback: {traceback.format_exc()}")
        state["final_answer"] = f"抱歉，生成答案时出错: {str(e)}"
        state["answer_source"] = "error"
        _add_debug_info(state, "answer_generation", f"生成失败: {str(e)}")

    return state


def feishu_notification_node(state: WorkflowState) -> WorkflowState:
    """
    飞书通知节点
    发送通知到飞书群组
    """
    config = get_workflow_config()
    node_config = config.get_node_config("feishu_notification")

    _add_debug_info(state, "feishu_notification", "开始飞书通知")

    if node_config.get("status") == NodeStatus.DISABLED:
        _add_debug_info(state, "feishu_notification", "节点已禁用，跳过")
        state["feishu_sent"] = False
        return state

    if not state.get("enable_feishu", False):
        _add_debug_info(state, "feishu_notification", "未启用飞书通知")
        state["feishu_sent"] = False
        return state

    try:
        from tools.feishu_notification_tool import send_feishu_text_message

        user_input = state["user_input"]
        final_answer = state.get("final_answer", "")

        message = f"用户咨询：{user_input}\n回复：{final_answer}"

        result = send_feishu_text_message(message)

        if "成功" in result:
            state["feishu_sent"] = True
            _add_debug_info(state, "feishu_notification", "飞书消息发送成功")
        else:
            state["feishu_sent"] = False
            _add_debug_info(state, "feishu_notification", f"飞书消息发送失败: {result}")

    except Exception as e:
        logger.error(f"飞书通知失败: {e}")
        state["feishu_sent"] = False
        _add_debug_info(state, "feishu_notification", f"发送失败: {str(e)}")

    return state
