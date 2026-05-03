import React from 'react';
import { BrowserRouter as Router, Routes, Route, useLocation } from 'react-router-dom';
import { AuthProvider } from './context/AuthContext';
import { ThemeProvider } from './context/ThemeContext';
import routes from './routes';
import Navbar from './components/common/Navbar';
import Footer from './components/common/Footer';
import './App.css';

function AppContent() {
  const location = useLocation();

  // Pages that should not show Navbar and Footer
  const authPages = ['/login', '/register', '/staff/setup-password'];
  const shouldShowLayout = !authPages.includes(location.pathname);

  return (
    <div className="app">
      {shouldShowLayout && <Navbar />}
      <main className={`main-content ${!shouldShowLayout ? 'full-height' : ''}`}>
        <Routes>
          {routes.map((route, index) => (
            <Route
              key={index}
              path={route.path}
              element={route.element}
            />
          ))}
        </Routes>
      </main>
      {shouldShowLayout && <Footer />}
    </div>
  );
}

function App() {
  return (
    <ThemeProvider>
      <AuthProvider>
        <Router>
          <AppContent />
        </Router>
      </AuthProvider>
    </ThemeProvider>
  );
}

export default App;