import docx
import re
import json
import os
import time

# ==========================================
# CONFIGURATION
# ==========================================
INPUT_FILENAME = "Story.docx"
OUTPUT_FILENAME = "Interactive_novel.html"

# ==========================================
# THE ENGINE (Local Storage Persistence)
# ==========================================
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Interactive Novel</title>
    <style>
        /* Base Colors - Used as fallbacks if not set per scene */
        :root {
            --bg-color: #1a1a1a;
            --text-color: #e0e0e0;
            --secondary-color: #2d2d2d;
            --font-main: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            --font-mono: 'Courier New', Courier, monospace;
        }

        body {
            background-color: var(--bg-color);
            color: var(--text-color);
            font-family: var(--font-main);
            margin: 0;
            padding: 0;
            display: flex;
            justify-content: center;
            align-items: center;
            height: 100vh;
            overflow: hidden;
        }

        #game-container {
            width: 90%;
            max-width: 800px;
            background: var(--secondary-color);
            border-radius: 8px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.5);
            display: flex;
            flex-direction: column;
            height: 90vh;
        }

        /* Visual Header & Icon */
        #scene-visual {
            flex-shrink: 0;
            height: 120px;
            background: linear-gradient(135deg, #2c3e50, #000);
            display: flex;
            align-items: center;
            justify-content: center;
            border-bottom: 2px solid #333;
            font-size: 3rem;
            color: #fff; /* Icon color is fixed white */
            transition: all 0.5s ease;
        }
        
        /* SCROLLING AREA */
        #content-scroll-area {
            flex-grow: 1;
            overflow-y: auto;
            padding: 40px;
            scroll-behavior: smooth;
        }
        
        /* Controls Footer */
        #control-panel {
            flex-shrink: 0;
            padding: 15px 40px;
            background: #252525;
            border-top: 1px solid #444;
            display: flex;
            justify-content: space-between;
            align-items: center;
            gap: 10px;
        }
        
        #control-panel button {
            padding: 8px 15px;
            border: 1px solid #777;
            background: transparent;
            color: #ccc;
            border-radius: 4px;
            cursor: pointer;
            transition: all 0.2s;
            font-family: var(--font-main);
        }

        #control-panel button:hover {
            border-color: var(--scene-color, #4ecdc4);
            color: var(--scene-color, #4ecdc4);
        }

        /* Status Message Area */
        #status-message {
            font-size: 0.9rem;
            color: #aaa;
            transition: opacity 0.3s;
        }
        .status-success { color: #4CAF50 !important; }
        .status-error { color: #F44336 !important; }
        .status-info { color: #2196F3 !important; }

        /* Dynamic Colors */
        .scene-accent-color { color: var(--scene-color); }
        .scene-accent-border { border-bottom: 1px solid var(--scene-color) !important; }

        /* Button Styling */
        button.choice-btn {
            background: transparent;
            padding: 15px 20px;
            font-size: 1rem;
            border-radius: 4px;
            cursor: pointer;
            text-align: left;
            transition: all 0.2s ease;
            font-family: var(--font-mono);
            width: 100%;
            border: 1px solid var(--scene-color); 
            color: var(--scene-color);
        }

        button.choice-btn:hover {
            background: var(--scene-color);
            color: var(--bg-color);
            transform: translateX(10px);
            box-shadow: -5px 0 15px var(--scene-color)30; 
        }

        /* Text Styling */
        h1 { padding-bottom: 10px; font-size: 1.8rem; margin-top: 0; }
        p { font-size: 1.1rem; line-height: 1.8; margin-bottom: 20px; }

        /* Choices Container (Inside the scroll area) */
        #choices-container {
            margin-top: 40px;
            padding-top: 20px;
            border-top: 1px dashed #444;
            display: flex;
            flex-direction: column;
            gap: 15px;
        }

        .fade-in { animation: fadeIn 0.5s ease-in; }
        @keyframes fadeIn { from { opacity: 0; transform: translateY(10px); } to { opacity: 1; transform: translateY(0); } }
        
        /* Scrollbar Styling */
        ::-webkit-scrollbar { width: 10px; }
        ::-webkit-scrollbar-track { background: #222; }
        ::-webkit-scrollbar-thumb { background: #444; border-radius: 5px; }
        ::-webkit-scrollbar-thumb:hover { background: var(--scene-color); }

        /* --- Modal Styles --- */
        #modal-overlay {
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: rgba(0, 0, 0, 0.8);
            display: flex;
            justify-content: center;
            align-items: center;
            z-index: 1000;
            /* Initial state: Hidden and ignores clicks */
            opacity: 0;
            visibility: hidden;
            pointer-events: none;
            transition: opacity 0.3s, visibility 0.3s;
        }

        /* Modal Class for Open State */
        #modal-overlay.modal-open {
            opacity: 1;
            visibility: visible;
            pointer-events: auto; /* Re-enables clicks when visible */
        }

        #modal-content {
            background: var(--secondary-color);
            padding: 30px;
            border-radius: 8px;
            width: 90%;
            max-width: 600px;
            box-shadow: 0 15px 35px rgba(0, 0, 0, 0.7);
        }
        .modal-header {
            color: var(--scene-color, #4ecdc4);
            border-bottom: 1px solid #444;
            padding-bottom: 10px;
            margin-bottom: 20px;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }
        #slots-container {
            max-height: 300px;
            overflow-y: auto;
            border: 1px solid #333;
            border-radius: 4px;
            padding: 10px;
        }
        .save-slot {
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 10px;
            border-bottom: 1px solid #333;
            cursor: pointer;
            transition: background 0.1s;
        }
        .save-slot:last-child { border-bottom: none; }
        .save-slot:hover { background: #353535; }
        .slot-info { font-size: 0.9rem; }
        .slot-name { font-weight: bold; color: var(--text-color); }
        .slot-time { font-size: 0.8rem; color: #999; }
        .slot-actions button {
            margin-left: 10px;
            padding: 5px 10px;
            border: 1px solid #555;
            background: transparent;
            border-radius: 3px;
            cursor: pointer;
            transition: background 0.2s, color 0.2s;
        }
        .slot-actions .load-btn {
            color: #4CAF50;
            border-color: #4CAF50;
        }
        .slot-actions .delete-btn {
            color: #F44336;
            border-color: #F44336;
        }
        .slot-actions button:hover {
            opacity: 0.8;
            background: #555;
            color: white;
        }
        #save-input-group {
            display: flex;
            gap: 10px;
            margin-top: 20px;
        }
        #save-input-group input {
            flex-grow: 1;
            padding: 10px;
            border: 1px solid #555;
            background: #222;
            color: var(--text-color);
            border-radius: 4px;
        }
        #save-input-group button {
            background: var(--scene-color, #4ecdc4);
            color: var(--bg-color);
            font-weight: bold;
            border: none;
            padding: 10px 15px;
            border-radius: 4px;
            cursor: pointer;
        }
    </style>
</head>
<body>

    <div id="game-container">
        <!-- Visual Header -->
        <div id="scene-visual">
            <div id="scene-icon"></div>
        </div>

        <!-- Single Scrolling Area for Text AND Choices -->
        <div id="content-scroll-area">
            <div id="story-content"></div>
            <div id="choices-container"></div>
        </div>
        
        <!-- Controls Footer -->
        <div id="control-panel">
            <button id="save-btn" onclick="openSaveLoadModal('save')">💾 Save Game</button>
            <div id="status-message">Ready.</div>
            <button id="load-btn" onclick="openSaveLoadModal('load')">↩️ Load Game</button>
        </div>
    </div>
    
    <!-- Save/Load Modal -->
    <div id="modal-overlay">
        <div id="modal-content">
            <div class="modal-header">
                <h2 id="modal-title">Save/Load</h2>
                <button onclick="closeSaveLoadModal()" style="font-size: 1.5rem; background: none; border: none; color: #fff; cursor: pointer;">&times;</button>
            </div>
            
            <div id="slots-container">
                <div id="slots-list"><!-- Save slots will be inserted here --></div>
                <p id="no-saves-msg" style="text-align: center; color: #999; margin-top:10px;">No saved games found in local storage.</p>
            </div>
            
            <div id="save-input-group" style="display: none;">
                <input type="text" id="slot-name-input" placeholder="Enter save slot name (e.g., Chapter 3 Backup)">
                <button onclick="handleSaveAction()">Save Now</button>
            </div>
            
        </div>
    </div>

    <script>
        // Data injected by Python
        const storyData = STORY_DATA_PLACEHOLDER;
        const defaultColor = "#4ecdc4"; // Cyan fallback
        const defaultIcon = '💠'; // Diamond fallback
        
        // --- Game State and Local Storage Key ---
        let currentSceneId = '';
        const SAVE_KEY = 'interactive_novel_saves'; // Key remains the same for continuity
        
        // --- Utility Functions ---

        function showStatus(message, type = 'info') {
            const statusDiv = document.getElementById('status-message');
            statusDiv.innerHTML = message;
            statusDiv.className = `status-${type}`;
            setTimeout(() => {
                statusDiv.className = ''; // Clear class after a delay
                statusDiv.innerHTML = 'Ready.';
            }, 3000);
        }
        
        // Function to format the timestamp
        function formatTime(timestamp) {
            const date = new Date(timestamp);
            return date.toLocaleDateString() + ' ' + date.toLocaleTimeString();
        }

        // --- Game Logic ---
        
        window.showScene = function(sceneId) {
            let key = Object.keys(storyData).find(k => k.trim().toLowerCase() === sceneId.trim().toLowerCase());
            if (!key) { 
                console.warn("Scene not found: " + sceneId); 
                showStatus(`Error: Scene '${sceneId}' not found.`, 'error');
                return; 
            }

            const scene = storyData[key];
            currentSceneId = key; // Update current scene state
            
            const scrollArea = document.getElementById('content-scroll-area');
            const contentDiv = document.getElementById('story-content');
            const choicesDiv = document.getElementById('choices-container');
            const iconDiv = document.getElementById('scene-icon');
            const visualDiv = document.getElementById('scene-visual');
            
            // Apply Dynamic Styles
            const accentColor = scene.color || defaultColor;
            document.documentElement.style.setProperty('--scene-color', accentColor);
            
            // Apply icon and visual updates
            iconDiv.innerHTML = scene.icon || defaultIcon;
            visualDiv.style.borderColor = accentColor;
            visualDiv.style.background = `linear-gradient(135deg, ${accentColor}AA, #000)`;

            // Render Text
            contentDiv.innerHTML = `
                <h1 class="fade-in scene-accent-color scene-accent-border">${key}</h1>
                <div class="fade-in">${scene.text}</div>
            `;

            // Render Choices
            choicesDiv.innerHTML = "";
            if (scene.choices.length === 0) {
                choicesDiv.innerHTML = "<p style='color:#777; text-align:center'>[End of Story]</p><button class='choice-btn' onclick='showScene(Object.keys(storyData)[0])'>Start Over</button>";
            } else {
                scene.choices.forEach(choice => {
                    const btn = document.createElement('button');
                    btn.className = "choice-btn fade-in";
                    btn.innerText = choice.text;
                    btn.onclick = () => window.showScene(choice.next);
                    choicesDiv.appendChild(btn);
                });
            }

            // Reset scroll to top
            scrollArea.scrollTop = 0;
            window.closeSaveLoadModal(); // Ensure modal closes when navigating
        }

        // --- Local Storage Persistence Functions ---

        function getSaveSlots() {
            try {
                const json = localStorage.getItem(SAVE_KEY);
                return json ? JSON.parse(json) : [];
            } catch (e) {
                console.error("Error reading localStorage:", e);
                return [];
            }
        }
        
        function saveSaveSlots(slots) {
             try {
                localStorage.setItem(SAVE_KEY, JSON.stringify(slots));
            } catch (e) {
                console.error("Error writing to localStorage:", e);
                showStatus("Error: Could not save game. Local storage is full or restricted.", 'error');
            }
        }

        window.saveGame = function(slotName) {
            if (!currentSceneId) {
                showStatus("Error: Cannot save empty scene.", 'error');
                return;
            }

            let slots = getSaveSlots();
            const newSave = {
                id: Date.now().toString(), // Unique ID
                name: slotName || `AutoSave @ ${formatTime(Date.now())}`,
                timestamp: Date.now(),
                sceneId: currentSceneId
            };

            slots.unshift(newSave); // Add to the beginning (most recent first)
            saveSaveSlots(slots);
            showStatus(`Game saved as '${newSave.name}'!`, 'success');
            
            loadSaveSlots();
            
            // Close the modal after a successful named save
            window.closeSaveLoadModal(); 
        };

        window.loadGame = function(slotId) {
            const slots = getSaveSlots();
            const slot = slots.find(s => s.id === slotId);

            if (slot && slot.sceneId) {
                window.showScene(slot.sceneId);
                showStatus(`Game loaded: '${slot.name}'`, 'success');
                window.closeSaveLoadModal(); // Close after loading
            } else {
                showStatus("Error: Save slot not found.", 'error');
            }
        };

        window.deleteSlot = function(slotId) {
            let slots = getSaveSlots();
            const initialLength = slots.length;
            slots = slots.filter(s => s.id !== slotId);
            
            if (slots.length < initialLength) {
                saveSaveSlots(slots);
                showStatus("Save slot deleted.", 'info');
                loadSaveSlots(); 
            }
        };

        // --- Modal Control ---
        
        let modalMode = 'load'; // 'save' or 'load'
        const modalOverlay = document.getElementById('modal-overlay');

        // Close modal when clicking outside the content box
        modalOverlay.addEventListener('click', function(e) {
            if (e.target === modalOverlay) {
                window.closeSaveLoadModal();
            }
        });
        function loadSaveSlots() {
            const slots = getSaveSlots();
            const list = document.getElementById('slots-list');
            const noSavesMsg = document.getElementById('no-saves-msg');
            // Only clear the list area so static elements (like the no-saves message)
            // are not accidentally removed from the DOM.
            list.innerHTML = '';
            
            if (slots.length === 0) {
                noSavesMsg.style.display = 'block';
                return;
            }
            noSavesMsg.style.display = 'none';

            slots.forEach(slot => {
                const slotDiv = document.createElement('div');
                slotDiv.className = 'save-slot';
                slotDiv.innerHTML = `
                    <div class="slot-info">
                        <div class="slot-name">${slot.name}</div>
                        <div class="slot-time">Scene: ${slot.sceneId} | Saved: ${formatTime(slot.timestamp)}</div>
                    </div>
                    <div class="slot-actions">
                        <button class="load-btn" onclick="loadGame('${slot.id}')">Load</button>
                        <button class="delete-btn" onclick="deleteSlot('${slot.id}')">Delete</button>
                    </div>
                `;
                list.appendChild(slotDiv);
            });
        }
        
        window.handleSaveAction = function() {
            const input = document.getElementById('slot-name-input');
            const slotName = input.value.trim() || `AutoSave @ ${formatTime(Date.now())}`;
            window.saveGame(slotName);
            input.value = ''; // Clear input after saving
        }

        window.openSaveLoadModal = function(mode) {
            modalMode = mode;
            const modalTitle = document.getElementById('modal-title');
            const saveInputGroup = document.getElementById('save-input-group');
            
            loadSaveSlots();

            if (mode === 'save') {
                modalTitle.textContent = 'Save Current Game';
                saveInputGroup.style.display = 'flex';
            } else {
                modalTitle.textContent = 'Load Saved Game';
                saveInputGroup.style.display = 'none';
            }
            
            modalOverlay.classList.add('modal-open');
        };

        window.closeSaveLoadModal = function() {
            modalOverlay.classList.remove('modal-open');
        };

        // --- Initialization ---

        function initializeGame() {
            // Check if there's a quick save to start with
            const startKey = Object.keys(storyData)[0];
            if (startKey) window.showScene(startKey);
            // Ensure the modal is closed on start
            window.closeSaveLoadModal(); 
        }

        // Start the application initialization
        initializeGame();

    </script>
</body>
</html>
"""

# ==========================================
# PARSER LOGIC
# ==========================================

def parse_docx(filename):
    if not os.path.exists(filename):
        print(f"Error: {filename} not found.")
        return None

    doc = docx.Document(filename)
    story = {}
    
    current_scene = None
    current_text = []
    
    # Regex for metadata: looks for a line starting with 'METADATA:'
    metadata_line_pattern = re.compile(r"^METADATA\s*:(.*)$", re.IGNORECASE)
    # Internal regex to parse 'key=value' pairs (handles icon=X, color=#Y)
    key_value_pattern = re.compile(r"(icon|color)\s*=\s*(.+?)(?:,\s*|\s*$)", re.IGNORECASE)
    
    # Regex for choice: [[Text -> Target]] or 【Text -> Target】
    choice_pattern = re.compile(r"[\[【](.*?)\s*(?:->|=>|→)\s*(.*?)[\]】]")

    print(f"Reading {filename}...")

    for para in doc.paragraphs:
        text = para.text.strip()
        if not text:
            continue
            
        # 1. Check for Heading 1 (New Scene)
        if para.style.name.startswith('Heading 1'):
            # Save previous scene
            if current_scene:
                story[current_scene]['text'] = "<p>" + "</p><p>".join(current_text) + "</p>"
            
            # Start new scene
            current_scene = text
            story[current_scene] = { "text": "", "choices": [], "icon": None, "color": None }
            current_text = []
            print(f"Found Scene: {current_scene}")
        
        else:
            if not current_scene: continue

            # 2. Check for Metadata Line (only immediately after a scene title)
            meta_line_match = metadata_line_pattern.match(text)
            if meta_line_match and not story[current_scene]['text']: # Only check metadata before main text starts
                metadata_string = meta_line_match.group(1).strip()
                
                # Parse key=value pairs within the metadata string
                for kv_match in key_value_pattern.finditer(metadata_string):
                    key = kv_match.group(1).lower()
                    value = kv_match.group(2).strip()

                    if key == 'icon':
                        story[current_scene]['icon'] = value
                    elif key == 'color':
                        # Simple hex validation
                        if re.match(r"^#([0-9A-Fa-f]{3}){1,2}$", value):
                            story[current_scene]['color'] = value.upper()
                        else:
                            print(f"  - Warning: Invalid color format '{value}'. Skipping.")
                
                continue # Do not add metadata line to story text

            # 3. Check for Choices
            choices_found = list(choice_pattern.finditer(text))
            
            if choices_found:
                for match in choices_found:
                    choice_text = match.group(1).strip()
                    target_scene = match.group(2).strip()
                    
                    # Store the choice
                    story[current_scene]['choices'].append({
                        "text": choice_text,
                        "next": target_scene
                    })
            else:
                # 4. Regular Text
                current_text.append(text)

    # Save last scene
    if current_scene:
        story[current_scene]['text'] = "<p>" + "</p><p>".join(current_text) + "</p>"

    return story

def generate_html(story_data):
    if not story_data:
        print("No scenes found. Please check Heading 1 styles and try again.")
        return

    # Convert to JSON and inject
    json_data = json.dumps(story_data, indent=4, ensure_ascii=False)
    final_html = HTML_TEMPLATE.replace("STORY_DATA_PLACEHOLDER", json_data)
    
    with open(OUTPUT_FILENAME, "w", encoding="utf-8") as f:
        f.write(final_html)
    
    print(f"Done! Created {OUTPUT_FILENAME}")

if __name__ == "__main__":
    data = parse_docx(INPUT_FILENAME)
    generate_html(data)
