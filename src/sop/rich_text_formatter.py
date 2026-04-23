"""
富文本/多媒体格式化器
支持图文、短链、视频、富文本等多种格式输出
"""
import logging
from typing import Dict, Any, List, Optional
from enum import Enum

logger = logging.getLogger(__name__)


class OutputFormat(str, Enum):
    """输出格式"""
    MARKDOWN = "markdown"
    HTML = "html"
    JSON = "json"
    PLAIN_TEXT = "plain_text"


class RichTextFormatter:
    """富文本格式化器"""

    def __init__(self, output_format: OutputFormat = OutputFormat.MARKDOWN):
        self.output_format = output_format

    def format(self, content: Dict[str, Any]) -> str:
        """
        格式化内容

        Args:
            content: 内容字典

        Returns:
            格式化后的字符串
        """
        content_type = content.get("type", "text")

        if content_type == "text":
            return self._format_text(content)
        elif content_type == "rich_text":
            return self._format_rich_text(content)
        elif content_type == "image":
            return self._format_image(content)
        elif content_type == "video":
            return self._format_video(content)
        elif content_type == "short_link":
            return self._format_short_link(content)
        elif content_type == "mixed":
            return self._format_mixed(content)
        else:
            return self._format_text(content)

    def _format_text(self, content: Dict[str, Any]) -> str:
        """格式化文本"""
        text = content.get("content", "")

        if self.output_format == OutputFormat.HTML:
            return f"<p>{text}</p>"
        elif self.output_format == OutputFormat.JSON:
            return content.get("json", text)
        else:
            return text

    def _format_rich_text(self, content: Dict[str, Any]) -> str:
        """格式化富文本"""
        title = content.get("title", "")
        text = content.get("content", "")
        image_url = content.get("image_url", "")
        video_url = content.get("video_url", "")
        short_link = content.get("short_link", "")
        link_text = content.get("link_text", "点击访问")

        parts = []

        if title:
            if self.output_format == OutputFormat.HTML:
                parts.append(f"<h2>{title}</h2>")
            else:
                parts.append(f"## {title}\n")

        if text:
            if self.output_format == OutputFormat.HTML:
                parts.append(f"<div class='rich-text'>{text}</div>")
            else:
                parts.append(text)

        if image_url:
            if self.output_format == OutputFormat.HTML:
                parts.append(f"<img src='{image_url}' alt='图片' class='content-image'>")
            else:
                parts.append(f"\n![图片]({image_url})\n")

        if video_url:
            if self.output_format == OutputFormat.HTML:
                parts.append(f"<video src='{video_url}' controls class='content-video'></video>")
            else:
                parts.append(f"\n📹 [视频链接]({video_url})\n")

        if short_link:
            if self.output_format == OutputFormat.HTML:
                parts.append(f"<a href='{short_link}' class='content-link'>{link_text}</a>")
            else:
                parts.append(f"\n[{link_text}]({short_link})\n")

        return "\n".join(parts)

    def _format_image(self, content: Dict[str, Any]) -> str:
        """格式化图片"""
        url = content.get("url", content.get("image_url", ""))
        caption = content.get("caption", "")
        alt = content.get("alt", "图片")

        parts = []

        if self.output_format == OutputFormat.HTML:
            parts.append(f"<div class='image-container'>")
            parts.append(f"<img src='{url}' alt='{alt}' class='content-image'>")
            if caption:
                parts.append(f"<p class='image-caption'>{caption}</p>")
            parts.append("</div>")
        else:
            parts.append(f"\n![{alt}]({url})\n")
            if caption:
                parts.append(f"*{caption}*\n")

        return "\n".join(parts)

    def _format_video(self, content: Dict[str, Any]) -> str:
        """格式化视频"""
        url = content.get("url", content.get("video_url", ""))
        caption = content.get("caption", "")
        poster = content.get("poster", "")

        parts = []

        if self.output_format == OutputFormat.HTML:
            poster_attr = f"poster='{poster}'" if poster else ""
            parts.append(f"<div class='video-container'>")
            parts.append(f"<video src='{url}' controls {poster_attr} class='content-video'></video>")
            if caption:
                parts.append(f"<p class='video-caption'>{caption}</p>")
            parts.append("</div>")
        else:
            parts.append(f"\n📹 [视频链接]({url})\n")
            if caption:
                parts.append(f"*{caption}*\n")

        return "\n".join(parts)

    def _format_short_link(self, content: Dict[str, Any]) -> str:
        """格式化短链"""
        url = content.get("url", content.get("short_link", ""))
        text = content.get("text", content.get("link_text", "点击访问"))
        description = content.get("description", "")

        parts = []

        if self.output_format == OutputFormat.HTML:
            parts.append(f"<div class='link-container'>")
            parts.append(f"<a href='{url}' class='content-link' target='_blank'>{text}</a>")
            if description:
                parts.append(f"<p class='link-description'>{description}</p>")
            parts.append("</div>")
        else:
            parts.append(f"\n[{text}]({url})\n")
            if description:
                parts.append(f"*{description}*\n")

        return "\n".join(parts)

    def _format_mixed(self, content: Dict[str, Any]) -> str:
        """格式化混合内容"""
        sections = content.get("sections", [])
        parts = []

        for section in sections:
            section_type = section.get("type", "text")
            formatted = self._format_section(section_type, section)
            if formatted:
                parts.append(formatted)

            # 添加分隔线
            if self.output_format == OutputFormat.HTML:
                parts.append("<hr class='section-divider'>")
            else:
                parts.append("\n---\n")

        return "\n".join(parts)

    def _format_section(self, section_type: str, section: Dict[str, Any]) -> str:
        """格式化单个区块"""
        if section_type == "text":
            return self._format_text(section)
        elif section_type == "image":
            return self._format_image(section)
        elif section_type == "video":
            return self._format_video(section)
        elif section_type == "short_link":
            return self._format_short_link(section)
        else:
            return self._format_text(section)


def format_rich_content(content: Dict[str, Any], output_format: str = "markdown") -> str:
    """
    格式化富文本内容（便捷函数）

    Args:
        content: 内容字典
        output_format: 输出格式

    Returns:
        格式化后的字符串
    """
    formatter = RichTextFormatter(OutputFormat(output_format))
    return formatter.format(content)


def create_rich_text_response(
    title: str = "",
    text: str = "",
    image_url: str = "",
    video_url: str = "",
    short_link: str = "",
    link_text: str = "点击访问",
    sections: Optional[List[Dict[str, Any]]] = None
) -> Dict[str, Any]:
    """
    创建富文本响应

    Args:
        title: 标题
        text: 文本内容
        image_url: 图片URL
        video_url: 视频URL
        short_link: 短链
        link_text: 链接文本
        sections: 混合内容区块列表

    Returns:
        富文本内容字典
    """
    # 判断内容类型
    if sections:
        return {
            "type": "mixed",
            "sections": sections
        }

    if image_url and video_url:
        # 有图片和视频，使用富文本
        return {
            "type": "rich_text",
            "title": title,
            "content": text,
            "image_url": image_url,
            "video_url": video_url
        }

    if video_url:
        # 只有视频
        return {
            "type": "video",
            "url": video_url,
            "caption": title or text
        }

    if image_url:
        # 只有图片
        return {
            "type": "image",
            "url": image_url,
            "caption": title or text
        }

    if short_link:
        # 只有短链
        return {
            "type": "short_link",
            "url": short_link,
            "text": link_text,
            "description": text
        }

    # 纯文本
    return {
        "type": "text",
        "content": title + "\n\n" + text if title else text
    }
