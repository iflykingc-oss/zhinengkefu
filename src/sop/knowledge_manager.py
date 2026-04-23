"""
SOP知识管理系统
支持配置SOP知识，命中后进入SOP流程
"""
import json
import os
import logging
from typing import Dict, List, Any, Optional
from datetime import datetime
from enum import Enum

logger = logging.getLogger(__name__)


class ContentType(str, Enum):
    """内容类型"""
    TEXT = "text"
    RICH_TEXT = "rich_text"
    IMAGE = "image"
    VIDEO = "video"
    SHORT_LINK = "short_link"
    MIXED = "mixed"


class SOPKnowledge:
    """SOP知识"""

    def __init__(
        self,
        id: str,
        name: str,
        trigger_keywords: List[str],
        content_type: ContentType,
        content: Dict[str, Any],
        flow_config: Optional[Dict[str, Any]] = None,
        metadata: Optional[Dict[str, Any]] = None
    ):
        self.id = id
        self.name = name
        self.trigger_keywords = trigger_keywords
        self.content_type = content_type
        self.content = content
        self.flow_config = flow_config or {}
        self.metadata = metadata or {}
        self.created_at = datetime.now().isoformat()
        self.updated_at = datetime.now().isoformat()

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "id": self.id,
            "name": self.name,
            "trigger_keywords": self.trigger_keywords,
            "content_type": self.content_type.value,
            "content": self.content,
            "flow_config": self.flow_config,
            "metadata": self.metadata,
            "created_at": self.created_at,
            "updated_at": self.updated_at
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "SOPKnowledge":
        """从字典创建"""
        return cls(
            id=data["id"],
            name=data["name"],
            trigger_keywords=data["trigger_keywords"],
            content_type=ContentType(data["content_type"]),
            content=data["content"],
            flow_config=data.get("flow_config"),
            metadata=data.get("metadata")
        )


