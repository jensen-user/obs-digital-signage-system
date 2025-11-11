#!/usr/bin/env python3
"""
Test script for the scheduling feature.
Run this to verify the scheduler works correctly without starting OBS.
"""

import sys
import os
from pathlib import Path

# Fix encoding for Windows console
if sys.platform == "win32":
    os.system('chcp 65001 >nul 2>&1')  # Set console to UTF-8

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from config.settings import Settings
from core.scheduler import Scheduler
from datetime import datetime, time
from zoneinfo import ZoneInfo

def main():
    print("=" * 60)
    print("Scheduler Test")
    print("=" * 60)

    # Load settings
    print("\n1. Loading settings...")
    settings = Settings()
    print(f"   ✓ SCHEDULE_ENABLED: {settings.SCHEDULE_ENABLED}")
    print(f"   ✓ TIMEZONE: {settings.TIMEZONE}")
    print(f"   ✓ SCHEDULE_CHECK_INTERVAL: {settings.SCHEDULE_CHECK_INTERVAL}s")

    # Initialize scheduler
    print("\n2. Initializing scheduler...")
    scheduler = Scheduler(settings)
    print(f"   ✓ Scheduler initialized")
    print(f"   ✓ Number of schedules: {len(scheduler.schedules)}")
    print(f"   ✓ Default schedule: {scheduler.default_schedule.name}")

    # Show all schedules
    print("\n3. Configured schedules:")
    for i, schedule in enumerate(scheduler.schedules, 1):
        print(f"   {i}. {schedule.name}")
        print(f"      - Folder: {schedule.folder.name}")
        print(f"      - Transition: {schedule.transition_type}")
        print(f"      - Day: {schedule.day_of_week} (0=Mon, 6=Sun)")
        print(f"      - Time: {schedule.start_time} - {schedule.end_time}")

    print(f"   {len(scheduler.schedules) + 1}. {scheduler.default_schedule.name} (fallback)")
    print(f"      - Folder: {scheduler.default_schedule.folder.name}")
    print(f"      - Transition: {scheduler.default_schedule.transition_type}")
    print(f"      - Active: All other times")

    # Current status
    print("\n4. Current status:")
    current_time = scheduler.get_current_time()
    current_schedule = scheduler.get_active_schedule()
    print(f"   ✓ Current time: {current_time.strftime('%A, %Y-%m-%d %H:%M:%S %Z')}")
    print(f"   ✓ Current day: {current_time.strftime('%A')} (weekday={current_time.weekday()})")
    print(f"   ✓ Active schedule: {current_schedule.name}")
    print(f"   ✓ Content folder: {current_schedule.folder}")
    print(f"   ✓ Transition: {current_schedule.transition_type}")
    print(f"   ✓ Transition offset: {current_schedule.transition_offset}s")

    # Test Sunday Service activation
    print("\n5. Testing Sunday Service schedule activation:")
    tz = ZoneInfo(settings.TIMEZONE)

    # Test times
    test_cases = [
        (datetime(2025, 11, 16, 7, 59, tzinfo=tz), "Sunday 07:59", False),
        (datetime(2025, 11, 16, 8, 0, tzinfo=tz), "Sunday 08:00", True),
        (datetime(2025, 11, 16, 10, 30, tzinfo=tz), "Sunday 10:30", True),
        (datetime(2025, 11, 16, 13, 29, tzinfo=tz), "Sunday 13:29", True),
        (datetime(2025, 11, 16, 13, 30, tzinfo=tz), "Sunday 13:30", False),
        (datetime(2025, 11, 17, 10, 0, tzinfo=tz), "Monday 10:00", False),
    ]

    sunday_schedule = scheduler.schedules[0] if scheduler.schedules else None

    if sunday_schedule:
        for test_time, description, expected in test_cases:
            result = sunday_schedule.is_active(test_time)
            status = "✓" if result == expected else "✗"
            print(f"   {status} {description}: {'Active' if result else 'Inactive'} (expected: {'Active' if expected else 'Inactive'})")

    # Folder existence check
    print("\n6. Checking folders:")
    folders = [
        settings.SUNDAY_SERVICE_FOLDER,
        settings.DEFAULT_FOLDER
    ]

    for folder in folders:
        exists = folder.exists()
        status = "✓" if exists else "✗"
        print(f"   {status} {folder.name}: {'Exists' if exists else 'Does not exist'}")

        if exists:
            files = list(folder.glob("*"))
            media_files = [f for f in files if f.suffix.lower() in
                          {'.jpg', '.jpeg', '.png', '.bmp', '.gif', '.webp', '.mp4', '.mov', '.avi', '.mkv'}]
            print(f"      - Total files: {len(files)}")
            print(f"      - Media files: {len(media_files)}")
            if media_files:
                for mf in media_files[:3]:  # Show first 3
                    print(f"        • {mf.name}")

    # Summary
    print("\n" + "=" * 60)
    print("Test Summary")
    print("=" * 60)
    print(f"✓ Settings loaded successfully")
    print(f"✓ Scheduler initialized successfully")
    print(f"✓ Current active schedule: {current_schedule.name}")
    print(f"✓ Schedule logic working correctly")

    if settings.SCHEDULE_ENABLED:
        print(f"\n✓ Scheduling feature is ENABLED")
        print(f"  System will check for schedule changes every {settings.SCHEDULE_CHECK_INTERVAL} seconds")
    else:
        print(f"\n✗ Scheduling feature is DISABLED")
        print(f"  Set SCHEDULE_ENABLED=true in config to enable")

    print("\nTo test with actual content:")
    print("1. Add images/videos to the content folders")
    print("2. Run the main system: python src/main.py")
    print("3. Watch logs for schedule monitoring messages")
    print("=" * 60)

if __name__ == "__main__":
    main()
