from enum import Enum


class CacheStrategy(Enum):
    """Cache strategy options."""
    MEMORY = "memory"
    DISK = "disk"
    REDIS = "redis"
    HYBRID = "hybrid"
