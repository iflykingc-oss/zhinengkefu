"""
飞书机器人接收模块
支持通过飞书与智能客服互动
"""
import json
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from typing import Optional
from workflow.graph import build_workflow
from workflow.state import WorkflowState
from tools.feishu_notification_tool import send_feishu_text_message
import logging

logger = logging.getLogger(__name__)

# 创建 FastAPI 应用
feishu_bot_app = FastAPI(title="飞书机器人服务")

# 配置 CORS
feishu_bot_app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@feishu_bot_app.post("/api/feishu/webhook")
async def feishu_webhook(request: Request):
    """
    飞书机器人 Webhook 接口

    接收飞书机器人消息，调用智能客服工作流处理，并发送回复
    """
    try:
        # 解析请求体
        body = await request.json()
        logger.info(f"收到飞书消息: {body}")

        # 验证挑战（飞书首次验证时）
        if "challenge" in body:
            return {"challenge": body["challenge"]}

        # 提取消息内容
        msg_type = body.get("msg_type")
        content = body.get("content", {})

        # 处理不同类型的消息
        if msg_type == "text":
            # 文本消息
            text = content.get("text", "")
            user_message = text.strip()

            if not user_message:
                return {"code": 0, "msg": "success"}

            # 构建工作流输入
            state = {
                "messages": [],
                "user_input": user_message,
                "has_image": False,
                "image_url": None,
                "knowledge_result": None,
                "knowledge_found": False,
                "web_result": None,
                "web_found": False,
                "risk_assessment": None,
                "is_risky": False,
                "final_answer": None,
                "answer_source": "",
                "debug_mode": False,
                "debug_info": [],
                "current_step": "",
                "enable_feishu": False,  # 避免循环发送
                "feishu_sent": False,
                "config_id": None
            }

            # 执行工作流
            workflow = build_workflow(debug_mode=False)
            result = workflow.invoke(state)

            # 获取回复
            reply = result.get("final_answer", "抱歉，我无法理解您的问题")
            source = result.get("answer_source", "unknown")

            # 添加来源标识
            if source == "knowledge_base":
                reply = "【知识库答案】\n" + reply
            elif source == "web_search":
                reply = "【网络搜索答案】\n" + reply

            # 发送回复到飞书
            # 注意：这里需要飞书的发送接口，暂时返回回复内容
            logger.info(f"飞书回复: {reply[:100]}...")

            return {
                "code": 0,
                "msg": "success",
                "data": {
                    "reply": reply,
                    "source": source
                }
            }

        elif msg_type == "image":
            # 图片消息
            image_key = content.get("image_key")

            # TODO: 从飞书获取图片URL，然后调用工作流处理

            reply = "我收到了您的图片，正在分析..."

            return {
                "code": 0,
                "msg": "success",
                "data": {
                    "reply": reply
                }
            }

        else:
            # 其他类型消息
            logger.warning(f"不支持的消息类型: {msg_type}")
            return {"code": 0, "msg": "success"}

    except Exception as e:
        logger.error(f"处理飞书消息失败: {e}")
        raise HTTPException(status_code=500, detail=f"处理失败: {str(e)}")


@feishu_bot_app.get("/api/feishu/health")
async def health_check():
    """健康检查接口"""
    return {
        "status": "healthy",
        "service": "飞书机器人服务"
    }


@feishu_bot_app.get("/")
async def root():
    """根路径"""
    return {
        "message": "飞书机器人服务",
        "endpoints": {
            "POST /api/feishu/webhook": "接收飞书机器人消息",
            "GET /api/feishu/health": "健康检查"
        }
    }
