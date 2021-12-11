import importlib
import os
from pathlib import Path

from django.core.management import BaseCommand, CommandError

from django_rest_tsg.build import TypeScriptBuilder, TypeScriptBuilderConfig


class Command(BaseCommand):
    help = 'Build typescript codes from DRF things.'

    def add_arguments(self, parser):
        parser.add_argument('package', nargs='?', type=str)
        parser.add_argument('--build-dir', type=str)

    def handle(self, *args, **options):
        package_option = options.get('package')
        build_dir_option = options.get('build_dir')
        if not package_option:
            package_option = os.environ.get('DJANGO_SETTINGS_MODULE').rpartition('.')[0]
        module = importlib.import_module(package_option + '.tsgconfig')
        build_dir: Path = getattr(module, 'BUILD_DIR', Path(build_dir_option))
        if not build_dir:
            raise CommandError("No build_dir is specified.")
        config = TypeScriptBuilderConfig(tasks=getattr(module, 'BUILD_TASKS', []),
                                         build_dir=build_dir)
        builder = TypeScriptBuilder(config)
        builder.build_all()
