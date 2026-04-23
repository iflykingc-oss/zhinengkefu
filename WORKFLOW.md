# 智能客服工作流 - 使用指南

## 概述

智能客服工作流是一个基于 LangGraph 构建的模块化、可配置的工作流系统，支持自定义调试、动态配置节点和灵活的扩展能力。

## 工作流架构

### 节点列表

| 节点ID | 名称 | 描述 |
|--------|------|------|
| `input_parser` | 输入解析节点 | 解析用户输入，判断是否包含图片 |
| `knowledge_search` | 知识库搜索节点 | 在知识库中搜索相关信息 |
| `web_search` | 联网搜索节点 | 在互联网上搜索信息 |
| `risk_assessment` | 风险评估节点 | 评估外部信息的风险 |
| `answer_generation` | 答案生成节点 | 生成最终答案 |
| `feishu_notification` | 飞书通知节点 | 发送通知到飞书群组 |

### 工作流图

```
┌─────────────┐
│ input_parser│
└──────┬──────┘
       │
       ▼
┌──────────────┐
│knowledge_srch│
└──────┬───────┘
       │
       ├─(找到知识)──────┐
       │                  │
       ▼                  ▼
  ┌─────────┐    ┌───────────┐
  │web_search│    │answer_gen │
  └────┬─────┘    └─────┬─────┘
       │                │
       ▼                ▼
  ┌──────────┐    ┌──────────┐
  │risk_asst │    │feishu_nt │
  └────┬─────┘    └────┬─────┘
       │                │
       └────────┬───────┘
                │
                ▼
            ┌──────┐
            │ END  │
            └──────┘
```

## 快速开始

### 1. 启动工作流 API 服务

```bash
# 开发环境
PYTHONPATH=/workspace/projects/src:$PYTHONPATH uv run python -m uvicorn src.api.workflow_service:app --reload --host 0.0.0.0 --port 8001

# 生产环境
uvicorn src.api.workflow_service:app --host 0.0.0.0 --port 8001
```

### 2. 访问 API 文档

服务启动后，访问 `http://localhost:8001/docs` 查看 Swagger API 文档。

## API 接口

### 聊天接口

```http
POST /api/workflow/chat
Content-Type: application/json

{
  "message": "用户问题",
  "image_url": "图片URL（可选）",
  "enable_feishu": false,
  "debug_mode": true
}
```

**响应示例：**

```json
{
  "answer": "【网络搜索答案】今天北京天气...",
  "source": "web_search",
  "debug_info": [
    "[input_parser] 开始解析用户输入",
    "[knowledge_search] 开始知识库搜索",
    ...
  ],
  "execution_steps": [...]
}
```

### 获取工作流结构

```http
GET /api/workflow/structure
```

**响应示例：**

```json
{
  "workflow": {
    "name": "智能客服工作流",
    "version": "1.0.0",
    "debug_mode": false
  },
  "nodes": {...},
  "edges": [...]
}
```

### 更新节点配置

```http
POST /api/workflow/nodes/config
Content-Type: application/json

{
  "node_id": "knowledge_search",
  "config": {
    "top_k": 10,
    "min_score": 0.6
  }
}
```

### 更新节点状态

```http
POST /api/workflow/nodes/status
Content-Type: application/json

{
  "node_id": "knowledge_search",
  "status": "debug"
}
```

**状态值：**
- `enabled`: 启用节点
- `disabled`: 禁用节点
- `debug`: 调试模式

### 添加新节点

```http
POST /api/workflow/nodes/add
Content-Type: application/json

{
  "node_id": "custom_node",
  "name": "自定义节点",
  "description": "这是一个自定义节点",
  "config": {
    "param1": "value1"
  }
}
```

### 删除节点

```http
DELETE /api/workflow/nodes/{node_id}
```

### 启用/禁用调试模式

```http
POST /api/workflow/debug/enable
POST /api/workflow/debug/disable
```

## 节点配置详解

### 输入解析节点 (input_parser)

```json
{
  "max_input_length": 10000
}
```

- `max_input_length`: 最大输入长度限制

### 知识库搜索节点 (knowledge_search)

```json
{
  "top_k": 5,
  "min_score": 0.5,
  "timeout": 30
}
```

- `top_k`: 返回结果数量
- `min_score`: 最小相似度阈值 (0.0-1.0)
- `timeout`: 超时时间（秒）

### 联网搜索节点 (web_search)

```json
{
  "count": 5,
  "need_summary": true,
  "timeout": 30
}
```

