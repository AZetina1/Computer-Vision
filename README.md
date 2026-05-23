# Proyecto 6: Computer Vision

#  Sistema de Control Biométrico

Este proyecto es un sistema local de reconocimiento facial y de voz. Utiliza una interfaz web (frontend) y un servidor en Python (backend) para registrar usuarios y verificar su identidad en tiempo real.

---

## Instalación y Uso Rápido

Ejecuta estos comandos en tu terminal dentro de la carpeta del proyecto:

### 1. Crear y activar el entorno virtual
* **Windows:**
  ```bash
  python -m venv venv
  .\venv\Scripts\activate

  #Instalar librerias
  pip install -r requirements.txt   


#Configurar el Frontend
  const BACKEND_URL = "[http://127.0.0.1:8000]";

#inicia el servidor

uvicorn main:app --reload --port 8000


##como usarlo

Abre el archivo indexRF.html en tu navegador (usa la extensión Live Server de VS Code).

Registro: Llena tus datos en la pestaña "Registro", mira a la cámara y presiona Registrar Credenciales (se guardarán en users_metadata.json).

Verificación: Cambia a la pestaña "Verificación" y mira a la cámara para que el sistema valide tu identidad.