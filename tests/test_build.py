import shutil
import tempfile
import time

import pytest
from pathlib import Path
from itertools import chain

from django.core.management import call_command
from rest_framework import serializers

from django_rest_tsg.build import (
    TypeScriptBuilder,
    TypeScriptBuilderConfig,
    build,
    get_relative_path,
    get_digest,
)
from tests.serializers import PathSerializer, PathWrapperSerializer
from tests.test_dataclass import USER_INTERFACE
from tests.tsgconfig import BUILD_TASKS
from tests.test_serializer import PATH_INTERFACE, DEPARTMENT_INTERFACE
from tests.test_enum import PERMISSION_FLAG_ENUM


FOOBAR_CHILD_INTERFACE = """import { FoobarParent } from './foobar-parent';

export interface FoobarChild {
  id: number;
  parent: Parent;
  parents: Parent[];
  text: string;
  intNumber: number;
  uuid: string;
  url: string;
  description: string;
  config: any;
  time: string;
  slug: string;
  ipAddress: string;
  email: string;
  boolValue: boolean;
  floatNumber: number;
}"""

PATH_WRAPPER_INTERFACE = """import { Path } from '../path';

export interface PathWrapper {
  path: Path;
  meta: any;
}"""

DEPARTMENT_INTERFACE = (
    """import { User } from './user';

"""
    + DEPARTMENT_INTERFACE
)

PATH_V2_INTERFACE = """export interface Path {
  name: string;
  suffix: string;
  suffixes: string[];
  stem: string;
  isDirectory: boolean;
  size: number;
  metadata: any;
}"""


@pytest.fixture()
def another_build_dir():
    d = tempfile.TemporaryDirectory(prefix="django-rest-tsg")
    path = Path(d.name)
    subdir = path / "sub"
    subdir.mkdir(exist_ok=True)
    yield path
    shutil.rmtree(path, ignore_errors=True)


def skip_lines(content: str, lines: int = 6):
    return "\n".join(content.splitlines()[lines:])


def test_get_relative_path():
    path = Path("/var/tmp/django-rest-tsg/foo/bar.ts")
    dependency_path = Path("/var/tmp/cache/django-rest-tsg/bar/foo.ts")
    assert (
        get_relative_path(path, dependency_path)
        == "../../cache/django-rest-tsg/bar/foo.ts"
    )
    path = Path("/var/tmp/django-rest-tsg/foo.ts")
    dependency_path = Path("/var/tmp/django-rest-tsg/foo/bar/foobar.ts")
    assert get_relative_path(path, dependency_path) == "./foo/bar/foobar.ts"
    path = Path("/var/tmp/django-rest-tsg/foo.ts")
    dependency_path = Path("/var/tmp/django-rest-tsg/bar.ts")
    assert get_relative_path(path, dependency_path) == "./bar.ts"


def test_builder(tmp_path: Path, another_build_dir: Path):
    sub_dir = another_build_dir / "sub"
    tasks = BUILD_TASKS[1:]
    tasks.insert(0, build(PathSerializer, options={"build_dir": another_build_dir}))
    tasks.append(build(PathWrapperSerializer, options={"build_dir": sub_dir}))
    config = TypeScriptBuilderConfig(build_dir=tmp_path, tasks=tasks)
    builder = TypeScriptBuilder(config)
    builder.build_all()
    tmp_files = {
        file.name: file.read_text()
        for file in chain(
            tmp_path.iterdir(),
            iter(f for f in another_build_dir.iterdir() if f.is_file()),
            sub_dir.iterdir(),
        )
    }
    assert len(tmp_files) == len(tasks)
    assert "path.ts" in tmp_files
    assert skip_lines(tmp_files["path.ts"]) == PATH_INTERFACE
    assert "foobar-child.ts" in tmp_files
    assert skip_lines(tmp_files["foobar-child.ts"]) == FOOBAR_CHILD_INTERFACE
    assert "permission-flag.enum.ts" in tmp_files
    assert skip_lines(tmp_files["permission-flag.enum.ts"], 6) == PERMISSION_FLAG_ENUM
    assert "user.ts" in tmp_files
    assert skip_lines(tmp_files["user.ts"], 8) == USER_INTERFACE
    assert "path-wrapper.ts" in tmp_files
    assert skip_lines(tmp_files["path-wrapper.ts"]) == PATH_WRAPPER_INTERFACE
    assert "department.ts" in tmp_files
    assert skip_lines(tmp_files["department.ts"]) == DEPARTMENT_INTERFACE


def test_command(tmp_path: Path):
    call_command("buildtypescript", "tests", "--build-dir", str(tmp_path))
    tmp_files = {
        file.name: file.read_text()
        for file in chain(tmp_path.iterdir(), tmp_path.iterdir())
    }
    assert len(tmp_files) == len(BUILD_TASKS)
    assert "path.ts" in tmp_files
    assert "foobar-child.ts" in tmp_files
    assert "permission-flag.enum.ts" in tmp_files


def test_content_change(tmp_path: Path):
    tasks = [build(PathSerializer)]
    config = TypeScriptBuilderConfig(build_dir=tmp_path, tasks=tasks)
    builder = TypeScriptBuilder(config)
    builder.build_all()
    build_file = tmp_path / "path.ts"
    digest = get_digest(build_file)
    content = build_file.read_text()
    last_modified_on = build_file.stat().st_mtime
    # no change
    builder.build_all()
    same_digest = get_digest(build_file)
    same_content = build_file.read_text()
    same_last_modified_on = build_file.stat().st_mtime
    assert digest == same_digest
    assert content == same_content
    assert last_modified_on == same_last_modified_on
    # add field
    class PathVersion2Serializer(PathSerializer):
        metadata = serializers.JSONField()

    tasks = [build(PathVersion2Serializer, {"alias": "Path"})]
    config = TypeScriptBuilderConfig(build_dir=tmp_path, tasks=tasks)
    builder = TypeScriptBuilder(config)
    time.sleep(0.1)
    builder.build_all()
    digest_v2 = get_digest(build_file)
    last_modified_on_v2 = build_file.stat().st_mtime

    assert skip_lines(build_file.read_text()) == PATH_V2_INTERFACE
    assert digest != digest_v2
    assert last_modified_on_v2 > last_modified_on
