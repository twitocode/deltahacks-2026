# Google Cloud Run Deployment

Quick setup guide for deploying the Beacon.ai backend to Google Cloud Run.

## Prerequisites

1. **Google Cloud SDK** installed

   ```bash
   # Install if needed
   curl https://sdk.cloud.google.com | bash
   ```

2. **Docker** installed and running

3. **Authenticate with Google Cloud**

   ```bash
   gcloud auth login
   gcloud auth configure-docker
   ```

4. **Set your project**
   ```bash
   gcloud config set project YOUR_PROJECT_ID
   ```

## Quick Deploy

```bash
cd backend
./deploy.sh YOUR_PROJECT_ID us-central1
```

## Manual Deployment Steps

### 1. Build the Docker Image

```bash
docker build -t gcr.io/YOUR_PROJECT_ID/beacon-ai-backend .
```

### 2. Push to Container Registry

```bash
docker push gcr.io/YOUR_PROJECT_ID/beacon-ai-backend
```

### 3. Deploy to Cloud Run

```bash
gcloud run deploy beacon-ai-backend \
  --image gcr.io/YOUR_PROJECT_ID/beacon-ai-backend \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --memory 2Gi \
  --cpu 2 \
  --timeout 300 \
  --max-instances 10 \
  --port 8080
```

## Configuration

- **Memory**: 2Gi (required for terrain processing)
- **CPU**: 2 cores (parallel agent simulation)
- **Timeout**: 300s (5 min for complex simulations)
- **Port**: 8080 (standard Cloud Run port)

## Environment Variables (Optional)

Set via `--set-env-vars` flag:

- `NUM_AGENTS`: Number of simulation agents (default: 1000)
- `MAX_RADIUS_KM`: Maximum search radius (default: 20)
- `DEM_DATA_PATH`: Path to DEM tiles (default: /app/data)

## Notes

⚠️ **DEM Data**: The current setup doesn't include DEM tiles in the container. For full functionality, you'll need to either:

- Mount DEM data from Cloud Storage
- Include tiles in the Docker build
- Use the mock data mode (automatic fallback)

## Testing Deployment

```bash
# Get the service URL
SERVICE_URL=$(gcloud run services describe beacon-ai-backend --region us-central1 --format 'value(status.url)')

# Test health endpoint
curl ${SERVICE_URL}/api/health

# Test search endpoint
curl -X POST ${SERVICE_URL}/api/v1/search \
  -H "Content-Type: application/json" \
  -d '{
    "latitude": 48.3562,
    "longitude": -120.6848,
    "age": 35,
    "experience": "novice"
  }'
```
