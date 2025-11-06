# Frontend - Tkinter Custom

## Ejecución

### Opción 1: Desde dentro del directorio frontend (recomendado)
```bash
cd frontend
python main.py
```

### Opción 2: Desde la raíz del proyecto
```bash
# Desde la raíz del proyecto
python -m frontend.main
```

### Opción 3: Ejecutar directamente ui_main.py
```bash
cd frontend
python ui_main.py
```

## Instalación

```bash
pip install -r frontend/requirements.txt
```

## Requisitos

**IMPORTANTE:** El backend debe estar ejecutándose antes de iniciar el frontend.

1. Inicia el backend primero:
```bash
cd backend
python main.py
```

2. Luego inicia el frontend:
```bash
cd frontend
python main.py
```

## Configuración

Si el backend está corriendo en un puerto diferente, edita `api_client.py`:

```python
self.api_client = APIClient(base_url="http://127.0.0.1:8001")  # Cambiar puerto si es necesario
```

## Credenciales por Defecto

- **Usuario:** `admin`
- **Contraseña:** `admin123`

⚠️ **IMPORTANTE:** Cambiar la contraseña después del primer inicio de sesión.

