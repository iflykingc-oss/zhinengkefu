# 智能客服系统 - 部署和使用指南

## 功能特性

✅ **智能客服能力**
- 支持知识库搜索（优先级最高）
- 支持联网搜索（知识库无结果时自动启用）
- 支持风险评估（自动过滤不安全信息）
- 支持多模态输入（文本、语音、图片）

✅ **飞书集成**
- 支持发送文本消息到飞书群组
- 支持发送富文本消息到飞书群组
- 自动在重要场景发送通知

✅ **微信小程序支持**
- 提供 RESTful API 接口
- 支持 CORS 跨域访问
- 支持多模态输入

✅ **动态配置**
- 支持自定义模型选择
- 支持自定义系统提示词
- 支持自定义工具列表
- 运行时配置更新

## 快速开始

### 1. 启动 API 服务

```bash
# 开发环境
cd /workspace/projects
PYTHONPATH=/workspace/projects/src:$PYTHONPATH uv run python -m uvicorn src.api.service:app --reload --host 0.0.0.0 --port 8000

# 生产环境
uvicorn src.api.service:app --host 0.0.0.0 --port 8000
```

### 2. API 接口文档

服务启动后，访问 `http://localhost:8000/docs` 查看 Swagger API 文档。

### 3. 主要接口

#### 聊天接口
```http
POST /api/chat
Content-Type: application/json

{
  "message": "用户问题",
  "image_url": "图片URL（可选）",
  "config_id": "配置ID（可选）",
  "enable_feishu": false
}
```

#### 获取配置接口
```http
GET /api/config
```

#### 更新配置接口
```http
POST /api/config
Content-Type: application/json

{
  "model": "doubao-seed-2-0-pro-260215",
  "temperature": 0.7,
  "system_prompt": "自定义提示词"
}
```

#### 获取模型列表接口
```http
GET /api/models
```

## 飞书集成配置

### 1. 获取 Webhook URL

飞书集成已通过环境变量自动配置，无需手动设置 Webhook URL。

### 2. 使用飞书通知

在智能体对话中，Agent 可以自动发送消息到飞书群组：

```
用户: 请帮我发送一条消息到飞书，内容是"测试通知"
Agent: 【已发送飞书通知】消息"测试通知"已成功发送到飞书群组。
```

### 3. 飞书通知触发场景

- 用户明确要求发送到飞书
- 系统检测到需要人工介入的重要问题
- 需要记录到飞书的重要咨询记录

## 微信小程序集成

### 1. 小程序代码示例

```javascript
// pages/chat/chat.js
Page({
  data: {
    message: '',
    response: '',
    imageUrl: ''
  },

  // 发送消息
  async sendMessage() {
    const { message, imageUrl } = this.data;

    wx.request({
      url: 'https://your-api-domain.com/api/chat',
      method: 'POST',
      data: {
        message: message,
        image_url: imageUrl || null,
        enable_feishu: false
      },
      header: {
        'content-type': 'application/json'
      },
      success: (res) => {
        this.setData({
          response: res.data.response
        });
      }
    });
  },

  // 选择图片
  chooseImage() {
    wx.chooseImage({
      count: 1,
      success: (res) => {
        const tempFilePaths = res.tempFilePaths;
        // 上传图片到服务器获取URL
        this.setData({
          imageUrl: tempFilePaths[0]
        });
      }
    });
  }
});
```

### 2. 小程序配置

在 `app.json` 中配置服务器域名：

```json
{
  "pages": ["pages/chat/chat"],
  "window": {
    "navigationBarTitleText": "智能客服"
  },
  "networkTimeout": {
    "request": 10000
  }
}
```

### 3. 语音输入

使用微信语音识别 API：

```javascript
wx.startRecord({
  success: function() {
    // 录音结束后转换文字
    wx.translateVoice({
      localId: res.localId,
      isShowProgressTips: 1,
      success: function(res) {
        const transcription = res.translateResult;
        // 发送识别的文本到服务器
        that.sendMessage(transcription);
      }
    });
  }
});
```

## 动态配置说明

### 1. 可用模型列表

| 模型ID | 名称 | 描述 |
|--------|------|------|
| doubao-seed-2-0-pro-260215 | 豆包 Seed 2.0 Pro | 旗舰级全能通用模型 |
| doubao-seed-2-0-lite-260215 | 豆包 Seed 2.0 Lite | 均衡型模型 |
| doubao-seed-1-8-251228 | 豆包 Seed 1.8 | 多模态 Agent 优化模型 |
| doubao-seed-1-6-vision-250815 | 豆包 Seed 1.6 Vision | 视觉理解 SOTA 模型 |
| deepseek-v3-2-251201 | DeepSeek V3.2 | 平衡推理能力与输出长度 |
| kimi-k2-5-260127 | Kimi K2.5 | Kimi 迄今最智能的模型 |
| glm-4-7-251222 | GLM-4.7 | 智谱最新旗舰模型 |

### 2. 配置参数说明

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| model | string | doubao-seed-1-8-251228 | 模型ID |
| temperature | float | 0.7 | 温度参数 (0-2) |
| top_p | float | 0.9 | Nucleus采样 (0-1) |
| max_completion_tokens | int | 4096 | 最大完成token数 |
| timeout | int | 600 | 超时时间（秒） |
| thinking | string | disabled | 思考模式 (enabled/disabled) |

### 3. 更新配置示例

```bash
# 使用 curl 更新配置
curl -X POST http://localhost:8000/api/config \
  -H "Content-Type: application/json" \
  -d '{
    "model": "doubao-seed-2-0-pro-260215",
    "temperature": 0.5,
    "system_prompt": "你是一个专业的智能客服助手..."
  }'
```

## 知识库配置

### 1. 添加文档到知识库

```python
from coze_coding_dev_sdk import KnowledgeClient, KnowledgeDocument, DataSourceType

client = KnowledgeClient()

# 添加文本
doc = KnowledgeDocument(
    source=DataSourceType.TEXT,
    raw_data="这是要添加到知识库的文本内容"
)
client.add_documents(documents=[doc], table_name="coze_doc_knowledge")

# 添加URL
doc = KnowledgeDocument(
    source=DataSourceType.URL,
    url="https://example.com"
)
client.add_documents(documents=[doc], table_name="coze_doc_knowledge")
```

### 2. 自定义知识库配置

通过更新系统提示词，可以自定义知识库的使用方式：

```json
{
  "system_prompt": "你的系统提示词...",
  "tools": ["search_knowledge_base", "search_web"]
}
```

## 部署建议

### 1. 生产环境部署

- 使用 Nginx 作为反向代理
- 启用 HTTPS
- 配置 CORS 白名单
- 设置合理的超时时间
- 启用日志记录

### 2. Nginx 配置示例

```nginx
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    }
}
```

### 3. Docker 部署

```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY . .
RUN pip install -r requirements.txt

CMD ["uvicorn", "src.api.service:app", "--host", "0.0.0.0", "--port", "8000"]
```

## 故障排查

### 1. 飞书通知失败

- 检查环境变量是否正确配置
- 检查 Webhook URL 是否有效
- 检查飞书群组权限

### 2. 微信小程序无法连接

- 检查服务器域名是否在白名单中
- 检查 CORS 配置
- 检查网络连接

### 3. 动态配置不生效

- 检查配置格式是否正确
- 检查模型ID是否有效
- 查看服务日志

## 技术支持

如有问题，请查看：
- API 文档：`http://localhost:8000/docs`
- 服务日志：`/app/work/logs/bypass/app.log`
