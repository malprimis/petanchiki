import { useState, useEffect } from 'react';
import { useParams, useNavigate, Link } from 'react-router-dom';

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

export default function GroupNew() {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const [group, setGroup] = useState<Group | null>(null);
  const [loading, setLoading] = useState(true); // Добавлено состояние загрузки

  // Навигационное меню
  const navItems = [
    { path: '/home', name: 'Главная' },
    { path: '/who', name: 'Отчеты' },
    { path: '/features', name: 'Группы' },
  ];

  useEffect(() => {
    const loadGroup = () => {
      try {
        const savedGroups = JSON.parse(localStorage.getItem('groups') || '[]');
        console.log('Loaded groups:', savedGroups);
        
        // Исправлено: явное преобразование id в число
        const foundGroup = savedGroups.find((g: Group) => g.id === Number(id));
        console.log('Found group:', foundGroup);
        
        if (foundGroup) {
          // Проверка и нормализация транзакций
          const normalizedTransactions = foundGroup.transactions.map(t => ({
            ...t,
            date: t.date || 'Не указана',
            category: t.category || 'Без категории',
            amount: Number(t.amount) || 0,
            member: t.member || 'Не указан'
          }));
          
          setGroup({
            ...foundGroup,
            transactions: normalizedTransactions
          });
        } else {
          console.error('Группа не найдена');
          navigate('/home');
        }
      } catch (error) {
        console.error('Ошибка загрузки группы:', error);
        navigate('/home');
      } finally {
        setLoading(false);
      }
    };

    loadGroup();
  }, [id, navigate]);

  if (loading) {
    return (
      <div className="loading-container">
        <p>Загрузка данных группы...</p>
      </div>
    );
  }

  if (!group) {
    return (
      <div className="not-found">
        <p>Группа не найдена</p>
      </div>
    );
  }

  return (
    <div className="page-container">
      {/* Верхнее меню */}
      <header className="page-header">
        <div className="header-container">
          <button onClick={() => navigate(-1)} className="back-button">
            ←
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
          <h1>{group.name}</h1>
          <div className="balance">Баланс: {group.balance} ₽</div>
        </div>

        <div className="section">
          <h2>Участники</h2>
          <div className="members-list">
            {group.members.length > 0 ? (
              group.members.map((member, index) => (
                <span key={`member-${index}`} className="member-tag">
                  {member}
                </span>
              ))
            ) : (
              <p>Нет участников</p>
            )}
          </div>
        </div>

        <div className="section">
          <div className="transactions-header">
            <h2>Список транзакций</h2>
            <button 
              onClick={() => navigate(`/group/${group.id}/add-transaction`)} 
              className="add-transaction-btn"
            >
              Добавить транзакцию
            </button>
          </div>

          {group.transactions.length > 0 ? (
            <div className="transactions-table">
              <table>
                <thead>
                  <tr>
                    <th>Дата</th>
                    <th>Категория</th>
                    <th>Сумма</th>
                    <th>Участник</th>
                  </tr>
                </thead>
                <tbody>
                  {group.transactions.map((transaction) => (
                    <tr key={`transaction-${transaction.id}`}>
                      <td>{transaction.date}</td>
                      <td>{transaction.category}</td>
                      <td>{transaction.amount} ₽</td>
                      <td>{transaction.member}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          ) : (
            <p className="no-transactions">Транзакции не добавлены</p>
          )}
        </div>
      </div>

      <style jsx>{`
        .page-container {
          min-height: 100vh;
          min-width: 208vh; 
          background: #f8fafc;
        }

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

        .group-content {
          max-width: 1200px;
          margin: 0 auto;
          padding: 2rem;
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
          font-weight: 500;
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

        .transactions-header {
          display: flex;
          justify-content: space-between;
          align-items: center;
          margin-bottom: 1rem;
        }

        .add-transaction-btn {
          background: #16a34a;
          color: white;
          border: none;
          padding: 0.5rem 1rem;
          border-radius: 0.375rem;
          cursor: pointer;
          transition: background 0.2s;
        }

        .add-transaction-btn:hover {
          background: #15803d;
        }

        .transactions-table {
          background: white;
          border-radius: 0.5rem;
          overflow: hidden;
          box-shadow: 0 1px 3px rgba(0,0,0,0.1);
          color: black; 
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

        .no-transactions {
          color: #64748b;
          font-style: italic;
          text-align: center;
          padding: 1rem;
        }

        .loading-container,
        .not-found {
          min-height: 100vh;
          display: flex;
          justify-content: center;
          align-items: center;
          font-size: 1.5rem;
          color: #64748b;
        }
      `}</style>
    </div>
  );
}