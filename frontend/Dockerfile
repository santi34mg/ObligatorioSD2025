# Etapa 1: Construir la aplicación
FROM node:20-alpine AS build

WORKDIR /app
COPY package*.json ./
RUN npm install
COPY . .
RUN npm run build

# Etapa 2: Servir con Nginx
FROM nginx:alpine

# Copiar los archivos de build a Nginx
COPY --from=build /app/dist /usr/share/nginx/html

# Copiar configuración de Nginx si tienes un custom.conf
# COPY nginx.conf /etc/nginx/conf.d/default.conf

EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
