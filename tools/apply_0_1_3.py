from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def read(path: str) -> str:
    return (ROOT / path).read_text(encoding="utf-8")


def write(path: str, content: str) -> None:
    (ROOT / path).write_text(content, encoding="utf-8")


def replace_once(content: str, old: str, new: str, label: str) -> str:
    count = content.count(old)
    if count != 1:
        raise RuntimeError(f"{label}: expected one match, found {count}")
    return content.replace(old, new, 1)


def patch_const() -> None:
    path = "custom_components/battery_charge_manager/const.py"
    content = read(path)
    content = replace_once(
        content,
        'VERSION = "0.1.2"\nALGORITHM_VERSION = "0.1.2"',
        'VERSION = "0.1.3"\nALGORITHM_VERSION = "0.1.3"',
        "version",
    )
    content = replace_once(content, "DATA_SCHEMA_VERSION = 3", "DATA_SCHEMA_VERSION = 4", "schema")
    write(path, content)


def patch_manifest() -> None:
    path = "custom_components/battery_charge_manager/manifest.json"
    data = json.loads(read(path))
    if data.get("version") != "0.1.2":
        raise RuntimeError(f"Unexpected manifest version {data.get('version')}")
    data["version"] = "0.1.3"
    write(path, json.dumps(data, indent=2, ensure_ascii=False) + "\n")


def patch_models() -> None:
    path = "custom_components/battery_charge_manager/models.py"
    content = read(path)
    content = replace_once(
        content,
        '    max_temperature_c: float | None = None\n    revision: int = 1',
        '    max_temperature_c: float | None = None\n    image: dict[str, Any] | str | None = None\n    revision: int = 1',
        "setup image field",
    )
    content = replace_once(
        content,
        '            "max_temperature_c": self.max_temperature_c,\n            "revision": self.revision,',
        '            "max_temperature_c": self.max_temperature_c,\n            "image": self.image,\n            "revision": self.revision,',
        "setup image serialization",
    )
    content = replace_once(
        content,
        '            max_temperature_c=_float_or_none(data.get("max_temperature_c")),\n            revision=_int_or(data.get("revision"), 1),',
        '            max_temperature_c=_float_or_none(data.get("max_temperature_c")),\n            image=data.get("image"),\n            revision=_int_or(data.get("revision"), 1),',
        "setup image deserialization",
    )
    write(path, content)


def patch_manager() -> None:
    path = "custom_components/battery_charge_manager/manager.py"
    content = read(path)
    content = replace_once(
        content,
        '        power_sensor = str(data.get("power_sensor", "")).strip() or None\n        temperature_sensor = (\n            str(data.get("temperature_sensor", "")).strip() or None\n        )',
        '        power_sensor = self._optional_entity_id(data.get("power_sensor"))\n        temperature_sensor = self._optional_entity_id(\n            data.get("temperature_sensor")\n        )',
        "optional setup sensors",
    )
    content = replace_once(
        content,
        '                max_temperature_c=self._optional_positive_float(\n                    data.get("max_temperature_c")\n                ),\n                created_at=now,',
        '                max_temperature_c=self._optional_positive_float(\n                    data.get("max_temperature_c")\n                ),\n                image=data.get("image") or None,\n                created_at=now,',
        "new setup image",
    )
    content = replace_once(
        content,
        '            existing.max_temperature_c = self._optional_positive_float(\n                data.get("max_temperature_c")\n            )\n            existing.updated_at = now',
        '            existing.max_temperature_c = self._optional_positive_float(\n                data.get("max_temperature_c")\n            )\n            existing.image = data.get("image") or None\n            existing.updated_at = now',
        "update setup image",
    )
    content = replace_once(
        content,
        '        nominal_capacity_mah = max(1, int(float(data.get("nominal_capacity_mah", 1000))))\n        nominal_voltage_v = self._optional_positive_float(data.get("nominal_voltage_v"))',
        '        raw_capacity = data.get("nominal_capacity_mah")\n        if raw_capacity in {None, ""}:\n            raise HomeAssistantError("Nominal capacity is required")\n        try:\n            nominal_capacity_mah = int(float(raw_capacity))\n        except (TypeError, ValueError) as err:\n            raise HomeAssistantError("Nominal capacity must be a number") from err\n        if nominal_capacity_mah <= 0:\n            raise HomeAssistantError("Nominal capacity must be greater than zero")\n        nominal_voltage_v = self._optional_positive_float(data.get("nominal_voltage_v"))',
        "required capacity",
    )
    insert_before = '''    @staticmethod\n    def _optional_positive_float(value: Any) -> float | None:\n'''
    helper = '''    @staticmethod\n    def _optional_entity_id(value: Any) -> str | None:\n        """Normalize an optional entity id without turning None into text."""\n        if value in {None, ""}:\n            return None\n        text = str(value).strip()\n        if not text or text.casefold() in {"none", "null"}:\n            return None\n        return text\n\n'''
    if insert_before not in content:
        raise RuntimeError("optional entity helper insertion point missing")
    content = content.replace(insert_before, helper + insert_before, 1)
    write(path, content)


