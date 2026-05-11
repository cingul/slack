#!/usr/bin/env python3
"""Build a styled HTML manuscript from Markdown and BibTeX.

The generated HTML is designed for clean PDF rendering with WeasyPrint, with a
Chrome DevTools fallback for lightweight environments.
"""

from __future__ import annotations

import html
import base64
import json
import os
import re
import socket
import subprocess
import sys
import tempfile
import time
import urllib.parse
import urllib.request
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
MANUSCRIPT = ROOT / "manuscripts" / "reporting_outcomes_orthostatic_hypotension_intolerance_trials.md"
BIB = ROOT / "references" / "meq_orthostatic_hypotension.bib"
OUT = ROOT / "outputs"
HTML_OUT = OUT / "reporting_outcomes_orthostatic_hypotension_intolerance_trials.html"
PDF_OUT = OUT / "reporting_outcomes_orthostatic_hypotension_intolerance_trials.pdf"
FIGURE_OUT = OUT / "figure1_outcome_framework.svg"


def parse_bibtex(text: str) -> dict[str, dict[str, str]]:
    entries: dict[str, dict[str, str]] = {}
    for match in re.finditer(r"@(?P<type>\w+)\{(?P<key>[^,]+),(?P<body>.*?)(?=\n@|\Z)", text, re.S):
        key = match.group("key").strip()
        body = match.group("body")
        fields: dict[str, str] = {}
        for field, value in re.findall(r"(\w+)\s*=\s*\{([^{}]*(?:\{[^{}]*\}[^{}]*)*)\}", body):
            fields[field.lower()] = re.sub(r"\s+", " ", value.replace("--", "-")).strip()
        entries[key] = fields
    return entries


def format_authors(authors: str) -> str:
    if not authors:
        return ""
    parts = [part.strip() for part in authors.split(" and ")]
    formatted: list[str] = []
    for part in parts[:6]:
        pieces = [p.strip() for p in part.split(",")]
        if len(pieces) >= 2:
            formatted.append(f"{pieces[0]} {pieces[1][0]}.")
        else:
            formatted.append(part)
    if len(parts) > 6:
        formatted.append("et al.")
    return ", ".join(formatted)


def format_reference(fields: dict[str, str]) -> str:
    authors = format_authors(fields.get("author", ""))
    title = fields.get("title", "")
    journal = fields.get("journal", "")
    year = fields.get("year", "")
    volume = fields.get("volume", "")
    number = fields.get("number", "")
    pages = fields.get("pages", "")
    doi = fields.get("doi", "")

    citation = ""
    if authors:
        citation += f"{authors} "
    if title:
        citation += f"{title}. "
    if journal:
        citation += f"<em>{html.escape(journal)}</em>. "
    if year:
        citation += f"{html.escape(year)}"
    if volume:
        citation += f";{html.escape(volume)}"
    if number:
        citation += f"({html.escape(number)})"
    if pages:
        citation += f":{html.escape(pages)}"
    if year or volume or pages:
        citation += ". "
    if doi:
        citation += f"doi:{html.escape(doi)}."
    return citation.strip()


