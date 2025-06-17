import { AuthForm } from './AuthForm';
import { register } from '../api/auth.ts';
import { useNavigate } from 'react-router-dom';
import { useState } from 'react'; // Обязательный импорт

export const RegisterForm = () => {
  const navigate = useNavigate();
  const [error, setError] = useState(''); // Теперь useState будет работать

  const handleRegister = async (email: string, password: string, name: string) => {
    try {
      setError('');
      const response = await register(email, password, name);
      localStorage.setItem('token', response.token);
      navigate('/');
    } catch {
      setError('Ошибка регистрации');
    }
  };

  return (
    <>
      <AuthForm type="register" onSubmit={handleRegister} />
      {error && <div className="text-red-500 mt-4">{error}</div>}
    </>
  );
};