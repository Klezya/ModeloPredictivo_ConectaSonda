<!-- filepath: frontend/src/views/DashboardView.vue -->
<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import { useRouter } from 'vue-router'

const router = useRouter()

// Estado del dashboard
const isLoading = ref(true)
const selectedTimeRange = ref('24h')
const selectedEquipment = ref('all')

// Datos simulados de predicciones
const predictions = ref([
  {
    id: 1,
    equipment: 'Sonda A-001',
    location: 'Sector Norte',
    riskLevel: 'alto',
    probability: 87,
    predictedFailure: 'Falla en sensor de presión',
    estimatedTime: '2-4 horas',
    lastMaintenance: '2024-01-15',
    status: 'activo'
  },
  {
    id: 2,
    equipment: 'Sonda B-023',
    location: 'Sector Sur',
    riskLevel: 'medio',
    probability: 54,
    predictedFailure: 'Desgaste en válvula principal',
    estimatedTime: '24-48 horas',
    lastMaintenance: '2024-02-01',
    status: 'activo'
  },
  {
    id: 3,
    equipment: 'Sonda C-105',
    location: 'Sector Este',
    riskLevel: 'bajo',
    probability: 23,
    predictedFailure: 'Calibración requerida',
    estimatedTime: '1 semana',
    lastMaintenance: '2024-01-28',
    status: 'activo'
  },
  {
    id: 4,
    equipment: 'Sonda D-042',
    location: 'Sector Oeste',
    riskLevel: 'critico',
    probability: 95,
    predictedFailure: 'Falla inminente en motor',
    estimatedTime: '< 1 hora',
    lastMaintenance: '2023-12-10',
    status: 'alerta'
  },
  {
    id: 5,
    equipment: 'Sonda E-078',
    location: 'Sector Norte',
    riskLevel: 'bajo',
    probability: 12,
    predictedFailure: 'Sin fallas previstas',
    estimatedTime: 'N/A',
    lastMaintenance: '2024-02-10',
    status: 'óptimo'
  }
])

// Métricas generales
const metrics = ref({
  totalEquipments: 156,
  activeAlerts: 12,
  predictedFailures: 8,
  maintenanceScheduled: 5,
  systemAccuracy: 94.5,
  avgResponseTime: '2.3h'
})

// Historial de fallas recientes
const recentFailures = ref([
  { date: '2024-02-18', equipment: 'Sonda F-012', type: 'Sensor', resolved: true },
  { date: '2024-02-17', equipment: 'Sonda A-045', type: 'Válvula', resolved: true },
  { date: '2024-02-16', equipment: 'Sonda B-089', type: 'Motor', resolved: false },
  { date: '2024-02-15', equipment: 'Sonda C-023', type: 'Presión', resolved: true }
])

// Filtrar predicciones
const filteredPredictions = computed(() => {
  if (selectedEquipment.value === 'all') {
    return predictions.value
  }
  return predictions.value.filter(p => 
    p.riskLevel === selectedEquipment.value
  )
})

// Contadores por nivel de riesgo
const riskCounts = computed(() => ({
  critico: predictions.value.filter(p => p.riskLevel === 'critico').length,
  alto: predictions.value.filter(p => p.riskLevel === 'alto').length,
  medio: predictions.value.filter(p => p.riskLevel === 'medio').length,
  bajo: predictions.value.filter(p => p.riskLevel === 'bajo').length
}))

const getRiskClass = (level: string) => {
  const classes: Record<string, string> = {
    critico: 'risk-critical',
    alto: 'risk-high',
    medio: 'risk-medium',
    bajo: 'risk-low'
  }
  return classes[level] || ''
}

const getStatusClass = (status: string) => {
  const classes: Record<string, string> = {
    activo: 'status-active',
    alerta: 'status-alert',
    óptimo: 'status-optimal'
  }
  return classes[status] || ''
}

const handleLogout = () => {
  localStorage.removeItem('isAuthenticated')
  router.push({ name: 'login' })
}

const viewDetails = (id: number) => {
  console.log('Ver detalles del equipo:', id)
  // Aquí se podría navegar a una vista de detalle
}

const scheduleMaintenace = (id: number) => {
  console.log('Programar mantenimiento para:', id)
  // Aquí se podría abrir un modal para programar mantenimiento
}

