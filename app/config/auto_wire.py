import importlib
import inspect
import logging
import os
import pkgutil
import sys
from pathlib import Path
from typing import Type, Any, Dict

from injector import Injector

component_registry: Dict[str, Type[Any]] = {}

logger = logging.getLogger(__name__)

injector = Injector()

"""" 
NOTE: this script assumes a package structure with a single shared root folder, 
which can be a package or a src folder.

Such a package structure could look like this:
- app/src/your_organisation/etc.
  - your_main.py
  - ui
    - main_window
      - main_window.py
      - ...
    - database
      - database.py
    - utils
      - ...
  - ...
"""

def component(cls: Type[Any]) -> Type[Any]:
    """
    Provides @component decorator to register a class as an injectable component (like a Spring bean).
    When a module is imported, all classes with this decorator will automatically be registered in the
    component_registry. This is why we need to package scan and import all modules in the project, to discover all
    injectable components.
    """
    logger.debug(f"Registering component {cls.__name__}")
    component_registry[cls.__name__] = cls
    return cls


def _get_main_module_name():
    """
    Get the name of the main module (i.e. the module that is run with `python -m` or directly).
    The reason we need this, is that we want to avoid importing the main module itself, as it is already currently
    being loaded (and therefor not in `sys.modules`, yet).
    """
    for frame_info in reversed(inspect.stack()):
        if frame_info.frame.f_globals.get('__name__') == '__main__':
            # Extract the module name from the file path
            return Path(frame_info.filename).stem
    return None


main_module_name = _get_main_module_name()  # for main.py, this would be 'main'


def _is_package(path):
    """Check if a given path is a Python package by looking for .py files in it and its subdirectories."""
    for root, dirs, files in os.walk(path):
        if any(file.endswith('.py') and file != '__init__.py' for file in files):
            return True
    return False


# I'm not sure if this is ever called, or whether it is needed, since we also nest our import calls in try-except blocks
def onerror(name):
    logger.error("Error importing module %s", name, exc_info=sys.exc_info())


def _scan_and_import_packages(package_name: str, is_source_folder_rather_base_package: bool = True):
    """
    Recursively scan and import all packages and modules in the given package.
    The complexity of this function is due to the fact that we need to handle namespace packages, which are packages
    that are spread across multiple directories. This is a common pattern in Python, but it makes it a bit more
    complex to scan and import all modules in a package. Moreover, we need to avoid importing the main module itself,
    as well as any modules that have already been imported prior to this function being called.

    :param is_source_folder_rather_base_package: Whether the package_name is the base package or a sub-package
    This dictates whether we should include the package name in the recursive call to this function. For example, if
    the package_name name is 'app' or 'src' and 'is_source_folder_rather_base_package' is true, we won't include the
    package name in the recursive call, as that will result in incorrect module names. However, if the package_name is
    'app' and 'is_source_folder_rather_base_package' is false, we will include the package name in the
    recursive call, as that will result in correct module names ('src' would be unlikely in this scenario).
    """
    try:
        logger.debug(f"Loading module [{package_name}]")
        package_obj = importlib.import_module(package_name)
    except ImportError as e:
        logger.error(f"Could not import package '{package_name}': {e}")
        return

    base_paths = list(package_obj.__path__)
    logger.debug(f"Scanning package {package_name} at paths {base_paths}")

    for base_path in base_paths:
        # Adjust the prefix based on whether this is the base package or a nested package
        prefix = '' if is_source_folder_rather_base_package else package_name + '.'
        for _, name, is_pkg in pkgutil.walk_packages([base_path], prefix=prefix, onerror=onerror):
            if name not in sys.modules and not name == main_module_name:
                logger.debug(f"Loading package/module ({name})")
                try:
                    importlib.import_module(name)
                except ImportError as e:
                    logger.error(f"Could not import module '{name}': {e}")
                    continue

        # Recursively scan subdirectories to handle namespace packages
        path_obj = Path(base_path)
        for path in path_obj.iterdir():
            if path.is_dir() and _is_package(path):
                # For sub-packages, always include the package name in the recursive call
                sub_package_name = package_name + '.' + path.name if not is_source_folder_rather_base_package else path.name
                logger.debug(f"Recursively scanning nested package {sub_package_name}")
                _scan_and_import_packages(sub_package_name, is_source_folder_rather_base_package=False)


def auto_wire(package: str):
    """
    Discover all injectable components in the given package and its sub-packages, and bind them to themselves in
    'injector'.
    """
    _scan_and_import_packages(package, is_source_folder_rather_base_package=True)
    for name, cls in component_registry.items():
        logger.info(f"Creating @component binding '{name}' -> {cls}")
        injector.binder.bind(cls, to=cls)
