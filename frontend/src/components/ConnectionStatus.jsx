import React from 'react';
import { motion } from 'framer-motion';
import { Wifi, WifiOff, Server, AlertCircle, CheckCircle } from 'lucide-react';

const ConnectionStatus = ({ 
  isConnected, 
  connectionType, 
  latency, 
  reconnectAttempts,
  serverStatus 
}) => {
  const getStatusColor = () => {
    if (!isConnected) return 'text-red-400';
    if (latency > 500) return 'text-yellow-400';
    return 'text-green-400';
  };

  const getStatusText = () => {
    if (!isConnected) {
      if (reconnectAttempts > 0) {
        return `Reconnecting... (${reconnectAttempts})`;
      }
      return 'Disconnected';
    }
    return 'Connected';
  };

  const getIcon = () => {
    if (!isConnected) {
      return <WifiOff className="w-4 h-4" />;
    }
    return <Wifi className="w-4 h-4" />;
  };

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      className="glass-panel p-4"
    >
      <div className="flex items-center justify-between">
        <div className="flex items-center space-x-3">
          <motion.div
            animate={{
              scale: isConnected ? [1, 1.2, 1] : 1,
            }}
            transition={{
              duration: 2,
              repeat: isConnected ? Infinity : 0,
              ease: "easeInOut"
            }}
            className={getStatusColor()}
          >
            {getIcon()}
          </motion.div>
          
          <div>
            <div className={`text-sm font-medium ${getStatusColor()}`}>
              {getStatusText()}
            </div>
            {connectionType && (
              <div className="text-xs text-slate-400">
                {connectionType.toUpperCase()}
              </div>
            )}
          </div>
        </div>

        {/* Connection metrics */}
        <div className="flex items-center space-x-4 text-xs text-slate-400">
          {isConnected && latency && (
            <div className="flex items-center space-x-1">
              <div className={`w-2 h-2 rounded-full ${
                latency < 100 ? 'bg-green-400' :
                latency < 300 ? 'bg-yellow-400' : 'bg-red-400'
              }`} />
              <span>{latency}ms</span>
            </div>
          )}
          
          <div className="flex items-center space-x-1">
            {serverStatus === 'healthy' ? (
              <CheckCircle className="w-3 h-3 text-green-400" />
            ) : serverStatus === 'degraded' ? (
              <AlertCircle className="w-3 h-3 text-yellow-400" />
            ) : (
              <AlertCircle className="w-3 h-3 text-red-400" />
            )}
            <Server className="w-3 h-3" />
          </div>
        </div>
      </div>

      {/* Connection quality indicator */}
      {isConnected && (
        <div className="mt-3">
          <div className="flex items-center justify-between text-xs text-slate-400 mb-1">
            <span>Connection Quality</span>
            <span>
              {latency < 100 ? 'Excellent' :
               latency < 300 ? 'Good' :
               latency < 500 ? 'Fair' : 'Poor'}
            </span>
          </div>
          <div className="w-full bg-slate-700 rounded-full h-1">
            <motion.div
              initial={{ width: 0 }}
              animate={{ 
                width: `${Math.max(0, Math.min(100, (1000 - (latency || 0)) / 10))}%`
              }}
              className={`h-1 rounded-full ${
                latency < 100 ? 'bg-green-400' :
                latency < 300 ? 'bg-yellow-400' : 'bg-red-400'
              }`}
            />
          </div>
        </div>
      )}

      {/* Reconnection progress */}
      {!isConnected && reconnectAttempts > 0 && (
        <div className="mt-3">
          <div className="flex items-center space-x-2">
            <motion.div
              animate={{ rotate: 360 }}
              transition={{ duration: 1, repeat: Infinity, ease: "linear" }}
              className="w-4 h-4 border-2 border-blue-400 border-t-transparent rounded-full"
            />
            <span className="text-xs text-slate-400">
              Attempting to reconnect...
            </span>
          </div>
        </div>
      )}
    </motion.div>
  );
};

export default ConnectionStatus;
