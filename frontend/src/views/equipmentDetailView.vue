<!-- filepath: frontend/src/views/EquipmentDetailView.vue -->
<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { apiService, type Equipment } from '@/services/api'

const route = useRoute()
const router = useRouter()

const equipment = ref<Equipment | null>(null)
const isLoading = ref(true)
const error = ref('')
const showMaintenanceModal = ref(false)
const predictionResult = ref<{
  probability: number
  confidence: number
} | null>(null)

const maintenanceForm = ref({
  scheduled_date: '',
  maintenance_type: 'preventivo',
  notes: ''
})

const loadData = async () => {
  try {
    isLoading.value = true
    error.value = ''
    const id = Number(route.params.id)
    equipment.value = await apiService.getEquipment(id)
  } catch (err) {
    console.error('Error loading data:', err)
    error.value = 'Error al cargar los datos del equipo'
    // Datos de demostración
    equipment.value = {
      id: Number(route.params.id),
      name: 'Torniquete T-001',
      type: 'torniquete',
      location: 'Estación Central - Acceso Norte',
      status: 'operativo',
      last_maintenance: '2024-11-15',
      last_failure: '2024-11-20',
      failure_count: 3,
      uptime: 98.5
    }
  } finally {
    isLoading.value = false
  }
}

const equipmentTypeLabel = computed(() => {
  if (!equipment.value) return ''
  return equipment.value.type === 'torniquete' ? 'Torniquete' : 'Transbank'
})

const getStatusClass = (status: string) => {
  const classes: Record<string, string> = {
    operativo: 'status-operational',
    falla: 'status-failure',
    mantenimiento: 'status-maintenance'
  }
  return classes[status] || ''
}

const getUptimeClass = (uptime: number) => {
  if (uptime >= 98) return 'uptime-excellent'
  if (uptime >= 95) return 'uptime-good'
  if (uptime >= 90) return 'uptime-warning'
  return 'uptime-critical'
}

const runPrediction = async () => {
  if (!equipment.value) return
  
  try {
    const result = await apiService.runPrediction(equipment.value.id)
    predictionResult.value = {
      probability: result.probability,
      confidence: result.confidence
    }
    alert(`Predicción ejecutada:\nProbabilidad de falla: ${result.probability}%\nConfianza: ${(result.confidence * 100).toFixed(0)}%`)
  } catch (err) {
    console.error('Error running prediction:', err)
    alert('Error al ejecutar la predicción')
  }
}

const scheduleMaintenance = async () => {
  if (!equipment.value) return
  
  try {
    await apiService.scheduleMaintenance({
      equipment_id: equipment.value.id,
      ...maintenanceForm.value
    })
    showMaintenanceModal.value = false
    alert('Mantenimiento programado exitosamente')
  } catch (err) {
    console.error('Error scheduling maintenance:', err)
    alert('Error al programar mantenimiento')
  }
}

const goBack = () => {
  router.push({ name: 'dashboard' })
}

onMounted(loadData)
</script>

