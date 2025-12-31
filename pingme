#!/usr/bin/env python3
"""
pingme - Schedule desktop notifications from the command line.

Usage:
    pingme now "message"           # Immediate notification
    pingme in 30m "message"        # In 30 minutes
    pingme at 17:30 "message"      # At specific time (24h format)
    pingme list                    # Show pending reminders
    pingme clear                   # Clear all pending
"""

import json
import os
import re
import subprocess
import sys
from datetime import datetime, timedelta
from pathlib import Path

PINGME_DIR = Path.home() / ".pingme"
SCHEDULED_FILE = PINGME_DIR / "scheduled.json"


def ensure_dir():
    PINGME_DIR.mkdir(exist_ok=True)
    if not SCHEDULED_FILE.exists():
        SCHEDULED_FILE.write_text("[]")


def load_scheduled():
    ensure_dir()
    return json.loads(SCHEDULED_FILE.read_text())


def save_scheduled(data):
    ensure_dir()
    SCHEDULED_FILE.write_text(json.dumps(data, indent=2))


def send_notification(message: str, title: str = "⏰ Ping"):
    subprocess.run([
        "osascript", "-e",
        f'display notification "{message}" with title "{title}" sound name "Glass"'
    ])


def parse_duration(s: str) -> int:
    """Parse duration like '30m', '1h', '1h30m', '90m' to seconds."""
    total = 0
    for match in re.finditer(r'(\d+)\s*(h|m|s)', s.lower()):
        val, unit = int(match.group(1)), match.group(2)
        if unit == 'h':
            total += val * 3600
        elif unit == 'm':
            total += val * 60
        elif unit == 's':
            total += val
    return total or int(s)  # fallback: treat as seconds


def parse_time(s: str) -> datetime:
    """Parse time like '17:30' or '5:30pm' to datetime today."""
    now = datetime.now()
    
    # Try 24h format first
    try:
        t = datetime.strptime(s, "%H:%M")
        return now.replace(hour=t.hour, minute=t.minute, second=0, microsecond=0)
    except ValueError:
        pass
    
    # Try 12h format
    try:
        t = datetime.strptime(s.lower(), "%I:%M%p")
        return now.replace(hour=t.hour, minute=t.minute, second=0, microsecond=0)
    except ValueError:
        pass
    
    # Try without colon
    try:
        t = datetime.strptime(s.lower(), "%I%p")
        return now.replace(hour=t.hour, minute=0, second=0, microsecond=0)
    except ValueError:
        pass
    
    raise ValueError(f"Can't parse time: {s}")


def schedule(at_time: datetime, message: str):
    """Schedule a notification and track it."""
    delay = int((at_time - datetime.now()).total_seconds())
    if delay <= 0:
        print(f"⚠️  Time is in the past, sending now")
        send_notification(message)
        return
    
    # Start background process
    cmd = f'(sleep {delay} && osascript -e \'display notification "{message}" with title "⏰ Ping" sound name "Glass"\') &'
    subprocess.Popen(cmd, shell=True, start_new_session=True)
    
    # Track it
    scheduled = load_scheduled()
    scheduled.append({
        "time": at_time.isoformat(),
        "message": message,
        "created": datetime.now().isoformat()
    })
    save_scheduled(scheduled)
    
    print(f"✅ Scheduled for {at_time.strftime('%H:%M')} ({delay // 60}m from now)")


def list_pending():
    """List and clean up pending reminders."""
    scheduled = load_scheduled()
    now = datetime.now()
    
    # Filter to only future reminders
    pending = []
    for r in scheduled:
        try:
            t = datetime.fromisoformat(r["time"])
            if t > now:
                pending.append(r)
        except:
            pass
    
    # Save cleaned list
    save_scheduled(pending)
    
    if not pending:
        print("No pending reminders")
        return
    
    print("Pending reminders:")
    for r in sorted(pending, key=lambda x: x["time"]):
        t = datetime.fromisoformat(r["time"])
        delta = t - now
        mins = int(delta.total_seconds() // 60)
        print(f"  {t.strftime('%H:%M')} ({mins}m) - {r['message']}")


def clear_all():
    """Clear all tracked reminders (doesn't kill background processes)."""
    save_scheduled([])
    print("✅ Cleared all tracked reminders")
    print("   Note: Already-running background processes will still fire")


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)
    
    cmd = sys.argv[1].lower()
    
    if cmd == "now":
        if len(sys.argv) < 3:
            print("Usage: pingme now 'message'")
            sys.exit(1)
        send_notification(sys.argv[2])
        print("✅ Notification sent")
    
    elif cmd == "in":
        if len(sys.argv) < 4:
            print("Usage: pingme in 30m 'message'")
            sys.exit(1)
        secs = parse_duration(sys.argv[2])
        at_time = datetime.now() + timedelta(seconds=secs)
        schedule(at_time, sys.argv[3])
    
    elif cmd == "at":
        if len(sys.argv) < 4:
            print("Usage: pingme at 17:30 'message'")
            sys.exit(1)
        at_time = parse_time(sys.argv[2])
        schedule(at_time, sys.argv[3])
    
    elif cmd == "list":
        list_pending()
    
    elif cmd == "clear":
        clear_all()
    
    else:
        print(f"Unknown command: {cmd}")
        print(__doc__)
        sys.exit(1)


if __name__ == "__main__":
    main()
