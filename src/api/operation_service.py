"""
运营后台API服务
提供运营配置管理、日志导出、SOP流程画布等API接口
"""
from fastapi import FastAPI, HTTPException, Query, Body
from fastapi.responses import JSONResponse
from typing import Dict, Any, List, Optional
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

app = FastAPI(title="智能客服运营后台API", version="5.0.0")


# ==================== 配置管理接口 ====================

@app.get("/api/v5/config")
async def get_full_config():
    """获取完整配置"""
    try:
        from src.config.operation_config import get_operation_config
        config = get_operation_config()
        return JSONResponse(content=config.get_full_config())
    except Exception as e:
        logger.error(f"获取配置失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.put("/api/v5/config")
async def update_config(config_data: Dict[str, Any] = Body(...)):
    """更新配置"""
    try:
        from src.config.operation_config import get_operation_config
        config_manager = get_operation_config()
        config_manager.update_config(config_data)
        return JSONResponse(content={"status": "success", "message": "配置更新成功"})
    except Exception as e:
        logger.error(f"更新配置失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/v5/config/{path:path}")
async def get_config_value(path: str):
    """获取配置值"""
    try:
        from src.config.operation_config import get_operation_config
        config = get_operation_config()
        value = config.get(path)
        if value is None:
            raise HTTPException(status_code=404, detail=f"配置路径不存在: {path}")
        return JSONResponse(content={"path": path, "value": value})
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"获取配置值失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.put("/api/v5/config/{path:path}")
async def set_config_value(path: str, value: Any = Body(...)):
    """设置配置值"""
    try:
        from src.config.operation_config import get_operation_config
        config = get_operation_config()
        config.set(path, value)
        return JSONResponse(content={"status": "success", "message": f"配置 {path} 已更新"})
    except Exception as e:
        logger.error(f"设置配置值失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ==================== 开场白管理接口 ====================

@app.get("/api/v5/greeting/messages")
async def get_greeting_messages():
    """获取开场白列表"""
    try:
        from src.config.operation_config import get_operation_config
        config = get_operation_config()
        messages = config.get("greeting.messages", [])
        return JSONResponse(content={"messages": messages})
    except Exception as e:
        logger.error(f"获取开场白列表失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/v5/greeting/messages")
async def add_greeting_message(message: str = Body(..., embed=True)):
    """添加开场白"""
    try:
        from ops.greeting import GreetingManager
        manager = GreetingManager()
        manager.add_greeting(message)
        return JSONResponse(content={"status": "success", "message": "开场白添加成功"})
    except Exception as e:
        logger.error(f"添加开场白失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.delete("/api/v5/greeting/messages")
async def remove_greeting_message(message: str = Query(...)):
    """移除开场白"""
    try:
        from ops.greeting import GreetingManager
        manager = GreetingManager()
        manager.remove_greeting(message)
        return JSONResponse(content={"status": "success", "message": "开场白移除成功"})
    except Exception as e:
        logger.error(f"移除开场白失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ==================== 闲聊管理接口 ====================

@app.get("/api/v5/chitchat/intents")
async def get_chitchat_intents():
    """获取闲聊意图列表"""
    try:
        from src.config.operation_config import get_operation_config
        config = get_operation_config()
        intents = config.get("chitchat.intents", [])
        return JSONResponse(content={"intents": intents})
    except Exception as e:
        logger.error(f"获取闲聊意图列表失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/v5/chitchat/intents")
async def add_chitchat_intent(
    intent: str = Body(...),
    keywords: List[str] = Body(...),
    responses: List[str] = Body(...)
):
    """添加闲聊意图"""
    try:
        from ops.chitchat import ChitchatManager
        manager = ChitchatManager()
        manager.add_intent(intent, keywords, responses)
        return JSONResponse(content={"status": "success", "message": "闲聊意图添加成功"})
    except Exception as e:
        logger.error(f"添加闲聊意图失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.delete("/api/v5/chitchat/intents/{intent}")
async def remove_chitchat_intent(intent: str):
    """移除闲聊意图"""
    try:
        from ops.chitchat import ChitchatManager
        manager = ChitchatManager()
        manager.remove_intent(intent)
        return JSONResponse(content={"status": "success", "message": "闲聊意图移除成功"})
    except Exception as e:
        logger.error(f"移除闲聊意图失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ==================== 转人工策略接口 ====================

@app.get("/api/v5/transfer/strategies")
async def get_transfer_strategies():
    """获取转人工策略列表"""
    try:
        from src.config.operation_config import get_operation_config
        config = get_operation_config()
        strategies = config.get("transfer_to_human.strategies", [])
        return JSONResponse(content={"strategies": strategies})
    except Exception as e:
        logger.error(f"获取转人工策略列表失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.put("/api/v5/transfer/strategies/{strategy_type}")
async def update_transfer_strategy(
    strategy_type: str,
    config: Dict[str, Any] = Body(...)
):
    """更新转人工策略"""
    try:
        from src.config.operation_config import get_operation_config
        config_manager = get_operation_config()
        config_manager.update_transfer_strategy(strategy_type, config)
        return JSONResponse(content={"status": "success", "message": f"转人工策略 {strategy_type} 已更新"})
    except Exception as e:
        logger.error(f"更新转人工策略失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/v5/transfer/channels")
async def get_transfer_channels():
    """获取转人工渠道"""
    try:
        from ops.human_handoff import HumanHandoffManager
        manager = HumanHandoffManager()
        channels = manager.get_transfer_channels()
        default = manager.get_default_channel()
        return JSONResponse(content={"channels": channels, "default": default})
    except Exception as e:
        logger.error(f"获取转人工渠道失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ==================== SOP流程接口 ====================

@app.get("/api/v5/sop/knowledge")
async def get_sop_knowledge():
    """获取SOP知识库"""
    try:
        from sop.knowledge_manager import get_sop_manager
        manager = get_sop_manager()
        sop_list = manager.list_knowledge()
        return JSONResponse(content={"sop_list": [sop.to_dict() for sop in sop_list]})
    except Exception as e:
        logger.error(f"获取SOP知识库失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/v5/sop/knowledge")
async def add_sop_knowledge(sop_data: Dict[str, Any] = Body(...)):
    """添加SOP知识"""
    try:
        from sop.knowledge_manager import get_sop_manager, SOPKnowledge, ContentType
        manager = get_sop_manager()

        sop = SOPKnowledge(
            id=sop_data.get("id", f"sop_{datetime.now().timestamp()}"),
            name=sop_data["name"],
            trigger_keywords=sop_data["trigger_keywords"],
            content_type=ContentType(sop_data["content_type"]),
            content=sop_data["content"],
            flow_config=sop_data.get("flow_config", {}),
            metadata=sop_data.get("metadata", {})
        )

        manager.add_knowledge(sop)
        return JSONResponse(content={"status": "success", "message": "SOP知识添加成功"})
    except Exception as e:
        logger.error(f"添加SOP知识失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.delete("/api/v5/sop/knowledge/{sop_id}")
async def delete_sop_knowledge(sop_id: str):
    """删除SOP知识"""
    try:
        from sop.knowledge_manager import get_sop_manager
        manager = get_sop_manager()
        success = manager.remove_knowledge(sop_id)
        if not success:
            raise HTTPException(status_code=404, detail=f"SOP知识不存在: {sop_id}")
        return JSONResponse(content={"status": "success", "message": "SOP知识删除成功"})
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"删除SOP知识失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ==================== 日志导出接口 ====================

@app.get("/api/v5/export/conversations")
async def export_conversations(
    format: str = Query("json", regex="^(json|csv|markdown)$"),
    conversation_id: Optional[str] = Query(None),
    start_date: Optional[str] = Query(None),
    end_date: Optional[str] = Query(None)
):
    """导出会话日志"""
    try:
        from tools.export_tools import export_conversation_history
        result = export_conversation_history(
            conversation_id=conversation_id,
            format=format
        )
        return JSONResponse(content={"result": result})
    except Exception as e:
        logger.error(f"导出会话日志失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/v5/export/search_history")
async def export_search_history(
    format: str = Query("json", regex="^(json|csv|markdown)$")
):
    """导出搜索日志"""
    try:
        from tools.export_tools import export_search_history
        result = export_search_history(format=format)
        return JSONResponse(content={"result": result})
    except Exception as e:
        logger.error(f"导出搜索日志失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/v5/export/knowledge_base")
async def export_knowledge_base(
    format: str = Query("json", regex="^(json|csv)$"),
    dataset_name: str = Query("default")
):
    """导出知识库"""
    try:
        from tools.export_tools import export_knowledge_base
        result = export_knowledge_base(dataset_name=dataset_name, format=format)
        return JSONResponse(content={"result": result})
    except Exception as e:
        logger.error(f"导出知识库失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ==================== 画布配置接口 ====================

@app.get("/api/v5/canvas/nodes")
async def get_canvas_nodes():
    """获取画布节点配置"""
    try:
        from src.config.operation_config import get_operation_config
        config = get_operation_config()
        nodes = config.get("sop_flow.canvas_nodes", [])
        return JSONResponse(content={"nodes": nodes})
    except Exception as e:
        logger.error(f"获取画布节点失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/v5/canvas/nodes")
async def add_canvas_node(node_data: Dict[str, Any] = Body(...)):
    """添加画布节点"""
    try:
        from src.config.operation_config import get_operation_config
        config = get_operation_config()

        nodes = config.get("sop_flow.canvas_nodes", [])
        node_id = node_data.get("id", f"node_{datetime.now().timestamp()}")
        node_data["id"] = node_id

        nodes.append(node_data)
        config.set("sop_flow.canvas_nodes", nodes)

        return JSONResponse(content={"status": "success", "message": "画布节点添加成功", "node_id": node_id})
    except Exception as e:
        logger.error(f"添加画布节点失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.put("/api/v5/canvas/nodes/{node_id}")
async def update_canvas_node(node_id: str, node_data: Dict[str, Any] = Body(...)):
    """更新画布节点"""
    try:
        from src.config.operation_config import get_operation_config
        config = get_operation_config()

        nodes = config.get("sop_flow.canvas_nodes", [])
        for i, node in enumerate(nodes):
            if node.get("id") == node_id:
                nodes[i] = {**nodes[i], **node_data, "id": node_id}
                break
        else:
            raise HTTPException(status_code=404, detail=f"节点不存在: {node_id}")

        config.set("sop_flow.canvas_nodes", nodes)
        return JSONResponse(content={"status": "success", "message": "画布节点更新成功"})
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"更新画布节点失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.delete("/api/v5/canvas/nodes/{node_id}")
async def delete_canvas_node(node_id: str):
    """删除画布节点"""
    try:
        from src.config.operation_config import get_operation_config
        config = get_operation_config()

        nodes = config.get("sop_flow.canvas_nodes", [])
        nodes = [node for node in nodes if node.get("id") != node_id]

        config.set("sop_flow.canvas_nodes", nodes)
        return JSONResponse(content={"status": "success", "message": "画布节点删除成功"})
    except Exception as e:
        logger.error(f"删除画布节点失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ==================== 统计数据接口 ====================

@app.get("/api/v5/stats/dashboard")
async def get_dashboard_stats():
    """获取仪表板统计数据"""
    try:
        from sop.knowledge_manager import get_sop_manager

        sop_manager = get_sop_manager()
        sop_list = sop_manager.list_knowledge()

        from src.config.operation_config import get_operation_config
        config = get_operation_config()

        stats = {
            "sop_count": len(sop_list),
            "greeting_enabled": config.get("greeting.enabled", False),
            "chitchat_enabled": config.get("chitchat.enabled", False),
            "transfer_enabled": config.get("transfer_to_human.enabled", False),
            "canvas_nodes_count": len(config.get("sop_flow.canvas_nodes", []))
        }

        return JSONResponse(content=stats)
    except Exception as e:
        logger.error(f"获取仪表板统计数据失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/health")
async def health_check():
    """健康检查"""
    return {"status": "healthy", "service": "operation_api"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8005)
