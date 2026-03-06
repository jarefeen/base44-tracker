from abc import ABC, abstractmethod
import pandas as pd


class DataSource(ABC):
    @property
    @abstractmethod
    def name(self) -> str:
        ...

    @abstractmethod
    def is_available(self) -> bool:
        ...

    @abstractmethod
    def fetch(self) -> dict:
        """Return a dict with at least 'df' (DataFrame) and 'kpi' (dict with value, delta, label)."""
        ...

    def fetch_safe(self) -> dict:
        """Fetch with error handling. Returns error info on failure."""
        try:
            return {"ok": True, **self.fetch()}
        except Exception as e:
            return {"ok": False, "error": str(e), "df": pd.DataFrame(), "kpi": None}
