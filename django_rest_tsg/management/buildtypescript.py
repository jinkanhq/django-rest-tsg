import importlib
import os
from dataclasses import is_dataclass
from enum import EnumMeta
from pathlib import Path
from typing import List

from django.core.management import BaseCommand, CommandError
from rest_framework.serializers import Serializer

from django_rest_tsg.typescript import build_interface_from_dataclass, build_interface_from_serializer, build_enum, \
    TypeScriptCode
from django_rest_tsg.build import TypeScriptBuildTask


class Command(BaseCommand):
    help = 'Closes the specified poll for voting'

    def build(self, task: TypeScriptBuildTask, default_directory: Path):
        code: TypeScriptCode = None
        if issubclass(task.type, Serializer):
            code = build_interface_from_serializer(task.type)
        elif isinstance(task.type, EnumMeta):
            code = build_enum(task.type)
        elif is_dataclass(task.type):
            code = build_interface_from_dataclass(task.type)
        else:
            raise CommandError(f"Unsupported build type: {task.type.__name__}")
        code.save(directory=task.directory or default_directory, with_name=task.with_name)

    def handle(self, *args, **options):
        prefix = os.environ.get('DJANGO_SETTINGS_MODULE').rpartition('.')[0]
        module = importlib.import_module(prefix + '.tsconfig')
        build_tasks: List[TypeScriptBuildTask] = getattr(module, 'build_tasks')
        default_directory: Path = getattr(module, 'DEFAULT_DIRECTORY')
        for task in build_tasks:
            self.build(task, default_directory)
