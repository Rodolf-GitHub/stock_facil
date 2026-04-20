from pathlib import Path

from django.core.management import BaseCommand, CommandError, call_command


class Command(BaseCommand):
    help = (
        "Create a Django app scaffold for Django Ninja with api.py and "
        "schemas.py, without admin.py, tests.py or views.py."
    )

    schemas_file_content = "\n".join(
        [
            "from ninja import Schema, ModelSchema",
            "from typing import Optional",
            "",
        ]
    )

    api_file_content = "\n".join(
        [
            "from ninja import Router",
            "from ninja.pagination import paginate",
            "from django.shortcuts import get_object_or_404",
            "from .schemas import *",
            "from core.utils.search_filter import search_filter",
            "",
            "router = Router()",
            "",
        ]
    )

    def add_arguments(self, parser):
        parser.add_argument("name", help="Name of the app to create")
        parser.add_argument(
            "directory",
            nargs="?",
            help="Optional destination directory (same behavior as startapp)",
        )

    def handle(self, *args, **options):
        app_name = options["name"]
        directory = options.get("directory")

        startapp_args = [app_name]
        if directory:
            startapp_args.append(directory)

        try:
            call_command("startapp", *startapp_args)
        except Exception as exc:
            raise CommandError(f"Could not create app '{app_name}': {exc}") from exc

        app_path = Path(directory) if directory else Path.cwd() / app_name

        for filename in ("admin.py", "tests.py", "views.py"):
            file_path = app_path / filename
            if file_path.exists():
                file_path.unlink()

        (app_path / "schemas.py").write_text(
            self.schemas_file_content,
            encoding="utf-8",
        )
        (app_path / "api.py").write_text(
            self.api_file_content,
            encoding="utf-8",
        )

        self.stdout.write(
            self.style.SUCCESS(
                f"Ninja app '{app_name}' created at '{app_path}' "
                "with api.py and schemas.py, without admin.py, tests.py or views.py."
            )
        )
