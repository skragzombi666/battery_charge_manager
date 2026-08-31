# Architecture

## Components

- `manager.py`: persistent domain model, sensor tracking, measurement evaluation, endpoint detection, safety, and statistics.
- `models.py`: versioned setup, battery, idle-measurement, calibration, trace-sample, and session records.
- `websocket_api.py`: authenticated frontend read and control API.
- `panel.py`: frontend module serving, custom-card registration, and sidebar-panel registration.
- `frontend/battery-charge-manager.js`: side panel and Lovelace card.
- standard Home Assistant entity platforms: automation-facing controls and measurements.

## Persistence

Data is stored through Home Assistant's `Store` helper. Measurement records contain immutable setup and battery snapshots. Current calculations filter by the current object revision and explicit validity.

## Frontend access

The same JavaScript module defines the full panel and the compact card. The card uses the direct `/battery-charge-manager` route, so it continues to open the panel when the user hides the sidebar entry.

## Safety boundary

The integration controls mains power to an existing charger. It does not implement chemistry-specific charging control. The charger and battery protection electronics remain the primary electrical safety layer.
