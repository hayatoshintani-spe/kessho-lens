"""Render Cron Job / GitHub Actions 用キックスクリプト

バックエンドの /api/intel/cron/daily-brief を CRON_SECRET 付きで叩くだけ。

必要な環境変数:
    BACKEND_URL    バックエンドのベースURL (例: https://tsuburaya-intel-backend.onrender.com)
    CRON_SECRET    バックエンドと同じ CRON_SECRET
"""
import os
import sys

import httpx


def main() -> int:
    backend_url = os.environ.get("BACKEND_URL", "").rstrip("/")
    secret = os.environ.get("CRON_SECRET", "")
    if not backend_url or not secret:
        print("Missing BACKEND_URL or CRON_SECRET", file=sys.stderr)
        return 1

    try:
        resp = httpx.post(
            f"{backend_url}/api/intel/cron/daily-brief",
            headers={"Authorization": f"Bearer {secret}"},
            timeout=90.0,  # Render コールドスタート考慮
        )
    except httpx.HTTPError as e:
        print(f"Request failed: {e}", file=sys.stderr)
        return 1

    print(f"HTTP {resp.status_code}")
    print(resp.text)
    return 0 if resp.is_success else 1


if __name__ == "__main__":
    sys.exit(main())