def write_framework_figure(path: Path) -> None:
    """Write Figure 1 as a standalone SVG used by the HTML/PDF build."""
    svg = """<svg xmlns="http://www.w3.org/2000/svg" width="1080" height="690" viewBox="0 0 1080 690" role="img" aria-labelledby="title desc">
  <title id="title">Multidomain outcome framework for OH/OI intervention trials</title>
  <desc id="desc">Six core reporting domains surround patient-centered net benefit, with mechanism-specific target engagement as an intervention-specific domain.</desc>
  <defs>
    <filter id="shadow" x="-20%" y="-20%" width="140%" height="140%">
      <feDropShadow dx="0" dy="5" stdDeviation="6" flood-color="#16324f" flood-opacity="0.14"/>
    </filter>
    <linearGradient id="center" x1="0" x2="1" y1="0" y2="1">
      <stop offset="0" stop-color="#16324f"/>
      <stop offset="1" stop-color="#177e89"/>
    </linearGradient>
  </defs>
  <rect width="1080" height="690" fill="#fbf8f0"/>
  <rect x="34" y="34" width="1012" height="622" rx="28" fill="#ffffff" stroke="#d8a23a" stroke-width="3"/>
  <text x="540" y="76" text-anchor="middle" font-family="Arial, Helvetica, sans-serif" font-size="25" font-weight="700" fill="#16324f">Figure 1. Multidomain outcome framework</text>
  <text x="540" y="107" text-anchor="middle" font-family="Georgia, serif" font-size="18" fill="#5b6572">Domains 1-6 form the shared core; Domain 7 bridges innovation to clinical metrics.</text>
  <circle cx="540" cy="340" r="112" fill="url(#center)" filter="url(#shadow)"/>
  <text x="540" y="304" text-anchor="middle" font-family="Arial, Helvetica, sans-serif" font-size="18" font-weight="700" fill="#ffffff">Patient-centered</text>
  <text x="540" y="331" text-anchor="middle" font-family="Arial, Helvetica, sans-serif" font-size="18" font-weight="700" fill="#ffffff">net benefit</text>
  <text x="540" y="362" text-anchor="middle" font-family="Georgia, serif" font-size="15" fill="#eef6f7">benefit + burden + safety</text>
  <text x="540" y="389" text-anchor="middle" font-family="Arial, Helvetica, sans-serif" font-size="12" fill="#fff8e8">MEQ quantifies medication burden</text>

  <g font-family="Arial, Helvetica, sans-serif" font-size="16" font-weight="700" fill="#16324f">
    <rect x="95" y="168" width="250" height="78" rx="14" fill="#eef6f7" stroke="#177e89" stroke-width="2"/>
    <text x="220" y="199" text-anchor="middle">1. Hemodynamics</text>
    <text x="220" y="224" text-anchor="middle" font-size="13" font-weight="400" fill="#5b6572">BP, HR, standing time</text>

    <rect x="415" y="145" width="250" height="78" rx="14" fill="#eef6f7" stroke="#177e89" stroke-width="2"/>
    <text x="540" y="176" text-anchor="middle">2. Symptoms / PROs</text>
    <text x="540" y="201" text-anchor="middle" font-size="13" font-weight="400" fill="#5b6572">OHQ, COMPASS-31, PGI</text>

    <rect x="735" y="168" width="250" height="78" rx="14" fill="#eef6f7" stroke="#177e89" stroke-width="2"/>
    <text x="860" y="199" text-anchor="middle">3. Function / QOL</text>
    <text x="860" y="224" text-anchor="middle" font-size="13" font-weight="400" fill="#5b6572">falls, ADLs, SF-36</text>

    <rect x="95" y="438" width="250" height="78" rx="14" fill="#fff8e8" stroke="#d8a23a" stroke-width="2.4"/>
    <text x="220" y="469" text-anchor="middle">4. Medication burden</text>
    <text x="220" y="494" text-anchor="middle" font-size="13" font-weight="400" fill="#5b6572">MEQ, rescue, failed taper</text>

    <rect x="415" y="475" width="250" height="78" rx="14" fill="#eef6f7" stroke="#177e89" stroke-width="2"/>
    <text x="540" y="506" text-anchor="middle">5. Safety / harms</text>
    <text x="540" y="531" text-anchor="middle" font-size="13" font-weight="400" fill="#5b6572">AEs, syncope, supine HTN</text>

    <rect x="735" y="438" width="250" height="78" rx="14" fill="#eef6f7" stroke="#177e89" stroke-width="2"/>
    <text x="860" y="469" text-anchor="middle">6. Durability / rescue</text>
    <text x="860" y="494" text-anchor="middle" font-size="13" font-weight="400" fill="#5b6572">relapse, reintervention</text>

    <rect x="340" y="584" width="400" height="58" rx="20" fill="#fff8e8" stroke="#d8a23a" stroke-width="2"/>
    <text x="540" y="607" text-anchor="middle" fill="#16324f">7. Mechanism-specific target engagement</text>
    <text x="540" y="630" text-anchor="middle" font-size="13" font-weight="400" fill="#5b6572">the bridge from innovation to clinical outcomes</text>
  </g>

  <g font-family="Arial, Helvetica, sans-serif" font-size="12" font-weight="700">
    <rect x="86" y="528" width="268" height="32" rx="16" fill="#16324f"/>
    <text x="220" y="549" text-anchor="middle" fill="#ffffff">MEQ = therapy intensity, not potency</text>
  </g>

  <g stroke="#d8a23a" stroke-width="3" stroke-linecap="round" opacity="0.8">
    <line x1="330" y1="238" x2="449" y2="278"/>
    <line x1="540" y1="223" x2="540" y2="228"/>
    <line x1="750" y1="238" x2="631" y2="278"/>
    <line x1="330" y1="450" x2="449" y2="402"/>
    <line x1="540" y1="475" x2="540" y2="452"/>
    <line x1="750" y1="450" x2="631" y2="402"/>
    <line x1="540" y1="584" x2="540" y2="452"/>
  </g>
</svg>
"""
    path.write_text(svg)


