I now have comprehensive knowledge of the codebase. Here is the full implementation roadmap.

---

# BuilderStream Feature Implementation Roadmap

**Generated:** 2026-03-04
**Codebase State:** 16 Django apps complete (backend), React frontend shell wired to all modules
**Next Phase:** Gap closure + 5 net-new modules

---

## Codebase Reality Check

### What is Actually Built
- **Backend (all 16 apps):** Full models, services, serializers, viewsets, signals, Celery tasks, tests
- **Frontend:** Router wired, one-page list/CRUD UIs exist for every module; no advanced views (Kanban, Gantt, Calendar) anywhere
- **Infrastructure:** Django 5.2, DRF, PostgreSQL 16, Redis, Celery Beat, S3/boto3, React 18 + TypeScript + Vite + TailwindCSS + React Query + Zustand
- **Not installed yet:** `channels`, `channels-redis`, `daphne` (Django Channels / WebSocket), 2FA library, SAML library

### What is Missing per Spec
| Gap | Category |
|---|---|
| Kanban / Gantt / Calendar / Timeline frontend views | Project Management (frontend) |
| Subtask hierarchies (partial in scheduling.Task.parent_task) | Project Management |
| Recurring tasks | Project Management |
| CSV import + deduplication for contacts | CRM |
| Contact enrichment + relationship map | CRM |
| WYSIWYG estimate editor + version diff | Estimating |
| Estimate conversion tracking | Estimating |
| PTO / leave + skills matrix + scenario planning | Resource Management |
| Billable vs non-billable reporting | Resource Management |
| Multi-currency billing | Billing |
| Dunning workflows | Billing |
| Client payment portal (Stripe hosted page stub only) | Billing |
| Threaded comments on tasks/projects/docs | Collaboration |
| Team channels, direct messaging | Collaboration (new app) |
| Real-time co-editing | Collaboration |
| HD video conferencing | Collaboration |
| Notification preferences engine | Collaboration |
| External collaborator access | Collaboration |
| Two-way email sync (Gmail/Outlook/IMAP) | Email & Communications (new app) |
| Email templates, campaigns, tracking | Email & Communications |
| Email-to-task, shared team inboxes | Email & Communications |
| SSO/SAML 2.0 | Security |
| 2FA (TOTP + SMS) | Security |
| IP whitelisting + geofencing | Security |
| Comprehensive audit logs | Security |
| Session management UI | Security |
| Custom fields (15+ types) with UI | Customization (new app) |
| Visual workflow builder | Customization |
| White-label branding | Customization |
| Localization (30+ languages) | Customization |
| Real-time collaborative document editing | Documents |
| OCR | Documents |
| Google Drive / Dropbox / OneDrive | Documents |
| File preview for 100+ types | Documents |
| Drag-and-drop form builder | Forms (extension of quality_safety) |
| Public forms for lead capture | Forms |
| Form analytics | Forms |
| Slack integration | Integrations |
| Zapier/Make.com | Integrations |
| Calendar sync (Google/Outlook) | Integrations |
| QuickBooks/Xero actual sync (not stubs) | Integrations |
| Zoom integration | Integrations |
| Issue Tracking module | New module |
| OKR module | New module |
| Custom report builder UI | Analytics frontend |
| Scheduled report delivery | Analytics |
| Interactive drill-down dashboards | Analytics frontend |
| Universal search | New feature |
| AI-powered suggestions | New feature |

---

## Infrastructure Changes Required

### New Python Packages

| Package | Purpose | Priority |
|---|---|---|
| `channels>=4.0` | WebSocket/real-time (chat, co-editing, notifications) | P1 |
| `channels-redis>=4.0` | Redis channel layer backend for Channels | P1 |
| `daphne>=4.0` | ASGI server replacing the dev runserver for WebSocket | P1 |
| `django-otp>=1.4` | TOTP-based 2FA (Google Authenticator) | P1 |
| `django-two-factor-auth>=1.16` | 2FA UI and flow wrapper | P1 |
| `python3-saml>=1.16` or `djangosaml2>=1.9` | SAML 2.0 SSO | P2 |
| `social-auth-app-django>=5.4` | OAuth SSO extensions beyond allauth | P2 |
| `djangorestframework-csv>=2.1` | CSV import/export for contact bulk operations | P2 |
| `pandas>=2.0` | CSV deduplication logic and data manipulation | P2 |
| `babel>=2.14` | Locale-aware formatting for multi-currency and i18n | P2 |
| `deep-translator>=1.11` or `django-rosetta` | Translation management for 30+ languages | P3 |
| `pytesseract>=0.3` + `pdf2image>=1.17` | OCR for documents | P3 |
| `google-api-python-client>=2.100` | Google Drive / Calendar sync | P3 |
| `O365>=2.0` | Microsoft 365 / Outlook / OneDrive | P3 |
| `slack-sdk>=3.21` | Slack integration | P3 |
| `imapclient>=3.0` + `email-validator` | IMAP email sync | P3 |
| `google-auth-oauthlib` | Gmail OAuth sync | P3 |
| `stripe>=8.0` (already installed) | Already present, extend for multi-currency | P1 |

### New Django Apps to Create

| App Name | Path | Purpose |
|---|---|---|
| `collaboration` | `apps/collaboration/` | Chat channels, DMs, threaded comments, notifications |
| `communications` | `apps/communications/` | Email sync, templates, campaigns, shared inboxes |
| `okrs` | `apps/okrs/` | Objectives, key results, check-ins, alignment |
| `issue_tracking` | `apps/issue_tracking/` | Issues, SLA, escalation, customer portal |
| `custom_fields` | `apps/custom_fields/` | Custom field definitions, values, workflow builder |
| `search` | `apps/search/` | Universal search index, saved searches, smart folders |

### Infrastructure Services to Add/Modify

- **ASGI:** Rewrite `config/asgi.py` to use `channels.routing.ProtocolTypeRouter` routing HTTP to Django and WebSocket to Channels consumers
- **docker-compose.yml:** Add `daphne` as the ASGI server container; add a `channels_worker` container for Django Channels worker layer if using separate processes
- **Redis:** Use db 2 for the Channels layer (db 0 = Celery broker, db 1 = Django cache)
- **`CHANNEL_LAYERS` setting:** Add to `base.py` pointing to Redis db 2
- **New module keys in `ActiveModule.ModuleKey`:** `COLLABORATION`, `COMMUNICATIONS`, `OKRS`, `ISSUE_TRACKING`, `CUSTOM_FIELDS`
- **Frontend packages:** `@tanstack/react-query` already present; add `@dnd-kit/core` + `@dnd-kit/sortable` (drag-and-drop), `react-grid-layout` (resizable dashboard), `quill` or `tiptap` (WYSIWYG), a Gantt library (`dhtmlx-gantt` or `frappe-gantt`), a calendar library (`fullcalendar`), `socket.io-client` or native browser WebSocket wrapper, `react-virtualized` or `@tanstack/react-virtual` (virtual lists for universal search), `i18next` + `react-i18next` (localization)

---

## Priority Tiers

- **P1 â€” Critical/Core Missing:** Foundational features blocking day-to-day use or other features
- **P2 â€” High Value:** Significant UX gaps that are highly visible to users
- **P3 â€” Medium Value:** Important completions but not blockers
- **P4 â€” Nice to Have:** Enhancement/polish features

---

## Phase 0: Infrastructure Foundation (P1, must be first)

### 0.1 â€” Django Channels + ASGI Setup

**Why first:** Every real-time feature (chat, notifications, co-editing) depends on this.

**Backend tasks:**
1. Add `channels`, `channels-redis`, `daphne` to `requirements/base.txt`
2. Rewrite `config/asgi.py` to use `ProtocolTypeRouter` with `URLRouter` for `ws/` paths and standard Django ASGI for HTTP
3. Add `channels` and `daphne` to `INSTALLED_APPS` in `config/settings/base.py`
4. Add `CHANNEL_LAYERS` setting in `base.py`:
   ```
   CHANNEL_LAYERS = {"default": {"BACKEND": "channels_redis.core.RedisChannelLayer", "CONFIG": {"hosts": [(REDIS_HOST, 6379, 2)]}}}
   ```
5. Update `docker-compose.yml`: replace `web` service `command` with `daphne config.asgi:application -b 0.0.0.0 -p 8000`; keep `celery_worker` and `celery_beat` unchanged

**Frontend tasks:**
- None â€” consumed by later features

**Complexity:** M
**Dependencies:** None

---

### 0.2 â€” 2FA (TOTP + SMS)

**Why now:** Security foundation; SAML builds on top of auth hardening.

**Backend tasks:**
1. Add `django-otp`, `django-two-factor-auth` to `requirements/base.txt`
2. Add `django_otp`, `django_otp.plugins.otp_totp`, `django_otp.plugins.otp_static`, `two_factor` to `INSTALLED_APPS`
3. Add `OTPMiddleware` after `AuthenticationMiddleware` in `MIDDLEWARE`
4. Extend `accounts.User` model: add `two_factor_enabled` BooleanField, `backup_codes` JSONField (encrypted), `sms_phone` CharField
5. Create migration for these new fields
6. Create API endpoints in `apps/accounts/views.py`:
   - `POST /api/v1/auth/2fa/setup/` â€” generate TOTP device + QR code URI
   - `POST /api/v1/auth/2fa/verify/` â€” verify OTP token during setup
   - `POST /api/v1/auth/2fa/disable/` â€” disable 2FA with confirmation
   - `POST /api/v1/auth/2fa/backup-codes/` â€” generate/regenerate backup codes
   - Modify `CustomTokenObtainPairSerializer`: if `user.two_factor_enabled`, return a `requires_2fa: true` flag and a short-lived pre-auth token; add `POST /api/v1/auth/2fa/confirm/` to exchange OTP + pre-auth token for full JWT pair
