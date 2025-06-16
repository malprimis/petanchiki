import { LoginForm } from '../../components/LoginForm';
import { Link } from 'react-router-dom';
import { Card, Typography, Divider, Space } from 'antd';
import { UserOutlined } from '@ant-design/icons';

const { Title, Text } = Typography;

export const LoginPage = () => {
  return (
    <div 
      className="min-h-screen flex items-center justify-center p-6"
      style={{ 
        background: 'linear-gradient(135deg, #f5f7fa 0%, #e4e8eb 100%)',
        display: 'flex', 
        alignItems: 'center', 
        justifyContent: 'center', 
      }}
    >
      <Card 
        className="w-full max-w-md mx-auto shadow-lg"
        style={{ 
          borderRadius: '16px',
          boxShadow: '0 8px 24px rgba(0, 0, 0, 0.1)',
          padding: '48px 40px',
          margin: '95px 595px 90px 595px',
          display: 'center',
          flexDirection: 'column',
          gap: '24px',
          alignItems: 'center',
          textAlign: 'center',
          backgroundColor: '#ffffff' // Белый фон для карточки
        }}
      >
        {/* Аватар/иконка */}
        <div 
          className="flex items-center justify-center"
          style={{
            width: '80px',
            height: '80px',
            borderRadius: '50%',
            margin: '10px 70px 10px 70px',
            backgroundColor: '#1890ff',
            color: 'white',
            boxShadow: '0 6px 16px rgba(24, 144, 255, 0.4)',
            fontSize: '36px'
          }}
        >
          <UserOutlined />
        </div>

        {/* Заголовок */}
        <Title level={3} style={{ margin: 0 }}>
          Вход в систему
        </Title>

        {/* Подзаголовок */}
        <Text type="secondary" style={{ marginBottom: '50px' }}>
          Введите email и пароль
        </Text>

        {/* Форма */}
        <div className="w-full">
          <LoginForm />
        </div>

        {/* Разделитель */}
        <Divider style={{ margin: '24px 0' }} />

        {/* Ссылки */}
        <Space direction="vertical" size="middle" className="w-full">
          <Text>
            Нет аккаунта?{' '}
            <Link 
              to="/register" 
              className="text-blue-600 hover:text-blue-700 font-medium transition-colors duration-200"
            >
              Создать аккаунт
            </Link>
          </Text>
          
          <Text type="secondary">
            <Link 
              to="/forgot-password" 
              className="hover:text-gray-800 transition-colors duration-200"
            >
              Забыли пароль?
            </Link>
          </Text>
        </Space>
      </Card>
    </div>
  );
};