class MarkdownRenderer:
    def __init__(self, bib_entries: dict[str, dict[str, str]]) -> None:
        self.bib_entries = bib_entries
        self.citation_numbers: dict[str, int] = {}
        self.citation_order: list[str] = []

    def cite(self, match: re.Match[str]) -> str:
        raw = match.group(1)
        keys = re.findall(r"@([A-Za-z0-9_:-]+)", raw)
        nums: list[str] = []
        for key in keys:
            if key not in self.citation_numbers:
                self.citation_numbers[key] = len(self.citation_order) + 1
                self.citation_order.append(key)
            nums.append(str(self.citation_numbers[key]))
        return f"<sup class=\"citation\">{','.join(nums)}</sup>"

    def inline(self, text: str) -> str:
        text = html.escape(text)
        text = re.sub(r"\[([^\]]*@[^]]+)\]", self.cite, text)
        text = re.sub(r"\*\*([^*]+)\*\*", r"<strong>\1</strong>", text)
        text = re.sub(r"`([^`]+)`", r"<code>\1</code>", text)
        return text

    def render_table(self, rows: list[str]) -> str:
        parsed = [[cell.strip() for cell in row.strip().strip("|").split("|")] for row in rows]
        header = parsed[0]
        body = [row for row in parsed[2:] if row]
        out = ["<div class=\"table-wrap\"><table>"]
        out.append("<thead><tr>" + "".join(f"<th>{self.inline(cell)}</th>" for cell in header) + "</tr></thead>")
        out.append("<tbody>")
        for row in body:
            out.append("<tr>" + "".join(f"<td>{self.inline(cell)}</td>" for cell in row) + "</tr>")
        out.append("</tbody></table></div>")
        return "\n".join(out)

    def render_image(self, line: str) -> str | None:
        match = re.match(r"!\[([^\]]+)\]\(([^)]+)\)", line)
        if not match:
            return None
        caption = match.group(1)
        src = Path(match.group(2)).name
        return (
            "<figure class=\"figure\">"
            f"<img src=\"{html.escape(src)}\" alt=\"{html.escape(caption)}\">"
            f"<figcaption>{self.inline(caption)}</figcaption>"
            "</figure>"
        )

    def render(self, markdown: str) -> str:
        lines = markdown.splitlines()
        blocks: list[str] = []
        paragraph: list[str] = []
        list_stack: list[str] = []
        i = 0

        def flush_paragraph() -> None:
            nonlocal paragraph
            if paragraph:
                blocks.append(f"<p>{self.inline(' '.join(paragraph))}</p>")
                paragraph = []

        def close_lists() -> None:
            nonlocal list_stack
            while list_stack:
                blocks.append(f"</{list_stack.pop()}>")

        while i < len(lines):
            line = lines[i].rstrip()

            if not line:
                flush_paragraph()
                close_lists()
                i += 1
                continue

            if line.startswith("|") and i + 1 < len(lines) and lines[i + 1].startswith("|"):
                flush_paragraph()
                close_lists()
                table_lines = []
                while i < len(lines) and lines[i].startswith("|"):
                    table_lines.append(lines[i])
                    i += 1
                blocks.append(self.render_table(table_lines))
                continue

            image_html = self.render_image(line)
            if image_html:
                flush_paragraph()
                close_lists()
                blocks.append(image_html)
                i += 1
                continue

            heading = re.match(r"^(#{1,4})\s+(.+)$", line)
            if heading:
                flush_paragraph()
                close_lists()
                level = len(heading.group(1))
                text = heading.group(2)
                if level == 1:
                    blocks.append(f"<h1>{self.inline(text)}</h1>")
                elif level == 2:
                    blocks.append(f"<h2>{self.inline(text)}</h2>")
                elif level == 3:
                    blocks.append(f"<h3>{self.inline(text)}</h3>")
                else:
                    blocks.append(f"<h4>{self.inline(text)}</h4>")
                i += 1
                continue

            bullet = re.match(r"^\s*-\s+(.+)$", line)
            numbered = re.match(r"^\s*\d+\.\s+(.+)$", line)
            if bullet or numbered:
                flush_paragraph()
                kind = "ul" if bullet else "ol"
                if not list_stack or list_stack[-1] != kind:
                    close_lists()
                    blocks.append(f"<{kind}>")
                    list_stack.append(kind)
                item = (bullet or numbered).group(1)
                blocks.append(f"<li>{self.inline(item)}</li>")
                i += 1
                continue

            close_lists()
            paragraph.append(line)
            i += 1

        flush_paragraph()
        close_lists()
        return "\n".join(blocks)

    def references_html(self) -> str:
        items = []
        for key in self.citation_order:
            ref = self.bib_entries.get(key)
            if not ref:
                continue
            items.append(f"<li id=\"ref-{key}\">{format_reference(ref)}</li>")
        if not items:
            return ""
        return "<h2>References</h2>\n<ol class=\"references\">\n" + "\n".join(items) + "\n</ol>"


