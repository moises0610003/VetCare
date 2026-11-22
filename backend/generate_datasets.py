"""Genera datasets ficticios deterministas y relacionados para VetCare.

Conserva los registros ya existentes de cada JSON como una base y los amplía.
La semilla es fija, así que siempre genera exactamente los mismos datos.
Ejecutar: python generate_datasets.py
"""
import json
import random
from datetime import date, timedelta
from pathlib import Path

ROOT = Path(__file__).parent / "datasets"
random.seed(20261121)

def read(name):
    with (ROOT / f"{name}.json").open(encoding="utf-8") as file:
        return json.load(file)

def write(name, rows):
    with (ROOT / f"{name}.json").open("w", encoding="utf-8") as file:
        json.dump(rows, file, ensure_ascii=False, indent=2)
        file.write("\n")

clientes = read("clientes")[:15]
nombres = ["Adriana","Alonso","Beatriz","Carlos","Daniela","Esteban","Fernanda","Hugo","Isabel","Javier","Karina","Leonardo","Mariana","Nicolás","Patricia","Raúl","Sandra","Tomás","Úrsula","Víctor"]
apellidos = ["Acosta","Benavides","Cárdenas","Delgado","Espinoza","Fuentes","Guerrero","Huamán","Ibarra","Jiménez","Kuroki","López","Mendoza","Núñez","Ocampo","Peña","Quiroz","Rivas","Soto","Tello"]
for i in range(len(clientes), 180):
    clientes.append({"nombres": nombres[i % len(nombres)], "apellidos": apellidos[(i * 3) % len(apellidos)], "dni": f"8{i:07d}", "telefono": f"9{70000000+i:08d}", "correo": f"cliente{i+1}@example.test", "direccion": f"Calle Veterinaria {i + 20}, Lima"})

veterinarios = read("veterinarios")[:6]
for i, (nombre, apellido, especialidad) in enumerate([("Juliana","Soto","Cardiología"),("Emilio","Rivas","Medicina interna"),("Claudia","Paz","Oftalmología"),("Federico","Luna","Oncología"),("Mónica","Cano","Etología"),("Iván","Serrano","Animales exóticos"),("Rosa","Mendoza","Anestesiología"),("Pablo","Sánchez","Diagnóstico por imagen"),("Inés","Valdez","Medicina aviar")], 6):
    veterinarios.append({"nombres":nombre,"apellidos":apellido,"dni":f"40{i:06d}","telefono":f"988{i:06d}","correo":f"{nombre.lower()}@vetcare.test","especialidad":especialidad,"estado":"activo"})

servicios = read("servicios")[:8]
for nombre, descripcion, precio, minutos in [("Ecografía","Diagnóstico por imagen",180,45),("Radiografía","Estudio radiológico",150,30),("Hospitalización","Cuidado y monitoreo diario",120,1440),("Consulta nutricional","Plan alimenticio personalizado",85,30),("Corte de uñas","Higiene básica",25,15),("Microchip","Identificación permanente",90,20),("Control geriátrico","Chequeo integral senior",110,45),("Hemograma","Análisis de sangre completo",75,20),("Examen coproparasitario","Análisis de heces",45,15),("Control posoperatorio","Revisión después de cirugía",60,20),("Eutanasia humanitaria","Procedimiento con acompañamiento",200,45),("Certificado de salud","Evaluación para viaje",80,25)]:
    servicios.append({"nombre":nombre,"descripcion":descripcion,"precio":precio,"duracion_minutos":minutos,"estado":"activo"})

