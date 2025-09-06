import React, { useState } from 'react';
import { motion } from 'framer-motion';
import { LogIn, Key, User, Mic } from 'lucide-react';
import { auth, utils } from '../utils/helpers';
import { endpoints } from '../utils/api';
import toast from 'react-hot-toast';

const LoginPage = ({ onLogin }) => {
  const [formData, setFormData] = useState({
    username: '',
    apiKey: import.meta.env.VITE_DEFAULT_API_KEY || '',
  });
  const [isLoading, setIsLoading] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setIsLoading(true);

    try {
      // Validate inputs
      if (!formData.username.trim()) {
        toast.error('Please enter a username');
        return;
      }

      if (!utils.isValidApiKey(formData.apiKey)) {
        toast.error('Please enter a valid API key');
        return;
      }

      // Test connection to backend
      await endpoints.health();
      
      // Store credentials
      auth.login(formData.username, formData.apiKey);
      
      toast.success('Welcome to Voice AI Bot!');
      onLogin();
    } catch (error) {
      console.error('Login failed:', error);
      toast.error('Failed to connect to backend. Please check your API key.');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center p-4">
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.6 }}
        className="glass-panel p-8 w-full max-w-md"
      >
        {/* Header */}
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.2, duration: 0.6 }}
          className="text-center mb-8"
        >
          <div className="flex items-center justify-center mb-4">
            <motion.div
              animate={{ rotate: [0, 360] }}
              transition={{ duration: 2, repeat: Infinity, ease: "linear" }}
              className="w-16 h-16 bg-gradient-to-r from-blue-600 to-purple-600 rounded-full flex items-center justify-center"
            >
              <Mic className="w-8 h-8 text-white" />
            </motion.div>
          </div>
          <h1 className="text-3xl font-bold text-gradient mb-2">Voice AI Bot</h1>
          <p className="text-slate-400">Multi-Voice Conversations with AI</p>
        </motion.div>

        {/* Login Form */}
        <motion.form
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.4, duration: 0.6 }}
          onSubmit={handleSubmit}
          className="space-y-6"
        >
          {/* Username Field */}
          <div>
            <label htmlFor="username" className="block text-sm font-medium text-slate-300 mb-2">
              Username
            </label>
            <div className="relative">
              <User className="absolute left-3 top-1/2 transform -translate-y-1/2 w-5 h-5 text-slate-400" />
              <input
                id="username"
                type="text"
                value={formData.username}
                onChange={(e) => setFormData({ ...formData, username: e.target.value })}
                className="input-field pl-12"
                placeholder="Enter your username"
                required
              />
            </div>
          </div>

          {/* API Key Field */}
          <div>
            <label htmlFor="apiKey" className="block text-sm font-medium text-slate-300 mb-2">
              API Key
            </label>
            <div className="relative">
              <Key className="absolute left-3 top-1/2 transform -translate-y-1/2 w-5 h-5 text-slate-400" />
              <input
                id="apiKey"
                type="password"
                value={formData.apiKey}
                onChange={(e) => setFormData({ ...formData, apiKey: e.target.value })}
                className="input-field pl-12"
                placeholder="Enter your API key"
                required
              />
            </div>
          </div>

          {/* Submit Button */}
          <motion.button
            type="submit"
            disabled={isLoading}
            whileHover={{ scale: 1.02 }}
            whileTap={{ scale: 0.98 }}
            className="btn-primary w-full flex items-center justify-center space-x-2"
          >
            {isLoading ? (
              <motion.div
                animate={{ rotate: 360 }}
                transition={{ duration: 1, repeat: Infinity, ease: "linear" }}
                className="w-5 h-5 border-2 border-white border-t-transparent rounded-full"
              />
            ) : (
              <>
                <LogIn className="w-5 h-5" />
                <span>Connect to Voice AI</span>
              </>
            )}
          </motion.button>
        </motion.form>

        {/* Features */}
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.6, duration: 0.6 }}
          className="mt-8 text-center"
        >
          <p className="text-sm text-slate-400 mb-4">Features:</p>
          <div className="grid grid-cols-2 gap-4 text-xs text-slate-500">
            <div>✨ Real-time Voice Chat</div>
            <div>🎭 Multi-Speaker Support</div>
            <div>😊 Emotion Detection</div>
            <div>🧠 Conversation Memory</div>
          </div>
        </motion.div>
      </motion.div>
    </div>
  );
};

export default LoginPage;
