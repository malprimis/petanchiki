import { Loading3QuartersOutlined } from '@ant-design/icons';
import { useState, useEffect } from 'react';
import { useParams, useNavigate, Link } from 'react-router-dom';
import styled from 'styled-components';
import { addMemberToGroup, getGroupById } from '../api/group';
import type { Category, Group, TransactionResponse } from '../types/types';
import { getCategories, getTransactionsInGroup } from '../api/transaction';


const PageContainer = styled.div`
  min-height: 100vh;
  min-width: 208vh; // что это...
  background: #f8fafc;
  color: #000;
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

const SectionHeader = styled.div`
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1rem;
`;

const SectionButton = styled.button`
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

const TransactionsTable = styled.div`
  background: white;
  border-radius: 0.5rem;
  overflow: hidden;
  box-shadow: 0 1px 3px rgba(0,0,0,0.1);
  color: black;

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
`;

const NoTransactions = styled.p`
  color: #64748b;
  font-style: italic;
  text-align: center;
  padding: 1rem;
`;

const Loading = styled.h1`
  color: black;
  justify-self: center;
  align-self: center;
`;

const SectionContent = styled.div`
  font-size: 1rem;
`;
const AddMemberInput= styled.input`
  padding: 0.75rem;
  margin-bottom:1rem;
  margin-left: 5px;
  border-radius: 10px;
  border: 2px solid grey;
`;
const AddMemberBlock= styled.div`
  display: flex;
  justify-content: space-between;
`;
const SectioncControl = styled.div`
  display: flex;
  gap:5px;
`;



export default function GroupNew() {
  const { id  } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const [group, setGroup] = useState<Group | null>(null);
  const [transactions, setTransactions] = useState<TransactionResponse[]>([]);
  const [categories, setCategories] = useState<Category[]>([]);
  const [addUserModal, setAddUserModal] = useState(false);
  const [memberEmail, setMemberEmail] = useState('')
  const [addMemberMessage, setAddMemberMessage] = useState('')

  //получение данных о группе
  useEffect(() => {
    const fetchGroup = async () => {
      try {
        const groupInfo = await getGroupById(id ?? "") ;
        setGroup(groupInfo);
        localStorage.setItem('groups', groupInfo)
      } catch {
        setGroup(null);
      }
    };
    fetchGroup();
  }, [id]);

  //получение данных о транзакциях
  useEffect(() => {
    const fetchTransactions = async () => {
      try {
        const transactionInfo = await getTransactionsInGroup(id ?? "") ;
        setTransactions(transactionInfo);
        localStorage.setItem(`transaction-${group?.id}`, transactionInfo)

        console.log(transactionInfo);
      } catch {
        setTransactions([]);
      }
     
    };
    fetchTransactions();
  }, [group?.id, id]);

  //получение данных о категориях
  useEffect(() => {
      const fetchCategories = async () => {
        try {
          const fetchedCategories = await getCategories(id ?? "");
          if (Array.isArray(fetchedCategories)) {
            setCategories([...fetchedCategories]);
          }
          
          console.log(fetchedCategories);
        } catch {
          console.log('fetchCategories error');
        }
      };
      fetchCategories();
     
      
    }, [id]);


  //можно сделать словарь с id - имя
  const findCategoryNameById = (CategoryId : string) => {
    const category = categories.find((category) => category.id === CategoryId);
    return category ? category.name : '';
  }
  const findMemberNameById = (UserId : string) => {
    const user = group?.members.find((member) => member.id === UserId);
    return user ? user.email : '';
  }
  const handleAddMember = async () => {
    // Простая валидация email
    if (!memberEmail || !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(memberEmail)) {
      setAddMemberMessage('Введите корректный email');
      return;
    }
    try {
      console.log(memberEmail);
      await addMemberToGroup(id ?? '', memberEmail.trim());
      setAddMemberMessage('Пользователь добавлен');
      setMemberEmail('');
      // Обновить группу, чтобы сразу показать нового участника
      const updatedGroup = await getGroupById(id ?? "");
      setGroup(updatedGroup);
      setAddUserModal(false);
    // eslint-disable-next-line @typescript-eslint/no-explicit-any
    } catch (error: any) {
      if (error.response && error.response.status === 422) {
        setAddMemberMessage('Такой пользователь не найден');
      } else {
        setAddMemberMessage('Ошибка при добавлении');
      }
    }
  }
  // Навигационное меню
  return (
    <PageContainer>
      <PageHeader>
        <HeaderContainer>
          <BackButton onClick={() => navigate(-1)}>←</BackButton>

          <AuthButtons>
            <Link to={'/login'}><LoginBtn >Вход</LoginBtn></Link>
            <Link to={'/register'}><RegisterBtn>Регистрация</RegisterBtn></Link> 
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
              <h2>Описание</h2>
              <SectionContent>{group.description}</SectionContent>
            </Section>
             <Section>
              <SectionHeader>
                <h2>Участники</h2>
                {!addUserModal && ( 
                <SectionButton onClick={() => {
                  setAddUserModal(true);
                  setAddMemberMessage('');
                }}>
                  Добавить участника
                </SectionButton>)}
               
              </SectionHeader>
              {addUserModal && (
                <>
                  <AddMemberBlock>
                    <div>
                      <span>Введите email пользователя</span>
                      <AddMemberInput 
                        type='email'
                        placeholder='name@exaple.com'
                        value={memberEmail}
                        onChange={(e) => setMemberEmail(e.target.value)}
                      />
                    </div>
                    <SectioncControl>
                      <SectionButton onClick={() => setAddUserModal(false)}>Отмена</SectionButton>
                      <SectionButton onClick={handleAddMember}>Добавить</SectionButton>
                    </SectioncControl>
                  </AddMemberBlock>
                  {addMemberMessage}
                </>)}
            <MembersList>
              {
                group.members.map((member) => (
                  <MemberTag key={`member-${member.id}`}>
                    {member.email}
                  </MemberTag>
                ))
              }
            </MembersList>
          </Section>
            <Section>
              <SectionHeader>
                <h2>Список транзакций</h2>
                <SectionButton onClick={() => navigate(`/group/${group.id}/add-transaction`)}>
                  Добавить транзакцию
                </SectionButton>
              </SectionHeader>
              {/* переделать, в групп нет поля транзакций */}
              {transactions.length > 0 ? (
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
                      {transactions.map((transaction) => (
                        <tr key={`transaction-${transaction.id}`}>
                          <td>{transaction.date}</td>
                          <td>{findCategoryNameById(transaction.category_id)}</td>
                          <td>{transaction.type === 'income'? +transaction.amount : -transaction.amount} ₽</td>
                          <td>{findMemberNameById(transaction.user_id)}</td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </TransactionsTable>
              ) : (
                <NoTransactions>Транзакции не добавлены</NoTransactions>
              )}
            </Section>
          </GroupContent>
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