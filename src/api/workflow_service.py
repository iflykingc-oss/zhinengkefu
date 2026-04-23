"""
工作流 API 服务
支持工作流模式、自定义调试和节点配置
"""
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from workflow.graph import build_workflow, print_workflow_structure
from workflow.config import get_workflow_config, NodeStatus
from workflow.state import WorkflowState

# 创建 FastAPI 应用
app = FastAPI(title="智能客服工作流 API", version="2.0.0")

# 配置 CORS，允许微信小程序跨域访问
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# 请求和响应模型
class WorkflowChatRequest(BaseModel):
    """工作流聊天请求"""
    message: str
    image_url: Optional[str] = None
    enable_feishu: bool = False
    debug_mode: bool = False
    config_id: Optional[str] = None


class WorkflowChatResponse(BaseModel):
    """工作流聊天响应"""
    answer: str
    source: str
    debug_info: Optional[List[str]] = None
    execution_steps: List[str]


class NodeConfigUpdateRequest(BaseModel):
    """节点配置更新请求"""
    node_id: str
    config: Dict[str, Any]


class NodeStatusUpdateRequest(BaseModel):
    """节点状态更新请求"""
    node_id: str
    status: str  # enabled, disabled, debug


class AddNodeRequest(BaseModel):
    """添加节点请求"""
    node_id: str
    name: str
    description: str
    config: Dict[str, Any]


# 工作流配置管理器
workflow_config = get_workflow_config()


@app.get("/")
async def root():
    """根路径"""
    return {
        "message": "智能客服工作流 API",
        "version": "2.0.0",
        "mode": "workflow",
        "endpoints": {
            "POST /api/workflow/chat": "工作流聊天",
            "GET /api/workflow/structure": "获取工作流结构",
            "GET /api/workflow/config": "获取工作流配置",
            "POST /api/workflow/nodes/config": "更新节点配置",
            "POST /api/workflow/nodes/status": "更新节点状态",
            "POST /api/workflow/nodes/add": "添加新节点",
            "DELETE /api/workflow/nodes/{node_id}": "删除节点"
        }
    }


@app.post("/api/workflow/chat", response_model=WorkflowChatResponse)
async def workflow_chat(request: WorkflowChatRequest):
    """
    工作流聊天接口

    支持自定义调试模式，显示每个节点的执行过程
    """
    try:
        # 构建工作流
        app_workflow = build_workflow(debug_mode=request.debug_mode)

        # 初始化状态
        initial_state: WorkflowState = {
            "messages": [],
            "user_input": request.message,
            "has_image": bool(request.image_url),
            "image_url": request.image_url,
            "knowledge_result": None,
            "knowledge_found": False,
            "web_result": None,
            "web_found": False,
            "risk_assessment": None,
            "is_risky": False,
            "final_answer": None,
            "answer_source": "",
            "debug_mode": request.debug_mode,
            "debug_info": [],
            "current_step": "",
            "enable_feishu": request.enable_feishu,
            "feishu_sent": False,
            "config_id": request.config_id
        }

        # 执行工作流
        result = app_workflow.invoke(initial_state)

        # 返回结果
        return WorkflowChatResponse(
            answer=result.get("final_answer", "抱歉，无法生成答案"),
            source=result.get("answer_source", "unknown"),
            debug_info=result.get("debug_info") if request.debug_mode else None,
            execution_steps=result.get("debug_info", [])
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"工作流执行失败: {str(e)}")


@app.get("/api/workflow/structure")
async def get_workflow_structure():
    """
    获取工作流结构
    """
    try:
        workflow_config.load_config()
        return workflow_config.config
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取工作流结构失败: {str(e)}")


@app.get("/api/workflow/structure/text")
async def get_workflow_structure_text():
    """
    获取工作流结构（文本格式）
    """
    try:
        from io import StringIO
        import sys

        # 捕获 print_workflow_structure 的输出
        old_stdout = sys.stdout
        sys.stdout = StringIO()

        print_workflow_structure()

        output = sys.stdout.getvalue()
        sys.stdout = old_stdout

        return {"structure": output}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取工作流结构失败: {str(e)}")


@app.get("/api/workflow/config")
async def get_workflow_config_endpoint():
    """
    获取工作流配置
    """
    try:
        return workflow_config.load_config()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取工作流配置失败: {str(e)}")


@app.post("/api/workflow/nodes/config")
async def update_node_config(request: NodeConfigUpdateRequest):
    """
    更新节点配置
    """
    try:
        workflow_config.update_node_config(request.node_id, request.config)
        return {"message": "节点配置更新成功"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"更新节点配置失败: {str(e)}")


@app.post("/api/workflow/nodes/status")
async def update_node_status(request: NodeStatusUpdateRequest):
    """
    更新节点状态
    """
    try:
        status = NodeStatus(request.status)
        workflow_config.update_node_status(request.node_id, status)
        return {"message": f"节点 {request.node_id} 状态更新为 {status}"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"更新节点状态失败: {str(e)}")


@app.post("/api/workflow/nodes/add")
async def add_node(request: AddNodeRequest):
    """
    添加新节点
    """
    try:
        workflow_config.add_node(
            request.node_id,
            request.name,
            request.description,
            request.config
        )
        return {"message": f"节点 {request.node_id} 添加成功"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"添加节点失败: {str(e)}")


@app.delete("/api/workflow/nodes/{node_id}")
async def remove_node(node_id: str):
    """
    删除节点
    """
    try:
        workflow_config.remove_node(node_id)
        return {"message": f"节点 {node_id} 删除成功"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"删除节点失败: {str(e)}")


@app.post("/api/workflow/debug/enable")
async def enable_debug_mode():
    """
    启用调试模式
    """
    try:
        workflow_config.set_debug_mode(True)
        return {"message": "调试模式已启用"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"启用调试模式失败: {str(e)}")


@app.post("/api/workflow/debug/disable")
async def disable_debug_mode():
    """
    禁用调试模式
    """
    try:
        workflow_config.set_debug_mode(False)
        return {"message": "调试模式已禁用"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"禁用调试模式失败: {str(e)}")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)
