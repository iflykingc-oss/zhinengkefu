"""
飞书通知工具
用于发送消息到飞书群组
"""
import requests
import json
from langchain.tools import tool


def _get_webhook_url() -> str:
    """获取飞书 webhook URL"""
    try:
        from coze_workload_identity import Client
        client = Client()
        feishu_credential = client.get_integration_credential("integration-feishu-message")
        webhook_key = json.loads(feishu_credential)["webhook_url"]
        return webhook_key
    except Exception as e:
        raise RuntimeError(f"获取飞书 webhook URL 失败: {str(e)}")


@tool
def send_feishu_text_message(message: str) -> str:
    """
    发送文本消息到飞书群组

    Args:
        message: 要发送的文本消息内容

    Returns:
        发送结果
    """
    try:
        webhook_url = _get_webhook_url()

        payload = {
            "msg_type": "text",
            "content": {"text": message}
        }

        response = requests.post(webhook_url, json=payload)
        result = response.json()

        if result.get("StatusCode") == 0 or result.get("code") == 0:
            return "飞书消息发送成功"
        else:
            return f"飞书消息发送失败: {result}"

    except Exception as e:
        return f"飞书消息发送异常: {str(e)}"


@tool
def send_feishu_rich_message(title: str, content: str) -> str:
    """
    发送富文本消息到飞书群组

    Args:
        title: 消息标题
        content: 消息内容（纯文本）

    Returns:
        发送结果
    """
    try:
        webhook_url = _get_webhook_url()

        payload = {
            "msg_type": "post",
            "content": {
                "post": {
                    "zh_cn": {
                        "title": title,
                        "content": [
                            [
                                {"tag": "text", "text": content}
                            ]
                        ]
                    }
                }
            }
        }

        response = requests.post(webhook_url, json=payload)
        result = response.json()

        if result.get("StatusCode") == 0 or result.get("code") == 0:
            return "飞书富文本消息发送成功"
        else:
            return f"飞书富文本消息发送失败: {result}"

    except Exception as e:
        return f"飞书富文本消息发送异常: {str(e)}"
