import logging
from dataclasses import dataclass, is_dataclass
from datetime import datetime
from enum import EnumMeta
from pathlib import Path
from typing import Type, List, Dict, TypedDict, Union

from inflection import dasherize, underscore
from rest_framework.serializers import Serializer

from django_rest_tsg import VERSION
from django_rest_tsg.templates import HEADER_TEMPLATE, IMPORT_TEMPLATE
from django_rest_tsg.typescript import (TypeScriptCode, build_interface_from_serializer, get_serializer_prefix,
                                        build_interface_from_dataclass, build_enum, TypeScriptCodeType)


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
            default_name = get_serializer_prefix(self.type)
        else:
            default_name = self.type.__name__
        return dasherize(underscore(self.options.get('alias', default_name)))


class TypeScriptBuildOptions(TypedDict, total=False):
    alias: str
    build_dir: Path


@dataclass
class TypeScriptBuilderConfig:
    tasks: List[TypeScriptBuildTask]
    build_dir: Path


def build(tp: Type, build_dir: Union[str, Path] = None, alias: str = None,
          options: TypeScriptBuildOptions = None) -> TypeScriptBuildTask:
    """
    Shortcut factory for TypeScriptBuildTask.
    """
    code: TypeScriptCode
    if issubclass(tp, Serializer):
        code = build_interface_from_serializer(tp)
    elif isinstance(tp, EnumMeta):
        code = build_enum(tp)
    elif is_dataclass(tp):
        code = build_interface_from_dataclass(tp)
    else:
        raise BuildException(f"Unsupported build type: {tp}")
    if not options:
        options = {}
    if build_dir:
        if isinstance(build_dir, str):
            build_dir = Path(build_dir)
        options['build_dir'] = build_dir
    if alias:
        options['alias'] = alias
    return TypeScriptBuildTask(type=tp, code=code, options=options)


class TypeScriptBuilder:
    def __init__(self, config: TypeScriptBuilderConfig):
        logger = logging.getLogger('django-rest-tsg')
        logger.addHandler(logging.StreamHandler())
        self.tasks = config.tasks
        self.build_dir = config.build_dir
        self.type_options_mapping: Dict[Type, TypeScriptBuildOptions] = {}
        for task in self.tasks:
            logger.info(f"Build task for \"{task.type}\" found.")
            self.type_options_mapping[task.type] = task.options

    def build_all(self):
        for task in self.tasks:
            self.build_task(task)

    def build_task(self, task: TypeScriptBuildTask):
        header = self.build_header(task)
        type_options = self.type_options_mapping.get(task.type, {})
        typescript_file = type_options.get('build_dir', self.build_dir) / self.get_typescript_filename(task)
        typescript_file.write_text(header + task.code.content)

    def build_header(self, task: TypeScriptBuildTask):
        header = HEADER_TEMPLATE.substitute(generator='django-rest-tsg', version=VERSION,
                                            type='.'.join((task.type.__module__,
                                                           task.type.__qualname__)),
                                            date=datetime.now().isoformat())
        for dependency in task.code.dependencies:
            dependency_options = self.type_options_mapping.get(dependency, {})
            dependency_filename = dependency_options.get('alias', dasherize(underscore(dependency.__name__)))
            if isinstance(dependency, EnumMeta):
                dependency_filename += '.enum'
            header += IMPORT_TEMPLATE.substitute(type=dependency.__name__,
                                                 filename=dependency_filename)
        header += '\n'
        return header

    def get_typescript_filename(self, task: TypeScriptBuildTask):
        if task.code.type == TypeScriptCodeType.ENUM:
            filename = f"{task.filename}.enum.ts"
        else:
            filename = f"{task.filename}.ts"
        return filename
