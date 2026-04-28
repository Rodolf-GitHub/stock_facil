from django.core.management.base import BaseCommand, CommandError

from cuenta.models import Cuenta


CAMPOS_EDITABLES = [
    ("nombre", str),
    ("cantidad_maxima_de_productos", int),
    ("cantidad_maxima_de_locales", int),
    ("cantidad_maxima_de_usuarios", int),
    ("cantidad_maxima_de_conteo_stock", int),
]


class Command(BaseCommand):
    help = "Edita los parametros (nombre y cantidades maximas) de una cuenta existente."

    def handle(self, *args, **options):
        self._listar_cuentas()

        # Buscar cuenta
        while True:
            entrada = input("Nombre o id de la cuenta a editar: ").strip()
            if not entrada:
                self.stderr.write("Debes ingresar un nombre o id.")
                continue
            cuenta = None
            if entrada.isdigit():
                cuenta = Cuenta.objects.filter(id=int(entrada)).first()
            if cuenta is None:
                cuenta = Cuenta.objects.filter(nombre=entrada).first()
            if cuenta is None:
                self.stderr.write("No se encontro ninguna cuenta con ese nombre o id.")
                continue
            break

        self.stdout.write(
            self.style.NOTICE(
                f"\nEditando cuenta '{cuenta.nombre}' (id={cuenta.id}). "
                "Deja vacio para mantener el valor actual.\n"
            )
        )

        cambios = {}
        for campo, tipo in CAMPOS_EDITABLES:
            actual = getattr(cuenta, campo)
            while True:
                nuevo = input(f"{campo} [{actual}]: ").strip()
                if not nuevo:
                    break
                if tipo is int:
                    try:
                        valor = int(nuevo)
                    except ValueError:
                        self.stderr.write("Debe ser un numero entero.")
                        continue
                    if valor < 0:
                        self.stderr.write("Debe ser un numero entero positivo.")
                        continue
                else:
                    valor = nuevo
                    if campo == "nombre" and valor != cuenta.nombre:
                        if Cuenta.objects.filter(nombre=valor).exclude(id=cuenta.id).exists():
                            self.stderr.write("Ya existe otra cuenta con ese nombre.")
                            continue
                cambios[campo] = valor
                break

        if not cambios:
            self.stdout.write("No se realizaron cambios.")
            return

        for campo, valor in cambios.items():
            setattr(cuenta, campo, valor)
        cuenta.save(update_fields=list(cambios.keys()))

        self.stdout.write(
            self.style.SUCCESS(
                f"Cuenta '{cuenta.nombre}' (id={cuenta.id}) actualizada. "
                f"Campos modificados: {', '.join(cambios.keys())}"
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
