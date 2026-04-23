# 智能客服运营后台使用指南

## 概述

运营后台提供了完整的客服运营配置能力，包括知识配置、日志导出、SOP流程画布、转人工策略、开场白、闲聊等功能。

## 功能模块

### 1. 运营配置管理

**端口**: 8005

**基础路径**: `/api/v5`

#### 配置管理接口

- `GET /api/v5/config` - 获取完整配置
- `PUT /api/v5/config` - 更新配置
- `GET /api/v5/config/{path:path}` - 获取配置值
- `PUT /api/v5/config/{path:path}` - 设置配置值

**示例**:
```bash
# 获取开场白配置
curl http://localhost:8005/api/v5/config/greeting.enabled

# 设置开场白延迟
curl -X PUT http://localhost:8005/api/v5/config/greeting.delay -d "3"
```

### 2. 开场白配置

**接口**:
- `GET /api/v5/greeting/messages` - 获取开场白列表
- `POST /api/v5/greeting/messages` - 添加开场白
- `DELETE /api/v5/greeting/messages?message=xxx` - 移除开场白

**配置项**:
```json
{
  "greeting": {
    "enabled": true,
    "messages": [
      "您好，我是智能客服助手，有什么可以帮您的吗？",
      "您好！请问有什么可以帮到您？"
    ],
    "delay": 0
  }
}
```

**使用场景**:
- 新用户首次进入
- 老用户再次访问
- VIP用户专属开场白

### 3. 闲聊配置

**接口**:
- `GET /api/v5/chitchat/intents` - 获取闲聊意图列表
- `POST /api/v5/chitchat/intents` - 添加闲聊意图
- `DELETE /api/v5/chitchat/intents/{intent}` - 移除闲聊意图

**配置项**:
```json
{
  "chitchat": {
    "enabled": true,
    "auto_detect": true,
    "intents": [
      {
        "intent": "greeting",
        "keywords": ["你好", "嗨", "hello", "hi"],
        "responses": ["你好！", "嗨！有什么可以帮您？"]
      }
    ]
  }
}
```

**内置意图**:
- greeting: 打招呼
- thanks: 感谢
- goodbye: 再见

### 4. 转人工策略

**接口**:
- `GET /api/v5/transfer/strategies` - 获取转人工策略列表
- `PUT /api/v5/transfer/strategies/{strategy_type}` - 更新转人工策略
- `GET /api/v5/transfer/channels` - 获取转人工渠道

**策略类型**:
1. **关键词策略** (keyword)
   - 触发条件: 用户输入包含关键词
   - 默认关键词: "转人工", "找客服", "投诉"

2. **轮次限制** (round_limit)
   - 触发条件: 对话轮次超过限制
   - 默认: 5轮

3. **情感分析** (sentiment)
   - 触发条件: 检测到负面/愤怒情绪
   - 默认阈值: 负面0.7, 愤怒0.8

**配置项**:
```json
{
  "transfer_to_human": {
    "enabled": true,
    "strategies": [
      {
        "type": "keyword",
        "name": "关键词转人工",
        "enabled": true,
        "config": {
          "keywords": ["转人工", "找客服"],
          "match_mode": "contains"
        }
      }
    ],
    "fallback_message": "正在为您转接人工客服，请稍候..."
  }
}
```

### 5. SOP流程配置

**接口**:
- `GET /api/v5/sop/knowledge` - 获取SOP知识库
- `POST /api/v5/sop/knowledge` - 添加SOP知识
- `DELETE /api/v5/sop/knowledge/{sop_id}` - 删除SOP知识

**SOP类型**:
- text: 纯文本
- rich_text: 富文本（图文混排）
- image: 图片内容
- video: 视频内容
- short_link: 短链接
- mixed: 混合内容

**示例**:
```json
{
  "id": "sop_refund",
  "name": "退款流程",
  "trigger_keywords": ["退款", "退货"],
  "content_type": "rich_text",
  "content": {
    "title": "退款申请流程",
    "text": "请按照以下步骤操作...",
    "image_url": "https://example.com/refund.png",
    "video_url": "https://example.com/refund.mp4"
  }
}
```

