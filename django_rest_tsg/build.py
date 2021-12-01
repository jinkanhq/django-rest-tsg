import importlib
import os
from dataclasses import dataclass, is_dataclass
from enum import EnumMeta
from pathlib import Path
from types import ModuleType
from typing import Type, Iterable, List

from rest_framework.serializers import Serializer

from django_rest_tsg.typescript import TypeScriptCode, build_interface_from_serializer, build_enum, \
    build_interface_from_dataclass


def get_typescript_generator_config(package: str = None) -> ModuleType:
    if not package:
        package = os.environ.get('DJANGO_SETTINGS_MODULE').rpartition('.')[0]
    module = importlib.import_module(package + '.tsgconfig')
    return module


@dataclass
class TypeScriptBuildTask:
    type: Type
    directory: Path
    with_name: str
    options: dict


def build(tp: Type, directory: Path = None, with_name: str = None, options: dict = None):
    """
    Shortcut factory function of build task.
    """
    if not options:
        options = {}
    return TypeScriptBuildTask(type=tp, directory=directory, with_name=with_name, options=options)
