import React, { useState, useEffect } from 'react';
import { 
  Card, 
  Row, 
  Col, 
  Statistic, 
  Button, 
  List, 
  Avatar, 
  Progress,
  Badge,
  Empty,
  Spin,
  Alert
} from 'antd';
import {
  FileTextOutlined,
  SendOutlined,
  ClockCircleOutlined,
  EditOutlined,
  EyeOutlined,
  LikeOutlined,
  MessageOutlined,
  ShareAltOutlined,
  TrophyOutlined,
  RocketOutlined,
  BulbOutlined,
  SettingOutlined
} from '@ant-design/icons';

const Dashboard = () => {
  const [loading, setLoading] = useState(true);
  const [stats, setStats] = useState({
    totalArticles: 0,
    published: 0,
    scheduled: 0,
    draft: 0
  });
  const [recentArticles, setRecentArticles] = useState([]);
  const [notifications, setNotifications] = useState([]);

  // 模拟数据加载
  useEffect(() => {
    const loadData = async () => {
      setLoading(true);
      
      // 模拟API调用
      await new Promise(resolve => setTimeout(resolve, 1000));
      
      setStats({
        totalArticles: 42,
        published: 28,
        scheduled: 8,
        draft: 6
      });

      setRecentArticles([
        {
          id: 1,
          title: "AI技术改变未来生活的10种方式",
          status: "published",
          createdAt: "2024-01-15 10:30",
          views: 3250,
          likes: 128,
          comments: 45
        },
        {
          id: 2,
          title: "2024年投资理财新趋势解析",
          status: "scheduled",
          createdAt: "2024-01-16 09:00",
          scheduledTime: "2024-01-18 10:00",
          views: 0,
          likes: 0,
          comments: 0
        },
        {
          id: 3,
          title: "健康饮食：地中海饮食法完全指南",
          status: "draft",
          createdAt: "2024-01-17 11:20",
          views: 0,
          likes: 0,
          comments: 0
        }
      ]);

      setNotifications([
        {
          id: 1,
          type: 'success',
          title: '文章发布成功',
          message: '《AI技术改变未来生活》已成功发布',
          time: '5分钟前'
        },
        {
          id: 2,
          type: 'warning',
          title: '定时发布提醒',
          message: '《投资理财新趋势》将在1小时后发布',
          time: '30分钟前'
        },
        {
          id: 3,
          type: 'info',
          title: '爬取任务完成',
          message: '成功爬取并改写了3篇文章',
          time: '2小时前'
        }
      ]);

      setLoading(false);
    };

    loadData();
  }, []);

  // 获取状态颜色
  const getStatusColor = (status) => {
    const colorMap = {
      published: 'success',
      scheduled: 'warning',
      draft: 'default'
    };
    return colorMap[status] || 'default';
  };

  // 获取状态文本
  const getStatusText = (status) => {
    const textMap = {
      published: '已发布',
      scheduled: '待发布',
      draft: '草稿'
    };
    return textMap[status] || status;
  };

  // 快速操作项
  const quickActions = [
    {
      title: '生成文章',
      icon: <BulbOutlined style={{ fontSize: '24px', color: '#1677ff' }} />,
      description: '使用AI生成新文章',
      action: () => console.log('生成文章')
    },
    {
      title: '爬取文章',
      icon: <RocketOutlined style={{ fontSize: '24px', color: '#52c41a' }} />,
      description: '爬取并改写文章',
      action: () => console.log('爬取文章')
    },
    {
      title: '查看统计',
      icon: <TrophyOutlined style={{ fontSize: '24px', color: '#faad14' }} />,
      description: '查看详细数据分析',
      action: () => console.log('查看统计')
    },
    {
      title: '系统设置',
      icon: <SettingOutlined style={{ fontSize: '24px', color: '#722ed1' }} />,
      description: '配置LLM和微信API',
      action: () => console.log('系统设置')
    }
  ];

  if (loading) {
    return (
      <div style={{ 
        display: 'flex', 
        justifyContent: 'center', 
        alignItems: 'center', 
        height: '400px' 
      }}>
        <Spin size="large" tip="正在加载数据..." />
      </div>
    );
  }

  return (
    <div style={{ padding: '24px' }}>
      {/* 欢迎信息 */}
      <div style={{ marginBottom: '24px' }}>
        <h1 style={{ fontSize: '24px', fontWeight: 'bold', margin: 0 }}>
          运营概览
        </h1>
        <p style={{ color: '#666', marginTop: '8px' }}>
          欢迎使用微信公众号自动运营系统，这里是您的运营数据概览
        </p>
      </div>

      {/* 统计卡片 */}
      <Row gutter={[16, 16]} style={{ marginBottom: '24px' }}>
        <Col xs={24} sm={12} lg={6}>
          <Card>
            <Statistic
              title="总文章数"
              value={stats.totalArticles}
              prefix={<FileTextOutlined />}
              valueStyle={{ color: '#1677ff' }}
            />
          </Card>
        </Col>
        <Col xs={24} sm={12} lg={6}>
          <Card>
            <Statistic
              title="已发布"
              value={stats.published}
              prefix={<SendOutlined />}
              valueStyle={{ color: '#52c41a' }}
            />
          </Card>
        </Col>
        <Col xs={24} sm={12} lg={6}>
          <Card>
            <Statistic
              title="待发布"
              value={stats.scheduled}
              prefix={<ClockCircleOutlined />}
              valueStyle={{ color: '#faad14' }}
            />
          </Card>
        </Col>
        <Col xs={24} sm={12} lg={6}>
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

      <Row gutter={[16, 16]}>
        {/* 快速操作 */}
        <Col xs={24} lg={12}>
          <Card title="快速操作" style={{ height: '400px' }}>
            <Row gutter={[16, 16]}>
              {quickActions.map((action, index) => (
                <Col xs={12} key={index}>
                  <Card
                    hoverable
                    size="small"
                    style={{ textAlign: 'center', height: '140px' }}
                    onClick={action.action}
                  >
                    <div style={{ marginBottom: '12px' }}>
                      {action.icon}
                    </div>
                    <div style={{ fontWeight: 'bold', marginBottom: '4px' }}>
                      {action.title}
                    </div>
                    <div style={{ fontSize: '12px', color: '#666' }}>
                      {action.description}
                    </div>
                  </Card>
                </Col>
              ))}
            </Row>
          </Card>
        </Col>

        {/* 最近文章 */}
        <Col xs={24} lg={12}>
          <Card 
            title="最近文章" 
            style={{ height: '400px' }}
            extra={<Button type="link">查看全部</Button>}
          >
            {recentArticles.length > 0 ? (
              <List
                dataSource={recentArticles}
                renderItem={(item) => (
                  <List.Item
                    actions={[
                      <div key="stats" style={{ display: 'flex', gap: '12px', fontSize: '12px', color: '#666' }}>
                        <span><EyeOutlined /> {item.views}</span>
                        <span><LikeOutlined /> {item.likes}</span>
                        <span><MessageOutlined /> {item.comments}</span>
                      </div>
                    ]}
                  >
                    <List.Item.Meta
                      avatar={
                        <Avatar 
                          icon={<FileTextOutlined />} 
                          style={{ backgroundColor: '#1677ff' }}
                        />
                      }
                      title={
                        <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                          <span style={{ fontSize: '14px' }}>{item.title}</span>
                          <Badge 
                            status={getStatusColor(item.status)} 
                            text={getStatusText(item.status)}
                          />
                        </div>
                      }
                      description={
                        <span style={{ fontSize: '12px', color: '#999' }}>
                          {item.createdAt}
                        </span>
                      }
                    />
                  </List.Item>
                )}
              />
            ) : (
              <Empty description="暂无文章" />
            )}
          </Card>
        </Col>
      </Row>

      {/* 系统通知 */}
      <Row style={{ marginTop: '16px' }}>
        <Col span={24}>
          <Card title="系统通知">
            {notifications.length > 0 ? (
              <List
                dataSource={notifications}
                renderItem={(item) => (
                  <List.Item>
                    <Alert
                      message={item.title}
                      description={
                        <div>
                          <div>{item.message}</div>
                          <div style={{ fontSize: '12px', color: '#999', marginTop: '4px' }}>
                            {item.time}
                          </div>
                        </div>
                      }
                      type={item.type}
                      showIcon
                      style={{ width: '100%' }}
                    />
                  </List.Item>
                )}
              />
            ) : (
              <Empty description="暂无通知" />
            )}
          </Card>
        </Col>
      </Row>
    </div>
  );
};

export default Dashboard;
