import React from 'react';
import { motion } from 'framer-motion';

const TypingIndicator = () => {
  return (
    <div className="flex items-center space-x-2">
      <div className="bg-gradient-to-r from-gray-700 to-gray-600 px-4 py-2 rounded-2xl flex items-center space-x-1">
        <motion.div
          className="w-2 h-2 bg-slate-400 rounded-full"
          animate={{
            scale: [1, 1.2, 1],
            opacity: [0.5, 1, 0.5],
          }}
          transition={{
            duration: 1,
            repeat: Infinity,
            delay: 0,
          }}
        />
        <motion.div
          className="w-2 h-2 bg-slate-400 rounded-full"
          animate={{
            scale: [1, 1.2, 1],
            opacity: [0.5, 1, 0.5],
          }}
          transition={{
            duration: 1,
            repeat: Infinity,
            delay: 0.2,
          }}
        />
        <motion.div
          className="w-2 h-2 bg-slate-400 rounded-full"
          animate={{
            scale: [1, 1.2, 1],
            opacity: [0.5, 1, 0.5],
          }}
          transition={{
            duration: 1,
            repeat: Infinity,
            delay: 0.4,
          }}
        />
      </div>
      <span className="text-xs text-slate-400">AI is thinking...</span>
    </div>
  );
};

export default TypingIndicator;
