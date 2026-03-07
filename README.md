# 🐱 Domoticat

Domoticat integra nodos IoT (ESP32) con una API REST para registrar, monitorear y cuidar a los gatos que habitan el campus. Combina dispensación automática de alimento, lectura de sensores ambientales, reconocimiento visual y seguimiento veterinario.

## 📁 Estructura del repositorio

```
domoticat/
├── main.py                    # API REST — todos los endpoints
├── requirements.txt           # Dependencias Python
├── .env.example               # Plantilla de variables de entorno
├── .gitignore                 # Excluye .env y archivos sensibles
│
└── docs/
    └── domoticat_erd.svg     # Diagrama Entidad-Relación (SVG)
```

## ⚙️ Instalación y configuración

### 1. Clonar el repositorio

```bash
git clone https://github.com//domoticat.git
cd domoticat
```

### 2. Crear y activar entorno virtual

```bash
python -m venv .venv
# Linux / macOS
source .venv/bin/activate
# Windows
.venv\Scripts\activate
```

### 3. Instalar dependencias

```bash
pip install -r requirements.txt
```

### 4. Configurar variables de entorno

```bash
cp .env.example .env
# Editar .env con los datos reales de la base de datos
```

> ⚠️ **El archivo `.env` no se sube al repositorio.** Ya está excluido en `.gitignore`.