"""
可视化展示API服务
提供数据可视化、统计图表等API接口
"""
from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import JSONResponse
from typing import Dict, Any, Optional, List
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

app = FastAPI(title="智能客服可视化API", version="4.0.0")


# 数据存储（生产环境应使用数据库）
visualization_data = {
    "query_stats": [],
    "rag_results": [],
    "knowledge_stats": {},
    "conversation_stats": []
}


@app.get("/api/v4/stats/overview")
async def get_overview_stats():
    """
    获取概览统计信息

    Returns:
        总体统计数据
    """
    try:
        stats = {
            "total_queries": len(visualization_data["query_stats"]),
            "total_rag_queries": len([r for r in visualization_data["query_stats"] if r.get("use_rag")]),
            "knowledge_queries": len([r for r in visualization_data["query_stats"] if r.get("source") == "knowledge_base"]),
            "web_queries": len([r for r in visualization_data["query_stats"] if r.get("source") == "web_search"]),
            "sop_matches": len([r for r in visualization_data["query_stats"] if r.get("source") == "sop"]),
            "avg_response_time": 0,
            "success_rate": 1.0
        }

        # 计算平均响应时间
        if visualization_data["query_stats"]:
            total_time = sum(r.get("response_time", 0) for r in visualization_data["query_stats"])
            stats["avg_response_time"] = total_time / len(visualization_data["query_stats"])

        # 计算成功率
        if visualization_data["query_stats"]:
            success_count = len([r for r in visualization_data["query_stats"] if r.get("status") == "success"])
            stats["success_rate"] = success_count / len(visualization_data["query_stats"])

        return JSONResponse(content=stats)

    except Exception as e:
        logger.error(f"获取概览统计失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/v4/stats/rag")
async def get_rag_stats():
    """
    获取RAG检索统计

    Returns:
        RAG检索统计数据
    """
    try:
        rag_queries = [r for r in visualization_data["query_stats"] if r.get("use_rag")]

        stats = {
            "total_rag_queries": len(rag_queries),
            "avg_retrieval_time": 0,
            "avg_retrieved_docs": 0,
            "avg_generation_time": 0
        }

        if rag_queries:
            # 计算平均检索时间
            retrieval_times = [r.get("rag_retrieval_time", 0) for r in rag_queries]
            stats["avg_retrieval_time"] = sum(retrieval_times) / len(retrieval_times) if retrieval_times else 0

            # 计算平均检索文档数
            doc_counts = [r.get("rag_doc_count", 0) for r in rag_queries]
            stats["avg_retrieved_docs"] = sum(doc_counts) / len(doc_counts) if doc_counts else 0

            # 计算平均生成时间
            gen_times = [r.get("rag_generation_time", 0) for r in rag_queries]
            stats["avg_generation_time"] = sum(gen_times) / len(gen_times) if gen_times else 0

        return JSONResponse(content=stats)

    except Exception as e:
        logger.error(f"获取RAG统计失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/v4/rag/results")
async def get_rag_results(
    limit: int = Query(10, ge=1, le=100),
    offset: int = Query(0, ge=0)
):
    """
    获取RAG检索结果

    Args:
        limit: 返回数量限制
        offset: 偏移量

    Returns:
        RAG检索结果列表
    """
    try:
        results = visualization_data["rag_results"]
        total = len(results)

        # 分页
        paginated_results = results[offset:offset + limit]

        return JSONResponse(content={
            "total": total,
            "offset": offset,
            "limit": limit,
            "data": paginated_results
        })

    except Exception as e:
        logger.error(f"获取RAG结果失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/v4/knowledge/stats")
async def get_knowledge_stats():
    """
    获取知识库统计

    Returns:
        知识库统计数据
    """
    try:
        from sop.knowledge_manager import get_sop_manager

        sop_manager = get_sop_manager()
        sop_list = sop_manager.list_knowledge()

        stats = {
            "total_sop": len(sop_list),
            "sop_by_type": {},
            "sop_list": []
        }

        # 按类型统计
        for sop in sop_list:
            content_type = sop.content_type.value
            stats["sop_by_type"][content_type] = stats["sop_by_type"].get(content_type, 0) + 1
            stats["sop_list"].append({
                "id": sop.id,
                "name": sop.name,
                "content_type": content_type,
                "trigger_keywords": sop.trigger_keywords,
                "created_at": sop.created_at
            })

        return JSONResponse(content=stats)

    except Exception as e:
        logger.error(f"获取知识库统计失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/v4/conversation/history")
