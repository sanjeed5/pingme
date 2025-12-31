---
name: pingme
description: Send desktop notifications to interrupt the user. Use when user asks to be reminded at a specific time or after a duration, or proactively during day planning to schedule check-ins, breaks, and hard stops. Helps combat time blindness and hyperfocus on wrong tasks.
---

# Pingme

Schedule desktop notifications from the command line.

## Commands

```bash
pingme now "message"           # Immediate notification
pingme in 30m "message"        # In 30 minutes
pingme in 1h30m "message"      # In 1 hour 30 minutes
pingme at 17:30 "message"      # At specific time (24h format)
pingme at 5:30pm "message"     # At specific time (12h format)
pingme list                    # Show pending reminders
pingme clear                   # Clear all tracked reminders
```

## When to Use

- User asks: "remind me in 30 minutes" or "ping me at 5:30pm"
- During day planning: schedule movement breaks, task check-ins, hard stops
- Before time blocks end: warn user 15 min before block ends
- ADHD support: break hyperfocus, enforce boundaries

## Examples

```bash
# User: "remind me in 45 min to check the build"
pingme in 45m "Check the build"

# Day planning: schedule hard stops
pingme at 17:30 "Wrap up client work - passion project time"
pingme at 19:45 "Start wrapping up - Sulbia time at 8pm"

# Movement breaks
pingme in 90m "Movement break - stand up, leave the room"

# Check what's pending
pingme list
```

## Setup

Requires the `pingme` script in PATH. Tracks reminders in `~/.pingme/scheduled.json`.
