"""
Real-time streaming service for Phase 5A
Handles WebSocket connections for bi-directional audio/text streaming.
"""
import asyncio
import json
import time
from typing import Dict, Optional, List, Any
from dataclasses import dataclass, asdict
from enum import Enum
import numpy as np

class MessageType(Enum):
    """WebSocket message types."""
    START = "start"
    STOP = "stop" 
    HEARTBEAT = "heartbeat"
    FLUSH = "flush"
    PARTIAL_TRANSCRIPT = "partial_transcript"
    FINAL_TRANSCRIPT = "final_transcript"
    TRANSLATION = "translation"
    ASSISTANT_TEXT = "assistant_text"
    TTS_AUDIO_CHUNK = "tts_audio_chunk"
    ERROR = "error"

@dataclass
class AudioChunk:
    """Audio chunk with metadata."""
    data: bytes
    sequence: int
    timestamp: float
    sample_rate: int = 16000
    channels: int = 1

@dataclass
class StreamSession:
    """Active streaming session."""
    session_id: str
    user_id: Optional[str]
    source_lang: str
    target_lang: str
    translate_enabled: bool
    voice_profile_id: Optional[str]
    created_at: float
    last_activity: float
    audio_buffer: List[AudioChunk]
    partial_text: str
    final_text: str
    sequence_counter: int

class AudioBuffer:
    """Buffer for managing audio chunks with VAD and reordering."""
    
    def __init__(self, max_size: int = 100):
        self.chunks: Dict[int, AudioChunk] = {}
        self.max_size = max_size
        self.last_processed_seq = -1
        self.vad_threshold = 0.01  # Voice Activity Detection threshold
        
    def add_chunk(self, chunk: AudioChunk) -> bool:
        """Add audio chunk to buffer."""
        if len(self.chunks) >= self.max_size:
            # Remove oldest chunks
            old_seqs = sorted(self.chunks.keys())[:10]
            for seq in old_seqs:
                del self.chunks[seq]
        
        self.chunks[chunk.sequence] = chunk
        return True
    
    def get_next_chunks(self) -> List[AudioChunk]:
        """Get next sequential chunks for processing."""
        chunks = []
        seq = self.last_processed_seq + 1
        
        while seq in self.chunks:
            chunks.append(self.chunks.pop(seq))
            self.last_processed_seq = seq
            seq += 1
            
        return chunks
    
    def detect_voice_activity(self, audio_data: bytes) -> bool:
        """Simple VAD based on audio energy."""
        try:
            # Convert bytes to numpy array (assuming 16-bit PCM)
            audio_array = np.frombuffer(audio_data, dtype=np.int16)
            energy = np.mean(np.abs(audio_array.astype(np.float32)))
            normalized_energy = energy / 32768.0  # Normalize to 0-1
            return normalized_energy > self.vad_threshold
        except:
            return True  # Default to voice active if detection fails

class StreamingTranscriber:
    """Real-time transcription with partial results."""
    
    def __init__(self):
        self.partial_buffer = ""
        self.confidence_threshold = 0.7
        
    async def process_audio_chunk(self, audio_data: bytes, sequence: int) -> Dict[str, Any]:
        """Process audio chunk and return transcription results."""
        try:
            # Simulate partial transcription (replace with actual Groq Whisper streaming)
            # This would integrate with Groq's streaming API when available
            
            # Mock partial transcription based on audio length
            audio_length = len(audio_data)
            
            if audio_length > 1000:  # Enough audio for words
                partial_text = f"transcribing audio chunk {sequence}..."
                final_text = None
                
                # Simulate completing transcription every 5 chunks
                if sequence % 5 == 0:
                    final_text = f"This is the final transcription for sequence {sequence-4} to {sequence}"
                    partial_text = ""
                
                return {
                    "partial_transcript": partial_text,
                    "final_transcript": final_text,
                    "sequence": sequence,
                    "confidence": 0.85
                }
            
            return {"sequence": sequence}
            
        except Exception as e:
            return {"error": str(e), "sequence": sequence}

class TranslationRouter:
    """Handles simultaneous translation routing."""
    
    def __init__(self):
        self.active_translations: Dict[str, Dict] = {}
        
    async def translate_text(self, 
                           text: str, 
                           source_lang: str, 
                           target_lang: str,
                           session_id: str) -> str:
        """Translate text between languages."""
        # Mock translation - replace with actual Groq translation API
        translation_map = {
            ("ur", "en"): f"[EN] {text}",
            ("en", "ur"): f"[UR] {text}",
            ("es", "en"): f"[EN] {text}",
            ("en", "es"): f"[ES] {text}",
        }
        
        key = (source_lang, target_lang)
        return translation_map.get(key, f"[{target_lang.upper()}] {text}")
    
    async def route_simultaneous_translation(self, 
                                           text: str,
                                           source_lang: str,
                                           session_participants: List[Dict]) -> List[Dict]:
        """Route translation to multiple participants."""
        results = []
        
        for participant in session_participants:
            if participant["lang"] != source_lang:
                translated = await self.translate_text(
                    text, source_lang, participant["lang"], participant["session_id"]
                )
                results.append({
                    "participant_id": participant["id"],
                    "translation": translated,
                    "target_lang": participant["lang"]
                })
        
        return results

