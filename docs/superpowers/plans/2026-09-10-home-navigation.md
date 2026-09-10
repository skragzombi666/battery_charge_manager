# Home and management navigation

The agreed daily task is normal charging. Quantity changes most often; battery
type changes every few charges. Both stay immediately editable. Setup and relative
energy target change rarely: show their current values with a collapsed editor.
Keep the existing server selection as the source of truth.

The home page shows any running operation first, with its live chart and controls.
A calibration starter can be expanded for periods of frequent calibration. Store
only its open/closed preference in browser-local storage (per HA user); default
closed, tolerate unavailable storage. Active calibration stays visible independently.

A compact header exposes the native HA sidebar menu and one management entry.
Management groups batteries, charging setups, idle measurements, calibration
history and settings. Child pages have explicit home/management navigation. A
running-operation link remains visible there. Histories, forms and live renderers
remain shared; no additional framework, service or duplicated measurement logic.

## Implementation sequence

1. Add regression tests for frequent/rare inputs, local disclosure persistence,
   live operations on home, management navigation and HA menu properties.
2. Replace peer tabs with home/management hierarchy. Extract existing live card
   rendering into reusable methods, shared by home and management pages.
3. Bind disclosure/selection/start actions with busy-state guards. After a
   successful start show home; failures retain inputs and their error.
4. Run Node and Python suites, syntax and diff checks. Independently review the
   diff and update release notes. Do not claim real browser/HA verification.

## Validation boundaries

Tests use the existing Node DOM stubs and fake HA Python environment. Cloud
browser access has failed; HA sidebar behavior and responsive appearance still
need a real HA check. No hardware commands, installation or publication are part
of local validation. Public GitHub publication still needs explicit permission.

## Outcome

Implemented on the existing isolated branch. Shared live renderers and selection
controls serve both navigation levels. HA's public icon control emits the native
sidebar event. Pending selection controls disable immediately, focus is restored
after completion, and navigation scrolls to the header. Independent review found
no critical or important issue; its three minor interaction findings were fixed
with regression coverage. Validation: 41 Python tests, 41 Node tests, JavaScript
syntax, Python compilation, four JSON files and diff whitespace checks. The
browser/HA limitations above remain.
