# pingme

An [Agent Skill](https://agentskills.io) that teaches AI agents to send scheduled desktop notifications.

## Why?

AI coding agents (Claude Code, Cursor, Copilot) can run commands but can't proactively notify you at future times. If you have ADHD or just lose track of time while coding, you need something to interrupt your hyperfocus.

**pingme** teaches your agent to schedule notifications using built-in OS tools — no extra software needed.

## Setup

### macOS

1. Open **Script Editor** app once (so it registers with Notification Center)
2. Go to **System Settings → Notifications → Script Editor** → Enable notifications

That's it. No install needed — uses built-in `osascript`.


## Usage

Once set up, just ask your agent:

- "Remind me in 30 minutes to check on the build"
- "Ping me at 5:30pm to wrap up"
- "Schedule movement breaks every 90 minutes"

The agent runs a background command and you get a notification at the right time.

## How it works

No magic — just built-in OS tools:

- `osascript` (macOS) or `notify-send` (Linux) for notifications
- `sleep` for delays
- Background processes `(&)` so commands don't block

## License

MIT
