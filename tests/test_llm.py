"""
测试 LLM 调用
"""
import os
from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage


def test_llm_call():
    """测试 LLM 调用"""
    print("测试 LLM 调用...")
    print("-" * 60)

    api_key = os.getenv("COZE_WORKLOAD_IDENTITY_API_KEY")
    base_url = os.getenv("COZE_INTEGRATION_MODEL_BASE_URL")

    print(f"API Key: {api_key[:20] if api_key else None}...")
    print(f"Base URL: {base_url}")

    try:
        llm = ChatOpenAI(
            model="doubao-seed-1-8-251228",
            api_key=api_key,
            base_url=base_url,
            temperature=0.7,
            streaming=False,
            timeout=600,
        )

        messages = [
            SystemMessage(content="你是一个助手"),
            HumanMessage(content="你好")
        ]

        print("\n调用 LLM...")
        response = llm.invoke(messages)

        print(f"响应类型: {type(response)}")
        print(f"响应内容: {response}")

        if hasattr(response, 'content'):
            print(f"Content: {response.content}")

    except Exception as e:
        print(f"调用失败: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    test_llm_call()
