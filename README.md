# Home Chef Marketplace

Production-oriented marketplace for Egyptian home chefs. Customers discover chefs and meals, choose a pickup time, order for pickup, and communicate entirely inside the platform.

## Stack

- Frontend: React 19, TypeScript, Vite, Tailwind CSS, React Router, TanStack Query, Zustand, Axios, React Hook Form, Zod, Framer Motion
- Backend: Django 5.2, Django REST Framework, PostgreSQL, Redis, Django Channels, SimpleJWT
- Media: Cloudinary in configured environments, local storage fallback for development
- Deployment: Docker Compose, Daphne ASGI, Nginx

## Architecture

Frontend server state is owned by TanStack Query. Zustand is restricted to authentication and UI preferences. Forms use React Hook Form with Zod schemas. Route pages are lazy-loaded.

The backend is split into domain apps (`users`, `sellers`, `products`, `orders`, `chat`, `notifications`, etc.). REST and WebSocket transports share the same models and permissions. Redis backs both Django cache and the production Channels layer.

No customer-facing API exposes chef email or phone details.

## Quick start with Docker

Copy `.env.example` to `.env`, set a strong `DJANGO_SECRET_KEY`, then:

```bash
docker compose up --build
docker compose exec backend python manage.py seed_marketplace
```

- Application: <http://localhost:5173>
- API documentation: <http://localhost:8000/api/docs/>
- Django admin: <http://localhost:8000/admin/>

Docker starts PostgreSQL, Redis, Daphne, and Nginx.

## Local development

Requirements: Python 3.11+ and Node.js 20.19+ or 22.12+.

Backend:

```powershell
cd backend
python -m venv .venv
.\.venv\Scripts\python -m pip install -r requirements.txt
$env:USE_SQLITE="True"
$env:USE_REDIS="False"
.\.venv\Scripts\python manage.py migrate
.\.venv\Scripts\python manage.py seed_marketplace
.\.venv\Scripts\python manage.py runserver
```

Frontend:

```powershell
cd frontend
npm install
npm run dev
```

Vite proxies `/api` and `/ws` to Django during development.

## Authentication

- Register with a unique email
- One-time email verification
- Login only after verification
- JWT access and rotating refresh tokens
- Refresh-token blacklist on logout
- Enumeration-safe forgot-password flow
- One-time password reset tokens
- Customer, chef, and admin route permissions
- Chef accounts activate immediately after email verification and can publish meals without manual review

Development writes emails to the backend console. Configure SMTP variables for production.

## Orders and commission

- Orders are collected directly from the chef; delivery is not offered by the platform.
- Every order stores the selected pickup time and a snapshot of the chef's pickup address.
- The customer pays the displayed meal total with no additional platform fee.
- The platform commission defaults to 10% and is deducted from the chef's earnings.
- Each order stores its commission rate, platform fee, and seller earnings as an
  accounting snapshot. Configure future orders with `PLATFORM_COMMISSION_RATE`.

Suggestions from customers and chefs are stored in the database and sent to
`SUGGESTIONS_EMAIL` (defaults to `elnono55555@gmail.com`). To deliver them to
Gmail instead of the development console, configure `EMAIL_BACKEND` as
`django.core.mail.backends.smtp.EmailBackend`, use `smtp.gmail.com` on port
`587`, and provide a sender account plus a Gmail app password through
`EMAIL_HOST_USER` and `EMAIL_HOST_PASSWORD`.

## Real-time transport

- `/ws/notifications/`
- `/ws/orders/<order-id>/chat/`

The access token is sent as a WebSocket subprotocol so it does not appear in proxy access logs. Access is checked against the authenticated user and order participants. REST remains available as a reconnect fallback.

## صنعتى support chat

Every authenticated customer and chef can open `/support` from the floating
**صنعتى Support** button to ask a question or submit a private complaint.
Administrators use the same page to search support conversations, reply, and
close or reopen complaints. New messages notify the other side, and the
support inbox refreshes automatically.

## Cloudinary

Set `CLOUDINARY_URL=cloudinary://API_KEY:API_SECRET@CLOUD_NAME`. When omitted, development uses local media storage. Secrets are never sent to the browser.

All newly uploaded images are resized and compressed before storage. WebP is the
default; set `MEDIA_IMAGE_FORMAT=AVIF` to use AVIF when the installed Pillow build
provides an AVIF encoder. Quality and maximum dimensions are controlled by
`MEDIA_IMAGE_QUALITY` and `MEDIA_MAX_IMAGE_DIMENSION`.

## Intelligent discovery

- `GET /api/v1/products/ai-search/?q=...` parses natural-language food, price,
  rating, category, and Egyptian location intent.
- `GET /api/v1/products/recommendations/` returns authenticated, explainable
  chef and meal recommendations using favorites, orders, ratings, searches,
  trends, location, and collaborative signals.

Recommendation results are cached briefly and automatically invalidated when
the customer's behavioral signals change.

## Quality checks

```powershell
cd backend
$env:USE_SQLITE="True"
$env:USE_REDIS="False"
.\.venv\Scripts\python manage.py check
.\.venv\Scripts\python manage.py makemigrations --check --dry-run
.\.venv\Scripts\python manage.py test
.\.venv\Scripts\python manage.py spectacular --validate --file schema.yml
```

```powershell
cd frontend
npm run lint
npm test
npm run build
npm audit
```

The same checks run in GitHub Actions.

## Production deployment

Create a private `.env` with a random 50+ character `DJANGO_SECRET_KEY`, strong
PostgreSQL password, production hosts/origins, SMTP credentials, Redis, and
Cloudinary. Then run:

```bash
docker compose -f docker-compose.yml -f docker-compose.prod.yml up -d --build
```

Terminate TLS at a trusted reverse proxy or load balancer and point the domain
to the frontend service. Never commit `.env` files. Before launch, create an
administrator, run the test commands above, verify email delivery, upload a
meal image, and complete one pickup order end to end.

The customer-facing terms and privacy pages are available at `/terms` and
`/privacy`.

## Demo data

After `seed_marketplace`:

- Customer: `alaa` / `Password123!`
- Chef: `seller1` / `Password123!`

Create an administrator with `python manage.py createsuperuser`.

Licensed under [MIT](LICENSE).
