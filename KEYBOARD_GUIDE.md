# ⌨️ Keyboard Input Guide

## 🎯 How to Type in Remote Browser

### Step 1: Click to Focus
1. **Click on any input field** in the video (search box, text field, etc.)
2. The input field will be focused in the remote browser

### Step 2: Start Typing
- Just start typing on your keyboard!
- Keys are sent in real-time to the remote browser

---

## ✅ Supported Keys

### Regular Keys
- ✅ All letters (a-z, A-Z)
- ✅ All numbers (0-9)
- ✅ All symbols (!, @, #, $, %, etc.)
- ✅ Spacebar

### Special Keys
- ✅ **Enter** - Submit forms, new lines
- ✅ **Backspace** - Delete characters
- ✅ **Delete** - Forward delete
- ✅ **Tab** - Navigate between fields
- ✅ **Escape** - Close popups/dialogs
- ✅ **Arrow Keys** (↑↓←→) - Navigate text
- ✅ **Home** - Jump to start of line
- ✅ **End** - Jump to end of line
- ✅ **Page Up/Down** - Scroll page

### Keyboard Shortcuts
- ✅ **Ctrl+A** - Select all
- ✅ **Ctrl+C** - Copy
- ✅ **Ctrl+V** - Paste
- ✅ **Ctrl+X** - Cut

---

## 🎮 Usage Example

### Example 1: Search on YouTube

1. **Start Stream** → Click "▶️ Start Stream"
2. **Navigate** → Go to youtube.com
3. **Click Search Box** → Click on the search input in the video
4. **Type** → Type "music" on your keyboard
5. **Submit** → Press **Enter**
6. Watch the search results appear!

### Example 2: Type a Comment

1. Navigate to any website with a comment box
2. Click on the comment input field
3. Type your message
4. Use **Backspace** to correct mistakes
5. Press **Enter** to submit (or click submit button)

---

## 🔧 Important Notes

### URL Input Field Exception
- When typing in the **URL input field** at the top of the page
- Keys are NOT sent to the remote browser
- This lets you type URLs without interference

### Focus Requirements
- You must **click on an input field first** before typing
- The remote browser needs to know where to send the keys
- After clicking, the video element captures your keyboard

### Key Repeat Prevention
- Keys are debounced to prevent flooding
- If a key seems stuck, release and press again

---

## 🐛 Troubleshooting

### Keys Not Working?

**Problem:** Typing doesn't do anything

**Solutions:**
1. Make sure you **clicked on an input field** in the video first
2. Check if you're connected (status should be green)
3. Check browser console for errors (F12)
4. Try clicking the video element to focus it

### Wrong Characters?

**Problem:** Getting wrong characters or symbols

**Solutions:**
1. Check your keyboard layout (US vs international)
2. Some special characters may not map correctly
3. Use standard alphanumeric keys for best results

### Backspace Not Working?

**Problem:** Backspace doesn't delete text

**Solutions:**
1. Make sure the input field is focused (click it again)
2. Check server console for "⌨️ Special key: Backspace"
3. Try clicking before the text you want to delete

---

## 📊 Technical Details

### How It Works

1. **Browser captures keydown events**
   ```javascript
   document.addEventListener('keydown', ...)
   ```

2. **Sends to server**
   ```javascript
   POST /keyboard { key, code, shift, ctrl, alt }
   ```

3. **Server processes with Selenium**
   ```python
   active_element.send_keys(Keys.ENTER)
   ```

4. **Remote browser receives input**
   - Text appears in input field
   - Actions execute (form submit, etc.)

### Key Mapping

JavaScript `event.key` → Selenium `Keys`:
- "Enter" → Keys.ENTER
- "Backspace" → Keys.BACKSPACE  
- "a" → "a"
- etc.

---

## ✨ Advanced Features

### Multi-Line Text
- Use **Enter** in textareas for new lines
- Supports multi-line editing

### Text Selection
- **Ctrl+A** selects all text
- **Arrow keys** navigate through text
- **Home/End** jump to line boundaries

### Form Navigation
- **Tab** moves between form fields
- **Shift+Tab** goes backwards
- **Enter** submits forms

---

## 🎯 Best Practices

1. ✅ **Always click the input field first** before typing
2. ✅ **Wait for video to update** before continuing
3. ✅ **Use Backspace** to correct mistakes
4. ✅ **Press Enter** to submit forms
5. ✅ **Check server console** to see keys being processed

---

## 📝 Examples of What You Can Do

### Search Engines
- Search Google, Bing, DuckDuckGo
- Type queries and press Enter
- Navigate results with Tab/Arrow keys

### Social Media
- Type posts and comments
- Edit text with Backspace
- Submit with Enter or click

### Forms
- Fill out registration forms
- Enter username/password
- Navigate fields with Tab
- Submit with Enter

### Coding Sites
- Type code snippets
- Use Ctrl+A to select all
- Copy/paste with Ctrl+C/V

---

## 🚀 Quick Reference

| Action | Key | Result |
|--------|-----|--------|
| Type letter | a-z | Character appears |
| Type number | 0-9 | Number appears |
| New line | Enter | Submit/New line |
| Delete back | Backspace | Remove character |
| Delete forward | Delete | Remove next char |
| Select all | Ctrl+A | All text selected |
| Copy | Ctrl+C | Copy selection |
| Paste | Ctrl+V | Paste clipboard |
| Move cursor | ← → ↑ ↓ | Navigate text |

---

## ⚡ Performance Tips

- **Type at normal speed** - system keeps up
- **Don't hold keys** - use single presses
- **Wait for echo** - watch video for feedback
- **Use Backspace sparingly** - plan your typing

---

**Enjoy full keyboard control of your remote browser!** ⌨️🚀

