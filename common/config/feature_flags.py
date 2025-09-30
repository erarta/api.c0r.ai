"""
Feature flags used across services.
"""

import os


class _FeatureFlags:
    @property
    def BYPASS_SUBSCRIPTION(self) -> bool:
        return os.getenv("BYPASS_SUBSCRIPTION", "false").lower() == "true"


feature_flags = _FeatureFlags()


