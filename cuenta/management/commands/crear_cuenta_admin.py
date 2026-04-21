import getpass
from django.contrib.auth.hashers import make_password
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from cuenta.models import Cuenta
from usuario.models import Usuario


class Command(BaseCommand):
    help = "Crea una cuenta y su usuario admin asociado."

    def handle(self, *args, **options):
        # Nombre de cuenta
        while True:
            cuenta_nombre = input("Nombre de cuenta: ").strip()
            if not cuenta_nombre:
                self.stderr.write("El nombre de la cuenta no puede estar vacio.")
                continue
            if Cuenta.objects.filter(nombre=cuenta_nombre).exists():
                self.stderr.write("Ya existe una cuenta con ese nombre.")
                continue
            break

        # Email
        while True:
            email = input("Email: ").strip().lower()
            if not email:
                self.stderr.write("El email no puede estar vacio.")
                continue
            if Usuario.objects.filter(email=email).exists():
                self.stderr.write("Ya existe un usuario con ese email.")
                continue
            break

        # Contraseña con confirmacion
        while True:
            raw_password = getpass.getpass("Contraseña: ")
            if not raw_password:
                self.stderr.write("La contraseña no puede estar vacia.")
                continue
            raw_password2 = getpass.getpass("Contraseña (confirmacion): ")
            if raw_password != raw_password2:
                self.stderr.write("Las contraseñas no coinciden.")
                continue
            break

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
                f"Cuenta '{cuenta.nombre}' creada (id={cuenta.id}) — "
                f"Admin creado (id={usuario.id}, email={usuario.email})"
            )
        )
