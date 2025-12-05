<!-- filepath: frontend/src/views/EquipmentDetailView.vue -->
<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { apiService, type Equipment, type Prediction } from '@/services/api'

const route = useRoute()
const router = useRouter()

const equipment = ref<Equipment | null>(null)
const prediction = ref<Prediction | null>(null)
const isLoading = ref(true)
const showMaintenanceModal = ref(false)

const maintenanceForm = ref({
  scheduled_date: '',
  maintenance_type: 'preventivo',
  notes: ''
})

const loadData = async () => {
  try {
    const id = Number(route.params.id)
    equipment.value = await apiService.getEquipment(id)
    
    const predictions = await apiService.getPredictions()
    prediction.value = predictions.find(p => p.equipment_id === id) || null
  } catch (error) {
    console.error('Error loading data:', error)
  } finally {
    isLoading.value = false
  }
}

const runPrediction = async () => {
  if (!equipment.value) return
  
  try {
    const result = await apiService.runPrediction(equipment.value.id)
    alert(`Predicción ejecutada:\nRiesgo: ${result.risk_level}\nProbabilidad: ${result.probability}%`)
  } catch (error) {
    console.error('Error running prediction:', error)
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
  } catch (error) {
    console.error('Error scheduling maintenance:', error)
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
      <div class="info-grid">
        <!-- Información del Equipo -->
        <section class="info-card">
          <h2>Información General</h2>
          <div class="info-row">
            <span class="label">Nombre:</span>
            <span class="value">{{ equipment.name }}</span>
          </div>
          <div class="info-row">
            <span class="label">Ubicación:</span>
            <span class="value">{{ equipment.location }}</span>
          </div>
          <div class="info-row">
            <span class="label">Estado:</span>
            <span :class="['status-badge', equipment.status]">{{ equipment.status }}</span>
          </div>
          <div class="info-row">
            <span class="label">Último Mantenimiento:</span>
            <span class="value">{{ equipment.last_maintenance }}</span>
          </div>
        </section>

        <!-- Predicción Actual -->
        <section v-if="prediction" class="info-card prediction-card">
          <h2>Predicción de Falla</h2>
          <div class="prediction-main">
            <div class="probability-circle" :class="prediction.risk_level">
              <span class="probability-value">{{ prediction.probability }}%</span>
              <span class="probability-label">Probabilidad</span>
            </div>
            <div class="prediction-info">
              <div class="info-row">
                <span class="label">Nivel de Riesgo:</span>
                <span :class="['risk-badge', prediction.risk_level]">
                  {{ prediction.risk_level.toUpperCase() }}
                </span>
              </div>
              <div class="info-row">
                <span class="label">Falla Predicha:</span>
                <span class="value">{{ prediction.predicted_failure }}</span>
              </div>
              <div class="info-row">
                <span class="label">Tiempo Estimado:</span>
                <span class="value warning">{{ prediction.estimated_time }}</span>
              </div>
            </div>
          </div>
        </section>
      </div>

      <!-- Acciones -->
      <section class="actions-section">
        <button class="btn-primary" @click="runPrediction">
          Ejecutar Nueva Predicción
        </button>
        <button class="btn-secondary" @click="showMaintenanceModal = true">
          Programar Mantenimiento
        </button>
        <button class="btn-outline">
          Ver Historial
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

.value.warning {
  color: #e67e22;
}

.status-badge {
  padding: 0.25rem 0.75rem;
  border-radius: 20px;
  font-size: 0.85rem;
}

.status-badge.activo { background: #e8f4fd; color: #3498db; }
.status-badge.alerta { background: #fde8e8; color: #e74c3c; }
.status-badge.óptimo { background: #e8f8f0; color: #27ae60; }

.risk-badge {
  padding: 0.25rem 0.75rem;
  border-radius: 4px;
  font-weight: 600;
  font-size: 0.85rem;
}

.risk-badge.critico { background: #fde8e8; color: #e74c3c; }
.risk-badge.alto { background: #fef3e2; color: #e67e22; }
.risk-badge.medio { background: #fef9e7; color: #b7950b; }
.risk-badge.bajo { background: #e8f8f0; color: #27ae60; }

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

.probability-circle.critico { background: #fde8e8; }
.probability-circle.alto { background: #fef3e2; }
.probability-circle.medio { background: #fef9e7; }
.probability-circle.bajo { background: #e8f8f0; }

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

.actions-section {
  display: flex;
  gap: 1rem;
  flex-wrap: wrap;
}

.btn-primary, .btn-secondary, .btn-outline {
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

.btn-outline {
  background: white;
  border: 2px solid #667eea;
  color: #667eea;
}

.btn-primary:hover, .btn-secondary:hover, .btn-outline:hover {
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