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
| pandas | `pd.read_sql` y `merge` para unir citas, servicios, mascotas y veterinarios; `isna`, `drop_duplicates` y `to_datetime` en `limpieza()`; `value_counts`, `groupby` y `describe` en los métodos de análisis |
| numpy | `mean`, `std`, `min` y `max` en `estadisticas_precio()`; `histogram` para las edades y `percentile` para el boxplot de precio por especie |
| Programación funcional | `map`, `filter`, `lambda` y `reduce` en `kpis()`; `aplicar_a_lista()` recibe otra función como parámetro |
| POO y herencia | `AnalizadorClinica` calcula todo; `AnalizadorFiltrado` hereda de ella y solo agrega los filtros |

Después de cambiar los datasets, ejecuta `python generate_datasets.py` y luego `python seed.py`.

