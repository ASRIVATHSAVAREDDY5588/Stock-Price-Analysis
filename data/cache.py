"""Caching layer for market data to minimize external network calls and enable offline caching."""

from __future__ import annotations

import json
import time
from pathlib import Path
from typing import Optional, Tuple
import pandas as pd

from config import CACHE_DIR, CACHE_TTL_SECONDS


class MarketDataCache:
    """Simple disk-backed parquet/JSON cache for stock time series."""

    def __init__(self, cache_dir: Path = CACHE_DIR, ttl_seconds: int = CACHE_TTL_SECONDS):
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.ttl_seconds = ttl_seconds

    def _get_paths(self, key: str) -> Tuple[Path, Path]:
        safe_key = "".join(c if c.isalnum() or c in ("-", "_") else "_" for c in key)
        data_path = self.cache_dir / f"{safe_key}.parquet"
        meta_path = self.cache_dir / f"{safe_key}.meta.json"
        return data_path, meta_path

    def get(self, key: str) -> Optional[Tuple[pd.DataFrame, dict]]:
        """Retrieve cached dataframe and metadata if within TTL."""
        data_path, meta_path = self._get_paths(key)
        if not data_path.exists() or not meta_path.exists():
            return None

        try:
            with open(meta_path, "r", encoding="utf-8") as f:
                meta = json.load(f)

            fetched_at = meta.get("fetched_at", 0)
            if (time.time() - fetched_at) > self.ttl_seconds:
                return None  # Stale

            df = pd.read_parquet(data_path)
            return df, meta
        except Exception:
            # On any disk read error, treat as cache miss
            return None

    def set(self, key: str, df: pd.DataFrame, source: str, extra_meta: Optional[dict] = None) -> None:
        """Save dataframe and metadata to disk cache."""
        data_path, meta_path = self._get_paths(key)
        try:
            df.to_parquet(data_path, index=True)
            meta = {
                "key": key,
                "source": source,
                "fetched_at": time.time(),
                "fetched_time_str": time.strftime("%Y-%m-%d %H:%M:%S UTC", time.gmtime()),
                "row_count": len(df),
                **(extra_meta or {}),
            }
            with open(meta_path, "w", encoding="utf-8") as f:
                json.dump(meta, f, indent=2)
        except Exception as e:
            # Caching failure shouldn't crash calculation
            pass

    def clear(self) -> None:
        """Clear all cached files."""
        for p in self.cache_dir.glob("*"):
            try:
                if p.is_file():
                    p.unlink()
            except Exception:
                pass


# Global singleton instance
cache = MarketDataCache()