onMounted(() => {
  // Simular carga de datos
  setTimeout(() => {
    isLoading.value = false
  }, 1000)
})
</script>

<template>
  <div class="dashboard">
    <!-- Header -->
    <header class="dashboard-header">
      <div class="header-left">
        <h1>Sistema Predictivo de Fallas</h1>
        <span class="subtitle">ConectaSonda - Monitoreo en Tiempo Real</span>
      </div>
      <div class="header-right">
        <select v-model="selectedTimeRange" class="time-select">
          <option value="1h">Última hora</option>
          <option value="24h">Últimas 24 horas</option>
          <option value="7d">Últimos 7 días</option>
          <option value="30d">Últimos 30 días</option>
        </select>
        <button class="btn-logout" @click="handleLogout">
          Cerrar Sesión
        </button>
      </div>
    </header>

    <!-- Loading State -->
    <div v-if="isLoading" class="loading">
      <div class="spinner"></div>
      <p>Cargando datos del sistema...</p>
    </div>

    <!-- Dashboard Content -->
    <main v-else class="dashboard-content">
      <!-- Métricas Principales -->
      <section class="metrics-section">
        <div class="metric-card">
          <div class="metric-icon"></div>
          <div class="metric-info">
            <span class="metric-value">{{ metrics.totalEquipments }}</span>
            <span class="metric-label">Equipos Monitoreados</span>
          </div>
        </div>
        <div class="metric-card alert">
          <div class="metric-icon"></div>
          <div class="metric-info">
            <span class="metric-value">{{ metrics.activeAlerts }}</span>
            <span class="metric-label">Alertas Activas</span>
          </div>
        </div>
        <div class="metric-card warning">
          <div class="metric-icon"></div>
          <div class="metric-info">
            <span class="metric-value">{{ metrics.predictedFailures }}</span>
            <span class="metric-label">Fallas Predichas</span>
          </div>
        </div>
        <div class="metric-card success">
          <div class="metric-icon"></div>
          <div class="metric-info">
            <span class="metric-value">{{ metrics.maintenanceScheduled }}</span>
            <span class="metric-label">Mantenimientos Programados</span>
          </div>
        </div>
        <div class="metric-card info">
          <div class="metric-icon"></div>
          <div class="metric-info">
            <span class="metric-value">{{ metrics.systemAccuracy }}%</span>
            <span class="metric-label">Precisión del Modelo</span>
          </div>
        </div>
        <div class="metric-card">
          <div class="metric-icon"></div>
          <div class="metric-info">
            <span class="metric-value">{{ metrics.avgResponseTime }}</span>
            <span class="metric-label">Tiempo Respuesta Promedio</span>
          </div>
        </div>
      </section>

      <!-- Resumen de Riesgos -->
      <section class="risk-summary">
        <h2>Resumen de Niveles de Riesgo</h2>
        <div class="risk-bars">
          <div class="risk-bar">
            <div class="risk-bar-label">
              <span class="risk-dot critical"></span>
              Crítico
            </div>
            <div class="risk-bar-track">
              <div 
                class="risk-bar-fill critical" 
                :style="{ width: (riskCounts.critico / predictions.length * 100) + '%' }"
              ></div>
            </div>
            <span class="risk-bar-count">{{ riskCounts.critico }}</span>
          </div>
          <div class="risk-bar">
            <div class="risk-bar-label">
              <span class="risk-dot high"></span>
              Alto
            </div>
            <div class="risk-bar-track">
              <div 
                class="risk-bar-fill high" 
                :style="{ width: (riskCounts.alto / predictions.length * 100) + '%' }"
              ></div>
            </div>
            <span class="risk-bar-count">{{ riskCounts.alto }}</span>
          </div>
          <div class="risk-bar">
            <div class="risk-bar-label">
              <span class="risk-dot medium"></span>
              Medio
            </div>
            <div class="risk-bar-track">
              <div 
                class="risk-bar-fill medium" 
                :style="{ width: (riskCounts.medio / predictions.length * 100) + '%' }"
              ></div>
            </div>
            <span class="risk-bar-count">{{ riskCounts.medio }}</span>
          </div>
          <div class="risk-bar">
            <div class="risk-bar-label">
              <span class="risk-dot low"></span>
              Bajo
            </div>
            <div class="risk-bar-track">
              <div 
                class="risk-bar-fill low" 
                :style="{ width: (riskCounts.bajo / predictions.length * 100) + '%' }"
              ></div>
            </div>
            <span class="risk-bar-count">{{ riskCounts.bajo }}</span>
          </div>
        </div>
      </section>

      <!-- Contenido Principal -->
      <div class="main-grid">
        <!-- Tabla de Predicciones -->
        <section class="predictions-section">
          <div class="section-header">
            <h2>Predicciones de Fallas</h2>
            <select v-model="selectedEquipment" class="filter-select">
              <option value="all">Todos los niveles</option>
              <option value="critico">Solo Críticos</option>
              <option value="alto">Solo Altos</option>
              <option value="medio">Solo Medios</option>
              <option value="bajo">Solo Bajos</option>
            </select>
          </div>
          
          <div class="predictions-table">
            <table>
              <thead>
                <tr>
                  <th>Equipo</th>
                  <th>Ubicación</th>
                  <th>Riesgo</th>
                  <th>Probabilidad</th>
                  <th>Falla Predicha</th>
                  <th>Tiempo Estimado</th>
                  <th>Estado</th>
                  <th>Acciones</th>
                </tr>
              </thead>
              <tbody>
                <tr 
                  v-for="prediction in filteredPredictions" 
                  :key="prediction.id"
                  :class="{ 'row-critical': prediction.riskLevel === 'critico' }"
                >
                  <td class="equipment-name">{{ prediction.equipment }}</td>
                  <td>{{ prediction.location }}</td>
                  <td>
                    <span :class="['risk-badge', getRiskClass(prediction.riskLevel)]">
                      {{ prediction.riskLevel.toUpperCase() }}
                    </span>
                  </td>
                  <td>
                    <div class="probability-bar">
                      <div 
                        class="probability-fill" 
                        :class="getRiskClass(prediction.riskLevel)"
                        :style="{ width: prediction.probability + '%' }"
                      ></div>
                      <span class="probability-text">{{ prediction.probability }}%</span>
                    </div>
                  </td>
                  <td>{{ prediction.predictedFailure }}</td>
                  <td class="time-estimate">{{ prediction.estimatedTime }}</td>
                  <td>
                    <span :class="['status-badge', getStatusClass(prediction.status)]">
                      {{ prediction.status }}
                    </span>
                  </td>
                  <td class="actions">
                    <button class="btn-action btn-view" @click="viewDetails(prediction.id)">
                      Ver
                    </button>
                    <button class="btn-action btn-schedule" @click="scheduleMaintenace(prediction.id)">
                      Programar
                    </button>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
        </section>

        <!-- Panel Lateral -->
        <aside class="sidebar">
          <!-- Historial Reciente -->
          <div class="sidebar-card">
            <h3>Fallas Recientes</h3>
            <ul class="recent-list">
              <li v-for="(failure, index) in recentFailures" :key="index">
                <div class="recent-item">
                  <div class="recent-info">
                    <span class="recent-equipment">{{ failure.equipment }}</span>
                    <span class="recent-type">{{ failure.type }}</span>
                  </div>
                  <div class="recent-meta">
                    <span class="recent-date">{{ failure.date }}</span>
                    <span 
                      :class="['recent-status', failure.resolved ? 'resolved' : 'pending']"
                    >
                      {{ failure.resolved ? 'Resuelto' : 'Pendiente' }}
                    </span>
                  </div>
                </div>
              </li>
            </ul>
          </div>

          <!-- Acciones Rápidas -->
          <div class="sidebar-card">
            <h3>Acciones Rápidas</h3>
            <div class="quick-actions">
              <button class="quick-btn">
                Generar Reporte
              </button>
              <button class="quick-btn">
                Configurar Alertas
              </button>
              <button class="quick-btn">
                Programar Mantenimiento
              </button>
              <button class="quick-btn">
                Exportar Datos
              </button>
            </div>
          </div>

          <!-- Estado del Sistema -->
          <div class="sidebar-card system-status">
            <h3>Estado del Sistema</h3>
            <div class="status-item">
              <span>Modelo ML</span>
              <span class="status-indicator online">● Activo</span>
            </div>
            <div class="status-item">
              <span>API Backend</span>
              <span class="status-indicator online">● Conectado</span>
            </div>
            <div class="status-item">
              <span>Base de Datos</span>
              <span class="status-indicator online">● Operativa</span>
            </div>
            <div class="status-item">
              <span>Última Sincronización</span>
              <span class="status-time">Hace 2 min</span>
            </div>
          </div>
        </aside>
      </div>
    </main>

    <!-- Footer -->
    <footer class="dashboard-footer">
      <p>© 2024 ConectaSonda - Sistema Predictivo de Fallas v1.0</p>
    </footer>
  </div>
