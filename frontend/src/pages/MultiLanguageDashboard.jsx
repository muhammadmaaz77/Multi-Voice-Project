import React, { useState, useEffect, useRef } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Settings, History, LogOut, Users, Globe, Mic, MicOff, Volume2, VolumeX } from 'lucide-react';
import { auth, utils } from '../utils/helpers';
import useMultiLanguageWebSocket from '../hooks/useMultiLanguageWebSocket';
import { useNotifications } from '../hooks/useNotifications';
import { useSettings } from '../hooks/useSettings';
import ChatWindow from '../components/ChatWindow';
import VoiceRecorder from '../components/VoiceRecorder';
import SettingsPanel from '../components/SettingsPanel';
import SessionHistory from '../components/SessionHistory';
import ConnectionStatus from '../components/ConnectionStatus';
import Notifications from '../components/Notifications';

const LANGUAGES = [
  { code: 'en', name: 'English', flag: '🇺🇸' },
  { code: 'es', name: 'Spanish', flag: '🇪🇸' },
  { code: 'fr', name: 'French', flag: '🇫🇷' },
  { code: 'de', name: 'German', flag: '🇩🇪' },
  { code: 'it', name: 'Italian', flag: '🇮🇹' },
  { code: 'pt', name: 'Portuguese', flag: '🇵🇹' },
  { code: 'ru', name: 'Russian', flag: '🇷🇺' },
  { code: 'zh', name: 'Chinese', flag: '🇨🇳' },
  { code: 'ja', name: 'Japanese', flag: '🇯🇵' },
  { code: 'ko', name: 'Korean', flag: '🇰🇷' },
  { code: 'ar', name: 'Arabic', flag: '🇸🇦' },
  { code: 'hi', name: 'Hindi', flag: '🇮🇳' },
  { code: 'ur', name: 'Urdu', flag: '🇵🇰' },
];