class SOPKnowledgeManager:
    """SOP知识管理器"""

    def __init__(self, config_path: Optional[str] = None):
        self.workspace_path = os.getenv("COZE_WORKSPACE_PATH", "/workspace/projects")
        if config_path is None:
            config_path = os.path.join(self.workspace_path, "config/sop_knowledge.json")
        self.config_path = config_path
        self.knowledge_base: Dict[str, SOPKnowledge] = {}
        self.load_knowledge()

    def load_knowledge(self):
        """加载知识库"""
        if os.path.exists(self.config_path):
            with open(self.config_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                for item in data:
                    sop = SOPKnowledge.from_dict(item)
                    self.knowledge_base[sop.id] = sop
            logger.info(f"已加载 {len(self.knowledge_base)} 条SOP知识")

    def save_knowledge(self):
        """保存知识库"""
        data = [sop.to_dict() for sop in self.knowledge_base.values()]
        os.makedirs(os.path.dirname(self.config_path), exist_ok=True)
        with open(self.config_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        logger.info(f"已保存 {len(self.knowledge_base)} 条SOP知识")

    def add_knowledge(self, sop: SOPKnowledge) -> bool:
        """
        添加知识

        Args:
            sop: SOP知识对象

        Returns:
            是否添加成功
        """
        if sop.id in self.knowledge_base:
            logger.warning(f"SOP知识 {sop.id} 已存在，将被覆盖")

        self.knowledge_base[sop.id] = sop
        self.save_knowledge()
        return True

    def remove_knowledge(self, sop_id: str) -> bool:
        """
        移除知识

        Args:
            sop_id: SOP知识ID

        Returns:
            是否移除成功
        """
        if sop_id in self.knowledge_base:
            del self.knowledge_base[sop_id]
            self.save_knowledge()
            return True
        return False

    def get_knowledge(self, sop_id: str) -> Optional[SOPKnowledge]:
        """
        获取知识

        Args:
            sop_id: SOP知识ID

        Returns:
            SOP知识对象
        """
        return self.knowledge_base.get(sop_id)

    def list_knowledge(self) -> List[SOPKnowledge]:
        """
        列出所有知识

        Returns:
            SOP知识列表
        """
        return list(self.knowledge_base.values())

    def match_knowledge(self, query: str) -> Optional[SOPKnowledge]:
        """
        匹配知识

        Args:
            query: 用户查询

        Returns:
            匹配的SOP知识
        """
        query_lower = query.lower()

        for sop in self.knowledge_base.values():
            # 检查是否包含触发关键词
            for keyword in sop.trigger_keywords:
                if keyword.lower() in query_lower:
                    logger.info(f"匹配到SOP知识: {sop.name} (关键词: {keyword})")
                    return sop

        return None

    def update_knowledge(self, sop_id: str, **kwargs) -> bool:
        """
        更新知识

        Args:
            sop_id: SOP知识ID
            **kwargs: 更新的字段

        Returns:
            是否更新成功
        """
        sop = self.get_knowledge(sop_id)
        if not sop:
            return False

        # 更新字段
        for key, value in kwargs.items():
            if hasattr(sop, key):
                setattr(sop, key, value)
                if key == "content_type" and isinstance(value, str):
                    setattr(sop, key, ContentType(value))

        sop.updated_at = datetime.now().isoformat()
        self.save_knowledge()
        return True


# 创建示例SOP知识
def create_sample_sop_knowledge():
    """创建示例SOP知识"""
    samples = []

    # 示例1：退款流程
    samples.append(SOPKnowledge(
        id="sop_refund",
        name="退款流程",
        trigger_keywords=["退款", "退货", "申请退款"],
        content_type=ContentType.RICH_TEXT,
        content={
            "title": "退款申请流程",
            "text": "您好，关于退款申请，请按照以下流程操作：\n\n1. 登录您的账户\n2. 找到订单详情\n3. 点击申请退款\n4. 填写退款原因\n5. 提交申请",
            "image_url": "https://example.com/refund_flow.png",
            "video_url": "https://example.com/refund_video.mp4",
            "short_link": "https://example.com/refund"
        },
        flow_config={
            "steps": [
                {"step": 1, "action": "verify_order", "message": "正在验证订单信息..."},
                {"step": 2, "action": "check_policy", "message": "正在检查退款政策..."},
                {"step": 3, "action": "process_refund", "message": "正在处理退款..."}
            ]
        }
    ))

    # 示例2：账号注册
    samples.append(SOPKnowledge(
        id="sop_register",
        name="账号注册流程",
        trigger_keywords=["注册", "开户", "创建账号"],
        content_type=ContentType.MIXED,
        content={
            "title": "账号注册指南",
            "sections": [
                {
                    "type": "text",
                    "content": "欢迎使用我们的服务！请按照以下步骤注册账号："
                },
                {
                    "type": "image",
                    "url": "https://example.com/register_step1.png",
                    "caption": "步骤1：填写基本信息"
                },
                {
                    "type": "text",
                    "content": "2. 验证手机号码"
                },
                {
                    "type": "video",
                    "url": "https://example.com/register_tutorial.mp4",
                    "caption": "注册教程视频"
                },
                {
                    "type": "short_link",
                    "url": "https://example.com/register_now",
                    "text": "立即注册"
                }
            ]
        }
    ))

    # 示例3：产品咨询
    samples.append(SOPKnowledge(
        id="sop_product",
        name="产品咨询",
        trigger_keywords=["产品", "价格", "功能"],
        content_type=ContentType.TEXT,
        content={
            "title": "产品信息",
            "text": "我们的产品包含以下功能：\n\n1. 智能问答\n2. 知识库管理\n3. 多模态交互\n\n价格方案请访问官网查看。"
        }
    ))

    return samples


# 初始化SOP知识管理器
_sop_manager: Optional[SOPKnowledgeManager] = None


def get_sop_manager() -> SOPKnowledgeManager:
    """获取SOP知识管理器"""
    global _sop_manager
    if _sop_manager is None:
        _sop_manager = SOPKnowledgeManager()

        # 如果知识库为空，添加示例数据
        if not _sop_manager.knowledge_base:
            samples = create_sample_sop_knowledge()
            for sample in samples:
                _sop_manager.add_knowledge(sample)

    return _sop_manager
