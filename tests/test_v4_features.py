"""
测试脚本 v4.0 (修复版)
测试所有新功能：RAG检索、SOP流程、数据导出、可视化API
"""
import asyncio
import sys
import os

# 添加项目路径到 PythonPATH
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, project_root)

from src.sop.knowledge_manager import get_sop_manager, SOPKnowledge, ContentType
from src.sop.rich_text_formatter import create_rich_text_response, format_rich_content
from tests.test_helpers import (
    rag_retrieve_and_generate_direct,
    rag_retrieve_only_direct,
    export_knowledge_base_direct,
    export_search_history_direct,
    export_conversation_history_direct,
    export_visualization_data_direct
)


def test_sop_knowledge_manager():
    """测试SOP知识管理系统"""
    print("=" * 60)
    print("测试1: SOP知识管理系统")
    print("=" * 60)

    try:
        # 获取SOP管理器
        sop_manager = get_sop_manager()

        # 列出现有的SOP知识
        sop_list = sop_manager.list_knowledge()
        print(f"\n当前SOP知识数量: {len(sop_list)}")
        for sop in sop_list:
            print(f"  - {sop.name} (类型: {sop.content_type.value})")

        # 测试匹配
        print("\n测试SOP匹配:")
        test_queries = ["我想申请退款", "怎么注册账号", "产品价格是多少", "不知道"]
        for query in test_queries:
            matched = sop_manager.match_knowledge(query)
            if matched:
                print(f"  查询: '{query}' -> 匹配: {matched.name}")
            else:
                print(f"  查询: '{query}' -> 未匹配")

        print("\n✓ SOP知识管理系统测试通过")
        return True

    except Exception as e:
        print(f"\n✗ SOP知识管理系统测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_rich_text_formatter():
    """测试富文本格式化器"""
    print("\n" + "=" * 60)
    print("测试2: 富文本格式化器")
    print("=" * 60)

    try:
        # 测试富文本响应
        print("\n测试富文本响应创建:")
        rich_content = create_rich_text_response(
            title="退款流程指南",
            text="请按照以下步骤操作...",
            image_url="https://example.com/refund.png",
            video_url="https://example.com/refund.mp4",
            short_link="https://example.com/refund",
            link_text="立即退款"
        )

        print(f"  类型: {rich_content.get('type')}")
        print(f"  包含字段: {list(rich_content.keys())}")

        # 测试格式化输出
        print("\n测试格式化输出 (Markdown):")
        formatted = format_rich_content(rich_content, "markdown")
        print(f"  输出长度: {len(formatted)} 字符")
        print(f"  预览: {formatted[:200]}...")

        # 测试混合内容
        print("\n测试混合内容:")
        mixed_content = {
            "type": "mixed",
            "sections": [
                {"type": "text", "content": "第一步：填写表单"},
                {"type": "image", "url": "https://example.com/step1.png", "caption": "填写表单截图"},
                {"type": "text", "content": "第二步：提交审核"},
                {"type": "video", "url": "https://example.com/tutorial.mp4", "caption": "操作教程"}
            ]
        }

        mixed_formatted = format_rich_content(mixed_content, "markdown")
        print(f"  输出长度: {len(mixed_formatted)} 字符")
        print(f"  预览: {mixed_formatted[:200]}...")

        print("\n✓ 富文本格式化器测试通过")
        return True

    except Exception as e:
        print(f"\n✗ 富文本格式化器测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_workflow_with_sop():
    """测试带SOP的工作流"""
    print("\n" + "=" * 60)
    print("测试3: 带SOP的工作流")
    print("=" * 60)

    try:
        from src.workflow.graph_v4 import build_workflow_v4
        from src.workflow.state import WorkflowState

        # 构建工作流
        workflow = build_workflow_v4(debug_mode=True)

        print("\n工作流构建成功")
        print("节点列表:", list(workflow.nodes.keys()))

        # 测试1: 匹配SOP
        print("\n测试场景1: 退款咨询（应该匹配SOP）")
        state1 = WorkflowState(
            user_input="我想申请退款",
            has_image=False,
            debug_mode=True
        )

        result1 = workflow.invoke(state1)
        print(f"  匹配SOP: {result1.get('sop_matched')}")
        print(f"  SOP名称: {result1.get('sop_name')}")
        print(f"  答案来源: {result1.get('answer_source')}")
        print(f"  答案预览: {result1.get('final_answer', '')[:100]}...")

        # 测试2: 不匹配SOP
        print("\n测试场景2: 通用咨询（不匹配SOP）")
        state2 = WorkflowState(
            user_input="今天的天气怎么样？",
            has_image=False,
            debug_mode=True
        )

        result2 = workflow.invoke(state2)
        print(f"  匹配SOP: {result2.get('sop_matched')}")
        print(f"  答案来源: {result2.get('answer_source')}")
        print(f"  答案预览: {result2.get('final_answer', '')[:100]}...")

        print("\n✓ 工作流测试通过")
        return True

    except Exception as e:
        print(f"\n✗ 工作流测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_rag_tools():
    """测试RAG工具"""
    print("\n" + "=" * 60)
    print("测试4: RAG检索工具")
    print("=" * 60)

    try:
        print("\n测试RAG检索 (仅检索):")
        result = rag_retrieve_only_direct("退款流程")
        print(f"  结果: {result[:200]}...")

        print("\n测试RAG检索 (检索+生成):")
        result = rag_retrieve_and_generate_direct("退款流程")
        print(f"  结果: {result[:200]}...")

        print("\n✓ RAG工具测试通过")
        return True

    except Exception as e:
        print(f"\n✗ RAG工具测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_export_tools():
    """测试数据导出工具"""
    print("\n" + "=" * 60)
    print("测试5: 数据导出工具")
    print("=" * 60)

    try:
        print("\n测试导出知识库 (JSON):")
        result = export_knowledge_base_direct(format="json")
        print(f"  结果: {result[:200]}...")

        print("\n测试导出搜索记录 (CSV):")
        result = export_search_history_direct(format="csv")
        print(f"  结果: {result[:200]}...")

        print("\n测试导出会话记录 (Markdown):")
        result = export_conversation_history_direct(format="markdown")
        print(f"  结果: {result[:200]}...")

        print("\n测试导出可视化数据 (JSON):")
        result = export_visualization_data_direct(format="json")
        print(f"  结果: {result[:200]}...")

        print("\n✓ 数据导出工具测试通过")
        return True

    except Exception as e:
        print(f"\n✗ 数据导出工具测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """主测试函数"""
    print("\n" + "=" * 60)
    print("智能客服系统 v4.0 测试")
    print("=" * 60)

    results = []

    # 运行所有测试
    results.append(("SOP知识管理系统", test_sop_knowledge_manager()))
    results.append(("富文本格式化器", test_rich_text_formatter()))
    results.append(("工作流 (带SOP)", test_workflow_with_sop()))
    results.append(("RAG工具", test_rag_tools()))
    results.append(("数据导出工具", test_export_tools()))

    # 汇总结果
    print("\n" + "=" * 60)
    print("测试结果汇总")
    print("=" * 60)

    passed = 0
    failed = 0

    for test_name, result in results:
        status = "✓ 通过" if result else "✗ 失败"
        print(f"  {test_name}: {status}")
        if result:
            passed += 1
        else:
            failed += 1

    print(f"\n总计: {passed} 通过, {failed} 失败")

    if failed == 0:
        print("\n🎉 所有测试通过！")
        return 0
    else:
        print(f"\n⚠️  有 {failed} 个测试失败")
        return 1


if __name__ == "__main__":
    sys.exit(main())
