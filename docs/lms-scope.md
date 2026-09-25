# LMS — Scope (planning only)

The in/out boundary for the LMS, drawn on top of the architecture in
`lms-and-platform-plan.md`. Planning artifact — no code committed. Effort figures
are estimates, not commitments.

---

## Goal (one line)

Add an LMS module to the platform so learning continues off the lab machines, and
so one student record spans **lessons -> lab practical -> certification exam**,
visible to college, admin, and founder.

---

## In scope — v1 (MVP)

- Course -> Module -> Lesson catalog (content authored by faculty/admin).
- Video playback via **YouTube IFrame API**, with progress events
  (percent-watched, completed) written to the platform DB.
- Notes/PDF attachment per lesson (Drive links fine).
- Per-student progress tracking + a "my progress" view.
- Faculty view: class progress + per-concept mastery.
- Admin/founder cross-tenant adoption dashboard.
- Offline lab -> online **sync** of submissions/marks into the one student record.
- Teacher-gated completion (teacher approval flips the LMS milestone).
- Certification exam in **lockdown mode**, with a **co-branded, verifiable
  certificate** (QR/verify URL).

## Out of scope — later (v2+)

- Webcam/biometric proctoring (only if a college demands remote exams).
- Auto-updater (v1 can re-download installer; build this soon after).
- Discussion forums / peer interaction / messaging.
- Mobile app (web-responsive is enough for v1).
- Payment/billing inside the platform (handled offline, case by case).
- AI tutor beyond the existing Circuit Doctor coaching.
- Multi-language content.

---

## Assumptions

- The platform already has auth, role layers (student/faculty/admin), an
  assessment/grading engine, and signed-PDF generation to reuse.
- Videos live on the founder's YouTube channel (public = intro, unlisted = spine).
- Colleges have internet for the LMS/video/sync portions (lab stays offline).
- College is the Data Fiduciary; founder is Processor under a DPA.

---

## Dependencies / prerequisites to building

- Access to the product codebase (stack, existing data model, assessment engine).
- A reusable **DPA template** from a lawyer.
- Certificate **co-branding sign-off** + college logo per tenant.
- Central server + India-region hosting chosen.
- Confirmation campus networks allow YouTube (or a fallback host).

---

## Open decisions (blockers to flag before build)

1. Product stack + where the LMS module slots in (needs the repo).
2. Retention period for student data.
3. Public-vs-unlisted policy per content tier (marketing vs graded spine).
4. Exact fields stored server-side vs kept on the college side.
5. Auto-grade threshold vs mandatory teacher approval, per module.
6. Certificate authority signatures (who signs on the college side).

---

## Rough effort (from the build plan)

| Phase | Ships | Est. |
|---|---|---|
| A | LMS MVP (catalog, playback + progress, student view) | ~2 wks |
| B | Tracking + offline-lab sync + dashboards | ~1-2 wks |
| C | Certification (lockdown exam, verifiable co-branded cert) | ~2-3 wks |
| D | Unified one-record across LMS + lab + cert | ~1 wk |
| | **Pilot-ready (A+B)** | **~3-4 wks** |
| | **Full v1 (A-D)** | **~6-8 wks** |
