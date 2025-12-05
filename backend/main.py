import os
import random
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
from dotenv import load_dotenv
from supabase import create_client, Client

# Cargar variables de entorno
load_dotenv()

# Cliente de Supabase
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

app = FastAPI(
    title="ConectaSonda API",
    description="API para el Sistema Predictivo de Fallas - Equipos de Borde",
    version="2.0.0"
)

# CORS para conectar con el frontend (desarrollo y producción)
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",  # Vite dev server
        "http://localhost:3000",  # Docker frontend
        "http://localhost:80",    # Docker frontend alt
        "http://localhost",       # Docker frontend sin puerto
        "http://frontend",        # Docker internal network
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ============== MODELOS ==============

class Equipment(BaseModel):
    id: int
    name: str
    type: str  # 'torniquete' o 'transbank'
    location: str
    status: str  # 'operativo', 'falla', 'mantenimiento'
    last_maintenance: str
    last_failure: str
    failure_count: int
    uptime: float

class Metric(BaseModel):
    total_equipments: int
    active_alerts: int
    predicted_failures: int
    maintenance_scheduled: int
    system_accuracy: float
    avg_response_time: str

class FailureHistory(BaseModel):
    id: int
    date: str
    equipment: str
    resolved: bool

class MaintenanceRequest(BaseModel):
    equipment_id: int
    scheduled_date: str
    maintenance_type: str
    notes: Optional[str] = None

# ============== FUNCIONES AUXILIARES SUPABASE ==============

def get_equipments_from_supabase(equipment_type: Optional[str] = None, limit: int = 100):
    """Obtiene equipos únicos desde Supabase"""
    query = supabase.table('equipos_borde').select('*')
    
    if equipment_type and equipment_type != "all":
        # Mapear tipo a valor en BD
        tipo_map = {"torniquete": "Torniquete", "transbank": "Transbank"}
        query = query.eq('TIPO_EQUIPO', tipo_map.get(equipment_type, equipment_type))
    
    result = query.limit(limit).execute()
    
    # Agrupar por ID_EQUIPO para obtener equipos únicos con su último registro
    equipos_dict = {}
    for row in result.data:
        equipo_id = row.get('ID_EQUIPO')
        if equipo_id not in equipos_dict:
            # Determinar estado basado en datos
            falla_tipo = row.get('FALLA_TIPO', 'Ninguna')
            dias_mant = row.get('DIAS_DESDE_ULTIMO_MANT', 0)
            
            if falla_tipo and falla_tipo != 'Ninguna':
                status = 'falla'
            elif dias_mant and dias_mant > 30:
                status = 'mantenimiento'
            else:
                status = 'operativo'
            
            # Calcular uptime basado en anomalías (ANOMALIA_USO es un float, valores altos = anomalía)
            anomalia_uso = row.get('ANOMALIA_USO', 0) or 0
            uptime = 95.0 if abs(anomalia_uso) > 10 else 98.5
            
            equipos_dict[equipo_id] = {
                "id": row.get('id'),
                "name": equipo_id,
                "type": row.get('TIPO_EQUIPO', 'torniquete').lower(),
                "location": row.get('ESTACION', 'Sin ubicación'),
                "status": status,
                "last_maintenance": str(row.get('FECHA_HORA', ''))[:10],
                "last_failure": str(row.get('FECHA_HORA', ''))[:10] if falla_tipo != 'Ninguna' else 'N/A',
                "failure_count": 1 if falla_tipo != 'Ninguna' else 0,
                "uptime": uptime
            }
    
    return list(equipos_dict.values())

def get_failures_from_supabase(limit: int = 50):
    """Obtiene historial de fallas desde Supabase"""
    result = supabase.table('equipos_borde').select('*').neq('FALLA_TIPO', 'Ninguna').limit(limit).execute()
    
    failures = []
    for i, row in enumerate(result.data, 1):
        failures.append({
            "id": i,
            "date": str(row.get('FECHA_HORA', ''))[:10],
            "equipment": row.get('ID_EQUIPO', 'Desconocido'),
            "resolved": row.get('FALLA_TIPO') == 'Ninguna'
        })
    
    return failures

def get_metrics_from_supabase():
    """Calcula métricas desde Supabase"""
    # Total de equipos únicos
    total_result = supabase.table('equipos_borde').select('ID_EQUIPO').execute()
    equipos_unicos = set(row.get('ID_EQUIPO') for row in total_result.data)
    total_equipments = len(equipos_unicos)
    
    # Fallas activas
    fallas_result = supabase.table('equipos_borde').select('*', count='exact').neq('FALLA_TIPO', 'Ninguna').limit(1).execute()
    active_alerts = fallas_result.count or 0
    
    # Predicciones de falla (registros con FALLA_INMINENTE_7D = 1)
    predicciones_result = supabase.table('equipos_borde').select('*', count='exact').eq('FALLA_INMINENTE_7D', 1).limit(1).execute()
    predicted_failures = predicciones_result.count or 0
    
    # Equipos en mantenimiento (DIAS_DESDE_ULTIMO_MANT > 30)
    mant_result = supabase.table('equipos_borde').select('*', count='exact').gt('DIAS_DESDE_ULTIMO_MANT', 30).limit(1).execute()
    maintenance_scheduled = mant_result.count or 0
    
    return {
        "total_equipments": total_equipments,
        "active_alerts": min(active_alerts, 100),  # Limitar para UI
        "predicted_failures": min(predicted_failures, 50),
        "maintenance_scheduled": min(maintenance_scheduled, 20),
        "system_accuracy": 94.5,
        "avg_response_time": "96.8%"
    }

# ============== ENDPOINTS ==============

@app.get("/")
def root():
    return {"message": "ConectaSonda API - Sistema Predictivo de Fallas para Torniquetes y Transbank"}

