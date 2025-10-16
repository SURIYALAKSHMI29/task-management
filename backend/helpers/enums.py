from enum import Enum


class TaskPriority(Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class TaskStatus(Enum):
    PENDING = "pending"
    COMPLETED = "completed"
    CANCELED = "cancelled"


class RecurrenceType(Enum):
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"
