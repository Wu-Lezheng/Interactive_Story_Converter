# Interactive Novel Converter

Convert a Word document (`.docx`) into a playable, interactive HTML novel with save/load functionality. It provides both English and Chinese support.

## What It Does

The `Converter.py` script reads your story from a Word file (`Story.docx`), parses scenes and choices, and generates a standalone `Interactive_novel.html` file. The resulting HTML is fully self-contained with:

- **Scene navigation** based on player choices
- **Dynamic styling** per scene (custom colors, icons)
- **Save/Load system** using browser local storage
- **Dark theme UI** with smooth transitions and responsive layout

## Requirements

- **Python 3.7+**
- **python-docx** library (for reading `.docx` files)

### Install Dependencies

```bash
pip install python-docx
```

## Quick Start

1. **Prepare your story** in `Story.docx` (see [Formatting Guide](#formatting-guide) below).
2. **Run the converter:**
   ```bash
   python Converter.py
   ```
3. **Open the generated HTML** in your browser.

## Formatting Guide

### Document Structure

Your `Story.docx` must follow this structure:

#### 1. Scene Titles (Heading 1 Style)

Create a new scene by using the **Heading 1** style:

```
First Scene          ← Use Heading 1 style
```

#### 2. Scene Metadata (Optional)

Immediately after the scene title, add metadata on a single line to customize the scene's appearance:

```
METADATA: color=#F54927, icon=🗝️
```

- **icon**: Any emoji or character to display in the scene header (default: 💠)
- **color**: Hex color code for the scene's accent color (default: #4ecdc4)

Example:
```
METADATA: color=#FF6B6B, icon=⚔️ 
```

#### 3. Scene Text

Add paragraphs normally — each paragraph will be displayed as-is:

```
This is the opening scene. The story begins here.

You have multiple choices ahead.
```

To have a line break, add the following in a new paragraph:

```
&nbsp;
```

#### 4. Choices

Define choices using one of these bracket formats. The English brackets `[]` and the Chinese ones `【】` are both supported. Choices link to the next scene:

```
[Choice Text → Next Scene Name]
【Choice Text → Next Scene Name】
[Choice Text -> Next Scene Name]
【Choice Text => Next Scene Name】
```

The `→`, `->`, and `=>` are all supported. The right side must match a scene's Heading 1 title exactly.

Example:
```
[Enter the castle → Chapter 2]
[Run away -> Chapter 3]
```

### Complete Example

```
Chapter 1
METADATA: color=#FF6B6B, icon=🏰

You stand at the castle gates. A guard stops you.

"State your business," he demands.

[I am a diplomat → Chapter 2]
[I am a merchant → Chapter 3]
[I attack! → Chapter 4]


Chapter 2
METADATA: icon=📜, color=#4ECDC4

The guard waves you through. Inside, the castle is grand...

[Continue exploring → Chapter 5]
[Visit the throne room → Chapter 6]


Chapter 3

You begin to haggle with the guard. After some negotiation...

[Proceed to the market → Chapter 5]
```

## Running the Converter

### From Command Line

```bash
python Converter.py
```

The script will:
1. Read `Story.docx` from the current directory
2. Parse all scenes, metadata, and choices
3. Generate `Interactive_novel.html` in the same directory
4. Print progress messages to the console

### Output

On success:
```
Reading Story.docx...
Found Scene: Chapter 1
Found Scene: Chapter 2
Found Scene: Chapter 3
Done! Created Interactive_novel.html
```

### Errors

- **"Story.docx not found"**: Make sure the file exists in the same directory as `Converter.py`
- **"No scenes found"**: Check that you're using **Heading 1** style for scene titles
- **Invalid color format warning**: Ensure color codes are valid hex (e.g., `#FF6B6B` or `#F0F`)

## How the HTML Works

### Player Experience

1. **Open** the HTML in a browser
2. **Read** the current scene
3. **Click** a choice to navigate to the next scene
4. **Save** your progress using the 💾 Save button
5. **Load** a previous save using the ↩️ Load button

### Save System

- Saves are stored in the browser's **local storage** (tied to the file's origin)
- Each save includes: scene name, custom name, timestamp
- **Note:** Saves are browser-specific. Clearing browser data will delete saves.
- To back up saves, export them via the browser console:
  ```javascript
  JSON.parse(localStorage.getItem('interactive_novel_saves_v8') || '[]')
  ```

### File Structure

The generated HTML contains:

- **CSS Styling**: Dark theme with dynamic per-scene colors
- **Story Data**: Embedded JSON containing all scenes and choices
- **JavaScript Engine**: Handles navigation, save/load, and UI updates

## Customization

### Changing the Output Filename

Edit `Converter.py`:
```python
OUTPUT_FILENAME = "Interactive_novel.html"
```

Change to your desired filename (e.g., `my_story.html`).

### Changing the Input Filename

Edit `Converter.py`:
```python
INPUT_FILENAME = "Story.docx"
```

Change to your Word document's filename.

## Troubleshooting

### Issue: Converter doesn't find Story.docx

**Solution:** Ensure `Story.docx` is in the same directory as `Converter.py`. Use absolute paths if needed:
```python
INPUT_FILENAME = r"C:\Path\To\Story.docx"
```

### Issue: Scenes not showing up

**Solution:** Verify all scene titles use the **Heading 1** style in Word. Regular text won't be recognized as scenes.

### Issue: Choices don't work

**Solution:** Make sure choice target names (right side of `→`) match your scene titles exactly (case-insensitive, but spelling must match).

### Issue: Saves disappear

**Solution:** This happens when you clear browser cache/cookies. Use the browser console to export and backup saves before clearing data.

### Issue: Custom colors/icons not applying

**Solution:** Check that the METADATA line is immediately after the scene title and uses the correct format:
```
METADATA: icon=emoji, color=#HEXCODE
```

Hex codes must be valid (3 or 6 hex digits), e.g., `#F0F` or `#FF00FF`.

## Tips & Best Practices

1. **Test choices thoroughly** — typos in scene names will create dead links.
2. **Use meaningful scene names** — they're case-insensitive but must be consistent.
3. **Keep scenes focused** — long scenes are harder to read. Break them into multiple scenes.
4. **Plan your story tree** — sketch out which choices lead where before writing.
5. **Backup your saves** — export from the browser console if saves are important.

## Advanced: Modifying the Template

To customize the HTML output (styling, layout, etc.), edit the `HTML_TEMPLATE` string in `Converter.py`. Changes will apply to all newly generated HTML files.

For example, to change the default accent color:
```python
const defaultColor = "#4ecdc4"; // Cyan fallback
```

Change to:
```python
const defaultColor = "#FF00FF"; // Magenta fallback
```

## License & Attribution

This project uses:
- **python-docx** for Word file parsing
- Vanilla JavaScript (ES6) for the interactive engine
- Browser `localStorage` API for save persistence

## Support

For issues or questions:
1. Check the [Troubleshooting](#troubleshooting) section
2. Verify your Word document formatting matches the [Formatting Guide](#formatting-guide)
3. Check browser console for error messages (F12 → Console tab)

---

**Happy storytelling! 📖**