7. Add SMS delivery via Twilio/SNS (stub with settings flag for SMS OTP)
8. Tests: 15+ covering setup, verify, disable, login flow with 2FA enabled

**Frontend tasks:**
- Settings page section: "Security" tab with 2FA toggle, QR code display (base32 secret + qrcode image), backup codes display
- Login flow: detect `requires_2fa` response, show OTP input modal before granting access, store pre-auth token in memory (not localStorage)

**Complexity:** L
**Dependencies:** 0.1 not required (pure auth)

---

### 0.3 â€” IP Whitelisting + Session Management + Audit Log API

**Backend tasks:**
1. Add `IPWhitelist` model to `apps/tenants/models.py` (TenantModel, `cidr_range` CharField, `label`, `is_active`)
2. Add `AuditLog` model to `apps/core/models.py` (TenantModel): `action`, `resource_type`, `resource_id`, `user` FK, `ip_address`, `user_agent`, `before_state` JSONField, `after_state` JSONField, `timestamp`
3. Create `AuditLogMiddleware` in `apps/core/middleware.py` that writes to AuditLog on all mutating requests (POST/PUT/PATCH/DELETE); exclude health checks and static
4. Add `IPWhitelistMiddleware` in `apps/tenants/middleware.py`: if org has active whitelist entries, deny requests from IPs not matching any CIDR range; return 403 with `X-Denied-Reason: ip_whitelist`
5. Add `UserSession` model in `apps/accounts/models.py`: `user` FK, `jti` (JWT ID claim), `ip_address`, `user_agent`, `created_at`, `last_seen_at`, `is_active`
6. Modify `CustomTokenObtainPairSerializer` to record session on login; add `jti` to token payload
7. Add `POST /api/v1/users/sessions/{jti}/revoke/` to blacklist specific JWT by JTI and deactivate session
8. ViewSets: `IPWhitelistViewSet`, `AuditLogViewSet` (read-only), `UserSessionViewSet`
9. Celery task: `cleanup_expired_sessions` â€” daily, deactivate sessions older than `REFRESH_TOKEN_LIFETIME`

**Frontend tasks:**
- Settings > Security: IP Whitelist management UI (CIDR range list, add/remove)
- Settings > Security: Active sessions list (device, IP, last seen, revoke button)
- Settings > Audit Log: filterable read-only table (user, action, resource, date range)

**Complexity:** L
**Dependencies:** 0.2 (audit log captures 2FA events too)

---

## Phase 1: Project Management Views (P1)

### 1.1 â€” Kanban Board View

**Why P1:** Most visible gap in the product. Project Management is the core module.

**Backend tasks:**
1. Add `GET /api/v1/projects/kanban/` endpoint on the existing `ProjectViewSet` as an `@action`
   - Returns projects grouped by `status` in a column structure
   - Accepts same filters as the list endpoint (search, project_type, health_status, date range)
   - Columns ordered by the 10-status lifecycle order
2. Add `POST /api/v1/projects/{pk}/move-column/` action: validates transition via `ProjectLifecycleService` (reuses existing state machine), returns updated project
3. Extend `ProjectViewSet` with bulk status change: `POST /api/v1/projects/bulk-update/` â€” accepts list of `{id, status}` pairs, applies lifecycle transitions, returns success/failure per item

**Frontend tasks:**
1. Install `@dnd-kit/core` and `@dnd-kit/sortable`
2. Create `features/projects/views/KanbanView.tsx`:
   - Column component per project status using `useDroppable`
   - Card component per project using `useDraggable` (shows project name, client, health badge, estimated value)
   - On drop: optimistically update Zustand store, call `move-column` mutation, rollback on failure
3. Add view toggle (List / Kanban / Gantt / Calendar) to `ProjectsPage.tsx` header
4. Wire `useProjects` hook to Kanban-specific query with `view=kanban` param or restructure response client-side from existing list data

**Complexity:** M
**Dependencies:** None (existing backend is sufficient for data; frontend work only for views)

---

### 1.2 â€” Gantt Chart View

**Backend tasks:**
1. Existing `GET /api/v1/scheduling/tasks/gantt/?project_id=` endpoint already provides full Gantt data structure
2. Add `GET /api/v1/projects/{pk}/gantt-summary/` for project-level Gantt (milestones + phases from `ProjectMilestone` model; tasks from `scheduling.Task`)
3. Add `PATCH /api/v1/scheduling/tasks/{pk}/dates/` â€” lightweight endpoint to update `start_date`, `end_date`, `estimated_hours` from drag-and-drop without full serializer overhead; triggers CPM recalculation async

**Frontend tasks:**
1. Evaluate and install either `frappe-gantt` (MIT) or `@dhtmlx/gantt` (commercial) â€” plan for `frappe-gantt` as the MIT option
2. Create `features/projects/views/GanttView.tsx`:
   - Fetch Gantt data from scheduling endpoint when a project is selected
   - Render tasks as Gantt bars with dependency arrows
   - On bar drag/resize: call `PATCH .../dates/` with debounce
   - Filter control: project selector dropdown (for cross-project view)
3. Create `features/scheduling/GanttPanel.tsx` as reusable panel that can be embedded in `ProjectDetailPage`

**Complexity:** L
**Dependencies:** 1.1 (view toggle infrastructure)

---

### 1.3 â€” Calendar View

**Backend tasks:**
1. Add `GET /api/v1/projects/calendar/` endpoint: returns milestones, task due dates, and project start/end dates within a date range (`?start=&end=` params)
2. Shape: `{events: [{id, title, start, end, type: 'milestone'|'task'|'project', project_id, color}]}`

**Frontend tasks:**
1. Install `@fullcalendar/react`, `@fullcalendar/daygrid`, `@fullcalendar/timegrid`, `@fullcalendar/interaction`
2. Create `features/projects/views/CalendarView.tsx`:
   - Month/week/day toggle
   - Color-coded by event type and health status
   - Click event: slide-out panel with entity detail
   - Drag event to new date: calls update endpoint

**Complexity:** M
**Dependencies:** 1.1 (view toggle)

---

### 1.4 â€” Recurring Tasks

**Backend tasks:**
1. Add `RecurringTaskTemplate` model to `apps/projects/models.py` (TenantModel): `title`, `project` FK (nullable for org-level templates), `recurrence_rule` CharField (iCal RRULE string), `assignee` FK, `estimated_hours`, `checklist_items` JSONField, `is_active`
2. Add `RecurringTaskInstance` through-model: `template` FK, `task` FK (to `scheduling.Task`), `scheduled_date`
3. `RecurringTaskService` in `apps/projects/services.py`:
   - `generate_occurrences(template, from_date, to_date)`: parses RRULE, returns list of dates
   - `create_next_occurrence(template)`: creates a `scheduling.Task` from the template
4. Celery task: `projects.expand_recurring_tasks` â€” daily at 6am, calls `create_next_occurrence` for all active templates where next occurrence is within 14 days and no instance exists yet
5. Add `RecurringTaskTemplateViewSet` to `apps/projects/views.py`; add route to `apps/projects/urls.py`

**Frontend tasks:**
1. Add "Recurring" toggle to task creation modal in `SchedulingPage` and `ProjectDetailPage`
2. `RecurringRuleBuilder.tsx` component: frequency (daily/weekly/monthly), interval, end condition (count or date), day-of-week checkboxes for weekly
3. List view of recurring templates in Settings or Project detail

**Complexity:** L
**Dependencies:** 1.1

---

### 1.5 â€” Subtask Hierarchies (Project-level)

**Note:** `scheduling.Task` already has `parent_task` self-FK. This is a frontend gap.

**Backend tasks:**
1. Verify `TaskSerializer` includes `children` as a nested list (may need to add `children = TaskListSerializer(many=True, read_only=True, source='child_tasks')`)
2. Add `subtask_count` and `completed_subtask_count` as SerializerMethodFields on `TaskListSerializer`
3. Add `POST /api/v1/scheduling/tasks/{pk}/subtasks/` convenience endpoint

**Frontend tasks:**
1. In task list/detail: render subtask tree with collapse/expand
2. Task card: show subtask progress (e.g., "3/5 subtasks done") as progress bar
3. Add subtask input directly within a parent task's detail view

**Complexity:** S
**Dependencies:** None

---

## Phase 2: CRM Enhancements (P2)

### 2.1 â€” CSV Import with Deduplication

**Backend tasks:**
1. Add `ContactImport` model in `apps/crm/models.py` (TenantModel): `file_key` (S3), `status` (pending/processing/complete/failed), `total_rows`, `imported_count`, `duplicate_count`, `error_count`, `field_mapping` JSONField, `errors` JSONField
2. `CSVImportService` in `apps/crm/services.py`:
   - `parse_csv(file_obj, field_mapping)`: reads CSV, maps columns to Contact fields
   - `deduplicate(row, strategy)`: checks existing contacts by email, phone, name+company combos; returns `DUPLICATE` / `UPDATE` / `CREATE`
   - `import_contact(row, org, user)`: creates or updates Contact, logs result
3. Upload endpoint: `POST /api/v1/crm/contacts/import/` â€” accepts multipart file, enqueues Celery task, returns `ContactImport.id`
4. Celery task: `crm.process_contact_import(import_id)` â€” streams CSV rows, calls `CSVImportService`, updates progress
5. Polling endpoint: `GET /api/v1/crm/contacts/import/{id}/status/` â€” returns progress

**Frontend tasks:**
1. Import wizard modal (3 steps): Upload CSV > Map Columns > Review & Import
2. Column mapper: drag-and-drop match (or dropdown) of CSV headers to Contact fields
3. Progress indicator polling during import; results summary (imported / duplicates / errors)

**Complexity:** L
**Dependencies:** None

---

### 2.2 â€” Contact Enrichment