def patch_websocket() -> None:
    path = "custom_components/battery_charge_manager/websocket_api.py"
    content = read(path)
    content = replace_once(
        content,
        'from __future__ import annotations\n\nfrom typing import Any',
        'from __future__ import annotations\n\nfrom functools import partial\nfrom typing import Any',
        "partial import",
    )
    content = replace_once(
        content,
        'from .const import DOMAIN, IDLE_MODE_AUTOMATIC\nfrom .manager import BatteryChargeManager',
        'from .const import DOMAIN, IDLE_MODE_AUTOMATIC\nfrom .image_store import save_uploaded_image\nfrom .manager import BatteryChargeManager',
        "image store import",
    )
    content = replace_once(
        content,
        '        ws_save_battery,\n        ws_delete_battery,',
        '        ws_save_battery,\n        ws_upload_image,\n        ws_delete_battery,',
        "register upload command",
    )
    marker = '''@websocket_api.require_admin\n@websocket_api.websocket_command(\n    {\n        vol.Required("type"): f"{DOMAIN}/delete_battery",\n'''
    upload = '''@websocket_api.require_admin\n@websocket_api.websocket_command(\n    {\n        vol.Required("type"): f"{DOMAIN}/upload_image",\n        vol.Required("filename"): str,\n        vol.Required("mime_type"): str,\n        vol.Required("data"): str,\n    }\n)\n@websocket_api.async_response\nasync def ws_upload_image(\n    hass: HomeAssistant,\n    connection: websocket_api.ActiveConnection,\n    msg: dict[str, Any],\n) -> None:\n    """Store an uploaded battery/setup image under /config/www."""\n    try:\n        path = await hass.async_add_executor_job(\n            partial(\n                save_uploaded_image,\n                hass.config.path(),\n                filename=msg["filename"],\n                mime_type=msg["mime_type"],\n                encoded_data=msg["data"],\n            )\n        )\n    except (OSError, ValueError) as err:\n        _send_error(connection, msg, err)\n        return\n    connection.send_result(msg["id"], {"path": path})\n\n\n'''
    if marker not in content:
        raise RuntimeError("upload insertion marker missing")
    content = content.replace(marker, upload + marker, 1)
    write(path, content)


