# Notifier — Backend

API REST + WebSocket para envío de notificaciones transaccionales.  
Stack: Django 5, DRF, Celery, Django Channels, SQLite (dev) / PostgreSQL (prod).

---

## Requisitos

- Python 3.12 o 3.13
- pip
- Redis (solo si quieres WebSocket real en local; no requerido para el API básica)

---

## Configuración inicial

### 1. Crear entorno virtual

```bash
cd notifier-backend
python -m venv .venv

# Windows
.venv\Scripts\activate

# macOS / Linux
source .venv/bin/activate
```

### 2. Instalar dependencias

```bash
pip install -r requirements/development.txt
```

### 3. Variables de entorno

El archivo `.env` ya existe con valores para desarrollo. Si no lo tienes, créalo:

```bash
cp .env.example .env   # o crea .env manualmente
```

Contenido mínimo para desarrollo local:

```env
SECRET_KEY=django-insecure-notifier-dev-key-change-in-production
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1
DJANGO_SETTINGS_MODULE=config.settings.development
FIELD_ENCRYPTION_KEY=<genera uno con el comando de abajo>
CORS_ALLOWED_ORIGINS=http://localhost:4200
```

Generar `FIELD_ENCRYPTION_KEY`:

```bash
python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
```

### 4. Migraciones

```bash
python manage.py migrate
```

Usa SQLite en desarrollo — no necesitas PostgreSQL corriendo localmente.

### 5. Crear superusuario (para acceder al admin)

```bash
python manage.py createsuperuser
```

---

## Levantar el servidor

```bash
python manage.py runserver
```

El servidor queda disponible en `http://localhost:8000`.

| URL                                 | Descripción           |
| ----------------------------------- | --------------------- |
| `http://localhost:8000/admin/`      | Django Admin          |
| `http://localhost:8000/api/docs/`   | Swagger UI            |
| `http://localhost:8000/api/schema/` | OpenAPI schema (JSON) |

---

## Flujo básico de uso

### 1. Crear una Organization en el admin

Ve a `http://localhost:8000/admin/` → Organizations → Agregar.

### 2. Generar una API Key

```bash
curl -X POST http://localhost:8000/api/v1/auth/api-keys/create/ \
  -H "Content-Type: application/json" \
  -d '{"name": "Mi primera key"}'
```

> **Importante:** la `raw_key` (`ntf_...`) se muestra solo en esta respuesta. Guárdala.

### 3. Enviar una notificación

```bash
curl -X POST http://localhost:8000/api/v1/notifications/send/ \
  -H "Authorization: Api-Key ntf_TUKEY" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Bienvenido",
    "message": "Hola desde Notifier",
    "channels": ["WEBSOCKET"],
    "recipients": [
      {"name": "Fabio", "email": "fabio@example.com", "app_user_id": "user-1"}
    ]
  }'
```

---

## Celery (procesamiento asíncrono)

Para que las notificaciones se envíen de verdad necesitas Redis y Celery corriendo.

### Instalar Redis localmente

- **Windows**: usa [Redis via WSL](https://redis.io/docs/install/install-redis/install-redis-on-windows/) o Docker: `docker run -p 6379:6379 redis:7-alpine`
- **macOS**: `brew install redis && brew services start redis`
- **Linux**: `sudo apt install redis-server && sudo systemctl start redis`

Actualiza `.env` para apuntar a Redis:

```env
REDIS_URL=redis://localhost:6379/0
```

### Levantar el worker

```bash
# En otra terminal (con el venv activado)
celery -A config.celery worker --loglevel=info -Q default,email,websocket
```

### Levantar el beat (notificaciones programadas)

```bash
celery -A config.celery beat --loglevel=info
```

---

## WebSocket (tiempo real)

Con Redis corriendo y `CHANNEL_LAYERS` configurado con Redis (no InMemory), conecta desde el browser:

```js
const ws = new WebSocket(
  "ws://localhost:8000/ws/notifications/?api_key=ntf_TUKEY&user_id=user-1",
);
ws.onmessage = (e) => console.log(JSON.parse(e.data));
```

> En desarrollo local con `InMemoryChannelLayer` (predeterminado), los mensajes WebSocket solo funcionan si el sender y el receiver están en el mismo proceso (no escala a múltiples workers, pero sirve para probar).

---

## Pruebas unitarias

```bash
# Correr todos los tests
pytest

# Con cobertura
pytest --cov=apps --cov-report=term-missing

# Un módulo específico
pytest apps/notifications/tests/test_views.py -v
```

Los tests usan SQLite + `InMemoryChannelLayer` — no requieren PostgreSQL ni Redis.

---

## Configurar un proveedor de email (opcional)

Para que el canal `EMAIL` funcione, crea un Provider desde el admin o via API:

```bash
curl -X POST http://localhost:8000/api/v1/providers/ \
  -H "Authorization: Api-Key ntf_TUKEY" \
  -H "Content-Type: application/json" \
  -d '{
    "channel": "EMAIL",
    "name": "smtp",
    "is_default": true,
    "config": {
      "host": "smtp.gmail.com",
      "port": 587,
      "username": "tu@gmail.com",
      "password": "tu-app-password",
      "use_tls": true,
      "from_email": "tu@gmail.com"
    }
  }'
```

---

## Estructura del proyecto

```
notifier-backend/
├── apps/
│   ├── authentication/     # API Key auth + endpoints
│   ├── organizations/      # Organization + ApiKey models
│   ├── users/              # Custom User model
│   ├── notifications/      # Notification, Recipient, DeliveryAttempt
│   ├── templates/          # Template con variables {{var}}
│   ├── delivery/           # EmailChannel, WebSocketChannel (strategy pattern)
│   ├── providers/          # Configuración cifrada por proveedor
│   ├── websocket/          # Consumer, middleware, routing
│   └── audit/              # AuditLog
├── config/
│   ├── settings/
│   │   ├── base.py
│   │   ├── development.py  # SQLite + InMemoryChannelLayer
│   │   └── production.py   # PostgreSQL + Redis
│   ├── asgi.py
│   ├── celery.py
│   └── urls.py
├── requirements/
│   ├── base.txt
│   └── development.txt
├── .env
├── manage.py
└── pytest.ini
```

fabio crdoba
