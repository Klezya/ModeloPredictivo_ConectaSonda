<!-- filepath: frontend/src/views/DashboardView.vue -->
<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import { useRouter } from 'vue-router'
import { apiService, type Metrics, type FailureHistory } from '@/services/api'

const router = useRouter()

// Estado del dashboard
const isLoading = ref(true)
const selectedTimeRange = ref('24h')
const selectedEquipmentType = ref('all')
const error = ref('')

// Datos de equipos
const equipments = ref<Array<{
  id: number
  name: string
  type: string
  location: string
  status: string
  lastFailure: string
  failureCount: number
  uptime: number
}>>([])

// Métricas generales
const metrics = ref({
  total_equipments: 0,
  active_equipments: 0,
  inactive_equipments: 0,
  maintenance_pending: 0,
  system_accuracy: 0,
  avg_uptime: '0%'
})

// Historial de fallas recientes
const recentFailures = ref<Array<{
  date: string
  equipment: string
  type: string
  resolved: boolean
}>>([])

// Cargar datos desde el API
const loadData = async () => {
  try {
    isLoading.value = true
    error.value = ''

    // Intentar cargar desde API
    const metricsData = await apiService.getMetrics()
    metrics.value = {
      total_equipments: metricsData.total_equipments,
      active_equipments: metricsData.active_alerts,
      inactive_equipments: metricsData.predicted_failures,
      maintenance_pending: metricsData.maintenance_scheduled,
      system_accuracy: metricsData.system_accuracy,
      avg_uptime: metricsData.avg_response_time
    }

    const failuresData = await apiService.getFailures()
    recentFailures.value = failuresData.map((f: FailureHistory) => ({
      date: f.date,
      equipment: f.equipment,
      type: f.failure_type,
      resolved: f.resolved
    }))

    loadDemoData() // Cargar equipos demo por ahora

  } catch (err) {
    console.error('Error loading data:', err)
    error.value = 'Error al cargar los datos. Usando datos de demostración.'
    loadDemoData()
  } finally {
    isLoading.value = false
  }
}

// Datos de demostración
const loadDemoData = () => {
  equipments.value = [
    { id: 1, name: 'Torniquete T-001', type: 'torniquete', location: 'Estación Central - Acceso Norte', status: 'operativo', lastFailure: '2024-11-20', failureCount: 3, uptime: 98.5 },
    { id: 2, name: 'Torniquete T-002', type: 'torniquete', location: 'Estación Central - Acceso Sur', status: 'operativo', lastFailure: '2024-12-01', failureCount: 1, uptime: 99.2 },
    { id: 3, name: 'Transbank TB-001', type: 'transbank', location: 'Estación Central - Hall Principal', status: 'falla', lastFailure: '2024-12-04', failureCount: 5, uptime: 94.1 },
    { id: 4, name: 'Torniquete T-003', type: 'torniquete', location: 'Estación Los Héroes - Acceso Este', status: 'mantenimiento', lastFailure: '2024-11-15', failureCount: 2, uptime: 97.8 },
    { id: 5, name: 'Transbank TB-002', type: 'transbank', location: 'Estación Los Héroes - Boletería', status: 'operativo', lastFailure: '2024-10-28', failureCount: 2, uptime: 96.5 },
    { id: 6, name: 'Torniquete T-004', type: 'torniquete', location: 'Estación Baquedano - Acceso Principal', status: 'operativo', lastFailure: '2024-11-30', failureCount: 1, uptime: 99.0 },
    { id: 7, name: 'Transbank TB-003', type: 'transbank', location: 'Estación Baquedano - Autoservicio', status: 'operativo', lastFailure: '2024-11-10', failureCount: 4, uptime: 95.3 },
    { id: 8, name: 'Torniquete T-005', type: 'torniquete', location: 'Estación Tobalaba - Acceso Oriente', status: 'falla', lastFailure: '2024-12-04', failureCount: 6, uptime: 92.1 }
  ]

  metrics.value = {
    total_equipments: 85,
    active_equipments: 78,
    inactive_equipments: 7,
    maintenance_pending: 4,
    system_accuracy: 94.5,
    avg_uptime: '96.8%'
  }

  recentFailures.value = [
    { date: '2024-12-04', equipment: 'Transbank TB-001', type: 'Lector de tarjetas', resolved: false },
    { date: '2024-12-04', equipment: 'Torniquete T-005', type: 'Motor de giro', resolved: false },
    { date: '2024-12-03', equipment: 'Torniquete T-002', type: 'Sensor de paso', resolved: true },
    { date: '2024-12-02', equipment: 'Transbank TB-003', type: 'Pantalla táctil', resolved: true }
  ]
}

