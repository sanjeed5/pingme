---
name: pingme
description: Schedule desktop notifications to interrupt the user. Use when user asks to be reminded at a specific time or after a duration, or proactively during day planning to schedule check-ins, breaks, and hard stops. Helps combat time blindness and hyperfocus.
---

# Pingme

Schedule desktop notifications from the command line. Tracks pending reminders in `~/.pingme/`. Reminders survive sleep and reboot (uses launchd).

## Usage

Run the script at `scripts/pingme.py`:

```bash
python3 scripts/pingme.py now "message"           # Immediate notification
python3 scripts/pingme.py in 30m "message"        # In 30 minutes
python3 scripts/pingme.py in 1h30m "message"      # In 1 hour 30 minutes
python3 scripts/pingme.py at 17:30 "message"      # At specific time (24h)
python3 scripts/pingme.py at 5:30pm "message"     # At specific time (12h)
python3 scripts/pingme.py every 90m "message"     # Recurring every 90 minutes
python3 scripts/pingme.py list                    # Show pending reminders
python3 scripts/pingme.py cancel <id>             # Cancel specific reminder
python3 scripts/pingme.py clear                   # Clear all reminders
```

Note: Times in the past auto-schedule for tomorrow. Reminders survive sleep/reboot.

## When to Use

- User asks: "remind me in 30 minutes" or "ping me at 5:30pm"
- During day planning: schedule movement breaks, task check-ins, hard stops
- Before time blocks end: warn user 15 min before block ends
- ADHD support: break hyperfocus, enforce boundaries

## Examples

```bash
# User: "remind me in 45 min to check the build"
python3 scripts/pingme.py in 45m "Check the build"

# Day planning: schedule hard stops
python3 scripts/pingme.py at 17:30 "Wrap up client work - passion project time"
python3 scripts/pingme.py at 19:45 "Start wrapping up - evening time at 8pm"

# Movement breaks (recurring)
python3 scripts/pingme.py every 90m "Movement break - stand up, leave the room"

# Check what's pending
python3 scripts/pingme.py list

# Cancel the 5pm reminder
python3 scripts/pingme.py cancel 17:30
python3 scripts/pingme.py cancel a3f     # or by ID prefix
python3 scripts/pingme.py cancel wrap    # or by message substring
```

## Setup

**macOS:** Open Script Editor app once, then enable notifications in System Settings → Notifications → Script Editor.

**Linux:** Replace `osascript` line in script with `notify-send`.
