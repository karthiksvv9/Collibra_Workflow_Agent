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
        fields = [FormField(**field) for field in data.get("fields", [])]
        return cls(key=data["key"], name=data.get("name", data["key"]), fields=fields)


def write_form_file(form: FormModel, path: str | Path) -> Path:
    output = Path(path)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(form.to_json(), encoding="utf-8")
    return output

