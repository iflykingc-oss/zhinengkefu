"""
工作流构建器
构建完整的工作流图
"""
from langgraph.graph import StateGraph, END
from src.workflow.state import WorkflowState
from src.workflow.config import get_workflow_config, NodeStatus
from src.workflow.nodes import (
    input_parser_node,
    knowledge_search_node,
    web_search_node,
    risk_assessment_node,
    answer_generation_node,
    feishu_notification_node
)
from src.workflow.routes import should_search_web, should_send_feishu


def build_workflow(debug_mode: bool = False):
    """
    构建工作流

    Args:
        debug_mode: 是否启用调试模式

    Returns:
        编译后的工作流图
    """
    # 创建状态图
    workflow = StateGraph(WorkflowState)

    # 添加节点
    workflow.add_node("input_parser", input_parser_node)
    workflow.add_node("knowledge_search", knowledge_search_node)
    workflow.add_node("web_search", web_search_node)
    workflow.add_node("risk_assessment", risk_assessment_node)
    workflow.add_node("answer_generation", answer_generation_node)
    workflow.add_node("feishu_notification", feishu_notification_node)

    # 设置入口
    workflow.set_entry_point("input_parser")

    # 添加边

    # 1. 输入解析 -> 知识库搜索
    workflow.add_edge("input_parser", "knowledge_search")

    # 2. 知识库搜索 -> 条件路由
    workflow.add_conditional_edges(
        "knowledge_search",
        should_search_web,
        {
            "web_search": "web_search",
            "answer_generation": "answer_generation"
        }
    )

    # 3. 联网搜索 -> 风险评估
    workflow.add_edge("web_search", "risk_assessment")

    # 4. 风险评估 -> 答案生成
    workflow.add_edge("risk_assessment", "answer_generation")

    # 5. 答案生成 -> 条件路由（飞书通知）
    workflow.add_conditional_edges(
        "answer_generation",
        should_send_feishu,
        {
            "feishu_notification": "feishu_notification",
            "__end__": END
        }
    )

    # 6. 飞书通知 -> 结束
    workflow.add_edge("feishu_notification", END)

    # 编译工作流
    app = workflow.compile()

    return app


def get_workflow_node_names() -> list:
    """获取工作流节点名称"""
    return [
        "input_parser",
        "knowledge_search",
        "web_search",
        "risk_assessment",
        "answer_generation",
        "feishu_notification"
    ]


def print_workflow_structure():
    """打印工作流结构"""
    config = get_workflow_config()
    workflow_config = config.config

    print("=" * 60)
    print(f"工作流名称: {workflow_config['workflow']['name']}")
    print(f"工作流版本: {workflow_config['workflow']['version']}")
    print(f"调试模式: {'启用' if workflow_config['workflow']['debug_mode'] else '禁用'}")
    print("=" * 60)
    print("\n节点列表:")
    print("-" * 60)

    for node_id, node_config in workflow_config.get("nodes", {}).items():
        status = node_config.get("status", NodeStatus.ENABLED)
        status_str = {
            NodeStatus.ENABLED: "✓ 启用",
            NodeStatus.DISABLED: "✗ 禁用",
            NodeStatus.DEBUG: "🔍 调试"
        }.get(status, status)

        print(f"\n{node_id}")
        print(f"  名称: {node_config.get('name')}")
        print(f"  描述: {node_config.get('description')}")
        print(f"  状态: {status_str}")
        print(f"  配置: {node_config.get('config')}")

    print("\n" + "=" * 60)
    print("边连接:")
    print("-" * 60)

    for edge in workflow_config.get("edges", []):
        from_node = edge.get("from")
        to_node = edge.get("to")
        condition = edge.get("condition", "")
        condition_str = f" (条件: {condition})" if condition else ""
        print(f"  {from_node} -> {to_node}{condition_str}")

    print("\n" + "=" * 60)


if __name__ == "__main__":
    print_workflow_structure()
