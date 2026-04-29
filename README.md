# DevOps Exercise

Microservicio REST para el ejercicio DevOps. Implementa `/DevOps`, API Key, JWT por transacción, pruebas automatizadas, análisis estático, contenedores, balanceador de carga y pipeline CI/CD.

## Requisitos

- Python 3.11+
- Docker y Docker Compose

## Ejecución local

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements-dev.txt
uvicorn app.main:app --reload
```

Generar un JWT único:

```bash
JWT=$(python scripts/generate_jwt.py --secret change-me-in-production)
```

Probar el endpoint:

```bash
curl -X POST \
  -H "X-Parse-REST-API-Key: 2f5ae96c-b558-4c7b-a590-a501ae1c3f6c" \
  -H "X-JWT-KWY: ${JWT}" \
  -H "Content-Type: application/json" \
  -d '{ "message": "This is a test", "to": "Juan Perez", "from": "Rita Asturia", "timeToLifeSec": 45 }' \
  http://localhost:8000/DevOps
```

Respuesta esperada:

```json
{"message":"Hello Juan Perez your message will be sent"}
```

Cualquier otro método sobre `/DevOps` devuelve:

```text
ERROR
```

## Contenedores y balanceador

El `docker-compose.yml` levanta dos nodos (`app1`, `app2`) y un gateway Nginx como balanceador/API gateway.

```bash
docker compose up --build
```

Endpoint balanceado:

```bash
http://localhost:8080/DevOps
```

## Pruebas y análisis estático

```bash
pip install -r requirements-dev.txt
ruff check .
pytest
```

## Infraestructura

La carpeta `infra/k8s` incluye:

- `deployment.yaml`: despliegue con 2 réplicas.
- `service.yaml`: servicio tipo `LoadBalancer`.
- `hpa.yaml`: escalabilidad dinámica por CPU.

Antes de aplicar en Kubernetes, cambie la imagen `docker.io/DOCKERHUB_USERNAME/devops-api-challenge:latest` por la imagen real publicada en Docker Hub y cree el secreto:

```bash
kubectl create secret generic devops-api-secret \
  --from-literal=api-key=2f5ae96c-b558-4c7b-a590-a501ae1c3f6c \
  --from-literal=jwt-secret=<secret-productivo>
```

## CI/CD

El workflow `.github/workflows/ci-cd.yml` ejecuta automáticamente:

1. Gestión de dependencias.
2. Análisis estático con Ruff.
3. Pruebas con cobertura.
4. Build de imagen Docker.
5. Publicación de imagen en Docker Hub.
6. Etapa de despliegue parametrizada.

La rama `main` o `master` despliega a producción. También soporta ejecución bajo demanda (`workflow_dispatch`) y despliegue por versión/tag (`v*`).

Para publicar imágenes en Docker Hub, configure estos secrets en GitHub:

- `DOCKERHUB_USERNAME`: usuario de Docker Hub.
- `DOCKERHUB_TOKEN`: access token de Docker Hub.

El pipeline publica:

- `${DOCKERHUB_USERNAME}/devops-api-challenge:<commit-sha>`
- `${DOCKERHUB_USERNAME}/devops-api-challenge:latest` en `main` o `master`
- `${DOCKERHUB_USERNAME}/devops-api-challenge:<tag>` cuando se empuja un tag `v*`

## Seguridad

- API Key requerida en `X-Parse-REST-API-Key`.
- JWT requerido en `X-JWT-KWY`.
- El JWT debe estar firmado con `DEVOPS_JWT_SECRET`, incluir `exp`, `iat` y `jti`.
- Cada `jti` se acepta una sola vez por proceso, evitando reuso simple de tokens.
