// вообще под снос, будет одна кнопка со скачиванием pdf файла


import { useState, useEffect } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { 
  PieChart, Pie, Cell, 
  LineChart, Line, XAxis, YAxis, 
  CartesianGrid, Tooltip, Legend, 
  ResponsiveContainer 
} from 'recharts';
import { DatePicker, Select, Spin, Alert, Button } from 'antd';
import dayjs from 'dayjs';
import styled from 'styled-components';

const { RangePicker } = DatePicker;
const { Option } = Select;

// Типы данных
interface CategoryData {
  name: string;
  value: number;
}

interface TransactionData {
  date: string;
  amount: number;
}

interface FilterParams {
  startDate: string;
  endDate: string;
  categories: string[];
}

const COLORS = ['#0088FE', '#00C49F', '#FFBB28', '#FF8042', '#8884D8'];

const ReportsPage = () => {
  const navigate = useNavigate();
  // Состояния для данных
  const [categoryData, setCategoryData] = useState<CategoryData[]>([]);
  const [lineData, setLineData] = useState<TransactionData[]>([]);
  const [categories, setCategories] = useState<string[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Состояния для фильтров
  const [dateRange, setDateRange] = useState<[dayjs.Dayjs, dayjs.Dayjs]>([
    dayjs().subtract(1, 'month'),
    dayjs()
  ]);
  const [selectedCategories, setSelectedCategories] = useState<string[]>([]);

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

  // Загрузка данных
  const fetchData = async (params?: FilterParams) => {
    try {
      setLoading(true);
      setError(null);
      
      // Имитация API запросов
      await new Promise(resolve => setTimeout(resolve, 800));
      
      // Моковые данные
      // Нет вообще запроса, а ручка ещё не написана
      const mockCategoryData: CategoryData[] = [
        { name: 'Продукты', value: 400 },
        { name: 'Транспорт', value: 300 },
        { name: 'Жильё', value: 200 },
        { name: 'Развлечения', value: 150 },
        { name: 'Здоровье', value: 100 },
      ];

      const mockLineData: TransactionData[] = [
        { date: '2023-01-01', amount: 400 },
        { date: '2023-01-02', amount: 300 },
        { date: '2023-01-03', amount: 600 },
        { date: '2023-01-04', amount: 200 },
        { date: '2023-01-05', amount: 500 },
      ];

      const mockCategories = ['Продукты', 'Транспорт', 'Жильё', 'Развлечения', 'Здоровье'];

      setCategoryData(mockCategoryData);
      setLineData(mockLineData);
      setCategories(mockCategories);
      
    } catch  {
      setError('Ошибка загрузки данных');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchData();
  }, []);

  // Обработчики фильтров
  const handleDateChange = (
    dates: [dayjs.Dayjs | null, dayjs.Dayjs | null] | null, 
    //dateStrings: [string, string] // вообще не используется 
  ) => {
    if (dates && dates[0] && dates[1]) {
      setDateRange([dates[0], dates[1]]);
    }
  };

  const handleCategoryChange = (value: string[]) => {
    setSelectedCategories(value);
  };

  const applyFilters = () => {
    fetchData({
      startDate: dateRange[0].format('YYYY-MM-DD'),
      endDate: dateRange[1].format('YYYY-MM-DD'),
      categories: selectedCategories
    });
  };

  // Функция для подписей круговой диаграммы
  const renderCustomizedLabel = ({
    name,
    percent
  }: {
    name: string;
    percent: number;
  }) => {
    return `${name} ${(percent * 100).toFixed(0)}%`;
  };

  // Styled components
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

  const ReportsContent = styled.div`
    max-width: 1200px;
    margin: 0 auto;
    padding: 1rem;
  `;

  const ReportsTitle = styled.h1`
    font-size: 2rem;
    font-weight: 700;
    color: #1e293b;
    margin-bottom: 1.5rem;
  `;

  const FiltersSection = styled.div`
    background: white;
    padding: 1.5rem;
    border-radius: 0.5rem;
    box-shadow: 0 1px 3px rgba(0,0,0,0.1);
    margin-bottom: 2rem;
  `;

  const FiltersTitle = styled.h2`
    font-size: 1.25rem;
    font-weight: 600;
    margin-bottom: 1rem;
    color: #1e293b;
  `;

  const FiltersGrid = styled.div`
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
    gap: 1rem;
    align-items: flex-end;
  `;

  const FilterGroup = styled.div`
    display: flex;
    flex-direction: column;

    label {
      font-size: 0.875rem;
      font-weight: 500;
      color: #334155;
      margin-bottom: 0.5rem;
    }
  `;

  const FilterInput = styled.div`
    width: 100%;
  `;

  const ApplyBtn = styled(Button)`
    width: 100%;
    background: #2563eb;
    border: none;

    &:hover {
      background: #1d4ed8;
    }
  `;

  const LoadingSpinner = styled.div`
    display: flex;
    justify-content: center;
    padding: 2rem;
  `;

  const ErrorAlert = styled.div`
    margin-bottom: 2rem;
  `;

  const ChartsGrid = styled.div`
    display: grid;
    grid-template-columns: 1fr;
    gap: 2rem;

    @media (min-width: 1024px) {
      grid-template-columns: 1fr 1fr;
    }
  `;

  const ChartContainer = styled.div`
    background: white;
    padding: 1.5rem;
    border-radius: 0.5rem;
    box-shadow: 0 1px 3px rgba(0,0,0,0.1);

    h2 {
      font-size: 1.25rem;
      font-weight: 600;
      margin-bottom: 1rem;
      color: #1e293b;
    }
  `;

  const ChartWrapper = styled.div`
    height: 400px;
  `;

  return (
    <PageContainer>
      <PageHeader>
        <HeaderContainer>
          <BackButton onClick={handleGoBack}>←</BackButton>
          <LogoLink to="/"><Logo>CashCrew</Logo></LogoLink>
          <MainNav>
            {navItems.map((item) => (
              <NavLink key={item.path} to={item.path}>{item.name}</NavLink>
            ))}
          </MainNav>
          <AuthButtons>
            <LoginBtn>Вход</LoginBtn>
            <RegisterBtn>Регистрация</RegisterBtn>
          </AuthButtons>
        </HeaderContainer>
      </PageHeader>

      <ReportsContent>
        <ReportsTitle>Отчеты</ReportsTitle>
        <FiltersSection>
          <FiltersTitle>Фильтры</FiltersTitle>
          <FiltersGrid>
            <FilterGroup>
              <label>Период</label>
              <FilterInput>
                <RangePicker
                  value={dateRange}
                  onChange={handleDateChange}
                  className="filter-input"
                />
              </FilterInput>
            </FilterGroup>
            <FilterGroup>
              <label>Категории</label>
              <FilterInput>
                <Select
                  mode="multiple"
                  placeholder="Все категории"
                  value={selectedCategories}
                  onChange={handleCategoryChange}
                  className="filter-input"
                >
                  {categories.map(category => (
                    <Option key={category} value={category}>{category}</Option>
                  ))}
                </Select>
              </FilterInput>
            </FilterGroup>
            <FilterGroup>
              <ApplyBtn 
                type="primary" 
                onClick={applyFilters}
                className="apply-btn"
              >
                Применить
              </ApplyBtn>
            </FilterGroup>
          </FiltersGrid>
        </FiltersSection>

        {loading && (
          <LoadingSpinner>
            <Spin size="large" />
          </LoadingSpinner>
        )}

        {error && (
          <ErrorAlert>
            <Alert 
              message={error} 
              type="error" 
              showIcon
              action={
                <Button 
                  size="small" 
                  type="text"
                  onClick={() => fetchData()}
                >
                  Повторить
                </Button>
              }
            />
          </ErrorAlert>
        )}

        {!loading && !error && (
          <ChartsGrid>
            <ChartContainer>
              <h2>Распределение по категориям</h2>
              <ChartWrapper>
                <ResponsiveContainer width="100%" height="100%">
                  <PieChart>
                    <Pie
                      data={categoryData}
                      cx="50%"
                      cy="50%"
                      labelLine={false}
                      outerRadius={80}
                      fill="#8884d8"
                      dataKey="value"
                      label={renderCustomizedLabel}
                    >
                      {categoryData.map((entry, index) => (
                        <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                      ))}
                    </Pie>
                    <Tooltip formatter={(value) => [`${value} ₽`, 'Сумма']} />
                    <Legend />
                  </PieChart>
                </ResponsiveContainer>
              </ChartWrapper>
            </ChartContainer>
            <ChartContainer>
              <h2>Динамика расходов</h2>
              <ChartWrapper>
                <ResponsiveContainer width="100%" height="100%">
                  <LineChart data={lineData}>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis dataKey="date" />
                    <YAxis />
                    <Tooltip formatter={(value) => [`${value} ₽`, 'Сумма']} />
                    <Legend />
                    <Line 
                      type="monotone" 
                      dataKey="amount" 
                      stroke="#8884d8" 
                      strokeWidth={2}
                      activeDot={{ r: 8 }}
                      animationDuration={500}
                    />
                  </LineChart>
                </ResponsiveContainer>
              </ChartWrapper>
            </ChartContainer>
          </ChartsGrid>
        )}
      </ReportsContent>
    </PageContainer>
  );
};

export default ReportsPage;