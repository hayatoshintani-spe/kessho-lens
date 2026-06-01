"""データ層: JSON ストレージ"""

from .storage import Storage, read_json, write_json, ensure_data_dir

__all__ = [
    "Storage",
    "read_json",
    "write_json",
    "ensure_data_dir",
]
