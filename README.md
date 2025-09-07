# task-management-api
# 📝 Task Management API

A secure and scalable **Task Management REST API** built with **Django REST Framework (DRF)**.  
Supports **user authentication (token-based)**, **task CRUD operations**, filtering, searching, pagination, and user profile management.

---

## 🚀 Features
- User registration & login with token authentication
- Each user can manage only their own tasks
- CRUD operations for tasks
- Filtering tasks by status and due date
- Search tasks by title/description
- Pagination for task lists
- Extra endpoints for:
  - Pending tasks
  - Completed tasks
  - Overdue tasks
  - Mark task as completed
- User profile endpoint with task statistics
- Django Admin integration
- Secure & production-ready settings (CORS, security headers)

---

## 📂 Project Structure
# 1. Register a new user
POST /api/register/
Content-Type: application/json
{
    "username": "johndoe",
    "email": "john@example.com",
    "password": "securepass123",
    "password_confirm": "securepass123",
    "first_name": "John",
    "last_name": "Doe"
}

# Response:
{
    "user": {
        "id": 1,
        "username": "johndoe",
        "email": "john@example.com",
        "first_name": "John",
        "last_name": "Doe"
    },
    "token": "your-auth-token-here",
    "message": "User registered successfully"
}

# 2. Login
POST /api/login/
Content-Type: application/json
{
    "username": "johndoe",
    "password": "securepass123"
}

# Response:
{
    "user": {
        "id": 1,
        "username": "johndoe",
        "email": "john@example.com",
        "first_name": "John",
        "last_name": "Doe"
    },
    "token": "your-auth-token-here",
    "message": "Login successful"
}

# 3. Create a task (requires authentication)
POST /api/tasks/
Authorization: Token your-auth-token-here
Content-Type: application/json
{
    "title": "Complete project documentation",
    "description": "Write comprehensive documentation for the API",
    "status": "pending",
    "due_date": "2024-12-31T23:59:59Z"
}

# 4. Get all tasks (requires authentication)
GET /api/tasks/
Authorization: Token your-auth-token-here

# 5. Get pending tasks only
GET /api/tasks/pending/
Authorization: Token your-auth-token-here

# 6. Filter tasks by status
GET /api/tasks/?status=completed
Authorization: Token your-auth-token-here

# 7. Search tasks by title
GET /api/tasks/?search=project
Authorization: Token your-auth-token-here

# 8. Update a task
PUT /api/tasks/1/
Authorization: Token your-auth-token-here
Content-Type: application/json
{
    "title": "Updated task title",
    "description": "Updated description",
    "status": "completed"
}

# 9. Mark a task as completed
POST /api/tasks/1/complete/
Authorization: Token your-auth-token-here

# 10. Delete a task
DELETE /api/tasks/1/
Authorization: Token your-auth-token-here

# 11. Get user profile
GET /api/profile/
Authorization: Token your-auth-token-here

# 12. Logout
POST /api/logout/
Authorization: Token your-auth-token-here
"""