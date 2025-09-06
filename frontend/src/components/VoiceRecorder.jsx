import React, { useState, useRef, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Mic, MicOff, Square, Play, Pause, Volume2 } from 'lucide-react';
import { startRecording, stopRecording, playAudio } from '../utils/websocket';

const VoiceRecorder = ({ isConnected, onVoiceMessage, isRecording, setIsRecording }) => {
  const [audioLevel, setAudioLevel] = useState(0);
  const [recordingTime, setRecordingTime] = useState(0);
  const [lastRecording, setLastRecording] = useState(null);
  const [isPlaying, setIsPlaying] = useState(false);
  const intervalRef = useRef(null);
  const audioContextRef = useRef(null);
  const analyserRef = useRef(null);
  const animationRef = useRef(null);

  useEffect(() => {
    if (isRecording) {
      // Start recording timer
      intervalRef.current = setInterval(() => {
        setRecordingTime(prev => prev + 1);
      }, 1000);
      
      // Start audio level monitoring
      startAudioLevelMonitoring();
    } else {
      // Clear timer
      if (intervalRef.current) {
        clearInterval(intervalRef.current);
        intervalRef.current = null;
      }
      setRecordingTime(0);
      setAudioLevel(0);
      
      // Stop audio monitoring
      stopAudioLevelMonitoring();
    }

    return () => {
      if (intervalRef.current) {
        clearInterval(intervalRef.current);
      }
      stopAudioLevelMonitoring();
    };
  }, [isRecording]);

  const startAudioLevelMonitoring = async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      audioContextRef.current = new (window.AudioContext || window.webkitAudioContext)();
      analyserRef.current = audioContextRef.current.createAnalyser();
      const source = audioContextRef.current.createMediaStreamSource(stream);
      source.connect(analyserRef.current);
      
      analyserRef.current.fftSize = 256;
      const bufferLength = analyserRef.current.frequencyBinCount;
      const dataArray = new Uint8Array(bufferLength);
      
      const updateAudioLevel = () => {
        if (analyserRef.current && isRecording) {
          analyserRef.current.getByteFrequencyData(dataArray);
          const average = dataArray.reduce((a, b) => a + b) / bufferLength;
          setAudioLevel(average / 255);
          animationRef.current = requestAnimationFrame(updateAudioLevel);
        }
      };
      
      updateAudioLevel();
    } catch (error) {
      console.error('Error accessing microphone:', error);
    }
  };

  const stopAudioLevelMonitoring = () => {
    if (animationRef.current) {
      cancelAnimationFrame(animationRef.current);
    }
    if (audioContextRef.current) {
      audioContextRef.current.close();
    }
  };

  const handleStartRecording = async () => {
    if (!isConnected) return;
    
    try {
      await startRecording();
      setIsRecording(true);
    } catch (error) {
      console.error('Failed to start recording:', error);
    }
  };

  const handleStopRecording = async () => {
    try {
      const audioBlob = await stopRecording();
      setIsRecording(false);
      setLastRecording(audioBlob);
      
      // Send to backend
      if (onVoiceMessage) {
        onVoiceMessage(audioBlob);
      }
    } catch (error) {
      console.error('Failed to stop recording:', error);
      setIsRecording(false);
    }
  };

  const handlePlayLastRecording = async () => {
    if (!lastRecording) return;
    
    setIsPlaying(true);
    try {
      await playAudio(lastRecording);
    } catch (error) {
      console.error('Failed to play recording:', error);
    } finally {
      setIsPlaying(false);
    }
  };

  const formatTime = (seconds) => {
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins}:${secs.toString().padStart(2, '0')}`;
  };

  return (
    <div className="glass-panel p-6">
      <h3 className="text-lg font-semibold text-slate-200 mb-4">Voice Input</h3>
      
      <div className="flex flex-col items-center space-y-4">
        {/* Main recording button */}
        <motion.button
          onClick={isRecording ? handleStopRecording : handleStartRecording}
          disabled={!isConnected}
          whileHover={{ scale: 1.05 }}
          whileTap={{ scale: 0.95 }}
          className={`
            relative w-20 h-20 rounded-full flex items-center justify-center
            ${isRecording 
              ? 'bg-gradient-to-r from-red-500 to-red-600' 
              : 'bg-gradient-to-r from-blue-500 to-purple-600'
            }
            disabled:opacity-50 disabled:cursor-not-allowed
            shadow-lg transition-all duration-200
          `}
        >
          {/* Audio level visualization */}
          <AnimatePresence>
            {isRecording && (
              <motion.div
                initial={{ scale: 1 }}
                animate={{ 
                  scale: 1 + audioLevel * 0.5,
                }}
                exit={{ scale: 1 }}
                className="absolute inset-0 rounded-full bg-white/20"
              />
            )}
          </AnimatePresence>
          
          {isRecording ? (
            <Square className="w-8 h-8 text-white" />
          ) : (
            <Mic className="w-8 h-8 text-white" />
          )}
        </motion.button>

        {/* Recording status */}
        <AnimatePresence>
          {isRecording && (
            <motion.div
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -10 }}
              className="text-center"
            >
              <div className="text-red-400 font-semibold">Recording...</div>
              <div className="text-slate-400 text-sm">{formatTime(recordingTime)}</div>
              
              {/* Audio level bars */}
              <div className="flex items-center justify-center space-x-1 mt-2">
                {[...Array(5)].map((_, i) => (
                  <motion.div
                    key={i}
                    className="w-2 bg-red-400 rounded-full"
                    animate={{
                      height: audioLevel > (i * 0.2) ? '20px' : '4px',
                    }}
                    transition={{ duration: 0.1 }}
                  />
                ))}
              </div>
            </motion.div>
          )}
        </AnimatePresence>

        {/* Connection status */}
        <div className={`text-sm ${isConnected ? 'text-green-400' : 'text-red-400'}`}>
          {isConnected ? '🔗 Connected' : '❌ Disconnected'}
        </div>

        {/* Last recording controls */}
        {lastRecording && (
          <motion.div
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            className="flex items-center space-x-2 p-3 bg-white/5 rounded-lg backdrop-blur-sm"
          >
            <motion.button
              onClick={handlePlayLastRecording}
              disabled={isPlaying}
              whileHover={{ scale: 1.05 }}
              whileTap={{ scale: 0.95 }}
              className="p-2 bg-blue-500 rounded-full text-white disabled:opacity-50"
            >
              {isPlaying ? <Pause className="w-4 h-4" /> : <Play className="w-4 h-4" />}
            </motion.button>
            <span className="text-sm text-slate-400">
              {isPlaying ? 'Playing...' : 'Last recording'}
            </span>
          </motion.div>
        )}

        {/* Instructions */}
        <div className="text-center text-xs text-slate-500 max-w-xs">
          {isConnected 
            ? "Click to start recording, click again to stop and send"
            : "Connect to the server to enable voice recording"
          }
        </div>
      </div>
    </div>
  );
};

export default VoiceRecorder;