**Backend tasks:**
1. Add `EnrichmentLog` model: `contact` FK, `provider` CharField, `raw_response` JSONField, `enriched_at`
2. `ContactEnrichmentService`: stub with provider interface; implement `Clearbit` as first provider (requires `CLEARBIT_API_KEY` setting); on response, update Contact's LinkedIn, job title, company size, annual revenue fields
3. Add new nullable fields to Contact: `linkedin_url`, `company_linkedin_url`, `company_size_range`, `annual_revenue_range`, `enriched_at` DateTimeField, `enrichment_score` IntegerField
4. Migration for new fields
5. `POST /api/v1/crm/contacts/{pk}/enrich/` â€” triggers enrichment async, returns 202

**Frontend tasks:**
1. Contact detail page: "Enrich" button with loading state; display enriched data section when present
2. Enrichment status indicator in contact list (enriched badge)

**Complexity:** M
**Dependencies:** 2.1

---

### 2.3 â€” Relationship Mapping Visualization

**Backend tasks:**
1. Add `ContactRelationship` model (TenantModel): `from_contact` FK, `to_contact` FK, `relationship_type` (REFERS_TO, REPORTS_TO, PARTNER, COMPETITOR, WORKS_AT), `notes`, unique_together
2. `GET /api/v1/crm/contacts/{pk}/relationship-graph/` â€” returns nodes (contacts) + edges (relationships) within 2 hops

**Frontend tasks:**
1. Install `d3` or `react-force-graph`
2. `RelationshipGraph.tsx` in Contact detail: force-directed graph with zoom/pan; click node to navigate to that contact

**Complexity:** M
**Dependencies:** None

---

## Phase 3: Proposals & Estimates (P2)

### 3.1 â€” WYSIWYG Estimate Editor

**Backend tasks:**
1. Add `content_json` JSONField to `estimating.Estimate` (stores Tiptap/ProseMirror document tree); keep `description` TextField for plain-text fallback
2. Add `EstimateTemplate` model: `name`, `content_json`, `variables` JSONField (list of variable names like `{{client_name}}`), `is_global` BooleanField
3. `EstimateTemplateViewSet` with org-scoped access; global templates accessible to all orgs

**Frontend tasks:**
1. Install `@tiptap/react`, `@tiptap/starter-kit`, `@tiptap/extension-table`, `@tiptap/extension-image`
2. Create `EstimateEditorPage.tsx` replacing the current form-based estimate creation
3. Custom Tiptap extensions: `LineItemBlock` (renders an editable estimate line item table inline), `VariableChip` (renders `{{client_name}}` as a styled chip)
4. Toolbar: Bold, Italic, Headings, Table insert, Line Item block insert, Variable insert
5. Auto-save via React Query mutation with 2s debounce

**Complexity:** XL
**Dependencies:** None; can run in parallel with phase 2

---

### 3.2 â€” Version Diff View

**Backend tasks:**
1. Existing `apps/documents/models.py` has versioning pattern; apply same pattern to `estimating.Estimate`:
   - Add `version` IntegerField, `previous_version` FK (self), `is_current_version` BooleanField
   - `EstimateVersionService.create_new_version(estimate)`: deep copies estimate + line items, increments version, sets old as not current
2. `GET /api/v1/estimating/estimates/{pk}/versions/` â€” list all versions (id, version number, created_at, created_by, total_amount)
3. `GET /api/v1/estimating/estimates/{pk}/diff/{version_b_pk}/` â€” returns a structured diff: list of `{field, old_value, new_value, change_type: added|removed|modified}` for the estimate header and each line item

**Frontend tasks:**
1. Version history sidebar in `EstimateEditorPage`
2. Diff view: two-column layout with line-by-line changes highlighted (green=added, red=removed, yellow=modified)

**Complexity:** L
**Dependencies:** 3.1

---

### 3.3 â€” Conversion Tracking

**Backend tasks:**
1. Add `EstimateConversionEvent` model: `estimate` FK, `event_type` (SENT, VIEWED, SIGNED, CONVERTED_TO_PROJECT, DECLINED), `occurred_at`, `metadata` JSONField
2. Signals: on estimate status change, create conversion event
3. `GET /api/v1/estimating/analytics/conversion/` â€” returns funnel: sent count, viewed count, signed count, converted count, average time per stage

**Frontend tasks:**
1. Conversion funnel widget in `EstimatingPage`

**Complexity:** S
**Dependencies:** 3.1

---

## Phase 4: Collaboration Module (P1 â€” new app)

### 4.1 â€” Threaded Comments

**Backend tasks:**
1. Create `apps/collaboration/` app with `AppConfig` and `ready()` for signals
2. `Comment` model (TenantModel): `content` TextField, `content_type` FK (Django ContentType), `object_id` UUIDField, `parent` FK (self, nullable for threading), `is_edited` BooleanField, `edited_at`, `mentions` JSONField (list of user UUIDs), `attachments` JSONField (list of S3 keys)
3. `CommentReaction` model: `comment` FK, `user` FK, `emoji` CharField
4. `CommentSerializer`, `CommentViewSet` with generic filtering by `content_type_id` + `object_id`
5. URL: `GET/POST /api/v1/collaboration/comments/?content_type=projects.project&object_id={uuid}`
6. `POST /api/v1/collaboration/comments/{pk}/reactions/` â€” add/toggle reaction
7. Signal: on `Comment.create`, send real-time update via Channels group `comments_{content_type}_{object_id}`
8. Add `collaboration` to `ActiveModule.ModuleKey`

**Frontend tasks:**
1. `CommentThread.tsx` reusable component: renders threaded list, reply form, reactions bar
2. Embed in `ProjectDetailPage`, task detail slide-out, document detail
3. WebSocket hook `useCommentSocket(entityType, entityId)` that subscribes to Channels group and appends new comments to React Query cache

**Complexity:** L
**Dependencies:** 0.1 (Channels), 4.2

---

### 4.2 â€” Team Channels + Direct Messaging

**Backend tasks:**
1. `Channel` model (TenantModel): `name`, `description`, `channel_type` (PUBLIC/PRIVATE/DIRECT), `members` M2M to User, `project` FK (nullable for project-linked channels)
2. `Message` model (TenantModel): `channel` FK, `content` TextField, `content_json` JSONField (rich text), `parent` FK (self â€” thread reply), `is_edited`, `attachments` JSONField
3. `MessageReaction` model: same pattern as `CommentReaction`
4. `ReadReceipt` model: `channel` FK, `user` FK, `last_read_at`, unique_together; used for unread counts
5. Django Channels consumer `ChatConsumer`:
   - WebSocket path: `ws/collaboration/channels/{channel_id}/`
   - Auth: authenticate via JWT query param `?token=` (since WebSocket headers are limited)
   - On connect: verify membership, join group `channel_{channel_id}`
   - On receive: validate message, save to DB, broadcast to group
   - On disconnect: update `ReadReceipt.last_read_at`
6. REST endpoints: `GET/POST /api/v1/collaboration/channels/`, `GET/POST /api/v1/collaboration/channels/{id}/messages/`, `POST /api/v1/collaboration/channels/{id}/read/` (mark read)
7. Celery task: `collaboration.send_unread_digest` â€” daily, notify users of channels with unread messages

**Frontend tasks:**
1. Zustand store `useChatStore`: current channel, unread counts map, socket connection state
2. `ChatSidebar.tsx`: channel list with unread badges, DM list, search within channels
3. `MessageFeed.tsx`: virtualized message list (use `@tanstack/react-virtual`), auto-scroll on new message
4. `MessageComposer.tsx`: rich text input, file attach (S3 presigned upload), `@mention` autocomplete
5. WebSocket management in `services/chat.ts`: singleton socket per channel, reconnect with exponential backoff

**Complexity:** XL
**Dependencies:** 0.1 (Channels)

---

### 4.3 â€” Notification Preferences Engine

**Backend tasks:**
1. `NotificationPreference` model (TenantModel): `user` FK, `event_type` CharField (e.g., `project.status_changed`, `comment.mention`, `task.assigned`), `channels` JSONField (`{email: true, push: false, in_app: true}`)
2. `Notification` model (TenantModel): `user` FK, `event_type`, `title`, `body`, `resource_type`, `resource_id`, `is_read` BooleanField, `read_at`
3. `NotificationService`:
   - `notify(user, event_type, context)`: checks preference, dispatches to enabled channels
   - `email`: Celery task via SES/SMTP
   - `in_app`: saves `Notification`, broadcasts via Channels group `user_{user_id}_notifications`
4. `NotificationConsumer` in Channels: `ws/notifications/` â€” single persistent connection per user for all in-app notifications
5. Replace ad-hoc signal-based notifications across all apps with `NotificationService.notify()` calls
6. REST endpoints: `GET /api/v1/collaboration/notifications/` (paginated, filterable by is_read), `POST /api/v1/collaboration/notifications/{id}/read/`, `POST /api/v1/collaboration/notifications/read-all/`, `GET/PUT /api/v1/collaboration/notification-preferences/`

**Frontend tasks:**
1. Notification bell in app header with unread count badge
2. `NotificationDropdown.tsx`: recent 20 notifications, mark read, link to resource
3. `NotificationPreferencesPage.tsx`: table of event types vs channels with toggle switches
4. `useNotificationSocket()` hook: connects `ws/notifications/`, appends to React Query cache, increments bell badge

**Complexity:** L
**Dependencies:** 4.1, 0.1

---

### 4.4 â€” External Collaborator Access

