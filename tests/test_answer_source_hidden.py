"""
测试答案来源标注是否隐藏
验证：1. 用户看不到答案来源标注 2. 导出数据中保留来源信息
"""
import sys
import os

# 添加项目路径到 PythonPATH
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, project_root)


def test_answer_source_hidden():
    """测试答案来源标注是否对用户隐藏"""
    print("=" * 60)
    print("测试：答案来源标注是否隐藏")
    print("=" * 60)

    try:
        from src.workflow.graph_v4 import build_workflow_v4
        from src.workflow.state import WorkflowState

        # 构建工作流
        workflow = build_workflow_v4(debug_mode=True)

        print("\n测试1: 退款咨询（不匹配SOP，走知识库流程）")
        state1 = WorkflowState(
            user_input="我想申请退款",
            has_image=False,
            debug_mode=False  # 关闭调试模式
        )

        result1 = workflow.invoke(state1)
        answer1 = result1.get('final_answer', '')
        source1 = result1.get('answer_source', '')

        print(f"  答案来源 (内部): {source1}")
        print(f"  答案内容:\n{answer1}")

        # 检查答案中是否包含来源标注
        has_annotation = any([
            "知识库答案" in answer1,
            "网络搜索答案" in answer1,
            "信息风险提醒" in answer1,
            "【" in answer1 and "】" in answer1
        ])

        if has_annotation:
            print("\n  ✗ 错误：答案中包含来源标注！")
            return False
        else:
            print("\n  ✓ 正确：答案中没有来源标注")

        # 验证来源信息保留在状态中
        if source1 in ["knowledge_base", "web_search", "sop", "llm"]:
            print(f"  ✓ 正确：来源信息保留在状态中: {source1}")
        else:
            print(f"  ⚠ 警告：来源信息异常: {source1}")

        print("\n" + "-" * 60)
        print("\n测试2: 通用咨询（走LLM流程）")
        state2 = WorkflowState(
            user_input="你好",
            has_image=False,
            debug_mode=False
        )

        result2 = workflow.invoke(state2)
        answer2 = result2.get('final_answer', '')
        source2 = result2.get('answer_source', '')

        print(f"  答案来源 (内部): {source2}")
        print(f"  答案内容:\n{answer2}")

        # 检查答案中是否包含来源标注
        has_annotation = any([
            "知识库答案" in answer2,
            "网络搜索答案" in answer2,
            "信息风险提醒" in answer2,
            "【" in answer2 and "】" in answer2
        ])

        if has_annotation:
            print("\n  ✗ 错误：答案中包含来源标注！")
            return False
        else:
            print("\n  ✓ 正确：答案中没有来源标注")

        print("\n" + "=" * 60)
        print("✓ 测试通过：答案来源标注已正确隐藏")
        return True

    except Exception as e:
        print(f"\n✗ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_export_contains_source():
    """测试导出数据是否包含来源信息"""
    print("\n" + "=" * 60)
    print("测试：导出数据是否包含来源信息")
    print("=" * 60)

    try:
        from tests.test_helpers import export_conversation_history_direct

        print("\n测试导出会话记录（Markdown格式）：")
        export_md = export_conversation_history_direct(format="markdown")
        print(export_md[:300])

        # 检查是否包含来源信息
        if "**来源**:" in export_md or "**来源**" in export_md:
            print("\n  ✓ 正确：导出数据包含来源信息")
            return True
        else:
            print("\n  ✗ 错误：导出数据缺少来源信息")
            return False

    except Exception as e:
        print(f"\n✗ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """主测试函数"""
    print("\n" + "=" * 60)
    print("答案来源标注隐藏测试")
    print("=" * 60)
    print("\n测试目标：")
    print("1. 用户回复中不显示答案来源标注")
    print("2. 导出数据中保留答案来源信息")
    print("=" * 60)

    results = []

    # 运行测试
    results.append(("答案来源隐藏", test_answer_source_hidden()))
    results.append(("导出包含来源", test_export_contains_source()))

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
        print("\n🎉 所有测试通过！答案来源标注已正确隐藏。")
        return 0
    else:
        print(f"\n⚠️  有 {failed} 个测试失败")
        return 1


if __name__ == "__main__":
    sys.exit(main())
