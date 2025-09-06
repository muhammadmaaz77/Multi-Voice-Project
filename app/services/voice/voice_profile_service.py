"""
Voice profile management service for Phase 5A
Handles voice cloning pipeline hooks and voice profile storage.
"""
import os
import uuid
import hashlib
import json
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
from datetime import datetime
import asyncio

@dataclass
class VoiceProfile:
    """Voice profile data structure."""
    profile_id: str
    user_id: str
    name: str
    language: str
    status: str  # queued, processing, ready, failed
    created_at: str
    updated_at: str
    sample_files: List[str]
    training_progress: float
    model_path: Optional[str] = None
    metadata: Dict[str, Any] = None

@dataclass
class VoiceSample:
    """Voice sample file information."""
    sample_id: str
    profile_id: str
    filename: str
    file_path: str
    duration_seconds: float
    sample_rate: int
    quality_score: float
    uploaded_at: str

class VoiceProfileManager:
    """Manages voice profiles and training pipeline."""
    
    def __init__(self, storage_path: str = "voice_profiles"):
        self.storage_path = storage_path
        self.profiles: Dict[str, VoiceProfile] = {}
        self.samples: Dict[str, VoiceSample] = {}
        self._ensure_storage_directory()
        self._load_existing_profiles()
    
    def _ensure_storage_directory(self):
        """Ensure voice profile storage directory exists."""
        os.makedirs(self.storage_path, exist_ok=True)
        os.makedirs(os.path.join(self.storage_path, "samples"), exist_ok=True)
        os.makedirs(os.path.join(self.storage_path, "models"), exist_ok=True)
    
    def _load_existing_profiles(self):
        """Load existing voice profiles from storage."""
        profiles_file = os.path.join(self.storage_path, "profiles.json")
        if os.path.exists(profiles_file):
            try:
                with open(profiles_file, 'r') as f:
                    data = json.load(f)
                    for profile_data in data.get("profiles", []):
                        profile = VoiceProfile(**profile_data)
                        self.profiles[profile.profile_id] = profile
            except Exception as e:
                print(f"Error loading voice profiles: {e}")
    
    def _save_profiles(self):
        """Save voice profiles to storage."""
        profiles_file = os.path.join(self.storage_path, "profiles.json")
        try:
            data = {
                "profiles": [asdict(profile) for profile in self.profiles.values()],
                "updated_at": datetime.now().isoformat()
            }
            with open(profiles_file, 'w') as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            print(f"Error saving voice profiles: {e}")
    
    async def create_voice_profile(self, 
                                 user_id: str, 
                                 name: str, 
                                 language: str = "en") -> str:
        """Create a new voice profile."""
        profile_id = str(uuid.uuid4())
        
        profile = VoiceProfile(
            profile_id=profile_id,
            user_id=user_id,
            name=name,
            language=language,
            status="queued",
            created_at=datetime.now().isoformat(),
            updated_at=datetime.now().isoformat(),
            sample_files=[],
            training_progress=0.0,
            metadata={}
        )
        
        self.profiles[profile_id] = profile
        self._save_profiles()
        
        return profile_id
    
    async def validate_audio_sample(self, 
                                  file_content: bytes, 
                                  filename: str) -> Dict[str, Any]:
        """Validate uploaded audio sample."""
        try:
            # Basic file format validation
            valid_extensions = ['.wav', '.mp3', '.flac', '.m4a']
            file_ext = os.path.splitext(filename)[1].lower()
            
            if file_ext not in valid_extensions:
                return {
                    "valid": False,
                    "error": f"Unsupported file format. Supported: {valid_extensions}"
                }
            
            # Check file size (30-60 seconds worth of audio)
            min_size = 480000  # ~30 seconds of 16kHz 16-bit mono
            max_size = 4800000  # ~5 minutes max
            
            if len(file_content) < min_size:
                return {
                    "valid": False,
                    "error": "Audio sample too short. Minimum 30 seconds required."
                }
            
            if len(file_content) > max_size:
                return {
                    "valid": False,
                    "error": "Audio sample too long. Maximum 5 minutes allowed."
                }
            
            # Mock audio analysis (replace with actual audio processing)
            estimated_duration = len(file_content) / 16000 / 2  # Rough estimate
            quality_score = 0.85  # Mock quality score
            
            return {
                "valid": True,
                "duration": estimated_duration,
                "quality_score": quality_score,
                "sample_rate": 16000,  # Mock sample rate
                "format": file_ext
            }
            
        except Exception as e:
            return {
                "valid": False,
                "error": f"Error validating audio: {str(e)}"
            }
    
    async def upload_voice_sample(self, 
                                profile_id: str, 
                                file_content: bytes, 
                                filename: str) -> Dict[str, Any]:
        """Upload and store voice sample for a profile."""
        if profile_id not in self.profiles:
            return {"success": False, "error": "Voice profile not found"}
        
        # Validate audio sample
        validation_result = await self.validate_audio_sample(file_content, filename)
        if not validation_result["valid"]:
            return {"success": False, "error": validation_result["error"]}
        
        # Generate unique sample ID
        sample_id = str(uuid.uuid4())
        
        # Create secure filename
        file_hash = hashlib.md5(file_content).hexdigest()[:8]
        file_ext = os.path.splitext(filename)[1]
        secure_filename = f"{profile_id}_{sample_id}_{file_hash}{file_ext}"
        file_path = os.path.join(self.storage_path, "samples", secure_filename)
        
        try:
            # Save file
            with open(file_path, 'wb') as f:
                f.write(file_content)
            
            # Create sample record
            sample = VoiceSample(
                sample_id=sample_id,
                profile_id=profile_id,
                filename=filename,
                file_path=file_path,
                duration_seconds=validation_result["duration"],
                sample_rate=validation_result["sample_rate"],
                quality_score=validation_result["quality_score"],
                uploaded_at=datetime.now().isoformat()
            )
            
            self.samples[sample_id] = sample
            
            # Update profile
            profile = self.profiles[profile_id]
            profile.sample_files.append(sample_id)
            profile.updated_at = datetime.now().isoformat()
            
            # Check if we have enough samples to start training
            if len(profile.sample_files) >= 3:  # Minimum 3 samples
                await self._queue_training_job(profile_id)
            
            self._save_profiles()
            
            return {
                "success": True,
                "sample_id": sample_id,
                "quality_score": validation_result["quality_score"],
                "duration": validation_result["duration"],
                "total_samples": len(profile.sample_files)
            }
            
        except Exception as e:
            return {"success": False, "error": f"Error saving sample: {str(e)}"}
    
    async def _queue_training_job(self, profile_id: str):
        """Queue voice training job (stub for Phase 5A)."""
        if profile_id not in self.profiles:
            return
        
        profile = self.profiles[profile_id]
        profile.status = "processing"
        profile.training_progress = 0.1
        profile.updated_at = datetime.now().isoformat()
        
        # In Phase 5B, this would integrate with actual training workers
        # For now, just simulate training progress
        import asyncio
        asyncio.create_task(self._simulate_training(profile_id))
    
    async def _simulate_training(self, profile_id: str):
        """Simulate voice training progress."""
        if profile_id not in self.profiles:
            return
        
        profile = self.profiles[profile_id]
        
        # Simulate training progress over time
        progress_steps = [0.1, 0.3, 0.5, 0.7, 0.9, 1.0]
        
        for progress in progress_steps:
            await asyncio.sleep(10)  # Wait 10 seconds between updates
            
            if profile_id not in self.profiles:  # Profile might be deleted
                return
            
            profile.training_progress = progress
            profile.updated_at = datetime.now().isoformat()
            
            if progress >= 1.0:
                profile.status = "ready"
                profile.model_path = f"models/{profile_id}_voice_model.bin"
                
                # Create mock model file
                model_path = os.path.join(self.storage_path, "models", f"{profile_id}_voice_model.bin")
                with open(model_path, 'wb') as f:
                    f.write(b"Mock voice model data")
            
            self._save_profiles()
    
    def get_voice_profile(self, profile_id: str) -> Optional[VoiceProfile]:
        """Get voice profile by ID."""
        return self.profiles.get(profile_id)
    
    def get_user_profiles(self, user_id: str) -> List[VoiceProfile]:
        """Get all voice profiles for a user."""
        return [
            profile for profile in self.profiles.values()
            if profile.user_id == user_id
        ]
    
    def get_profile_samples(self, profile_id: str) -> List[VoiceSample]:
        """Get all samples for a voice profile."""
        return [
            sample for sample in self.samples.values()
            if sample.profile_id == profile_id
        ]
    
    async def delete_voice_profile(self, profile_id: str, user_id: str) -> bool:
        """Delete voice profile and associated files."""
        if profile_id not in self.profiles:
            return False
        
        profile = self.profiles[profile_id]
        
        # Verify ownership
        if profile.user_id != user_id:
            return False
        
        try:
            # Delete sample files
            samples = self.get_profile_samples(profile_id)
            for sample in samples:
                if os.path.exists(sample.file_path):
                    os.remove(sample.file_path)
                del self.samples[sample.sample_id]
            
            # Delete model file if exists
            if profile.model_path:
                model_path = os.path.join(self.storage_path, profile.model_path)
                if os.path.exists(model_path):
                    os.remove(model_path)
            
            # Remove profile
            del self.profiles[profile_id]
            self._save_profiles()
            
            return True
            
        except Exception as e:
            print(f"Error deleting voice profile: {e}")
            return False
    
    def get_training_status(self, profile_id: str) -> Dict[str, Any]:
        """Get training status for a voice profile."""
        profile = self.get_voice_profile(profile_id)
        if not profile:
            return {"error": "Profile not found"}
        
        return {
            "profile_id": profile_id,
            "status": profile.status,
            "progress": profile.training_progress,
            "total_samples": len(profile.sample_files),
            "estimated_completion": None,  # Could calculate based on progress
            "updated_at": profile.updated_at
        }

# Global voice profile manager instance
voice_profile_manager = VoiceProfileManager()