mascotas = read("mascotas")[:15]
nombres_mascota = ["Canela","Thor","Mía","Zeus","Sasha","Rocco","Pelusa","Dante","Maya","Apolo","Nina","Balú","Cira","Benji","Mora","Gaia","Otto","Lía","Rex","Frida","Paco","Noa","Bowie","Uma","Sam","Arya","Doki","Greta","Polo","Vera","Leo","Suki","Chester","Tina","Boris","Maggie","Pipo","Duna","Teo","Rita","Koda","Ayla","Momo","Runa","Chispa","Kenzo","Pepa","Abby","Bella","Blacky","Camila","Chiqui","Cleo","Copito","Dobby","Dulce","Eros","Estrella","Fido","Fiona","Galleta","Gringo","Hachi","Hera","Iker","Isis","Jack","Jazz","Kali","Kiko","Lassie","Lucas","Lupe","Mango","Manchas","Maki","Miel","Mishi","Nacho","Nube","Oreo","Osito","Pancho","Peke","Pluto","Princesa","Quila","Rambo","Rufo","Salem","Sombra","Tango","Tigre","Trufa","Violeta","Wendy","Yuki","Zoe","Zafiro","Aquiles","Bambi","Bruja","Canelo","Chocolate","Dálmata","Duque","Elsa","Flecha","Gala","Harley","Indie","Jade","Kira II","Lobo","Magnolia","Nemo","Olaf","Pantera","Piolín","Queso","Ron","Simón","Tobi","Vainilla","Xena","Yoda","Zorro","Alma","Brisa","Cometa","Delta","Fresa","Gordo"]
random.shuffle(nombres_mascota)
# (especie, raza, peso mínimo, peso máximo): perros y gatos son la mayoría
tipos_mascota = [("Perro","Mestizo",8,25),("Gato","Mestizo",3,6),("Perro","Bulldog francés",8,14),("Gato","Angora",3,6),("Perro","Schnauzer",5,12),("Gato","Bengalí",4,7),("Perro","Labrador",25,36),("Perro","Dachshund",5,10),("Gato","Siamés",3,5),("Perro","Yorkshire Terrier",2,4),("Perro","Pastor alemán",28,38),("Gato","Persa",3,6),("Perro","Poodle",4,9),("Conejo","Mini Lop",1.5,3),("Perro","Mestizo",10,30),("Gato","Mestizo",3,6),("Hámster","Sirio",0.1,0.2),("Ave","Canario",0.02,0.03),("Perro","Chihuahua",1.5,3.5),("Gato","Maine Coon",5,9)]
colores = ["Negro","Blanco","Marrón","Atigrado","Dorado","Gris","Canela","Tricolor","Crema"]
for i in range(len(mascotas), 270):
    especie, raza, peso_min, peso_max = tipos_mascota[random.randrange(len(tipos_mascota))]
    nacimiento = date(2013, 1, 1) + timedelta(days=random.randint(0, 4300))
    mascotas.append({"cliente_dni": clientes[i % len(clientes)]["dni"], "nombre":nombres_mascota[i % len(nombres_mascota)], "especie":especie, "raza":raza, "sexo":random.choice(["Macho","Hembra"]), "fecha_nacimiento":str(nacimiento), "peso":round(random.uniform(peso_min, peso_max), 1), "color":random.choice(colores), "observaciones":"Registro ficticio para pruebas de VetCare."})
# Datos sucios a propósito: unos pocos pesos vacíos (solo en mascotas generadas)
for pos in random.sample(range(15, len(mascotas)), 8):
    mascotas[pos]["peso"] = None

def ref(index, vet_index):
    pet = mascotas[index % len(mascotas)]
    return {"cliente_dni":pet["cliente_dni"],"mascota_nombre":pet["nombre"],"veterinario_dni":veterinarios[vet_index % len(veterinarios)]["dni"]}

