# 🐳 Docker Deployment Guide

## Voraussetzungen

- Docker installiert (https://docs.docker.com/get-docker/)
- Docker Compose installiert (bei Docker Desktop inklusive)

## Schnellstart mit Docker Compose (EMPFOHLEN)

### 1. Vorbereitung

```bash
# Repository klonen oder entpacken
cd discord_log_bot

# .env Datei erstellen
cp .env.example .env
nano .env  # Oder ein anderer Editor

# credentials.json platzieren
# Stelle sicher, dass credentials.json im Hauptverzeichnis liegt
```

### 2. Starten

```bash
# Build und Start
docker-compose up -d

# Logs anzeigen
docker-compose logs -f

# Status checken
docker-compose ps
```

### 3. Verwalten

```bash
# Stoppen
docker-compose stop

# Starten
docker-compose start

# Neu starten
docker-compose restart

# Stoppen und entfernen
docker-compose down

# Neu bauen nach Code-Änderungen
docker-compose up -d --build
```

## Manuelles Docker Build

### Build

```bash
docker build -t discord-log-bot .
```

### Run

```bash
docker run -d \
  --name discord-log-bot \
  --env-file .env \
  -v $(pwd)/credentials.json:/app/credentials.json:ro \
  --restart unless-stopped \
  discord-log-bot
```

### Verwalten

```bash
# Logs
docker logs -f discord-log-bot

# Stoppen
docker stop discord-log-bot

# Starten
docker start discord-log-bot

# Entfernen
docker rm discord-log-bot
```

## Production Setup

### Mit Docker Swarm

```bash
# Swarm initialisieren
docker swarm init

# Secret für credentials.json
cat credentials.json | docker secret create credentials_json -

# Service erstellen
docker service create \
  --name discord-bot \
  --secret credentials_json \
  --env-file .env \
  --replicas 1 \
  --restart-condition on-failure \
  discord-log-bot
```

### Mit Kubernetes

Erstelle `k8s-deployment.yaml`:

```yaml
apiVersion: v1
kind: Secret
metadata:
  name: bot-secrets
type: Opaque
stringData:
  .env: |
    DISCORD_TOKEN=your_token
    SPREADSHEET_ID=your_id
---
apiVersion: v1
kind: ConfigMap
metadata:
  name: bot-config
data:
  credentials.json: |
    {your_credentials_json_content}
---
apiVersion: apps/v1
kind: Deployment
metadata:
  name: discord-bot
spec:
  replicas: 1
  selector:
    matchLabels:
      app: discord-bot
  template:
    metadata:
      labels:
        app: discord-bot
    spec:
      containers:
      - name: bot
        image: discord-log-bot:latest
        envFrom:
        - secretRef:
            name: bot-secrets
        volumeMounts:
        - name: credentials
          mountPath: /app/credentials.json
          subPath: credentials.json
      volumes:
      - name: credentials
        configMap:
          name: bot-config
```

Deploy:
```bash
kubectl apply -f k8s-deployment.yaml
```

## Docker Hub Deployment

### Image auf Docker Hub pushen

```bash
# Login
docker login

# Tag
docker tag discord-log-bot yourusername/discord-log-bot:latest

# Push
docker push yourusername/discord-log-bot:latest
```

### Von Docker Hub pullen

```bash
docker pull yourusername/discord-log-bot:latest

docker run -d \
  --name discord-log-bot \
  --env-file .env \
  -v $(pwd)/credentials.json:/app/credentials.json:ro \
  yourusername/discord-log-bot:latest
```

## Portainer Integration

**Portainer** ist ein GUI für Docker Management.

### Installation

```bash
docker volume create portainer_data

docker run -d \
  -p 9000:9000 \
  --name portainer \
  --restart=always \
  -v /var/run/docker.sock:/var/run/docker.sock \
  -v portainer_data:/data \
  portainer/portainer-ce
```

Dann: http://localhost:9000

### Bot in Portainer deployen

1. Gehe zu "Containers" → "Add container"
2. Name: `discord-log-bot`
3. Image: `discord-log-bot:latest`
4. Volumes:
   - Container: `/app/credentials.json`
   - Host: `path/to/credentials.json`
5. Environment Variables: Aus .env einfügen
6. Restart Policy: `unless-stopped`
7. Deploy!

## Monitoring

### Docker Stats

```bash
# Real-time stats
docker stats discord-log-bot

# Einmalig
docker stats --no-stream discord-log-bot
```

### Logs exportieren

```bash
# Letzte 100 Zeilen
docker logs --tail 100 discord-log-bot

# In Datei speichern
docker logs discord-log-bot > bot-logs.txt

# Live mit Timestamp
docker logs -f --timestamps discord-log-bot
```

### Health Check

```bash
# Status checken
docker inspect --format='{{.State.Health.Status}}' discord-log-bot

# Health Check manuell
docker exec discord-log-bot python -c "print('Bot is running!')"
```

## Troubleshooting

### Container startet nicht

```bash
# Logs checken
docker logs discord-log-bot

# Häufige Probleme:
# 1. .env fehlt oder falsch
# 2. credentials.json nicht gemountet
# 3. Port-Konflikt
```

### Memory Issues

```bash
# Memory Limit setzen
docker run -d \
  --name discord-log-bot \
  --memory="512m" \
  --memory-swap="1g" \
  discord-log-bot
```

In docker-compose.yml:
```yaml
deploy:
  resources:
    limits:
      memory: 512M
```

### Permissions

```bash
# credentials.json Permissions
chmod 644 credentials.json

# Wenn Volume Mount nicht funktioniert
docker run -d \
  --name discord-log-bot \
  --user $(id -u):$(id -g) \
  -v $(pwd)/credentials.json:/app/credentials.json:ro \
  discord-log-bot
```

### Clean Up

```bash
# Alle gestoppten Container entfernen
docker container prune

# Unbenutzte Images entfernen
docker image prune -a

# Alle unbenutzten Daten entfernen
docker system prune -a --volumes
```

## Multi-Stage Build (Optimiert)

Für kleinere Images, erstelle `Dockerfile.optimized`:

```dockerfile
# Build Stage
FROM python:3.11-slim as builder

WORKDIR /app

COPY requirements.txt .
RUN pip install --user --no-cache-dir -r requirements.txt

# Runtime Stage
FROM python:3.11-slim

WORKDIR /app

# Kopiere nur die installierten Packages
COPY --from=builder /root/.local /root/.local
ENV PATH=/root/.local/bin:$PATH

COPY bot.py .
COPY credentials.json .

CMD ["python", "-u", "bot.py"]
```

Build:
```bash
docker build -f Dockerfile.optimized -t discord-log-bot:slim .
```

## Best Practices

1. **Secrets Management**
   ```bash
   # Nie Secrets im Image
   # Immer als Environment Variables oder Volumes
   docker run -d \
     --env DISCORD_TOKEN \
     --env SPREADSHEET_ID \
     discord-log-bot
   ```

2. **Resource Limits**
   ```yaml
   deploy:
     resources:
       limits:
         cpus: '0.5'
         memory: 512M
   ```

3. **Logging**
   ```yaml
   logging:
     driver: "json-file"
     options:
       max-size: "10m"
       max-file: "3"
   ```

4. **Updates**
   ```bash
   # Code ändern
   git pull
   
   # Neu bauen
   docker-compose build
   
   # Neu starten
   docker-compose up -d
   ```

5. **Backups**
   ```bash
   # Container committen
   docker commit discord-log-bot discord-log-bot:backup
   
   # Image speichern
   docker save discord-log-bot:backup > backup.tar
   
   # Image laden
   docker load < backup.tar
   ```

## Docker mit CI/CD

### GitHub Actions

`.github/workflows/docker.yml`:

```yaml
name: Docker Build & Push

on:
  push:
    branches: [ main ]

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v2
    
    - name: Login to Docker Hub
      uses: docker/login-action@v1
      with:
        username: ${{ secrets.DOCKER_USERNAME }}
        password: ${{ secrets.DOCKER_PASSWORD }}
    
    - name: Build and push
      uses: docker/build-push-action@v2
      with:
        context: .
        push: true
        tags: yourusername/discord-log-bot:latest
```

---

**Docker Deployment = Production Ready! 🚀**
