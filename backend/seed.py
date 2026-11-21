"""Importa datasets ficticios a MySQL sin borrar ni duplicar datos."""
import json
from pathlib import Path
from sqlalchemy import func
from app import create_app, db
from app.models import Cliente, Veterinario, Servicio, Mascota, Cita, HistorialClinico, Vacuna
from app.routes.api import clean

DATASETS = Path(__file__).parent / "datasets"
MODELOS = {"clientes": Cliente, "veterinarios": Veterinario, "servicios": Servicio, "mascotas": Mascota, "citas": Cita, "historial_clinico": HistorialClinico, "vacunas": Vacuna}
app = create_app()

def rows(nombre):
    with (DATASETS / f"{nombre}.json").open(encoding="utf-8") as archivo:
        return json.load(archivo)

def require(valor, mensaje):
    if valor is None: raise ValueError(mensaje)
    return valor

def mascota(cliente_dni, nombre):
    cliente = require(Cliente.query.filter_by(dni=cliente_dni).first(), f"Cliente DNI {cliente_dni} no encontrado")
    return require(Mascota.query.filter_by(cliente_id=cliente.id, nombre=nombre).first(), f"Mascota {nombre} no encontrada")

def simple(nombre, modelo, clave):
    nuevos = 0
    for data in rows(nombre):
        if not modelo.query.filter_by(**{clave: data[clave]}).first():
            db.session.add(modelo(**clean(data.copy()))); nuevos += 1
    db.session.commit()
    return nuevos

def cargar_mascotas():
    nuevos = 0
    for registro in rows("mascotas"):
        data = registro.copy()
        cliente = require(Cliente.query.filter_by(dni=data.pop("cliente_dni")).first(), "Propietario no encontrado")
        if not Mascota.query.filter_by(cliente_id=cliente.id, nombre=data["nombre"]).first():
            db.session.add(Mascota(cliente_id=cliente.id, **clean(data))); nuevos += 1
    db.session.commit()
    return nuevos

def relacionados(registro, servicio=False):
    data = registro.copy()
    pet = mascota(data.pop("cliente_dni"), data.pop("mascota_nombre"))
    vet = require(Veterinario.query.filter_by(dni=data.pop("veterinario_dni")).first(), "Veterinario no encontrado")
    data["mascota_id"], data["veterinario_id"] = pet.id, vet.id
    if servicio:
        srv = require(Servicio.query.filter_by(nombre=data.pop("servicio_nombre")).first(), "Servicio no encontrado")
        data["servicio_id"] = srv.id
    return clean(data)

def cargar_citas():
    nuevos = 0
    for registro in rows("citas"):
        data = relacionados(registro, True)
        if not Cita.query.filter_by(veterinario_id=data["veterinario_id"], fecha=data["fecha"], hora=data["hora"]).first():
            db.session.add(Cita(**data)); nuevos += 1
    db.session.commit()
    return nuevos

def cargar_historial():
    nuevos = 0
    for registro in rows("historial"):
        data = relacionados(registro)
        if not HistorialClinico.query.filter_by(mascota_id=data["mascota_id"], fecha_atencion=data["fecha_atencion"], motivo_consulta=data["motivo_consulta"]).first():
            db.session.add(HistorialClinico(**data)); nuevos += 1
    db.session.commit()
    return nuevos

def cargar_vacunas():
    nuevos = 0
    for registro in rows("vacunas"):
        data = relacionados(registro)
        if not Vacuna.query.filter_by(mascota_id=data["mascota_id"], nombre_vacuna=data["nombre_vacuna"], fecha_aplicacion=data["fecha_aplicacion"]).first():
            db.session.add(Vacuna(**data)); nuevos += 1
    db.session.commit()
    return nuevos

with app.app_context():
    tareas = [("clientes", lambda: simple("clientes", Cliente, "dni")), ("veterinarios", lambda: simple("veterinarios", Veterinario, "dni")), ("servicios", lambda: simple("servicios", Servicio, "nombre")), ("mascotas", cargar_mascotas), ("citas", cargar_citas), ("historial_clinico", cargar_historial), ("vacunas", cargar_vacunas)]
    try:
        for tabla, tarea in tareas:
            print(f"{tabla}: {tarea()} insertados | total MySQL: {db.session.query(func.count()).select_from(MODELOS[tabla]).scalar()}")
        print("Importación terminada y relaciones verificadas.")
    except Exception as error:
        db.session.rollback()
        raise SystemExit(f"Importación cancelada: {error}")
