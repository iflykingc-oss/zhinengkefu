"""
测试辅助函数
用于直接调用工具的内部逻辑进行测试
"""
import logging

logger = logging.getLogger(__name__)


def rag_retrieve_and_generate_direct(
    query: str,
    dataset_name: str = "default",
    top_k: int = 5,
    min_score: float = 0.5,
    include_content: bool = True
) -> str:
    """
    RAG检索增强生成（直接调用版本）

    Args:
        query: 用户问题
        dataset_name: 数据集名称
        top_k: 返回结果数量
        min_score: 最小相似度阈值
        include_content: 是否在答案中引用检索内容

    Returns:
        生成的答案
    """
    try:
        from coze_coding_dev_sdk import KnowledgeClient, LLMClient
        from coze_coding_utils.log.write_log import request_context
        from coze_coding_utils.runtime_ctx.context import new_context
        from langchain_core.messages import SystemMessage, HumanMessage

        ctx = request_context.get() or new_context(method="rag_retrieve_and_generate")

        # 步骤1：检索知识库
        kb_client = KnowledgeClient(ctx=ctx)
        response = kb_client.search(
            query=query,
            top_k=top_k,
            min_score=min_score
        )

        # 步骤2：构建检索结果
        retrieved_docs = []
        if response and hasattr(response, 'data'):
            for doc in response.data[:top_k]:
                retrieved_docs.append({
                    "content": doc.get("content", ""),
                    "metadata": doc.get("metadata", {}),
                    "score": doc.get("score", 0)
                })

        # 步骤3：如果没有检索到文档，返回提示
        if not retrieved_docs:
            return f"未在知识库中找到与'{query}'相关的信息。"

        # 步骤4：构建上下文
        context_parts = []
        for i, doc in enumerate(retrieved_docs, 1):
            content = doc.get("content", "")
            score = doc.get("score", 0)
            context_parts.append(f"【文档{i}】(相似度: {score:.2f})\n{content}")

        context = "\n\n".join(context_parts)

        # 步骤5：使用LLM生成答案
        llm_client = LLMClient(ctx=ctx)

        system_prompt = """你是一个专业的智能客服助手。

请根据提供的知识库文档回答用户问题。
如果文档中包含答案，请基于文档回答并引用文档编号。
如果文档中没有答案，请告知用户知识库中暂无此信息。"""

        if include_content:
            human_message = f"知识库参考：\n{context}\n\n用户问题：{query}"
        else:
            human_message = f"用户问题：{query}\n\n（已检索到 {len(retrieved_docs)} 篇相关文档）"

        messages = [
            SystemMessage(content=system_prompt),
            HumanMessage(content=human_message)
        ]

        # 调用LLM生成答案
        llm_response = llm_client.invoke(
            messages=messages,
            model="doubao-seed-1-8-251228",
            temperature=0.7
        )

        # 获取响应内容
        if hasattr(llm_response, 'content'):
            content = llm_response.content
        else:
            content = str(llm_response)

        # 如果内容是列表，提取文本
        if isinstance(content, list):
            if content and isinstance(content[0], str):
                content = " ".join(content)
            else:
                text_parts = [item.get("text", "") for item in content if isinstance(item, dict)]
                content = " ".join(text_parts)

        answer = str(content)

        return answer

    except Exception as e:
        logger.error(f"RAG检索生成失败: {e}")
        import traceback
        logger.error(f"Traceback: {traceback.format_exc()}")
        return f"RAG检索生成失败: {str(e)}"


def rag_retrieve_only_direct(
    query: str,
    dataset_name: str = "default",
    top_k: int = 5,
    min_score: float = 0.5
) -> str:
    """
    仅RAG检索（直接调用版本）

    Args:
        query: 用户问题
        dataset_name: 数据集名称
        top_k: 返回结果数量
        min_score: 最小相似度阈值

    Returns:
        检索结果文本
    """
    try:
        from coze_coding_dev_sdk import KnowledgeClient
        from coze_coding_utils.log.write_log import request_context
        from coze_coding_utils.runtime_ctx.context import new_context

        ctx = request_context.get() or new_context(method="rag_retrieve_only")

        # 检索知识库
        kb_client = KnowledgeClient(ctx=ctx)
        response = kb_client.search(
            query=query,
            top_k=top_k,
            min_score=min_score
        )

        # 构建检索结果
        if not response or not hasattr(response, 'data') or not response.data:
            return f"未在知识库中找到与'{query}'相关的信息。"

        results = []
        for i, doc in enumerate(response.data[:top_k], 1):
            content = doc.get("content", "")
            score = doc.get("score", 0)
            metadata = doc.get("metadata", {})

            result = f"【文档{i}】相似度: {score:.2f}\n内容: {content}\n"
            if metadata:
                result += f"元数据: {metadata}\n"

            results.append(result)

        return "\n".join(results)

    except Exception as e:
        logger.error(f"RAG检索失败: {e}")
        return f"RAG检索失败: {str(e)}"


