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
      
    } catch (err) {
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
    dateStrings: [string, string]
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

  return (
    <div className="page-container">
      {/* Верхнее меню */}
      <header className="page-header">
        <div className="header-container">
          <button onClick={handleGoBack} className="back-button">
            ← {/* Символ стрелки */}
          </button>
          
          <Link to="/" className="logo-link">
            <div className="logo">CashCrew</div>
          </Link>

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

      <div className="reports-content">
        <h1>Отчеты</h1>
        
        {/* Блок фильтров */}
        <div className="filters-section">
          <h2>Фильтры</h2>
          
          <div className="filters-grid">
            <div className="filter-group">
              <label>Период</label>
              <RangePicker
                value={dateRange}
                onChange={handleDateChange}
                className="filter-input"
              />
            </div>
            
            <div className="filter-group">
              <label>Категории</label>
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
            </div>
            
            <div className="filter-group">
              <Button 
                type="primary" 
                onClick={applyFilters}
                className="apply-btn"
              >
                Применить
              </Button>
            </div>
          </div>
        </div>

        {/* Состояние загрузки */}
        {loading && (
          <div className="loading-spinner">
            <Spin size="large" />
          </div>
        )}

        {/* Ошибка */}
        {error && (
          <div className="error-alert">
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
          </div>
        )}

        {/* Графики */}
        {!loading && !error && (
          <div className="charts-grid">
            {/* Круговая диаграмма */}
            <div className="chart-container">
              <h2>Распределение по категориям</h2>
              <div className="chart-wrapper">
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
              </div>
            </div>

            {/* Линейный график */}
            <div className="chart-container">
              <h2>Динамика расходов</h2>
              <div className="chart-wrapper">
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
              </div>
            </div>
          </div>
        )}
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
        .reports-content {
          max-width: 1200px;
          margin: 0 auto;
          padding: 1rem;
        }

        .reports-content h1 {
          font-size: 2rem;
          font-weight: 700;
          color: #1e293b;
          margin-bottom: 1.5rem;
        }

        /* Стили для фильтров */
        .filters-section {
          background: white;
          padding: 1.5rem;
          border-radius: 0.5rem;
          box-shadow: 0 1px 3px rgba(0,0,0,0.1);
          margin-bottom: 2rem;
        }

        .filters-section h2 {
          font-size: 1.25rem;
          font-weight: 600;
          margin-bottom: 1rem;
          color: #1e293b;
        }

        .filters-grid {
          display: grid;
          grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
          gap: 1rem;
          align-items: flex-end;
        }

        .filter-group {
          display: flex;
          flex-direction: column;
        }

        .filter-group label {
          font-size: 0.875rem;
          font-weight: 500;
          color: #334155;
          margin-bottom: 0.5rem;
        }

        .filter-input {
          width: 100%;
        }

        .apply-btn {
          width: 100%;
          background: #2563eb;
          border: none;
        }

        .apply-btn:hover {
          background: #1d4ed8;
        }

        /* Стили для загрузки и ошибок */
        .loading-spinner {
          display: flex;
          justify-content: center;
          padding: 2rem;
        }

        .error-alert {
          margin-bottom: 2rem;
        }

        /* Стили для графиков */
        .charts-grid {
          display: grid;
          grid-template-columns: 1fr;
          gap: 2rem;
        }

        @media (min-width: 1024px) {
          .charts-grid {
            grid-template-columns: 1fr 1fr;
          }
        }

        .chart-container {
          background: white;
          padding: 1.5rem;
          border-radius: 0.5rem;
          box-shadow: 0 1px 3px rgba(0,0,0,0.1);
        }

        .chart-container h2 {
          font-size: 1.25rem;
          font-weight: 600;
          margin-bottom: 1rem;
          color: #1e293b;
        }

        .chart-wrapper {
          height: 400px;
        }
      `}</style>
    </div>
  );
};

export default ReportsPage;