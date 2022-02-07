import shutil
from pathlib import Path
from itertools import chain

import pytest
from django.core.management import call_command

from django_rest_tsg.build import TypeScriptBuilder, TypeScriptBuilderConfig
from tests.test_dataclass import USER_INTERFACE
from tests.tsgconfig import BUILD_TASKS
from tests.test_serializer import PATH_INTERFACE
from tests.test_enum import PERMISSION_FLAG_ENUM


FOOBAR_CHILD_INTERFACE = """import { FoobarParent } from './foobar-parent.ts';

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


TEST_BUILD_DIR = "/tmp/django-rest-tsg"


@pytest.fixture(scope="module", autouse=True)
def cleanup():
    shutil.rmtree(TEST_BUILD_DIR, ignore_errors=True)


def skip_lines(content: str, lines: int = 4):
    return "\n".join(content.splitlines()[lines:])


def test_builder(tmp_path: Path):
    config = TypeScriptBuilderConfig(build_dir=tmp_path, tasks=BUILD_TASKS)
    builder = TypeScriptBuilder(config)
    builder.build_all()
    tmp_files = {
        file.name: file.read_text()
        for file in chain(tmp_path.iterdir(), Path(TEST_BUILD_DIR).iterdir())
    }
    assert len(tmp_files) == len(BUILD_TASKS)
    assert "path.ts" in tmp_files
    assert skip_lines(tmp_files["path.ts"], 5) == PATH_INTERFACE
    assert "foobar-child.ts" in tmp_files
    assert skip_lines(tmp_files["foobar-child.ts"]) == FOOBAR_CHILD_INTERFACE
    assert "permission-flag.enum.ts" in tmp_files
    assert skip_lines(tmp_files["permission-flag.enum.ts"], 5) == PERMISSION_FLAG_ENUM
    assert "user.ts" in tmp_files
    assert skip_lines(tmp_files["user.ts"], 6) == USER_INTERFACE


def test_command(tmp_path: Path):
    call_command("buildtypescript", "tests", "--build-dir", str(tmp_path))
    tmp_files = {
        file.name: file.read_text()
        for file in chain(tmp_path.iterdir(), Path(TEST_BUILD_DIR).iterdir())
    }
    assert len(tmp_files) == len(BUILD_TASKS)
    assert "path.ts" in tmp_files
    assert "foobar-child.ts" in tmp_files
    assert "permission-flag.enum.ts" in tmp_files
