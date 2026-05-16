from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path
from urllib.parse import urljoin, urlparse

import requests
from bs4 import BeautifulSoup
from urllib3.exceptions import InsecureRequestWarning


@dataclass(slots=True)
class ScrapeReport:
    pages: int
    output_dir: Path
    files: list[Path]


class CollibraDocsMirror:
    """Small official-doc mirror for building a local, cited RAG corpus."""

    def __init__(self, output_dir: Path, max_pages: int = 40, verify_ssl: bool = True) -> None:
        self.output_dir = output_dir
        self.max_pages = max_pages
        self.verify_ssl = verify_ssl
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def scrape(self, seed_urls: list[str]) -> ScrapeReport:
        visited: set[str] = set()
        queue = list(seed_urls)
        files: list[Path] = []
        allowed_hosts = {urlparse(url).netloc for url in seed_urls}
        if not self.verify_ssl:
            requests.packages.urllib3.disable_warnings(category=InsecureRequestWarning)  # type: ignore[attr-defined]
        while queue and len(visited) < self.max_pages:
            url = queue.pop(0)
            if url in visited or urlparse(url).netloc not in allowed_hosts:
                continue
            response = requests.get(url, timeout=20, verify=self.verify_ssl)
            response.raise_for_status()
            visited.add(url)
            soup = BeautifulSoup(response.text, "html.parser")
            title = soup.find(["h1", "title"])
            text = soup.get_text("\n")
            text = re.sub(r"\n{3,}", "\n\n", text)
            filename = _safe_filename(title.get_text(" ", strip=True) if title else url)
            output_path = self.output_dir / f"{filename}.md"
            suffix = 1
            while output_path.exists():
                output_path = self.output_dir / f"{filename}_{suffix}.md"
                suffix += 1
            output_path.write_text(f"# {title.get_text(' ', strip=True) if title else url}\n\nSource: {url}\n\n{text}", encoding="utf-8")
            files.append(output_path)
            for anchor in soup.find_all("a", href=True):
                href = urljoin(url, anchor["href"])
                parsed = urlparse(href)
                if parsed.netloc in allowed_hosts and "/workflows/" in parsed.path and href not in visited:
                    queue.append(href)
        return ScrapeReport(pages=len(visited), output_dir=self.output_dir, files=files)


def _safe_filename(value: str) -> str:
    value = re.sub(r"[^A-Za-z0-9._-]+", "_", value.strip())[:90].strip("_")
    return value or "collibra_doc"
