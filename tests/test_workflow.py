"""
测试工作流功能
"""
import asyncio
from workflow.graph import build_workflow
from workflow.config import get_workflow_config
from workflow.state import WorkflowState


def test_workflow_structure():
    """测试工作流结构"""
    print("=" * 60)
    print("测试1: 打印工作流结构")
    print("=" * 60)

    from workflow.graph import print_workflow_structure
    print_workflow_structure()

    print()


def test_workflow_execution():
    """测试工作流执行"""
    print("=" * 60)
    print("测试2: 执行工作流（调试模式）")
    print("=" * 60)

    # 构建工作流
    app = build_workflow(debug_mode=True)

    # 初始化状态
    initial_state: WorkflowState = {
        "messages": [],
        "user_input": "今天北京的天气怎么样？",
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

    # 执行工作流
    print("\n开始执行工作流...")
    print("-" * 60)

    result = app.invoke(initial_state)

    print("-" * 60)
    print("\n工作流执行完成")
    print("=" * 60)
    print("执行步骤:")
    for step in result.get("debug_info", []):
        print(f"  - {step}")

    print("\n最终答案:")
    print(f"  {result.get('final_answer')}")

    print(f"\n答案来源: {result.get('answer_source')}")
    print("=" * 60)


def test_node_configuration():
    """测试节点配置"""
    print("\n" + "=" * 60)
    print("测试3: 节点配置管理")
    print("=" * 60)

    config = get_workflow_config()

    # 获取节点配置
    print("\n获取知识库搜索节点配置:")
    kb_config = config.get_node_config("knowledge_search")
    print(f"  名称: {kb_config.get('name')}")
    print(f"  状态: {kb_config.get('status')}")
    print(f"  配置: {kb_config.get('config')}")

    # 更新节点配置
    print("\n更新节点配置...")
    config.update_node_config("knowledge_search", {"top_k": 10})
    print("  top_k 已更新为 10")

    # 获取更新后的配置
    updated_config = config.get_node_config("knowledge_search")
    print(f"  更新后的配置: {updated_config.get('config')}")

    # 切换节点状态
    print("\n切换节点状态...")
    config.set_debug_node("knowledge_search")
    print("  知识库搜索节点已设置为调试模式")

    # 获取调试节点
    debug_nodes = config.get_debug_nodes()
    print(f"  调试节点: {debug_nodes}")

    print("=" * 60)


if __name__ == "__main__":
    # 测试1: 工作流结构
    test_workflow_structure()

    # 测试2: 工作流执行
    test_workflow_execution()

    # 测试3: 节点配置
    test_node_configuration()

    print("\n所有测试完成！")
