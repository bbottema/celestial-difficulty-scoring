import importlib
import pkgutil
from types import ModuleType

import app
from injector import Injector

component_registry = {}


def component(cls):
    component_registry[cls.__name__] = cls
    return cls


def _scan_and_import_packages(base_package: ModuleType):
    for finder, name, ispkg in pkgutil.walk_packages(base_package.__path__, base_package.__name__ + '.'):
        if ispkg:
            continue  # Skip packages, only import modules
        importlib.import_module(name)


def auto_wire():
    _scan_and_import_packages(app)
    injector = Injector()
    for name, cls in component_registry.items():
        injector.binder.bind(cls, to=cls)
