import axios from 'axios';
import { API } from '../main';
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
  
  const response = await axios.post(`${API}/auth/login`, {'email': email, 'password': password} );
  return response.data
};


//правильно
export const register = async (email: string, password: string, name: string): Promise<AuthResponse> => {
  const response = await axios.post(`${API}/auth/register`, {'email': email, 'password': password, 'name' : name} );
  return response.data
};