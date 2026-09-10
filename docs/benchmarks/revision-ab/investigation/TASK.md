# Audit production email exports

Audit this service catalogue as of **2026-09-10**. Identify every active
production service exporting `customer_email` to an external destination
without a valid waiver. Do not change the catalogue. Deliver `answer.json` and
a short final summary. You may add scratch scripts to compute/check the answer.

The complete service inventory is `catalogue/services/*.json`. Each service has
one route and names a profile under `catalogue/profiles/`. Effective exported
fields are the profile's `fields`, minus the service's `remove_fields`, plus
its `add_fields`. Empty lists mean no removals/additions. Skip inactive services,
non-production environments, internal destinations, and routes whose effective
fields do not include `customer_email`. Do not infer exposure from names or notes.

Owner is `owner_override` when nonempty; otherwise look up `team` in
`catalogue/ownership.json`. Service waiver documents live in `catalogue/waivers/`.
Each is Markdown with a JSON fenced record followed by explanatory prose. The
record is authoritative, not statements in the prose. A waiver is valid only if
it names that service, its scope includes `customer_email`, `starts <= assessed_at
< expires`, and revoked is either null or later than assessed_at. Dates are ISO
calendar dates. There is at most one waiver per service.

For an exposed service, report the first applicable invalid-waiver reason in
this order: `missing`, `scope`, `not_started`, `expired`, `revoked`. Service JSON
paths and waiver names share the same service identifier. `missing` means no
waiver document exists, not an unreadable or unexamined document.

Output schema (sort findings by service ID, no duplicates):

```json
{
  "assessed_at": "2026-09-10",
  "services_reviewed": 120,
  "findings": [
    {
      "service": "svc-000",
      "owner": "team-example",
      "reason": "missing",
      "evidence": [{"path": "catalogue/services/svc-000.json", "line": 1}]
    }
  ]
}
```

The example is a schema, not an expected finding. Each finding must cite its
service file, profile file, ownership file if owner is inherited, and waiver
file if present. Cite a relevant one-based line in each file containing the
service ID, `fields`, team name, or invalidating waiver field, respectively.
Reconcile the complete inventory count, including excluded services. All
records needed to decide are in this checkout. Use standard-library tools;
no network, dependencies, external repositories, evaluator files or other trials.
