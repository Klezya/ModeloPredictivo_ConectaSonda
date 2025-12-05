const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'

export interface Equipment {
  id: number
  name: string
  type: string
  location: string
  status: string
  last_maintenance: string
  last_failure: string
  failure_count: number
  uptime: number
}

export interface Prediction {
  id: number
  equipment_id: number
  equipment_name: string
  location: string
  risk_level: string
  probability: number
  predicted_failure: string
  estimated_time: string
  status: string
}

export interface Metrics {
  total_equipments: number
  active_alerts: number
  predicted_failures: number
  maintenance_scheduled: number
  system_accuracy: number
  avg_response_time: string
}

export interface FailureHistory {
  id: number
  date: string
  equipment: string
  failure_type: string
  resolved: boolean
}

export interface TypeSummary {
  torniquetes: number
  transbank: number
}

export interface StatusSummary {
  operativo: number
  falla: number
  mantenimiento: number
}

export interface PredictionResult {
  equipment_id: number
  equipment_name: string
  probability: number
  risk_level: string
  predicted_failure: string
  confidence: number
  timestamp: string
}

class ApiService {
  private async request<T>(endpoint: string, options?: RequestInit): Promise<T> {
    const response = await fetch(`${API_BASE_URL}${endpoint}`, {
      headers: {
        'Content-Type': 'application/json',
      },
      ...options,
    })

    if (!response.ok) {
      throw new Error(`API Error: ${response.status}`)
    }

    return response.json()
  }

  // Health Check
  async healthCheck() {
    return this.request<{ status: string; services: Record<string, string> }>('/api/health')
  }

  // Métricas
  async getMetrics(): Promise<Metrics> {
    return this.request<Metrics>('/api/metrics')
  }

  // Equipos
  async getEquipments(): Promise<Equipment[]> {
    return this.request<Equipment[]>('/api/equipments')
  }

  async getEquipment(id: number): Promise<Equipment> {
    return this.request<Equipment>(`/api/equipments/${id}`)
  }

  // Predicciones
  async getPredictions(riskLevel?: string): Promise<Prediction[]> {
    const query = riskLevel && riskLevel !== 'all' ? `?risk_level=${riskLevel}` : ''
    return this.request<Prediction[]>(`/api/predictions${query}`)
  }

  async getPrediction(id: number): Promise<Prediction> {
    return this.request<Prediction>(`/api/predictions/${id}`)
  }

  // Historial de Fallas
  async getFailures(): Promise<FailureHistory[]> {
    return this.request<FailureHistory[]>('/api/failures')
  }

  // Resumen por Tipo
  async getTypeSummary(): Promise<TypeSummary> {
    return this.request<TypeSummary>('/api/type-summary')
  }

  // Resumen por Estado
  async getStatusSummary(): Promise<StatusSummary> {
    return this.request<StatusSummary>('/api/status-summary')
  }

  // Programar Mantenimiento
  async scheduleMaintenance(data: {
    equipment_id: number
    scheduled_date: string
    maintenance_type: string
    notes?: string
  }) {
    return this.request('/api/maintenance', {
      method: 'POST',
      body: JSON.stringify(data),
    })
  }

  // Ejecutar Predicción
  async runPrediction(equipmentId: number): Promise<PredictionResult> {
    return this.request<PredictionResult>(`/api/predict/${equipmentId}`, {
      method: 'POST',
    })
  }

  // Generar Reporte
  async generateReport(reportType: string = 'general') {
    return this.request(`/api/reports/generate?report_type=${reportType}`)
  }
}

export const apiService = new ApiService()