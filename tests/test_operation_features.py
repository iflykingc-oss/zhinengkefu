"""
测试运营配置功能
测试开场白、闲聊、转人工策略等
"""
import sys
import os

# 添加项目路径到 PythonPATH
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, project_root)


def test_operation_config():
    """测试运营配置系统"""
    print("=" * 60)
    print("测试1: 运营配置系统")
    print("=" * 60)

    try:
        from src.config.operation_config import get_operation_config

        config = get_operation_config()

        # 测试获取配置
        print("\n测试获取配置:")
        print(f"  开场白启用: {config.get('greeting.enabled')}")
        print(f"  闲聊启用: {config.get('chitchat.enabled')}")
        print(f"  转人工启用: {config.get('transfer_to_human.enabled')}")

        # 测试设置配置
        print("\n测试设置配置:")
        config.set("greeting.delay", 2)
        delay = config.get("greeting.delay")
        print(f"  设置延迟为 2，获取: {delay}")

        # 测试获取完整配置
        print("\n测试获取完整配置:")
        full_config = config.get_full_config()
        print(f"  配置项数量: {len(full_config)}")

        print("\n✓ 运营配置系统测试通过")
        return True

    except Exception as e:
        print(f"\n✗ 运营配置系统测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_greeting():
    """测试开场白功能"""
    print("\n" + "=" * 60)
    print("测试2: 开场白功能")
    print("=" * 60)

    try:
        from src.ops.greeting import get_greeting_message

        # 测试新用户开场白
        print("\n测试新用户开场白:")
        context = {
            "is_first_message": True,
            "is_new_user": True
        }
        greeting = get_greeting_message(context)
        print(f"  开场白: {greeting}")

        # 测试老用户开场白
        print("\n测试老用户开场白:")
        context = {
            "is_first_message": True,
            "is_new_user": False
        }
        greeting = get_greeting_message(context)
        print(f"  开场白: {greeting}")

        # 测试非首条消息
        print("\n测试非首条消息:")
        context = {
            "is_first_message": False,
            "is_new_user": True
        }
        greeting = get_greeting_message(context)
        print(f"  开场白: {greeting}")

        print("\n✓ 开场白功能测试通过")
        return True

    except Exception as e:
        print(f"\n✗ 开场白功能测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_chitchat():
    """测试闲聊功能"""
    print("\n" + "=" * 60)
    print("测试3: 闲聊功能")
    print("=" * 60)

    try:
        from src.ops.chitchat import handle_chitchat

        # 测试打招呼
        print("\n测试打招呼:")
        is_chitchat, response = handle_chitchat("你好")
        print(f"  是闲聊: {is_chitchat}")
        print(f"  回复: {response}")

        # 测试感谢
        print("\n测试感谢:")
        is_chitchat, response = handle_chitchat("谢谢你的帮助")
        print(f"  是闲聊: {is_chitchat}")
        print(f"  回复: {response}")

        # 测试再见
        print("\n测试再见:")
        is_chitchat, response = handle_chitchat("再见，拜拜")
        print(f"  是闲聊: {is_chitchat}")
        print(f"  回复: {response}")

        # 测试非闲聊
        print("\n测试非闲聊:")
        is_chitchat, response = handle_chitchat("我想申请退款")
        print(f"  是闲聊: {is_chitchat}")
        print(f"  回复: {response}")

        print("\n✓ 闲聊功能测试通过")
        return True

    except Exception as e:
        print(f"\n✗ 闲聊功能测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_human_handoff():
    """测试转人工功能"""
    print("\n" + "=" * 60)
    print("测试4: 转人工功能")
    print("=" * 60)

    try:
        from src.ops.human_handoff import check_should_transfer_human, TransferReason

        # 测试关键词转人工
        print("\n测试关键词转人工:")
        context = {
            "user_input": "我要转人工客服",
            "round": 1,
            "has_solution": True
        }
        should_transfer, message, reason = check_should_transfer_human(context)
        print(f"  是否转人工: {should_transfer}")
        print(f"  消息: {message}")
        print(f"  原因: {reason}")

        # 测试轮次超限
        print("\n测试轮次超限:")
        context = {
            "user_input": "还是不行",
            "round": 6,
            "has_solution": True
        }
        should_transfer, message, reason = check_should_transfer_human(context)
        print(f"  是否转人工: {should_transfer}")
        print(f"  消息: {message}")
        print(f"  原因: {reason}")

        # 测试情感转人工
        print("\n测试情感转人工:")
        context = {
            "user_input": "你们太糟糕了，我要投诉",
            "round": 2,
            "has_solution": False
        }
        should_transfer, message, reason = check_should_transfer_human(context)
        print(f"  是否转人工: {should_transfer}")
        print(f"  消息: {message}")
        print(f"  原因: {reason}")

        # 测试正常对话
        print("\n测试正常对话:")
        context = {
            "user_input": "你好",
            "round": 1,
            "has_solution": True
        }
        should_transfer, message, reason = check_should_transfer_human(context)
        print(f"  是否转人工: {should_transfer}")
        print(f"  消息: {message}")
        print(f"  原因: {reason}")

        print("\n✓ 转人工功能测试通过")
        return True

    except Exception as e:
        print(f"\n✗ 转人工功能测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_sop_knowledge():
    """测试SOP知识"""
    print("\n" + "=" * 60)
    print("测试5: SOP知识")
    print("=" * 60)

    try:
        from src.sop.knowledge_manager import get_sop_manager

        sop_manager = get_sop_manager()

        # 列出所有SOP
        print("\n列出所有SOP:")
        sop_list = sop_manager.list_knowledge()
        for sop in sop_list:
            print(f"  - {sop.name} (类型: {sop.content_type.value})")

        # 测试匹配
        print("\n测试SOP匹配:")
        test_queries = ["退款", "注册", "价格"]
        for query in test_queries:
            matched = sop_manager.match_knowledge(query)
            if matched:
                print(f"  '{query}' -> {matched.name}")
            else:
                print(f"  '{query}' -> 未匹配")

        print("\n✓ SOP知识测试通过")
        return True

    except Exception as e:
        print(f"\n✗ SOP知识测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """主测试函数"""
    print("\n" + "=" * 60)
    print("智能客服运营功能测试")
    print("=" * 60)

    results = []

    # 运行所有测试
    results.append(("运营配置系统", test_operation_config()))
    results.append(("开场白功能", test_greeting()))
    results.append(("闲聊功能", test_chitchat()))
    results.append(("转人工功能", test_human_handoff()))
    results.append(("SOP知识", test_sop_knowledge()))

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
