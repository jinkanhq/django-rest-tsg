from pathlib import Path

from django.core.management import call_command

from django_rest_tsg.build import TypeScriptBuilder, TypeScriptBuilderConfig
from tests.tsgconfig import BUILD_TASKS


def test_builder(tmp_path: Path):
    config = TypeScriptBuilderConfig(build_dir=tmp_path, tasks=BUILD_TASKS)
    builder = TypeScriptBuilder(config)
    builder.build_all()
    tmp_files = {file.name: file.read_text() for file in tmp_path.iterdir()}
    assert len(tmp_files) == len(BUILD_TASKS)
    assert 'path.ts' in tmp_files
    assert 'foobar-child.ts' in tmp_files
    assert 'permission-flag.enum.ts' in tmp_files


def test_command(tmp_path: Path):
    call_command('buildtypescript', 'tests', '--build-dir', str(tmp_path))
    tmp_files = {file.name: file.read_text() for file in tmp_path.iterdir()}
    assert len(tmp_files) == len(BUILD_TASKS)
    assert 'path.ts' in tmp_files
    assert 'foobar-child.ts' in tmp_files
    assert 'permission-flag.enum.ts' in tmp_files
