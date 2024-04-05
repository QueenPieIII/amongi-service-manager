from .base_exceptions import *

class ServiceTypeNotCompatible(ServiceManagerRuntimeError):
    """The service type provided is not compatible with the given factory"""
    pass