// Filtrar equipos
const filteredEquipments = computed(() => {
  if (selectedEquipmentType.value === 'all') {
    return equipments.value
  }
  return equipments.value.filter(e => e.type === selectedEquipmentType.value)
})

// Contadores por tipo
const typeCounts = computed(() => ({
  torniquetes: equipments.value.filter(e => e.type === 'torniquete').length,
  transbank: equipments.value.filter(e => e.type === 'transbank').length
}))

// Contadores por estado
const statusCounts = computed(() => ({
  operativo: equipments.value.filter(e => e.status === 'operativo').length,
  falla: equipments.value.filter(e => e.status === 'falla').length,
  mantenimiento: equipments.value.filter(e => e.status === 'mantenimiento').length
}))

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

const handleLogout = () => {
  localStorage.removeItem('isAuthenticated')
  router.push({ name: 'login' })
}

const viewDetails = (id: number) => {
  router.push({ name: 'equipment-detail', params: { id } })
}

const scheduleMaintenace = (id: number) => {
  alert(`Programar mantenimiento para equipo ID: ${id}`)
}

const generateReport = async () => {
  try {
    await apiService.generateReport('general')
    alert('Reporte generado exitosamente')
  } catch (err) {
    alert('Error al generar el reporte')
  }
}

onMounted(() => {
  loadData()
})
</script>

