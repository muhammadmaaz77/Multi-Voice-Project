import { useState, useEffect, useRef, useCallback } from 'react';
import { connectWebSocket, disconnectWebSocket, sendMessage } from '../utils/websocket';

export const useWebSocket = (token, onMessage, onConnectionChange) => {
  const [isConnected, setIsConnected] = useState(false);
  const [connectionState, setConnectionState] = useState('disconnected');
  const [latency, setLatency] = useState(null);
  const [reconnectAttempts, setReconnectAttempts] = useState(0);
  const wsRef = useRef(null);
  const reconnectTimeoutRef = useRef(null);
  const pingIntervalRef = useRef(null);

  const handleConnect = useCallback(() => {
    setIsConnected(true);
    setConnectionState('connected');
    setReconnectAttempts(0);
    onConnectionChange?.(true);

    // Start ping interval for latency measurement
    pingIntervalRef.current = setInterval(() => {
      if (wsRef.current?.readyState === WebSocket.OPEN) {
        const pingTime = Date.now();
        sendMessage({
          type: 'ping',
          timestamp: pingTime
        });
      }
    }, 10000); // Ping every 10 seconds
  }, [onConnectionChange]);

  const handleDisconnect = useCallback(() => {
    setIsConnected(false);
    setConnectionState('disconnected');
    onConnectionChange?.(false);
    
    if (pingIntervalRef.current) {
      clearInterval(pingIntervalRef.current);
      pingIntervalRef.current = null;
    }
  }, [onConnectionChange]);

  const handleMessage = useCallback((data) => {
    if (data.type === 'pong') {
      const pingTime = data.originalTimestamp;
      const currentTime = Date.now();
      setLatency(currentTime - pingTime);
      return;
    }
    
    onMessage?.(data);
  }, [onMessage]);

  const handleError = useCallback((error) => {
    console.error('WebSocket error:', error);
    setConnectionState('error');
  }, []);

  const connect = useCallback(async () => {
    if (!token) return;

    try {
      setConnectionState('connecting');
      wsRef.current = await connectWebSocket(
        token,
        handleMessage,
        handleConnect,
        handleDisconnect,
        handleError
      );
    } catch (error) {
      console.error('Failed to connect WebSocket:', error);
      setConnectionState('error');
      
      // Attempt to reconnect
      if (reconnectAttempts < 5) {
        setReconnectAttempts(prev => prev + 1);
        reconnectTimeoutRef.current = setTimeout(() => {
          connect();
        }, Math.pow(2, reconnectAttempts) * 1000); // Exponential backoff
      }
    }
  }, [token, handleMessage, handleConnect, handleDisconnect, handleError, reconnectAttempts]);

  const disconnect = useCallback(() => {
    if (reconnectTimeoutRef.current) {
      clearTimeout(reconnectTimeoutRef.current);
      reconnectTimeoutRef.current = null;
    }
    
    if (pingIntervalRef.current) {
      clearInterval(pingIntervalRef.current);
      pingIntervalRef.current = null;
    }
    
    setReconnectAttempts(0);
    disconnectWebSocket();
  }, []);

  const sendWSMessage = useCallback((message) => {
    if (isConnected) {
      sendMessage(message);
    }
  }, [isConnected]);

  useEffect(() => {
    if (token) {
      connect();
    }

    return () => {
      disconnect();
    };
  }, [token]);

  return {
    isConnected,
    connectionState,
    latency,
    reconnectAttempts,
    connect,
    disconnect,
    sendMessage: sendWSMessage
  };
};
