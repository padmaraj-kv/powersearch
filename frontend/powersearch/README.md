# PowerSearch - Desktop Search Application

A beautiful, glass-morphism styled desktop search application built with Electron, React, and TypeScript.

## Features

### 🖼️ **Neumorphic Glass Design**
- Transparent, frameless window with glass-morphism effects
- Beautiful backdrop blur and vibrancy effects on macOS
- Soft shadows and inset/outset styling for neumorphic appearance
- Responsive hover effects and smooth animations

### 🔍 **Smart Search Interface**
- Dynamic left icon that changes based on search keywords:
  - `🖼️` for image searches (image:, img:, photo:)
  - `📄` for documents (pdf:, document:, doc:)
  - `🎬` for videos (video:, movie:)
  - `🎵` for audio (music:, audio:)
  - `💻` for code (code:, programming:)
  - `📁` for folders (folder:, directory:)
  - `🔍` default search icon
- Real-time icon updates as you type
- Loading states with animated indicators

### 🌐 **API Integration**
- Sends search queries to configurable backend endpoint
- POST requests to `https://api.backend.dev/search`
- Handles API responses and error states
- Secure IPC communication between processes

### 🎯 **Window Behavior**
- Dimensions: 700x60 pixels
- Shows immediately when application launches
- Automatically hides when window loses focus
- Click on dock/taskbar icon to show window again
- Non-resizable, non-movable for consistent UX
- Always on top for quick access
- Transparent background with vibrancy effects

## Technical Architecture

### Main Process (`src/main.ts`)
- Window configuration and management
- IPC event handling
- API communication
- Cross-platform compatibility

### Preload Script (`src/preload.ts`)
- Secure context bridge for renderer-main communication
- Type-safe API exposure
- Platform detection

### Renderer Process (`src/renderer.tsx`, `src/components/SearchApp.tsx`)
- React-based user interface
- TypeScript for type safety
- State management with React hooks
- Dynamic icon system
- Keyboard event handling

### Styling (`src/index.css`)
- Modern glass-morphism design
- Neumorphic shadows and effects
- Responsive design principles
- Cross-platform compatibility
- Smooth animations and transitions

## Development

### Prerequisites
- Node.js 16+ 
- npm or yarn

### Setup
```bash
cd frontend/powersearch
npm install
```

### Development Mode
```bash
npm start
```

### Build for Production
```bash
npm run package
```

### Create Installers
```bash
npm run make
```

## Usage

1. **Launch**: Run the application - the search window will appear automatically
2. **Search**: Type your query in the search bar
3. **Smart Prefixes**: Use keywords like `image:`, `pdf:`, `code:` to get context-specific icons
4. **Execute**: Press Enter to send the search query to the backend
5. **Hide**: Click outside the window to hide it
6. **Show Again**: Click the app icon in dock/taskbar to bring the window back

## Configuration

### Backend API Endpoint
Modify the API endpoint in `src/main.ts`:
```typescript
const response = await fetch('YOUR_API_ENDPOINT_HERE', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({ query }),
});
```

## Project Structure
```
src/
├── main.ts          # Main Electron process
├── preload.ts       # Preload script for IPC
├── renderer.tsx     # React renderer entry point
├── index.css        # Global styles
└── components/
    └── SearchApp.tsx # Main React component
```

## Dependencies

### Runtime
- `react` - UI library
- `react-dom` - React DOM renderer
- `electron-squirrel-startup` - Squirrel startup handling

### Development
- `electron` - Desktop app framework
- `@vitejs/plugin-react` - Vite React plugin
- `typescript` - Type safety
- `@types/react` - React type definitions
- Electron Forge - Build and packaging tools

## License

MIT - Feel free to use this project as a template for your own applications! 
