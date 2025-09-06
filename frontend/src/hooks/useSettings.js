import { useState, useEffect } from 'react';

const defaultSettings = {
  general: {
    theme: 'dark',
    language: 'en',
    autoSave: true,
  },
  audio: {
    outputVolume: 80,
    inputSensitivity: 50,
    noiseReduction: true,
    echoCancellation: true,
  },
  voice: {
    model: 'default',
    speed: 100,
    autoPlay: true,
    voiceActivation: false,
  },
  privacy: {
    storeLocally: true,
    analytics: false,
    dataRetention: 30,
  },
};

export const useSettings = () => {
  const [settings, setSettings] = useState(defaultSettings);

  useEffect(() => {
    // Load settings from localStorage
    const savedSettings = localStorage.getItem('multivoice_settings');
    if (savedSettings) {
      try {
        const parsed = JSON.parse(savedSettings);
        setSettings(prev => ({
          ...prev,
          ...parsed
        }));
      } catch (error) {
        console.error('Failed to parse saved settings:', error);
      }
    }
  }, []);

  const updateSettings = (newSettings) => {
    setSettings(newSettings);
    localStorage.setItem('multivoice_settings', JSON.stringify(newSettings));
  };

  const resetSettings = () => {
    setSettings(defaultSettings);
    localStorage.removeItem('multivoice_settings');
  };

  return {
    settings,
    updateSettings,
    resetSettings
  };
};
