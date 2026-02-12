# Builders Stream Pro

[![Version](https://img.shields.io/badge/version-3.0-blue.svg)](https://github.com/yourusername/builders-stream-pro)
[![License](https://img.shields.io/badge/license-Confidential-red.svg)]()
[![Framework](https://img.shields.io/badge/framework-Wasp%20v0.16+-orange.svg)](https://wasp-lang.dev)
[![Stack](https://img.shields.io/badge/stack-React%20%7C%20Node.js%20%7C%20PostgreSQL-green.svg)]()

> **Construction & Renovation Management Platform** - A comprehensive, modular, web-based software platform purpose-built for construction and renovation contractors.

## 🏗️ Overview

Builders Stream Pro is an all-in-one platform that unifies every aspect of the contractor workflow—from initial lead capture and estimating through project execution, financial management, and client delivery—eliminating the need for multiple disconnected software tools.

Built on **Open SaaS** and the **Wasp Framework** (v0.16+), this platform delivers enterprise-grade construction management capabilities with the agility of modern full-stack development.

### Key Features

- **12 Integrated Modules** - Project management, CRM, estimating, scheduling, financials, client portal, and more
- **Multi-Tenant Architecture** - Complete data isolation for each contractor organization
- **Mobile-Native Design** - Built for field operations with offline capability
- **Open Source Foundation** - No framework licensing fees, full code control
- **AI-Ready Architecture** - Optimized for AI-assisted development with declarative DSL

---

## 📋 Table of Contents

- [Technology Stack](#technology-stack)
- [Architecture](#architecture)
- [Core Modules](#core-modules)
- [Getting Started](#getting-started)
- [Installation](#installation)
- [Configuration](#configuration)
- [Development](#development)
- [Deployment](#deployment)
- [API Documentation](#api-documentation)
- [Roadmap](#roadmap)
- [Contributing](#contributing)
- [License](#license)

---

## 🛠️ Technology Stack

### Framework & Core
- **Wasp v0.16+** - Full-stack framework with declarative DSL
- **TypeScript** - Type-safe development across frontend and backend
- **React 18** - Modern UI with Vite bundler
- **Node.js/Express** - Auto-generated backend server
- **PostgreSQL** - Primary database with Prisma ORM
- **TailwindCSS + TailAdmin** - Responsive UI components

### Infrastructure
- **Database**: PostgreSQL 14+ with TimescaleDB extension
- **ORM**: Prisma with auto-generated TypeScript types
- **Authentication**: Wasp Auth (Email, Google OAuth, GitHub OAuth)
- **File Storage**: AWS S3 with CloudFront CDN
- **Payments**: Stripe with Customer Portal integration
- **Background Jobs**: pg-boss (PostgreSQL-backed job queues)
- **Email**: SendGrid/Mailgun integration with React Email templates
- **Analytics**: Plausible Analytics, Sentry error tracking

### Mobile & PWA
- **Progressive Web App** - Service workers for offline capability
- **Responsive Design** - Mobile-first field operations interface
- **Camera Integration** - Photo capture with GPS and timestamp

---

## 🏛️ Architecture

### Multi-Tenant Design

Each contractor organization operates in a fully isolated tenant with:
- Separate data partitions using PostgreSQL Row-Level Security (RLS)
- Prisma middleware for automatic tenant filtering
- Independent Stripe subscriptions per organization
- Role-based access control within each tenant

### Modular System

Contractors activate only the modules they need:

```
┌─────────────────────────────────────────────────┐
│         Project Command Center (Core)           │
└─────────────────────────────────────────────────┘
         ▲                ▲                ▲
         │                │                │
    ┌────┴────┐      ┌────┴────┐     ┌────┴────┐
    │   CRM   │      │Estimate │     │Schedule │
    └─────────┘      └─────────┘     └─────────┘
         │                │                │
    ┌────┴────────────────┴────────────────┴────┐
    │         PostgreSQL Data Layer              │
    └────────────────────────────────────────────┘
```

### main.wasp Configuration

The `main.wasp` file serves as the central nervous system, declaring:
- App metadata and configuration
- Entity definitions (Prisma models)
- Authentication methods
- Routes and pages
- Queries and actions
- Background jobs and cron schedules
- API endpoints

Example structure:
```wasp
app BuildersStreamPro {
  wasp: { version: "^0.16.0" },
  title: "Builders Stream Pro",
  auth: {
    userEntity: User,
    methods: {
      email: { /* ... */ },
      google: {},
      github: {}
    }
  },
  db: { system: PostgreSQL }
}

entity Project {=psl
  id          String   @id @default(uuid())
  name        String
  status      String
  client      Client   @relation(fields: [clientId], references: [id])
  clientId    String
  organization Organization @relation(fields: [organizationId], references: [id])
  organizationId String
  createdAt   DateTime @default(now())
  updatedAt   DateTime @updatedAt
psl=}

route DashboardRoute { path: "/dashboard", to: DashboardPage }
page DashboardPage {
  authRequired: true,
  component: import { Dashboard } from "@client/pages/Dashboard"
}

query getProjects {
  fn: import { getProjects } from "@server/projects",
  entities: [Project, Client, Organization]
}

action createProject {
  fn: import { createProject } from "@server/projects",
  entities: [Project, Client, Organization]
}

job syncQuickBooks {
  executor: PgBoss,
  perform: {
    fn: import { syncQB } from "@server/jobs/quickbooks"
  },
  schedule: {
    cron: "0 */4 * * *"
  }
}
```

---

## 📦 Core Modules

### Module 1: Project Command Center (Core)
- Unified dashboard with real-time project health indicators
- Customizable widgets and KPI tracking
- Project lifecycle management (Lead → Closeout)
- Financial snapshot and schedule overview
- AI-prioritized action items feed

### Module 2: CRM & Lead Management
- Multi-source lead capture (web, phone, email, home shows)
- Sales pipeline with automated follow-ups
- Contact management with interaction timeline
- Marketing automation and email campaigns
- Review management (Google, Yelp, Facebook)

### Module 3: Estimating & Digital Takeoff Engine
- Digital takeoff from plans, photos, or satellite imagery
- Assembly-based cost estimating with historical data
- Proposal and contract generation with e-signature
- Excel/CSV export capabilities
- Aerial measurement integration

### Module 4: Scheduling & Resource Management
- Interactive Gantt chart scheduling
- Drag-and-drop task management
- Resource allocation and crew dispatch
- Equipment tracking with depreciation
- Multi-project capacity planning

### Module 5: Financial Management Suite
- Real-time job costing with variance alerts
- Construction accounting (WIP, A/P, A/R)
- Invoicing (AIA G702/G703 format support)
- QuickBooks Online/Desktop & Xero integration
- Change order and purchase order management

### Module 6: Client Collaboration Portal
- Client-facing project dashboard
- Photo galleries and progress updates
- Selection management with approval workflows
- Online payment portal (Stripe/ACH)
- 3D floor plan visualization

### Module 7: Document & Photo Control
- Version-controlled document management
- RFI and submittal tracking
- Photo management with AI organization
- Before/after pairing and time-lapse generation
- Permit and compliance tracking

### Module 8: Field Operations Hub
- Digital daily logs with weather integration
- Mobile time clock with GPS geofencing
- Expense tracking with photo receipts
- Mileage and equipment hours logging
- Offline-first mobile capability

### Module 9: Quality & Safety Compliance
- Digital inspection checklists
- Deficiency and punch list tracking
- Safety incident reporting
- OSHA compliance forms
- Training record management

### Module 10: Payroll & Workforce Management (NEW)
- Multi-rate payroll with job cost allocation
- Certified payroll (WH-347) and prevailing wage
- Union reporting and fringe benefit tracking
- Employee onboarding and benefits administration
- Direct deposit and tax filing

### Module 11: Service & Warranty Management (NEW)
- Service ticket dispatching and management
- Warranty registration and claim tracking
- Recurring maintenance agreements
- Parts inventory management
- Mobile service technician interface

### Module 12: Analytics & Reporting Engine
- Customizable dashboards with real-time widgets
- Financial reports (P&L, WIP, cash flow)
- Project performance analytics
- Sales pipeline and conversion metrics
- Automated report distribution

---

## 🚀 Getting Started

### Prerequisites

- **Node.js** v18+ and npm/yarn
- **PostgreSQL** 14+
- **Wasp CLI** v0.16+
- **Git**
- **AWS Account** (for S3 storage)
- **Stripe Account** (for payments)

### Quick Start

1. **Install Wasp CLI**
   ```bash
   curl -sSL https://get.wasp-lang.dev/installer.sh | sh
   ```

2. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/builders-stream-pro.git
   cd builders-stream-pro
   ```

3. **Install dependencies**
   ```bash
   wasp install
   ```

4. **Configure environment variables**
   ```bash
   cp .env.example .env.server
   # Edit .env.server with your credentials
   ```

5. **Start PostgreSQL database**
   ```bash
   wasp start db
   ```

6. **Run database migrations**
   ```bash
   wasp db migrate-dev
   ```

7. **Start development server**
   ```bash
   wasp start
   ```

8. **Access the application**
   - Frontend: http://localhost:3000
   - Backend: http://localhost:3001

---

## ⚙️ Configuration

### Environment Variables

Create a `.env.server` file in the project root:

```bash
# Database
DATABASE_URL=postgresql://user:password@localhost:5432/buildersstream

# Authentication
GOOGLE_CLIENT_ID=your_google_client_id
GOOGLE_CLIENT_SECRET=your_google_secret
GITHUB_CLIENT_ID=your_github_client_id
GITHUB_CLIENT_SECRET=your_github_secret

# Payments
STRIPE_SECRET_KEY=sk_test_your_stripe_key
STRIPE_WEBHOOK_SECRET=whsec_your_webhook_secret

# Email
SENDGRID_API_KEY=your_sendgrid_key
FROM_EMAIL=noreply@buildersstream.com

# File Storage
AWS_ACCESS_KEY_ID=your_aws_access_key
AWS_SECRET_ACCESS_KEY=your_aws_secret
AWS_S3_BUCKET=buildersstream-files
AWS_REGION=us-east-1

# Analytics
PLAUSIBLE_DOMAIN=yourdomain.com
SENTRY_DSN=your_sentry_dsn
```

### Module Activation

Configure module availability per pricing tier in `src/server/config/modules.ts`:

```typescript
export const MODULE_CONFIG = {
  starter: ['project', 'crm', 'basic-estimating', 'client-portal'],
  professional: ['*', '!payroll', '!enterprise-features'],
  enterprise: ['*']
}
```

---

## 💻 Development

### Project Structure

```
builders-stream-pro/
├── main.wasp                    # Wasp configuration file
├── .env.server                  # Environment variables
├── migrations/                  # Prisma database migrations
├── public/                      # Static assets
├── src/
│   ├── client/                  # React frontend
│   │   ├── components/          # Reusable UI components
│   │   ├── pages/               # Page components
│   │   ├── hooks/               # Custom React hooks
│   │   └── styles/              # Tailwind styles
│   ├── server/                  # Node.js backend
│   │   ├── actions/             # Wasp actions (write operations)
│   │   ├── queries/             # Wasp queries (read operations)
│   │   ├── jobs/                # Background job handlers
│   │   ├── api/                 # API route handlers
│   │   └── integrations/        # External service integrations
│   └── shared/                  # Shared types and utilities
├── docs/                        # Documentation
└── tests/                       # Test files
```

### Key Commands

```bash
# Start development server
wasp start

# Database operations
wasp db migrate-dev          # Create new migration
wasp db studio              # Open Prisma Studio
wasp db seed                # Seed database

# Build for production
wasp build

# Clean build artifacts
wasp clean

# Run tests
npm test                    # Run all tests
npm run test:watch          # Watch mode

# Code quality
npm run lint                # Run ESLint
npm run type-check          # TypeScript type checking
npm run format              # Format with Prettier
```

### Adding a New Module

1. **Define entities in main.wasp**
   ```wasp
   entity NewModule {=psl
     id String @id @default(uuid())
     // fields...
   psl=}
   ```

2. **Create queries and actions**
   ```wasp
   query getNewModuleData {
     fn: import { getData } from "@server/newmodule",
     entities: [NewModule]
   }
   ```

3. **Add route and page**
   ```wasp
   route NewModuleRoute { path: "/newmodule", to: NewModulePage }
   page NewModulePage {
     authRequired: true,
     component: import { NewModule } from "@client/pages/NewModule"
   }
   ```

4. **Implement server logic** in `src/server/newmodule.ts`

5. **Create React component** in `src/client/pages/NewModule.tsx`

6. **Run migration**
   ```bash
   wasp db migrate-dev
   ```

---

## 🚢 Deployment

### Fly.io (Recommended)

```bash
# Login to Fly.io
fly auth login

# Deploy (first time)
wasp deploy fly launch builders-stream-pro us-east-1

# Subsequent deploys
wasp deploy fly deploy
```

### Railway

```bash
# Install Railway CLI
npm i -g @railway/cli

# Login and deploy
railway login
wasp build
cd .wasp/build
railway up
```

### Self-Hosted (Docker)

```bash
# Build Docker image
wasp build
cd .wasp/build
docker build -t builders-stream-pro .

# Run with Docker Compose
docker-compose up -d
```

Example `docker-compose.yml`:
```yaml
version: '3.8'
services:
  postgres:
    image: postgres:14
    environment:
      POSTGRES_PASSWORD: ${DATABASE_PASSWORD}
    volumes:
      - postgres_data:/var/lib/postgresql/data

  app:
    image: builders-stream-pro
    depends_on:
      - postgres
    environment:
      DATABASE_URL: ${DATABASE_URL}
      # ... other env vars
    ports:
      - "3000:3000"

volumes:
  postgres_data:
```

### Environment-Specific Configuration

- **Development**: `.env.server`
- **Staging**: Configure in Railway/Fly.io dashboard
- **Production**: Use secrets management (AWS Secrets Manager, Doppler, etc.)

---

## 📚 API Documentation

### REST API

All API endpoints are documented with OpenAPI 3.0 specification.

**Base URL**: `https://api.buildersstream.com/v1`

#### Authentication

```bash
# Obtain access token
POST /auth/login
Content-Type: application/json

{
  "email": "user@example.com",
  "password": "password"
}

# Response
{
  "token": "eyJhbGciOiJIUzI1NiIs...",
  "user": { /* user object */ }
}
```

#### Example Endpoints

```bash
# Get all projects
GET /api/projects
Authorization: Bearer {token}

# Create new project
POST /api/projects
Authorization: Bearer {token}
Content-Type: application/json

{
  "name": "Kitchen Remodel",
  "clientId": "uuid",
  "status": "planning"
}

# Get project details
GET /api/projects/{id}
Authorization: Bearer {token}

# Update project
PATCH /api/projects/{id}
Authorization: Bearer {token}

# Delete project
DELETE /api/projects/{id}
Authorization: Bearer {token}
```

### Webhooks

Configure webhooks for real-time event notifications:

```bash
POST /api/webhooks
{
  "url": "https://yourapp.com/webhook",
  "events": ["project.created", "invoice.paid", "estimate.signed"]
}
```

### Rate Limiting

- **Starter**: 100 requests/minute
- **Professional**: 500 requests/minute
- **Enterprise**: 5000 requests/minute

---

## 🗓️ Roadmap

### Phase 1: Foundation (Months 1-4) ✅
- [x] Wasp/Open SaaS setup
- [x] Multi-tenant architecture
- [x] Project Command Center
- [x] User & organization management
- [x] QuickBooks integration

### Phase 2: Client Experience (Months 5-8) 🚧
- [x] Client Portal
- [x] Estimating Engine
- [ ] CRM Module (In Progress)
- [ ] Document Management

### Phase 3: Operations Excellence (Months 9-12) 📅
- [ ] Scheduling & Resource Management
- [ ] Field Operations Hub
- [ ] Advanced Financial Management
- [ ] Quality & Safety Compliance

### Phase 4: Enterprise & Specialty (Months 13-18) 📅
- [ ] Payroll Module
- [ ] Service & Warranty Management
- [ ] Advanced Analytics
- [ ] Public API & Marketplace

---

## 🤝 Contributing

We welcome contributions! Please see our [Contributing Guide](CONTRIBUTING.md) for details.

### Development Workflow

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

### Code Style

- **TypeScript**: Strict mode enabled
- **ESLint**: Airbnb style guide with Wasp-specific rules
- **Prettier**: Automatic formatting on save
- **Commit Messages**: Conventional Commits format

### Testing

```bash
# Run unit tests
npm test

# Run integration tests
npm run test:integration

# Run E2E tests
npm run test:e2e

# Coverage report
npm run test:coverage
```

---

## 📊 Success Metrics

### Target KPIs

- **User Activation**: 70%+ complete onboarding within 3 days
- **Monthly Active Users**: 80%+ weekly logins
- **Feature Adoption**: 50%+ mobile app usage
- **System Reliability**: 99.9%+ uptime
- **Customer Satisfaction**: NPS > 50
- **Financial Impact**: 15%+ reduction in admin time

---

## 🎯 Pricing

### Tier Structure

| Tier | Price/User/Month | Users | Features |
|------|-----------------|-------|----------|
| **Starter** | $15 | Up to 5 | Core + CRM + Basic Estimating |
| **Professional** | $50 | Up to 25 | All modules except Payroll |
| **Enterprise** | $125 | Unlimited | All modules + API + Premium support |

**Annual Discount**: 20% off with annual billing

---

## 📄 License

This project is **Confidential** and proprietary. All rights reserved.

For licensing inquiries, contact: licensing@buildersstream.com

---

## 🔗 Links

- **Website**: https://buildersstream.com
- **Documentation**: https://docs.buildersstream.com
- **API Docs**: https://api.buildersstream.com/docs
- **Community Forum**: https://community.buildersstream.com
- **Support**: support@buildersstream.com

---

## 👥 Team

- **Product Lead**: [Your Name]
- **Technical Lead**: [Your Name]
- **Location**: Dallas, Texas, US

---

## 🙏 Acknowledgments

- [Wasp Framework](https://wasp-lang.dev) - Full-stack framework
- [Open SaaS](https://opensaas.sh) - SaaS boilerplate
- [Prisma](https://www.prisma.io) - Database ORM
- [TailwindCSS](https://tailwindcss.com) - UI framework

---

## 📞 Support

- **Documentation**: [docs.buildersstream.com](https://docs.buildersstream.com)
- **Discord Community**: [Join our Discord](https://discord.gg/buildersstream)
- **Email Support**: support@buildersstream.com
- **Emergency Hotline**: 1-800-BUILD-PRO (Enterprise only)

---

**Built with ❤️ for the construction industry**

*Last Updated: February 2026*