async def get_conversation_history(
    limit: int = Query(10, ge=1, le=100),
    offset: int = Query(0, ge=0)
):
    """
    获取会话历史

    Args:
        limit: 返回数量限制
        offset: 偏移量

    Returns:
        会话历史列表
    """
    try:
        history = visualization_data["conversation_stats"]
        total = len(history)

        # 分页
        paginated_history = history[offset:offset + limit]

        return JSONResponse(content={
            "total": total,
            "offset": offset,
            "limit": limit,
            "data": paginated_history
        })

    except Exception as e:
        logger.error(f"获取会话历史失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/v4/query/timeline")
async def get_query_timeline(
    days: int = Query(7, ge=1, le=30)
):
    """
    获取查询时间线

    Args:
        days: 查询天数

    Returns:
        时间线数据
    """
    try:
        from datetime import timedelta

        timeline = {}
        end_date = datetime.now()

        for i in range(days):
            date = (end_date - timedelta(days=days - 1 - i)).strftime("%Y-%m-%d")
            timeline[date] = {
                "total": 0,
                "knowledge": 0,
                "web": 0,
                "sop": 0,
                "rag": 0
            }

        # 统计每天的查询
        for query in visualization_data["query_stats"]:
            query_date = query.get("timestamp", "")
            if query_date:
                date_str = query_date.split(" ")[0]
                if date_str in timeline:
                    timeline[date_str]["total"] += 1

                    if query.get("source") == "knowledge_base":
                        timeline[date_str]["knowledge"] += 1
                    elif query.get("source") == "web_search":
                        timeline[date_str]["web"] += 1
                    elif query.get("source") == "sop":
                        timeline[date_str]["sop"] += 1

                    if query.get("use_rag"):
                        timeline[date_str]["rag"] += 1

        return JSONResponse(content=timeline)

    except Exception as e:
        logger.error(f"获取查询时间线失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/v4/visualization/record")
async def record_query(data: Dict[str, Any]):
    """
    记录查询数据

    Args:
        data: 查询数据

    Returns:
        记录结果
    """
    try:
        # 添加时间戳
        data["timestamp"] = datetime.now().isoformat()

        # 记录查询统计
        visualization_data["query_stats"].append(data)

        # 如果是RAG查询，记录RAG结果
        if data.get("use_rag") and "rag_result" in data:
            visualization_data["rag_results"].append({
                "query": data.get("query"),
                "retrieved_docs": data.get("rag_retrieved_docs", []),
                "generated_answer": data.get("rag_generated_answer"),
                "timestamp": data["timestamp"]
            })

        # 记录会话数据
        visualization_data["conversation_stats"].append({
            "query": data.get("query"),
            "answer": data.get("answer"),
            "source": data.get("source"),
            "timestamp": data["timestamp"]
        })

        return JSONResponse(content={"status": "success", "message": "记录成功"})

    except Exception as e:
        logger.error(f"记录查询数据失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/v4/visualization/dashboard")
async def get_dashboard_data():
    """
    获取仪表板数据（综合数据）

    Returns:
        仪表板数据
    """
    try:
        from sop.knowledge_manager import get_sop_manager

        # 获取各种统计数据
        overview = await get_overview_stats()
        rag_stats = await get_rag_stats()
        knowledge_stats = await get_knowledge_stats()
        timeline = await get_query_timeline(days=7)

        dashboard_data = {
            "overview": overview.body,
            "rag_stats": rag_stats.body,
            "knowledge_stats": knowledge_stats.body,
            "timeline": timeline.body,
            "workflow_nodes": {
                "input_parser": {"name": "输入解析", "status": "active"},
                "sop_match": {"name": "SOP匹配", "status": "active"},
                "sop_execute": {"name": "SOP执行", "status": "active"},
                "knowledge_search": {"name": "知识库搜索", "status": "active"},
                "web_search": {"name": "联网搜索", "status": "active"},
                "risk_assessment": {"name": "风险评估", "status": "active"},
                "answer_generation": {"name": "答案生成", "status": "active"},
                "feishu_notification": {"name": "飞书通知", "status": "active"}
            }
        }

        return JSONResponse(content=dashboard_data)

    except Exception as e:
        logger.error(f"获取仪表板数据失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/health")
async def health_check():
    """健康检查"""
    return {"status": "healthy", "service": "visualization_api"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8004)
