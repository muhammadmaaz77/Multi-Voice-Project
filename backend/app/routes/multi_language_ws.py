from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends, HTTPException
from typing import Dict, List, Optional
import json
import asyncio
import base64
import logging
import uuid
from datetime import datetime

from ..core.groq_client import groq_client
from ..core.translator import translator
from ..core.emotion_analyzer import emotion_analyzer
from ..core.tts_service import tts_service
from ..db.database import get_db
from ..db.models import ChatSession, Message
from sqlalchemy.orm import Session

router = APIRouter()
logger = logging.getLogger(__name__)

# Active WebSocket connections
class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[str, WebSocket] = {}
        self.rooms: Dict[str, Dict] = {}  # room_code -> room_data
        self.user_rooms: Dict[str, str] = {}  # user_id -> room_code

    async def connect(self, websocket: WebSocket, user_id: str):
        await websocket.accept()
        self.active_connections[user_id] = websocket
        logger.info(f"User {user_id} connected")

    def disconnect(self, user_id: str):
        if user_id in self.active_connections:
            del self.active_connections[user_id]
        
        # Remove from room
        if user_id in self.user_rooms:
            room_code = self.user_rooms[user_id]
            self.leave_room(user_id, room_code)
        
        logger.info(f"User {user_id} disconnected")

    def join_room(self, user_id: str, room_code: str, user_data: dict):
        # Leave previous room if any
        if user_id in self.user_rooms:
            old_room = self.user_rooms[user_id]
            self.leave_room(user_id, old_room)

        # Create room if doesn't exist
        if room_code not in self.rooms:
            self.rooms[room_code] = {
                'users': {},
                'created_at': datetime.now(),
                'message_count': 0
            }

        # Add user to room
        self.rooms[room_code]['users'][user_id] = user_data
        self.user_rooms[user_id] = room_code
        
        logger.info(f"User {user_id} joined room {room_code}")
        return self.rooms[room_code]

    def leave_room(self, user_id: str, room_code: str):
        if room_code in self.rooms and user_id in self.rooms[room_code]['users']:
            del self.rooms[room_code]['users'][user_id]
            
            # Remove empty rooms
            if not self.rooms[room_code]['users']:
                del self.rooms[room_code]
            
        if user_id in self.user_rooms:
            del self.user_rooms[user_id]
        
        logger.info(f"User {user_id} left room {room_code}")

    async def send_personal_message(self, user_id: str, message: dict):
        if user_id in self.active_connections:
            try:
                await self.active_connections[user_id].send_text(json.dumps(message))
            except Exception as e:
                logger.error(f"Error sending message to {user_id}: {e}")

    async def broadcast_to_room(self, room_code: str, message: dict, exclude_user: Optional[str] = None):
        if room_code not in self.rooms:
            return

        for user_id in self.rooms[room_code]['users']:
            if user_id != exclude_user and user_id in self.active_connections:
                try:
                    await self.active_connections[user_id].send_text(json.dumps(message))
                except Exception as e:
                    logger.error(f"Error broadcasting to {user_id}: {e}")

    def get_room_users(self, room_code: str) -> List[dict]:
        if room_code not in self.rooms:
            return []
        return list(self.rooms[room_code]['users'].values())

manager = ConnectionManager()

@router.websocket("/ws/{user_id}")
async def websocket_endpoint(websocket: WebSocket, user_id: str):
    await manager.connect(websocket, user_id)
    try:
        while True:
            data = await websocket.receive_text()
            message = json.loads(data)
            await handle_websocket_message(user_id, message)
    except WebSocketDisconnect:
        manager.disconnect(user_id)
    except Exception as e:
        logger.error(f"WebSocket error for user {user_id}: {e}")
        manager.disconnect(user_id)

