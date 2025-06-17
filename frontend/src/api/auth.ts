interface AuthResponse {
  token: string;
  user: {
    id: string;
    email: string;
    name?: string;
  };
}


//правильно
export const login = async (email: string, password: string): Promise<AuthResponse> => {
  const response = await fetch('/auth/login', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({ email, password }),
  });
  
  if (!response.ok) {
    throw new Error('Ошибка входа');
  }
  
  return response.json();
};


//правильно
export const register = async (email: string, password: string, name: string): Promise<AuthResponse> => {
  const response = await fetch('/auth/register', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({ email, password, name }),
  });
  
  if (!response.ok) {
    throw new Error('Ошибка регистрации');
  }
  
  return response.json();
};