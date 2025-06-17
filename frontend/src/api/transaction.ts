import axios from 'axios';
import { API } from '../main';

export const getCategories = async (groupId: string) => {
  try{
  const response = await axios.get(`${API}/groups/${groupId}/categories`);
  return response.data;
  } catch {
  console.log("getCategories error"); 
  }
};

export const addCategory = async (groupId: string, categoryData : {
  name: string,
  icon?: string //добавления иконки просто нет в создании категории + она не обязательна на беке, её никогда не будет в беке придобавлении
}) => {
  try{
  const response = await axios.post(`${API}/groups/${groupId}/categories`, categoryData);
  return response.data;
  }
  catch {
    console.log("addCategory error"); 
  }

};


export const addTransaction = async (groupId:string, transactionData: {
  amount: number;
  groupId : string;
  categoryId: string;
  date: string;
  description: string;
}) => {
  try{
    const response = await axios.post(`${API}/groups/${groupId}/transactions`, transactionData);
    return response.data;
  }
  catch {
    console.log("addCategory error"); 
  }
};