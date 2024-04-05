from servicemanager.exceptions.base_exceptions import ServiceManagerRuntimeError

class ServiceTypeAlreadyRegisteredError(ServiceManagerRuntimeError):
    """Said type was already registered for this id"""

class NoCompatibleFactoryFound(ServiceManagerRuntimeError):
    """Said type does not have any compatible factory"""