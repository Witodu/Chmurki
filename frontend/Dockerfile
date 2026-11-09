# --- Etap 1: budowanie aplikacji React ---
FROM node:18-alpine AS build

WORKDIR /app

# Najpierw kopiujemy tylko pliki zależności, by Docker mógł wykorzystać cache
COPY package*.json ./
RUN npm install

# Kopiujemy resztę kodu i budujemy aplikację
COPY . .
RUN npm run build

# --- Etap 2: serwowanie plików statycznych przez nginx ---
FROM nginx:alpine

# Usuwamy domyślną stronę nginx i wkładamy zbudowane pliki z Vite
COPY --from=build /app/dist /usr/share/nginx/html

EXPOSE 80

# Healthcheck: sprawdza czy nginx odpowiada na głównym adresie
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
  CMD wget --no-verbose --tries=1 --spider http://localhost/ || exit 1

CMD ["nginx", "-g", "daemon off;"]