**Backend tasks:**
1. `ExternalCollaborator` model (TenantModel): `email`, `name`, `project` FK (access scoped to one project), `access_token` UUID, `permissions` JSONField (`{view_tasks, add_comments, view_documents}`), `expires_at`, `last_accessed_at`
2. `ExternalCollaboratorAuthentication` DRF backend: validates `Authorization: Collaborator <token>` header (same pattern as client portal's `Portal <token>`)
3. Limited REST endpoints under `/api/v1/external/`:
   - `GET /tasks/` scoped to collaborator's project
   - `GET/POST /comments/` limited to project entities
   - `GET /documents/` if `view_documents` permission

**Frontend tasks:**
1. In Project detail > Sharing: invite external collaborator (email + permission checkboxes + expiry)
2. Light external view (separate route `/external/:token`) with minimal UI showing project tasks and comment thread

**Complexity:** L
**Dependencies:** 4.1, 4.3

---

## Phase 5: Security & Access (P1)

### 5.1 â€” SSO / SAML 2.0

**Backend tasks:**
1. Add `djangosaml2` (or `python3-saml`) to requirements
2. Add `SSOConfiguration` model in `apps/accounts/models.py` (per-org): `provider_type` (SAML/GOOGLE_WORKSPACE/AZURE_AD/OKTA), `idp_metadata_url`, `idp_metadata_xml`, `sp_entity_id`, `assertion_consumer_service_url`, `attribute_mapping` JSONField (maps IdP attributes to User fields), `is_active`
3. SAML views: `GET /api/v1/auth/sso/initiate/` (generates SAML AuthnRequest), `POST /api/v1/auth/sso/callback/` (processes SAMLResponse, creates/updates User, returns JWT)
4. Organization login slug: `GET /api/v1/auth/sso/{org_slug}/` â€” redirects to IdP if SSO configured for that org
5. Admin UI for SSO config in Django admin + REST endpoint for org admins

**Frontend tasks:**
1. Settings > Security > SSO Configuration: form to paste IdP metadata URL, test connection, enable/disable
2. Login page: "Login with SSO" button; if org slug typed, redirect to `/api/v1/auth/sso/{slug}/`

**Complexity:** XL
**Dependencies:** 0.2 (2FA), 0.3 (audit log records SSO events)

---

## Phase 6: Email & Communications (P2 â€” new app)

### 6.1 â€” Email Integration Infrastructure

**Backend tasks:**
1. Create `apps/communications/` app
2. `EmailAccount` model (TenantModel): `provider` (GMAIL/OUTLOOK/IMAP/SMTP), `email_address`, `access_token_encrypted`, `refresh_token_encrypted`, `imap_host`, `imap_port`, `smtp_host`, `smtp_port`, `sync_enabled`, `last_synced_at`, `shared` BooleanField (shared team inbox vs personal)
3. `EmailMessage` model (TenantModel): `account` FK, `message_id` CharField (RFC 2822 Message-ID), `thread_id`, `subject`, `from_address`, `to_addresses` JSONField, `cc_addresses` JSONField, `body_text` TextField, `body_html` TextField, `received_at`, `is_read`, `is_sent`, `folder` CharField, `linked_contact` FK (crm.Contact, nullable), `linked_project` FK (nullable), `linked_lead` FK (nullable)
4. `EmailThread` model: `thread_id`, `account` FK, `subject`, `last_message_at`, `participant_emails` JSONField, `message_count`
5. `GmailSyncService`: OAuth2 refresh, Gmail API history sync (incremental), writes `EmailMessage` records
6. `OutlookSyncService`: MS Graph API sync
7. `IMAPSyncService`: IMAP IDLE for real-time; fallback to polling every 5 min
8. Celery tasks: `communications.sync_email_accounts` â€” every 5 min, calls appropriate sync service per connected account
9. `GET /api/v1/communications/email-accounts/`, `GET /api/v1/communications/threads/`, `GET /api/v1/communications/messages/`, `POST /api/v1/communications/messages/send/`
10. Add `communications` to `ActiveModule.ModuleKey`

**Frontend tasks:**
1. Email module route `/communications/email`
2. Three-panel layout: account/folder tree (left), thread list (center), message/reply (right)
3. Connect Gmail button (OAuth redirect flow), Connect Outlook button
4. Thread list: sender, subject, preview, date, unread badge
5. Message viewer: HTML email rendering in sandboxed iframe, reply/forward composer

**Complexity:** XL
**Dependencies:** None directly; benefits from 4.3 notifications

---

### 6.2 â€” Email-to-Task and Thread Linking

**Backend tasks:**
1. `EmailToTaskService`: parse inbound email (subject line rules or manual trigger), create `scheduling.Task` or `service.ServiceTicket`
2. `POST /api/v1/communications/messages/{id}/create-task/` â€” manual convert to task
3. `POST /api/v1/communications/messages/{id}/link-to/` â€” link message/thread to project, lead, or contact

**Frontend tasks:**
1. In message viewer: "Convert to Task" button, "Link to Project/Lead" button
2. Linked entities sidebar showing related project/contact data inline in email view

**Complexity:** M
**Dependencies:** 6.1

---

### 6.3 â€” Email Templates + Automated Campaigns

**Backend tasks:**
1. `EmailTemplate` model already exists in `apps/crm/models.py`; move or extend to `apps/communications/models.py` and make generic (not CRM-specific)
2. `EmailCampaign` model (TenantModel): `name`, `template` FK, `audience_filter` JSONField (conditions to select contacts), `trigger_type` (MANUAL/SCHEDULE/EVENT), `scheduled_at`, `status`, `sent_count`, `open_count`, `click_count`
3. `EmailTrackingPixel` model: `message_id` UUID, `campaign` FK, `contact` FK, `opened_at`
4. `CampaignService.send_campaign(campaign)`: resolves audience, renders template per contact, enqueues individual send tasks
5. Celery task: `communications.process_scheduled_campaigns` â€” every 15 min

**Frontend tasks:**
1. Campaign builder: audience filter builder (tag/status/last-contact-date conditions), template picker, schedule or send now
2. Campaign analytics: open rate, click rate, bounce rate graphs

**Complexity:** L
**Dependencies:** 6.1

---

## Phase 7: Resource Management Enhancements (P2)

### 7.1 â€” PTO / Leave Management

**Backend tasks:**
1. `LeaveType` model (TenantModel): `name`, `accrual_rate_hours_per_year`, `max_balance_hours`, `is_paid`
2. `LeaveRequest` model (TenantModel): `employee` FK (payroll.Employee), `leave_type` FK, `start_date`, `end_date`, `hours_requested`, `status` (PENDING/APPROVED/DENIED/CANCELED), `approved_by` FK, `notes`
3. `LeaveBalance` model: `employee` FK, `leave_type` FK, `balance_hours`, `used_hours`, `accrued_hours`, `as_of_date`
4. `LeaveService`: `accrue_balances(employee)`, `approve_request(request, approver)`, `deny_request(request, approver)`, `check_conflicts(request)` (checks against crew task assignments in scheduling)
5. ViewSets for `LeaveType`, `LeaveRequest`, `LeaveBalance`
6. Celery task: `payroll.accrue_leave_balances` â€” weekly, runs accrual for all active employees
7. Integrate: when leave approved, block crew member from scheduling tasks during that period

**Frontend tasks:**
1. Resource Management page section "Leave": calendar heatmap of team leave, request form, approval queue for admins
2. In crew availability view (scheduling): show leave blocks as red periods

**Complexity:** L
**Dependencies:** None (extends payroll app)

---

### 7.2 â€” Skills Matrix

**Backend tasks:**
1. `Skill` model (TenantModel): `name`, `category` (TRADE/CERT/SOFTWARE/SOFT_SKILL)
2. `EmployeeSkill` model: `employee` FK, `skill` FK, `proficiency_level` (1-5 scale), `certified_at` DateField, `expires_at` DateField, `certification_number`
3. `SkillViewSet`, `EmployeeSkillViewSet`
4. `GET /api/v1/payroll/employees/skills-matrix/` â€” returns org-wide skills matrix as 2D data (employees x skills with proficiency levels)
5. `GET /api/v1/scheduling/crews/skill-match/?skill_ids=` â€” returns crews/employees who have specified skills above a minimum proficiency

**Frontend tasks:**
1. Skills Matrix page: spreadsheet-style grid (employees as rows, skills as columns, proficiency dots in cells)
2. Crew assignment filter by skill in scheduling task creation

**Complexity:** M
**Dependencies:** 7.1

---

### 7.3 â€” Scenario Planning + Billable/Non-Billable Reporting

**Backend tasks:**
1. `ResourceScenario` model (TenantModel): `name`, `base_schedule_snapshot` JSONField (copy of current schedule state), `adjustments` JSONField (list of changes to apply), `is_active`
2. `ScenarioService.simulate(scenario)`: applies adjustments to snapshot, returns projected resource utilization + cost
3. Extend `scheduling.Task`: add `is_billable` BooleanField, `billing_rate` DecimalField (nullable â€” falls back to crew.hourly_rate)
4. `GET /api/v1/scheduling/reports/billable-utilization/?start=&end=` â€” returns hours split by billable/non-billable per crew member per project

**Frontend tasks:**
1. Scenario planner: "What if" panel allowing temporary task/crew reassignment; show impact on costs
2. Billable vs non-billable report chart (stacked bar by week, filterable by project/crew)

**Complexity:** L
**Dependencies:** 7.1, 7.2

---

## Phase 8: Billing Enhancements (P2)

### 8.1 â€” Multi-Currency

**Backend tasks:**
1. Add `currency` CharField (ISO 4217, default "USD") to `financials.Invoice`, `financials.Budget`, `estimating.Estimate`, `financials.ChangeOrder`
2. `CurrencyService`:
   - `get_exchange_rate(from_currency, to_currency, date)`: fetch from Open Exchange Rates API (configurable), cache 1 hour in Redis
   - `convert(amount, from_currency, to_currency, date)`: returns converted `Decimal`
3. Add `base_currency` field to `Organization` settings JSONField
4. `CurrencyConversion` log model: `from_currency`, `to_currency`, `rate`, `fetched_at`
5. All financial report endpoints: accept `?currency=` param, convert amounts on the fly using cached rates
6. Add `babel` to requirements; use `babel.numbers.format_currency()` in serializers for display formatting

**Frontend tasks:**
1. Currency selector in invoice/estimate create forms
2. Organization settings: base currency
3. All financial figures display with currency symbol and locale formatting

**Complexity:** L
**Dependencies:** None

---

### 8.2 â€” Dunning Workflows

**Backend tasks:**
1. `DunningRule` model (TenantModel): `name`, `days_past_due` IntegerField, `action_type` (EMAIL_REMINDER/SUSPEND_PORTAL/FLAG_ESCALATION), `email_template` FK (communications.EmailTemplate), `is_active`
2. `DunningEvent` model: `invoice` FK, `rule` FK, `triggered_at`, `action_taken`, `success`
3. `DunningService.process_overdue_invoices()`: for each overdue invoice, checks which `DunningRule` thresholds have been crossed but not yet triggered, executes action
4. Celery task: `financials.run_dunning_workflow` â€” daily 8am

**Frontend tasks:**
1. Settings > Billing > Dunning: list/create/edit dunning rules (timeline visual showing when each rule fires)

**Complexity:** M
**Dependencies:** 8.1, 6.3 (email templates)

---

### 8.3 â€” Client Payment Portal (Hosted)

**Backend tasks:**
1. Existing `Invoice` model has `public_token` UUID field; extend:
   - Add `payment_due_date`, `payment_terms` CharField, `allow_partial_payment` BooleanField, `minimum_payment_amount` DecimalField
2. `PaymentPortalService`:
   - `generate_payment_link(invoice)`: returns URL `{FRONTEND_URL}/pay/{public_token}`
   - `create_payment_intent(invoice, amount)`: calls `stripe.PaymentIntent.create()` with amount
   - `confirm_payment(payment_intent_id)`: called by Stripe webhook, records payment, sends receipt
3. Public endpoint (no auth): `GET /api/v1/public/invoices/{public_token}/` â€” returns invoice summary for payment page
4. `POST /api/v1/public/invoices/{public_token}/pay/` â€” creates Stripe PaymentIntent, returns `client_secret`
5. Stripe webhook: handle `payment_intent.succeeded` â†’ record payment â†’ send receipt email

**Frontend tasks:**
1. Public-facing `/pay/:token` route (no auth required)
2. Invoice summary display + Stripe Elements payment form
3. Success/failure confirmation page

**Complexity:** M
**Dependencies:** 8.1 (currency on invoices)

---

## Phase 9: Forms & Checklists Builder (P2)

### 9.1 â€” Drag-and-Drop Form Builder

**Note:** `apps/quality_safety/` has `InspectionChecklist` model with checklist items. The new builder generalizes this.

**Backend tasks:**
1. `FormTemplate` model (TenantModel): `name`, `description`, `form_type` (INSPECTION/LEAD_CAPTURE/CUSTOM/SAFETY), `schema` JSONField (array of field definitions), `is_public` BooleanField, `public_slug` CharField (unique), `is_active`
2. Field definition schema (stored in JSONField): `{id, type, label, required, options, conditional_logic, validation}`
3. Field types supported: text, textarea, number, date, time, dropdown, multi-select, checkbox, radio, file_upload, signature, rating, section_header, spacer, geolocation
4. `FormSubmission` model (TenantModel, nullable org for public forms): `form_template` FK, `submitted_by` FK (nullable), `submitter_name`, `submitter_email`, `data` JSONField (field_id â†’ value), `ip_address`, `completed_at`
5. `GET/POST /api/v1/forms/templates/`, `GET/POST /api/v1/forms/submissions/`, `GET /api/v1/forms/templates/{pk}/analytics/`
6. Public submission endpoint (no auth): `GET /api/v1/public/forms/{slug}/` (schema), `POST /api/v1/public/forms/{slug}/submit/`
7. Migrate `InspectionChecklist` to use `FormTemplate` as its backing schema OR add adapter so existing checklists render through the new form engine

**Frontend tasks:**
1. Install `@dnd-kit/core` (already needed for Kanban), use for form builder
2. `FormBuilderPage.tsx`: left panel (field type palette), center canvas (drag-and-drop field ordering), right panel (field properties)
3. Field property panel: label, placeholder, required toggle, options editor (for dropdowns), conditional logic builder (if field X = value Y, show/hide this field)
4. `FormRenderer.tsx`: renders any form schema for data collection; used in mobile offline mode (IndexedDB queue)
5. Public form embed: `/forms/fill/:slug` route, no auth required

**Complexity:** XL
**Dependencies:** None

---

### 9.2 â€” Conditional Logic

Already included in 9.1 schema design. Frontend: visual logic builder (condition builder UI with AND/OR groups).

**Complexity:** M (included in 9.1 estimate)
**Dependencies:** 9.1

---

### 9.3 â€” Form Analytics

**Backend tasks:**
1. `GET /api/v1/forms/templates/{pk}/analytics/`:
   - Submission count over time (by day/week)
   - Completion rate (started vs completed â€” requires tracking partial submissions)
   - Average completion time
   - Per-field response distribution (for dropdowns/radio)
2. Add `started_at` DateTimeField to `FormSubmission`; `POST /api/v1/public/forms/{slug}/start/` â€” creates in-progress submission, returns session ID
3. `PATCH /api/v1/public/forms/{slug}/submit/{session_id}/` â€” updates in-progress submission (enables completion rate tracking)

**Frontend tasks:**
1. Form analytics dashboard: submission trend chart, completion rate gauge, per-field breakdown

**Complexity:** M
**Dependencies:** 9.1

---

## Phase 10: Issue Tracking (P1 â€” new app)

### 10.1 â€” Core Issue Tracking Module

**Backend tasks:**
1. Create `apps/issue_tracking/` app
2. Models:
   - `IssueType` (TenantModel): `name`, `description`, `icon`, `color`, `default_priority`, `sla_response_hours`, `sla_resolution_hours`
   - `Issue` (TenantModel): `number` (auto, per-org), `title`, `description`, `issue_type` FK, `project` FK (nullable), `client` FK (nullable), `assignee` FK, `reporter` FK, `priority` (CRITICAL/HIGH/MEDIUM/LOW), `status` (NEW/OPEN/IN_PROGRESS/PENDING/RESOLVED/CLOSED), `sla_response_due_at`, `sla_resolution_due_at`, `sla_response_met` BooleanField, `sla_resolution_met` BooleanField, `tags` JSONField, `custom_fields` JSONField
   - `IssueComment` model: same pattern as collaboration.Comment (or reuse it via ContentType)
   - `IssueAttachment` (TenantModel): `issue` FK, `file_key`, `filename`, `file_size`, `uploaded_by` FK
   - `CannedResponse` (TenantModel): `name`, `content`, `issue_type` FK (nullable â€” global or type-specific)
   - `EscalationRule` (TenantModel): `trigger_condition` JSONField, `action_type` (REASSIGN/NOTIFY/CHANGE_PRIORITY), `action_config` JSONField
3. Services:
   - `IssueNumberService.generate(org)`: sequential per org, format `ISS-{SEQ:05d}`
   - `SLAService.calculate_due_dates(issue)`: computes response/resolution due dates from `IssueType` SLA config, respects business hours
   - `SLAService.check_sla_breaches()`: called by Celery, marks overdue issues, triggers escalations
   - `EscalationService.process_rules(issue)`: evaluates escalation rules against current issue state
4. Celery tasks: `issue_tracking.check_sla_breaches` â€” every 15 min; `issue_tracking.send_sla_warning_notifications` â€” every 30 min
5. Signals: `on_issue_created` â€” calculates SLA, sends notification to assignee; `on_issue_status_changed` â€” logs activity, checks SLA met flags
6. ViewSets for all models + report endpoint `GET /api/v1/issue-tracking/reports/sla-compliance/`
7. Add `ISSUE_TRACKING` to `ActiveModule.ModuleKey`

**Frontend tasks:**
1. Issue tracking route `/issues`
2. `IssuesPage.tsx`: list view with filters (status, priority, type, assignee), search
3. Issue detail page: full detail with comment thread (reuse `CommentThread.tsx`), SLA countdown timers (visual badge turning yellow/red as deadline approaches), status transitions, canned response picker
4. Issue create modal: type picker, project/client link, priority selector, assignee
5. SLA dashboard widget showing compliance rates

**Complexity:** XL
**Dependencies:** 4.1 (comments), 4.3 (notifications)

---

## Phase 11: OKRs (P2 â€” new app)

### 11.1 â€” Core OKR Module

**Backend tasks:**
1. Create `apps/okrs/` app
2. Models:
   - `OKRCycle` (TenantModel): `name`, `cycle_type` (ANNUAL/QUARTERLY/MONTHLY), `start_date`, `end_date`, `is_active`
   - `Objective` (TenantModel): `title`, `description`, `cycle` FK, `owner` FK (User), `parent_objective` FK (self â€” cascading), `team` CharField (nullable), `status` (ON_TRACK/AT_RISK/BEHIND/ACHIEVED/MISSED), `confidence_score` (1-10)
   - `KeyResult` (TenantModel): `objective` FK, `title`, `metric_type` (PERCENTAGE/NUMBER/CURRENCY/BOOLEAN), `baseline_value`, `target_value`, `current_value`, `unit` CharField
   - `CheckIn` (TenantModel): `key_result` FK, `checked_in_by` FK, `current_value`, `confidence_score`, `notes`, `checked_in_at`
3. Services:
   - `OKRProgressService.calculate_objective_progress(objective)`: aggregates key result completion percentages, returns 0-100
   - `OKRProgressService.calculate_alignment_score(org, cycle)`: measures how well KR progress maps to objectives
   - `OKRService.auto_update_status(objective)`: sets status based on progress and days remaining
4. Celery task: `okrs.recalculate_progress` â€” daily, recalculates all active cycle objective statuses
5. ViewSets for all models; report `GET /api/v1/okrs/reports/alignment/`
6. Add `OKRS` to `ActiveModule.ModuleKey`

**Frontend tasks:**
1. OKRs route `/okrs`
2. Cycle selector in page header
3. `ObjectiveTree.tsx`: expandable tree of objectives with cascading key results; progress bars
4. `AlignmentMap.tsx`: horizontal hierarchy visualization showing org > team > individual objective alignment (use `d3` or CSS flexbox tree)
5. Check-in modal: slider for confidence score, numeric input for current value, notes field
6. OKR health overview: status distribution donuts per cycle

**Complexity:** XL
**Dependencies:** 4.3 (notifications for check-in reminders)

---

## Phase 12: Integrations Completion (P2)

### 12.1 â€” QuickBooks/Xero Actual Sync

**Note:** `QuickBooksSyncService` in `apps/integrations/services.py` has OAuth2 flow already coded. The data sync methods are stubs.

**Backend tasks:**
1. Complete `QuickBooksSyncService`:
   - `sync_invoices(connection)`: push BuilderStream invoices to QB as Invoices; pull QB payments back
   - `sync_expenses(connection)`: pull QB bills/expenses into BuilderStream financials
   - `sync_contacts(connection)`: bidirectional contact sync (QB Customers â†” crm.Contact)
   - `sync_vendors(connection)`: QB Vendors â†” crm.Company
   - `handle_webhook(payload)`: process QB webhook events (payments received, bills updated)
2. `XeroSyncService`: same interface, Xero API v2 (OAuth2)
3. Celery tasks: `integrations.sync_quickbooks` â€” every 15 min per connected org; `integrations.sync_xero` â€” every 15 min
4. Conflict resolution: last-write-wins with `last_synced_at` timestamp tracking; log conflicts to `SyncLog`

**Frontend tasks:**
1. Integrations page: QB/Xero connection status, last sync time, sync now button
2. Sync conflict resolver: list of conflicts requiring manual resolution (select which version wins)

**Complexity:** XL
**Dependencies:** None (infrastructure exists)

---

### 12.2 â€” Slack Integration

**Backend tasks:**
1. Add `slack` to `IntegrationConnection.IntegrationType`
2. `SlackIntegrationService`:
   - `install(code, org)`: exchanges OAuth code for bot token, stores in `IntegrationConnection`
   - `send_notification(channel, message, attachments)`: calls Slack Web API
   - `handle_slash_command(payload)`: handles `/builderstream` slash command (returns project status, create task, etc.)
3. `SlackEvent` model: log incoming Slack events
4. Webhook: `POST /api/v1/webhooks/slack/` (no auth, signature verification via `X-Slack-Signature`)
5. Notification integration: `NotificationService` channel type `SLACK`; users can set their Slack user ID in profile to receive DMs

**Frontend tasks:**
1. Integrations page: Slack connect button (OAuth), channel mapping (which org notifications go to which Slack channel)

**Complexity:** L
**Dependencies:** 4.3

---

### 12.3 â€” Calendar Sync (Google + Outlook)

**Backend tasks:**
1. `CalendarSyncService`:
   - `push_milestone(milestone, connection)`: creates Google Calendar event or Outlook event
   - `push_task(task, connection)`: creates calendar event for tasks with due dates
   - `sync_user_calendar(user, connection)`: pulls user's existing calendar events to check availability (feeds into scheduling conflict detection)
2. Celery task: `integrations.sync_calendars` â€” every 30 min

**Frontend tasks:**
1. User profile > Integrations: connect Google Calendar / Outlook Calendar (OAuth)
2. Scheduling page: toggle "Show calendar events" to overlay personal calendar on Gantt

**Complexity:** L
**Dependencies:** None

---

### 12.4 â€” Zapier/Make.com Webhooks

**Backend tasks:**
1. Extend existing `apps/integrations/models.py` `WebhookEndpoint` model: add `trigger_event` CharField (specific event like `project.created`), `filter_conditions` JSONField (e.g., only fire if `status=completed`), `secret_key`, `retry_count`, `max_retries`
2. `ZapierTriggerService.fire(event_type, payload, org)`: finds all active webhook endpoints for event + org, calls `WebhookDispatchService` (already exists)
3. Extend `WebhookDispatchService` with retry logic: on 4xx/5xx, schedule retry with exponential backoff via Celery
4. Zapier webhook subscription endpoint: `POST /api/v1/public/webhook-subscriptions/` (Zapier's standard polling-to-webhook migration pattern)

**Frontend tasks:**
1. Integrations page: webhook management (create, test, view delivery log)

**Complexity:** M
**Dependencies:** None (existing webhook infrastructure)

---

### 12.5 â€” Zoom Integration

**Backend tasks:**
1. `ZoomIntegrationService`: OAuth flow, `create_meeting(topic, start_time, duration)` â†’ returns join URL, `add_to_project(project, meeting_data)`
2. Extend `scheduling.Task` or `collaboration.Channel`: add `zoom_meeting_url` CharField, `zoom_meeting_id`

**Frontend tasks:**
1. In task detail or channel header: "Start Zoom Meeting" button
2. Meeting join link display in project timeline

**Complexity:** S
**Dependencies:** None

---

## Phase 13: Document Enhancements (P3)

### 13.1 â€” Real-Time Collaborative Editing

**Backend tasks:**
1. Evaluate approach: for MVP, use Y.js Conflict-free Replicated Data Type (CRDT) with the `y-websocket` server (standalone Node.js process) OR implement a basic OT approach in Django Channels
2. Recommended: Add a lightweight `y-websocket` container in docker-compose (Node.js, port 1234); BuilderStream backend handles auth and document creation; Y.js handles the CRDT sync
3. `CollaborativeDocument` model: `document` FK (documents.Document), `content_json` JSONField (Y.js snapshot), `version` IntegerField
4. Auth handshake: when user connects to `ws/docs/{document_id}/`, verify JWT, authorize against document access, pass user identity to Y.js room

**Frontend tasks:**
1. Install `yjs`, `y-websocket`, `@tiptap/extension-collaboration`, `@tiptap/extension-collaboration-cursor`
2. Wrap document editor in Y.js provider; Tiptap extension handles cursor rendering for other users

**Complexity:** XL
**Dependencies:** 0.1 (Channels or separate WS server), 3.1 (Tiptap already installed)

---

### 13.2 â€” OCR

**Backend tasks:**
1. Add `pytesseract`, `pdf2image`, `Pillow` (already installed) to requirements
2. `OCRService.extract_text(file_key)`: downloads from S3, converts to images, runs Tesseract, returns structured text
3. Add `ocr_text` TextField to `documents.Document`, `ocr_status` CharField (PENDING/PROCESSING/DONE/FAILED)
4. Celery task: `documents.run_ocr(document_id)` â€” triggered on PDF/image upload; `tesseract` must be installed in Docker image (add to `Dockerfile`)
5. Search integration: Phase 15 universal search indexes `ocr_text` field

**Frontend tasks:**
1. Document detail: "OCR Text" tab showing extracted text with copy button
2. Search results can highlight OCR text matches

**Complexity:** M
**Dependencies:** 15.1 (search for full value)

---

### 13.3 â€” Google Drive / Dropbox / OneDrive Integration

**Backend tasks:**
1. `CloudStorageService` interface: `list_files(path)`, `download_file(file_id)`, `upload_file(content, name)`, `get_preview_url(file_id)`
2. Implement for Google Drive (`google-api-python-client`), OneDrive (`O365`), Dropbox (`dropbox` SDK)
3. `LinkedCloudFile` model (TenantModel): `document` FK (nullable â€” can link to project without a full document record), `provider` CharField, `provider_file_id`, `provider_path`, `name`, `size`, `web_url`, `thumbnail_url`, `last_synced_at`
4. Import endpoint: `POST /api/v1/documents/import-from-cloud/` â€” fetches file from cloud, uploads to S3, creates `Document` record

**Frontend tasks:**
1. Documents page: "Connect cloud storage" button; file picker modal showing cloud folder tree

**Complexity:** L
**Dependencies:** None

---

### 13.4 â€” File Preview for 100+ Types

**Backend tasks:**
1. Use `LibreOffice` headless (Docker) to convert Office docs (docx, xlsx, pptx) to PDF â†’ then render with browser native PDF viewer
2. Alternative for quick implementation: integrate with a third-party preview API (PSPDFKit, Filestack Transform)
3. `FilePreviewService.get_preview_url(document)`: for PDF/images returns S3 presigned URL directly; for Office docs returns converted PDF URL (cached in S3); for video returns S3 HLS stream URL
4. Add `preview_url` as computed field in `DocumentSerializer`

**Frontend tasks:**
1. In document list/detail: click-to-preview slide-out panel
2. Preview renderer: `<iframe>` for PDF, `<img>` for images, `<video>` for video, `<audio>` for audio, syntax-highlighted code view for code files

**Complexity:** L
**Dependencies:** None

---

## Phase 14: Custom Fields + Workflow Builder (P2 â€” new app)

### 14.1 â€” Custom Fields Engine

**Backend tasks:**
1. Create `apps/custom_fields/` app
2. `CustomFieldDefinition` model (TenantModel): `name`, `api_key` (slugified, unique per org+entity), `entity_type` (PROJECT/CONTACT/LEAD/ESTIMATE/TASK/ISSUE), `field_type` (15 types: text, number, currency, date, datetime, checkbox, dropdown, multi_select, url, email, phone, user, file, rating, formula), `options` JSONField (for dropdown/multi_select), `formula` TextField (for formula type), `is_required` BooleanField, `default_value`, `display_order`, `section` CharField (groups fields in UI)
3. `CustomFieldValue` model: `definition` FK, `content_type` FK (GenericFK), `object_id` UUIDField, `value_text`, `value_number`, `value_json`, `value_date` â€” polymorphic storage
4. `CustomFieldService.get_values_for_object(obj)`: returns dict of `{api_key: value}` for an entity
5. `CustomFieldService.set_values(obj, data)`: validates and saves all custom field values for an entity
6. Hook custom fields into existing ViewSets via `CustomFieldMixin`:
   - Override `get_serializer_context()` to include custom field definitions
   - Add `custom_fields` to serializer output as a computed dict
   - Add `custom_fields` to `perform_create`/`perform_update` via mixin

**Frontend tasks:**
1. Settings > Custom Fields: entity type selector, field definition list, create/edit field drawer
2. Formula builder: simple expression builder (add/subtract/multiply other field values or constants)
3. Inject custom fields into existing forms: each entity's create/edit form has a "Custom Fields" section at the bottom, rendered dynamically from field definitions
4. Custom fields filter: filter lists by custom field values

**Complexity:** XL
**Dependencies:** None; but must be done before workflow builder

---

### 14.2 â€” Visual Workflow Builder

**Backend tasks:**
1. `WorkflowDefinition` model (TenantModel): `name`, `trigger_entity` (PROJECT/LEAD/ISSUE/TASK), `trigger_event` (CREATED/STATUS_CHANGED/FIELD_CHANGED/DUE_DATE_APPROACHING), `trigger_conditions` JSONField (filter conditions), `is_active`
2. `WorkflowStep` model: `workflow` FK, `step_order` IntegerField, `step_type` (ASSIGN/SEND_EMAIL/CREATE_TASK/UPDATE_FIELD/NOTIFY/WEBHOOK/WAIT), `config` JSONField, `condition_logic` JSONField (AND/OR conditions for conditional branching)
3. `WorkflowEngine.run(trigger_entity_type, trigger_event, instance)`:
   - Finds matching active `WorkflowDefinition` records
   - Evaluates trigger conditions against instance
   - Executes steps in order; respects WAIT steps via Celery countdown
4. Add `WorkflowEngine.run()` calls to signals in `apps/projects/signals.py`, `apps/crm/signals.py`, `apps/issue_tracking/` signals
5. `WorkflowExecution` log model: `workflow` FK, `triggered_by_id`, `status`, `step_results` JSONField, `started_at`, `completed_at`

**Frontend tasks:**
1. Workflow builder page: canvas-based node editor
   - Trigger block (entity + event + condition)
   - Action blocks (drag from palette to canvas, connect with arrows)
   - Condition branch blocks (IF/ELSE)
   - Configure each block via right-panel properties
2. Execution log table: shows recent runs with step-by-step results

**Complexity:** XL
**Dependencies:** 14.1

---

### 14.3 â€” White-Label Branding

**Backend tasks:**
1. `OrganizationBranding` model (TenantModel, OneToOne with org): `primary_color`, `secondary_color`, `logo_dark` ImageField, `logo_light` ImageField, `favicon` ImageField, `company_name_override`, `custom_domain` CharField, `hide_builderstream_branding` BooleanField
2. `GET /api/v1/tenants/branding/` â€” returns branding config for current org (public endpoint, cached)
3. CSS variables: backend returns branding; frontend applies as CSS custom properties

**Frontend tasks:**
1. `useBranding()` hook: fetches branding on app load, applies CSS variables (`--color-primary`, `--color-secondary`)
2. Settings > Branding: color pickers, logo upload (with preview), company name override
3. All hardcoded "BuilderStream" references replaced with `{branding.company_name_override || 'BuilderStream'}`

**Complexity:** M
**Dependencies:** None

---

### 14.4 â€” Localization (30+ Languages)

**Backend tasks:**
1. Add `django.middleware.locale.LocaleMiddleware` to MIDDLEWARE
2. Run `django-admin makemessages -l <locale>` for all target languages; use `django-rosetta` for translation UI
3. Add user `preferred_language` CharField to `accounts.User`
4. API responses: date/number formatting via `babel` using user's locale
5. Create locale files for initial 5 languages: `en`, `es`, `fr`, `de`, `pt`

**Frontend tasks:**
1. Install `i18next`, `react-i18next`, `i18next-http-backend`
2. Extract all UI string literals to `public/locales/{lang}/translation.json`
3. Language selector in user profile dropdown
4. RTL support via TailwindCSS `dir="rtl"` class on `<html>` for Arabic/Hebrew

**Complexity:** XL
**Dependencies:** None (can run in parallel)

---

## Phase 15: Universal Search (P2 â€” new app)

### 15.1 â€” Search Infrastructure

**Backend tasks:**
1. Create `apps/search/` app
2. Choose approach: **PostgreSQL full-text search** (no new infrastructure needed) vs Elasticsearch (new service). Recommend PostgreSQL FTS for Phase 1, with Elasticsearch migration path documented.
3. `SearchIndex` strategy using Django's `django.contrib.postgres.search`:
   - Add `search_vector` `SearchVectorField` to: `projects.Project`, `crm.Contact`, `crm.Lead`, `estimating.Estimate`, `documents.Document`, `service.ServiceTicket`, `issue_tracking.Issue`, `scheduling.Task`
   - Celery task: `search.update_search_vectors` â€” on post_save signals and periodically (nightly full rebuild)
4. `UniversalSearchService.search(query, org, user, entity_types, limit)`:
   - Executes `SearchQuery` across all entity types in parallel using `Union`
   - Returns ranked results with entity type, snippet, relevance score
   - Respects user's access permissions (module-gated results)
5. `SavedSearch` model (TenantModel): `name`, `query`, `entity_types` JSONField, `filters` JSONField, `is_smart_folder` BooleanField (auto-updates)
6. `GET /api/v1/search/?q=&types=&page=` â€” universal search endpoint
7. `GET/POST /api/v1/search/saved/` â€” saved searches CRUD

**Frontend tasks:**
1. Global search input in nav header (Command+K / Ctrl+K keyboard shortcut)
2. `SearchModal.tsx`: full-screen overlay with debounced search, results grouped by entity type, keyboard navigation
3. Result previews: entity-type-specific mini cards (project card shows status/client, contact shows company/email)
4. Saved searches panel in sidebar

**Complexity:** XL
**Dependencies:** 13.2 (OCR text in search index)

---

### 15.2 â€” AI-Powered Suggestions

**Backend tasks:**
1. `AISuggestionService` (stub with OpenAI/Claude API): `suggest_related(entity)` â€” returns list of related entities or actions; `suggest_next_action(project)` â€” context-aware next steps
2. Cache suggestions in Redis per entity ID (TTL 1 hour)
3. `GET /api/v1/search/suggestions/?entity_type=project&entity_id={uuid}` â€” returns AI suggestions

**Frontend tasks:**
1. "Related" panel in entity detail pages (projects, issues, contacts) showing AI suggestions
2. Smart search suggestions dropdown as user types (autocomplete powered by suggestions API)

**Complexity:** L
**Dependencies:** 15.1

---

## Phase 16: Analytics & Reporting Frontend (P2)

### 16.1 â€” Custom Report Builder UI

**Backend tasks:**
1. Extend `analytics.Report.query_config` schema to support:
   - `data_source`: entity type (projects, financials, tasks, etc.)
   - `dimensions`: list of fields to group by
   - `metrics`: list of aggregate functions (sum, count, avg) with field names
   - `filters`: list of filter conditions
   - `sort`: sort field + direction
   - `date_range`: relative (LAST_30_DAYS) or absolute
2. `ReportExecutionService.execute(report)`: translates `query_config` into Django ORM query, returns tabular data
3. `GET /api/v1/analytics/reports/{pk}/execute/` â€” run report, returns rows + column definitions
4. `POST /api/v1/analytics/reports/{pk}/schedule/` â€” configure email schedule (store cron in `report.schedule`)
5. Celery task: `analytics.send_scheduled_reports` â€” checks reports due to run at current cron expression

**Frontend tasks:**
1. Install `react-grid-layout` for resizable dashboard
2. Report builder wizard:
   - Step 1: data source selector
   - Step 2: dimension/metric selector (drag fields from schema panel to canvas)
   - Step 3: filter builder
   - Step 4: visualization picker (table, bar chart, line chart, pie chart, KPI card)
3. `ReportCanvas.tsx`: renders visualization using recharts (install `recharts`)
4. Schedule delivery modal: cron expression helper (daily/weekly/monthly presets), recipient email list
5. `AnalyticsPage` becomes a customizable dashboard of `Report` widgets dragged onto a grid

**Complexity:** XL
**Dependencies:** None

---

### 16.2 â€” Interactive Drill-Down Dashboards

**Backend tasks:**
1. Extend `analytics.Dashboard.widget_config` schema: each widget has `report_id` FK, `drill_down_field`, `drill_down_entity_type`
2. `GET /api/v1/analytics/dashboards/{pk}/widget/{widget_id}/drill-down/?dimension_value=` â€” runs a filtered sub-report for the clicked data point

**Frontend tasks:**
1. Dashboard widgets are clickable: clicking a bar in a chart opens a drill-down panel showing the underlying records
2. Breadcrumb trail tracking drill-down path

**Complexity:** M
**Dependencies:** 16.1

---

### 16.3 â€” Project Accounting UI (Revenue Recognition + Profitability)

**Backend tasks:**
1. `GET /api/v1/analytics/revenue-recognition/?project_id=&method=` â€” returns revenue recognized over time using Percentage of Completion or Completed Contract methods
2. `GET /api/v1/analytics/profitability/?group_by=client|team_member|project_type&start=&end=` â€” returns gross margin per grouping

**Frontend tasks:**
1. `ProjectAccountingPage.tsx` (extend `FinancialsPage`):
   - Revenue recognition timeline chart: planned vs actual vs recognized
   - Profitability table: sortable, filterable by client/team member/type

**Complexity:** M
**Dependencies:** 16.1

---

## Summary Table

| Phase | Feature | Priority | Complexity | New App? | Channels? | New Packages |
|---|---|---|---|---|---|---|
| 0.1 | Django Channels setup | P1 | M | No | Yes (foundational) | channels, channels-redis, daphne |
| 0.2 | 2FA (TOTP + SMS) | P1 | L | No | No | django-otp, django-two-factor-auth |
| 0.3 | IP Whitelist + Sessions + Audit Log | P1 | L | No | No | None |
| 1.1 | Kanban Board | P1 | M | No | No | @dnd-kit |
| 1.2 | Gantt View | P1 | L | No | No | frappe-gantt |
| 1.3 | Calendar View | P2 | M | No | No | @fullcalendar |
| 1.4 | Recurring Tasks | P2 | L | No | No | None |
| 1.5 | Subtask Hierarchies (FE) | P2 | S | No | No | None |
| 2.1 | CSV Import + Deduplication | P2 | L | No | No | pandas, djangorestframework-csv |
| 2.2 | Contact Enrichment | P3 | M | No | No | requests (already implied) |
| 2.3 | Relationship Mapping | P3 | M | No | No | d3 or react-force-graph |
| 3.1 | WYSIWYG Estimate Editor | P2 | XL | No | No | @tiptap/* |
| 3.2 | Estimate Version Diff | P2 | L | No | No | None |
| 3.3 | Conversion Tracking | P3 | S | No | No | None |
| 4.1 | Threaded Comments | P1 | L | Yes (collaboration) | Yes | None |
| 4.2 | Chat Channels + DMs | P1 | XL | Yes | Yes | @tanstack/react-virtual |
| 4.3 | Notification Preferences | P1 | L | No | Yes | None |
| 4.4 | External Collaborators | P2 | L | No | No | None |
| 5.1 | SSO / SAML 2.0 | P2 | XL | No | No | djangosaml2 |
| 6.1 | Email Sync Infrastructure | P2 | XL | Yes (communications) | No | imapclient, google-api-python-client, O365 |
| 6.2 | Email-to-Task | P2 | M | No | No | None |
| 6.3 | Email Templates + Campaigns | P2 | L | No | No | None |
| 7.1 | PTO / Leave Management | P2 | L | No | No | None |
| 7.2 | Skills Matrix | P3 | M | No | No | None |
| 7.3 | Scenario Planning + Billable Reports | P3 | L | No | No | None |
| 8.1 | Multi-Currency | P2 | L | No | No | babel |
| 8.2 | Dunning Workflows | P2 | M | No | No | None |
| 8.3 | Client Payment Portal | P2 | M | No | No | Stripe Elements (frontend) |
| 9.1 | Form Builder | P2 | XL | No (extends QS) | No | @dnd-kit (already) |
| 9.2 | Conditional Logic | P2 | M | Included | No | None |
| 9.3 | Form Analytics | P3 | M | Included | No | recharts |
| 10.1 | Issue Tracking Module | P1 | XL | Yes (issue_tracking) | No | None |
| 11.1 | OKR Module | P2 | XL | Yes (okrs) | No | None |
| 12.1 | QuickBooks/Xero Real Sync | P2 | XL | No | No | None (OAuth stubs exist) |
| 12.2 | Slack Integration | P2 | L | No | No | slack-sdk |
| 12.3 | Calendar Sync | P2 | L | No | No | google-api-python-client (already for 6.1), O365 |
| 12.4 | Zapier/Make Webhooks | P2 | M | No | No | None |
| 12.5 | Zoom Integration | P3 | S | No | No | None |
| 13.1 | Collaborative Doc Editing | P3 | XL | No | Yes | yjs, y-websocket |
| 13.2 | OCR | P3 | M | No | No | pytesseract, pdf2image |
| 13.3 | Cloud Storage Integration | P3 | L | No | No | google-api-python-client, dropbox |
| 13.4 | File Preview 100+ Types | P3 | L | No | No | LibreOffice (Docker) |
| 14.1 | Custom Fields Engine | P2 | XL | Yes (custom_fields) | No | None |
| 14.2 | Workflow Builder | P2 | XL | Included | No | None |
| 14.3 | White-Label Branding | P3 | M | No | No | None |
| 14.4 | Localization 30+ Languages | P4 | XL | No | No | i18next, babel, django-rosetta |
| 15.1 | Universal Search | P2 | XL | Yes (search) | No | recharts (already for 9.3) |
| 15.2 | AI Suggestions | P4 | L | No | No | openai or anthropic SDK |
| 16.1 | Custom Report Builder UI | P2 | XL | No | No | recharts, react-grid-layout |
| 16.2 | Drill-Down Dashboards | P2 | M | No | No | None |
| 16.3 | Revenue Recognition + Profitability | P2 | M | No | No | None |

---

## Recommended Execution Order

### Sprint 1 (Immediate foundations â€” must be done before anything real-time)
1. Phase 0.1 â€” Channels + ASGI
2. Phase 0.2 â€” 2FA
3. Phase 0.3 â€” Audit Log + Sessions

### Sprint 2 (Core UX gaps â€” highest user-visible impact)
4. Phase 1.1 â€” Kanban Board
5. Phase 1.2 â€” Gantt View
6. Phase 4.3 â€” Notification Preferences (prerequisite for chat UX)
7. Phase 14.3 â€” White-Label Branding (fast win, no dependencies)

### Sprint 3 (Collaboration foundation)
8. Phase 4.1 â€” Threaded Comments
9. Phase 4.2 â€” Team Channels + DMs
10. Phase 8.1 â€” Multi-Currency (unblocks billing suite)

### Sprint 4 (New modules + billing)
11. Phase 10.1 â€” Issue Tracking
12. Phase 8.2 â€” Dunning Workflows
13. Phase 8.3 â€” Client Payment Portal
14. Phase 14.1 â€” Custom Fields Engine

### Sprint 5 (Data + content)
15. Phase 11.1 â€” OKRs
16. Phase 9.1 â€” Form Builder
17. Phase 3.1 â€” WYSIWYG Estimate Editor
18. Phase 2.1 â€” CSV Import

### Sprint 6 (Integrations)
19. Phase 12.1 â€” QuickBooks/Xero Real Sync
20. Phase 12.2 â€” Slack
21. Phase 6.1 â€” Email Sync Infrastructure
22. Phase 5.1 â€” SSO/SAML

### Sprint 7 (Analytics + search)
23. Phase 16.1 â€” Custom Report Builder UI
24. Phase 15.1 â€” Universal Search
25. Phase 16.2 â€” Drill-Down Dashboards

### Sprint 8 (Polish + advanced)
26. Phase 7.1 â€” PTO / Leave
27. Phase 14.2 â€” Workflow Builder
28. Phase 1.4 â€” Recurring Tasks
29. Phase 13.2 â€” OCR
30. Phase 13.1 â€” Collaborative Editing

### Sprint 9 (P4 / enhancement)
31. Phase 14.4 â€” Localization
32. Phase 15.2 â€” AI Suggestions
33. Phase 12.3 â€” Calendar Sync
34. Remaining P3 items

---

## Key Architectural Decisions

1. **Django Channels over raw WebSocket:** Use `channels` + `daphne` (ASGI). This keeps everything in Django's ecosystem, reuses JWT auth, and integrates with existing `TenantMiddleware` patterns. The `ProtocolTypeRouter` routes HTTP to standard Django views and `ws://` to Channels consumers.

2. **PostgreSQL FTS over Elasticsearch for Universal Search:** No new infrastructure needed. Leverage Django's built-in `django.contrib.postgres.search.SearchVectorField`. Migration to Elasticsearch is straightforward if needed at scale â€” just swap the backend service.

3. **Y.js for Collaborative Editing:** Preferred over custom OT implementation. Run `y-websocket` as a separate lightweight Node.js container. BuilderStream handles auth and document CRUD; Y.js handles the CRDT sync protocol.

4. **New Apps vs Extending Existing:** New modules (collaboration, communications, okrs, issue_tracking, custom_fields, search) get their own apps following the established 16-app pattern. Each new app requires: `AppConfig` with `ready()` for signals, migrations, `ActiveModule` registration, URL namespace, and module key in `INSTALLED_APPS`.

5. **Custom Fields Storage:** Polymorphic EAV (Entity-Attribute-Value) pattern using `ContentType` FK and separate typed value columns rather than a single JSONField. This enables indexed queries on custom field values â€” critical for filtering and search.

6. **Real-time Architecture:** All real-time features route through the same Channels Redis layer (db 2). Consumer groups follow naming convention: `channel_{id}`, `comments_{type}_{id}`, `user_{id}_notifications`, `doc_{id}_edit`. JWT auth via query param `?token=` on WebSocket upgrade.

---

### Critical Files for Implementation

- `d:/Development/Builderds Stream Pro v3.0/builderstream/config/asgi.py` - Must be rewritten to ProtocolTypeRouter for all real-time features (Phase 0.1 â€” blocks all Channels work)
- `d:/Development/Builderds Stream Pro v3.0/builderstream/config/settings/base.py` - Needs CHANNEL_LAYERS, new INSTALLED_APPS entries, 2FA middleware, audit log middleware, and new module keys in ActiveModule (modified in nearly every phase)
- `d:/Development/Builderds Stream Pro v3.0/builderstream/apps/core/models.py` - TenantModel and TenantManager patterns that every new model must extend; AuditLog model goes here
- `d:/Development/Builderds Stream Pro v3.0/builderstream/apps/tenants/models.py` - ActiveModule.ModuleKey enum needs new module keys for collaboration, communications, okrs, issue_tracking, custom_fields added before those apps can be activated
- `d:/Development/Builderds Stream Pro v3.0/builderstream/frontend/src/router.tsx` - Every new module page (issues, okrs, communications, search, forms) requires a new route entry here, and the view toggle for Kanban/Gantt/Calendar is added to the existing projects routes