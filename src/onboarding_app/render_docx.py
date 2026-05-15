from __future__ import annotations

from html import escape
from pathlib import Path
from zipfile import ZIP_DEFLATED, ZipFile


NS_WORD = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"


def write_docx(
    path: Path,
    title: str,
    paragraphs: list[str],
    tables: list[dict[str, object]] | None = None,
    links: list[dict[str, str]] | None = None,
) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    body = [_paragraph(title, style="Title")]
    for paragraph in paragraphs:
        body.append(_paragraph(paragraph))
    relationships = []
    for link in links or []:
        label = str(link.get("label", ""))
        target = str(link.get("target", ""))
        if not label or not target:
            continue
        body.append(_hyperlink_paragraph(label, target))
        path_text = str(link.get("path_text", "")).strip()
        if path_text:
            body.append(_paragraph(f"Путь: {path_text}"))
    for table in tables or []:
        table_title = str(table.get("title", ""))
        if table_title:
            body.append(_paragraph(table_title, style="Heading1"))
        headers = [str(item) for item in table.get("headers", [])]
        rows = [[str(cell) for cell in row] for row in table.get("rows", [])]
        body.append(_table(headers, rows))
    body.append("<w:sectPr><w:pgSz w:w=\"11906\" w:h=\"16838\"/><w:pgMar w:top=\"1440\" w:right=\"1440\" w:bottom=\"1440\" w:left=\"1440\"/></w:sectPr>")
    document = f"""<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<w:document xmlns:w="{NS_WORD}" xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships">
  <w:body>
    {''.join(body)}
  </w:body>
</w:document>
"""
    with ZipFile(path, "w", ZIP_DEFLATED) as archive:
        archive.writestr("[Content_Types].xml", CONTENT_TYPES)
        archive.writestr("_rels/.rels", RELS)
        archive.writestr("word/document.xml", document)
        archive.writestr("word/styles.xml", STYLES)
        if relationships:
            archive.writestr("word/_rels/document.xml.rels", _document_rels(relationships))


def _paragraph(text: str, style: str | None = None) -> str:
    style_xml = f'<w:pPr><w:pStyle w:val="{style}"/></w:pPr>' if style else ""
    safe = escape(text)
    return f'<w:p>{style_xml}<w:r><w:t xml:space="preserve">{safe}</w:t></w:r></w:p>'


def _hyperlink_paragraph(text: str, target: str) -> str:
    safe = escape(text)
    safe_target = escape(target.replace("\\", "\\\\").replace('"', ""), quote=False)
    return (
        '<w:p>'
        '<w:r><w:fldChar w:fldCharType="begin"/></w:r>'
        f'<w:r><w:instrText xml:space="preserve"> HYPERLINK "{safe_target}" </w:instrText></w:r>'
        '<w:r><w:fldChar w:fldCharType="separate"/></w:r>'
        '<w:r><w:rPr><w:rStyle w:val="Hyperlink"/></w:rPr>'
        f'<w:t xml:space="preserve">{safe}</w:t>'
        '</w:r>'
        '<w:r><w:fldChar w:fldCharType="end"/></w:r>'
        '</w:p>'
    )


def _table(headers: list[str], rows: list[list[str]]) -> str:
    all_rows = [headers] + rows if headers else rows
    row_xml = []
    for row in all_rows:
        cells = "".join(
            f"<w:tc><w:tcPr><w:tcW w:w=\"2400\" w:type=\"dxa\"/></w:tcPr>{_paragraph(cell)}</w:tc>"
            for cell in row
        )
        row_xml.append(f"<w:tr>{cells}</w:tr>")
    return f"""<w:tbl>
<w:tblPr>
  <w:tblW w:w="0" w:type="auto"/>
  <w:tblBorders>
    <w:top w:val="single" w:sz="4" w:space="0" w:color="999999"/>
    <w:left w:val="single" w:sz="4" w:space="0" w:color="999999"/>
    <w:bottom w:val="single" w:sz="4" w:space="0" w:color="999999"/>
    <w:right w:val="single" w:sz="4" w:space="0" w:color="999999"/>
    <w:insideH w:val="single" w:sz="4" w:space="0" w:color="999999"/>
    <w:insideV w:val="single" w:sz="4" w:space="0" w:color="999999"/>
  </w:tblBorders>
</w:tblPr>
{''.join(row_xml)}
</w:tbl>"""


CONTENT_TYPES = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">
  <Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>
  <Default Extension="xml" ContentType="application/xml"/>
  <Override PartName="/word/document.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.document.main+xml"/>
  <Override PartName="/word/styles.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.styles+xml"/>
</Types>
"""

RELS = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">
  <Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="word/document.xml"/>
</Relationships>
"""


def _document_rels(relationships: list[tuple[str, str]]) -> str:
    rows = []
    for rel_id, target in relationships:
        rows.append(
            f'<Relationship Id="{rel_id}" '
            'Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/hyperlink" '
            f'Target="{escape(target, quote=True)}" TargetMode="External"/>'
        )
    return (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>\n'
        '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">'
        f"{''.join(rows)}</Relationships>"
    )

STYLES = f"""<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<w:styles xmlns:w="{NS_WORD}">
  <w:style w:type="paragraph" w:styleId="Normal"><w:name w:val="Normal"/></w:style>
  <w:style w:type="paragraph" w:styleId="Title"><w:name w:val="Title"/><w:basedOn w:val="Normal"/><w:rPr><w:b/><w:sz w:val="32"/></w:rPr></w:style>
  <w:style w:type="paragraph" w:styleId="Heading1"><w:name w:val="heading 1"/><w:basedOn w:val="Normal"/><w:rPr><w:b/><w:sz w:val="24"/></w:rPr></w:style>
  <w:style w:type="character" w:styleId="Hyperlink"><w:name w:val="Hyperlink"/><w:rPr><w:color w:val="0563C1"/><w:u w:val="single"/></w:rPr></w:style>
</w:styles>
"""