async def handle_websocket_message(user_id: str, message: dict):
    """Handle incoming WebSocket messages"""
    message_type = message.get('type')
    
    try:
        if message_type == 'setup_languages':
            await handle_setup_languages(user_id, message)
        elif message_type == 'join_room':
            await handle_join_room(user_id, message)
        elif message_type == 'voice_message':
            await handle_voice_message(user_id, message)
        elif message_type == 'text_message':
            await handle_text_message(user_id, message)
        elif message_type == 'ping':
            await manager.send_personal_message(user_id, {'type': 'pong', 'timestamp': datetime.now().isoformat()})
        else:
            logger.warning(f"Unknown message type: {message_type}")
    except Exception as e:
        logger.error(f"Error handling message {message_type} from {user_id}: {e}")
        await manager.send_personal_message(user_id, {
            'type': 'error',
            'message': f'Failed to process {message_type}: {str(e)}'
        })

async def handle_setup_languages(user_id: str, message: dict):
    """Handle language setup"""
    user_language = message.get('user_language', 'en')
    listen_language = message.get('listen_language', 'en')
    
    await manager.send_personal_message(user_id, {
        'type': 'languages_setup',
        'user_language': user_language,
        'listen_language': listen_language,
        'message': f'Languages configured: Speaking {user_language}, Listening {listen_language}'
    })

async def handle_join_room(user_id: str, message: dict):
    """Handle room joining"""
    room_code = message.get('room_code')
    user_language = message.get('user_language', 'en')
    listen_language = message.get('listen_language', 'en')
    user_name = message.get('user_name', f'User-{user_id}')
    
    if not room_code:
        room_code = f"room-{uuid.uuid4().hex[:8]}"
    
    user_data = {
        'id': user_id,
        'name': user_name,
        'language': user_language,
        'listen_language': listen_language,
        'joined_at': datetime.now().isoformat()
    }
    
    # Join the room
    room_data = manager.join_room(user_id, room_code, user_data)
    
    # Notify user they joined
    await manager.send_personal_message(user_id, {
        'type': 'room_joined',
        'room_code': room_code,
        'users': manager.get_room_users(room_code),
        'message': f'Joined room {room_code}'
    })
    
    # Notify other users in room
    await manager.broadcast_to_room(room_code, {
        'type': 'user_joined',
        'user': user_data,
        'room_code': room_code
    }, exclude_user=user_id)

async def handle_voice_message(user_id: str, message: dict):
    """Handle voice message processing and translation"""
    try:
        audio_data = message.get('audio_data')
        room_code = message.get('room_code')
        user_language = message.get('user_language', 'en')
        user_name = message.get('user_name', f'User-{user_id}')
        
        if not audio_data or not room_code:
            raise ValueError("Missing audio_data or room_code")
        
        # Decode audio
        audio_bytes = base64.b64decode(audio_data)
        
        # Step 1: Transcribe audio
        transcription_result = await groq_client.transcribe_audio(audio_bytes, user_language)
        transcribed_text = transcription_result.get('text', '')
        detected_language = transcription_result.get('language', user_language)
        
        if not transcribed_text.strip():
            await manager.send_personal_message(user_id, {
                'type': 'error',
                'message': 'No speech detected in audio'
            })
            return
        
        # Step 2: Detect emotion
        emotion = await emotion_analyzer.analyze_emotion(transcribed_text)
        
        # Step 3: Send original transcription to sender
        await manager.send_personal_message(user_id, {
            'type': 'voice_transcription',
            'transcription': transcribed_text,
            'detected_language': detected_language,
            'speaker_name': user_name,
            'emotion': emotion
        })
        
        # Step 4: Get room users and their language preferences
        room_users = manager.get_room_users(room_code)
        
        # Step 5: Translate and send to each user in their preferred language
        for target_user in room_users:
            if target_user['id'] == user_id:
                continue  # Skip sender
            
            target_language = target_user.get('listen_language', 'en')
            
            # Translate if needed
            if detected_language != target_language:
                translated_text = await translator.translate_text(
                    transcribed_text,
                    source_lang=detected_language,
                    target_lang=target_language
                )
            else:
                translated_text = transcribed_text
            
            # Step 6: Generate TTS audio
            tts_result = await tts_service.generate_speech(
                translated_text,
                target_language,
                voice_style=emotion
            )
            
            # Step 7: Send translated message with audio to target user
            await manager.send_personal_message(target_user['id'], {
                'type': 'room_message',
                'content': translated_text,
                'original_text': transcribed_text,
                'original_language': detected_language,
                'target_language': target_language,
                'sender_type': 'user',
                'speaker_name': user_name,
                'timestamp': datetime.now().isoformat(),
                'emotion': emotion,
                'audio_url': tts_result.get('audio_url') if tts_result else None,
                'room_code': room_code
            })
            
            # Also send TTS audio separately for immediate playback
            if tts_result and tts_result.get('audio_url'):
                await manager.send_personal_message(target_user['id'], {
                    'type': 'tts_audio',
                    'audio_url': tts_result['audio_url'],
                    'text': translated_text,
                    'language': target_language
                })
        
        logger.info(f"Voice message processed: {user_name} in room {room_code}")
        
    except Exception as e:
        logger.error(f"Error processing voice message from {user_id}: {e}")
        await manager.send_personal_message(user_id, {
            'type': 'error',
            'message': f'Failed to process voice message: {str(e)}'
        })

