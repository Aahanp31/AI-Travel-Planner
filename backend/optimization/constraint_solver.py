"""
Constraint Satisfaction solver for itinerary planning.

Implements constraint propagation and backtracking to ensure itineraries
satisfy all hard and soft constraints (time windows, opening hours,
travel time budgets, activity duration limits).

Used alongside TSP optimization to produce feasible, optimal itineraries.
"""

from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass, field
import random


@dataclass
class ActivityConstraint:
    name: str
    duration_min: int
    earliest_start: int = 0       # minutes from 8:00 AM
    latest_end: int = 840         # minutes from 8:00 AM (10:00 PM)
    category: str = "attraction"  # attraction, food, transport, rest
    priority: float = 1.0
    requires: List[str] = field(default_factory=list)
    conflicts_with: List[str] = field(default_factory=list)


@dataclass
class DaySchedule:
    activities: List[Tuple[int, int, ActivityConstraint]]  # (start_min, end_min, activity)
    total_duration_min: int
    idle_time_min: int
    constraint_violations: int
    feasible: bool


class ConstraintSolver:
    """
    Constraint satisfaction + backtracking solver for daily schedules.

    Ensures all activities fit within time windows while respecting:
    - Opening hours / time windows
    - Activity duration constraints
    - Travel time between locations
    - Mandatory rest periods
    - Activity dependency ordering
    """

    DAY_START = 0       # 8:00 AM in minutes offset
    DAY_END = 840       # 10:00 PM
    MIN_REST = 15       # Minimum rest between activities (minutes)
    LUNCH_START = 240   # 12:00 PM
    LUNCH_END = 330     # 1:30 PM
    LUNCH_DURATION = 45

    def solve_day(
        self,
        activities: List[ActivityConstraint],
        travel_times: Optional[Dict[str, Dict[str, int]]] = None,
        enforce_lunch: bool = True
    ) -> DaySchedule:
        """
        Schedule activities for a single day satisfying all constraints.
        Uses constraint propagation + backtracking search.
        """
        if not activities:
            return DaySchedule([], 0, self.DAY_END, 0, True)

        # Sort by priority (high first) then by earliest start
        activities = sorted(activities, key=lambda a: (-a.priority, a.earliest_start))

        # Add lunch break if needed
        if enforce_lunch:
            lunch = ActivityConstraint(
                name="Lunch Break",
                duration_min=self.LUNCH_DURATION,
                earliest_start=self.LUNCH_START,
                latest_end=self.LUNCH_END + self.LUNCH_DURATION,
                category="food",
                priority=2.0
            )
            activities.insert(0, lunch)
            activities.sort(key=lambda a: (-a.priority, a.earliest_start))

        schedule = []
        violations = 0

        result = self._backtrack(activities, [], 0, travel_times or {})

        if result is not None:
            schedule = result
        else:
            # Fallback: greedy scheduling with violation tracking
            schedule, violations = self._greedy_schedule(activities, travel_times or {})

        total_duration = sum(end - start for start, end, _ in schedule)
        idle_time = self.DAY_END - total_duration if schedule else self.DAY_END

        return DaySchedule(
            activities=schedule,
            total_duration_min=total_duration,
            idle_time_min=max(0, idle_time),
            constraint_violations=violations,
            feasible=violations == 0
        )

    def _backtrack(
        self,
        remaining: List[ActivityConstraint],
        scheduled: List[Tuple[int, int, ActivityConstraint]],
        current_time: int,
        travel_times: Dict[str, Dict[str, int]],
        depth: int = 0
    ) -> Optional[List[Tuple[int, int, ActivityConstraint]]]:
        """Recursive backtracking with constraint propagation."""
        if not remaining:
            return scheduled[:]

        if depth > 50:  # Prevent excessive recursion
            return None

        for i, activity in enumerate(remaining):
            # Calculate earliest feasible start
            start = max(current_time + self.MIN_REST, activity.earliest_start)

            # Add travel time from previous activity
            if scheduled and travel_times:
                prev_name = scheduled[-1][2].name
                travel = travel_times.get(prev_name, {}).get(activity.name, 0)
                start = max(start, current_time + travel)

            end = start + activity.duration_min

            # Check time window constraint
            if end > activity.latest_end or end > self.DAY_END + self.DAY_START:
                continue

            # Check dependency constraints
            if activity.requires:
                scheduled_names = {s[2].name for s in scheduled}
                if not all(req in scheduled_names for req in activity.requires):
                    continue

            # Check conflict constraints
            if activity.conflicts_with:
                scheduled_names = {s[2].name for s in scheduled}
                if any(c in scheduled_names for c in activity.conflicts_with):
                    continue

            # Try this assignment
            new_remaining = remaining[:i] + remaining[i + 1:]
            new_scheduled = scheduled + [(start, end, activity)]

            result = self._backtrack(
                new_remaining, new_scheduled, end, travel_times, depth + 1
            )
            if result is not None:
                return result

        return None

    def _greedy_schedule(
        self,
        activities: List[ActivityConstraint],
        travel_times: Dict[str, Dict[str, int]]
    ) -> Tuple[List[Tuple[int, int, ActivityConstraint]], int]:
        """Greedy fallback scheduler that minimizes constraint violations."""
        schedule = []
        violations = 0
        current_time = self.DAY_START

        for activity in activities:
            start = max(current_time + self.MIN_REST, activity.earliest_start)

            if schedule and travel_times:
                prev_name = schedule[-1][2].name
                travel = travel_times.get(prev_name, {}).get(activity.name, 0)
                start = max(start, current_time + travel)

            end = start + activity.duration_min

            if end > activity.latest_end:
                violations += 1
            if end > self.DAY_END:
                violations += 1

            schedule.append((start, end, activity))
            current_time = end

        return schedule, violations

    def validate_itinerary(self, itinerary: dict) -> Dict[str, any]:
        """
        Validate an entire itinerary for constraint satisfaction.
        Returns metrics on feasibility and constraint violations.
        """
        total_violations = 0
        day_results = {}

        for day_key, day_data in itinerary.items():
            if not isinstance(day_data, dict):
                continue

            activities = []
            time_offset = 0

            for period, (start_offset, end_offset) in [
                ('morning', (0, 240)),
                ('afternoon', (240, 480)),
                ('evening', (480, 840))
            ]:
                items = day_data.get(period, [])
                if not isinstance(items, list):
                    continue

                for item in items:
                    name = item if isinstance(item, str) else str(item)
                    activities.append(ActivityConstraint(
                        name=name,
                        duration_min=60,
                        earliest_start=start_offset,
                        latest_end=end_offset,
                        category="attraction"
                    ))

            result = self.solve_day(activities, enforce_lunch=True)
            total_violations += result.constraint_violations
            day_results[day_key] = {
                'feasible': result.feasible,
                'violations': result.constraint_violations,
                'idle_time_min': result.idle_time_min,
                'total_duration_min': result.total_duration_min
            }

        return {
            'total_violations': total_violations,
            'all_feasible': total_violations == 0,
            'days': day_results
        }
