from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
# --- ✨ 1. AÑADE ESTOS IMPORTS ---
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
import datetime
import json
# -----------------------------------

import models
from database import engine # Asegúrate de que tu import de engine sea así
import trabajos
import auth
import dashboard
import tecnicos

models.Base.metadata.create_all(bind=engine)

# --- ✨ 2. CREA UNA CLASE PERSONALIZADA PARA CODIFICAR JSON ---
# Esta clase interceptará todas las respuestas y formateará las fechas correctamente.
class CustomJSONResponse(JSONResponse):
    def render(self, content: any) -> bytes:
        return json.dumps(
            content,
            ensure_ascii=False,
            allow_nan=False,
            indent=None,
            separators=(",", ":"),
            default=self.default_encoder, # Usamos un encoder personalizado
        ).encode("utf-8")

    def default_encoder(self, obj):
        if isinstance(obj, datetime.datetime):
            # Si el objeto es una fecha, lo convertimos a formato ISO 8601 con 'Z'
            # Ejemplo: '2025-10-18T01:12:00Z'
            # Si la fecha ya tiene zona horaria, la respeta
            if obj.tzinfo:
                return obj.isoformat()
            # Si no, asumimos que es UTC y la formateamos
            return obj.isoformat() + "Z"
        return jsonable_encoder(obj)
# -----------------------------------------------------------------

app = FastAPI(
    title="Taller Dashboard API",
    description="API para la gestión de procesos del taller mecánico.",
    version="0.1.0",
    default_response_class=CustomJSONResponse # <-- ✨ 3. USA LA CLASE PERSONALIZADA
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Se incluyen todos los routers
app.include_router(auth.router)
app.include_router(dashboard.router)
app.include_router(tecnicos.router)
app.include_router(trabajos.router)

@app.get("/")
def read_root():
    return {"status": "ok", "message": "El backend del taller está funcionando!"}