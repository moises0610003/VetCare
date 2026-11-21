from datetime import date, datetime
from flask import Blueprint, jsonify, request
from sqlalchemy.exc import IntegrityError
from sqlalchemy import or_, func
from app import db
from app.models import Cliente, Mascota, Veterinario, Servicio, Cita, HistorialClinico, Vacuna

api = Blueprint("api", __name__)
RESOURCES = {
 "clientes": (Cliente, ["nombres","apellidos","dni","telefono"]), "mascotas": (Mascota,["cliente_id","nombre","especie","sexo"]),
 "veterinarios": (Veterinario,["nombres","apellidos","dni","telefono","especialidad"]), "servicios": (Servicio,["nombre","precio","duracion_minutos"]),
 "citas": (Cita,["mascota_id","veterinario_id","servicio_id","fecha","hora","motivo"]), "historial": (HistorialClinico,["mascota_id","veterinario_id","fecha_atencion","motivo_consulta"]),
 "vacunas": (Vacuna,["mascota_id","nombre_vacuna","fecha_aplicacion"])}
DATE_FIELDS={"fecha","fecha_nacimiento","fecha_atencion","fecha_aplicacion","proxima_dosis"}; TIME_FIELDS={"hora"}
def serialize(obj):
    value=obj.to_dict()
    if hasattr(obj,"cliente") and obj.cliente: value["cliente_nombre"] = f"{obj.cliente.nombres} {obj.cliente.apellidos}"
    if hasattr(obj,"mascota") and obj.mascota: value["mascota_nombre"] = obj.mascota.nombre
    if hasattr(obj,"veterinario") and obj.veterinario: value["veterinario_nombre"] = f"{obj.veterinario.nombres} {obj.veterinario.apellidos}"
    if hasattr(obj,"servicio") and obj.servicio: value["servicio_nombre"] = obj.servicio.nombre
    return value
def clean(data):
    for k in DATE_FIELDS:
        if data.get(k): data[k]=datetime.strptime(data[k], "%Y-%m-%d").date()
    for k in TIME_FIELDS:
        if data.get(k): data[k]=datetime.strptime(data[k], "%H:%M").time()
    return data
def error(message, status=400): return jsonify(error=message),status
@api.route("/<resource>", methods=["GET","POST"])
def collection(resource):
    if resource not in RESOURCES: return error("Módulo no válido",404)
    Model, required=RESOURCES[resource]
    if request.method=="GET":
        query=Model.query
        term=request.args.get("buscar","").strip()
        if term:
            cols=[c for c in Model.__table__.columns if hasattr(c.type,"length") and c.type.length]
            query=query.filter(or_(*[c.ilike(f"%{term}%") for c in cols]))
        return jsonify(data=[serialize(x) for x in query.order_by(Model.id.desc()).all()])
    data=request.get_json(silent=True) or {}
    missing=[x for x in required if data.get(x) in (None,"")]
    if missing:return error("Campos obligatorios: "+", ".join(missing))
    try:
        entity=Model(**clean(data)); db.session.add(entity); db.session.commit(); return jsonify(data=serialize(entity),message="Registro creado"),201
    except (ValueError,TypeError): return error("Formato de fecha u hora inválido")
    except IntegrityError: db.session.rollback(); return error("El registro viola una restricción o está duplicado",409)
@api.route("/<resource>/<int:item_id>", methods=["GET","PUT","PATCH","DELETE"])
def item(resource,item_id):
    if resource not in RESOURCES:return error("Módulo no válido",404)
    Model,_=RESOURCES[resource]; entity=db.session.get(Model,item_id)
    if not entity:return error("Registro no encontrado",404)
    if request.method=="GET":return jsonify(data=serialize(entity))
    if request.method=="DELETE":
        try: db.session.delete(entity);db.session.commit();return jsonify(message="Registro eliminado")
        except IntegrityError:db.session.rollback();return error("No puede eliminarse porque tiene registros relacionados",409)
    try:
        for k,v in clean(request.get_json(silent=True) or {}).items():
            if hasattr(entity,k):setattr(entity,k,v)
        db.session.commit();return jsonify(data=serialize(entity),message="Registro actualizado")
    except (ValueError,TypeError):return error("Formato de fecha u hora inválido")
    except IntegrityError:db.session.rollback();return error("El registro viola una restricción o está duplicado",409)
@api.get("/dashboard")
def dashboard():
    today=date.today()
    citas=Cita.query.filter_by(fecha=today).all()
    inicio=today.fromordinal(today.toordinal()-6)
    por_dia=dict(db.session.query(Cita.fecha,func.count(Cita.id)).filter(Cita.fecha.between(inicio,today)).group_by(Cita.fecha).all())
    actividad_diaria=[{"fecha":str(inicio.fromordinal(inicio.toordinal()+offset)),"citas":por_dia.get(inicio.fromordinal(inicio.toordinal()+offset),0)} for offset in range(7)]
    por_estado=db.session.query(Cita.estado,func.count(Cita.id)).group_by(Cita.estado).all()
    estados=[{"estado":estado,"cantidad":cantidad} for estado,cantidad in por_estado]
    return jsonify(data={"totales":{"mascotas":Mascota.query.count(),"clientes":Cliente.query.count(),"citas_hoy":len(citas),"pendientes":Cita.query.filter(Cita.estado.in_(["Pendiente","Confirmada"])).count(),"completadas":Cita.query.filter_by(estado="Completada").count()},"proximas":[serialize(x) for x in Cita.query.filter(Cita.fecha>=today).order_by(Cita.fecha,Cita.hora).limit(8)],"actividad":[serialize(x) for x in Mascota.query.order_by(Mascota.creado_en.desc()).limit(5)],"actividad_diaria":actividad_diaria,"citas_por_estado":estados})