- `count`: 返回结果数量
- `need_summary`: 是否启用 AI 摘要
- `timeout`: 超时时间（秒）

### 风险评估节点 (risk_assessment)

```json
{
  "strict_mode": true,
  "check_reliability": true,
  "check_safety": true
}
```

- `strict_mode`: 严格模式
- `check_reliability`: 检查来源可靠性
- `check_safety`: 检查内容安全性

### 答案生成节点 (answer_generation)

```json
{
  "model": "doubao-seed-1-8-251228",
  "temperature": 0.7,
  "max_tokens": 4096
}
```

- `model`: 模型ID
- `temperature`: 温度参数 (0-2)
- `max_tokens`: 最大生成token数

### 飞书通知节点 (feishu_notification)

```json
{
  "auto_send": false,
  "send_on_important": true
}
```

- `auto_send`: 自动发送
- `send_on_important`: 重要信息发送

## 调试模式

### 启用调试模式

调试模式会记录每个节点的执行过程，方便排查问题。

**方法1：通过 API**
```http
POST /api/workflow/debug/enable
```

**方法2：在聊天时启用**
```json
{
  "message": "测试问题",
  "debug_mode": true
}
```

**方法3：配置文件**
```python
from workflow.config import get_workflow_config

config = get_workflow_config()
config.set_debug_mode(True)
```

### 查看调试信息

当 `debug_mode` 为 `true` 时，响应会包含 `debug_info` 字段：

```json
{
  "answer": "...",
  "debug_info": [
    "[input_parser] 开始解析用户输入",
    "[input_parser] 纯文本输入: 今天北京的天气怎么样？...",
    "[input_parser] 输入解析完成",
    "[knowledge_search] 开始知识库搜索",
    ...
  ]
}
```

## 自定义节点

### 步骤 1: 定义节点函数

在 `src/workflow/nodes.py` 中添加新节点：

```python
def custom_node(state: WorkflowState) -> WorkflowState:
    """
    自定义节点
    """
    _add_debug_info(state, "custom_node", "开始执行自定义节点")

    # 你的业务逻辑
    result = process_data(state["user_input"])

    state["custom_result"] = result

    _add_debug_info(state, "custom_node", "自定义节点执行完成")
    return state
```

### 步骤 2: 注册节点

在 `src/workflow/graph.py` 中注册节点：

```python
def build_workflow(debug_mode: bool = False):
    workflow = StateGraph(WorkflowState)

    # 添加节点
    workflow.add_node("custom_node", custom_node)

    # 添加边
    workflow.add_edge("answer_generation", "custom_node")
    workflow.add_edge("custom_node", END)

    return workflow.compile()
```

### 步骤 3: 更新配置

在 `src/workflow/config.py` 中添加节点配置：

```python
def _load_default_config(self) -> Dict[str, Any]:
    return {
        "nodes": {
            "custom_node": {
                "name": "自定义节点",
                "description": "这是一个自定义节点",
                "status": NodeStatus.ENABLED,
                "config": {
                    "param1": "value1"
                }
            }
        }
    }
```

## Python SDK 使用

### 基本使用

```python
from workflow.graph import build_workflow
from workflow.state import WorkflowState

# 构建工作流
app = build_workflow(debug_mode=True)

# 初始化状态
initial_state: WorkflowState = {
    "messages": [],
    "user_input": "今天北京的天气怎么样？",
    "has_image": False,
    "image_url": None,
    "knowledge_result": None,
    "knowledge_found": False,
    "web_result": None,
    "web_found": False,
    "risk_assessment": None,
    "is_risky": False,
    "final_answer": None,
    "answer_source": "",
    "debug_mode": True,
    "debug_info": [],
    "current_step": "",
    "enable_feishu": False,
    "feishu_sent": False,
    "config_id": None
}

# 执行工作流
result = app.invoke(initial_state)

# 获取结果
print(result["final_answer"])
print(result["debug_info"])
```

### 节点配置管理

```python
from workflow.config import get_workflow_config, NodeStatus

config = get_workflow_config()

# 获取节点配置
kb_config = config.get_node_config("knowledge_search")

# 更新节点配置
config.update_node_config("knowledge_search", {"top_k": 10})

# 切换节点状态
config.enable_node("knowledge_search")
config.disable_node("knowledge_search")
config.set_debug_node("knowledge_search")

# 添加新节点
config.add_node(
    "custom_node",
    "自定义节点",
    "节点描述",
    {"param": "value"}
)

# 删除节点
config.remove_node("custom_node")

# 获取启用/调试节点列表
enabled_nodes = config.get_enabled_nodes()
debug_nodes = config.get_debug_nodes()
```

