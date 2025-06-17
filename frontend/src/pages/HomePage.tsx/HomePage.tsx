import { useState, useEffect } from 'react';
import { useNavigate, Link, useLocation } from 'react-router-dom';
import styled, { keyframes } from 'styled-components';

interface Group {
  id: number;
  name: string;
  balance: number;
  members: number;
  color: string;
}

const PageContainer = styled.div`
  min-height: 100vh;
  width: 208vh;
  display: flex;
  flex-direction: column;
  background: linear-gradient(to bottom right, #f9fafb, #f3f4f6);
  font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
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

const LogoLink = styled(Link)`
  display: flex;
  align-items: center;
  text-decoration: none;
`;

const Logo = styled.div`
  font-size: 1.5rem;
  font-weight: 700;
  color: #059669;
`;

const MainNav = styled.nav`
  display: none;
  width: 100%;
  justify-content: space-between;
  padding: 0 2rem;

  @media (min-width: 768px) {
    display: flex;
  }
`;

const NavLinkStyled = styled(Link)<{ $active?: boolean }>`
  position: relative;
  padding: 1rem 1.5rem;
  font-size: 1.25rem;
  font-weight: 600;
  text-align: center;
  flex: 1;
  transition: all 0.3s ease;
  color: ${({ $active }) => ($active ? '#059669' : '#4b5563')};
  text-decoration: none;

  &:hover {
    color: #111827;
    transform: scale(1.05);
  }
`;

const NavIndicator = styled.span`
  position: absolute;
  left: 50%;
  bottom: 0.5rem;
  height: 2px;
  width: 2.5rem;
  transform: translateX(-50%);
  background-color: #059669;
  border-radius: 9999px;
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

const MainContent = styled.main`
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 2rem 1rem;
`;

const ContentContainer = styled.div`
  width: 100%;
  max-width: 72rem;
  margin: 0 auto;
`;

const TitleSection = styled.div`
  text-align: center;
  margin-bottom: 3rem;

  h1 {
    font-size: 2.25rem;
    font-weight: 700;
    margin-bottom: 1rem;
    background: linear-gradient(to right, #059669, #06b6d4);
    -webkit-background-clip: text;
    background-clip: text;
    color: transparent;

    @media (min-width: 768px) {
      font-size: 3rem;
    }
  }

  p {
    font-size: 1.125rem;
    color: #4b5563;
    max-width: 36rem;
    margin: 0 auto;
    line-height: 1.6;
  }
`;

const GroupsGrid = styled.div`
  display: grid;
  grid-template-columns: 1fr;
  gap: 1.5rem;
  margin-bottom: 3rem;

  @media (min-width: 640px) {
    grid-template-columns: repeat(2, 1fr);
  }
  @media (min-width: 1024px) {
    grid-template-columns: repeat(3, 1fr);
  }
`;

const GroupCard = styled.div<{ $color: string }>`
  position: relative;
  overflow: hidden;
  border-radius: 0.75rem;
  cursor: pointer;
  transition: all 0.3s ease;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
  background: ${({ $color }) => {
    switch ($color) {
      case 'group-color-1': return 'linear-gradient(to right, #6366f1, #8b5cf6)';
      case 'group-color-2': return 'linear-gradient(to right, #f59e0b, #ec4899)';
      case 'group-color-3': return 'linear-gradient(to right, #10b981, #0d9488)';
      case 'group-color-4': return 'linear-gradient(to right, #3b82f6, #06b6d4)';
      case 'group-color-5': return 'linear-gradient(to right, #f43f5e, #ef4444)';
      default: return '#fff';
    }
  }};

  &:hover {
    transform: translateY(-0.5rem);
    box-shadow: 0 10px 15px rgba(0, 0, 0, 0.1);
  }
`;

const GroupContent = styled.div`
  position: relative;
  z-index: 10;
  padding: 1.5rem;
  color: white;
`;

const GroupHeader = styled.div`
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 2rem;

  h2 {
    font-size: 1.25rem;
    font-weight: 700;
  }
`;

//не используется, возможно посеялось при переписывании
const MembersCount = styled.div`
  background: rgba(255, 255, 255, 0.2);
  backdrop-filter: blur(10px);
  border-radius: 9999px;
  padding: 0.25rem 0.75rem;
  font-size: 0.75rem;
  font-weight: 500;
`;

const GroupBalance = styled.div`
  font-size: 1.5rem;
  font-weight: 700;
  margin-bottom: 0.25rem;
`;

const BalanceLabel = styled.div`
  font-size: 0.875rem;
  opacity: 0.8;
`;

