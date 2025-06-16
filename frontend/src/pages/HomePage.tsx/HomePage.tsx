import { useState, useEffect } from 'react';
import { useNavigate, Link, useLocation } from 'react-router-dom';

interface Group {
  id: number;
  name: string;
  balance: number;
  members: number;
  color: string;
}

export default function HomePage() {
  const [groups, setGroups] = useState<Group[]>(() => {
    // Загружаем группы из localStorage при инициализации
    const savedGroups = localStorage.getItem('groups');
    return savedGroups ? JSON.parse(savedGroups) : [
      { id: 1, name: "Семья", balance: 12500, members: 4, color: "group-color-1" },
      { id: 2, name: "Путешествия", balance: 8700, members: 3, color: "group-color-2" },
      { id: 3, name: "Друзья", balance: 4300, members: 5, color: "group-color-3" }
    ];
  });

  const [isModalOpen, setIsModalOpen] = useState<boolean>(false);
  const [newGroupName, setNewGroupName] = useState<string>('');
  const navigate = useNavigate();
  const location = useLocation();

  const handleDeleteGroup = (id: number, e: React.MouseEvent) => {
  e.stopPropagation(); // Предотвращаем переход по ссылке при клике на крестик
  setGroups(groups.filter(group => group.id !== id));
};
  // Сохраняем группы в localStorage при их изменении
  useEffect(() => {
    localStorage.setItem('groups', JSON.stringify(groups));
  }, [groups]);

  const handleCreateGroup = () => {
    if (newGroupName.trim()) {
      const colors = ["group-color-1", "group-color-2", "group-color-3", "group-color-4", "group-color-5"];
      const newGroup: Group = {
        id: Date.now(), // Используем timestamp для уникального ID
        name: newGroupName,
        balance: 0,
        members: 1,
        color: colors[Math.floor(Math.random() * colors.length)]
      };
      
      const updatedGroups = [...groups, newGroup];
      setGroups(updatedGroups);
      setNewGroupName('');
      setIsModalOpen(false);
      
      // Перенаправляем на страницу новой группы
      navigate(`/group/${newGroup.id}`);
    }
  };

  const isActive = (path: string) => location.pathname === path;

  return (
    <div className="page-container">
      {/* Верхнее меню */}
      <header className="page-header">
        <div className="header-container">
          {/* Логотип */}
          <Link to="/" className="logo-link">
            <div className="logo">CashCrew</div>
          </Link>

          {/* Навигация */}
          <nav className="main-nav">
            {[
              { path: '/home', name: 'Главная' },
              { path: '/reports', name: 'Отчеты' },
              { path: '/features', name: 'Группы' },
            ].map((item) => (
              <Link
                key={item.path}
                to={item.path}
                className={`nav-link ${isActive(item.path) ? 'active' : ''}`}
              >
                {item.name}
                {isActive(item.path) && <span className="nav-indicator"></span>}
              </Link>
            ))}
          </nav>

          {/* Кнопки авторизации */}
          <div className="auth-buttons">
            <button 
              className="login-btn"
              onClick={() => navigate('/login')}
            >
              Вход
            </button>
            <button 
              className="register-btn"
              onClick={() => navigate('/register')}
            >
              Регистрация
            </button>
          </div>
        </div>
      </header>

      {/* Основной контент */}
      <main className="main-content">
        <div className="content-container">
          {/* Заголовок */}
          <div className="title-section">
            <h1>Управляйте финансами вместе</h1>
            <p>Создавайте группы, отслеживайте общие расходы и легко управляйте бюджетами с друзьями и семьей</p>
          </div>

          {/* Карточки групп */}
          <div className="groups-grid">
            {groups.map(group => (
              <div 
                key={group.id}
                className={`group-card ${group.color}`}
                onClick={() => navigate(`/group/${group.id}`)}
              >
                <div className="group-content">
                  <div className="group-header">
                    <h2>{group.name}</h2>
                    <button 
  className="delete-group-btn"
  onClick={(e) => handleDeleteGroup(group.id, e)}
>
  <div className="close-btn">×</div>
  <svg viewBox="0 0 24 24" width="16" height="16">
    <path d="M6 18L18 6M6 6l12 12" stroke="currentColor" strokeWidth="2" />
  </svg>
</button>
                  </div>
                  <div className="group-balance">{group.balance.toLocaleString()} ₽</div>
                  <div className="balance-label">Общий баланс</div>
                </div>
                <div className="group-footer"></div>
              </div>
            ))}
            
            {/* Карточка для создания новой группы */}
            <div 
              className="create-group-card"
              onClick={() => navigate('/create-group')}
            >
              <div className="plus-icon">
                <svg viewBox="0 0 24 24">
                  <path d="M12 6v6m0 0v6m0-6h6m-6 0H6"></path>
                </svg>
              </div>
              <h3>Создать группу</h3>
              <p>Общий бюджет с друзьями или семьей</p>
            </div>
          </div>

          {/* Дополнительные CTA */}
          <div className="cta-section">
            <h2>Нужен полный контроль над финансами?</h2>
            <p>Получайте детальные отчеты, устанавливайте лимиты и синхронизируйте данные между устройствами</p>
            <div className="cta-buttons">
              <button className="primary-btn">Попробовать бесплатно</button>
              <button className="secondary-btn">Узнать больше</button>
            </div>
          </div>
        </div>
      </main>

      {/* Модальное окно */}
      {isModalOpen && (
        <div className="modal-overlay">
          <div className="modal-content">
            <div className="modal-header">
              <h3>Новая группа</h3>
              <button onClick={() => setIsModalOpen(false)} className="close-btn">
                <svg viewBox="0 0 24 24">
                  <path d="M6 18L18 6M6 6l12 12"></path>
                </svg>
              </button>
            </div>
            
            <div className="modal-body">
              <label htmlFor="groupName">Название группы</label>
              <input
                type="text"
                id="groupName"
                placeholder="Например: Путешествие в Сочи"
                value={newGroupName}
                onChange={(e) => setNewGroupName(e.target.value)}
                autoFocus
              />
            </div>
            
            <div className="modal-footer">
              <button onClick={() => setIsModalOpen(false)} className="cancel-btn">
                Отмена
              </button>
              <button onClick={handleCreateGroup} disabled={!newGroupName.trim()} className="confirm-btn">
                Создать
              </button>
            </div>
          </div>
        </div>
      )}

      {/* CSS стили */}
      <style jsx>{`
       
        .page-container {
          min-height: 100vh;
          width: 208vh;
          display: flex;
          flex-direction: column;
          background: linear-gradient(to bottom right, #f9fafb, #f3f4f6);
          font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
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
          display: none;
          width: 100%;
          justify-content: space-between;
          padding: 0 2rem;
        }

        @media (min-width: 768px) {
          .main-nav {
            display: flex;
          }
        }

        .nav-link {
          position: relative;
          padding: 1rem 1.5rem;
          font-size: 1.25rem;
          font-weight: 600;
          text-align: center;
          flex: 1;
          transition: all 0.3s ease;
          color: #4b5563;
          text-decoration: none;
        }

        .nav-link:hover {
          color: #111827;
          transform: scale(1.05);
        }

        .nav-link.active {
          color: #059669;
        }

        .nav-indicator {
          position: absolute;
          left: 50%;
          bottom: 0.5rem;
          height: 2px;
          width: 2.5rem;
          transform: translateX(-50%);
          background-color: #059669;
          border-radius: 9999px;
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

        .main-content {
          flex: 1;
          display: flex;
          align-items: center;
          justify-content: center;
          padding: 2rem 1rem;
        }

        .content-container {
          width: 100%;
          max-width: 72rem;
          margin: 0 auto;
        }

        .title-section {
          text-align: center;
          margin-bottom: 3rem;
        }

        .title-section h1 {
          font-size: 2.25rem;
          font-weight: 700;
          margin-bottom: 1rem;
          background: linear-gradient(to right, #059669, #06b6d4);
          -webkit-background-clip: text;
          background-clip: text;
          color: transparent;
        }

        @media (min-width: 768px) {
          .title-section h1 {
            font-size: 3rem;
          }
        }

        .title-section p {
          font-size: 1.125rem;
          color: #4b5563;
          max-width: 36rem;
          margin: 0 auto;
          line-height: 1.6;
        }

        .groups-grid {
          display: grid;
          grid-template-columns: 1fr;
          gap: 1.5rem;
          margin-bottom: 3rem;
        }

        @media (min-width: 640px) {
          .groups-grid {
            grid-template-columns: repeat(2, 1fr);
          }
        }

        @media (min-width: 1024px) {
          .groups-grid {
            grid-template-columns: repeat(3, 1fr);
          }
        }

        .group-card {
          position: relative;
          overflow: hidden;
          border-radius: 0.75rem;
          cursor: pointer;
          transition: all 0.3s ease;
          box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        }

        .group-card:hover {
          transform: translateY(-0.5rem);
          box-shadow: 0 10px 15px rgba(0, 0, 0, 0.1);
        }

        .group-color-1 {
          background: linear-gradient(to right, #6366f1, #8b5cf6);
        }

        .group-color-2 {
          background: linear-gradient(to right, #f59e0b, #ec4899);
        }

        .group-color-3 {
          background: linear-gradient(to right, #10b981, #0d9488);
        }

        .group-color-4 {
          background: linear-gradient(to right, #3b82f6, #06b6d4);
        }

        .group-color-5 {
          background: linear-gradient(to right, #f43f5e, #ef4444);
        }

        .group-content {
          position: relative;
          z-index: 10;
          padding: 1.5rem;
          color: white;
        }

        .group-header {
          display: flex;
          justify-content: space-between;
          align-items: flex-start;
          margin-bottom: 2rem;
        }

        .group-header h2 {
          font-size: 1.25rem;
          font-weight: 700;
        }

        .members-count {
          background: rgba(255, 255, 255, 0.2);
          backdrop-filter: blur(10px);
          border-radius: 9999px;
          padding: 0.25rem 0.75rem;
          font-size: 0.75rem;
          font-weight: 500;
        }

        .group-balance {
          font-size: 1.5rem;
          font-weight: 700;
          margin-bottom: 0.25rem;
        }

        .balance-label {
          font-size: 0.875rem;
          opacity: 0.8;
        }

        .group-footer {
          position: absolute;
          bottom: 0;
          left: 0;
          right: 0;
          height: 2px;
          background: rgba(255, 255, 255, 0.3);
          transition: all 0.3s ease;
        }

        .group-card:hover .group-footer {
          background: rgba(255, 255, 255, 0.5);
        }

        .create-group-card {
          border: 2px dashed #d1d5db;
          border-radius: 0.75rem;
          display: flex;
          flex-direction: column;
          align-items: center;
          justify-content: center;
          padding: 1.5rem;
          cursor: pointer;
          transition: all 0.3s ease;
        }

        .create-group-card:hover {
          border-color: #34d399;
          background: rgba(209, 250, 229, 0.3);
        }

        .plus-icon {
          width: 3rem;
          height: 3rem;
          border-radius: 9999px;
          background: #d1fae5;
          display: flex;
          align-items: center;
          justify-content: center;
          margin-bottom: 1rem;
          transition: all 0.3s ease;
        }

        .create-group-card:hover .plus-icon {
          background: #a7f3d0;
        }

        .plus-icon svg {
          width: 1.5rem;
          height: 1.5rem;
          color: #059669;
        }

        .create-group-card h3 {
          font-size: 1.125rem;
          font-weight: 500;
          color: #374151;
          margin-bottom: 0.25rem;
          transition: all 0.3s ease;
        }

        .create-group-card:hover h3 {
          color: #065f46;
        }

        .create-group-card p {
          font-size: 0.875rem;
          color: #6b7280;
          text-align: center;
        }

        .cta-section {
          background: white;
          border-radius: 0.75rem;
          padding: 2rem;
          text-align: center;
          box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
        }

        .cta-section h2 {
          font-size: 1.5rem;
          font-weight: 700;
          color: #1f2937;
          margin-bottom: 0.75rem;
        }

        .cta-section p {
          font-size: 1rem;
          color: #4b5563;
          max-width: 42rem;
          margin: 0 auto 1.5rem;
          line-height: 1.6;
        }

        .cta-buttons {
          display: flex;
          flex-direction: column;
          gap: 1rem;
          justify-content: center;
        }

        @media (min-width: 640px) {
          .cta-buttons {
            flex-direction: row;
          }
        }

        .primary-btn {
          padding: 0.75rem 1.5rem;
          background: linear-gradient(to right, #10b981, #0d9488);
          color: white;
          border: none;
          border-radius: 0.5rem;
          font-weight: 500;
          cursor: pointer;
          box-shadow: 0 1px 2px rgba(0, 0, 0, 0.1);
          transition: all 0.3s ease;
        }

        .primary-btn:hover {
          background: linear-gradient(to right, #0ea472, #0d9488);
          box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        }

        .secondary-btn {
          padding: 0.75rem 1.5rem;
          border: 1px solid #d1d5db;
          color: #374151;
          background: white;
          border-radius: 0.5rem;
          font-weight: 500;
          cursor: pointer;
          transition: all 0.3s ease;
        }

        .secondary-btn:hover {
          border-color: #34d399;
          color: #065f46;
        }

        .modal-overlay {
          position: fixed;
          top: 0;
          left: 0;
          right: 0;
          bottom: 0;
          background: rgba(0, 0, 0, 0.5);
          backdrop-filter: blur(5px);
          display: flex;
          align-items: center;
          justify-content: center;
          padding: 1rem;
          z-index: 50;
          animation: fadeIn 0.3s ease-out;
        }

        .modal-content {
          background: white;
          border-radius: 0.75rem;
          max-width: 28rem;
          width: 100%;
          padding: 1.5rem;
          box-shadow: 0 10px 25px rgba(0, 0, 0, 0.1);
          animation: scaleIn 0.2s ease-out;
        }

        .modal-header {
          display: flex;
          justify-content: space-between;
          align-items: center;
          margin-bottom: 1rem;
        }

        .modal-header h3 {
          font-size: 1.25rem;
          font-weight: 600;
          color: #111827;
        }

        .close-btn {
          color: #9ca3af;
          background: none;
          border: none;
          cursor: pointer;
          padding: 0.25rem;
        }

        .close-btn:hover {
          color: #6b7280;
        }

        .close-btn svg {
          width: 1.5rem;
          height: 1.5rem;
        }

        .modal-body {
          margin-bottom: 1.5rem;
        }

        .modal-body label {
          display: block;
          font-size: 0.875rem;
          font-weight: 500;
          color: #374151;
          margin-bottom: 0.5rem;
        }

        .modal-body input {
          width: 100%;
          padding: 0.5rem 1rem;
          border: 1px solid #d1d5db;
          border-radius: 0.5rem;
          font-size: 1rem;
        }

        .modal-body input:focus {
          outline: none;
          border-color: #059669;
          box-shadow: 0 0 0 2px rgba(5, 150, 105, 0.2);
        }

        .modal-footer {
          display: flex;
          justify-content: flex-end;
          gap: 0.75rem;
        }

        .cancel-btn {
          padding: 0.5rem 1rem;
          border: 1px solid #d1d5db;
          background: white;
          color: #374151;
          border-radius: 0.5rem;
          font-weight: 500;
          cursor: pointer;
        }

        .cancel-btn:hover {
          background: #f3f4f6;
        }

        .confirm-btn {
          padding: 0.5rem 1rem;
          background: #059669;
          color: white;
          border: none;
          border-radius: 0.5rem;
          font-weight: 500;
          cursor: pointer;
        }

        .confirm-btn:hover {
          background: #047857;
        }

        .confirm-btn:disabled {
          background: #9ca3af;
          cursor: not-allowed;
        }

        @keyframes fadeIn {
          from { opacity: 0; }
          to { opacity: 1; }
        }

        @keyframes scaleIn {
          from { transform: scale(0.95); opacity: 0; }
          to { transform: scale(1); opacity: 1; }
        }
          .delete-group-btn {
  position: absolute;
  top: 0.75rem;
  right: 0.75rem;
  width: 1.5rem;
  height: 1.5rem;
  display: flex;
  align-items: center;
  justify-content: center;
  background: rgba(0, 0, 0, 0.3);
  border: none;
  border-radius: 50%;
  color: white;
  cursor: pointer;
  z-index: 20;
  opacity: 0;
  transition: opacity 0.2s ease;
}

.group-card:hover .delete-group-btn {
  opacity: 1;
}

.delete-group-btn:hover {
  background: rgba(0, 0, 0, 0.5);
}

.delete-group-btn svg {
  width: 1rem;
  height: 1rem;
}
      `}</style>
    </div>
  );
} 