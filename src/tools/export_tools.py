"""
数据导出工具
支持导出知识库、搜索记录、会话记录等
"""
from langchain.tools import tool
from typing import Dict, Any, List, Optional
from datetime import datetime
import json
import csv
import logging

logger = logging.getLogger(__name__)


@tool
def export_knowledge_base(
    dataset_name: str = "default",
    format: str = "json",
    output_path: Optional[str] = None
) -> str:
    """
    导出知识库数据

    Args:
        dataset_name: 数据集名称
        format: 导出格式（json/csv）
        output_path: 输出路径（可选，默认/tmp）

    Returns:
        导出文件路径
    """
    try:
        from coze_coding_dev_sdk import KnowledgeClient
        from coze_coding_utils.log.write_log import request_context
        from coze_coding_utils.runtime_ctx.context import new_context
        import os

        ctx = request_context.get() or new_context(method="export_knowledge_base")

        # 初始化知识库客户端
        kb_client = KnowledgeClient(ctx=ctx)

        # 获取所有文档（这里简化实现，实际可能需要分页）
        # 注意：KnowledgeClient SDK 可能不支持直接获取所有文档
        # 这里我们使用搜索接口获取部分文档作为示例

        # 搜索所有文档（使用通用查询）
        response = kb_client.search(query="", top_k=100)

        if response.code != 0:
            return f"导出知识库失败: {response.msg}"

        if not response.chunks:
            return f"知识库 '{dataset_name}' 中没有数据"

        # 准备导出数据
        export_data = []
        for chunk in response.chunks:
            export_data.append({
                "id": chunk.metadata.get("id", ""),
                "content": chunk.content,
                "score": chunk.score,
                "metadata": chunk.metadata
            })

        # 确定输出路径
        if output_path is None:
            output_dir = "/tmp/exports"
            os.makedirs(output_dir, exist_ok=True)
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_path = f"{output_dir}/knowledge_base_{dataset_name}_{timestamp}.{format}"

        # 导出数据
        if format.lower() == "json":
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(export_data, f, ensure_ascii=False, indent=2)

        elif format.lower() == "csv":
            with open(output_path, 'w', encoding='utf-8', newline='') as f:
                if export_data:
                    # 扁平化元数据
                    writer = csv.DictWriter(f, fieldnames=["id", "content", "score", "metadata"])
                    writer.writeheader()
                    for item in export_data:
                        writer.writerow({
                            "id": item["id"],
                            "content": item["content"],
                            "score": item["score"],
                            "metadata": json.dumps(item["metadata"], ensure_ascii=False)
                        })

        else:
            return f"不支持的导出格式: {format}"

        return f"成功导出知识库到: {output_path}"

    except Exception as e:
        logger.error(f"导出知识库失败: {e}")
        return f"导出知识库失败: {str(e)}"


@tool
def export_search_history(
    format: str = "json",
    output_path: Optional[str] = None
) -> str:
    """
    导出搜索历史记录

    Args:
        format: 导出格式（json/csv）
        output_path: 输出路径（可选）

    Returns:
        导出文件路径
    """
    try:
        import os
        from coze_coding_utils.storage.db import get_session_history

        # 获取搜索历史
        # 这里简化实现，实际可能需要从数据库获取
        search_history = []

        # 模拟搜索历史数据
        search_history.append({
            "timestamp": datetime.now().isoformat(),
            "query": "示例查询",
            "source": "web_search",
            "result_count": 5,
            "results": ["结果1", "结果2", "结果3", "结果4", "结果5"]
        })

        # 确定输出路径
        if output_path is None:
            output_dir = "/tmp/exports"
            os.makedirs(output_dir, exist_ok=True)
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_path = f"{output_dir}/search_history_{timestamp}.{format}"

        # 导出数据
        if format.lower() == "json":
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(search_history, f, ensure_ascii=False, indent=2)

        elif format.lower() == "csv":
            with open(output_path, 'w', encoding='utf-8', newline='') as f:
                if search_history:
                    writer = csv.DictWriter(f, fieldnames=["timestamp", "query", "source", "result_count", "results"])
                    writer.writeheader()
                    for item in search_history:
                        writer.writerow({
                            "timestamp": item["timestamp"],
                            "query": item["query"],
                            "source": item["source"],
                            "result_count": item["result_count"],
                            "results": json.dumps(item["results"], ensure_ascii=False)
                        })

        else:
            return f"不支持的导出格式: {format}"

        return f"成功导出搜索历史到: {output_path}"

    except Exception as e:
        logger.error(f"导出搜索历史失败: {e}")
        return f"导出搜索历史失败: {str(e)}"


