import React, { createContext, useContext, useReducer, useEffect } from 'react';
import { message } from 'antd';

// 初始状态
const initialState = {
  theme: localStorage.getItem('theme') || 'light',
  language: localStorage.getItem('language') || 'zh-CN',
  autoSave: JSON.parse(localStorage.getItem('autoSave') || 'true'),
  notifications: JSON.parse(localStorage.getItem('notifications') || 'true'),
  compactMode: JSON.parse(localStorage.getItem('compactMode') || 'false'),
  sidebarCollapsed: JSON.parse(localStorage.getItem('sidebarCollapsed') || 'false'),
  llmConfig: {
    provider: 'openai',
    apiKey: '',
    baseUrl: 'https://api.openai.com/v1',
    model: 'gpt-4',
    temperature: 0.7,
  },
  wechatConfig: {
    appId: '',
    appSecret: '',
    token: '',
  },
  crawlConfig: {
    sources: [],
    schedule: 'daily',
    autoRewrite: true,
    delay: 2,
  },
  loading: false,
};

// Action types
const SETTINGS_ACTIONS = {
  SET_THEME: 'SET_THEME',
  SET_LANGUAGE: 'SET_LANGUAGE',
  SET_AUTO_SAVE: 'SET_AUTO_SAVE',
  SET_NOTIFICATIONS: 'SET_NOTIFICATIONS',
  SET_COMPACT_MODE: 'SET_COMPACT_MODE',
  SET_SIDEBAR_COLLAPSED: 'SET_SIDEBAR_COLLAPSED',
  UPDATE_LLM_CONFIG: 'UPDATE_LLM_CONFIG',
  UPDATE_WECHAT_CONFIG: 'UPDATE_WECHAT_CONFIG',
  UPDATE_CRAWL_CONFIG: 'UPDATE_CRAWL_CONFIG',
  SET_LOADING: 'SET_LOADING',
  RESET_SETTINGS: 'RESET_SETTINGS',
  LOAD_SETTINGS: 'LOAD_SETTINGS',
};

// Reducer
const settingsReducer = (state, action) => {
  switch (action.type) {
    case SETTINGS_ACTIONS.SET_THEME:
      localStorage.setItem('theme', action.payload);
      return { ...state, theme: action.payload };
    
    case SETTINGS_ACTIONS.SET_LANGUAGE:
      localStorage.setItem('language', action.payload);
      return { ...state, language: action.payload };
    
    case SETTINGS_ACTIONS.SET_AUTO_SAVE:
      localStorage.setItem('autoSave', JSON.stringify(action.payload));
      return { ...state, autoSave: action.payload };
    
    case SETTINGS_ACTIONS.SET_NOTIFICATIONS:
      localStorage.setItem('notifications', JSON.stringify(action.payload));
      return { ...state, notifications: action.payload };
    
    case SETTINGS_ACTIONS.SET_COMPACT_MODE:
      localStorage.setItem('compactMode', JSON.stringify(action.payload));
      return { ...state, compactMode: action.payload };
    
    case SETTINGS_ACTIONS.SET_SIDEBAR_COLLAPSED:
      localStorage.setItem('sidebarCollapsed', JSON.stringify(action.payload));
      return { ...state, sidebarCollapsed: action.payload };
    
    case SETTINGS_ACTIONS.UPDATE_LLM_CONFIG:
      return {
        ...state,
        llmConfig: { ...state.llmConfig, ...action.payload },
      };
    
    case SETTINGS_ACTIONS.UPDATE_WECHAT_CONFIG:
      return {
        ...state,
        wechatConfig: { ...state.wechatConfig, ...action.payload },
      };
    
    case SETTINGS_ACTIONS.UPDATE_CRAWL_CONFIG:
      return {
        ...state,
        crawlConfig: { ...state.crawlConfig, ...action.payload },
      };
    
    case SETTINGS_ACTIONS.SET_LOADING:
      return { ...state, loading: action.payload };
    
    case SETTINGS_ACTIONS.LOAD_SETTINGS:
      return { ...state, ...action.payload };
    
    case SETTINGS_ACTIONS.RESET_SETTINGS:
      // 重置本地存储
      localStorage.removeItem('theme');
      localStorage.removeItem('language');
      localStorage.removeItem('autoSave');
      localStorage.removeItem('notifications');
      localStorage.removeItem('compactMode');
      localStorage.removeItem('sidebarCollapsed');
      return {
        ...initialState,
        llmConfig: state.llmConfig, // 保留API配置
        wechatConfig: state.wechatConfig,
        crawlConfig: state.crawlConfig,
      };
    
    default:
      return state;
  }
};

