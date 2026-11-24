"""Módulo de carga: lee un Excel, lo limpia con pandas y guarda en MySQL solo las filas buenas."""
from datetime import datetime

import pandas as pd

from app import db
from app.models import Cliente, Mascota, Veterinario, Servicio, Cita

HOJAS = ["mascotas", "citas"]
# Columnas que debe traer cada hoja del Excel
COLUMNAS = {
    "mascotas": ["cliente_dni", "nombre", "especie", "raza", "sexo", "fecha_nacimiento", "peso", "color", "observaciones"],
    "citas": ["cliente_dni", "mascota_nombre", "veterinario_dni", "servicio_nombre", "fecha", "hora", "motivo", "observaciones", "estado"],
}
# Dos filas son repetidas si coinciden en estas columnas
CLAVES = {"mascotas": ["cliente_dni", "nombre"], "citas": ["cliente_dni", "mascota_nombre", "servicio_nombre", "fecha"]}
COLUMNAS_TEXTO = ["cliente_dni", "nombre", "mascota_nombre", "veterinario_dni", "servicio_nombre", "especie", "raza", "sexo", "color", "motivo", "estado", "hora"]
ESTADOS = ["Pendiente", "Confirmada", "En atención", "Completada", "Cancelada"]
MAX_FILAS = 5000


def texto(valor):
    """Quita espacios; si queda vacío devuelve None (nulo)."""
    if pd.isna(valor):
        return None
    valor = str(valor).strip()
    return valor or None


def vacio(valor):
    return pd.isna(valor)


