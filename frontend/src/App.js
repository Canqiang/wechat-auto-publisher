import React, { useState, useEffect } from 'react';
import { Routes, Route, Navigate, useLocation } from 'react-router-dom';
import { 
  Layout, 
  Menu, 
  Avatar, 
  Dropdown, 
  Button, 
  Spin, 
  message,
  Badge,
  Tooltip
} from 'antd';
import {
  DashboardOutlined,
  FileTextOutlined,
  CalendarOutlined,
  SettingOutlined,
  UserOutlined,
  LogoutOutlined,
  BellOutlined,
  MenuFoldOutlined,
  MenuUnfoldOutlined,
  GlobalOutlined,
  BulbOutlined
} from '@ant-design/icons';

// 页面组件
import Dashboard from './pages/Dashboard';
import ArticleManagement from './pages/ArticleManagement';
import PublishSchedule from './pages/PublishSchedule';
import Settings from './pages/Settings';
import Login from './pages/Login';
import NotFound from './pages/NotFound';

// Context hooks
import { useAuth } from './contexts/AuthContext';
import { useSettings } from './contexts/SettingsContext';

const { Header, Sider, Content } = Layout;

// 主应用组件
const WeChatAutoPublisher = () => {
  const location = useLocation();
  const { user, isAuthenticated, loading: authLoading, logout } = useAuth();
  const { 
    theme, 
    sidebarCollapsed, 
    setSidebarCollapsed,
    notifications,
    setTheme
  } = useSettings();

  // 本地状态
  const [notificationCount, setNotificationCount] = useState(3);

  // 如果正在验证身份，显示加载页面
  if (authLoading) {
    return (
      <div style={{ 
        height: '100vh', 
        display: 'flex', 
        alignItems: 'center', 
        justifyContent: 'center',
        background: '#f5f5f5'
      }}>
        <Spin size="large" tip="正在加载..." />
      </div>
    );
  }

  // 如果未登录，显示登录页面
  if (!isAuthenticated) {
    return <Login />;
  }

  // 侧边栏菜单项
  const menuItems = [
    {
      key: '/dashboard',
      icon: <DashboardOutlined />,
      label: '仪表板',
    },
    {
      key: '/articles',
      icon: <FileTextOutlined />,
      label: '文章管理',
    },
    {
      key: '/schedule',
      icon: <CalendarOutlined />,
      label: '发布计划',
    },
    {
      key: '/settings',
      icon: <SettingOutlined />,
      label: '系统设置',
    },
  ];

  // 用户下拉菜单
  const userMenuItems = [
    {
      key: 'profile',
      icon: <UserOutlined />,
      label: '个人资料',
    },
    {
      key: 'preferences',
      icon: <BulbOutlined />,
      label: '偏好设置',
    },
    {
      type: 'divider',
    },
    {
      key: 'logout',
      icon: <LogoutOutlined />,
      label: '退出登录',
      danger: true,
    },
  ];

  // 处理菜单点击
  const handleMenuClick = ({ key }) => {
    if (key === 'logout') {
      logout();
    } else {
      message.info(`点击了 ${key}`);
    }
  };

  // 切换主题
  const toggleTheme = () => {
    setTheme(theme === 'light' ? 'dark' : 'light');
  };

  // 获取当前页面标题
  const getPageTitle = () => {
    const path = location.pathname;
    switch (path) {
      case '/dashboard':
        return '运营概览';
      case '/articles':
        return '文章管理';
      case '/schedule':
        return '发布计划';
      case '/settings':
        return '系统设置';
      default:
        return '微信公众号自动运营系统';
    }
  };

    return (
    <Layout style={{ minHeight: '100vh' }}>
      {/* 侧边栏 */}
      <Sider
        trigger={null}
        collapsible
        collapsed={sidebarCollapsed}
        theme={theme}
        style={{
          position: 'fixed',
          height: '100vh',
          left: 0,
          top: 0,
          zIndex: 1000,
        }}
      >
        {/* Logo */}
        <div style={{
          height: '64px',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          borderBottom: '1px solid #f0f0f0',
          margin: '0 16px',
        }}>
          <div style={{
            fontSize: sidebarCollapsed ? '16px' : '18px',
            fontWeight: 'bold',
            color: theme === 'dark' ? '#fff' : '#1677ff',
            transition: 'all 0.3s',
          }}>
            {sidebarCollapsed ? 'WA' : '微信运营'}
          </div>
        </div>

        {/* 菜单 */}
        <Menu
          theme={theme}
          mode="inline"
          selectedKeys={[location.pathname]}
          items={menuItems}
          style={{ border: 'none' }}
          onClick={({ key }) => {
            window.history.pushState({}, '', key);
            window.dispatchEvent(new PopStateEvent('popstate'));
          }}
        />
      </Sider>

      {/* 主布局 */}
      <Layout style={{ marginLeft: sidebarCollapsed ? 80 : 200, transition: 'all 0.3s' }}>
        {/* 头部 */}
        <Header style={{
          padding: '0 24px',
          background: '#fff',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'space-between',
          borderBottom: '1px solid #f0f0f0',
          position: 'fixed',
          width: `calc(100% - ${sidebarCollapsed ? 80 : 200}px)`,
          zIndex: 999,
          transition: 'all 0.3s',
        }}>
          <div style={{ display: 'flex', alignItems: 'center' }}>
            <Button
                type="text"
              icon={sidebarCollapsed ? <MenuUnfoldOutlined /> : <MenuFoldOutlined />}
              onClick={() => setSidebarCollapsed(!sidebarCollapsed)}
              style={{ marginRight: '16px' }}
            />
            <h1 style={{ margin: 0, fontSize: '18px', fontWeight: '500' }}>
              {getPageTitle()}
            </h1>
        </div>

          <div style={{ display: 'flex', alignItems: 'center', gap: '16px' }}>
            {/* 主题切换 */}
            <Tooltip title={`切换到${theme === 'light' ? '暗色' : '亮色'}主题`}>
              <Button
                type="text"
                icon={<BulbOutlined />}
                onClick={toggleTheme}
              />
            </Tooltip>

            {/* 通知 */}
            <Tooltip title="通知">
              <Badge count={notificationCount} size="small">
                <Button type="text" icon={<BellOutlined />} />
              </Badge>
            </Tooltip>

            {/* 用户菜单 */}
            <Dropdown
              menu={{
                items: userMenuItems,
                onClick: handleMenuClick,
              }}
              placement="bottomRight"
            >
              <div style={{ 
                display: 'flex', 
                alignItems: 'center', 
                cursor: 'pointer',
                padding: '4px 8px',
                borderRadius: '6px',
                transition: 'background 0.3s'
              }}>
                <Avatar 
                  size="small" 
                  icon={<UserOutlined />} 
                  style={{ marginRight: '8px' }}
                />
                <span style={{ fontSize: '14px' }}>
                  {user?.username || '用户'}
                          </span>
              </div>
            </Dropdown>
          </div>
        </Header>

        {/* 内容区域 */}
        <Content style={{
          margin: '64px 0 0 0',
          minHeight: 'calc(100vh - 64px)',
          background: '#f5f5f5',
          overflow: 'auto',
        }}>
          <Routes>
            <Route path="/" element={<Navigate to="/dashboard" replace />} />
            <Route path="/dashboard" element={<Dashboard />} />
            <Route path="/articles" element={<ArticleManagement />} />
            <Route path="/schedule" element={<PublishSchedule />} />
            <Route path="/settings" element={<Settings />} />
            <Route path="*" element={<NotFound />} />
          </Routes>
        </Content>
      </Layout>
    </Layout>
  );
};

export default WeChatAutoPublisher;