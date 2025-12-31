---
name: pingme
description: Send desktop notifications to interrupt the user. Use when user asks to be reminded at a specific time or after a duration, or proactively during day planning to schedule check-ins, breaks, and hard stops. Helps combat time blindness and hyperfocus on wrong tasks.
---

# Pingme

Send desktop notifications from the command line. Use this to interrupt the user at specific times.

## When to Use

- User asks: "remind me in 30 minutes" or "ping me at 5:30pm"
- During day planning: schedule movement breaks, task check-ins, hard stops
- Before time blocks end: "15 minutes left on this task"
- ADHD support: break hyperfocus, enforce boundaries

## Commands

### Immediate notification

```bash
# macOS
terminal-notifier -title "Ping" -message "YOUR MESSAGE" -sound default

# Linux
notify-send "Ping" "YOUR MESSAGE"
```

### Delayed notification (relative time)

Run in background so it doesn't block:

```bash
# "in 30m" = 1800 seconds
(sleep 1800 && terminal-notifier -title "⏰ Ping" -message "YOUR MESSAGE" -sound default) &

# "in 1h" = 3600 seconds
(sleep 3600 && terminal-notifier -title "⏰ Ping" -message "YOUR MESSAGE" -sound default) &

# "in 90m" = 5400 seconds
(sleep 5400 && terminal-notifier -title "🚶 Break" -message "Movement break - stand up" -sound default) &
```

### Scheduled notification (absolute time)

Calculate seconds until target time, then sleep:

```bash
# For a specific time today (e.g., 5:30pm)
TARGET=$(date -j -f "%H:%M" "17:30" +%s 2>/dev/null || date -d "17:30" +%s)
NOW=$(date +%s)
DELAY=$((TARGET - NOW))
if [ $DELAY -gt 0 ]; then
  (sleep $DELAY && terminal-notifier -title "⏰ Ping" -message "YOUR MESSAGE" -sound default) &
fi
```

## Quick Reference

| Duration | Seconds |
|----------|---------|
| 15m      | 900     |
| 30m      | 1800    |
| 45m      | 2700    |
| 1h       | 3600    |
| 90m      | 5400    |
| 2h       | 7200    |

## Setup

macOS: `brew install terminal-notifier`
Linux: `notify-send` is usually pre-installed

## Examples

```bash
# User: "remind me in 45 min to check the build"
(sleep 2700 && terminal-notifier -title "⏰ Ping" -message "Check the build" -sound default) &

# Day planning: schedule wrap-up reminder
TARGET=$(date -j -f "%H:%M" "17:30" +%s); NOW=$(date +%s); DELAY=$((TARGET - NOW)); (sleep $DELAY && terminal-notifier -title "🏠 Wrap Up" -message "Client work done - evening time" -sound default) &

# Movement break every 90 min
(sleep 5400 && terminal-notifier -title "🚶 Break" -message "Stand up, leave the room" -sound default) &
```
