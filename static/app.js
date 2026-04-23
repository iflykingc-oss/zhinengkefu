// API基础URL
const API_BASE_URL = 'http://localhost:8005/api/v5';

// 当前页面
let currentPage = 'dashboard';

// 页面加载完成后初始化
document.addEventListener('DOMContentLoaded', function() {
    initNavigation();
    loadDashboard();
});

// 初始化导航
function initNavigation() {
    const navItems = document.querySelectorAll('.nav-item');
    navItems.forEach(item => {
        item.addEventListener('click', function() {
            const page = this.getAttribute('data-page');
            navigateTo(page);
        });
    });
}

// 页面导航
function navigateTo(page) {
    // 更新导航栏状态
    document.querySelectorAll('.nav-item').forEach(item => {
        item.classList.remove('active');
        if (item.getAttribute('data-page') === page) {
            item.classList.add('active');
        }
    });

    // 隐藏所有页面
    document.querySelectorAll('.page').forEach(p => {
        p.classList.remove('active');
    });

    // 显示目标页面
    const targetPage = document.getElementById(page);
    if (targetPage) {
        targetPage.classList.add('active');
        currentPage = page;

        // 根据页面加载对应数据
        switch(page) {
            case 'dashboard':
                loadDashboard();
                break;
            case 'config':
                loadFullConfig();
                break;
            case 'greeting':
                loadGreetings();
                break;
            case 'chitchat':
                loadChitchatIntents();
                break;
            case 'transfer':
                loadTransferStrategies();
                break;
            case 'sop':
                loadSopKnowledge();
                break;
            case 'canvas':
                loadCanvasNodes();
                break;
        }
    }
}

// API调用封装
async function apiCall(endpoint, method = 'GET', data = null) {
    try {
        const options = {
            method: method,
            headers: {
                'Content-Type': 'application/json'
            }
        };

        if (data && (method === 'POST' || method === 'PUT')) {
            options.body = JSON.stringify(data);
        }

        const response = await fetch(`${API_BASE_URL}${endpoint}`, options);
        const result = await response.json();

        if (!response.ok) {
            throw new Error(result.detail || '请求失败');
        }

        return result;
    } catch (error) {
        console.error('API调用失败:', error);
        alert('API调用失败: ' + error.message);
        return null;
    }
}

// 加载仪表板
async function loadDashboard() {
    try {
        // 检查API状态
        const apiStatus = document.getElementById('apiStatus');
        try {
            const health = await fetch('http://localhost:8005/health');
            if (health.ok) {
                apiStatus.className = 'api-status online';
                apiStatus.innerHTML = '<i class="bi bi-circle-fill"></i> API状态: 在线';
            } else {
                apiStatus.className = 'api-status offline';
                apiStatus.innerHTML = '<i class="bi bi-circle-fill"></i> API状态: 离线';
            }
        } catch (e) {
            apiStatus.className = 'api-status offline';
            apiStatus.innerHTML = '<i class="bi bi-circle-fill"></i> API状态: 无法连接';
        }

        // 获取统计数据
        const stats = await apiCall('/stats/dashboard');
        if (stats) {
            document.getElementById('sopCount').textContent = stats.sop_count || 0;
            document.getElementById('greetingStatus').textContent = stats.greeting_enabled ? '已启用' : '已禁用';
            document.getElementById('chitchatStatus').textContent = stats.chitchat_enabled ? '已启用' : '已禁用';
            document.getElementById('transferStatus').textContent = stats.transfer_enabled ? '已启用' : '已禁用';
        }
    } catch (error) {
        console.error('加载仪表板失败:', error);
    }
}

// 加载完整配置
async function loadFullConfig() {
    const container = document.getElementById('fullConfig');
    container.innerHTML = '<div class="loading-spinner"></div><p>加载中...</p>';

    const config = await apiCall('/config');
    if (config) {
        const html = `
            <pre style="background: #f5f5f5; padding: 20px; border-radius: 8px; overflow-x: auto;">
${JSON.stringify(config, null, 2)}
            </pre>
        `;
        container.innerHTML = html;
    }
}

