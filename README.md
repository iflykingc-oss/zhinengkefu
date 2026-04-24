# 智能客服系统 (Intelligent Customer Service System)

一个功能全面的企业级智能客服系统，支持知识库搜索、联网搜索、多模态交互、SOP流程管理、运营配置等功能。

## 🌟 核心功能

### 基础能力
- ✅ **知识库搜索** - 优先在知识库中查找答案
- ✅ **联网搜索** - 知识库无答案时自动联网搜索
- ✅ **风险评估** - 评估外部信息的风险
- ✅ **多模态输入** - 支持文本、语音、图片
- ✅ **多轮对话** - 上下文记忆和对话管理

### 高级功能
- ✅ **RAG检索增强** - 检索+生成一体化
- ✅ **SOP流程管理** - 支持图文、视频、短链、富文本
- ✅ **转人工策略** - 关键词/轮次/情感分析触发
- ✅ **开场白配置** - 场景化、时间感知开场白
- ✅ **闲聊配置** - 意图识别和模板化闲聊
- ✅ **数据导出** - 支持JSON/CSV/Markdown格式

### 运营功能
- ✅ **可视化运营后台** - Web端管理界面
- ✅ **配置热更新** - 无需重启服务
- ✅ **日志导出** - 会话/搜索/知识库日志
- ✅ **统计分析** - 仪表板和可视化数据
- ✅ **画布配置** - 可视化流程节点配置

### 集成能力
- ✅ **飞书集成** - 机器人互动和通知
- ✅ **微信小程序** - 小程序部署支持
- ✅ **飞书多维表格** - 知识库导入
- ✅ **多格式导入** - Excel/CSV/飞书表格

## 📁 项目结构

```
.
├── config/                      # 配置目录
│   ├── agent_llm_config.json    # LLM配置
│   ├── operation_config.json    # 运营配置
│   ├── sop_knowledge.json       # SOP知识
│   └── workflow_config.json     # 工作流配置
├── docs/                        # 文档
│   ├── operation_backend_guide.md     # 运营后台指南
│   └── web_operation_backend_guide.md  # Web后台指南
├── scripts/                     # 脚本
│   ├── local_run.sh             # 本地运行脚本
│   └── http_run.sh              # HTTP服务脚本
├── src/                         # 源码
│   ├── agents/                  # Agent定义
│   ├── api/                     # API服务
│   │   ├── workflow_service.py      # 工作流API (8001)
│   │   ├── integrated_service.py    # 综合服务API (8002)
│   │   ├── feishu_bot_service.py    # 飞书机器人API (8003)
│   │   ├── visualization_service.py # 可视化API (8004)
│   │   └── operation_service.py     # 运营后台API (8005)
│   ├── config/                  # 配置管理
│   │   ├── hot_reload.py        # 配置热更新
│   │   ├── dynamic_config.py    # 动态配置
│   │   └── operation_config.py  # 运营配置
│   ├── ops/                     # 运营模块
│   │   ├── greeting.py          # 开场白管理
│   │   ├── chitchat.py          # 闲聊管理
│   │   └── human_handoff.py     # 转人工策略
│   ├── sop/                     # SOP模块
│   │   ├── knowledge_manager.py # SOP知识管理
│   │   ├── sop_nodes.py         # SOP流程节点
│   │   └── rich_text_formatter.py # 富文本格式化
│   ├── storage/                 # 存储模块
│   ├── tools/                   # 工具定义
│   │   ├── rag_tools.py         # RAG检索工具
│   │   ├── export_tools.py      # 数据导出工具
│   │   ├── knowledge_search_tool.py    # 知识库搜索
│   │   ├── web_search_tool.py   # 联网搜索
│   │   ├── knowledge_import_tools.py   # 知识导入
│   │   ├── data_analysis_tools.py      # 数据分析
│   │   └── feishu_notification_tool.py # 飞书通知
│   ├── utils/                   # 工具函数
│   ├── workflow/                # 工作流
│   │   ├── graph_v4.py          # 工作流v4.0
│   │   ├── nodes.py             # 节点定义
│   │   ├── state.py             # 状态定义
│   │   ├── routes.py            # 路由定义
│   │   └── debugger.py          # 调试器
│   └── main.py                  # 主入口
├── static/                      # 静态文件
│   ├── index.html               # 运营后台页面
│   └── app.js                   # 前端逻辑
├── tests/                       # 测试
│   ├── test_v4_features.py      # v4.0功能测试
│   ├── test_operation_features.py  # 运营功能测试
│   ├── test_answer_source_hidden.py  # 答案来源隐藏测试
│   └── test_helpers.py          # 测试辅助函数
├── pyproject.toml               # 项目配置
├── uv.lock                      # 依赖锁定
└── .coze                        # 配置文件
```

