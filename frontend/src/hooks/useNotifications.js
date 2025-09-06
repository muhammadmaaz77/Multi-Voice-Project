import { useState, useCallback } from 'react';

export const useNotifications = () => {
  const [notifications, setNotifications] = useState([]);

  const addNotification = useCallback((notification) => {
    const id = Date.now() + Math.random();
    const newNotification = {
      id,
      ...notification,
      timestamp: new Date().toISOString()
    };

    setNotifications(prev => [newNotification, ...prev]);

    // Auto-dismiss if specified
    if (notification.autoDismiss) {
      setTimeout(() => {
        dismissNotification(id);
      }, notification.duration || 5000);
    }

    return id;
  }, []);

  const dismissNotification = useCallback((id) => {
    setNotifications(prev => prev.filter(notification => notification.id !== id));
  }, []);

  const clearAllNotifications = useCallback(() => {
    setNotifications([]);
  }, []);

  return {
    notifications,
    addNotification,
    dismissNotification,
    clearAllNotifications
  };
};