def build_html(body: str, refs: str) -> str:
    css = r"""
@page {
  size: Letter;
  margin: 0.72in 0.72in 0.78in;
}
:root {
  --ink: #1f2933;
  --muted: #5b6572;
  --navy: #16324f;
  --teal: #177e89;
  --gold: #d8a23a;
  --cream: #fbf8f0;
  --pale: #eef6f7;
  --line: #d9e2ec;
}
* { box-sizing: border-box; }
body {
  color: var(--ink);
  font-family: Georgia, "Times New Roman", "Liberation Serif", serif;
  font-size: 10.8pt;
  line-height: 1.48;
  margin: 0;
  background: white;
}
.page {
  max-width: 7.15in;
  margin: 0 auto;
}
.cover {
  border-top: 9px solid var(--navy);
  border-bottom: 2px solid var(--gold);
  background: linear-gradient(135deg, var(--cream), #ffffff 58%, var(--pale));
  padding: 0.42in 0.44in 0.36in;
  margin-bottom: 0.22in;
}
.label {
  color: var(--teal);
  font-family: Arial, Helvetica, sans-serif;
  font-size: 9pt;
  font-weight: 700;
  letter-spacing: 0.14em;
  text-transform: uppercase;
  margin-bottom: 0.14in;
}
h1 {
  color: var(--navy);
  font-size: 27pt;
  line-height: 1.08;
  letter-spacing: -0.02em;
  margin: 0 0 0.15in;
}
.deck {
  color: var(--muted);
  font-size: 12.2pt;
  margin: 0;
}
h2 {
  color: var(--navy);
  font-size: 17pt;
  line-height: 1.16;
  margin: 0.28in 0 0.08in;
  padding-bottom: 0.035in;
  border-bottom: 1.5px solid var(--gold);
}
h3 {
  color: var(--teal);
  font-size: 13.3pt;
  line-height: 1.22;
  margin: 0.19in 0 0.06in;
}
h4 {
  color: var(--navy);
  font-size: 11.2pt;
  margin: 0.15in 0 0.04in;
}
p { margin: 0 0 0.095in; }
ul, ol { margin: 0.04in 0 0.12in 0.23in; padding-left: 0.14in; }
li { margin-bottom: 0.035in; }
strong { color: var(--navy); }
code {
  font-family: "Courier New", monospace;
  background: #f3f6f8;
  padding: 0.01in 0.035in;
  border-radius: 3px;
}
sup.citation {
  color: var(--teal);
  font-family: Arial, Helvetica, sans-serif;
  font-size: 7.2pt;
  font-weight: 700;
}
.table-wrap {
  margin: 0.13in 0 0.18in;
  break-inside: avoid;
}
table {
  border-collapse: collapse;
  width: 100%;
  font-size: 9.2pt;
  line-height: 1.32;
  box-shadow: 0 0 0 1px var(--line);
}
thead th {
  background: var(--navy);
  color: white;
  border: 1px solid var(--navy);
  font-family: Arial, Helvetica, sans-serif;
  font-size: 8.6pt;
  letter-spacing: 0.02em;
  padding: 0.075in;
  text-align: left;
}
td {
  border: 1px solid var(--line);
  padding: 0.07in;
  vertical-align: top;
}
tbody tr:nth-child(even) td { background: #f8fbfc; }
tbody tr:nth-child(odd) td { background: #ffffff; }
.callout {
  background: var(--pale);
  border-left: 5px solid var(--teal);
  padding: 0.13in 0.16in;
  margin: 0.16in 0;
}
.figure {
  margin: 0.18in 0 0.22in;
  padding: 0.1in;
  background: #ffffff;
  border: 1px solid var(--line);
  break-inside: avoid;
}
.figure img {
  display: block;
  width: 100%;
  height: auto;
}
.figure figcaption {
  color: var(--muted);
  font-family: Arial, Helvetica, sans-serif;
  font-size: 8.7pt;
  line-height: 1.32;
  margin-top: 0.07in;
}
.references {
  font-size: 8.7pt;
  line-height: 1.34;
}
.references li { margin-bottom: 0.07in; }
.footer-note {
  color: var(--muted);
  font-family: Arial, Helvetica, sans-serif;
  font-size: 8pt;
  border-top: 1px solid var(--line);
  margin-top: 0.3in;
  padding-top: 0.08in;
}
"""
    title_match = re.search(r"<h1>(.*?)</h1>", body)
    title = title_match.group(1) if title_match else "Orthostatic Outcomes Manuscript"
    body_without_title = re.sub(r"^<h1>.*?</h1>\n?", "", body, count=1, flags=re.S)
    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <title>{title}</title>
  <style>{css}</style>
