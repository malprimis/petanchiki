import { AuthForm } from '../components/AuthForm.tsx';
import { login } from '../api/auth.ts';

export const LoginForm = () => {
  const handleLogin = async (email: string, password: string) => {
    await login(email, password);
  };

  return <AuthForm type="login" onSubmit={handleLogin} />;
};