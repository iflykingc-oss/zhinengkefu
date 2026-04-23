"""
数据分析工具
支持从飞书多维表格、Excel等数据源进行数据分析
"""
from langchain.tools import tool
import pandas as pd
import numpy as np
from typing import List, Dict, Any
import logging

logger = logging.getLogger(__name__)


@tool
def analyze_feishu_bitable(app_token: str, table_id: str) -> str:
    """
    分析飞书多维表格数据

    Args:
        app_token: 飞书多维表格的 App Token
        table_id: 数据表的 Table ID

    Returns:
        数据分析结果
    """
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

        # 转换为 DataFrame
        df = records_to_dataframe(records_data)

        if df.empty:
            return "数据为空"

        # 进行数据分析
        analysis_result = perform_data_analysis(df)

        return analysis_result

    except Exception as e:
        logger.error(f"分析飞书多维表格失败: {e}")
        return f"分析失败: {str(e)}"


@tool
def analyze_excel(file_path: str) -> str:
    """
    分析 Excel 文件数据

    Args:
        file_path: Excel 文件路径

    Returns:
        数据分析结果
    """
    try:
        # 读取 Excel 文件
        df = pd.read_excel(file_path)

        if df.empty:
            return f"Excel 文件 {file_path} 中没有数据"

        # 进行数据分析
        analysis_result = perform_data_analysis(df)

        return analysis_result

    except Exception as e:
        logger.error(f"分析 Excel 文件失败: {e}")
        return f"分析失败: {str(e)}"


@tool
def analyze_csv(file_path: str) -> str:
    """
    分析 CSV 文件数据

    Args:
        file_path: CSV 文件路径

    Returns:
        数据分析结果
    """
    try:
        # 读取 CSV 文件
        df = pd.read_csv(file_path)

        if df.empty:
            return f"CSV 文件 {file_path} 中没有数据"

        # 进行数据分析
        analysis_result = perform_data_analysis(df)

        return analysis_result

    except Exception as e:
        logger.error(f"分析 CSV 文件失败: {e}")
        return f"分析失败: {str(e)}"


@tool
def query_data(app_token: str, table_id: str, query_condition: str) -> str:
    """
    查询飞书多维表格数据

    Args:
        app_token: 飞书多维表格的 App Token
        table_id: 数据表的 Table ID
        query_condition: 查询条件（自然语言描述）

    Returns:
        查询结果
    """
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

        # 转换为 DataFrame
        df = records_to_dataframe(records_data)

        # 使用自然语言查询（这里简化实现）
        # TODO: 可以集成 LLM 进行更智能的查询解析
        result = perform_simple_query(df, query_condition)

        return result

    except Exception as e:
        logger.error(f"查询数据失败: {e}")
        return f"查询失败: {str(e)}"


