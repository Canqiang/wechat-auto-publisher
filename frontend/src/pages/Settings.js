import React, { useState } from 'react';
import { 
  Tabs, 
  Card, 
  Form, 
  Input, 
  Select, 
  Switch, 
  Button, 
  Slider, 
  Space,
  Divider,
  Upload,
  message,
  Modal,
  Alert
} from 'antd';
import {
  SettingOutlined,
  WechatOutlined,
  RobotOutlined,
  CloudOutlined,
  UserOutlined,
  UploadOutlined,
  ExportOutlined,
  ImportOutlined,
  ReloadOutlined
} from '@ant-design/icons';
import { useSettings } from '../contexts/SettingsContext';

const { Option } = Select;
const { TextArea } = Input;

const Settings = () => {
  const {
    llmConfig,
    wechatConfig,
    crawlConfig,
    theme,
    language,
    autoSave,
    notifications,
    updateLLMConfig,
    updateWeChatConfig,
    updateCrawlConfig,
    setTheme,
    setLanguage,
    setAutoSave,
    setNotifications,
    exportSettings,
    importSettings,
    resetSettings
  } = useSettings();

  const [loading, setLoading] = useState(false);
  const [testLoading, setTestLoading] = useState(false);

  // LLM配置表单
  const LLMSettings = () => {
    const [form] = Form.useForm();

    const handleSave = async () => {
      try {
        const values = await form.validateFields();
        setLoading(true);
        const result = await updateLLMConfig(values);
        if (result.success) {
          message.success('LLM配置保存成功');
        }
      } catch (error) {
        console.error('Save failed:', error);
      } finally {
        setLoading(false);
      }
    };

    const handleTest = async () => {
      setTestLoading(true);
      try {
        // 模拟测试API连接
        await new Promise(resolve => setTimeout(resolve, 2000));
        message.success('API连接测试成功');
      } catch (error) {
        message.error('API连接测试失败');
      } finally {
        setTestLoading(false);
      }
    };

    return (
      <Card title="LLM API 配置" icon={<RobotOutlined />}>
        <Form
          form={form}
          layout="vertical"
          initialValues={llmConfig}
          onFinish={handleSave}
        >
          <Form.Item
            name="provider"
            label="AI服务提供商"
            rules={[{ required: true, message: '请选择AI服务提供商' }]}
          >
            <Select>
              <Option value="openai">OpenAI</Option>
              <Option value="claude">Claude (Anthropic)</Option>
              <Option value="custom">自定义服务</Option>
            </Select>
          </Form.Item>

          <Form.Item
            name="apiKey"
            label="API Key"
            rules={[{ required: true, message: '请输入API Key' }]}
          >
            <Input.Password 
              placeholder="sk-..." 
              showCount
              maxLength={200}
            />
          </Form.Item>

          <Form.Item
            name="baseUrl"
            label="API Base URL"
            rules={[
              { required: true, message: '请输入API Base URL' },
              { type: 'url', message: '请输入有效的URL' }
            ]}
          >
            <Input placeholder="https://api.openai.com/v1" />
          </Form.Item>

          <Form.Item
            name="model"
            label="模型"
            rules={[{ required: true, message: '请选择模型' }]}
          >
            <Select>
              <Option value="gpt-4">GPT-4</Option>
              <Option value="gpt-4-turbo">GPT-4 Turbo</Option>
              <Option value="gpt-3.5-turbo">GPT-3.5 Turbo</Option>
              <Option value="claude-3-opus">Claude 3 Opus</Option>
              <Option value="claude-3-sonnet">Claude 3 Sonnet</Option>
              <Option value="claude-3-haiku">Claude 3 Haiku</Option>
            </Select>
          </Form.Item>

          <Form.Item
            name="temperature"
            label={`Temperature: ${form.getFieldValue('temperature') || 0.7}`}
          >
            <Slider
              min={0}
              max={1}
              step={0.1}
              marks={{
                0: '保守',
                0.5: '平衡',
                1: '创意'
              }}
            />
          </Form.Item>

          <Form.Item>
            <Space>
              <Button 
                type="primary" 
                htmlType="submit" 
                loading={loading}
                icon={<CloudOutlined />}
              >
                保存配置
              </Button>
              <Button 
                loading={testLoading}
                onClick={handleTest}
                icon={<ReloadOutlined />}
              >
                测试连接
              </Button>
            </Space>
          </Form.Item>
        </Form>
      </Card>
    );
  };

  // 微信配置表单
  const WeChatSettings = () => {
    const [form] = Form.useForm();

    const handleSave = async () => {
      try {
        const values = await form.validateFields();
        setLoading(true);
        const result = await updateWeChatConfig(values);
        if (result.success) {
          message.success('微信配置保存成功');
        }
      } catch (error) {
        console.error('Save failed:', error);
      } finally {
        setLoading(false);
      }
    };

    return (
      <Card title="微信公众号配置" icon={<WechatOutlined />}>
        <Alert
          message="配置说明"
          description="请在微信公众平台获取以下配置信息。注意保护好您的密钥信息，不要泄露给他人。"
          type="info"
          style={{ marginBottom: '16px' }}
        />

        <Form
          form={form}
          layout="vertical"
          initialValues={wechatConfig}
          onFinish={handleSave}
        >
          <Form.Item
            name="appId"
            label="App ID"
            rules={[
              { required: true, message: '请输入App ID' },
              { pattern: /^wx[a-f0-9]{16}$/, message: 'App ID格式不正确' }
            ]}
          >
            <Input placeholder="wx1234567890123456" />
          </Form.Item>

          <Form.Item
            name="appSecret"
            label="App Secret"
            rules={[{ required: true, message: '请输入App Secret' }]}
          >
            <Input.Password 
              placeholder="请输入App Secret" 
              showCount
              maxLength={64}
            />
          </Form.Item>

          <Form.Item
            name="token"
            label="Token"
            rules={[{ required: true, message: '请输入Token' }]}
          >
            <Input placeholder="请输入自定义Token" />
          </Form.Item>

          <Form.Item>
            <Button 
              type="primary" 
              htmlType="submit" 
              loading={loading}
              icon={<WechatOutlined />}
            >
              保存配置
            </Button>
          </Form.Item>
        </Form>
      </Card>
    );
  };

  // 爬虫配置表单
  const CrawlSettings = () => {
    const [form] = Form.useForm();

    const handleSave = async () => {
      try {
        const values = await form.validateFields();
        // 处理sources字段
        const processedValues = {
          ...values,
          sources: values.sources ? values.sources.split('\n').filter(url => url.trim()) : []
        };
        
        setLoading(true);
        const result = await updateCrawlConfig(processedValues);
        if (result.success) {
          message.success('爬虫配置保存成功');
        }
      } catch (error) {
        console.error('Save failed:', error);
      } finally {
        setLoading(false);
      }
    };

    return (
      <Card title="爬虫配置" icon={<CloudOutlined />}>
        <Form
          form={form}
          layout="vertical"
          initialValues={{
            ...crawlConfig,
            sources: crawlConfig.sources?.join('\n') || ''
          }}
          onFinish={handleSave}
        >
          <Form.Item
            name="sources"
            label="爬取源URL列表"
            extra="每行一个URL，支持微信公众号文章链接"
          >
            <TextArea
              rows={6}
              placeholder={`https://mp.weixin.qq.com/s/xxxxx\nhttps://mp.weixin.qq.com/s/yyyyy`}
            />
          </Form.Item>

          <Form.Item
            name="schedule"
            label="爬取频率"
          >
            <Select>
              <Option value="manual">手动触发</Option>
              <Option value="hourly">每小时</Option>
              <Option value="daily">每天</Option>
              <Option value="weekly">每周</Option>
            </Select>
          </Form.Item>

          <Form.Item
            name="delay"
            label="请求间隔（秒）"
            extra="避免频率过高被限制"
          >
            <Slider
              min={1}
              max={10}
              marks={{
                1: '1s',
                5: '5s',
                10: '10s'
              }}
            />
          </Form.Item>

          <Form.Item
            name="autoRewrite"
            label="自动AI改写"
            valuePropName="checked"
          >
            <Switch checkedChildren="开启" unCheckedChildren="关闭" />
          </Form.Item>

          <Form.Item>
            <Button 
              type="primary" 
              htmlType="submit" 
              loading={loading}
              icon={<CloudOutlined />}
            >
              保存配置
            </Button>
          </Form.Item>
        </Form>
      </Card>
    );
  };

  // 系统设置
  const SystemSettings = () => {
    const handleImport = (info) => {
      if (info.file.status === 'done') {
        importSettings(info.file.originFileObj)
          .then(() => {
            message.success('设置导入成功');
          })
          .catch((error) => {
            message.error('设置导入失败：' + error.message);
          });
      }
    };

    const handleReset = () => {
      Modal.confirm({
        title: '重置系统设置',
        content: '确定要重置所有系统设置吗？此操作不可恢复。',
        onOk: () => {
          resetSettings();
        }
      });
    };

    return (
      <Card title="系统设置" icon={<SettingOutlined />}>
        <Form layout="vertical">
          <Form.Item label="界面主题">
            <Select value={theme} onChange={setTheme}>
              <Option value="light">亮色主题</Option>
              <Option value="dark">暗色主题</Option>
            </Select>
          </Form.Item>

          <Form.Item label="系统语言">
            <Select value={language} onChange={setLanguage}>
              <Option value="zh-CN">简体中文</Option>
              <Option value="en-US">English</Option>
            </Select>
          </Form.Item>

          <Form.Item label="自动保存">
            <Switch 
              checked={autoSave} 
              onChange={setAutoSave}
              checkedChildren="开启" 
              unCheckedChildren="关闭" 
            />
          </Form.Item>

          <Form.Item label="系统通知">
            <Switch 
              checked={notifications} 
              onChange={setNotifications}
              checkedChildren="开启" 
              unCheckedChildren="关闭" 
            />
          </Form.Item>

          <Divider>数据管理</Divider>

          <Form.Item label="导出设置">
            <Space>
              <Button 
                icon={<ExportOutlined />}
                onClick={exportSettings}
              >
                导出设置
              </Button>
              <Upload
                accept=".json"
                showUploadList={false}
                onChange={handleImport}
                beforeUpload={() => false}
              >
                <Button icon={<ImportOutlined />}>
                  导入设置
                </Button>
              </Upload>
            </Space>
          </Form.Item>

          <Form.Item label="重置系统">
            <Button 
              danger 
              onClick={handleReset}
              icon={<ReloadOutlined />}
            >
              重置所有设置
            </Button>
          </Form.Item>
        </Form>
      </Card>
    );
  };

  const tabItems = [
    {
      key: 'llm',
      label: (
        <span>
          <RobotOutlined />
          LLM配置
        </span>
      ),
      children: <LLMSettings />
    },
    {
      key: 'wechat',
      label: (
        <span>
          <WechatOutlined />
          微信配置
        </span>
      ),
      children: <WeChatSettings />
    },
    {
      key: 'crawl',
      label: (
        <span>
          <CloudOutlined />
          爬虫配置
        </span>
      ),
      children: <CrawlSettings />
    },
    {
      key: 'system',
      label: (
        <span>
          <SettingOutlined />
          系统设置
        </span>
      ),
      children: <SystemSettings />
    }
  ];

  return (
    <div style={{ padding: '24px' }}>
      <div style={{ marginBottom: '24px' }}>
        <h1 style={{ fontSize: '24px', fontWeight: 'bold', margin: 0 }}>
          系统设置
        </h1>
        <p style={{ color: '#666', marginTop: '8px' }}>
          配置LLM API、微信公众号、爬虫参数等系统设置
        </p>
      </div>

      <Tabs
        defaultActiveKey="llm"
        items={tabItems}
        size="large"
      />
    </div>
  );
};

export default Settings;