def patch_frontend() -> None:
    path = "custom_components/battery_charge_manager/frontend/battery-charge-manager.js"
    content = read(path)
    content = replace_once(content, '    voltage: "Nennspannung (V)",', '    voltage: "Nennspannung (Ausgangsspannung) (V)",', "German voltage label")
    content = replace_once(content, '    image: "Bild-URL oder /local-Pfad",', '    image: "Bild-URL oder /local-Pfad",\n    uploadImage: "Bild hochladen",\n    removeImage: "Bild entfernen",\n    uploadingImage: "Bild wird hochgeladen …",', "German image strings")
    content = replace_once(content, '    voltage: "Nominal voltage (V)",', '    voltage: "Nominal voltage (output voltage) (V)",', "English voltage label")
    content = replace_once(content, '    image: "Image URL or /local path",', '    image: "Image URL or /local path",\n    uploadImage: "Upload image",\n    removeImage: "Remove image",\n    uploadingImage: "Uploading image …",', "English image strings")
    content = replace_once(
        content,
        '    this._renderPending = false;\n    this.shadowRoot.addEventListener("focusout", () => {',
        '    this._renderPending = false;\n    this._renderLock = 0;\n    this.shadowRoot.addEventListener("focusout", () => {',
        "render lock init",
    )
    content = replace_once(
        content,
        '  _requestRender(force = false) {\n    if (!force && isEditingElement(this.shadowRoot?.activeElement)) {',
        '  _requestRender(force = false) {\n    if (!force && this._renderLock > 0) {\n      this._renderPending = true;\n      return false;\n    }\n    if (!force && isEditingElement(this.shadowRoot?.activeElement)) {',
        "render lock behavior",
    )
    content = replace_once(
        content,
        '  async call(type, payload = {}) {\n    if (!this._hass || this._busy) return null;\n    this._busy = true;\n    this._error = "";\n    this.render();',
        '  async call(type, payload = {}, options = {}) {\n    if (!this._hass || this._busy) return null;\n    this._busy = true;\n    this._error = "";\n    if (options.renderBusy !== false) this._requestRender();',
        "call busy render",
    )
    content = replace_once(
        content,
        '    } finally {\n      this._busy = false;\n      this._requestRender();\n    }\n  }\n\n  entityOptions',
        '    } finally {\n      this._busy = false;\n      if (options.renderDone !== false) this._requestRender();\n    }\n  }\n\n  entityOptions',
        "call final render",
    )
    content = replace_once(
        content,
        '    this._tabsScrollLeft = 0;\n    this._formValues = {',
        '    this._tabsScrollLeft = 0;\n    this._dialogScrollTop = 0;\n    this._formValues = {',
        "dialog scroll init",
    )
    content = replace_once(
        content,
        '    const previousTabs = this.shadowRoot.querySelector(".bcm-tabs");\n    const tabsScrollLeft = previousTabs?.scrollLeft ?? this._tabsScrollLeft ?? 0;',
        '    const previousTabs = this.shadowRoot.querySelector(".bcm-tabs");\n    const tabsScrollLeft = previousTabs?.scrollLeft ?? this._tabsScrollLeft ?? 0;\n    const previousDialog = this.shadowRoot.querySelector(".bcm-dialog");\n    const dialogScrollTop = previousDialog?.scrollTop ?? this._dialogScrollTop ?? 0;',
        "capture dialog scroll",
    )
    content = replace_once(
        content,
        '      tabs.addEventListener("scroll", () => { this._tabsScrollLeft = tabs.scrollLeft; });\n    }\n    this.bindEvents();',
        '      tabs.addEventListener("scroll", () => { this._tabsScrollLeft = tabs.scrollLeft; });\n    }\n    const dialog = this.shadowRoot.querySelector(".bcm-dialog");\n    if (dialog) {\n      dialog.scrollTop = dialogScrollTop;\n      this._dialogScrollTop = dialogScrollTop;\n      dialog.addEventListener("scroll", () => { this._dialogScrollTop = dialog.scrollTop; });\n    }\n    this.bindEvents();',
        "restore dialog scroll",
    )
    content = replace_once(
        content,
        '  .bcm-chart-empty { margin-top:14px; padding:18px; text-align:center; border:1px dashed var(--divider-color); border-radius:12px; color:var(--secondary-text-color); }',
        '  .bcm-chart-empty { margin-top:14px; padding:18px; text-align:center; border:1px dashed var(--divider-color); border-radius:12px; color:var(--secondary-text-color); }\n  .bcm-image-preview { width:100%; max-height:220px; object-fit:contain; border-radius:10px; background:var(--secondary-background-color); margin-bottom:8px; }\n  .bcm-file-btn { display:inline-flex; align-items:center; }\n  .bcm-file-btn input { display:none; }',
        "image CSS",
    )
    content = replace_once(
        content,
        '    return `<div class="bcm-list-item"><div class="bcm-list-head"><div><strong>${esc(setup.name)}</strong>',
        '    const img = imageUrl(setup.image);\n    return `<div class="bcm-list-item"><div class="bcm-list-head"><div style="display:flex;gap:12px;align-items:center">${img ? `<img class="bcm-thumb" src="${esc(img)}">` : ""}<div><strong>${esc(setup.name)}</strong>',
        "setup thumbnail start",
    )
    content = replace_once(
        content,
        '${esc((setup.port_labels || []).join(" / "))}</div></div><span class="bcm-badge">${this.t("revision")} ${setup.revision}</span>',
        '${esc((setup.port_labels || []).join(" / "))}</div></div></div><span class="bcm-badge">${this.t("revision")} ${setup.revision}</span>',
        "setup thumbnail close",
    )
    content = replace_once(
        content,
        '${this.input("nominal_capacity_mah",this.t("capacity"),d.nominal_capacity_mah ?? 1000,true,"number")}',
        '${this.input("nominal_capacity_mah",this.t("capacity"),d.nominal_capacity_mah ?? "",true,"number")}',
        "blank battery capacity",
    )
    content = replace_once(
        content,
        '${this.input("rest_time_minutes",this.t("restTime"),d.rest_time_minutes,"", "number", "1")}${this.input("image",this.t("image"),typeof d.image === "string" ? d.image : "")}',
        '${this.input("rest_time_minutes",this.t("restTime"),d.rest_time_minutes ?? "","", "number", "1")}${this.imageField("battery",d.image)}',
        "battery image field",
    )
    content = replace_once(
        content,
        '${this.input("max_temperature_c",this.t("maxTemperature"),d.max_temperature_c,"", "number", "0.1")}</div>${this.textarea("description",this.t("description"),d.description)}',
        '${this.input("max_temperature_c",this.t("maxTemperature"),d.max_temperature_c,"", "number", "0.1")}${this.imageField("setup",d.image)}</div>${this.textarea("description",this.t("description"),d.description)}',
        "setup image field",
    )
    input_marker = '''  input(key, label, value = "", required = false, type = "text", step = "1") {\n    return `<div class="bcm-field"><label>${label}</label><input data-draft="${key}" type="${type}" step="${step}" value="${esc(value ?? "")}" ${required ? "required" : ""}></div>`;\n  }\n'''
    image_method = input_marker + '''  imageField(kind, image) {\n    const url = imageUrl(image);\n    const textValue = typeof image === "string" ? image : (image?.url || image?.media_content_id || "");\n    return `<div class="bcm-field"><label>${this.t("image")}</label>${url ? `<img class="bcm-image-preview" src="${esc(url)}">` : ""}<input data-draft="image" type="text" value="${esc(textValue)}"><div class="bcm-actions"><label class="bcm-btn secondary bcm-file-btn">${this.t("uploadImage")}<input data-image-upload="${kind}" type="file" accept="image/jpeg,image/png,image/webp"></label>${url ? `<button type="button" class="bcm-btn secondary" data-remove-image>${this.t("removeImage")}</button>` : ""}</div></div>`;\n  }\n'''
    content = replace_once(content, input_marker, image_method, "image field method")
    content = replace_once(
        content,
        '    this.shadowRoot.querySelectorAll("[data-form-value]").forEach((el) => {',
        '    this.shadowRoot.querySelectorAll("[data-image-upload]").forEach((el) => el.addEventListener("change", () => this.handleImageUpload(el)));\n    this.shadowRoot.querySelectorAll("[data-remove-image]").forEach((el) => el.addEventListener("click", () => { this._draft.image = ""; this._dialogScrollTop = this.shadowRoot.querySelector(".bcm-dialog")?.scrollTop || 0; this.render(); }));\n    this.shadowRoot.querySelectorAll("[data-form-value]").forEach((el) => {',
        "image event bindings",
    )
    content = replace_once(
        content,
        '      if (action === "new-battery") { this._draft = {}; this._dialog = "battery"; this.render(); return; }\n      if (action === "new-setup") { this._draft = { port_labels:["A","B","C","D"], max_power_w:100 }; this._dialog = "setup"; this.render(); return; }\n      if (action === "close-dialog") { this._dialog = null; this._draft = {}; this.render(); return; }\n      if (action === "save-battery") { await this.call("save_battery", { data: this.normalizeDraft("battery") }); this._dialog = null; this._draft = {}; return; }\n      if (action === "save-setup") { await this.call("save_setup", { data: this.normalizeDraft("setup") }); this._dialog = null; this._draft = {}; return; }',
        '      if (action === "new-battery") { this._draft = {}; this._dialog = "battery"; this._dialogScrollTop = 0; this.render(); return; }\n      if (action === "new-setup") { this._draft = { port_labels:["A","B","C","D"], max_power_w:100 }; this._dialog = "setup"; this._dialogScrollTop = 0; this.render(); return; }\n      if (action === "close-dialog") { this._dialog = null; this._draft = {}; this._dialogScrollTop = 0; this.render(); return; }\n      if (action === "save-battery") { await this.saveDialog("battery", "save_battery"); return; }\n      if (action === "save-setup") { await this.saveDialog("setup", "save_setup"); return; }',
        "save flow",
    )
    content = replace_once(
        content,
        '    this.shadowRoot.querySelectorAll("[data-edit-battery]").forEach((el) => el.addEventListener("click", () => { const item = this._state.batteries.find((x) => x.battery_id === el.dataset.editBattery); this._draft = structuredClone(item || {}); this._dialog = "battery"; this.render(); }));\n    this.shadowRoot.querySelectorAll("[data-edit-setup]").forEach((el) => el.addEventListener("click", () => { const item = this._state.setups.find((x) => x.setup_id === el.dataset.editSetup); this._draft = structuredClone(item || {}); this._dialog = "setup"; this.render(); }));',
        '    this.shadowRoot.querySelectorAll("[data-edit-battery]").forEach((el) => el.addEventListener("click", () => { const item = this._state.batteries.find((x) => x.battery_id === el.dataset.editBattery); this._draft = structuredClone(item || {}); this._dialog = "battery"; this._dialogScrollTop = 0; this.render(); }));\n    this.shadowRoot.querySelectorAll("[data-edit-setup]").forEach((el) => el.addEventListener("click", () => { const item = this._state.setups.find((x) => x.setup_id === el.dataset.editSetup); this._draft = structuredClone(item || {}); this._dialog = "setup"; this._dialogScrollTop = 0; this.render(); }));',
        "edit dialog scroll reset",
    )
    normalize_marker = '''  commitNumberInput(input, fallbackValue = undefined) {\n'''
    methods = '''  async saveDialog(kind, command) {\n    this._renderLock += 1;\n    const button = this.shadowRoot.querySelector(`[data-action="save-${kind}"]`);\n    if (button) button.disabled = true;\n    try {\n      await this.call(command, { data: this.normalizeDraft(kind) }, { renderBusy:false, renderDone:false });\n      this._dialog = null;\n      this._draft = {};\n      this._dialogScrollTop = 0;\n    } finally {\n      this._renderLock = Math.max(0, this._renderLock - 1);\n      this._requestRender(true);\n    }\n  }\n\n  async handleImageUpload(input) {\n    const file = input.files?.[0];\n    if (!file) return;\n    this._renderLock += 1;\n    try {\n      const prepared = await this.prepareImageFile(file);\n      const data = await this.fileToBase64(prepared);\n      const result = await this.call("upload_image", {\n        filename: prepared.name || file.name || "image",\n        mime_type: prepared.type,\n        data,\n      }, { renderBusy:false, renderDone:false });\n      if (result?.path) this._draft.image = result.path;\n    } catch (err) {\n      this._error = err?.message || String(err);\n    } finally {\n      this._renderLock = Math.max(0, this._renderLock - 1);\n      this._requestRender(true);\n    }\n  }\n\n  async prepareImageFile(file) {\n    const allowed = ["image/jpeg", "image/png", "image/webp"];\n    if (!allowed.includes(file.type)) throw new Error("Unsupported image type");\n    if (file.size <= 1800000) return file;\n    if (typeof createImageBitmap !== "function" || typeof document === "undefined") {\n      throw new Error("Image is too large; choose an image below 2 MB");\n    }\n    const bitmap = await createImageBitmap(file);\n    const maxSide = 1600;\n    const scale = Math.min(1, maxSide / Math.max(bitmap.width, bitmap.height));\n    const canvas = document.createElement("canvas");\n    canvas.width = Math.max(1, Math.round(bitmap.width * scale));\n    canvas.height = Math.max(1, Math.round(bitmap.height * scale));\n    canvas.getContext("2d").drawImage(bitmap, 0, 0, canvas.width, canvas.height);\n    bitmap.close?.();\n    const blob = await new Promise((resolve, reject) => canvas.toBlob((value) => value ? resolve(value) : reject(new Error("Could not resize image")), "image/webp", 0.85));\n    if (blob.size > 2000000) throw new Error("Image is too large after resizing");\n    return new File([blob], "upload.webp", { type:"image/webp" });\n  }\n\n  fileToBase64(file) {\n    return new Promise((resolve, reject) => {\n      const reader = new FileReader();\n      reader.onload = () => resolve(String(reader.result || "").split(",", 2)[1] || "");\n      reader.onerror = () => reject(new Error("Could not read image"));\n      reader.readAsDataURL(file);\n    });\n  }\n\n'''
    if normalize_marker not in content:
        raise RuntimeError("frontend helper insertion point missing")
    content = content.replace(normalize_marker, methods + normalize_marker, 1)
    content = replace_once(
        content,
        '    if (type === "battery") {\n      d.nominal_capacity_mah = Number(d.nominal_capacity_mah || 1000);\n      d.nominal_voltage_v = d.nominal_voltage_v === "" ? null : Number(d.nominal_voltage_v);\n      d.nominal_energy_wh = d.nominal_energy_wh === "" ? null : Number(d.nominal_energy_wh);\n      d.rest_time_minutes = d.rest_time_minutes === "" ? null : Number(d.rest_time_minutes);\n    } else {\n      d.max_power_w = Number(d.max_power_w || 100);\n      d.max_temperature_c = d.max_temperature_c === "" ? null : Number(d.max_temperature_c);',
        '    if (type === "battery") {\n      d.nominal_capacity_mah = d.nominal_capacity_mah === "" || d.nominal_capacity_mah === null || d.nominal_capacity_mah === undefined ? null : Number(d.nominal_capacity_mah);\n      d.nominal_voltage_v = d.nominal_voltage_v === "" || d.nominal_voltage_v === undefined ? null : Number(d.nominal_voltage_v);\n      d.nominal_energy_wh = d.nominal_energy_wh === "" || d.nominal_energy_wh === undefined ? null : Number(d.nominal_energy_wh);\n      d.rest_time_minutes = d.rest_time_minutes === "" || d.rest_time_minutes === undefined ? null : Number(d.rest_time_minutes);\n    } else {\n      d.power_sensor = d.power_sensor || null;\n      d.temperature_sensor = d.temperature_sensor || null;\n      d.max_power_w = Number(d.max_power_w || 100);\n      d.max_temperature_c = d.max_temperature_c === "" ? null : Number(d.max_temperature_c);',
        "draft normalization",
    )
    write(path, content)


