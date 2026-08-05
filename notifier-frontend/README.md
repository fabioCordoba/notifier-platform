# Notifier — Frontend

Panel de administración para la plataforma Notifier.  
Stack: Angular 21, Angular Material, RxJS.

---

## Requisitos

- Node.js 20 o superior
- npm 10 o superior

Verifica tu versión:

```bash
node -v
npm -v
```

---

## Configuración inicial

### 1. Instalar dependencias

```bash
cd notifier-frontend
npm install
```

### 2. Entorno de desarrollo

El archivo `src/environments/environment.ts` ya apunta al backend local:

```ts
export const environment = {
  production: false,
  apiUrl: 'http://localhost:8000',
  wsUrl: 'ws://localhost:8000',
};
```

No necesitas modificar nada para desarrollo local.

---

## Levantar el servidor de desarrollo

```bash
npm start
```

La app queda disponible en `http://localhost:4200`.

> El backend debe estar corriendo en `http://localhost:8000` para que las peticiones funcionen.

---

## Primer acceso

1. Abre `http://localhost:4200`
2. Ve a **Settings → API Keys**
3. Ingresa tu `Api-Key` (`ntf_...`) generada desde el backend
4. La key se guarda en `localStorage` y se inyecta en cada request automáticamente

---

## Pantallas disponibles

| Ruta | Descripción |
|------|-------------|
| `/dashboard` | Estadísticas globales + lista de notificaciones recientes |
| `/notifications` | Tabla de notificaciones con filtro por estado |
| `/notifications/:id` | Detalle con acordeón por destinatario y árbol de delivery attempts |
| `/notifications/send` | Formulario para enviar una nueva notificación |
| `/templates` | CRUD de plantillas con variables `{{var}}` |
| `/settings/api-keys` | Conectar key existente, generar nuevas, revocar |

---

## WebSocket en tiempo real

El servicio `WebSocketService` se conecta automáticamente cuando tienes una API Key configurada. Para probarlo desde la consola del browser:

```js
const ws = new WebSocket(
  'ws://localhost:8000/ws/notifications/?api_key=ntf_TUKEY&user_id=mi-user-id'
);
ws.onmessage = (e) => console.log(JSON.parse(e.data));
```

---

## Pruebas unitarias

```bash
# Correr tests una vez
npm test -- --no-watch

# Con reporte de cobertura
npm test -- --no-watch --code-coverage
```

Los reportes de cobertura quedan en `coverage/notifier-frontend/index.html`.

### Tests incluidos

| Archivo | Qué verifica |
|---------|-------------|
| `api-key.interceptor.spec.ts` | Header `Authorization` agregado/omitido según localStorage |
| `notification.service.spec.ts` | Llamadas HTTP correctas (URL, método, payload) |
| `websocket.service.spec.ts` | Conexión WS, recepción de mensajes, `markRead`, reconexión automática |

---

## Build de producción

```bash
npm run build -- --configuration production
```

Los archivos compilados quedan en `dist/notifier-frontend/browser/`.

---

## Estructura del proyecto

```
notifier-frontend/src/app/
├── core/
│   ├── interceptors/
│   │   └── api-key.interceptor.ts      # Agrega Authorization a cada request
│   ├── models/
│   │   ├── notification.model.ts
│   │   └── template.model.ts
│   └── services/
│       ├── auth.service.ts             # Gestiona API key (signal)
│       ├── notification.service.ts
│       ├── template.service.ts
│       └── websocket.service.ts        # Reconexión automática cada 5s
├── layout/
│   └── shell/                          # Sidenav + toolbar
└── features/
    ├── dashboard/
    ├── notifications/
    │   ├── list/
    │   ├── detail/
    │   └── send/
    ├── templates/
    └── settings/
        └── api-keys/
```