def perform_data_analysis(df: pd.DataFrame) -> str:
    """
    执行数据分析

    Args:
        df: 数据 DataFrame

    Returns:
        分析结果（Markdown 格式）
    """
    result_parts = []

    result_parts.append("# 数据分析报告")
    result_parts.append("")

    # 1. 数据概览
    result_parts.append("## 1. 数据概览")
    result_parts.append("")
    result_parts.append(f"- 总行数: {len(df)}")
    result_parts.append(f"- 总列数: {len(df.columns)}")
    result_parts.append(f"- 列名: {', '.join(df.columns.tolist())}")
    result_parts.append("")

    # 2. 数据类型
    result_parts.append("## 2. 数据类型")
    result_parts.append("")
    for col, dtype in df.dtypes.items():
        result_parts.append(f"- {col}: {dtype}")
    result_parts.append("")

    # 3. 缺失值统计
    result_parts.append("## 3. 缺失值统计")
    result_parts.append("")
    missing_counts = df.isnull().sum()
    if missing_counts.sum() > 0:
        for col, count in missing_counts[missing_counts > 0].items():
            result_parts.append(f"- {col}: {count} ({count/len(df)*100:.2f}%)")
    else:
        result_parts.append("- 无缺失值")
    result_parts.append("")

    # 4. 数值型列统计
    numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
    if numeric_cols:
        result_parts.append("## 4. 数值型列统计")
        result_parts.append("")
        for col in numeric_cols:
            result_parts.append(f"### {col}")
            result_parts.append(f"- 平均值: {df[col].mean():.2f}")
            result_parts.append(f"- 中位数: {df[col].median():.2f}")
            result_parts.append(f"- 标准差: {df[col].std():.2f}")
            result_parts.append(f"- 最小值: {df[col].min()}")
            result_parts.append(f"- 最大值: {df[col].max()}")
            result_parts.append("")

    # 5. 分类列统计
    categorical_cols = df.select_dtypes(include=['object']).columns.tolist()
    if categorical_cols:
        result_parts.append("## 5. 分类列统计")
        result_parts.append("")
        for col in categorical_cols:
            value_counts = df[col].value_counts()
            result_parts.append(f"### {col}")
            result_parts.append(f"- 唯一值数量: {len(value_counts)}")
            result_parts.append(f"- Top 5 值:")
            for val, count in value_counts.head(5).items():
                result_parts.append(f"  - {val}: {count} ({count/len(df)*100:.2f}%)")
            result_parts.append("")

    # 6. 数据预览
    result_parts.append("## 6. 数据预览（前5行）")
    result_parts.append("")
    result_parts.append(df.head(5).to_markdown(index=False))
    result_parts.append("")

    return "\n".join(result_parts)


def perform_simple_query(df: pd.DataFrame, query: str) -> str:
    """
    执行简单查询

    Args:
        df: 数据 DataFrame
        query: 查询条件

    Returns:
        查询结果
    """
    result_parts = []
    result_parts.append(f"# 查询结果: {query}")
    result_parts.append("")

    # 简单的关键词匹配
    query_lower = query.lower()

    # 检查是否包含"最大"、"最小"、"平均"等关键词
    if "最大" in query or "max" in query_lower:
        numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
        if numeric_cols:
            result_parts.append("## 最大值")
            for col in numeric_cols:
                max_val = df[col].max()
                max_row = df[df[col] == max_val]
                result_parts.append(f"- {col}: {max_val}")
                result_parts.append(f"  对应行数据: {max_row.to_dict('records')[0]}")
            result_parts.append("")
            return "\n".join(result_parts)

    if "最小" in query or "min" in query_lower:
        numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
        if numeric_cols:
            result_parts.append("## 最小值")
            for col in numeric_cols:
                min_val = df[col].min()
                min_row = df[df[col] == min_val]
                result_parts.append(f"- {col}: {min_val}")
                result_parts.append(f"  对应行数据: {min_row.to_dict('records')[0]}")
            result_parts.append("")
            return "\n".join(result_parts)

    if "平均" in query or "average" in query_lower or "mean" in query_lower:
        numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
        if numeric_cols:
            result_parts.append("## 平均值")
            for col in numeric_cols:
                mean_val = df[col].mean()
                result_parts.append(f"- {col}: {mean_val:.2f}")
            result_parts.append("")
            return "\n".join(result_parts)

    # 模糊匹配
    matching_rows = []
    for idx, row in df.iterrows():
        row_str = str(row).lower()
        if any(keyword in row_str for keyword in query_lower.split()):
            matching_rows.append(row)

    if matching_rows:
        result_parts.append(f"## 找到 {len(matching_rows)} 条匹配记录")
        result_parts.append("")
        for i, row in enumerate(matching_rows[:10], 1):  # 最多显示10条
            result_parts.append(f"### 记录 {i}")
            for col, val in row.items():
                result_parts.append(f"- {col}: {val}")
            result_parts.append("")
    else:
        result_parts.append("未找到匹配的记录")

    return "\n".join(result_parts)


def records_to_dataframe(records_data: List[Dict[str, Any]]) -> pd.DataFrame:
    """
    将飞书记录转换为 DataFrame

    Args:
        records_data: 记录列表

    Returns:
        DataFrame
    """
    data = []
    for record in records_data:
        fields = record.get("fields", {})
        data.append(fields)

    return pd.DataFrame(data)


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
