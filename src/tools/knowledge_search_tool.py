"""
知识库搜索工具
用于在知识库中搜索相关信息
"""
from langchain.tools import tool
from coze_coding_dev_sdk import KnowledgeClient
from coze_coding_utils.log.write_log import request_context
from coze_coding_utils.runtime_ctx.context import new_context


@tool
def search_knowledge_base(query: str) -> str:
    """
    在知识库中搜索相关信息

    Args:
        query: 搜索关键词或问题

    Returns:
        搜索结果，包含相关内容和相似度分数
    """
    # 获取上下文，优先从请求上下文获取以保持链路透传
    ctx = request_context.get() or new_context(method="search_knowledge_base")

    # 初始化知识库客户端
    client = KnowledgeClient(ctx=ctx)

    try:
        # 调用知识库搜索API
        response = client.search(
            query=query,
            top_k=5,
            min_score=0.5  # 设置最小相似度阈值，过滤不相关结果
        )

        # 检查响应状态
        if response.code != 0:
            return f"知识库搜索失败: {response.msg}"

        # 如果没有搜索结果
        if not response.chunks:
            return "知识库中未找到相关信息"

        # 格式化搜索结果
        results = []
        for i, chunk in enumerate(response.chunks, 1):
            results.append(f"[结果 {i}] (相似度: {chunk.score:.2f})\n{chunk.content}")

        return "\n\n".join(results)

    except Exception as e:
        return f"知识库搜索异常: {str(e)}"