const GroupFooter = styled.div`
  position: absolute;
  bottom: 0;
  left: 0;
  right: 0;
  height: 2px;
  background: rgba(255, 255, 255, 0.3);
  transition: all 0.3s ease;

  ${GroupCard}:hover & {
    background: rgba(255, 255, 255, 0.5);
  }
`;

const DeleteGroupBtn = styled.button`
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

  ${GroupCard}:hover & {
    opacity: 1;
  }

  &:hover {
    background: rgba(0, 0, 0, 0.5);
  }

  svg {
    width: 1rem;
    height: 1rem;
  }
`;

const CreateGroupCard = styled.div`
  border: 2px dashed #d1d5db;
  border-radius: 0.75rem;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 1.5rem;
  cursor: pointer;
  transition: all 0.3s ease;

  &:hover {
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

    svg {
      width: 1.5rem;
      height: 1.5rem;
      color: #059669;
    }
  }

  &:hover .plus-icon {
    background: #a7f3d0;
  }

  h3 {
    font-size: 1.125rem;
    font-weight: 500;
    color: #374151;
    margin-bottom: 0.25rem;
    transition: all 0.3s ease;
  }

  &:hover h3 {
    color: #065f46;
  }

  p {
    font-size: 0.875rem;
    color: #6b7280;
    text-align: center;
  }
`;

const CtaSection = styled.div`
  background: white;
  border-radius: 0.75rem;
  padding: 2rem;
  text-align: center;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);

  h2 {
    font-size: 1.5rem;
    font-weight: 700;
    color: #1f2937;
    margin-bottom: 0.75rem;
  }

  p {
    font-size: 1rem;
    color: #4b5563;
    max-width: 42rem;
    margin: 0 auto 1.5rem;
    line-height: 1.6;
  }
`;

const CtaButtons = styled.div`
  display: flex;
  flex-direction: column;
  gap: 1rem;
  justify-content: center;

  @media (min-width: 640px) {
    flex-direction: row;
  }
`;

const PrimaryBtn = styled.button`
  padding: 0.75rem 1.5rem;
  background: linear-gradient(to right, #10b981, #0d9488);
  color: white;
  border: none;
  border-radius: 0.5rem;
  font-weight: 500;
  cursor: pointer;
  box-shadow: 0 1px 2px rgba(0, 0, 0, 0.1);
  transition: all 0.3s ease;

  &:hover {
    background: linear-gradient(to right, #0ea472, #0d9488);
    box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
  }
`;

const SecondaryBtn = styled.button`
  padding: 0.75rem 1.5rem;
  border: 1px solid #d1d5db;
  color: #374151;
  background: white;
  border-radius: 0.5rem;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.3s ease;

  &:hover {
    border-color: #34d399;
    color: #065f46;
  }
`;

const fadeIn = keyframes`
  from { opacity: 0; }
  to { opacity: 1; }
`;

const scaleIn = keyframes`
  from { transform: scale(0.95); opacity: 0; }
  to { transform: scale(1); opacity: 1; }
`;

const ModalOverlay = styled.div`
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
  animation: ${fadeIn} 0.3s ease-out;
`;

const ModalContent = styled.div`
  background: white;
  border-radius: 0.75rem;
  max-width: 28rem;
  width: 100%;
  padding: 1.5rem;
  box-shadow: 0 10px 25px rgba(0, 0, 0, 0.1);
  animation: ${scaleIn} 0.2s ease-out;
`;

const ModalHeader = styled.div`
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1rem;

  h3 {
    font-size: 1.25rem;
    font-weight: 600;
    color: #111827;
  }
`;

const CloseBtn = styled.button`
  color: #9ca3af;
  background: none;
  border: none;
  cursor: pointer;
  padding: 0.25rem;

  &:hover {
    color: #6b7280;
  }

  svg {
    width: 1.5rem;
    height: 1.5rem;
  }
`;

const ModalBody = styled.div`
  margin-bottom: 1.5rem;

  label {
    display: block;
    font-size: 0.875rem;
    font-weight: 500;
    color: #374151;
    margin-bottom: 0.5rem;
  }

  input {
    width: 100%;
    padding: 0.5rem 1rem;
    border: 1px solid #d1d5db;
    border-radius: 0.5rem;
    font-size: 1rem;

    &:focus {
      outline: none;
      border-color: #059669;
      box-shadow: 0 0 0 2px rgba(5, 150, 105, 0.2);
    }
  }
`;

const ModalFooter = styled.div`
  display: flex;
  justify-content: flex-end;
  gap: 0.75rem;
`;

