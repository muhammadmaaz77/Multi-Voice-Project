import React, { useState, useRef, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Send, Smile } from 'lucide-react';
import ChatBubble from './ChatBubble';
import TypingIndicator from './TypingIndicator';

const ChatWindow = ({ messages, onSendMessage, isConnected, speakers }) => {
  const [inputText, setInputText] = useState('');
  const [isTyping, setIsTyping] = useState(false);
  const messagesEndRef = useRef(null);

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    if (inputText.trim() && isConnected) {
      onSendMessage(inputText);
      setInputText('');
    }
  };

  const handleInputChange = (e) => {
    setInputText(e.target.value);
    
    // Simulate typing indicator
    if (!isTyping && e.target.value.length > 0) {
      setIsTyping(true);
      setTimeout(() => setIsTyping(false), 1000);
    }
  };

  return (
    <div className="glass-panel flex flex-col h-[70vh]">
      {/* Header */}
      <div className="p-4 border-b border-white/10">
        <h2 className="text-lg font-semibold text-slate-200">Conversation</h2>
        <div className="flex items-center space-x-2 mt-2">
          {speakers.length > 0 && (
            <div className="flex items-center space-x-1">
              {speakers.map((speaker, index) => (
                <motion.div
                  key={speaker.id}
                  initial={{ scale: 0 }}
                  animate={{ scale: 1 }}
                  className="w-6 h-6 bg-gradient-to-r from-purple-500 to-pink-500 rounded-full flex items-center justify-center text-xs text-white"
                >
                  {speaker.name.charAt(0)}
                </motion.div>
              ))}
            </div>
          )}
          <span className="text-sm text-slate-400">
            {isConnected ? 'Connected' : 'Disconnected'}
          </span>
        </div>
      </div>

      {/* Messages */}
      <div className="flex-1 overflow-y-auto p-4 space-y-4 scrollbar-hide">
        <AnimatePresence>
          {messages.map((message, index) => (
            <motion.div
              key={message.id}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -20 }}
              transition={{ delay: index * 0.1 }}
            >
              <ChatBubble message={message} />
            </motion.div>
          ))}
        </AnimatePresence>
        
        {isTyping && <TypingIndicator />}
        <div ref={messagesEndRef} />
      </div>

      {/* Input */}
      <div className="p-4 border-t border-white/10">
        <form onSubmit={handleSubmit} className="flex space-x-2">
          <div className="flex-1 relative">
            <input
              type="text"
              value={inputText}
              onChange={handleInputChange}
              placeholder={isConnected ? "Type your message..." : "Connect to start chatting"}
              disabled={!isConnected}
              className="input-field pr-12"
            />
            <button
              type="button"
              className="absolute right-3 top-1/2 transform -translate-y-1/2 text-slate-400 hover:text-slate-300"
            >
              <Smile className="w-5 h-5" />
            </button>
          </div>
          
          <motion.button
            type="submit"
            disabled={!inputText.trim() || !isConnected}
            whileHover={{ scale: 1.05 }}
            whileTap={{ scale: 0.95 }}
            className="btn-primary px-4 py-2 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            <Send className="w-5 h-5" />
          </motion.button>
        </form>
      </div>
    </div>
  );
};

export default ChatWindow;