## 🚀 快速开始

### 1. 环境准备
```bash
# 确保已安装 Python 3.8+
python --version

# 安装 uv 包管理器
pip install uv

# 安装依赖
uv sync
```

### 2. 配置文件
编辑 `config/agent_llm_config.json`，配置LLM模型参数。

### 3. 启动服务

#### 启动运营后台（推荐首先启动）
```bash
# 启动运营后台API和Web界面
python -m src.api.operation_service
```
访问 http://localhost:8005

#### 启动其他服务
```bash
# 工作流API
python -m src.api.workflow_service

# 综合服务API
python -m src.api.integrated_service

# 飞书机器人API
python -m src.api.feishu_bot_service

# 可视化API
python -m src.api.visualization_service
```

### 4. 本地运行
```bash
# 运行工作流
bash scripts/local_run.sh -m flow

# 运行节点
bash scripts/local_run.sh -m node -n node_name

# 启动HTTP服务
bash scripts/http_run.sh -m http -p 5000
```

## 🌐 访问地址

| 服务 | 端口 | 地址 |
|------|------|------|
| 运营后台 | 8005 | http://localhost:8005 |
| 工作流API | 8001 | http://localhost:8001 |
| 综合服务API | 8002 | http://localhost:8002 |
| 飞书机器人API | 8003 | http://localhost:8003 |
| 可视化API | 8004 | http://localhost:8004 |

## 📖 文档

- [运营后台指南](docs/operation_backend_guide.md)
- [Web后台指南](docs/web_operation_backend_guide.md)

## 🧪 测试

```bash
# 测试v4.0功能（RAG、SOP、数据导出）
python tests/test_v4_features.py

# 测试运营功能（开场白、闲聊、转人工）
python tests/test_operation_features.py

# 测试答案来源隐藏
python tests/test_answer_source_hidden.py
```

## 🔧 主要功能模块

### 1. 工作流系统
基于LangGraph构建的灵活工作流，支持：
- 6个独立节点：输入解析、SOP匹配、知识库搜索、联网搜索、风险评估、答案生成
- 条件路由：动态选择执行路径
- 短期记忆：保留最近20轮对话
- 调试模式：支持断点和单步执行

### 2. RAG检索增强
- 检索+生成一体化
- 可配置检索参数
- 支持多种数据格式

### 3. SOP流程管理
- 支持多种内容类型：文本、富文本、图片、视频、短链、混合
- 关键词匹配机制
- 完整的CRUD操作

### 4. 转人工策略
- 关键词策略（转人工、投诉等）
- 轮次限制策略
- 情感分析策略
- 多渠道转接（飞书、微信、邮件）

### 5. 运营配置
- 开场白配置（场景化、时间感知）
- 闲聊配置（意图识别、模板化）
- 配置热更新（立即生效）

### 6. 数据导出
- 会话日志导出
- 搜索记录导出
- 知识库导出
- 支持JSON/CSV/Markdown格式

## 🎯 使用场景

### 企业客服
- 自动应答常见问题
- 知识库管理
- 转人工服务

### 在线咨询
- 7x24小时服务
- 多渠道接入
- 智能路由

### 内部支持
- SOP流程执行
- 知识沉淀
- 数据分析

## 📝 版本历史

### v5.0.0 (2024-01-23)
- ✅ 实现运营后台配置管理系统
- ✅ 创建Web端运营后台可视化界面
- ✅ 支持转人工策略配置
- ✅ 支持开场白和闲聊配置
- ✅ 支持日志导出功能

### v4.0.0
- ✅ 实现RAG检索增强生成
- ✅ 实现SOP知识管理
- ✅ 实现数据导出工具
- ✅ 实现可视化展示API
- ✅ 实现富文本/多媒体输出

### v3.0.0
- ✅ 实现飞书机器人互动
- ✅ 实现多格式知识库导入
- ✅ 实现数据分析功能
- ✅ 实现分模块调试
- ✅ 实现配置热更新

### v2.0.0
- ✅ 添加飞书通知
- ✅ 添加微信小程序支持
- ✅ 实现动态配置

### v1.0.0
- ✅ 基础智能客服Agent
- ✅ 知识库搜索
- ✅ 联网搜索
- ✅ 多模态输入

## 🤝 贡献

欢迎提交 Issue 和 Pull Request！

## 📄 许可证

MIT License

## 📧 联系方式

如有问题，请提交 Issue 或联系项目维护者。
