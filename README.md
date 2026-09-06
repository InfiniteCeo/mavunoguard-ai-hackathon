# MavunoGuard AI

**MavunoGuard AI: An AI-Powered Climate Risk and Crop Advisory System for Smallholder Farmers.**

This version keeps the existing farm assessment, GPS/Leaflet map, risk scoring, charts, optional AI layer and offline fallback, while repairing the live-data pipeline.

## Live data architecture

- **Weather:** Open-Meteo `/v1/forecast` using the farm latitude/longitude. No API key is required.
- **Satellite discovery:** Copernicus Data Space public STAC search for recent Sentinel-2 L2A scenes.
- **NDVI:** Copernicus Data Space Sentinel Hub Statistical API using Sentinel-2 L2A B04/B08 and an authenticated OAuth client.
- **Frontend:** HTML/CSS/JavaScript with Leaflet and SVG charts.
- **Backend:** FastAPI + httpx.
- **Deployment:** GitHub → Render.

Open-Meteo supports forecasts up to 16 days, including daily precipitation, temperature and precipitation probability. MavunoGuard requests 14 days and also requests hourly 0–1 cm soil moisture, which is aggregated into daily values when available.

## Local run

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn server.app:app --host 0.0.0.0 --port 8000
```

Open `http://127.0.0.1:8000`.

## Render deployment

Build command:

```text
pip install -r requirements.txt
```

Start command:

```text
python -m uvicorn server.app:app --host 0.0.0.0 --port $PORT
```

The included `render.yaml` contains the same deployment settings.

### Render environment variables

Required for weather: **none**.

Optional AI:
- `OPENAI_API_KEY`
- `OPENAI_MODEL`

Sentinel-2:
- `SENTINEL_CLIENT_ID`
- `SENTINEL_CLIENT_SECRET`
- `SENTINEL_TOKEN_URL`
- `SENTINEL_STATS_URL`
- `SATELLITE_MAX_CLOUD`

Use these Sentinel defaults unless you have a deliberate reason to override them:

```text
SENTINEL_TOKEN_URL=https://identity.dataspace.copernicus.eu/auth/realms/CDSE/protocol/openid-connect/token
SENTINEL_STATS_URL=https://sh.dataspace.copernicus.eu/statistics/v1
SATELLITE_MAX_CLOUD=35
```

**Never put Sentinel secrets, OpenAI keys, tokens or passwords in HTML, JavaScript, GitHub, or this ZIP.** Add the secret values only in Render Environment Variables.

## Testing the live weather service

After deployment, open:

```text
https://YOUR-RENDER-DOMAIN/api/health
```

Then test weather for a farm point:

```text
https://YOUR-RENDER-DOMAIN/api/weather?latitude=-0.6752&longitude=34.7888
```

A successful response contains `daily.time`, `daily.precipitation_sum`, `daily.temperature_2m_max`, `daily.precipitation_probability_max`, and other requested values.

For a compact service diagnostic:

```text
https://YOUR-RENDER-DOMAIN/api/diagnostics?latitude=-0.6752&longitude=34.7888
```

## Testing Sentinel-2 / NDVI

First add the Sentinel OAuth client ID and secret to Render. Do not send the secret through ChatGPT.

Then open:

```text
https://YOUR-RENDER-DOMAIN/api/diagnostics?latitude=-0.6752&longitude=34.7888&planting_date=2026-06-01
```

The diagnostic distinguishes:
- `not_configured` — credentials are missing.
- `authenticated` — OAuth succeeded.
- `authentication_failed` — OAuth failed.
- `authenticated_no_observation` — authentication worked but no valid NDVI was returned for the location/time window.
- statistics errors — authentication worked but the statistics request failed.

The main `/api/analyze` response also reports whether weather and Sentinel-2 NDVI were live.

## Online vs offline behavior

The app deliberately distinguishes three states:

1. **Online + live data:** `Live analysis`.
2. **Online + server/live-data failure:** `Live data temporarily unavailable`. Local field inputs are shown, but no fake weather or satellite values are invented.
3. **Genuinely offline:** `Offline farm check`.

The browser's `navigator.onLine` state is therefore not used as proof that an upstream API is healthy.

## Risk scoring

The existing scoring concept is preserved:
- Dryness
- Heavy rain
- Crop stress
- Overall risk

When live weather is available, forecast rainfall/temperature/probability feed the weather risk. When valid Sentinel-2 NDVI is available, its latest value and trend feed vegetation stress. If a live source is unavailable, the system does not invent a measurement.

## Security

Secrets are read only by the FastAPI backend from environment variables. The frontend never receives the Copernicus client secret or OpenAI API key.

## Repository hygiene

The deployment ZIP should contain source files only. `__pycache__`, `.env`, Python bytecode and runtime-generated uploads/database data are excluded.

## Current storage note

Farm history is stored in `data/farms.json`, so this remains appropriate for a demonstration/small deployment. A future multi-user production release should move farm records to PostgreSQL/PostGIS.

## Live-data troubleshooting (v2.3)

### Weather

Open-Meteo requires no API key for this public forecast use. The server requests a 14-day forecast from `https://api.open-meteo.com/v1/forecast`. Core weather variables are requested separately from optional soil moisture, so an optional soil variable cannot suppress rainfall/temperature data.

Test the deployed service:

`GET /api/weather?latitude=-0.6753&longitude=34.7890`

For a safe end-to-end diagnostic:

`GET /api/diagnostics?latitude=-0.6753&longitude=34.7890&planting_date=2026-06-01`

The diagnostic response reports whether Open-Meteo was reached, how many forecast days were returned, and (without exposing secrets) whether Sentinel OAuth/statistics succeeded.

### Sentinel-2

Configure these only in the Render Environment settings:

- `SENTINEL_CLIENT_ID`
- `SENTINEL_CLIENT_SECRET`

The public configuration values are:

- `SENTINEL_TOKEN_URL=https://identity.dataspace.copernicus.eu/auth/realms/CDSE/protocol/openid-connect/token`
- `SENTINEL_STATS_URL=https://sh.dataspace.copernicus.eu/statistics/v1`
- `SATELLITE_MAX_CLOUD=35`

The frontend never receives the Sentinel client secret.

### Service worker

API requests are deliberately excluded from service-worker caching. This prevents an old `/api/weather` or `/api/diagnostics` response from being reused after deployment. The application cache version is incremented whenever the service-worker behavior changes.


## v2.6 Hackathon upgrade
- Robust weather retrieval: Open-Meteo primary with retries and MET Norway fallback.
- Browser-side weather fallback so a temporary Render outbound/API issue does not blank the rainfall graph.
- No fake 0 mm / 0°C values when weather is unavailable.
- Dynamic weather-provider labels and diagnostics.
- Safer Open-Meteo request using stable core daily variables; optional soil moisture cannot break the forecast.
- Fixed/strengthened Sentinel-2 scene-search fallback for catalogue HTTP 400 responses.
- Crop-specific practical guidance for maize, beans, sorghum, Irish potato, banana and vegetables.
- Visual “Why am I at risk?” driver bars.
- Plain-language “Vegetation story” using Sentinel-2 NDVI and trend.
- Local farm history and comparison of recent assessments.
- Offline/local fallback clearly distinguishes field-only results from live analysis.
- Service-worker cache version bumped so deployed browsers can receive the new build.

### Deployment
Upload the contents of this folder to a new GitHub repository and connect that repository to Render. Do not upload `.env` or secrets. Render environment variables remain required for OpenAI and Copernicus Sentinel-2 features.
