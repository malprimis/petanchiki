import { useState } from 'react';
import { useNavigate, useParams, Link } from 'react-router-dom';
import type { FormEvent } from 'react';
import Header from '../../components/Header';
import Breadcrumbs from '../../components/Breadcrumbs';

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
    <div className="page-container">
      {/* Верхнее меню */}
      <header className="page-header">
        <div className="header-container">
          <button onClick={handleGoBack} className="back-button">
            ← {/* Символ стрелки */}
          </button>
          
        
          <nav className="main-nav">
            {navItems.map((item) => (
              <Link
                key={item.path}
                to={item.path}
                className="nav-link"
              >
                {item.name}
              </Link>
            ))}
          </nav>

          <div className="auth-buttons">
            <button className="login-btn">Вход</button>
            <button className="register-btn">Регистрация</button>
          </div>
        </div>
      </header>
     
      <Header />
      <Breadcrumbs />
       
      <div className="form-container">
        <h1>Добавить транзакцию</h1>

        <div className="category-management">
          <h2>Добавить категорию</h2>
          <div className="category-input">
            <input
              type="text"
              value={newCategory}
              onChange={(e) => setNewCategory(e.target.value)}
              placeholder="Новая категория"
            />
            <button onClick={handleAddCategory} type="button">
              Добавить
            </button>
          </div>
        </div>

        <form onSubmit={handleSubmit}>
          <div className="form-group">
            <label>Категория</label>
            <select
              value={category}
              onChange={(e) => setCategory(e.target.value)}
              className={errors.category ? 'error' : ''}
            >
              <option value="">Выберите категорию</option>
              {categories.map((cat, index) => (
                <option key={index} value={cat}>{cat}</option>
              ))}
            </select>
            {errors.category && <span className="error-message">{errors.category}</span>}
          </div>

          <div className="form-group">
            <label>Сумма (₽)</label>
            <input
              type="number"
              value={amount}
              onChange={(e) => setAmount(e.target.value)}
              className={errors.amount ? 'error' : ''}
              placeholder="500"
              min="0"
              step="0.01"
            />
            {errors.amount && <span className="error-message">{errors.amount}</span>}
          </div>

          <div className="form-group">
            <label>Описание</label>
            <textarea
              value={description}
              onChange={(e) => setDescription(e.target.value)}
              rows={3}
              className={errors.description ? 'error' : ''}
              placeholder="Детали транзакции..."
            />
            {errors.description && <span className="error-message">{errors.description}</span>}
          </div>

          <div className="form-actions">
            <button
              type="button"
              onClick={() => groupId ? navigate(`/group/${groupId}`) : navigate('/')}
              className="cancel-btn"
            >
              Отмена
            </button>
            <button type="submit" className="submit-btn">
              Сохранить
            </button>
          </div>
        </form>
      </div>

      <style jsx>{`
        .page-container {
          min-height: 100vh;
          min-width: 208vh; 
          background: #f8fafc;
        }

        /* Стили для верхнего меню */
        .page-header {
          background: rgba(255, 255, 255, 0.9);
          backdrop-filter: blur(12px);
          position: sticky;
          top: 0;
          z-index: 40;
          border-bottom: 1px solid #e5e7eb;
          box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
        }

        .header-container {
          max-width: 1200px;
          margin: 0 auto;
          padding: 0.75rem 1rem;
          display: flex;
          align-items: center;
          justify-content: space-between;
        }

        /* Стили для кнопки назад */
        .back-button {
          background: none;
          border: none;
          cursor: pointer;
          padding: 0.5rem;
          margin-right: 1rem;
          color: #4b5563;
          transition: color 0.2s;
          font-size: 1.5rem;
          line-height: 1;
        }

        .back-button:hover {
          color: #059669;
        }

        .logo-link {
          display: flex;
          align-items: center;
          text-decoration: none;
        }

        .logo {
          font-size: 1.5rem;
          font-weight: 700;
          color: #059669;
        }

        .main-nav {
          display: flex;
          gap: 1rem;
        }

        .nav-link {
          padding: 0.5rem 1rem;
          font-size: 1rem;
          font-weight: 500;
          color: #4b5563;
          text-decoration: none;
          transition: color 0.2s;
        }

        .nav-link:hover {
          color: #059669;
        }

        .auth-buttons {
          display: flex;
          gap: 0.75rem;
        }

        .login-btn {
          padding: 0.5rem 1rem;
          background: transparent;
          border: none;
          color: #4b5563;
          font-weight: 500;
          cursor: pointer;
        }

        .login-btn:hover {
          color: #111827;
        }

        .register-btn {
          padding: 0.5rem 1rem;
          background: linear-gradient(to right, #10b981, #059669);
          color: white;
          border: none;
          border-radius: 0.375rem;
          font-weight: 500;
          cursor: pointer;
          box-shadow: 0 1px 2px rgba(0, 0, 0, 0.1);
        }

        .register-btn:hover {
          background: linear-gradient(to right, #0ea472, #047857);
          box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        }

        /* Стили для формы */
        .form-container {
          max-width: 28rem;
          margin: 2rem auto;
          padding: 2rem;
          background: white;
          border-radius: 0.5rem;
          box-shadow: 0 1px 3px rgba(0,0,0,0.1);
        }

        .form-container h1 {
          font-size: 1.5rem;
          font-weight: 600;
          color: #1e293b;
          text-align: center;
          margin-bottom: 1.5rem;
        }

        .category-management {
          background: #f1f5f9;
          padding: 1rem;
          border-radius: 0.375rem;
          margin-bottom: 1.5rem;
          border: 1px solid #e2e8f0;
        }

        .category-management h2 {
          font-size: 1rem;
          font-weight: 500;
          color: #334155;
          margin-bottom: 0.5rem;
        }

        .category-input {
          display: flex;
          gap: 0.5rem;
        }

        .category-input input {
          flex: 1;
          padding: 0.5rem;
          border: 1px solid #cbd5e1;
          border-radius: 0.25rem;
          font-size: 1rem;
        }

        .category-input button {
          background: #2563eb;
          color: white;
          border: none;
          padding: 0.5rem 1rem;
          border-radius: 0.25rem;
          cursor: pointer;
          transition: background 0.2s;
        }

        .category-input button:hover {
          background: #1d4ed8;
        }

        .form-group {
          margin-bottom: 1rem;
        }

        .form-group label {
          display: block;
          font-size: 0.875rem;
          font-weight: 500;
          color: #334155;
          margin-bottom: 0.25rem;
        }

        .form-group select,
        .form-group input,
        .form-group textarea {
          width: 100%;
          padding: 0.5rem;
          border: 1px solid #cbd5e1;
          border-radius: 0.25rem;
          font-size: 1rem;
        }

        .form-group textarea {
          min-height: 6rem;
        }

        .error {
          border-color: #dc2626;
        }

        .error-message {
          display: block;
          font-size: 0.75rem;
          color: #dc2626;
          margin-top: 0.25rem;
        }

        .form-actions {
          display: flex;
          justify-content: flex-end;
          gap: 0.75rem;
          margin-top: 1.5rem;
          padding-top: 1rem;
          border-top: 1px solid #e2e8f0;
        }

        .cancel-btn {
          padding: 0.5rem 1rem;
          border: 1px solid #cbd5e1;
          background: white;
          color: #334155;
          border-radius: 0.25rem;
          cursor: pointer;
          transition: background 0.2s;
        }

        .cancel-btn:hover {
          background: #f1f5f9;
        }

        .submit-btn {
          padding: 0.5rem 1rem;
          background: #2563eb;
          color: white;
          border: none;
          border-radius: 0.25rem;
          cursor: pointer;
          transition: background 0.2s;
        }

        .submit-btn:hover {
          background: #1d4ed8;
        }
      `}</style>
    </div>
  );
}