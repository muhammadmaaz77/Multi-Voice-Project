import React, { useState } from 'react';
import { motion } from 'framer-motion';
import { Globe, Users, Settings } from 'lucide-react';
import useMultiLanguageWebSocket from '../hooks/useMultiLanguageWebSocket';

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
];

const SimpleMultiLanguageDashboard = ({ user, onLogout }) => {
  const [roomId, setRoomId] = useState('demo-room');
  const [userId, setUserId] = useState(user?.username || 'user-' + Math.random().toString(36).substr(2, 9));
  const [userLanguage, setUserLanguage] = useState('en');
  const [isSetup, setIsSetup] = useState(false);
  const [messageText, setMessageText] = useState('');

  const {
    isConnected,
    messages,
    roomUsers,
    isReconnecting,
    sendMessage,
    sendTyping
  } = useMultiLanguageWebSocket(
    isSetup ? roomId : null,
    userId,
    userLanguage
  );

  const handleJoinRoom = () => {
    if (!roomId || !userId || !userLanguage) return;
    setIsSetup(true);
  };

  const handleSendMessage = (e) => {
    e.preventDefault();
    if (!messageText.trim()) return;
    
    sendMessage(messageText);
    setMessageText('');
  };

  const getLanguageName = (code) => {
    return LANGUAGES.find(lang => lang.code === code)?.name || code;
  };

  const getLanguageFlag = (code) => {
    return LANGUAGES.find(lang => lang.code === code)?.flag || '🌐';
  };

  if (!isSetup) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-slate-900 via-purple-900 to-slate-900 flex items-center justify-center p-4">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="bg-white/10 backdrop-blur-md rounded-2xl p-8 max-w-md w-full"
        >
          <div className="text-center mb-8">
            <Globe className="w-16 h-16 text-blue-400 mx-auto mb-4" />
            <h2 className="text-2xl font-bold text-white mb-2">Multi-Language Chat</h2>
            <p className="text-slate-300">Set up your language preferences</p>
          </div>

          <div className="space-y-4">
            <div>
              <label className="block text-white text-sm font-medium mb-2">Room ID</label>
              <input
                type="text"
                value={roomId}
                onChange={(e) => setRoomId(e.target.value)}
                className="w-full px-4 py-2 bg-white/10 border border-white/20 rounded-lg text-white placeholder-slate-400 focus:outline-none focus:border-blue-400"
                placeholder="Enter room ID"
              />
            </div>

            <div>
              <label className="block text-white text-sm font-medium mb-2">Your Name</label>
              <input
                type="text"
                value={userId}
                onChange={(e) => setUserId(e.target.value)}
                className="w-full px-4 py-2 bg-white/10 border border-white/20 rounded-lg text-white placeholder-slate-400 focus:outline-none focus:border-blue-400"
                placeholder="Enter your name"
              />
            </div>

            <div>
              <label className="block text-white text-sm font-medium mb-2">Your Language</label>
              <select
                value={userLanguage}
                onChange={(e) => setUserLanguage(e.target.value)}
                className="w-full px-4 py-2 bg-white/10 border border-white/20 rounded-lg text-white focus:outline-none focus:border-blue-400"
              >
                {LANGUAGES.map(lang => (
                  <option key={lang.code} value={lang.code} className="bg-slate-800">
                    {lang.flag} {lang.name}
                  </option>
                ))}
              </select>
            </div>

            <motion.button
              onClick={handleJoinRoom}
              whileHover={{ scale: 1.02 }}
              whileTap={{ scale: 0.98 }}
              className="w-full bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-700 hover:to-purple-700 text-white font-semibold py-3 px-6 rounded-lg transition-all duration-200"
            >
              🚀 Join Room
            </motion.button>
          </div>
        </motion.div>
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
              <h1 className="text-xl font-bold">Room: {roomId}</h1>
              <p className="text-sm text-slate-400">
                {getLanguageFlag(userLanguage)} Speaking {getLanguageName(userLanguage)}
              </p>
            </div>
          </div>
          
          <div className="flex items-center space-x-2">
            <div className={`flex items-center space-x-1 px-3 py-1 rounded-full text-sm ${isConnected ? 'bg-green-500/20 text-green-400' : 'bg-red-500/20 text-red-400'}`}>
              <div className={`w-2 h-2 rounded-full ${isConnected ? 'bg-green-400' : 'bg-red-400'}`}></div>
              <span>{isConnected ? 'Connected' : isReconnecting ? 'Reconnecting...' : 'Disconnected'}</span>
            </div>
            
            <div className="flex items-center space-x-1 px-3 py-1 bg-white/10 rounded-full text-sm">
              <Users className="w-4 h-4" />
              <span>{roomUsers.length}</span>
            </div>
          </div>
        </div>
      </div>

      {/* Messages */}
      <div className="flex-1 p-4">
        <div className="max-w-4xl mx-auto">
          <div className="bg-white/5 backdrop-blur-md rounded-2xl h-96 overflow-y-auto p-4 mb-4">
            {messages.length === 0 ? (
              <div className="text-center text-slate-400 mt-20">
                <Globe className="w-16 h-16 mx-auto mb-4 opacity-50" />
                <p>No messages yet. Start the conversation!</p>
              </div>
            ) : (
              messages.map((message) => (
                <div key={message.id} className="mb-4">
                  <div className={`flex ${message.user_id === userId ? 'justify-end' : 'justify-start'}`}>
                    <div className={`max-w-xs lg:max-w-md px-4 py-2 rounded-lg ${
                      message.user_id === userId 
                        ? 'bg-blue-600 text-white' 
                        : message.type === 'system'
                        ? 'bg-yellow-600/20 text-yellow-400'
                        : 'bg-white/10 text-white'
                    }`}>
                      <div className="text-xs opacity-70 mb-1">
                        {message.user_id} • {new Date(message.timestamp).toLocaleTimeString()}
                      </div>
                      <div>{message.content}</div>
                      {message.original_content && message.original_content !== message.content && (
                        <div className="text-xs opacity-70 mt-1">
                          Original: {message.original_content}
                        </div>
                      )}
                    </div>
                  </div>
                </div>
              ))
            )}
          </div>

          {/* Message Input */}
          <form onSubmit={handleSendMessage} className="flex space-x-2">
            <input
              type="text"
              value={messageText}
              onChange={(e) => setMessageText(e.target.value)}
              placeholder="Type your message..."
              className="flex-1 px-4 py-3 bg-white/10 border border-white/20 rounded-lg text-white placeholder-slate-400 focus:outline-none focus:border-blue-400"
              disabled={!isConnected}
            />
            <motion.button
              type="submit"
              disabled={!isConnected || !messageText.trim()}
              whileHover={{ scale: 1.05 }}
              whileTap={{ scale: 0.95 }}
              className="px-6 py-3 bg-blue-600 hover:bg-blue-700 disabled:bg-gray-600 disabled:cursor-not-allowed rounded-lg transition-colors"
            >
              Send
            </motion.button>
          </form>
        </div>
      </div>
    </div>
  );
};

export default SimpleMultiLanguageDashboard;
