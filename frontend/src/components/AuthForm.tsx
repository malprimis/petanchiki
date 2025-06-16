import { useState } from 'react';
import { useNavigate } from 'react-router-dom';

// Правильное определение типов для пропсов
interface AuthFormBaseProps {
  type: 'login' | 'register';
}

interface LoginFormProps extends AuthFormBaseProps {
  type: 'login';
  onSubmit: (email: string, password: string) => Promise<void>;
}

interface RegisterFormProps extends AuthFormBaseProps {
  type: 'register';
  onSubmit: (email: string, password: string, name: string) => Promise<void>;
}

type AuthFormProps = LoginFormProps | RegisterFormProps;

export const AuthForm = (props: AuthFormProps) => {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [name, setName] = useState('');
  const [error, setError] = useState('');
  const navigate = useNavigate();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!email.includes('@')) {
      setError('Некорректный email');
      return;
    }
    
    if (password.length < 6) {
      setError('Пароль должен содержать минимум 6 символов');
      return;
    }

    try {
      if (props.type === 'register') {
        // Для регистрации передаём все три параметра
        await props.onSubmit(email, password, name);
      } else {
        // Для входа передаём только email и password
        await props.onSubmit(email, password);
      }
      navigate('/');
    } catch (err) {
      setError('Ошибка авторизации');
    }
  };

  return (
    <form onSubmit={handleSubmit} className="max-w-md mx-auto mt-8">
      <h2 className="text-2xl font-bold mb-6">
        {props.type === 'login' ? 'Вход' : 'Регистрация'}
      </h2>
      
      {error && <div className="text-red-500 mb-4">{error}</div>}
      
      {props.type === 'register' && (
        <div className="mb-4">
          <label className="block mb-2">Имя</label>
          <input
            type="text"
            value={name}
            onChange={(e) => setName(e.target.value)}
            className="w-full p-2 border rounded"
            required
          />
        </div>
      )}
      
      <div className="mb-4">
        <label className="block mb-2">Email</label>
        <input
          type="email"
          value={email}
          onChange={(e) => setEmail(e.target.value)}
          className="w-full p-2 border rounded"
          required
        />
      </div>
      
      <div className="mb-6">
        <label className="block mb-2">Пароль</label>
        <input
          type="password"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
          className="w-full p-2 border rounded"
          required
          minLength={6}
        />
      </div>
      
      <button
        type="submit"
        className="w-full bg-blue-500 text-white py-2 px-4 rounded hover:bg-blue-600"
      >
        {props.type === 'login' ? 'Войти' : 'Зарегистрироваться'}
      </button>
    </form>
  );
};