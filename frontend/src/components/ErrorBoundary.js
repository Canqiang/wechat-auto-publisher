import React from 'react';
import { Result, Button } from 'antd';

class ErrorBoundary extends React.Component {
  constructor(props) {
    super(props);
    this.state = { 
      hasError: false, 
      error: null, 
      errorInfo: null 
    };
  }

  static getDerivedStateFromError(error) {
    // 更新 state 使下一次渲染能够显示降级后的 UI
    return { hasError: true };
  }

  componentDidCatch(error, errorInfo) {
    // 可以将错误日志上报给服务器
    console.error('Error caught by boundary:', error, errorInfo);
    
    this.setState({
      error: error,
      errorInfo: errorInfo
    });

    // 可以在这里上报错误到监控服务
    this.reportError(error, errorInfo);
  }

  reportError = (error, errorInfo) => {
    // 发送错误信息到后端或第三方监控服务
    const errorData = {
      message: error.message,
      stack: error.stack,
      componentStack: errorInfo.componentStack,
      timestamp: new Date().toISOString(),
      userAgent: navigator.userAgent,
      url: window.location.href
    };

    // 这里可以调用API发送错误信息
    console.log('Error reported:', errorData);
  };

  handleReload = () => {
    // 重新加载页面
    window.location.reload();
  };

  handleGoHome = () => {
    // 回到首页
    window.location.href = '/';
  };

  render() {
    if (this.state.hasError) {
      // 可以自定义降级后的 UI 并渲染
      return (
        <div style={{ 
          height: '100vh', 
          display: 'flex', 
          alignItems: 'center', 
          justifyContent: 'center',
          background: '#f5f5f5'
        }}>
          <Result
            status="500"
            title="500"
            subTitle="抱歉，系统出现了错误。"
            extra={
              <div style={{ textAlign: 'center' }}>
                <Button type="primary" onClick={this.handleReload} style={{ marginRight: 16 }}>
                  重新加载
                </Button>
                <Button onClick={this.handleGoHome}>
                  返回首页
                </Button>
              </div>
            }
          >
            {process.env.NODE_ENV === 'development' && this.state.error && (
              <div style={{ 
                textAlign: 'left', 
                background: '#f6f6f6', 
                padding: '16px', 
                borderRadius: '6px',
                marginTop: '24px',
                maxWidth: '600px',
                margin: '24px auto 0'
              }}>
                <h4>错误详情（开发环境）：</h4>
                <p style={{ color: '#ff4d4f', fontFamily: 'monospace', fontSize: '12px' }}>
                  {this.state.error.toString()}
                </p>
                <details style={{ marginTop: '16px' }}>
                  <summary style={{ cursor: 'pointer', fontWeight: 'bold' }}>
                    组件堆栈
                  </summary>
                  <pre style={{ 
                    fontSize: '11px', 
                    overflow: 'auto', 
                    background: '#fff', 
                    padding: '8px',
                    border: '1px solid #d9d9d9',
                    borderRadius: '4px',
                    marginTop: '8px'
                  }}>
                    {this.state.errorInfo.componentStack}
                  </pre>
                </details>
                <details style={{ marginTop: '8px' }}>
                  <summary style={{ cursor: 'pointer', fontWeight: 'bold' }}>
                    错误堆栈
                  </summary>
                  <pre style={{ 
                    fontSize: '11px', 
                    overflow: 'auto', 
                    background: '#fff', 
                    padding: '8px',
                    border: '1px solid #d9d9d9',
                    borderRadius: '4px',
                    marginTop: '8px'
                  }}>
                    {this.state.error.stack}
                  </pre>
                </details>
              </div>
            )}
          </Result>
        </div>
      );
    }

    return this.props.children;
  }
}

export default ErrorBoundary;
