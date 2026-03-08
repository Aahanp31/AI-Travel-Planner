"""
Multi-Armed Bandit for exploration vs exploitation in recommendations.

Implements Thompson Sampling bandit algorithm to balance:
- Exploration: suggesting new/unknown attractions to gather data
- Exploitation: recommending proven favorites (user preferences)

Ensures diverse, personalized itineraries that improve over time.
"""

import random
import math
from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass, field
from collections import defaultdict


@dataclass
class ArmStats:
    """Statistics for a single bandit arm (attraction/activity)."""
    arm_id: str
    successes: int = 0    # Positive feedback (saved, liked, high rating)
    failures: int = 0     # Negative feedback (skipped, low rating)
    total_reward: float = 0.0
    category: str = ""

    @property
    def pulls(self) -> int:
        return self.successes + self.failures

    @property
    def mean_reward(self) -> float:
        return self.total_reward / self.pulls if self.pulls > 0 else 0.0


class ExplorationBandit:
    """
    Thompson Sampling bandit for balancing exploration vs exploitation
    in travel recommendations.

    - Exploration: Discover new attractions users might enjoy
    - Exploitation: Recommend known-good attractions based on preferences

    Uses Beta distribution for Thompson Sampling, providing:
    - Natural exploration that decreases as confidence grows
    - Automatic adaptation to user feedback
    - Contextual awareness (destination, category, time of day)
    """

    def __init__(self, exploration_bonus: float = 0.1):
        self.arms: Dict[str, ArmStats] = {}
        self.exploration_bonus = exploration_bonus
        self.context_arms: Dict[str, Dict[str, ArmStats]] = defaultdict(dict)

    def add_arm(self, arm_id: str, category: str = ""):
        """Register a new attraction/activity as a bandit arm."""
        if arm_id not in self.arms:
            self.arms[arm_id] = ArmStats(arm_id=arm_id, category=category)

    def record_feedback(self, arm_id: str, reward: float, context: str = ""):
        """
        Record user feedback for an attraction.
        reward: 0.0-1.0 (0=negative, 1=positive)
        """
        if arm_id not in self.arms:
            self.add_arm(arm_id)

        arm = self.arms[arm_id]
        arm.total_reward += reward

        if reward >= 0.5:
            arm.successes += 1
        else:
            arm.failures += 1

        # Context-specific tracking
        if context:
            if arm_id not in self.context_arms[context]:
                self.context_arms[context][arm_id] = ArmStats(
                    arm_id=arm_id, category=arm.category
                )
            ctx_arm = self.context_arms[context][arm_id]
            ctx_arm.total_reward += reward
            if reward >= 0.5:
                ctx_arm.successes += 1
            else:
                ctx_arm.failures += 1

    def select_arms(
        self,
        n: int = 5,
        context: str = "",
        category_filter: Optional[str] = None,
        exclude: Optional[set] = None
    ) -> List[Tuple[str, float, str]]:
        """
        Select n arms using Thompson Sampling.

        Returns list of (arm_id, sampled_value, selection_reason) tuples.
        Selection reason is either "exploration" or "exploitation".
        """
        exclude = exclude or set()
        candidates = []

        arms_to_check = self.arms
        if context and context in self.context_arms:
            # Merge context-specific stats
            arms_to_check = dict(self.arms)
            for arm_id, ctx_stats in self.context_arms[context].items():
                if arm_id in arms_to_check:
                    # Weighted merge
                    merged = ArmStats(
                        arm_id=arm_id,
                        successes=arms_to_check[arm_id].successes + ctx_stats.successes,
                        failures=arms_to_check[arm_id].failures + ctx_stats.failures,
                        total_reward=arms_to_check[arm_id].total_reward + ctx_stats.total_reward,
                        category=arms_to_check[arm_id].category
                    )
                    arms_to_check[arm_id] = merged

        for arm_id, stats in arms_to_check.items():
            if arm_id in exclude:
                continue
            if category_filter and stats.category != category_filter:
                continue

            # Thompson Sampling: draw from Beta distribution
            alpha = stats.successes + 1  # +1 prior
            beta = stats.failures + 1
            sampled = random.betavariate(alpha, beta)

            # Add exploration bonus for under-explored arms
            if stats.pulls < 5:
                sampled += self.exploration_bonus * (5 - stats.pulls) / 5

            is_exploration = stats.pulls < 3 or sampled > stats.mean_reward + 0.1
            reason = "exploration" if is_exploration else "exploitation"

            candidates.append((arm_id, sampled, reason))

        # Sort by sampled value (descending)
        candidates.sort(key=lambda x: -x[1])
        return candidates[:n]

    def get_exploration_rate(self) -> float:
        """Calculate current exploration vs exploitation ratio."""
        if not self.arms:
            return 1.0

        under_explored = sum(1 for a in self.arms.values() if a.pulls < 5)
        return under_explored / len(self.arms)

    def get_arm_stats(self, arm_id: str) -> Optional[Dict]:
        """Get detailed statistics for a specific arm."""
        if arm_id not in self.arms:
            return None

        stats = self.arms[arm_id]
        return {
            'arm_id': arm_id,
            'category': stats.category,
            'pulls': stats.pulls,
            'successes': stats.successes,
            'failures': stats.failures,
            'mean_reward': round(stats.mean_reward, 4),
            'confidence': round(1 - 1 / (stats.pulls + 1), 4),
            'exploration_potential': round(self.exploration_bonus * max(0, 5 - stats.pulls) / 5, 4)
        }

    def get_category_summary(self) -> Dict[str, Dict]:
        """Get aggregated statistics by category."""
        categories = defaultdict(lambda: {'pulls': 0, 'successes': 0, 'total_reward': 0.0, 'count': 0})

        for arm in self.arms.values():
            cat = arm.category or 'uncategorized'
            categories[cat]['pulls'] += arm.pulls
            categories[cat]['successes'] += arm.successes
            categories[cat]['total_reward'] += arm.total_reward
            categories[cat]['count'] += 1

        return {
            cat: {
                **stats,
                'mean_reward': round(stats['total_reward'] / stats['pulls'], 4) if stats['pulls'] > 0 else 0,
                'success_rate': round(stats['successes'] / stats['pulls'], 4) if stats['pulls'] > 0 else 0
            }
            for cat, stats in categories.items()
        }