async def handle_text_message(user_id: str, message: dict):
    """Handle text message processing and translation"""
    try:
        content = message.get('content')
        room_code = message.get('room_code')
        user_language = message.get('user_language', 'en')
        user_name = message.get('user_name', f'User-{user_id}')
        
        if not content or not room_code:
            raise ValueError("Missing content or room_code")
        
        # Step 1: Detect emotion
        emotion = await emotion_analyzer.analyze_emotion(content)
        
        # Step 2: Get room users and their language preferences
        room_users = manager.get_room_users(room_code)
        
        # Step 3: Translate and send to each user in their preferred language
        for target_user in room_users:
            if target_user['id'] == user_id:
                continue  # Skip sender
            
            target_language = target_user.get('listen_language', 'en')
            
            # Translate if needed
            if user_language != target_language:
                translated_content = await translator.translate_text(
                    content,
                    source_lang=user_language,
                    target_lang=target_language
                )
            else:
                translated_content = content
            
            # Step 4: Generate TTS audio for translated text
            tts_result = await tts_service.generate_speech(
                translated_content,
                target_language,
                voice_style=emotion
            )
            
            # Step 5: Send translated message to target user
            await manager.send_personal_message(target_user['id'], {
                'type': 'room_message',
                'content': translated_content,
                'original_text': content,
                'original_language': user_language,
                'target_language': target_language,
                'sender_type': 'user',
                'speaker_name': user_name,
                'timestamp': datetime.now().isoformat(),
                'emotion': emotion,
                'audio_url': tts_result.get('audio_url') if tts_result else None,
                'room_code': room_code
            })
            
            # Also send TTS audio separately for immediate playback
            if tts_result and tts_result.get('audio_url'):
                await manager.send_personal_message(target_user['id'], {
                    'type': 'tts_audio',
                    'audio_url': tts_result['audio_url'],
                    'text': translated_content,
                    'language': target_language
                })
        
        logger.info(f"Text message processed: {user_name} in room {room_code}")
        
    except Exception as e:
        logger.error(f"Error processing text message from {user_id}: {e}")
        await manager.send_personal_message(user_id, {
            'type': 'error',
            'message': f'Failed to process text message: {str(e)}'
        })

@router.get("/rooms/{room_code}/users")
async def get_room_users(room_code: str):
    """Get list of users in a room"""
    users = manager.get_room_users(room_code)
    return {"room_code": room_code, "users": users, "count": len(users)}

@router.get("/rooms")
async def get_active_rooms():
    """Get list of active rooms"""
    rooms = []
    for room_code, room_data in manager.rooms.items():
        rooms.append({
            "room_code": room_code,
            "user_count": len(room_data['users']),
            "created_at": room_data['created_at'].isoformat(),
            "message_count": room_data.get('message_count', 0)
        })
    return {"rooms": rooms, "total": len(rooms)}

@router.post("/rooms/{room_code}/leave")
async def leave_room(room_code: str, user_id: str):
    """Leave a room"""
    manager.leave_room(user_id, room_code)
    
    # Notify other users
    await manager.broadcast_to_room(room_code, {
        'type': 'user_left',
        'user': {'id': user_id},
        'room_code': room_code
    })
    
    return {"message": f"User {user_id} left room {room_code}"}
