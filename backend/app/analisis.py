"""Análisis de datos de la clínica con pandas y numpy."""
from functools import reduce

import numpy as np
import pandas as pd

from app import db

MESES = ["Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio", "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"]
DIAS = ["lunes", "martes", "miércoles", "jueves", "viernes", "sábado", "domingo"]


# Programación funcional: función que recibe otra función como parámetro
def aplicar_a_lista(funcion, lista):
    return list(map(funcion, lista))


def redondear(valor):
    """Devuelve None si no hay valor (NaN), para que el JSON sea válido."""
    return None if pd.isna(valor) else round(float(valor), 2)


def formatear_hora(tiempo):
    """MySQL entrega la hora como timedelta; la pasamos a 'HH:MM'."""
    if isinstance(tiempo, str):
        return tiempo[:5]
    segundos = int(tiempo.total_seconds())
    return f"{segundos // 3600:02d}:{segundos % 3600 // 60:02d}"


class AnalizadorClinica:
    """Carga las tablas de MySQL en pandas y calcula los análisis."""

    def __init__(self):
        self.datos = self._cargar_datos()
        self.resumen_limpieza = self.limpieza()
        self._calcular_edad()

    def _cargar_datos(self):
        # pandas: leer las tablas de MySQL y unirlas con merge
        citas = pd.read_sql("SELECT id, mascota_id, veterinario_id, servicio_id, fecha, hora, estado FROM citas", db.engine)
        servicios = pd.read_sql("SELECT id AS servicio_id, nombre AS servicio, precio FROM servicios", db.engine)
        mascotas = pd.read_sql("SELECT id AS mascota_id, nombre AS mascota, especie, fecha_nacimiento, peso FROM mascotas", db.engine)
        veterinarios = pd.read_sql("SELECT id AS veterinario_id, nombres, apellidos FROM veterinarios", db.engine)

        veterinarios["veterinario"] = veterinarios["nombres"] + " " + veterinarios["apellidos"]
        tabla = citas.merge(mascotas, on="mascota_id", how="left")
        tabla = tabla.merge(servicios, on="servicio_id", how="left")
        tabla = tabla.merge(veterinarios[["veterinario_id", "veterinario"]], on="veterinario_id", how="left")
        tabla["hora"] = tabla["hora"].apply(formatear_hora)
        tabla["precio"] = pd.to_numeric(tabla["precio"])
        tabla["peso"] = pd.to_numeric(tabla["peso"])
        return tabla

    def limpieza(self):
        """Cuenta nulos, quita duplicados y convierte fechas. Devuelve un resumen."""
        filas_antes = len(self.datos)
        nulos = self.datos.isna().sum()                      # pandas: isna
        nulos = {columna: int(n) for columna, n in nulos.items() if n > 0}

        # Una cita duplicada: misma mascota, mismo servicio y mismo día
        columnas_clave = ["mascota_id", "servicio_id", "fecha"]
        self.datos = self.datos.drop_duplicates(subset=columnas_clave, keep="first")
        duplicados = filas_antes - len(self.datos)

        self.datos["fecha"] = pd.to_datetime(self.datos["fecha"])
        self.datos["fecha_nacimiento"] = pd.to_datetime(self.datos["fecha_nacimiento"])
        self.datos["mes"] = self.datos["fecha"].dt.month
        self.datos["dia_semana"] = self.datos["fecha"].dt.dayofweek
        return {
            "filas_antes": filas_antes,
            "filas_despues": len(self.datos),
            "nulos_por_columna": nulos,
            "duplicados_eliminados": duplicados,
            "fechas_convertidas": ["fecha", "fecha_nacimiento"],
        }

    def _calcular_edad(self):
        dias = pd.Timestamp.today().normalize() - self.datos["fecha_nacimiento"]
        self.datos["edad"] = (dias.dt.days / 365.25).round(1)

    def _mascotas_unicas(self):
        """Una fila por mascota, para no contarla varias veces."""
        return self.datos.drop_duplicates(subset="mascota_id")

    def kpis(self):
        estados = list(self.datos["estado"])
        contar = lambda estado: len(list(filter(lambda e: e == estado, estados)))   # filter + lambda
        completadas = contar("Completada")
        canceladas = contar("Cancelada")
        # Pendientes = todo lo que aún no se cerró (Pendiente, Confirmada, En atención)
        pendientes = len(estados) - completadas - canceladas

        precios = self.datos.loc[self.datos["estado"] == "Completada", "precio"]
        precios_completadas = aplicar_a_lista(float, precios)                       # función que recibe otra función (map)
        ingresos = reduce(lambda total, precio: total + precio, precios_completadas, 0)  # reduce
        return {"total": len(estados), "pendientes": pendientes, "completadas": completadas, "canceladas": canceladas, "ingresos": round(ingresos, 2)}

    def citas_por_estado(self):
        conteo = self.datos["estado"].value_counts()                                # value_counts
        return [{"estado": estado, "cantidad": int(cantidad)} for estado, cantidad in conteo.items()]

    def citas_por_mes(self):
        conteo = self.datos.groupby("mes").size()                                   # groupby
        conteo = conteo.reindex(range(1, 13), fill_value=0)                         # meses sin citas = 0
        return [{"mes": MESES[mes - 1][:3], "cantidad": int(cantidad)} for mes, cantidad in conteo.items()]

    def estadisticas_precio(self):
        precios = self.datos["precio"].dropna().to_numpy()
        if len(precios) == 0:
            return {"promedio": None, "desviacion": None, "minimo": None, "maximo": None}
        return {"promedio": redondear(np.mean(precios)), "desviacion": redondear(np.std(precios)),
                "minimo": redondear(np.min(precios)), "maximo": redondear(np.max(precios))}

    def resumen_estadistico(self):
        """describe() de precio, peso y edad, más la mediana."""
        columnas = {"precio": self.datos["precio"], "peso": self._mascotas_unicas()["peso"], "edad": self._mascotas_unicas()["edad"]}
        resultado = {}
        for nombre, serie in columnas.items():
            resumen = serie.describe()                                              # pandas: describe
            resultado[nombre] = {"cantidad": int(resumen["count"]), "promedio": redondear(resumen["mean"]), "desviacion": redondear(resumen["std"]),
                                 "minimo": redondear(resumen["min"]), "mediana": redondear(serie.median()), "maximo": redondear(resumen["max"])}
        return resultado

    def histograma_edades(self):
        edades = self._mascotas_unicas()["edad"].dropna().to_numpy()
        if len(edades) == 0:
            return []
        limite = int(np.ceil(edades.max() / 2) * 2) + 2
        cantidades, bordes = np.histogram(edades, bins=np.arange(0, limite + 1, 2))   # numpy: histogram
        return [{"rango": f"{int(bordes[i])}-{int(bordes[i + 1])}", "cantidad": int(cantidades[i])} for i in range(len(cantidades))]

    def boxplot_precio_por_servicio(self):
        resultado = []
        for servicio, grupo in self.datos.groupby("servicio"):
            q1, mediana, q3 = np.percentile(grupo["precio"], [25, 50, 75])
            resultado.append({"servicio": servicio, "minimo": redondear(grupo["precio"].min()), "q1": redondear(q1), "mediana": redondear(mediana),
                              "q3": redondear(q3), "maximo": redondear(grupo["precio"].max()), "citas": len(grupo)})
        return resultado

    def conclusiones(self):
        if self.datos.empty:
            return ["No hay citas con los filtros seleccionados."]
        frases = []
        total = len(self.datos)

        perros_gatos = self.datos["especie"].isin(["Perro", "Gato"]).sum()
        frases.append(f"Perros y gatos son el {perros_gatos / total * 100:.1f}% de las citas.")

        mes_top = self.datos["mes"].value_counts().idxmax()
        frases.append(f"El mes con más citas es {MESES[mes_top - 1]} ({int((self.datos['mes'] == mes_top).sum())} citas).")

        canceladas = self.datos[self.datos["estado"] == "Cancelada"]
        if not canceladas.empty:
            dia_top = canceladas["dia_semana"].value_counts().idxmax()
            frases.append(f"El día con más cancelaciones es el {DIAS[dia_top]} ({int((canceladas['dia_semana'] == dia_top).sum())} citas canceladas).")

        servicio_top = self.datos["servicio"].value_counts().idxmax()
        frases.append(f"El servicio más solicitado es {servicio_top}.")

        completadas = (self.datos["estado"] == "Completada").sum()
        frases.append(f"El {completadas / total * 100:.1f}% de las citas se completó.")
        return frases

    def tabla(self):
        filas = self.datos.sort_values(["fecha", "hora"], ascending=False)
        resultado = []
        for _, fila in filas.iterrows():
            resultado.append({"id": int(fila["id"]), "fecha": fila["fecha"].strftime("%Y-%m-%d"), "hora": fila["hora"], "mascota": fila["mascota"],
                              "especie": fila["especie"], "servicio": fila["servicio"], "precio": redondear(fila["precio"]),
                              "veterinario": fila["veterinario"], "estado": fila["estado"]})
        return resultado

    def opciones(self):
        meses = sorted(self.datos["mes"].unique())
        return {"especies": sorted(self.datos["especie"].dropna().unique()), "servicios": sorted(self.datos["servicio"].dropna().unique()),
                "meses": [{"valor": int(mes), "nombre": MESES[mes - 1]} for mes in meses]}


# POO: herencia, AnalizadorFiltrado hereda todo lo de AnalizadorClinica
class AnalizadorFiltrado(AnalizadorClinica):
    def __init__(self, especie=None, servicio=None, mes=None):
        super().__init__()
        if especie:
            self.datos = self.datos[self.datos["especie"] == especie]
        if servicio:
            self.datos = self.datos[self.datos["servicio"] == servicio]
        if mes:
            self.datos = self.datos[self.datos["mes"] == mes]
