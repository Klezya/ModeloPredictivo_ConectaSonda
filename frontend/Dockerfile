# Frontend Dockerfile - Vue.js con Vite
# Etapa de build
FROM node:22-alpine AS build

WORKDIR /app

# Copiar package files
COPY package*.json ./

# Instalar dependencias
RUN npm install

# Copiar el código fuente
COPY . .

# Argumentos para build time (Vite necesita esto en build, no en runtime)
ARG VITE_API_URL=http://localhost:8000
ARG VITE_ADMIN_USER=admin_user
ARG VITE_ADMIN_PASSWORD=admin_password
ENV VITE_API_URL=$VITE_API_URL
ENV VITE_ADMIN_USER=$VITE_ADMIN_USER
ENV VITE_ADMIN_PASSWORD=$VITE_ADMIN_PASSWORD

# Build de producción
RUN npm run build

# Etapa de producción con nginx
FROM nginx:alpine

# Copiar configuración de nginx
COPY nginx.conf /etc/nginx/conf.d/default.conf

# Copiar archivos compilados desde la etapa de build
COPY --from=build /app/dist /usr/share/nginx/html

# Exponer puerto
EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]