// Context
const SettingsContext = createContext();

// Provider
export const SettingsProvider = ({ children }) => {
  const [state, dispatch] = useReducer(settingsReducer, initialState);

  // 加载服务器端配置
  useEffect(() => {
    loadServerSettings();
  }, []);

  // 主题变化时更新document class
  useEffect(() => {
    document.documentElement.setAttribute('data-theme', state.theme);
    if (state.theme === 'dark') {
      document.body.classList.add('dark-theme');
    } else {
      document.body.classList.remove('dark-theme');
    }
  }, [state.theme]);

  // 加载服务器端设置
  const loadServerSettings = async () => {
    try {
      dispatch({ type: SETTINGS_ACTIONS.SET_LOADING, payload: true });
      
      const token = localStorage.getItem('token');
      if (token) {
        const response = await fetch('/api/config', {
          headers: {
            'Authorization': `Bearer ${token}`,
          },
        });

        if (response.ok) {
          const configs = await response.json();
          
          // 解析配置数据
          const serverSettings = {};
          configs.forEach(config => {
            if (config.key === 'llm_config') {
              serverSettings.llmConfig = JSON.parse(config.value || '{}');
            } else if (config.key === 'wechat_config') {
              serverSettings.wechatConfig = JSON.parse(config.value || '{}');
            } else if (config.key === 'crawl_config') {
              serverSettings.crawlConfig = JSON.parse(config.value || '{}');
            }
          });

          dispatch({
            type: SETTINGS_ACTIONS.LOAD_SETTINGS,
            payload: serverSettings,
          });
        }
      }
    } catch (error) {
      console.error('Load settings error:', error);
    } finally {
      dispatch({ type: SETTINGS_ACTIONS.SET_LOADING, payload: false });
    }
  };

  // 保存配置到服务器
  const saveServerConfig = async (configType, config) => {
    try {
      const token = localStorage.getItem('token');
      if (!token) {
        message.error('请先登录');
        return { success: false };
      }

      const response = await fetch('/api/config', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`,
        },
        body: JSON.stringify({
          key: configType,
          value: JSON.stringify(config),
        }),
      });

      if (response.ok) {
        message.success('配置保存成功');
        return { success: true };
      } else {
        const data = await response.json();
        message.error(data.message || '配置保存失败');
        return { success: false };
      }
    } catch (error) {
      console.error('Save config error:', error);
      message.error('网络错误，请稍后重试');
      return { success: false };
    }
  };

  // 设置主题
  const setTheme = (theme) => {
    dispatch({ type: SETTINGS_ACTIONS.SET_THEME, payload: theme });
  };

  // 设置语言
  const setLanguage = (language) => {
    dispatch({ type: SETTINGS_ACTIONS.SET_LANGUAGE, payload: language });
  };

  // 设置自动保存
  const setAutoSave = (autoSave) => {
    dispatch({ type: SETTINGS_ACTIONS.SET_AUTO_SAVE, payload: autoSave });
  };

  // 设置通知
  const setNotifications = (notifications) => {
    dispatch({ type: SETTINGS_ACTIONS.SET_NOTIFICATIONS, payload: notifications });
  };

  // 设置紧凑模式
  const setCompactMode = (compactMode) => {
    dispatch({ type: SETTINGS_ACTIONS.SET_COMPACT_MODE, payload: compactMode });
  };

  // 设置侧边栏折叠
  const setSidebarCollapsed = (collapsed) => {
    dispatch({ type: SETTINGS_ACTIONS.SET_SIDEBAR_COLLAPSED, payload: collapsed });
  };

  // 更新LLM配置
  const updateLLMConfig = async (config) => {
    dispatch({ type: SETTINGS_ACTIONS.UPDATE_LLM_CONFIG, payload: config });
    return await saveServerConfig('llm_config', { ...state.llmConfig, ...config });
  };

  // 更新微信配置
  const updateWeChatConfig = async (config) => {
    dispatch({ type: SETTINGS_ACTIONS.UPDATE_WECHAT_CONFIG, payload: config });
    return await saveServerConfig('wechat_config', { ...state.wechatConfig, ...config });
  };

  // 更新爬虫配置
  const updateCrawlConfig = async (config) => {
    dispatch({ type: SETTINGS_ACTIONS.UPDATE_CRAWL_CONFIG, payload: config });
    return await saveServerConfig('crawl_config', { ...state.crawlConfig, ...config });
  };

  // 重置设置
  const resetSettings = () => {
    dispatch({ type: SETTINGS_ACTIONS.RESET_SETTINGS });
    message.success('设置已重置');
  };

  // 导出设置
  const exportSettings = () => {
    const settings = {
      theme: state.theme,
      language: state.language,
      autoSave: state.autoSave,
      notifications: state.notifications,
      compactMode: state.compactMode,
      sidebarCollapsed: state.sidebarCollapsed,
      exportTime: new Date().toISOString(),
    };

    const dataStr = JSON.stringify(settings, null, 2);
    const dataBlob = new Blob([dataStr], { type: 'application/json' });
    const url = URL.createObjectURL(dataBlob);
    
    const link = document.createElement('a');
    link.href = url;
    link.download = `settings-${new Date().toISOString().split('T')[0]}.json`;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    URL.revokeObjectURL(url);
    
    message.success('设置已导出');
  };

  // 导入设置
  const importSettings = (file) => {
    return new Promise((resolve, reject) => {
      const reader = new FileReader();
      
      reader.onload = (e) => {
        try {
          const settings = JSON.parse(e.target.result);
          
          // 验证设置格式
          const validKeys = ['theme', 'language', 'autoSave', 'notifications', 'compactMode', 'sidebarCollapsed'];
          const isValid = validKeys.some(key => settings.hasOwnProperty(key));
          
          if (!isValid) {
            throw new Error('无效的设置文件格式');
          }

          // 应用设置
          Object.entries(settings).forEach(([key, value]) => {
            if (validKeys.includes(key)) {
              switch (key) {
                case 'theme':
                  setTheme(value);
                  break;
                case 'language':
                  setLanguage(value);
                  break;
                case 'autoSave':
                  setAutoSave(value);
                  break;
                case 'notifications':
                  setNotifications(value);
                  break;
                case 'compactMode':
                  setCompactMode(value);
                  break;
                case 'sidebarCollapsed':
                  setSidebarCollapsed(value);
                  break;
                default:
                  break;
              }
            }
          });

          message.success('设置导入成功');
          resolve(settings);
        } catch (error) {
          message.error('设置导入失败：' + error.message);
          reject(error);
        }
      };

      reader.onerror = () => {
        const error = new Error('文件读取失败');
        message.error(error.message);
        reject(error);
      };

      reader.readAsText(file);
    });
  };

  const value = {
    ...state,
    setTheme,
    setLanguage,
    setAutoSave,
    setNotifications,
    setCompactMode,
    setSidebarCollapsed,
    updateLLMConfig,
    updateWeChatConfig,
    updateCrawlConfig,
    resetSettings,
    exportSettings,
    importSettings,
    loadServerSettings,
  };

  return (
    <SettingsContext.Provider value={value}>
      {children}
    </SettingsContext.Provider>
  );
};

// Hook
export const useSettings = () => {
  const context = useContext(SettingsContext);
  if (!context) {
    throw new Error('useSettings must be used within a SettingsProvider');
  }
  return context;
};