def export_knowledge_base_direct(format: str = "json") -> str:
    """
    导出知识库（直接调用版本）

    Args:
        format: 导出格式

    Returns:
        导出结果
    """
    try:
        from src.sop.knowledge_manager import get_sop_manager
        import json
        import io

        sop_manager = get_sop_manager()
        sop_list = sop_manager.list_knowledge()

        if format == "json":
            data = [sop.to_dict() for sop in sop_list]
            return json.dumps(data, ensure_ascii=False, indent=2)

        elif format == "csv":
            import csv
            output = io.StringIO()
            writer = csv.writer(output)

            # 写入表头
            writer.writerow(["ID", "名称", "内容类型", "触发关键词", "创建时间"])

            # 写入数据
            for sop in sop_list:
                writer.writerow([
                    sop.id,
                    sop.name,
                    sop.content_type.value,
                    ",".join(sop.trigger_keywords),
                    sop.created_at
                ])

            return output.getvalue()

        else:
            return "不支持的导出格式"

    except Exception as e:
        logger.error(f"导出知识库失败: {e}")
        return f"导出知识库失败: {str(e)}"


def export_search_history_direct(format: str = "json") -> str:
    """
    导出搜索记录（直接调用版本）

    Args:
        format: 导出格式

    Returns:
        导出结果
    """
    # 模拟数据
    mock_data = [
        {"query": "退款流程", "timestamp": "2024-01-01 10:00:00", "source": "knowledge_base"},
        {"query": "产品价格", "timestamp": "2024-01-01 11:00:00", "source": "web_search"}
    ]

    try:
        import json
        import io
        import csv

        if format == "json":
            return json.dumps(mock_data, ensure_ascii=False, indent=2)

        elif format == "csv":
            output = io.StringIO()
            writer = csv.writer(output)
            writer.writerow(["查询", "时间", "来源"])

            for item in mock_data:
                writer.writerow([item["query"], item["timestamp"], item["source"]])

            return output.getvalue()

        elif format == "markdown":
            lines = ["# 搜索记录\n\n"]
            for item in mock_data:
                lines.append(f"- {item['timestamp']} - {item['query']} ({item['source']})\n")

            return "".join(lines)

        else:
            return "不支持的导出格式"

    except Exception as e:
        logger.error(f"导出搜索记录失败: {e}")
        return f"导出搜索记录失败: {str(e)}"


def export_conversation_history_direct(format: str = "json") -> str:
    """
    导出会话记录（直接调用版本）

    Args:
        format: 导出格式

    Returns:
        导出结果
    """
    # 模拟数据
    mock_data = [
        {"user": "怎么退款？", "bot": "请按照以下流程操作...", "timestamp": "2024-01-01 10:00:00"},
        {"user": "产品价格", "bot": "我们的产品价格...", "timestamp": "2024-01-01 11:00:00"}
    ]

    try:
        import json
        import io
        import csv

        if format == "json":
            return json.dumps(mock_data, ensure_ascii=False, indent=2)

        elif format == "csv":
            output = io.StringIO()
            writer = csv.writer(output)
            writer.writerow(["用户", "机器人", "时间"])

            for item in mock_data:
                writer.writerow([item["user"], item["bot"], item["timestamp"]])

            return output.getvalue()

        elif format == "markdown":
            lines = ["# 会话记录\n\n"]
            for item in mock_data:
                lines.append(f"## {item['timestamp']}\n\n")
                lines.append(f"**用户**: {item['user']}\n\n")
                lines.append(f"**机器人**: {item['bot']}\n\n")
                lines.append("---\n\n")

            return "".join(lines)

        else:
            return "不支持的导出格式"

    except Exception as e:
        logger.error(f"导出会话记录失败: {e}")
        return f"导出会话记录失败: {str(e)}"


def export_visualization_data_direct(format: str = "json") -> str:
    """
    导出可视化数据（直接调用版本）

    Args:
        format: 导出格式

    Returns:
        导出结果
    """
    mock_data = {
        "total_queries": 100,
        "rag_queries": 30,
        "sop_matches": 15,
        "knowledge_queries": 40,
        "web_queries": 25,
        "timeline": {
            "2024-01-01": 10,
            "2024-01-02": 15,
            "2024-01-03": 20
        }
    }

    try:
        import json

        if format == "json":
            return json.dumps(mock_data, ensure_ascii=False, indent=2)

        else:
            return "不支持的导出格式"

    except Exception as e:
        logger.error(f"导出可视化数据失败: {e}")
        return f"导出可视化数据失败: {str(e)}"
