import { RegisterForm } from '../../components/RegisterForm';
import { Link } from 'react-router-dom';
import { Card, Typography, Divider, Space } from 'antd';
import { UserAddOutlined } from '@ant-design/icons';

const { Title, Text } = Typography;

export const RegisterPage = () => {
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
          display: 'flex',
          flexDirection: 'column',
          gap: '24px',
          alignItems: 'center',
          textAlign: 'center',
          backgroundColor: '#ffffff'
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
          <UserAddOutlined />
        </div>

        {/* Заголовок */}
        <Title level={3} style={{ margin: 0 }}>
          Регистрация
        </Title>

        {/* Подзаголовок */}
        <Text type="secondary" style={{ marginBottom: '50px' }}>
          Заполните форму для создания аккаунта
        </Text>

        {/* Форма */}
        <div className="w-full">
          <RegisterForm />
        </div>

        {/* Разделитель */}
        <Divider style={{ margin: '24px 0' }} />

        {/* Ссылки */}
        <Space direction="vertical" size="middle" className="w-full">
          <Text>
            Уже есть аккаунт?{' '}
            <Link 
              to="/login" 
              className="text-blue-600 hover:text-blue-700 font-medium transition-colors duration-200"
            >
              Войти
            </Link>
          </Text>
          
          <Text type="secondary">
            <Link 
              to="/" 
              className="hover:text-gray-800 transition-colors duration-200"
            >
              Вернуться на главную
            </Link>
          </Text>
        </Space>
      </Card>
    </div>
  );
};