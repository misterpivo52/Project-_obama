

### **1. Register**

```http
POST /auth/register/
```

**Response (201)**

```json
{
  "user": {
    "id": "550e8400-e29b-41d4-a716-446655440000",
    "email": "user@example.com",
    "first_name": "Ivan",
    "last_name": "Petrov",
    "country": "Ukraine",
    "phone": "+380123456789",
    "two_factor_enabled": false
  },
  "tokens": {
    "access": "eyJ0eXAiOiJKV1QiLCJhbGc...",
    "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc..."
  }
}
```

---

### **2. Login**

```http
POST /auth/login/
```

**Response (200) — No 2FA**

```json
{
  "user": {
    "id": "550e8400-e29b-41d4-a716-446655440000",
    "email": "user@example.com",
    "first_name": "Ivan",
    "last_name": "Petrov",
    "country": "Ukraine",
    "phone": "+380123456789",
    "two_factor_enabled": false
  },
  "tokens": {
    "access": "eyJ0eXAiOiJKV1QiLCJhbGc...",
    "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc..."
  }
}
```

**Response (200) — 2FA Required**

```json
{
  "requires_2fa": true,
  "user_id": "550e8400-e29b-41d4-a716-446655440000",
  "message": "Verification code sent to Discord"
}
```

---

### **3. Verify 2FA**

```http
POST /auth/verify-2fa/
```

**Response (200)**

```json
{
  "user": {
    "id": "550e8400-e29b-41d4-a716-446655440000",
    "email": "user@example.com",
    "first_name": "Ivan",
    "last_name": "Petrov",
    "country": "Ukraine",
    "phone": "+380123456789",
    "two_factor_enabled": true
  },
  "tokens": {
    "access": "eyJ0eXAiOiJKV1QiLCJhbGc...",
    "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc..."
  }
}
```

---

### **4. Get Profile**

```http
GET /auth/profile/
```

**Headers**

```
Authorization: Bearer <access_token>
```

**Response (200)**

```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "email": "user@example.com",
  "first_name": "Ivan",
  "last_name": "Petrov",
  "country": "Ukraine",
  "phone": "+380123456789",
  "discord_id": "1234567890",
  "two_factor_enabled": true,
  "created_at": "2025-11-10T12:00:00Z",
  "updated_at": "2025-11-10T12:00:00Z"
}
```

---

### **5. Update Profile**

```http
PATCH /auth/profile/update/
```

**Headers**

```
Authorization: Bearer <access_token>
```

**Response (200)**

```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "email": "user@example.com",
  "first_name": "New Name",
  "last_name": "New Lastname",
  "country": "Poland",
  "phone": "+380123456789",
  "discord_id": "1234567890",
  "two_factor_enabled": true,
  "created_at": "2025-11-10T12:00:00Z",
  "updated_at": "2025-11-10T13:00:00Z"
}
```

---

### **6. Logout**

```http
POST /auth/logout/
```

**Headers**

```
Authorization: Bearer <access_token>
```

**Response (200)**

```json
{
  "message": "Successfully logged out"
}
```

---

### **7. Refresh Token**

```http
POST /auth/refresh/
```

**Response (200)**

```json
{
  "access": "eyJ0eXAiOiJKV1QiLCJhbGc..."
}
```

---

### **8. Unlink Discord**

```http
POST /auth/unlink-discord/
```

**Headers**

```
Authorization: Bearer <access_token>
```

**Response (200)**

```json
{
  "message": "Discord account unlinked successfully",
  "two_factor_enabled": false
}
```
