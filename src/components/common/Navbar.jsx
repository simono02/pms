import React, { useContext, useState, useEffect } from 'react';
import { Link, useNavigate, useLocation } from 'react-router-dom';
import { AuthContext } from '../../context/AuthContext';
import './Navbar.css';

const Navbar = () => {
  const { user, logout } = useContext(AuthContext);
  const navigate = useNavigate();
  const location = useLocation();
  const [currentDateTime, setCurrentDateTime] = useState(new Date());

  useEffect(() => {
    const timer = setInterval(() => {
      setCurrentDateTime(new Date());
    }, 1000); // Update every second

    return () => clearInterval(timer);
  }, []);

  const formatDateTime = (date) => {
    const days = ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat'];
    const months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'];
    
    const dayName = days[date.getDay()];
    const day = date.getDate();
    const month = months[date.getMonth()];
    const hours = date.getHours().toString().padStart(2, '0');
    const minutes = date.getMinutes().toString().padStart(2, '0');
    
    // Add ordinal suffix (st, nd, rd, th)
    const getOrdinal = (n) => {
      const s = ['th', 'st', 'nd', 'rd'];
      const v = n % 100;
      return n + (s[(v - 20) % 10] || s[v] || s[0]);
    };
    
    return `${dayName} ${getOrdinal(day)} ${month} ${hours}:${minutes}`;
  };

  const handleLogout = () => {
    logout();
    navigate('/');
  };

  const isActive = (path) => location.pathname === path;

  const getInitials = (name) => {
    if (!name) return 'U';
    const parts = name.trim().split(' ');
    if (parts.length >= 2) {
      return (parts[0][0] + parts[parts.length - 1][0]).toUpperCase();
    }
    return parts[0][0].toUpperCase();
  };

  // Hide navbar on dashboard pages
  const isDashboardPage = location.pathname === '/dashboard' || 
                          location.pathname === '/staff/dashboard' || 
                          location.pathname === '/admin/dashboard';

  if (isDashboardPage) {
    return null;
  }

  return (
    <nav className="navbar">
      <div className="navbar-container">
        <Link to="/" className="navbar-logo">
          Project Management
        </Link>
        
        <div className="navbar-datetime">
          {formatDateTime(currentDateTime)}
        </div>
        
        <div className="navbar-menu">
          <Link 
            to="/" 
            className={`navbar-link ${isActive('/') ? 'active' : ''}`}
          >
            Home
          </Link>
          
          {user ? (
            <>
              <div className="navbar-user">
                <div className="navbar-avatar">{getInitials(user.name)}</div>
                <span className="navbar-username">{user.name?.split(' ')[0]}</span>
                <button onClick={handleLogout} className="navbar-logout">
                  Logout
                </button>
              </div>
            </>
          ) : (
            <>
              <Link 
                to="/login" 
                className={`navbar-link ${isActive('/login') ? 'active' : ''}`}
              >
                Login
              </Link>
              <Link 
                to="/register" 
                className={`navbar-link ${isActive('/register') ? 'active' : ''}`}
              >
                Register
              </Link>
            </>
          )}
        </div>
      </div>
    </nav>
  );
};

export default Navbar;