"""
工具调用辅助函数
用于在工作流节点中调用工具
"""
from coze_coding_dev_sdk import KnowledgeClient, SearchClient
from coze_coding_utils.log.write_log import request_context
from coze_coding_utils.runtime_ctx.context import new_context


def call_knowledge_search(query: str) -> str:
    """
    调用知识库搜索

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


def call_web_search(query: str) -> str:
    """
    调用联网搜索

    Args:
        query: 搜索关键词或问题

    Returns:
        搜索结果，包含标题、摘要和来源
    """
    # 获取上下文，优先从请求上下文获取以保持链路透传
    ctx = request_context.get() or new_context(method="search_web")

    # 初始化搜索客户端
    client = SearchClient(ctx=ctx)

    try:
        # 调用联网搜索API，启用AI摘要
        response = client.web_search(
            query=query,
            count=5,
            need_summary=True
        )

        # 如果没有搜索结果
        if not response.web_items:
            return "互联网搜索未找到相关信息"

        # 格式化搜索结果
        results = []

        # 添加AI摘要（如果有）
        if response.summary:
            results.append(f"【搜索摘要】\n{response.summary}\n")

        # 添加各个搜索结果
        for i, item in enumerate(response.web_items, 1):
            result = f"【结果 {i}】\n"
            result += f"标题: {item.title}\n"
            result += f"来源: {item.site_name}\n"
            result += f"链接: {item.url}\n"
            result += f"摘要: {item.snippet}\n"

            # 如果有权威度信息，添加到结果中
            if hasattr(item, 'auth_info_des') and item.auth_info_des:
                result += f"权威度: {item.auth_info_des}\n"

            results.append(result)

        return "\n".join(results)

    except Exception as e:
        return f"联网搜索异常: {str(e)}"