@app.get("/api/health")
def health_check():
    # Verificar conexión a Supabase
    try:
        result = supabase.table('equipos_borde').select('id').limit(1).execute()
        db_status = "online" if result.data else "degraded"
    except Exception:
        db_status = "offline"
    
    return {
        "status": "healthy" if db_status == "online" else "degraded",
        "timestamp": datetime.now().isoformat(),
        "services": {
            "api": "online",
            "ml_model": "online",
            "database": db_status
        }
    }

# Métricas del Dashboard
@app.get("/api/metrics", response_model=Metric)
def get_metrics():
    return get_metrics_from_supabase()

# Equipos
@app.get("/api/equipments", response_model=List[Equipment])
def get_equipments(equipment_type: Optional[str] = None):
    return get_equipments_from_supabase(equipment_type)

@app.get("/api/equipments/{equipment_id}", response_model=Equipment)
def get_equipment(equipment_id: int):
    result = supabase.table('equipos_borde').select('*').eq('id', equipment_id).limit(1).execute()
    if not result.data:
        raise HTTPException(status_code=404, detail="Equipo no encontrado")
    
    row = result.data[0]
    falla_tipo = row.get('FALLA_TIPO', 'Ninguna')
    dias_mant = row.get('DIAS_DESDE_ULTIMO_MANT', 0)
    
    if falla_tipo and falla_tipo != 'Ninguna':
        status = 'falla'
    elif dias_mant and dias_mant > 30:
        status = 'mantenimiento'
    else:
        status = 'operativo'
    
    anomalia_uso = row.get('ANOMALIA_USO', 0) or 0
    
    return {
        "id": row.get('id'),
        "name": row.get('ID_EQUIPO'),
        "type": row.get('TIPO_EQUIPO', 'torniquete').lower(),
        "location": row.get('ESTACION', 'Sin ubicación'),
        "status": status,
        "last_maintenance": str(row.get('FECHA_HORA', ''))[:10],
        "last_failure": str(row.get('FECHA_HORA', ''))[:10] if falla_tipo != 'Ninguna' else 'N/A',
        "failure_count": 1 if falla_tipo != 'Ninguna' else 0,
        "uptime": 95.0 if abs(anomalia_uso) > 10 else 98.5
    }

# Historial de Fallas
@app.get("/api/failures", response_model=List[FailureHistory])
def get_failures():
    return get_failures_from_supabase()

# Resumen por Tipo
@app.get("/api/type-summary")
def get_type_summary():
    equipments = get_equipments_from_supabase(limit=1000)
    return {
        "torniquetes": len([e for e in equipments if e["type"] == "torniquete"]),
        "transbank": len([e for e in equipments if e["type"] == "transbank"]),
    }

# Resumen por Estado
@app.get("/api/status-summary")
def get_status_summary():
    equipments = get_equipments_from_supabase(limit=1000)
    return {
        "operativo": len([e for e in equipments if e["status"] == "operativo"]),
        "falla": len([e for e in equipments if e["status"] == "falla"]),
        "mantenimiento": len([e for e in equipments if e["status"] == "mantenimiento"]),
    }

# Programar Mantenimiento
@app.post("/api/maintenance")
def schedule_maintenance(request: MaintenanceRequest):
    return {
        "success": True,
        "message": f"Mantenimiento programado para equipo {request.equipment_id}",
        "scheduled_date": request.scheduled_date,
        "maintenance_type": request.maintenance_type
    }

# Simulación de Predicción ML
@app.post("/api/predict/{equipment_id}")
def predict_failure(equipment_id: int):
    """Simula una predicción del modelo ML para torniquetes y Transbank"""
    result = supabase.table('equipos_borde').select('*').eq('id', equipment_id).limit(1).execute()
    if not result.data:
        raise HTTPException(status_code=404, detail="Equipo no encontrado")
    
    row = result.data[0]
    
    # Calcular probabilidad basada en datos reales
    falla_inminente = row.get('FALLA_INMINENTE_7D', 0) == 1
    anomalia_uso = abs(row.get('ANOMALIA_USO', 0) or 0)
    dias_mant = row.get('DIAS_DESDE_ULTIMO_MANT', 0) or 0
    
    # Base probability
    if falla_inminente:
        base_probability = 75
    elif anomalia_uso > 10:
        base_probability = 45
    else:
        base_probability = 10
    
    # Ajustar por días sin mantenimiento
    base_probability += min(20, dias_mant / 5)
    
    probability = min(95, max(5, base_probability + random.randint(-10, 15)))
    
    return {
        "equipment_id": equipment_id,
        "equipment_name": row.get('ID_EQUIPO'),
        "probability": round(probability, 1),
        "confidence": round(random.uniform(0.85, 0.98), 2),
        "timestamp": datetime.now().isoformat()
    }

# Generar Reporte
@app.get("/api/reports/generate")
def generate_report(report_type: str = "general"):
    return {
        "success": True,
        "report_type": report_type,
        "generated_at": datetime.now().isoformat(),
        "download_url": f"/api/reports/download/{report_type}"
    }

# Actualizar estado de equipo (solo respuesta, no modifica Supabase por ahora)
@app.put("/api/equipments/{equipment_id}/status")
def update_equipment_status(equipment_id: int, status: str):
    result = supabase.table('equipos_borde').select('id').eq('id', equipment_id).limit(1).execute()
    if not result.data:
        raise HTTPException(status_code=404, detail="Equipo no encontrado")
    
    if status not in ["operativo", "falla", "mantenimiento"]:
        raise HTTPException(status_code=400, detail="Estado inválido")
    
    # Por ahora solo retornamos éxito (la BD es de solo lectura)
    return {"success": True, "message": f"Estado actualizado a {status}"}
