# Auto-Capture Hook

This hook automatically triggers journal entries every 30 minutes when you're actively working.

## Installation

### 1. Copy the hook file

```bash
cp hooks/journal-auto-capture.js ~/.claude/hooks/
chmod +x ~/.claude/hooks/journal-auto-capture.js
```

### 2. Configure Claude Code hooks

Edit or create `~/.claude/hooks/config.json`:

```json
{
  "hooks": {
    "UserPromptSubmit": [
      {
        "matchers": ["*"],
        "hooks": [
          {
            "type": "command",
            "command": "node ~/.claude/hooks/journal-auto-capture.js",
            "timeout": 5
          }
        ]
      }
    ]
  }
}
```

### 3. Configure auto-capture behavior (optional)

The hook uses these defaults:
- **Capture Interval**: 30 minutes
- **Activity Threshold**: 3 messages minimum

To customize, edit the constants at the top of `journal-auto-capture.js`:

```javascript
const CAPTURE_INTERVAL = 30 * 60 * 1000; // Change to your preferred interval
const MIN_ACTIVITY_THRESHOLD = 3;        // Change minimum activity level
```

## How It Works

1. **State Tracking**: Stores state in `~/.claude/journal-capture-state.json`
   - Last capture timestamp
   - Message count since last capture
   - Current project (detected from working directory)

2. **Activity Detection**: Increments message count on each user prompt

3. **Trigger Conditions**: Auto-capture triggers when:
   - ✅ 30+ minutes elapsed since last capture
   - ✅ 3+ messages sent (activity threshold)

4. **Signal to Claude**: Prints a message that Claude Code sees, prompting it to use the `journal_auto_capture` tool

5. **Reset**: After capturing, resets message count and timestamp

## Manual Testing

Test the hook manually:

```bash
node ~/.claude/hooks/journal-auto-capture.js
```

This will increment the message count. After running 3+ times with 30+ minutes elapsed, you'll see:

```
🕐 Auto-capture triggered: 30 minutes elapsed with activity
   Messages since last capture: 5
   Current project: my-project
   Consider using journal_auto_capture to save recent work.
```

## Troubleshooting

**Hook not triggering:**
- Check `~/.claude/hooks/config.json` is valid JSON
- Verify hook file is executable: `ls -l ~/.claude/hooks/journal-auto-capture.js`
- Check state file: `cat ~/.claude/journal-capture-state.json`

**Force a capture:**
- Delete state file: `rm ~/.claude/journal-capture-state.json`
- Send 3+ messages in Claude Code
- Hook will trigger on next message

**Change intervals:**
- Edit `CAPTURE_INTERVAL` in the hook file
- Example for 15 minutes: `const CAPTURE_INTERVAL = 15 * 60 * 1000;`

## State File Format

```json
{
  "lastCapture": 1699564800000,
  "messageCount": 5,
  "lastProject": "claude-journal-mcp"
}
```

- `lastCapture`: Unix timestamp (milliseconds) of last auto-capture
- `messageCount`: Number of messages since last capture
- `lastProject`: Last detected project directory name

## Disabling Auto-Capture

**Temporarily:**
- Comment out the hook in `~/.claude/hooks/config.json`

**Permanently:**
- Remove the hook entry from `config.json`
- Delete `~/.claude/hooks/journal-auto-capture.js`
- Delete `~/.claude/journal-capture-state.json`
