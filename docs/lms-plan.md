# LMS — Feasibility, Plan, and Pitch Brief

Prep note for the director meeting. Covers: how hard the LMS is to build, the
Google Drive video question, a build timeline, why it strengthens the pitch, and
what to say in the room. Timelines are estimates, not commitments.

---

## 1. Difficulty — low, because most of it already exists

The lab suite already has auth, role layers (student / faculty / admin), an
assessment/grading engine, and signed-PDF report generation. The LMS reuses all
of it. What is genuinely new is small:

- Content model: Course -> Module -> Lesson -> (video + notes/PDF)
- Player page + "mark complete" / watch-progress tracking
- Progress dashboard (dashboards already exist for the gradebook)
- Certification exam = the existing assessment engine pointed at a final test,
  plus a certificate PDF (signed lab-report PDFs already exist)

It is assembly of existing capabilities, not new invention.

---

## 2. Google Drive for video — possible for a pilot, not for scale

**Works:** embed the Drive file via the `/preview` URL
(`drive.google.com/file/d/FILE_ID/preview`) in an iframe; it plays in Drive's own
player, no download. Storage = Drive quota. Fine for a small pilot cohort.

**Real limits — state them up front:**

| Limit | Consequence |
|---|---|
| Per-file streaming quota | A whole batch watching one lecture can hit "quota exceeded, try later." Drive is not a video CDN. |
| No adaptive streaming | One fixed file; buffers on weak college Wi-Fi. |
| Access leakage | Files must be "anyone with link"; the link can be forwarded outside the platform. |
| Google can change it | Drive embeds have been restricted before without notice. |

**Recommendation:** use **YouTube unlisted** for videos (free, real CDN, adaptive
quality, handles a full batch) and **Google Drive for PDFs/notes**. Keep
progress, tests, and certification in the platform's own database — the video
host is only the pipe, swappable later (Cloudflare Stream / Bunny / Mux) without
touching anything else. Same honest split as the rest of the product: offline
where it needs to be, online only for the video stream.

**In the room:** promise "video lessons stream in the platform," NOT "plays
through Google Drive" — keeps the host swappable.

---

## 3. Build plan + timeline (estimates)

| Phase | Ships | Est. |
|---|---|---|
| A — MVP | Catalog, video playback, manual mark-complete, student view | ~2 weeks |
| B — Real tracking | Auto watch-progress %, per-student completion, admin/college/founder dashboard | ~1-2 weeks |
| C — Certification exam | Reuse assessment engine -> timed final exam, pass threshold, signed certificate PDF | ~2-3 weeks |
| D — One record | LMS progress + lab test results roll into a single per-student record for all three roles | ~1 week |
| **Pilot-ready (A+B)** | | **~3-4 weeks** |
| **Full v1 (A-D)** | | **~6-8 weeks** |

---

## 4. Why it matters — completes the tracking loop

Closes the arc into: **review lessons (LMS) -> hands-on practical (lab software,
in college) -> certification exam (same platform)** — completion and marks
visible to the college, admin, and founder, end to end, in one record.

- Strengthens **Slide 4 (accreditation):** outcome evidence now covers learning
  effort, not just final marks.
- Strengthens **Slide 5 (self-proving loop):** the one record now spans
  learn + practise + certify.

---

## 5. What to say to the director

> "Since we last spoke, I've decided to add an LMS so learning continues off the
> lab machines. Students review video lessons and notes there, then do the
> hands-on practical on the lab software in college, then sit a certification
> exam on the same platform. Every step — lessons watched, practical done, exam
> passed — is trackable by the college, the admin, and me, in one student record.
> For the pilot the videos stream in-platform, so there's zero infrastructure
> cost to the college; it's offline where it needs to be and online only for
> video, same as the real-hardware run. Pilot-ready in about three to four weeks,
> full learn-practise-certify loop in roughly six to eight."
