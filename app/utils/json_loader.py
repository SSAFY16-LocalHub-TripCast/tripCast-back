import json
from pathlib import Path

DATA_DIR = Path(__file__).resolve().parent.parent / "data"


def load_travel_data() -> list[dict]:
    result = []

    for file_path in DATA_DIR.glob("*.json"):

        with open(file_path, encoding="utf-8") as f:

            root = json.load(f)

            region = root.get("region", "")
            content_type = root.get("contentType", "")

            for item in root.get("items", []):

                # 원본 item을 그대로 사용하면서
                # 검색에 필요한 정보만 추가
                item["region"] = region
                item["contentType"] = content_type

                result.append(item)

    return result