const CancelBtn = styled.button`
  padding: 0.5rem 1rem;
  border: 1px solid #d1d5db;
  background: white;
  color: #374151;
  border-radius: 0.5rem;
  font-weight: 500;
  cursor: pointer;

  &:hover {
    background: #f3f4f6;
  }
`;

const ConfirmBtn = styled.button`
  padding: 0.5rem 1rem;
  background: #059669;
  color: white;
  border: none;
  border-radius: 0.5rem;
  font-weight: 500;
  cursor: pointer;

  &:hover {
    background: #047857;
  }

  &:disabled {
    background: #9ca3af;
    cursor: not-allowed;
  }
`;

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
    <PageContainer>
      <PageHeader>
        <HeaderContainer>
          <LogoLink to="/"><Logo>CashCrew</Logo></LogoLink>
          <MainNav>
            {[
              { path: '/home', name: 'Главная' },
              { path: '/reports', name: 'Отчеты' },
              { path: '/features', name: 'Группы' },
            ].map((item) => (
              <NavLinkStyled
                key={item.path}
                to={item.path}
                $active={isActive(item.path)}
              >
                {item.name}
                {isActive(item.path) && <NavIndicator />}
              </NavLinkStyled>
            ))}
          </MainNav>
          <AuthButtons>
            <LoginBtn onClick={() => navigate('/login')}>Вход</LoginBtn>
            <RegisterBtn onClick={() => navigate('/register')}>Регистрация</RegisterBtn>
          </AuthButtons>
        </HeaderContainer>
      </PageHeader>

      <MainContent>
        <ContentContainer>
          <TitleSection>
            <h1>Управляйте финансами вместе</h1>
            <p>Создавайте группы, отслеживайте общие расходы и легко управляйте бюджетами с друзьями и семьей</p>
          </TitleSection>

          <GroupsGrid>
            {groups.map(group => (
              <GroupCard
                key={group.id}
                $color={group.color}
                onClick={() => navigate(`/group/${group.id}`)}
              >
                <GroupContent>
                  <GroupHeader>
                    <h2>{group.name}</h2>
                    <DeleteGroupBtn onClick={(e) => handleDeleteGroup(group.id, e)}>
                      <CloseBtn as="div">×</CloseBtn>
                      <svg viewBox="0 0 24 24" width="16" height="16">
                        <path d="M6 18L18 6M6 6l12 12" stroke="currentColor" strokeWidth="2" />
                      </svg>
                    </DeleteGroupBtn>
                  </GroupHeader>
                  <GroupBalance>{group.balance.toLocaleString()} ₽</GroupBalance>
                  <BalanceLabel>Общий баланс</BalanceLabel>
                </GroupContent>
                <GroupFooter />
              </GroupCard>
            ))}

            <CreateGroupCard onClick={() => navigate('/create-group')}>
              <div className="plus-icon">
                <svg viewBox="0 0 24 24">
                  <path d="M12 6v6m0 0v6m0-6h6m-6 0H6"></path>
                </svg>
              </div>
              <h3>Создать группу</h3>
              <p>Общий бюджет с друзьями или семьей</p>
            </CreateGroupCard>
          </GroupsGrid>

          <CtaSection>
            <h2>Нужен полный контроль над финансами?</h2>
            <p>Получайте детальные отчеты, устанавливайте лимиты и синхронизируйте данные между устройствами</p>
            <CtaButtons>
              <PrimaryBtn>Попробовать бесплатно</PrimaryBtn>
              <SecondaryBtn>Узнать больше</SecondaryBtn>
            </CtaButtons>
          </CtaSection>
        </ContentContainer>
      </MainContent>

      {/* Модальное окно */}
      {isModalOpen && (
        <ModalOverlay>
          <ModalContent>
            <ModalHeader>
              <h3>Новая группа</h3>
              <CloseBtn onClick={() => setIsModalOpen(false)}>
                <svg viewBox="0 0 24 24">
                  <path d="M6 18L18 6M6 6l12 12"></path>
                </svg>
              </CloseBtn>
            </ModalHeader>
            <ModalBody>
              <label htmlFor="groupName">Название группы</label>
              <input
                type="text"
                id="groupName"
                placeholder="Например: Путешествие в Сочи"
                value={newGroupName}
                onChange={(e) => setNewGroupName(e.target.value)}
                autoFocus
              />
            </ModalBody>
            <ModalFooter>
              <CancelBtn onClick={() => setIsModalOpen(false)}>
                Отмена
              </CancelBtn>
              <ConfirmBtn
                onClick={handleCreateGroup}
                disabled={!newGroupName.trim()}
              >
                Создать
              </ConfirmBtn>
            </ModalFooter>
          </ModalContent>
        </ModalOverlay>
      )}
    </PageContainer>
  );
}