def patch_docs() -> None:
    path = "CHANGELOG.md"
    content = read(path)
    content = replace_once(
        content,
        "# Changelog\n\n",
        "# Changelog\n\n## 0.1.3\n\n- Fixed setup editing with optional power/temperature sensors left unselected.\n- Fixed battery/setup save dialogs rerendering and jumping to the top during the first save attempt.\n- Added direct JPG/PNG/WebP image upload for battery types and charging setups, with local Home Assistant storage and previews.\n- Added charging-setup images to the setup overview.\n- Clarified nominal voltage as output voltage and removed implicit 1000 mAh population from new battery forms/saves.\n- Optional technical numeric fields remain empty until explicitly entered.\n\n",
        "changelog",
    )
    write(path, content)
    (ROOT / "docs/version-0.1.3.md").write_text(
        "# Battery Charge Manager 0.1.3\n\n"
        "This release fixes management-form persistence and optional sensor handling, clarifies battery voltage terminology, removes implicit numeric values, and adds direct image uploads for battery types and charging setups. Uploaded images are validated and stored under Home Assistant's `www/battery_charge_manager` directory and referenced through `/local/battery_charge_manager/...`.\n",
        encoding="utf-8",
    )


def main() -> None:
    manifest = json.loads(read("custom_components/battery_charge_manager/manifest.json"))
    if manifest.get("version") == "0.1.3":
        print("0.1.3 already applied")
        return
    patch_const()
    patch_manifest()
    patch_models()
    patch_manager()
    patch_websocket()
    patch_frontend()
    patch_docs()
    print("Applied Battery Charge Manager 0.1.3")


if __name__ == "__main__":
    main()
