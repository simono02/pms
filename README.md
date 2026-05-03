# Project Management System

A comprehensive project management system for research projects with role-based access control, file management, and payment processing.

## Features

- **User Management**: Registration, authentication, and role-based access (User, Staff, Admin)
- **Project Management**: Upload PDFs, describe projects, track progress
- **Payment Processing**: Secure payment integration for project completion
- **File Management**: PDF upload, preview, and download functionality
- **Admin Dashboard**: User management, staff allocation, analytics
- **Staff Workspace**: Project assignment and result upload

## Technology Stack

### Frontend
- React 18
- React Router
- Axios for API calls
- CSS3 with responsive design

### Backend
- Python Flask
- SQLAlchemy ORM
- JWT Authentication
- PyPDF2 for PDF processing
- SMTP for email notifications

### Database
- PostgreSQL/MySQL support
- Alembic for migrations

## Project Structure

```
project-management-system/
├── frontend/          # React frontend application
├── backend/           # Python Flask backend
├── database/          # Database schema and migrations
├── docs/             # Documentation
├── docker/           # Docker configuration
└── README.md         # This file
```

## Quick Start

### Prerequisites
- Node.js 16+
- Python 3.8+
- PostgreSQL or MySQL

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd project-management-system
   ```

2. **Set up the backend**
   ```bash
   cd backend
   pip install -r requirements.txt
   python run.py
   ```

3. **Set up the frontend**
   ```bash
   cd frontend
   npm install
   npm start
   ```

4. **Configure environment variables**
   - Copy `.env.example` to `.env` in both frontend and backend
   - Update with your database credentials and API keys

## Documentation

- [API Documentation](docs/API.md)
- [Database Schema](docs/DATABASE.md)
- [Setup Guide](docs/SETUP.md)
- [User Guide](docs/USER_GUIDE.md)

## License

MIT License
