import React from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { X, CheckCircle, AlertCircle, Info, AlertTriangle } from 'lucide-react';

const Notifications = ({ notifications, onDismiss }) => {
  const getIcon = (type) => {
    switch (type) {
      case 'success':
        return <CheckCircle className="w-5 h-5" />;
      case 'error':
        return <AlertCircle className="w-5 h-5" />;
      case 'warning':
        return <AlertTriangle className="w-5 h-5" />;
      case 'info':
      default:
        return <Info className="w-5 h-5" />;
    }
  };

  const getColorClasses = (type) => {
    switch (type) {
      case 'success':
        return 'bg-green-500/10 border-green-500/20 text-green-300';
      case 'error':
        return 'bg-red-500/10 border-red-500/20 text-red-300';
      case 'warning':
        return 'bg-yellow-500/10 border-yellow-500/20 text-yellow-300';
      case 'info':
      default:
        return 'bg-blue-500/10 border-blue-500/20 text-blue-300';
    }
  };

  return (
    <div className="fixed top-4 right-4 z-50 space-y-2 max-w-md">
      <AnimatePresence>
        {notifications.map((notification) => (
          <motion.div
            key={notification.id}
            initial={{ opacity: 0, x: 300, scale: 0.8 }}
            animate={{ opacity: 1, x: 0, scale: 1 }}
            exit={{ opacity: 0, x: 300, scale: 0.8 }}
            layout
            className={`
              p-4 rounded-lg border backdrop-blur-sm shadow-lg
              ${getColorClasses(notification.type)}
            `}
          >
            <div className="flex items-start space-x-3">
              <div className="flex-shrink-0 mt-0.5">
                {getIcon(notification.type)}
              </div>
              
              <div className="flex-1 min-w-0">
                {notification.title && (
                  <h4 className="text-sm font-medium mb-1">
                    {notification.title}
                  </h4>
                )}
                <p className="text-sm opacity-90">
                  {notification.message}
                </p>
                
                {notification.action && (
                  <motion.button
                    onClick={notification.action.onClick}
                    whileHover={{ scale: 1.05 }}
                    whileTap={{ scale: 0.95 }}
                    className="mt-2 text-xs font-medium underline hover:no-underline"
                  >
                    {notification.action.label}
                  </motion.button>
                )}
              </div>
              
              <motion.button
                onClick={() => onDismiss(notification.id)}
                whileHover={{ scale: 1.1 }}
                whileTap={{ scale: 0.9 }}
                className="flex-shrink-0 text-current opacity-70 hover:opacity-100"
              >
                <X className="w-4 h-4" />
              </motion.button>
            </div>

            {/* Auto-dismiss progress bar */}
            {notification.autoDismiss && (
              <motion.div
                initial={{ scaleX: 1 }}
                animate={{ scaleX: 0 }}
                transition={{ duration: notification.duration || 5, ease: 'linear' }}
                className="absolute bottom-0 left-0 h-1 bg-current rounded-b-lg origin-left"
              />
            )}
          </motion.div>
        ))}
      </AnimatePresence>
    </div>
  );
};

export default Notifications;
