# Pair catalog

Common A↔B linkages by repo type. Each entry: the pair, what breaks when it
drifts, and extraction hints. Verify the mechanism on the real code before
writing the check — these are starting points, not guarantees.

## Android (any)
| # | A (definition) | B (must appear) | Breaks as | Extract A | Scan B |
|---|---|---|---|---|---|
| 1 | Feature toggle / enum entry | Editor UI row | Dead setting, user can't change it | enum entries + flags | UI tree references |
| 2 | `AndroidManifest` permission | Runtime `requestPermissions` call | Silent denial | `<uses-permission>` | `ActivityCompat.requestPermissions` args |
| 3 | Navigation route constant | `navController.navigate(...)` call sites | Dead screen | route registry | navigate args |
| 4 | `external fun` (Kotlin) | Native impl (`Java_*` or `RegisterNatives` table) | `UnsatisfiedLinkError` at runtime | `external fun` decls | C++ `Java_` symbols + `JNINativeMethod` tables |
| 5 | String resource key | `values-xx/strings.xml` per locale | Blank text in that locale | `R.string.*` refs | each `values*/strings.xml` |

## Backend / API
| # | A | B | Breaks as |
|---|---|---|---|
| 6 | Route handler | OpenAPI spec / docs | Undocumented endpoint |
| 7 | Env var read in code | `.env.example` | Deploys with missing config |
| 8 | DB migration file | Migration registry / applied order | Migration never runs |
| 9 | Error code defined | Client-side handling / docs | Unhandled error |

## Web frontend
| # | A | B | Breaks as |
|---|---|---|---|
| 10 | i18n key used in code | Locale JSON files | Missing translation |
| 11 | Route path defined | `<Link>` / router push sites | Dead link |

## Event / message systems
| # | A | B | Breaks as |
|---|---|---|---|
| 12 | Event name emitted | Event name subscribed | Event nobody handles |
| 13 | MCP tool documented | Tool implemented in handler | Doc lies / tool missing |

## CI / repo hygiene
| # | A | B | Breaks as |
|---|---|---|---|
| 14 | Check script in `scripts/checks/` | Reference in CI workflow (`.github/workflows/*.yml`) | Check never runs — dead file, false sense of safety |

Extract A: executable `*.sh` under `scripts/checks/` (basename). Scan B:
workflow YAML files for the script name. Escape hatch: `NO_CI_WIRE: <reason>`
comment at the top of the script (e.g. manual-only diagnostic tools).

## Choosing
Prefer pairs where (a) drift already caused a real bug, (b) both sides are
statically extractable, (c) the check runs in seconds. Start with one pair;
a suite grows pair by pair, not all at once.
