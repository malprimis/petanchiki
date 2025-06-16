import { AuthForm } from '../components/AuthForm.tsx';
import { login } from '../api/auth.ts';

export const LoginForm = () => {
  const handleLogin = async (email: string, password: string) => {
    const response = await login(email, password);
    localStorage.setItem('token', response.token);
  };

  return <AuthForm type="login" onSubmit={handleLogin} />;
};