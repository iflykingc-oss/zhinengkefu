"""
智能客服 API 服务
支持微信小程序调用
"""
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
import asyncio
from langchain_core.messages import HumanMessage
from agents.agent import build_agent
from config.dynamic_config import get_config_manager

# 创建 FastAPI 应用
app = FastAPI(title="智能客服 API", version="1.0.0")

# 配置 CORS，允许微信小程序跨域访问
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 生产环境应该指定具体域名
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# 请求和响应模型
class ChatRequest(BaseModel):
    """聊天请求"""
    message: str
    image_url: Optional[str] = None  # 可选的图片URL
    config_id: Optional[str] = None  # 可选的配置ID
    enable_feishu: bool = False  # 是否发送到飞书


class ChatResponse(BaseModel):
    """聊天响应"""
    response: str
    source: str  # 来源：knowledge_base, web_search, llm


class ConfigUpdateRequest(BaseModel):
    """配置更新请求"""
    model: Optional[str] = None
    temperature: Optional[float] = None
    top_p: Optional[float] = None
    max_completion_tokens: Optional[int] = None
    timeout: Optional[int] = None
    thinking: Optional[str] = None
    system_prompt: Optional[str] = None
    tools: Optional[List[str]] = None


class ModelInfo(BaseModel):
    """模型信息"""
    id: str
    name: str
    description: str


# 配置管理器
config_manager = get_config_manager()


@app.get("/")
async def root():
    """根路径"""
    return {
        "message": "智能客服 API",
        "version": "1.0.0",
        "endpoints": {
            "POST /api/chat": "发送聊天消息",
            "GET /api/config": "获取当前配置",
            "POST /api/config": "更新配置",
            "GET /api/models": "获取可用模型列表"
        }
    }


@app.post("/api/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """
    聊天接口

    支持文本和图片输入，自动调用知识库和联网搜索
    """
    try:
        # 构建 Agent
        agent = build_agent()

        # 构建消息
        if request.image_url:
            # 多模态输入（文本 + 图片）
            message = HumanMessage(content=[
                {"type": "text", "text": request.message},
                {"type": "image_url", "image_url": {"url": request.image_url}}
            ])
        else:
            # 纯文本输入
            message = HumanMessage(content=request.message)

        # 调用 Agent
        response = await agent.ainvoke({"messages": [message]})

        # 提取响应内容
        ai_message = response["messages"][-1]
        content = ai_message.content

        # 判断信息来源
        if isinstance(content, str):
            if "【知识库答案】" in content:
                source = "knowledge_base"
            elif "【网络搜索答案】" in content:
                source = "web_search"
            else:
                source = "llm"
        else:
            source = "llm"

        # 如果启用了飞书通知
        if request.enable_feishu:
            from tools.feishu_notification_tool import send_feishu_text_message
            asyncio.create_task(
                asyncio.to_thread(send_feishu_text_message, f"用户咨询：{request.message}\n回复：{content}")
            )

        return ChatResponse(response=str(content), source=source)

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"聊天失败: {str(e)}")


@app.get("/api/config")
async def get_config():
    """
    获取当前配置
    """
    try:
        config = config_manager.load_config()
        return config
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取配置失败: {str(e)}")


@app.post("/api/config")
async def update_config(request: ConfigUpdateRequest):
    """
    更新配置

    支持更新模型配置、系统提示词和工具列表
    """
    try:
        # 更新模型配置
        if request.model is not None:
            config = config_manager.update_model_config(
                model=request.model,
                temperature=request.temperature,
                top_p=request.top_p,
                max_completion_tokens=request.max_completion_tokens,
                timeout=request.timeout,
                thinking=request.thinking
            )

        # 更新系统提示词
        if request.system_prompt is not None:
            config = config_manager.update_system_prompt(request.system_prompt)

        # 更新工具列表
        if request.tools is not None:
            config = config_manager.update_tools(request.tools)

        return {
            "message": "配置更新成功",
            "config": config
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"更新配置失败: {str(e)}")


@app.get("/api/models", response_model=List[ModelInfo])
async def get_models():
    """
    获取可用模型列表
    """
    try:
        models = config_manager.get_available_models()
        return [ModelInfo(**model) for model in models]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取模型列表失败: {str(e)}")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
