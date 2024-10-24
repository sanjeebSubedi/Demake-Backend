# Backend API Documentation

## Overview

This document provides an overview of the backend API endpoints implemented so far, including user registration, login, tweet creation, and tweet viewing. The API allows users to register, log in, post tweets, and view existing tweets.

---

## 1. **User Registration**

### Endpoint: `POST /users`

This endpoint allows a new user to create an account by providing their username, email, password, and optional profile information.

#### **Request Body:**

- **Content Type:** `application/json`

| Parameter    | Type   | Description                 | Required |
| ------------ | ------ | --------------------------- | -------- |
| `username`   | string | The user's desired username | Yes      |
| `email`      | string | User's email address        | Yes      |
| `password`   | string | User's password             | Yes      |
| `bio`        | string | Short biography of the user | No       |
| `location`   | string | User's location             | No       |
| `birth_date` | string | User's birth date           | No       |

**Example Request Body:**

```json
{
  "username": "john_doe",
  "email": "john.doe@example.com",
  "password": "mysecurepassword",
  "bio": "Lover of technology",
  "location": "California",
  "birth_date": "1990-05-15"
}
```

**Responses**:
201 - Successful Response:

Content Type: application/json
Example Response

**Responses**:
201 - Successful Response:

Content Type: application/json
Example Response:

```json
{
  "id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
  "username": "john_doe",
  "email": "john.doe@example.com",
  "bio": "Lover of technology",
  "location": "California",
  "birth_date": "1990-05-15",
  "created_at": "2024-10-10T19:55:37.317Z",
  "is_verified": false
}
```

**422 - Validation Error:
**
Content Type: application/json
Example Error Response:

```json
{
  "detail": [
    {
      "loc": ["body", "email"],
      "msg": "Invalid email format",
      "type": "value_error"
    }
  ]
}
```

## 2. User Login

**Endpoint:** `POST /login`  
This endpoint allows an existing user to log in using their email and password. It returns an OAuth2 access token for further authentication.

### Request Body:

- **Content Type:** `application/x-www-form-urlencoded`

| Parameter    | Type   | Description                                      | Required                 |
| ------------ | ------ | ------------------------------------------------ | ------------------------ |
| `username`   | string | The user's email (as username)                   | Yes                      |
| `password`   | string | User's password                                  | Yes                      |
| `grant_type` | string | The grant type for OAuth2 (should be `password`) | No (default: `password`) |

#### **Example Request Body:**

```plaintext
username=john.doe@example.com&password=mysecurepassword
OAuth2 Details:
The login endpoint uses the OAuth2 password grant type to authenticate the user.
Upon successful login, an access token is provided, which must be included in the Authorization header for subsequent API requests (as Bearer <token>).
```

**Responses**:
200 - Successful Response:

Content Type: application/json

**Example Response:
**

```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

**422 - Validation Error:
**
Content Type: application/json
Example Error Response:

```json
{
  "detail": [
    {
      "loc": ["body", "password"],
      "msg": "Incorrect password",
      "type": "value_error"
    }
  ]
}
```

## 3. Tweet Creation

**Endpoint: POST /tweets
**
This endpoint allows authenticated users to create a new tweet.

**Request Headers:
**
Authorization: Bearer <access_token> (obtained from the login endpoint)
Request Body:
Content Type: application/json
Parameter Type Description Required
content string The tweet content Yes
parent_tweet_id string ID of the tweet being replied to (if any) No
Example Request Body:

```json
Copy code
{
"content": "This is my first tweet!",
"parent_tweet_id": null
}
```

**Responses:
**
201 - Tweet Created:

Content Type: application/json
Example Response:

```json
{
  "id": "a9f85f64-5717-4562-b3fc-2c963f66afa6",
  "content": "This is my first tweet!",
  "user_id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
  "created_at": "2024-10-10T20:55:37.317Z"
}
```

**422 - Validation Error:
**

Content Type: application/json
Example Error Response:

```json
{
  "detail": [
    {
      "loc": ["body", "content"],
      "msg": "Tweet content cannot be empty",
      "type": "value_error"
    }
  ]
}
```
