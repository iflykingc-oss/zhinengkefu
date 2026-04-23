"""
知识库导入工具
支持飞书多维表格、Excel 等多种格式
"""
from langchain.tools import tool
from coze_coding_dev_sdk import KnowledgeClient, KnowledgeDocument, DataSourceType
from coze_coding_utils.log.write_log import request_context
from coze_coding_utils.runtime_ctx.context import new_context
import pandas as pd
import logging

logger = logging.getLogger(__name__)


@tool
def import_feishu_bitable_to_knowledge_base(app_token: str, table_id: str, dataset_name: str) -> str:
    """
    从飞书多维表格导入数据到知识库

    Args:
        app_token: 飞书多维表格的 App Token
        table_id: 数据表的 Table ID
        dataset_name: 知识库名称

    Returns:
        导入结果
    """
    ctx = request_context.get() or new_context(method="import_feishu_bitable_to_knowledge_base")

    try:
        # 获取飞书访问令牌
        from coze_workload_identity import Client
        client = Client()
        access_token = client.get_integration_credential("integration-feishu-base")

        # 创建飞书多维表格客户端
        feishu_client = FeishuBitableClient(access_token)

        # 获取数据
        records_data = feishu_client.get_all_records(app_token, table_id)

        if not records_data:
            return f"飞书多维表格 {table_id} 中没有数据"

        # 初始化知识库客户端
        kb_client = KnowledgeClient(ctx=ctx)

        # 批量导入到知识库
        imported_count = 0
        batch_size = 50  # 每批处理50条记录

        for i in range(0, len(records_data), batch_size):
            batch = records_data[i:i + batch_size]
            documents = []

            for record in batch:
                # 将记录转换为文本
                text_content = format_record_as_text(record)

                if text_content:
                    doc = KnowledgeDocument(
                        source=DataSourceType.TEXT,
                        raw_data=text_content
                    )
                    documents.append(doc)

            # 批量添加到知识库
            if documents:
                try:
                    kb_client.add_documents(
                        documents=documents,
                        table_name=dataset_name
                    )
                    imported_count += len(documents)
                except Exception as e:
                    logger.warning(f"批量导入失败（批次 {i//batch_size + 1}）: {e}")

        return f"成功导入 {imported_count} 条记录到知识库 '{dataset_name}'"

    except Exception as e:
        logger.error(f"导入飞书多维表格失败: {e}")
        return f"导入失败: {str(e)}"


@tool
def import_excel_to_knowledge_base(file_path: str, dataset_name: str) -> str:
    """
    从 Excel 文件导入数据到知识库

    Args:
        file_path: Excel 文件路径
        dataset_name: 知识库名称

    Returns:
        导入结果
    """
    ctx = request_context.get() or new_context(method="import_excel_to_knowledge_base")

    try:
        # 读取 Excel 文件
        df = pd.read_excel(file_path)

        if df.empty:
            return f"Excel 文件 {file_path} 中没有数据"

        # 将 DataFrame 转换为文本
        texts = []
        for idx, row in df.iterrows():
            row_text = format_row_as_text(row, idx)
            texts.append(row_text)

        # 初始化知识库客户端
        kb_client = KnowledgeClient(ctx=ctx)

        # 批量导入到知识库
        imported_count = 0
        batch_size = 50

        for i in range(0, len(texts), batch_size):
            batch = texts[i:i + batch_size]
            documents = []

            for text in batch:
                doc = KnowledgeDocument(
                    source=DataSourceType.TEXT,
                    raw_data=text
                )
                documents.append(doc)

            # 批量添加到知识库
            if documents:
                try:
                    kb_client.add_documents(
                        documents=documents,
                        table_name=dataset_name
                    )
                    imported_count += len(documents)
                except Exception as e:
                    logger.warning(f"批量导入失败（批次 {i//batch_size + 1}）: {e}")

        return f"成功导入 {imported_count} 条记录到知识库 '{dataset_name}'"

    except Exception as e:
        logger.error(f"导入 Excel 文件失败: {e}")
        return f"导入失败: {str(e)}"


