#!/usr/bin/env node

/**
 * Auto-capture hook for Claude Journal MCP
 *
 * Triggers auto-capture every 30 minutes if activity occurred.
 *
 * Installation:
 *   1. Copy to ~/.claude/hooks/journal-auto-capture.js
 *   2. Make executable: chmod +x ~/.claude/hooks/journal-auto-capture.js
 *   3. Add to ~/.claude/hooks/config.json (see README.md)
 */

const fs = require('fs');
const path = require('path');
const os = require('os');

// Configuration
const CAPTURE_INTERVAL = 30 * 60 * 1000; // 30 minutes in milliseconds
const MIN_ACTIVITY_THRESHOLD = 3; // Minimum messages since last capture
const STATE_FILE = path.join(os.homedir(), '.claude', 'journal-capture-state.json');

// Load or initialize state
function loadState() {
  try {
    if (fs.existsSync(STATE_FILE)) {
      const data = fs.readFileSync(STATE_FILE, 'utf8');
      return JSON.parse(data);
    }
  } catch (error) {
    console.error(`Warning: Failed to load state: ${error.message}`);
  }

  return {
    lastCapture: 0,
    messageCount: 0,
    lastProject: null
  };
}

// Save state
function saveState(state) {
  try {
    // Ensure directory exists
    const dir = path.dirname(STATE_FILE);
    if (!fs.existsSync(dir)) {
      fs.mkdirSync(dir, { recursive: true });
    }

    fs.writeFileSync(STATE_FILE, JSON.stringify(state, null, 2), 'utf8');
  } catch (error) {
    console.error(`Warning: Failed to save state: ${error.message}`);
  }
}

// Get current working directory (project detection)
function getCurrentProject() {
  try {
    const cwd = process.cwd();
    const parts = cwd.split(path.sep);
    // Return last directory name as project
    return parts[parts.length - 1];
  } catch {
    return null;
  }
}

// Main logic
function main() {
  const state = loadState();
  const now = Date.now();
  const elapsed = now - state.lastCapture;

  // Increment message count
  state.messageCount++;

  // Update current project
  const currentProject = getCurrentProject();
  if (currentProject) {
    state.lastProject = currentProject;
  }

  // Check if we should trigger auto-capture
  const shouldCapture = (
    elapsed > CAPTURE_INTERVAL ||
    state.messageCount >= MIN_ACTIVITY_THRESHOLD
  );

  if (shouldCapture) {
    console.log('🕐 Journal auto-capture triggered');
    console.log(`   ${state.messageCount} messages exchanged since last capture`);
    if (state.lastProject) {
      console.log(`   Project: ${state.lastProject}`);
    }
    console.log('');
    console.log('📝 Please capture this session to the journal:');
    console.log('   - Summarize the goal (what we were trying to do)');
    console.log('   - Summarize what was accomplished');
    console.log('   - Use journal_auto_capture with a brief summary');
    console.log('');

    // Reset state
    state.lastCapture = now;
    state.messageCount = 0;
  }

  // Save updated state
  saveState(state);
}

// Run
main();
