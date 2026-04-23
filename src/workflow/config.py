"""
工作流配置系统
支持自定义节点配置和调试模式
"""
import json
import os
from typing import Dict, List, Optional, Any
from enum import Enum


class NodeStatus(str, Enum):
    """节点状态"""
    ENABLED = "enabled"
    DISABLED = "disabled"
    DEBUG = "debug"


class WorkflowConfig:
    """工作流配置"""

    def __init__(self, config_path: Optional[str] = None):
        self.workspace_path = os.getenv("COZE_WORKSPACE_PATH", "/workspace/projects")
        if config_path is None:
            config_path = os.path.join(self.workspace_path, "config/workflow_config.json")
        self.config_path = config_path
        self.config = self._load_default_config()

    def _load_default_config(self) -> Dict[str, Any]:
        """加载默认配置"""
        return {
            "workflow": {
                "name": "智能客服工作流",
                "version": "1.0.0",
                "debug_mode": False
            },
            "nodes": {
                "input_parser": {
                    "name": "输入解析节点",
                    "description": "解析用户输入，判断是否包含图片",
                    "status": NodeStatus.ENABLED,
                    "config": {
                        "max_input_length": 10000
                    }
                },
                "knowledge_search": {
                    "name": "知识库搜索节点",
                    "description": "在知识库中搜索相关信息",
                    "status": NodeStatus.ENABLED,
                    "config": {
                        "top_k": 5,
                        "min_score": 0.5,
                        "timeout": 30
                    }
                },
                "web_search": {
                    "name": "联网搜索节点",
                    "description": "在互联网上搜索信息",
                    "status": NodeStatus.ENABLED,
                    "config": {
                        "count": 5,
                        "need_summary": True,
                        "timeout": 30
                    }
                },
                "risk_assessment": {
                    "name": "风险评估节点",
                    "description": "评估外部信息的风险",
                    "status": NodeStatus.ENABLED,
                    "config": {
                        "strict_mode": True,
                        "check_reliability": True,
                        "check_safety": True
                    }
                },
                "answer_generation": {
                    "name": "答案生成节点",
                    "description": "生成最终答案",
                    "status": NodeStatus.ENABLED,
                    "config": {
                        "model": "doubao-seed-1-8-251228",
                        "temperature": 0.7,
                        "max_tokens": 4096
                    }
                },
                "feishu_notification": {
                    "name": "飞书通知节点",
                    "description": "发送通知到飞书群组",
                    "status": NodeStatus.ENABLED,
                    "config": {
                        "auto_send": False,
                        "send_on_important": True
                    }
                }
            },
            "edges": [
                {"from": "input_parser", "to": "knowledge_search"},
                {"from": "knowledge_search", "to": "web_search", "condition": "not_knowledge_found"},
                {"from": "knowledge_search", "to": "answer_generation", "condition": "knowledge_found"},
                {"from": "web_search", "to": "risk_assessment"},
                {"from": "risk_assessment", "to": "answer_generation", "condition": "not_risky"},
                {"from": "risk_assessment", "to": "answer_generation", "condition": "risky"},
                {"from": "answer_generation", "to": "feishu_notification", "condition": "enable_feishu"},
                {"from": "feishu_notification", "to": "__end__"},
                {"from": "answer_generation", "to": "__end__", "condition": "not_enable_feishu"}
            ]
        }

    def load_config(self) -> Dict[str, Any]:
        """加载配置"""
        if os.path.exists(self.config_path):
            with open(self.config_path, 'r', encoding='utf-8') as f:
                self.config = json.load(f)
        else:
            self.config = self._load_default_config()
            self.save_config()
        return self.config

    def save_config(self):
        """保存配置"""
        os.makedirs(os.path.dirname(self.config_path), exist_ok=True)
        with open(self.config_path, 'w', encoding='utf-8') as f:
            json.dump(self.config, f, ensure_ascii=False, indent=2)

    def get_node_config(self, node_id: str) -> Optional[Dict[str, Any]]:
        """获取节点配置"""
        return self.config.get("nodes", {}).get(node_id)

    def update_node_config(self, node_id: str, config: Dict[str, Any]):
        """更新节点配置"""
        if node_id in self.config.get("nodes", {}):
            self.config["nodes"][node_id]["config"].update(config)
            self.save_config()

    def update_node_status(self, node_id: str, status: NodeStatus):
        """更新节点状态"""
        if node_id in self.config.get("nodes", {}):
            self.config["nodes"][node_id]["status"] = status
            self.save_config()

    def enable_node(self, node_id: str):
        """启用节点"""
        self.update_node_status(node_id, NodeStatus.ENABLED)

    def disable_node(self, node_id: str):
        """禁用节点"""
        self.update_node_status(node_id, NodeStatus.DISABLED)

    def set_debug_node(self, node_id: str):
        """设置节点为调试模式"""
        self.update_node_status(node_id, NodeStatus.DEBUG)

    def add_node(self, node_id: str, name: str, description: str, config: Dict[str, Any]):
        """添加新节点"""
        self.config["nodes"][node_id] = {
            "name": name,
            "description": description,
            "status": NodeStatus.ENABLED,
            "config": config
        }
        self.save_config()

    def remove_node(self, node_id: str):
        """移除节点"""
        if node_id in self.config.get("nodes", {}):
            del self.config["nodes"][node_id]
            self.save_config()

    def set_debug_mode(self, enabled: bool):
        """设置调试模式"""
        self.config["workflow"]["debug_mode"] = enabled
        self.save_config()

    def get_enabled_nodes(self) -> List[str]:
        """获取启用的节点"""
        nodes = []
        for node_id, node_config in self.config.get("nodes", {}).items():
            if node_config.get("status") in [NodeStatus.ENABLED, NodeStatus.DEBUG]:
                nodes.append(node_id)
        return nodes

    def get_debug_nodes(self) -> List[str]:
        """获取调试模式的节点"""
        nodes = []
        for node_id, node_config in self.config.get("nodes", {}).items():
            if node_config.get("status") == NodeStatus.DEBUG:
                nodes.append(node_id)
        return nodes


# 全局配置实例
_workflow_config: Optional[WorkflowConfig] = None


def get_workflow_config() -> WorkflowConfig:
    """获取工作流配置单例"""
    global _workflow_config
    if _workflow_config is None:
        _workflow_config = WorkflowConfig()
    return _workflow_config
