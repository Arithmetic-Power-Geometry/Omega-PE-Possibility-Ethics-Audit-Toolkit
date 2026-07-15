# Changelog

## Version 1.0.1 — Corrected presentation record counts

- Corrected the presentation-level record counts.
- The authoritative analytic dataset contains 7,909 student-presentation records:
  1,767 (2013B), 2,237 (2013J), 1,613 (2014B), and 2,292 (2014J).
- Replaced the misleading `total_students` field with
  `student_presentation_records`.
- Regenerated the presentation comparison CSV, synthetic-versus-real JSON,
  validation report, figures, and README.
- Added an explicit validation check requiring the presentation counts to sum to
  the analytic dataset size.
- Preserved all Option Entropy, weighted-level, ranking, and Option Repair results.
