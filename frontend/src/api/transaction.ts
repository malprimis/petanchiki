import axios from 'axios';
import { API } from '../main';
import type { Category, CreateTransaction, TransactionResponse } from '../types/types';

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

interface TransactionsInGroupByType{
  expense: [
    {
      amount: number,
      data: string,
    }
  ]

  ,
  income: [
    {
      value: number,
      category: string,
    }
  ],
  categories_names: string[]
}


export const getTransactionsInGroupByType = async (groupId: string) =>  {
  const categories = await getCategories(groupId);
  const categories_names = categories.map((category: Category) => category.name);
  const transactions = await getTransactionsInGroup(groupId);
  const expenseTransactions: TransactionResponse[] = transactions.filter((transaction: TransactionResponse) => transaction.type === 'expense');
  const incomeTransactions: TransactionResponse[] = transactions.filter((transaction: TransactionResponse) => transaction.type === 'income');
  const expense: { amount: number, data: string }[] = [];
  const income: { value: number, category: string }[] = [];
  expenseTransactions.map((transaction: TransactionResponse) => {
    const foundExpense = expense.find((item) => item.data === transaction.date);
    if (foundExpense) {
      foundExpense.amount += transaction.amount;
    } else {
      expense.push({ amount: transaction.amount, data: transaction.date });
    }


  });

  incomeTransactions.map((transaction: TransactionResponse) => {
    const category_name = findCategoryNameById(transaction.category_id, categories);
    const foundIncome = income.find((item) => item.category === category_name);
    if (foundIncome) {
      foundIncome.value += transaction.amount;
    } else {
      income.push({ value: transaction.amount, category: category_name });
    }
  });

  return {
    expense,
    income,
    categories_names
  } as TransactionsInGroupByType;
};

export const findCategoryNameById = (CategoryId : string, categories: Category[]) => {
  const category = categories.find((category) => category.id === CategoryId);
  return category ? category.name : '';
}