const MultiLanguageDashboard = ({ user, onLogout }) => {
  // Core state
  const [messages, setMessages] = useState([]);
  const [currentSession, setCurrentSession] = useState(null);
  const [speakers, setSpeakers] = useState([]);
  
  // UI state
  const [showSettings, setShowSettings] = useState(false);
  const [showHistory, setShowHistory] = useState(false);
  const [showLanguageSetup, setShowLanguageSetup] = useState(true);
  const [isRecording, setIsRecording] = useState(false);
  
  // Language settings
  const [userLanguage, setUserLanguage] = useState('en'); // User's native language
  const [listenLanguage, setListenLanguage] = useState('en'); // Language they want to hear
  const [roomCode, setRoomCode] = useState('');
  const [isInRoom, setIsInRoom] = useState(false);
  
  // Audio settings
  const [isMuted, setIsMuted] = useState(false);
  const [volume, setVolume] = useState(80);
  
  // Hooks
  const { settings, updateSettings } = useSettings();
  const { notifications, addNotification, dismissNotification } = useNotifications();
  
  // WebSocket connection
  const {
    isConnected,
    messages: wsMessages,
    roomUsers,
    isReconnecting,
    sendMessage: sendWSMessage,
    sendTyping,
    connect,
    disconnect
  } = useMultiLanguageWebSocket(
    isInRoom ? roomCode : null,
    user?.username || 'anonymous', 
    userLanguage
  );

  // Audio processing
  const audioContextRef = useRef(null);
  const mediaRecorderRef = useRef(null);
  const audioChunksRef = useRef([]);

  useEffect(() => {
    // Initialize welcome messages
    setMessages([
      {
        id: 'welcome-1',
        content: `Welcome ${user?.username || 'User'}! Set up your languages to start multi-language conversations.`,
        sender_type: 'bot',
        speaker_name: 'AI Assistant',
        timestamp: new Date().toISOString(),
        emotion: 'neutral'
      }
    ]);
  }, [user]);

  // Sync WebSocket messages
  useEffect(() => {
    if (wsMessages && wsMessages.length > 0) {
      // Convert WebSocket messages to our format
      const formattedMessages = wsMessages.map(msg => ({
        id: msg.id || `ws-${Date.now()}-${Math.random()}`,
        content: msg.content,
        sender_type: msg.type === 'system' ? 'system' : (msg.user_id === (user?.username || 'anonymous') ? 'user' : 'other'),
        speaker_name: msg.user_id || 'Unknown',
        timestamp: msg.timestamp,
        original_content: msg.original_content,
        language: msg.language,
        is_original: msg.is_original,
        emotion: 'neutral'
      }));
      
      setMessages(prev => {
        // Remove welcome messages and replace with WebSocket messages
        const nonWelcomeMessages = prev.filter(m => !m.id.startsWith('welcome'));
        return [...nonWelcomeMessages, ...formattedMessages];
      });
    }
  }, [wsMessages, user]);

  // Update room users from WebSocket
  useEffect(() => {
    if (roomUsers && roomUsers.length > 0) {
      setSpeakers(roomUsers.map(user => ({
        id: user.user_id,
        name: user.user_id,
        language: user.language,
        isActive: true
      })));
    }
  }, [roomUsers]);

  const setupLanguages = () => {
    if (!userLanguage || !listenLanguage) {
      addNotification({
        type: 'error',
        message: 'Please select both your speaking and listening languages',
        duration: 3000,
        autoDismiss: true
      });
      return;
    }

    setShowLanguageSetup(false);
    addNotification({
      type: 'success',
      message: `Languages set: Speaking ${getLanguageName(userLanguage)}, Listening ${getLanguageName(listenLanguage)}`,
      duration: 3000,
      autoDismiss: true
    });
  };

  const joinRoom = () => {
    if (!roomCode.trim()) {
      const newRoomCode = `room-${Date.now().toString(36)}`;
      setRoomCode(newRoomCode);
    }

    if (!userLanguage) {
      addNotification({
        type: 'error',
        title: 'Language Required',
        message: 'Please select your language first',
        duration: 3000,
        autoDismiss: true
      });
      return;
    }

    setIsInRoom(true);
    setShowLanguageSetup(false);
    
    addNotification({
      type: 'success',
      title: 'Joined Room',
      message: `Connected to room: ${roomCode}`,
      duration: 3000,
      autoDismiss: true
    });
  };

  const startVoiceRecording = async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      
      audioContextRef.current = new (window.AudioContext || window.webkitAudioContext)();
      mediaRecorderRef.current = new MediaRecorder(stream);
      audioChunksRef.current = [];

      mediaRecorderRef.current.ondataavailable = (event) => {
        audioChunksRef.current.push(event.data);
      };

      mediaRecorderRef.current.onstop = async () => {
        const audioBlob = new Blob(audioChunksRef.current, { type: 'audio/wav' });
        await sendVoiceMessage(audioBlob);
        stream.getTracks().forEach(track => track.stop());
      };

      mediaRecorderRef.current.start();
      setIsRecording(true);

      addNotification({
        type: 'info',
        message: 'Recording started... Speak now!',
        duration: 2000,
        autoDismiss: true
      });
    } catch (error) {
      console.error('Error starting recording:', error);
      addNotification({
        type: 'error',
        message: 'Failed to start recording. Check microphone permissions.',
        duration: 3000,
        autoDismiss: true
      });
    }
  };

  const stopVoiceRecording = () => {
    if (mediaRecorderRef.current && isRecording) {
      mediaRecorderRef.current.stop();
      setIsRecording(false);
      
      addNotification({
        type: 'info',
        message: 'Processing your voice...',
        duration: 2000,
        autoDismiss: true
      });
    }
  };

  const sendVoiceMessage = async (audioBlob) => {
    try {
      // Voice message functionality will be added in next iteration
      addNotification({
        type: 'info',
        title: 'Voice Recording',
        message: 'Voice message recorded. Voice-to-text integration coming soon!',
        duration: 3000,
        autoDismiss: true
      });
    } catch (error) {
      console.error('Error sending voice message:', error);
      addNotification({
        type: 'error',
        message: 'Failed to send voice message',
        duration: 3000,
        autoDismiss: true
      });
    }
  };

  const sendTextMessage = (text) => {
    if (!text.trim() || !isInRoom) return;

    // Send message through WebSocket
    const success = sendWSMessage(text);
    
    if (!success) {
      addNotification({
        type: 'error',
        title: 'Message Failed',
        message: 'Could not send message. Please check your connection.',
        duration: 3000,
        autoDismiss: true
      });
    }
  };

  const playAudio = async (audioUrl) => {
    try {
      const audio = new Audio(audioUrl);
      audio.volume = volume / 100;
      await audio.play();
    } catch (error) {
      console.error('Error playing audio:', error);
    }
  };

  const getLanguageName = (code) => {
    return LANGUAGES.find(lang => lang.code === code)?.name || code;
  };

  const getLanguageFlag = (code) => {
    return LANGUAGES.find(lang => lang.code === code)?.flag || '🌐';
  };

  if (showLanguageSetup) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-slate-900 via-purple-900 to-slate-900 flex items-center justify-center p-4">
        <motion.div
          initial={{ opacity: 0, scale: 0.9 }}
          animate={{ opacity: 1, scale: 1 }}
          className="bg-white/10 backdrop-blur-md border border-white/20 rounded-2xl p-8 max-w-lg w-full"
        >
          <div className="text-center mb-8">
            <h1 className="text-3xl font-bold text-white mb-2">🌍 Multi-Language Room</h1>
            <p className="text-slate-300">Set up your languages for real-time translation</p>
          </div>

          <div className="space-y-6">
            <div>
              <label className="block text-sm font-medium text-slate-300 mb-3">
                🗣️ I speak (your native language):
              </label>
              <select
                value={userLanguage}
                onChange={(e) => setUserLanguage(e.target.value)}
                className="w-full px-4 py-3 bg-slate-800 border border-slate-600 rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-blue-500"
              >
                {LANGUAGES.map(lang => (
                  <option key={lang.code} value={lang.code}>
                    {lang.flag} {lang.name}
                  </option>
                ))}
              </select>
            </div>

            <div>
              <label className="block text-sm font-medium text-slate-300 mb-3">
                👂 I want to hear (translation language):
              </label>
              <select
                value={listenLanguage}
                onChange={(e) => setListenLanguage(e.target.value)}
                className="w-full px-4 py-3 bg-slate-800 border border-slate-600 rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-blue-500"
              >
                {LANGUAGES.map(lang => (
                  <option key={lang.code} value={lang.code}>
                    {lang.flag} {lang.name}
                  </option>
                ))}
              </select>
            </div>

            <div>
              <label className="block text-sm font-medium text-slate-300 mb-3">
                🏠 Room Code (optional):
              </label>
              <input
                type="text"
                value={roomCode}
                onChange={(e) => setRoomCode(e.target.value)}
                placeholder="Enter room code or leave empty to create new"
                className="w-full px-4 py-3 bg-slate-800 border border-slate-600 rounded-lg text-white placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
            </div>

            <motion.button
              onClick={() => {
                setupLanguages();
                joinRoom();
              }}
              whileHover={{ scale: 1.02 }}
              whileTap={{ scale: 0.98 }}
              className="w-full bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-700 hover:to-purple-700 text-white font-semibold py-4 px-6 rounded-lg transition-all duration-200"
            >
              🚀 Start Multi-Language Chat
            </motion.button>
          </div>
        </motion.div>

        <Notifications
          notifications={notifications}
          onDismiss={dismissNotification}
        />
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-purple-900 to-slate-900 text-white">
      {/* Header */}
      <div className="border-b border-white/10 p-4">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-4">
            <div className="w-10 h-10 bg-gradient-to-r from-blue-500 to-purple-600 rounded-full flex items-center justify-center">
              <Globe className="w-6 h-6 text-white" />
            </div>
            <div>
              <h1 className="text-xl font-bold">Multi-Language Room</h1>
              <p className="text-sm text-slate-400">
                {getLanguageFlag(userLanguage)} Speaking {getLanguageName(userLanguage)} → 
                {getLanguageFlag(listenLanguage)} Hearing {getLanguageName(listenLanguage)}
              </p>
            </div>
          </div>
          
          <div className="flex items-center space-x-2">
            <div className="flex items-center space-x-1 px-3 py-1 bg-white/10 rounded-full text-sm">
              <Users className="w-4 h-4" />
              <span>{speakers.length + 1}</span>
            </div>
            
            <motion.button
              onClick={() => setIsMuted(!isMuted)}
              whileHover={{ scale: 1.1 }}
              whileTap={{ scale: 0.9 }}
              className={`p-2 rounded-full ${isMuted ? 'bg-red-500' : 'bg-green-500'}`}
            >
              {isMuted ? <VolumeX className="w-4 h-4" /> : <Volume2 className="w-4 h-4" />}
            </motion.button>
            
            <motion.button
              onClick={() => setShowSettings(true)}
              whileHover={{ scale: 1.1 }}
              whileTap={{ scale: 0.9 }}
              className="p-2 bg-white/10 rounded-full"
            >
              <Settings className="w-4 h-4" />
            </motion.button>
            
            <motion.button
              onClick={onLogout}
              whileHover={{ scale: 1.1 }}
              whileTap={{ scale: 0.9 }}
              className="p-2 bg-red-500/20 rounded-full"
            >
              <LogOut className="w-4 h-4" />
            </motion.button>
          </div>
        </div>
      </div>

      {/* Main Content */}
      <div className="flex h-[calc(100vh-80px)]">
        {/* Chat Area */}
        <div className="flex-1 flex flex-col">
          <ChatWindow
            messages={messages}
            onSendMessage={sendTextMessage}
            isConnected={isConnected}
            speakers={speakers}
          />
        </div>

        {/* Voice Controls */}
        <div className="w-80 p-4 border-l border-white/10 flex flex-col space-y-4">
          <ConnectionStatus
            isConnected={isConnected}
            connectionType="websocket"
            latency={latency}
            reconnectAttempts={reconnectAttempts}
            serverStatus="healthy"
          />

          {/* Voice Recording */}
          <div className="bg-white/10 backdrop-blur-md border border-white/20 rounded-xl p-6">
            <h3 className="text-lg font-semibold mb-4">🎤 Voice Input</h3>
            
            <div className="flex flex-col items-center space-y-4">
              <motion.button
                onMouseDown={startVoiceRecording}
                onMouseUp={stopVoiceRecording}
                onMouseLeave={stopVoiceRecording}
                whileHover={{ scale: 1.05 }}
                whileTap={{ scale: 0.95 }}
                className={`w-20 h-20 rounded-full flex items-center justify-center transition-all duration-200 ${
                  isRecording 
                    ? 'bg-gradient-to-r from-red-500 to-red-600 animate-pulse' 
                    : 'bg-gradient-to-r from-blue-500 to-purple-600'
                }`}
              >
                {isRecording ? (
                  <MicOff className="w-8 h-8 text-white" />
                ) : (
                  <Mic className="w-8 h-8 text-white" />
                )}
              </motion.button>
              
              <p className="text-sm text-slate-400 text-center">
                {isRecording 
                  ? 'Release to send voice message'
                  : 'Hold to record voice message'
                }
              </p>
            </div>
          </div>

          {/* Volume Control */}
          <div className="bg-white/10 backdrop-blur-md border border-white/20 rounded-xl p-4">
            <h4 className="text-sm font-medium mb-3">🔊 Volume</h4>
            <input
              type="range"
              min="0"
              max="100"
              value={volume}
              onChange={(e) => setVolume(parseInt(e.target.value))}
              className="w-full"
            />
            <div className="text-xs text-slate-400 mt-1">{volume}%</div>
          </div>

          {/* Active Speakers */}
          <div className="bg-white/10 backdrop-blur-md border border-white/20 rounded-xl p-4">
            <h4 className="text-sm font-medium mb-3">👥 Active Speakers</h4>
            <div className="space-y-2">
              <div className="flex items-center space-x-2 text-sm">
                <div className="w-6 h-6 bg-gradient-to-r from-blue-500 to-purple-600 rounded-full flex items-center justify-center text-xs">
                  {user?.username?.charAt(0) || 'Y'}
                </div>
                <span>{user?.username || 'You'}</span>
                <span className="text-xs text-slate-400">
                  {getLanguageFlag(userLanguage)} {getLanguageName(userLanguage)}
                </span>
              </div>
              
              {speakers.map((speaker, index) => (
                <div key={speaker.id} className="flex items-center space-x-2 text-sm">
                  <div className="w-6 h-6 bg-gradient-to-r from-purple-500 to-pink-500 rounded-full flex items-center justify-center text-xs">
                    {speaker.name.charAt(0)}
                  </div>
                  <span>{speaker.name}</span>
                  <span className="text-xs text-slate-400">
                    {getLanguageFlag(speaker.language)} {getLanguageName(speaker.language)}
                  </span>
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>

      {/* Settings Panel */}
      <SettingsPanel
        isOpen={showSettings}
        onClose={() => setShowSettings(false)}
        settings={settings}
        onUpdateSettings={updateSettings}
      />

      {/* Notifications */}
      <Notifications
        notifications={notifications}
        onDismiss={dismissNotification}
      />
    </div>
  );
};

export default MultiLanguageDashboard;
