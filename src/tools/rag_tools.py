"""
RAG检索工具
支持增强的检索增强生成
"""
from langchain.tools import tool
from coze_coding_dev_sdk import KnowledgeClient, KnowledgeDocument, DataSourceType, LLMClient
from coze_coding_utils.log.write_log import request_context
from coze_coding_utils.runtime_ctx.context import new_context
from langchain_core.messages import SystemMessage, HumanMessage
from typing import List, Dict, Any, Optional
import logging

logger = logging.getLogger(__name__)


@tool
def rag_retrieve_and_generate(
    query: str,
    dataset_name: str = "default",
    top_k: int = 5,
    min_score: float = 0.5,
    include_content: bool = True
) -> str:
    """
    RAG检索增强生成

    先从知识库检索相关文档，然后基于检索结果生成答案

    Args:
        query: 用户问题
        dataset_name: 数据集名称
        top_k: 返回结果数量
        min_score: 最小相似度阈值
        include_content: 是否在答案中引用检索内容

    Returns:
        生成的答案
    """
    ctx = request_context.get() or new_context(method="rag_retrieve_and_generate")

    try:
        # 步骤1：检索知识库
        kb_client = KnowledgeClient(ctx=ctx)
        response = kb_client.search(
            query=query,
            top_k=top_k,
            min_score=min_score
        )

        # 步骤2：构建检索结果
        retrieval_results = []

        if response.code != 0:
            return f"知识库检索失败: {response.msg}"

        if not response.chunks:
            # 没有检索到结果，使用LLM直接回答
            return rag_generate_without_retrieval(query, ctx)

        # 处理检索结果
        for i, chunk in enumerate(response.chunks, 1):
            retrieval_results.append({
                "id": chunk.metadata.get("id", f"doc_{i}"),
                "content": chunk.content,
                "score": chunk.score,
                "metadata": chunk.metadata
            })

        # 步骤3：使用LLM基于检索结果生成答案
        answer = rag_generate_with_retrieval(query, retrieval_results, ctx, include_content)

        # 返回结构化结果
        result = {
            "query": query,
            "answer": answer,
            "retrieved_docs": retrieval_results,
            "source": "rag"
        }

        # 简化输出（如果不需要完整结构）
        return format_rag_result(result, include_content)

    except Exception as e:
        logger.error(f"RAG检索生成失败: {e}")
        return f"RAG检索生成失败: {str(e)}"


def rag_generate_with_retrieval(
    query: str,
    retrieval_results: List[Dict[str, Any]],
    ctx: Any,
    include_content: bool = True
) -> str:
    """
    基于检索结果生成答案

    Args:
        query: 用户问题
        retrieval_results: 检索结果列表
        ctx: 上下文
        include_content: 是否包含检索内容

    Returns:
        生成的答案
    """
    try:
        # 构建上下文
        context_parts = ["参考文档："]

        for i, doc in enumerate(retrieval_results, 1):
            context_parts.append(f"\n【文档{i}】（相似度: {doc['score']:.2f}）")
            context_parts.append(doc['content'])

        context = "\n".join(context_parts)

        # 系统提示词
        system_prompt = """你是一个专业的AI助手，基于检索到的文档回答用户问题。

回答要求：
1. 优先使用检索到的文档中的信息回答
2. 如果文档中没有相关信息，诚实地说明
3. 引用文档时，标注来源（如【文档1】）
4. 回答要准确、简洁、友好
5. 可以适当概括和总结文档内容
"""

        # 构建消息
        messages = [
            SystemMessage(content=system_prompt),
            HumanMessage(content=f"参考文档：\n{context}\n\n用户问题：{query}")
        ]

        # 调用LLM
        llm_client = LLMClient(ctx=ctx)
        response = llm_client.invoke(messages=messages)

        # 提取答案
        if hasattr(response, 'content'):
            answer = str(response.content)
        else:
            answer = str(response)

        return answer

    except Exception as e:
        logger.error(f"基于检索结果生成答案失败: {e}")
        return f"生成答案失败: {str(e)}"


