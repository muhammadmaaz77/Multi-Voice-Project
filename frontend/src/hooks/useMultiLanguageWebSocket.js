import { useState, useEffect, useRef, useCallback } from 'react';

const useMultiLanguageWebSocket = (roomId, userId, userLanguage) => {
  const [socket, setSocket] = useState(null);
  const [isConnected, setIsConnected] = useState(false);
  const [messages, setMessages] = useState([]);
  const [roomUsers, setRoomUsers] = useState([]);
  const [isReconnecting, setIsReconnecting] = useState(false);
  const reconnectAttemptsRef = useRef(0);
  const maxReconnectAttempts = 5;

  const connect = useCallback(() => {
    if (!roomId || !userId || !userLanguage) return;

    try {
      const wsUrl = `ws://localhost:8001/api/v2/ws/multi-language/${roomId}`;
      const ws = new WebSocket(wsUrl);

      ws.onopen = () => {
        console.log('WebSocket connected to room:', roomId);
        
        // Send initial connection message with user info
        ws.send(JSON.stringify({
          user_id: userId,
          language: userLanguage
        }));
        
        setIsConnected(true);
        setIsReconnecting(false);
        reconnectAttemptsRef.current = 0;
      };

      ws.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data);
          console.log('Received message:', data);

          switch (data.type) {
            case 'connected':
              console.log('Successfully connected to room');
              break;
              
            case 'message':
              setMessages(prev => [...prev, {
                id: Date.now() + Math.random(),
                user_id: data.user_id,
                content: data.content,
                original_content: data.original_content,
                language: data.language,
                is_original: data.is_original,
                timestamp: data.timestamp || new Date().toISOString()
              }]);
              break;
              
            case 'user_joined':
              setRoomUsers(prev => {
                const exists = prev.find(u => u.user_id === data.user_id);
                if (!exists) {
                  return [...prev, { user_id: data.user_id, language: data.language }];
                }
                return prev;
              });
              setMessages(prev => [...prev, {
                id: Date.now() + Math.random(),
                type: 'system',
                content: data.message,
                timestamp: new Date().toISOString()
              }]);
              break;
              
            case 'user_left':
              setRoomUsers(prev => prev.filter(u => u.user_id !== data.user_id));
              setMessages(prev => [...prev, {
                id: Date.now() + Math.random(),
                type: 'system',
                content: data.message,
                timestamp: new Date().toISOString()
              }]);
              break;
              
            case 'typing':
              // Handle typing indicators if needed
              break;
              
            default:
              console.log('Unknown message type:', data.type);
          }
        } catch (error) {
          console.error('Error parsing WebSocket message:', error);
        }
      };

      ws.onclose = (event) => {
        console.log('WebSocket closed:', event.code, event.reason);
        setIsConnected(false);
        setSocket(null);

        // Attempt to reconnect if not intentionally closed
        if (event.code !== 1000 && reconnectAttemptsRef.current < maxReconnectAttempts) {
          setIsReconnecting(true);
          reconnectAttemptsRef.current += 1;
          setTimeout(() => connect(), 2000 * reconnectAttemptsRef.current);
        }
      };

      ws.onerror = (error) => {
        console.error('WebSocket error:', error);
        setIsConnected(false);
      };

      setSocket(ws);
    } catch (error) {
      console.error('Failed to create WebSocket connection:', error);
    }
  }, [roomId, userId, userLanguage]);

  const disconnect = useCallback(() => {
    if (socket) {
      socket.close(1000, 'User disconnected');
      setSocket(null);
      setIsConnected(false);
    }
  }, [socket]);

  const sendMessage = useCallback((content) => {
    if (socket && isConnected) {
      const message = {
        type: 'chat',
        content: content,
        timestamp: new Date().toISOString()
      };
      socket.send(JSON.stringify(message));
      return true;
    }
    return false;
  }, [socket, isConnected]);

  const sendTyping = useCallback((isTyping) => {
    if (socket && isConnected) {
      socket.send(JSON.stringify({
        type: 'typing',
        is_typing: isTyping
      }));
    }
  }, [socket, isConnected]);

  // Connect when dependencies change
  useEffect(() => {
    connect();
    return () => disconnect();
  }, [connect, disconnect]);

  // Cleanup on unmount
  useEffect(() => {
    return () => {
      if (socket) {
        socket.close(1000, 'Component unmounted');
      }
    };
  }, [socket]);

  return {
    isConnected,
    messages,
    roomUsers,
    isReconnecting,
    sendMessage,
    sendTyping,
    connect,
    disconnect
  };
};

export default useMultiLanguageWebSocket;
