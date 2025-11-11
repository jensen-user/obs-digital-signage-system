"""
Time-based content scheduling system.
Manages switching between different content folders and transitions based on time/day.
"""

import logging
from datetime import datetime, time
from pathlib import Path
from typing import List, Optional
from zoneinfo import ZoneInfo


class Schedule:
    """Represents a content schedule with time/day restrictions."""

    def __init__(
        self,
        name: str,
        folder: Path,
        transition_type: str,
        transition_offset: float,
        day_of_week: Optional[int] = None,
        start_time: Optional[time] = None,
        end_time: Optional[time] = None
    ):
        """
        Initialize a schedule.

        Args:
            name: Human-readable schedule name (e.g., "Sunday Service")
            folder: Path to content folder for this schedule
            transition_type: OBS transition name (e.g., "Stinger Transition", "Fade")
            transition_offset: Transition timing offset in seconds
            day_of_week: Optional day restriction (0=Monday, 6=Sunday)
            start_time: Optional start time (e.g., time(8, 0) for 08:00)
            end_time: Optional end time (e.g., time(13, 30) for 13:30)
        """
        self.name = name
        self.folder = folder
        self.transition_type = transition_type
        self.transition_offset = transition_offset
        self.day_of_week = day_of_week
        self.start_time = start_time
        self.end_time = end_time

        self.logger = logging.getLogger(__name__)

    def is_active(self, current_time: datetime) -> bool:
        """
        Check if this schedule is currently active.

        Args:
            current_time: Current datetime to check against

        Returns:
            True if schedule is active, False otherwise
        """
        # Check day of week if restricted
        if self.day_of_week is not None:
            if current_time.weekday() != self.day_of_week:
                return False

        # If no time restrictions, schedule is active (based on day only)
        if self.start_time is None and self.end_time is None:
            return True

        # Check time range if restricted
        if self.start_time is not None and self.end_time is not None:
            current_time_only = current_time.time()

            # Handle normal time range (e.g., 08:00-13:30)
            if self.start_time <= self.end_time:
                return self.start_time <= current_time_only < self.end_time

            # Handle midnight-crossing range (e.g., 23:00-02:00)
            else:
                return current_time_only >= self.start_time or current_time_only < self.end_time

        return True

    def __repr__(self) -> str:
        """String representation for debugging."""
        return (f"Schedule({self.name}, folder={self.folder.name}, "
                f"transition={self.transition_type}, day={self.day_of_week}, "
                f"time={self.start_time}-{self.end_time})")


