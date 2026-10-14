"""Compare the official UCI 412 copy against local UCI 411, without pooling either."""
from __future__ import annotations

import hashlib
import json
import sys
from io import BytesIO
from pathlib import Path
from zipfile import ZipFile

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from ml.schema import ROOT


AUDIT_DIR = ROOT / "data" / "external_audit" / "v2"
ARCHIVE = AUDIT_DIR / "uci412.zip"
LOCAL_411 = ROOT / "data" / "raw" / "extention of Z-Alizadeh sani dataset.xlsx"
OUTPUT = AUDIT_DIR / "uci412-audit.json"
UCI412_URL = "https://archive.ics.uci.edu/static/public/412/z%2Balizadeh%2Bsani.zip"


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def canonical(series: pd.Series) -> pd.Series:
    return series.map(lambda value: value.casefold() if isinstance(value, str) else value)


def main() -> None:
    if not ARCHIVE.is_file() or not LOCAL_411.is_file():
        raise FileNotFoundError("Audit requires the separately stored UCI 412 ZIP and the original UCI 411 workbook.")

    with ZipFile(ARCHIVE) as archive:
        names = archive.namelist()
        workbook_name = "Z-Alizadeh sani dataset.xlsx"
        if names != [workbook_name]:
            raise ValueError(f"Unexpected UCI 412 archive contents: {names}")
        workbook_bytes = archive.read(workbook_name)
        df412 = pd.read_excel(BytesIO(workbook_bytes), sheet_name="Sheet 1 - Table 1")
        empty_sheet = pd.read_excel(BytesIO(workbook_bytes), sheet_name="Sheet1")

    df411 = pd.read_excel(LOCAL_411, sheet_name="Sheet 1 - Table 1")
    shared = sorted(set(df412.columns) & set(df411.columns))
    if "Cath" not in shared:
        raise ValueError("Expected common CAD label Cath.")
    input_columns = [column for column in shared if column != "Cath"]

    exact_input_mismatches = {
        column: int((df411[column] != df412[column]).sum())
        for column in input_columns
    }
    normalized_input_mismatches = {
        column: int((canonical(df411[column]) != canonical(df412[column])).sum())
        for column in input_columns
    }
    cath_exact_mismatches = int((df411["Cath"] != df412["Cath"]).sum())
    cath_casefold_mismatches = int((canonical(df411["Cath"]) != canonical(df412["Cath"])).sum())

    result = {
        "audited_at": "2026-10-08",
        "sources": {
            "uci412": {
                "page": "https://archive.ics.uci.edu/dataset/412/z",
                "download": UCI412_URL,
                "doi": "10.24432/C5Q31T",
                "authors": "Roohallah Alizadehsani, Mohamad Roshanzamir, Zahra Sani",
                "license": "CC BY 4.0",
                "archive": str(ARCHIVE.relative_to(ROOT)),
                "archive_bytes": ARCHIVE.stat().st_size,
                "archive_sha256": sha256(ARCHIVE),
                "contained_workbook": workbook_name,
                "workbook_bytes": len(workbook_bytes),
                "workbook_sha256": hashlib.sha256(workbook_bytes).hexdigest(),
                "populated_sheet_shape": list(df412.shape),
                "empty_sheet_shape": list(empty_sheet.shape),
            },
            "uci411": {
                "page": "https://archive.ics.uci.edu/dataset/411/extention%2Bof%2Bz%2Balizadeh%2Bsani%2Bdataset",
                "doi": "10.24432/C5461K",
                "license": "CC BY 4.0",
                "workbook": str(LOCAL_411.relative_to(ROOT)),
                "workbook_sha256": sha256(LOCAL_411),
                "populated_sheet_shape": list(df411.shape),
            },
        },
        "comparison": {
            "shared_columns": len(shared),
            "shared_input_columns_excluding_cath": len(input_columns),
            "rows_uci412": len(df412),
            "rows_uci411": len(df411),
            "same_row_order_and_exact_shared_inputs": not any(exact_input_mismatches.values()),
            "input_exact_mismatch_counts_by_column": exact_input_mismatches,
            "input_casefold_mismatch_counts_by_column": normalized_input_mismatches,
            "cath_exact_mismatch_rows": cath_exact_mismatches,
            "cath_casefold_mismatch_rows": cath_casefold_mismatches,
            "uci411_only_columns": sorted(set(df411.columns) - set(df412.columns)),
            "uci412_only_columns": sorted(set(df412.columns) - set(df411.columns)),
            "cath_counts_uci411": {str(k): int(v) for k, v in df411["Cath"].value_counts().items()},
            "cath_counts_uci412": {str(k): int(v) for k, v in df412["Cath"].value_counts().items()},
        },
        "decision": (
            "UCI 412 is the same 303-row cohort as UCI 411: all 55 shared pre-outcome input columns "
            "match exactly in the same row order; Cath differs only by uppercase CAD spelling in 216 rows. "
            "UCI 411 adds LAD/LCX/RCA labels. Do not pool, split across train/test, or describe UCI 412 as independent validation."
        ),
        "scope": "Audit-only copy. This script reads only shared inputs and Cath for the comparison; no rows are added to production data or model evaluation.",
    }
    OUTPUT.write_text(json.dumps(result, indent=2, ensure_ascii=False), encoding="utf-8")
    print(json.dumps(result, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
