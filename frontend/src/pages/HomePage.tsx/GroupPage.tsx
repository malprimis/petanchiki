import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import styled from 'styled-components';
import { createNewGroup } from '../../api/group';


const PageContainer = styled.div`
  min-height: 100vh;
  min-width: 208vh;
  background: #f8fafc;
`;

const PageHeader = styled.header`
  background: rgba(255, 255, 255, 0.9);
  backdrop-filter: blur(12px);
  position: sticky;
  top: 0;
  z-index: 40;
  border-bottom: 1px solid #e5e7eb;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
`;

const HeaderContainer = styled.div`
  max-width: 1200px;
  margin: 0 auto;
  padding: 0.75rem 1rem;
  display: flex;
  align-items: center;
  justify-content: space-between;
`;

const BackButton = styled.button`
  background: none;
  border: none;
  cursor: pointer;
  padding: 0.5rem;
  margin-right: 1rem;
  color: #4b5563;
  transition: color 0.2s;
  font-size: 1.5rem;
  line-height: 1;

  &:hover {
    color: #059669;
  }
`;

const AuthButtons = styled.div`
  display: flex;
  gap: 0.75rem;
`;

const LoginBtn = styled.button`
  padding: 0.5rem 1rem;
  background: transparent;
  border: none;
  color: #4b5563;
  font-weight: 500;
  cursor: pointer;

  &:hover {
    color: #111827;
  }
`;

const RegisterBtn = styled.button`
  padding: 0.5rem 1rem;
  background: linear-gradient(to right, #10b981, #059669);
  color: white;
  border: none;
  border-radius: 0.375rem;
  font-weight: 500;
  cursor: pointer;
  box-shadow: 0 1px 2px rgba(0, 0, 0, 0.1);

  &:hover {
    background: linear-gradient(to right, #0ea472, #047857);
    box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
  }
`;

const GroupContent = styled.div`
  max-width: 1200px;
  margin: 0 auto;
  padding: 1rem;
`;

const Header = styled.div`
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 2rem;
  padding-bottom: 1rem;
  border-bottom: 1px solid #e2e8f0;

  h1 {
    font-size: 2rem;
    font-weight: 700;
    color: #1e293b;
  }
`;

const Section = styled.div`
  margin-bottom: 2rem;
  background: white;
  padding: 1.5rem;
  border-radius: 0.5rem;
  box-shadow: 0 1px 3px rgba(0,0,0,0.1);

  h2 {
    font-size: 1.5rem;
    font-weight: 600;
    margin-bottom: 1rem;
    color: #1e293b;
  }
`;

const SubmitBtn = styled.button`
  display: block;
  width: 100%;
  padding: 1rem;
  background: #059669;
  color: white;
  border: none;
  border-radius: 0.5rem;
  font-size: 1.1rem;
  font-weight: 500;
  cursor: pointer;
  transition: background 0.2s;
  margin-top: 2rem;

  &:hover {
    background: #047857;
  }

  &:disabled {
    background: #9ca3af;
    cursor: not-allowed;
  }
`;

export default function CreateGroupPage() {
  const navigate = useNavigate();

  // Функция для возврата назад
  const handleGoBack = () => {
    navigate(-1);
  };

  // Состояние формы
  const [name, setName] = useState('');
  const [description, setDescription] = useState('')

  // Функция отправки формы
  const handleSubmit = async () => {
    if (!name.trim()) {
      alert('Пожалуйста, введите название группы');
      return;
    }
    if (!name.trim()) {
      alert('Пожалуйста, введите описание группы');
      return;
    }

    // Генерируем ID группы
    const response = await createNewGroup(name, description)
    console.log(response);
    
    // Сохраняем группу в localStorage
    
    // localStorage.setItem('groups', JSON.stringify(updatedGroups));
    // navigate(`/group/${groupId}`);
  };

  return (
    <PageContainer>
      <PageHeader>
        <HeaderContainer>
          <BackButton onClick={handleGoBack}>←</BackButton>
          <AuthButtons>
            <LoginBtn>Вход</LoginBtn>
            <RegisterBtn>Регистрация</RegisterBtn>
          </AuthButtons>
        </HeaderContainer>
      </PageHeader>

      <GroupContent>
        <Header>
          <h1>Создание новой группы</h1>
        </Header>

        <Section>
          <label>Название группы</label>
          <input
            type="text"
            placeholder="Например: Путешествие в Сочи"
            value={name}
            onChange={(e) => setName(e.target.value)}
          />
        </Section>

        <Section>
          <label>Описание</label>
          <input
            type="text"
            placeholder="Иван@gmail.com, Мария@mail.ru, Алексей@yandex.ru"
            value={description}
            onChange={(e) => setDescription(e.target.value)}
          />
        </Section>

        
        <SubmitBtn
          onClick={handleSubmit}
          disabled={!name.trim()}
        >
          Создать группу
        </SubmitBtn>
      </GroupContent>
    </PageContainer>
  );
}