from collections import defaultdict

from servicemanager.factory.base.abstract import BaseServiceFactory, BaseService
from servicemanager.exceptions.manager_exceptions import *

class ServiceManager:
    def __init__(self, *args, **kwargs) -> None:
        self._factories: set[BaseServiceFactory] = set()
        self._filter = kwargs["filter"]
        for factory_class in args:
            self.add_factory(factory_class)

        self._registered_service_types: dict[str, set[str]] = defaultdict(set)
        self._registered_services: dict[str, list[BaseService]] = defaultdict(list)

        self.register_existing_services()

    def add_factory(self, factory: BaseServiceFactory):
        self._factories.add(factory(self._filter))

    def refresh(self):
        for factory in self._factories:
            factory.refresh()
    
    def register_service(self, type: str, id: str) -> BaseService:
        if type in self._registered_service_types[id]:
            raise ServiceTypeAlreadyRegisteredError(f"Service type \"{type}\" has already been registered to id \"{id}\"")
        if (factory := self._get_factory_for_type(type)) is None:
            raise NoCompatibleFactoryFound(f"Service type \"{type}\" does not have any compatible registered factory")
        service = factory.create_service(type, id)
        self._registered_service_types[id].add(type)
        self._registered_services[id].append(service)
        return service

    def get_services(self):
        return self._registered_services
    
    def register_existing_services(self):
        for factory in self._factories:
            for service in factory.get_initial_services():
                if service.type in self._registered_service_types[service.id]:
                    raise ServiceTypeAlreadyRegisteredError(f"Service type \"{type}\" has already been registered to id \"{id}\"")
                self._registered_service_types[service.id].add(service.type)
                self._registered_services[service.id].append(service)


    def _get_factory_for_type(self, type: str) -> BaseServiceFactory:
        for factory in self._factories:
            if factory.has_support(type):
                return factory
        return None