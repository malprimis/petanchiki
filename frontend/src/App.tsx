import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import HomePage from '../src/pages/HomePage.tsx/HomePage.tsx';
import GroupNew from  '../src/pages/GroupNew.tsx';
import AddTransaction from '../src/pages/HomePage.tsx/AddTransaction.tsx';
import Reports from '../src/pages/HomePage.tsx/Reports.tsx';
import { LoginPage } from '../src/pages/HomePage.tsx/LoginPage.tsx';
import { RegisterPage } from '../src/pages/HomePage.tsx/RegisterPage.tsx';
import CreateGroup from '../src/pages/CreateGroup.tsx';

function App() {
  return (
    <Router>
      <Routes>
        {/* Публичные маршруты */}
        <Route path="/login" element={<LoginPage />} />
        <Route path="/register" element={<RegisterPage />} />
        
        {/* Маршруты групп */}
        <Route path="/group/:id" element={<GroupNew />} />
        <Route path="/group/:id/add-transaction" element={<AddTransaction />} />
        
        {/* Создание группы */}
        <Route path="/create-group" element={<CreateGroup />} />
        
        {/* Другие маршруты */}
        <Route path="/" element={<HomePage />} />
        <Route path="/reports" element={<Reports />} />
        
        {/* Fallback route */}
        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>
    </Router>
  );
}

export default App;