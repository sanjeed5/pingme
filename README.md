# pingme

An [Agent Skill](https://agentskills.io) that teaches AI agents to schedule desktop notifications.

## Why?

AI coding agents can run commands but can't proactively notify you at future times. If you have ADHD or lose track of time while coding, you need something to interrupt your hyperfocus.

**pingme** lets your agent schedule notifications using built-in OS tools.

## Setup

### macOS

1. Open **Script Editor** app once (registers with Notification Center)
2. Go to **System Settings → Notifications → Script Editor** → Enable

No other install needed — uses built-in `osascript`.

## Install CLI (optional)

If you want `pingme` available globally (not just via agent):

```bash
git clone https://github.com/sanjeed5/pingme.git
cd pingme
./install.sh
```

This symlinks to `~/.local/bin/pingme`.

## Structure

```
pingme/
├── SKILL.md              # Agent skill definition
├── scripts/
│   └── pingme.py         # The CLI script
├── README.md
└── LICENSE
```

## Usage

```bash
python3 scripts/pingme.py now "message"      # Immediate
python3 scripts/pingme.py in 30m "message"   # In 30 minutes  
python3 scripts/pingme.py at 17:30 "message" # At specific time
python3 scripts/pingme.py list               # Show pending
python3 scripts/pingme.py clear              # Clear all
```

Or symlink to PATH for easier access:

```bash
ln -s /path/to/pingme/scripts/pingme.py ~/.local/bin/pingme
pingme in 30m "Check progress"
```

## How it works

- Uses `osascript` (macOS) or `notify-send` (Linux) for notifications
- Runs `sleep` in background subprocess so it doesn't block
- Tracks scheduled reminders in `~/.pingme/scheduled.json`

## License

MIT
