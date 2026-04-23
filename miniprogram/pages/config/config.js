// pages/config/config.js
Page({
  data: {
    apiBaseUrl: 'https://your-api-domain.com',
    config: {
      workflow: {
        debugMode: false,
        enableFeishu: false
      },
      knowledge: {
        defaultDataset: 'default'
      },
      model: {
        modelId: 'doubao-seed-1-8-251228',
        temperature: 0.7
      }
    },
    nodes: [],
    loading: false
  },

  onLoad() {
    this.loadConfig();
    this.loadNodes();
  },

  // 加载配置
  loadConfig() {
    wx.request({
      url: `${this.data.apiBaseUrl}/api/miniprogram/config`,
      method: 'GET',
      success: (res) => {
        if (res.data.success) {
          this.setData({
            config: res.data.config || this.data.config
          });
        }
      }
    });
  },

  // 加载节点列表
  loadNodes() {
    wx.request({
      url: `${this.data.apiBaseUrl}/api/workflow/structure`,
      method: 'GET',
      success: (res) => {
        if (res.data.nodes) {
          const nodes = Object.keys(res.data.nodes).map(key => ({
            id: key,
            ...res.data.nodes[key]
          }));
          this.setData({ nodes });
        }
      }
    });
  },

  // 更新配置
  updateConfig(e) {
    const field = e.currentTarget.dataset.field;
    const value = e.detail.value;

    this.setData({
      [`config.${field}`]: value
    });
  },

  // 保存配置
  saveConfig() {
    this.setData({ loading: true });

    wx.request({
      url: `${this.data.apiBaseUrl}/api/miniprogram/config`,
      method: 'POST',
      data: this.data.config,
      success: (res) => {
        if (res.data.success) {
          wx.showToast({
            title: '配置保存成功',
            icon: 'success'
          });
        }
      },
      fail: () => {
        wx.showToast({
          title: '保存失败',
          icon: 'error'
        });
      },
      complete: () => {
        this.setData({ loading: false });
      }
    });
  },

  // 切换调试模式
  toggleDebugMode() {
    const action = this.data.config.workflow.debugMode ? 'disable_step' : 'enable_step';

    wx.request({
      url: `${this.data.apiBaseUrl}/api/debug/config`,
      method: 'POST',
      data: {
        action: action
      },
      success: (res) => {
        if (res.data.success) {
          this.setData({
            'config.workflow.debugMode': !this.data.config.workflow.debugMode
          });
          wx.showToast({
            title: res.data.message,
            icon: 'success'
          });
        }
      }
    });
  },

  // 切换节点状态
  toggleNodeStatus(e) {
    const nodeId = e.currentTarget.dataset.id;
    const node = this.data.nodes.find(n => n.id === nodeId);

    if (!node) return;

    const action = node.status === 'enabled' ? 'disable' : 'enable';

    wx.request({
      url: `${this.data.apiBaseUrl}/api/workflow/nodes/status`,
      method: 'POST',
      data: {
        node_id: nodeId,
        status: action
      },
      success: (res) => {
        if (res.data.success || res.statusCode === 200) {
          this.loadNodes();
          wx.showToast({
            title: '节点状态已更新',
            icon: 'success'
          });
        }
      }
    });
  },

  // 重新加载配置
  reloadConfig() {
    wx.showLoading({ title: '重新加载中...' });

    wx.request({
      url: `${this.data.apiBaseUrl}/api/config/reload`,
      method: 'POST',
      success: (res) => {
        if (res.data.success) {
          wx.showToast({
            title: '配置已重新加载',
            icon: 'success'
          });
          this.loadConfig();
        } else {
          wx.showToast({
            title: '重新加载失败',
            icon: 'error'
          });
        }
      },
      complete: () => {
        wx.hideLoading();
      }
    });
  },

  // 测试连接
  testConnection() {
    wx.showLoading({ title: '测试连接中...' });

    wx.request({
      url: `${this.data.apiBaseUrl}/api/status`,
      method: 'GET',
      success: (res) => {
        if (res.data.success) {
          wx.showModal({
            title: '连接成功',
            content: JSON.stringify(res.data.status, null, 2),
            showCancel: false
          });
        }
      },
      fail: () => {
        wx.showToast({
          title: '连接失败',
          icon: 'error'
        });
      },
      complete: () => {
        wx.hideLoading();
      }
    });
  }
});
