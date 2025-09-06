import React, { useState, useEffect, useRef } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Settings, History, LogOut, Users, Brain, Mic2 } from 'lucide-react';
import { auth, utils } from '../utils/helpers';
import { VoiceWebSocket } from '../utils/websocket';
import ChatWindow from '../components/ChatWindow';
import VoiceRecorder from '../components/VoiceRecorder';
import SettingsPanel from '../components/SettingsPanel';
import SessionHistory from '../components/SessionHistory';
import ConnectionStatus from '../components/ConnectionStatus';
import toast from 'react-hot-toast';

const Dashboard = ({ onLogout }) => {
  const [messages, setMessages] = useState([]);
  const [isConnected, setIsConnected] = useState(false);
  const [currentSession, setCurrentSession] = useState(null);
  const [speakers, setSpeakers] = useState([]);
  const [showSettings, setShowSettings] = useState(false);
  const [showHistory, setShowHistory] = useState(false);
  const [isRecording, setIsRecording] = useState(false);
  const [connectionStatus, setConnectionStatus] = useState('disconnected');
  
  const wsRef = useRef(null);
  const currentUser = auth.getCurrentUser();

  useEffect(() => {
    initializeSession();
    return () => {
      if (wsRef.current) {
        wsRef.current.disconnect();
      }
    };
  }, []);

  const initializeSession = async () => {
    try {
      const sessionId = utils.generateSessionId();
      setCurrentSession(sessionId);
      
      // Initialize WebSocket connection
      wsRef.current = new VoiceWebSocket(
        sessionId,
        handleWebSocketMessage,
        handleWebSocketError,
        handleWebSocketConnect,
        handleWebSocketDisconnect
      );
      
      wsRef.current.connect();
      
      // Add welcome message
      addMessage({
        id: Date.now(),
        content: `Welcome ${currentUser.username}! Start a conversation by clicking the microphone or typing a message.`,
        speaker: 'System',
        type: 'system',
        timestamp: new Date().toISOString(),
        emotion: 'neutral'
      });
      
    } catch (error) {
      console.error('Failed to initialize session:', error);
      toast.error('Failed to initialize voice session');
    }
  };

  const handleWebSocketMessage = (data) => {
    console.log('WebSocket message received:', data);
    
    switch (data.type) {
      case 'transcription':
        addMessage({
          id: Date.now(),
          content: data.text,
          speaker: data.speaker_id || 'You',
          type: 'transcription',
          timestamp: new Date().toISOString(),
          emotion: data.emotion || 'neutral'
        });
        break;
        
      case 'response':
        addMessage({
          id: Date.now(),
          content: data.text,
          speaker: 'AI Assistant',
          type: 'response',
          timestamp: new Date().toISOString(),
          emotion: data.emotion || 'neutral'
        });
        
        // Play audio response if available
        if (data.audio) {
          playAudioResponse(data.audio);
        }
        break;
        
      case 'speaker_joined':
        setSpeakers(prev => [...prev, data.speaker]);
        toast.success(`${data.speaker.name} joined the conversation`);
        break;
        
      case 'speaker_left':
        setSpeakers(prev => prev.filter(s => s.id !== data.speaker_id));
        toast.info(`Speaker left the conversation`);
        break;
        
      case 'error':
        toast.error(data.message || 'An error occurred');
        break;
        
      default:
        console.log('Unknown message type:', data.type);
    }
  };

  const handleWebSocketConnect = () => {
    setIsConnected(true);
    setConnectionStatus('connected');
    toast.success('Connected to Voice AI Bot');
  };

  const handleWebSocketDisconnect = () => {
    setIsConnected(false);
    setConnectionStatus('disconnected');
    toast.error('Disconnected from Voice AI Bot');
  };

  const handleWebSocketError = (error) => {
    console.error('WebSocket error:', error);
    setConnectionStatus('error');
    toast.error('Connection error occurred');
  };

  const addMessage = (message) => {
    setMessages(prev => [...prev, message]);
  };

  const handleAudioMessage = (audioBlob) => {
    if (wsRef.current) {
      wsRef.current.sendAudio(audioBlob);
      
      // Add placeholder message
      addMessage({
        id: Date.now(),
        content: 'Processing voice input...',
        speaker: 'You',
        type: 'processing',
        timestamp: new Date().toISOString(),
        emotion: 'neutral'
      });
    }
  };

  const handleTextMessage = (text) => {
    if (wsRef.current) {
      wsRef.current.send({
        type: 'text',
        content: text
      });
      
      addMessage({
        id: Date.now(),
        content: text,
        speaker: 'You',
        type: 'text',
        timestamp: new Date().toISOString(),
        emotion: 'neutral'
      });
    }
  };

  const playAudioResponse = (audioData) => {
    try {
      const audio = new Audio(`data:audio/wav;base64,${audioData}`);
      audio.play();
    } catch (error) {
      console.error('Failed to play audio response:', error);
    }
  };

  const handleLogout = () => {
    if (wsRef.current) {
      wsRef.current.disconnect();
    }
    auth.logout();
    onLogout();
  };

  return (
    <div className="min-h-screen flex flex-col">
      {/* Header */}
      <motion.header
        initial={{ opacity: 0, y: -20 }}
        animate={{ opacity: 1, y: 0 }}
        className="glass-panel m-4 p-4 flex items-center justify-between"
      >
        <div className="flex items-center space-x-4">
          <div className="w-10 h-10 bg-gradient-to-r from-blue-600 to-purple-600 rounded-full flex items-center justify-center">
            <Mic2 className="w-6 h-6 text-white" />
          </div>
          <div>
            <h1 className="text-xl font-bold text-gradient">Voice AI Bot</h1>
            <p className="text-sm text-slate-400">Welcome, {currentUser.username}</p>
          </div>
        </div>

        <div className="flex items-center space-x-2">
          {/* Connection Status */}
          <ConnectionStatus status={connectionStatus} />
          
          {/* Speakers Count */}
          <div className="flex items-center space-x-1 text-sm text-slate-400">
            <Users className="w-4 h-4" />
            <span>{speakers.length + 1}</span>
          </div>
          
          {/* Action Buttons */}
          <motion.button
            whileHover={{ scale: 1.05 }}
            whileTap={{ scale: 0.95 }}
            onClick={() => setShowHistory(true)}
            className="btn-secondary p-2"
          >
            <History className="w-5 h-5" />
          </motion.button>
          
          <motion.button
            whileHover={{ scale: 1.05 }}
            whileTap={{ scale: 0.95 }}
            onClick={() => setShowSettings(true)}
            className="btn-secondary p-2"
          >
            <Settings className="w-5 h-5" />
          </motion.button>
          
          <motion.button
            whileHover={{ scale: 1.05 }}
            whileTap={{ scale: 0.95 }}
            onClick={handleLogout}
            className="btn-secondary p-2 text-red-400 hover:text-red-300"
          >
            <LogOut className="w-5 h-5" />
          </motion.button>
        </div>
      </motion.header>

      {/* Main Content */}
      <div className="flex-1 flex flex-col lg:flex-row gap-4 p-4 pt-0">
        {/* Chat Window */}
        <motion.div
          initial={{ opacity: 0, x: -20 }}
          animate={{ opacity: 1, x: 0 }}
          className="flex-1 flex flex-col"
        >
          <ChatWindow
            messages={messages}
            onSendMessage={handleTextMessage}
            isConnected={isConnected}
            speakers={speakers}
          />
        </motion.div>

        {/* Voice Controls */}
        <motion.div
          initial={{ opacity: 0, x: 20 }}
          animate={{ opacity: 1, x: 0 }}
          className="lg:w-80"
        >
          <VoiceRecorder
            onAudioMessage={handleAudioMessage}
            isConnected={isConnected}
            isRecording={isRecording}
            setIsRecording={setIsRecording}
          />
        </motion.div>
      </div>

      {/* Panels */}
      <AnimatePresence>
        {showSettings && (
          <SettingsPanel
            onClose={() => setShowSettings(false)}
            sessionId={currentSession}
          />
        )}
        
        {showHistory && (
          <SessionHistory
            onClose={() => setShowHistory(false)}
            currentSession={currentSession}
          />
        )}
      </AnimatePresence>
    </div>
  );
};

export default Dashboard;
