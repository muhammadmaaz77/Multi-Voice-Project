import React from 'react';
import { motion } from 'framer-motion';
import { formatDistanceToNow } from 'date-fns';
import { User, Bot, Volume2, VolumeX } from 'lucide-react';
import { cn } from '../utils/helpers';

const ChatBubble = ({ message }) => {
  const isUser = message.sender_type === 'user';
  const isBot = message.sender_type === 'bot';
  
  const getEmotionColor = (emotion) => {
    const emotionColors = {
      happy: 'text-yellow-400',
      sad: 'text-blue-400',
      angry: 'text-red-400',
      excited: 'text-green-400',
      neutral: 'text-slate-400',
      surprised: 'text-purple-400',
      confused: 'text-orange-400',
    };
    return emotionColors[emotion] || 'text-slate-400';
  };

  const getBubbleClass = () => {
    if (isUser) {
      return 'bg-gradient-to-r from-blue-500 to-purple-600 text-white ml-auto';
    } else if (isBot) {
      return 'bg-gradient-to-r from-gray-700 to-gray-600 text-white mr-auto';
    } else {
      return 'bg-gradient-to-r from-green-500 to-teal-600 text-white mr-auto';
    }
  };

  const getIcon = () => {
    if (isUser) return <User className="w-4 h-4" />;
    if (isBot) return <Bot className="w-4 h-4" />;
    return <div className="w-4 h-4 bg-gradient-to-r from-purple-500 to-pink-500 rounded-full" />;
  };

  return (
    <motion.div
      initial={{ opacity: 0, scale: 0.9 }}
      animate={{ opacity: 1, scale: 1 }}
      className={cn(
        'flex flex-col max-w-[70%]',
        isUser ? 'items-end' : 'items-start'
      )}
    >
      {/* Sender info */}
      <div className={cn(
        'flex items-center space-x-2 mb-1',
        isUser ? 'flex-row-reverse space-x-reverse' : ''
      )}>
        {getIcon()}
        <span className="text-sm text-slate-400">
          {message.speaker_name || (isUser ? 'You' : 'AI Assistant')}
        </span>
        {message.emotion && (
          <span className={cn('text-xs', getEmotionColor(message.emotion))}>
            {message.emotion}
          </span>
        )}
      </div>

      {/* Message bubble */}
      <motion.div
        whileHover={{ scale: 1.02 }}
        className={cn(
          'px-4 py-2 rounded-2xl shadow-lg backdrop-blur-sm',
          getBubbleClass()
        )}
      >
        <p className="text-sm leading-relaxed">{message.content}</p>
        
        {/* Audio controls */}
        {message.audio_url && (
          <div className="flex items-center space-x-2 mt-2 pt-2 border-t border-white/20">
            <motion.button
              whileHover={{ scale: 1.1 }}
              whileTap={{ scale: 0.9 }}
              className="text-white/80 hover:text-white"
              onClick={() => {
                const audio = new Audio(message.audio_url);
                audio.play();
              }}
            >
              <Volume2 className="w-4 h-4" />
            </motion.button>
            <span className="text-xs text-white/60">Play audio</span>
          </div>
        )}
      </motion.div>

      {/* Timestamp */}
      <div className="text-xs text-slate-500 mt-1">
        {formatDistanceToNow(new Date(message.timestamp), { addSuffix: true })}
      </div>

      {/* Confidence indicator for AI responses */}
      {!isUser && message.confidence && (
        <motion.div
          initial={{ width: 0 }}
          animate={{ width: `${message.confidence * 100}%` }}
          className="h-1 bg-gradient-to-r from-green-500 to-blue-500 rounded-full mt-1"
          style={{ maxWidth: '100px' }}
        />
      )}
    </motion.div>
  );
};

export default ChatBubble;
