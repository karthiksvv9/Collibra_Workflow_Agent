from __future__ import annotations

import json
import re
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any


@dataclass(slots=True)
class FormField:
    id: str
    name: str
    type: str = "string"
    required: bool = False
    label: str = ""
    readable: bool = True
    writable: bool = True
    default: Any = None
    values: list[dict[str, str]] = field(default_factory=list)


@dataclass(slots=True)
class FormModel:
    key: str
    name: str
    fields: list[FormField] = field(default_factory=list)

    def validate(self) -> list[str]:
        errors: list[str] = []
        seen: set[str] = set()
        for field in self.fields:
            if not re.fullmatch(r"[A-Za-z][A-Za-z0-9_]*", field.id):
                errors.append(f"Form field id '{field.id}' must start with a letter and contain only letters, numbers, and underscores.")
            if field.id in seen:
                errors.append(f"Duplicate form field id '{field.id}'.")
            seen.add(field.id)
        return errors

    def to_json(self) -> str:
        return json.dumps(
            {
                "key": self.key,
                "name": self.name,
                "fields": [asdict(field) for field in self.fields],
            },
            indent=2,
            sort_keys=True,
        )

    @classmethod
    def from_json(cls, text: str) -> "FormModel":
        data = json.loads(text)
        fields = [form_field_from_mapping(field) for field in data.get("fields", []) if isinstance(field, dict)]
        return cls(key=data["key"], name=data.get("name", data["key"]), fields=fields)


def form_field_from_mapping(field: dict[str, Any]) -> FormField:
    field_id = str(field.get("id") or field.get("key") or field.get("name") or "field").strip()
    field_id = re.sub(r"[^A-Za-z0-9_]+", "_", field_id).strip("_") or "field"
    if field_id[0].isdigit():
        field_id = f"field_{field_id}"
    label = str(field.get("label") or field.get("name") or field_id)
    values = field.get("values")
    if not isinstance(values, list):
        extra_settings = field.get("extraSettings") if isinstance(field.get("extraSettings"), dict) else {}
        values = extra_settings.get("values") if isinstance(extra_settings.get("values"), list) else []
    return FormField(
        id=field_id,
        name=str(field.get("name") or label or field_id),
        type=str(field.get("type") or "string"),
        required=_coerce_bool(field.get("required", field.get("isRequired", False))),
        label=label,
        readable=_coerce_bool(field.get("readable", field.get("visible", True))),
        writable=_coerce_bool(field.get("writable", field.get("enabled", True))),
        default=field.get("default", field.get("value")),
        values=[value for value in values if isinstance(value, dict)],
    )


def _coerce_bool(value: Any) -> bool:
    if isinstance(value, str):
        return value.strip().lower() not in {"", "0", "false", "no", "off"}
    return bool(value)


def write_form_file(form: FormModel, path: str | Path) -> Path:
    output = Path(path)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(form.to_json(), encoding="utf-8")
    return output
