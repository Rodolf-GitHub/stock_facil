import getpass
from django.contrib.auth.hashers import make_password
from django.core.management.base import BaseCommand
from django.db import transaction

from cuenta.models import Cuenta
from usuario.models import Usuario


class Command(BaseCommand):
    help = (
        "Crea una cuenta y su usuario admin asociado. "
        "Si la cuenta ya existe, crea el usuario y lo asigna a esa cuenta."
    )

    def handle(self, *args, **options):
        self._listar_cuentas()

        # Nombre de cuenta
        cuenta_existente = None
        while True:
            cuenta_nombre = input("Nombre de cuenta: ").strip()
            if not cuenta_nombre:
                self.stderr.write("El nombre de la cuenta no puede estar vacio.")
                continue
            cuenta_existente = Cuenta.objects.filter(nombre=cuenta_nombre).first()
            if cuenta_existente:
                self.stdout.write(
                    f"La cuenta '{cuenta_nombre}' ya existe (id={cuenta_existente.id}). "
                    "Se creara el usuario y se asignara a esta cuenta."
                )
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
            if cuenta_existente:
                cuenta = cuenta_existente
                cuenta_creada = False
            else:
                cuenta = Cuenta.objects.create(nombre=cuenta_nombre)
                cuenta_creada = True
            usuario = Usuario.objects.create(
                cuenta=cuenta,
                email=email,
                hash_password=make_password(raw_password),
                es_admin=True,
            )

        if cuenta_creada:
            self.stdout.write(
                self.style.SUCCESS(
                    f"Cuenta '{cuenta.nombre}' creada (id={cuenta.id}) — "
                    f"Admin creado (id={usuario.id}, email={usuario.email})"
                )
            )
        else:
            self.stdout.write(
                self.style.SUCCESS(
                    f"Usuario admin creado (id={usuario.id}, email={usuario.email}) "
                    f"y asignado a la cuenta existente '{cuenta.nombre}' (id={cuenta.id})"
                )
            )

    def _listar_cuentas(self):
        cuentas = Cuenta.objects.order_by("nombre").values_list("id", "nombre")
        if not cuentas:
            self.stdout.write("No hay cuentas existentes.\n")
            return
        self.stdout.write("Cuentas existentes:")
        for cuenta_id, nombre in cuentas:
            self.stdout.write(f"  - [{cuenta_id}] {nombre}")
        self.stdout.write("")
