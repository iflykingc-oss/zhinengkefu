"""
综合 API 服务
整合所有功能：工作流、飞书、知识库导入、数据分析、调试等
"""
from fastapi import FastAPI, HTTPException, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
import logging

logger = logging.getLogger(__name__)

# 创建 FastAPI 应用
app = FastAPI(title="智能客服综合服务", version="3.0.0")

# 配置 CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# 请求和响应模型
class KnowledgeImportRequest(BaseModel):
    """知识库导入请求"""
    source_type: str  # feishu_bitable, excel, csv
    app_token: Optional[str] = None  # 飞书多维表格使用
    table_id: Optional[str] = None  # 飞书多维表格使用
    dataset_name: str
    file_path: Optional[str] = None  # Excel/CSV 使用


class DataAnalysisRequest(BaseModel):
    """数据分析请求"""
    source_type: str  # feishu_bitable, excel, csv
    app_token: Optional[str] = None
    table_id: Optional[str] = None
    file_path: Optional[str] = None
    query: Optional[str] = None  # 可选的查询条件


class DebugStepRequest(BaseModel):
    """调试步骤请求"""
    node_id: str
    state: Dict[str, Any]


class DebugConfigRequest(BaseModel):
    """调试配置请求"""
    action: str  # set_breakpoint, remove_breakpoint, enable_step, disable_step
    node_id: Optional[str] = None


@app.get("/")
async def root():
    """根路径"""
    return {
        "message": "智能客服综合服务",
        "version": "3.0.0",
        "features": [
            "工作流聊天",
            "飞书机器人互动",
            "知识库导入（飞书多维表格、Excel、CSV）",
            "数据分析",
            "分模块调试",
            "配置热更新",
            "微信小程序配置"
        ],
        "endpoints": {
            "POST /api/workflow/chat": "工作流聊天",
            "POST /api/knowledge/import": "导入知识库",
            "POST /api/data/analyze": "数据分析",
            "POST /api/debug/step": "调试单步执行",
            "POST /api/debug/config": "配置调试",
            "POST /api/config/reload": "重新加载配置",
            "POST /api/miniprogram/config": "小程序配置",
            "POST /api/feishu/webhook": "飞书机器人webhook"
        }
    }


@app.post("/api/knowledge/import")
async def import_knowledge(request: KnowledgeImportRequest):
    """
    导入知识库

    支持飞书多维表格、Excel、CSV
    """
    try:
        from tools.knowledge_import_tools import (
            import_feishu_bitable_to_knowledge_base,
            import_excel_to_knowledge_base,
            import_csv_to_knowledge_base
        )

        if request.source_type == "feishu_bitable":
            if not request.app_token or not request.table_id:
                raise HTTPException(status_code=400, detail="飞书多维表格需要 app_token 和 table_id")

            result = import_feishu_bitable_to_knowledge_base(
                app_token=request.app_token,
                table_id=request.table_id,
                dataset_name=request.dataset_name
            )

        elif request.source_type == "excel":
            if not request.file_path:
                raise HTTPException(status_code=400, detail="Excel 导入需要 file_path")

            result = import_excel_to_knowledge_base(
                file_path=request.file_path,
                dataset_name=request.dataset_name
            )

        elif request.source_type == "csv":
            if not request.file_path:
                raise HTTPException(status_code=400, detail="CSV 导入需要 file_path")

            result = import_csv_to_knowledge_base(
                file_path=request.file_path,
                dataset_name=request.dataset_name
            )

        else:
            raise HTTPException(status_code=400, detail=f"不支持的来源类型: {request.source_type}")

        return {"success": True, "result": result}

    except Exception as e:
        logger.error(f"导入知识库失败: {e}")
        raise HTTPException(status_code=500, detail=f"导入失败: {str(e)}")