### 6. 画布配置

**接口**:
- `GET /api/v5/canvas/nodes` - 获取画布节点
- `POST /api/v5/canvas/nodes` - 添加画布节点
- `PUT /api/v5/canvas/nodes/{node_id}` - 更新画布节点
- `DELETE /api/v5/canvas/nodes/{node_id}` - 删除画布节点

**节点类型**:
- 输入节点
- 处理节点
- 输出节点
- 条件节点
- 转人工节点

### 7. 日志导出

**接口**:
- `GET /api/v5/export/conversations` - 导出会话日志
- `GET /api/v5/export/search_history` - 导出搜索日志
- `GET /api/v5/export/knowledge_base` - 导出知识库

**导出格式**:
- JSON
- CSV
- Markdown

**示例**:
```bash
# 导出会话日志（CSV格式）
curl "http://localhost:8005/api/v5/export/conversations?format=csv"

# 导出指定日期范围的会话日志
curl "http://localhost:8005/api/v5/export/conversations?format=json&start_date=2024-01-01&end_date=2024-01-31"
```

### 8. 统计数据

**接口**:
- `GET /api/v5/stats/dashboard` - 获取仪表板统计数据

**返回数据**:
```json
{
  "sop_count": 3,
  "greeting_enabled": true,
  "chitchat_enabled": true,
  "transfer_enabled": true,
  "canvas_nodes_count": 5
}
```

## 启动服务

### 1. 启动运营后台API

```bash
python -m src.api.operation_service
```

服务将在 `http://localhost:8005` 启动

### 2. 测试运营功能

```bash
python tests/test_operation_features.py
```

## 配置文件位置

- **运营配置**: `/workspace/projects/config/operation_config.json`
- **SOP知识**: `/workspace/projects/config/sop_knowledge.json`
- **工作流配置**: `/workspace/projects/config/workflow_config.json`

## 使用场景

### 场景1: 配置开场白

1. 获取当前开场白列表
```bash
curl http://localhost:8005/api/v5/greeting/messages
```

2. 添加新开场白
```bash
curl -X POST http://localhost:8005/api/v5/greeting/messages \
  -d "欢迎来到我们的客服中心，有什么可以帮您的吗？"
```

### 场景2: 配置转人工策略

1. 更新关键词策略
```bash
curl -X PUT http://localhost:8005/api/v5/transfer/strategies/keyword \
  -H "Content-Type: application/json" \
  -d '{
    "keywords": ["转人工", "找客服", "投诉", "人工帮助"],
    "match_mode": "contains"
  }'
```

### 场景3: 添加SOP知识

```bash
curl -X POST http://localhost:8005/api/v5/sop/knowledge \
  -H "Content-Type: application/json" \
  -d '{
    "name": "产品咨询",
    "trigger_keywords": ["产品", "功能", "价格"],
    "content_type": "text",
    "content": {
      "text": "我们的产品包含智能问答、知识库管理等功能。"
    }
  }'
```

### 场景4: 导出日志

```bash
# 导出本月会话日志
curl "http://localhost:8005/api/v5/export/conversations?format=csv&start_date=2024-01-01&end_date=2024-01-31" \
  -o conversations_202401.csv
```

## 注意事项

1. 配置修改后立即生效，无需重启服务
2. 导出的日志包含来源信息（knowledge_base/web_search/sop/llm）
3. 转人工策略优先级: 关键词 > 情感 > 轮次限制
4. 闲聊配置会优先于知识库搜索
5. 开场白仅在首条消息时发送

## 扩展能力

- 支持多渠道转人工（飞书、微信、邮件）
- 支持场景化开场白（新用户/VIP/老用户）
- 支持模板化闲聊（时间、天气、身份等）
- 支持可视化流程画布配置
- 支持多种格式导出日志

## API文档

详细的API文档请访问:
- Swagger UI: `http://localhost:8005/docs`
- ReDoc: `http://localhost:8005/redoc`