<template>
  <div class="equipment-detail">
    <header class="detail-header">
      <button class="btn-back" @click="goBack">← Volver</button>
      <h1>Detalle del Equipo</h1>
    </header>

    <div v-if="isLoading" class="loading">
      <p>Cargando...</p>
    </div>

    <main v-else-if="equipment" class="detail-content">
      <!-- Error Banner -->
      <div v-if="error" class="error-banner">
        {{ error }}
      </div>

      <div class="info-grid">
        <!-- Información del Equipo -->
        <section class="info-card">
          <h2>Información General</h2>
          <div class="info-row">
            <span class="label">Nombre:</span>
            <span class="value">{{ equipment.name }}</span>
          </div>
          <div class="info-row">
            <span class="label">Tipo:</span>
            <span :class="['type-badge', equipment.type]">{{ equipmentTypeLabel }}</span>
          </div>
          <div class="info-row">
            <span class="label">Ubicación:</span>
            <span class="value">{{ equipment.location }}</span>
          </div>
          <div class="info-row">
            <span class="label">Estado:</span>
            <span :class="['status-badge', getStatusClass(equipment.status)]">{{ equipment.status }}</span>
          </div>
          <div class="info-row">
            <span class="label">Último Mantenimiento:</span>
            <span class="value">{{ equipment.last_maintenance }}</span>
          </div>
        </section>

        <!-- Estadísticas -->
        <section class="info-card stats-card">
          <h2>Estadísticas de Operación</h2>
          <div class="stats-grid">
            <div class="stat-item">
              <span class="stat-value" :class="getUptimeClass(equipment.uptime)">{{ equipment.uptime }}%</span>
              <span class="stat-label">Uptime</span>
            </div>
            <div class="stat-item">
              <span class="stat-value failure-count">{{ equipment.failure_count }}</span>
              <span class="stat-label">Fallas Registradas</span>
            </div>
            <div class="stat-item">
              <span class="stat-value">{{ equipment.last_failure }}</span>
              <span class="stat-label">Última Falla</span>
            </div>
          </div>
        </section>

        <!-- Predicción -->
        <section v-if="predictionResult" class="info-card prediction-card">
          <h2>Última Predicción</h2>
          <div class="prediction-content">
            <div class="prediction-main">
              <div class="probability-circle" :class="predictionResult.probability > 50 ? 'high' : 'low'">
                <span class="probability-value">{{ predictionResult.probability }}%</span>
                <span class="probability-label">Probabilidad de Falla</span>
              </div>
              <div class="prediction-info">
                <div class="info-row">
                  <span class="label">Confianza del Modelo:</span>
                  <span class="value">{{ (predictionResult.confidence * 100).toFixed(0) }}%</span>
                </div>
              </div>
            </div>
          </div>
        </section>
      </div>

      <!-- Acciones -->
      <section class="actions-section">
        <button class="btn-primary" @click="runPrediction">
          Ejecutar Predicción
        </button>
        <button class="btn-secondary" @click="showMaintenanceModal = true">
          Programar Mantenimiento
        </button>
      </section>
    </main>

    <!-- Modal de Mantenimiento -->
    <div v-if="showMaintenanceModal" class="modal-overlay" @click.self="showMaintenanceModal = false">
      <div class="modal">
        <h2>Programar Mantenimiento</h2>
        <form @submit.prevent="scheduleMaintenance">
          <div class="form-group">
            <label>Fecha Programada</label>
            <input type="date" v-model="maintenanceForm.scheduled_date" required />
          </div>
          <div class="form-group">
            <label>Tipo de Mantenimiento</label>
            <select v-model="maintenanceForm.maintenance_type">
              <option value="preventivo">Preventivo</option>
              <option value="correctivo">Correctivo</option>
              <option value="predictivo">Predictivo</option>
            </select>
          </div>
          <div class="form-group">
            <label>Notas</label>
            <textarea v-model="maintenanceForm.notes" rows="3"></textarea>
          </div>
          <div class="modal-actions">
            <button type="button" class="btn-cancel" @click="showMaintenanceModal = false">
              Cancelar
            </button>
            <button type="submit" class="btn-confirm">
              Confirmar
            </button>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>

<style scoped>
.equipment-detail {
  min-height: 100vh;
  background: #f0f2f5;
}

.detail-header {
  background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
  color: white;
  padding: 1rem 2rem;
  display: flex;
  align-items: center;
  gap: 1rem;
}

.btn-back {
  background: rgba(255,255,255,0.1);
  border: none;
  color: white;
  padding: 0.5rem 1rem;
  border-radius: 4px;
  cursor: pointer;
}

.loading {
  display: flex;
  justify-content: center;
  padding: 4rem;
}

.detail-content {
  padding: 2rem;
  max-width: 1200px;
  margin: 0 auto;
}

.error-banner {
  background: #fef3e2;
  border: 1px solid #e67e22;
  color: #d35400;
  padding: 0.75rem 1rem;
  border-radius: 8px;
  margin-bottom: 1.5rem;
}

.info-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(400px, 1fr));
  gap: 1.5rem;
  margin-bottom: 2rem;
}

