# pingme

An [Agent Skill](https://agentskills.io) that teaches AI agents to send scheduled desktop notifications.

## Why?

AI coding agents (Claude Code, Cursor, Copilot) can run commands but can't proactively notify you at future times. If you have ADHD or just lose track of time while coding, you need something to interrupt your hyperfocus.

**pingme** teaches your agent to schedule notifications using existing CLI tools — no new software needed.

## Setup

### 1. Install notification tool

```bash
# macOS
brew install terminal-notifier

# Linux (usually pre-installed)
sudo apt install libnotify-bin
```

### 2. Add the skill to your agent

**Claude Code:** Copy `SKILL.md` to your `.claude/skills/pingme/` folder or reference it in your project.

**Cursor:** Add the SKILL.md content to your `.cursorrules` or project instructions.

**Other agents:** Include the SKILL.md content in your agent's context.

## Usage

Once set up, just ask your agent:

- "Remind me in 30 minutes to check on the build"
- "Ping me at 5:30pm to wrap up"
- "Schedule movement breaks every 90 minutes"

The agent will run the appropriate background command and you'll get a desktop notification at the right time.

## How it works

No magic — just existing tools:

- `terminal-notifier` (macOS) or `notify-send` (Linux) for notifications
- `sleep` for delays
- Background processes `(&)` so commands don't block

## License

MIT
