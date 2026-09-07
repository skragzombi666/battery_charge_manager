# 0.1.2 review checklist

- Calibration must not show the relative-charge-energy target.
- Charging must retain the relative-charge-energy target.
- Charging and calibration must show the exact configured first-N ports.
- Horizontal tab navigation must preserve scroll position across live rerenders.
- Active fixed idle measurement must show elapsed time, remaining time, expected end, progress, current power, accumulated energy, sample count, preliminary value and chart.
- Active automatic idle measurement must show elapsed time, minimum/max duration context, live estimate/reliability and chart without invented remaining-to-completion time.
- Active calibration must show phase, ports, duration, power/energy metrics, endpoint candidate information and chart without invented percent progress.
- Active charging must show real target-based progress, ports and chart with target-energy marker.
- Dashboard card must show ports and compact chart while charging.
- Frontend websocket state must bound chart data while retaining full-session first and last samples.
