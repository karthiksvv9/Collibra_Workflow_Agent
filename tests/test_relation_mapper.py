from __future__ import annotations

import zipfile
from pathlib import Path

from src.rag.relation_mapper import RelationMapper


def test_relation_mapper_extracts_excel_uuid_relations(tmp_path: Path) -> None:
    workbook = tmp_path / "relations.xlsx"
    _write_minimal_xlsx(workbook)

    graph = RelationMapper(sample_rows=20).map_path(workbook)

    assert len(graph.relations) == 1
    relation = graph.relations[0]
    assert relation.source == "11111111-1111-1111-1111-111111111111"
    assert relation.target == "22222222-2222-2222-2222-222222222222"
    assert relation.relation_type == "DataAssetContainsColumn"
    assert "source id" in graph.uuid_index


def _write_minimal_xlsx(path: Path) -> None:
    with zipfile.ZipFile(path, "w", zipfile.ZIP_DEFLATED) as archive:
        archive.writestr(
            "[Content_Types].xml",
            """<?xml version="1.0" encoding="UTF-8"?>
<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">
  <Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>
  <Default Extension="xml" ContentType="application/xml"/>
  <Override PartName="/xl/workbook.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet.main+xml"/>
  <Override PartName="/xl/worksheets/sheet1.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.worksheet+xml"/>
  <Override PartName="/xl/sharedStrings.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.sharedStrings+xml"/>
</Types>""",
        )
        archive.writestr(
            "xl/workbook.xml",
            """<workbook xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main"
 xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships">
 <sheets><sheet name="Relations" sheetId="1" r:id="rId1"/></sheets>
</workbook>""",
        )
        archive.writestr(
            "xl/_rels/workbook.xml.rels",
            """<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">
 <Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/worksheet" Target="worksheets/sheet1.xml"/>
</Relationships>""",
        )
        archive.writestr(
            "xl/sharedStrings.xml",
            """<sst xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main" count="6" uniqueCount="6">
 <si><t>source id</t></si><si><t>target id</t></si><si><t>relation type</t></si>
 <si><t>11111111-1111-1111-1111-111111111111</t></si>
 <si><t>22222222-2222-2222-2222-222222222222</t></si>
 <si><t>DataAssetContainsColumn</t></si>
</sst>""",
        )
        archive.writestr(
            "xl/worksheets/sheet1.xml",
            """<worksheet xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main">
 <sheetData>
  <row r="1"><c t="s"><v>0</v></c><c t="s"><v>1</v></c><c t="s"><v>2</v></c></row>
  <row r="2"><c t="s"><v>3</v></c><c t="s"><v>4</v></c><c t="s"><v>5</v></c></row>
 </sheetData>
</worksheet>""",
        )

