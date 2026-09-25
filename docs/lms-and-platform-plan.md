# LMS & Platform — Architecture Decisions and Build Plan

Decisions and detailed plan for the LMS + hosting + data + assessment integration.
Product-architecture guidance, not legal advice — have a lawyer produce a reusable
Data Processing Agreement (DPA) template.

---

## 1. Hosting — own multi-tenant cloud server (decided)

Per-college servers do not scale: N deployments to maintain, no single update path,
and no cross-college adoption data (which the self-proving-loop pitch depends on).

**Decision:** one central multi-tenant server, hosted in an **India region**.
- One update reaches every college.
- Adoption/usage visible for quarterly reviews.
- Each college is a "tenant"; data is partitioned per college.

---

## 2. DPDP Act — be the Processor, not the Fiduciary

- **College = Data Fiduciary** (owns the student relationship + consent).
- **You = Data Processor** — process learning data on the college's instructions
  under a signed **DPA**. This keeps the heavy consent burden on the college.

**Keep on server (low-risk, necessary):** opaque internal student ID, register
number + name (for reports/certificates), progress, marks, submissions (circuits/
code), timestamps.

**Minimize / avoid:** phone, address, DOB (unless age-gating), government IDs,
anything not needed. Set a retention window; delete/anonymize after it. Never use
data beyond the stated purpose. No selling, no ads.

**Notes:** host data in India; under-18 students get stricter DPDP treatment, but
that sits mainly with the college as Fiduciary. Storing everything on the college's
own cloud is most DPDP-friendly but breaks scalability and the adoption dashboard —
do not do it. Own server + DPA + India region is the balance.

---

## 3. One student record — offline lab + LMS reconciliation

Everything hangs off a unique **student ID** in the central DB.

- **LMS (online):** writes progress directly — lessons watched, % complete, exam
  scores.
- **Offline lab:** records each submission locally (student ID + assignment ID +
  timestamp + hash). On next online connection it **syncs** queued records up.
  Idempotent key = student + assignment, so re-sync never duplicates.
- **Teacher check = authoritative gate (not transport):** student submits (offline)
  -> auto-grades locally -> syncs up -> teacher sees it -> teacher approves/grades
  -> LMS milestone flips to complete. Auto-grade past a professor-set threshold can
  stand in for the teacher's tick. Do NOT rely on the student's own check — that is
  the integrity hole.

**Record shape (per student, per module/assignment):** LMS lessons done, lab
submission, auto-score, teacher-approved flag, timestamp, source device ID.

Marks are not real-time — they appear after sync. State this plainly.

---

## 4. Deployment, licensing, updates

- Installer distributed via download link (Drive is fine for v1).
- **Per-device license key**, activated remotely; also identifies device + college
  for sync and adoption tracking (double duty). Issue/revoke remotely = license
  control.
- **Auto-updater** (build soon): app checks the server when online and patches
  itself, so releases don't require re-sending links to every college.

---

## 5. Video hosting

- **YouTube via the IFrame Player API** — gives play/pause/percent-watched/ended
  events the LMS reads for progress. Real CDN, adaptive quality, free.
- **Public** videos for intro/marketing (grows the channel); **unlisted** for the
  graded course spine. Platform tracks progress on both.
- Keep course videos **non-monetized** (no ads mid-lesson). `rel=0` limits
  suggestions to your channel.
- **Risk:** some campus networks block YouTube — confirm with college IT early;
  allowlist or fallback host if blocked.

---

## 6. Proctoring — human + lockdown, no webcam

The in-lab teacher is the proctor. In software add:
- **Lockdown/kiosk mode** — full-screen exam, disable alt-tab/other apps/copy-paste/
  external browser.
- **Activity flags** — log focus-loss/window-switch attempts for the teacher.
- **Per-student variants** — randomize assignment parameters to stop copying.
- **Skip webcam/biometric proctoring** — sensitive data under DPDP and redundant
  with a teacher present. Add only if a college demands remote exams.

---

## 7. Certificate — co-branded + verifiable

College name/logo + platform/company + course & modules completed + marks +
**unique QR / verification URL** resolving on your site to prove authenticity +
signatures (college authority + platform). Align wording to NQM/industry skills.
The verification link is what gives the certificate real credibility to employers.

---

## 8. LMS build plan (detailed)

**Data model (new tables, sharing existing auth/roles):**
- `courses` -> `modules` -> `lessons` (lesson: video ID, notes/PDF ref, order)
- `enrollments` (student <-> course, per college/tenant)
- `lesson_progress` (student, lesson, percent_watched, completed_at)
- `assessments` / `submissions` / `grades` (reuse existing engine)
- `certificates` (student, course, marks, verify_id, issued_at, college)

**Screens:**
- Student: course home, lesson player (YouTube IFrame + progress), notes, "my
  progress", take-exam, download certificate.
- Faculty: view class progress, approve/grade submissions, see mastery per concept.
- Admin/founder: cross-tenant adoption + progress dashboard.

**Phases (estimates):**
| Phase | Ships | Est. |
|---|---|---|
| A — LMS MVP | Catalog, YouTube playback + progress, student view | ~2 wks |
| B — Tracking + sync | Auto progress %, offline-lab sync, dashboards | ~1-2 wks |
| C — Certification | Timed exam (lockdown), pass threshold, co-branded verifiable cert PDF | ~2-3 wks |
| D — One record | LMS + lab + cert unified per-student record, all roles | ~1 wk |

**Open items for a lawyer / college:** DPA template, retention period, consent text,
certificate co-branding sign-off.