</head>
<body>
  <main class="page">
    <section class="cover">
      <div class="label">Outcome reporting framework</div>
      <h1>{title}</h1>
      <p class="deck">A multidomain framework for orthostatic hypotension and orthostatic intolerance intervention trials, incorporating medication burden and Midodrine Equivalents.</p>
    </section>
    {body_without_title}
    {refs}
    <p class="footer-note">Generated from the repository manuscript using a Georgia-style serif theme with navy, teal, gold, and warm neutral accents.</p>
  </main>
</body>
</html>
"""


def read_exact(sock: socket.socket, length: int) -> bytes:
    chunks = []
    remaining = length
    while remaining:
        chunk = sock.recv(remaining)
        if not chunk:
            raise RuntimeError("WebSocket connection closed unexpectedly")
        chunks.append(chunk)
        remaining -= len(chunk)
    return b"".join(chunks)


class DevToolsSocket:
    def __init__(self, websocket_url: str) -> None:
        parsed = urllib.parse.urlparse(websocket_url)
        if parsed.scheme != "ws":
            raise ValueError(f"Expected ws URL, got {websocket_url}")
        self.host = parsed.hostname or "127.0.0.1"
        self.port = parsed.port or 80
        self.path = parsed.path
        if parsed.query:
            self.path += "?" + parsed.query
        self.sock = socket.create_connection((self.host, self.port), timeout=10)
        key = base64.b64encode(os.urandom(16)).decode()
        request = (
            f"GET {self.path} HTTP/1.1\r\n"
            f"Host: {self.host}:{self.port}\r\n"
            "Upgrade: websocket\r\n"
            "Connection: Upgrade\r\n"
            f"Sec-WebSocket-Key: {key}\r\n"
            "Sec-WebSocket-Version: 13\r\n\r\n"
        )
        self.sock.sendall(request.encode())
        response = b""
        while b"\r\n\r\n" not in response:
            response += self.sock.recv(4096)
        if b" 101 " not in response.split(b"\r\n", 1)[0]:
            raise RuntimeError(f"WebSocket handshake failed: {response[:200]!r}")

    def send_text(self, text: str) -> None:
        payload = text.encode()
        frame = bytearray([0x81])
        length = len(payload)
        if length < 126:
            frame.append(0x80 | length)
        elif length < 65536:
            frame.extend([0x80 | 126, (length >> 8) & 0xFF, length & 0xFF])
        else:
            frame.append(0x80 | 127)
            frame.extend(length.to_bytes(8, "big"))
        mask = os.urandom(4)
        frame.extend(mask)
        frame.extend(bytes(byte ^ mask[i % 4] for i, byte in enumerate(payload)))
        self.sock.sendall(frame)

    def recv_text(self) -> str:
        chunks: list[bytes] = []
        while True:
            b1, b2 = read_exact(self.sock, 2)
            fin = b1 & 0x80
            opcode = b1 & 0x0F
            masked = b2 & 0x80
            length = b2 & 0x7F
            if length == 126:
                length = int.from_bytes(read_exact(self.sock, 2), "big")
            elif length == 127:
                length = int.from_bytes(read_exact(self.sock, 8), "big")
            mask = read_exact(self.sock, 4) if masked else b""
            payload = read_exact(self.sock, length)
            if masked:
                payload = bytes(byte ^ mask[i % 4] for i, byte in enumerate(payload))
            if opcode == 0x8:
                raise RuntimeError("WebSocket closed by Chrome")
            if opcode in (0x1, 0x0):
                chunks.append(payload)
            if fin:
                return b"".join(chunks).decode()

    def close(self) -> None:
        self.sock.close()


def chrome_json(port: int, path: str, timeout: float = 10.0) -> object:
    url = f"http://127.0.0.1:{port}{path}"
    deadline = time.time() + timeout
    last_error: Exception | None = None
    while time.time() < deadline:
        try:
            with urllib.request.urlopen(url, timeout=1) as response:
                return json.loads(response.read().decode())
        except Exception as exc:  # Chrome may still be starting.
            last_error = exc
            time.sleep(0.1)
    raise RuntimeError(f"Could not read {url}: {last_error}")


def render_pdf_with_chrome(html_path: Path, pdf_path: Path) -> None:
    port = 9333
    chrome = os.environ.get("CHROME", "google-chrome")
    user_data_dir = tempfile.mkdtemp(prefix="manuscript-pdf-")
    process = subprocess.Popen(
        [
            chrome,
            "--headless=new",
            "--no-sandbox",
            "--disable-gpu",
            f"--remote-debugging-port={port}",
            f"--user-data-dir={user_data_dir}",
            "about:blank",
        ],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    try:
        chrome_json(port, "/json/version")
        targets = chrome_json(port, "/json")
        if not isinstance(targets, list) or not targets:
            raise RuntimeError("Chrome did not expose a debuggable page")
        ws_url = targets[0]["webSocketDebuggerUrl"]
        client = DevToolsSocket(ws_url)
        next_id = 1

        def command(method: str, params: dict[str, object] | None = None) -> dict[str, object]:
            nonlocal next_id
            message_id = next_id
            next_id += 1
            client.send_text(json.dumps({"id": message_id, "method": method, "params": params or {}}))
            while True:
                response = json.loads(client.recv_text())
                if response.get("id") == message_id:
                    if "error" in response:
                        raise RuntimeError(f"Chrome DevTools error for {method}: {response['error']}")
                    return response

        file_url = html_path.resolve().as_uri()
        command("Page.enable")
        command("Page.navigate", {"url": file_url})
        time.sleep(1.0)
        response = command(
            "Page.printToPDF",
            {
                "printBackground": True,
                "displayHeaderFooter": False,
                "preferCSSPageSize": True,
                "marginTop": 0,
                "marginBottom": 0,
                "marginLeft": 0,
                "marginRight": 0,
            },
        )
        data = response["result"]["data"]
        pdf_path.write_bytes(base64.b64decode(data))
        client.close()
    finally:
        process.terminate()
        try:
            process.wait(timeout=5)
        except subprocess.TimeoutExpired:
            process.kill()


def render_pdf(html_path: Path, pdf_path: Path) -> None:
    """Render PDF with WeasyPrint when available, otherwise Chrome DevTools."""
    try:
        from weasyprint import HTML  # type: ignore
    except Exception:
        render_pdf_with_chrome(html_path, pdf_path)
        return
    HTML(filename=str(html_path), base_url=str(html_path.parent)).write_pdf(str(pdf_path))


def main() -> None:
    OUT.mkdir(exist_ok=True)
    write_framework_figure(FIGURE_OUT)
    bib_entries = parse_bibtex(BIB.read_text())
    renderer = MarkdownRenderer(bib_entries)
    body = renderer.render(MANUSCRIPT.read_text())
    refs = renderer.references_html()
    HTML_OUT.write_text(build_html(body, refs))
    print(HTML_OUT)
    if "--pdf" in sys.argv:
        render_pdf(HTML_OUT, PDF_OUT)
        print(PDF_OUT)


if __name__ == "__main__":
    main()
