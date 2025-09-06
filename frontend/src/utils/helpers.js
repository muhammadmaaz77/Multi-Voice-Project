// Authentication utilities
export const auth = {
  // Check if user is authenticated
  isAuthenticated() {
    return !!localStorage.getItem('voice_ai_api_key');
  },

  // Get current user info
  getCurrentUser() {
    return {
      username: localStorage.getItem('voice_ai_username'),
      apiKey: localStorage.getItem('voice_ai_api_key'),
    };
  },

  // Login user
  login(username, apiKey) {
    localStorage.setItem('voice_ai_username', username);
    localStorage.setItem('voice_ai_api_key', apiKey);
  },

  // Logout user
  logout() {
    localStorage.removeItem('voice_ai_username');
    localStorage.removeItem('voice_ai_api_key');
  },
};

// Utility functions
export const utils = {
  // Format timestamp
  formatTime(timestamp) {
    return new Date(timestamp).toLocaleTimeString('en-US', {
      hour: '2-digit',
      minute: '2-digit',
    });
  },

  // Format date
  formatDate(timestamp) {
    return new Date(timestamp).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
    });
  },

  // Generate unique session ID
  generateSessionId() {
    return `session_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
  },

  // Generate speaker ID
  generateSpeakerId() {
    return `speaker_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
  },

  // Get emotion emoji
  getEmotionEmoji(emotion) {
    const emotions = {
      happy: '😊',
      sad: '😢',
      angry: '😡',
      neutral: '😐',
      excited: '🤩',
      confused: '😕',
      surprised: '😲',
      fear: '😨',
      disgust: '🤢',
    };
    return emotions[emotion?.toLowerCase()] || '😐';
  },

  // Get speaker color
  getSpeakerColor(speakerId) {
    const colors = [
      'from-blue-600 to-blue-700',
      'from-purple-600 to-purple-700',
      'from-green-600 to-green-700',
      'from-red-600 to-red-700',
      'from-yellow-600 to-yellow-700',
      'from-indigo-600 to-indigo-700',
    ];
    
    // Generate consistent color based on speaker ID
    const hash = speakerId.split('').reduce((a, b) => {
      a = ((a << 5) - a) + b.charCodeAt(0);
      return a & a;
    }, 0);
    
    return colors[Math.abs(hash) % colors.length];
  },

  // Download conversation as JSON
  downloadAsJSON(data, filename = 'conversation.json') {
    const blob = new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = filename;
    a.click();
    URL.revokeObjectURL(url);
  },

  // Download conversation as text
  downloadAsText(messages, filename = 'conversation.txt') {
    const text = messages.map(msg => 
      `[${utils.formatTime(msg.timestamp)}] ${msg.speaker}: ${msg.content}`
    ).join('\n');
    
    const blob = new Blob([text], { type: 'text/plain' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = filename;
    a.click();
    URL.revokeObjectURL(url);
  },

  // Validate API key format
  isValidApiKey(apiKey) {
    return apiKey && apiKey.length > 10;
  },

  // Truncate text
  truncate(text, maxLength = 100) {
    if (text.length <= maxLength) return text;
    return text.substring(0, maxLength) + '...';
  },

  // Copy to clipboard
  async copyToClipboard(text) {
    try {
      await navigator.clipboard.writeText(text);
      return true;
    } catch (error) {
      console.error('Failed to copy to clipboard:', error);
      return false;
    }
  },

  // Debounce function
  debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
      const later = () => {
        clearTimeout(timeout);
        func(...args);
      };
      clearTimeout(timeout);
      timeout = setTimeout(later, wait);
    };
  },

  // Throttle function
  throttle(func, limit) {
    let inThrottle;
    return function() {
      const args = arguments;
      const context = this;
      if (!inThrottle) {
        func.apply(context, args);
        inThrottle = true;
        setTimeout(() => inThrottle = false, limit);
      }
    };
  },
};

// Individual function exports for convenience
export const getStoredToken = () => localStorage.getItem('voice_ai_api_key');
export const removeStoredToken = () => {
  localStorage.removeItem('voice_ai_api_key');
  localStorage.removeItem('voice_ai_username');
};

// Tailwind merge utility function
export const cn = (...classes) => {
  return classes.filter(Boolean).join(' ');
};
