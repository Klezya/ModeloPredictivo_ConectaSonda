from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
import random

app = FastAPI(
    title="ConectaSonda API",
    description="API para el Sistema Predictivo de Fallas - Torniquetes y Transbank",
    version="1.0.0"
)

# CORS para conectar con el frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
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
    failure_type: str
    resolved: bool

class MaintenanceRequest(BaseModel):
    equipment_id: int
    scheduled_date: str
    maintenance_type: str
    notes: Optional[str] = None

# ============== DATOS SIMULADOS ==============

equipments_db = [
    {"id": 1, "name": "Torniquete T-001", "type": "torniquete", "location": "Estación Central - Acceso Norte", "status": "operativo", "last_maintenance": "2024-11-15", "last_failure": "2024-11-20", "failure_count": 3, "uptime": 98.5},
    {"id": 2, "name": "Torniquete T-002", "type": "torniquete", "location": "Estación Central - Acceso Sur", "status": "operativo", "last_maintenance": "2024-11-20", "last_failure": "2024-12-01", "failure_count": 1, "uptime": 99.2},
    {"id": 3, "name": "Transbank TB-001", "type": "transbank", "location": "Estación Central - Hall Principal", "status": "falla", "last_maintenance": "2024-10-30", "last_failure": "2024-12-04", "failure_count": 5, "uptime": 94.1},
    {"id": 4, "name": "Torniquete T-003", "type": "torniquete", "location": "Estación Los Héroes - Acceso Este", "status": "mantenimiento", "last_maintenance": "2024-12-04", "last_failure": "2024-11-15", "failure_count": 2, "uptime": 97.8},
    {"id": 5, "name": "Transbank TB-002", "type": "transbank", "location": "Estación Los Héroes - Boletería", "status": "operativo", "last_maintenance": "2024-11-25", "last_failure": "2024-10-28", "failure_count": 2, "uptime": 96.5},
    {"id": 6, "name": "Torniquete T-004", "type": "torniquete", "location": "Estación Baquedano - Acceso Principal", "status": "operativo", "last_maintenance": "2024-11-28", "last_failure": "2024-11-30", "failure_count": 1, "uptime": 99.0},
    {"id": 7, "name": "Transbank TB-003", "type": "transbank", "location": "Estación Baquedano - Autoservicio", "status": "operativo", "last_maintenance": "2024-11-10", "last_failure": "2024-11-10", "failure_count": 4, "uptime": 95.3},
    {"id": 8, "name": "Torniquete T-005", "type": "torniquete", "location": "Estación Tobalaba - Acceso Oriente", "status": "falla", "last_maintenance": "2024-10-15", "last_failure": "2024-12-04", "failure_count": 6, "uptime": 92.1},
]

failures_history_db = [
    {"id": 1, "date": "2024-12-04", "equipment": "Transbank TB-001", "failure_type": "Lector de tarjetas", "resolved": False},
    {"id": 2, "date": "2024-12-04", "equipment": "Torniquete T-005", "failure_type": "Motor de giro", "resolved": False},
    {"id": 3, "date": "2024-12-03", "equipment": "Torniquete T-002", "failure_type": "Sensor de paso", "resolved": True},
    {"id": 4, "date": "2024-12-02", "equipment": "Transbank TB-003", "failure_type": "Pantalla táctil", "resolved": True},
    {"id": 5, "date": "2024-12-01", "equipment": "Torniquete T-001", "failure_type": "Brazo mecánico", "resolved": True},
    {"id": 6, "date": "2024-11-30", "equipment": "Torniquete T-004", "failure_type": "Lector BIP", "resolved": True},
]

# ============== ENDPOINTS ==============

@app.get("/")
def root():
    return {"message": "ConectaSonda API - Sistema Predictivo de Fallas para Torniquetes y Transbank"}

@app.get("/api/health")
def health_check():
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "services": {
            "api": "online",
            "ml_model": "online",
            "database": "online"
        }
    }

# Métricas del Dashboard
@app.get("/api/metrics", response_model=Metric)
def get_metrics():
    operativos = len([e for e in equipments_db if e["status"] == "operativo"])
    con_falla = len([e for e in equipments_db if e["status"] == "falla"])
    en_mantenimiento = len([e for e in equipments_db if e["status"] == "mantenimiento"])
    
    return {
        "total_equipments": len(equipments_db),
        "active_alerts": con_falla,
        "predicted_failures": con_falla + en_mantenimiento,
        "maintenance_scheduled": en_mantenimiento,
        "system_accuracy": 94.5,
        "avg_response_time": "96.8%"
    }

# Equipos
@app.get("/api/equipments", response_model=List[Equipment])
def get_equipments(equipment_type: Optional[str] = None):
    if equipment_type and equipment_type != "all":
        return [e for e in equipments_db if e["type"] == equipment_type]
    return equipments_db

@app.get("/api/equipments/{equipment_id}", response_model=Equipment)
def get_equipment(equipment_id: int):
    equipment = next((e for e in equipments_db if e["id"] == equipment_id), None)
    if not equipment:
        raise HTTPException(status_code=404, detail="Equipo no encontrado")
    return equipment

# Historial de Fallas
@app.get("/api/failures", response_model=List[FailureHistory])
def get_failures():
    return failures_history_db

# Resumen por Tipo
@app.get("/api/type-summary")
def get_type_summary():
    return {
        "torniquetes": len([e for e in equipments_db if e["type"] == "torniquete"]),
        "transbank": len([e for e in equipments_db if e["type"] == "transbank"]),
    }

# Resumen por Estado
@app.get("/api/status-summary")
def get_status_summary():
    return {
        "operativo": len([e for e in equipments_db if e["status"] == "operativo"]),
        "falla": len([e for e in equipments_db if e["status"] == "falla"]),
        "mantenimiento": len([e for e in equipments_db if e["status"] == "mantenimiento"]),
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
    equipment = next((e for e in equipments_db if e["id"] == equipment_id), None)
    if not equipment:
        raise HTTPException(status_code=404, detail="Equipo no encontrado")
    
    # Tipos de falla según el tipo de equipo
    if equipment["type"] == "torniquete":
        failure_types = [
            "Motor de giro",
            "Sensor de paso",
            "Brazo mecánico",
            "Lector BIP",
            "Placa controladora",
            "Sistema de bloqueo"
        ]
    else:  # transbank
        failure_types = [
            "Lector de tarjetas",
            "Pantalla táctil",
            "Impresora de boletas",
            "Conexión de red",
            "Teclado PIN",
            "Sistema de pago NFC"
        ]
    
    # Calcular probabilidad basada en historial
    base_probability = 100 - equipment["uptime"]
    probability = min(95, max(5, base_probability + random.randint(-10, 20)))
    
    return {
        "equipment_id": equipment_id,
        "equipment_name": equipment["name"],
        "probability": round(probability, 1),
        "risk_level": "alto" if probability > 70 else "medio" if probability > 40 else "bajo",
        "predicted_failure": random.choice(failure_types),
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

# Actualizar estado de equipo
@app.put("/api/equipments/{equipment_id}/status")
def update_equipment_status(equipment_id: int, status: str):
    equipment = next((e for e in equipments_db if e["id"] == equipment_id), None)
    if not equipment:
        raise HTTPException(status_code=404, detail="Equipo no encontrado")
    
    if status not in ["operativo", "falla", "mantenimiento"]:
        raise HTTPException(status_code=400, detail="Estado inválido")
    
    equipment["status"] = status
    return {"success": True, "message": f"Estado actualizado a {status}"}
