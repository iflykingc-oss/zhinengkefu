"""
测试 SDK LLM 调用
"""
import os
from coze_coding_dev_sdk import LLMClient
from coze_coding_utils.runtime_ctx.context import new_context
from langchain_core.messages import SystemMessage, HumanMessage


def test_sdk_llm_call():
    """测试 SDK LLM 调用"""
    print("测试 SDK LLM 调用...")
    print("-" * 60)

    try:
        ctx = new_context(method="test")
        client = LLMClient(ctx=ctx)

        messages = [
            SystemMessage(content="你是一个助手"),
            HumanMessage(content="你好")
        ]

        print("\n调用 LLM...")
        response = client.invoke(messages=messages)

        print(f"响应类型: {type(response)}")
        print(f"响应内容: {response}")

        if hasattr(response, 'content'):
            content = response.content
            print(f"Content 类型: {type(content)}")
            print(f"Content: {content}")

    except Exception as e:
        print(f"调用失败: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    test_sdk_llm_call()
