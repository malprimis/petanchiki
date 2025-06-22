# API Documentation

This document provides example requests and responses for all API endpoints of the service.

Base URL: `https://{host}/api/v1`

---

## Auth

### Register a new user

**Endpoint:** `POST /auth/register`  
**Description:** Register a new user with email, name, and password. 
**Request Body:**

```json
{
  "email": "user@example.com",
  "name": "Alice",
  "password": "securePassword123"
}
```

**Response (201 Created):**

```json
{
  "id": "123e4567-e89b-12d3-a456-426614174000",
  "email": "user@example.com",
  "name": "Alice",
  "role": "user",
  "is_active": true,
  "created_at": "2025-06-22T10:00:00Z",
  "updated_at": "2025-06-22T10:00:00Z",
  "deleted_at": null
}
```

### Login

**Endpoint:** `POST /auth/login`  
**Description:** Obtain JWT access token using email and password form-data.
**Request (form-data):**

```
username=user@example.com
password=securePassword123
```

**Response (200 OK):**

```json
{
  "access_token": "eyJhbGciOiJI...",
  "token_type": "bearer"
}
```

### Refresh token

**Endpoint:** `POST /auth/refresh`  
**Description:** Refresh an expired access token.
**Request Body:**

```json
{
  "token": "eyJhbGciOiJI..."
}
```

**Response (200 OK):**

```json
{
  "access_token": "eyJhbGciOiJI...",
  "token_type": "bearer"
}
```

---

## Users

All user endpoints require a Bearer token in the `Authorization` header:  
`Authorization: Bearer <access_token>`  
Routes under `/users`. 

### Create a new user

**Endpoint:** `POST /users`  
**Request Body:**

```json
{
  "email": "newuser@example.com",
  "name": "Bob",
  "password": "anotherPass123"
}
```

**Response (201 Created):**

```json
{
  "id": "c56a4180-65aa-42ec-a945-5fd21dec0538",
  "email": "newuser@example.com",
  "name": "Bob",
  "role": "user",
  "is_active": true,
  "created_at": "2025-06-22T11:00:00Z",
  "updated_at": "2025-06-22T11:00:00Z",
  "deleted_at": null
}
```

### List all users (admin-only)

**Endpoint:** `GET /users`  
**Response (200 OK):**

```json
[
  {
    "id": "...",
    "email": "admin@example.com",
    "name": "Admin",
    "role": "admin",
    ...
  },
  {
    "id": "...",
    "email": "user@example.com",
    "name": "Alice",
    "role": "user",
    ...
  }
]
```

### Get current user profile

**Endpoint:** `GET /users/me`  
**Response (200 OK):**

```json
{
  "id": "...",
  "email": "user@example.com",
  "name": "Alice",
  "role": "user",
  ...
}
```

### Get user by ID

**Endpoint:** `GET /users/{user_id}`  
**Response (200 OK):**

```json
{
  "id": "...",
  "email": "someone@example.com",
  "name": "Someone",
  "role": "user",
  ...
}
```

### Update user

**Endpoint:** `PATCH /users/{user_id}`  
**Request Body:**

```json
{
  "name": "New Name",
  "password": "newPassword123"
}
```

**Response (200 OK):**

```json
{
  "id": "...",
  "email": "someone@example.com",
  "name": "New Name",
  "role": "user",
  ...
}
```

### Delete (deactivate) user

**Endpoint:** `DELETE /users/{user_id}`  
**Response (204 No Content)**

---

## Groups

All group endpoints require authorization. Routes under `/groups`.

### Create a new group

**Endpoint:** `POST /groups`  
**Request Body:**

```json
{
  "name": "Trip Planning",
  "description": "Group for our summer trip"
}
```

**Response (201 Created):**

```json
{
  "id": "...",
  "name": "Trip Planning",
  "description": "Group for our summer trip",
  "owner_id": "...",
  "members": [],
  ...
}
```

### List groups for current user

**Endpoint:** `GET /groups`  
**Response (200 OK):**

```json
[
  { "id": "...", "name": "Trip Planning", ... },
  { "id": "...", "name": "Household", ... }
]
```

### Get group by ID

**Endpoint:** `GET /groups/{group_id}`  
**Response (200 OK):**

```json
{
  "id": "...",
  "name": "Trip Planning",
  "description": "Group for our summer trip",
  "owner_id": "...",
  "members": [ { "user_id": "...", "role": "member", ...} ],
  ...
}
```

### Update group

**Endpoint:** `PATCH /groups/{group_id}`  
**Request Body:**

```json
{ "name": "New Group Name" }
```

**Response (200 OK):** updated `GroupRead`

### Delete (deactivate) group

**Endpoint:** `DELETE /groups/{group_id}`  
**Response (204 No Content)**

### Add member to group

**Endpoint:** `POST /groups/{group_id}/members`  
**Request Body:**

```json
{ "email": "invitee@example.com", "role": "member" }
```

**Response (201 Created):**

```json
{ "user_id": "...", "group_id": "...", "role": "member", "joined_at": "..." }
```

### List group members

**Endpoint:** `GET /groups/{group_id}/members`  
**Response (200 OK):**

```json
[ { "user_id": "...", "role": "member", ... }, ... ]
```

### Change member role

**Endpoint:** `PATCH /groups/{group_id}/members/{user_id}`  
**Query Params:** `new_role=admin`  
**Response (200 OK):** updated `UserGroupRead`

### Remove member from group

**Endpoint:** `DELETE /groups/{group_id}/members/{user_id}`  
**Response (204 No Content)**

---

## Categories

Routes under `/groups/{group_id}/categories` and `/categories/{category_id}`.

### Create a new category in a group

**Endpoint:** `POST /groups/{group_id}/categories`  
**Request Body:**

```json
{ "name": "Groceries", "icon": "shopping-cart" }
```

**Response (201 Created):** `CategoryRead`

### List all categories in a group

**Endpoint:** `GET /groups/{group_id}/categories`  
**Response (200 OK):** array of `CategoryRead`

### Update a category

**Endpoint:** `PATCH /categories/{category_id}`  
**Request Body:**

```json
{ "name": "Food" }
```

**Response (200 OK):** updated `CategoryRead`

### Delete a category

**Endpoint:** `DELETE /categories/{category_id}`  
**Response (204 No Content)**

---

## Transactions

Routes under `/transactions`. 

### Create a transaction

**Endpoint:** `POST /transactions`  
**Request Body:**

```json
{
  "group_id": "...",
  "category_id": "...",
  "amount": 42.50,
  "type": "expense",
  "description": "Lunch at cafe",
  "date": "2025-06-22T12:30:00Z"
}
```

**Response (201 Created):** `TransactionRead`

### List transactions in a group

**Endpoint:** `GET /transactions`  
**Query Parameters:**

- `group_id` (required)
    
- `skip`, `limit`
    
- `user_id`, `category_id`, `date_from`, `date_to`, `tx_type`
    

**Example:** `/transactions?group_id=...&limit=50`  
**Response (200 OK):** array of `TransactionRead`

### Get a transaction by ID

**Endpoint:** `GET /transactions/{tx_id}`  
**Response (200 OK):** `TransactionRead`

### Update a transaction

**Endpoint:** `PATCH /transactions/{tx_id}`  
**Request Body:** partial `TransactionUpdate`

### Delete a transaction

**Endpoint:** `DELETE /transactions/{tx_id}`  
**Response (204 No Content)**

---

_Note: All endpoints requiring authentication must include the `Authorization: Bearer <token>` header._