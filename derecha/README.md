
sudo apt update
sudo apt install python3 python3-pip python3-venv -y
sudo snap install astral-uv --classic

```bash
# Crear entorno virtual
uv venv

# Activar entorno virtualc
source .venv/bin/activate  # Linux/Mac
.venv\Scripts\activate     # Windows

# Instalar dependencias
uv pip install -r requirements.txt
```
## Ejecutar el servidor
python main.py