@app.post("/api/knowledge/import/file")
async def import_knowledge_file(
    source_type: str,
    dataset_name: str,
    file: UploadFile = File(...)
):
    """
    通过上传文件导入知识库
    """
    try:
        import os

        # 保存上传的文件
        upload_dir = "/tmp/uploads"
        os.makedirs(upload_dir, exist_ok=True)

        file_path = os.path.join(upload_dir, file.filename)
        with open(file_path, "wb") as f:
            f.write(await file.read())

        # 根据文件类型导入
        if file.filename.endswith(('.xlsx', '.xls')):
            from tools.knowledge_import_tools import import_excel_to_knowledge_base
            result = import_excel_to_knowledge_base(file_path, dataset_name)
        elif file.filename.endswith('.csv'):
            from tools.knowledge_import_tools import import_csv_to_knowledge_base
            result = import_csv_to_knowledge_base(file_path, dataset_name)
        else:
            raise HTTPException(status_code=400, detail="不支持的文件类型")

        return {"success": True, "result": result}

    except Exception as e:
        logger.error(f"文件导入失败: {e}")
        raise HTTPException(status_code=500, detail=f"导入失败: {str(e)}")


@app.post("/api/data/analyze")
async def analyze_data(request: DataAnalysisRequest):
    """
    数据分析

    支持飞书多维表格、Excel、CSV
    """
    try:
        from tools.data_analysis_tools import (
            analyze_feishu_bitable,
            analyze_excel,
            analyze_csv,
            query_data
        )

        if request.source_type == "feishu_bitable":
            if not request.app_token or not request.table_id:
                raise HTTPException(status_code=400, detail="飞书多维表格需要 app_token 和 table_id")

            if request.query:
                result = query_data(
                    app_token=request.app_token,
                    table_id=request.table_id,
                    query_condition=request.query
                )
            else:
                result = analyze_feishu_bitable(
                    app_token=request.app_token,
                    table_id=request.table_id
                )

        elif request.source_type == "excel":
            if not request.file_path:
                raise HTTPException(status_code=400, detail="Excel 分析需要 file_path")

            result = analyze_excel(file_path=request.file_path)

        elif request.source_type == "csv":
            if not request.file_path:
                raise HTTPException(status_code=400, detail="CSV 分析需要 file_path")

            result = analyze_csv(file_path=request.file_path)

        else:
            raise HTTPException(status_code=400, detail=f"不支持的来源类型: {request.source_type}")

        return {"success": True, "result": result}

    except Exception as e:
        logger.error(f"数据分析失败: {e}")
        raise HTTPException(status_code=500, detail=f"分析失败: {str(e)}")


@app.post("/api/data/analyze/file")
async def analyze_data_file(
    source_type: str,
    query: Optional[str] = None,
    file: UploadFile = File(...)
):
    """
    通过上传文件进行数据分析
    """
    try:
        import os

        # 保存上传的文件
        upload_dir = "/tmp/uploads"
        os.makedirs(upload_dir, exist_ok=True)

        file_path = os.path.join(upload_dir, file.filename)
        with open(file_path, "wb") as f:
            f.write(await file.read())

        # 根据文件类型分析
        if file.filename.endswith(('.xlsx', '.xls')):
            from tools.data_analysis_tools import analyze_excel
            result = analyze_excel(file_path)
        elif file.filename.endswith('.csv'):
            from tools.data_analysis_tools import analyze_csv
            result = analyze_csv(file_path)
        else:
            raise HTTPException(status_code=400, detail="不支持的文件类型")

        return {"success": True, "result": result}

    except Exception as e:
        logger.error(f"文件分析失败: {e}")
        raise HTTPException(status_code=500, detail=f"分析失败: {str(e)}")


@app.post("/api/debug/step")
async def debug_step(request: DebugStepRequest):
    """
    调试单步执行
    """
    try:
        from workflow.debugger import create_enhanced_workflow_runner
        from workflow.state import WorkflowState

        runner = create_enhanced_workflow_runner()
        state = WorkflowState(**request.state)

        # 执行单个节点
        updated_state = runner.execute_single_node(request.node_id, state)

        return {
            "success": True,
            "state": updated_state
        }

    except Exception as e:
        logger.error(f"调试执行失败: {e}")
        raise HTTPException(status_code=500, detail=f"执行失败: {str(e)}")


