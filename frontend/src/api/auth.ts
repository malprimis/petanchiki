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
  console.log('Login response:', response.data); // Debugging line to check the response structure
  
  localStorage.setItem('access_token', response.data.access_token);
  localStorage.setItem('token_type', response.data.token_type);
  
  axios.defaults.headers.common['Authorization'] = `${response.data.token_type} ${response.data.access_token}`;
  return response.data;
};

export const register = async (email: string, password: string, name: string) => {
  const response = await axios.post(`${API}/auth/register`, {'email': email, 'password': password, 'name' : name} );
  return response.data
};

export const refreshAuthToken = async (refreshToken: string) => {
  const params = new URLSearchParams();
  params.append('token', refreshToken); // имя поля строго "token"!
  const response = await axios.post(
    `${API}/auth/refresh`,
    null,
    { headers: { 'Content-Type': 'application/x-www-form-urlencoded' }, params }
  );
  localStorage.setItem('access_token', response.data.access_token);
  localStorage.setItem('token_type', response.data.token_type);
  axios.defaults.headers.common['Authorization'] = `${response.data.token_type} ${response.data.access_token}`;
  return response.data;
};


//access_token: "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJmZmE2NjUxNS1iZDk0LTQxZTMtYjJhZC1kNGJlOGY5YjEwNGEiLCJleHAiOjE3NTA1MjQ2NDN9.wn6_e0J3cIMtE1g5LpcOQwWWytfnN2TIrf9uXgIuSoo"
//                eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJmZmE2NjUxNS1iZDk0LTQxZTMtYjJhZC1kNGJlOGY5YjEwNGEiLCJleHAiOjE3NTA1MjY0Mjl9.SqBCp79tPfnKptBk_rDsAZIFj08kBqfTLrzt3oAWwlg
//token_type:"bearer"