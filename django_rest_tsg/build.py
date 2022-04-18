import logging
import hashlib
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
    TypeScriptCodeType,
    build_enum,
    build_interface_from_dataclass,
    build_interface_from_serializer,
    get_serializer_prefix,
    register,
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
    build_dir: Union[str, Path]
    enforce_uppercase: bool


@dataclass
class TypeScriptBuilderConfig:
    tasks: List[TypeScriptBuildTask]
    build_dir: Union[str, Path]


def build(
    tp: Type,
    options: TypeScriptBuildOptions = None,
) -> TypeScriptBuildTask:
    """
    Shortcut factory for TypeScriptBuildTask.
    """
    if options is None:
        options = {}
    alias = options.get("alias")
    if alias:
        register(tp, alias)
    code: TypeScriptCode
    if not options:
        options = {}
    if issubclass(tp, Serializer):
        code = build_interface_from_serializer(tp, interface_name=alias)
    elif isinstance(tp, EnumMeta):
        code = build_enum(
            tp,
            enum_name=alias,
            enforce_uppercase=options.get("enforce_uppercase", False),
        )
    elif is_dataclass(tp):
        code = build_interface_from_dataclass(tp, interface_name=alias)
    else:
        raise BuildException(f"Unsupported build type: {tp.__name__}")
    build_dir = options.get("build_dir")
    if build_dir and isinstance(build_dir, str):
        options["build_dir"] = Path(build_dir)
    return TypeScriptBuildTask(type=tp, code=code, options=options)


def get_relative_path(path: Path, dependency_path: Path) -> str:
    path_length = len(path.parts)
    dependency_path_length = len(dependency_path.parts)
    common_path_length = min(path_length, dependency_path_length)
    break_idx = 0
    for i in range(common_path_length):
        if path.parts[i] != dependency_path.parts[i]:
            break_idx = i
            break
    if common_path_length == dependency_path_length and break_idx == 0:
        return f"./{dependency_path.name}"
    levels = path_length - break_idx - 1
    if levels > 0:
        parents = levels * "../"
    else:
        parents = "./"
    return parents + "/".join(dependency_path.parts[break_idx:])


def get_digest(typescript_file: Path) -> str:
    with typescript_file.open("r") as f:
        for i, line in enumerate(f):
            line: str
            if i == 3 and line.startswith("// Digest: ") and len(line) == 64 + 11 + 1:
                return line[11:-1]
            if i > 3:
                break
    return ""


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
        type_options = self.type_options_mapping.get(task.type, {})
        build_dir = type_options.get("build_dir", self.build_dir)
        build_dir.mkdir(parents=True, exist_ok=True)
        typescript_file = build_dir / task.filename
        hexdigest = None
        if typescript_file.exists():
            hexdigest = get_digest(typescript_file)
        import_statements = self.build_import_statements(task)
        content_without_header = import_statements + task.code.content
        content_without_header_hexdigest = hashlib.sha256(
            content_without_header.encode("utf8")
        ).hexdigest()
        if hexdigest == content_without_header_hexdigest:
            self.logger.info(
                f'No change in content. Skip saving task "{task.type.__name__}".'
            )
            return

        header = self.build_header(task, content_without_header_hexdigest)
        typescript_file.write_text(header + content_without_header)
        self.logger.debug(
            f'Typescript code for "{task.type.__name__}" saved as "{typescript_file}".'
        )

    def build_header(self, task: TypeScriptBuildTask, hexdigest: str):
        header = HEADER_TEMPLATE.substitute(
            generator="django-rest-tsg",
            version=VERSION,
            type=".".join((task.type.__module__, task.type.__qualname__)),
            date=datetime.now().isoformat(),
            digest=hexdigest,
        )
        header += "\n"
        return header

    def build_import_statements(self, task: TypeScriptBuildTask):
        result = ""
        for dependency in task.code.dependencies:
            dependency_options = self.type_options_mapping.get(dependency, {})
            if "alias" in dependency_options:
                dependency_name = dependency_options["alias"]
            elif issubclass(dependency, Serializer):
                dependency_name = get_serializer_prefix(dependency)
            else:
                dependency_name = dependency.__name__
            dependency_filename = dasherize(underscore(dependency_name))
            if isinstance(dependency, EnumMeta):
                dependency_filename += ".enum"
            build_dir = task.options.get("build_dir", self.build_dir)
            dependency_build_dir = dependency_options.get("build_dir", self.build_dir)
            dependency_path = get_relative_path(
                build_dir / "foobar", dependency_build_dir / dependency_filename
            )
            result += IMPORT_TEMPLATE.substitute(
                type=dependency_name, filename=dependency_path
            )
        if result:
            result += "\n"
        return result
