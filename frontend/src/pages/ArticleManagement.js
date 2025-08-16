import React, { useState, useEffect } from 'react';
import { 
  Table, 
  Button, 
  Space, 
  Tag, 
  Modal, 
  Form, 
  Input, 
  Select, 
  Card,
  Row,
  Col,
  Statistic,
  message,
  Popconfirm,
  Tooltip,
  Badge,
  Alert,
  Switch
} from 'antd';
import {
  PlusOutlined,
  EditOutlined,
  DeleteOutlined,
  EyeOutlined,
  SendOutlined,
  DownloadOutlined,
  RocketOutlined,
  BulbOutlined,
  FileTextOutlined,
  ClockCircleOutlined
} from '@ant-design/icons';

const { Option } = Select;
const { TextArea } = Input;

const ArticleManagement = () => {
  const [articles, setArticles] = useState([]);
  const [loading, setLoading] = useState(false);
  const [selectedRowKeys, setSelectedRowKeys] = useState([]);
  const [modalVisible, setModalVisible] = useState(false);
  const [modalType, setModalType] = useState('create'); // create, edit, preview
  const [currentArticle, setCurrentArticle] = useState(null);
  const [filterStatus, setFilterStatus] = useState('all');
  const [form] = Form.useForm();
  
  // 新增状态用于AI生成和爬取对话框
  const [generateModalVisible, setGenerateModalVisible] = useState(false);
  const [crawlModalVisible, setCrawlModalVisible] = useState(false);
  const [generateLoading, setGenerateLoading] = useState(false);
  const [crawlLoading, setCrawlLoading] = useState(false);
  const [generateForm] = Form.useForm();
  const [crawlForm] = Form.useForm();

  // 模拟数据
  useEffect(() => {
    loadArticles();
  }, []);

  const loadArticles = async () => {
    setLoading(true);
    
    // 模拟API调用
    await new Promise(resolve => setTimeout(resolve, 1000));
    
    const mockArticles = [
      {
        id: 1,
        title: "AI技术改变未来生活的10种方式",
        content: "人工智能正在深刻改变我们的生活方式...",
        status: "published",
        createdAt: "2024-01-15 10:30",
        publishedAt: "2024-01-15 14:00",
        views: 3250,
        likes: 128,
        comments: 45,
        tags: ["AI", "科技", "未来"]
      },
      {
        id: 2,
        title: "2024年投资理财新趋势解析",
        content: "随着经济形势的变化，投资策略也需要相应调整...",
        status: "scheduled",
        createdAt: "2024-01-16 09:00",
        scheduledTime: "2024-01-18 10:00",
        views: 0,
        likes: 0,
        comments: 0,
        tags: ["投资", "理财", "趋势"]
      },
      {
        id: 3,
        title: "健康饮食：地中海饮食法完全指南",
        content: "地中海饮食被认为是世界上最健康的饮食方式之一...",
        status: "draft",
        createdAt: "2024-01-17 11:20",
        views: 0,
        likes: 0,
        comments: 0,
        tags: ["健康", "饮食", "生活方式"]
      }
    ];
    
    setArticles(mockArticles);
    setLoading(false);
  };

  // 状态配置
  const statusConfig = {
    published: { color: 'green', text: '已发布' },
    scheduled: { color: 'orange', text: '待发布' },
    draft: { color: 'default', text: '草稿' }
  };

  // 表格列定义
  const columns = [
    {
      title: '标题',
      dataIndex: 'title',
      key: 'title',
      ellipsis: true,
      render: (text, record) => (
        <div>
          <div style={{ fontWeight: 'bold', marginBottom: '4px' }}>
            {text}
          </div>
          <div style={{ fontSize: '12px', color: '#666' }}>
            {record.content.substring(0, 50)}...
          </div>
        </div>
      )
    },
    {
      title: '状态',
      dataIndex: 'status',
      key: 'status',
      width: 100,
      render: (status) => (
        <Tag color={statusConfig[status]?.color}>
          {statusConfig[status]?.text}
        </Tag>
      )
    },
    {
      title: '标签',
      dataIndex: 'tags',
      key: 'tags',
      width: 150,
      render: (tags) => (
        <Space wrap>
          {tags?.map(tag => (
            <Tag key={tag} size="small">{tag}</Tag>
          ))}
        </Space>
      )
    },
    {
      title: '数据',
      key: 'stats',
      width: 120,
      render: (_, record) => (
        <Space direction="vertical" size="small">
          <div style={{ fontSize: '12px' }}>
            👀 {record.views} | 👍 {record.likes} | 💬 {record.comments}
          </div>
        </Space>
      )
    },
    {
      title: '创建时间',
      dataIndex: 'createdAt',
      key: 'createdAt',
      width: 120,
      render: (time) => (
        <div style={{ fontSize: '12px' }}>{time}</div>
      )
    },
    {
      title: '操作',
      key: 'action',
      width: 180,
      render: (_, record) => (
        <Space>
          <Tooltip title="预览">
            <Button 
              type="text" 
              icon={<EyeOutlined />} 
              onClick={() => handlePreview(record)}
            />
          </Tooltip>
          <Tooltip title="编辑">
            <Button 
              type="text" 
              icon={<EditOutlined />} 
              onClick={() => handleEdit(record)}
            />
          </Tooltip>
          {record.status === 'draft' && (
            <Tooltip title="发布">
              <Button 
                type="text" 
                icon={<SendOutlined />} 
                onClick={() => handlePublish(record.id)}
              />
            </Tooltip>
          )}
          <Popconfirm
            title="确定删除这篇文章吗？"
            onConfirm={() => handleDelete(record.id)}
            okText="确定"
            cancelText="取消"
          >
            <Tooltip title="删除">
              <Button 
                type="text" 
                danger 
                icon={<DeleteOutlined />} 
              />
            </Tooltip>
          </Popconfirm>
        </Space>
      )
    }
  ];

  // 行选择配置
  const rowSelection = {
    selectedRowKeys,
    onChange: setSelectedRowKeys,
  };

  // 过滤后的文章
  const filteredArticles = filterStatus === 'all' 
    ? articles 
    : articles.filter(article => article.status === filterStatus);

  // 处理函数
  const handleCreate = () => {
    setModalType('create');
    setCurrentArticle(null);
    setModalVisible(true);
    form.resetFields();
  };

  const handleEdit = (record) => {
    setModalType('edit');
    setCurrentArticle(record);
    setModalVisible(true);
    form.setFieldsValue(record);
  };

  const handlePreview = (record) => {
    setModalType('preview');
    setCurrentArticle(record);
    setModalVisible(true);
  };

  const handleDelete = (id) => {
    setArticles(articles.filter(article => article.id !== id));
    message.success('删除成功');
  };

  const handlePublish = (id) => {
    setArticles(articles.map(article => 
      article.id === id 
        ? { ...article, status: 'published', publishedAt: new Date().toLocaleString() }
        : article
    ));
    message.success('发布成功');
  };

  const handleBatchDelete = () => {
    if (selectedRowKeys.length === 0) {
      message.warning('请选择要删除的文章');
      return;
    }
    
    Modal.confirm({
      title: '批量删除',
      content: `确定删除选中的 ${selectedRowKeys.length} 篇文章吗？`,
      onOk: () => {
        setArticles(articles.filter(article => !selectedRowKeys.includes(article.id)));
        setSelectedRowKeys([]);
        message.success('批量删除成功');
      }
    });
  };

  const handleModalOk = async () => {
    try {
      const values = await form.validateFields();
      
      if (modalType === 'create') {
        const newArticle = {
          id: Date.now(),
          ...values,
          status: 'draft',
          createdAt: new Date().toLocaleString(),
          views: 0,
          likes: 0,
          comments: 0,
          tags: values.tags || []
        };
        setArticles([newArticle, ...articles]);
        message.success('创建成功');
      } else if (modalType === 'edit') {
        setArticles(articles.map(article => 
          article.id === currentArticle.id 
            ? { ...article, ...values }
            : article
        ));
        message.success('更新成功');
      }
      
      setModalVisible(false);
    } catch (error) {
      console.error('Validation failed:', error);
    }
  };

  // AI生成文章
  const handleGenerate = () => {
    setGenerateModalVisible(true);
    generateForm.resetFields();
  };

  const handleGenerateOk = async () => {
    try {
      const values = await generateForm.validateFields();
      setGenerateLoading(true);
      
      const response = await fetch('/api/generate', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(values)
      });
      
      const result = await response.json();
      
      if (result.success) {
        const newArticle = {
          id: Date.now(),
          title: result.article.title,
          content: result.article.content,
          status: 'draft',
          createdAt: new Date().toLocaleString(),
          views: 0,
          likes: 0,
          comments: 0,
          tags: ['AI生成']
        };
        setArticles([newArticle, ...articles]);
        message.success(result.message);
        setGenerateModalVisible(false);
      } else {
        message.error(result.message);
      }
    } catch (error) {
      message.error('生成失败，请检查网络连接');
      console.error('Generate error:', error);
    } finally {
      setGenerateLoading(false);
    }
  };

  // 爬取文章
  const handleCrawl = () => {
    setCrawlModalVisible(true);
    crawlForm.resetFields();
  };

  const handleCrawlOk = async () => {
    try {
      const values = await crawlForm.validateFields();
      setCrawlLoading(true);
      
      const response = await fetch('/api/crawl', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(values)
      });
      
      const result = await response.json();
      
      if (result.success) {
        const newArticles = result.articles.map((article, index) => ({
          id: Date.now() + index,
          title: article.title,
          content: article.content,
          status: 'draft',
          createdAt: new Date().toLocaleString(),
          views: 0,
          likes: 0,
          comments: 0,
          tags: ['爬取', article.source || '外部']
        }));
        setArticles([...newArticles, ...articles]);
        message.success(result.message);
        setCrawlModalVisible(false);
      } else {
        message.error(result.message);
      }
    } catch (error) {
      message.error('爬取失败，请检查网络连接');
      console.error('Crawl error:', error);
    } finally {
      setCrawlLoading(false);
    }
  };

  // 统计数据
  const stats = {
    total: articles.length,
    published: articles.filter(a => a.status === 'published').length,
    scheduled: articles.filter(a => a.status === 'scheduled').length,
    draft: articles.filter(a => a.status === 'draft').length
  };

  return (
    <div style={{ padding: '24px' }}>
      {/* 统计卡片 */}
      <Row gutter={16} style={{ marginBottom: '24px' }}>
        <Col span={6}>
          <Card>
            <Statistic
              title="总文章数"
              value={stats.total}
              prefix={<FileTextOutlined />}
            />
          </Card>
        </Col>
        <Col span={6}>
          <Card>
            <Statistic
              title="已发布"
              value={stats.published}
              prefix={<SendOutlined />}
              valueStyle={{ color: '#52c41a' }}
            />
          </Card>
        </Col>
        <Col span={6}>
          <Card>
            <Statistic
              title="待发布"
              value={stats.scheduled}
              prefix={<ClockCircleOutlined />}
              valueStyle={{ color: '#faad14' }}
            />
          </Card>
        </Col>
        <Col span={6}>
          <Card>
            <Statistic
              title="草稿"
              value={stats.draft}
              prefix={<EditOutlined />}
              valueStyle={{ color: '#8c8c8c' }}
            />
          </Card>
        </Col>
      </Row>

      {/* 操作栏 */}
      <Card style={{ marginBottom: '16px' }}>
        <Row justify="space-between" align="middle">
          <Col>
            <Space>
              <Button type="primary" icon={<PlusOutlined />} onClick={handleCreate}>
                新建文章
              </Button>
              <Button icon={<BulbOutlined />} onClick={handleGenerate}>
                AI生成
              </Button>
              <Button icon={<RocketOutlined />} onClick={handleCrawl}>
                爬取文章
              </Button>
              <Button 
                danger 
                disabled={selectedRowKeys.length === 0}
                onClick={handleBatchDelete}
              >
                批量删除
              </Button>
            </Space>
          </Col>
          <Col>
            <Space>
              <Select
                value={filterStatus}
                onChange={setFilterStatus}
                style={{ width: 120 }}
              >
                <Option value="all">全部状态</Option>
                <Option value="published">已发布</Option>
                <Option value="scheduled">待发布</Option>
                <Option value="draft">草稿</Option>
              </Select>
              <Button icon={<DownloadOutlined />}>
                导出数据
              </Button>
            </Space>
          </Col>
        </Row>
      </Card>

      {/* 文章表格 */}
      <Card>
        <Table
          rowSelection={rowSelection}
          columns={columns}
          dataSource={filteredArticles}
          rowKey="id"
          loading={loading}
          pagination={{
            total: filteredArticles.length,
            pageSize: 10,
            showSizeChanger: true,
            showQuickJumper: true,
            showTotal: (total, range) => 
              `第 ${range[0]}-${range[1]} 条/共 ${total} 条`
          }}
        />
      </Card>

      {/* 弹窗 */}
      <Modal
        title={
          modalType === 'create' ? '新建文章' :
          modalType === 'edit' ? '编辑文章' : '预览文章'
        }
        open={modalVisible}
        onOk={modalType === 'preview' ? undefined : handleModalOk}
        onCancel={() => setModalVisible(false)}
        width={800}
        footer={modalType === 'preview' ? [
          <Button key="close" onClick={() => setModalVisible(false)}>
            关闭
          </Button>
        ] : undefined}
      >
        {modalType === 'preview' ? (
          <div>
            <h3>{currentArticle?.title}</h3>
            <div style={{ marginBottom: '16px' }}>
              <Space>
                <Tag color={statusConfig[currentArticle?.status]?.color}>
                  {statusConfig[currentArticle?.status]?.text}
                </Tag>
                <span style={{ color: '#666' }}>
                  {currentArticle?.createdAt}
                </span>
              </Space>
            </div>
            <div style={{ lineHeight: 1.6 }}>
              {currentArticle?.content}
            </div>
          </div>
        ) : (
          <Form form={form} layout="vertical">
            <Form.Item
              name="title"
              label="标题"
              rules={[{ required: true, message: '请输入文章标题' }]}
            >
              <Input placeholder="请输入文章标题" />
            </Form.Item>
            <Form.Item
              name="content"
              label="内容"
              rules={[{ required: true, message: '请输入文章内容' }]}
            >
              <TextArea 
                rows={10} 
                placeholder="请输入文章内容" 
                showCount
                maxLength={5000}
              />
            </Form.Item>
            <Form.Item
              name="tags"
              label="标签"
            >
              <Select
                mode="tags"
                placeholder="请输入标签，按回车确认"
                style={{ width: '100%' }}
              >
                <Option value="AI">AI</Option>
                <Option value="科技">科技</Option>
                <Option value="投资">投资</Option>
                <Option value="健康">健康</Option>
                <Option value="生活方式">生活方式</Option>
              </Select>
            </Form.Item>
          </Form>
        )}
      </Modal>

      {/* AI生成文章模态框 */}
      <Modal
        title="AI生成文章"
        open={generateModalVisible}
        onOk={handleGenerateOk}
        onCancel={() => setGenerateModalVisible(false)}
        confirmLoading={generateLoading}
        width={600}
      >
        <Form form={generateForm} layout="vertical">
          <Form.Item
            name="topic"
            label="文章主题"
            rules={[{ required: true, message: '请输入文章主题' }]}
          >
            <Input 
              placeholder="例如：人工智能在医疗领域的应用" 
              showCount 
              maxLength={100}
            />
          </Form.Item>
          
          <Form.Item
            name="style"
            label="写作风格"
            initialValue="professional"
          >
            <Select>
              <Select.Option value="professional">专业严谨</Select.Option>
              <Select.Option value="casual">轻松随意</Select.Option>
              <Select.Option value="creative">创意有趣</Select.Option>
            </Select>
          </Form.Item>
          
          <Form.Item
            name="length"
            label="文章长度"
            initialValue="medium"
          >
            <Select>
              <Select.Option value="short">短文章 (500字左右)</Select.Option>
              <Select.Option value="medium">中等篇幅 (1000字左右)</Select.Option>
              <Select.Option value="long">长文章 (2000字左右)</Select.Option>
            </Select>
          </Form.Item>
          
          <Alert
            message="提示"
            description="AI将根据您的要求生成文章，生成后将自动保存为草稿，您可以进一步编辑和完善。"
            type="info"
            showIcon
            style={{ marginTop: '16px' }}
          />
        </Form>
      </Modal>

      {/* 爬取文章模态框 */}
      <Modal
        title="智能爬取文章"
        open={crawlModalVisible}
        onOk={handleCrawlOk}
        onCancel={() => setCrawlModalVisible(false)}
        confirmLoading={crawlLoading}
        width={700}
      >
        <Form form={crawlForm} layout="vertical">
          <Form.Item
            name="source_type"
            label="爬取源类型"
            initialValue="auto"
          >
            <Select>
              <Select.Option value="auto">🤖 自动识别</Select.Option>
              <Select.Option value="wechat">📱 微信公众号</Select.Option>
              <Select.Option value="zhihu">🎓 知乎答主</Select.Option>
              <Select.Option value="website">🌐 通用网站</Select.Option>
            </Select>
          </Form.Item>
          
          <Form.Item
            name="source_url"
            label="爬取源URL"
            rules={[
              { required: true, message: '请输入爬取源URL' }
            ]}
          >
            <Input.TextArea 
              placeholder={`请输入URL，支持多种类型：
              
• 微信公众号文章：https://mp.weixin.qq.com/s/xxxxx
• 知乎答主主页：https://www.zhihu.com/people/xxxxx  
• 通用网站：https://example.com
• RSS订阅：https://example.com/rss`}
              rows={4}
            />
          </Form.Item>
          
          <Row gutter={16}>
            <Col span={12}>
              <Form.Item
                name="max_count"
                label="最大爬取数量"
                initialValue={5}
              >
                <Select>
                  <Select.Option value={1}>1篇</Select.Option>
                  <Select.Option value={3}>3篇</Select.Option>
                  <Select.Option value={5}>5篇</Select.Option>
                  <Select.Option value={10}>10篇</Select.Option>
                </Select>
              </Form.Item>
            </Col>
            <Col span={12}>
              <Form.Item
                name="enable_rewrite"
                label="LLM智能改写"
                initialValue={true}
                valuePropName="checked"
              >
                <Switch 
                  checkedChildren="启用" 
                  unCheckedChildren="关闭"
                />
              </Form.Item>
            </Col>
          </Row>
          
          <Alert
            message="🚀 智能爬取功能"
            description={
              <div>
                <p><strong>✨ 支持多种内容源：</strong></p>
                <p>• <strong>微信公众号</strong>：爬取单篇文章内容</p>
                <p>• <strong>知乎答主</strong>：获取用户最新文章和优质回答</p>
                <p>• <strong>通用网站</strong>：智能识别RSS源或页面文章</p>
                <p><strong>🤖 AI改写：</strong>将爬取内容智能改写为微信公众号风格</p>
                <p><strong>📝 版权提醒：</strong>请确保内容使用符合法律法规</p>
              </div>
            }
            type="info"
            showIcon
            style={{ marginTop: '16px' }}
          />
        </Form>
      </Modal>
    </div>
  );
};

export default ArticleManagement;
