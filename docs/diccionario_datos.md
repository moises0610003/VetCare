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
| peso | número o vacío | Peso en kg con 2 decimales; hay 8 vacíos a propósito para practicar la limpieza |
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

## Columnas calculadas en el análisis

Estas columnas no están en los JSON; `analisis.py` las genera al unir las tablas con pandas.

| Columna | Tipo | Descripción |
|---|---|---|
| precio | número | Precio del servicio de la cita (viene de `servicios`) |
| mes | entero | Mes de la cita (1 a 12), sacado de `fecha` |
| dia_semana | entero | Día de la semana de la cita (0 = lunes) |
| edad | número | Edad de la mascota en años, calculada desde `fecha_nacimiento` |
| porcentaje | número | Porcentaje sobre el total, usado en diagnósticos, sexo, servicios e ingresos |

## Excel de carga

Es el archivo que se sube en la pantalla **Carga de datos**. Usa las mismas columnas que `mascotas.json` y `citas.json`; los nulos y los duplicados se limpian al subirlo.

**Hoja `mascotas`:** cliente_dni, nombre, especie, raza, sexo, fecha_nacimiento, peso, color, observaciones. Son obligatorios cliente_dni, nombre, especie y sexo (`Macho` o `Hembra`). El peso vacío se rellena con la mediana de la especie.

**Hoja `citas`:** cliente_dni, mascota_nombre, veterinario_dni, servicio_nombre, fecha, hora (`HH:MM`), motivo, observaciones, estado. El cliente, la mascota, el veterinario y el servicio deben existir ya en la base. Un estado vacío pasa a `Pendiente` y un motivo vacío a `Sin motivo registrado`.