</template>

<style scoped>
.dashboard {
  min-height: 100vh;
  background: #f0f2f5;
  display: flex;
  flex-direction: column;
}

/* Header */
.dashboard-header {
  background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
  color: white;
  padding: 1rem 2rem;
  display: flex;
  justify-content: space-between;
  align-items: center;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.2);
}

.header-left h1 {
  font-size: 1.5rem;
  margin: 0;
}

.subtitle {
  font-size: 0.85rem;
  opacity: 0.8;
}

.header-right {
  display: flex;
  gap: 1rem;
  align-items: center;
}

.time-select {
  padding: 0.5rem 1rem;
  border-radius: 4px;
  border: none;
  background: rgba(255, 255, 255, 0.1);
  color: white;
  cursor: pointer;
}

.time-select option {
  color: #333;
}

.btn-logout {
  padding: 0.5rem 1rem;
  background: #e74c3c;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  transition: background 0.3s;
}

.btn-logout:hover {
  background: #c0392b;
}

/* Loading */
.loading {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 1rem;
}

.spinner {
  width: 50px;
  height: 50px;
  border: 4px solid #e0e0e0;
  border-top-color: #667eea;
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

/* Content */
.dashboard-content {
  flex: 1;
  padding: 1.5rem 2rem;
}

/* Metrics */
.metrics-section {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 1rem;
  margin-bottom: 1.5rem;
}

.metric-card {
  background: white;
  border-radius: 8px;
  padding: 1.25rem;
  display: flex;
  align-items: center;
  gap: 1rem;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
  border-left: 4px solid #667eea;
}

.metric-card.alert { border-left-color: #e74c3c; }
.metric-card.warning { border-left-color: #f39c12; }
.metric-card.success { border-left-color: #27ae60; }
.metric-card.info { border-left-color: #3498db; }

.metric-icon {
  font-size: 2rem;
}

.metric-info {
  display: flex;
  flex-direction: column;
}

.metric-value {
  font-size: 1.75rem;
  font-weight: 700;
  color: #1a1a2e;
}

.metric-label {
  font-size: 0.85rem;
  color: #666;
}

/* Risk Summary */
.risk-summary {
  background: white;
  border-radius: 8px;
  padding: 1.25rem;
  margin-bottom: 1.5rem;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
}

.risk-summary h2 {
  margin: 0 0 1rem 0;
  font-size: 1.1rem;
  color: #1a1a2e;
}

.risk-bars {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 1rem;
}

.risk-bar {
  display: flex;
  align-items: center;
  gap: 0.75rem;
}

.risk-bar-label {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  min-width: 80px;
  font-size: 0.9rem;
}

.risk-dot {
  width: 10px;
  height: 10px;
  border-radius: 50%;
}

.risk-dot.critical { background: #e74c3c; }
.risk-dot.high { background: #e67e22; }
.risk-dot.medium { background: #f1c40f; }
.risk-dot.low { background: #27ae60; }

.risk-bar-track {
  flex: 1;
  height: 8px;
  background: #e0e0e0;
  border-radius: 4px;
  overflow: hidden;
}

.risk-bar-fill {
  height: 100%;
  border-radius: 4px;
  transition: width 0.5s ease;
}

.risk-bar-fill.critical { background: #e74c3c; }
.risk-bar-fill.high { background: #e67e22; }
.risk-bar-fill.medium { background: #f1c40f; }
.risk-bar-fill.low { background: #27ae60; }

.risk-bar-count {
  font-weight: 600;
  min-width: 20px;
}

/* Main Grid */
.main-grid {
  display: grid;
  grid-template-columns: 1fr 320px;
  gap: 1.5rem;
}

/* Predictions Section */
.predictions-section {
  background: white;
  border-radius: 8px;
  padding: 1.25rem;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1rem;
}

.section-header h2 {
  margin: 0;
  font-size: 1.1rem;
  color: #1a1a2e;
}

.filter-select {
  padding: 0.5rem 1rem;
  border: 1px solid #ddd;
  border-radius: 4px;
  background: white;
  cursor: pointer;
}

.predictions-table {
  overflow-x: auto;
}

table {
  width: 100%;
  border-collapse: collapse;
}

th, td {
  padding: 0.75rem;
  text-align: left;
  border-bottom: 1px solid #eee;
}

th {
  background: #f8f9fa;
  font-weight: 600;
  color: #555;
  font-size: 0.85rem;
  text-transform: uppercase;
}

.row-critical {
  background: #fff5f5;
}

.equipment-name {
  font-weight: 600;
  color: #1a1a2e;
}

.risk-badge {
  padding: 0.25rem 0.5rem;
  border-radius: 4px;
  font-size: 0.75rem;
  font-weight: 600;
}

.risk-critical { background: #fde8e8; color: #e74c3c; }
.risk-high { background: #fef3e2; color: #e67e22; }
.risk-medium { background: #fef9e7; color: #b7950b; }
.risk-low { background: #e8f8f0; color: #27ae60; }

.probability-bar {
  position: relative;
  height: 20px;
  background: #e0e0e0;
  border-radius: 10px;
  min-width: 100px;
  overflow: hidden;
}

.probability-fill {
  height: 100%;
  border-radius: 10px;
  transition: width 0.5s ease;
}

.probability-text {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  font-size: 0.75rem;
  font-weight: 600;
  color: #333;
}

.time-estimate {
  font-weight: 500;
  color: #e67e22;
}

.status-badge {
  padding: 0.25rem 0.5rem;
  border-radius: 4px;
  font-size: 0.75rem;
}

.status-active { background: #e8f4fd; color: #3498db; }
.status-alert { background: #fde8e8; color: #e74c3c; }
.status-optimal { background: #e8f8f0; color: #27ae60; }

.actions {
  display: flex;
  gap: 0.5rem;
}

.btn-action {
  padding: 0.25rem 0.5rem;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  transition: transform 0.2s;
}

.btn-action:hover {
  transform: scale(1.1);
}

.btn-view { background: #e8f4fd; }
.btn-schedule { background: #e8f8f0; }

/* Sidebar */
.sidebar {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.sidebar-card {
  background: white;
  border-radius: 8px;
  padding: 1.25rem;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
}

.sidebar-card h3 {
  margin: 0 0 1rem 0;
  font-size: 1rem;
  color: #1a1a2e;
}

.recent-list {
  list-style: none;
  padding: 0;
  margin: 0;
}

.recent-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0.75rem 0;
  border-bottom: 1px solid #eee;
}

.recent-item:last-child {
  border-bottom: none;
}

.recent-equipment {
  font-weight: 500;
  display: block;
}

.recent-type {
  font-size: 0.8rem;
  color: #888;
}

.recent-date {
  font-size: 0.8rem;
  color: #888;
}

.recent-status {
  margin-left: 0.5rem;
}

.recent-status.resolved { color: #27ae60; }
.recent-status.pending { color: #f39c12; }

.quick-actions {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.quick-btn {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  padding: 0.75rem;
  background: #f8f9fa;
  border: 1px solid #eee;
  border-radius: 4px;
  cursor: pointer;
  transition: background 0.3s;
}

.quick-btn:hover {
  background: #e8f4fd;
}

.quick-icon {
  font-size: 1.25rem;
}

.system-status .status-item {
  display: flex;
  justify-content: space-between;
  padding: 0.5rem 0;
  border-bottom: 1px solid #eee;
}

.status-indicator.online {
  color: #27ae60;
}

.status-time {
  color: #888;
  font-size: 0.85rem;
}

/* Footer */
.dashboard-footer {
  background: #1a1a2e;
  color: #888;
  text-align: center;
  padding: 1rem;
  font-size: 0.85rem;
}

/* Responsive */
@media (max-width: 1024px) {
  .main-grid {
    grid-template-columns: 1fr;
  }
}

@media (max-width: 768px) {
  .dashboard-header {
    flex-direction: column;
    gap: 1rem;
    text-align: center;
  }
  
  .dashboard-content {
    padding: 1rem;
  }
  
  .metrics-section {
    grid-template-columns: repeat(2, 1fr);
  }
}
</style>