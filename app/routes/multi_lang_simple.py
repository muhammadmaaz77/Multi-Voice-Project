"""
Multi-Language Simple WebSocket Route
Simple implementation for multi-party translation without complex dependencies
"""
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from typing import Dict, List, Set
import json
import asyncio
import logging
from groq import Groq
import os

router = APIRouter()

# Simple connection manager for multi-language rooms
class MultiLanguageManager:
    def __init__(self):
        self.rooms: Dict[str, Dict[str, WebSocket]] = {}  # room_id -> {user_id: websocket}
        self.user_languages: Dict[str, str] = {}  # user_id -> language_code
        
    async def connect(self, websocket: WebSocket, room_id: str, user_id: str, language: str):
        await websocket.accept()
        
        if room_id not in self.rooms:
            self.rooms[room_id] = {}
        
        self.rooms[room_id][user_id] = websocket
        self.user_languages[user_id] = language
        
        # Notify room about new user
        await self.broadcast_to_room(room_id, {
            "type": "user_joined",
            "user_id": user_id,
            "language": language,
            "message": f"User {user_id} joined the room"
        }, exclude_user=user_id)
        
    def disconnect(self, room_id: str, user_id: str):
        if room_id in self.rooms and user_id in self.rooms[room_id]:
            del self.rooms[room_id][user_id]
            if user_id in self.user_languages:
                del self.user_languages[user_id]
            
            # Clean up empty rooms
            if not self.rooms[room_id]:
                del self.rooms[room_id]
                
    async def broadcast_to_room(self, room_id: str, message: dict, exclude_user: str = None):
        if room_id not in self.rooms:
            return
            
        disconnected_users = []
        for user_id, websocket in self.rooms[room_id].items():
            if exclude_user and user_id == exclude_user:
                continue
                
            try:
                await websocket.send_text(json.dumps(message))
            except:
                disconnected_users.append(user_id)
        
        # Clean up disconnected users
        for user_id in disconnected_users:
            self.disconnect(room_id, user_id)

# Global manager instance
multi_lang_manager = MultiLanguageManager()

# Initialize Groq client
groq_client = None
try:
    groq_api_key = os.getenv("GROQ_API_KEY")
    if groq_api_key:
        groq_client = Groq(api_key=groq_api_key)
except Exception as e:
    logging.warning(f"Failed to initialize Groq client: {e}")

async def translate_text(text: str, target_language: str) -> str:
    """Simple translation using Groq"""
    if not groq_client:
        return text
        
    try:
        # Simple translation prompt
        prompt = f"Translate this text to {target_language}. Only return the translation, no explanation:\n\n{text}"
        
        response = groq_client.chat.completions.create(
            model="llama-3.1-70b-versatile",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=512,
            temperature=0.3
        )
        
        return response.choices[0].message.content.strip()
    except Exception as e:
        logging.error(f"Translation error: {e}")
        return text

@router.websocket("/ws/multi-language/{room_id}")
async def multi_language_websocket(websocket: WebSocket, room_id: str):
    """Multi-language room WebSocket endpoint"""
    user_id = None
    
    try:
        # Wait for initial connection message with user info
        await websocket.accept()
        
        # Wait for user info
        init_data = await websocket.receive_text()
        init_message = json.loads(init_data)
        
        user_id = init_message.get("user_id", f"user_{len(multi_lang_manager.user_languages) + 1}")
        language = init_message.get("language", "en")
        
        # Connect user to room
        await multi_lang_manager.connect(websocket, room_id, user_id, language)
        
        # Send welcome message
        await websocket.send_text(json.dumps({
            "type": "connected",
            "message": f"Connected to room {room_id} as {user_id}",
            "user_id": user_id,
            "room_id": room_id,
            "language": language
        }))
        
        # Listen for messages
        while True:
            data = await websocket.receive_text()
            message = json.loads(data)
            
            message_type = message.get("type", "chat")
            content = message.get("content", "")
            
            if message_type == "chat":
                # Broadcast original message to same language users
                original_message = {
                    "type": "message",
                    "user_id": user_id,
                    "content": content,
                    "language": multi_lang_manager.user_languages[user_id],
                    "is_original": True,
                    "timestamp": message.get("timestamp")
                }
                
                # Send to all users in room
                if room_id in multi_lang_manager.rooms:
                    translation_tasks = []
                    
                    for target_user_id, target_websocket in multi_lang_manager.rooms[room_id].items():
                        target_language = multi_lang_manager.user_languages.get(target_user_id, "en")
                        user_language = multi_lang_manager.user_languages[user_id]
                        
                        if target_user_id == user_id:
                            # Send original to sender
                            try:
                                await target_websocket.send_text(json.dumps(original_message))
                            except:
                                pass
                        elif target_language == user_language:
                            # Same language, send original
                            try:
                                await target_websocket.send_text(json.dumps(original_message))
                            except:
                                pass
                        else:
                            # Different language, translate
                            translation_tasks.append(
                                send_translated_message(
                                    target_websocket, content, target_language, 
                                    user_id, message.get("timestamp")
                                )
                            )
                    
                    # Execute translations in parallel
                    if translation_tasks:
                        await asyncio.gather(*translation_tasks, return_exceptions=True)
            
            elif message_type == "typing":
                # Broadcast typing indicator
                await multi_lang_manager.broadcast_to_room(room_id, {
                    "type": "typing",
                    "user_id": user_id,
                    "is_typing": message.get("is_typing", False)
                }, exclude_user=user_id)
            
    except WebSocketDisconnect:
        if user_id:
            multi_lang_manager.disconnect(room_id, user_id)
            await multi_lang_manager.broadcast_to_room(room_id, {
                "type": "user_left",
                "user_id": user_id,
                "message": f"User {user_id} left the room"
            })
    except Exception as e:
        logging.error(f"WebSocket error: {e}")
        if user_id:
            multi_lang_manager.disconnect(room_id, user_id)

async def send_translated_message(websocket: WebSocket, content: str, target_language: str, sender_id: str, timestamp: str):
    """Send translated message to a specific websocket"""
    try:
        translated_content = await translate_text(content, target_language)
        
        translated_message = {
            "type": "message",
            "user_id": sender_id,
            "content": translated_content,
            "original_content": content,
            "language": target_language,
            "is_original": False,
            "timestamp": timestamp
        }
        
        await websocket.send_text(json.dumps(translated_message))
    except Exception as e:
        logging.error(f"Failed to send translated message: {e}")

@router.get("/rooms/{room_id}/users")
async def get_room_users(room_id: str):
    """Get list of users in a room"""
    if room_id not in multi_lang_manager.rooms:
        return {"users": []}
    
    users = []
    for user_id in multi_lang_manager.rooms[room_id].keys():
        users.append({
            "user_id": user_id,
            "language": multi_lang_manager.user_languages.get(user_id, "en")
        })
    
    return {"users": users}
