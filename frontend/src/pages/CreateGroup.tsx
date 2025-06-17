import { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import styled from 'styled-components';

interface Transaction {
  id: number;
  date: string;
  category: string;
  amount: number;
  member: string;
}

interface Group {
  id: number;
  name: string;
  balance: number;
  members: string[];
  transactions: Transaction[];
  color: string;
}

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

const MainNav = styled.nav`
  display: flex;
  gap: 1rem;
`;

const NavLink = styled(Link)`
  padding: 0.5rem 1rem;
  font-size: 1rem;
  font-weight: 500;
  color: #4b5563;
  text-decoration: none;
  transition: color 0.2s;

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
  padding: 2rem;
`;

const Header = styled.div`
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

  label {
    display: block;
    font-size: 1rem;
    font-weight: 500;
    margin-bottom: 0.5rem;
    color: #334155;
  }

  input {
    width: 100%;
    padding: 0.75rem 1rem;
    border: 1px solid #cbd5e1;
    border-radius: 0.375rem;
    font-size: 1rem;
    margin-bottom: 1rem;

    &:focus {
      outline: none;
      border-color: #059669;
      box-shadow: 0 0 0 2px rgba(5, 150, 105, 0.2);
    }
  }
`;

const TransactionsHeader = styled.div`
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1rem;

  h2 {
    font-size: 1.25rem;
    font-weight: 600;
    color: #1e293b;
  }
`;

const AddTransactionBtn = styled.button`
  background: #2563eb;
  color: white;
  border: none;
  padding: 0.5rem 1rem;
  border-radius: 0.375rem;
  cursor: pointer;
  transition: background 0.2s;

  &:hover {
    background: #1d4ed8;
  }
`;

const TransactionFields = styled.div`
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 1rem;
  margin-bottom: 1rem;

  input {
    padding: 0.5rem 1rem;
    border: 1px solid #cbd5e1;
    border-radius: 0.375rem;
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

  // Навигационное меню
  const navItems = [
    { path: '/home', name: 'Главная' },
    { path: '/who', name: 'Отчеты' },
    { path: '/features', name: 'Группы' },
  ];

  // Функция для возврата назад
  const handleGoBack = () => {
    navigate(-1);
  };

  // Состояние формы
  const [name, setName] = useState('');
  const [members, setMembers] = useState('');
  const [balance, setBalance] = useState(0);
  const [transactions, setTransactions] = useState<Transaction[]>([]);
  const [transactionCount, setTransactionCount] = useState(0);

  // Добавление поля транзакции
  const addTransactionField = () => {
    const newId = transactions.length + 1;
    const newTransaction: Transaction = {
      id: newId,
      date: '',
      category: '',
      amount: 0,
      member: ''
    };
    setTransactions([...transactions, newTransaction]);
    setTransactionCount(transactionCount + 1);
  };

  // Обработчики изменения полей транзакций
  const handleTransactionChange = (
    index: number,
    field: keyof Transaction,
    value: string | number
  ) => {
    const updated = [...transactions];
    updated[index][field] = value as never;
    setTransactions(updated);
  };

  // Цвета для групп
  const colors = ['group-color-1', 'group-color-2', 'group-color-3', 'group-color-4', 'group-color-5'];

  const handleSubmit = () => {
    if (!name.trim()) {
      alert('Пожалуйста, введите название группы');
      return;
    }

    const groupId = Date.now();

    const newGroup: Group = {
      id: groupId,
      name,
      balance: balance || 0,
      members: members.split(',')
        .map(m => m.trim())
        .filter(m => m.length > 0),
      transactions: transactions.map(t => ({
        ...t,
        id: Date.now() + Math.floor(Math.random() * 1000)
      })),
      color: colors[Math.floor(Math.random() * colors.length)]
    };

    try {
      const existingGroups = JSON.parse(localStorage.getItem('groups') || '[]');
      const updatedGroups = [...existingGroups, newGroup];
      localStorage.setItem('groups', JSON.stringify(updatedGroups));
      
      // Перенаправляем на страницу GroupNew с ID новой группы
      navigate(`/group/${groupId}`);
      
    } catch (error) {
      console.error('Ошибка сохранения группы:', error);
      alert('Произошла ошибка при создании группы');
    }
  };

  return (
    <PageContainer>
      <PageHeader>
        <HeaderContainer>
          <BackButton onClick={handleGoBack}>←</BackButton>
          <MainNav>
            {navItems.map((item) => (
              <NavLink key={item.path} to={item.path}>
                {item.name}
              </NavLink>
            ))}
          </MainNav>
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
          <label>Участники (через запятую)</label>
          <input
            type="text"
            placeholder="Иван, Мария, Алексей"
            value={members}
            onChange={(e) => setMembers(e.target.value)}
          />
        </Section>

        <Section>
          <label>Начальный баланс</label>
          <input
            type="number"
            value={balance}
            onChange={(e) => setBalance(Number(e.target.value))}
          />
        </Section>

        <Section>
          <TransactionsHeader>
            <h2>Транзакции (необязательно)</h2>
            <AddTransactionBtn onClick={addTransactionField}>
              Добавить транзакцию
            </AddTransactionBtn>
          </TransactionsHeader>

          {transactions.map((t, idx) => (
            <TransactionFields key={idx}>
              <input
                type="date"
                value={t.date}
                onChange={(e) => handleTransactionChange(idx, 'date', e.target.value)}
              />
              <input
                type="text"
                placeholder="Категория"
                value={t.category}
                onChange={(e) => handleTransactionChange(idx, 'category', e.target.value)}
              />
              <input
                type="number"
                placeholder="Сумма"
                value={t.amount}
                onChange={(e) => handleTransactionChange(idx, 'amount', Number(e.target.value))}
              />
              <input
                type="text"
                placeholder="Участник"
                value={t.member}
                onChange={(e) => handleTransactionChange(idx, 'member', e.target.value)}
              />
            </TransactionFields>
          ))}
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