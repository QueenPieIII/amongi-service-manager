from abc import ABC, abstractmethod
from .enums import ServiceState

class BaseService(ABC):

    @staticmethod
    @abstractmethod
    def get_provider() -> str:
        """Returns the provider (factory type) of the service"""
        pass

    @property
    @abstractmethod
    def type(self) -> str:
        """Returns the service type"""
        pass

    @property
    @abstractmethod
    def id(self) -> str:
        """Returns the asociated ID of the service"""
        pass
    
    @property
    @abstractmethod
    def state(self) -> ServiceState:
        """Returns the current state of the service"""
        pass

    @abstractmethod
    def start(self) -> bool:
        """Starts the service. Returns true if it was succesful"""
        pass
    
    @abstractmethod
    def stop(self) -> bool:
        """Stops the service. Returns true if it was succesful"""
        pass
    
    @abstractmethod
    def restart(self) -> bool:
        """Restarts the service. Returns true if it was succesful"""
        pass

    @abstractmethod
    def get_information(self) -> dict:
        """Returns any kind of information about the service"""
        pass

class BaseServiceFactory(ABC):

    @staticmethod
    @abstractmethod
    def get_description() -> str:
        """Returns the description of the service factory"""
        pass

    @staticmethod
    @abstractmethod
    def get_factory_type() -> str:
        """Returns the identifier (type) of the factory"""
        pass

    @abstractmethod
    def create_service(self, service_type: str, service_id: str) -> BaseService:
        """Create's a service using the type and id given"""
        pass

    @abstractmethod
    def has_support(self, service_type: str) -> bool:
        """Checks whether the factory has support for the given service type"""
        pass

    @abstractmethod
    def refresh(self):
        """Refreshes the list of existing services and compatible services"""
        pass

    @abstractmethod
    def get_initial_services(self) -> list[BaseService]:
        """Returns a list of existing initial service."""
        pass

    @abstractmethod
    def get_services(self) -> list[BaseService]:
        """Returns a list of services"""
        pass