def rag_generate_without_retrieval(query: str, ctx: Any) -> str:
    """
    没有检索结果时，直接使用LLM回答

    Args:
        query: 用户问题
        ctx: 上下文

    Returns:
        生成的答案
    """
    try:
        # 系统提示词
        system_prompt = """你是一个专业的AI助手。

回答要求：
1. 基于你的知识库回答用户问题
2. 如果不确定，诚实地说明
3. 回答要准确、简洁、友好
"""

        # 构建消息
        messages = [
            SystemMessage(content=system_prompt),
            HumanMessage(content=query)
        ]

        # 调用LLM
        llm_client = LLMClient(ctx=ctx)
        response = llm_client.invoke(messages=messages)

        # 提取答案
        if hasattr(response, 'content'):
            answer = str(response.content)
        else:
            answer = str(response)

        return answer

    except Exception as e:
        logger.error(f"直接生成答案失败: {e}")
        return f"生成答案失败: {str(e)}"


def format_rag_result(result: Dict[str, Any], include_content: bool = True) -> str:
    """
    格式化RAG结果

    Args:
        result: RAG结果
        include_content: 是否包含详细内容

    Returns:
        格式化的字符串
    """
    if include_content:
        # 详细格式
        parts = [f"【RAG检索结果】\n"]
        parts.append(f"问题：{result['query']}\n")
        parts.append(f"答案：{result['answer']}\n")

        if result['retrieved_docs']:
            parts.append("\n检索到的文档：\n")
            for i, doc in enumerate(result['retrieved_docs'], 1):
                parts.append(f"\n文档{i}（相似度: {doc['score']:.2f}）：\n")
                parts.append(doc['content'])

        return "\n".join(parts)
    else:
        # 简化格式
        return result['answer']


@tool
def rag_retrieve_only(
    query: str,
    dataset_name: str = "default",
    top_k: int = 5,
    min_score: float = 0.5
) -> str:
    """
    仅检索知识库，不生成答案

    Args:
        query: 用户问题
        dataset_name: 数据集名称
        top_k: 返回结果数量
        min_score: 最小相似度阈值

    Returns:
        检索结果
    """
    ctx = request_context.get() or new_context(method="rag_retrieve_only")

    try:
        # 检索知识库
        kb_client = KnowledgeClient(ctx=ctx)
        response = kb_client.search(
            query=query,
            top_k=top_k,
            min_score=min_score
        )

        if response.code != 0:
            return f"知识库检索失败: {response.msg}"

        if not response.chunks:
            return "知识库中未找到相关文档"

        # 格式化检索结果
        results = []
        for i, chunk in enumerate(response.chunks, 1):
            results.append(f"【文档{i}】（相似度: {chunk.score:.2f}）\n{chunk.content}")

        return "\n\n".join(results)

    except Exception as e:
        logger.error(f"RAG检索失败: {e}")
        return f"RAG检索失败: {str(e)}"


@tool
def rag_add_document(
    content: str,
    dataset_name: str = "default",
    metadata: Optional[Dict[str, Any]] = None
) -> str:
    """
    添加文档到知识库（用于RAG）

    Args:
        content: 文档内容
        dataset_name: 数据集名称
        metadata: 元数据（可选）

    Returns:
        添加结果
    """
    ctx = request_context.get() or new_context(method="rag_add_document")

    try:
        # 创建文档
        doc = KnowledgeDocument(
            source=DataSourceType.TEXT,
            raw_data=content,
            metadata=metadata or {}
        )

        # 添加到知识库
        kb_client = KnowledgeClient(ctx=ctx)
        response = kb_client.add_documents(documents=[doc], table_name=dataset_name)

        if response.code != 0:
            return f"添加文档失败: {response.msg}"

        return f"成功添加文档到数据集 '{dataset_name}'"

    except Exception as e:
        logger.error(f"添加文档失败: {e}")
        return f"添加文档失败: {str(e)}"
