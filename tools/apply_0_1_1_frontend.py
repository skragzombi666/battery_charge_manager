from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PATH = ROOT / "custom_components/battery_charge_manager/frontend/battery-charge-manager.js"


def replace_once(content: str, old: str, new: str, label: str) -> str:
    count = content.count(old)
    if count != 1:
        raise RuntimeError(f"{label}: expected exactly one match, found {count}")
    return content.replace(old, new, 1)


def main() -> None:
    content = PATH.read_text(encoding="utf-8")
    if "export { BcmBase, clampNumberValue, isEditingElement };" in content:
        print("0.1.1 frontend implementation already applied")
        return

    content = replace_once(
        content,
        '    idleRequired: "Vor der Kalibration ist mindestens eine gültige Leerlaufmessung der aktuellen Ladeanordnung erforderlich.",',
        '    idleRequired: "Keine zuverlässige Leerlaufmessung vorhanden. Die Kalibration wird vorläufig als Bruttomessung gespeichert und nach einer zuverlässigen Leerlaufmessung automatisch korrigiert.",\n'
        '    pendingCorrection: "Leerlaufkorrektur ausstehend",',
        "German provisional text",
    )
    content = replace_once(
        content,
        '    idleRequired: "At least one valid idle measurement for the current setup is required before calibration.",',
        '    idleRequired: "No reliable idle measurement is available. The calibration is stored provisionally as a gross measurement and corrected automatically after a reliable idle measurement.",\n'
        '    pendingCorrection: "Idle correction pending",',
        "English provisional text",
    )

    helper_marker = '''const navigateToPanel = () => {
  try {
    window.history.pushState(null, "", BCM_PANEL_PATH);
    window.dispatchEvent(new Event("location-changed"));
  } catch (_err) {
    window.location.assign(BCM_PANEL_PATH);
  }
};

'''
    helper_replacement = helper_marker + '''const isEditingElement = (element) => Boolean(
  element?.matches?.("input, select, textarea"),
);

const clampNumberValue = (value, minimum, maximum, fallback) => {
  const parsed = Number(value);
  const fallbackNumber = Number(fallback);
  if (value === "" || value === null || value === undefined || !Number.isFinite(parsed)) {
    return Number.isFinite(fallbackNumber) ? fallbackNumber : minimum;
  }
  return Math.min(maximum, Math.max(minimum, parsed));
};

'''
    content = replace_once(
        content,
        helper_marker,
        helper_replacement,
        "frontend helpers",
    )

    content = replace_once(
        content,
        '    this._busy = false;\n'
        '    this._error = "";\n'
        '  }\n\n'
        '  set hass(value) {\n'
        '    this._hass = value;\n'
        '    this._connect();\n'
        '    this.render();\n'
        '  }',
        '    this._busy = false;\n'
        '    this._error = "";\n'
        '    this._renderPending = false;\n'
        '    this.shadowRoot.addEventListener("focusout", () => {\n'
        '      queueMicrotask(() => this._flushDeferredRender());\n'
        '    });\n'
        '  }\n\n'
        '  set hass(value) {\n'
        '    this._hass = value;\n'
        '    this._connect();\n'
        '    this._requestRender();\n'
        '  }',
        "focus-safe hass setter",
    )
    content = replace_once(
        content,
        '  connectedCallback() {\n'
        '    this._connect();\n'
        '    this.render();\n'
        '  }\n',
        '  connectedCallback() {\n'
        '    this._connect();\n'
        '    this._requestRender(true);\n'
        '  }\n\n'
        '  _requestRender(force = false) {\n'
        '    if (!force && isEditingElement(this.shadowRoot?.activeElement)) {\n'
        '      this._renderPending = true;\n'
        '      return false;\n'
        '    }\n'
        '    this._renderPending = false;\n'
        '    this.render();\n'
        '    return true;\n'
        '  }\n\n'
        '  _flushDeferredRender() {\n'
        '    if (this._renderPending && !this.shadowRoot?.activeElement) {\n'
        '      this._requestRender(true);\n'
        '    }\n'
        '  }\n',
        "focus-safe render scheduler",
    )

    content = content.replace("      this.render();", "      this._requestRender();")

    content = replace_once(
        content,
        '    this._draft = {};\n'
        '  }\n',
        '    this._draft = {};\n'
        '    this._formValues = {\n'
        '      idleMin: 30,\n'
        '      idleMax: 480,\n'
        '      idleFixed: 300,\n'
        '      maxSession: null,\n'
        '    };\n'
        '  }\n',
        "persistent panel form state",
    )

    old_idle_fields = '<div class="bcm-form-grid"><div class="bcm-field"><label>${this.t("minMinutes")}</label><input id="idle-min" type="number" min="10" value="30"></div><div class="bcm-field"><label>${this.t("maxMinutes")}</label><input id="idle-max" type="number" min="30" value="480"></div><div class="bcm-field"><label>${this.t("durationMinutes")}</label><input id="idle-fixed" type="number" min="5" value="300"></div></div>'
    new_idle_fields = '<div class="bcm-form-grid"><div class="bcm-field"><label>${this.t("minMinutes")}</label><input id="idle-min" data-form-value="idleMin" type="number" min="10" max="1440" value="${esc(this._formValues.idleMin)}"></div><div class="bcm-field"><label>${this.t("maxMinutes")}</label><input id="idle-max" data-form-value="idleMax" type="number" min="30" max="1440" value="${esc(this._formValues.idleMax)}"></div><div class="bcm-field"><label>${this.t("durationMinutes")}</label><input id="idle-fixed" data-form-value="idleFixed" type="number" min="5" max="1440" value="${esc(this._formValues.idleFixed)}"></div></div>'
    content = replace_once(
        content,
        old_idle_fields,
        new_idle_fields,
        "persistent idle fields",
    )
    content = replace_once(
        content,
        '${idle.reliable_count ? "" : `<div class="bcm-error" style="margin-top:10px">${this.t("idleRequired")}</div>`}',
        '${idle.reliable_count ? "" : `<div class="bcm-note" style="margin-top:10px">${this.t("idleRequired")}</div>`}',
        "provisional calibration note style",
    )
    content = replace_once(
        content,
        '${s.session.mode !== "idle" || !idle.reliable_count || this._busy ? "disabled" : ""}',
        '${s.session.mode !== "idle" || this._busy ? "disabled" : ""}',
        "enable provisional calibration",
    )
    content = replace_once(
        content,
        '${this.metric(this.t("measurements"), String(summary.count || 0))}${this.metric(this.t("spread"),',
        '${this.metric(this.t("measurements"), String(summary.count || 0))}${this.metric(this.t("pendingCorrection"), String(summary.pending_count || 0))}${this.metric(this.t("spread"),',
        "pending calibration metric",
    )
    content = replace_once(
        content,
        '${item.valid ? this.t("valid") : this.t("invalid")}</span></td><td>${fmt(item.net_energy_wh)} Wh</td>',
        '${item.valid ? (item.idle_correction_status === "pending" ? this.t("pendingCorrection") : this.t("valid")) : this.t("invalid")}</span></td><td>${fmt(item.net_energy_wh)} Wh</td>',
        "pending calibration table status",
    )
    content = replace_once(
        content,
        '<input id="max-session" type="number" min="1" max="48" step="0.5" value="${esc(s.max_session_hours)}">',
        '<input id="max-session" data-form-value="maxSession" type="number" min="1" max="48" step="0.5" value="${esc(this._formValues.maxSession ?? s.max_session_hours)}">',
        "persistent settings value",
    )

    content = replace_once(
        content,
        '    this.shadowRoot.querySelectorAll("[data-draft]").forEach((el) => el.addEventListener("input", () => { this._draft[el.dataset.draft] = el.value; }));\n',
        '    this.shadowRoot.querySelectorAll("[data-draft]").forEach((el) => el.addEventListener("input", () => { this._draft[el.dataset.draft] = el.value; }));\n'
        '    this.shadowRoot.querySelectorAll("[data-form-value]").forEach((el) => {\n'
        '      el.addEventListener("input", () => {\n'
        '        this._formValues[el.dataset.formValue] = el.value;\n'
        '      });\n'
        '      el.addEventListener("change", () => this.commitNumberInput(el));\n'
        '    });\n',
        "bind persistent numeric values",
    )

    content = replace_once(
        content,
        '      if (action === "idle-auto") await this.call("start_idle_measurement", { mode:"automatic", auto_min_minutes:Number(this.shadowRoot.getElementById("idle-min")?.value || 30), auto_max_minutes:Number(this.shadowRoot.getElementById("idle-max")?.value || 480) });\n'
        '      if (action === "idle-fixed") await this.call("start_idle_measurement", { mode:"fixed", duration_minutes:Number(this.shadowRoot.getElementById("idle-fixed")?.value || 300) });\n'
        '      if (action === "save-settings") await this.call("set_settings", { max_session_hours:Number(this.shadowRoot.getElementById("max-session")?.value || 12) });',
        '      if (action === "idle-auto") {\n'
        '        const minimum = this.readNumberInput("idle-min", 30);\n'
        '        let maximum = this.readNumberInput("idle-max", 480);\n'
        '        if (maximum < minimum) {\n'
        '          maximum = minimum;\n'
        '          this._formValues.idleMax = maximum;\n'
        '          const field = this.shadowRoot.getElementById("idle-max");\n'
        '          if (field) field.value = String(maximum);\n'
        '        }\n'
        '        await this.call("start_idle_measurement", {\n'
        '          mode: "automatic",\n'
        '          auto_min_minutes: minimum,\n'
        '          auto_max_minutes: maximum,\n'
        '        });\n'
        '      }\n'
        '      if (action === "idle-fixed") await this.call("start_idle_measurement", {\n'
        '        mode: "fixed",\n'
        '        duration_minutes: this.readNumberInput("idle-fixed", 300),\n'
        '      });\n'
        '      if (action === "save-settings") await this.call("set_settings", {\n'
        '        max_session_hours: this.readNumberInput("max-session", 12),\n'
        '      });',
        "clamped action values",
    )

    content = replace_once(
        content,
        '  normalizeDraft(type) {\n',
        '  commitNumberInput(input, fallbackValue = undefined) {\n'
        '    const minimum = Number(input.min || Number.NEGATIVE_INFINITY);\n'
        '    const maximum = Number(input.max || Number.POSITIVE_INFINITY);\n'
        '    const key = input.dataset.formValue;\n'
        '    const stored = this._formValues[key];\n'
        '    const fallback = fallbackValue ?? (stored === "" || stored === null ? minimum : stored);\n'
        '    const value = clampNumberValue(input.value, minimum, maximum, fallback);\n'
        '    input.value = String(value);\n'
        '    this._formValues[key] = value;\n'
        '    return value;\n'
        '  }\n\n'
        '  readNumberInput(id, fallback) {\n'
        '    const input = this.shadowRoot.getElementById(id);\n'
        '    if (!input) return fallback;\n'
        '    return this.commitNumberInput(input, fallback);\n'
        '  }\n\n'
        '  normalizeDraft(type) {\n',
        "panel number helpers",
    )

    content = content.rstrip() + "\n\nexport { BcmBase, clampNumberValue, isEditingElement };\n"
    PATH.write_text(content, encoding="utf-8")
    print("Applied Battery Charge Manager 0.1.1 frontend implementation")


if __name__ == "__main__":
    main()
