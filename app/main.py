from fastapi import FastAPI
from dotenv import load_dotenv
import os

# Cargar configuración desde las variables de entorno (.env)
load_dotenv()

app = FastAPI(
    title="API de Sistema de Agentes IA",
    description="Backend modular para controlar agentes, modelos y vistas de datos",
    version="1.0.0"
)

# Aquí normalmentes harías import de los "routers" desde los Endpoints
# Ejemplo: 
# from app.api.endpoints import agent_endpoints
# app.include_router(agent_endpoints.router, prefix="/api/v1")

@app.get("/")
def home_status():
    """ Health-check básico del entorno """
    env_name = os.getenv("ENVIRONMENT", "Desconocido")
    return {
        "status": "Online",
        "ambiente": env_name,
        "message": "Bienvenido al API del Sistema de Agentes."
    }

if __name__ == "__main__":
    import uvicorn
    # Se utiliza cuando se lanza el script directo (ej: python app/main.py)
    uvicorn.run(app, host="0.0.0.0", port=8000)
