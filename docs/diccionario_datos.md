# Diccionario de datos

Describe las columnas de cada archivo de `backend/datasets/`. Los archivos se generan con `python generate_datasets.py` (semilla fija) y se cargan a MySQL con `python seed.py`. Las fechas van como `AAAA-MM-DD` y las horas como `HH:MM`.

## clientes.json (180 registros)

| Columna | Tipo | Descripción |
|---|---|---|
| nombres | texto | Nombres del dueño |
| apellidos | texto | Apellidos del dueño |
| dni | texto | Documento de identidad (único) |
| telefono | texto | Teléfono de contacto |
| correo | texto | Correo electrónico |
| direccion | texto | Dirección del dueño |

## veterinarios.json (15 registros)

| Columna | Tipo | Descripción |
|---|---|---|
| nombres | texto | Nombres del veterinario |
| apellidos | texto | Apellidos del veterinario |
| dni | texto | Documento de identidad (único) |
| telefono | texto | Teléfono de contacto |
| correo | texto | Correo electrónico |
| especialidad | texto | Especialidad médica |
| estado | texto | `activo` o `inactivo` |

## servicios.json (20 registros)

| Columna | Tipo | Descripción |
|---|---|---|
| nombre | texto | Nombre del servicio (único) |
| descripcion | texto | Qué incluye el servicio |
| precio | número | Precio en soles (S/) |
| duracion_minutos | entero | Duración aproximada |
| estado | texto | `activo` o `inactivo` |

## mascotas.json (270 registros)

| Columna | Tipo | Descripción |
|---|---|---|
| cliente_dni | texto | DNI del dueño (relaciona con `clientes`) |
| nombre | texto | Nombre de la mascota |
| especie | texto | Perro, Gato, Conejo, Hámster o Ave |
| raza | texto | Raza o tipo |
| sexo | texto | `Macho` o `Hembra` |
| fecha_nacimiento | fecha | Sirve para calcular la edad |
| peso | número o vacío | Peso en kg; hay 8 vacíos a propósito para practicar la limpieza |
| color | texto | Color del pelaje o plumaje |
| observaciones | texto | Notas libres |

## citas.json (603 registros)

| Columna | Tipo | Descripción |
|---|---|---|
| cliente_dni | texto | DNI del dueño (junto con `mascota_nombre` identifica a la mascota) |
| mascota_nombre | texto | Nombre de la mascota atendida |
| veterinario_dni | texto | DNI del veterinario (relaciona con `veterinarios`) |
| servicio_nombre | texto | Servicio solicitado (relaciona con `servicios`) |
| fecha | fecha | Día de la cita, entre enero y diciembre de 2026 |
| hora | hora | Hora de la cita; un veterinario no repite fecha y hora |
| motivo | texto | Motivo de la consulta |
| observaciones | texto | Notas libres |
| estado | texto | `Pendiente`, `Confirmada`, `En atención`, `Completada` o `Cancelada` |

Datos sucios a propósito: 3 citas aparecen dos veces (misma mascota, día y servicio, con otra hora y otro veterinario). Se eliminan en `limpieza()` del análisis.

## historial.json (150 registros)

| Columna | Tipo | Descripción |
|---|---|---|
| cliente_dni | texto | DNI del dueño |
| mascota_nombre | texto | Nombre de la mascota atendida |
| veterinario_dni | texto | DNI del veterinario que atendió |
| fecha_atencion | fecha | Día de la atención |
| motivo_consulta | texto | Por qué se consultó |
| diagnostico | texto | Diagnóstico del veterinario |
| tratamiento | texto | Tratamiento indicado |
| observaciones | texto | Notas libres |

## vacunas.json (185 registros)

| Columna | Tipo | Descripción |
|---|---|---|
| cliente_dni | texto | DNI del dueño |
| mascota_nombre | texto | Nombre de la mascota vacunada |
| veterinario_dni | texto | DNI del veterinario que aplicó la vacuna |
| nombre_vacuna | texto | Nombre de la vacuna |
| fecha_aplicacion | fecha | Día de la aplicación |
| proxima_dosis | fecha | Fecha del siguiente refuerzo |
| observaciones | texto | Notas libres |
