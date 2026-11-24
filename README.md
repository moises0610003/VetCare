# VetCare

Sistema de gestión para clínica veterinaria: React/Vite en el frontend y Flask/SQLAlchemy conectado exclusivamente a MySQL.

## Requisitos (macOS)

- Node.js 20+ y npm
- Python 3.10+
- MySQL Server 8+ y MySQL Workbench

## Base de datos

1. Inicia MySQL Server.
2. Abre MySQL Workbench, conecta con tu servidor y abre [database/schema.sql](database/schema.sql).
3. Ejecuta el script completo; crea la base `veterinaria_db` con UTF-8 (`utf8mb4`).

## Backend

Desde la terminal integrada de VS Code:

```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
```

Edita `backend/.env` con tus credenciales locales de MySQL. No subas este archivo al repositorio.

```bash
python seed.py
python run.py
```

El importador usa datasets ficticios de `backend/datasets/`; se puede ejecutar varias veces sin duplicar los registros. La API queda disponible en `http://localhost:5000/api`.

## Frontend

En otra terminal:

```bash
npm install
npm run dev
```

Abre la dirección que indique Vite (normalmente `http://localhost:5173`). Si el backend usa otro host o puerto, crea un archivo `.env` en la raíz con:

```bash
VITE_API_URL=http://localhost:5000/api
```

## Comprobación rápida

1. Abre Dashboard: los contadores y próximas citas proceden de MySQL.
2. Registra un cliente, mascota, veterinario y servicio desde el menú.
3. Crea una cita; MySQL impide horarios duplicados para el mismo veterinario.
4. Prueba editar, buscar y eliminar. Cuando una relación evita el borrado, la API devuelve un mensaje explicativo.

## Endpoints

`/api/dashboard`, `/api/clientes`, `/api/mascotas`, `/api/veterinarios`, `/api/servicios`, `/api/citas`, `/api/historial` y `/api/vacunas` aceptan JSON y operaciones GET/POST; cada recurso individual acepta GET/PUT/PATCH/DELETE.

## Análisis de datos

La pantalla **Análisis** del menú lateral es un mini dashboard. Todos los cálculos se hacen en Python (`backend/app/analisis.py`) y el frontend solo los dibuja. Los endpoints son `GET /api/analisis` (acepta `?especie=&servicio=&mes=`) y `GET /api/analisis/opciones`. Las columnas de los datasets están en [docs/diccionario_datos.md](docs/diccionario_datos.md).

| Tema del curso | Dónde se usa |
|---|---|
| pandas | `pd.read_sql` y `merge` para unir citas, servicios, mascotas, veterinarios e historial clínico; `isna`, `drop_duplicates` y `to_datetime` en `limpieza()`; `value_counts`, `groupby` y `describe` en los métodos de análisis (ingresos, diagnósticos, mascotas, horarios y servicios) |
| numpy | `mean`, `std`, `min` y `max` en `estadisticas_precio()`; `histogram` para las edades y `percentile` para el boxplot de precio por especie |
| Programación funcional | `map`, `filter`, `lambda` y `reduce` en `kpis()`; `filter` y `lambda` también en `ingresos_por_mes()`; `aplicar_a_lista()` recibe otra función como parámetro |
| POO y herencia | `AnalizadorClinica` calcula todo; `AnalizadorFiltrado` hereda de ella y solo agrega los filtros |

La pantalla se divide en cinco secciones, cada una con su método en `AnalizadorClinica`:

| Sección | Método | Qué muestra |
|---|---|---|
| Ventas e ingresos | `ingresos_por_mes()`, `ingresos_por_servicio()` | Ingresos de las citas completadas, mes con más y con menos ingresos y % por servicio |
| Diagnósticos | `diagnosticos()` | Enfermedad más diagnosticada, casos con %, top 5 en perros y top 5 en gatos |
| Mascotas | `mascotas()` | Cantidad por especie, top 5 razas y distribución por sexo |
| Citas | `horarios_demanda()` | Citas por hora del día y promedio de citas por día |
| Servicios | `servicios()` | Ranking de servicios más y menos solicitados con % de demanda |

Después de cambiar los datasets, ejecuta `python generate_datasets.py` y luego `python seed.py`.

## Carga de datos desde Excel

El menú **Carga de datos** permite subir un Excel `.xlsx`. Python lo limpia con pandas y solo guarda en MySQL las filas buenas (`backend/app/carga.py`, clase `CargadorExcel`, endpoint `POST /api/carga`).

El Excel puede tener una hoja `mascotas` y/o una hoja `citas`, con las columnas que se describen en [docs/diccionario_datos.md](docs/diccionario_datos.md). Las dos hojas se limpian así:

| Paso | pandas | Qué hace |
|---|---|---|
| Contar nulos | `isna` | Muestra cuántos vacíos hay por columna |
| Convertir fechas | `to_datetime` | Pasa el texto a fecha; si no es válida queda vacía |
| Quitar duplicados | `duplicated` | Mascotas: mismo cliente y nombre. Citas: misma mascota, servicio y fecha |
| Rellenar nulos | `fillna` | Peso vacío: mediana de su especie. Cita sin estado: "Pendiente". Cita sin motivo: "Sin motivo registrado" |

Después de limpiar, una fila se omite (y se informa el motivo) si el cliente, la mascota, el veterinario o el servicio no existen, si el veterinario ya tiene una cita a esa fecha y hora, o si ya existe en la base. Si se vuelve a subir el mismo Excel no se duplica nada.

