-- Database initialization script
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Create indexes for better performance
CREATE INDEX IF NOT EXISTS idx_conversation_sessions_user_id ON conversation_sessions(user_id);
CREATE INDEX IF NOT EXISTS idx_conversation_sessions_created_at ON conversation_sessions(created_at);
CREATE INDEX IF NOT EXISTS idx_conversation_messages_session_id ON conversation_messages(session_id);
CREATE INDEX IF NOT EXISTS idx_conversation_messages_timestamp ON conversation_messages(timestamp);
CREATE INDEX IF NOT EXISTS idx_speaker_profiles_user_id ON speaker_profiles(user_id);
CREATE INDEX IF NOT EXISTS idx_speaker_profiles_speaker_id ON speaker_profiles(speaker_id);
