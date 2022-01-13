import logging
from dataclasses import dataclass, is_dataclass
from datetime import datetime
from enum import EnumMeta
from pathlib import Path
from typing import Type, List, Dict, TypedDict, Union

from django.conf import settings
from inflection import dasherize, underscore
from rest_framework.serializers import Serializer

from django_rest_tsg import VERSION
from django_rest_tsg.templates import HEADER_TEMPLATE, IMPORT_TEMPLATE
from django_rest_tsg.typescript import (
    TypeScriptCode,
    build_interface_from_serializer,
    get_serializer_prefix,
    build_interface_from_dataclass,
    build_enum,
    TypeScriptCodeType,
)


class BuildException(Exception):
    pass


@dataclass
class TypeScriptBuildTask:
    type: Type
    code: TypeScriptCode
    options: dict

    @property
    def filename(self):
        if issubclass(self.type, Serializer):
            default_stem = get_serializer_prefix(self.type)
        else:
            default_stem = self.type.__name__
        stem = dasherize(underscore(self.options.get("alias", default_stem)))
        if self.code.type == TypeScriptCodeType.ENUM:
            result = f"{stem}.enum.ts"
        else:
            result = f"{stem}.ts"
        return result


class TypeScriptBuildOptions(TypedDict, total=False):
    alias: str
    build_dir: Path


@dataclass
class TypeScriptBuilderConfig:
    tasks: List[TypeScriptBuildTask]
    build_dir: Path


def build(
    tp: Type,
    build_dir: Union[str, Path] = None,
    alias: str = None,
    options: TypeScriptBuildOptions = None,
) -> TypeScriptBuildTask:
    """
    Shortcut factory for TypeScriptBuildTask.
    """
    code: TypeScriptCode
    if not options:
        options = {}
    if issubclass(tp, Serializer):
        code = build_interface_from_serializer(tp, interface_name=options.get("alias"))
    elif isinstance(tp, EnumMeta):
        code = build_enum(tp, enum_name=options.get("alias"))
    elif is_dataclass(tp):
        code = build_interface_from_dataclass(tp, options)
    else:
        raise BuildException(f"Unsupported build type: {tp.__name__}")
    if build_dir:
        if isinstance(build_dir, str):
            build_dir = Path(build_dir)
        options["build_dir"] = build_dir
    if alias:
        options["alias"] = alias
    return TypeScriptBuildTask(type=tp, code=code, options=options)


class TypeScriptBuilder:
    def __init__(self, config: TypeScriptBuilderConfig):
        self.logger = logging.getLogger("django-rest-tsg")
        log_level = logging.DEBUG if settings.DEBUG else logging.INFO
        self.logger.setLevel(log_level)
        handler = logging.StreamHandler()
        handler.setLevel(log_level)
        formatter = logging.Formatter("%(asctime)s|%(name)s|%(levelname)s|%(message)s")
        handler.setFormatter(formatter)
        self.logger.addHandler(handler)
        self.tasks = config.tasks
        self.build_dir = config.build_dir
        self.type_options_mapping: Dict[Type, TypeScriptBuildOptions] = {}
        self.logger.info(f"{len(self.tasks)} build tasks found.")
        for task in self.tasks:
            self.logger.debug(f'Build task found: "{task.type.__name__}".')
            self.type_options_mapping[task.type] = task.options

    def build_all(self):
        for task in self.tasks:
            self.logger.info(f'Building "{task.type.__name__}"...')
            self.build_task(task)

    def build_task(self, task: TypeScriptBuildTask):
        header = self.build_header(task)
        type_options = self.type_options_mapping.get(task.type, {})
        typescript_file = type_options.get("build_dir", self.build_dir) / task.filename
        typescript_file.write_text(header + task.code.content)
        self.logger.debug(
            f'Typescript code for "{task.type.__name__}" saved as "{typescript_file}".'
        )

    def build_header(self, task: TypeScriptBuildTask):
        header = HEADER_TEMPLATE.substitute(
            generator="django-rest-tsg",
            version=VERSION,
            type=".".join((task.type.__module__, task.type.__qualname__)),
            date=datetime.now().isoformat(),
        )
        for dependency in task.code.dependencies:
            dependency_options = self.type_options_mapping.get(dependency, {})
            dependency_filename = dependency_options.get(
                "alias", dasherize(underscore(dependency.__name__))
            )
            if isinstance(dependency, EnumMeta):
                dependency_filename += ".enum"
            header += IMPORT_TEMPLATE.substitute(
                type=dependency.__name__, filename=dependency_filename
            )
        header += "\n"
        return header
