import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { History, Search, Trash2, Download, Calendar, MessageSquare } from 'lucide-react';
import { formatDistanceToNow, format } from 'date-fns';

const SessionHistory = ({ sessions, onLoadSession, onDeleteSession }) => {
  const [searchTerm, setSearchTerm] = useState('');
  const [filteredSessions, setFilteredSessions] = useState(sessions);
  const [selectedDate, setSelectedDate] = useState('');

  useEffect(() => {
    let filtered = sessions;

    if (searchTerm) {
      filtered = filtered.filter(session =>
        session.title.toLowerCase().includes(searchTerm.toLowerCase()) ||
        session.messages.some(msg => 
          msg.content.toLowerCase().includes(searchTerm.toLowerCase())
        )
      );
    }

    if (selectedDate) {
      filtered = filtered.filter(session =>
        format(new Date(session.created_at), 'yyyy-MM-dd') === selectedDate
      );
    }

    setFilteredSessions(filtered);
  }, [sessions, searchTerm, selectedDate]);

  const handleSessionClick = (session) => {
    onLoadSession(session);
  };

  const handleDeleteSession = (sessionId, e) => {
    e.stopPropagation();
    if (window.confirm('Are you sure you want to delete this session?')) {
      onDeleteSession(sessionId);
    }
  };

  const handleExportSession = (session, e) => {
    e.stopPropagation();
    const exportData = {
      title: session.title,
      created_at: session.created_at,
      messages: session.messages,
      speakers: session.speakers
    };
    
    const blob = new Blob([JSON.stringify(exportData, null, 2)], {
      type: 'application/json'
    });
    
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `${session.title.replace(/[^a-z0-9]/gi, '_')}.json`;
    a.click();
    URL.revokeObjectURL(url);
  };

  return (
    <div className="glass-panel h-full flex flex-col">
      {/* Header */}
      <div className="p-4 border-b border-white/10">
        <div className="flex items-center space-x-2 mb-4">
          <History className="w-5 h-5 text-blue-400" />
          <h2 className="text-lg font-semibold text-slate-200">Session History</h2>
        </div>

        {/* Search and filters */}
        <div className="space-y-3">
          <div className="relative">
            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 w-4 h-4 text-slate-400" />
            <input
              type="text"
              placeholder="Search sessions..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="input-field pl-10"
            />
          </div>

          <input
            type="date"
            value={selectedDate}
            onChange={(e) => setSelectedDate(e.target.value)}
            className="input-field w-full"
          />
        </div>
      </div>

      {/* Sessions list */}
      <div className="flex-1 overflow-y-auto p-4 space-y-3">
        <AnimatePresence>
          {filteredSessions.length === 0 ? (
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              className="text-center py-8 text-slate-400"
            >
              <MessageSquare className="w-12 h-12 mx-auto mb-4 text-slate-600" />
              <p>No sessions found</p>
            </motion.div>
          ) : (
            filteredSessions.map((session, index) => (
              <motion.div
                key={session.id}
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0, y: -20 }}
                transition={{ delay: index * 0.05 }}
                onClick={() => handleSessionClick(session)}
                className="group p-4 bg-white/5 rounded-lg border border-white/10 hover:bg-white/10 cursor-pointer transition-all duration-200"
              >
                <div className="flex items-start justify-between">
                  <div className="flex-1">
                    <h3 className="font-medium text-slate-200 group-hover:text-white transition-colors">
                      {session.title}
                    </h3>
                    
                    <div className="flex items-center space-x-4 mt-2 text-sm text-slate-400">
                      <span>{formatDistanceToNow(new Date(session.created_at), { addSuffix: true })}</span>
                      <span>{session.messages.length} messages</span>
                      {session.speakers && session.speakers.length > 0 && (
                        <span>{session.speakers.length} speakers</span>
                      )}
                    </div>

                    {/* Preview of last message */}
                    {session.messages.length > 0 && (
                      <p className="text-xs text-slate-500 mt-2 line-clamp-2">
                        {session.messages[session.messages.length - 1].content}
                      </p>
                    )}

                    {/* Speakers preview */}
                    {session.speakers && session.speakers.length > 0 && (
                      <div className="flex items-center space-x-1 mt-2">
                        {session.speakers.slice(0, 3).map((speaker, i) => (
                          <div
                            key={speaker.id}
                            className="w-6 h-6 bg-gradient-to-r from-purple-500 to-pink-500 rounded-full flex items-center justify-center text-xs text-white"
                          >
                            {speaker.name.charAt(0)}
                          </div>
                        ))}
                        {session.speakers.length > 3 && (
                          <span className="text-xs text-slate-400">
                            +{session.speakers.length - 3} more
                          </span>
                        )}
                      </div>
                    )}
                  </div>

                  {/* Action buttons */}
                  <div className="flex items-center space-x-1 opacity-0 group-hover:opacity-100 transition-opacity">
                    <motion.button
                      onClick={(e) => handleExportSession(session, e)}
                      whileHover={{ scale: 1.1 }}
                      whileTap={{ scale: 0.9 }}
                      className="p-2 text-slate-400 hover:text-blue-400 rounded"
                      title="Export session"
                    >
                      <Download className="w-4 h-4" />
                    </motion.button>
                    
                    <motion.button
                      onClick={(e) => handleDeleteSession(session.id, e)}
                      whileHover={{ scale: 1.1 }}
                      whileTap={{ scale: 0.9 }}
                      className="p-2 text-slate-400 hover:text-red-400 rounded"
                      title="Delete session"
                    >
                      <Trash2 className="w-4 h-4" />
                    </motion.button>
                  </div>
                </div>
              </motion.div>
            ))
          )}
        </AnimatePresence>
      </div>

      {/* Footer stats */}
      <div className="p-4 border-t border-white/10">
        <div className="flex justify-between text-sm text-slate-400">
          <span>{filteredSessions.length} session{filteredSessions.length !== 1 ? 's' : ''}</span>
          <span>
            {filteredSessions.reduce((total, session) => total + session.messages.length, 0)} total messages
          </span>
        </div>
      </div>
    </div>
  );
};

export default SessionHistory;
