<!-- filepath: frontend/src/views/HomeView.vue -->
<script setup lang="ts">
import { useRouter } from 'vue-router'

const router = useRouter()

const handleLogout = () => {
  localStorage.removeItem('isAuthenticated')
  router.push({ name: 'login' })
}
</script>

<template>
  <div class="home-container">
    <h1>¡Bienvenido!</h1>
    <p>Has iniciado sesión correctamente.</p>
    <button @click="handleLogout">Cerrar Sesión</button>
  </div>
</template>

<style scoped>
.home-container {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  background: #f5f5f5;
}

h1 {
  color: #333;
}

button {
  padding: 0.75rem 2rem;
  background: #e74c3c;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  margin-top: 1rem;
}

button:hover {
  opacity: 0.9;
}
</style>