# ---- Citas: enero a diciembre de 2026 (~600), con meses más cargados que otros ----
HOY = date(2026, 11, 21)
citas = read("citas")[:15]
horas = [f"{h:02d}:{m}" for h in list(range(8, 13)) + list(range(14, 18)) for m in ("00", "30")]
# (mes, día inicial, día final, cantidad): noviembre se parte en pasado, hoy y futuro
periodos = [(1,1,31,30),(2,1,28,33),(3,1,31,42),(4,1,30,40),(5,1,31,46),(6,1,30,38),(7,1,31,56),(8,1,31,60),(9,1,30,52),(10,1,31,62),(11,1,20,48),(11,21,21,4),(11,22,30,14),(12,1,31,60)]
motivos_por_servicio = {
    "Consulta general": ["Control preventivo","Revisión general","Consulta de bienestar","Pérdida de apetito","Decaimiento","Vómitos ocasionales","Cojera leve"],
    "Vacunación": ["Vacunación programada","Refuerzo anual","Primera dosis de cachorro","Vacuna antirrábica"],
    "Desparasitación": ["Desparasitación interna","Control de pulgas y garrapatas","Antiparasitario trimestral"],
    "Consulta dermatológica": ["Picazón persistente","Caída de pelo","Alergia en la piel","Heridas en la piel"],
    "Baño y peluquería": ["Baño medicado","Corte de pelo","Baño y corte de uñas"],
    "Emergencia": ["Intoxicación sospechosa","Golpe o caída","Dificultad para respirar","Convulsiones"],
    "Profilaxis dental": ["Sarro dental","Mal aliento","Limpieza dental anual"],
    "Cirugía menor": ["Extracción de quiste","Sutura de herida","Retiro de masa pequeña"],
}
motivos_generales = ["Control preventivo","Seguimiento de tratamiento","Revisión programada","Consulta solicitada por el dueño","Evaluación previa"]
# Más peso a los primeros servicios (consulta general, vacunación...) y poco a los especiales
pesos_servicio = [22,16,9,7,6,4,5,4] + [3,2,2,3,3,2,2,3,3,2,1,2]
dias_con_cita = set()          # (mascota, fecha): una mascota no tiene dos citas el mismo día
horarios_ocupados = set()      # (veterinario, fecha, hora): evita citas que choquen
for c in citas:
    horarios_ocupados.add((c["veterinario_dni"], c["fecha"], c["hora"]))
    dias_con_cita.add((c["cliente_dni"], c["mascota_nombre"], c["fecha"]))

nuevas = []
for mes, dia_ini, dia_fin, cantidad in periodos:
    for _ in range(cantidad):
        while True:
            dia = date(2026, mes, random.randint(dia_ini, dia_fin))
            if dia.weekday() == 6:      # la clínica no atiende los domingos
                continue
            mascota_elegida = mascotas[random.randrange(len(mascotas))]
            vet = veterinarios[random.randrange(len(veterinarios))]["dni"]
            hora = random.choice(horas)
            clave_mascota = (mascota_elegida["cliente_dni"], mascota_elegida["nombre"], str(dia))
            if (vet, str(dia), hora) in horarios_ocupados or clave_mascota in dias_con_cita:
                continue
            break
        horarios_ocupados.add((vet, str(dia), hora))
        dias_con_cita.add(clave_mascota)
        servicio = random.choices(servicios, weights=pesos_servicio)[0]["nombre"]
        motivo = random.choice(motivos_por_servicio.get(servicio, motivos_generales))
        nuevas.append({"cliente_dni":mascota_elegida["cliente_dni"],"mascota_nombre":mascota_elegida["nombre"],"veterinario_dni":vet,"servicio_nombre":servicio,"fecha":str(dia),"hora":hora,"motivo":motivo,"observaciones":"Cita ficticia generada para pruebas.","estado":""})

# Estados realistas: pasado = Completada (~85%) o Cancelada; hoy = en curso; futuro = Pendiente o Confirmada
pasadas = [c for c in nuevas if c["fecha"] < str(HOY)]
for c in nuevas:
    if c["fecha"] == str(HOY):
        c["estado"] = random.choice(["En atención","En atención","Confirmada","Pendiente"])
    elif c["fecha"] > str(HOY):
        dias_faltan = (date.fromisoformat(c["fecha"]) - HOY).days
        probabilidad_confirmada = 0.8 if dias_faltan <= 7 else 0.4 if dias_faltan <= 21 else 0.1
        c["estado"] = "Confirmada" if random.random() < probabilidad_confirmada else "Pendiente"
    else:
        c["estado"] = "Completada"
for c in random.sample(pasadas, 92):
    c["estado"] = "Cancelada"
nuevas.sort(key=lambda c: (c["fecha"], c["hora"]))
citas.extend(nuevas)