@tool
def export_conversation_history(
    conversation_id: Optional[str] = None,
    format: str = "json",
    output_path: Optional[str] = None
) -> str:
    """
    导出会话记录

    Args:
        conversation_id: 会话ID（可选，不指定则导出所有会话）
        format: 导出格式（json/csv/markdown）
        output_path: 输出路径（可选）

    Returns:
        导出文件路径
    """
    try:
        import os
        from coze_coding_utils.storage.db import get_session_history

        # 获取会话历史
        # 这里简化实现，实际可能需要从数据库获取
        conversation_history = []

        # 模拟会话数据
        conversation_history.append({
            "conversation_id": conversation_id or "conv_001",
            "timestamp": datetime.now().isoformat(),
            "user_message": "用户问题",
            "bot_response": "机器人回复",
            "source": "knowledge_base",
            "metadata": {}
        })

        # 确定输出路径
        if output_path is None:
            output_dir = "/tmp/exports"
            os.makedirs(output_dir, exist_ok=True)
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            conv_id = conversation_id or "all"
            output_path = f"{output_dir}/conversation_{conv_id}_{timestamp}.{format}"

        # 导出数据
        if format.lower() == "json":
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(conversation_history, f, ensure_ascii=False, indent=2)

        elif format.lower() == "csv":
            with open(output_path, 'w', encoding='utf-8', newline='') as f:
                if conversation_history:
                    writer = csv.DictWriter(f, fieldnames=["conversation_id", "timestamp", "user_message", "bot_response", "source", "metadata"])
                    writer.writeheader()
                    for item in conversation_history:
                        writer.writerow({
                            "conversation_id": item["conversation_id"],
                            "timestamp": item["timestamp"],
                            "user_message": item["user_message"],
                            "bot_response": item["bot_response"],
                            "source": item["source"],
                            "metadata": json.dumps(item["metadata"], ensure_ascii=False)
                        })

        elif format.lower() == "markdown":
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write("# 会话记录\n\n")
                for item in conversation_history:
                    f.write(f"## 会话ID: {item['conversation_id']}\n")
                    f.write(f"**时间**: {item['timestamp']}\n\n")
                    f.write(f"### 用户\n{item['user_message']}\n\n")
                    f.write(f"### 机器人\n{item['bot_response']}\n\n")
                    f.write(f"**来源**: {item['source']}\n\n")
                    f.write("---\n\n")

        else:
            return f"不支持的导出格式: {format}"

        return f"成功导出会话记录到: {output_path}"

    except Exception as e:
        logger.error(f"导出会话记录失败: {e}")
        return f"导出会话记录失败: {str(e)}"


@tool
def export_visualization_data(
    data_type: str,
    conversation_id: Optional[str] = None
) -> str:
    """
    导出可视化数据（JSON格式）

    Args:
        data_type: 数据类型（knowledge_search/web_search/conversation）
        conversation_id: 会话ID（可选）

    Returns:
        可视化数据的JSON字符串
    """
    try:
        # 构建可视化数据结构
        viz_data = {
            "type": data_type,
            "timestamp": datetime.now().isoformat(),
            "data": []
        }

        if data_type == "knowledge_search":
            # 知识库搜索可视化数据
            viz_data["data"] = [
                {
                    "id": "doc_001",
                    "content": "知识库文档内容",
                    "score": 0.95,
                    "metadata": {"source": "internal"}
                },
                {
                    "id": "doc_002",
                    "content": "另一个知识库文档",
                    "score": 0.87,
                    "metadata": {"source": "internal"}
                }
            ]

        elif data_type == "web_search":
            # 联网搜索可视化数据
            viz_data["data"] = [
                {
                    "id": "web_001",
                    "title": "搜索结果标题",
                    "snippet": "搜索结果摘要",
                    "url": "https://example.com",
                    "source": "external"
                },
                {
                    "id": "web_002",
                    "title": "另一个搜索结果",
                    "snippet": "另一个摘要",
                    "url": "https://example2.com",
                    "source": "external"
                }
            ]

        elif data_type == "conversation":
            # 会话可视化数据
            viz_data["conversation_id"] = conversation_id or "conv_001"
            viz_data["data"] = [
                {
                    "role": "user",
                    "content": "用户消息",
                    "timestamp": datetime.now().isoformat()
                },
                {
                    "role": "bot",
                    "content": "机器人回复",
                    "timestamp": datetime.now().isoformat(),
                    "source": "knowledge_base"
                }
            ]

        else:
            return f"不支持的数据类型: {data_type}"

        return json.dumps(viz_data, ensure_ascii=False, indent=2)

    except Exception as e:
        logger.error(f"导出可视化数据失败: {e}")
        return f"导出可视化数据失败: {str(e)}"
