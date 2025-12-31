#!/usr/bin/env python3
"""
pingme - Schedule desktop notifications from the command line.

Usage:
    pingme now "message"           # Immediate notification
    pingme in 30m "message"        # In 30 minutes
    pingme at 17:30 "message"      # At specific time (tomorrow if past)
    pingme every 90m "message"     # Recurring every 90 minutes
    pingme list                    # Show pending reminders with IDs
    pingme cancel <id>             # Cancel by ID or message substring
    pingme clear                   # Clear all reminders

Reminders survive sleep and reboot (uses launchd).
"""

import json
import os
import plistlib
import re
import subprocess
import sys
import uuid
from datetime import datetime, timedelta
from pathlib import Path

PINGME_DIR = Path.home() / ".pingme"
JOBS_DIR = PINGME_DIR / "jobs"
SCHEDULED_FILE = PINGME_DIR / "scheduled.json"
LAUNCHD_LABEL_PREFIX = "com.pingme"


def ensure_dir():
    """Create necessary directories and files."""
    PINGME_DIR.mkdir(exist_ok=True)
    JOBS_DIR.mkdir(exist_ok=True)
    if not SCHEDULED_FILE.exists():
        SCHEDULED_FILE.write_text("[]")


def load_scheduled():
    """Load scheduled reminders from JSON."""
    ensure_dir()
    return json.loads(SCHEDULED_FILE.read_text())


def save_scheduled(data):
    """Save scheduled reminders to JSON."""
    ensure_dir()
    SCHEDULED_FILE.write_text(json.dumps(data, indent=2))


def escape_for_applescript(s: str) -> str:
    """Escape a string for safe use in AppleScript."""
    return s.replace("\\", "\\\\").replace('"', '\\"')


def send_notification(message: str, title: str = "⏰ Ping"):
    """Send a macOS notification via osascript."""
    escaped_msg = escape_for_applescript(message)
    escaped_title = escape_for_applescript(title)
    subprocess.run([
        "osascript", "-e",
        f'display notification "{escaped_msg}" with title "{escaped_title}" sound name "Glass"'
    ], capture_output=True)


def parse_duration(s: str) -> int:
    """Parse duration like '30m', '1h', '1h30m', '90m' to seconds."""
    total = 0
    matches = list(re.finditer(r'(\d+)\s*(h|m|s)', s.lower()))
    if matches:
        for match in matches:
            val, unit = int(match.group(1)), match.group(2)
            if unit == 'h':
                total += val * 3600
            elif unit == 'm':
                total += val * 60
            elif unit == 's':
                total += val
        return total
    return int(s)  # fallback: treat as seconds


def parse_time(s: str) -> datetime:
    """Parse time like '17:30' or '5:30pm'. Auto-advances to tomorrow if past."""
    now = datetime.now()
    result = None
    
    # Try 24h format (17:30)
    try:
        t = datetime.strptime(s, "%H:%M")
        result = now.replace(hour=t.hour, minute=t.minute, second=0, microsecond=0)
    except ValueError:
        pass
    
    # Try 12h format with colon (5:30pm)
    if result is None:
        try:
            t = datetime.strptime(s.lower(), "%I:%M%p")
            result = now.replace(hour=t.hour, minute=t.minute, second=0, microsecond=0)
        except ValueError:
            pass
    
    # Try 12h format without colon (5pm)
    if result is None:
        try:
            t = datetime.strptime(s.lower(), "%I%p")
            result = now.replace(hour=t.hour, minute=0, second=0, microsecond=0)
        except ValueError:
            pass
    
    if result is None:
        raise ValueError(f"Can't parse time: {s}")
    
    # Auto-advance to tomorrow if time has passed
    if result <= now:
        result += timedelta(days=1)
    
    return result


def get_script_path() -> str:
    """Get the absolute path to this script."""
    return str(Path(__file__).resolve())


def create_oneshot_plist(job_id: str, at_time: datetime) -> Path:
    """Create a launchd plist that fires pingme fire <job_id> at the specified time."""
    label = f"{LAUNCHD_LABEL_PREFIX}.{job_id}"
    plist_path = JOBS_DIR / f"{job_id}.plist"
    
    plist = {
        "Label": label,
        "ProgramArguments": [
            "/usr/bin/python3",
            get_script_path(),
            "fire",
            job_id,
        ],
        "StartCalendarInterval": {
            "Month": at_time.month,
            "Day": at_time.day,
            "Hour": at_time.hour,
            "Minute": at_time.minute,
        },
        "StandardOutPath": str(PINGME_DIR / "pingme.log"),
        "StandardErrorPath": str(PINGME_DIR / "pingme.log"),
    }
    
    with open(plist_path, "wb") as f:
        plistlib.dump(plist, f)
    
    return plist_path


