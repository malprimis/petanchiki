import { useState } from 'react';
import { useNavigate, useParams, Link } from 'react-router-dom';
import type { FormEvent } from 'react';
import Header from '../../components/Header';
import Breadcrumbs from '../../components/Breadcrumbs';
import styled from 'styled-components';

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

const FormContainer = styled.div`
  max-width: 28rem;
  margin: 2rem auto;
  padding: 2rem;
  background: white;
  border-radius: 0.5rem;
  box-shadow: 0 1px 3px rgba(0,0,0,0.1);

  h1 {
    font-size: 1.5rem;
    font-weight: 600;
    color: #1e293b;
    text-align: center;
    margin-bottom: 1.5rem;
  }
`;

const CategoryManagement = styled.div`
  background: #f1f5f9;
  padding: 1rem;
  border-radius: 0.375rem;
  margin-bottom: 1.5rem;
  border: 1px solid #e2e8f0;

  h2 {
    font-size: 1rem;
    font-weight: 500;
    color: #334155;
    margin-bottom: 0.5rem;
  }
`;

const CategoryInput = styled.div`
  display: flex;
  gap: 0.5rem;

  input {
    flex: 1;
    padding: 0.5rem;
    border: 1px solid #cbd5e1;
    border-radius: 0.25rem;
    font-size: 1rem;
  }

  button {
    background: #2563eb;
    color: white;
    border: none;
    padding: 0.5rem 1rem;
    border-radius: 0.25rem;
    cursor: pointer;
    transition: background 0.2s;

    &:hover {
      background: #1d4ed8;
    }
  }
`;

const FormGroup = styled.div`
  margin-bottom: 1rem;

  label {
    display: block;
    font-size: 0.875rem;
    font-weight: 500;
    color: #334155;
    margin-bottom: 0.25rem;
  }

  select,
  input,
  textarea {
    width: 100%;
    padding: 0.5rem;
    border: 1px solid #cbd5e1;
    border-radius: 0.25rem;
    font-size: 1rem;
  }

  textarea {
    min-height: 6rem;
  }

  &.error input,
  &.error select,
  &.error textarea {
    border-color: #dc2626;
  }
`;

const ErrorMessage = styled.span`
  display: block;
  font-size: 0.75rem;
  color: #dc2626;
  margin-top: 0.25rem;
`;

const FormActions = styled.div`
  display: flex;
  justify-content: flex-end;
  gap: 0.75rem;
  margin-top: 1.5rem;
  padding-top: 1rem;
  border-top: 1px solid #e2e8f0;
`;

const CancelBtn = styled.button`
  padding: 0.5rem 1rem;
  border: 1px solid #cbd5e1;
  background: white;
  color: #334155;
  border-radius: 0.25rem;
  cursor: pointer;
  transition: background 0.2s;

  &:hover {
    background: #f1f5f9;
  }
`;

const SubmitBtn = styled.button`
  padding: 0.5rem 1rem;
  background: #2563eb;
  color: white;
  border: none;
  border-radius: 0.25rem;
  cursor: pointer;
  transition: background 0.2s;

  &:hover {
    background: #1d4ed8;
  }
`;

export default function AddTransactionPage() {
  const { id: groupId } = useParams();
  const navigate = useNavigate();
  const [category, setCategory] = useState('');
  const [amount, setAmount] = useState('');
  const [description, setDescription] = useState('');
  const [date] = useState(new Date().toISOString().split('T')[0]);
  const [errors, setErrors] = useState({
    category: '',
    amount: '',
    description: ''
  });
  const [categories, setCategories] = useState<string[]>(['Другое']);
  const [newCategory, setNewCategory] = useState('');

  // Навигационное меню
  const navItems = [
    { path: '/home', name: 'Главная' },
    { path: '/who', name: 'Отчеты' },
    { path: '/features', name: 'Группы' },
  ];

  // Функция для возврата назад
  const handleGoBack = () => {
    navigate(-1); // Возврат на предыдущую страницу в истории
  };

  const validateForm = () => {
    let isValid = true;
    const newErrors = {
      category: '',
      amount: '',
      description: ''
    };

    if (!category) {
      newErrors.category = 'Выберите категорию';
      isValid = false;
    }

    if (!amount || isNaN(Number(amount)) || Number(amount) <= 0) {
      newErrors.amount = 'Введите корректную сумму';
      isValid = false;
    }

    if (!description.trim()) {
      newErrors.description = 'Введите описание';
      isValid = false;
    }

    setErrors(newErrors);
    return isValid;
  };

  const handleSubmit = (e: FormEvent<HTMLFormElement>) => {
    e.preventDefault();

    if (validateForm()) {
      console.log('Данные для сохранения:', {
        category,
        amount: Number(amount),
        description,
        date,
        groupId: groupId ? Number(groupId) : 0
      });

      if (groupId) {
        navigate(`/group/${groupId}`);
      }
    }
  };

  const handleAddCategory = () => {
    const trimmed = newCategory.trim();
    if (trimmed && !categories.includes(trimmed)) {
      setCategories([...categories, trimmed]);
      setNewCategory('');
    }
  };

  return (
    <PageContainer>
      {/* Верхнее меню */}
      <PageHeader>
        <HeaderContainer>
          <BackButton onClick={handleGoBack}>
            ← {/* Символ стрелки */}
          </BackButton>
          
          <MainNav>
            {navItems.map((item) => (
              <NavLink
                key={item.path}
                to={item.path}
              >
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
     
      <Header />
      <Breadcrumbs />
       
      <FormContainer>
        <h1>Добавить транзакцию</h1>

        <CategoryManagement>
          <h2>Добавить категорию</h2>
          <CategoryInput>
            <input
              type="text"
              value={newCategory}
              onChange={(e) => setNewCategory(e.target.value)}
              placeholder="Новая категория"
            />
            <button onClick={handleAddCategory} type="button">
              Добавить
            </button>
          </CategoryInput>
        </CategoryManagement>

        <form onSubmit={handleSubmit}>
          <FormGroup className={errors.category ? 'error' : ''}>
            <label>Категория</label>
            <select
              value={category}
              onChange={(e) => setCategory(e.target.value)}
            >
              <option value="">Выберите категорию</option>
              {categories.map((cat, index) => (
                <option key={index} value={cat}>{cat}</option>
              ))}
            </select>
            {errors.category && <ErrorMessage>{errors.category}</ErrorMessage>}
          </FormGroup>

          <FormGroup className={errors.amount ? 'error' : ''}>
            <label>Сумма (₽)</label>
            <input
              type="number"
              value={amount}
              onChange={(e) => setAmount(e.target.value)}
              placeholder="500"
              min="0"
              step="0.01"
            />
            {errors.amount && <ErrorMessage>{errors.amount}</ErrorMessage>}
          </FormGroup>

          <FormGroup className={errors.description ? 'error' : ''}>
            <label>Описание</label>
            <textarea
              value={description}
              onChange={(e) => setDescription(e.target.value)}
              rows={3}
              placeholder="Детали транзакции..."
            />
            {errors.description && <ErrorMessage>{errors.description}</ErrorMessage>}
          </FormGroup>

          <FormActions>
            <CancelBtn
              type="button"
              onClick={() => groupId ? navigate(`/group/${groupId}`) : navigate('/')}
            >
              Отмена
            </CancelBtn>
            <SubmitBtn type="submit">
              Сохранить
            </SubmitBtn>
          </FormActions>
        </form>
      </FormContainer>
    </PageContainer>
  );
}