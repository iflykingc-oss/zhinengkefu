# 智能客服系统 - v3.0 功能详解

## 新增功能总览

### ✅ 1. 飞书机器人互动
- 支持通过飞书机器人与智能客服实时互动
- 支持文本消息和图片消息
- 自动调用工作流处理，返回智能回复

### ✅ 2. 知识库多格式导入
- **飞书多维表格**：直接从飞书多维表格导入数据到知识库
- **Excel 文件**：支持 .xlsx 和 .xls 格式
- **CSV 文件**：支持标准 CSV 格式
- 批量导入，自动分块处理

### ✅ 3. 数据分析功能
- 支持从飞书多维表格、Excel、CSV 进行数据分析
- 自动生成数据概览、统计信息
- 支持自然语言查询
- 数据预览和可视化

### ✅ 4. 分模块调试
- **断点调试**：在任意节点设置断点
- **单步执行**：逐个节点执行，查看状态
- **模块测试**：单独测试每个节点
- **执行历史**：查看完整的执行历史

### ✅ 5. 配置热更新（无需重启）
- 运行时更新配置，无需重启服务
- 自动监听配置文件变化
- 支持配置变更回调
- 批量配置更新

### ✅ 6. 微信小程序深度集成
- 完整的小程序配置界面
- 支持在小程序端配置智能客服入口
- 节点状态管理
- 实时配置更新

---

## 🔥 核心问题回答

### Q: 必须部署后才能去改配置吗？

**A: 不需要！系统支持配置热更新，无需重启服务即可修改配置。**

#### 配置热更新机制

1. **自动监听配置文件**
   ```python
   # 系统会自动监听配置文件变化
   config_manager = get_config_manager()
   config_manager.start_watch_all()  # 启动监听
   ```

2. **运行时更新配置**
   ```bash
   # 方法1：通过 API 更新
   POST /api/config/reload

   # 方法2：直接修改配置文件（系统自动检测）
   vim config/workflow_config.json
   # 保存后，系统会自动重新加载

   # 方法3：通过小程序配置界面
   # 在小程序配置页面修改，自动生效
   ```

3. **支持的配置类型**
   - 工作流配置（workflow_config.json）
   - Agent 配置（agent_llm_config.json）
   - 小程序配置（miniprogram_config.json）

4. **配置变更回调**
   ```python
   # 配置变更时会自动触发回调
   def on_config_change(key, value):
       logger.info(f"配置 {key} 已更新为: {value}")

   config.register_callback("model", on_config_change)
   ```

---

## 📋 详细功能说明

### 1. 飞书机器人互动

#### 部署飞书机器人服务
```bash
PYTHONPATH=/workspace/projects/src:$PYTHONPATH uv run python -m uvicorn src.api.feishu_bot_service:app --reload --host 0.0.0.0 --port 8003
```

#### Webhook 配置
- URL: `http://your-server:8003/api/feishu/webhook`
- 支持文本消息和图片消息
- 自动调用智能客服工作流

#### 使用示例
```
用户（飞书）：今天北京的天气怎么样？
飞书机器人：【网络搜索答案】
根据中国天气网信息，今天北京天气...
```

---

### 2. 知识库多格式导入

#### API 接口
```http
POST /api/knowledge/import
Content-Type: application/json

{
  "source_type": "feishu_bitable",
  "app_token": "xxx",
  "table_id": "xxx",
  "dataset_name": "my_knowledge"
}
```

#### 支持的来源类型
| 来源类型 | 说明 | 必需参数 |
|---------|------|---------|
| `feishu_bitable` | 飞书多维表格 | app_token, table_id |
| `excel` | Excel 文件 | file_path |
| `csv` | CSV 文件 | file_path |

#### 文件上传接口
```http
POST /api/knowledge/import/file
Content-Type: multipart/form-data

source_type: excel
dataset_name: my_knowledge
file: (上传文件)
```

---

### 3. 数据分析功能

