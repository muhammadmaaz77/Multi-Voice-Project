import React, { useState, useEffect } from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { motion, AnimatePresence } from 'framer-motion';
import LoginPage from './pages/LoginPage';
import Dashboard from './pages/Dashboard';
import MultiLanguageDashboard from './pages/MultiLanguageDashboard';
import SimpleMultiLanguageDashboard from './pages/SimpleMultiLanguageDashboard';
import { getStoredToken, removeStoredToken } from './utils/helpers';
import { useNotifications } from './hooks/useNotifications';
import Notifications from './components/Notifications';
import './styles/globals.css';

function App() {
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [isLoading, setIsLoading] = useState(true);
  const [user, setUser] = useState(null);
  const { notifications, addNotification, dismissNotification } = useNotifications();

  useEffect(() => {
    // Check for stored authentication
    const checkAuth = async () => {
      const token = getStoredToken();
      if (token) {
        try {
          // Validate token with backend
          const response = await fetch(`${import.meta.env.VITE_API_BASE_URL}/api/auth/me`, {
            headers: {
              'Authorization': `Bearer ${token}`
            }
          });
          
          if (response.ok) {
            const userData = await response.json();
            setUser(userData);
            setIsAuthenticated(true);
            addNotification({
              type: 'success',
              title: 'Welcome back!',
              message: `Logged in as ${userData.username}`,
              duration: 3000,
              autoDismiss: true
            });
          } else {
            // Token is invalid
            removeStoredToken();
            addNotification({
              type: 'warning',
              title: 'Session expired',
              message: 'Please log in again',
              duration: 5000,
              autoDismiss: true
            });
          }
        } catch (error) {
          console.error('Auth check failed:', error);
          removeStoredToken();
          addNotification({
            type: 'error',
            title: 'Connection error',
            message: 'Failed to verify authentication',
            duration: 5000,
            autoDismiss: true
          });
        }
      }
      setIsLoading(false);
    };

    checkAuth();
  }, [addNotification]);

  const handleLogin = (userData, token) => {
    setUser(userData);
    setIsAuthenticated(true);
    addNotification({
      type: 'success',
      title: 'Login successful',
      message: `Welcome, ${userData.username}!`,
      duration: 3000,
      autoDismiss: true
    });
  };

  const handleLogout = () => {
    removeStoredToken();
    setUser(null);
    setIsAuthenticated(false);
    addNotification({
      type: 'info',
      title: 'Logged out',
      message: 'You have been logged out successfully',
      duration: 3000,
      autoDismiss: true
    });
  };

  if (isLoading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-slate-900 via-purple-900 to-slate-900 flex items-center justify-center">
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          className="text-center"
        >
          <motion.div
            animate={{ rotate: 360 }}
            transition={{ duration: 2, repeat: Infinity, ease: "linear" }}
            className="w-16 h-16 border-4 border-blue-400 border-t-transparent rounded-full mx-auto mb-4"
          />
          <h2 className="text-xl font-semibold text-slate-200 mb-2">Loading Multi Voice</h2>
          <p className="text-slate-400">Preparing your voice AI experience...</p>
        </motion.div>
      </div>
    );
  }

  return (
    <Router>
      <div className="min-h-screen bg-gradient-to-br from-slate-900 via-purple-900 to-slate-900">
        <AnimatePresence mode="wait">
          <Routes>
            <Route
              path="/login"
              element={
                !isAuthenticated ? (
                  <motion.div
                    key="login"
                    initial={{ opacity: 0 }}
                    animate={{ opacity: 1 }}
                    exit={{ opacity: 0 }}
                    transition={{ duration: 0.3 }}
                  >
                    <LoginPage onLogin={handleLogin} />
                  </motion.div>
                ) : (
                  <Navigate to="/dashboard" replace />
                )
              }
            />
            
            <Route
              path="/dashboard"
              element={
                isAuthenticated ? (
                  <motion.div
                    key="dashboard"
                    initial={{ opacity: 0 }}
                    animate={{ opacity: 1 }}
                    exit={{ opacity: 0 }}
                    transition={{ duration: 0.3 }}
                  >
                    <Dashboard user={user} onLogout={handleLogout} />
                  </motion.div>
                ) : (
                  <Navigate to="/login" replace />
                )
              }
            />
            
            <Route
              path="/multi-language"
              element={
                <motion.div
                  key="multi-language"
                  initial={{ opacity: 0 }}
                  animate={{ opacity: 1 }}
                  exit={{ opacity: 0 }}
                  transition={{ duration: 0.3 }}
                >
                  <MultiLanguageDashboard user={user || {username: 'Guest'}} onLogout={handleLogout} />
                </motion.div>
              }
            />
            
            <Route
              path="/"
              element={
                <Navigate to={isAuthenticated ? "/dashboard" : "/login"} replace />
              }
            />
          </Routes>
        </AnimatePresence>

        {/* Global notifications */}
        <Notifications
          notifications={notifications}
          onDismiss={dismissNotification}
        />
      </div>
    </Router>
  );
}

export default App;
