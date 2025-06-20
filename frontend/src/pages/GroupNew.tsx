import { Loading3QuartersOutlined } from '@ant-design/icons';
import { useState, useEffect } from 'react';
import { useParams, useNavigate, Link } from 'react-router-dom';
import styled from 'styled-components';
import { getGroupById } from '../api/group';
import type { Group } from '../types/types';


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

// const Balance = styled.div`
//   font-size: 1.25rem;
//   color: #334155;
//   font-weight: 500;
// `;

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

const MembersList = styled.div`
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem;
`;

const MemberTag = styled.span`
  background: #e2e8f0;
  padding: 0.5rem 1rem;
  border-radius: 9999px;
  font-size: 0.875rem;
  color: #334155;
`;

const TransactionsHeader = styled.div`
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1rem;
`;

const AddTransactionBtn = styled.button`
  background: #16a34a;
  color: white;
  border: none;
  padding: 0.5rem 1rem;
  border-radius: 0.375rem;
  cursor: pointer;
  transition: background 0.2s;

  &:hover {
    background: #15803d;
  }
`;

// const TransactionsTable = styled.div`
//   background: white;
//   border-radius: 0.5rem;
//   overflow: hidden;
//   box-shadow: 0 1px 3px rgba(0,0,0,0.1);
//   color: black;

//   table {
//     width: 100%;
//     border-collapse: collapse;
//   }

//   th, td {
//     padding: 1rem;
//     text-align: left;
//     border-bottom: 1px solid #e2e8f0;
//   }

//   th {
//     background: #f1f5f9;
//     font-weight: 600;
//     color: #334155;
//   }

//   tr:hover {
//     background: #f8fafc;
//   }
// `;

// const NoTransactions = styled.p`
//   color: #64748b;
//   font-style: italic;
//   text-align: center;
//   padding: 1rem;
// `;

const Loading = styled.h1`
  color: black;
  justify-self: center;
  align-self: center;
`


export default function GroupNew() {
  const { id  } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const [group, setGroup] = useState<Group | null>(null);
  useEffect(() => {
    const fetchGroup = async () => {
      try {
        const data = await getGroupById(id ?? "") ;
        setGroup(data);
        localStorage.setItem('groups', data)
      } catch {
        setGroup(null);
      }
    };
    fetchGroup();
  }, []);

  // Навигационное меню
  const navItems = [
    { path: '/home', name: 'Главная' },
    { path: '/who', name: 'Отчеты' },
    { path: '/features', name: 'Группы' },
  ];
  return (
    <PageContainer>
      <PageHeader>
        <HeaderContainer>
          <BackButton onClick={() => navigate(-1)}>←</BackButton>

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
      {group && (
        <>
          <GroupContent>
            <Header>
              <h1>{group.name}</h1>
              {/* <Balance>Баланс: {group.balance} ₽</Balance> */}
            </Header>
            <Section>
              <TransactionsHeader>
                <h2>Список транзакций</h2>
                <AddTransactionBtn onClick={() => navigate(`/group/${group.id}/add-transaction`)}>
                  Добавить транзакцию
                </AddTransactionBtn>
              </TransactionsHeader>

              {/* {group.transactions.length > 0 ? (
                <TransactionsTable>
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
                </TransactionsTable>
              ) : (
                <NoTransactions>Транзакции не добавлены</NoTransactions>
              )} */}
            </Section>
          </GroupContent>
          
          <Section>
            <h2>Участники</h2>
            <MembersList>
              {group.members.length > 0 ? (
                group.members.map((member, index) => (
                  <MemberTag key={`member-${index}`}>
                    {member}
                  </MemberTag>
                ))
              ) : (
                <p>Нет участников</p>
              )}
            </MembersList>
          </Section>

          <Section>
            <TransactionsHeader>
              <h2>Список транзакций</h2>
              <AddTransactionBtn onClick={() => navigate(`/group/${group.id}/add-transaction`)}>
                Добавить транзакцию
              </AddTransactionBtn>
            </TransactionsHeader>
          </Section>
        </>
      )}
      {!group && (
        <>
          <Loading>Loading</Loading>
          <Loading3QuartersOutlined color='#000'></Loading3QuartersOutlined>
        </>
      )}

    </PageContainer>
  );
}