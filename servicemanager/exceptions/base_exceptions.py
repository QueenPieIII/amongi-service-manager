class ServiceManagerException(Exception):
    """Base class for ServiceManager exceptions"""
    pass

class ServiceManagerRuntimeError(ServiceManagerException, RuntimeError):
    """Base class for ServiceManager runtime errors"""