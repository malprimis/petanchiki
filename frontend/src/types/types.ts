


export  interface Group {
  name: string,
  description: string,
  id: string,
  owner_id: string,
  created_at: string,
  updated_at: string,
  members: Member[],
  is_active: true,
  deleted_at: string
}


export  interface Member {
  name: string,
  email: string,
  id: string,
  role: string,
  created_at: string,
  updated_at: string,
  is_active: boolean,
  deleted_at: string
}

export  interface CreateTransaction {  
  amount: number,
  type: "expense" | "income",
  description: string,
  date: string,
  category_id: string,
  group_id: string
}

export  interface TransactionResponse {  
amount: number,
type: "expense" | "income",
description: string,
date: string,
category_id: string,
group_id: string,
id: string,
user_id: string,
created_at: string,
updated_at: string
}


export  interface Category {
  name: string,
  icon: string,
  id: string,
  group_id: string,
  created_at: string
}