def create_recurring_plist(job_id: str, interval_seconds: int) -> Path:
    """Create a launchd plist that fires every N seconds."""
    label = f"{LAUNCHD_LABEL_PREFIX}.{job_id}"
    plist_path = JOBS_DIR / f"{job_id}.plist"
    
    plist = {
        "Label": label,
        "ProgramArguments": [
            "/usr/bin/python3",
            get_script_path(),
            "fire",
            job_id,
        ],
        "StartInterval": interval_seconds,
        "RunAtLoad": True,  # Fire immediately when loaded
        "StandardOutPath": str(PINGME_DIR / "pingme.log"),
        "StandardErrorPath": str(PINGME_DIR / "pingme.log"),
    }
    
    with open(plist_path, "wb") as f:
        plistlib.dump(plist, f)
    
    return plist_path


def load_job(plist_path: Path) -> bool:
    """Load a launchd job. Returns True on success."""
    result = subprocess.run(
        ["launchctl", "bootstrap", f"gui/{os.getuid()}", str(plist_path)],
        capture_output=True
    )
    return result.returncode == 0


def unload_job(job_id: str) -> bool:
    """Unload a launchd job by ID. Returns True on success."""
    label = f"{LAUNCHD_LABEL_PREFIX}.{job_id}"
    result = subprocess.run(
        ["launchctl", "bootout", f"gui/{os.getuid()}/{label}"],
        capture_output=True
    )
    return result.returncode == 0


def is_job_loaded(job_id: str) -> bool:
    """Check if a launchd job is currently loaded."""
    label = f"{LAUNCHD_LABEL_PREFIX}.{job_id}"
    result = subprocess.run(
        ["launchctl", "print", f"gui/{os.getuid()}/{label}"],
        capture_output=True
    )
    return result.returncode == 0


def schedule(at_time: datetime, message: str):
    """Schedule a one-shot notification using launchd."""
    delay = int((at_time - datetime.now()).total_seconds())
    
    if delay <= 0:
        # Time is now or past, send immediately
        send_notification(message)
        print("✅ Notification sent (time was now/past)")
        return
    
    job_id = uuid.uuid4().hex[:8]
    
    # Create and load plist
    plist_path = create_oneshot_plist(job_id, at_time)
    if not load_job(plist_path):
        print("❌ Failed to schedule reminder")
        plist_path.unlink(missing_ok=True)
        return
    
    # Track in JSON
    scheduled = load_scheduled()
    scheduled.append({
        "id": job_id,
        "time": at_time.isoformat(),
        "message": message,
        "created": datetime.now().isoformat(),
        "recurring": False,
    })
    save_scheduled(scheduled)
    
    # Confirm
    is_tomorrow = at_time.date() > datetime.now().date()
    time_str = at_time.strftime("%H:%M")
    if is_tomorrow:
        time_str += " tomorrow"
    print(f"✅ [{job_id}] Scheduled for {time_str} ({delay // 60}m from now)")


def schedule_recurring(interval_seconds: int, message: str):
    """Schedule a recurring notification using launchd."""
    if interval_seconds < 60:
        print("❌ Minimum interval is 1 minute")
        return
    
    job_id = uuid.uuid4().hex[:8]
    
    # Create and load plist
    plist_path = create_recurring_plist(job_id, interval_seconds)
    if not load_job(plist_path):
        print("❌ Failed to schedule recurring reminder")
        plist_path.unlink(missing_ok=True)
        return
    
    # Track in JSON
    scheduled = load_scheduled()
    scheduled.append({
        "id": job_id,
        "time": datetime.now().isoformat(),  # First fire time
        "message": message,
        "created": datetime.now().isoformat(),
        "recurring": True,
        "interval": interval_seconds,
    })
    save_scheduled(scheduled)
    
    mins = interval_seconds // 60
    print(f"✅ [{job_id}] Recurring every {mins}m: \"{message}\"")


