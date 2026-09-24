# Notifier Platform

Plataforma multi-canal de notificaciones. Envía emails, SMS, WhatsApp, Push y notificaciones en tiempo real (WebSocket/InApp) desde una única API REST, con soporte para plantillas, programación de envíos y gestión de proveedores por organización.

---

## Contenido

- [Arquitectura](#arquitectura)
- [Funcionalidades](#funcionalidades)
- [Stack tecnológico](#stack-tecnológico)
- [Inicio rápido con Docker](#inicio-rápido-con-docker)
- [Desarrollo local](#desarrollo-local)
- [Variables de entorno](#variables-de-entorno)
- [API](#api)
- [Canales y proveedores](#canales-y-proveedores)
- [WebSocket en tiempo real](#websocket-en-tiempo-real)
- [Panel de administración](#panel-de-administración)
- [Frontend](#frontend)

---

## Arquitectura

```
┌────────────────────────────────────────────────────────┐
│                      Cliente / Frontend                │
│              Angular SPA  ·  WebSocket                 │
└──────────────────────┬─────────────────────────────────┘
                       │ HTTP / WS
                  ┌────▼─────┐
                  │  Nginx   │  :4200 (proxy)
                  └────┬─────┘
                       │
          ┌────────────▼────────────┐
          │   Django + Channels     │  :8000
          │   REST API  ·  ASGI/WS  │
          └──────┬──────────┬───────┘
                 │          │
         ┌───────▼──┐  ┌────▼──────────────┐
         │ PostgreSQL│  │  Celery Workers   │
         │    :5432  │  │  (6 queues)       │
         └───────────┘  └────────┬──────────┘
                                 │
                         ┌───────▼───────┐
                         │     Redis     │  :6379
                         │  broker · WS  │
                         └───────────────┘
```

**Servicios Docker:**

| Servicio        | Imagen                 | Puerto | Rol                                       |
|-----------------|------------------------|--------|-------------------------------------------|
| `db`            | postgres:16-alpine     | 5432   | Base de datos principal                   |
| `redis`         | redis:7-alpine         | 6379   | Broker Celery + capa WebSocket            |
| `backend`       | Django (Python 3.12)   | 8000   | API REST + ASGI (uvicorn, 4 workers)      |
| `celery_worker` | Django                 | —      | Procesamiento async (6 queues, 4 workers) |
| `celery_beat`   | Django                 | —      | Scheduler de tareas programadas           |
| `frontend`      | Nginx + Angular        | 4200   | SPA + proxy inverso                       |

---

## Funcionalidades

- **Multi-canal:** EMAIL, SMS, WHATSAPP, PUSH y WEBSOCKET/INAPP en una sola llamada
- **Multi-proveedor:** selecciona el proveedor por canal (SMTP, SendGrid, Twilio, Firebase, Chatwoot)
- **Plantillas:** soporte Jinja2 con variables dinámicas (`{{ nombre }}`)
- **Notificaciones programadas:** via `scheduled_at`
- **Reintentos:** reencola notificaciones con estado FAILED
- **Tiempo real:** WebSocket autenticado por API Key
- **Multi-tenant:** cada organización gestiona sus propios proveedores, plantillas y API Keys
- **Configs cifradas:** credenciales de proveedores almacenadas con Fernet (AES-128-CBC)
- **Admin panel:** Django Admin para gestión interna
- **OpenAPI:** esquema generado automáticamente en `/api/docs/`

---

## Stack tecnológico

| Capa         | Tecnología                                          |
|--------------|-----------------------------------------------------|
| API          | Django 5.0 · Django REST Framework 3.15             |
| Async        | Celery 5.3 · Django Channels 4.1 · Redis 7          |
| Base de datos| PostgreSQL 16                                       |
| ASGI         | Uvicorn 0.29 · Gunicorn 22                          |
| Frontend     | Angular 21 · Angular Material 21 · TypeScript 5.9   |
| Infra        | Docker · Docker Compose · Nginx                     |
| Email        | SMTP nativo · SendGrid SDK                          |
| SMS/WA       | Twilio SDK · Chatwoot API                           |
| Push         | Firebase Admin SDK (FCM)                            |
| Cifrado      | cryptography (Fernet)                               |

---

## Inicio rápido con Docker

### Requisitos previos

- Docker Desktop 24+
- Docker Compose v2

### 1. Clonar el repositorio

```bash
git clone <repo-url>
cd notifier-platform
```

### 2. Configurar variables de entorno

```bash
cp notifier-backend/.env.example notifier-backend/.env
```

Edita `notifier-backend/.env` con tus valores (ver [Variables de entorno](#variables-de-entorno)).

El `FIELD_ENCRYPTION_KEY` es obligatorio. Genera uno con:

```python
from cryptography.fernet import Fernet
print(Fernet.generate_key().decode())
```

### 3. Levantar todos los servicios

```bash
docker compose up -d
```

### 4. Crear la base de datos y el superusuario

```bash
docker compose exec backend python manage.py migrate
docker compose exec backend python manage.py createsuperuser
```

### 5. Acceder

| URL                          | Descripción              |
|------------------------------|--------------------------|
| http://localhost:4200        | Frontend Angular         |
| http://localhost:4200/api/   | API REST (via proxy)     |
| http://localhost:4200/admin/ | Django Admin             |
| http://localhost:8000/api/docs/ | Swagger UI            |

---

## Desarrollo local

### Backend

**Requisitos:** Python 3.12+, PostgreSQL, Redis

```bash
cd notifier-backend

# Crear y activar entorno virtual
python -m venv .venv
.venv\Scripts\activate          # Windows
source .venv/bin/activate       # Linux/macOS

# Instalar dependencias
pip install -r requirements/local.txt

# Configurar variables de entorno
cp .env.example .env            # editar con valores locales

# Aplicar migraciones
python manage.py migrate

# Crear superusuario
python manage.py createsuperuser

# Iniciar servidor
python manage.py runserver
```

**Iniciar Celery (en terminal separada):**

```bash
celery -A config.celery worker --loglevel=info -Q default,email,sms,whatsapp,push,websocket
```

**Iniciar Celery Beat (en terminal separada):**

```bash
celery -A config.celery beat --loglevel=info --scheduler django_celery_beat.schedulers:DatabaseScheduler
```

### Frontend

**Requisitos:** Node.js 20+, npm 11+

```bash
cd notifier-frontend
npm install
ng serve --port 4200
```

---

## Variables de entorno

Archivo: `notifier-backend/.env`

```env
# Django
SECRET_KEY=django-insecure-cambia-esto-en-produccion
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1
DJANGO_SETTINGS_MODULE=config.settings.local

# Base de datos
DATABASE_NAME=notifier
DATABASE_USER=postgres
DATABASE_PASSWD=postgres
DATABASE_HOST=localhost        # usar "db" en Docker
DATABASE_PORT=5432

# Redis
REDIS_URL=redis://localhost:6379/0    # usar redis://redis:6379/0 en Docker

# Cifrado de configs de proveedores (obligatorio)
FIELD_ENCRYPTION_KEY=<clave-fernet-base64>

# CORS / CSRF
CORS_ALLOWED_ORIGINS=http://localhost:4200
CSRF_TRUSTED_ORIGINS=http://localhost:4200,http://127.0.0.1:4200

# Opcional
SENTRY_DSN=
```

---

## API

### Autenticación

Todas las peticiones requieren el header:

```
Authorization: Api-Key ntf_<tu-api-key>
```

Las API Keys se crean en el panel de administración o desde el frontend en **Settings → API Keys**.

### Endpoints

#### API Keys

| Método | Endpoint                          | Descripción           |
|--------|-----------------------------------|-----------------------|
| POST   | `/api/v1/auth/api-keys/create/`   | Crear nueva API Key   |
| GET    | `/api/v1/auth/api-keys/`          | Listar API Keys       |
| DELETE | `/api/v1/auth/api-keys/<id>/revoke/` | Revocar API Key    |

#### Notificaciones

| Método | Endpoint                              | Descripción                          |
|--------|---------------------------------------|--------------------------------------|
| GET    | `/api/v1/notifications/`              | Listar notificaciones (filtro: status) |
| POST   | `/api/v1/notifications/send/`         | Enviar notificación                  |
| GET    | `/api/v1/notifications/<id>/`         | Detalle + destinatarios + intentos   |
| POST   | `/api/v1/notifications/<id>/retry/`   | Reintentar notificación fallida      |
| DELETE | `/api/v1/notifications/<id>/cancel/`  | Cancelar notificación en cola        |

**Ejemplo — enviar notificación multi-canal:**

```json
POST /api/v1/notifications/send/
{
  "title": "Bienvenido",
  "message": "Tu cuenta ha sido activada.",
  "priority": "NORMAL",
  "channels": ["EMAIL", "WHATSAPP"],
  "recipients": [
    {
      "name": "Juan García",
      "email": "juan@ejemplo.com",
      "phone": "+573001234567"
    }
  ]
}
```

**Con plantilla:**

```json
{
  "title": "Alerta de seguridad",
  "channels": ["EMAIL"],
  "template_id": "<uuid-plantilla>",
  "template_variables": { "codigo": "123456", "nombre": "Ana" },
  "recipients": [{ "email": "ana@ejemplo.com" }]
}
```

**Programada:**

```json
{
  "title": "Recordatorio",
  "channels": ["SMS"],
  "scheduled_at": "2025-12-31T08:00:00Z",
  "recipients": [{ "phone": "+573001234567" }]
}
```

#### Plantillas

| Método | Endpoint                    | Descripción              |
|--------|-----------------------------|--------------------------|
| GET    | `/api/v1/templates/`        | Listar plantillas activas |
| POST   | `/api/v1/templates/`        | Crear plantilla           |
| GET    | `/api/v1/templates/<id>/`   | Ver plantilla             |
| PUT    | `/api/v1/templates/<id>/`   | Actualizar plantilla      |
| DELETE | `/api/v1/templates/<id>/`   | Eliminar (soft delete)   |

**Estructura de plantilla:**

```json
{
  "name": "Bienvenida",
  "subject": "Bienvenido, {{ nombre }}",
  "body": "Hola {{ nombre }}, tu código es {{ codigo }}.",
  "channel": "EMAIL"
}
```

#### Proveedores

| Método | Endpoint                    | Descripción                      |
|--------|-----------------------------|----------------------------------|
| GET    | `/api/v1/providers/`        | Listar proveedores configurados  |
| POST   | `/api/v1/providers/`        | Agregar proveedor                |
| PUT    | `/api/v1/providers/<id>/`   | Actualizar configuración         |
| DELETE | `/api/v1/providers/<id>/`   | Eliminar proveedor               |

---

## Canales y proveedores

### EMAIL

**SMTP:**
```json
{
  "channel": "EMAIL", "name": "smtp", "is_default": true,
  "config": {
    "EMAIL_HOST": "smtp.gmail.com",
    "EMAIL_PORT": 465,
    "EMAIL_USE_SSL": true,
    "EMAIL_USE_TLS": false,
    "EMAIL_HOST_USER": "tu@gmail.com",
    "EMAIL_HOST_PASSWORD": "contraseña-de-app",
    "DEFAULT_FROM_EMAIL": "tu@gmail.com"
  }
}
```

**SendGrid:**
```json
{
  "channel": "EMAIL", "name": "sendgrid", "is_default": true,
  "config": {
    "api_key": "SG.xxxxxxxxxxxx",
    "DEFAULT_FROM_EMAIL": "noreply@tudominio.com"
  }
}
```

### SMS — Twilio

```json
{
  "channel": "SMS", "name": "twilio", "is_default": true,
  "config": {
    "TWILIO_ACCOUNT_SID": "ACxxxxxxxx",
    "TWILIO_AUTH_TOKEN": "xxxxxxxx",
    "TWILIO_FROM_NUMBER": "+19876543210"
  }
}
```

### WHATSAPP

**Twilio (WhatsApp Business):**
```json
{
  "channel": "WHATSAPP", "name": "twilio", "is_default": true,
  "config": {
    "TWILIO_ACCOUNT_SID": "ACxxxxxxxx",
    "TWILIO_AUTH_TOKEN": "xxxxxxxx",
    "TWILIO_FROM_NUMBER": "+14155238886"
  }
}
```

**Chatwoot** (alternativa — enruta mensajes a través de un inbox de Chatwoot):
```json
{
  "channel": "WHATSAPP", "name": "chatwoot", "is_default": true,
  "config": {
    "CHATWOOT_BASE_URL": "https://app.chatwoot.com",
    "CHATWOOT_ACCOUNT_ID": "1",
    "CHATWOOT_INBOX_ID": "5",
    "CHATWOOT_API_TOKEN": "tu-token"
  }
}
```

> Con Chatwoot los agentes de soporte pueden ver el historial y responder las notificaciones de WhatsApp desde la misma plataforma.

### PUSH — Firebase FCM

```json
{
  "channel": "PUSH", "name": "firebase", "is_default": true,
  "config": {
    "type": "service_account",
    "project_id": "mi-proyecto",
    "private_key_id": "xxxxx",
    "private_key": "-----BEGIN PRIVATE KEY-----\n...",
    "client_email": "firebase-adminsdk@mi-proyecto.iam.gserviceaccount.com",
    "client_id": "123456789"
  }
}
```

El destinatario debe incluir el campo `push_token`:
```json
{ "name": "Usuario", "push_token": "ExponentPushToken[xxx]" }
```

### WEBSOCKET / INAPP

No requiere proveedor. El mensaje se entrega en tiempo real al cliente conectado vía WebSocket.

---

## WebSocket en tiempo real

### Conexión

```
ws://localhost:8000/ws/notifications/?api_key=ntf_<tu-api-key>
```

### Eventos recibidos

```json
{
  "type": "notification",
  "data": {
    "id": "uuid",
    "title": "Mensaje de prueba",
    "message": "Contenido",
    "priority": "NORMAL",
    "timestamp": "2025-01-01T12:00:00Z"
  }
}
```

### Ejemplo JavaScript

```js
const ws = new WebSocket('ws://localhost:8000/ws/notifications/?api_key=ntf_xxx');

ws.onmessage = ({ data }) => {
  const { type, data: payload } = JSON.parse(data);
  if (type === 'notification') {
    console.log('Nueva notificación:', payload.title);
  }
};
```

---

## Panel de administración

Accede en `http://localhost:4200/admin/` con las credenciales del superusuario.

Desde el Admin puedes:
- Gestionar organizaciones y generar API Keys (botón **Generar nueva API Key**)
- Ver y editar proveedores con validación de configuración por tipo
- Consultar notificaciones, destinatarios e intentos de entrega
- Gestionar plantillas
- Ver audit logs

---

## Frontend

SPA Angular disponible en `http://localhost:4200`.

| Ruta                    | Página                                                      |
|-------------------------|-------------------------------------------------------------|
| `/dashboard`            | Métricas y notificaciones recientes                         |
| `/notifications`        | Lista con filtro por estado                                 |
| `/notifications/send`   | Formulario de envío (canales, destinatarios, programación)  |
| `/notifications/:id`    | Detalle: destinatarios, intentos por canal y estado         |
| `/templates`            | Gestión de plantillas                                       |
| `/settings/api-keys`    | Crear y revocar API Keys                                    |
| `/settings/providers`   | Configurar proveedores por canal                            |

El formulario de envío adapta los campos de destinatario según los canales seleccionados:
- EMAIL → muestra campo **Email**
- SMS / WHATSAPP → muestra campo **Teléfono**
- PUSH → muestra campo **Push Token (FCM)**
- WEBSOCKET / INAPP → muestra campo **App User ID**

---

## Colección Postman

Importa `notifier-platform.postman_collection.json` (raíz del repositorio) para tener todos los endpoints preconfigurados con ejemplos para cada proveedor y canal.

---

## Licencia

MIT
