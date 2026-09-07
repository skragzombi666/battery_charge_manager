from pathlib import Path

path = Path("custom_components/battery_charge_manager/frontend/battery-charge-manager.js")
content = path.read_text(encoding="utf-8")

old = '''  if (mode === "idle" && session.idle_measurement_mode === "fixed" && session.requested_duration_minutes) {
    lastTime = Math.max(lastTime, firstTime + Number(session.requested_duration_minutes) * 60000);
  }
  const span = Math.max(1, lastTime - firstTime);
'''
new = '''  if (mode === "idle" && session.idle_measurement_mode === "fixed" && session.requested_duration_minutes) {
    lastTime = Math.max(lastTime, firstTime + Number(session.requested_duration_minutes) * 60000);
  } else if (mode === "idle" && session.idle_measurement_mode === "automatic" && session.auto_min_minutes) {
    lastTime = Math.max(lastTime, firstTime + Number(session.auto_min_minutes) * 60000);
  }
  const span = Math.max(1, lastTime - firstTime);
'''
if old not in content:
    raise SystemExit("time-range block not found")
content = content.replace(old, new, 1)

old = '''  const powerValues = samples.map((item) => Number(item[powerKey])).filter(Number.isFinite);
  const energyValues = samples.map((item) => Number(item[energyKey])).filter(Number.isFinite);
'''
new = '''  const hasNumber = (value) => value !== null && value !== undefined && value !== "" && Number.isFinite(Number(value));
  const powerValues = samples.map((item) => item[powerKey]).filter(hasNumber).map(Number);
  const energyValues = samples.map((item) => item[energyKey]).filter(hasNumber).map(Number);
'''
if old not in content:
    raise SystemExit("series-values block not found")
content = content.replace(old, new, 1)

old = '''  const points = (key, y) => samples
    .filter((item) => Number.isFinite(Number(item[key])))
    .map((item) => `${x(item.time).toFixed(1)},${y(item[key]).toFixed(1)}`)
'''
new = '''  const points = (key, y) => samples
    .filter((item) => hasNumber(item[key]))
    .map((item) => `${x(item.time).toFixed(1)},${y(item[key]).toFixed(1)}`)
'''
if old not in content:
    raise SystemExit("series-points block not found")
content = content.replace(old, new, 1)

path.write_text(content, encoding="utf-8")