class TTSStreamer:
    """Text-to-speech streaming service."""
    
    def __init__(self):
        self.voice_models = {
            "neural_en": "English Neural Voice",
            "neural_ur": "Urdu Neural Voice", 
            "default": "Default Voice"
        }
        
    async def synthesize_speech(self, 
                              text: str, 
                              voice_model: str = "default",
                              voice_profile_id: Optional[str] = None) -> bytes:
        """Synthesize speech from text."""
        # Mock TTS - replace with actual TTS service
        # This would integrate with Groq TTS or other providers
        
        # Generate mock audio data (silence with length proportional to text)
        text_length = len(text)
        audio_duration = max(1.0, text_length * 0.1)  # ~0.1s per character
        sample_rate = 16000
        samples = int(audio_duration * sample_rate)
        
        # Generate simple sine wave as mock audio
        frequency = 440  # A4 note
        t = np.linspace(0, audio_duration, samples)
        audio_signal = np.sin(2 * np.pi * frequency * t) * 0.1  # Low volume
        
        # Convert to 16-bit PCM
        audio_int16 = (audio_signal * 32767).astype(np.int16)
        return audio_int16.tobytes()
    
    async def stream_synthesis(self, 
                             text: str,
                             chunk_size: int = 1024,
                             voice_model: str = "default") -> List[bytes]:
        """Stream TTS synthesis in chunks for low latency."""
        full_audio = await self.synthesize_speech(text, voice_model)
        
        # Split into chunks
        chunks = []
        for i in range(0, len(full_audio), chunk_size):
            chunks.append(full_audio[i:i + chunk_size])
        
        return chunks

class StreamingManager:
    """Main streaming session manager."""
    
    def __init__(self):
        self.active_sessions: Dict[str, StreamSession] = {}
        self.audio_buffers: Dict[str, AudioBuffer] = {}
        self.transcriber = StreamingTranscriber()
        self.translator = TranslationRouter()
        self.tts_streamer = TTSStreamer()
        
    def create_session(self, 
                      session_id: str,
                      user_id: Optional[str] = None,
                      source_lang: str = "auto",
                      target_lang: str = "en",
                      translate_enabled: bool = False,
                      voice_profile_id: Optional[str] = None) -> StreamSession:
        """Create new streaming session."""
        session = StreamSession(
            session_id=session_id,
            user_id=user_id,
            source_lang=source_lang,
            target_lang=target_lang,
            translate_enabled=translate_enabled,
            voice_profile_id=voice_profile_id,
            created_at=time.time(),
            last_activity=time.time(),
            audio_buffer=[],
            partial_text="",
            final_text="",
            sequence_counter=0
        )
        
        self.active_sessions[session_id] = session
        self.audio_buffers[session_id] = AudioBuffer()
        
        return session
    
    def get_session(self, session_id: str) -> Optional[StreamSession]:
        """Get active session."""
        return self.active_sessions.get(session_id)
    
    def update_session_activity(self, session_id: str):
        """Update session last activity timestamp."""
        if session_id in self.active_sessions:
            self.active_sessions[session_id].last_activity = time.time()
    
    async def process_audio_chunk(self, 
                                session_id: str, 
                                audio_data: bytes, 
                                sequence: int) -> Dict[str, Any]:
        """Process incoming audio chunk."""
        session = self.get_session(session_id)
        if not session:
            return {"error": "Session not found"}
        
        # Add to buffer
        chunk = AudioChunk(
            data=audio_data,
            sequence=sequence,
            timestamp=time.time()
        )
        
        buffer = self.audio_buffers[session_id]
        buffer.add_chunk(chunk)
        
        # Process available chunks
        ready_chunks = buffer.get_next_chunks()
        results = []
        
        for chunk in ready_chunks:
            # Voice activity detection
            if buffer.detect_voice_activity(chunk.data):
                # Transcribe
                transcription_result = await self.transcriber.process_audio_chunk(
                    chunk.data, chunk.sequence
                )
                
                if transcription_result:
                    results.append(transcription_result)
                    
                    # Handle final transcription
                    if "final_transcript" in transcription_result and transcription_result["final_transcript"]:
                        final_text = transcription_result["final_transcript"]
                        session.final_text = final_text
                        
                        # Translation if enabled
                        if session.translate_enabled:
                            translation = await self.translator.translate_text(
                                final_text,
                                session.source_lang,
                                session.target_lang,
                                session_id
                            )
                            results.append({
                                "type": MessageType.TRANSLATION.value,
                                "text": translation,
                                "target_lang": session.target_lang,
                                "sequence": chunk.sequence
                            })
        
        self.update_session_activity(session_id)
        return {"results": results}
    
    async def generate_assistant_response(self, 
                                        session_id: str, 
                                        text: str) -> Optional[str]:
        """Generate assistant response to user input."""
        session = self.get_session(session_id)
        if not session:
            return None
        
        # Mock assistant response - integrate with Groq chat API
        responses = [
            "I understand. How can I help you further?",
            "That's interesting. Could you tell me more?",
            "I see. What would you like to know?",
            "Thank you for sharing that. What's next?"
        ]
        
        import random
        return random.choice(responses)
    
    async def synthesize_and_stream_response(self, 
                                           session_id: str, 
                                           text: str) -> List[bytes]:
        """Synthesize assistant response and return audio chunks."""
        session = self.get_session(session_id)
        if not session:
            return []
        
        voice_model = "neural_en" if session.target_lang == "en" else "default"
        
        audio_chunks = await self.tts_streamer.stream_synthesis(
            text, voice_model=voice_model
        )
        
        return audio_chunks
    
    def end_session(self, session_id: str) -> bool:
        """End streaming session."""
        if session_id in self.active_sessions:
            del self.active_sessions[session_id]
            
        if session_id in self.audio_buffers:
            del self.audio_buffers[session_id]
            
        return True
    
    def cleanup_expired_sessions(self, timeout_seconds: int = 3600):
        """Clean up expired sessions."""
        current_time = time.time()
        expired_sessions = [
            sid for sid, session in self.active_sessions.items()
            if current_time - session.last_activity > timeout_seconds
        ]
        
        for session_id in expired_sessions:
            self.end_session(session_id)

# Global streaming manager instance
streaming_manager = StreamingManager()