# Datos sucios a propósito: 3 citas registradas dos veces (misma mascota, día y servicio,
# pero con otro veterinario y otra hora, por eso MySQL no las rechaza)
for original in random.sample([c for c in nuevas if c["estado"] == "Completada"], 3):
    copia = original.copy()
    while True:
        vet = veterinarios[random.randrange(len(veterinarios))]["dni"]
        hora = random.choice(horas)
        if (vet, copia["fecha"], hora) not in horarios_ocupados:
            break
    horarios_ocupados.add((vet, copia["fecha"], hora))
    copia["veterinario_dni"], copia["hora"] = vet, hora
    citas.append(copia)

# ---- Historial clínico: más motivos y diagnósticos ----
clinicos = [
    ("Control preventivo","Paciente saludable","Control anual"),
    ("Revisión de piel","Dermatitis leve","Shampoo medicado y control en 15 días"),
    ("Consulta digestiva","Gastritis leve","Dieta blanda y protector gástrico"),
    ("Control de peso","Sobrepeso leve","Plan nutricional y ejercicio diario"),
    ("Chequeo anual","Sin hallazgos clínicos","Mantener rutina de vacunas"),
    ("Cojera en pata trasera","Esguince leve","Reposo y antiinflamatorio por 5 días"),
    ("Picazón en las orejas","Otitis externa","Limpieza y gotas óticas por 10 días"),
    ("Ojos con secreción","Conjuntivitis","Colirio antibiótico cada 8 horas"),
    ("Tos persistente","Traqueobronquitis","Antitusivo y reposo"),
    ("Diarrea de dos días","Parasitosis intestinal","Antiparasitario y probióticos"),
    ("Mal aliento","Sarro dental grado 2","Limpieza dental programada"),
    ("Pérdida de apetito","Estrés por cambio de casa","Observación y alimento palatable"),
    ("Alergia estacional","Rinitis alérgica","Antihistamínico por 7 días"),
    ("Herida en la almohadilla","Laceración superficial","Curación diaria y vendaje"),
    ("Vómitos repetidos","Indigestión por cambio de alimento","Ayuno corto y dieta suave"),
    ("Control geriátrico","Artrosis inicial","Suplemento articular"),
    ("Infección urinaria","Cistitis bacteriana","Antibiótico y mayor ingesta de agua"),
    ("Pulgas y rascado","Pulicosis","Pipeta antipulgas y limpieza del hogar"),
]
historial = read("historial")[:12]
usados = {(h["cliente_dni"], h["mascota_nombre"], h["fecha_atencion"], h["motivo_consulta"]) for h in historial}
while len(historial) < 150:
    data = ref(random.randrange(len(mascotas)), random.randrange(len(veterinarios)))
    motivo, diagnostico, tratamiento = random.choice(clinicos)
    fecha_atencion = str(date(2026, 1, 1) + timedelta(days=random.randint(0, (HOY - date(2026, 1, 1)).days)))
    clave = (data["cliente_dni"], data["mascota_nombre"], fecha_atencion, motivo)
    if clave in usados:
        continue
    usados.add(clave)
    data.update({"fecha_atencion":fecha_atencion,"motivo_consulta":motivo,"diagnostico":diagnostico,"tratamiento":tratamiento,"observaciones":"Historia clínica ficticia para pruebas."})
    historial.append(data)

vacunas = read("vacunas")[:16]
for i in range(16, 185):
    data = ref(i + 50, i)
    applied = date(2025 + i % 2, 1 + i % 12, 1 + i % 27)
    data.update({"nombre_vacuna":["Séxtuple canina","Antirrábica","Triple felina","Bordetella","Leucemia felina"][i % 5],"fecha_aplicacion":str(applied),"proxima_dosis":str(applied + timedelta(days=365)),"observaciones":"Vacuna ficticia registrada para pruebas."})
    vacunas.append(data)

for name, data in [("clientes",clientes),("veterinarios",veterinarios),("servicios",servicios),("mascotas",mascotas),("citas",citas),("historial",historial),("vacunas",vacunas)]:
    write(name, data)
    print(f"{name}: {len(data)} registros generados")
