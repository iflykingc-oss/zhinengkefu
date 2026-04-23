"""
测试简化的工作流
"""
import asyncio
from workflow.graph import build_workflow
from workflow.state import WorkflowState


def test_simple_workflow():
    """测试简化的工作流执行"""
    print("=" * 60)
    print("测试简化的工作流执行（不包含答案生成）")
    print("=" * 60)

    # 构建工作流
    app = build_workflow(debug_mode=True)

    # 初始化状态（使用 dict 而不是 WorkflowState）
    initial_state = {
        "messages": [],
        "user_input": "测试输入",
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
        "debug_mode": True,
        "debug_info": [],
        "current_step": "",
        "enable_feishu": False,
        "feishu_sent": False,
        "config_id": None
    }

    print("\n开始执行工作流...")
    print("-" * 60)

    try:
        result = app.invoke(initial_state)
        print("-" * 60)
        print("\n工作流执行成功")
        print(f"执行步骤: {len(result.get('debug_info', []))}")
    except Exception as e:
        print(f"\n工作流执行失败: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    test_simple_workflow()
