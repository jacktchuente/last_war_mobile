import json
import os
import re
from datetime import datetime, timezone, timedelta

import requests

import settings

BASE_URL = "https://cpt-hedge.com"


def compute_server_day(timestamp_ms: int, now: datetime) -> int:
    creation_dt = datetime.fromtimestamp(timestamp_ms / 1000, tz=timezone.utc)
    aligned = creation_dt.replace(hour=2, minute=0, second=0, microsecond=0)
    if creation_dt < aligned:
        aligned -= timedelta(days=1)
    return int((now - aligned).total_seconds() // 86400) + 1


def is_shiny(server_day: int) -> bool:
    return server_day % 3 == 1


def get_servers(use_saved=True, save_path="servers.json"):
    if use_saved and os.path.exists(save_path):
        with open(save_path, "r", encoding="utf-8") as f:
            servers = json.load(f)
        print(f"[+] {len(servers)} serveurs chargés depuis {save_path}")
    else:
        html = requests.get(f"{BASE_URL}/servers").text
        match = re.search(r'src="(/_next/static/chunks/app/servers/page-[^"]+\.js)"', html)
        if not match:
            raise RuntimeError("Impossible de trouver le JS des serveurs dans le HTML")

        js_url = BASE_URL + match.group(1)
        js_code = requests.get(js_url).text

        json_match = re.search(r'JSON\.parse\(\'({.*})\'\)', js_code)
        if not json_match:
            raise RuntimeError("Impossible de trouver le JSON.parse dans le JS")

        data = json.loads(json_match.group(1))
        servers = data.get("c", [])

        with open(save_path, "w", encoding="utf-8") as f:
            json.dump(servers, f, indent=2, ensure_ascii=False)
        print(f"[+] {len(servers)} serveurs téléchargés et sauvegardés dans {save_path}")

    now = datetime.now(timezone.utc)
    simplified = []
    for s in servers:
        ts = s.get("timestamp")
        if not ts:
            continue
        server_day = compute_server_day(int(ts), now)
        simplified.append({
            "id": int(s["id"]),
            "shiny": is_shiny(server_day)
        })

    simplified.sort(key=lambda x: x["id"])
    return simplified


def in_ranges(sid: int, server_filter) -> bool:
    for rng in server_filter:
        if not rng:
            continue
        if len(rng) == 1:
            if sid == int(rng[0]):
                return True
        else:
            a, b = int(rng[0]), int(rng[1])
            if a <= sid <= b:
                return True
    return False


def filter_shiny_servers(server_filter: list[list[int]]) -> list[int]:
    server_file_path = os.path.join(settings.BASE_DIR, "data", "servers.json")
    os.makedirs(os.path.dirname(server_file_path), exist_ok=True)
    servers = get_servers(True, server_file_path)

    filtered_servers = [s for s in servers if in_ranges(s["id"], server_filter)]
    if filtered_servers:
        filtered_servers.sort(key=lambda s: s["id"])
        shiny_ids = [s["id"] for s in filtered_servers if s["shiny"]]
        return shiny_ids