def fire(job_id: str):
    """Called by launchd to fire a notification. Handles cleanup for one-shots."""
    scheduled = load_scheduled()
    job = None
    for r in scheduled:
        if r.get("id") == job_id:
            job = r
            break
    
    if not job:
        # Job not found in JSON (maybe already cancelled), just exit
        return
    
    # Send the notification
    message = job.get("message", "Reminder")
    is_recurring = job.get("recurring", False)
    title = "🔁 Ping" if is_recurring else "⏰ Ping"
    send_notification(message, title)
    
    # If one-shot, clean up
    if not is_recurring:
        # Remove from JSON
        scheduled = [r for r in scheduled if r.get("id") != job_id]
        save_scheduled(scheduled)
        
        # Unload self (we're being run by launchd, so unload after we exit)
        # Use subprocess to unload in background after a short delay
        label = f"{LAUNCHD_LABEL_PREFIX}.{job_id}"
        plist_path = JOBS_DIR / f"{job_id}.plist"
        
        # Schedule cleanup in background (can't unload while running)
        cleanup_cmd = f'sleep 1 && launchctl bootout gui/{os.getuid()}/{label} 2>/dev/null; rm -f "{plist_path}"'
        subprocess.Popen(cleanup_cmd, shell=True, start_new_session=True)


def cancel_reminder(identifier: str):
    """Cancel reminder(s) by ID prefix or message substring."""
    scheduled = load_scheduled()
    to_cancel = []
    remaining = []
    
    for r in scheduled:
        job_id = r.get("id", "")
        message = r.get("message", "")
        
        # Match by ID prefix or message substring (case-insensitive)
        if job_id.startswith(identifier) or identifier.lower() in message.lower():
            to_cancel.append(r)
        else:
            remaining.append(r)
    
    if not to_cancel:
        print(f"❌ No reminder found matching: {identifier}")
        return
    
    for r in to_cancel:
        job_id = r.get("id")
        if job_id:
            unload_job(job_id)
            plist_path = JOBS_DIR / f"{job_id}.plist"
            plist_path.unlink(missing_ok=True)
        
        msg_preview = r.get("message", "")[:30]
        if r.get("recurring"):
            print(f"✅ Cancelled recurring [{job_id}]: {msg_preview}")
        else:
            print(f"✅ Cancelled [{job_id}]: {msg_preview}")
    
    save_scheduled(remaining)


def list_pending():
    """List pending reminders with IDs."""
    scheduled = load_scheduled()
    now = datetime.now()
    
    # Validate: check which jobs are actually still loaded
    valid = []
    for r in scheduled:
        job_id = r.get("id")
        if not job_id:
            continue
        
        # For recurring, keep if job is loaded
        # For one-shot, keep if time is in future OR job is loaded
        if r.get("recurring"):
            if is_job_loaded(job_id):
                valid.append(r)
        else:
            try:
                t = datetime.fromisoformat(r["time"])
                if t > now or is_job_loaded(job_id):
                    valid.append(r)
            except (ValueError, KeyError):
                pass
    
    save_scheduled(valid)
    
    if not valid:
        print("No pending reminders")
        return
    
    # Separate one-shot and recurring
    oneshot = sorted(
        [r for r in valid if not r.get("recurring")],
        key=lambda x: x.get("time", "")
    )
    recurring = [r for r in valid if r.get("recurring")]
    
    if oneshot:
        print("One-time reminders:")
        for r in oneshot:
            job_id = r.get("id", "???")
            t = datetime.fromisoformat(r["time"])
            delta = t - now
            mins = max(0, int(delta.total_seconds() // 60))
            is_tomorrow = t.date() > now.date()
            time_str = t.strftime("%H:%M") + (" tmrw" if is_tomorrow else "")
            print(f"  [{job_id}]  {time_str}  ({mins}m)  {r.get('message', '')}")
    
    if recurring:
        print("\nRecurring:")
        for r in recurring:
            job_id = r.get("id", "???")
            interval_mins = r.get("interval", 0) // 60
            print(f"  [{job_id}]  every {interval_mins}m  {r.get('message', '')}")
    
    print(f"\nCancel: pingme cancel <id>")


def clear_all():
    """Clear all reminders and unload their launchd jobs."""
    scheduled = load_scheduled()
    count = 0
    
    for r in scheduled:
        job_id = r.get("id")
        if job_id:
            unload_job(job_id)
            plist_path = JOBS_DIR / f"{job_id}.plist"
            plist_path.unlink(missing_ok=True)
            count += 1
    
    save_scheduled([])
    print(f"✅ Cleared {count} reminder(s)")


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
    
    elif cmd == "every":
        if len(sys.argv) < 4:
            print("Usage: pingme every 90m 'message'")
            sys.exit(1)
        secs = parse_duration(sys.argv[2])
        schedule_recurring(secs, sys.argv[3])
    
    elif cmd == "fire":
        # Internal: called by launchd
        if len(sys.argv) < 3:
            sys.exit(1)
        fire(sys.argv[2])
    
    elif cmd == "cancel":
        if len(sys.argv) < 3:
            print("Usage: pingme cancel <id-or-substring>")
            sys.exit(1)
        cancel_reminder(sys.argv[2])
    
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
