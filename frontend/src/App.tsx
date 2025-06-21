import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import HomePage from '../src/pages/HomePage.tsx/HomePage.tsx';
import GroupNew from  '../src/pages/GroupNew.tsx';
import AddTransaction from '../src/pages/HomePage.tsx/AddTransaction.tsx';
import Reports from '../src/pages/HomePage.tsx/Reports.tsx';
import { LoginPage } from '../src/pages/HomePage.tsx/LoginPage.tsx';
import { RegisterPage } from '../src/pages/HomePage.tsx/RegisterPage.tsx';
import CreateGroup from '../src/pages/CreateGroup.tsx';
import { refreshAuthToken } from './api/auth.ts';
import { useState, useEffect } from 'react';
import axios from 'axios';

axios.interceptors.request.use(config => {
  const token = localStorage.getItem('access_token');
  if (token) {
    config.headers = config.headers || {};
    config.headers['Authorization'] = `Bearer ${token}`;
  }
  return config;
}, error => Promise.reject(error));


function App() {
  const [isAuthenticated, setIsAuthenticated] = useState(false);

  useEffect(() => {
    const restoreAuth = async () => {
      const savedRefreshToken = localStorage.getItem('access_token');
      if (savedRefreshToken && !isAuthenticated) {
        try {
          await refreshAuthToken(savedRefreshToken);
          setIsAuthenticated(true);
        } catch {
          localStorage.removeItem('access_token');
          localStorage.removeItem('refresh_token');
        }
      }
    };
    restoreAuth();
  }, []);

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