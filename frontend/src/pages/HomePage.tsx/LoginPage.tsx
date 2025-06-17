import styled from 'styled-components';
import { LoginForm } from '../../components/LoginForm';
import { Link } from 'react-router-dom';
import { Card, Typography, Divider, Space } from 'antd';
import { UserOutlined } from '@ant-design/icons';

const { Title, Text } = Typography;

// Styled components
const PageWrapper = styled.div`
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 1.5rem;
  background: linear-gradient(135deg, #f5f7fa 0%, #e4e8eb 100%);
`;

const StyledCard = styled(Card)`
  border-radius: 16px !important;
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.1) !important;
  padding: 48px 40px !important;
  margin: 95px auto 90px auto;
  display: flex;
  flex-direction: column;
  gap: 24px;
  align-items: center;
  text-align: center;
  background-color: #ffffff !important;
  max-width: 400px;
  width: 100%;
`;

const AvatarCircle = styled.div`
  width: 80px;
  height: 80px;
  border-radius: 50%;
  margin: 10px auto;
  background-color: #1890ff;
  color: white;
  box-shadow: 0 6px 16px rgba(24, 144, 255, 0.4);
  font-size: 36px;
  display: flex;
  align-items: center;
  justify-content: center;
`;

const FullWidth = styled.div`
  width: 100%;
`;

const StyledLink = styled(Link)`
  color: #2563eb;
  font-weight: 500;
  transition: color 0.2s;

  &:hover {
    color: #1d4ed8;
  }
`;

export const LoginPage = () => {
  return (
    <PageWrapper>
      <StyledCard>
        {/* Аватар/иконка */}
        <AvatarCircle>
          <UserOutlined />
        </AvatarCircle>

        {/* Заголовок */}
        <Title level={3} style={{ margin: 0 }}>
          Вход в систему
        </Title>

        {/* Подзаголовок */}
        <Text type="secondary" style={{ marginBottom: '50px' }}>
          Введите email и пароль
        </Text>

        {/* Форма */}
        <FullWidth>
          <LoginForm />
        </FullWidth>

        {/* Разделитель */}
        <Divider style={{ margin: '24px 0' }} />

        {/* Ссылки */}
        <Space direction="vertical" size="middle" style={{ width: '100%' }}>
          <Text>
            Нет аккаунта?{' '}
            <StyledLink to="/register">
              Создать аккаунт
            </StyledLink>
          </Text>
          <Text type="secondary">
            <StyledLink to="/forgot-password">
              Забыли пароль?
            </StyledLink>
          </Text>
        </Space>
      </StyledCard>
    </PageWrapper>
  );
};