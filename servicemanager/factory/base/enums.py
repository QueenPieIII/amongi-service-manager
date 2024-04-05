from enum import Enum, auto, Flag

class ServiceState(Flag):
    ACTIVE = auto()
    ACTIVATING = auto()
    INACTIVE = auto()
    DEACTIVATING = auto()
    FAILED = auto()
    MISSING = auto()
    
    STOPPED = INACTIVE | FAILED