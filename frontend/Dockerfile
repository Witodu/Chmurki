# --- Etap 1: budowanie aplikacji React ---
FROM node:22-slim AS build

WORKDIR /app

# Najpierw kopiujemy tylko pliki zależności, by Docker mógł wykorzystać cache
COPY package*.json ./
RUN npm ci

# Kopiujemy resztę kodu i budujemy aplikację
COPY . .
RUN npm run build

# --- Etap 2: serwowanie plików statycznych przez nginx ---
FROM nginx:alpine

# Własna konfiguracja: proxy /api -> backend + fallback SPA na index.html
COPY nginx.conf /etc/nginx/conf.d/default.conf

# Zbudowane pliki z Vite
COPY --from=build /app/dist /usr/share/nginx/html

EXPOSE 80

# Healthcheck: sprawdza czy nginx odpowiada na głównym adresie
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
  CMD wget --no-verbose --tries=1 --spider http://127.0.0.1/ || exit 1

CMD ["nginx", "-g", "daemon off;"]
