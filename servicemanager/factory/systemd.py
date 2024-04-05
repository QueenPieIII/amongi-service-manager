from collections import defaultdict
from typing import NamedTuple

from dasbus.connection import SystemMessageBus

from ..exceptions.factory_exceptions import ServiceTypeNotCompatible
from .base.abstract import BaseServiceFactory, BaseService
from .base.enums import ServiceState

SERVICE_STATUS_MAP = {
    "active": ServiceState.ACTIVE,
    "activating": ServiceState.ACTIVATING,
    "inactive": ServiceState.INACTIVE,
    "deactivating": ServiceState.DEACTIVATING,
    "failed": ServiceState.FAILED
}

def _get_service_type(object_path: str, bus):
    proxy = bus.get_proxy("org.freedesktop.systemd1", object_path)
    return serviceType(
        proxy.Get('org.freedesktop.systemd1.Unit', "Names")[0],
        proxy.Get('org.freedesktop.systemd1.Unit', "Description").get_string(),
        proxy.Get('org.freedesktop.systemd1.Unit', "LoadState").get_string(),
        proxy.Get('org.freedesktop.systemd1.Unit', "ActiveState").get_string(),
        proxy.Get('org.freedesktop.systemd1.Unit', "SubState").get_string(),
        proxy.Get('org.freedesktop.systemd1.Unit', "Following").get_string(),
        object_path,
        proxy.Get('org.freedesktop.systemd1.Unit', "Job")[0],
        "", # this is temporary (i need to find job types)
        proxy.Get('org.freedesktop.systemd1.Unit', "Job")[1]
    )

# resource https://www.freedesktop.org/software/systemd/man/latest/org.freedesktop.systemd1.html
class serviceType(NamedTuple):
    name: str
    description: str
    state: str
    active_state: str
    substate: str
    follow: str
    object_path: str
    job: int
    job_type: str
    job_path: str

class ServiceFile:

    def __init__(self, unit_name: str, state: str) -> None:
        self._state = state
        self._unit_name = unit_name
        self._extension = unit_name.split(".")[-1]
        self._name = unit_name.split("/")[-1]
        name_list = self._name.removesuffix(f".{self._extension}").split("@")
        if len(name_list) == 2:
            self._type = name_list[0]
            self._id = name_list[1]
        else:
            self._type = name_list[0]
            self._id = None
    
    @property
    def is_template(self):
        return self._id == ""
    
    @property
    def is_templated_service(self):
        return bool(self._id)
    
    @property
    def is_service(self):
        return self._id is None

    @property
    def name(self):
        return self._name
    
    @property
    def type(self):
        return self._type
    
    @property
    def id(self):
        return self._id
    
    @property
    def extension(self):
        return self._extension
    
    @property
    def state(self):
        return self._state

# Actual implementations

class SystemdService(BaseService):
    def __init__(self, type: str, id: str, proxy, bus) -> None:
        self._proxy = proxy
        self._bus = bus
        self._type = type
        self._id = id
        self._name = f"{type}@{id}.service"
        self._object_path = proxy.LoadUnit(self._name)

    @staticmethod
    def get_provider() -> str:
        return SystemdServiceFactory.get_factory_type()

    @property
    def type(self):
        return self._type

    @property
    def id(self):
        return self._id
    
    @property
    def state(self):
        return SERVICE_STATUS_MAP[self._info.active_state]
    
    # i used polkit to allow starting and stopping units
    def start(self):
        if self.state in ServiceState.STOPPED:
            self._proxy.StartUnit(self._name, 'replace')
            return True
        return False

    def stop(self):
        if self.state == ServiceState.ACTIVE:
            self._proxy.StopUnit(self._name, 'replace')
            return True
        return False
    
    def restart(self):
        if self.state == ServiceState.ACTIVE:
            self._proxy.RestartUnit(self._name, 'replace')
            return True
        return False
    
    def get_information(self) -> dict:
        info = self._info
        proxy = self._bus.get_proxy("org.freedesktop.systemd1", self._object_path)
        return {
            "Provider": self.get_provider(),
            "Name": info.name,
            "Description": info.description,
            "State": info.state,
            "Substate": info.substate,
            "ExecStartPre": proxy.Get('org.freedesktop.systemd1.Service', "ExecStartPre").print_(False),
            "ExecStart": proxy.Get('org.freedesktop.systemd1.Service', "ExecStart").print_(False),
            "ExecStartPost": proxy.Get('org.freedesktop.systemd1.Service', "ExecStartPost").print_(False),
            "ExecReload": proxy.Get('org.freedesktop.systemd1.Service', "ExecReload").print_(False),
            "ExecStop": proxy.Get('org.freedesktop.systemd1.Service', "ExecStop").print_(False),
            "MemoryCurrent": proxy.Get('org.freedesktop.systemd1.Service', "MemoryCurrent").print_(False),
        }

    
    @property
    def _info(self):
        return _get_service_type(self._object_path, self._bus)

class SystemdServiceFactory(BaseServiceFactory):

    def __init__(self, service_filter: list[str]) -> None:
        self._bus = SystemMessageBus()
        self._filter = service_filter
        self._proxy = self._bus.get_proxy(
            "org.freedesktop.systemd1",
            "/org/freedesktop/systemd1"
        )

        self._compatible_services = set()
        self._existing_services: dict[str, set] = defaultdict(set)

        self.refresh()

    @staticmethod
    def get_description() -> str:
        return "Interface to use systemd services as services"

    @staticmethod
    def get_factory_type() -> str:
        return "systemd"

    def create_service(self, service_type: str, service_id: str) -> BaseService:
        if not self.has_support(service_type):
            raise ServiceTypeNotCompatible(f"SystemdServiceFactory does not support services of type \"{service_type}\"")
        return SystemdService(service_type, service_id, self._proxy, self._bus)

    def has_support(self, service_type: str) -> bool:
        return service_type in self._compatible_services

    def refresh(self):
        for elem in self._proxy.ListUnitFiles():
            file = ServiceFile(elem[0], elem[1])
            if file.extension != "service" or file.type not in self._filter:
                continue
            if file.is_template:
                self._compatible_services.add(file.type)
            if file.is_templated_service:
                self._existing_services[file.id].add(file.type)

    def get_initial_services(self) -> list[BaseService]:
        service_list = []
        for id, types in self._existing_services.items():
            for type in types:
                service_list.append(SystemdService(type, id, self._proxy, self._bus))
        return service_list

    def get_services(self) -> list[BaseService]:
        pass