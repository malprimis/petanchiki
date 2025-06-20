import axios from 'axios';
import { API } from '../main';

// Define AuthResponse type or import it if defined elsewhere


export const login = async (email: string, password: string)=> {
  const params = new URLSearchParams();
  params.append('username', email);
  params.append('password', password);

  const response = await axios.post(
    `${API}/auth/login`,
    params,
    { headers: { 'Content-Type': 'application/x-www-form-urlencoded' } }
  );
  return response.data;
};

export const register = async (email: string, password: string, name: string) => {
  const response = await axios.post(`${API}/auth/register`, {'email': email, 'password': password, 'name' : name} );
  return response.data
};