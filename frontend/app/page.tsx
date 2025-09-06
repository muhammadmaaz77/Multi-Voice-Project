'use client'

import { useState, useEffect } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import ChatWindow from '@/components/ChatWindow'
import VoiceRecorder from '@/components/VoiceRecorder'
import SettingsPanel from '@/components/SettingsPanel'
import SessionHistory from '@/components/SessionHistory'
import ParticleBackground from '@/components/ParticleBackground'
import WaveformVisualizer from '@/components/WaveformVisualizer'
import toast, { Toaster } from 'react-hot-toast'

export default function Home() {
  const [isRecording, setIsRecording] = useState(false)
  const [messages, setMessages] = useState([
    {
      id: '1',
      type: 'ai',
      content: 'Hello! I\'m your Voice AI assistant. How can I help you today?',
      timestamp: new Date(),
      emotion: 'happy'
    }
  ])
  const [showSettings, setShowSettings] = useState(false)
  const [showHistory, setShowHistory] = useState(false)
  const [currentSession, setCurrentSession] = useState(null)
  const [audioLevel, setAudioLevel] = useState(0)
  const [isProcessing, setIsProcessing] = useState(false)
  const [selectedLanguage, setSelectedLanguage] = useState('en')
  const [selectedVoice, setSelectedVoice] = useState('default')

  useEffect(() => {
    // Initialize session
    createNewSession()
  }, [])

  const createNewSession = async () => {
    try {
      const response = await fetch('/api/v1/sessions/multiparty', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'X-API-Key': process.env.NEXT_PUBLIC_API_KEY || 'test_api_key'
        },
        body: JSON.stringify({
          participants: [{ name: 'User', role: 'participant' }],
          session_type: 'multiparty'
        })
      })
      
      if (response.ok) {
        const data = await response.json()
        setCurrentSession(data)
        toast.success('New session created!')
      }
    } catch (error) {
      console.error('Error creating session:', error)
      toast.error('Failed to create session')
    }
  }

  const handleVoiceInput = async (audioBlob) => {
    setIsProcessing(true)
    try {
      // Transcribe audio
      const formData = new FormData()
      formData.append('audio', audioBlob, 'recording.wav')
      
      const transcribeResponse = await fetch('/api/v1/stt/transcribe', {
        method: 'POST',
        headers: {
          'X-API-Key': process.env.NEXT_PUBLIC_API_KEY || 'test_api_key'
        },
        body: formData
      })
      
      if (transcribeResponse.ok) {
        const transcription = await transcribeResponse.json()
        
        // Add user message
        const userMessage = {
          id: Date.now().toString(),
          type: 'user',
          content: transcription.transcript,
          timestamp: new Date(),
          audioBlob: audioBlob
        }
        setMessages(prev => [...prev, userMessage])
        
        // Get AI response
        const chatResponse = await fetch('/api/v1/chat', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            'X-API-Key': process.env.NEXT_PUBLIC_API_KEY || 'test_api_key'
          },
          body: JSON.stringify({
            message: transcription.transcript,
            session_id: currentSession?.session_id || 'default'
          })
        })
        
        if (chatResponse.ok) {
          const aiResponse = await chatResponse.json()
          
          // Add AI message
          const aiMessage = {
            id: (Date.now() + 1).toString(),
            type: 'ai',
            content: aiResponse.response,
            timestamp: new Date(),
            emotion: aiResponse.emotion || 'neutral'
          }
          setMessages(prev => [...prev, aiMessage])
          
          // Speak the response
          if ('speechSynthesis' in window) {
            const utterance = new SpeechSynthesisUtterance(aiResponse.response)
            utterance.lang = selectedLanguage
            speechSynthesis.speak(utterance)
          }
        }
      }
    } catch (error) {
      console.error('Error processing voice input:', error)
      toast.error('Failed to process voice input')
    } finally {
      setIsProcessing(false)
    }
  }

  const handleTextInput = async (text) => {
    if (!text.trim()) return
    
    setIsProcessing(true)
    try {
      // Add user message
      const userMessage = {
        id: Date.now().toString(),
        type: 'user',
        content: text,
        timestamp: new Date()
      }
      setMessages(prev => [...prev, userMessage])
      
      // Get AI response
      const response = await fetch('/api/v1/chat', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'X-API-Key': process.env.NEXT_PUBLIC_API_KEY || 'test_api_key'
        },
        body: JSON.stringify({
          message: text,
          session_id: currentSession?.session_id || 'default'
        })
      })
      
      if (response.ok) {
        const aiResponse = await response.json()
        
        // Add AI message
        const aiMessage = {
          id: (Date.now() + 1).toString(),
          type: 'ai',
          content: aiResponse.response,
          timestamp: new Date(),
          emotion: aiResponse.emotion || 'neutral'
        }
        setMessages(prev => [...prev, aiMessage])
      }
    } catch (error) {
      console.error('Error processing text input:', error)
      toast.error('Failed to send message')
    } finally {
      setIsProcessing(false)
    }
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-dark-900 via-primary-900 to-secondary-900 text-white relative overflow-hidden">
      <ParticleBackground />
      
      {/* Header */}
      <motion.header 
        initial={{ y: -100, opacity: 0 }}
        animate={{ y: 0, opacity: 1 }}
        transition={{ duration: 0.8, ease: "easeOut" }}
        className="relative z-10 p-6"
      >
        <div className="max-w-7xl mx-auto flex items-center justify-between">
          <motion.div 
            className="flex items-center space-x-4"
            whileHover={{ scale: 1.05 }}
          >
            <div className="w-12 h-12 bg-gradient-to-r from-primary-500 to-secondary-500 rounded-xl flex items-center justify-center">
              <svg className="w-8 h-8" fill="currentColor" viewBox="0 0 24 24">
                <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm-2 15l-5-5 1.41-1.41L10 14.17l7.59-7.59L19 8l-9 9z"/>
              </svg>
            </div>
            <div>
              <h1 className="text-2xl font-bold bg-gradient-to-r from-white to-gray-300 bg-clip-text text-transparent">
                Voice AI Bot
              </h1>
              <p className="text-sm text-gray-400">Phase 6 - Advanced UI</p>
            </div>
          </motion.div>
          
          <div className="flex items-center space-x-4">
            <motion.button
              whileHover={{ scale: 1.1 }}
              whileTap={{ scale: 0.9 }}
              onClick={() => setShowHistory(!showHistory)}
              className="p-3 rounded-xl glass-morphism hover:bg-white/10 transition-all"
            >
              <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
            </motion.button>
            
            <motion.button
              whileHover={{ scale: 1.1 }}
              whileTap={{ scale: 0.9 }}
              onClick={() => setShowSettings(!showSettings)}
              className="p-3 rounded-xl glass-morphism hover:bg-white/10 transition-all"
            >
              <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z" />
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
              </svg>
            </motion.button>
          </div>
        </div>
      </motion.header>

      {/* Main Content */}
      <div className="max-w-7xl mx-auto px-6 pb-6">
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8 h-[calc(100vh-200px)]">
          {/* Chat Window */}
          <motion.div 
            initial={{ x: -100, opacity: 0 }}
            animate={{ x: 0, opacity: 1 }}
            transition={{ duration: 0.8, delay: 0.2 }}
            className="lg:col-span-2"
          >
            <ChatWindow 
              messages={messages}
              onTextInput={handleTextInput}
              isProcessing={isProcessing}
            />
          </motion.div>
          
          {/* Voice Controls */}
          <motion.div 
            initial={{ x: 100, opacity: 0 }}
            animate={{ x: 0, opacity: 1 }}
            transition={{ duration: 0.8, delay: 0.4 }}
            className="space-y-6"
          >
            {/* Voice Recorder */}
            <div className="glass-morphism rounded-2xl p-6">
              <h3 className="text-lg font-semibold mb-4 text-center">Voice Control</h3>
              <VoiceRecorder 
                onVoiceInput={handleVoiceInput}
                isRecording={isRecording}
                setIsRecording={setIsRecording}
                audioLevel={audioLevel}
                setAudioLevel={setAudioLevel}
              />
            </div>
            
            {/* Waveform Visualizer */}
            <div className="glass-morphism rounded-2xl p-6">
              <h3 className="text-lg font-semibold mb-4 text-center">Audio Visualization</h3>
              <WaveformVisualizer 
                isRecording={isRecording}
                audioLevel={audioLevel}
              />
            </div>
            
            {/* Quick Actions */}
            <div className="glass-morphism rounded-2xl p-6">
              <h3 className="text-lg font-semibold mb-4">Quick Actions</h3>
              <div className="grid grid-cols-2 gap-3">
                <motion.button
                  whileHover={{ scale: 1.02 }}
                  whileTap={{ scale: 0.98 }}
                  onClick={createNewSession}
                  className="p-3 bg-primary-500/20 hover:bg-primary-500/30 rounded-lg transition-all text-sm"
                >
                  New Session
                </motion.button>
                <motion.button
                  whileHover={{ scale: 1.02 }}
                  whileTap={{ scale: 0.98 }}
                  className="p-3 bg-secondary-500/20 hover:bg-secondary-500/30 rounded-lg transition-all text-sm"
                >
                  Clear Chat
                </motion.button>
                <motion.button
                  whileHover={{ scale: 1.02 }}
                  whileTap={{ scale: 0.98 }}
                  className="p-3 bg-accent-500/20 hover:bg-accent-500/30 rounded-lg transition-all text-sm"
                >
                  Export
                </motion.button>
                <motion.button
                  whileHover={{ scale: 1.02 }}
                  whileTap={{ scale: 0.98 }}
                  className="p-3 bg-green-500/20 hover:bg-green-500/30 rounded-lg transition-all text-sm"
                >
                  Share
                </motion.button>
              </div>
            </div>
          </motion.div>
        </div>
      </div>

      {/* Settings Panel */}
      <AnimatePresence>
        {showSettings && (
          <SettingsPanel 
            isOpen={showSettings}
            onClose={() => setShowSettings(false)}
            selectedLanguage={selectedLanguage}
            setSelectedLanguage={setSelectedLanguage}
            selectedVoice={selectedVoice}
            setSelectedVoice={setSelectedVoice}
          />
        )}
      </AnimatePresence>

      {/* Session History */}
      <AnimatePresence>
        {showHistory && (
          <SessionHistory 
            isOpen={showHistory}
            onClose={() => setShowHistory(false)}
            currentSession={currentSession}
          />
        )}
      </AnimatePresence>

      {/* Toast Notifications */}
      <Toaster 
        position="top-right"
        toastOptions={{
          duration: 3000,
          style: {
            background: 'rgba(0, 0, 0, 0.8)',
            color: 'white',
            borderRadius: '12px',
            border: '1px solid rgba(255, 255, 255, 0.1)',
            backdropFilter: 'blur(10px)',
          },
        }}
      />
    </div>
  )
}
