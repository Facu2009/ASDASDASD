# Backend Flask - API de Personas API REST para gestionar personas con Flask y SQLAlchemy.

## Requisitos

- Python 3.9+

## Instalación

### Entorno virtual con uv

```bash
# Crear entorno virtual
uv venv

# Activar entorno virtual
source .venv/bin/activate  # Linux/Mac
.venv\Scripts\activate     # Windows

# Instalar dependencias
uv pip install -r requirements.txt
```

### Entorno virtual con venv (alternativo)

```bash
# Crear entorno virtual
python -m venv .venv

# Activar entorno virtual
source .venv/bin/activate  # Linux/Mac
.venv\Scripts\activate     # Windows

# Instalar dependencias
pip install -r requirements.txt ```

## Ejecutar el servidor

```bash
python main.py
```

El servidor iniciara en `http://localhost:5000`

## Endpoints

| Método | Endpoint | Descripción |
|--------|----------|-------------|
| GET | `/api/personas` | Listar todas las personas |
| GET | `/api/personas/{id}` | Obtener una persona por ID |
| POST | `/api/personas` | Crear una nueva persona |
| PUT | `/api/personas/{id}` | Actualizar una persona (completo) |
| PATCH | `/api/personas/{id}` | Actualizar una persona (parcial) |
| DELETE | `/api/personas/{id}` | Eliminar una persona |

## Probar con VS Code

Abre el archivo `requests.http` y usa las extensiones REST Client o HTTP Client.