@app.post("/api/debug/config")
async def configure_debug(request: DebugConfigRequest):
    """
    配置调试
    """
    try:
        from workflow.debugger import get_global_debugger

        debugger = get_global_debugger()

        if request.action == "set_breakpoint":
            if not request.node_id:
                raise HTTPException(status_code=400, detail="设置断点需要 node_id")
            debugger.set_breakpoint(request.node_id)
            return {"success": True, "message": f"断点已设置: {request.node_id}"}

        elif request.action == "remove_breakpoint":
            if not request.node_id:
                raise HTTPException(status_code=400, detail="移除断点需要 node_id")
            debugger.remove_breakpoint(request.node_id)
            return {"success": True, "message": f"断点已移除: {request.node_id}"}

        elif request.action == "enable_step":
            debugger.enable_step_mode()
            return {"success": True, "message": "单步模式已启用"}

        elif request.action == "disable_step":
            debugger.disable_step_mode()
            return {"success": True, "message": "单步模式已禁用"}

        elif request.action == "pause":
            debugger.pause()
            return {"success": True, "message": "工作流已暂停"}

        elif request.action == "resume":
            debugger.resume()
            return {"success": True, "message": "工作流已恢复"}

        else:
            raise HTTPException(status_code=400, detail=f"不支持的操作: {request.action}")

    except Exception as e:
        logger.error(f"配置调试失败: {e}")
        raise HTTPException(status_code=500, detail=f"配置失败: {str(e)}")


@app.post("/api/config/reload")
async def reload_config():
    """
    重新加载配置（热更新）
    """
    try:
        from config.hot_reload import reload_all_configs

        success = reload_all_configs()

        if success:
            return {"success": True, "message": "配置已重新加载"}
        else:
            return {"success": False, "message": "部分配置重新加载失败"}

    except Exception as e:
        logger.error(f"重新加载配置失败: {e}")
        raise HTTPException(status_code=500, detail=f"重新加载失败: {str(e)}")


@app.post("/api/miniprogram/config")
async def miniprogram_config(config: Dict[str, Any]):
    """
    微信小程序配置

    支持在小程序端配置智能客服入口
    """
    try:
        from config.hot_reload import get_config_manager

        manager = get_config_manager()

        # 保存小程序配置
        miniprogram_config = manager.get_config("miniprogram")

        if miniprogram_config is None:
            # 创建小程序配置
            config_path = os.path.join(os.getenv("COZE_WORKSPACE_PATH", "/workspace/projects"), "config/miniprogram_config.json")
            miniprogram_config = manager.register_config("miniprogram", config_path)

        # 更新配置
        miniprogram_config.update(config)

        return {"success": True, "message": "小程序配置已更新"}

    except Exception as e:
        logger.error(f"更新小程序配置失败: {e}")
        raise HTTPException(status_code=500, detail=f"更新失败: {str(e)}")


@app.get("/api/miniprogram/config")
async def get_miniprogram_config():
    """
    获取微信小程序配置
    """
    try:
        from config.hot_reload import get_config_manager

        manager = get_config_manager()
        miniprogram_config = manager.get_config("miniprogram")

        if miniprogram_config:
            return {"success": True, "config": miniprogram_config.get_config()}
        else:
            return {"success": True, "config": {}}

    except Exception as e:
        logger.error(f"获取小程序配置失败: {e}")
        raise HTTPException(status_code=500, detail=f"获取失败: {str(e)}")


@app.get("/api/status")
async def get_status():
    """获取系统状态"""
    try:
        from workflow.debugger import get_global_debugger
        from config.hot_reload import get_config_manager

        debugger = get_global_debugger()
        manager = get_config_manager()

        return {
            "success": True,
            "status": {
                "debug_mode": debugger.step_mode,
                "paused": debugger.paused,
                "breakpoints": list(debugger.breakpoints),
                "configs_watching": list(manager._configs.keys())
            }
        }

    except Exception as e:
        logger.error(f"获取状态失败: {e}")
        raise HTTPException(status_code=500, detail=f"获取失败: {str(e)}")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8002)
