import React, { useState, useEffect } from 'react';
import { 
  Calendar,
  Card, 
  Button, 
  Modal, 
  Form, 
  Input,
  Select, 
  DatePicker, 
  TimePicker,
  List,
  Tag,
  Space,
  Tooltip,
  Row,
  Col,
  Badge,
  message
} from 'antd';
import {
  PlusOutlined,
  EditOutlined,
  DeleteOutlined,
  ClockCircleOutlined,
  CalendarOutlined,
  ReloadOutlined
} from '@ant-design/icons';
import dayjs from 'dayjs';

const { Option } = Select;

const PublishSchedule = () => {
  const [schedules, setSchedules] = useState([]);
  const [articles, setArticles] = useState([]);
  const [modalVisible, setModalVisible] = useState(false);
  const [currentSchedule, setCurrentSchedule] = useState(null);
  const [selectedDate, setSelectedDate] = useState(dayjs());
  const [form] = Form.useForm();

  // 模拟数据
  useEffect(() => {
    loadData();
  }, []);

  const loadData = () => {
    // 模拟文章数据
    const mockArticles = [
      { id: 1, title: "AI技术改变未来生活的10种方式", status: "draft" },
      { id: 2, title: "2024年投资理财新趋势解析", status: "draft" },
      { id: 3, title: "健康饮食：地中海饮食法完全指南", status: "draft" },
      { id: 4, title: "远程工作时代的生产力提升秘诀", status: "draft" }
    ];

    // 模拟发布计划数据
    const mockSchedules = [
      {
        id: 1,
        articleId: 1,
        articleTitle: "AI技术改变未来生活的10种方式",
        scheduledTime: dayjs().add(1, 'day').hour(10).minute(0),
        status: "pending",
        repeat: "none",
        description: "重要技术分析文章"
      },
      {
        id: 2,
        articleId: 2,
        articleTitle: "2024年投资理财新趋势解析",
        scheduledTime: dayjs().add(2, 'days').hour(14).minute(30),
        status: "pending",
        repeat: "weekly",
        description: "每周投资分析"
      },
      {
        id: 3,
        articleId: 3,
        articleTitle: "健康饮食：地中海饮食法完全指南",
        scheduledTime: dayjs().add(3, 'days').hour(9).minute(0),
        status: "pending",
        repeat: "none",
        description: "健康生活系列"
      }
    ];

    setArticles(mockArticles);
    setSchedules(mockSchedules);
  };

  // 状态配置
  const statusConfig = {
    pending: { color: 'orange', text: '待发布' },
    published: { color: 'green', text: '已发布' },
    failed: { color: 'red', text: '发布失败' },
    cancelled: { color: 'default', text: '已取消' }
  };

  const repeatConfig = {
    none: '不重复',
    daily: '每天',
    weekly: '每周',
    monthly: '每月'
  };

  // 获取日期的发布计划
  const getDateSchedules = (date) => {
    return schedules.filter(schedule => 
      schedule.scheduledTime.format('YYYY-MM-DD') === date.format('YYYY-MM-DD')
    );
  };

  // 日历单元格渲染
  const dateCellRender = (date) => {
    const daySchedules = getDateSchedules(date);
    
    if (daySchedules.length === 0) return null;
    
    return (
      <div style={{ position: 'relative' }}>
        {daySchedules.slice(0, 2).map(schedule => (
          <div 
            key={schedule.id}
            style={{
              fontSize: '12px',
              padding: '2px 4px',
              margin: '1px 0',
              background: '#f0f2f5',
              borderRadius: '2px',
              overflow: 'hidden',
              textOverflow: 'ellipsis',
              whiteSpace: 'nowrap'
            }}
          >
            {schedule.scheduledTime.format('HH:mm')} {schedule.articleTitle.substring(0, 10)}...
          </div>
        ))}
        {daySchedules.length > 2 && (
          <div style={{ fontSize: '12px', color: '#999' }}>
            +{daySchedules.length - 2} 更多
          </div>
        )}
      </div>
    );
  };

  // 月视图单元格渲染
  const monthCellRender = (date) => {
    const monthSchedules = schedules.filter(schedule => 
      schedule.scheduledTime.format('YYYY-MM') === date.format('YYYY-MM')
    );
    
    if (monthSchedules.length === 0) return null;
    
    return (
      <div style={{ textAlign: 'center' }}>
        <Badge 
          count={monthSchedules.length} 
          style={{ backgroundColor: '#52c41a' }}
        />
      </div>
    );
  };

  // 处理函数
  const handleCreate = () => {
    setCurrentSchedule(null);
    setModalVisible(true);
    form.resetFields();
  };

  const handleEdit = (schedule) => {
    setCurrentSchedule(schedule);
    setModalVisible(true);
    form.setFieldsValue({
      articleId: schedule.articleId,
      scheduledDate: schedule.scheduledTime,
      scheduledTime: schedule.scheduledTime,
      repeat: schedule.repeat,
      description: schedule.description
    });
  };

  const handleDelete = (id) => {
    Modal.confirm({
      title: '确认删除',
      content: '确定要删除这个发布计划吗？',
      onOk: () => {
        setSchedules(schedules.filter(s => s.id !== id));
        message.success('删除成功');
      }
    });
  };

  const handleModalOk = async () => {
    try {
      const values = await form.validateFields();
      const article = articles.find(a => a.id === values.articleId);
      
      const scheduleData = {
        id: currentSchedule ? currentSchedule.id : Date.now(),
        articleId: values.articleId,
        articleTitle: article.title,
        scheduledTime: dayjs(values.scheduledDate)
          .hour(dayjs(values.scheduledTime).hour())
          .minute(dayjs(values.scheduledTime).minute()),
        status: 'pending',
        repeat: values.repeat,
        description: values.description || ''
      };

      if (currentSchedule) {
        setSchedules(schedules.map(s => 
          s.id === currentSchedule.id ? scheduleData : s
        ));
        message.success('更新成功');
      } else {
        setSchedules([...schedules, scheduleData]);
        message.success('创建成功');
      }

      setModalVisible(false);
    } catch (error) {
      console.error('Validation failed:', error);
    }
  };

  // 获取选中日期的计划
  const selectedDateSchedules = getDateSchedules(selectedDate);

  return (
    <div style={{ padding: '24px' }}>
      <Row gutter={16}>
        {/* 日历视图 */}
        <Col span={16}>
          <Card 
            title="发布日历"
            extra={
              <Space>
                <Button icon={<PlusOutlined />} type="primary" onClick={handleCreate}>
                  新建计划
                </Button>
                <Button icon={<ReloadOutlined />} onClick={loadData}>
                  刷新
                </Button>
              </Space>
            }
          >
            <Calendar
              value={selectedDate}
              onSelect={setSelectedDate}
              dateCellRender={dateCellRender}
              monthCellRender={monthCellRender}
            />
          </Card>
        </Col>

        {/* 当日计划列表 */}
        <Col span={8}>
          <Card 
            title={
              <Space>
                <CalendarOutlined />
                {selectedDate.format('YYYY年MM月DD日')}
              </Space>
            }
            extra={
              <Badge 
                count={selectedDateSchedules.length} 
                style={{ backgroundColor: '#52c41a' }}
              />
            }
          >
            {selectedDateSchedules.length > 0 ? (
              <List
                dataSource={selectedDateSchedules}
                renderItem={(item) => (
                  <List.Item
                    actions={[
                      <Tooltip title="编辑">
                        <Button 
                          type="text" 
                          icon={<EditOutlined />} 
                          onClick={() => handleEdit(item)}
                        />
                      </Tooltip>,
                      <Tooltip title="删除">
                        <Button 
                          type="text" 
                          danger 
                          icon={<DeleteOutlined />} 
                          onClick={() => handleDelete(item.id)}
                        />
                      </Tooltip>
                    ]}
                  >
                    <List.Item.Meta
                      avatar={<ClockCircleOutlined style={{ color: '#1677ff' }} />}
                      title={
                        <div>
                          <div style={{ fontWeight: 'bold', marginBottom: '4px' }}>
                            {item.scheduledTime.format('HH:mm')} - {item.articleTitle}
                          </div>
                          <Space>
                            <Tag color={statusConfig[item.status]?.color}>
                              {statusConfig[item.status]?.text}
                            </Tag>
                            {item.repeat !== 'none' && (
                              <Tag color="blue">
                                {repeatConfig[item.repeat]}
                              </Tag>
                            )}
                          </Space>
                        </div>
                      }
                      description={item.description}
                    />
                  </List.Item>
                )}
              />
            ) : (
              <div style={{ textAlign: 'center', padding: '40px 0', color: '#999' }}>
                <ClockCircleOutlined style={{ fontSize: '48px', marginBottom: '16px' }} />
                <div>当日暂无发布计划</div>
                <Button type="link" onClick={handleCreate}>
                  点击创建
                </Button>
              </div>
            )}
          </Card>

          {/* 统计信息 */}
          <Card title="计划统计" style={{ marginTop: '16px' }}>
            <Row gutter={16}>
              <Col span={12}>
                <div style={{ textAlign: 'center' }}>
                  <div style={{ fontSize: '24px', fontWeight: 'bold', color: '#1677ff' }}>
                    {schedules.filter(s => s.status === 'pending').length}
                  </div>
                  <div style={{ color: '#666' }}>待发布</div>
                </div>
              </Col>
              <Col span={12}>
                <div style={{ textAlign: 'center' }}>
                  <div style={{ fontSize: '24px', fontWeight: 'bold', color: '#52c41a' }}>
                    {schedules.filter(s => s.status === 'published').length}
                  </div>
                  <div style={{ color: '#666' }}>已完成</div>
                </div>
              </Col>
            </Row>
          </Card>
        </Col>
      </Row>

      {/* 创建/编辑弹窗 */}
      <Modal
        title={currentSchedule ? '编辑发布计划' : '新建发布计划'}
        open={modalVisible}
        onOk={handleModalOk}
        onCancel={() => setModalVisible(false)}
        width={600}
      >
        <Form form={form} layout="vertical">
          <Form.Item
            name="articleId"
            label="选择文章"
            rules={[{ required: true, message: '请选择要发布的文章' }]}
          >
            <Select placeholder="请选择文章">
              {articles.map(article => (
                <Option key={article.id} value={article.id}>
                  {article.title}
                </Option>
              ))}
            </Select>
          </Form.Item>

          <Row gutter={16}>
            <Col span={12}>
              <Form.Item
                name="scheduledDate"
                label="发布日期"
                rules={[{ required: true, message: '请选择发布日期' }]}
              >
                <DatePicker 
                  style={{ width: '100%' }}
                  disabledDate={(current) => current && current < dayjs().startOf('day')}
                />
              </Form.Item>
            </Col>
            <Col span={12}>
              <Form.Item
                name="scheduledTime"
                label="发布时间"
                rules={[{ required: true, message: '请选择发布时间' }]}
              >
                <TimePicker 
                  style={{ width: '100%' }}
                  format="HH:mm"
                />
              </Form.Item>
            </Col>
          </Row>

          <Form.Item
            name="repeat"
            label="重复频率"
            initialValue="none"
          >
            <Select>
              <Option value="none">不重复</Option>
              <Option value="daily">每天</Option>
              <Option value="weekly">每周</Option>
              <Option value="monthly">每月</Option>
            </Select>
          </Form.Item>

          <Form.Item
            name="description"
            label="备注说明"
          >
            <Input.TextArea 
              rows={3} 
              placeholder="可选择添加备注说明"
              maxLength={200}
              showCount
            />
          </Form.Item>
        </Form>
      </Modal>
    </div>
  );
};

export default PublishSchedule;