## 微信小程序集成

### 基本聊天

```javascript
// 发送消息
wx.request({
  url: 'https://your-api-domain.com/api/workflow/chat',
  method: 'POST',
  data: {
    message: '用户问题',
    debug_mode: false
  },
  success: (res) => {
    console.log(res.data.answer);
    console.log(res.data.execution_steps);
  }
});
```

### 带图片的聊天

```javascript
// 选择图片
wx.chooseImage({
  success: (res) => {
    const tempFilePaths = res.tempFilePaths;

    // 发送消息和图片
    wx.request({
      url: 'https://your-api-domain.com/api/workflow/chat',
      method: 'POST',
      data: {
        message: '这张图片是什么？',
        image_url: tempFilePaths[0],
        debug_mode: true
      },
      success: (res) => {
        console.log(res.data);
      }
    });
  }
});
```

### 配置工作流

```javascript
// 获取工作流结构
wx.request({
  url: 'https://your-api-domain.com/api/workflow/structure',
  success: (res) => {
    console.log(res.data);
  }
});

// 更新节点配置
wx.request({
  url: 'https://your-api-domain.com/api/workflow/nodes/config',
  method: 'POST',
  data: {
    node_id: 'knowledge_search',
    config: { top_k: 10 }
  },
  success: (res) => {
    console.log('配置更新成功');
  }
});
```

## 高级特性

### 条件路由

工作流支持基于状态的条件路由：

```python
from workflow.routes import should_search_web

workflow.add_conditional_edges(
    "knowledge_search",
    should_search_web,
    {
        "web_search": "web_search",
        "answer_generation": "answer_generation"
    }
)
```

### 状态管理

工作流状态在节点之间传递和更新：

```python
class WorkflowState(TypedDict):
    # 消息历史
    messages: Annotated[List[BaseMessage], add_messages]

    # 用户输入
    user_input: str

    # ... 其他状态字段
```

### 调试信息

每个节点都可以记录调试信息：

```python
def my_node(state: WorkflowState) -> WorkflowState:
    _add_debug_info(state, "my_node", "开始执行")
    # 节点逻辑
    _add_debug_info(state, "my_node", "执行完成")
    return state
```

## 故障排查

### 常见问题

**问题1：工作流执行失败**
- 检查节点配置是否正确
- 启用调试模式查看详细日志
- 检查 API 密钥和基础 URL

**问题2：节点未执行**
- 检查节点状态是否为 `enabled`
- 检查工作流边的连接
- 检查条件路由逻辑

**问题3：调试信息未显示**
- 确保已启用调试模式
- 检查节点中是否正确调用 `_add_debug_info`

### 日志查看

```bash
# 查看工作流日志
tail -f /app/work/logs/bypass/app.log

# 搜索特定错误
grep "ERROR" /app/work/logs/bypass/app.log
```

## 最佳实践

1. **启用调试模式**：在开发阶段启用调试模式，方便排查问题
2. **节点配置**：根据业务需求调整节点参数
3. **错误处理**：在节点中添加适当的错误处理
4. **状态管理**：合理设计状态结构，避免冗余
5. **性能优化**：对于耗时操作，考虑使用异步处理

## 示例场景

### 场景1：纯知识库问答

```json
{
  "message": "公司服务时间",
  "debug_mode": true
}
```

工作流路径：`input_parser → knowledge_search → answer_generation → END`

### 场景2：联网搜索

```json
{
  "message": "今天北京的天气",
  "debug_mode": true
}
```

工作流路径：`input_parser → knowledge_search → web_search → risk_assessment → answer_generation → END`

### 场景3：图片识别 + 联网搜索

```json
{
  "message": "这是什么？",
  "image_url": "https://example.com/image.jpg",
  "debug_mode": true
}
```

工作流路径：`input_parser → knowledge_search → web_search → risk_assessment → answer_generation → END`

### 场景4：飞书通知

```json
{
  "message": "重要问题",
  "enable_feishu": true,
  "debug_mode": true
}
```

工作流路径：`input_parser → knowledge_search → web_search → risk_assessment → answer_generation → feishu_notification → END`

## 总结

智能客服工作流提供了：
- ✅ 模块化设计，易于扩展
- ✅ 灵活的配置系统
- ✅ 强大的调试功能
- ✅ 完整的 API 支持
- ✅ 微信小程序集成
- ✅ 自定义节点能力

通过合理配置和使用，可以快速构建出功能强大的智能客服系统。