// 加载开场白列表
async function loadGreetings() {
    const container = document.getElementById('greetingList');
    container.innerHTML = '<div class="loading-spinner"></div><p>加载中...</p>';

    const data = await apiCall('/greeting/messages');
    if (data && data.messages) {
        if (data.messages.length === 0) {
            container.innerHTML = '<p class="text-muted">暂无开场白</p>';
            return;
        }

        const html = data.messages.map((msg, index) => `
            <div class="d-flex justify-content-between align-items-center mb-2 p-3 border rounded">
                <span>${msg}</span>
                <button class="btn btn-sm btn-danger" onclick="deleteGreeting('${encodeURIComponent(msg)}')">
                    <i class="bi bi-trash"></i> 删除
                </button>
            </div>
        `).join('');

        container.innerHTML = html;
    }
}

// 添加开场白
async function addGreeting() {
    const input = document.getElementById('newGreeting');
    const message = input.value.trim();

    if (!message) {
        alert('请输入开场白内容');
        return;
    }

    const result = await apiCall('/greeting/messages', 'POST', message);
    if (result) {
        alert('添加成功！');
        input.value = '';
        loadGreetings();
    }
}

// 删除开场白
async function deleteGreeting(message) {
    const decodedMessage = decodeURIComponent(message);
    if (!confirm(`确定要删除开场白"${decodedMessage}"吗？`)) {
        return;
    }

    const result = await apiCall(`/greeting/messages?message=${message}`, 'DELETE');
    if (result) {
        alert('删除成功！');
        loadGreetings();
    }
}

// 加载闲聊意图列表
async function loadChitchatIntents() {
    const container = document.getElementById('chitchatList');
    container.innerHTML = '<div class="loading-spinner"></div><p>加载中...</p>';

    const data = await apiCall('/chitchat/intents');
    if (data && data.intents) {
        if (data.intents.length === 0) {
            container.innerHTML = '<p class="text-muted">暂无闲聊意图</p>';
            return;
        }

        const html = data.intents.map(intent => `
            <div class="card mb-3">
                <div class="card-header d-flex justify-content-between align-items-center">
                    <strong>${intent.intent}</strong>
                    <button class="btn btn-sm btn-danger" onclick="deleteChitchatIntent('${intent.intent}')">
                        <i class="bi bi-trash"></i> 删除
                    </button>
                </div>
                <div class="card-body">
                    <p><strong>关键词:</strong> ${intent.keywords.join(', ')}</p>
                    <p><strong>回复:</strong> ${intent.responses.join(', ')}</p>
                </div>
            </div>
        `).join('');

        container.innerHTML = html;
    }
}

// 添加闲聊意图
async function addChitchatIntent() {
    const intent = document.getElementById('newIntent').value.trim();
    const keywords = document.getElementById('newKeywords').value.split(',').map(k => k.trim()).filter(k => k);
    const responses = document.getElementById('newResponses').value.split(',').map(r => r.trim()).filter(r => r);

    if (!intent || keywords.length === 0 || responses.length === 0) {
        alert('请填写完整的意图信息');
        return;
    }

    const result = await apiCall('/chitchat/intents', 'POST', {
        intent,
        keywords,
        responses
    });

    if (result) {
        alert('添加成功！');
        document.getElementById('newIntent').value = '';
        document.getElementById('newKeywords').value = '';
        document.getElementById('newResponses').value = '';
        loadChitchatIntents();
    }
}

// 删除闲聊意图
async function deleteChitchatIntent(intent) {
    if (!confirm(`确定要删除意图"${intent}"吗？`)) {
        return;
    }

    const result = await apiCall(`/chitchat/intents/${intent}`, 'DELETE');
    if (result) {
        alert('删除成功！');
        loadChitchatIntents();
    }
}

// 加载转人工策略
async function loadTransferStrategies() {
    const container = document.getElementById('transferList');
    container.innerHTML = '<div class="loading-spinner"></div><p>加载中...</p>';

    const data = await apiCall('/transfer/strategies');
    if (data && data.strategies) {
        const html = data.strategies.map(strategy => `
            <div class="card mb-3">
                <div class="card-header">
                    <div class="d-flex justify-content-between align-items-center">
                        <strong>${strategy.name}</strong>
                        <span class="badge ${strategy.enabled ? 'badge-enabled' : 'badge-disabled'}">
                            ${strategy.enabled ? '已启用' : '已禁用'}
                        </span>
                    </div>
                </div>
                <div class="card-body">
                    <p><strong>类型:</strong> ${strategy.type}</p>
                    <p><strong>配置:</strong></p>
                    <pre style="background: #f5f5f5; padding: 10px; border-radius: 5px;">${JSON.stringify(strategy.config, null, 2)}</pre>
                </div>
            </div>
        `).join('');

        container.innerHTML = html;
    }
}

