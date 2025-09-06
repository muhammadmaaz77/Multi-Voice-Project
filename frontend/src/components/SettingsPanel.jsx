import React, { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Settings, X, Save, RefreshCw, Mic, Volume2, Globe, Lock } from 'lucide-react';

const SettingsPanel = ({ isOpen, onClose, settings, onUpdateSettings }) => {
  const [localSettings, setLocalSettings] = useState(settings);
  const [activeTab, setActiveTab] = useState('general');

  const handleSave = () => {
    onUpdateSettings(localSettings);
    onClose();
  };

  const updateSetting = (category, key, value) => {
    setLocalSettings(prev => ({
      ...prev,
      [category]: {
        ...prev[category],
        [key]: value
      }
    }));
  };

  const tabs = [
    { id: 'general', label: 'General', icon: Settings },
    { id: 'audio', label: 'Audio', icon: Volume2 },
    { id: 'voice', label: 'Voice', icon: Mic },
    { id: 'privacy', label: 'Privacy', icon: Lock },
  ];

  return (
    <AnimatePresence>
      {isOpen && (
        <>
          {/* Backdrop */}
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="fixed inset-0 bg-black/50 backdrop-blur-sm z-40"
            onClick={onClose}
          />

          {/* Settings panel */}
          <motion.div
            initial={{ opacity: 0, x: 300 }}
            animate={{ opacity: 1, x: 0 }}
            exit={{ opacity: 0, x: 300 }}
            className="fixed right-0 top-0 h-full w-96 bg-slate-900/90 backdrop-blur-xl border-l border-white/10 z-50"
          >
            <div className="flex flex-col h-full">
              {/* Header */}
              <div className="p-6 border-b border-white/10">
                <div className="flex items-center justify-between">
                  <h2 className="text-xl font-semibold text-slate-200">Settings</h2>
                  <motion.button
                    onClick={onClose}
                    whileHover={{ scale: 1.1 }}
                    whileTap={{ scale: 0.9 }}
                    className="p-2 text-slate-400 hover:text-slate-200 rounded-lg hover:bg-white/10"
                  >
                    <X className="w-5 h-5" />
                  </motion.button>
                </div>
              </div>

              {/* Tabs */}
              <div className="flex border-b border-white/10">
                {tabs.map((tab) => {
                  const IconComponent = tab.icon;
                  return (
                    <motion.button
                      key={tab.id}
                      onClick={() => setActiveTab(tab.id)}
                      whileHover={{ backgroundColor: 'rgba(255, 255, 255, 0.05)' }}
                      className={`
                        flex-1 px-4 py-3 text-sm font-medium flex items-center justify-center space-x-2
                        ${activeTab === tab.id 
                          ? 'text-blue-400 border-b-2 border-blue-400' 
                          : 'text-slate-400 hover:text-slate-200'
                        }
                      `}
                    >
                      <IconComponent className="w-4 h-4" />
                      <span className="hidden sm:inline">{tab.label}</span>
                    </motion.button>
                  );
                })}
              </div>

              {/* Content */}
              <div className="flex-1 overflow-y-auto p-6">
                {activeTab === 'general' && (
                  <div className="space-y-6">
                    <div>
                      <label className="block text-sm font-medium text-slate-300 mb-2">
                        Theme
                      </label>
                      <select
                        value={localSettings.general?.theme || 'dark'}
                        onChange={(e) => updateSetting('general', 'theme', e.target.value)}
                        className="input-field"
                      >
                        <option value="dark">Dark</option>
                        <option value="light">Light</option>
                        <option value="auto">Auto</option>
                      </select>
                    </div>

                    <div>
                      <label className="block text-sm font-medium text-slate-300 mb-2">
                        Language
                      </label>
                      <select
                        value={localSettings.general?.language || 'en'}
                        onChange={(e) => updateSetting('general', 'language', e.target.value)}
                        className="input-field"
                      >
                        <option value="en">English</option>
                        <option value="es">Spanish</option>
                        <option value="fr">French</option>
                        <option value="de">German</option>
                      </select>
                    </div>

                    <div className="flex items-center justify-between">
                      <span className="text-sm font-medium text-slate-300">Auto-save conversations</span>
                      <motion.button
                        onClick={() => updateSetting('general', 'autoSave', !localSettings.general?.autoSave)}
                        className={`
                          relative w-12 h-6 rounded-full transition-colors
                          ${localSettings.general?.autoSave ? 'bg-blue-500' : 'bg-slate-600'}
                        `}
                      >
                        <motion.div
                          animate={{
                            x: localSettings.general?.autoSave ? 24 : 2,
                          }}
                          className="absolute top-1 w-4 h-4 bg-white rounded-full"
                        />
                      </motion.button>
                    </div>
                  </div>
                )}

                {activeTab === 'audio' && (
                  <div className="space-y-6">
                    <div>
                      <label className="block text-sm font-medium text-slate-300 mb-2">
                        Output Volume
                      </label>
                      <input
                        type="range"
                        min="0"
                        max="100"
                        value={localSettings.audio?.outputVolume || 80}
                        onChange={(e) => updateSetting('audio', 'outputVolume', parseInt(e.target.value))}
                        className="w-full accent-blue-500"
                      />
                      <span className="text-xs text-slate-400">{localSettings.audio?.outputVolume || 80}%</span>
                    </div>

                    <div>
                      <label className="block text-sm font-medium text-slate-300 mb-2">
                        Input Sensitivity
                      </label>
                      <input
                        type="range"
                        min="0"
                        max="100"
                        value={localSettings.audio?.inputSensitivity || 50}
                        onChange={(e) => updateSetting('audio', 'inputSensitivity', parseInt(e.target.value))}
                        className="w-full accent-blue-500"
                      />
                      <span className="text-xs text-slate-400">{localSettings.audio?.inputSensitivity || 50}%</span>
                    </div>

                    <div className="flex items-center justify-between">
                      <span className="text-sm font-medium text-slate-300">Noise Reduction</span>
                      <motion.button
                        onClick={() => updateSetting('audio', 'noiseReduction', !localSettings.audio?.noiseReduction)}
                        className={`
                          relative w-12 h-6 rounded-full transition-colors
                          ${localSettings.audio?.noiseReduction ? 'bg-blue-500' : 'bg-slate-600'}
                        `}
                      >
                        <motion.div
                          animate={{
                            x: localSettings.audio?.noiseReduction ? 24 : 2,
                          }}
                          className="absolute top-1 w-4 h-4 bg-white rounded-full"
                        />
                      </motion.button>
                    </div>

                    <div className="flex items-center justify-between">
                      <span className="text-sm font-medium text-slate-300">Echo Cancellation</span>
                      <motion.button
                        onClick={() => updateSetting('audio', 'echoCancellation', !localSettings.audio?.echoCancellation)}
                        className={`
                          relative w-12 h-6 rounded-full transition-colors
                          ${localSettings.audio?.echoCancellation ? 'bg-blue-500' : 'bg-slate-600'}
                        `}
                      >
                        <motion.div
                          animate={{
                            x: localSettings.audio?.echoCancellation ? 24 : 2,
                          }}
                          className="absolute top-1 w-4 h-4 bg-white rounded-full"
                        />
                      </motion.button>
                    </div>
                  </div>
                )}

                {activeTab === 'voice' && (
                  <div className="space-y-6">
                    <div>
                      <label className="block text-sm font-medium text-slate-300 mb-2">
                        Voice Model
                      </label>
                      <select
                        value={localSettings.voice?.model || 'default'}
                        onChange={(e) => updateSetting('voice', 'model', e.target.value)}
                        className="input-field"
                      >
                        <option value="default">Default</option>
                        <option value="neural">Neural</option>
                        <option value="premium">Premium</option>
                      </select>
                    </div>

                    <div>
                      <label className="block text-sm font-medium text-slate-300 mb-2">
                        Speech Speed
                      </label>
                      <input
                        type="range"
                        min="50"
                        max="200"
                        value={localSettings.voice?.speed || 100}
                        onChange={(e) => updateSetting('voice', 'speed', parseInt(e.target.value))}
                        className="w-full accent-blue-500"
                      />
                      <span className="text-xs text-slate-400">{localSettings.voice?.speed || 100}%</span>
                    </div>

                    <div className="flex items-center justify-between">
                      <span className="text-sm font-medium text-slate-300">Auto-play responses</span>
                      <motion.button
                        onClick={() => updateSetting('voice', 'autoPlay', !localSettings.voice?.autoPlay)}
                        className={`
                          relative w-12 h-6 rounded-full transition-colors
                          ${localSettings.voice?.autoPlay ? 'bg-blue-500' : 'bg-slate-600'}
                        `}
                      >
                        <motion.div
                          animate={{
                            x: localSettings.voice?.autoPlay ? 24 : 2,
                          }}
                          className="absolute top-1 w-4 h-4 bg-white rounded-full"
                        />
                      </motion.button>
                    </div>

                    <div className="flex items-center justify-between">
                      <span className="text-sm font-medium text-slate-300">Voice activation</span>
                      <motion.button
                        onClick={() => updateSetting('voice', 'voiceActivation', !localSettings.voice?.voiceActivation)}
                        className={`
                          relative w-12 h-6 rounded-full transition-colors
                          ${localSettings.voice?.voiceActivation ? 'bg-blue-500' : 'bg-slate-600'}
                        `}
                      >
                        <motion.div
                          animate={{
                            x: localSettings.voice?.voiceActivation ? 24 : 2,
                          }}
                          className="absolute top-1 w-4 h-4 bg-white rounded-full"
                        />
                      </motion.button>
                    </div>
                  </div>
                )}

                {activeTab === 'privacy' && (
                  <div className="space-y-6">
                    <div className="flex items-center justify-between">
                      <span className="text-sm font-medium text-slate-300">Store conversations locally</span>
                      <motion.button
                        onClick={() => updateSetting('privacy', 'storeLocally', !localSettings.privacy?.storeLocally)}
                        className={`
                          relative w-12 h-6 rounded-full transition-colors
                          ${localSettings.privacy?.storeLocally ? 'bg-blue-500' : 'bg-slate-600'}
                        `}
                      >
                        <motion.div
                          animate={{
                            x: localSettings.privacy?.storeLocally ? 24 : 2,
                          }}
                          className="absolute top-1 w-4 h-4 bg-white rounded-full"
                        />
                      </motion.button>
                    </div>

                    <div className="flex items-center justify-between">
                      <span className="text-sm font-medium text-slate-300">Analytics</span>
                      <motion.button
                        onClick={() => updateSetting('privacy', 'analytics', !localSettings.privacy?.analytics)}
                        className={`
                          relative w-12 h-6 rounded-full transition-colors
                          ${localSettings.privacy?.analytics ? 'bg-blue-500' : 'bg-slate-600'}
                        `}
                      >
                        <motion.div
                          animate={{
                            x: localSettings.privacy?.analytics ? 24 : 2,
                          }}
                          className="absolute top-1 w-4 h-4 bg-white rounded-full"
                        />
                      </motion.button>
                    </div>

                    <div>
                      <label className="block text-sm font-medium text-slate-300 mb-2">
                        Data Retention (days)
                      </label>
                      <input
                        type="number"
                        min="1"
                        max="365"
                        value={localSettings.privacy?.dataRetention || 30}
                        onChange={(e) => updateSetting('privacy', 'dataRetention', parseInt(e.target.value))}
                        className="input-field"
                      />
                    </div>

                    <motion.button
                      whileHover={{ scale: 1.02 }}
                      whileTap={{ scale: 0.98 }}
                      className="w-full btn-primary bg-red-500 hover:bg-red-600"
                    >
                      Clear All Data
                    </motion.button>
                  </div>
                )}
              </div>

              {/* Footer */}
              <div className="p-6 border-t border-white/10">
                <div className="flex space-x-3">
                  <motion.button
                    onClick={onClose}
                    whileHover={{ scale: 1.02 }}
                    whileTap={{ scale: 0.98 }}
                    className="flex-1 btn-secondary"
                  >
                    Cancel
                  </motion.button>
                  <motion.button
                    onClick={handleSave}
                    whileHover={{ scale: 1.02 }}
                    whileTap={{ scale: 0.98 }}
                    className="flex-1 btn-primary"
                  >
                    <Save className="w-4 h-4 mr-2" />
                    Save
                  </motion.button>
                </div>
              </div>
            </div>
          </motion.div>
        </>
      )}
    </AnimatePresence>
  );
};

export default SettingsPanel;