class Scheduler:
    """Manages multiple schedules and determines which is currently active."""

    def __init__(self, settings):
        """
        Initialize scheduler with settings.

        Args:
            settings: Settings object containing schedule configuration
        """
        self.settings = settings
        self.logger = logging.getLogger(__name__)

        # Timezone for time calculations
        try:
            self.timezone = ZoneInfo(settings.TIMEZONE)
        except Exception as e:
            self.logger.warning(f"Invalid timezone '{settings.TIMEZONE}': {e}")
            self.logger.warning("Falling back to system timezone")
            self.timezone = None

        # Initialize schedules
        self.schedules: List[Schedule] = []
        self.default_schedule: Optional[Schedule] = None
        self.current_schedule: Optional[Schedule] = None

        # Load schedules from settings
        self._load_schedules()

    def _load_schedules(self) -> None:
        """Load all schedules from settings."""
        try:
            self.logger.info("Initializing scheduler...")

            # Load Sunday Service schedule (if configured)
            if hasattr(self.settings, 'SUNDAY_SERVICE_FOLDER'):
                sunday_schedule = self._create_sunday_service_schedule()
                if sunday_schedule:
                    self.schedules.append(sunday_schedule)
                    self.logger.info(f"Loaded schedule: {sunday_schedule}")

            # Load default schedule (fallback)
            default_schedule = self._create_default_schedule()
            if default_schedule:
                self.default_schedule = default_schedule
                self.logger.info(f"Loaded default schedule: {default_schedule}")
            else:
                raise Exception("Failed to create default schedule")

            # Set initial active schedule
            self.current_schedule = self.get_active_schedule()
            self.logger.info(f"Initial active schedule: {self.current_schedule.name}")

        except Exception as e:
            self.logger.error(f"Failed to load schedules: {e}")
            raise

    def _create_sunday_service_schedule(self) -> Optional[Schedule]:
        """Create Sunday Service schedule from settings."""
        try:
            # Parse start and end times
            start_time_str = self.settings.SUNDAY_SERVICE_START_TIME
            end_time_str = self.settings.SUNDAY_SERVICE_END_TIME

            start_time = self._parse_time(start_time_str)
            end_time = self._parse_time(end_time_str)

            if start_time is None or end_time is None:
                self.logger.warning("Invalid Sunday Service time configuration")
                return None

            # Create schedule
            schedule = Schedule(
                name="Sunday Service",
                folder=self.settings.SUNDAY_SERVICE_FOLDER,
                transition_type=self.settings.SUNDAY_SERVICE_TRANSITION,
                transition_offset=self.settings.SUNDAY_SERVICE_TRANSITION_OFFSET,
                day_of_week=self.settings.SUNDAY_SERVICE_DAY,
                start_time=start_time,
                end_time=end_time
            )

            return schedule

        except Exception as e:
            self.logger.error(f"Failed to create Sunday Service schedule: {e}")
            return None

    def _create_default_schedule(self) -> Optional[Schedule]:
        """Create default schedule from settings."""
        try:
            schedule = Schedule(
                name="Default",
                folder=self.settings.DEFAULT_FOLDER,
                transition_type=self.settings.DEFAULT_TRANSITION,
                transition_offset=self.settings.DEFAULT_TRANSITION_OFFSET,
                day_of_week=None,  # Active all days
                start_time=None,   # Active all times
                end_time=None
            )

            return schedule

        except Exception as e:
            self.logger.error(f"Failed to create default schedule: {e}")
            return None

    def _parse_time(self, time_str: str) -> Optional[time]:
        """
        Parse time string in HH:MM format.

        Args:
            time_str: Time string like "08:00" or "13:30"

        Returns:
            time object or None if parsing fails
        """
        try:
            parts = time_str.split(':')
            if len(parts) != 2:
                return None

            hour = int(parts[0])
            minute = int(parts[1])

            if 0 <= hour <= 23 and 0 <= minute <= 59:
                return time(hour, minute)
            else:
                return None

        except Exception as e:
            self.logger.error(f"Failed to parse time '{time_str}': {e}")
            return None

    def get_current_time(self) -> datetime:
        """
        Get current time in configured timezone.

        Returns:
            Current datetime in configured timezone
        """
        if self.timezone:
            return datetime.now(self.timezone)
        else:
            return datetime.now()

    def get_active_schedule(self) -> Schedule:
        """
        Get the currently active schedule based on current time.

        Returns:
            Active schedule (specific schedule or default fallback)
        """
        current_time = self.get_current_time()

        # Check each specific schedule in priority order
        for schedule in self.schedules:
            if schedule.is_active(current_time):
                return schedule

        # Fall back to default schedule
        return self.default_schedule

    def check_schedule_change(self) -> bool:
        """
        Check if the active schedule has changed since last check.

        Returns:
            True if schedule changed, False otherwise
        """
        new_schedule = self.get_active_schedule()

        if new_schedule != self.current_schedule:
            old_name = self.current_schedule.name if self.current_schedule else "None"
            self.logger.info(f"Schedule changed: {old_name} → {new_schedule.name}")
            self.current_schedule = new_schedule
            return True

        return False

    def get_current_content_folder(self) -> Path:
        """Get content folder for current schedule."""
        schedule = self.get_active_schedule()
        return schedule.folder

    def get_current_transition_type(self) -> str:
        """Get transition type for current schedule."""
        schedule = self.get_active_schedule()
        return schedule.transition_type

    def get_current_transition_offset(self) -> float:
        """Get transition offset for current schedule."""
        schedule = self.get_active_schedule()
        return schedule.transition_offset
