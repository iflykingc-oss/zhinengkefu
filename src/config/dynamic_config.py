"""
动态配置管理
支持自定义模型和知识库配置
"""
import json
import os
from typing import Optional, Dict, Any
from datetime import datetime


class DynamicConfigManager:
    """动态配置管理器"""

    def __init__(self):
        self.workspace_path = os.getenv("COZE_WORKSPACE_PATH", "/workspace/projects")
        self.default_config_path = os.path.join(self.workspace_path, "config/agent_llm_config.json")

    def load_default_config(self) -> Dict[str, Any]:
        """加载默认配置"""
        with open(self.default_config_path, 'r', encoding='utf-8') as f:
            return json.load(f)

    def load_config(self, config_id: Optional[str] = None) -> Dict[str, Any]:
        """
        加载配置

        Args:
            config_id: 配置ID，如果为None则加载默认配置

        Returns:
            配置字典
        """
        if config_id is None:
            return self.load_default_config()

        # TODO: 从数据库加载配置
        # 这里先返回默认配置，后续可以扩展为从数据库加载
        return self.load_default_config()

    def save_config(self, config: Dict[str, Any], config_id: Optional[str] = None) -> bool:
        """
        保存配置

        Args:
            config: 配置字典
            config_id: 配置ID，如果为None则保存到数据库

        Returns:
            是否保存成功
        """
        # TODO: 保存到数据库
        # 这里先返回True，后续可以扩展为保存到数据库
        return True

    def update_model_config(
        self,
        model: str,
        temperature: Optional[float] = None,
        top_p: Optional[float] = None,
        max_completion_tokens: Optional[int] = None,
        timeout: Optional[int] = None,
        thinking: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        更新模型配置

        Args:
            model: 模型ID
            temperature: 温度参数
            top_p: top_p参数
            max_completion_tokens: 最大完成token数
            timeout: 超时时间
            thinking: 思考模式

        Returns:
            更新后的配置
        """
        config = self.load_config()

        # 更新模型配置
        config["config"]["model"] = model
        if temperature is not None:
            config["config"]["temperature"] = temperature
        if top_p is not None:
            config["config"]["top_p"] = top_p
        if max_completion_tokens is not None:
            config["config"]["max_completion_tokens"] = max_completion_tokens
        if timeout is not None:
            config["config"]["timeout"] = timeout
        if thinking is not None:
            config["config"]["thinking"] = thinking

        # 保存配置
        self.save_config(config)

        return config

    def update_system_prompt(self, system_prompt: str) -> Dict[str, Any]:
        """
        更新系统提示词

        Args:
            system_prompt: 新的系统提示词

        Returns:
            更新后的配置
        """
        config = self.load_config()
        config["sp"] = system_prompt

        # 保存配置
        self.save_config(config)

        return config

    def update_tools(self, tools: list) -> Dict[str, Any]:
        """
        更新工具列表

        Args:
            tools: 工具列表

        Returns:
            更新后的配置
        """
        config = self.load_config()
        config["tools"] = tools

        # 保存配置
        self.save_config(config)

        return config

    def get_available_models(self) -> list:
        """
        获取可用模型列表

        Returns:
            可用模型列表
        """
        # 从技能文档中获取的可用模型
        return [
            {
                "id": "doubao-seed-2-0-pro-260215",
                "name": "豆包 Seed 2.0 Pro",
                "description": "旗舰级全能通用模型，面向 Agent 时代的复杂推理与长链路任务"
            },
            {
                "id": "doubao-seed-2-0-lite-260215",
                "name": "豆包 Seed 2.0 Lite",
                "description": "均衡型模型，兼顾性能与成本"
            },
            {
                "id": "doubao-seed-1-8-251228",
                "name": "豆包 Seed 1.8",
                "description": "多模态 Agent 优化模型"
            },
            {
                "id": "doubao-seed-1-6-vision-250815",
                "name": "豆包 Seed 1.6 Vision",
                "description": "视觉理解 SOTA 模型"
            },
            {
                "id": "deepseek-v3-2-251201",
                "name": "DeepSeek V3.2",
                "description": "平衡推理能力与输出长度"
            },
            {
                "id": "kimi-k2-5-260127",
                "name": "Kimi K2.5",
                "description": "Kimi 迄今最智能的模型"
            },
            {
                "id": "glm-4-7-251222",
                "name": "GLM-4.7",
                "description": "智谱最新旗舰模型"
            }
        ]


# 全局配置管理器实例
_config_manager: Optional[DynamicConfigManager] = None


def get_config_manager() -> DynamicConfigManager:
    """获取配置管理器单例"""
    global _config_manager
    if _config_manager is None:
        _config_manager = DynamicConfigManager()
    return _config_manager
