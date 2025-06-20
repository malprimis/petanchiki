import { AuthForm } from '../components/AuthForm.tsx';
import { login } from '../api/auth.ts';
import axios from 'axios';

export const LoginForm = () => {
  const handleLogin = async (email: string, password: string) => {
    const response = await login(email, password);
    localStorage.setItem('access_token', response.access_token);
    localStorage.setItem('token_type', response.token_type);
    axios.defaults.headers.common['Authorization'] = `${response.token_type} ${response.access_token}`;
  };

  return <AuthForm type="login" onSubmit={handleLogin} />;
};