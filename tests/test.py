import sys
sys.path.append("../")
from servicemanager.factory.systemd import SystemdServiceFactory
from servicemanager.servicemanager import ServiceManager

FILTER = ["mc-server", "ngrok"]

manager = ServiceManager(SystemdServiceFactory, filter=FILTER)


for id, services in manager.get_services().items():
    for service in services:
        for k, v in service.get_information().items():
            print(f"{service.type}@{service.id}/{id}: {k} -> {v}")
        print(f"STATE: {service.state}")