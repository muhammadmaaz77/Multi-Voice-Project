// WebSocket utility for real-time communication
export class VoiceWebSocket {
  constructor(sessionId, onMessage, onError, onConnect, onDisconnect) {
    this.sessionId = sessionId;
    this.onMessage = onMessage;
    this.onError = onError;
    this.onConnect = onConnect;
    this.onDisconnect = onDisconnect;
    this.ws = null;
    this.reconnectAttempts = 0;
    this.maxReconnectAttempts = 5;
    this.reconnectInterval = 1000;
  }

  connect() {
    const wsUrl = `${import.meta.env.VITE_WS_BASE_URL || 'ws://localhost:3000'}/api/v1/ws/${this.sessionId}`;
    const apiKey = localStorage.getItem('voice_ai_api_key');
    
    try {
      this.ws = new WebSocket(wsUrl);
      
      this.ws.onopen = () => {
        console.log('WebSocket connected');
        this.reconnectAttempts = 0;
        
        // Send authentication
        this.send({
          type: 'auth',
          api_key: apiKey
        });
        
        this.onConnect?.();
      };
      
      this.ws.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data);
          this.onMessage?.(data);
        } catch (error) {
          console.error('Failed to parse WebSocket message:', error);
        }
      };
      
      this.ws.onerror = (error) => {
        console.error('WebSocket error:', error);
        this.onError?.(error);
      };
      
      this.ws.onclose = () => {
        console.log('WebSocket disconnected');
        this.onDisconnect?.();
        
        if (this.reconnectAttempts < this.maxReconnectAttempts) {
          setTimeout(() => {
            this.reconnectAttempts++;
            console.log(`Reconnecting... Attempt ${this.reconnectAttempts}`);
            this.connect();
          }, this.reconnectInterval * this.reconnectAttempts);
        }
      };
    } catch (error) {
      console.error('Failed to create WebSocket:', error);
      this.onError?.(error);
    }
  }

  send(data) {
    if (this.ws && this.ws.readyState === WebSocket.OPEN) {
      this.ws.send(JSON.stringify(data));
    } else {
      console.warn('WebSocket not connected');
    }
  }

  sendAudio(audioBlob) {
    if (this.ws && this.ws.readyState === WebSocket.OPEN) {
      const reader = new FileReader();
      reader.onload = () => {
        this.send({
          type: 'audio',
          data: reader.result.split(',')[1], // Remove data URL prefix
          format: 'wav'
        });
      };
      reader.readAsDataURL(audioBlob);
    }
  }

  disconnect() {
    if (this.ws) {
      this.ws.close();
      this.ws = null;
    }
  }
}

// Audio recording utility
export class AudioRecorder {
  constructor(onDataAvailable, onError) {
    this.onDataAvailable = onDataAvailable;
    this.onError = onError;
    this.mediaRecorder = null;
    this.stream = null;
    this.chunks = [];
    this.isRecording = false;
  }

  async startRecording() {
    try {
      this.stream = await navigator.mediaDevices.getUserMedia({ 
        audio: {
          sampleRate: 16000,
          channelCount: 1,
          echoCancellation: true,
          noiseSuppression: true
        } 
      });
      
      this.mediaRecorder = new MediaRecorder(this.stream, {
        mimeType: 'audio/webm;codecs=opus'
      });
      
      this.chunks = [];
      
      this.mediaRecorder.ondataavailable = (event) => {
        if (event.data.size > 0) {
          this.chunks.push(event.data);
        }
      };
      
      this.mediaRecorder.onstop = () => {
        const audioBlob = new Blob(this.chunks, { type: 'audio/webm' });
        this.onDataAvailable?.(audioBlob);
        this.chunks = [];
      };
      
      this.mediaRecorder.start();
      this.isRecording = true;
    } catch (error) {
      console.error('Failed to start recording:', error);
      this.onError?.(error);
    }
  }

  stopRecording() {
    if (this.mediaRecorder && this.isRecording) {
      this.mediaRecorder.stop();
      this.isRecording = false;
      
      if (this.stream) {
        this.stream.getTracks().forEach(track => track.stop());
        this.stream = null;
      }
    }
  }

  getAudioLevel() {
    if (!this.stream) return 0;
    
    const audioContext = new AudioContext();
    const analyser = audioContext.createAnalyser();
    const source = audioContext.createMediaStreamSource(this.stream);
    source.connect(analyser);
    
    const dataArray = new Uint8Array(analyser.frequencyBinCount);
    analyser.getByteFrequencyData(dataArray);
    
    const average = dataArray.reduce((sum, value) => sum + value, 0) / dataArray.length;
    return average / 255; // Normalize to 0-1
  }
}

// Individual function exports for convenience
let wsInstance = null;
let recorderInstance = null;

export const connectWebSocket = (token, onMessage, onConnect, onDisconnect, onError) => {
  return new Promise((resolve, reject) => {
    try {
      wsInstance = new VoiceWebSocket('default', onMessage, onError, 
        () => {
          onConnect?.();
          resolve(wsInstance);
        }, 
        onDisconnect
      );
      wsInstance.connect();
    } catch (error) {
      reject(error);
    }
  });
};

export const disconnectWebSocket = () => {
  if (wsInstance) {
    wsInstance.disconnect();
    wsInstance = null;
  }
};

export const sendMessage = (message) => {
  if (wsInstance) {
    wsInstance.send(message);
  }
};

export const startRecording = () => {
  return new Promise((resolve, reject) => {
    if (!recorderInstance) {
      recorderInstance = new AudioRecorder();
    }
    
    recorderInstance.onError = reject;
    recorderInstance.startRecording();
    resolve();
  });
};

export const stopRecording = () => {
  return new Promise((resolve, reject) => {
    if (recorderInstance) {
      recorderInstance.onAudioReady = resolve;
      recorderInstance.stopRecording();
    } else {
      reject(new Error('No recording in progress'));
    }
  });
};

export const playAudio = (audioBlob) => {
  return new Promise((resolve, reject) => {
    try {
      const audio = new Audio(URL.createObjectURL(audioBlob));
      audio.onended = resolve;
      audio.onerror = reject;
      audio.play();
    } catch (error) {
      reject(error);
    }
  });
};
