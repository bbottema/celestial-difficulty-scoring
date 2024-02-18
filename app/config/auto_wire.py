import importlib
import logging
import os
import pkgutil
import sys
from pathlib import Path
from typing import Type, Any, Dict

from injector import Injector

component_registry: Dict[str, Type[Any]] = {}

logger = logging.getLogger(__name__)

print("THIS SHOULD ONLY BE CALLED ONCE")


def component(cls: Type[Any]) -> Type[Any]:
    logger.debug(f"Registering component {cls.__name__}")
    component_registry[cls.__name__] = cls
    return cls


def _is_package(path):
    """Check if a given path is a Python package by looking for .py files in it and its subdirectories."""
    for root, dirs, files in os.walk(path):
        if any(file.endswith('.py') and file != '__init__.py' for file in files):
            return True
    return False


def onerror(name):
    logger.error("Error importing module %s", name, exc_info=sys.exc_info())


def _scan_and_import_packages(package_name: str):
    try:
        logger.debug(f"Attempting to load module [{package_name}]")
        package_obj = importlib.import_module(package_name)
    except ImportError as e:
        logger.error(f"Could not import package '{package_name}': {e}")
        return

    # Use __path__ for namespace packages
    base_paths = list(package_obj.__path__)
    logger.debug(f"Scanning package {package_name} at paths {base_paths}")

    for base_path in base_paths:
        for _, name, is_pkg in pkgutil.walk_packages([base_path], prefix=package_name + '.', onerror=onerror):
            if name not in sys.modules:
                logger.debug(f"Loading package/module ({name})")
                try:
                    importlib.import_module(name)
                except ImportError as e:
                    logger.error(f"Could not import module '{name}': {e}")
                    continue
            else:
                logger.debug(f"Module {name} already loaded.")

        # Recursively scan subdirectories to handle namespace packages
        path_obj = Path(base_path)
        for path in path_obj.iterdir():
            if path.is_dir() and _is_package(path):
                sub_package_name = package_name + '.' + path.name
                logger.debug(f"Recursively scanning nested package {sub_package_name}")
                _scan_and_import_packages(sub_package_name)


def auto_wire(package: str):
    _scan_and_import_packages(package)
    injector = Injector()
    for name, cls in component_registry.items():
        injector.binder.bind(cls, to=cls)
