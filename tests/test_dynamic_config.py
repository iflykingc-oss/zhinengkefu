"""
测试动态配置和 API 功能
"""
from config.dynamic_config import get_config_manager


def test_dynamic_config():
    """测试动态配置功能"""
    config_manager = get_config_manager()

    print("=== 测试1: 获取默认配置 ===")
    config = config_manager.load_config()
    print(f"当前模型: {config['config']['model']}")
    print(f"当前工具: {config['tools']}")
    print()

    print("=== 测试2: 获取可用模型列表 ===")
    models = config_manager.get_available_models()
    print(f"可用模型数量: {len(models)}")
    for model in models[:3]:  # 只打印前3个
        print(f"- {model['name']} ({model['id']})")
    print()

    print("=== 测试3: 更新模型配置 ===")
    new_config = config_manager.update_model_config(
        model="doubao-seed-2-0-pro-260215",
        temperature=0.5
    )
    print(f"更新后的模型: {new_config['config']['model']}")
    print(f"更新后的温度: {new_config['config']['temperature']}")
    print()

    print("=== 测试完成 ===")


if __name__ == "__main__":
    test_dynamic_config()
