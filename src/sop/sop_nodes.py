"""
SOP流程节点
当用户命中SOP知识后，进入SOP流程节点
"""
import logging
from typing import Dict, Any
from src.workflow.state import WorkflowState
from src.workflow.config import get_workflow_config
from src.sop.knowledge_manager import get_sop_manager, ContentType
from src.sop.rich_text_formatter import format_rich_content

logger = logging.getLogger(__name__)


def _add_debug_info(state: WorkflowState, step_name: str, info: str):
    """添加调试信息"""
    if state.get("debug_mode", False):
        debug_info = state.get("debug_info", [])
        debug_info.append(f"[{step_name}] {info}")
        state["debug_info"] = debug_info
    state["current_step"] = step_name
    logger.info(f"[{step_name}] {info}")


def sop_match_node(state: WorkflowState) -> WorkflowState:
    """
    SOP匹配节点
    检查用户输入是否命中SOP知识
    """
    _add_debug_info(state, "sop_match", "开始SOP匹配")

    try:
        user_input = state["user_input"]
        sop_manager = get_sop_manager()

        # 匹配SOP知识
        matched_sop = sop_manager.match_knowledge(user_input)

        if matched_sop:
            state["sop_matched"] = True
            state["sop_id"] = matched_sop.id
            state["sop_name"] = matched_sop.name
            state["sop_content"] = matched_sop.content
            state["sop_content_type"] = matched_sop.content_type.value
            state["sop_flow_config"] = matched_sop.flow_config

            _add_debug_info(state, "sop_match", f"匹配到SOP知识: {matched_sop.name}")
        else:
            state["sop_matched"] = False
            state["sop_id"] = None
            state["sop_name"] = None
            state["sop_content"] = None
            state["sop_content_type"] = None
            state["sop_flow_config"] = None

            _add_debug_info(state, "sop_match", "未匹配到SOP知识")

    except Exception as e:
        logger.error(f"SOP匹配失败: {e}")
        state["sop_matched"] = False
        _add_debug_info(state, "sop_match", f"SOP匹配失败: {str(e)}")

    return state


def sop_execute_node(state: WorkflowState) -> WorkflowState:
    """
    SOP执行节点
    执行SOP流程并生成响应
    """
    _add_debug_info(state, "sop_execute", "开始执行SOP流程")

    try:
        if not state.get("sop_matched"):
            # 没有匹配到SOP，跳过
            _add_debug_info(state, "sop_execute", "未匹配到SOP，跳过执行")
            return state

        sop_content = state.get("sop_content", {})
        sop_content_type = state.get("sop_content_type", ContentType.TEXT.value)
        sop_flow_config = state.get("sop_flow_config", {})

        # 根据内容类型格式化输出
        if sop_content_type == ContentType.TEXT.value:
            # 纯文本内容
            answer = format_text_content(sop_content)

        elif sop_content_type == ContentType.RICH_TEXT.value:
            # 富文本内容
            answer = format_rich_content(sop_content)

        elif sop_content_type == ContentType.IMAGE.value:
            # 图片内容
            answer = format_image_content(sop_content)

        elif sop_content_type == ContentType.VIDEO.value:
            # 视频内容
            answer = format_video_content(sop_content)

        elif sop_content_type == ContentType.SHORT_LINK.value:
            # 短链内容
            answer = format_short_link_content(sop_content)

        elif sop_content_type == ContentType.MIXED.value:
            # 混合内容
            answer = format_mixed_content(sop_content)

        else:
            answer = "不支持的SOP内容类型"

        # 执行SOP流程步骤（如果有）
        if sop_flow_config and "steps" in sop_flow_config:
            steps = sop_flow_config["steps"]
            _add_debug_info(state, "sop_execute", f"执行SOP流程，共 {len(steps)} 个步骤")

            # 这里可以根据步骤执行具体操作
            # 目前只是记录日志
            for i, step in enumerate(steps, 1):
                logger.info(f"SOP步骤 {i}: {step.get('action')} - {step.get('message')}")

        # 生成最终答案
        state["final_answer"] = answer
        state["answer_source"] = "sop"

        _add_debug_info(state, "sop_execute", f"SOP执行完成，内容类型: {sop_content_type}")

    except Exception as e:
        logger.error(f"SOP执行失败: {e}")
        state["final_answer"] = f"SOP执行失败: {str(e)}"
        state["answer_source"] = "error"
        _add_debug_info(state, "sop_execute", f"SOP执行失败: {str(e)}")

    return state


def format_text_content(content: Dict[str, Any]) -> str:
    """格式化文本内容"""
    title = content.get("title", "")
    text = content.get("text", "")

    parts = []
    if title:
        parts.append(f"## {title}\n")
    if text:
        parts.append(text)

    return "\n".join(parts)


def format_image_content(content: Dict[str, Any]) -> str:
    """格式化图片内容"""
    title = content.get("title", "")
    image_url = content.get("image_url", "")
    caption = content.get("caption", "")

    parts = []
    if title:
        parts.append(f"## {title}\n")
    if image_url:
        parts.append(f"![图片]({image_url})\n")
    if caption:
        parts.append(f"*{caption}*\n")

    return "\n".join(parts)


def format_video_content(content: Dict[str, Any]) -> str:
    """格式化视频内容"""
    title = content.get("title", "")
    video_url = content.get("video_url", "")
    caption = content.get("caption", "")

    parts = []
    if title:
        parts.append(f"## {title}\n")
    if video_url:
        parts.append(f"📹 [视频链接]({video_url})\n")
    if caption:
        parts.append(f"*{caption}*\n")

    return "\n".join(parts)


def format_short_link_content(content: Dict[str, Any]) -> str:
    """格式化短链内容"""
    title = content.get("title", "")
    short_link = content.get("short_link", "")
    link_text = content.get("link_text", "点击访问")

    parts = []
    if title:
        parts.append(f"## {title}\n")
    if short_link:
        parts.append(f"[{link_text}]({short_link})\n")

    return "\n".join(parts)


def format_mixed_content(content: Dict[str, Any]) -> str:
    """格式化混合内容"""
    sections = content.get("sections", [])
    parts = []

    for section in sections:
        section_type = section.get("type")
        section_content = section.get("content", "")

        if section_type == "text":
            parts.append(section_content)

        elif section_type == "image":
            url = section.get("url", "")
            caption = section.get("caption", "")
            if url:
                parts.append(f"\n![图片]({url})\n")
                if caption:
                    parts.append(f"*{caption}*\n")

        elif section_type == "video":
            url = section.get("url", "")
            caption = section.get("caption", "")
            if url:
                parts.append(f"\n📹 [视频链接]({url})\n")
                if caption:
                    parts.append(f"*{caption}*\n")

        elif section_type == "short_link":
            url = section.get("url", "")
            text = section.get("text", "点击访问")
            if url:
                parts.append(f"\n[{text}]({url})\n")

        parts.append("\n---\n")

    return "\n".join(parts)
