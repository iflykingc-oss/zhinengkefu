"""
工作流构建器 (v4.0)
构建完整的工作流图，支持RAG检索和SOP流程
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

# v4.0 新增节点
from src.sop.sop_nodes import sop_match_node, sop_execute_node


def check_sop_matched(state: WorkflowState) -> str:
    """
    检查是否匹配到SOP知识

    Args:
        state: 工作流状态

    Returns:
        下一个节点: "sop_execute" 或 "knowledge_search"
    """
    if state.get("sop_matched", False):
        return "sop_execute"
    else:
        return "knowledge_search"


def build_workflow_v4(debug_mode: bool = False):
    """
    构建工作流 v4.0
    支持 RAG 检索和 SOP 流程

    Args:
        debug_mode: 是否启用调试模式

    Returns:
        编译后的工作流图
    """
    # 创建状态图
    workflow = StateGraph(WorkflowState)

    # 添加节点
    workflow.add_node("input_parser", input_parser_node)
    workflow.add_node("sop_match", sop_match_node)
    workflow.add_node("sop_execute", sop_execute_node)
    workflow.add_node("knowledge_search", knowledge_search_node)
    workflow.add_node("web_search", web_search_node)
    workflow.add_node("risk_assessment", risk_assessment_node)
    workflow.add_node("answer_generation", answer_generation_node)
    workflow.add_node("feishu_notification", feishu_notification_node)

    # 设置入口
    workflow.set_entry_point("input_parser")

    # 添加边

    # 1. 输入解析 -> SOP匹配
    workflow.add_edge("input_parser", "sop_match")

    # 2. SOP匹配 -> 条件路由（SOP执行 或 知识库搜索）
    workflow.add_conditional_edges(
        "sop_match",
        check_sop_matched,
        {
            "sop_execute": "sop_execute",
            "knowledge_search": "knowledge_search"
        }
    )

    # 3. SOP执行 -> 飞书通知
    workflow.add_conditional_edges(
        "sop_execute",
        should_send_feishu,
        {
            "feishu_notification": "feishu_notification",
            "__end__": END
        }
    )

    # 4. 知识库搜索 -> 条件路由（联网搜索 或 答案生成）
    workflow.add_conditional_edges(
        "knowledge_search",
        should_search_web,
        {
            "web_search": "web_search",
            "answer_generation": "answer_generation"
        }
    )

    # 5. 联网搜索 -> 风险评估
    workflow.add_edge("web_search", "risk_assessment")

    # 6. 风险评估 -> 答案生成
    workflow.add_edge("risk_assessment", "answer_generation")

    # 7. 答案生成 -> 条件路由（飞书通知）
    workflow.add_conditional_edges(
        "answer_generation",
        should_send_feishu,
        {
            "feishu_notification": "feishu_notification",
            "__end__": END
        }
    )

    # 8. 飞书通知 -> 结束
    workflow.add_edge("feishu_notification", END)

    # 编译工作流
    app = workflow.compile()

    return app


def build_workflow(debug_mode: bool = False):
    """
    构建工作流（兼容旧版本）

    Args:
        debug_mode: 是否启用调试模式

    Returns:
        编译后的工作流图
    """
    # 使用 v4.0 版本
    return build_workflow_v4(debug_mode)


def get_workflow_node_names() -> list:
    """获取工作流节点名称"""
    return [
        "input_parser",
        "sop_match",
        "sop_execute",
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

    # 默认节点配置
    default_nodes = {
        "input_parser": {
            "name": "输入解析",
            "description": "解析用户输入，识别图片和文本",
            "status": NodeStatus.ENABLED,
            "config": {}
        },
        "sop_match": {
            "name": "SOP匹配",
            "description": "匹配用户输入与SOP知识库",
            "status": NodeStatus.ENABLED,
            "config": {}
        },
        "sop_execute": {
            "name": "SOP执行",
            "description": "执行SOP流程并生成富文本响应",
            "status": NodeStatus.ENABLED,
            "config": {}
        },
        "knowledge_search": {
            "name": "知识库搜索",
            "description": "在知识库中搜索相关信息",
            "status": NodeStatus.ENABLED,
            "config": {"top_k": 5}
        },
        "web_search": {
            "name": "联网搜索",
            "description": "在互联网上搜索信息",
            "status": NodeStatus.ENABLED,
            "config": {"max_results": 3}
        },
        "risk_assessment": {
            "name": "风险评估",
            "description": "评估外部信息的风险",
            "status": NodeStatus.ENABLED,
            "config": {}
        },
        "answer_generation": {
            "name": "答案生成",
            "description": "生成最终答案",
            "status": NodeStatus.ENABLED,
            "config": {
                "model": "doubao-seed-1-8-251228",
                "temperature": 0.7
            }
        },
        "feishu_notification": {
            "name": "飞书通知",
            "description": "发送通知到飞书群组",
            "status": NodeStatus.ENABLED,
            "config": {}
        }
    }

    nodes_config = workflow_config.get("nodes", default_nodes)

    for node_id, node_config in nodes_config.items():
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
    print("工作流流程:")
    print("-" * 60)
    print("  输入解析 → SOP匹配")
    print("    ├─ 匹配成功 → SOP执行 → 飞书通知 → 结束")
    print("    └─ 未匹配 → 知识库搜索")
    print("        ├─ 找到答案 → 答案生成 → 飞书通知 → 结束")
    print("        └─ 未找到 → 联网搜索 → 风险评估 → 答案生成 → 飞书通知 → 结束")
    print("\n" + "=" * 60)


if __name__ == "__main__":
    print_workflow_structure()