class CargadorExcel:
    def __init__(self, archivo):
        try:
            # dtype=str en los DNI para no perder ceros a la izquierda
            hojas = pd.read_excel(archivo, sheet_name=None, dtype={"cliente_dni": str, "veterinario_dni": str})
        except Exception:
            raise ValueError("No se pudo leer el archivo. Verifica que sea un Excel .xlsx válido")
        self.hojas = {}
        for nombre, tabla in hojas.items():
            tabla.columns = [str(columna).strip().lower() for columna in tabla.columns]
            self.hojas[nombre.strip().lower()] = tabla
        self.validar()

    def validar(self):
        presentes = [hoja for hoja in HOJAS if hoja in self.hojas]
        if not presentes:
            raise ValueError('El Excel debe tener una hoja "mascotas" y/o una hoja "citas"')
        for hoja in presentes:
            faltan = [columna for columna in COLUMNAS[hoja] if columna not in self.hojas[hoja].columns]
            if faltan:
                raise ValueError(f'A la hoja "{hoja}" le faltan las columnas: {", ".join(faltan)}')
            if len(self.hojas[hoja]) > MAX_FILAS:
                raise ValueError(f'La hoja "{hoja}" tiene más de {MAX_FILAS} filas')

    def limpiar(self, nombre):
        """Cuenta nulos, convierte fechas, quita duplicados y rellena nulos. Devuelve la tabla limpia y el informe."""
        tabla = self.hojas[nombre][COLUMNAS[nombre]].copy()
        for columna in COLUMNAS_TEXTO:
            if columna in tabla.columns:
                tabla[columna] = tabla[columna].map(texto)

        informe = {"filas_leidas": len(tabla)}
        nulos = tabla.isna().sum()                                                  # pandas: isna
        informe["nulos_por_columna"] = {columna: int(n) for columna, n in nulos.items() if n > 0}

        columna_fecha = "fecha_nacimiento" if nombre == "mascotas" else "fecha"
        tabla[columna_fecha] = pd.to_datetime(tabla[columna_fecha], errors="coerce")  # pandas: to_datetime

        repetidas = tabla.duplicated(subset=CLAVES[nombre], keep="first")           # pandas: duplicated
        informe["filas_duplicadas"] = [int(indice) + 2 for indice in tabla.index[repetidas]]   # fila del Excel (la 1 es el encabezado)
        informe["duplicados_eliminados"] = int(repetidas.sum())
        tabla = tabla[~repetidas]

        rellenados = {}
        if nombre == "mascotas":
            # Peso vacío: se rellena con la mediana de su especie
            tabla["peso"] = pd.to_numeric(tabla["peso"], errors="coerce")
            vacios_antes = int(tabla["peso"].isna().sum())
            mediana_especie = tabla.groupby("especie")["peso"].transform("median")
            tabla["peso"] = tabla["peso"].fillna(mediana_especie).fillna(tabla["peso"].median())   # pandas: fillna
            rellenados["peso"] = vacios_antes - int(tabla["peso"].isna().sum())
        else:
            for columna, valor in [("estado", "Pendiente"), ("motivo", "Sin motivo registrado")]:
                vacios = int(tabla[columna].isna().sum())
                tabla[columna] = tabla[columna].fillna(valor)
                rellenados[columna] = vacios
        informe["nulos_rellenados"] = {columna: n for columna, n in rellenados.items() if n > 0}
        return tabla, informe

    def guardar_mascotas(self, tabla, informe):
        omitidas, insertadas = [], 0
        for indice, fila in tabla.iterrows():
            numero = int(indice) + 2
            if any(vacio(fila[columna]) for columna in ["cliente_dni", "nombre", "especie", "sexo"]):
                omitidas.append({"fila": numero, "motivo": "Falta un dato obligatorio (cliente_dni, nombre, especie o sexo)"})
                continue
            if fila["sexo"] not in ("Macho", "Hembra"):
                omitidas.append({"fila": numero, "motivo": 'El sexo debe ser "Macho" o "Hembra"'})
                continue
            cliente = Cliente.query.filter_by(dni=fila["cliente_dni"]).first()
            if cliente is None:
                omitidas.append({"fila": numero, "motivo": f'El cliente con DNI {fila["cliente_dni"]} no existe'})
                continue
            if Mascota.query.filter_by(cliente_id=cliente.id, nombre=fila["nombre"]).first():
                omitidas.append({"fila": numero, "motivo": "La mascota ya existe en la base de datos"})
                continue
            db.session.add(Mascota(cliente_id=cliente.id, nombre=fila["nombre"], especie=fila["especie"], raza=fila["raza"], sexo=fila["sexo"],
                                   fecha_nacimiento=None if vacio(fila["fecha_nacimiento"]) else fila["fecha_nacimiento"].date(),
                                   peso=None if vacio(fila["peso"]) else float(fila["peso"]), color=fila["color"], observaciones=texto(fila["observaciones"])))
            insertadas += 1
        informe["insertadas"], informe["omitidas"] = insertadas, omitidas

    def guardar_citas(self, tabla, informe):
        omitidas, insertadas = [], 0
        for indice, fila in tabla.iterrows():
            numero = int(indice) + 2
            if any(vacio(fila[columna]) for columna in ["cliente_dni", "mascota_nombre", "veterinario_dni", "servicio_nombre"]):
                omitidas.append({"fila": numero, "motivo": "Falta un dato obligatorio (cliente_dni, mascota_nombre, veterinario_dni o servicio_nombre)"})
                continue
            if vacio(fila["fecha"]):
                omitidas.append({"fila": numero, "motivo": "La fecha está vacía o no es válida"})
                continue
            try:
                hora = datetime.strptime(str(fila["hora"])[:5], "%H:%M").time()
            except ValueError:
                omitidas.append({"fila": numero, "motivo": "La hora está vacía o no es válida (usa HH:MM)"})
                continue
            if fila["estado"] not in ESTADOS:
                omitidas.append({"fila": numero, "motivo": f'El estado "{fila["estado"]}" no es válido'})
                continue

            cliente = Cliente.query.filter_by(dni=fila["cliente_dni"]).first()
            mascota = cliente and Mascota.query.filter_by(cliente_id=cliente.id, nombre=fila["mascota_nombre"]).first()
            veterinario = Veterinario.query.filter_by(dni=fila["veterinario_dni"]).first()
            servicio = Servicio.query.filter_by(nombre=fila["servicio_nombre"]).first()
            if not mascota:
                motivo = "La mascota no existe (revisa cliente_dni y mascota_nombre)"
            elif not veterinario:
                motivo = f'El veterinario con DNI {fila["veterinario_dni"]} no existe'
            elif not servicio:
                motivo = f'El servicio "{fila["servicio_nombre"]}" no existe'
            elif Cita.query.filter_by(veterinario_id=veterinario.id, fecha=fila["fecha"].date(), hora=hora).first():
                motivo = "El veterinario ya tiene una cita en esa fecha y hora"
            elif Cita.query.filter_by(mascota_id=mascota.id, servicio_id=servicio.id, fecha=fila["fecha"].date()).first():
                motivo = "La cita ya existe en la base de datos"
            else:
                motivo = None
            if motivo:
                omitidas.append({"fila": numero, "motivo": motivo})
                continue
            db.session.add(Cita(mascota_id=mascota.id, veterinario_id=veterinario.id, servicio_id=servicio.id, fecha=fila["fecha"].date(), hora=hora,
                                motivo=fila["motivo"], observaciones=texto(fila["observaciones"]), estado=fila["estado"]))
            insertadas += 1
        informe["insertadas"], informe["omitidas"] = insertadas, omitidas

    def procesar(self):
        """Limpia cada hoja y guarda las filas buenas. Si algo falla, no se guarda nada."""
        resumen = {}
        try:
            for nombre in HOJAS:                       # primero mascotas y después citas
                if nombre not in self.hojas:
                    continue
                tabla, informe = self.limpiar(nombre)
                if nombre == "mascotas":
                    self.guardar_mascotas(tabla, informe)
                else:
                    self.guardar_citas(tabla, informe)
                resumen[nombre] = informe
            db.session.commit()
        except Exception:
            db.session.rollback()
            raise
        return resumen
