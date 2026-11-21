"""Genera datasets ficticios deterministas y relacionados para VetCare.

Conserva los registros ya existentes de cada JSON como una base y los amplía.
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
pet_names = ["Canela","Thor","Mía","Zeus","Sasha","Rocco","Pelusa","Dante","Maya","Apolo","Nina","Balú","Cira","Benji","Mora","Gaia","Otto","Lía","Rex","Frida","Paco","Noa","Bowie","Uma","Sam","Arya","Doki","Greta","Polo","Vera","Leo","Suki","Chester","Tina","Boris","Maggie","Pipo","Duna","Teo","Rita","Koda","Ayla","Momo","Runa","Chispa","Kenzo","Pepa"]
species = [("Perro","Mestizo"),("Gato","Mestizo"),("Perro","Bulldog francés"),("Gato","Angora"),("Perro","Schnauzer"),("Gato","Bengalí"),("Perro","Dachshund"),("Conejo","Mini Lop"),("Perro","Yorkshire Terrier")]
for i in range(len(mascotas), 270):
    especie, raza = species[i % len(species)]
    nombre = pet_names[i % len(pet_names)] + (" II" if i >= 120 else "")
    mascotas.append({"cliente_dni": clientes[i % len(clientes)]["dni"], "nombre":nombre, "especie":especie, "raza":raza, "sexo":"Hembra" if i % 2 else "Macho", "fecha_nacimiento":str(date(2018 + i % 8, 1 + i % 12, 1 + i % 27)), "peso":round(1.5 + (i % 35) * 0.9, 1), "color":["Negro","Blanco","Marrón","Atigrado","Dorado","Gris"][i % 6], "observaciones":"Registro ficticio para pruebas de VetCare."})

def ref(index, vet_index):
    pet = mascotas[index % len(mascotas)]
    return {"cliente_dni":pet["cliente_dni"],"mascota_nombre":pet["nombre"],"veterinario_dni":veterinarios[vet_index % len(veterinarios)]["dni"]}

citas = read("citas")[:15]
inicio = date(2026, 11, 1)
horas = ["08:00","08:30","09:00","09:30","10:00","10:30","11:00","11:30"]
estados = ["Pendiente","Confirmada","En atención","Completada","Cancelada"]
for i in range(15, 180):
    data = ref(i, i)
    data.update({"servicio_nombre":servicios[i % len(servicios)]["nombre"],"fecha":str(inicio + timedelta(days=i // 8)),"hora":horas[i % len(horas)],"motivo":["Control preventivo","Vacunación programada","Revisión general","Seguimiento de tratamiento","Consulta de bienestar"][i % 5],"observaciones":"Cita ficticia generada para pruebas.","estado":estados[i % len(estados)]})
    citas.append(data)

historial = read("historial")[:12]
for i in range(12, 150):
    data = ref(i + 20, i)
    data.update({"fecha_atencion":str(date(2026, 1, 1) + timedelta(days=i * 3)),"motivo_consulta":["Control preventivo","Revisión de piel","Consulta digestiva","Control de peso","Chequeo anual"][i % 5],"diagnostico":["Paciente estable","Dermatitis leve","Gastritis leve","Sobrepeso leve","Sin hallazgos clínicos"][i % 5],"tratamiento":"Indicaciones y control según evolución.","observaciones":"Historia clínica ficticia para pruebas."})
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