.info-card {
  background: white;
  border-radius: 8px;
  padding: 1.5rem;
  box-shadow: 0 2px 8px rgba(0,0,0,0.08);
}

.info-card h2 {
  margin: 0 0 1rem 0;
  font-size: 1.1rem;
  color: #1a1a2e;
  border-bottom: 1px solid #eee;
  padding-bottom: 0.5rem;
}

.info-row {
  display: flex;
  justify-content: space-between;
  padding: 0.5rem 0;
}

.label {
  color: #666;
}

.value {
  font-weight: 500;
}

/* Type badges */
.type-badge {
  padding: 0.25rem 0.75rem;
  border-radius: 20px;
  font-size: 0.85rem;
  font-weight: 500;
}

.type-badge.torniquete {
  background: #e8f4fd;
  color: #2980b9;
}

.type-badge.transbank {
  background: #f3e8fd;
  color: #8e44ad;
}

/* Status badges */
.status-badge {
  padding: 0.25rem 0.75rem;
  border-radius: 20px;
  font-size: 0.85rem;
  font-weight: 500;
  text-transform: capitalize;
}

.status-badge.status-operational {
  background: #e8f8f0;
  color: #27ae60;
}

.status-badge.status-failure {
  background: #fde8e8;
  color: #e74c3c;
}

.status-badge.status-maintenance {
  background: #fef3e2;
  color: #e67e22;
}

/* Stats card */
.stats-card .stats-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 1rem;
  text-align: center;
}

.stat-item {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
}

.stat-value {
  font-size: 1.5rem;
  font-weight: 700;
}

.stat-label {
  font-size: 0.8rem;
  color: #666;
}

/* Uptime colors */
.uptime-excellent { color: #27ae60; }
.uptime-good { color: #2ecc71; }
.uptime-warning { color: #e67e22; }
.uptime-critical { color: #e74c3c; }

.failure-count { color: #e74c3c; }

/* Prediction card */
.prediction-content {
  padding: 1rem 0;
}

.prediction-main {
  display: flex;
  gap: 2rem;
  align-items: center;
}

.probability-circle {
  width: 120px;
  height: 120px;
  border-radius: 50%;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  background: #f0f2f5;
}

.probability-circle.high {
  background: #fde8e8;
}

.probability-circle.low {
  background: #e8f8f0;
}

.probability-value {
  font-size: 1.75rem;
  font-weight: 700;
}

.probability-label {
  font-size: 0.75rem;
  color: #666;
}

.prediction-info {
  flex: 1;
}

/* Actions */
.actions-section {
  display: flex;
  gap: 1rem;
  flex-wrap: wrap;
}

.btn-primary, .btn-secondary {
  padding: 0.75rem 1.5rem;
  border-radius: 8px;
  font-size: 1rem;
  cursor: pointer;
  border: none;
  transition: transform 0.2s;
}

.btn-primary {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
}

.btn-secondary {
  background: #27ae60;
  color: white;
}

.btn-primary:hover, .btn-secondary:hover {
  transform: translateY(-2px);
}

/* Modal */
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0,0,0,0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}

.modal {
  background: white;
  padding: 2rem;
  border-radius: 8px;
  width: 100%;
  max-width: 450px;
}

.modal h2 {
  margin: 0 0 1.5rem 0;
}

.form-group {
  margin-bottom: 1rem;
}

.form-group label {
  display: block;
  margin-bottom: 0.5rem;
  font-weight: 500;
}

.form-group input,
.form-group select,
.form-group textarea {
  width: 100%;
  padding: 0.75rem;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 1rem;
}

.modal-actions {
  display: flex;
  gap: 1rem;
  justify-content: flex-end;
  margin-top: 1.5rem;
}

.btn-cancel {
  padding: 0.75rem 1.5rem;
  background: #f0f2f5;
  border: none;
  border-radius: 4px;
  cursor: pointer;
}

.btn-confirm {
  padding: 0.75rem 1.5rem;
  background: #27ae60;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
}
</style>