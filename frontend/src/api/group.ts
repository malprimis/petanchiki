import axios from 'axios';
import { API } from '../main';

export const createNewGroup = async (name: string, description: string) => {
  const response = await axios.post(`${API}/groups`, { 'name': name, 'description': description });
  return response.data;
};

export const getGroups = async () => {
  const response = await axios.get(`${API}/groups`);
  return response.data;
};


export const deleteGroup = async (groupId: string) => {
    const response = await axios.delete(`${API}/groups/${groupId}`);
    return response.data;
  };

export const getGroupById = async (groupId: string) => {
  const response = await axios.get(`${API}/groups/${groupId}`);
  return response.data;
};
