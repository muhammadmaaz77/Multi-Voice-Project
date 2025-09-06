# Multi Voice AI Bot - Frontend

A modern, animated React frontend for the Voice AI Bot with real-time voice interactions.

## Features

- 🎨 **Modern UI/UX**: Beautiful, animated interface built with React, Framer Motion, and TailwindCSS
- 🎙️ **Real-time Voice**: Voice recording, playback, and real-time audio visualization
- 💬 **Real-time Chat**: WebSocket-based messaging with typing indicators
- 👥 **Multi-speaker Support**: Speaker identification and emotion display
- 📊 **Session History**: Persistent conversation history and search
- ⚙️ **Settings Panel**: Comprehensive audio, voice, and privacy settings
- 🔔 **Notifications**: Toast notifications for system events
- 📱 **Responsive Design**: Mobile-first, fully responsive layout
- 🌙 **Dark Theme**: Elegant dark theme with glass morphism effects

## Tech Stack

- **React 18** with modern hooks and functional components
- **Framer Motion** for smooth animations and transitions
- **TailwindCSS** for utility-first styling
- **React Router** for client-side routing
- **Axios** for HTTP requests
- **WebSocket API** for real-time communication
- **Web Audio API** for voice recording and playback
- **Lucide React** for beautiful icons
- **Vite** for fast development and building

## Project Structure

```
frontend/
├── src/
│   ├── components/          # Reusable UI components
│   │   ├── ChatWindow.jsx
│   │   ├── ChatBubble.jsx
│   │   ├── VoiceRecorder.jsx
│   │   ├── SettingsPanel.jsx
│   │   ├── SessionHistory.jsx
│   │   ├── Notifications.jsx
│   │   └── ConnectionStatus.jsx
│   ├── pages/               # Page components
│   │   ├── LoginPage.jsx
│   │   └── Dashboard.jsx
│   ├── hooks/               # Custom React hooks
│   │   ├── useNotifications.js
│   │   ├── useWebSocket.js
│   │   └── useSettings.js
│   ├── utils/               # Utility functions
│   │   ├── api.js
│   │   ├── websocket.js
│   │   └── helpers.js
│   ├── styles/              # Global styles
│   │   └── globals.css
│   ├── App.jsx              # Main app component
│   └── main.jsx             # Entry point
├── public/                  # Static assets
├── index.html               # HTML template
├── package.json             # Dependencies and scripts
├── vite.config.js           # Vite configuration
├── tailwind.config.js       # TailwindCSS configuration
└── postcss.config.js        # PostCSS configuration
```

## Getting Started

### Prerequisites

- Node.js 18+ 
- npm or yarn
- Running backend server (see ../README.md)

### Installation

1. Navigate to the frontend directory:
   ```bash
   cd frontend
   ```

2. Install dependencies:
   ```bash
   npm install
   ```

3. Configure environment variables:
   ```bash
   # Copy the example environment file
   cp .env.example .env.local
   
   # Edit .env.local with your settings
   VITE_API_URL=http://localhost:8000
   VITE_WS_URL=ws://localhost:8000
   ```

4. Start the development server:
   ```bash
   npm run dev
   ```

5. Open your browser to `http://localhost:3000`

### Building for Production

1. Build the project:
   ```bash
   npm run build
   ```

2. Preview the production build:
   ```bash
   npm run preview
   ```

## Environment Variables

Create a `.env.local` file with the following variables:

```env
# Backend API URL
VITE_API_URL=http://localhost:8000

# WebSocket URL  
VITE_WS_URL=ws://localhost:8000

# Environment
VITE_NODE_ENV=development
```

## Features Guide

### Authentication
- Secure login with JWT tokens
- Persistent authentication state
- Automatic token refresh

### Voice Recording
- Click-to-record voice messages
- Real-time audio level visualization
- Noise reduction and echo cancellation
- Playback of recorded messages

### Real-time Chat
- WebSocket-based messaging
- Typing indicators
- Message delivery status
- Speaker identification with avatars

### Settings Panel
- **General**: Theme, language, auto-save preferences
- **Audio**: Volume controls, noise reduction, echo cancellation
- **Voice**: Model selection, speech speed, auto-play settings
- **Privacy**: Data retention, analytics, local storage options

### Session History
- Search through conversation history
- Filter by date and speaker
- Export conversations as JSON
- Delete individual sessions

### Connection Status
- Real-time connection monitoring
- Latency measurement
- Automatic reconnection
- Server health indicators

## Customization

### Themes
The app uses a dark theme by default with glass morphism effects. To customize:

1. Edit `tailwind.config.js` for color schemes
2. Modify `globals.css` for custom styles
3. Update component classes for different aesthetics

### Animations
Framer Motion animations can be customized in individual components:

- Adjust `initial`, `animate`, and `exit` props
- Modify transition durations and easings
- Add custom animation variants

### API Integration
The frontend communicates with the backend via:

- **REST API** (axios) for authentication and data fetching
- **WebSocket** for real-time messaging and voice data
- **File Upload** for voice messages and media

## Development

### Code Style
- Use functional components with hooks
- Follow React best practices
- Use TypeScript types where beneficial
- Maintain consistent naming conventions

### Performance
- Components are optimized with `useCallback` and `useMemo`
- Lazy loading for route-based code splitting
- Efficient WebSocket connection management
- Optimized re-renders with proper dependency arrays

### Testing
```bash
# Run linting
npm run lint

# Run tests (when implemented)
npm test
```

## Deployment

### Static Hosting (Recommended)
1. Build the project: `npm run build`
2. Deploy the `dist/` folder to your hosting provider:
   - Vercel
   - Netlify
   - GitHub Pages
   - AWS S3 + CloudFront

### Docker
```dockerfile
FROM node:18-alpine AS builder
WORKDIR /app
COPY package*.json ./
RUN npm ci --only=production
COPY . .
RUN npm run build

FROM nginx:alpine
COPY --from=builder /app/dist /usr/share/nginx/html
COPY nginx.conf /etc/nginx/nginx.conf
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
```

## Troubleshooting

### Common Issues

1. **Connection Failed**: Check backend server is running and URLs are correct
2. **Audio Not Working**: Ensure microphone permissions are granted
3. **WebSocket Errors**: Verify WebSocket URL and server WebSocket support
4. **Build Errors**: Clear node_modules and reinstall dependencies

### Debug Mode
Set `VITE_NODE_ENV=development` to enable debug logging and additional tools.

## Browser Compatibility

- Chrome 90+
- Firefox 88+
- Safari 14+
- Edge 90+

Note: Voice recording requires modern browser support for Web Audio API.

## Contributing

1. Follow the existing code style
2. Add tests for new features
3. Update documentation
4. Ensure responsive design
5. Test across different browsers

## License

This project is part of the Multi Voice AI Bot system. See the main project license for details.
