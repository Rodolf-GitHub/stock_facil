from django.contrib.auth.hashers import make_password
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from cuenta.models import Cuenta
from usuario.models import Usuario


class Command(BaseCommand):
    help = "Crea una cuenta y su usuario admin asociado."

    def add_arguments(self, parser):
        parser.add_argument(
            "--cuenta",
            required=True,
            help="Nombre de la cuenta a crear",
        )
        parser.add_argument(
            "--email",
            required=True,
            help="Email del usuario admin",
        )
        parser.add_argument(
            "--password",
            required=True,
            help="Contrasena del usuario admin",
        )

    def handle(self, *args, **options):
        cuenta_nombre = (options["cuenta"] or "").strip()
        email = (options["email"] or "").strip().lower()
        raw_password = (options["password"] or "").strip()

        if not cuenta_nombre:
            raise CommandError("El nombre de la cuenta no puede ser vacio")

        if not email:
            raise CommandError("El email no puede ser vacio")

        if not raw_password:
            raise CommandError("La contrasena no puede ser vacia")

        if Cuenta.objects.filter(nombre=cuenta_nombre).exists():
            raise CommandError("Ya existe una cuenta con ese nombre")

        if Usuario.objects.filter(email=email).exists():
            raise CommandError("Ya existe un usuario con ese email")

        with transaction.atomic():
            cuenta = Cuenta.objects.create(nombre=cuenta_nombre)
            usuario = Usuario.objects.create(
                cuenta=cuenta,
                email=email,
                hash_password=make_password(raw_password),
                es_admin=True,
            )

        self.stdout.write(
            self.style.SUCCESS(
                f"Cuenta creada (id={cuenta.id}) y admin creado (id={usuario.id}, email={usuario.email})"
            )
        )