// 加载SOP知识
async function loadSopKnowledge() {
    const container = document.getElementById('sopList');
    container.innerHTML = '<div class="loading-spinner"></div><p>加载中...</p>';

    const data = await apiCall('/sop/knowledge');
    if (data && data.sop_list) {
        if (data.sop_list.length === 0) {
            container.innerHTML = '<p class="text-muted">暂无SOP知识</p>';
            return;
        }

        const html = data.sop_list.map(sop => `
            <div class="card mb-3">
                <div class="card-header">
                    <div class="d-flex justify-content-between align-items-center">
                        <strong>${sop.name}</strong>
                        <button class="btn btn-sm btn-danger" onclick="deleteSopKnowledge('${sop.id}')">
                            <i class="bi bi-trash"></i> 删除
                        </button>
                    </div>
                </div>
                <div class="card-body">
                    <p><strong>ID:</strong> ${sop.id}</p>
                    <p><strong>类型:</strong> ${sop.content_type}</p>
                    <p><strong>触发关键词:</strong> ${sop.trigger_keywords.join(', ')}</p>
                </div>
            </div>
        `).join('');

        container.innerHTML = html;
    }
}

// 删除SOP知识
async function deleteSopKnowledge(sopId) {
    if (!confirm(`确定要删除SOP知识"${sopId}"吗？`)) {
        return;
    }

    const result = await apiCall(`/sop/knowledge/${sopId}`, 'DELETE');
    if (result) {
        alert('删除成功！');
        loadSopKnowledge();
    }
}

// 加载画布节点
async function loadCanvasNodes() {
    const container = document.getElementById('canvasList');
    container.innerHTML = '<div class="loading-spinner"></div><p>加载中...</p>';

    const data = await apiCall('/canvas/nodes');
    if (data && data.nodes) {
        if (data.nodes.length === 0) {
            container.innerHTML = '<p class="text-muted">暂无画布节点</p>';
            return;
        }

        const html = data.nodes.map(node => `
            <div class="card mb-3">
                <div class="card-header">
                    <div class="d-flex justify-content-between align-items-center">
                        <strong>${node.name || node.id}</strong>
                        <button class="btn btn-sm btn-danger" onclick="deleteCanvasNode('${node.id}')">
                            <i class="bi bi-trash"></i> 删除
                        </button>
                    </div>
                </div>
                <div class="card-body">
                    <p><strong>ID:</strong> ${node.id}</p>
                    <p><strong>类型:</strong> ${node.type || '未定义'}</p>
                </div>
            </div>
        `).join('');

        container.innerHTML = html;
    }
}

// 删除画布节点
async function deleteCanvasNode(nodeId) {
    if (!confirm(`确定要删除节点"${nodeId}"吗？`)) {
        return;
    }

    const result = await apiCall(`/canvas/nodes/${nodeId}`, 'DELETE');
    if (result) {
        alert('删除成功！');
        loadCanvasNodes();
    }
}

// 导出会话日志
async function exportConversations() {
    const format = document.getElementById('exportFormat').value;
    const conversationId = document.getElementById('exportConversationId').value;

    let url = `/export/conversations?format=${format}`;
    if (conversationId) {
        url += `&conversation_id=${conversationId}`;
    }

    const data = await apiCall(url);
    if (data && data.result) {
        downloadFile(data.result, `conversations_${format}.${format === 'json' ? 'json' : format === 'csv' ? 'csv' : 'md'}`);
    }
}

// 导出搜索记录
async function exportSearchHistory() {
    const format = document.getElementById('exportSearchFormat').value;

    const data = await apiCall(`/export/search_history?format=${format}`);
    if (data && data.result) {
        downloadFile(data.result, `search_history.${format === 'json' ? 'json' : format === 'csv' ? 'csv' : 'md'}`);
    }
}

// 导出知识库
async function exportKnowledgeBase() {
    const format = document.getElementById('exportKbFormat').value;

    const data = await apiCall(`/export/knowledge_base?format=${format}`);
    if (data && data.result) {
        downloadFile(data.result, `knowledge_base.${format === 'json' ? 'json' : 'csv'}`);
    }
}

// 下载文件
function downloadFile(content, filename) {
    const blob = new Blob([content], { type: 'text/plain;charset=utf-8' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = filename;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
}