@tool
def import_csv_to_knowledge_base(file_path: str, dataset_name: str) -> str:
    """
    从 CSV 文件导入数据到知识库

    Args:
        file_path: CSV 文件路径
        dataset_name: 知识库名称

    Returns:
        导入结果
    """
    ctx = request_context.get() or new_context(method="import_csv_to_knowledge_base")

    try:
        # 读取 CSV 文件
        df = pd.read_csv(file_path)

        if df.empty:
            return f"CSV 文件 {file_path} 中没有数据"

        # 将 DataFrame 转换为文本
        texts = []
        for idx, row in df.iterrows():
            row_text = format_row_as_text(row, idx)
            texts.append(row_text)

        # 初始化知识库客户端
        kb_client = KnowledgeClient(ctx=ctx)

        # 批量导入到知识库
        imported_count = 0
        batch_size = 50

        for i in range(0, len(texts), batch_size):
            batch = texts[i:i + batch_size]
            documents = []

            for text in batch:
                doc = KnowledgeDocument(
                    source=DataSourceType.TEXT,
                    raw_data=text
                )
                documents.append(doc)

            # 批量添加到知识库
            if documents:
                try:
                    kb_client.add_documents(
                        documents=documents,
                        table_name=dataset_name
                    )
                    imported_count += len(documents)
                except Exception as e:
                    logger.warning(f"批量导入失败（批次 {i//batch_size + 1}）: {e}")

        return f"成功导入 {imported_count} 条记录到知识库 '{dataset_name}'"

    except Exception as e:
        logger.error(f"导入 CSV 文件失败: {e}")
        return f"导入失败: {str(e)}"


def format_record_as_text(record: dict) -> str:
    """
    将飞书多维表格记录格式化为文本

    Args:
        record: 记录字典

    Returns:
        格式化后的文本
    """
    fields = record.get("fields", {})

    if not fields:
        return ""

    # 将字段转换为文本
    parts = []
    for field_name, field_value in fields.items():
        if field_value:
            # 处理不同类型的字段值
            if isinstance(field_value, list):
                value_str = ", ".join(str(v) for v in field_value)
            elif isinstance(field_value, dict):
                value_str = str(field_value)
            else:
                value_str = str(field_value)

            parts.append(f"{field_name}: {value_str}")

    return "\n".join(parts)


def format_row_as_text(row: pd.Series, idx: int) -> str:
    """
    将 DataFrame 行格式化为文本

    Args:
        row: DataFrame 行
        idx: 行索引

    Returns:
        格式化后的文本
    """
    parts = [f"记录 {idx + 1}:"]

    for col_name, col_value in row.items():
        if pd.notna(col_value):
            parts.append(f"  {col_name}: {col_value}")

    return "\n".join(parts)


class FeishuBitableClient:
    """飞书多维表格客户端"""

    def __init__(self, access_token: str):
        self.access_token = access_token
        self.base_url = "https://open.larkoffice.com/open-apis"

    def get_all_records(self, app_token: str, table_id: str, page_size: int = 100) -> list:
        """
        获取所有记录

        Args:
            app_token: App Token
            table_id: Table ID
            page_size: 每页大小

        Returns:
            记录列表
        """
        import requests

        records = []
        page_token = None

        while True:
            url = f"{self.base_url}/bitable/v1/apps/{app_token}/tables/{table_id}/records"

            headers = {
                "Authorization": f"Bearer {self.access_token}",
                "Content-Type": "application/json"
            }

            params = {"page_size": page_size}
            if page_token:
                params["page_token"] = page_token

            response = requests.get(url, headers=headers, params=params)
            response.raise_for_status()
            data = response.json()

            if data.get("code") != 0:
                raise Exception(f"飞书API错误: {data}")

            items = data.get("data", {}).get("items", [])
            records.extend(items)

            # 检查是否还有更多数据
            has_more = data.get("data", {}).get("has_more", False)
            if not has_more:
                break

            page_token = data.get("data", {}).get("page_token")

        return records
