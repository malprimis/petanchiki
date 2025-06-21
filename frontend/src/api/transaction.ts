import axios from 'axios';
import { API } from '../main';
import type { CreateTransaction } from '../types/types';

export const getCategories = async (groupId: string) => {
  try{
  const response = await axios.get(`${API}/groups/${groupId}/categories`);
  return response.data;
  } catch {
  console.log("getCategories error"); 
  }
};

export const addCategory = async (groupId: string, categoryData : string,) => {
   //добавления иконки просто нет в создании категории + она не обязательна на беке, её никогда не будет в беке придобавлении

  try{
  const response = await axios.post(`${API}/groups/${groupId}/categories`,  {'name':categoryData, icon: null} );
  return response.data;
  }
  catch {
    console.log("addCategory error"); 
  }
};

export const addTransaction = async ( transactionData: CreateTransaction) => {
  try{
    const response = await axios.post(`${API}/transactions`, transactionData);
    return response.data;
  }
  catch {
    console.log("addTransaction error");
  }
};

export const getTransactionsInGroup = async (groupId: string) => {
  try{
    const response = await axios.get(`${API}/transactions`, {params:{'group_id' : groupId}});
    return response.data;
  }
  catch {
    console.log("getTransactionsInGroup error");
  }
};