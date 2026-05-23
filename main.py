from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import base64
import os
import json
from deepface import DeepFace
import cv2
import numpy as np

app = FastAPI(title="Sistema de Autenticación Biométrica")

# 🛑 CONFIGURACIÓN DE CORS (Permite la comunicación sin bloqueos del navegador)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

DB_DIR = "face_db"
USER_DATA_FILE = "users_metadata.json"

# Asegurar existencia del directorio de la base de datos de rostros
if not os.path.exists(DB_DIR):
    os.makedirs(DB_DIR)

# --- MODELOS DE DATOS (Pydantic) ---
class RegisterRequest(BaseModel):
    username: str
    fullname: str
    rank: str
    image_base64: str

class LoginRequest(BaseModel):
    username: str
    image_base64: str

# --- GESTIÓN DE METADATOS LOCALES (JSON) ---
def load_metadata():
    if os.path.exists(USER_DATA_FILE):
        with open(USER_DATA_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}

def save_metadata(data):
    with open(USER_DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

def decode_base64_image(image_b64):
    try:
        if "," in image_b64:
            image_b64 = image_b64.split(",")[1]
        img_bytes = base64.b64decode(image_b64)
        np_arr = np.frombuffer(img_bytes, np.uint8)
        return cv2.imdecode(np_arr, cv2.IMREAD_COLOR)
    except Exception:
        raise HTTPException(status_code=400, detail="Error de procesamiento óptico.")

# --- ENDPOINTS DEL SISTEMA ---

# 🌐 Servidor del Frontend apuntando exactamente a indexRF.html
@app.get("/", response_class=HTMLResponse)
async def get_frontend():
    # 🔍 Vinculación exacta con el nombre de tu archivo en pantalla
    target_file = "indexRF.html"
    if os.path.exists(target_file):
        with open(target_file, "r", encoding="utf-8") as f:
            return f.read()
    return f"""
    <body style="background:#0f172a;color:#f1f5f9;font-family:sans-serif;padding:3rem;text-align:center;">
        <h2>⚠️ Archivo '{target_file}' no detectado en el directorio</h2>
        <p>Asegúrate de que el archivo esté exactamente en la carpeta 'Computer-Vision' junto a 'main.py'.</p>
    </body>
    """

# Registro Único de Credenciales con Grado Jerárquico
@app.post("/register")
async def register_face(data: RegisterRequest):
    metadata = load_metadata()
    
    if data.username in metadata:
        raise HTTPException(status_code=400, detail="El ID de Usuario ya existe.")
        
    img = decode_base64_image(data.image_base64)
    user_path = os.path.join(DB_DIR, f"{data.username}.jpg")
    cv2.imwrite(user_path, img)
    
    metadata[data.username] = {
        "fullname": data.fullname,
        "rank": data.rank
    }
    save_metadata(metadata)
    
    return {"status": "success", "message": f"Registro completado. {data.rank} añadido con éxito."}

# Validación Biométrica (Login)
@app.post("/verify")
async def verify_face(data: LoginRequest):
    metadata = load_metadata()
    user_path = os.path.join(DB_DIR, f"{data.username}.jpg")
    
    if data.username not in metadata or not os.path.exists(user_path):
        raise HTTPException(status_code=404, detail="ID credencial no encontrado.")
    
    current_img = decode_base64_image(data.image_base64)
    temp_path = f"temp_{data.username}.jpg"
    cv2.imwrite(temp_path, current_img)
    
    try:
        result = DeepFace.verify(
            img1_path=user_path, 
            img2_path=temp_path, 
            model_name="VGG-Face",
            enforce_detection=True
        )
        
        if os.path.exists(temp_path):
            os.remove(temp_path)
            
        if result["verified"]:
            return {
                "verified": True,
                "fullname": metadata[data.username]["fullname"],
                "rank": metadata[data.username]["rank"],
                "message": "Acceso Concedido."
            }
        else:
            return {"verified": False, "message": "Discrepancia de rasgos faciales."}
            
    except Exception:
        if os.path.exists(temp_path):
            os.remove(temp_path)
        raise HTTPException(status_code=422, detail="Rostro no encuadrado en el visor.")

# Endpoint de consulta para Plan B de Voz
@app.get("/user/{username}")
async def get_user(username: str):
    metadata = load_metadata()
    if username in metadata:
        return metadata[username]
    raise HTTPException(status_code=404, detail="Usuario no existente.")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)