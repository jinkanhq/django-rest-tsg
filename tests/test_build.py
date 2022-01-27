from pathlib import Path

from django.core.management import call_command

from django_rest_tsg.build import TypeScriptBuilder, TypeScriptBuilderConfig
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


def skip_lines(content: str, lines: int = 4):
    return "\n".join(content.splitlines()[lines:])


def test_builder(tmp_path: Path):
    config = TypeScriptBuilderConfig(build_dir=tmp_path, tasks=BUILD_TASKS)
    builder = TypeScriptBuilder(config)
    builder.build_all()
    tmp_files = {file.name: file.read_text() for file in tmp_path.iterdir()}
    assert len(tmp_files) == len(BUILD_TASKS)
    assert "path.ts" in tmp_files
    assert skip_lines(tmp_files["path.ts"], 5) == PATH_INTERFACE
    assert "foobar-child.ts" in tmp_files
    assert skip_lines(tmp_files["foobar-child.ts"]) == FOOBAR_CHILD_INTERFACE
    assert "permission-flag.enum.ts" in tmp_files
    assert skip_lines(tmp_files["permission-flag.enum.ts"], 5) == PERMISSION_FLAG_ENUM


def test_command(tmp_path: Path):
    call_command("buildtypescript", "tests", "--build-dir", str(tmp_path))
    tmp_files = {file.name: file.read_text() for file in tmp_path.iterdir()}
    assert len(tmp_files) == len(BUILD_TASKS)
    assert "path.ts" in tmp_files
    assert "foobar-child.ts" in tmp_files
    assert "permission-flag.enum.ts" in tmp_files
