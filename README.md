# DeliveryGo Menu Service

FastAPI para consultar los menús de los seis restaurantes, guardados en MongoDB.

## Especificaciones

Consulta la [documentación técnica y funcional](docs/README.md) (SPEC-01 a SPEC-13).

FastAPI + PyMongo + MongoDB. `python -m venv .venv`, activar entorno, `pip install -r requirements.txt`, configurar `.env` tomando `.env.example` y ejecutar `uvicorn app.main:app --reload --port 8082`.

Swagger: `/docs`. Endpoints: `GET /api/v1/menus/{restauranteId}`, `GET /api/v1/menus/{restauranteId}/{productoId}`, `/health/live`, `/health/ready`. Los datos iniciales usan UUID estables compartidos con Restaurant Service; tres pollerías tienen las tres porciones obligatorias. Mongo inicializa índices y semillas idempotentes al iniciar.

Validaciones: `python -m unittest discover -s tests -v`. Prueba de integración del stack: `python integration_smoke.py` desde la carpeta principal con Compose levantado.