<template>
  <div class="dashboard">
    <!-- Header -->
    <header class="dashboard-header">
      <div class="header-left">
        <h1>Sistema Predictivo de Fallas</h1>
        <span class="subtitle">ConectaSonda - Torniquetes y Transbank</span>
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
      <!-- Error Banner -->
      <div v-if="error" class="error-banner">
        {{ error }}
      </div>

      <!-- Métricas Principales -->
      <section class="metrics-section">
        <div class="metric-card">
          <div class="metric-icon"></div>
          <div class="metric-info">
            <span class="metric-value">{{ metrics.total_equipments }}</span>
            <span class="metric-label">Equipos Totales</span>
          </div>
        </div>
        <div class="metric-card success">
          <div class="metric-icon"></div>
          <div class="metric-info">
            <span class="metric-value">{{ metrics.active_equipments }}</span>
            <span class="metric-label">Equipos Operativos</span>
          </div>
        </div>
        <div class="metric-card alert">
          <div class="metric-icon"></div>
          <div class="metric-info">
            <span class="metric-value">{{ metrics.inactive_equipments }}</span>
            <span class="metric-label">Equipos con Falla</span>
          </div>
        </div>
        <div class="metric-card warning">
          <div class="metric-icon"></div>
          <div class="metric-info">
            <span class="metric-value">{{ metrics.maintenance_pending }}</span>
            <span class="metric-label">Mantenimientos Pendientes</span>
          </div>
        </div>
        <div class="metric-card info">
          <div class="metric-icon"></div>
          <div class="metric-info">
            <span class="metric-value">{{ metrics.system_accuracy }}%</span>
            <span class="metric-label">Precisión del Modelo</span>
          </div>
        </div>
        <div class="metric-card">
          <div class="metric-icon"></div>
          <div class="metric-info">
            <span class="metric-value">{{ metrics.avg_uptime }}</span>
            <span class="metric-label">Uptime Promedio</span>
          </div>
        </div>
      </section>

      <!-- Resumen por Tipo y Estado -->
      <section class="summary-section">
        <div class="summary-card">
          <h2>Equipos por Tipo</h2>
          <div class="summary-bars">
            <div class="summary-bar">
              <div class="summary-bar-label">Torniquetes</div>
              <div class="summary-bar-track">
                <div 
                  class="summary-bar-fill torniquete" 
                  :style="{ width: (typeCounts.torniquetes / equipments.length * 100) + '%' }"
                ></div>
              </div>
              <span class="summary-bar-count">{{ typeCounts.torniquetes }}</span>
            </div>
            <div class="summary-bar">
              <div class="summary-bar-label">Transbank</div>
              <div class="summary-bar-track">
                <div 
                  class="summary-bar-fill transbank" 
                  :style="{ width: (typeCounts.transbank / equipments.length * 100) + '%' }"
                ></div>
              </div>
              <span class="summary-bar-count">{{ typeCounts.transbank }}</span>
            </div>
          </div>
        </div>
        <div class="summary-card">
          <h2>Estado de Equipos</h2>
          <div class="summary-bars">
            <div class="summary-bar">
              <div class="summary-bar-label">
                <span class="status-dot operational"></span>
                Operativo
              </div>
              <div class="summary-bar-track">
                <div 
                  class="summary-bar-fill operational" 
                  :style="{ width: (statusCounts.operativo / equipments.length * 100) + '%' }"
                ></div>
              </div>
              <span class="summary-bar-count">{{ statusCounts.operativo }}</span>
            </div>
            <div class="summary-bar">
              <div class="summary-bar-label">
                <span class="status-dot failure"></span>
                Con Falla
              </div>
              <div class="summary-bar-track">
                <div 
                  class="summary-bar-fill failure" 
                  :style="{ width: (statusCounts.falla / equipments.length * 100) + '%' }"
                ></div>
              </div>
              <span class="summary-bar-count">{{ statusCounts.falla }}</span>
            </div>
            <div class="summary-bar">
              <div class="summary-bar-label">
                <span class="status-dot maintenance"></span>
                Mantenimiento
              </div>
              <div class="summary-bar-track">
                <div 
                  class="summary-bar-fill maintenance" 
                  :style="{ width: (statusCounts.mantenimiento / equipments.length * 100) + '%' }"
                ></div>
              </div>
              <span class="summary-bar-count">{{ statusCounts.mantenimiento }}</span>
            </div>
          </div>
        </div>
      </section>

      <!-- Contenido Principal -->
      <div class="main-grid">
        <!-- Tabla de Equipos -->
        <section class="equipments-section">
          <div class="section-header">
            <h2>Estado de Equipos</h2>
            <select v-model="selectedEquipmentType" class="filter-select">
              <option value="all">Todos los equipos</option>
              <option value="torniquete">Solo Torniquetes</option>
              <option value="transbank">Solo Transbank</option>
            </select>
          </div>
          
          <div class="equipments-table">
            <table>
              <thead>
                <tr>
                  <th>Equipo</th>
                  <th>Tipo</th>
                  <th>Ubicación</th>
                  <th>Estado</th>
                  <th>Última Falla</th>
                  <th>N° Fallas</th>
                  <th>Uptime</th>
                  <th>Acciones</th>
                </tr>
              </thead>
              <tbody>
                <tr 
                  v-for="equipment in filteredEquipments" 
                  :key="equipment.id"
                  :class="{ 'row-failure': equipment.status === 'falla' }"
                >
                  <td class="equipment-name">{{ equipment.name }}</td>
                  <td>
                    <span :class="['type-badge', equipment.type]">
                      {{ equipment.type === 'torniquete' ? 'Torniquete' : 'Transbank' }}
                    </span>
                  </td>
                  <td>{{ equipment.location }}</td>
                  <td>
                    <span :class="['status-badge', getStatusClass(equipment.status)]">
                      {{ equipment.status }}
                    </span>
                  </td>
                  <td>{{ equipment.lastFailure }}</td>
                  <td class="failure-count">{{ equipment.failureCount }}</td>
                  <td>
                    <div class="uptime-bar">
                      <div 
                        class="uptime-fill" 
                        :class="getUptimeClass(equipment.uptime)"
                        :style="{ width: equipment.uptime + '%' }"
                      ></div>
                      <span class="uptime-text">{{ equipment.uptime }}%</span>
                    </div>
                  </td>
                  <td class="actions">
                    <button class="btn-action btn-view" @click="viewDetails(equipment.id)">
                      Ver
                    </button>
                    <button class="btn-action btn-schedule" @click="scheduleMaintenace(equipment.id)">
                      Mantención
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
              <button class="quick-btn" @click="generateReport">
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

