import React from 'react';
import HomePage from './pages/HomePage';
import LoginPage from './pages/LoginPage';
import RegisterPage from './pages/RegisterPage';
import UserDashboardPage from './pages/UserDashboardPage';
import StaffDashboardPage from './pages/StaffDashboardPage';
import AdminDashboardPage from './pages/AdminDashboardPage';
import ProjectPage from './pages/ProjectPage';
import PaymentPage from './pages/PaymentPage';
import NotFoundPage from './pages/NotFoundPage';
import SetupPassword from './pages/SetupPassword';
import ProtectedRoute from './components/auth/ProtectedRoute';

const routes = [
  {
    path: '/',
    element: <HomePage />
  },
  {
    path: '/login',
    element: <LoginPage />
  },
  {
    path: '/register',
    element: <RegisterPage />
  },
  {
    path: '/staff/setup-password',
    element: <SetupPassword />
  },
  {
    path: '/dashboard',
    element: (
      <ProtectedRoute>
        <UserDashboardPage />
      </ProtectedRoute>
    )
  },
  {
    path: '/staff/dashboard',
    element: (
      <ProtectedRoute requiredRole="staff">
        <StaffDashboardPage />
      </ProtectedRoute>
    )
  },
  {
    path: '/admin/dashboard',
    element: (
      <ProtectedRoute requiredRole="admin">
        <AdminDashboardPage />
      </ProtectedRoute>
    )
  },
  {
    path: '/project/:id',
    element: (
      <ProtectedRoute>
        <ProjectPage />
      </ProtectedRoute>
    )
  },
  {
    path: '/payment/:projectId',
    element: (
      <ProtectedRoute>
        <PaymentPage />
      </ProtectedRoute>
    )
  },
  {
    path: '*',
    element: <NotFoundPage />
  }
];

export default routes;