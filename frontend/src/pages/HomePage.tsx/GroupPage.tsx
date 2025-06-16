import { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';

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
    updated[index][field] = value as any;
    setTransactions(updated);
  };

  // Цвета для групп
  const colors = ['group-color-1', 'group-color-2', 'group-color-3', 'group-color-4', 'group-color-5'];

  // Функция отправки формы
  const handleSubmit = () => {
    if (!name.trim()) {
      alert('Пожалуйста, введите название группы');
      return;
    }

    // Генерируем ID группы
    const groupId = Date.now();

    const newGroup: Group = {
      id: groupId,
      name,
      balance,
      members: members.split(',').map((m) => m.trim()).filter(Boolean),
      transactions: transactions.map(t => ({
        ...t,
        id: Date.now() + Math.floor(Math.random() * 1000) // Уникальный ID для транзакции
      })),
      color: colors[Math.floor(Math.random() * colors.length)]
    };

    // Сохраняем группу в localStorage
    const existingGroups = JSON.parse(localStorage.getItem('groups') || '[]');
    const updatedGroups = [...existingGroups, newGroup];
    localStorage.setItem('groups', JSON.stringify(updatedGroups));

    // Перенаправляем на страницу группы
    navigate(`/group/${groupId}`);
  };

  // ... остальной код (return и стили остаются без изменений)
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

      <div className="group-content">
        <div className="header">
          <h1>Создание новой группы</h1>
        </div>

        <div className="section">
          <label>Название группы</label>
          <input
            type="text"
            placeholder="Например: Путешествие в Сочи"
            value={name}
            onChange={(e) => setName(e.target.value)}
          />
        </div>

        <div className="section">
          <label>Участники (через запятую)</label>
          <input
            type="text"
            placeholder="Иван, Мария, Алексей"
            value={members}
            onChange={(e) => setMembers(e.target.value)}
          />
        </div>

        <div className="section">
          <label>Начальный баланс</label>
          <input
            type="number"
            value={balance}
            onChange={(e) => setBalance(Number(e.target.value))}
          />
        </div>

        <div className="section">
          <div className="transactions-header">
            <h2>Транзакции (необязательно)</h2>
            <button onClick={addTransactionField} className="add-transaction-btn">
              Добавить транзакцию
            </button>
          </div>

          {transactions.map((t, idx) => (
            <div key={idx} className="transaction-fields">
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
            </div>
          ))}
        </div>

        <button 
          onClick={handleSubmit} 
          disabled={!name.trim()} 
          className="submit-btn"
        >
          Создать группу
        </button>
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

        /* Стили для основного содержимого */
        .group-content {
          max-width: 1200px;
          margin: 0 auto;
          padding: 1rem;
        }

        .header {
          display: flex;
          justify-content: space-between;
          align-items: center;
          margin-bottom: 2rem;
          padding-bottom: 1rem;
          border-bottom: 1px solid #e2e8f0;
        }

        .header h1 {
          font-size: 2rem;
          font-weight: 700;
          color: #1e293b;
        }

        .balance {
          font-size: 1.25rem;
          color: #334155;
        }

        .section {
          margin-bottom: 2rem;
          background: white;
          padding: 1.5rem;
          border-radius: 0.5rem;
          box-shadow: 0 1px 3px rgba(0,0,0,0.1);
        }

        .section h2 {
          font-size: 1.5rem;
          font-weight: 600;
          margin-bottom: 1rem;
          color: #1e293b;
        }

        .members-list {
          display: flex;
          flex-wrap: wrap;
          gap: 0.5rem;
        }

        .member-tag {
          background: #e2e8f0;
          padding: 0.5rem 1rem;
          border-radius: 9999px;
          font-size: 0.875rem;
          color: #334155;
        }

        .category-section {
          background: white;
          padding: 1.5rem;
          border-radius: 0.5rem;
          margin-bottom: 2rem;
          box-shadow: 0 1px 3px rgba(0,0,0,0.1);
        }

        .categories-list {
          display: flex;
          flex-wrap: wrap;
          gap: 0.5rem;
          margin-bottom: 1rem;
        }

        .category-tag {
          background: #dbeafe;
          color: #1d4ed8;
          padding: 0.5rem 1rem;
          border-radius: 9999px;
          font-size: 0.875rem;
        }

        .category-input {
          display: flex;
          gap: 0.5rem;
        }

        .category-input input {
          flex: 1;
          padding: 0.5rem 1rem;
          border: 1px solid #cbd5e1;
          border-radius: 0.375rem;
          font-size: 1rem;
        }

        .category-input button {
          background: #2563eb;
          color: white;
          border: none;
          padding: 0.5rem 1rem;
          border-radius: 0.375rem;
          cursor: pointer;
          transition: background 0.2s;
        }

        .category-input button:hover {
          background: #1d4ed8;
        }

        .transactions-header {
          display: flex;
          justify-content: space-between;
          align-items: center;
          margin-bottom: 1rem;
        }

        .transactions-header button {
          background: #16a34a;
          color: white;
          border: none;
          padding: 0.5rem 1rem;
          border-radius: 0.375rem;
          cursor: pointer;
          transition: background 0.2s;
        }

        .transactions-header button:hover {
          background: #15803d;
        }

        .transactions-table {
          background: white;
          border-radius: 0.5rem;
          overflow: hidden;
          box-shadow: 0 1px 3px rgba(0,0,0,0.1);
        }

        table {
          width: 100%;
          border-collapse: collapse;
        }

        th, td {
          padding: 1rem;
          text-align: left;
          border-bottom: 1px solid #e2e8f0;
        }

        th {
          background: #f1f5f9;
          font-weight: 600;
          color: #334155;
        }

        tr:hover {
          background: #f8fafc;
        }

        .transactions-table button {
          color: #dc2626;
          background: none;
          border: none;
          cursor: pointer;
          transition: color 0.2s;
        }

        .transactions-table button:hover {
          color: #b91c1c;
        }

        .loading, .not-found {
          min-height: 100vh;
          display: flex;
          justify-content: center;
          align-items: center;
          font-size: 1.5rem;
        }
      `}</style>
    </div>
  );
} 