/* Error Banner */
.error-banner {
  background: #fef3e2;
  color: #e67e22;
  padding: 0.75rem 1rem;
  border-radius: 4px;
  margin-bottom: 1rem;
  border-left: 4px solid #e67e22;
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
.summary-section {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 1rem;
  margin-bottom: 1.5rem;
}

.summary-card {
  background: white;
  border-radius: 8px;
  padding: 1.25rem;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
}

.summary-card h2 {
  margin: 0 0 1rem 0;
  font-size: 1.1rem;
  color: #1a1a2e;
}

.summary-bars {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}

.summary-bar {
  display: flex;
  align-items: center;
  gap: 0.75rem;
}

.summary-bar-label {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  min-width: 120px;
  font-size: 0.9rem;
}

.status-dot {
  width: 10px;
  height: 10px;
  border-radius: 50%;
}

.status-dot.operational { background: #27ae60; }
.status-dot.failure { background: #e74c3c; }
.status-dot.maintenance { background: #f39c12; }

.summary-bar-track {
  flex: 1;
  height: 8px;
  background: #e0e0e0;
  border-radius: 4px;
  overflow: hidden;
}

.summary-bar-fill {
  height: 100%;
  border-radius: 4px;
  transition: width 0.5s ease;
}

.summary-bar-fill.torniquete { background: #3498db; }
.summary-bar-fill.transbank { background: #9b59b6; }
.summary-bar-fill.operational { background: #27ae60; }
.summary-bar-fill.failure { background: #e74c3c; }
.summary-bar-fill.maintenance { background: #f39c12; }

.summary-bar-count {
  font-weight: 600;
  min-width: 30px;
  text-align: right;
}

/* Main Grid */
.main-grid {
  display: grid;
  grid-template-columns: 1fr 320px;
  gap: 1.5rem;
}

/* Equipments Section */
.equipments-section {
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

.equipments-table {
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

.row-failure {
  background: #fff5f5;
}

.equipment-name {
  font-weight: 600;
  color: #1a1a2e;
}

.type-badge {
  padding: 0.25rem 0.5rem;
  border-radius: 4px;
  font-size: 0.75rem;
  font-weight: 600;
}

.type-badge.torniquete { background: #e8f4fd; color: #3498db; }
.type-badge.transbank { background: #f3e8fd; color: #9b59b6; }

.status-badge {
  padding: 0.25rem 0.5rem;
  border-radius: 4px;
  font-size: 0.75rem;
  text-transform: capitalize;
}

.status-operational { background: #e8f8f0; color: #27ae60; }
.status-failure { background: #fde8e8; color: #e74c3c; }
.status-maintenance { background: #fef9e7; color: #b7950b; }

.failure-count {
  font-weight: 600;
  color: #e74c3c;
}

.uptime-bar {
  position: relative;
  height: 20px;
  background: #e0e0e0;
  border-radius: 10px;
  min-width: 100px;
  overflow: hidden;
}

.uptime-fill {
  height: 100%;
  border-radius: 10px;
  transition: width 0.5s ease;
}

.uptime-excellent { background: #27ae60; }
.uptime-good { background: #3498db; }
.uptime-warning { background: #f39c12; }
.uptime-critical { background: #e74c3c; }

.uptime-text {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  font-size: 0.75rem;
  font-weight: 600;
  color: #333;
}

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
  font-size: 0.8rem;
}

.btn-action:hover {
  transform: scale(1.05);
}

.btn-view { background: #e8f4fd; color: #3498db; }
.btn-schedule { background: #fef9e7; color: #b7950b; }

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