#### API 接口
```http
POST /api/data/analyze
Content-Type: application/json

{
  "source_type": "feishu_bitable",
  "app_token": "xxx",
  "table_id": "xxx"
}
```

#### 分析报告内容
- 数据概览（行数、列数、列名）
- 数据类型统计
- 缺失值统计
- 数值型列统计（平均值、中位数、标准差等）
- 分类列统计（唯一值数量、Top 5 值）
- 数据预览（前5行）

#### 自然语言查询
```http
POST /api/data/analyze
Content-Type: application/json

{
  "source_type": "feishu_bitable",
  "app_token": "xxx",
  "table_id": "xxx",
  "query": "查找销售额最大的记录"
}
```

---

### 4. 分模块调试

#### 设置断点
```http
POST /api/debug/config
Content-Type: application/json

{
  "action": "set_breakpoint",
  "node_id": "knowledge_search"
}
```

#### 单步执行
```http
POST /api/debug/config
Content-Type: application/json

{
  "action": "enable_step"
}
```

#### 执行单个节点
```http
POST /api/debug/step
Content-Type: application/json

{
  "node_id": "knowledge_search",
  "state": {...}
}
```

#### 查看执行历史
```python
from workflow.debugger import get_global_debugger

debugger = get_global_debugger()
history = debugger.get_execution_history()
for record in history:
    print(f"节点: {record['node_id']}, 耗时: {record['execution_time']:.3f}s")
```

---

### 5. 配置热更新（无需重启）

#### 重新加载配置
```http
POST /api/config/reload
```

#### 监听配置文件变化
```python
from config.hot_reload import get_config_manager

manager = get_config_manager()
manager.start_watch_all()  # 自动监听配置文件变化

# 当配置文件被修改时，系统会自动重新加载
# 无需重启服务！
```

#### 运行时更新配置
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

#### 配置变更回调
```python
from config.hot_reload import get_config_manager

manager = get_config_manager()
workflow_config = manager.get_config("workflow")

# 注册回调
def on_config_change(key, value):
    print(f"配置已更新: {key} = {value}")
    # 在这里可以执行一些自定义逻辑

workflow_config.register_callback("debug_mode", on_config_change)
```

---

### 6. 微信小程序配置界面

#### 小程序配置页面
- **路径**：`miniprogram/pages/config/`
- **功能**：
  - 工作流配置（调试模式、飞书通知）
  - 节点管理（启用/禁用节点）
  - 知识库配置（默认数据集）
  - 模型配置（模型ID、温度参数）
  - 保存配置、重新加载、测试连接

#### 小程序代码结构
```
miniprogram/
├── pages/
│   ├── config/
│   │   ├── config.js      # 配置页面逻辑
│   │   ├── config.wxml    # 配置页面结构
│   │   └── config.wxss    # 配置页面样式
│   └── index/
│       └── index.js       # 主页面（智能客服入口）
```

#### 小程序配置 API
```javascript
// 获取配置
wx.request({
  url: 'https://your-api.com/api/miniprogram/config',
  method: 'GET',
  success: (res) => {
    console.log(res.data.config);
  }
});

// 保存配置
wx.request({
  url: 'https://your-api.com/api/miniprogram/config',
  method: 'POST',
  data: {
    workflow: { debugMode: true },
    model: { temperature: 0.7 }
  }
});
```

---

## 🚀 快速开始

### 启动所有服务

```bash
# 1. 工作流 API 服务（端口 8001）
PYTHONPATH=/workspace/projects/src:$PYTHONPATH uv run python -m uvicorn src.api.workflow_service:app --reload --host 0.0.0.0 --port 8001

# 2. 综合服务（端口 8002）
PYTHONPATH=/workspace/projects/src:$PYTHONPATH uv run python -m uvicorn src.api.integrated_service:app --reload --host 0.0.0.0 --port 8002

# 3. 飞书机器人服务（端口 8003）
PYTHONPATH=/workspace/projects/src:$PYTHONPATH uv run python -m uvicorn src.api.feishu_bot_service:app --reload --host 0.0.0.0 --port 8003
```

