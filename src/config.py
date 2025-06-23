import os
import yaml

def load_channels_from_yaml(path: str = "channels.yaml") -> list[str]:
    if not os.path.exists(path):
        return []
    with open(path, "r", encoding="utf-8") as f:
        data = yaml.safe_load(f)
    if not data:
        return []
    # Если это просто список строк
    if isinstance(data, list):
        if all(isinstance(x, str) for x in data):
            return data
    # Если это словарь с ключом channels
    if isinstance(data, dict) and "channels" in data:
        channels = data["channels"]
        if isinstance(channels, list):
            result = []
            for ch in channels:
                if isinstance(ch, str):
                    result.append(ch)
                elif isinstance(ch, dict):
                    if ch.get("enabled", True):
                        result.append(ch.get("id"))
            return [c for c in result if c]
    return [] 