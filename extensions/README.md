# prompt makeuper Chrome Extension

A Chrome extension that provides a convenient interface for the prompt makeuper service. Optimize your prompts using AI-powered skill selection and iterative refinement.

## Prerequisites

Before using this extension, ensure that:

1. **The backend server is running** at `http://localhost:8000`
   ```bash
   cd /home/yubo/AI_PRJ/prompt_makeuper
   uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
   ```

2. **You have Chrome or Chromium-based browser** installed (Chrome, Edge, Brave, etc.)

## Installation

### Step 1: Open Chrome Extensions Page

Navigate to `chrome://extensions/` in your browser address bar.

Alternatively:
- Click the three-dot menu in the top-right corner
- Go to **More Tools** > **Extensions**

### Step 2: Enable Developer Mode

- Toggle the **Developer mode** switch in the top-right corner

### Step 3: Load the Extension

1. Click the **Load unpacked** button
2. Navigate to and select the `extensions/` directory
3. Click **Select Folder**

The extension should now appear in your extensions list with the name "prompt makeuper".

## Usage

### Basic Usage

1. **Click the extension icon** in your browser toolbar
2. **Check the status indicator** in the header:
   - 🟢 Green dot = Server is online
   - 🔴 Red dot = Server is offline
3. **Enter your prompt** in the input textarea at the top
4. **Click "Optimize & Open Results"** or press `Ctrl/Cmd + Enter`
5. **A persistent results window opens** with your optimized prompt
6. **Click "Copy"** in the results window to copy to your clipboard

### Features

- **Persistent Results Window**: Optimization results open in a dedicated window that stays open until you close it - click outside won't close it
- **Server Health Monitoring**: Real-time status indicator shows if the backend is available
- **Keyboard Shortcut**: Press `Ctrl/Cmd + Enter` to quickly optimize your prompt
- **Copy to Clipboard**: One-click copying of the optimized prompt
- **Metadata Display**: Shows which skill was used and how many iterations were performed
- **Collapsible Original Prompt**: View your original prompt for comparison
- **Input Validation**: The Optimize button is disabled when input is empty
- **Error Handling**: Clear error messages for network issues, timeouts, and server problems
- **Auto-Refresh**: Server status is checked every 30 seconds
- **Keyboard Shortcuts in Results Window**: Use `Ctrl/Cmd+W` to close, `Ctrl/Cmd+C` to copy

## Troubleshooting

### Server Shows as Offline (Red Dot)

**Possible causes:**
1. Backend server is not running
2. Server is running on a different port
3. CORS is not enabled on the backend

**Solutions:**
1. Start the backend server:
   ```bash
   cd /home/yubo/AI_PRJ/prompt_makeuper
   uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
   ```

2. Verify the server is running:
   ```bash
   curl http://localhost:8000/health
   ```

3. Check if the port is correct in `popup.js`:
   - Look for `const API_BASE_URL = 'http://localhost:8000';`
   - Adjust if your server uses a different port

### "Network Error" or "Request Timeout"

**Possible causes:**
1. Backend server is not responding
2. Request is taking too long (>30 seconds)
3. Firewall or antivirus blocking the connection

**Solutions:**
1. Check the backend server logs for errors
2. Try a shorter prompt for faster processing
3. Temporarily disable firewall/antivirus to test
4. Increase the timeout in `popup.js` (line ~93):
   ```javascript
   timeout: 30000 // Increase to 60000 for 60 seconds
   ```

### "Nothing to Copy" Message

**Solution:**
- Ensure there is text in the output textarea before clicking Copy
- A successful optimization must have completed first

### Extension Not Loading

**Possible causes:**
1. Manifest.json syntax error
2. Missing files (popup.html, popup.js, popup.css)

**Solutions:**
1. Check Chrome Extensions page for error messages
2. Verify all required files are present in the directory:
   - `manifest.json`
   - `popup.html`
   - `popup.js`
   - `popup.css`
3. Try removing and re-adding the extension

### CORS Errors

If you see CORS-related errors in the browser console:

**Solution:**
Ensure the backend has CORS enabled for `chrome-extension://` origins. The FastAPI backend should have:

```python
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Or specific chrome-extension:// URLs
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

## Development

### Modifying the Extension

1. Make changes to any file in the `extensions/` directory
2. Go to `chrome://extensions/`
3. Click the **Refresh** icon on the prompt makeuper extension card
4. Re-open the popup to see changes

### API Endpoints Used

- **GET `/health`**: Check if the server is running
  ```json
  { "status": "healthy" }
  ```

- **POST `/makeup_prompt`**: Optimize a prompt
  ```json
  // Request
  { "input_prompt": "Your prompt here" }

  // Response
  {
    "output_prompt": "Optimized prompt",
    "skill_used": "clarity",
    "iterations": 2
  }
  ```

## File Structure

```
extensions/
├── manifest.json    # Extension configuration (Manifest V3)
├── popup.html       # Main popup UI structure
├── popup.js         # Application logic and API calls
├── popup.css        # Styling for popup
├── results.html     # Persistent results window UI
├── results.js       # Results window logic
├── results.css      # Styling for results window
├── README.md        # This file
└── icon*.png        # Extension icons (optional, not included)
```

## Permissions

The extension requires:

- **`activeTab`**: To interact with the current tab (for future features)
- **`host_permissions` for `http://localhost:8000/*`**: To communicate with the backend API

## Browser Compatibility

This extension uses **Manifest V3** and is compatible with:
- Google Chrome (version 88+)
- Microsoft Edge (version 88+)
- Brave Browser
- Opera (version 74+)
- Other Chromium-based browsers

## License

This extension is part of the prompt makeuper project.
