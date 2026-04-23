# Web端运营后台使用指南

## 🌐 访问入口

### 方式一：直接访问根路径
```
http://localhost:8005
```

### 方式二：访问管理后台路径
```
http://localhost:8005/admin
```

### 方式三：访问静态文件
```
http://localhost:8005/static/index.html
```

## 🚀 启动步骤

### 1. 启动运营后台API服务

```bash
cd /workspace/projects
python -m src.api.operation_service
```

服务将在 **http://localhost:8005** 启动

### 2. 在浏览器中打开访问

打开浏览器，访问以下任一地址：
- http://localhost:8005
- http://localhost:8005/admin
- http://localhost:8005/static/index.html

## 📋 功能模块

### 1. 仪表板
- 系统概览
- API状态检查
- SOP知识数量
- 开场白状态
- 闲聊功能状态
- 转人工状态

### 2. 配置管理
- 查看完整系统配置
- JSON格式展示配置
- 支持刷新配置

### 3. 开场白配置
- 查看开场白列表
- 添加新开场白
- 删除开场白
- 支持场景化开场白

### 4. 闲聊配置
- 查看闲聊意图列表
- 添加闲聊意图（意图名称、关键词、回复）
- 删除闲聊意图
- 内置意图：greeting, thanks, goodbye

### 5. 转人工策略
- 查看转人工策略列表
- 策略类型：
  - 关键词策略
  - 轮次限制策略
  - 情感分析策略
- 查看策略配置详情

### 6. SOP流程
- 查看SOP知识库
- 查看SOP详细信息
- 删除SOP知识
- 支持多种SOP类型

### 7. 画布配置
- 查看画布节点列表
- 查看节点详情
- 删除画布节点

### 8. 日志导出
- **导出会话日志**
  - 支持 JSON/CSV/Markdown 格式
  - 可指定会话ID
- **导出搜索记录**
  - 支持 JSON/CSV/Markdown 格式
- **导出知识库**
  - 支持 JSON/CSV 格式

## 🎨 界面特点

### 响应式设计
- 支持PC端访问
- 支持移动端访问
- 自适应屏幕尺寸

### 现代化UI
- 基于Bootstrap 5
- 渐变色侧边栏
- 卡片式布局
- 统计卡片带动画效果

### 交互功能
- 实时数据加载
- 确认删除操作
- 文件下载功能
- 加载状态提示

## 🔧 配置说明

### 前端API地址
前端默认连接到：`http://localhost:8005/api/v5`

如果需要修改API地址，编辑 `static/app.js` 文件：
```javascript
const API_BASE_URL = 'http://your-api-address/api/v5';
```

### CORS配置
如果遇到跨域问题，需要在API服务中配置CORS：
```python
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

## 📱 使用示例

### 示例1：添加开场白
1. 访问 http://localhost:8005
2. 点击左侧"开场白配置"
3. 在输入框中输入开场白内容
4. 点击"添加"按钮
5. 开场白添加成功，列表自动刷新

### 示例2：添加闲聊意图
1. 点击左侧"闲聊配置"
2. 填写意图名称：greeting
3. 填写关键词：你好,嗨,hello
4. 填写回复：你好！,嗨！
5. 点击"添加"按钮
6. 意图添加成功

### 示例3：导出会话日志
1. 点击左侧"日志导出"
2. 选择导出格式（CSV）
3. （可选）输入会话ID
4. 点击"导出"按钮
5. 文件自动下载

## 🔍 常见问题

### Q1: 访问页面显示空白？
**A**: 检查API服务是否正常启动，浏览器控制台是否有错误信息。

### Q2: 加载数据失败？
**A**: 确认API服务运行正常，检查浏览器网络请求。

### Q3: 删除操作没有反应？
**A**: 检查浏览器控制台是否有错误，确认API调用成功。

### Q4: 文件下载失败？
**A**: 检查导出数据量是否过大，尝试选择小范围数据。

## 📊 技术栈

### 前端
- HTML5
- CSS3
- JavaScript (ES6+)
- Bootstrap 5
- Bootstrap Icons

### 后端
- FastAPI
- Uvicorn
- Python 3.8+

## 🎯 快速开始

1. **启动服务**
   ```bash
   python -m src.api.operation_service
   ```

2. **打开浏览器**
   ```
   http://localhost:8005
   ```

3. **开始使用**
   - 查看仪表板统计
   - 配置开场白
   - 管理闲聊意图
   - 查看转人工策略
   - 导出日志数据

## 📝 注意事项

1. **API服务必须先启动**
   - 前端页面依赖API服务
   - 确保API服务运行在8005端口

2. **浏览器兼容性**
   - 推荐使用Chrome、Edge、Firefox
   - 不支持IE浏览器

3. **网络要求**
   - 前端需要CDN加载Bootstrap资源
   - 确保网络连接正常

4. **数据安全**
   - 配置修改立即生效
   - 删除操作不可恢复
   - 建议定期备份配置

## 🔗 相关链接

- API文档: http://localhost:8005/docs
- API文档: http://localhost:8005/redoc
- 运营指南: `docs/operation_backend_guide.md`

## 🆕 更新日志

### v5.0.0 (2024-01-23)
- ✅ 创建Web端运营后台界面
- ✅ 集成所有运营配置模块
- ✅ 支持可视化操作
- ✅ 实现文件导出功能
- ✅ 响应式设计