### 配置热更新测试

```bash
# 1. 修改配置文件
vim config/workflow_config.json

# 2. 查看日志，确认配置已自动重新加载
tail -f /app/work/logs/bypass/app.log

# 3. 调用 API 确认配置已更新
curl http://localhost:8002/api/status
```

---

## 📊 API 接口汇总

### 工作流相关
| 接口 | 方法 | 说明 |
|------|------|------|
| `/api/workflow/chat` | POST | 工作流聊天 |
| `/api/workflow/structure` | GET | 获取工作流结构 |
| `/api/workflow/nodes/config` | POST | 更新节点配置 |
| `/api/workflow/nodes/status` | POST | 更新节点状态 |

### 知识库相关
| 接口 | 方法 | 说明 |
|------|------|------|
| `/api/knowledge/import` | POST | 导入知识库 |
| `/api/knowledge/import/file` | POST | 上传文件导入知识库 |

### 数据分析相关
| 接口 | 方法 | 说明 |
|------|------|------|
| `/api/data/analyze` | POST | 数据分析 |
| `/api/data/analyze/file` | POST | 上传文件分析 |

### 调试相关
| 接口 | 方法 | 说明 |
|------|------|------|
| `/api/debug/step` | POST | 调试单步执行 |
| `/api/debug/config` | POST | 配置调试 |

### 配置相关
| 接口 | 方法 | 说明 |
|------|------|------|
| `/api/config/reload` | POST | 重新加载配置 |
| `/api/miniprogram/config` | GET/POST | 小程序配置 |

### 飞书相关
| 接口 | 方法 | 说明 |
|------|------|------|
| `/api/feishu/webhook` | POST | 飞书机器人 Webhook |
| `/api/feishu/health` | GET | 健康检查 |

---

## 💡 最佳实践

### 1. 配置管理
- ✅ 使用配置热更新，避免频繁重启
- ✅ 重要配置修改前先备份
- ✅ 使用小程序配置界面，操作更便捷

### 2. 调试技巧
- ✅ 使用断点调试，快速定位问题
- ✅ 单步执行，观察状态变化
- ✅ 查看执行历史，分析性能瓶颈

### 3. 知识库导入
- ✅ 批量导入时注意分块大小
- ✅ 定期清理无效数据
- ✅ 使用飞书多维表格，方便协作

### 4. 数据分析
- ✅ 先进行数据概览，了解数据结构
- ✅ 使用自然语言查询，更直观
- ✅ 定期分析数据，发现业务洞察

---

## 🔧 故障排查

### 配置热更新不生效
- 检查配置文件路径是否正确
- 查看日志是否有错误信息
- 尝试手动调用 `/api/config/reload`

### 飞书机器人无响应
- 检查 Webhook URL 是否正确
- 查看飞书机器人日志
- 确认网络连接正常

### 知识库导入失败
- 检查文件格式是否正确
- 确认数据集名称是否有效
- 查看详细错误信息

---

## 📝 总结

### 核心优势
1. ✅ **无需重启即可修改配置** - 配置热更新机制
2. ✅ **飞书机器人互动** - 实时智能客服
3. ✅ **多格式知识库导入** - 飞书多维表格、Excel、CSV
4. ✅ **强大的数据分析** - 自动生成分析报告
5. ✅ **分模块调试** - 断点、单步、模块测试
6. ✅ **微信小程序深度集成** - 完整配置界面

### 关键特性
- **配置热更新**：无需重启，实时生效
- **模块化设计**：每个节点独立，易于维护
- **多模态支持**：文本、语音、图片
- **风险自动评估**：过滤不安全信息
- **飞书深度集成**：机器人互动、多维表格导入
- **小程序友好**：完整的配置界面和API

所有功能已开发完成，可以投入使用！🎉
