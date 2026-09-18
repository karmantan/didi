#!/usr/bin/env python3

from __future__ import annotations


USER_CONFIG = {
    "raw_glob": r"D:\gastwissenschaftler\gastw_20\DIDI\XPrivat\Tan\processed_data\parquet_files\df_4pct_processed\*.parquet",
    "output_dir": r"D:\gastwissenschaftler\gastw_20\DIDI\XPrivat\Tan\processed_data\pipeline_runs",
    "sample_tag": "4pct_firstmarriage_lag1_lag3_notyetdivorced",
    "data_profile": "canonical",
    "source_has_entgelt": True,
    "first_marriage_source": "date_fields",
    "year_start": 2012,
    "year_cap": 2018,
    "followup_years": 5,
    "mortality_horizon": 10,
    "lag_depth": 1,
    "lag_comparison_common_year_start": 2014,
    "control_pool": "not_yet_divorced",
    "caliper": 0.01,
    "controls_per_treated": 1,
    "reuse_controls_across_years": False,
    "seed": 42,
    "strict_main_run": True,
    "minimum_category_frequency": 10,
    "max_propensity_fit_rows": 500_000,
    "propensity_score_batch_size": 100_000,
    "checkpoint_row_group_size": 200_000,
    "propensity_max_iter": 1_000_000,
    "propensity_tol": 1e-4,
    "smd_threshold": 0.10,
    "outcome_bootstrap_replicates": 200,
    "absolute_effect_bootstrap_replicates": 200,
    "optimal_match_dense_max_entries": 5_000_000,
    "optimal_match_sparse_max_edges": 100_000_000,
    "run_lag1_vs_lag3": True,
    "generate_figures": True,
    "run_longitudinal_mediation": True,
    "run_msk_dropout_sensitivity": True,
    "mediation_bootstrap_replicates": 200,


    "mediation_bootstrap_workers": 0,


    "propensity_solver": "lbfgs",
    "gcomp_horizon_years": 5,
    "gcomp_simulation_repetitions": 25,
    "gcomp_bootstrap_simulation_repetitions": 25,
    "gcomp_use_observation_ipcw": True,
    "gcomp_observation_probability_floor": 0.02,
    "gcomp_ipcw_cap": 20.0,
    "gcomp_timevarying_continuous": ["entgelt_value", "rtzb_value"],
    "gcomp_timevarying_binary": ["non_success_app_this_year", "non_msk_rehab_this_year"],
    "gcomp_timevarying_categorical": ["income_source_status"],
    "death_registry_end_year": 2023,
    "total_rebuild": True,
    "msk_diagnosis_codes": [20, 53, 56],
    "mental_health_diagnosis_codes": [30],
    "outcome_logit_max_iter": 5_000,
    "gcomp_logit_max_iter": 20_000,
    "gcomp_logit_tol": 1e-6,
    "gcomp_continuous_log_cap_headroom": 3.0,
    "protect_matching": True,
}

PAPER_REPORTING_CONFIG = {
    "minimum_cell_people": 20,
    "pool_small_diagnosis_codes": True,
    "protect_matchability_cells": True,
    "withhold_small_overlap_counts": True,
}

DEFAULT_RUN_MODE = "main"
DEFAULT_FORCE_REBUILD = False
DEFAULT_REUSE_EXISTING = False
DEFAULT_BOOTSTRAP_REPLICATIONS = 100

TARGET_PYTHON_VERSION = "3.9.1"
TARGET_POLARS_VERSION = "0.20.16"

CANONICAL_DEFINITIONS = {
    "whot_bland": "Bundesland/state code; categorical",
    "whot_skt": "settlement/region type such as city or village; categorical",
    "rtzb": "pension income amount",
    "entgelt": "employment earnings amount",
    "byvlgs": "full-time employment contribution periods; missingness may be economically informative",
    "bygmgs": "part-time employment contribution periods; missingness may be economically informative",
    "byvlgs_missing": "indicator that full-time contribution-period information is unavailable",
    "bygmgs_missing": "indicator that part-time contribution-period information is unavailable",
    "mcdams": "rehabilitation duration in days",
    "maciufzt": "categorical months of incapacity before rehabilitation",
    "fmsd": "annual marital status after researcher reconstruction: 1 non-married mixed category, 2 married, 3 divorced",
    "first_marriage_start": "start date of the earliest observed marriage spell",
    "first_marriage_end": "end date of the earliest observed marriage spell",
    "is_first_marriage": "playdata indicator used only as a proxy for first-marriage validation",
}

CORE_RAW_COLUMNS = [
    "simple_id", "ja", "gbja", "rtwf_jjjj", "ge", "divorcing", "fmsd",
    "marriage_start", "marriage_end", "court_decision",
    "first_marriage_start", "first_marriage_end", "is_first_marriage",
    "entgelt", "rtzb", "byvlgs", "bygmgs",
    "whot_bland", "whot_skt", "ttsc1_kldb1988",
    "seg_start_rsd_1", "seg_end_rsd_1", "rehab_start_1", "rehab_end_1",
    "mcdggr_succeed_1", "mcdams_succeed_1",
    "seg_start_rsd_2", "seg_end_rsd_2", "rehab_start_2", "rehab_end_2",
    "mcdggr_succeed_2", "mcdams_succeed_2",
    "application_date_fail", "decision_date_fail",
    "application_date_withdrawn", "decision_date_withdrawn",
    "application_date_forward", "decision_date_forward",
]

INCAPACITY_CANDIDATES = {
    1: ["maciufzt_succeed_1", "mcaiufzt_succeed_1"],
    2: ["maciufzt_succeed_2", "mcaiufzt_succeed_2"],
}

DATE_COLUMNS = [
    "marriage_start", "marriage_end", "court_decision",
    "first_marriage_start", "first_marriage_end",
    "seg_start_rsd_1", "seg_end_rsd_1", "rehab_start_1", "rehab_end_1",
    "seg_start_rsd_2", "seg_end_rsd_2", "rehab_start_2", "rehab_end_2",
    "application_date_fail", "decision_date_fail",
    "application_date_withdrawn", "decision_date_withdrawn",
    "application_date_forward", "decision_date_forward",
]

CATEGORICAL_BASELINE = {
    "ge", "age_band", "whot_bland", "whot_skt", "occ_l1", "income_source_status", "fmsd"
}

CONTINUOUS_BASELINE = {
    "age", "cum_rehabs_by_year", "cum_mental_health_rehabs_by_year",
    "years_since_last_rehab", "byvlgs_value", "bygmgs_value", "entgelt_value", "rtzb_value"
}

BINARY_BASELINE = {
    "ever_rehab_to_date", "ever_mental_health_rehab_to_date",
    "non_success_app_this_year", "byvlgs_missing", "bygmgs_missing",
}

from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any
import json
import sys

try:
    import yaml
except ImportError:
    yaml = None

_DATACLASS_KWARGS = {"slots": True} if sys.version_info >= (3, 10) else {}

def _normalize_diagnosis_codes(codes) -> list[int]:
    if codes is None:
        return []
    if isinstance(codes, (int, float, str)):
        codes = [codes]
    normalized: list[int] = []
    for code in codes:
        if code is None:
            continue
        try:
            value = int(float(str(code).strip()))
        except (TypeError, ValueError):
            continue
        if value not in normalized:
            normalized.append(value)
    return sorted(normalized)

@dataclass(**_DATACLASS_KWARGS)
class PipelineConfig:
    raw_glob: str
    output_dir: str
    sample_tag: str = "sample"
    year_start: int = 2012
    year_cap: int | None = 2018
    followup_years: int = 5
    mortality_horizon: int = 10
    lag_depth: int = 1
    control_pool: str = "not_yet_divorced"
    caliper: float = 0.01
    controls_per_treated: int = 1
    seed: int = 42
    reuse_controls_across_years: bool = False
    minimum_category_frequency: int = 10
    strict_main_run: bool = True
    checkpoint_row_group_size: int = 200_000
    max_propensity_fit_rows: int = 500_000
    propensity_score_batch_size: int = 100_000
    propensity_max_iter: int = 10_000
    propensity_tol: float = 1e-4
    smd_threshold: float = 0.10
    outcome_bootstrap_replicates: int = 200
    absolute_effect_bootstrap_replicates: int = 200
    optimal_match_dense_max_entries: int = 5_000_000
    optimal_match_sparse_max_edges: int = 20_000_000
    run_lag1_vs_lag3: bool = True
    lag_comparison_common_year_start: int = 2014
    generate_figures: bool = True
    run_longitudinal_mediation: bool = True
    run_msk_dropout_sensitivity: bool = True
    mediation_bootstrap_replicates: int = 200
    mediation_bootstrap_workers: int = 0
    propensity_solver: str = "lbfgs"
    gcomp_horizon_years: int = 5
    gcomp_simulation_repetitions: int = 25
    gcomp_bootstrap_simulation_repetitions: int = 25
    gcomp_use_observation_ipcw: bool = True
    gcomp_observation_probability_floor: float = 0.02
    gcomp_ipcw_cap: float = 20.0
    gcomp_timevarying_continuous: list[str] = field(default_factory=lambda: [
        "entgelt_value", "rtzb_value"
    ])
    gcomp_timevarying_binary: list[str] = field(default_factory=lambda: [
        "non_success_app_this_year", "non_msk_rehab_this_year"
    ])
    gcomp_timevarying_categorical: list[str] = field(default_factory=lambda: [
        "income_source_status"
    ])
    death_registry_end_year: int = 2023
    total_rebuild: bool = True
    msk_diagnosis_codes: list[int] = field(default_factory=lambda: [20, 53, 56])
    mental_health_diagnosis_codes: list[int] = field(default_factory=lambda: [30])
    outcome_logit_max_iter: int = 5_000
    gcomp_logit_max_iter: int = 20_000
    gcomp_logit_tol: float = 1e-6
    gcomp_continuous_log_cap_headroom: float = 3.0
    protect_matching: bool = True
    reuse_existing_outputs: bool = False
    data_profile: str = "canonical"
    source_has_entgelt: bool = True
    first_marriage_source: str = "date_fields"
    exact_covariates: list[str] = field(default_factory=lambda: [
        "lag1_ge_cat", "lag1_age_band", "lag1_ever_rehab_to_date"
    ])
    propensity_numeric: list[str] = field(default_factory=lambda: [
        "lag1_age",
        "lag1_cum_rehabs_by_year",
        "lag1_cum_mental_health_rehabs_by_year",
        "lag1_years_since_last_rehab",
        "lag1_byvlgs_value",
        "lag1_bygmgs_value",
        "lag1_entgelt_value",
        "lag1_rtzb_value",
    ])
    propensity_binary: list[str] = field(default_factory=lambda: [
        "lag1_ever_rehab_to_date",
        "lag1_ever_mental_health_rehab_to_date",
        "lag1_non_success_app_this_year",
        "lag1_byvlgs_missing",
        "lag1_bygmgs_missing",
    ])
    propensity_categorical: list[str] = field(default_factory=lambda: [
        "lag1_whot_bland_cat",
        "lag1_occ_l1_cat",
        "lag1_income_source_status",
        "lag1_fmsd_cat",
    ])
    def validate(self) -> None:
        if self.data_profile not in {"canonical", "playdata"}:
            raise ValueError("data_profile must be 'canonical' or 'playdata'")
        if self.first_marriage_source not in {"date_fields", "is_first_marriage"}:
            raise ValueError(
                "first_marriage_source must be 'date_fields' or 'is_first_marriage'"
            )
        if self.data_profile == "playdata" and self.source_has_entgelt:
            raise ValueError("The playdata profile must not claim that entgelt is available.")
        if self.lag_depth not in (1, 3):
            raise ValueError("lag_depth must be 1 or 3")
        if self.lag_comparison_common_year_start < self.year_start:
            raise ValueError(
                "lag_comparison_common_year_start must not precede year_start"
            )
        if (self.year_cap is not None
                and self.lag_comparison_common_year_start > self.year_cap):
            raise ValueError(
                "lag_comparison_common_year_start must not exceed year_cap"
            )
        if self.control_pool != "not_yet_divorced":
            raise ValueError(
                "The canonical pipeline currently uses only not-yet-divorced controls. "
                "Alternative marital-status control pools are intentionally deferred."
            )
        if self.controls_per_treated != 1:
            raise ValueError("The memory-bounded matcher currently supports 1:1 matching only.")
        if self.caliper <= 0:
            raise ValueError("caliper must be positive")
        if self.followup_years < 1 or self.mortality_horizon < 1:
            raise ValueError("follow-up horizons must be positive")
        if self.year_cap is not None and self.year_start > self.year_cap:
            raise ValueError("year_start must not exceed year_cap")
        if self.max_propensity_fit_rows < 100:
            raise ValueError("max_propensity_fit_rows must be at least 100")
        if self.propensity_score_batch_size < 10:
            raise ValueError("propensity_score_batch_size must be at least 10")
        if self.propensity_max_iter < 100:
            raise ValueError("propensity_max_iter must be at least 100")
        if not 0 < self.propensity_tol < 1:
            raise ValueError("propensity_tol must lie strictly between 0 and 1")
        if not 0 <= self.smd_threshold < 1:
            raise ValueError("smd_threshold must lie in [0, 1)")
        if (self.outcome_bootstrap_replicates < 20
                or self.absolute_effect_bootstrap_replicates < 20
                or self.mediation_bootstrap_replicates < 20):
            raise ValueError("bootstrap replicate counts must be at least 20")
        if self.gcomp_horizon_years < 1:
            raise ValueError("gcomp_horizon_years must be positive")
        if self.gcomp_horizon_years > self.mortality_horizon:
            raise ValueError("gcomp_horizon_years must not exceed mortality_horizon")
        if self.year_cap is not None and (
            self.year_cap + self.gcomp_horizon_years > self.death_registry_end_year
        ):
            raise ValueError(
                "The longitudinal mediation horizon must be observed for every treatment cohort."
            )
        if self.gcomp_simulation_repetitions < 1:
            raise ValueError("gcomp_simulation_repetitions must be positive")
        if self.gcomp_bootstrap_simulation_repetitions < 1:
            raise ValueError("gcomp_bootstrap_simulation_repetitions must be positive")
        if not isinstance(self.mediation_bootstrap_workers, int) or self.mediation_bootstrap_workers < 0:
            raise ValueError("mediation_bootstrap_workers must be 0 (automatic) or a positive integer")
        if self.propensity_solver not in {"lbfgs", "saga"}:
            raise ValueError("propensity_solver must be 'lbfgs' or 'saga'")
        if not 0 < self.gcomp_observation_probability_floor < 0.5:
            raise ValueError("gcomp_observation_probability_floor must lie in (0, 0.5)")
        if self.gcomp_ipcw_cap <= 1:
            raise ValueError("gcomp_ipcw_cap must be greater than 1")
        if self.gcomp_continuous_log_cap_headroom <= 0:
            raise ValueError("gcomp_continuous_log_cap_headroom must be positive")
        if not isinstance(self.run_longitudinal_mediation, bool):
            raise ValueError("run_longitudinal_mediation must be True or False")
        if not isinstance(self.gcomp_use_observation_ipcw, bool):
            raise ValueError("gcomp_use_observation_ipcw must be True or False")
        if self.death_registry_end_year < (self.year_cap or self.year_start):
            raise ValueError("death_registry_end_year must not precede the latest index year")
        if self.optimal_match_dense_max_entries < 1_000:
            raise ValueError("optimal_match_dense_max_entries is implausibly small")
        if self.optimal_match_sparse_max_edges < 1_000:
            raise ValueError("optimal_match_sparse_max_edges is implausibly small")
        if not isinstance(self.run_msk_dropout_sensitivity, bool):
            raise ValueError("run_msk_dropout_sensitivity must be True or False")
        if not isinstance(self.total_rebuild, bool):
            raise ValueError("total_rebuild must be True or False")
        if not self.sample_tag or self.sample_tag.strip() in {".", ".."}:
            raise ValueError("sample_tag must be a non-empty, safe folder name")
        if Path(self.sample_tag).name != self.sample_tag:
            raise ValueError("sample_tag must be a simple folder name, not a path")
        if self.reuse_controls_across_years:
            raise ValueError(
                "The canonical outcome pipeline currently requires global control non-reuse. "
                "Cross-year reuse needs dependence-aware inference and is intentionally disabled."
            )
        if not _normalize_diagnosis_codes(self.msk_diagnosis_codes):
            raise ValueError("msk_diagnosis_codes must contain at least one integer diagnosis code")
        if not _normalize_diagnosis_codes(self.mental_health_diagnosis_codes):
            raise ValueError("mental_health_diagnosis_codes must contain at least one integer diagnosis code")
        if set(_normalize_diagnosis_codes(self.msk_diagnosis_codes)) & set(
            _normalize_diagnosis_codes(self.mental_health_diagnosis_codes)
        ):
            raise ValueError("msk_diagnosis_codes and mental_health_diagnosis_codes must not overlap")
        if self.outcome_logit_max_iter < 100:
            raise ValueError("outcome_logit_max_iter must be at least 100")
        if self.gcomp_logit_max_iter < 100:
            raise ValueError("gcomp_logit_max_iter must be at least 100")
        if not 0 < self.gcomp_logit_tol < 1e-2:
            raise ValueError("gcomp_logit_tol must lie strictly between 0 and 0.01")
        if not isinstance(self.protect_matching, bool):
            raise ValueError("protect_matching must be True or False")
    @property
    def run_dir(self) -> Path:
        return Path(self.output_dir) / self.sample_tag
    @property
    def panels_dir(self) -> Path:
        return self.run_dir / "panels"
    @property
    def analysis_dir(self) -> Path:
        return self.run_dir / "analysis"
    @property
    def diagnostics_dir(self) -> Path:
        return self.run_dir / "diagnostics"
    @property
    def logs_dir(self) -> Path:
        return self.run_dir / "logs"
    @property
    def figures_dir(self) -> Path:
        return self.run_dir / "figures"
    def ensure_dirs(self) -> None:
        for path in (self.run_dir, self.panels_dir, self.analysis_dir, self.diagnostics_dir, self.logs_dir, self.figures_dir):
            path.mkdir(parents=True, exist_ok=True)
    def to_dict(self) -> dict[str, Any]:
        return asdict(self)
    def write(self, path: str | Path) -> None:
        Path(path).write_text(json.dumps(self.to_dict(), indent=2), encoding="utf-8")
    @classmethod
    def from_yaml(cls, path: str | Path) -> "PipelineConfig":
        if yaml is None:
            raise ImportError("PyYAML is not installed. Edit USER_CONFIG at the top of the file instead.")
        data = yaml.safe_load(Path(path).read_text(encoding="utf-8")) or {}
        data = dict(data)
        data.pop("paper_reporting", None)
        cfg = cls(**data)
        cfg.validate()
        return cfg

@dataclass(**_DATACLASS_KWARGS)
class PaperReportingConfig:
    minimum_cell_people: int = 20
    pool_small_diagnosis_codes: bool = True
    protect_matchability_cells: bool = True
    withhold_small_overlap_counts: bool = True
    def validate(self) -> None:
        if self.minimum_cell_people < 0:
            raise ValueError(
                "minimum_cell_people must be non-negative (0 disables threshold rules)"
            )
        for name in (
            "pool_small_diagnosis_codes",
            "protect_matchability_cells",
            "withhold_small_overlap_counts",
        ):
            if not isinstance(getattr(self, name), bool):
                raise ValueError(f"{name} must be True or False")
    def to_dict(self) -> dict[str, Any]:
        return asdict(self)
    def write(self, path: str | Path) -> None:
        Path(path).write_text(json.dumps(self.to_dict(), indent=2), encoding="utf-8")

def load_pipeline_and_reporting_config(
    path: str | Path,
) -> tuple[PipelineConfig, PaperReportingConfig]:
    if yaml is None:
        raise ImportError("PyYAML is not installed. Edit the settings blocks instead.")
    data = yaml.safe_load(Path(path).read_text(encoding="utf-8")) or {}
    data = dict(data)
    reporting_data = data.pop("paper_reporting", {}) or {}
    pipeline = PipelineConfig(**data)
    reporting = PaperReportingConfig(**reporting_data)
    pipeline.validate()
    reporting.validate()
    return pipeline, reporting

from functools import lru_cache
from glob import glob
from pathlib import Path
import hashlib
import json
import logging
import os
import platform
import sys
import time

import polars as pl

log = logging.getLogger(__name__)

@lru_cache(maxsize=1)
def _streaming_collect_kwargs() -> dict[str, object]:
    probe = pl.LazyFrame({"_polars_api_probe": [1]})
    version_text = str(getattr(pl, "__version__", ""))
    try:
        major = int(version_text.split(".", 1)[0])
    except (TypeError, ValueError):
        major = 0
    candidates = (
        ({"streaming": True}, {"engine": "streaming"})
        if major == 0
        else ({"engine": "streaming"}, {"streaming": True})
    )
    errors: list[str] = []
    for kwargs in candidates:
        try:
            probe.collect(**kwargs)
            return kwargs
        except (TypeError, ValueError) as exc:
            errors.append(f"{kwargs}: {exc}")
    raise RuntimeError(
        "Installed Polars exposes neither supported streaming collect API. "
        + " | ".join(errors)
    )

def _can_retry_polars_nonstreaming(exc: BaseException) -> bool:
    if isinstance(exc, (KeyboardInterrupt, SystemExit, GeneratorExit, MemoryError, OSError)):
        return False
    module = type(exc).__module__
    name = type(exc).__name__
    return (
        module.startswith("polars")
        or module.startswith("pyo3_runtime")
        or name == "PanicException"
        or isinstance(exc, (TypeError, ValueError, RuntimeError))
    )

@lru_cache(maxsize=1)
def _polars_runtime_capabilities() -> dict[str, object]:
    kwargs = _streaming_collect_kwargs()
    return {
        "polars_version": getattr(pl, "__version__", "unknown"),
        "polars_path": getattr(pl, "__file__", "unknown"),
        "streaming_collect_mode": (
            "engine=streaming" if "engine" in kwargs else "streaming=True"
        ),
        "collect_batches_available": hasattr(pl.LazyFrame, "collect_batches"),
        "slice_batch_fallback_available": True,
    }

def _safe_collect(lf: pl.LazyFrame, **extra_kwargs) -> pl.DataFrame:
    try:
        return lf.collect(**_streaming_collect_kwargs(), **extra_kwargs)
    except BaseException as exc:
        if not _can_retry_polars_nonstreaming(exc):
            raise
        log.warning(
            "Streaming collect failed (%s: %s); retrying with the non-streaming engine. "
            "If you see this warning at a call site that isn't already using "
            "_safe_collect, that's the signal for where to apply it next.",
            type(exc).__name__, exc,
        )
        return lf.collect(**extra_kwargs)

DTYPE_OVERRIDES = {
    "simple_id": pl.Int64,
    "ja": pl.Int32,
    "gbja": pl.Int32,
    "rtwf_jjjj": pl.Int32,
    "ge": pl.Int32,
    "divorcing": pl.Int8,
    "mcdggr_succeed_1": pl.Int32,
    "mcdggr_succeed_2": pl.Int32,
    "mcdams_succeed_1": pl.Float64,
    "mcdams_succeed_2": pl.Float64,
    "maciufzt_succeed_1": pl.Utf8,
    "maciufzt_succeed_2": pl.Utf8,
    "mcaiufzt_succeed_1": pl.Utf8,
    "mcaiufzt_succeed_2": pl.Utf8,
}

@lru_cache(maxsize=16)
def schema_union(shards_glob: str) -> dict[str, pl.DataType]:
    schema: dict[str, pl.DataType] = {}
    files = sorted(glob(shards_glob))
    if not files:
        raise FileNotFoundError(f"No parquet files matched {shards_glob!r}")
    for file in files:
        for name, dtype in pl.read_parquet_schema(file).items():
            schema.setdefault(name, dtype)
    return schema

def present_columns(schema: dict[str, pl.DataType], requested: list[str]) -> list[str]:
    return [column for column in requested if column in schema]

def _pandas_arrow_roundtrip_status() -> dict[str, object]:
    try:
        import pyarrow as pa
    except ImportError as exc:
        return {
            "pyarrow_available": False,
            "pyarrow_version": None,
            "polars_pandas_roundtrip_ok": False,
            "error": f"{type(exc).__name__}: {exc}",
        }
    try:
        test = pl.DataFrame({"_roundtrip": [1, 2]}).to_pandas()
        back = pl.from_pandas(test)
        ok = back.height == 2 and back.get_column("_roundtrip").to_list() == [1, 2]
        return {
            "pyarrow_available": True,
            "pyarrow_version": getattr(pa, "__version__", "unknown"),
            "polars_pandas_roundtrip_ok": bool(ok),
            "error": None if ok else "round-trip returned unexpected values",
        }
    except Exception as exc:
        return {
            "pyarrow_available": True,
            "pyarrow_version": getattr(pa, "__version__", "unknown"),
            "polars_pandas_roundtrip_ok": False,
            "error": f"{type(exc).__name__}: {exc}",
        }

def _require_pandas_arrow_roundtrip() -> None:
    status = _pandas_arrow_roundtrip_status()
    if not status["polars_pandas_roundtrip_ok"]:
        raise RuntimeError(
            "Polars<->pandas conversion preflight failed. This pipeline requires a "
            "working PyArrow-backed round trip because matching and outcome models use "
            f"pandas/scikit-learn after Polars preprocessing. Diagnostic: {status}"
        )

def scan_aligned(shards_glob: str, columns: list[str]) -> pl.LazyFrame:
    files = sorted(glob(shards_glob))
    schema = schema_union(shards_glob)
    columns = present_columns(schema, columns)
    if not files:
        raise FileNotFoundError(f"No parquet files matched {shards_glob!r}")
    frames: list[pl.LazyFrame] = []
    for file in files:
        file_schema = pl.read_parquet_schema(file)
        expressions = []
        for column in columns:
            target = DTYPE_OVERRIDES.get(column, schema[column])
            if column in file_schema:
                expressions.append(pl.col(column).cast(target, strict=False).alias(column))
            else:
                expressions.append(pl.lit(None, dtype=target).alias(column))
        frames.append(pl.scan_parquet(file).select(expressions))
    return pl.concat(frames, how="vertical_relaxed")

def normalize_date(column: str, dtype: pl.DataType) -> pl.Expr:
    value = pl.col(column)
    if dtype == pl.Null:
        return pl.lit(None, dtype=pl.Date).alias(column)
    if dtype == pl.Date:
        return value.alias(column)
    if isinstance(dtype, pl.Datetime):
        return value.dt.date().alias(column)
    text = value.cast(pl.Utf8, strict=False).str.strip_chars()
    for missing_code in ("", "0", "0000-00-00", "9999-99-99", "99999999", "NaN", "nan", "NA", "N/A", "NaT"):
        text = text.replace(missing_code, None)
    text = text.str.replace(r"\.0+$", "")
    return pl.coalesce([
        value.cast(pl.Date, strict=False),
        value.cast(pl.Datetime, strict=False).dt.date(),
        text.str.strptime(pl.Date, format="%Y-%m-%d", strict=False),
        text.str.strptime(pl.Date, format="%Y%m%d", strict=False),
        text.str.strptime(pl.Date, format="%d.%m.%Y", strict=False),
        text.str.strptime(pl.Date, format="%Y/%m/%d", strict=False),
    ]).alias(column)

def sink_parquet(frame: pl.LazyFrame, path: str | Path, row_group_size: int = 200_000) -> Path:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.unlink(missing_ok=True)
    write_kwargs = dict(
        compression="zstd", compression_level=3, statistics=True, row_group_size=row_group_size,
    )
    try:
        frame.sink_parquet(temporary, maintain_order=False, **write_kwargs)
    except BaseException as exc:
        if not _can_retry_polars_nonstreaming(exc):
            raise
        log.warning(
            "Streaming sink_parquet rejected this plan (%s); falling back to an eager "
            "collect + write_parquet for %s.",
            exc, temporary,
        )
        _safe_collect(frame).write_parquet(temporary, **write_kwargs)
    temporary.replace(path)
    return path

def file_fingerprint(path: str | Path, chunk_size: int = 1 << 20) -> str:
    digest = hashlib.sha256()
    with Path(path).open("rb") as stream:
        while chunk := stream.read(chunk_size):
            digest.update(chunk)
    return digest.hexdigest()

def write_manifest(config, found_columns: list[str], generated_columns: list[str], path: str | Path) -> None:
    files = sorted(glob(config.raw_glob))
    payload = {
        "config": config.to_dict(),
        "target_runtime": {
            "python": TARGET_PYTHON_VERSION,
            "polars": TARGET_POLARS_VERSION,
        },
        "runtime": {
            "python": sys.version,
            "python_executable": sys.executable,
            "platform": platform.platform(),
            **_polars_runtime_capabilities(),
            "numpy": getattr(np, "__version__", "unknown"),
            "pandas": getattr(pd, "__version__", "unknown"),
            "scikit_learn": getattr(__import__("sklearn"), "__version__", "unknown"),
            "scipy": getattr(__import__("scipy"), "__version__", "unknown"),
        },
        "raw_files": [
            {"path": file, "size": os.path.getsize(file), "mtime": os.path.getmtime(file)}
            for file in files
        ],
        "found_raw_columns": found_columns,
        "generated_columns": generated_columns,
    }
    Path(path).write_text(json.dumps(payload, indent=2), encoding="utf-8")

def _run_signature_payload(config) -> dict:
    raw_files = sorted(glob(config.raw_glob))
    source_file = Path(globals().get("__file__", "")).resolve() if globals().get("__file__") else None
    package_dir = source_file.parent if source_file is not None else Path.cwd()
    code_files = [source_file] if source_file is not None and source_file.exists() else []
    return {
        "config": config.to_dict(),
        "raw_files": [
            {"path": file, "size": os.path.getsize(file), "mtime": os.path.getmtime(file)}
            for file in raw_files
        ],
        "code_files": [
            {"path": file.name, "sha256": file_fingerprint(file)}
            for file in code_files
        ],
    }

def clear_run_directory(config) -> dict:
    import shutil
    from datetime import datetime, timezone
    config.validate()
    run_dir = config.run_dir
    output_root = Path(config.output_dir)
    if run_dir == output_root or run_dir.name != config.sample_tag:
        raise RuntimeError(
            f"Unsafe rebuild target {run_dir}. The run directory must be a child named "
            f"exactly {config.sample_tag!r} under output_dir."
        )
    raw_files = [Path(path) for path in glob(config.raw_glob)]
    try:
        run_resolved = run_dir.resolve()
        for raw_file in raw_files:
            raw_resolved = raw_file.resolve()
            if raw_resolved == run_resolved or run_resolved in raw_resolved.parents:
                raise RuntimeError(
                    f"Refusing total rebuild because raw input {raw_file} is inside {run_dir}."
                )
    except OSError:
        pass
    existed = run_dir.exists()
    if existed:
        shutil.rmtree(run_dir)
    config.ensure_dirs()
    receipt = {
        "mode": "total_rebuild",
        "run_directory": str(run_dir),
        "previous_run_directory_existed": existed,
        "raw_files_deleted": False,
        "started_utc": datetime.now(timezone.utc).isoformat(),
    }
    (run_dir / "total_rebuild_receipt.json").write_text(
        json.dumps(receipt, indent=2), encoding="utf-8"
    )
    return receipt

STAGE_TIER_PANEL, STAGE_TIER_RISKSETS, STAGE_TIER_MATCHING, STAGE_TIER_DOWNSTREAM = 0, 1, 2, 3
STAGE_TIER_LABELS = {0: "analysis panel", 1: "risk sets", 2: "matching", 3: "post-matching analysis"}
CONFIG_KEY_STAGE_TIER = {
    **{key: STAGE_TIER_PANEL for key in (
        "raw_glob", "data_profile", "first_marriage_source", "source_has_entgelt",
    )},
    **{key: STAGE_TIER_RISKSETS for key in (
        "lag_depth", "control_pool", "year_start", "year_cap",
    )},
    **{key: STAGE_TIER_MATCHING for key in (
        "caliper", "controls_per_treated", "reuse_controls_across_years", "exact_covariates",
        "propensity_numeric", "propensity_binary", "propensity_categorical",
        "minimum_category_frequency", "max_propensity_fit_rows", "propensity_max_iter",
        "propensity_tol", "propensity_solver", "optimal_match_dense_max_entries",
        "optimal_match_sparse_max_edges", "seed", "strict_main_run",
    )},
}
RUN_POLICY_CONFIG_KEYS = {
    "output_dir", "sample_tag", "total_rebuild", "reuse_existing_outputs", "run_lag1_vs_lag3",
    "lag_comparison_common_year_start", "generate_figures", "run_longitudinal_mediation",
    "run_msk_dropout_sensitivity", "checkpoint_row_group_size", "propensity_score_batch_size",
    "mediation_bootstrap_workers", "protect_matching",
}
LEGACY_CONFIG_DEFAULTS = {
    "msk_diagnosis_codes": [20],
    "mental_health_diagnosis_codes": [30],
}

def _legacy_comparable(key: str, value):
    if key in ("msk_diagnosis_codes", "mental_health_diagnosis_codes"):
        return _normalize_diagnosis_codes(value)
    return value
PANEL_TIER_DIAGNOSTIC_PATTERNS = (
    "source_schema_report.json", "duplicate_person_year_keys*", "conflicting_person_death_years*",
    "panel_coverage_diagnostics.csv", "rehab_code_relabel_audit*",
)
RISKSET_TIER_PATTERNS = {
    "analysis": ("riskset_*.parquet",),
    "diagnostics": ("filter_audit_*.csv", "riskset_rehab_code_definition_*.json"),
}
MATCHING_TIER_PATTERNS = {
    "analysis": ("matched_pairs_*.parquet", "propensity_scores_*.parquet"),
    "diagnostics": ("matching_audit_*.csv", "matching_edge_preflight_*.csv"),
}

def _config_key_stage_tier(key: str) -> int | None:
    if key in RUN_POLICY_CONFIG_KEYS:
        return None
    return CONFIG_KEY_STAGE_TIER.get(key, STAGE_TIER_DOWNSTREAM)

def _stage_tier_of_output(directory_kind: str, name: str) -> int:
    from fnmatch import fnmatch
    if directory_kind == "diagnostics" and any(fnmatch(name, p) for p in PANEL_TIER_DIAGNOSTIC_PATTERNS):
        return STAGE_TIER_PANEL
    if any(fnmatch(name, p) for p in RISKSET_TIER_PATTERNS.get(directory_kind, ())):
        return STAGE_TIER_RISKSETS
    if any(fnmatch(name, p) for p in MATCHING_TIER_PATTERNS.get(directory_kind, ())):
        return STAGE_TIER_MATCHING
    return STAGE_TIER_DOWNSTREAM

def _remove_outputs_from_stage_tier(config, first_tier: int) -> list[str]:
    import shutil
    removed: list[str] = []
    if first_tier <= STAGE_TIER_PANEL:
        for path in (config.panels_dir, config.analysis_dir, config.diagnostics_dir, config.figures_dir):
            if path.exists():
                shutil.rmtree(path, ignore_errors=True)
                removed.append(str(path))
        config.ensure_dirs()
        return removed
    for kind, directory in (("analysis", config.analysis_dir), ("diagnostics", config.diagnostics_dir), ("figures", config.figures_dir)):
        if not directory.exists():
            continue
        for entry in sorted(directory.iterdir()):
            tier = STAGE_TIER_DOWNSTREAM if kind == "figures" else _stage_tier_of_output(kind, entry.name)
            if tier >= first_tier:
                if entry.is_dir():
                    shutil.rmtree(entry, ignore_errors=True)
                else:
                    entry.unlink(missing_ok=True)
                removed.append(str(entry))
    if first_tier <= STAGE_TIER_MATCHING:
        temp = config.run_dir / "_matching_temp"
        if temp.exists():
            shutil.rmtree(temp, ignore_errors=True)
            removed.append(str(temp))
    config.ensure_dirs()
    return removed

def _signature_change_report(previous_payload: dict, payload: dict) -> dict:
    old_config = previous_payload.get("config", {}) or {}
    new_config = payload.get("config", {}) or {}


    introduced_keys = sorted(key for key in new_config if key not in old_config)
    all_changed = sorted(
        key for key in set(old_config) & set(new_config)
        if old_config.get(key) != new_config.get(key)
    )
    legacy_changed = sorted(
        key for key in introduced_keys
        if key in LEGACY_CONFIG_DEFAULTS
        and _legacy_comparable(key, new_config.get(key))
        != _legacy_comparable(key, LEGACY_CONFIG_DEFAULTS[key])
    )
    if legacy_changed:
        old_config = dict(old_config)
        for key in legacy_changed:
            old_config[key] = LEGACY_CONFIG_DEFAULTS[key]
        introduced_keys = [key for key in introduced_keys if key not in legacy_changed]
        all_changed = sorted(set(all_changed) | set(legacy_changed))
    changed_policy_keys = [key for key in all_changed if key in RUN_POLICY_CONFIG_KEYS]
    changed_keys = [key for key in all_changed if key not in RUN_POLICY_CONFIG_KEYS]
    tiers = [t for t in (_config_key_stage_tier(k) for k in changed_keys) if t is not None]
    raw_changed = previous_payload.get("raw_files") != payload.get("raw_files")
    code_changed = previous_payload.get("code_files") != payload.get("code_files")
    first_tier = STAGE_TIER_PANEL if raw_changed else (min(tiers) if tiers else None)
    return {
        "changed_config_keys": changed_keys,
        "changed_run_policy_keys": changed_policy_keys,
        "settings_introduced_by_this_script_version": introduced_keys,
        "changed_config_details": {
            key: {"previous": old_config.get(key), "current": new_config.get(key)}
            for key in all_changed
        },
        "raw_files_changed": raw_changed,
        "code_files_changed": code_changed,
        "previous_code_files": previous_payload.get("code_files"),
        "first_stage_to_rebuild": first_tier,
        "first_stage_to_rebuild_label": STAGE_TIER_LABELS.get(first_tier) if first_tier is not None else None,
    }

def describe_signature_change(config) -> dict:
    config.ensure_dirs()
    payload = _run_signature_payload(config)
    signature_path = config.run_dir / "run_signature.json"
    if not signature_path.exists():
        return {
            "run_directory": str(config.run_dir),
            "previous_signature_found": False,
            "note": "No run_signature.json in this run directory; a run would start from the analysis panel.",
        }
    previous = json.loads(signature_path.read_text(encoding="utf-8"))
    report = _signature_change_report(previous.get("payload", {}) or {}, payload)
    canonical = json.dumps(payload, sort_keys=True, separators=(",", ":"))
    signature = hashlib.sha256(canonical.encode("utf-8")).hexdigest()
    report.update({
        "run_directory": str(config.run_dir),
        "previous_signature_found": True,
        "signature_unchanged": previous.get("signature") == signature,
        "protect_matching": bool(getattr(config, "protect_matching", False)),
        "would_be_refused_by_protect_matching": bool(
            report["first_stage_to_rebuild"] is not None
            and report["first_stage_to_rebuild"] <= STAGE_TIER_MATCHING
            and getattr(config, "protect_matching", False)
        ),
    })
    return report

def initialize_run(config, force: bool = False) -> Path:
    import shutil
    from datetime import datetime, timezone
    config.ensure_dirs()
    payload = _run_signature_payload(config)
    canonical = json.dumps(payload, sort_keys=True, separators=(",", ":"))
    signature = hashlib.sha256(canonical.encode("utf-8")).hexdigest()
    signature_path = config.run_dir / "run_signature.json"
    previous = None
    if signature_path.exists():
        previous = json.loads(signature_path.read_text(encoding="utf-8"))
    generated_dirs = (config.panels_dir, config.analysis_dir, config.diagnostics_dir, config.figures_dir)
    has_generated_outputs = any(path.exists() and any(path.iterdir()) for path in generated_dirs)
    changed = previous is not None and previous.get("signature") != signature
    untracked_existing = previous is None and has_generated_outputs
    lineage = list(previous.get("lineage", [])) if previous else []
    reuse_existing = bool(getattr(config, "reuse_existing_outputs", False))
    if untracked_existing and not force:
        raise RuntimeError(
            f"Refusing to reuse {config.run_dir} because untracked outputs already exist. "
            "Choose a new sample_tag or rerun with --force so stale files cannot be mixed."
        )
    if changed and force:
        _remove_outputs_from_stage_tier(config, STAGE_TIER_PANEL)
        lineage.append({
            "at_utc": datetime.now(timezone.utc).isoformat(),
            "previous_signature": previous.get("signature"),
            "action": "forced full rebuild (--force)",
        })
    elif changed and not reuse_existing:
        raise RuntimeError(
            f"Refusing to reuse {config.run_dir} because the run signature changed. "
            "Rerun with --reuse-existing to keep the stages whose inputs are unchanged, "
            "or with --force to rebuild everything, or choose a new sample_tag."
        )
    elif changed:
        report = _signature_change_report(previous.get("payload", {}) or {}, payload)
        first_tier = report["first_stage_to_rebuild"]
        if (
            first_tier is not None
            and first_tier <= STAGE_TIER_MATCHING
            and bool(getattr(config, "protect_matching", False))
        ):
            raise RuntimeError(
                f"Refusing to rebuild {config.run_dir} from the "
                f"'{STAGE_TIER_LABELS.get(first_tier)}' stage because protect_matching is True. "
                f"Changed settings: "
                f"{ {key: report['changed_config_details'][key] for key in report['changed_config_keys']} }; "
                f"raw files changed: "
                f"{report['raw_files_changed']}. Nothing was removed. Restore the previous values "
                "of those settings to keep the existing matching, or set protect_matching to False "
                "if re-matching is intended."
            )
        if first_tier is not None and first_tier <= STAGE_TIER_PANEL:
            reason = (
                "the raw input files changed" if report["raw_files_changed"]
                else f"panel-defining settings changed: {report['changed_config_keys']}"
            )
            raise RuntimeError(
                f"Refusing to reuse {config.run_dir} with --reuse-existing because {reason}; "
                "the existing analysis panel would be stale. Rerun with --force to rebuild "
                "everything, or choose a new sample_tag."
            )
        removed: list[str] = []
        if first_tier is None:
            log.info(
                "Run signature changed only in run-policy settings, newly introduced settings, "
                "or the script itself (policy keys: %s; introduced: %s; script changed: %s). "
                "Reusing every existing stage output.",
                report["changed_run_policy_keys"],
                report["settings_introduced_by_this_script_version"],
                report["code_files_changed"],
            )
        else:
            removed = _remove_outputs_from_stage_tier(config, first_tier)
            log.warning(
                "Run signature changed (keys: %s). Rebuilding from the '%s' stage onward; "
                "removed %d existing output(s), kept everything earlier in the pipeline.",
                report["changed_config_keys"], report["first_stage_to_rebuild_label"], len(removed),
            )
        lineage.append({
            "at_utc": datetime.now(timezone.utc).isoformat(),
            "previous_signature": previous.get("signature"),
            "action": "stage-aware reuse (--reuse-existing)",
            "removed_outputs": removed,
            **report,
        })
    signature_path.write_text(
        json.dumps({"signature": signature, "payload": payload, "lineage": lineage}, indent=2),
        encoding="utf-8",
    )
    return signature_path

from pathlib import Path
import logging

import polars as pl

log = logging.getLogger(__name__)

MSK_DIAGNOSIS_CODES_LEGACY = [20]
MENTAL_HEALTH_REHAB_CODES_LEGACY = [30]
PANEL_REHAB_CODE_MARKER = "analysis_panel_rehab_code_definition.json"
PANEL_RELABEL_BATCH_ROWS = 200_000

def _diagnosis_code_in(expression: pl.Expr, codes) -> pl.Expr:
    values = _normalize_diagnosis_codes(codes)
    return (
        expression.cast(pl.Utf8, strict=False)
        .cast(pl.Float64, strict=False)
        .cast(pl.Int64, strict=False)
        .is_in(values)
        .fill_null(False)
    )

def _rehab_code_definition(config: "PipelineConfig") -> dict:
    return {
        "msk_diagnosis_codes": _normalize_diagnosis_codes(config.msk_diagnosis_codes),
        "mental_health_diagnosis_codes": _normalize_diagnosis_codes(config.mental_health_diagnosis_codes),
    }

def _age_band(column: str = "age") -> pl.Expr:
    age = pl.col(column)
    return (
        pl.when(age.is_null()).then(None)
        .when(age < 20).then(pl.lit("<20"))
        .when(age < 25).then(pl.lit("20-24"))
        .when(age < 30).then(pl.lit("25-29"))
        .when(age < 35).then(pl.lit("30-34"))
        .when(age < 40).then(pl.lit("35-39"))
        .when(age < 45).then(pl.lit("40-44"))
        .when(age < 50).then(pl.lit("45-49"))
        .when(age < 55).then(pl.lit("50-54"))
        .when(age < 60).then(pl.lit("55-59"))
        .when(age < 65).then(pl.lit("60-64"))
        .when(age < 70).then(pl.lit("65-69"))
        .when(age < 75).then(pl.lit("70-74"))
        .when(age < 80).then(pl.lit("75-79"))
        .when(age < 85).then(pl.lit("80-84"))
        .when(age < 90).then(pl.lit("85-89"))
        .otherwise(pl.lit("90+"))
        .alias("age_band")
    )

def _occupation_major_group(column: str = "ttsc1_kldb1988") -> pl.Expr:
    code = pl.col(column).cast(pl.Int32, strict=False)
    padded = pl.when(code.is_not_null()).then(code.cast(pl.Utf8).str.zfill(4)).otherwise(None)
    return padded.str.slice(0, 1).alias("occ_l1")

def _optional_nulls(frame: pl.LazyFrame, requested: list[str], schema: dict[str, pl.DataType]) -> pl.LazyFrame:
    existing = set(frame.columns)
    expressions: list[pl.Expr] = []
    numeric_float = {
        "entgelt", "rtzb", "byvlgs", "bygmgs",
        "mcdams_succeed_1", "mcdams_succeed_2",
    }
    numeric_int = {
        "rtwf_jjjj", "ge", "divorcing", "is_first_marriage", "whot_bland", "whot_skt",
        "ttsc1_kldb1988",
        "mcdggr_succeed_1", "mcdggr_succeed_2",
    }
    for column in requested:
        if column in existing:
            continue
        if column in DATE_COLUMNS:
            dtype = pl.Date
        elif column in numeric_float:
            dtype = pl.Float64
        elif column in numeric_int:
            dtype = pl.Int32
        elif "iufzt" in column:
            dtype = pl.Utf8
        else:
            dtype = schema.get(column, pl.Utf8)
        expressions.append(pl.lit(None, dtype=dtype).alias(column))
    return frame.with_columns(expressions) if expressions else frame

def _incapacity_source(schema: dict[str, pl.DataType], slot: int) -> str | None:
    for candidate in INCAPACITY_CANDIDATES[slot]:
        if candidate in schema:
            return candidate
    return None

PANEL_BUCKET_TARGET_ROWS = 1_000_000
PANEL_READ_BATCH_ROWS = 2_000_000
PANEL_BUCKET_COMPRESSION = "lz4"
PANEL_ORDER_COLUMN = "_dedup_orig_row_order"

def _raw_row_count(files: list[str]) -> int:

    import pyarrow.parquet as pq
    return sum(int(pq.ParquetFile(file).metadata.num_rows) for file in files)

def _aligned_cast_expressions(file: str, columns: list[str], schema: dict) -> list[pl.Expr]:


    file_schema = pl.read_parquet_schema(file)
    expressions = []
    for column in columns:
        target = DTYPE_OVERRIDES.get(column, schema[column])
        if column in file_schema:
            expressions.append(pl.col(column).cast(target, strict=False).alias(column))
        else:
            expressions.append(pl.lit(None, dtype=target).alias(column))
    return expressions

def _bucket_raw_data(
    config: "PipelineConfig",
    found: list[str],
    schema: dict,
    buckets_dir: Path,
    n_buckets: int,
    seed: int,
) -> int:


    import shutil
    import time
    import pyarrow as pa
    import pyarrow.parquet as pq
    files = sorted(glob(config.raw_glob))
    if not files:
        raise FileNotFoundError(f"No parquet files matched {config.raw_glob!r}")
    shutil.rmtree(buckets_dir, ignore_errors=True)
    for bucket in range(n_buckets):
        (buckets_dir / f"b{bucket:05d}").mkdir(parents=True)
    total_rows = _raw_row_count(files)
    writers: dict[int, pq.ParquetWriter] = {}
    global_offset = 0
    time_read = time_transform = time_write = 0.0
    started = time.perf_counter()
    last_progress_log = started
    try:
        for file_index, file in enumerate(files):
            expressions = _aligned_cast_expressions(file, found, schema)
            file_schema = pl.read_parquet_schema(file)
            read_columns = [column for column in found if column in file_schema]
            reader = pq.ParquetFile(file)
            n_row_groups = reader.metadata.num_row_groups
            largest_row_group = max(
                (reader.metadata.row_group(i).num_rows for i in range(n_row_groups)), default=0
            )
            if largest_row_group > 4 * PANEL_READ_BATCH_ROWS:


                log.warning(
                    "  raw shard %s has a row group of %s rows (batch target %s): the first "
                    "batch of this shard will take proportionally longer and more memory.",
                    Path(file).name, f"{largest_row_group:,}", f"{PANEL_READ_BATCH_ROWS:,}",
                )
            t_mark = time.perf_counter()
            for batch in reader.iter_batches(batch_size=PANEL_READ_BATCH_ROWS, columns=read_columns):
                data = pl.from_arrow(pa.Table.from_batches([batch]))
                now = time.perf_counter()
                time_read += now - t_mark
                t_mark = now
                if data.height == 0:
                    continue
                data = (
                    data.select(expressions)
                    .with_row_index(PANEL_ORDER_COLUMN, offset=global_offset)
                    .with_columns(
                        (pl.col("simple_id").hash(seed=seed) % n_buckets)
                        .cast(pl.UInt32).alias("_bucket")
                    )
                )
                parts = data.partition_by(["_bucket"], as_dict=True)
                now = time.perf_counter()
                time_transform += now - t_mark
                t_mark = now
                for key, part in parts.items():
                    bucket = int(key[0] if isinstance(key, tuple) else key)
                    table = part.drop("_bucket").to_arrow()
                    writer = writers.get(bucket)
                    if writer is None:
                        writer = pq.ParquetWriter(
                            buckets_dir / f"b{bucket:05d}" / "rows.parquet",
                            table.schema,
                            compression=PANEL_BUCKET_COMPRESSION,
                            write_statistics=False,
                        )
                        writers[bucket] = writer
                    writer.write_table(table)
                now = time.perf_counter()
                time_write += now - t_mark
                t_mark = now
                global_offset += data.height
                if now - last_progress_log >= 60.0:
                    last_progress_log = now
                    elapsed = now - started
                    rate = global_offset / max(elapsed, 1e-9)
                    remaining = max(total_rows - global_offset, 0) / max(rate, 1e-9)
                    log.info(
                        "  bucketing progress: %s/%s rows (%.1f%%), %.0f rows/s, ~%.0f min left "
                        "[read %.0fs, transform %.0fs, write %.0fs]",
                        f"{global_offset:,}", f"{total_rows:,}", 100.0 * global_offset / max(total_rows, 1),
                        rate, remaining / 60.0, time_read, time_transform, time_write,
                    )
            log.info(
                "  bucketed raw shard %d/%d (%s rows so far; cumulative read %.0fs, transform %.0fs, write %.0fs)",
                file_index + 1, len(files), f"{global_offset:,}", time_read, time_transform, time_write,
            )
    finally:
        for writer in writers.values():
            writer.close()
    log.info(
        "Bucketing pass finished: %s rows into %d bucket files in %.1f min",
        f"{global_offset:,}", len(writers), (time.perf_counter() - started) / 60.0,
    )
    return global_offset

def _dedup_person_years(frame: pl.LazyFrame) -> pl.LazyFrame:


    if PANEL_ORDER_COLUMN not in frame.columns:
        frame = frame.with_row_index(PANEL_ORDER_COLUMN)
    value_columns = [c for c in frame.columns if c not in ("simple_id", "ja", PANEL_ORDER_COLUMN)]
    return (
        frame.with_columns(
            pl.sum_horizontal([pl.col(c).is_null().cast(pl.Int32) for c in value_columns])
            .alias("_dedup_n_missing_other_vars")
        )
        .sort(["simple_id", "ja", "_dedup_n_missing_other_vars", PANEL_ORDER_COLUMN])
        .unique(subset=["simple_id", "ja"], keep="first", maintain_order=True)
        .sort(PANEL_ORDER_COLUMN)
        .drop([PANEL_ORDER_COLUMN, "_dedup_n_missing_other_vars"])
    )

def _build_pre_history_chunk_frame(
    frame: pl.LazyFrame,
    config: "PipelineConfig",
    schema: dict,
    incapacity_1: str | None,
    incapacity_2: str | None,
    conflicted_ids: pl.LazyFrame,
) -> pl.LazyFrame:


    frame = frame.join(conflicted_ids, on="simple_id", how="anti")
    date_expressions = [normalize_date(column, schema[column]) for column in DATE_COLUMNS if column in schema]
    if date_expressions:
        frame = frame.with_columns(date_expressions)
    frame = frame.with_columns(
        pl.col("is_first_marriage").cast(pl.Int8, strict=False).alias("is_first_marriage")
    )
    if config.first_marriage_source == "is_first_marriage":
        frame = frame.with_columns([
            pl.when(pl.col("is_first_marriage") == 1)
            .then(pl.col("marriage_start")).otherwise(None)
            .alias("first_marriage_start"),
            pl.when(pl.col("is_first_marriage") == 1)
            .then(pl.coalesce([pl.col("court_decision"), pl.col("marriage_end")]))
            .otherwise(None).alias("first_marriage_end"),
        ])
    if incapacity_1:
        frame = frame.with_columns(pl.col(incapacity_1).cast(pl.Utf8, strict=False).alias("incapacity_months_cat_slot1_raw"))
    else:
        frame = frame.with_columns(pl.lit(None, dtype=pl.Utf8).alias("incapacity_months_cat_slot1_raw"))
    if incapacity_2:
        frame = frame.with_columns(pl.col(incapacity_2).cast(pl.Utf8, strict=False).alias("incapacity_months_cat_slot2_raw"))
    else:
        frame = frame.with_columns(pl.lit(None, dtype=pl.Utf8).alias("incapacity_months_cat_slot2_raw"))
    frame = frame.with_columns([
        pl.col("divorcing").fill_null(0).cast(pl.Int8, strict=False),
        (pl.col("ja") - pl.col("gbja")).cast(pl.Int16, strict=False).alias("age_raw"),
        pl.col("marriage_start").dt.year().cast(pl.Int32, strict=False).alias("marriage_start_year"),
        pl.col("first_marriage_start").dt.year().cast(pl.Int32, strict=False).alias("first_marriage_start_year"),
        pl.col("first_marriage_end").dt.year().cast(pl.Int32, strict=False).alias("first_marriage_end_year"),
        pl.coalesce([pl.col("court_decision"), pl.col("marriage_end")]).alias("marriage_end_proxy"),
        pl.col("fmsd").cast(pl.Int8, strict=False).alias("fmsd"),
    ])
    frame = frame.with_columns([
        pl.when(
            pl.col("rtwf_jjjj").is_not_null() & (pl.col("rtwf_jjjj") < pl.col("ja"))
        ).then(None).otherwise(pl.col("age_raw")).alias("age_raw"),
        pl.col("marriage_end_proxy").dt.year().cast(pl.Int32, strict=False).alias("marriage_end_proxy_year"),
    ])
    frame = frame.with_columns([
        pl.when(pl.col("age_raw").is_between(0, 125, closed="both"))
        .then(pl.col("age_raw")).otherwise(None).cast(pl.Int16).alias("age"),
        pl.when(
            pl.col("marriage_start_year").is_not_null()
            & (pl.col("marriage_start_year") <= pl.col("ja"))
            & (
                pl.col("marriage_end_proxy_year").is_null()
                | (pl.col("marriage_end_proxy_year") > pl.col("ja"))
            )
        ).then(1).otherwise(0).cast(pl.Int8).alias("is_observed_married_this_year"),
        pl.when(pl.col("marriage_start_year").is_not_null())
        .then(
            pl.when(
                pl.col("marriage_end_proxy_year").is_null()
                | (pl.col("marriage_end_proxy_year") > pl.col("ja"))
            ).then(pl.col("ja")).otherwise(pl.col("marriage_end_proxy_year"))
            - pl.col("marriage_start_year")
        )
        .otherwise(None)
        .clip(lower_bound=0)
        .cast(pl.Int16)
        .alias("marriage_duration_years"),
    ]).with_columns(_age_band("age"))
    if config.source_has_entgelt:
        income_status = (
            pl.when(pl.col("entgelt").is_not_null() & pl.col("rtzb").is_null())
            .then(pl.lit("earnings_only"))
            .when(pl.col("entgelt").is_null() & pl.col("rtzb").is_not_null())
            .then(pl.lit("pension_only"))
            .when(pl.col("entgelt").is_not_null() & pl.col("rtzb").is_not_null())
            .then(pl.lit("earnings_and_pension"))
            .otherwise(pl.lit("neither_observed"))
        )
        entgelt_value = pl.col("entgelt").fill_null(0).cast(pl.Float64, strict=False)
        entgelt_missing = pl.col("entgelt").is_null().cast(pl.Int8)
    else:
        income_status = pl.lit("not_constructible_without_entgelt")
        entgelt_value = pl.lit(None, dtype=pl.Float64)
        entgelt_missing = pl.lit(1, dtype=pl.Int8)
    frame = frame.with_columns([
        income_status.alias("income_source_status"),
        entgelt_value.alias("entgelt_value"),
        pl.col("rtzb").fill_null(0).cast(pl.Float64, strict=False).alias("rtzb_value"),
        entgelt_missing.alias("entgelt_missing"),
        pl.col("rtzb").is_null().cast(pl.Int8).alias("rtzb_missing"),
        pl.when(pl.col("rtzb").is_not_null())
        .then(pl.lit("pension_income_observed"))
        .otherwise(pl.lit("pension_income_not_observed"))
        .alias("pension_income_observation_status"),
        pl.col("byvlgs").cast(pl.Float64, strict=False).fill_null(0).alias("byvlgs_value"),
        pl.col("bygmgs").cast(pl.Float64, strict=False).fill_null(0).alias("bygmgs_value"),
        pl.col("byvlgs").cast(pl.Float64, strict=False).is_null().cast(pl.Int8).alias("byvlgs_missing"),
        pl.col("bygmgs").cast(pl.Float64, strict=False).is_null().cast(pl.Int8).alias("bygmgs_missing"),
        pl.col("ge").cast(pl.Utf8, strict=False).fill_null("__MISSING__").alias("ge_cat"),
        pl.col("fmsd").cast(pl.Utf8, strict=False).fill_null("__MISSING__").alias("fmsd_cat"),
        pl.col("whot_bland").cast(pl.Utf8, strict=False).fill_null("__MISSING__").alias("whot_bland_cat"),
        pl.col("whot_skt").cast(pl.Utf8, strict=False).fill_null("__MISSING__").alias("whot_skt_cat"),
        pl.lit(config.first_marriage_source).alias("first_marriage_definition_source"),
        pl.lit(config.data_profile).alias("data_profile"),
    ])
    rehab_exprs: list[pl.Expr] = []
    for slot in (1, 2):
        start = f"rehab_start_{slot}"
        seg_start = f"seg_start_rsd_{slot}"
        seg_end = f"seg_end_rsd_{slot}"
        diagnosis = f"mcdggr_succeed_{slot}"
        duration = f"mcdams_succeed_{slot}"
        rehab_exprs.extend([
            pl.when(pl.col(start).is_not_null() & (pl.col(start).dt.year() == pl.col("ja")))
            .then(1).otherwise(0).cast(pl.Int8).alias(f"rehab_start_slot{slot}"),
            pl.when(pl.col(start).is_not_null() & (pl.col(start).dt.year() == pl.col("ja")))
            .then(pl.col(diagnosis).cast(pl.Utf8, strict=False))
            .otherwise(None)
            .alias(f"rehab_diagnosis_code_slot{slot}_this_year"),
            pl.when(
                pl.col(start).is_not_null()
                & (pl.col(start).dt.year() == pl.col("ja"))
                & _diagnosis_code_in(pl.col(diagnosis), config.msk_diagnosis_codes)
            ).then(1).otherwise(0).cast(pl.Int8).alias(f"msk_start_slot{slot}"),
            pl.when(
                pl.col(start).is_not_null()
                & (pl.col(start).dt.year() == pl.col("ja"))
                & _diagnosis_code_in(pl.col(diagnosis), config.mental_health_diagnosis_codes)
            ).then(1).otherwise(0).cast(pl.Int8).alias(f"mental_health_start_slot{slot}"),
            pl.when(pl.col(duration).is_not_null())
            .then(pl.col(duration).cast(pl.Float64, strict=False))
            .when(pl.col(seg_start).is_not_null() & pl.col(seg_end).is_not_null())
            .then((pl.col(seg_end) - pl.col(seg_start)).dt.total_days() + 1)
            .otherwise(None).cast(pl.Float64).alias(f"rehab_duration_days_slot{slot}"),
        ])
    frame = frame.with_columns(rehab_exprs)
    frame = frame.with_columns([
        (pl.col("rehab_start_slot1") + pl.col("rehab_start_slot2")).cast(pl.Int16).alias("rehab_starts_this_year"),
        (pl.col("msk_start_slot1") + pl.col("msk_start_slot2")).cast(pl.Int16).alias("msk_starts_this_year"),
        (pl.col("mental_health_start_slot1") + pl.col("mental_health_start_slot2"))
        .cast(pl.Int16).alias("mental_health_rehab_starts_this_year"),
        pl.when(pl.col("msk_start_slot1") == 1).then(pl.col("rehab_duration_days_slot1")).otherwise(0).fill_null(0)
        .add(pl.when(pl.col("msk_start_slot2") == 1).then(pl.col("rehab_duration_days_slot2")).otherwise(0).fill_null(0))
        .alias("msk_duration_days_this_year"),
        pl.when(pl.col("msk_start_slot1") == 1)
        .then(pl.col("incapacity_months_cat_slot1_raw")).otherwise(None)
        .alias("msk_incapacity_months_cat_slot1_this_year"),
        pl.when(pl.col("msk_start_slot2") == 1)
        .then(pl.col("incapacity_months_cat_slot2_raw")).otherwise(None)
        .alias("msk_incapacity_months_cat_slot2_this_year"),
        (
            (pl.col("application_date_fail").is_not_null()
             & (pl.col("application_date_fail").dt.year() == pl.col("ja")))
            | (pl.col("decision_date_fail").is_not_null()
               & (pl.col("decision_date_fail").dt.year() == pl.col("ja")))
        ).cast(pl.Int8).alias("failed_app_this_year"),
        (
            (pl.col("application_date_withdrawn").is_not_null()
             & (pl.col("application_date_withdrawn").dt.year() == pl.col("ja")))
            | (pl.col("decision_date_withdrawn").is_not_null()
               & (pl.col("decision_date_withdrawn").dt.year() == pl.col("ja")))
        ).cast(pl.Int8).alias("withdrawn_app_this_year"),
        (
            (pl.col("application_date_forward").is_not_null()
             & (pl.col("application_date_forward").dt.year() == pl.col("ja")))
            | (pl.col("decision_date_forward").is_not_null()
               & (pl.col("decision_date_forward").dt.year() == pl.col("ja")))
        ).cast(pl.Int8).alias("forwarded_app_this_year"),
    ])
    frame = frame.with_columns([
        pl.coalesce([
            pl.col("msk_incapacity_months_cat_slot1_this_year"),
            pl.col("msk_incapacity_months_cat_slot2_this_year"),
        ]).alias("msk_incapacity_months_cat_this_year"),
        (pl.col("rehab_starts_this_year") > pl.col("msk_starts_this_year"))
        .cast(pl.Int8).alias("non_msk_rehab_this_year"),
        pl.max_horizontal("failed_app_this_year", "withdrawn_app_this_year", "forwarded_app_this_year")
        .cast(pl.Int8).alias("non_success_app_this_year"),
        (
            pl.col("failed_app_this_year")
            + pl.col("withdrawn_app_this_year")
            + pl.col("forwarded_app_this_year")
            + (pl.col("rehab_starts_this_year") > 0).cast(pl.Int8)
        ).cast(pl.Int16).alias("n_application_activity_types_this_year"),
    ])
    return frame

PRE_HISTORY_CHECKPOINT_COLUMNS = [
    "simple_id", "ja", "rtwf_jjjj", "ge_cat", "fmsd", "fmsd_cat", "age", "age_band", "divorcing",
    "marriage_start", "first_marriage_start", "first_marriage_end", "is_first_marriage",
    "first_marriage_definition_source", "data_profile",
    "marriage_start_year", "first_marriage_start_year", "first_marriage_end_year",
    "marriage_end_proxy_year", "is_observed_married_this_year",
    "marriage_duration_years", "entgelt_value", "rtzb_value",
    "entgelt_missing", "rtzb_missing", "income_source_status",
    "pension_income_observation_status",
    "byvlgs", "bygmgs", "byvlgs_value", "bygmgs_value", "byvlgs_missing", "bygmgs_missing",
    "whot_bland_cat", "whot_skt_cat",
    "ttsc1_kldb1988",
    "rehab_start_slot1", "rehab_start_slot2",
    "rehab_diagnosis_code_slot1_this_year", "rehab_diagnosis_code_slot2_this_year",
    "rehab_starts_this_year", "msk_starts_this_year", "mental_health_rehab_starts_this_year",
    "non_msk_rehab_this_year", "msk_duration_days_this_year",
    "failed_app_this_year", "withdrawn_app_this_year", "forwarded_app_this_year",
    "non_success_app_this_year", "n_application_activity_types_this_year",
    "msk_incapacity_months_cat_slot1_this_year",
    "msk_incapacity_months_cat_slot2_this_year",
    "msk_incapacity_months_cat_this_year",
]

def _apply_history_window_features(
    history: pl.LazyFrame,
    first_marriage_divorce_expr: pl.Expr,
) -> pl.LazyFrame:
    history = history.with_columns([
        pl.when(pl.col("divorcing") == 1).then(pl.col("ja")).otherwise(None)
        .min().over("simple_id").cast(pl.Int32).alias("first_divorce_year"),
        first_marriage_divorce_expr.cast(pl.Int8)
        .alias("divorce_from_first_marriage_this_year"),
        pl.col("divorcing").sum().over("simple_id").cast(pl.Int16)
        .alias("n_distinct_divorce_flag_years"),
        (pl.col("is_observed_married_this_year").cum_sum().over("simple_id") > 0)
        .cast(pl.Int8).alias("ever_observed_married_to_date"),
        pl.col("rehab_starts_this_year").cum_sum().over("simple_id").cast(pl.Int32).alias("cum_rehabs_by_year"),
        pl.col("msk_starts_this_year").cum_sum().over("simple_id").cast(pl.Int32).alias("cum_msk_rehabs_by_year"),
        pl.col("mental_health_rehab_starts_this_year").cum_sum().over("simple_id")
        .cast(pl.Int32).alias("cum_mental_health_rehabs_by_year"),
    ])
    history = history.with_columns([
        (pl.col("ja") - pl.col("first_divorce_year")).cast(pl.Int16).alias("divorce_event_time"),
        (pl.col("first_divorce_year").is_not_null() & (pl.col("ja") < pl.col("first_divorce_year")))
        .cast(pl.Int8).alias("pre_first_divorce"),
        (pl.col("first_divorce_year").is_not_null() & (pl.col("ja") >= pl.col("first_divorce_year")))
        .cast(pl.Int8).alias("post_first_divorce"),
        (pl.col("first_divorce_year").is_not_null() & (pl.col("ja") == pl.col("first_divorce_year")))
        .cast(pl.Int8).alias("first_divorce_this_year"),
        (
            (pl.col("first_divorce_year").is_not_null())
            & (pl.col("ja") == pl.col("first_divorce_year"))
            & (pl.col("divorce_from_first_marriage_this_year") == 1)
        ).cast(pl.Int8).alias("qualifying_first_divorce_this_year"),
        (pl.col("cum_rehabs_by_year") > 0).cast(pl.Int8).alias("ever_rehab_to_date"),
        (pl.col("cum_msk_rehabs_by_year") > 0).cast(pl.Int8).alias("ever_msk_rehab_to_date"),
        (pl.col("cum_mental_health_rehabs_by_year") > 0)
        .cast(pl.Int8).alias("ever_mental_health_rehab_to_date"),
        pl.when(pl.col("rehab_starts_this_year") > 0).then(pl.col("ja")).otherwise(None)
        .forward_fill().over("simple_id").alias("last_rehab_year"),
    ])
    history = history.with_columns([
        pl.when(pl.col("last_rehab_year").is_not_null())
        .then(pl.col("ja") - pl.col("last_rehab_year")).otherwise(None)
        .cast(pl.Int16).alias("years_since_last_rehab"),
        _occupation_major_group("ttsc1_kldb1988"),
    ])
    history = history.with_columns([
        pl.col("occ_l1").fill_null("__MISSING__").alias("occ_l1_cat"),
    ])
    return history

def _process_panel_bucket(
    bucket_dir: Path,
    config: "PipelineConfig",
    requested: list[str],
    schema: dict,
    incapacity_1: str | None,
    incapacity_2: str | None,
    first_marriage_divorce_expr: pl.Expr,
    final_columns: list[str],
) -> tuple[pl.DataFrame | None, dict]:


    files = sorted(glob(str(bucket_dir / "*.parquet")))
    empty = {
        "duplicate_keys": None, "death_conflicts": None,
        "n_persons": 0, "n_conflicted": 0, "n_conflicted_divorcing": 0,
        "n_retained": 0, "n_retained_divorcing": 0,
    }
    if not files:
        return None, empty
    raw = pl.scan_parquet(files)
    raw = _optional_nulls(raw, requested, schema)
    duplicate_keys = (
        raw.group_by(["simple_id", "ja"])
        .agg(pl.len().alias("n_rows"))
        .filter(pl.col("n_rows") > 1)
        .pipe(_safe_collect)
    )


    frame = _safe_collect(_dedup_person_years(raw)).lazy()
    death_conflicts = (
        frame.filter(pl.col("rtwf_jjjj").is_not_null())
        .group_by("simple_id")
        .agg([
            pl.col("rtwf_jjjj").n_unique().alias("n_distinct_death_years"),
            pl.col("rtwf_jjjj").unique().sort().alias("observed_death_years"),
        ])
        .filter(pl.col("n_distinct_death_years") > 1)
        .pipe(_safe_collect)
    )
    conflicted_ids = death_conflicts.select("simple_id")
    person_flags = (
        frame.group_by("simple_id")
        .agg(pl.col("divorcing").fill_null(0).max().alias("any_divorcing"))
        .pipe(_safe_collect)
        .with_columns(pl.col("simple_id").is_in(conflicted_ids.get_column("simple_id")).alias("_conflicted"))
    )
    stats = {
        "duplicate_keys": duplicate_keys,
        "death_conflicts": death_conflicts,
        "n_persons": person_flags.height,
        "n_conflicted": int(person_flags.get_column("_conflicted").sum()),
        "n_conflicted_divorcing": int(person_flags.filter(pl.col("_conflicted")).get_column("any_divorcing").sum()),
        "n_retained": int((~person_flags.get_column("_conflicted")).sum()),
        "n_retained_divorcing": int(person_flags.filter(~pl.col("_conflicted")).get_column("any_divorcing").sum()),
    }
    chunk = _build_pre_history_chunk_frame(
        frame, config, schema, incapacity_1, incapacity_2, conflicted_ids.lazy(),
    )
    chunk = chunk.select(PRE_HISTORY_CHECKPOINT_COLUMNS).sort(["simple_id", "ja"])
    chunk = _apply_history_window_features(chunk, first_marriage_divorce_expr).select(final_columns)


    return _safe_collect(chunk), stats

def _write_panel_diagnostics(config: "PipelineConfig", bucket_stats: list[dict]) -> None:
    duplicate_frames = [s["duplicate_keys"] for s in bucket_stats if s["duplicate_keys"] is not None and s["duplicate_keys"].height > 0]
    if duplicate_frames:
        duplicate_keys = pl.concat(duplicate_frames, how="vertical")
        n_duplicate_keys = duplicate_keys.height
        n_excess_rows = int((duplicate_keys.get_column("n_rows") - 1).sum())
        duplicate_path = config.diagnostics_dir / "duplicate_person_year_keys.csv"
        duplicate_keys.sort("n_rows", descending=True).limit(100_000).write_csv(duplicate_path)
        log.warning(
            "Found %d duplicate (simple_id, ja) keys (%d excess rows) in the processed "
            "input. See %s. Resolving by keeping the least-missing row per key; see "
            "duplicate_person_year_keys_resolution.json for the exact rule and counts.",
            n_duplicate_keys, n_excess_rows, duplicate_path,
        )
        (config.diagnostics_dir / "duplicate_person_year_keys_resolution.json").write_text(
            json.dumps(
                {
                    "n_duplicate_person_year_keys": n_duplicate_keys,
                    "n_excess_rows_dropped": n_excess_rows,
                    "reconciliation_rule": (
                        "Within each (simple_id, ja) group, keep the row with the fewest "
                        "null values across all other available columns; ties broken by "
                        "original row order (first-encountered row wins), not at random."
                    ),
                },
                indent=2,
            ),
            encoding="utf-8",
        )
    conflict_frames = [s["death_conflicts"] for s in bucket_stats if s["death_conflicts"] is not None and s["death_conflicts"].height > 0]
    if conflict_frames:
        death_year_conflicts = pl.concat(conflict_frames, how="vertical")
        n_death_conflicts = death_year_conflicts.height
        total_ids = sum(s["n_persons"] for s in bucket_stats)
        n_conflicted = sum(s["n_conflicted"] for s in bucket_stats)
        n_retained = sum(s["n_retained"] for s in bucket_stats)
        excluded_divorcing_share = sum(s["n_conflicted_divorcing"] for s in bucket_stats) / max(n_conflicted, 1)
        retained_divorcing_share = sum(s["n_retained_divorcing"] for s in bucket_stats) / max(n_retained, 1)
        conflict_path = config.diagnostics_dir / "conflicting_person_death_years.csv"
        (
            death_year_conflicts.limit(100_000)
            .with_columns(pl.col("observed_death_years").cast(pl.List(pl.Utf8)).list.join(", "))
            .write_csv(conflict_path)
        )
        log.warning(
            "Found %d simple_ids (%.2f%% of %d total) with conflicting non-null "
            "rtwf_jjjj (death year) values. Excluding these people entirely -- see %s "
            "and conflicting_person_death_years_resolution.json. divorcing-flag share: "
            "excluded=%.4f vs retained=%.4f (a large gap here means the exclusion is not "
            "a free lunch even at this share of the sample).",
            n_death_conflicts, 100.0 * n_death_conflicts / max(total_ids, 1), total_ids,
            conflict_path, excluded_divorcing_share, retained_divorcing_share,
        )
        (config.diagnostics_dir / "conflicting_person_death_years_resolution.json").write_text(
            json.dumps(
                {
                    "n_affected_simple_ids": n_death_conflicts,
                    "total_simple_ids": total_ids,
                    "affected_share": n_death_conflicts / max(total_ids, 1),
                    "resolution": "excluded (dropped entirely from the analysis panel)",
                    "rationale": (
                        "rtwf_jjjj is the terminal outcome (mortality), not a covariate; "
                        "the pipeline will not guess which conflicting value is correct. "
                        "Excluding the affected person's full history (not just nulling "
                        "the field) avoids a partially-defined death year feeding "
                        "risk-set eligibility and age-masking logic elsewhere in the file."
                    ),
                    "identification_check": {
                        "description": (
                            "Share of excluded vs. retained simple_ids with at least one "
                            "divorcing==1 person-year row, as a crude check for whether "
                            "exclusion is differential by (proxy-)treatment status. If "
                            "these differ substantially, exclusion may not be ignorable "
                            "and should be reported as a limitation, not assumed away."
                        ),
                        "excluded_share_with_divorcing_flag": excluded_divorcing_share,
                        "retained_share_with_divorcing_flag": retained_divorcing_share,
                    },
                },
                indent=2,
            ),
            encoding="utf-8",
        )

def write_analysis_panel_single_pass(
    config: "PipelineConfig",
    found: list[str],
    requested: list[str],
    schema: dict,
    incapacity_1: str | None,
    incapacity_2: str | None,
    first_marriage_divorce_expr: pl.Expr,
    final_columns: list[str],
    output: Path,
    n_buckets: int | None = None,
    seed: int = 42,
) -> None:


    import shutil
    import pyarrow.parquet as pq
    files = sorted(glob(config.raw_glob))
    total_rows = _raw_row_count(files)
    if n_buckets is None:
        n_buckets = max(1, -(-total_rows // PANEL_BUCKET_TARGET_ROWS))
    buckets_dir = output.parent / f"_{output.stem}_buckets"
    log.info("Bucketing %s raw rows into %d person-hash buckets", f"{total_rows:,}", n_buckets)
    _bucket_raw_data(config, found, schema, buckets_dir, n_buckets, seed)
    output.parent.mkdir(parents=True, exist_ok=True)
    temporary = output.with_suffix(output.suffix + ".tmp")
    temporary.unlink(missing_ok=True)
    bucket_stats: list[dict] = []
    writer = None
    try:
        for bucket in range(n_buckets):
            bucket_dir = buckets_dir / f"b{bucket:05d}"
            part, stats = _process_panel_bucket(
                bucket_dir, config, requested, schema, incapacity_1, incapacity_2,
                first_marriage_divorce_expr, final_columns,
            )
            bucket_stats.append(stats)
            if part is not None and part.height > 0:
                table = part.to_arrow()
                if writer is None:
                    writer = pq.ParquetWriter(
                        temporary, table.schema, compression="zstd", compression_level=3,
                        write_statistics=True,
                    )
                writer.write_table(table, row_group_size=config.checkpoint_row_group_size)
            shutil.rmtree(bucket_dir, ignore_errors=True)
            log.info("  final-panel bucket %d/%d written", bucket + 1, n_buckets)
    finally:
        if writer is not None:
            writer.close()
    if writer is None:


        temporary.unlink(missing_ok=True)
        raise RuntimeError(
            "No rows survived the analysis-panel build across any bucket; refusing to "
            "write an empty panel. Check diagnostics/source_schema_report.json and the "
            "duplicate/death-year-conflict diagnostics."
        )
    _write_panel_diagnostics(config, bucket_stats)
    temporary.replace(output)
    shutil.rmtree(buckets_dir, ignore_errors=True)

def build_analysis_panel(config: PipelineConfig, force: bool = False) -> Path:
    config.validate()
    config.ensure_dirs()
    output = config.panels_dir / "analysis_panel.parquet"
    manifest = config.run_dir / "run_manifest.json"
    if output.exists() and not force:
        log.info("[skip] analysis panel exists: %s", output)
        return output
    schema = schema_union(config.raw_glob)
    incapacity_1 = _incapacity_source(schema, 1)
    incapacity_2 = _incapacity_source(schema, 2)
    requested = CORE_RAW_COLUMNS.copy()
    requested += [name for name in (incapacity_1, incapacity_2) if name]
    found = present_columns(schema, requested)
    required_identifiers = {
        "simple_id", "ja", "gbja", "divorcing", "fmsd", "marriage_start",
    }
    if config.first_marriage_source == "date_fields":
        required_identifiers.add("first_marriage_start")
    else:
        required_identifiers.add("is_first_marriage")
    if config.source_has_entgelt:
        required_identifiers.add("entgelt")
    missing_required = sorted(required_identifiers - set(found))
    schema_report = {
        "data_profile": config.data_profile,
        "first_marriage_source": config.first_marriage_source,
        "source_has_entgelt": config.source_has_entgelt,
        "required_columns": sorted(required_identifiers),
        "missing_required_columns": missing_required,
        "optional_canonical_columns_absent": sorted(set(requested) - set(found)),
        "playdata_only_columns_detected": sorted(
            set(schema) & {
                "is_first_marriage", "rtbt", "bzgs", "bzegptgs", "byfhzt",
                "byfhegptgs", "auazgs", "ajazgs", "whot_ow",
                "spell_no_rsd_1", "spell_no_rsd_2",
            }
        ),
    }
    (config.diagnostics_dir / "source_schema_report.json").write_text(
        json.dumps(schema_report, indent=2), encoding="utf-8"
    )
    if missing_required:
        raise KeyError(
            "Raw data are missing required columns for the selected source profile: "
            f"{missing_required}. See source_schema_report.json."
        )
    if config.first_marriage_source == "date_fields":
        first_marriage_divorce_expr = (
            (pl.col("divorcing") == 1)
            & pl.col("marriage_start").is_not_null()
            & pl.col("first_marriage_start").is_not_null()
            & (pl.col("marriage_start") == pl.col("first_marriage_start"))
        )
    else:
        first_marriage_divorce_expr = (
            (pl.col("divorcing") == 1) & (pl.col("is_first_marriage") == 1)
        )
    final_columns = [
        "simple_id", "ja", "rtwf_jjjj", "age", "age_band", "ge_cat", "fmsd", "fmsd_cat",
        "divorcing", "first_divorce_year", "n_distinct_divorce_flag_years",
        "divorce_event_time", "pre_first_divorce", "post_first_divorce", "first_divorce_this_year",
        "divorce_from_first_marriage_this_year", "qualifying_first_divorce_this_year",
        "marriage_start", "first_marriage_start", "first_marriage_end", "is_first_marriage",
        "first_marriage_definition_source", "data_profile",
        "marriage_start_year", "first_marriage_start_year", "first_marriage_end_year",
        "marriage_end_proxy_year", "marriage_duration_years",
        "is_observed_married_this_year", "ever_observed_married_to_date",
        "rehab_start_slot1", "rehab_start_slot2",
        "rehab_diagnosis_code_slot1_this_year", "rehab_diagnosis_code_slot2_this_year",
        "rehab_starts_this_year", "msk_starts_this_year", "mental_health_rehab_starts_this_year",
        "non_msk_rehab_this_year", "msk_duration_days_this_year",
        "cum_rehabs_by_year", "cum_msk_rehabs_by_year", "cum_mental_health_rehabs_by_year",
        "ever_rehab_to_date", "ever_msk_rehab_to_date", "ever_mental_health_rehab_to_date",
        "last_rehab_year", "years_since_last_rehab",
        "failed_app_this_year", "withdrawn_app_this_year", "forwarded_app_this_year",
        "non_success_app_this_year", "n_application_activity_types_this_year",
        "entgelt_value", "rtzb_value", "entgelt_missing", "rtzb_missing",
        "income_source_status", "pension_income_observation_status", "byvlgs", "bygmgs",
        "byvlgs_value", "bygmgs_value", "byvlgs_missing", "bygmgs_missing",
        "whot_bland_cat", "whot_skt_cat", "occ_l1_cat",
        "msk_incapacity_months_cat_slot1_this_year",
        "msk_incapacity_months_cat_slot2_this_year",
        "msk_incapacity_months_cat_this_year",
    ]
    log.info("Writing final analysis panel (single raw pass, person-hash buckets)")
    write_analysis_panel_single_pass(
        config, found, requested, schema, incapacity_1, incapacity_2,
        first_marriage_divorce_expr, final_columns, output, seed=config.seed,
    )
    log.info("Final analysis panel written")
    write_manifest(config, found, final_columns, manifest)
    _write_rehab_code_marker(config, output, {"source": "panel_build_from_raw"})
    log.info("Built analysis panel: %s", output)
    return output


def _rehab_code_marker_path(panel_path: str | Path) -> Path:
    return Path(panel_path).parent / PANEL_REHAB_CODE_MARKER

def _read_rehab_code_marker(panel_path: str | Path) -> dict | None:
    path = _rehab_code_marker_path(panel_path)
    if not path.exists():
        return None
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return None
    return payload if isinstance(payload, dict) else None

def _write_rehab_code_marker(config: "PipelineConfig", panel_path: str | Path, extra: dict | None = None) -> Path:
    from datetime import datetime, timezone
    panel_path = Path(panel_path)
    path = _rehab_code_marker_path(panel_path)
    payload = {
        "applied": _rehab_code_definition(config),
        "legacy_definition_before_this_script": {
            "msk_diagnosis_codes": list(MSK_DIAGNOSIS_CODES_LEGACY),
            "mental_health_diagnosis_codes": list(MENTAL_HEALTH_REHAB_CODES_LEGACY),
        },
        "panel": {
            "path": str(panel_path),
            "size": int(panel_path.stat().st_size),
            "mtime": float(panel_path.stat().st_mtime),
        },
        "written_utc": datetime.now(timezone.utc).isoformat(),
        "columns_recomputed_by_relabel": [
            "msk_starts_this_year", "mental_health_rehab_starts_this_year",
            "non_msk_rehab_this_year", "cum_msk_rehabs_by_year",
            "cum_mental_health_rehabs_by_year", "ever_msk_rehab_to_date",
            "ever_mental_health_rehab_to_date",
        ],
        "columns_not_recomputable_from_the_panel": [
            "msk_duration_days_this_year", "msk_incapacity_months_cat_slot1_this_year",
            "msk_incapacity_months_cat_slot2_this_year", "msk_incapacity_months_cat_this_year",
        ],
        **(extra or {}),
    }
    path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    return path

def _rehab_code_relabel_stages(config: "PipelineConfig", columns: set[str]) -> list[list[pl.Expr]]:
    def starts(codes) -> pl.Expr:
        total = None
        for slot in (1, 2):
            flag = (
                (pl.col(f"rehab_start_slot{slot}") == 1)
                & _diagnosis_code_in(pl.col(f"rehab_diagnosis_code_slot{slot}_this_year"), codes)
            ).cast(pl.Int16)
            total = flag if total is None else total + flag
        return total.cast(pl.Int16)
    first: list[pl.Expr] = []
    if "msk_starts_this_year" in columns:
        first.append(starts(config.msk_diagnosis_codes).alias("msk_starts_this_year"))
    if "mental_health_rehab_starts_this_year" in columns:
        first.append(starts(config.mental_health_diagnosis_codes).alias("mental_health_rehab_starts_this_year"))
    second: list[pl.Expr] = []
    if "non_msk_rehab_this_year" in columns:
        second.append(
            (pl.col("rehab_starts_this_year") > pl.col("msk_starts_this_year"))
            .cast(pl.Int8).alias("non_msk_rehab_this_year")
        )
    if "cum_msk_rehabs_by_year" in columns:
        second.append(
            pl.col("msk_starts_this_year").cum_sum().over("simple_id")
            .cast(pl.Int32).alias("cum_msk_rehabs_by_year")
        )
    if "cum_mental_health_rehabs_by_year" in columns:
        second.append(
            pl.col("mental_health_rehab_starts_this_year").cum_sum().over("simple_id")
            .cast(pl.Int32).alias("cum_mental_health_rehabs_by_year")
        )
    third: list[pl.Expr] = []
    if "ever_msk_rehab_to_date" in columns and "cum_msk_rehabs_by_year" in columns:
        third.append((pl.col("cum_msk_rehabs_by_year") > 0).cast(pl.Int8).alias("ever_msk_rehab_to_date"))
    if "ever_mental_health_rehab_to_date" in columns and "cum_mental_health_rehabs_by_year" in columns:
        third.append(
            (pl.col("cum_mental_health_rehabs_by_year") > 0).cast(pl.Int8)
            .alias("ever_mental_health_rehab_to_date")
        )
    return [stage for stage in (first, second, third) if stage]

def _relabel_year_counts(frame: pl.DataFrame) -> pl.DataFrame:
    return frame.group_by("ja").agg([
        pl.len().alias("person_year_rows"),
        pl.col("rehab_starts_this_year").fill_null(0).cast(pl.Int64).sum().alias("rehab_starts"),
        pl.col("msk_starts_this_year").fill_null(0).cast(pl.Int64).sum().alias("msk_starts"),
        pl.col("mental_health_rehab_starts_this_year").fill_null(0).cast(pl.Int64).sum()
        .alias("mental_health_starts"),
    ])

def _assert_person_contiguous(chunk: pl.DataFrame, seen_carry_ids: set) -> None:
    ids = chunk.get_column("simple_id")
    runs = int((ids != ids.shift(1)).fill_null(True).sum())
    if runs != ids.n_unique():
        raise RuntimeError(
            "The analysis panel is not stored with each person's rows contiguous, so the "
            "memory-bounded relabel pass cannot recompute cumulative rehabilitation columns "
            "safely. Rebuild the panel with --force instead."
        )
    if seen_carry_ids:
        overlap = int(ids.is_in(list(seen_carry_ids)).sum())
        if overlap:
            raise RuntimeError(
                "A person's rows reappear after their block ended; the analysis panel is not "
                "person-contiguous. Rebuild the panel with --force instead of relabelling in place."
            )

def relabel_panel_rehab_codes(
    config: "PipelineConfig",
    panel_path: str | Path,
    batch_rows: int | None = None,
) -> Path:
    import pyarrow as pa
    import pyarrow.parquet as pq
    panel_path = Path(panel_path)
    if not panel_path.exists():
        raise FileNotFoundError(panel_path)
    wanted = _rehab_code_definition(config)
    marker = _read_rehab_code_marker(panel_path)
    if marker is not None and isinstance(marker.get("applied"), dict):
        applied = {
            "msk_diagnosis_codes": _normalize_diagnosis_codes(marker["applied"].get("msk_diagnosis_codes")),
            "mental_health_diagnosis_codes": _normalize_diagnosis_codes(
                marker["applied"].get("mental_health_diagnosis_codes")
            ),
        }
        assumed = False
    else:
        applied = {
            "msk_diagnosis_codes": list(MSK_DIAGNOSIS_CODES_LEGACY),
            "mental_health_diagnosis_codes": list(MENTAL_HEALTH_REHAB_CODES_LEGACY),
        }
        assumed = True
    if applied == wanted:
        if marker is None:
            _write_rehab_code_marker(config, panel_path, {"source": "existing panel matches the configured definition"})
        log.info("[skip] analysis panel already uses rehabilitation code definition %s", wanted)
        return panel_path
    log.info(
        "Relabelling rehabilitation diagnosis codes in %s: %s -> %s%s",
        panel_path, applied, wanted,
        " (previous definition assumed from the pre-260914 script)" if assumed else "",
    )
    source_handle = open(panel_path, "rb")
    reader = pq.ParquetFile(source_handle)
    columns = set(reader.schema_arrow.names)
    required = {
        "simple_id", "ja", "rehab_start_slot1", "rehab_start_slot2",
        "rehab_diagnosis_code_slot1_this_year", "rehab_diagnosis_code_slot2_this_year",
        "rehab_starts_this_year", "msk_starts_this_year", "mental_health_rehab_starts_this_year",
    }
    missing = sorted(required - columns)
    if missing:
        source_handle.close()
        raise KeyError(
            f"The analysis panel lacks {missing}; it predates the per-slot diagnosis code columns "
            "and must be rebuilt with --force before the code definition can change."
        )
    original_rows = int(reader.metadata.num_rows)
    stages = _rehab_code_relabel_stages(config, columns)
    batch_rows = int(batch_rows or PANEL_RELABEL_BATCH_ROWS)
    temporary = panel_path.with_suffix(panel_path.suffix + ".relabel.tmp")
    temporary.unlink(missing_ok=True)
    before_parts: list[pl.DataFrame] = []
    after_parts: list[pl.DataFrame] = []
    writer = None
    writer_schema = None
    carry: pl.DataFrame | None = None
    seen_carry_ids: set = set()
    previous_last_id = None
    rows_written = 0
    started = time.perf_counter()
    last_log = started
    def process(frame: pl.DataFrame) -> pl.DataFrame:
        before_parts.append(_relabel_year_counts(frame))
        frame = frame.sort(["simple_id", "ja"])
        for stage in stages:
            frame = frame.with_columns(stage)
        after_parts.append(_relabel_year_counts(frame))
        return frame
    def write(frame: pl.DataFrame) -> None:
        nonlocal writer, writer_schema, rows_written
        table = frame.to_arrow()
        if writer is None:
            writer_schema = table.schema
            writer = pq.ParquetWriter(
                temporary, writer_schema, compression="zstd", compression_level=3,
                write_statistics=True,
            )
        elif not table.schema.equals(writer_schema):
            table = table.cast(writer_schema)
        writer.write_table(table, row_group_size=config.checkpoint_row_group_size)
        rows_written += table.num_rows
    try:
        for batch in reader.iter_batches(batch_size=batch_rows):
            chunk = pl.from_arrow(pa.Table.from_batches([batch]))
            if not isinstance(chunk, pl.DataFrame):
                chunk = pl.DataFrame(chunk)
            if carry is not None and carry.height:
                chunk = pl.concat([carry, chunk], how="vertical")
            if chunk.height == 0:
                continue
            _assert_person_contiguous(chunk, seen_carry_ids)
            last_id = chunk.get_column("simple_id")[-1]
            head = chunk.filter(pl.col("simple_id") != last_id)
            carry = chunk.filter(pl.col("simple_id") == last_id)
            if previous_last_id is not None and previous_last_id != last_id:
                seen_carry_ids.add(previous_last_id)
            previous_last_id = last_id
            if head.height:
                write(process(head))
            now = time.perf_counter()
            if now - last_log >= 60:
                log.info("  relabel pass: %s rows written (%.0f rows/s)", f"{rows_written:,}", rows_written / max(now - started, 1e-9))
                last_log = now
        if carry is not None and carry.height:
            write(process(carry))
    finally:
        if writer is not None:
            writer.close()
        source_handle.close()
    if writer is None:
        temporary.unlink(missing_ok=True)
        raise RuntimeError("The analysis panel produced no rows during the relabel pass; refusing to replace it.")
    if rows_written != original_rows:
        temporary.unlink(missing_ok=True)
        raise RuntimeError(
            f"Relabel pass wrote {rows_written:,} rows but the panel holds {original_rows:,}; "
            "refusing to replace the panel."
        )
    temporary.replace(panel_path)
    before = pl.concat(before_parts, how="vertical").group_by("ja").agg(pl.all().sum()).sort("ja")
    after = pl.concat(after_parts, how="vertical").group_by("ja").agg(pl.all().sum()).sort("ja")
    audit = (
        before.rename({
            "msk_starts": "msk_starts_previous_definition",
            "mental_health_starts": "mental_health_starts_previous_definition",
        })
        .join(
            after.select([
                "ja",
                pl.col("msk_starts").alias("msk_starts_new_definition"),
                pl.col("mental_health_starts").alias("mental_health_starts_new_definition"),
            ]),
            on="ja", how="left",
        )
        .with_columns([
            (pl.col("msk_starts_new_definition") / pl.col("rehab_starts")).alias("msk_share_new_definition"),
            (pl.col("msk_starts_previous_definition") / pl.col("rehab_starts")).alias("msk_share_previous_definition"),
        ])
        .sort("ja")
    )
    config.ensure_dirs()
    audit_path = config.diagnostics_dir / "rehab_code_relabel_audit_by_year.csv"
    audit.write_csv(audit_path)
    totals = {
        "person_year_rows": int(rows_written),
        "msk_starts_previous_definition": int(audit.get_column("msk_starts_previous_definition").sum()),
        "msk_starts_new_definition": int(audit.get_column("msk_starts_new_definition").sum()),
        "mental_health_starts_previous_definition": int(audit.get_column("mental_health_starts_previous_definition").sum()),
        "mental_health_starts_new_definition": int(audit.get_column("mental_health_starts_new_definition").sum()),
        "elapsed_seconds": round(time.perf_counter() - started, 1),
        "audit_by_year": str(audit_path),
    }
    _write_rehab_code_marker(config, panel_path, {
        "source": "in_place_relabel",
        "previous_definition": applied,
        "previous_definition_assumed": assumed,
        "relabel_totals": totals,
    })
    log.info(
        "Relabelled analysis panel in %.0fs: MSK starts %s -> %s, mental-health starts %s -> %s",
        totals["elapsed_seconds"],
        f"{totals['msk_starts_previous_definition']:,}", f"{totals['msk_starts_new_definition']:,}",
        f"{totals['mental_health_starts_previous_definition']:,}",
        f"{totals['mental_health_starts_new_definition']:,}",
    )
    return panel_path

def audit_matched_sample_rehab_definition(
    config: "PipelineConfig",
    panel_path: str | Path,
    matches_path: str | Path,
    force: bool = False,
) -> Path:
    spec = f"{config.control_pool}_lag{config.lag_depth}"
    output = config.diagnostics_dir / f"rehab_code_definition_eligibility_audit_{spec}.json"
    if output.exists() and not force:
        return output
    assignment = _assignment_frame(matches_path)
    msk_rows = (
        pl.scan_parquet(panel_path)
        .select(["simple_id", "ja", "msk_starts_this_year"])
        .filter(pl.col("msk_starts_this_year").fill_null(0) > 0)
    )
    flags = (
        assignment.join(msk_rows, on="simple_id", how="left")
        .group_by(["simple_id", "t0", "match_group", "treated"])
        .agg([
            (pl.col("ja").is_not_null() & (pl.col("ja") < pl.col("t0"))).any().alias("msk_before_t0"),
            (pl.col("ja").is_not_null() & (pl.col("ja") == pl.col("t0"))).any().alias("msk_in_t0"),
        ])
    )
    by_role = (
        flags.group_by("treated")
        .agg([
            pl.len().alias("matched_people"),
            pl.col("msk_before_t0").sum().alias("people_with_msk_before_t0_under_current_definition"),
            pl.col("msk_in_t0").sum().alias("people_with_msk_in_t0_under_current_definition"),
            (pl.col("msk_before_t0") | pl.col("msk_in_t0")).sum()
            .alias("people_who_would_now_fail_eligibility"),
        ])
        .sort("treated")
        .pipe(_safe_collect)
    )
    groups = (
        flags.filter(pl.col("msk_before_t0") | pl.col("msk_in_t0"))
        .select(pl.col("match_group").n_unique().alias("n"))
        .pipe(_safe_collect)
        .item()
    )
    payload = {
        "definition_in_force_for_outcomes": _rehab_code_definition(config),
        "definition_used_when_eligibility_was_applied": _riskset_rehab_code_definition(config),
        "eligibility_rule": (
            "Matched individuals were required to have no musculoskeletal rehabilitation through "
            "t0 under the definition in force when the risk sets and matching were built. This audit "
            "counts how many matched individuals would fail that rule under the definition now used "
            "for outcomes. Matching is not redone for these people; the count is reported so the gap "
            "can be stated."
        ),
        "by_role": by_role.to_dicts(),
        "matched_sets_with_any_member_affected": int(groups or 0),
        "matched_sets_total": int(
            _safe_collect(assignment.select(pl.col("match_group").n_unique())).item()
        ),
    }
    output.write_text(json.dumps(payload, indent=2, default=_json_default), encoding="utf-8")
    return output

from pathlib import Path
import logging

import polars as pl

log = logging.getLogger(__name__)

BASELINE_COLUMNS = [
    "age", "age_band", "ge_cat", "fmsd_cat",
    "cum_rehabs_by_year", "years_since_last_rehab", "ever_rehab_to_date",
    "cum_mental_health_rehabs_by_year", "ever_mental_health_rehab_to_date",
    "ever_msk_rehab_to_date", "non_success_app_this_year", "non_msk_rehab_this_year",
    "entgelt_value", "rtzb_value", "income_source_status",
    "byvlgs_value", "bygmgs_value", "byvlgs_missing", "bygmgs_missing",
    "whot_bland_cat", "whot_skt_cat", "occ_l1_cat",
]
TREND_COLUMNS = [
    "entgelt_value", "rtzb_value", "income_source_status",
    "non_success_app_this_year", "rehab_starts_this_year",
]

def _count(frame: pl.LazyFrame) -> tuple[int, int]:
    result = frame.select([
        pl.len().alias("n_rows"),
        pl.col("simple_id").n_unique().alias("n_persons"),
    ]).pipe(_safe_collect).row(0)
    return int(result[0]), int(result[1])

def _record(audit: list[dict], group: str, stage: str, frame: pl.LazyFrame, previous_rows: int | None) -> int:
    rows, persons = _count(frame)
    audit.append({
        "group": group,
        "stage": stage,
        "n_rows": rows,
        "n_persons": persons,
        "removed_since_previous": None if previous_rows is None else previous_rows - rows,
    })
    return rows

def _lag_frame(panel: pl.LazyFrame, depth: int, columns: list[str]) -> pl.LazyFrame:
    schema = set(panel.columns)
    available = [column for column in columns if column in schema]
    return panel.select([
        pl.col("simple_id"),
        (pl.col("ja") + depth).cast(pl.Int32).alias("t0"),
        pl.col("ja").alias(f"lag{depth}_source_year"),
        *[pl.col(column).alias(f"lag{depth}_{column}") for column in available],
    ]).unique(subset=["simple_id", "t0"], keep="first")

RISK_SET_PARTITION_TARGET_ROWS = 20_000_000
RISK_SET_PARTITION_HASH_SEED = 20_260_908

def _risk_set_panel_columns(config: PipelineConfig, schema: set[str]) -> list[str]:
    needed = [
        "simple_id", "ja", "rtwf_jjjj", "first_divorce_this_year",
        "divorce_from_first_marriage_this_year", "first_divorce_year", "msk_starts_this_year",
        *BASELINE_COLUMNS,
    ]
    if config.lag_depth == 3:
        needed += TREND_COLUMNS
    return [column for column in dict.fromkeys(needed) if column in schema]

def _risk_set_partition(
    config: PipelineConfig,
    panel_path: str | Path,
    columns: list[str],
    partition: int,
    n_partitions: int,
    candidate_years: list[int] | None,
    build_treated: bool,
) -> tuple[pl.DataFrame | None, pl.DataFrame, list[tuple[str, str, int, int]]]:


    counts: list[tuple[str, str, int, int]] = []
    def record(group: str, stage: str, frame: pl.LazyFrame) -> None:
        rows, persons = _count(frame)
        counts.append((group, stage, rows, persons))
    earliest_year = config.year_start - config.lag_depth
    scan = pl.scan_parquet(panel_path).select(columns)
    if n_partitions > 1:
        scan = scan.filter(
            (pl.col("simple_id").hash(seed=RISK_SET_PARTITION_HASH_SEED) % n_partitions) == partition
        )
    scan = scan.filter(pl.col("ja") >= earliest_year)
    if config.year_cap is not None:
        scan = scan.filter(pl.col("ja") <= config.year_cap)
    panel = _safe_collect(scan).lazy()
    index_panel = panel.filter(pl.col("ja") >= config.year_start)
    lag1 = _lag_frame(panel, 1, BASELINE_COLUMNS)
    lag2 = _lag_frame(panel, 2, TREND_COLUMNS) if config.lag_depth == 3 else None
    lag3 = _lag_frame(panel, 3, TREND_COLUMNS) if config.lag_depth == 3 else None
    def attach_lags(base: pl.LazyFrame) -> pl.LazyFrame:
        result = base.join(lag1, on=["simple_id", "t0"], how="left")
        if config.lag_depth == 3:
            result = result.join(lag2, on=["simple_id", "t0"], how="left")
            result = result.join(lag3, on=["simple_id", "t0"], how="left")
        return result
    treated_frame = None
    if build_treated:
        first_marriage_stage = (
            "restrict to marriage spell with marriage_start equal to first_marriage_start"
            if config.first_marriage_source == "date_fields"
            else "playdata proxy: require is_first_marriage equal to 1 on the divorce row"
        )
        treated = index_panel.filter(pl.col("first_divorce_this_year") == 1)
        record("treated", "first observed divorce in 2012-2018 before first-marriage restriction", treated)
        treated = treated.filter(pl.col("divorce_from_first_marriage_this_year") == 1)
        record("treated", first_marriage_stage, treated)
        treated = treated.filter(
            pl.col("rtwf_jjjj").is_null() | (pl.col("rtwf_jjjj") > pl.col("ja"))
        )
        record("treated", "require alive at assigned t0", treated)
        treated = treated.select([
            "simple_id", pl.col("ja").alias("t0"), pl.lit(1, dtype=pl.Int8).alias("treated"),
            "msk_starts_this_year",
        ])
        treated = treated.filter(pl.col("msk_starts_this_year") == 0)
        record("treated", "exclude MSK rehabilitation starting in t0", treated)
        treated = attach_lags(treated)
        treated = treated.filter(pl.col("lag1_source_year").is_not_null())
        record("treated", "require an observed t0-1 record", treated)
        treated = treated.filter(pl.col("lag1_age_band").is_not_null())
        record("treated", "require valid age at t0-1 for exact matching", treated)
        treated = treated.filter(pl.col("lag1_ever_msk_rehab_to_date").fill_null(0) == 0)
        record("treated", "exclude prior MSK rehabilitation through t0-1", treated)
        if config.lag_depth == 3:
            treated = treated.filter(
                pl.col("lag2_source_year").is_not_null() & pl.col("lag3_source_year").is_not_null()
            )
            record("treated", "require observed t0-2 and t0-3 records", treated)
        treated_frame = _safe_collect(treated.drop("msk_starts_this_year"))
    controls = index_panel
    if candidate_years is not None:
        controls = controls.filter(pl.col("ja").is_in(candidate_years))
    record("controls", "person-years in treated index years", controls)
    controls = controls.filter(
        pl.col("first_divorce_year").is_null() | (pl.col("first_divorce_year") > pl.col("ja"))
    )
    record("controls", "not yet divorced at candidate t0", controls)
    controls = controls.filter(
        pl.col("rtwf_jjjj").is_null() | (pl.col("rtwf_jjjj") > pl.col("ja"))
    )
    record("controls", "require alive at assigned t0", controls)
    controls = controls.filter(pl.col("msk_starts_this_year") == 0)
    record("controls", "exclude MSK rehabilitation starting in t0", controls)
    controls = controls.select([
        "simple_id", pl.col("ja").alias("t0"), pl.lit(0, dtype=pl.Int8).alias("treated"),
        "msk_starts_this_year",
    ])
    controls = attach_lags(controls)
    controls = controls.filter(pl.col("lag1_source_year").is_not_null())
    record("controls", "require an observed t0-1 record", controls)
    controls = controls.filter(pl.col("lag1_age_band").is_not_null())
    record("controls", "require valid age at t0-1 for exact matching", controls)
    controls = controls.filter(pl.col("lag1_ever_msk_rehab_to_date").fill_null(0) == 0)
    record("controls", "exclude prior MSK rehabilitation through t0-1", controls)
    if config.lag_depth == 3:
        controls = controls.filter(
            pl.col("lag2_source_year").is_not_null() & pl.col("lag3_source_year").is_not_null()
        )
        record("controls", "require observed t0-2 and t0-3 records", controls)
    controls_frame = _safe_collect(controls.drop("msk_starts_this_year"))
    return treated_frame, controls_frame, counts

class _PartitionedParquetOutput:


    def __init__(self, target: Path, row_group_size: int) -> None:
        self.target = target
        self.temporary = target.with_suffix(target.suffix + ".tmp")
        self.temporary.unlink(missing_ok=True)
        self.row_group_size = row_group_size
        self.writer = None
        self.rows = 0
    def append(self, frame: pl.DataFrame) -> None:
        import pyarrow.parquet as pq
        table = frame.to_arrow()
        if self.writer is None:
            self.target.parent.mkdir(parents=True, exist_ok=True)
            self.writer = pq.ParquetWriter(
                self.temporary, table.schema, compression="zstd", compression_level=3,
                write_statistics=True,
            )
        if table.num_rows > 0:
            self.writer.write_table(table, row_group_size=self.row_group_size)
            self.rows += table.num_rows
    def close(self, final: bool) -> None:
        if self.writer is not None:
            self.writer.close()
            self.writer = None
        if final and self.temporary.exists():
            self.temporary.replace(self.target)
        elif not final:
            self.temporary.unlink(missing_ok=True)

def _riskset_rehab_code_definition_path(config: PipelineConfig) -> Path:
    return config.diagnostics_dir / (
        f"riskset_rehab_code_definition_{config.control_pool}_lag{config.lag_depth}.json"
    )

def _riskset_rehab_code_definition(config: PipelineConfig) -> dict:
    path = _riskset_rehab_code_definition_path(config)
    if path.exists():
        try:
            payload = json.loads(path.read_text(encoding="utf-8"))
            applied = payload.get("applied") or {}
            return {
                "msk_diagnosis_codes": _normalize_diagnosis_codes(applied.get("msk_diagnosis_codes")),
                "mental_health_diagnosis_codes": _normalize_diagnosis_codes(
                    applied.get("mental_health_diagnosis_codes")
                ),
            }
        except (OSError, ValueError, AttributeError):
            pass
    return {
        "msk_diagnosis_codes": list(MSK_DIAGNOSIS_CODES_LEGACY),
        "mental_health_diagnosis_codes": list(MENTAL_HEALTH_REHAB_CODES_LEGACY),
    }

def build_risk_sets(config: PipelineConfig, panel_path: str | Path, force: bool = False) -> dict[str, Path]:


    treated_path = config.analysis_dir / f"riskset_treated_lag{config.lag_depth}.parquet"
    controls_path = config.analysis_dir / f"riskset_controls_{config.control_pool}_lag{config.lag_depth}.parquet"
    audit_path = config.diagnostics_dir / f"filter_audit_{config.control_pool}_lag{config.lag_depth}.csv"
    if treated_path.exists() and controls_path.exists() and audit_path.exists() and not force:
        return {"treated": treated_path, "controls": controls_path, "audit": audit_path}
    panel_schema = set(pl.read_parquet_schema(panel_path))
    columns = _risk_set_panel_columns(config, panel_schema)
    total_rows = _parquet_row_count(panel_path)
    n_partitions = max(1, -(-total_rows // RISK_SET_PARTITION_TARGET_ROWS))
    log.info(
        "Building lag-%d risk sets from %s panel rows in %d person-hash partition(s)",
        config.lag_depth, f"{total_rows:,}", n_partitions,
    )
    def run_partitions(candidate_years: list[int] | None, build_treated: bool):
        totals: dict[tuple[str, str], list[int]] = {}
        order: list[tuple[str, str]] = []
        treated_out = _PartitionedParquetOutput(treated_path, config.checkpoint_row_group_size) if build_treated else None
        controls_out = _PartitionedParquetOutput(controls_path, config.checkpoint_row_group_size)
        try:
            for partition in range(n_partitions):
                treated_frame, controls_frame, counts = _risk_set_partition(
                    config, panel_path, columns, partition, n_partitions, candidate_years, build_treated,
                )
                for group, stage, rows, persons in counts:
                    key = (group, stage)
                    if key not in totals:
                        totals[key] = [0, 0]
                        order.append(key)
                    totals[key][0] += rows
                    totals[key][1] += persons
                if treated_out is not None:
                    treated_out.append(treated_frame)
                controls_out.append(controls_frame)
                log.info(
                    "  risk-set partition %d/%d: %s treated, %s control person-years",
                    partition + 1, n_partitions,
                    f"{treated_frame.height:,}" if treated_frame is not None else "-",
                    f"{controls_frame.height:,}",
                )
        except BaseException:
            if treated_out is not None:
                treated_out.close(final=False)
            controls_out.close(final=False)
            raise
        if treated_out is not None:
            treated_out.close(final=True)
        controls_out.close(final=True)
        return order, totals


    order, totals = run_partitions(None, True)
    treated_years = sorted(
        int(y) for y in pl.scan_parquet(treated_path).select("t0").unique()
        .pipe(_safe_collect).get_column("t0").to_list()
    )
    control_years = sorted(
        int(y) for y in pl.scan_parquet(controls_path).select("t0").unique()
        .pipe(_safe_collect).get_column("t0").to_list()
    )
    if any(year not in treated_years for year in control_years):
        log.info(
            "Index years without any treated case after filtering: %s; rebuilding the control "
            "risk set restricted to the %d treated year(s).",
            [y for y in control_years if y not in treated_years], len(treated_years),
        )
        control_order, control_totals = run_partitions(treated_years, False)
        for key in control_order:
            totals[key] = control_totals[key]
    audit: list[dict] = []
    previous_rows: dict[str, int | None] = {"treated": None, "controls": None}
    for group, stage in order:
        rows, persons = totals[(group, stage)]
        audit.append({
            "group": group,
            "stage": stage,
            "n_rows": int(rows),
            "n_persons": int(persons),
            "removed_since_previous": (
                None if previous_rows[group] is None else int(previous_rows[group] - rows)
            ),
        })
        previous_rows[group] = int(rows)
    pl.DataFrame(audit).write_csv(audit_path)
    _riskset_rehab_code_definition_path(config).write_text(
        json.dumps({"applied": _rehab_code_definition(config), "source": "risk_set_build"}, indent=2),
        encoding="utf-8",
    )
    return {"treated": treated_path, "controls": controls_path, "audit": audit_path}

from dataclasses import dataclass
from pathlib import Path
import logging
import shutil

import numpy as np
import pandas as pd
import polars as pl
from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression, LinearRegression
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from scipy.special import expit
from scipy.optimize import linear_sum_assignment
from scipy.sparse import csr_matrix
from scipy.sparse.csgraph import min_weight_full_bipartite_matching

log = logging.getLogger(__name__)

@dataclass(**_DATACLASS_KWARGS)
class FeatureColumns:
    numeric: list[str]
    binary: list[str]
    categorical: list[str]
    exact: list[str]
    @property
    def model(self) -> list[str]:
        return self.numeric + self.binary + self.categorical

def _make_one_hot_encoder(*, sparse_output: bool, min_frequency: int) -> OneHotEncoder:
    common = {"handle_unknown": "ignore"}
    try:
        return OneHotEncoder(
            **common,
            min_frequency=min_frequency,
            sparse_output=sparse_output,
        )
    except TypeError:
        try:
            return OneHotEncoder(
                **common,
                min_frequency=min_frequency,
                sparse=sparse_output,
            )
        except TypeError:
            log.warning(
                "Installed scikit-learn lacks OneHotEncoder(min_frequency=...); "
                "rare categories will not be automatically pooled."
            )
            return OneHotEncoder(**common, sparse=sparse_output)

def resolve_features(config: PipelineConfig, columns: set[str]) -> FeatureColumns:
    numeric = [column for column in config.propensity_numeric if column in columns]
    binary = [column for column in config.propensity_binary if column in columns]
    categorical = [column for column in config.propensity_categorical if column in columns]
    exact = [column for column in config.exact_covariates if column in columns]
    if not config.source_has_entgelt:
        numeric = [name for name in numeric if "entgelt_value" not in name]
        binary = [name for name in binary if "entgelt_missing" not in name]
        categorical = [
            name for name in categorical if "income_source_status" not in name
        ]
    if config.lag_depth == 3:
        for depth in (2, 3):
            numeric_bases = ["rtzb_value", "rehab_starts_this_year"]
            if config.source_has_entgelt:
                numeric_bases.insert(0, "entgelt_value")
            for base in [*numeric_bases, "non_success_app_this_year"]:
                name = f"lag{depth}_{base}"
                if name in columns:
                    (binary if base == "non_success_app_this_year" else numeric).append(name)
            if config.source_has_entgelt:
                name = f"lag{depth}_income_source_status"
                if name in columns:
                    categorical.append(name)
    exact_set = set(exact)
    numeric = [column for column in numeric if column not in exact_set]
    binary = [column for column in binary if column not in exact_set]
    categorical = [column for column in categorical if column not in exact_set]
    if not exact:
        raise KeyError("None of the configured exact-match variables are available.")
    if not (numeric or binary or categorical):
        raise KeyError("None of the configured propensity-score variables are available.")
    return FeatureColumns(numeric, binary, categorical, exact)

def _fit_propensity(data: pd.DataFrame, features: FeatureColumns, config: PipelineConfig) -> tuple[np.ndarray, Pipeline]:
    y = data["treated"].astype(np.int8).to_numpy()
    if np.unique(y).size != 2:
        raise ValueError("A yearly propensity model requires both treated and controls.")
    transformers = []
    if features.numeric:
        transformers.append((
            "numeric",
            Pipeline([
                ("impute", SimpleImputer(strategy="median", add_indicator=True)),
                ("scale", StandardScaler(with_mean=False)),
            ]),
            features.numeric,
        ))
    if features.binary:
        transformers.append((
            "binary",
            SimpleImputer(strategy="most_frequent", add_indicator=True),
            features.binary,
        ))
    if features.categorical:
        transformers.append((
            "categorical",
            Pipeline([
                ("impute", SimpleImputer(strategy="constant", fill_value="__MISSING__")),
                ("onehot", _make_one_hot_encoder(
                    sparse_output=True,
                    min_frequency=config.minimum_category_frequency,
                )),
            ]),
            features.categorical,
        ))
    preprocessor = ColumnTransformer(transformers=transformers, sparse_threshold=0.1)


    solver = config.propensity_solver
    model = LogisticRegression(
        C=1.0,
        solver=solver,
        max_iter=config.propensity_max_iter,
        tol=config.propensity_tol,
        random_state=config.seed,
    )
    pipeline = Pipeline([("prepare", preprocessor), ("logit", model)])
    pipeline.fit(data[features.model], y)
    if int(np.max(model.n_iter_)) >= model.max_iter:
        raise RuntimeError(
            f"Propensity model did not converge with solver={solver} after {model.max_iter} iterations."
        )
    scores = pipeline.predict_proba(data[features.model])[:, 1]
    scores = np.clip(scores, 1e-6, 1 - 1e-6)
    return scores, pipeline

def _file_identity(path: str | Path) -> dict:
    stat = Path(path).stat()
    return {"path": str(path), "size": int(stat.st_size), "mtime": float(stat.st_mtime)}

def _parquet_row_count(path: str | Path) -> int:
    import pyarrow.parquet as pq
    path = Path(path)
    if not path.exists():
        return 0
    return int(pq.ParquetFile(path).metadata.num_rows)

def _iter_parquet_batches(path: str | Path, batch_size: int, columns: list[str] | None = None):


    import pyarrow.parquet as pq
    reader = pq.ParquetFile(path)
    for batch in reader.iter_batches(batch_size=batch_size, columns=columns):
        if batch.num_rows == 0:
            continue
        yield pl.from_arrow(batch)

RISK_SET_PARTITION_BATCH_ROWS = 1_000_000

def _partition_risk_sets_by_year(
    treated_path: str | Path,
    controls_path: str | Path,
    years: list[int],
    use_columns: list[str],
    partition_dir: Path,
) -> dict:


    import pyarrow.parquet as pq
    marker = partition_dir / "partition_manifest.json"
    expected = {
        "treated": _file_identity(treated_path),
        "controls": _file_identity(controls_path),
        "years": [int(y) for y in years],
        "use_columns": list(use_columns),
    }
    if marker.exists():
        try:
            previous = json.loads(marker.read_text(encoding="utf-8"))
        except (OSError, ValueError):
            previous = None
        if previous == expected:
            log.info("[skip] per-year risk-set partition exists: %s", partition_dir)
            return expected
    shutil.rmtree(partition_dir, ignore_errors=True)
    partition_dir.mkdir(parents=True)
    wanted = {int(y) for y in years}
    for kind, path, flag in (("treated", treated_path, 1), ("controls", controls_path, 0)):
        writers: dict[int, pq.ParquetWriter] = {}
        rows_seen = 0
        try:
            for batch in _iter_parquet_batches(path, RISK_SET_PARTITION_BATCH_ROWS, columns=use_columns):
                batch = batch.with_columns(pl.lit(flag, dtype=pl.Int8).alias("treated"))
                for key, part in batch.partition_by(["t0"], as_dict=True).items():
                    year = int(key[0] if isinstance(key, tuple) else key)
                    if year not in wanted:
                        continue
                    table = part.to_arrow()
                    writer = writers.get(year)
                    if writer is None:
                        writer = pq.ParquetWriter(
                            partition_dir / f"{kind}_{year}.parquet.tmp", table.schema,
                            compression="zstd", compression_level=1, write_statistics=False,
                        )
                        writers[year] = writer
                    writer.write_table(table)
                rows_seen += batch.height
        finally:
            for writer in writers.values():
                writer.close()
        for year in writers:
            (partition_dir / f"{kind}_{year}.parquet.tmp").replace(partition_dir / f"{kind}_{year}.parquet")
        log.info(
            "Partitioned %s risk set (%s rows) into %d treatment-year files under %s",
            kind, f"{rows_seen:,}", len(writers), partition_dir,
        )
    marker.write_text(json.dumps(expected, indent=2), encoding="utf-8")
    return expected

def _score_year_memory_bounded(
    config: PipelineConfig,
    treated_year_path: Path,
    controls_year_path: Path,
    year: int,
    features: FeatureColumns,
    use_columns: list[str],
    output: Path,
) -> dict:
    import pyarrow.parquet as pq
    n_treated = _parquet_row_count(treated_year_path)
    n_controls = _parquet_row_count(controls_year_path)
    if n_treated == 0 or n_controls == 0:
        raise RuntimeError(f"Year {year}: propensity model has {n_treated} treated and {n_controls} controls.")
    treated_lf = pl.scan_parquet(treated_year_path)
    controls_lf = pl.scan_parquet(controls_year_path)
    fit_cap = config.max_propensity_fit_rows
    if n_treated >= fit_cap:
        raise MemoryError(
            f"Year {year}: treated risk set alone ({n_treated:,}) exceeds max_propensity_fit_rows={fit_cap:,}."
        )
    desired_controls = min(n_controls, fit_cap - n_treated)
    minimum_controls_for_fit = max(20, n_treated * 2)
    if desired_controls < minimum_controls_for_fit:
        raise MemoryError(
            f"Year {year}: max_propensity_fit_rows={fit_cap:,} leaves room for only "
            f"{desired_controls:,} controls; at least {minimum_controls_for_fit:,} are required."
        )
    if desired_controls < n_controls:


        target_fraction = desired_controls / n_controls
        hash_limit = int(target_fraction * np.iinfo(np.uint64).max)
        sampled_controls_lf = (
            controls_lf.with_columns(pl.col("simple_id").hash(seed=config.seed).alias("_sample_hash"))
            .filter(pl.col("_sample_hash") <= hash_limit)
            .drop("_sample_hash")
        )
        sampled_controls = sampled_controls_lf.pipe(_safe_collect).to_pandas()
        if len(sampled_controls) < minimum_controls_for_fit:
            raise RuntimeError(
                f"Year {year}: hash sampling produced too few controls "
                f"({len(sampled_controls)} < {minimum_controls_for_fit})."
            )
    else:
        sampled_controls = controls_lf.pipe(_safe_collect).to_pandas()
    treated_fit = treated_lf.pipe(_safe_collect).to_pandas()
    fit_data = pd.concat([treated_fit, sampled_controls], ignore_index=True)


    fit_data = fit_data.sort_values(
        ["treated", "simple_id"], ascending=[False, True], kind="mergesort"
    ).reset_index(drop=True)
    log.info(
        "Year %s: fitting propensity model on %s rows (%s treated, %s sampled controls; %s total eligible controls)",
        year, f"{len(fit_data):,}", f"{n_treated:,}", f"{len(sampled_controls):,}", f"{n_controls:,}",
    )
    _, pipeline = _fit_propensity(fit_data, features, config)
    fitted_model = pipeline.named_steps["logit"]
    log.info(
        "Year %s: propensity model converged with solver=%s in %s iterations (max_iter=%s, tol=%g)",
        year, fitted_model.solver, int(np.max(fitted_model.n_iter_)),
        fitted_model.max_iter, fitted_model.tol,
    )
    n_fit_rows = int(len(fit_data))
    n_sampled_controls = int(len(sampled_controls))


    del fit_data, treated_fit, sampled_controls
    actual_control_fraction = n_sampled_controls / n_controls
    log_odds_offset = float(np.log(actual_control_fraction)) if actual_control_fraction < 1 else 0.0
    score_columns = ["simple_id", "t0", "treated", *features.exact]
    temporary = output.with_suffix(output.suffix + ".tmp")
    temporary.unlink(missing_ok=True)
    writer = None
    rows_scored = 0
    try:
        for source in (treated_year_path, controls_year_path):
            for batch in _iter_parquet_batches(source, config.propensity_score_batch_size):
                frame = batch.to_pandas()
                linear_predictor = pipeline.decision_function(frame[features.model]) + log_odds_offset
                pscore = np.clip(expit(linear_predictor), 1e-6, 1 - 1e-6).astype(np.float64)
                table = (
                    batch.select(score_columns)
                    .with_columns(pl.Series("pscore", pscore, dtype=pl.Float64))
                    .to_arrow()
                )
                if writer is None:
                    writer = pq.ParquetWriter(
                        temporary, table.schema, compression="zstd", compression_level=3,
                        write_statistics=True,
                    )
                writer.write_table(table, row_group_size=config.checkpoint_row_group_size)
                rows_scored += batch.height
    finally:
        if writer is not None:
            writer.close()
    if rows_scored == 0:
        temporary.unlink(missing_ok=True)
        raise RuntimeError(f"Year {year}: scoring produced no batches.")
    temporary.replace(output)
    log.info("Year %s: scored %s rows (%s treated + %s controls)", year, f"{rows_scored:,}", f"{n_treated:,}", f"{n_controls:,}")
    return {
        "n_treated": n_treated,
        "n_controls": n_controls,
        "propensity_fit_rows": n_fit_rows,
        "controls_used_to_fit_propensity": n_sampled_controls,
        "control_sampling_fraction": float(actual_control_fraction),
        "propensity_solver": pipeline.named_steps["logit"].solver,
        "propensity_iterations": int(np.max(pipeline.named_steps["logit"].n_iter_)),
        "propensity_max_iter": int(pipeline.named_steps["logit"].max_iter),
        "propensity_tol": float(pipeline.named_steps["logit"].tol),
    }

def _greedy_quality_benchmark(
    treated_scores: np.ndarray,
    control_scores: np.ndarray,
    caliper: float,
) -> tuple[int, float]:
    remaining = list(range(len(control_scores)))
    total = 0.0
    matched = 0
    for score in treated_scores:
        if not remaining:
            break
        values = control_scores[remaining]
        position = int(np.argmin(np.abs(values - score)))
        distance = float(abs(values[position] - score))
        if distance <= caliper:
            total += distance
            matched += 1
            remaining.pop(position)
    return matched, total

def _caliper_edge_metrics(
    treated: pd.DataFrame,
    controls: pd.DataFrame,
    caliper: float,
) -> dict[str, int | float]:
    t_scores = np.sort(treated["pscore"].to_numpy(float))
    c_scores = np.sort(controls["pscore"].to_numpy(float))
    m, n = len(t_scores), len(c_scores)
    if m == 0 or n == 0:
        return {
            "n_treated_in_stratum": int(m),
            "n_controls_in_stratum": int(n),
            "dense_assignment_entries": int(m * (n + m)),
            "candidate_real_edges": 0,
            "candidate_edges_plus_dummies": int(m),
        }
    left = np.searchsorted(c_scores, t_scores - caliper, side="left")
    right = np.searchsorted(c_scores, t_scores + caliper, side="right")
    n_real_edges = int((right - left).sum())
    return {
        "n_treated_in_stratum": int(m),
        "n_controls_in_stratum": int(n),
        "dense_assignment_entries": int(m * (n + m)),
        "candidate_real_edges": n_real_edges,
        "candidate_edges_plus_dummies": int(n_real_edges + m),
    }

def _append_matching_edge_preflight(path: str | Path, row: dict) -> None:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    pd.DataFrame([row]).to_csv(
        path,
        mode="a",
        header=not path.exists(),
        index=False,
    )

def _optimal_without_replacement(
    treated: pd.DataFrame,
    controls: pd.DataFrame,
    config: PipelineConfig,
) -> tuple[pd.DataFrame, dict]:
    columns = ["t_id", "c_id", "t0", "t_pscore", "c_pscore", "abs_ps_diff"]
    if treated.empty or controls.empty:
        return pd.DataFrame(columns=columns), {
            "optimal_solver": "none", "candidate_real_edges": 0,
            "optimal_total_distance": 0.0, "greedy_benchmark_matches": None,
            "greedy_benchmark_total_distance": None,
        }
    t = treated[["simple_id", "t0", "pscore"]].sort_values(
        ["pscore", "simple_id"], kind="mergesort"
    ).reset_index(drop=True)
    c = controls[["simple_id", "t0", "pscore"]].sort_values(
        ["pscore", "simple_id"], kind="mergesort"
    ).reset_index(drop=True)
    t_scores = t["pscore"].to_numpy(float)
    c_scores = c["pscore"].to_numpy(float)
    m, n = len(t), len(c)
    left = np.searchsorted(c_scores, t_scores - config.caliper, side="left")
    right = np.searchsorted(c_scores, t_scores + config.caliper, side="right")
    edge_counts = right - left
    n_real_edges = int(edge_counts.sum())
    if n_real_edges == 0:
        return pd.DataFrame(columns=columns), {
            "optimal_solver": "none_no_caliper_edges", "candidate_real_edges": 0,
            "optimal_total_distance": 0.0, "greedy_benchmark_matches": 0,
            "greedy_benchmark_total_distance": 0.0,
        }
    dummy_cost = float((m + 1) * (config.caliper + 1e-9))
    invalid_cost = dummy_cost * 2.0
    dense_entries = int(m * (n + m))
    if dense_entries <= config.optimal_match_dense_max_entries:
        cost = np.full((m, n + m), invalid_cost, dtype=np.float64)
        for i, (lo, hi) in enumerate(zip(left, right)):
            if hi > lo:
                cost[i, lo:hi] = np.abs(c_scores[lo:hi] - t_scores[i])
            cost[i, n + i] = dummy_cost
        row_ind, col_ind = linear_sum_assignment(cost)
        solver = "dense_hungarian_exact"
        selected_cost = cost[row_ind, col_ind]
    else:
        if n_real_edges + m > config.optimal_match_sparse_max_edges:
            raise MemoryError(
                "Exact optimal matching would require "
                f"{n_real_edges + m:,} sparse edges in one exact stratum, above "
                f"optimal_match_sparse_max_edges={config.optimal_match_sparse_max_edges:,}. "
                "The pipeline will not silently use greedy matching. Tighten the caliper, "
                "add a substantively justified exact stratum, or raise the edge limit after "
                "checking available RAM."
            )
        rows = np.empty(n_real_edges + m, dtype=np.int32)
        cols = np.empty(n_real_edges + m, dtype=np.int64)
        values = np.empty(n_real_edges + m, dtype=np.float64)
        cursor = 0
        epsilon = 1e-12
        for i, (lo, hi) in enumerate(zip(left, right)):
            count = int(hi - lo)
            if count:
                sl = slice(cursor, cursor + count)
                rows[sl] = i
                cols[sl] = np.arange(lo, hi, dtype=np.int64)
                values[sl] = np.abs(c_scores[lo:hi] - t_scores[i]) + epsilon
                cursor += count
            rows[cursor] = i
            cols[cursor] = n + i
            values[cursor] = dummy_cost
            cursor += 1
        matrix = csr_matrix((values[:cursor], (rows[:cursor], cols[:cursor])), shape=(m, n + m))
        row_ind, col_ind = min_weight_full_bipartite_matching(matrix, maximize=False)
        solver = "sparse_bipartite_exact"
        selected_cost = np.asarray(matrix[row_ind, col_ind]).reshape(-1)
    real = col_ind < n
    row_real = row_ind[real]
    col_real = col_ind[real]
    if len(row_real):
        distances = np.abs(t_scores[row_real] - c_scores[col_real])
        result = pd.DataFrame({
            "t_id": t.loc[row_real, "simple_id"].to_numpy(np.int64),
            "c_id": c.loc[col_real, "simple_id"].to_numpy(np.int64),
            "t0": t.loc[row_real, "t0"].to_numpy(np.int32),
            "t_pscore": t_scores[row_real],
            "c_pscore": c_scores[col_real],
            "abs_ps_diff": distances,
        })
    else:
        result = pd.DataFrame(columns=columns)
    greedy_n = greedy_total = None
    if m * n <= 1_000_000:
        greedy_n, greedy_total = _greedy_quality_benchmark(t_scores, c_scores, config.caliper)
    diagnostic = {
        "optimal_solver": solver,
        "candidate_real_edges": n_real_edges,
        "dense_assignment_entries": dense_entries,
        "optimal_total_distance": float(result["abs_ps_diff"].sum()) if not result.empty else 0.0,
        "greedy_benchmark_matches": greedy_n,
        "greedy_benchmark_total_distance": greedy_total,
    }
    return result[columns], diagnostic

def _match_scored_year_by_exact_strata(
    score_file: str | Path,
    features: FeatureColumns,
    config: PipelineConfig,
    used_controls: set[int],
    preflight_path: str | Path,
) -> tuple[pd.DataFrame, dict]:
    score_lf = pl.scan_parquet(score_file)
    treated = score_lf.filter(pl.col("treated") == 1).pipe(_safe_collect).to_pandas()
    match_parts: list[pd.DataFrame] = []
    n_no_exact_control = 0
    n_controls_available = 0
    solver_counts: dict[str, int] = {}
    candidate_edges = 0
    optimal_distance = 0.0
    greedy_benchmark_distance = 0.0
    greedy_benchmark_matches = 0
    greedy_benchmark_strata = 0
    for key, t_group in treated.groupby(features.exact, dropna=False, sort=False):
        key_tuple = key if isinstance(key, tuple) else (key,)
        condition = pl.col("treated") == 0
        for column, value in zip(features.exact, key_tuple):
            condition = condition & (pl.col(column).is_null() if pd.isna(value) else (pl.col(column) == value))
        controls = (
            score_lf.filter(condition).select(["simple_id", "t0", "pscore"])
            .pipe(_safe_collect).to_pandas()
        )
        if used_controls and not controls.empty:
            controls = controls.loc[~controls["simple_id"].astype(np.int64).isin(used_controls)].copy()
        n_controls_available += len(controls)
        edge_metrics = _caliper_edge_metrics(t_group, controls, config.caliper)
        exact_values = {
            column: (None if pd.isna(value) else str(value))
            for column, value in zip(features.exact, key_tuple)
        }
        preflight_row = {
            "t0": int(t_group["t0"].iloc[0]),
            "exact_stratum": json.dumps(exact_values, sort_keys=True),
            "probability_scale_caliper": float(config.caliper),
            **edge_metrics,
            "dense_entry_cap": int(config.optimal_match_dense_max_entries),
            "requires_sparse_solver": bool(
                edge_metrics["dense_assignment_entries"]
                > config.optimal_match_dense_max_entries
            ),
            "sparse_edge_cap": int(config.optimal_match_sparse_max_edges),
            "would_fail_current_matcher": bool(
                edge_metrics["dense_assignment_entries"]
                > config.optimal_match_dense_max_entries
                and edge_metrics["candidate_edges_plus_dummies"]
                > config.optimal_match_sparse_max_edges
            ),
            "treated_pscore_min": float(t_group["pscore"].min()),
            "treated_pscore_max": float(t_group["pscore"].max()),
            "control_pscore_min": (
                float(controls["pscore"].min()) if not controls.empty else None
            ),
            "control_pscore_max": (
                float(controls["pscore"].max()) if not controls.empty else None
            ),
        }
        _append_matching_edge_preflight(preflight_path, preflight_row)
        if preflight_row["would_fail_current_matcher"]:
            log.error(
                "Year %s exact stratum %s requires the sparse solver but has %s admissible edges including dummies, above cap %s.",
                preflight_row["t0"],
                preflight_row["exact_stratum"],
                f'{edge_metrics["candidate_edges_plus_dummies"]:,}',
                f'{config.optimal_match_sparse_max_edges:,}',
            )
        if controls.empty:
            n_no_exact_control += len(t_group)
            continue
        matched, diagnostic = _optimal_without_replacement(t_group, controls, config)
        solver = diagnostic["optimal_solver"]
        solver_counts[solver] = solver_counts.get(solver, 0) + 1
        candidate_edges += int(diagnostic.get("candidate_real_edges") or 0)
        optimal_distance += float(diagnostic.get("optimal_total_distance") or 0.0)
        if diagnostic.get("greedy_benchmark_matches") is not None:
            greedy_benchmark_strata += 1
            greedy_benchmark_matches += int(diagnostic["greedy_benchmark_matches"])
            greedy_benchmark_distance += float(diagnostic["greedy_benchmark_total_distance"] or 0.0)
        if not matched.empty:
            match_parts.append(matched)
    matches = pd.concat(match_parts, ignore_index=True) if match_parts else pd.DataFrame(
        columns=["t_id", "c_id", "t0", "t_pscore", "c_pscore", "abs_ps_diff"]
    )
    diagnostics = {
        "n_treated": int(len(treated)),
        "n_controls_available_after_prior_year_use": int(n_controls_available),
        "n_matched": int(len(matches)),
        "n_without_exact_control": int(n_no_exact_control),
        "n_unmatched_after_exact_and_caliper": int(len(treated) - n_no_exact_control - len(matches)),
        "optimal_solver_counts": json.dumps(solver_counts, sort_keys=True),
        "candidate_real_edges": int(candidate_edges),
        "optimal_total_distance": float(optimal_distance),
        "greedy_benchmark_strata": int(greedy_benchmark_strata),
        "greedy_benchmark_matches": int(greedy_benchmark_matches) if greedy_benchmark_strata else None,
        "greedy_benchmark_total_distance": float(greedy_benchmark_distance) if greedy_benchmark_strata else None,
    }
    return matches, diagnostics

def _matching_checkpoint_expectation(
    config: PipelineConfig,
    treated_path: str | Path,
    controls_path: str | Path,
    use_columns: list[str],
    years: list[int],
) -> dict:


    matching_keys = sorted(
        key for key, tier in CONFIG_KEY_STAGE_TIER.items() if tier <= STAGE_TIER_MATCHING
    )
    settings = config.to_dict()
    return {
        "treated": _file_identity(treated_path),
        "controls": _file_identity(controls_path),
        "use_columns": list(use_columns),
        "years": [int(y) for y in years],
        "settings": {key: settings.get(key) for key in matching_keys},
    }

def fit_and_match(
    config: PipelineConfig,
    treated_path: str | Path,
    controls_path: str | Path,
    force: bool = False,
) -> dict[str, Path]:
    spec = f"{config.control_pool}_lag{config.lag_depth}"
    matched_path = config.analysis_dir / f"matched_pairs_{spec}.parquet"
    scores_path = config.analysis_dir / f"propensity_scores_{spec}.parquet"
    audit_path = config.diagnostics_dir / f"matching_audit_{spec}.csv"
    preflight_path = config.diagnostics_dir / f"matching_edge_preflight_{spec}.csv"
    if (
        matched_path.exists() and scores_path.exists() and audit_path.exists()
        and preflight_path.exists() and not force
    ):
        return {
            "matches": matched_path,
            "scores": scores_path,
            "audit": audit_path,
            "edge_preflight": preflight_path,
        }
    treated_schema = set(pl.read_parquet_schema(treated_path))
    control_schema = set(pl.read_parquet_schema(controls_path))
    common = treated_schema & control_schema
    features = resolve_features(config, common)
    use_columns = list(dict.fromkeys(["simple_id", "t0", *features.exact, *features.model]))
    years = [
        int(y) for y in pl.scan_parquet(treated_path)
        .select("t0").unique().sort("t0").pipe(_safe_collect)
        .get_column("t0").to_list()
    ]
    if not years:
        raise RuntimeError("No treated index years remain after risk-set filtering.")


    temp = config.run_dir / "_matching_temp"
    manifest_path = temp / "checkpoint_manifest.json"
    expected = _matching_checkpoint_expectation(config, treated_path, controls_path, use_columns, years)
    resume = False
    if temp.exists() and manifest_path.exists() and not force:
        try:
            resume = json.loads(manifest_path.read_text(encoding="utf-8")) == expected
        except (OSError, ValueError):
            resume = False
    if not resume:
        if temp.exists():
            shutil.rmtree(temp)
        temp.mkdir(parents=True)
        manifest_path.write_text(json.dumps(expected, indent=2), encoding="utf-8")
        preflight_path.unlink(missing_ok=True)
    partition_dir = temp / "risk_sets_by_year"
    _partition_risk_sets_by_year(treated_path, controls_path, years, use_columns, partition_dir)
    score_files: list[Path] = []
    match_files: list[Path] = []
    used_controls: set[int] = set()
    audits: list[dict] = []
    next_group = 1
    completed_years: list[int] = []
    if resume:
        for year in years:
            year_audit = temp / f"year_{year}_audit.json"
            score_file = temp / f"scores_{year}.parquet"
            match_file = temp / f"matches_{year}.parquet"
            if not (year_audit.exists() and score_file.exists()):
                break
            diagnostic = json.loads(year_audit.read_text(encoding="utf-8"))
            if diagnostic["n_matched"] > 0 and not match_file.exists():
                break
            completed_years.append(year)
            score_files.append(score_file)
            audits.append(diagnostic)
            if match_file.exists():
                match_files.append(match_file)
                done = pl.read_parquet(match_file, columns=["c_id", "match_group"])
                used_controls.update(done.get_column("c_id").cast(pl.Int64).to_list())
                next_group = max(next_group, int(done.get_column("match_group").max()) + 1)
        if completed_years:


            if preflight_path.exists():
                preflight = pd.read_csv(preflight_path)
                preflight = preflight.loc[preflight["t0"].isin(completed_years)]
                preflight.to_csv(preflight_path, index=False)
            log.info(
                "Resuming matching after %d completed treatment year(s): %s",
                len(completed_years), completed_years,
            )
        else:
            preflight_path.unlink(missing_ok=True)
    try:
        for year in years:
            if year in completed_years:
                continue
            score_file = temp / f"scores_{year}.parquet"
            score_diagnostic_path = temp / f"scores_{year}_diagnostic.json"
            if score_file.exists() and score_diagnostic_path.exists():
                score_diagnostic = json.loads(score_diagnostic_path.read_text(encoding="utf-8"))
                log.info("Year %s: reusing checkpointed propensity scores", year)
            else:
                score_diagnostic_path.unlink(missing_ok=True)
                score_diagnostic = _score_year_memory_bounded(
                    config,
                    partition_dir / f"treated_{year}.parquet",
                    partition_dir / f"controls_{year}.parquet",
                    int(year),
                    features,
                    use_columns,
                    score_file,
                )
                score_diagnostic_path.write_text(json.dumps(score_diagnostic, indent=2), encoding="utf-8")
            score_files.append(score_file)

            if preflight_path.exists():
                preflight = pd.read_csv(preflight_path)
                if (preflight["t0"] == int(year)).any():
                    preflight.loc[preflight["t0"] != int(year)].to_csv(preflight_path, index=False)
            matches, diagnostic = _match_scored_year_by_exact_strata(
                score_file, features, config, used_controls, preflight_path
            )
            if matches.empty and config.strict_main_run:
                raise RuntimeError(f"Year {year}: no treated cases could be matched.")
            match_file = temp / f"matches_{year}.parquet"
            match_file.unlink(missing_ok=True)
            if not matches.empty:
                matches["match_group"] = np.arange(next_group, next_group + len(matches), dtype=np.int64)
                next_group += len(matches)
                used_controls.update(matches["c_id"].astype(np.int64).tolist())
                match_tmp = temp / f"matches_{year}.parquet.tmp"
                pl.from_pandas(matches).write_parquet(match_tmp, compression="zstd")
                match_tmp.replace(match_file)
                match_files.append(match_file)
            diagnostic.update(score_diagnostic)
            diagnostic.update({
                "t0": int(year),
                "match_rate": diagnostic["n_matched"] / max(diagnostic["n_treated"], 1),
                "mean_abs_ps_diff": float(matches["abs_ps_diff"].mean()) if not matches.empty else np.nan,
                "max_abs_ps_diff": float(matches["abs_ps_diff"].max()) if not matches.empty else np.nan,
            })
            audits.append(diagnostic)
            (temp / f"year_{year}_audit.json").write_text(
                json.dumps(diagnostic, indent=2, default=_json_default), encoding="utf-8"
            )
            log.info(
                "Year %s: matched %s of %s treated (checkpoint written)",
                year, f"{diagnostic['n_matched']:,}", f"{diagnostic['n_treated']:,}",
            )
        if not match_files:
            raise RuntimeError("Matching produced no matched pairs.")
        sink_parquet(pl.scan_parquet([str(p) for p in match_files]), matched_path, config.checkpoint_row_group_size)
        sink_parquet(pl.scan_parquet([str(p) for p in score_files]), scores_path, config.checkpoint_row_group_size)
        pl.DataFrame(audits).sort("t0").write_csv(audit_path)
    except BaseException:
        log.warning(
            "Matching did not finish; per-year checkpoints kept under %s for --reuse-existing.", temp,
        )
        raise
    shutil.rmtree(temp, ignore_errors=True)
    matches = pl.scan_parquet(matched_path)
    integrity = matches.select([
        pl.len().alias("n_matches"),
        pl.col("t_id").n_unique().alias("unique_treated"),
        pl.col("c_id").n_unique().alias("unique_controls"),
        pl.col("match_group").n_unique().alias("unique_match_groups"),
        pl.col("abs_ps_diff").max().alias("max_distance"),
    ]).pipe(_safe_collect).row(0, named=True)
    if integrity["n_matches"] != integrity["unique_treated"]:
        raise AssertionError("A treated case was matched more than once.")
    if integrity["n_matches"] != integrity["unique_controls"]:
        raise AssertionError("A control was reused despite no-replacement matching.")
    if integrity["n_matches"] != integrity["unique_match_groups"]:
        raise AssertionError("match_group is not unique per pair.")
    if integrity["max_distance"] > config.caliper + 1e-12:
        raise AssertionError("At least one pair violates the configured caliper.")
    return {
        "matches": matched_path,
        "scores": scores_path,
        "audit": audit_path,
        "edge_preflight": preflight_path,
    }

def _json_default(value):

    if isinstance(value, (np.integer,)):
        return int(value)
    if isinstance(value, (np.floating,)):
        return None if np.isnan(value) else float(value)
    if isinstance(value, (np.bool_,)):
        return bool(value)
    raise TypeError(f"Object of type {type(value).__name__} is not JSON serializable")

from pathlib import Path
import math

import polars as pl

def _safe_smd(mean_t: float | None, var_t: float | None, mean_c: float | None, var_c: float | None) -> float | None:
    if any(value is None for value in (mean_t, var_t, mean_c, var_c)):
        return None
    denominator = math.sqrt(max((float(var_t) + float(var_c)) / 2.0, 0.0))
    if denominator == 0:
        return 0.0 if float(mean_t) == float(mean_c) else None
    return (float(mean_t) - float(mean_c)) / denominator

def _weighted_numeric(frame: pl.LazyFrame, variable: str) -> dict:
    valid = frame.filter(pl.col(variable).is_not_null())
    row = valid.select([
        pl.col("weight").sum().alias("sum_w"),
        (pl.col(variable) * pl.col("weight")).sum().alias("sum_wx"),
        ((pl.col(variable) ** 2) * pl.col("weight")).sum().alias("sum_wx2"),
    ]).pipe(_safe_collect).row(0, named=True)
    total_weight = frame.select(pl.col("weight").sum()).pipe(_safe_collect).item()
    sum_w = row["sum_w"] or 0.0
    mean = row["sum_wx"] / sum_w if sum_w else None
    variance = max(row["sum_wx2"] / sum_w - mean**2, 0.0) if sum_w and mean is not None else None
    missing_weight = float(total_weight or 0.0) - float(sum_w)
    return {
        "mean": mean,
        "variance": variance,
        "missing_rate": missing_weight / total_weight if total_weight else None,
    }

def _weighted_proportions(frame: pl.LazyFrame, variable: str) -> dict[str, float]:
    data = frame.with_columns(
        pl.col(variable).cast(pl.Utf8, strict=False).fill_null("__MISSING__").alias("_level")
    )
    total = data.select(pl.col("weight").sum()).pipe(_safe_collect).item()
    if not total:
        return {}
    rows = (
        data.group_by("_level")
        .agg(pl.col("weight").sum().alias("weighted_n"))
        .pipe(_safe_collect)
    )
    return {str(level): float(weight) / float(total) for level, weight in rows.iter_rows()}

def _analysis_frames(
    treated_path: str | Path,
    controls_path: str | Path,
    matches_path: str | Path,
) -> dict[str, tuple[pl.LazyFrame, pl.LazyFrame]]:
    treated = pl.scan_parquet(treated_path)
    controls = pl.scan_parquet(controls_path)
    matches = pl.scan_parquet(matches_path)
    pre_t = treated.with_columns(pl.lit(1.0).alias("weight"))
    pre_c = controls.with_columns(pl.lit(1.0).alias("weight"))
    t_map = matches.select([
        pl.col("t_id").alias("simple_id"), "t0", "match_group"
    ])
    c_map = matches.select([
        pl.col("c_id").alias("simple_id"), "t0", "match_group"
    ])
    post_t = treated.join(t_map, on=["simple_id", "t0"], how="inner").with_columns(pl.lit(1.0).alias("weight"))
    post_c = controls.join(c_map, on=["simple_id", "t0"], how="inner").with_columns(pl.lit(1.0).alias("weight"))
    return {"pre": (pre_t, pre_c), "post": (post_t, post_c)}

def build_balance_tables(
    config: PipelineConfig,
    treated_path: str | Path,
    controls_path: str | Path,
    matches_path: str | Path,
    force: bool = False,
) -> dict[str, Path]:
    spec = f"{config.control_pool}_lag{config.lag_depth}"
    detail_path = config.diagnostics_dir / f"balance_detail_{spec}.csv"
    summary_path = config.diagnostics_dir / f"balance_summary_{spec}.csv"
    if detail_path.exists() and summary_path.exists() and not force:
        return {"detail": detail_path, "summary": summary_path}
    common = set(pl.read_parquet_schema(treated_path)) & set(pl.read_parquet_schema(controls_path))
    features = resolve_features(config, common)
    frames = _analysis_frames(treated_path, controls_path, matches_path)
    rows: list[dict] = []
    for sample, (treated, controls) in frames.items():
        for variable in features.numeric:
            stats_t = _weighted_numeric(treated, variable)
            stats_c = _weighted_numeric(controls, variable)
            rows.append({
                "sample": sample, "variable": variable, "level": None, "variable_type": "continuous",
                "treated_value": stats_t["mean"], "control_value": stats_c["mean"],
                "smd": _safe_smd(stats_t["mean"], stats_t["variance"], stats_c["mean"], stats_c["variance"]),
                "treated_missing_rate": stats_t["missing_rate"], "control_missing_rate": stats_c["missing_rate"],
            })
            mt, mc = stats_t["missing_rate"], stats_c["missing_rate"]
            if mt is not None and mc is not None:
                rows.append({
                    "sample": sample, "variable": f"{variable}__missing", "level": "missing",
                    "variable_type": "binary_missingness", "treated_value": mt, "control_value": mc,
                    "smd": _safe_smd(mt, mt * (1 - mt), mc, mc * (1 - mc)),
                    "treated_missing_rate": None, "control_missing_rate": None,
                })
        for variable in features.binary:
            stats_t = _weighted_numeric(treated, variable)
            stats_c = _weighted_numeric(controls, variable)
            rows.append({
                "sample": sample, "variable": variable, "level": "1", "variable_type": "binary",
                "treated_value": stats_t["mean"], "control_value": stats_c["mean"],
                "smd": _safe_smd(stats_t["mean"], stats_t["variance"], stats_c["mean"], stats_c["variance"]),
                "treated_missing_rate": stats_t["missing_rate"], "control_missing_rate": stats_c["missing_rate"],
            })
        for variable in list(dict.fromkeys(features.categorical + features.exact)):
            proportions_t = _weighted_proportions(treated, variable)
            proportions_c = _weighted_proportions(controls, variable)
            for level in sorted(set(proportions_t) | set(proportions_c)):
                pt = proportions_t.get(level, 0.0)
                pc = proportions_c.get(level, 0.0)
                rows.append({
                    "sample": sample, "variable": variable, "level": level, "variable_type": "categorical_level",
                    "treated_value": pt, "control_value": pc,
                    "smd": _safe_smd(pt, pt * (1 - pt), pc, pc * (1 - pc)),
                    "treated_missing_rate": None, "control_missing_rate": None,
                })
    detail = pl.DataFrame(rows)
    detail.write_csv(detail_path)
    summary = (
        detail.with_columns(pl.col("smd").abs().alias("abs_smd"))
        .group_by(["sample", "variable", "variable_type"])
        .agg([
            pl.col("abs_smd").max().alias("max_abs_smd"),
            pl.col("abs_smd").mean().alias("mean_abs_smd"),
            pl.len().alias("n_levels_or_components"),
        ])
        .sort(["sample", "max_abs_smd"], descending=[False, True])
    )
    summary.write_csv(summary_path)
    return {"detail": detail_path, "summary": summary_path}

def build_descriptive_statistics_table(
    config: PipelineConfig,
    treated_path: str | Path,
    controls_path: str | Path,
    matches_path: str | Path,
    output_path: str | Path,
    force: bool = False,
) -> Path:
    """Classic n/mean/median/SD/min/max (continuous) and n/% (binary) table.

    This is deliberately a *different* view of the same matched sample as
    build_balance_tables: the balance table answers "did matching close the
    gap between divorced people and their controls" (treated mean vs. control
    mean vs. SMD). This function answers "what does the matched sample look
    like overall" (pooled distributional summary), which a referee expects
    to see as a plain sample-characteristics table alongside, not instead
    of, the balance table. Reuses the same feature lists and the same
    post-match analysis frames as build_balance_tables so the two tables can
    never silently disagree about which covariates or which matched
    population they describe.
    """
    output_path = Path(output_path)
    if output_path.exists() and not force:
        return output_path
    common = set(pl.read_parquet_schema(treated_path)) & set(pl.read_parquet_schema(controls_path))
    features = resolve_features(config, common)
    frames = _analysis_frames(treated_path, controls_path, matches_path)
    post_t, post_c = frames["post"]
    # Fix an explicit column order before concatenating: the two source
    # parquet files are not guaranteed to list columns in the same order,
    # and relying on positional (rather than name-based) vertical concat
    # would silently misalign columns rather than raising an error.
    ordered_columns = sorted(common)
    pooled = pl.concat(
        [post_t.select(ordered_columns), post_c.select(ordered_columns)],
        how="vertical",
    )
    rows: list[dict] = []
    for variable in features.numeric:
        valid = pooled.filter(pl.col(variable).is_not_null())
        stats = valid.select([
            pl.len().alias("n"),
            pl.col(variable).mean().alias("mean"),
            pl.col(variable).median().alias("median"),
            pl.col(variable).std().alias("sd"),
            pl.col(variable).min().alias("min"),
            pl.col(variable).max().alias("max"),
        ]).pipe(_safe_collect).row(0, named=True)
        rows.append({
            "variable": variable, "variable_type": "continuous",
            "n": stats["n"], "mean": stats["mean"], "median": stats["median"],
            "sd": stats["sd"], "min": stats["min"], "max": stats["max"],
        })
    for variable in features.binary:
        valid = pooled.filter(pl.col(variable).is_not_null())
        stats = valid.select([
            pl.len().alias("n"),
            (pl.col(variable).cast(pl.Float64).mean() * 100.0).alias("mean_pct"),
        ]).pipe(_safe_collect).row(0, named=True)
        rows.append({
            "variable": variable, "variable_type": "binary",
            "n": stats["n"], "mean": stats["mean_pct"],
            "median": None, "sd": None, "min": None, "max": None,
        })
    table = pl.DataFrame(
        rows,
        schema={
            "variable": pl.Utf8, "variable_type": pl.Utf8, "n": pl.Int64,
            "mean": pl.Float64, "median": pl.Float64, "sd": pl.Float64,
            "min": pl.Float64, "max": pl.Float64,
        },
    )
    table.write_csv(output_path)
    return output_path

def select_imbalanced_covariates(
    config: PipelineConfig,
    balance_summary_path: str | Path,
    threshold: float | None = None,
) -> list[dict]:
    threshold = config.smd_threshold if threshold is None else threshold
    summary = pl.read_csv(balance_summary_path).filter(
        (pl.col("sample") == "post") & (pl.col("max_abs_smd") > threshold)
    ).sort("max_abs_smd", descending=True)
    allowed = set(
        config.propensity_numeric + config.propensity_binary
        + config.propensity_categorical + config.exact_covariates
    )
    if config.lag_depth == 3:
        for depth in (2, 3):
            allowed.update({
                f"lag{depth}_rtzb_value",
                f"lag{depth}_non_success_app_this_year",
                f"lag{depth}_rehab_starts_this_year",
            })
            if config.source_has_entgelt:
                allowed.update({
                    f"lag{depth}_entgelt_value",
                    f"lag{depth}_income_source_status",
                })
    selected: dict[str, dict] = {}
    for row in summary.iter_rows(named=True):
        raw = str(row["variable"])
        base = raw[:-len("__missing")] if raw.endswith("__missing") else raw
        if base not in allowed:
            continue
        current = selected.get(base)
        if current is None or float(row["max_abs_smd"]) > current["max_abs_smd"]:
            selected[base] = {
                "variable": base,
                "trigger_component": raw,
                "variable_type": row["variable_type"],
                "max_abs_smd": float(row["max_abs_smd"]),
            }
    result = sorted(selected.values(), key=lambda item: item["max_abs_smd"], reverse=True)
    output = config.diagnostics_dir / f"smd_selected_covariates_{config.control_pool}_lag{config.lag_depth}.json"
    output.write_text(json.dumps({
        "threshold": threshold,
        "selection_rule": "post-match max absolute SMD above threshold; categorical variables use level-specific SMDs",
        "selected": result,
    }, indent=2), encoding="utf-8")
    return result

def build_panel_coverage_diagnostics(
    config: PipelineConfig,
    panel_path: str | Path,
    force: bool = False,
) -> Path:
    output = config.diagnostics_dir / "panel_coverage_diagnostics.csv"
    if output.exists() and not force:
        return output
    people = (
        pl.scan_parquet(panel_path)
        .group_by("simple_id")
        .agg([
            pl.col("ja").min().alias("first_record_year"),
            pl.col("ja").max().alias("last_record_year"),
            pl.col("ja").n_unique().alias("n_observed_years"),
            pl.col("rtwf_jjjj").drop_nulls().max().alias("death_year"),
        ])
        .with_columns([
            (pl.col("last_record_year") - pl.col("first_record_year") + 1)
            .alias("calendar_span_years"),
        ])
        .with_columns([
            (pl.col("calendar_span_years") - pl.col("n_observed_years")).alias("n_gap_years"),
            (
                pl.col("death_year").is_not_null()
                & (pl.col("death_year") > pl.col("last_record_year"))
            ).alias("death_after_last_annual_record"),
            (
                pl.col("death_year").is_not_null()
                & (pl.col("death_year") <= pl.col("last_record_year"))
            ).alias("death_on_or_before_last_annual_record"),
        ])
    )
    summary = people.select([
        pl.len().alias("n_people"),
        pl.col("first_record_year").min().alias("earliest_record_year"),
        pl.col("last_record_year").max().alias("latest_record_year"),
        (pl.col("n_gap_years") > 0).sum().alias("people_with_internal_year_gaps"),
        pl.col("n_gap_years").sum().alias("total_internal_gap_years"),
        pl.col("death_year").is_not_null().sum().alias("people_with_recorded_death_year"),
        pl.col("death_after_last_annual_record").sum().alias("deaths_recorded_after_last_annual_record"),
        pl.col("death_on_or_before_last_annual_record").sum().alias("deaths_on_or_before_last_annual_record"),
    ]).pipe(_safe_collect).transpose(
        include_header=True, header_name="diagnostic", column_names=["value"]
    )
    summary.write_csv(output)
    return output

from pathlib import Path
import json

import numpy as np
import pandas as pd
import polars as pl

def _scalar(frame: pl.LazyFrame, expression: pl.Expr) -> int | float | None:
    value = frame.select(expression).pipe(_safe_collect).item()
    if value is None:
        return None
    if isinstance(value, (np.integer, int)):
        return int(value)
    if isinstance(value, (np.floating, float)):
        return float(value)
    return value

def _write_metric_table(rows: list[dict], path: Path) -> Path:
    pd.DataFrame(rows).to_csv(path, index=False)
    return path

PAPER_POOLED_CODE_LABEL = "__POOLED_BELOW_THRESHOLD__"

def _pool_small_code_cells(
    rehab_long: pl.LazyFrame,
    threshold: int,
    key_columns: list[str],
    include_year_span: bool,
) -> pl.DataFrame:
    group_keys = [*key_columns, "rehabilitation_diagnosis_code"]
    aggregations = [
        pl.len().alias("rehabilitation_events"),
        pl.col("simple_id").n_unique().alias("unique_people"),
    ]
    if include_year_span:
        aggregations += [
            pl.col("ja").min().alias("first_observed_year"),
            pl.col("ja").max().alias("last_observed_year"),
        ]
    counts = rehab_long.group_by(group_keys).agg(aggregations).pipe(_safe_collect)
    empty_extras = [
        pl.lit(None, dtype=pl.Int64).alias("n_codes_pooled"),
        pl.lit(None, dtype=pl.Utf8).alias("disclosure_note"),
    ]
    if threshold <= 0 or counts.height == 0:
        return counts.with_columns(empty_extras)
    label_rows: list[dict] = []
    key_values = counts.select(key_columns).unique().rows() if key_columns else [()]
    for key in key_values:
        subset = counts
        for column, value in zip(key_columns, key):
            subset = subset.filter(pl.col(column) == value)
        ordered = subset.sort([
            "unique_people", "rehabilitation_events", "rehabilitation_diagnosis_code"
        ])
        pooled_codes = (
            ordered.filter(pl.col("unique_people") < threshold)
            .get_column("rehabilitation_diagnosis_code").to_list()
        )
        retained = ordered.filter(pl.col("unique_people") >= threshold)
        if len(pooled_codes) == 1 and retained.height > 0:
            pooled_codes.append(retained.get_column("rehabilitation_diagnosis_code")[0])
        for code in ordered.get_column("rehabilitation_diagnosis_code").to_list():
            label_rows.append({
                **dict(zip(key_columns, key)),
                "rehabilitation_diagnosis_code": code,
                "final_code_label": (
                    PAPER_POOLED_CODE_LABEL if code in pooled_codes else code
                ),
            })
    label_map = pl.DataFrame(label_rows).with_columns([
        pl.col(column).cast(counts.schema[column]) for column in group_keys
    ])
    relabelled = rehab_long.join(label_map.lazy(), on=group_keys, how="left").with_columns(
        pl.col("final_code_label").fill_null(pl.col("rehabilitation_diagnosis_code"))
    )
    final = (
        relabelled.group_by([*key_columns, "final_code_label"])
        .agg(aggregations)
        .rename({"final_code_label": "rehabilitation_diagnosis_code"})
        .pipe(_safe_collect)
    )
    is_pooled = pl.col("rehabilitation_diagnosis_code") == PAPER_POOLED_CODE_LABEL
    if key_columns:
        pooled_sizes = (
            label_map.filter(pl.col("final_code_label") == PAPER_POOLED_CODE_LABEL)
            .group_by(key_columns)
            .agg(pl.len().alias("n_codes_pooled"))
        )
        final = final.join(pooled_sizes, on=key_columns, how="left").with_columns(
            pl.when(is_pooled).then(pl.col("n_codes_pooled"))
            .otherwise(pl.lit(None)).alias("n_codes_pooled")
        )
    else:
        n_pooled_codes = int(
            (label_map.get_column("final_code_label") == PAPER_POOLED_CODE_LABEL).sum()
        )
        final = final.with_columns(
            pl.when(is_pooled).then(pl.lit(n_pooled_codes))
            .otherwise(pl.lit(None)).alias("n_codes_pooled")
        )
    value_columns = ["rehabilitation_events", "unique_people"]
    if include_year_span:
        value_columns += ["first_observed_year", "last_observed_year"]
    withheld = is_pooled & (pl.col("unique_people") < threshold)
    final = final.with_columns([
        pl.when(withheld).then(pl.lit(None)).otherwise(pl.col(column)).alias(column)
        for column in value_columns
    ] + [
        pl.when(withheld)
        .then(pl.lit("pooled bucket still below threshold; counts withheld"))
        .otherwise(pl.lit(None, dtype=pl.Utf8))
        .alias("disclosure_note")
    ])
    return final

def _paper_summary_signature(
    reporting: PaperReportingConfig,
    input_paths: list[str | Path],
) -> tuple[str, dict]:
    payload = {
        "reporting": reporting.to_dict(),
        "inputs": [],
    }
    for raw_path in input_paths:
        path = Path(raw_path)
        stat = path.stat()
        payload["inputs"].append({
            "path": str(path),
            "size": int(stat.st_size),
            "mtime": float(stat.st_mtime),
        })
    canonical = json.dumps(payload, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest(), payload

def _small_cell(value: int | float | None, threshold: int) -> bool:
    if value is None or threshold <= 0:
        return False
    numeric = float(value)
    return 0.0 <= numeric < float(threshold)

def _release_binary_allowed(
    count_one: int,
    count_zero: int,
    threshold: int,
) -> bool:
    if threshold <= 0:
        return True
    return count_one >= threshold and count_zero >= threshold

def build_paper_summary_tables(
    config: PipelineConfig,
    reporting: PaperReportingConfig,
    panel_path: str | Path,
    treated_path: str | Path,
    controls_path: str | Path,
    matches_path: str | Path,
    scores_path: str | Path,
    filter_audit_path: str | Path,
    balance_summary_path: str | Path,
    force: bool = False,
) -> dict[str, Path]:
    reporting.validate()
    output_dir = config.diagnostics_dir / "paper_summary_tables"
    output_dir.mkdir(parents=True, exist_ok=True)
    paths = {
        "sample_overview": output_dir / "paper_sample_overview.csv",
        "descriptive_statistics": output_dir / "paper_descriptive_statistics.csv",
        "annual_panel": output_dir / "paper_annual_panel_counts.csv",
        "divorce_cohorts": output_dir / "paper_divorce_and_matching_by_t0.csv",
        "rehab_codes": output_dir / "paper_rehabilitation_codes.csv",
        "rehab_codes_by_year": output_dir / "paper_rehabilitation_codes_by_year.csv",
        "filter_attrition": output_dir / "paper_filter_attrition.csv",
        "matching_overall": output_dir / "paper_matching_overall.csv",
        "matching_by_year": output_dir / "paper_matching_by_year.csv",
        "matched_vs_unmatched_treated": output_dir / "paper_matched_vs_unmatched_treated.csv",
        "repeated_person_overlap": output_dir / "paper_repeated_person_overlap.csv",
        "propensity_distribution": output_dir / "paper_propensity_score_distribution.csv",
        "propensity_overlap": output_dir / "paper_propensity_score_overlap_by_t0.csv",
        "balance_overview": output_dir / "paper_balance_overview.csv",
        "limitations": output_dir / "paper_summary_limitations.json",
        "manifest": output_dir / "paper_summary_manifest.json",
        "signature": output_dir / "paper_summary_signature.json",
    }
    exact_matchability_path = config.diagnostics_dir / (
        f"matched_vs_unmatched_treated_internal_{config.control_pool}_lag{config.lag_depth}.csv"
    )
    overlap_detail_path = config.diagnostics_dir / (
        f"repeated_person_overlap_detail_{config.control_pool}_lag{config.lag_depth}.csv"
    )
    cohort_internal_path = config.diagnostics_dir / (
        f"divorce_and_matching_by_t0_internal_{config.control_pool}_lag{config.lag_depth}.csv"
    )
    matching_overall_internal_path = config.diagnostics_dir / (
        f"matching_overall_internal_{config.control_pool}_lag{config.lag_depth}.csv"
    )
    summary_signature, signature_payload = _paper_summary_signature(
        reporting,
        [
            panel_path, treated_path, controls_path, matches_path, scores_path,
            filter_audit_path, balance_summary_path,
        ],
    )
    internal_outputs = [
        exact_matchability_path, overlap_detail_path, cohort_internal_path,
        matching_overall_internal_path,
    ]
    if (
        not force
        and all(path.exists() for path in paths.values())
        and all(path.exists() for path in internal_outputs)
    ):
        previous = json.loads(paths["signature"].read_text(encoding="utf-8"))
        if previous.get("signature") == summary_signature:
            return paths
    panel = pl.scan_parquet(panel_path)
    treated = pl.scan_parquet(treated_path)
    controls = pl.scan_parquet(controls_path)
    matches = pl.scan_parquet(matches_path)
    scores = pl.scan_parquet(scores_path)
    report_threshold = reporting.minimum_cell_people
    n_person_years = _scalar(panel, pl.len())
    n_people = _scalar(panel, pl.col("simple_id").n_unique())
    first_year = _scalar(panel, pl.col("ja").min())
    last_year = _scalar(panel, pl.col("ja").max())
    all_first_divorces = panel.filter(pl.col("first_divorce_this_year") == 1)
    qualifying_first_divorces = panel.filter(
        pl.col("qualifying_first_divorce_this_year") == 1
    )
    any_rehab = panel.filter(pl.col("rehab_starts_this_year") > 0)
    any_msk = panel.filter(pl.col("msk_starts_this_year") > 0)
    any_mental = panel.filter(pl.col("mental_health_rehab_starts_this_year") > 0)
    overview_rows = [
        {"section": "source_panel", "metric": "configured_sample_tag", "value": config.sample_tag, "unit": "text"},
        {"section": "source_panel", "metric": "data_profile", "value": config.data_profile, "unit": "text"},
        {"section": "source_panel", "metric": "person_year_rows", "value": n_person_years, "unit": "person-years"},
        {"section": "source_panel", "metric": "unique_people", "value": n_people, "unit": "people"},
        {"section": "source_panel", "metric": "first_observed_year", "value": first_year, "unit": "calendar year"},
        {"section": "source_panel", "metric": "last_observed_year", "value": last_year, "unit": "calendar year"},
        {"section": "divorce", "metric": "people_with_first_observed_divorce_any_year", "value": _scalar(all_first_divorces, pl.col("simple_id").n_unique()), "unit": "people"},
        {"section": "divorce", "metric": "people_with_qualifying_first_marriage_divorce_any_year", "value": _scalar(qualifying_first_divorces, pl.col("simple_id").n_unique()), "unit": "people"},
        {"section": "rehabilitation", "metric": "completed_medical_rehabilitation_events", "value": _scalar(panel, pl.col("rehab_starts_this_year").sum()), "unit": "rehabilitation starts"},
        {"section": "rehabilitation", "metric": "people_with_any_completed_medical_rehabilitation", "value": _scalar(any_rehab, pl.col("simple_id").n_unique()), "unit": "people"},
        {"section": "rehabilitation", "metric": "musculoskeletal_rehabilitation_events", "value": _scalar(panel, pl.col("msk_starts_this_year").sum()), "unit": "rehabilitation starts"},
        {"section": "rehabilitation", "metric": "people_with_any_musculoskeletal_rehabilitation", "value": _scalar(any_msk, pl.col("simple_id").n_unique()), "unit": "people"},
        {"section": "rehabilitation", "metric": "mental_health_rehabilitation_events", "value": _scalar(panel, pl.col("mental_health_rehab_starts_this_year").sum()), "unit": "rehabilitation starts"},
        {"section": "rehabilitation", "metric": "people_with_any_mental_health_rehabilitation", "value": _scalar(any_mental, pl.col("simple_id").n_unique()), "unit": "people"},
    ]
    _write_metric_table(overview_rows, paths["sample_overview"])
    build_descriptive_statistics_table(
        config, treated_path, controls_path, matches_path,
        paths["descriptive_statistics"], force=force,
    )
    annual_count_columns = [
        "person_year_rows", "unique_people", "first_observed_divorces",
        "qualifying_first_marriage_divorces", "medical_rehabilitation_events",
        "people_with_medical_rehabilitation", "msk_rehabilitation_events",
        "people_with_msk_rehabilitation", "mental_health_rehabilitation_events",
        "recorded_deaths_in_year",
    ]
    annual_by_row_year = panel.group_by("ja").agg([
        pl.len().alias("person_year_rows"),
        pl.col("simple_id").n_unique().alias("unique_people"),
        pl.col("first_divorce_this_year").sum().alias("first_observed_divorces"),
        pl.col("qualifying_first_divorce_this_year").sum().alias(
            "qualifying_first_marriage_divorces"
        ),
        pl.col("rehab_starts_this_year").sum().alias("medical_rehabilitation_events"),
        pl.col("simple_id").filter(pl.col("rehab_starts_this_year") > 0)
        .n_unique().alias("people_with_medical_rehabilitation"),
        pl.col("msk_starts_this_year").sum().alias("msk_rehabilitation_events"),
        pl.col("simple_id").filter(pl.col("msk_starts_this_year") > 0)
        .n_unique().alias("people_with_msk_rehabilitation"),
        pl.col("mental_health_rehab_starts_this_year").sum().alias(
            "mental_health_rehabilitation_events"
        ),
        # Kept only as an audit trail against the old (buggy) definition: this counts a
        # death only in a year where the person ALSO happens to have a person-year row.
        # Per the panel-coverage diagnostics, most recorded deaths (rtwf_jjjj) occur
        # strictly after a person's last annual record -- i.e. death does not require an
        # annual record -- so this undercounts substantially and must not be quoted as
        # "the" annual death count. See deaths_by_death_year below for the corrected count.
        (pl.col("rtwf_jjjj") == pl.col("ja")).sum().alias("recorded_deaths_in_year"),
    ])
    # Corrected death count: take each person's death year exactly once (person-level
    # attribute, per CANONICAL_DEFINITIONS / death_measure elsewhere in this file), then
    # count by that year directly. This deliberately does NOT require the person to also
    # have a person-year row in their death year -- a death that arrives after someone's
    # last observed economic-activity record is still a real death in that calendar year.
    death_year_per_person = (
        panel.group_by("simple_id")
        .agg(pl.col("rtwf_jjjj").drop_nulls().max().alias("death_year"))
        .filter(pl.col("death_year").is_not_null())
    )
    deaths_by_death_year = (
        death_year_per_person
        .group_by("death_year")
        .agg(pl.len().alias("deaths_by_death_year"))
    )
    # An outer join (not a left join) matters here: a death year with zero ordinary
    # person-year rows anywhere in the panel (everyone who died that year had already
    # stopped appearing beforehand) must still surface as its own row, or that year's
    # deaths would silently vanish from the table rather than just being undercounted.
    annual = (
        annual_by_row_year
        .join(deaths_by_death_year, left_on="ja", right_on="death_year", how="outer")
        .with_columns(pl.coalesce(["ja", "death_year"]).alias("ja"))
        .drop("death_year")
        .with_columns([
            pl.col(column).fill_null(0) for column in [*annual_count_columns, "deaths_by_death_year"]
        ])
        .sort("ja")
        .pipe(_safe_collect)
    )
    annual.write_csv(paths["annual_panel"])
    year_end = int(config.year_cap if config.year_cap is not None else last_year)
    cohort = pl.DataFrame({"t0": list(range(int(config.year_start), year_end + 1))})
    divorce_counts = (
        panel.filter(
            (pl.col("ja") >= config.year_start)
            & (pl.col("ja") <= year_end)
        )
        .group_by("ja")
        .agg([
            pl.col("first_divorce_this_year").sum().alias("first_observed_divorces"),
            pl.col("qualifying_first_divorce_this_year").sum().alias(
                "qualifying_first_marriage_divorces"
            ),
        ])
        .rename({"ja": "t0"})
        .pipe(_safe_collect)
    )
    treated_counts = (
        treated.group_by("t0")
        .agg([
            pl.len().alias("eligible_treated_assignments"),
            pl.col("simple_id").n_unique().alias("eligible_treated_people"),
        ])
        .pipe(_safe_collect)
    )
    control_counts = (
        controls.group_by("t0")
        .agg([
            pl.len().alias("eligible_control_assignments"),
            pl.col("simple_id").n_unique().alias("eligible_control_people"),
        ])
        .pipe(_safe_collect)
    )
    matched_counts = (
        matches.group_by("t0")
        .agg([
            pl.len().alias("matched_pairs"),
            pl.col("t_id").n_unique().alias("matched_treated_people"),
            pl.col("c_id").n_unique().alias("matched_control_people"),
            pl.col("abs_ps_diff").mean().alias("mean_abs_ps_diff"),
            pl.col("abs_ps_diff").median().alias("median_abs_ps_diff"),
            pl.col("abs_ps_diff").max().alias("max_abs_ps_diff"),
        ])
        .pipe(_safe_collect)
    )
    cohort = cohort.with_columns(pl.col("t0").cast(pl.Int64))
    divorce_counts, treated_counts, control_counts, matched_counts = (
        frame.with_columns(pl.col("t0").cast(pl.Int64))
        for frame in (divorce_counts, treated_counts, control_counts, matched_counts)
    )
    cohort = (
        cohort.join(divorce_counts, on="t0", how="left")
        .join(treated_counts, on="t0", how="left")
        .join(control_counts, on="t0", how="left")
        .join(matched_counts, on="t0", how="left")
    )
    integer_columns = [
        "first_observed_divorces", "qualifying_first_marriage_divorces",
        "eligible_treated_assignments", "eligible_treated_people",
        "eligible_control_assignments", "eligible_control_people", "matched_pairs",
        "matched_treated_people", "matched_control_people",
    ]
    cohort = cohort.with_columns([
        pl.col(column).fill_null(0).cast(pl.Int64) for column in integer_columns
    ]).with_columns([
        (pl.col("eligible_treated_people") - pl.col("matched_treated_people"))
        .alias("unmatched_treated_people"),
        pl.when(pl.col("eligible_treated_people") > 0)
        .then(pl.col("matched_treated_people") / pl.col("eligible_treated_people"))
        .otherwise(None)
        .alias("match_rate"),
    ]).sort("t0")
    cohort_exact = cohort.to_pandas()
    cohort_exact.to_csv(cohort_internal_path, index=False)
    cohort_release = cohort_exact.copy()
    cohort_release["disclosure_note"] = None
    if reporting.protect_matchability_cells and report_threshold > 0:
        count_columns = [
            "first_observed_divorces", "qualifying_first_marriage_divorces",
            "eligible_treated_assignments", "eligible_treated_people",
            "eligible_control_assignments", "eligible_control_people",
            "matched_pairs", "matched_treated_people", "matched_control_people",
            "unmatched_treated_people",
        ]
        for index, row in cohort_exact.iterrows():
            notes: list[str] = []
            unmatched = int(row.get("unmatched_treated_people", 0) or 0)
            matched = int(row.get("matched_treated_people", 0) or 0)
            if unmatched < report_threshold:
                for column in (
                    "eligible_treated_assignments", "eligible_treated_people",
                    "unmatched_treated_people", "match_rate",
                ):
                    cohort_release.at[index, column] = np.nan
                notes.append("eligible/unmatched treated cells complementarily withheld")
            if matched < report_threshold:
                for column in (
                    "matched_pairs", "matched_treated_people", "matched_control_people",
                    "match_rate",
                ):
                    cohort_release.at[index, column] = np.nan
                notes.append("matched cells below provisional threshold")
            for column in count_columns:
                value = row.get(column)
                if pd.notna(value) and _small_cell(value, report_threshold):
                    cohort_release.at[index, column] = np.nan
                    notes.append(f"{column} withheld")
            cohort_release.at[index, "disclosure_note"] = (
                "; ".join(sorted(set(notes))) if notes else None
            )
    cohort_release.to_csv(paths["divorce_cohorts"], index=False)
    slot_frames: list[pl.LazyFrame] = []
    for slot in (1, 2):
        slot_frames.append(
            panel.filter(pl.col(f"rehab_start_slot{slot}") == 1).select([
                "simple_id", "ja",
                pl.lit(slot, dtype=pl.Int8).alias("rehab_slot"),
                pl.col(f"rehab_diagnosis_code_slot{slot}_this_year")
                .fill_null("__MISSING__")
                .alias("rehabilitation_diagnosis_code"),
            ])
        )
    rehab_long = pl.concat(slot_frames, how="vertical")
    total_rehab_events = _scalar(rehab_long, pl.len()) or 0
    diagnosis_threshold = (
        reporting.minimum_cell_people if reporting.pool_small_diagnosis_codes else 0
    )
    rehab_codes = _pool_small_code_cells(
        rehab_long,
        diagnosis_threshold,
        key_columns=[],
        include_year_span=True,
    )
    share_expression = (
        (pl.col("rehabilitation_events") / total_rehab_events)
        if total_rehab_events
        else pl.lit(None, dtype=pl.Float64)
    )
    rehab_codes = rehab_codes.with_columns(
        share_expression.alias("share_of_rehabilitation_events")
    ).sort("rehabilitation_events", descending=True, nulls_last=True)
    rehab_codes.write_csv(paths["rehab_codes"])
    rehab_codes_by_year = _pool_small_code_cells(
        rehab_long,
        diagnosis_threshold,
        key_columns=["ja"],
        include_year_span=False,
    ).sort(["ja", "rehabilitation_events"], descending=[False, True], nulls_last=True)
    rehab_codes_by_year.write_csv(paths["rehab_codes_by_year"])
    attrition = pd.read_csv(filter_audit_path)
    attrition["removed_unique_people_since_previous"] = (
        attrition.groupby("group", sort=False)["n_persons"].shift(1)
        - attrition["n_persons"]
    )
    attrition["count_unit_note"] = np.where(
        attrition["group"].eq("controls"),
        "n_rows are eligible person-t0 assignments; the same person may appear in more than one year before matching",
        "n_rows are treated person-t0 assignments and should equal people within a stage",
    )
    attrition["disclosure_note"] = None
    if reporting.protect_matchability_cells and report_threshold > 0:
        eligible_treated_for_release = int(_scalar(treated, pl.len()) or 0)
        matched_treated_for_release = int(_scalar(matches, pl.len()) or 0)
        unmatched_for_release = max(
            eligible_treated_for_release - matched_treated_for_release, 0
        )
        if unmatched_for_release < report_threshold:
            treated_indices = attrition.index[attrition["group"].eq("treated")].tolist()
            if treated_indices:
                final_index = treated_indices[-1]
                for column in (
                    "n_rows", "n_persons", "removed_since_previous",
                    "removed_unique_people_since_previous",
                ):
                    if column in attrition.columns:
                        attrition.at[final_index, column] = np.nan
                attrition.at[final_index, "disclosure_note"] = (
                    "final eligible-treated count complementarily withheld because "
                    "unmatched treated count is below the provisional threshold"
                )
    attrition.to_csv(paths["filter_attrition"], index=False)
    match_stats = matches.select([
        pl.len().alias("matched_pairs"),
        pl.col("t_id").n_unique().alias("unique_matched_treated"),
        pl.col("c_id").n_unique().alias("unique_matched_controls"),
        pl.col("match_group").n_unique().alias("unique_match_groups"),
        pl.col("abs_ps_diff").mean().alias("mean_abs_ps_diff"),
        pl.col("abs_ps_diff").median().alias("median_abs_ps_diff"),
        pl.col("abs_ps_diff").quantile(0.90).alias("p90_abs_ps_diff"),
        pl.col("abs_ps_diff").quantile(0.95).alias("p95_abs_ps_diff"),
        pl.col("abs_ps_diff").max().alias("max_abs_ps_diff"),
    ]).pipe(_safe_collect).row(0, named=True)
    eligible_treated = _scalar(treated, pl.len())
    spec = f"{config.control_pool}_lag{config.lag_depth}"
    matching_audit_path = config.diagnostics_dir / f"matching_audit_{spec}.csv"
    matching_audit = pl.read_csv(matching_audit_path)
    matching_rows = [
        {"metric": "eligible_treated_assignments", "value": eligible_treated, "unit": "treated person-t0 assignments"},
        {"metric": "matched_pairs", "value": int(match_stats["matched_pairs"]), "unit": "pairs"},
        {"metric": "unique_matched_treated", "value": int(match_stats["unique_matched_treated"]), "unit": "people"},
        {"metric": "unique_matched_controls", "value": int(match_stats["unique_matched_controls"]), "unit": "people"},
        {"metric": "unmatched_treated", "value": int(eligible_treated - match_stats["unique_matched_treated"]), "unit": "people"},
        {"metric": "overall_match_rate", "value": float(match_stats["unique_matched_treated"] / max(eligible_treated, 1)), "unit": "proportion"},
        {"metric": "treated_without_exact_control", "value": int(matching_audit.get_column("n_without_exact_control").sum()), "unit": "people"},
        {"metric": "treated_unmatched_after_exact_and_caliper", "value": int(matching_audit.get_column("n_unmatched_after_exact_and_caliper").sum()), "unit": "people"},
        {"metric": "controls_reused", "value": int(match_stats["matched_pairs"] - match_stats["unique_matched_controls"]), "unit": "duplicate uses"},
        {"metric": "caliper", "value": float(config.caliper), "unit": "absolute propensity-score distance"},
        {"metric": "mean_abs_ps_diff", "value": float(match_stats["mean_abs_ps_diff"]), "unit": "absolute propensity-score distance"},
        {"metric": "median_abs_ps_diff", "value": float(match_stats["median_abs_ps_diff"]), "unit": "absolute propensity-score distance"},
        {"metric": "p90_abs_ps_diff", "value": float(match_stats["p90_abs_ps_diff"]), "unit": "absolute propensity-score distance"},
        {"metric": "p95_abs_ps_diff", "value": float(match_stats["p95_abs_ps_diff"]), "unit": "absolute propensity-score distance"},
        {"metric": "max_abs_ps_diff", "value": float(match_stats["max_abs_ps_diff"]), "unit": "absolute propensity-score distance"},
    ]
    _write_metric_table(matching_rows, matching_overall_internal_path)
    matching_release_rows = [dict(row, disclosure_note=None) for row in matching_rows]
    if reporting.protect_matchability_cells and report_threshold > 0:
        unmatched_total = int(eligible_treated - match_stats["unique_matched_treated"])
        direct_person_metrics = {
            "eligible_treated_assignments",
            "matched_pairs",
            "unique_matched_treated",
            "unique_matched_controls",
            "unmatched_treated",
            "treated_without_exact_control",
            "treated_unmatched_after_exact_and_caliper",
        }
        for row in matching_release_rows:
            metric = row["metric"]
            value = row["value"]
            if metric in direct_person_metrics and _small_cell(value, report_threshold):
                row["value"] = None
                row["disclosure_note"] = "count below provisional reporting threshold"
        if unmatched_total < report_threshold:
            for row in matching_release_rows:
                if row["metric"] in {
                    "eligible_treated_assignments", "unmatched_treated",
                    "overall_match_rate",
                }:
                    row["value"] = None
                    row["disclosure_note"] = (
                        "complementarily withheld because unmatched treated count is below threshold"
                    )
    _write_metric_table(matching_release_rows, paths["matching_overall"])
    matching_by_year_exact = matching_audit.to_pandas()
    matching_by_year_release = matching_by_year_exact.copy()
    matching_by_year_release["disclosure_note"] = None
    if reporting.protect_matchability_cells and report_threshold > 0:
        count_columns = [
            "n_treated", "n_controls_available_after_prior_year_use", "n_matched",
            "n_without_exact_control", "n_unmatched_after_exact_and_caliper",
            "n_controls", "propensity_fit_rows", "controls_used_to_fit_propensity",
        ]
        for index, row in matching_by_year_exact.iterrows():
            notes: list[str] = []
            n_treated_year = int(row.get("n_treated", 0) or 0)
            n_matched_year = int(row.get("n_matched", 0) or 0)
            n_unmatched_year = max(n_treated_year - n_matched_year, 0)
            if n_unmatched_year < report_threshold:
                for column in ("n_treated", "match_rate"):
                    if column in matching_by_year_release.columns:
                        matching_by_year_release.at[index, column] = np.nan
                notes.append("treated total/rate complementarily withheld")
            for column in count_columns:
                if column not in matching_by_year_release.columns:
                    continue
                value = row.get(column)
                if pd.notna(value) and _small_cell(value, report_threshold):
                    matching_by_year_release.at[index, column] = np.nan
                    notes.append(f"{column} withheld")
            matching_by_year_release.at[index, "disclosure_note"] = (
                "; ".join(sorted(set(notes))) if notes else None
            )
    matching_by_year_release.to_csv(paths["matching_by_year"], index=False)
    features = resolve_features(config, set(pl.read_parquet_schema(treated_path)))
    match_keys = matches.select([pl.col("t_id").alias("simple_id"), "t0"])
    matched_treated = treated.join(
        match_keys, on=["simple_id", "t0"], how="semi"
    )
    unmatched_treated = treated.join(
        match_keys, on=["simple_id", "t0"], how="anti"
    )
    n_matched_treated = int(_scalar(matched_treated, pl.len()) or 0)
    n_unmatched_treated = int(_scalar(unmatched_treated, pl.len()) or 0)
    comparison_columns = list(dict.fromkeys([
        *features.numeric, *features.binary, *features.categorical,
        *features.exact, "t0",
    ]))
    matched_pd = _safe_collect(
        matched_treated.select(comparison_columns)
    ).to_pandas()
    unmatched_pd = _safe_collect(
        unmatched_treated.select(comparison_columns)
    ).to_pandas()
    internal_rows: list[dict] = []
    release_rows: list[dict] = []
    threshold = report_threshold
    protect_cells = reporting.protect_matchability_cells and threshold > 0
    group_too_small = (
        protect_cells
        and (n_matched_treated < threshold or n_unmatched_treated < threshold)
    )
    group_note = None
    if n_unmatched_treated == 0:
        group_note = "no unmatched treated in this specification"
    elif group_too_small:
        group_note = (
            f"at least one comparison group is below minimum_cell_people={threshold}; "
            "paper-facing covariate values withheld"
        )
    def _internal_row(
        variable: str,
        level: str | None,
        variable_type: str,
        matched_value: float | None,
        unmatched_value: float | None,
        smd: float | None,
        matched_count: int | None,
        unmatched_count: int | None,
        matched_complement_count: int | None = None,
        unmatched_complement_count: int | None = None,
        matched_missing_rate: float | None = None,
        unmatched_missing_rate: float | None = None,
    ) -> None:
        internal_rows.append({
            "variable": variable,
            "level": level,
            "variable_type": variable_type,
            "matched_value": matched_value,
            "unmatched_value": unmatched_value,
            "smd": smd,
            "matched_count": matched_count,
            "unmatched_count": unmatched_count,
            "matched_complement_count": matched_complement_count,
            "unmatched_complement_count": unmatched_complement_count,
            "matched_missing_rate": matched_missing_rate,
            "unmatched_missing_rate": unmatched_missing_rate,
            "n_matched_treated": n_matched_treated,
            "n_unmatched_treated": n_unmatched_treated,
        })
    def _release_row(
        source: dict,
        allowed: bool,
        disclosure_note: str | None,
        n_levels_pooled: int | None = None,
    ) -> None:
        release_rows.append({
            "variable": source["variable"],
            "level": source["level"],
            "variable_type": source["variable_type"],
            "matched_value": source["matched_value"] if allowed else None,
            "unmatched_value": source["unmatched_value"] if allowed else None,
            "smd": source["smd"] if allowed else None,
            "matched_count": source["matched_count"] if allowed else None,
            "unmatched_count": source["unmatched_count"] if allowed else None,
            "matched_complement_count": (
                source["matched_complement_count"] if allowed else None
            ),
            "unmatched_complement_count": (
                source["unmatched_complement_count"] if allowed else None
            ),
            "matched_missing_rate": (
                source["matched_missing_rate"] if allowed else None
            ),
            "unmatched_missing_rate": (
                source["unmatched_missing_rate"] if allowed else None
            ),
            "n_matched_treated": (
                n_matched_treated
                if not protect_cells or n_matched_treated >= threshold else None
            ),
            "n_unmatched_treated": (
                n_unmatched_treated
                if not protect_cells or n_unmatched_treated >= threshold else None
            ),
            "n_levels_pooled": n_levels_pooled,
            "disclosure_note": disclosure_note,
        })
    for variable in features.numeric:
        matched_values = pd.to_numeric(matched_pd[variable], errors="coerce")
        unmatched_values = pd.to_numeric(unmatched_pd[variable], errors="coerce")
        matched_nonmissing = int(matched_values.notna().sum())
        unmatched_nonmissing = int(unmatched_values.notna().sum())
        matched_missing = int(matched_values.isna().sum())
        unmatched_missing = int(unmatched_values.isna().sum())
        mean_m = float(matched_values.mean()) if matched_nonmissing else None
        mean_u = float(unmatched_values.mean()) if unmatched_nonmissing else None
        var_m = float(matched_values.var(ddof=0)) if matched_nonmissing else None
        var_u = float(unmatched_values.var(ddof=0)) if unmatched_nonmissing else None
        smd = _safe_smd(mean_m, var_m, mean_u, var_u)
        _internal_row(
            variable, None, "continuous", mean_m, mean_u, smd,
            matched_nonmissing, unmatched_nonmissing,
            matched_missing, unmatched_missing,
            matched_missing / max(n_matched_treated, 1),
            unmatched_missing / max(n_unmatched_treated, 1),
        )
        source = internal_rows[-1]
        allowed = (
            not group_too_small
            and (
                not protect_cells
                or (
                    matched_nonmissing >= threshold
                    and unmatched_nonmissing >= threshold
                )
            )
        )
        note = group_note
        if note is None and not allowed:
            note = "non-missing analytic cell below provisional threshold; values withheld"
        _release_row(source, allowed, note)
        missing_rate_m = matched_missing / max(n_matched_treated, 1)
        missing_rate_u = unmatched_missing / max(n_unmatched_treated, 1)
        missing_smd = _safe_smd(
            missing_rate_m, missing_rate_m * (1 - missing_rate_m),
            missing_rate_u, missing_rate_u * (1 - missing_rate_u),
        )
        _internal_row(
            f"{variable}__missing", "missing", "binary_missingness",
            missing_rate_m, missing_rate_u, missing_smd,
            matched_missing, unmatched_missing,
            matched_nonmissing, unmatched_nonmissing,
        )
        source = internal_rows[-1]
        allowed = (
            not group_too_small
            and (
                not protect_cells
                or (
                    _release_binary_allowed(
                        matched_missing, matched_nonmissing, threshold
                    )
                    and _release_binary_allowed(
                        unmatched_missing, unmatched_nonmissing, threshold
                    )
                )
            )
        )
        note = group_note
        if note is None and not allowed:
            note = "binary missingness cell or complement below provisional threshold"
        _release_row(source, allowed, note)
    for variable in features.binary:
        matched_values = pd.to_numeric(matched_pd[variable], errors="coerce")
        unmatched_values = pd.to_numeric(unmatched_pd[variable], errors="coerce")
        matched_valid = matched_values.dropna()
        unmatched_valid = unmatched_values.dropna()
        matched_one = int((matched_valid == 1).sum())
        unmatched_one = int((unmatched_valid == 1).sum())
        matched_zero = int((matched_valid == 0).sum())
        unmatched_zero = int((unmatched_valid == 0).sum())
        p_m = float(matched_valid.mean()) if len(matched_valid) else None
        p_u = float(unmatched_valid.mean()) if len(unmatched_valid) else None
        smd = _safe_smd(
            p_m, p_m * (1 - p_m) if p_m is not None else None,
            p_u, p_u * (1 - p_u) if p_u is not None else None,
        )
        _internal_row(
            variable, "1", "binary", p_m, p_u, smd,
            matched_one, unmatched_one, matched_zero, unmatched_zero,
            float(matched_values.isna().mean()),
            float(unmatched_values.isna().mean()),
        )
        source = internal_rows[-1]
        allowed = (
            not group_too_small
            and (
                not protect_cells
                or (
                    _release_binary_allowed(matched_one, matched_zero, threshold)
                    and _release_binary_allowed(unmatched_one, unmatched_zero, threshold)
                )
            )
        )
        note = group_note
        if note is None and not allowed:
            note = "binary cell or complement below provisional threshold"
        _release_row(source, allowed, note)
    categorical_variables = list(dict.fromkeys([
        *features.categorical, *features.exact, "t0",
    ]))
    pooled_label = "__POOLED_LEVELS_BELOW_THRESHOLD__"
    for variable in categorical_variables:
        matched_levels = matched_pd[variable].astype("string").fillna("__MISSING__")
        unmatched_levels = unmatched_pd[variable].astype("string").fillna("__MISSING__")
        counts_m = matched_levels.value_counts(dropna=False).to_dict()
        counts_u = unmatched_levels.value_counts(dropna=False).to_dict()
        levels = sorted(set(counts_m) | set(counts_u), key=str)
        for level in levels:
            count_m = int(counts_m.get(level, 0))
            count_u = int(counts_u.get(level, 0))
            p_m = count_m / max(n_matched_treated, 1)
            p_u = count_u / max(n_unmatched_treated, 1)
            _internal_row(
                variable, str(level), "categorical_level", p_m, p_u,
                _safe_smd(p_m, p_m * (1 - p_m), p_u, p_u * (1 - p_u)),
                count_m, count_u,
                n_matched_treated - count_m,
                n_unmatched_treated - count_u,
            )
        pooled_levels: list[object] = []
        if protect_cells and not group_too_small:
            pooled_levels = [
                level for level in levels
                if int(counts_m.get(level, 0)) < threshold
                or int(counts_u.get(level, 0)) < threshold
            ]
            retained_levels = [level for level in levels if level not in pooled_levels]
            if len(pooled_levels) == 1 and retained_levels:
                retained_levels.sort(key=lambda level: (
                    min(int(counts_m.get(level, 0)), int(counts_u.get(level, 0))),
                    int(counts_m.get(level, 0)) + int(counts_u.get(level, 0)),
                    str(level),
                ))
                pooled_levels.append(retained_levels[0])
        final_levels = [level for level in levels if level not in pooled_levels]
        if pooled_levels:
            final_levels.append(pooled_label)
        for final_level in final_levels:
            source_levels = pooled_levels if final_level == pooled_label else [final_level]
            count_m = int(sum(int(counts_m.get(level, 0)) for level in source_levels))
            count_u = int(sum(int(counts_u.get(level, 0)) for level in source_levels))
            p_m = count_m / max(n_matched_treated, 1)
            p_u = count_u / max(n_unmatched_treated, 1)
            release_source = {
                "variable": variable,
                "level": str(final_level),
                "variable_type": "categorical_level",
                "matched_value": p_m,
                "unmatched_value": p_u,
                "smd": _safe_smd(
                    p_m, p_m * (1 - p_m), p_u, p_u * (1 - p_u)
                ),
                "matched_count": count_m,
                "unmatched_count": count_u,
                "matched_complement_count": n_matched_treated - count_m,
                "unmatched_complement_count": n_unmatched_treated - count_u,
                "matched_missing_rate": None,
                "unmatched_missing_rate": None,
            }
            allowed = (
                not group_too_small
                and (
                    not protect_cells
                    or (count_m >= threshold and count_u >= threshold)
                )
            )
            note = group_note
            if note is None and not allowed:
                note = "categorical cell below provisional threshold after pooling"
            elif final_level == pooled_label:
                note = (
                    f"{len(pooled_levels)} original levels pooled; source labels withheld"
                )
            _release_row(
                release_source, allowed, note,
                n_levels_pooled=(len(pooled_levels) if final_level == pooled_label else None),
            )
    _write_metric_table(internal_rows, exact_matchability_path)
    _write_metric_table(release_rows, paths["matched_vs_unmatched_treated"])
    assignment_roles = pl.concat([
        matches.select([
            pl.col("t_id").alias("simple_id"), "t0",
            pl.lit("treated").alias("assignment_role"),
            "match_group",
        ]),
        matches.select([
            pl.col("c_id").alias("simple_id"), "t0",
            pl.lit("control").alias("assignment_role"),
            "match_group",
        ]),
    ], how="vertical")
    overlap_detail = (
        assignment_roles.group_by("simple_id")
        .agg([
            pl.len().alias("n_matched_assignments"),
            (pl.col("assignment_role") == "treated").sum().alias("n_treated_assignments"),
            (pl.col("assignment_role") == "control").sum().alias("n_control_assignments"),
            pl.col("t0").filter(pl.col("assignment_role") == "treated")
            .min().alias("treated_t0"),
            pl.col("t0").filter(pl.col("assignment_role") == "control")
            .min().alias("first_control_t0"),
            pl.col("t0").filter(pl.col("assignment_role") == "control")
            .max().alias("last_control_t0"),
            pl.col("match_group").n_unique().alias("n_distinct_match_groups"),
        ])
        .with_columns([
            (
                (pl.col("n_treated_assignments") > 0)
                & (pl.col("n_control_assignments") > 0)
            ).alias("appears_in_both_roles"),
            (
                (pl.col("n_treated_assignments") > 0)
                & (pl.col("n_control_assignments") > 0)
                & (pl.col("last_control_t0") < pl.col("treated_t0"))
            ).alias("control_before_later_treatment"),
            (
                (pl.col("n_treated_assignments") > 0)
                & (pl.col("n_control_assignments") > 0)
                & (pl.col("last_control_t0") >= pl.col("treated_t0"))
            ).alias("control_not_strictly_before_treatment"),
        ])
        .with_columns(
            pl.when(pl.col("appears_in_both_roles"))
            .then(pl.col("treated_t0") - pl.col("last_control_t0"))
            .otherwise(None)
            .alias("years_from_last_control_assignment_to_treatment")
        )
        .sort(["appears_in_both_roles", "simple_id"], descending=[True, False])
        .pipe(_safe_collect)
    )
    overlap_detail.write_csv(overlap_detail_path)
    n_unique_people = int(overlap_detail.height)
    n_both_roles = int(overlap_detail.get_column("appears_in_both_roles").sum())
    n_control_then_treated = int(
        overlap_detail.get_column("control_before_later_treatment").sum()
    )
    n_invalid_order = int(
        overlap_detail.get_column("control_not_strictly_before_treatment").sum()
    )
    n_repeat_treated = int(
        (overlap_detail.get_column("n_treated_assignments") > 1).sum()
    )
    n_repeat_controls = int(
        (overlap_detail.get_column("n_control_assignments") > 1).sum()
    )
    dual_years = overlap_detail.filter(pl.col("appears_in_both_roles")).get_column(
        "years_from_last_control_assignment_to_treatment"
    )
    exact_overlap_rows = [
        {"metric": "matched_pair_assignments", "value": int(match_stats["matched_pairs"]), "unit": "pairs"},
        {"metric": "unique_people_across_both_roles", "value": n_unique_people, "unit": "people"},
        {"metric": "people_appearing_as_control_and_treated", "value": n_both_roles, "unit": "people"},
        {"metric": "people_control_before_later_treatment", "value": n_control_then_treated, "unit": "people"},
        {"metric": "people_control_not_strictly_before_treatment", "value": n_invalid_order, "unit": "people"},
        {"metric": "people_with_multiple_treated_assignments", "value": n_repeat_treated, "unit": "people"},
        {"metric": "people_with_multiple_control_assignments", "value": n_repeat_controls, "unit": "people"},
        {"metric": "maximum_matched_assignments_per_person", "value": int(overlap_detail.get_column("n_matched_assignments").max()), "unit": "assignments"},
        {"metric": "share_of_unique_people_in_both_roles", "value": n_both_roles / max(n_unique_people, 1), "unit": "proportion"},
        {"metric": "median_years_control_to_treatment", "value": (float(dual_years.median()) if len(dual_years) else None), "unit": "years"},
        {"metric": "minimum_years_control_to_treatment", "value": (int(dual_years.min()) if len(dual_years) else None), "unit": "years"},
    ]
    release_overlap_rows: list[dict] = []
    overlap_sensitive = (
        reporting.withhold_small_overlap_counts
        and threshold > 0
        and n_both_roles < threshold
    )
    for row in exact_overlap_rows:
        metric = row["metric"]
        value = row["value"]
        note = None
        allowed = True
        if reporting.withhold_small_overlap_counts and threshold > 0:
            if metric in {
                "people_appearing_as_control_and_treated",
                "people_control_before_later_treatment",
                "people_control_not_strictly_before_treatment",
                "people_with_multiple_treated_assignments",
                "people_with_multiple_control_assignments",
            } and _small_cell(value, threshold):
                allowed = False
                note = "count below provisional reporting threshold"
            if metric in {
                "share_of_unique_people_in_both_roles",
                "median_years_control_to_treatment",
                "minimum_years_control_to_treatment",
            } and overlap_sensitive:
                allowed = False
                note = "derived from a below-threshold dual-role group"
        release_overlap_rows.append({
            **row,
            "value": value if allowed else None,
            "disclosure_note": note,
        })
    _write_metric_table(release_overlap_rows, paths["repeated_person_overlap"])
    ps_distribution = (
        scores.with_columns(
            pl.when(pl.col("treated") == 1).then(pl.lit("treated"))
            .otherwise(pl.lit("controls")).alias("analysis_group")
        )
        .group_by(["t0", "analysis_group"])
        .agg([
            pl.len().alias("n"),
            pl.col("pscore").mean().alias("mean"),
            pl.col("pscore").std().alias("standard_deviation"),
            pl.col("pscore").min().alias("minimum"),
            pl.col("pscore").quantile(0.01).alias("p01"),
            pl.col("pscore").quantile(0.05).alias("p05"),
            pl.col("pscore").quantile(0.25).alias("p25"),
            pl.col("pscore").median().alias("median"),
            pl.col("pscore").quantile(0.75).alias("p75"),
            pl.col("pscore").quantile(0.95).alias("p95"),
            pl.col("pscore").quantile(0.99).alias("p99"),
            pl.col("pscore").max().alias("maximum"),
        ])
        .sort(["t0", "analysis_group"])
        .pipe(_safe_collect)
    )
    ps_distribution.write_csv(paths["propensity_distribution"])
    ps_overlap = (
        scores.group_by("t0")
        .agg([
            pl.col("pscore").filter(pl.col("treated") == 1).min().alias("treated_min"),
            pl.col("pscore").filter(pl.col("treated") == 1).max().alias("treated_max"),
            pl.col("pscore").filter(pl.col("treated") == 0).min().alias("control_min"),
            pl.col("pscore").filter(pl.col("treated") == 0).max().alias("control_max"),
        ])
        .with_columns([
            pl.max_horizontal("treated_min", "control_min").alias("overlap_lower"),
            pl.min_horizontal("treated_max", "control_max").alias("overlap_upper"),
        ])
        .with_columns(
            (pl.col("overlap_upper") >= pl.col("overlap_lower")).alias("ranges_overlap")
        )
        .sort("t0")
        .pipe(_safe_collect)
    )
    ps_overlap.write_csv(paths["propensity_overlap"])
    balance = pl.read_csv(balance_summary_path)
    balance_overview = (
        balance.group_by("sample")
        .agg([
            pl.len().alias("n_covariate_summaries"),
            pl.col("max_abs_smd").max().alias("maximum_abs_smd"),
            pl.col("max_abs_smd").mean().alias("mean_of_variable_max_abs_smd"),
            (pl.col("max_abs_smd") > config.smd_threshold).sum().alias(
                "variables_above_smd_threshold"
            ),
        ])
        .with_columns(pl.lit(config.smd_threshold).alias("smd_threshold"))
        .sort("sample")
    )
    balance_overview.write_csv(paths["balance_overview"])
    limitations = {
        "source_boundary": (
            "Counts begin with the already processed longitudinal parquet files. The original "
            "VA/RSD source files are unavailable to this pipeline, so exclusions made during "
            "upstream merging or preprocessing cannot be reconstructed from this run."
        ),
        "not_reproducible_from_current_source": [
            "cases removed because BASE and RTWF death information disagreed",
            "people removed upstream for three or more rehabilitation spells in one year",
            "the original pre-processed denominator before the current parquet files",
        ],
        "sample_fraction_warning": (
            f"These tables were generated from sample_tag '{config.sample_tag}' reading "
            f"'{config.raw_glob}'. Manuscript placeholders asking for the 20% dataset may "
            "only be filled from a run whose configured source is actually the 20% "
            "extract; verify this recorded tag and glob rather than trusting file names "
            "mentioned in prose."
        ),
        "annual_death_count_definition": (
            "paper_annual_panel_counts.csv now reports two different death counts; quote "
            "deaths_by_death_year, not recorded_deaths_in_year. deaths_by_death_year "
            "counts each person once, by their person-level death year (rtwf_jjjj), "
            "regardless of whether that person also has an ordinary person-year row in "
            "that year. recorded_deaths_in_year is kept only for backward-compatible "
            "auditing: it counts person-year rows whose calendar year equals the death "
            "year, so a death with no annual record in the death year was previously "
            "invisible there entirely (resolved guideline open question 14.2: the "
            "register does not reliably write a row at the death year -- per "
            "panel_coverage_diagnostics.csv, most recorded deaths occur strictly after "
            "the person's last annual record, so the old definition was not a minor "
            "undercount). Mortality follow-up and all mortality estimates were always "
            "unaffected by this: the death year enters the outcome builders as a "
            "person-level attribute, not "
            "through annual rows."
        ),
        "provisional_output_control": (
            "Paper-summary thresholds are reporting settings, not identification or "
            "estimation choices. The configured minimum_cell_people is "
            f"{reporting.minimum_cell_people}. Diagnosis codes are pooled when requested; "
            "matched-versus-unmatched categorical levels are pooled across both groups, "
            "and binary/continuous cells are withheld when their analytic cell or "
            "complement is below the threshold. Repeated-person overlap counts derived "
            "from a small dual-role group are withheld. These rules reduce avoidable "
            "disclosure but do not guarantee FDZ-RV release approval: totals, related "
            "tables, and the complete requested export must still be reviewed jointly."
        ),
        "matched_vs_unmatched_definition": (
            "paper_matched_vs_unmatched_treated.csv compares baseline covariates of "
            "matched and unmatched treated person-t0 assignments using balance_detail "
            "SMD conventions. Treatment year t0 is included as a categorical feature. "
            "The paper-facing file is disclosure-aware; exact original-level values are "
            "written only to the explicitly internal diagnostic named in the manifest. "
            "The comparison characterizes the matched-treated estimand and is not a "
            "treated-versus-control balance table."
        ),
        "repeated_person_overlap_definition": (
            "A person may serve as a control before later becoming treated. This is valid "
            "under annual risk-set sampling and fixed treatment assignment, but it links "
            "matched sets through the same person. The overlap table quantifies this "
            "dependence; it does not imply control reuse within the matching algorithm."
        ),
        "rehabilitation_count_definition": (
            "Rehabilitation events are successful rehabilitation starts represented in slot 1 "
            "or slot 2 of the processed annual records. Diagnosis-code tables count starts, not "
            "applications, and report unique people separately from events."
        ),
        "musculoskeletal_definition": {
            "msk_diagnosis_codes": _normalize_diagnosis_codes(config.msk_diagnosis_codes),
            "mental_health_diagnosis_codes": _normalize_diagnosis_codes(config.mental_health_diagnosis_codes),
            "note": (
                "The RSD approval diagnosis field (mcdggr) is an ICD-10 based Diagnosengruppe for "
                "approvals up to 31 December 2020 (20 = Muskel-Skelett-System und Bindegewebe) and "
                "an Indikationsgruppe for approvals from 1 January 2021 (53 = Orthopaedie, "
                "56 = Rheumatologie; 30 = psychische Erkrankungen becomes 55 = Psychosomatik). The "
                "code is assigned to the calendar year of the rehabilitation start, so 2021 contains "
                "both schemes. Diagnosis-code tables report the raw codes; the musculoskeletal and "
                "mental-health flags use the configured code sets across all years."
            ),
        },
        "control_count_definition": (
            "Before matching, control counts are person-t0 assignments. A person may be eligible "
            "in more than one annual risk set. Matching without replacement prevents a selected "
            "control from being used again in a later treatment year."
        ),
        "reporting_configuration": reporting.to_dict(),
        "generated_for_specification": {
            "year_start": config.year_start,
            "year_cap": config.year_cap,
            "lag_depth": config.lag_depth,
            "control_pool": config.control_pool,
            "caliper": config.caliper,
            "controls_per_treated": config.controls_per_treated,
            "reuse_controls_across_years": config.reuse_controls_across_years,
        },
    }
    paths["limitations"].write_text(
        json.dumps(limitations, indent=2), encoding="utf-8"
    )
    manifest = {
        "description": "Paper-ready descriptive, attrition, overlap, matching and balance summaries.",
        "files": {key: str(value) for key, value in paths.items() if key != "manifest"},
        "definitions": {
            "sample_overview": "Headline counts of the processed source panel: people, person-years, observation window, divorce and rehabilitation totals.",
            "descriptive_statistics": "Classic n/mean/median/SD/min/max (continuous) and n/% (binary) summary of the matched (post-match) covariates, pooled across divorced individuals and their controls. Same feature list and same matched population as the balance table; use the balance table instead for the treated-vs-control comparison itself.",
            "annual_panel": "Annual person-year rows, unique people, divorces, rehabilitation events and deaths by death year (deaths_by_death_year); the annual death-count definition in the limitations file explains why recorded_deaths_in_year is kept only as an audit column and must not be quoted.",
            "divorce_cohorts": "Per treatment year t0: observed divorces, eligible treated and controls, matched pairs, match rate and matched-pair distance summaries.",
            "rehab_codes": "Rehabilitation starts by broad diagnosis code with unique people, year span and event shares; small cells pooled per the limitations file.",
            "rehab_codes_by_year": "Rehabilitation starts by calendar year and diagnosis code; small cells pooled per the limitations file.",
            "filter_attrition": "Every treated/control exclusion step with rows remaining and the person-versus-assignment counting caveat per group.",
            "matching_overall": "Aggregate matched counts, match rate, unmatched decomposition, caliper and matched-distance distribution.",
            "matching_by_year": "Exact annual matching audit, including treated without any exact-stratum control and caliper failures.",
            "matched_vs_unmatched_treated": "Disclosure-aware baseline covariates of matched versus unmatched treated individuals, including treatment-year composition; categorical levels are pooled when needed.",
            "repeated_person_overlap": "Summary of people appearing in both matched roles, especially controls who later become treated; small overlap counts may be withheld.",
            "propensity_distribution": "Propensity-score distribution quantiles by treatment year and analysis group.",
            "propensity_overlap": "Treated/control propensity-score ranges and common-support overlap by treatment year.",
            "balance_overview": "Per-sample SMD headline numbers for manuscript prose only; the per-covariate table comes from balance_detail (see related sources).",
            "limitations": "Definitions and boundaries that constrain how these tables may be quoted.",
        },
        "related_sources_outside_this_folder": {
            "per_covariate_balance_detail": str(
                config.diagnostics_dir / f"balance_detail_{spec}.csv"
            ),
            "balance_summary": str(balance_summary_path),
            "matching_audit": str(matching_audit_path),
            "divorce_and_matching_by_t0_internal_not_for_export": str(cohort_internal_path),
            "matching_overall_internal_not_for_export": str(matching_overall_internal_path),
            "matched_vs_unmatched_treated_internal_not_for_export": str(exact_matchability_path),
            "repeated_person_overlap_detail_internal_not_for_export": str(overlap_detail_path),
            "panel_coverage_diagnostics": (
                str(config.diagnostics_dir / "panel_coverage_diagnostics.csv")
                if (config.diagnostics_dir / "panel_coverage_diagnostics.csv").exists()
                else (
                    "generated by the parent full-window run; see "
                    "parent_panel_reference.json in this specification's folder"
                )
            ),
            "longitudinal_mediation_audit": str(
                config.diagnostics_dir / f"longitudinal_mediation_data_audit_{spec}.json"
            ),
        },
        "important_note": (
            "Use values generated by the confidential-data run, not older code versions "
            "or synthetic tests. Files explicitly labelled internal_not_for_export retain "
            "exact cells for secure-machine diagnosis and should not be submitted for "
            "release without separate review."
        ),
    }
    paths["manifest"].write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    paths["signature"].write_text(
        json.dumps({
            "signature": summary_signature,
            "payload": signature_payload,
        }, indent=2),
        encoding="utf-8",
    )
    return paths

from pathlib import Path

import polars as pl

def _fmsd_label() -> pl.Expr:
    return (
        pl.when(pl.col("fmsd").is_null()).then(pl.lit("missing"))
        .when(pl.col("fmsd") == 1).then(pl.lit("1_non_married_mixed"))
        .when(pl.col("fmsd") == 2).then(pl.lit("2_married"))
        .when(pl.col("fmsd") == 3).then(pl.lit("3_divorced"))
        .otherwise(pl.concat_str([pl.lit("other_"), pl.col("fmsd").cast(pl.Utf8, strict=False)]))
        .alias("fmsd_label")
    )

def _marital_assignment_groups(
    treated_path: str | Path,
    controls_path: str | Path,
    matches_path: str | Path,
) -> pl.LazyFrame:
    treated = pl.scan_parquet(treated_path).select([
        "simple_id", "t0", pl.lit("eligible_treated").alias("analysis_group")
    ])
    controls = pl.scan_parquet(controls_path).select([
        "simple_id", "t0", pl.lit("eligible_controls").alias("analysis_group")
    ])
    matched = pl.scan_parquet(matches_path)
    matched_treated = matched.select([
        pl.col("t_id").alias("simple_id"), "t0",
        pl.lit("matched_treated").alias("analysis_group"),
    ])
    matched_controls = matched.select([
        pl.col("c_id").alias("simple_id"), "t0",
        pl.lit("matched_controls").alias("analysis_group"),
    ])
    return pl.concat([treated, controls, matched_treated, matched_controls], how="vertical")

def build_marital_status_tables(
    config: PipelineConfig,
    panel_path: str | Path,
    treated_path: str | Path,
    controls_path: str | Path,
    matches_path: str | Path,
    force: bool = False,
) -> dict[str, Path]:
    order_path = config.diagnostics_dir / "marriage_order_restriction_summary.csv"
    composition_path = config.diagnostics_dir / "marital_state_composition_around_t0.csv"
    sequence_path = config.diagnostics_dir / "marital_state_sequences_around_t0.csv"
    outputs = [order_path, composition_path, sequence_path]
    if all(path.exists() for path in outputs) and not force:
        return {
            "marriage_order": order_path,
            "composition": composition_path,
            "sequences": sequence_path,
        }
    panel = pl.scan_parquet(panel_path)
    candidates = panel.filter(
        (pl.col("first_divorce_this_year") == 1)
        & (pl.col("ja") >= config.year_start)
        & (pl.col("ja") <= config.year_cap)
    )
    if config.first_marriage_source == "date_fields":
        marriage_order_expr = (
            pl.when(pl.col("marriage_start").is_null() | pl.col("first_marriage_start").is_null())
            .then(pl.lit("missing_marriage_start_information"))
            .when(pl.col("marriage_start") == pl.col("first_marriage_start"))
            .then(pl.lit("marriage_start_equals_first_marriage_start"))
            .otherwise(pl.lit("marriage_start_differs_from_first_marriage_start"))
        )
    else:
        marriage_order_expr = (
            pl.when(pl.col("is_first_marriage").is_null())
            .then(pl.lit("missing_is_first_marriage"))
            .when(pl.col("is_first_marriage") == 1)
            .then(pl.lit("playdata_flag_is_first_marriage_1"))
            .otherwise(pl.lit("playdata_flag_is_first_marriage_not_1"))
        )
    candidates = candidates.with_columns(
        marriage_order_expr.alias("marriage_order_category")
    )
    order = (
        candidates.group_by("marriage_order_category")
        .agg([
            pl.len().alias("n_first_observed_divorces"),
            pl.col("simple_id").n_unique().alias("n_people"),
        ])
        .with_columns(
            (pl.col("n_people") / pl.col("n_people").sum()).alias("share_people")
        )
        .sort("n_people", descending=True)
        .pipe(_safe_collect)
    )
    order.write_csv(order_path)
    assignments = _marital_assignment_groups(treated_path, controls_path, matches_path)
    status_panel = panel.select(["simple_id", "ja", "fmsd"])
    status_minus_1 = status_panel.select([
        "simple_id", (pl.col("ja") + 1).alias("t0"),
        pl.col("fmsd").alias("fmsd_t0_minus_1_raw"),
    ])
    status_t0 = status_panel.select([
        "simple_id", pl.col("ja").alias("t0"),
        pl.col("fmsd").alias("fmsd_t0_raw"),
    ])
    status_plus_1 = status_panel.select([
        "simple_id", (pl.col("ja") - 1).alias("t0"),
        pl.col("fmsd").alias("fmsd_t0_plus_1_raw"),
    ])
    wide = (
        assignments
        .join(status_minus_1, on=["simple_id", "t0"], how="left")
        .join(status_t0, on=["simple_id", "t0"], how="left")
        .join(status_plus_1, on=["simple_id", "t0"], how="left")
    )
    around = pl.concat([
        wide.select([
            "analysis_group", "simple_id", "t0",
            pl.lit(-1, dtype=pl.Int8).alias("relative_year"),
            pl.col("fmsd_t0_minus_1_raw").alias("fmsd"),
        ]),
        wide.select([
            "analysis_group", "simple_id", "t0",
            pl.lit(0, dtype=pl.Int8).alias("relative_year"),
            pl.col("fmsd_t0_raw").alias("fmsd"),
        ]),
        wide.select([
            "analysis_group", "simple_id", "t0",
            pl.lit(1, dtype=pl.Int8).alias("relative_year"),
            pl.col("fmsd_t0_plus_1_raw").alias("fmsd"),
        ]),
    ], how="vertical").with_columns(_fmsd_label())
    composition = (
        around.group_by(["analysis_group", "relative_year", "fmsd_label"])
        .agg(pl.len().alias("n_person_t0_assignments"))
        .with_columns(
            (pl.col("n_person_t0_assignments") / pl.col("n_person_t0_assignments").sum().over(
                ["analysis_group", "relative_year"]
            )).alias("share_assignments")
        )
        .sort(["analysis_group", "relative_year", "fmsd_label"])
        .pipe(_safe_collect)
    )
    composition.write_csv(composition_path)
    sequences = (
        wide.with_columns([
            pl.when(pl.col("fmsd_t0_minus_1_raw").is_null()).then(pl.lit("missing"))
            .when(pl.col("fmsd_t0_minus_1_raw") == 1).then(pl.lit("1_non_married_mixed"))
            .when(pl.col("fmsd_t0_minus_1_raw") == 2).then(pl.lit("2_married"))
            .when(pl.col("fmsd_t0_minus_1_raw") == 3).then(pl.lit("3_divorced"))
            .otherwise(pl.lit("other")).alias("fmsd_t0_minus_1"),
            pl.when(pl.col("fmsd_t0_raw").is_null()).then(pl.lit("missing"))
            .when(pl.col("fmsd_t0_raw") == 1).then(pl.lit("1_non_married_mixed"))
            .when(pl.col("fmsd_t0_raw") == 2).then(pl.lit("2_married"))
            .when(pl.col("fmsd_t0_raw") == 3).then(pl.lit("3_divorced"))
            .otherwise(pl.lit("other")).alias("fmsd_t0"),
            pl.when(pl.col("fmsd_t0_plus_1_raw").is_null()).then(pl.lit("missing"))
            .when(pl.col("fmsd_t0_plus_1_raw") == 1).then(pl.lit("1_non_married_mixed"))
            .when(pl.col("fmsd_t0_plus_1_raw") == 2).then(pl.lit("2_married"))
            .when(pl.col("fmsd_t0_plus_1_raw") == 3).then(pl.lit("3_divorced"))
            .otherwise(pl.lit("other")).alias("fmsd_t0_plus_1"),
        ])
        .group_by([
            "analysis_group", "fmsd_t0_minus_1", "fmsd_t0", "fmsd_t0_plus_1"
        ])
        .agg(pl.len().alias("n_person_t0_assignments"))
        .with_columns(
            (pl.col("n_person_t0_assignments") / pl.col("n_person_t0_assignments").sum().over("analysis_group"))
            .alias("share_assignments")
        )
        .sort(["analysis_group", "n_person_t0_assignments"], descending=[False, True])
        .pipe(_safe_collect)
    )
    sequences.write_csv(sequence_path)
    return {
        "marriage_order": order_path,
        "composition": composition_path,
        "sequences": sequence_path,
    }

from pathlib import Path
import json
import logging
import warnings
import re

import numpy as np
import pandas as pd
import polars as pl
from scipy import linalg, stats

log = logging.getLogger(__name__)

def _assignment_frame(matches_path: str | Path) -> pl.LazyFrame:
    matches = pl.scan_parquet(matches_path)
    treated = matches.select([
        pl.col("t_id").alias("simple_id"), "t0", "match_group",
        pl.lit(1, dtype=pl.Int8).alias("treated"),
    ])
    controls = matches.select([
        pl.col("c_id").alias("simple_id"), "t0", "match_group",
        pl.lit(0, dtype=pl.Int8).alias("treated"),
    ])
    return pl.concat([treated, controls], how="vertical")

def _baseline_frame(
    treated_path: str | Path,
    controls_path: str | Path,
    matches_path: str | Path,
) -> pl.LazyFrame:
    matches = pl.scan_parquet(matches_path)
    treated_map = matches.select([
        pl.col("t_id").alias("simple_id"), "t0", "match_group"
    ])
    control_map = matches.select([
        pl.col("c_id").alias("simple_id"), "t0", "match_group"
    ])
    treated = pl.scan_parquet(treated_path).join(treated_map, on=["simple_id", "t0"], how="inner")
    controls = pl.scan_parquet(controls_path).join(control_map, on=["simple_id", "t0"], how="inner")
    return pl.concat([treated, controls], how="vertical")

def build_msk_followup(
    config: PipelineConfig,
    panel_path: str | Path,
    matches_path: str | Path,
    treated_path: str | Path,
    controls_path: str | Path,
    force: bool = False,
) -> Path:
    spec = f"{config.control_pool}_lag{config.lag_depth}"
    output = config.analysis_dir / f"msk_followup_{spec}_fixed_assignment.parquet"
    audit_path = config.diagnostics_dir / f"msk_followup_audit_{spec}_fixed_assignment.json"
    if output.exists() and audit_path.exists() and not force:
        return output
    assignment = _assignment_frame(matches_path)
    baseline = _baseline_frame(treated_path, controls_path, matches_path)
    baseline_columns = [
        column for column in baseline.columns
        if re.match(r"lag[123]_", column) and not column.endswith("_source_year")
    ]
    assignment = assignment.join(
        baseline.select(["simple_id", "t0", *baseline_columns]),
        on=["simple_id", "t0"], how="left",
    )
    panel = pl.scan_parquet(panel_path).select([
        "simple_id", "ja", "rtwf_jjjj", "msk_starts_this_year",
    ])
    death_years = panel.group_by("simple_id").agg(
        pl.col("rtwf_jjjj").drop_nulls().max().cast(pl.Int32).alias("death_year")
    )
    annual_msk = panel.select([
        "simple_id", "ja", "msk_starts_this_year",
        pl.lit(1, dtype=pl.Int8).alias("annual_panel_observed"),
    ])
    followup = assignment.join(death_years, on="simple_id", how="left").filter(
        pl.col("death_year").is_null() | (pl.col("death_year") > pl.col("t0"))
    ).with_columns(
        pl.int_ranges(1, config.followup_years + 1).alias("follow_year")
    ).explode("follow_year").with_columns(
        (pl.col("t0") + pl.col("follow_year")).cast(pl.Int32).alias("ja")
    ).join(annual_msk, on=["simple_id", "ja"], how="left")
    followup = followup.with_columns([
        pl.col("follow_year").cast(pl.Int8),
        pl.col("annual_panel_observed").fill_null(0).cast(pl.Int8),
        pl.col("msk_starts_this_year").fill_null(0).cast(pl.Int16),
        (pl.col("msk_starts_this_year").fill_null(0) > 0).cast(pl.Int8).alias("msk_event"),
        (
            pl.col("death_year").is_not_null()
            & (pl.col("ja") == pl.col("death_year"))
        ).cast(pl.Int8).alias("death_event"),
    ])
    followup = followup.with_columns([
        pl.when(pl.col("msk_event") == 1).then(1)
        .when(pl.col("death_event") == 1).then(2)
        .otherwise(0).cast(pl.Int8).alias("event_type"),
        ((pl.col("msk_event") == 1) & (pl.col("death_event") == 1))
        .cast(pl.Int8).alias("same_year_msk_and_death"),
    ]).sort(["match_group", "treated", "follow_year"])
    followup = followup.with_columns([
        (pl.col("event_type") > 0).cum_sum().over(["simple_id", "t0"]).alias("cum_terminal_events")
    ]).filter(
        (
            pl.col("cum_terminal_events")
            - (pl.col("event_type") > 0).cast(pl.Int8)
        ) == 0
    ).with_columns(pl.lit(1.0).alias("analysis_weight"))
    sink_parquet(followup, output, config.checkpoint_row_group_size)
    audit = (
        pl.scan_parquet(output).select([
            pl.len().alias("person_year_rows"),
            pl.col("simple_id").n_unique().alias("people_with_followup"),
            pl.col("match_group").n_unique().alias("matched_sets_with_followup"),
            pl.col("msk_event").sum().alias("msk_events"),
            ((pl.col("death_event") == 1) & (pl.col("msk_event") == 0)).sum().alias("competing_deaths"),
            pl.col("same_year_msk_and_death").sum().alias("same_year_msk_and_death"),
            (pl.col("annual_panel_observed") == 0).sum().alias("followup_rows_without_annual_panel_record"),
            pl.col("simple_id").filter(pl.col("annual_panel_observed") == 0)
            .n_unique().alias("people_with_at_least_one_missing_annual_followup_row"),
        ]).pipe(_safe_collect).row(0, named=True)
    )
    audit.update({
        "death_measure": "person-level rtwf_jjjj used directly",
        "missing_annual_row_rule": (
            "The full five-year grid is retained; an absent annual panel row contributes no "
            "recorded MSK start and is separately counted in this audit."
        ),
    })
    gap_detail_path = config.diagnostics_dir / (
        f"msk_followup_observation_gaps_{spec}_fixed_assignment.csv"
    )
    gap_detail = (
        pl.scan_parquet(output)
        .group_by(["treated", "t0", "follow_year"])
        .agg([
            pl.len().alias("person_year_rows"),
            (pl.col("annual_panel_observed") == 0).sum().alias("rows_without_annual_panel_record"),
            pl.col("simple_id").filter(pl.col("annual_panel_observed") == 0)
            .n_unique().alias("people_without_annual_panel_record"),
        ])
        .with_columns(
            (
                pl.col("rows_without_annual_panel_record")
                / pl.col("person_year_rows")
            ).alias("share_rows_without_annual_panel_record")
        )
        .sort(["treated", "t0", "follow_year"])
        .pipe(_safe_collect)
    )
    gap_detail.write_csv(gap_detail_path)
    audit.update({
        "observation_gap_detail": str(gap_detail_path),
    })
    audit_path.write_text(json.dumps(audit, indent=2), encoding="utf-8")
    return output

def build_msk_pair_censored_sensitivity(
    config: PipelineConfig,
    main_followup_path: str | Path,
    force: bool = False,
) -> dict[str, Path]:
    spec = f"{config.control_pool}_lag{config.lag_depth}"
    output = config.analysis_dir / f"msk_followup_{spec}_pair_censored_at_first_gap.parquet"
    audit_path = config.diagnostics_dir / f"msk_pair_censored_at_first_gap_audit_{spec}.json"
    if output.exists() and audit_path.exists() and not force:
        return {"followup": output, "audit": audit_path}
    followup = pl.scan_parquet(main_followup_path)
    first_gap = (
        followup.filter(pl.col("annual_panel_observed") == 0)
        .group_by("match_group")
        .agg(pl.col("follow_year").min().alias("first_pair_gap_year"))
    )
    censored = (
        followup.join(first_gap, on="match_group", how="left")
        .filter(
            pl.col("first_pair_gap_year").is_null()
            | (pl.col("follow_year") < pl.col("first_pair_gap_year"))
        )
        .sort(["match_group", "treated", "follow_year"])
    )
    sink_parquet(censored, output, config.checkpoint_row_group_size)
    main_summary = followup.select([
        pl.len().alias("main_person_year_rows"),
        pl.col("match_group").n_unique().alias("main_matched_sets"),
        pl.col("msk_event").sum().alias("main_msk_events"),
    ]).pipe(_safe_collect).row(0, named=True)
    sensitivity_summary = pl.scan_parquet(output).select([
        pl.len().alias("sensitivity_person_year_rows"),
        pl.col("match_group").n_unique().alias("sensitivity_matched_sets"),
        pl.col("msk_event").sum().alias("sensitivity_msk_events"),
    ]).pipe(_safe_collect).row(0, named=True)
    gap_summary = first_gap.select([
        pl.col("match_group").n_unique().alias("pairs_with_observation_gap"),
        pl.col("first_pair_gap_year").min().alias("earliest_gap_follow_year"),
        pl.col("first_pair_gap_year").median().alias("median_first_gap_follow_year"),
    ]).pipe(_safe_collect).row(0, named=True)
    audit = {
        **main_summary,
        **sensitivity_summary,
        **gap_summary,
        "rule": (
            "Both members of a matched pair are censored immediately before the first "
            "follow-up year in which either member lacks an annual panel row."
        ),
        "estimand_warning": (
            "This sensitivity changes the observed follow-up population and can induce "
            "selection if annual-record dropout is affected by treatment or health."
        ),
    }
    audit_path.write_text(json.dumps(audit, indent=2), encoding="utf-8")
    return {"followup": output, "audit": audit_path}

def build_mortality_followup(
    config: PipelineConfig,
    panel_path: str | Path,
    matches_path: str | Path,
    treated_path: str | Path,
    controls_path: str | Path,
    force: bool = False,
) -> Path:
    output = config.analysis_dir / f"mortality_followup_{config.control_pool}_lag{config.lag_depth}_fixed_assignment.parquet"
    audit_path = config.diagnostics_dir / f"mortality_followup_audit_{config.control_pool}_lag{config.lag_depth}.json"
    if output.exists() and audit_path.exists() and not force:
        return output
    assignment = _assignment_frame(matches_path)
    baseline = _baseline_frame(treated_path, controls_path, matches_path)
    baseline_columns = [
        column for column in baseline.columns
        if re.match(r"lag[123]_", column) and not column.endswith("_source_year")
    ]
    assignment = assignment.join(
        baseline.select(["simple_id", "t0", *baseline_columns]),
        on=["simple_id", "t0"], how="left",
    )
    death_years = (
        pl.scan_parquet(panel_path)
        .group_by("simple_id")
        .agg(pl.col("rtwf_jjjj").drop_nulls().max().cast(pl.Int32).alias("death_year"))
    )
    followup = assignment.join(death_years, on="simple_id", how="left").filter(
        pl.col("death_year").is_null() | (pl.col("death_year") > pl.col("t0"))
    )
    followup = followup.with_columns([
        pl.min_horizontal(
            pl.col("t0") + config.mortality_horizon,
            pl.lit(config.death_registry_end_year, dtype=pl.Int32),
            pl.coalesce([
                pl.col("death_year"),
                pl.lit(config.death_registry_end_year, dtype=pl.Int32),
            ]),
        ).cast(pl.Int32).alias("followup_end_year"),
    ]).filter(pl.col("followup_end_year") >= pl.col("t0") + 1)
    followup = followup.with_columns(
        pl.int_ranges(
            pl.col("t0") + 1,
            pl.col("followup_end_year") + 1,
        ).alias("ja")
    ).explode("ja")
    followup = followup.with_columns([
        (pl.col("ja") - pl.col("t0")).cast(pl.Int8).alias("follow_year"),
        (
            pl.col("death_year").is_not_null()
            & (pl.col("ja") == pl.col("death_year"))
        ).cast(pl.Int8).alias("death_event"),
        pl.lit(1.0).alias("analysis_weight"),
    ]).sort(["match_group", "treated", "follow_year"])
    sink_parquet(followup, output, config.checkpoint_row_group_size)
    audit = followup.select([
        pl.len().alias("person_year_rows"),
        pl.col("simple_id").n_unique().alias("people_with_followup"),
        pl.col("match_group").n_unique().alias("matched_sets_with_followup"),
        pl.col("death_event").sum().alias("deaths"),
        pl.col("follow_year").max().alias("maximum_follow_year"),
    ]).pipe(_safe_collect).row(0, named=True)
    audit.update({
        "death_measure": "person-level rtwf_jjjj used directly",
        "death_registry_end_year": config.death_registry_end_year,
        "common_five_year_horizon_available": bool(
            config.year_cap is not None
            and config.death_registry_end_year - config.year_cap >= 5
        ),
    })
    audit_path.write_text(json.dumps(audit, indent=2), encoding="utf-8")
    return output

def _covariate_role(config: PipelineConfig, variable: str) -> str:
    if variable in config.propensity_numeric or re.match(r"lag[23]_(entgelt_value|rtzb_value|byvlgs_value|bygmgs_value|cum_rehabs_by_year)$", variable):
        return "numeric"
    if variable in config.propensity_binary or re.match(r"lag[23]_(non_success_app_this_year|byvlgs_missing|bygmgs_missing)$", variable):
        return "binary"
    return "categorical"

def _build_design_matrix(
    data: pd.DataFrame,
    config: PipelineConfig,
    selected_covariates: list[str],
    outcome: str,
) -> tuple[np.ndarray, pd.DataFrame, list[dict]]:
    y = pd.to_numeric(data[outcome], errors="raise").to_numpy(np.int8)
    design = pd.DataFrame({
        "Intercept": np.ones(len(data), dtype=float),
        "treated": pd.to_numeric(data["treated"], errors="raise").to_numpy(float),
    })
    follow = pd.get_dummies(
        data["follow_year"].astype("string"), prefix="follow_year", drop_first=True, dtype=float
    )
    design = pd.concat([design, follow.reset_index(drop=True)], axis=1)
    transformations: list[dict] = []
    for variable in selected_covariates:
        if variable not in data.columns:
            transformations.append({"variable": variable, "status": "unavailable_in_followup"})
            continue
        role = _covariate_role(config, variable)
        if role in {"numeric", "binary"}:
            values = pd.to_numeric(data[variable], errors="coerce")
            missing = values.isna().astype(float)
            fill = float(values.median()) if role == "numeric" and values.notna().any() else (
                float(values.mode().iloc[0]) if values.notna().any() else 0.0
            )
            filled = values.fillna(fill).to_numpy(float)
            transformed_name = variable
            if variable.endswith(("entgelt_value", "rtzb_value")):
                filled = np.log1p(np.clip(filled, 0.0, None))
                transformed_name = f"{variable}__log1p"
            if role == "numeric":
                scale = float(np.std(filled))
                center = float(np.mean(filled))
                if scale > 1e-12:
                    filled = (filled - center) / scale
                else:
                    scale = 1.0
                    filled = filled - center
            else:
                center, scale = 0.0, 1.0
            design[transformed_name] = filled
            if missing.sum() > 0:
                design[f"{variable}__missing"] = missing.to_numpy(float)
            transformations.append({
                "variable": variable, "role": role, "imputation": fill,
                "center": center, "scale": scale,
                "missing_indicator_included": bool(missing.sum() > 0),
            })
        else:
            values = data[variable].astype("string").fillna("__MISSING__")
            dummies = pd.get_dummies(values, prefix=variable, drop_first=True, dtype=float)
            design = pd.concat([design, dummies.reset_index(drop=True)], axis=1)
            transformations.append({
                "variable": variable, "role": "categorical",
                "levels": sorted(values.unique().tolist()),
                "reference_level": sorted(values.unique().tolist())[0] if values.nunique() else None,
            })
    keep = [
        column for column in design.columns
        if column in {"Intercept", "treated"} or float(np.nanstd(design[column])) > 1e-12
    ]
    design = design[keep]
    matrix = design.to_numpy(float)
    _, r, pivot = linalg.qr(matrix, mode="economic", pivoting=True)
    tolerance = np.finfo(float).eps * max(matrix.shape) * (abs(r[0, 0]) if r.size else 0.0)
    rank = int(np.sum(np.abs(np.diag(r)) > tolerance))
    selected = list(pivot[:rank])
    treated_index = design.columns.get_loc("treated")
    if treated_index not in selected:
        selected = selected[:-1] + [treated_index]
    selected = sorted(set(selected))
    reduced = design.iloc[:, selected]
    if np.linalg.matrix_rank(reduced.to_numpy(float)) < reduced.shape[1]:
        raise np.linalg.LinAlgError("Outcome design remains rank deficient after QR reduction.")
    return y, reduced, transformations

def _unpenalized_logistic_regression(
    x: np.ndarray,
    y: np.ndarray,
    sample_weight: np.ndarray | None = None,
    max_iter: int | None = None,
    tol: float = 1e-7,
    extra_fallbacks: bool = False,
    accept_unconverged: bool = False,
) -> LogisticRegression:
    base_iter = int(max_iter) if max_iter else 500
    attempts = [
        {"penalty": None, "solver": "lbfgs", "max_iter": base_iter, "label": "unpenalized_none_lbfgs"},
        {"penalty": "none", "solver": "lbfgs", "max_iter": base_iter, "label": "unpenalized_string_lbfgs"},
        {"penalty": "l2", "C": 1e4, "solver": "liblinear", "max_iter": 2 * base_iter, "label": "tiny_ridge_fallback_C1e4"},
    ]
    if extra_fallbacks:
        attempts += [
            {"penalty": "l2", "C": 1e4, "solver": "lbfgs", "max_iter": 2 * base_iter, "label": "tiny_ridge_fallback_C1e4_lbfgs"},
            {"penalty": "l2", "C": 1e2, "solver": "lbfgs", "max_iter": 2 * base_iter, "label": "ridge_fallback_C1e2"},
            {"penalty": "l2", "C": 1.0, "solver": "lbfgs", "max_iter": 2 * base_iter, "label": "ridge_fallback_C1"},
        ]
    last_error = None
    last_model = None
    last_label = None
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        for attempt in attempts:
            label = attempt.pop("label")
            try:
                model = LogisticRegression(fit_intercept=False, tol=tol, **attempt)
                model.fit(x, y, sample_weight=sample_weight)
                model._pipeline_fit_method = label
                model._pipeline_unpenalized_approximation = not label.startswith("unpenalized")
                model._pipeline_converged = bool(int(np.max(model.n_iter_)) < model.max_iter)
                model._pipeline_n_iter = int(np.max(model.n_iter_))
                if model._pipeline_converged:
                    return model
                last_model, last_label = model, label
                last_error = RuntimeError(f"{label} reached max_iter={model.max_iter}")
            except (TypeError, ValueError, RuntimeError) as exc:
                last_error = exc
                continue
    if accept_unconverged and last_model is not None:
        log.warning(
            "Logistic fit accepted without convergence (%s after %d iterations, tol=%g); "
            "recorded in the model diagnostics.",
            last_label, last_model._pipeline_n_iter, tol,
        )
        return last_model
    raise RuntimeError(f"All sklearn logistic fitting routes failed: {last_error}")

def _cluster_robust_logit_covariance(
    x: np.ndarray,
    y: np.ndarray,
    probabilities: np.ndarray,
    groups: np.ndarray,
    sample_weight: np.ndarray,
) -> np.ndarray:
    n, k = x.shape
    unique_groups, inverse = np.unique(groups, return_inverse=True)
    g = len(unique_groups)
    if g <= k + 1:
        raise np.linalg.LinAlgError(f"Only {g} matched sets for {k} model columns.")
    hessian_weight = sample_weight * probabilities * (1.0 - probabilities)
    bread = x.T @ (x * hessian_weight[:, None])
    bread_inv = np.linalg.pinv(bread, rcond=1e-10)
    row_scores = x * (sample_weight * (y - probabilities))[:, None]
    cluster_scores = np.zeros((g, k), dtype=float)
    np.add.at(cluster_scores, inverse, row_scores)
    meat = cluster_scores.T @ cluster_scores
    correction = (g / (g - 1.0)) * ((n - 1.0) / max(n - k, 1.0))
    covariance = correction * bread_inv @ meat @ bread_inv
    if not np.all(np.isfinite(covariance)):
        raise np.linalg.LinAlgError("Cluster-robust covariance is non-finite.")
    return covariance

def _bootstrap_treated_coefficient_sklearn(
    x: np.ndarray,
    y: np.ndarray,
    groups: np.ndarray,
    weights: np.ndarray,
    treated_index: int,
    seed: int,
    n_replicates: int,
    max_iter: int | None = None,
) -> tuple[float, float, float, int]:
    rng = np.random.default_rng(seed)
    unique = np.unique(groups)
    group_indices = {group: np.flatnonzero(groups == group) for group in unique}
    coefficients: list[float] = []
    for _ in range(n_replicates):
        sampled = rng.choice(unique, size=len(unique), replace=True)
        indices = np.concatenate([group_indices[group] for group in sampled])
        try:
            model = _unpenalized_logistic_regression(x[indices], y[indices], weights[indices], max_iter=max_iter)
            coefficient = float(model.coef_[0, treated_index])
            if np.isfinite(coefficient):
                coefficients.append(coefficient)
        except Exception:
            continue
    minimum = max(20, n_replicates // 2)
    if len(coefficients) < minimum:
        raise RuntimeError(f"Only {len(coefficients)}/{n_replicates} matched-set bootstrap fits succeeded.")
    values = np.asarray(coefficients)
    return (
        float(values.std(ddof=1)), float(np.quantile(values, 0.025)),
        float(np.quantile(values, 0.975)), len(values),
    )

def fit_discrete_time_model(
    config: PipelineConfig,
    followup_path: str | Path,
    outcome: str,
    label: str,
    adjusted: bool,
    balance_summary_path: str | Path | None = None,
) -> dict:
    columns = set(pl.read_parquet_schema(followup_path))
    required = {outcome, "treated", "follow_year", "match_group", "analysis_weight"}
    missing = required - columns
    if missing:
        raise KeyError(f"Follow-up file is missing model columns: {sorted(missing)}")
    selected_details: list[dict] = []
    selected_covariates: list[str] = []
    if adjusted:
        if balance_summary_path is None:
            raise ValueError("Adjusted SMD-driven model requires balance_summary_path.")
        selected_details = select_imbalanced_covariates(config, balance_summary_path)
        selected_covariates = [item["variable"] for item in selected_details]
    requested = list(required) + [column for column in selected_covariates if column in columns]
    data = pl.read_parquet(followup_path, columns=list(dict.fromkeys(requested))).to_pandas()
    y, design, transformations = _build_design_matrix(data, config, selected_covariates, outcome)
    x = design.to_numpy(float)
    weights = pd.to_numeric(data["analysis_weight"], errors="raise").to_numpy(float)
    groups = data["match_group"].to_numpy()
    model = _unpenalized_logistic_regression(x, y, weights, max_iter=config.outcome_logit_max_iter)
    probabilities = np.clip(model.predict_proba(x)[:, 1], 1e-9, 1 - 1e-9)
    treated_index = design.columns.get_loc("treated")
    coefficient = float(model.coef_[0, treated_index])
    fit_method = getattr(model, "_pipeline_fit_method", "unknown")
    inference_method = "manual matched-set cluster-robust sandwich around unpenalized sklearn logit"
    bootstrap_successes = None
    try:
        if getattr(model, "_pipeline_unpenalized_approximation", False):
            raise np.linalg.LinAlgError("Tiny-ridge fallback requires bootstrap inference.")
        covariance = _cluster_robust_logit_covariance(x, y, probabilities, groups, weights)
        standard_error = float(np.sqrt(max(covariance[treated_index, treated_index], 0.0)))
        if not np.isfinite(standard_error) or standard_error <= 0:
            raise np.linalg.LinAlgError("Invalid sandwich standard error.")
        ci_low_log = coefficient - 1.96 * standard_error
        ci_high_log = coefficient + 1.96 * standard_error
    except (np.linalg.LinAlgError, ValueError):
        standard_error, ci_low_log, ci_high_log, bootstrap_successes = _bootstrap_treated_coefficient_sklearn(
            x, y, groups, weights, treated_index, config.seed, config.outcome_bootstrap_replicates,
            max_iter=config.outcome_logit_max_iter,
        )
        inference_method = "matched-set bootstrap fallback around unpenalized sklearn logit"
    z_value = coefficient / standard_error if standard_error > 0 else np.nan
    p_value = float(2.0 * stats.norm.sf(abs(z_value))) if np.isfinite(z_value) else None
    output = {
        "label": label,
        "adjusted": adjusted,
        "adjustment_rule": (
            f"post-match max absolute SMD > {config.smd_threshold}; categorical variables use level-specific SMDs"
            if adjusted else "none"
        ),
        "selected_covariates": selected_details,
        "design_columns_used": design.columns.tolist(),
        "transformations": transformations,
        "n_person_years": int(len(data)),
        "n_matched_sets": int(data["match_group"].nunique()),
        "events": int(data[outcome].sum()),
        "log_odds": coefficient,
        "standard_error": standard_error,
        "z_value": z_value,
        "p_value": p_value,
        "inference_method": inference_method,
        "successful_bootstrap_replicates": bootstrap_successes,
        "odds_ratio": float(np.exp(np.clip(coefficient, -50.0, 50.0))),
        "ci_low": float(np.exp(np.clip(ci_low_log, -50.0, 50.0))),
        "ci_high": float(np.exp(np.clip(ci_high_log, -50.0, 50.0))),
        "separation_warning": (
            "Treatment log-odds magnitude exceeds 10; the outcome may be sparse or separated and the OR is clipped for numerical output."
            if abs(coefficient) > 10 else None
        ),
        "sklearn_fit_method": fit_method,
        "sklearn_iterations": getattr(model, "_pipeline_n_iter", None),
        "sklearn_max_iter": int(config.outcome_logit_max_iter),
        "fit_warning": (
            "Tiny-ridge fallback used because the unpenalized MLE did not converge; interpret as a sparse-data sensitivity result."
            if getattr(model, "_pipeline_unpenalized_approximation", False) else None
        ),
    }
    output_path = config.analysis_dir / f"model_{label}_{'smd_adjusted' if adjusted else 'unadjusted'}.json"
    output_path.write_text(json.dumps(output, indent=2), encoding="utf-8")
    return output

def cumulative_incidence_msk(followup_path: str | Path, output_path: str | Path) -> Path:
    data = pl.read_parquet(followup_path).to_pandas()
    rows: list[dict] = []
    for treated, group in data.groupby("treated"):
        survival = 1.0
        cif_msk = 0.0
        cif_death = 0.0
        for year in sorted(group["follow_year"].unique()):
            year_data = group.loc[group["follow_year"] == year]
            risk = float(year_data["analysis_weight"].sum())
            d_msk = float((year_data["event_type"] == 1).mul(year_data["analysis_weight"]).sum())
            d_death = float((year_data["event_type"] == 2).mul(year_data["analysis_weight"]).sum())
            if risk > 0:
                cif_msk += survival * d_msk / risk
                cif_death += survival * d_death / risk
                survival *= 1.0 - (d_msk + d_death) / risk
            rows.append({
                "treated": int(treated), "follow_year": int(year), "risk_set_weight": risk,
                "msk_events": d_msk, "competing_deaths": d_death,
                "cumulative_incidence_msk": cif_msk,
                "cumulative_incidence_death_before_msk": cif_death,
                "event_free_survival": survival,
            })
    path = Path(output_path)
    pl.DataFrame(rows).write_csv(path)
    return path

def cumulative_mortality(followup_path: str | Path, output_path: str | Path) -> Path:
    data = pl.read_parquet(followup_path).to_pandas()
    rows: list[dict] = []
    for treated, group in data.groupby("treated"):
        survival = 1.0
        for year in sorted(group["follow_year"].unique()):
            year_data = group.loc[group["follow_year"] == year]
            risk = float(year_data["analysis_weight"].sum())
            deaths = float(year_data["death_event"].mul(year_data["analysis_weight"]).sum())
            if risk > 0:
                survival *= 1.0 - deaths / risk
            rows.append({
                "treated": int(treated), "follow_year": int(year), "risk_set_weight": risk,
                "deaths": deaths, "cumulative_mortality": 1.0 - survival,
            })
    path = Path(output_path)
    pl.DataFrame(rows).write_csv(path)
    return path

def _curve_arrays(followup_path: str | Path, kind: str) -> tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    data = pl.read_parquet(followup_path).to_pandas()
    groups = np.array(sorted(data["match_group"].unique()))
    group_index = {group: index for index, group in enumerate(groups)}
    years = np.array(sorted(data["follow_year"].unique()), dtype=int)
    year_index = {year: index for index, year in enumerate(years)}
    risk = np.zeros((len(groups), 2, len(years)), dtype=float)
    event = np.zeros_like(risk)
    competing = np.zeros_like(risk)
    for row in data.itertuples(index=False):
        g = group_index[row.match_group]
        a = int(row.treated)
        h = year_index[int(row.follow_year)]
        w = float(row.analysis_weight)
        risk[g, a, h] += w
        if kind == "msk":
            event[g, a, h] += w * int(row.event_type == 1)
            competing[g, a, h] += w * int(row.event_type == 2)
        else:
            event[g, a, h] += w * int(row.death_event == 1)
    return groups, years, risk, np.stack([event, competing], axis=0)

def _risk_from_counts(risk: np.ndarray, events: np.ndarray, competing: np.ndarray | None) -> np.ndarray:
    survival = np.ones(2, dtype=float)
    cumulative = np.zeros(2, dtype=float)
    for year in range(risk.shape[1]):
        for arm in (0, 1):
            if risk[arm, year] <= 0:
                continue
            hazard = events[arm, year] / risk[arm, year]
            if competing is None:
                survival[arm] *= 1.0 - hazard
                cumulative[arm] = 1.0 - survival[arm]
            else:
                competing_hazard = competing[arm, year] / risk[arm, year]
                cumulative[arm] += survival[arm] * hazard
                survival[arm] *= 1.0 - hazard - competing_hazard
    return cumulative

def _absolute_effect_bootstrap(
    followup_path: str | Path,
    kind: str,
    seed: int,
    n_replicates: int,
    horizon_year: int,
) -> dict:
    data = pl.read_parquet(followup_path).filter(pl.col("follow_year") <= horizon_year)
    if data.height == 0:
        raise ValueError(f"No {kind} follow-up rows are available through year {horizon_year}.")
    temporary = Path(followup_path).with_name(f"_{Path(followup_path).stem}_h{horizon_year}.parquet")
    data.write_parquet(temporary)
    try:
        groups, years, risk_by_group, stacked = _curve_arrays(temporary, kind)
    finally:
        temporary.unlink(missing_ok=True)
    event_by_group, competing_by_group = stacked[0], stacked[1]
    point = _risk_from_counts(
        risk_by_group.sum(axis=0), event_by_group.sum(axis=0),
        competing_by_group.sum(axis=0) if kind == "msk" else None,
    )
    rng = np.random.default_rng(seed)
    rows = []
    for _ in range(n_replicates):
        sampled = rng.integers(0, len(groups), size=len(groups))
        counts = np.bincount(sampled, minlength=len(groups)).astype(float)
        risk = np.tensordot(counts, risk_by_group, axes=(0, 0))
        event = np.tensordot(counts, event_by_group, axes=(0, 0))
        competing = np.tensordot(counts, competing_by_group, axes=(0, 0)) if kind == "msk" else None
        arm_risk = _risk_from_counts(risk, event, competing)
        rd = arm_risk[1] - arm_risk[0]
        rr = arm_risk[1] / arm_risk[0] if arm_risk[0] > 0 else np.nan
        rows.append((arm_risk[0], arm_risk[1], rd, rr))
    values = np.asarray(rows, dtype=float)
    rd_ci = np.quantile(values[:, 2], [0.025, 0.975])
    return {
        "reported_horizon_year": int(horizon_year),
        "control_risk": float(point[0]),
        "control_risk_ci": [float(x) for x in np.quantile(values[:, 0], [0.025, 0.975])],
        "treated_risk": float(point[1]),
        "treated_risk_ci": [float(x) for x in np.quantile(values[:, 1], [0.025, 0.975])],
        "risk_difference": float(point[1] - point[0]),
        "risk_difference_ci": [float(x) for x in rd_ci],
        "risk_difference_per_1000": float((point[1] - point[0]) * 1000.0),
        "risk_difference_per_1000_ci": [float(x * 1000.0) for x in rd_ci],
        "risk_ratio": float(point[1] / point[0]) if point[0] > 0 else None,
        "risk_ratio_ci": [float(x) for x in np.nanquantile(values[:, 3], [0.025, 0.975])],
        "direction": "harm" if point[1] > point[0] else ("benefit" if point[1] < point[0] else "no_difference"),
        "bootstrap_unit": "matched set",
        "bootstrap_replicates": int(n_replicates),
    }

def summarize_absolute_effects(
    msk_followup_path: str | Path,
    mortality_followup_path: str | Path,
    output_path: str | Path,
    seed: int,
    n_replicates: int,
    msk_horizon_year: int = 5,
    mortality_horizon_year: int = 5,
) -> Path:
    payload = {
        "first_msk_rehabilitation_with_death_as_competing_event": _absolute_effect_bootstrap(
            msk_followup_path, "msk", seed, n_replicates, msk_horizon_year
        ),
        "mortality": _absolute_effect_bootstrap(
            mortality_followup_path, "mortality", seed + 1, n_replicates, mortality_horizon_year
        ),
        "interpretation_note": (
            "Absolute contrasts are calculated from matched-cohort cumulative-incidence or mortality curves. "
            "Intervals resample whole matched sets. They complement the conditional discrete-time hazard odds ratios."
        ),
    }
    path = Path(output_path)
    path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    return path

from pathlib import Path
import json
import math

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import polars as pl

SEX_LABELS = {"1": "Male", "2": "Female"}

def _save_figure(fig: plt.Figure, base_path: str | Path) -> dict[str, str]:
    base = Path(base_path)
    base.parent.mkdir(parents=True, exist_ok=True)
    png = base.with_suffix(".png")
    pdf = base.with_suffix(".pdf")
    fig.savefig(png, dpi=220, bbox_inches="tight")
    fig.savefig(pdf, bbox_inches="tight")
    plt.close(fig)
    return {"png": str(png), "pdf": str(pdf)}

def _plot_point_estimates_with_intervals(
    ax: plt.Axes,
    estimate: np.ndarray,
    ci_low: np.ndarray,
    ci_high: np.ndarray,
    positions: np.ndarray,
    orientation: str = "x",
    marker: str = "o",
    capsize: float = 4.0,
    color: str | None = None,
    connect: bool = False,
    linewidth: float = 1.5,
    zorder: float = 2.0,
) -> dict[str, object]:
    """Draw point estimates and their confidence intervals as two independent
    graphical elements, instead of via ``Axes.errorbar(..., xerr=...)`` /
    ``yerr=...``.

    Why this exists: ``errorbar`` computes bar half-lengths as
    ``estimate - ci_low`` and ``ci_high - estimate`` and raises
    ``ValueError: 'xerr'/'yerr' must not contain negative values`` if either
    is negative. A percentile-bootstrap confidence interval is not
    guaranteed to contain the point estimate that produced it -- that is a
    valid statistical outcome (e.g. a skewed bootstrap distribution, or a
    point estimate near a boundary of the estimand), not bad input, so it
    must never be clipped, reordered, or otherwise forced to "fit" the
    errorbar API.

    This helper sidesteps the constraint entirely: it draws the interval as
    a line segment directly between the recorded ``ci_low`` and ``ci_high``
    endpoints (never as a +/- offset from the point estimate), and draws the
    point estimate as a separate marker at its own recorded value. The two
    share only a position and a color. A point that lies above, below,
    inside, or exactly on its interval all render correctly, with the point
    visibly outside the interval line when that is what the data show.

    Parameters mirror the pieces of an ``errorbar`` call being replaced:
    ``orientation="x"`` means the interval runs along the x-axis at a fixed
    y ``positions`` value (replacing ``xerr``); ``orientation="y"`` means the
    interval runs along the y-axis at a fixed x ``positions`` value
    (replacing ``yerr``). ``connect=True`` additionally draws a line through
    the point estimates in position order (replacing the implicit
    connecting line ``errorbar`` draws when a ``marker`` is requested without
    an explicit ``fmt``).
    """
    estimate = np.asarray(estimate, dtype=float)
    ci_low = np.asarray(ci_low, dtype=float)
    ci_high = np.asarray(ci_high, dtype=float)
    positions = np.asarray(positions, dtype=float)
    n = len(estimate)
    if not (len(ci_low) == len(ci_high) == len(positions) == n):
        raise ValueError(
            "estimate, ci_low, ci_high, and positions must all have the same "
            f"length (got {n}, {len(ci_low)}, {len(ci_high)}, {len(positions)})."
        )
    if orientation not in ("x", "y"):
        raise ValueError(f"orientation must be 'x' or 'y', got {orientation!r}")
    if color is None:
        # Pull the next color from the axes' property cycle via a no-op,
        # empty artist (public API), so this series gets the same automatic
        # color an equivalent errorbar()/plot() call would have used.
        (probe,) = ax.plot([], [])
        color = probe.get_color()
        probe.remove()
    interval_lines: list[plt.Line2D] = []
    cap_lines: list[plt.Line2D] = []
    for pos, lo, hi in zip(positions, ci_low, ci_high):
        if orientation == "x":
            (segment,) = ax.plot(
                [lo, hi], [pos, pos], linestyle="-", linewidth=linewidth,
                color=color, zorder=zorder,
            )
        else:
            (segment,) = ax.plot(
                [pos, pos], [lo, hi], linestyle="-", linewidth=linewidth,
                color=color, zorder=zorder,
            )
        interval_lines.append(segment)
        if capsize:
            cap_marker = "|" if orientation == "x" else "_"
            if orientation == "x":
                (cap,) = ax.plot(
                    [lo, hi], [pos, pos], marker=cap_marker,
                    markersize=2.0 * capsize, linestyle="None",
                    color=color, zorder=zorder,
                )
            else:
                (cap,) = ax.plot(
                    [pos, pos], [lo, hi], marker=cap_marker,
                    markersize=2.0 * capsize, linestyle="None",
                    color=color, zorder=zorder,
                )
            cap_lines.append(cap)
    connect_line = None
    if connect:
        order = np.argsort(positions)
        if orientation == "x":
            (connect_line,) = ax.plot(
                estimate[order], positions[order], linestyle="-",
                linewidth=linewidth, color=color, zorder=zorder,
            )
        else:
            (connect_line,) = ax.plot(
                positions[order], estimate[order], linestyle="-",
                linewidth=linewidth, color=color, zorder=zorder,
            )
    if orientation == "x":
        (point,) = ax.plot(
            estimate, positions, marker=marker, linestyle="None",
            color=color, zorder=zorder + 1,
        )
    else:
        (point,) = ax.plot(
            positions, estimate, marker=marker, linestyle="None",
            color=color, zorder=zorder + 1,
        )
    return {
        "color": color,
        "interval_lines": interval_lines,
        "cap_lines": cap_lines,
        "connect_line": connect_line,
        "point": point,
    }

def plot_balance_love(
    balance_detail_path: str | Path,
    output_base: str | Path,
    threshold: float = 0.10,
) -> dict[str, str]:
    data = pl.read_csv(balance_detail_path).to_pandas()
    data["abs_smd"] = pd.to_numeric(data["smd"], errors="coerce").abs()
    collapsed = (
        data.groupby(["sample", "variable"], as_index=False)["abs_smd"].max()
        .pivot(index="variable", columns="sample", values="abs_smd")
        .fillna(0.0)
        .reset_index()
    )
    if "post" in collapsed.columns:
        collapsed = collapsed.sort_values("post", ascending=True)
    if collapsed.empty:
        raise ValueError("Balance table contains no plottable variables.")
    for column in ("pre", "post"):
        if column not in collapsed:
            collapsed[column] = 0.0
    height = max(5.0, 0.34 * len(collapsed) + 1.5)
    fig, ax = plt.subplots(figsize=(8.5, height))
    y = np.arange(len(collapsed))
    ax.scatter(collapsed["pre"], y, marker="o", label="Before matching")
    ax.scatter(collapsed["post"], y, marker="s", label="After matching")
    ax.axvline(threshold, linestyle="--", linewidth=1, label=f"|SMD| = {threshold:.2f}")
    ax.set_yticks(y)
    ax.set_yticklabels(collapsed["variable"])
    ax.set_xlabel("Maximum absolute standardized mean difference")
    ax.set_title("Figure 1. Covariate balance before and after matching")
    ax.legend(loc="lower right")
    ax.grid(axis="x", alpha=0.25)
    return _save_figure(fig, output_base)

def _curve_arrays_from_data(data: pd.DataFrame, kind: str) -> tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    if data.empty:
        raise ValueError("No follow-up rows are available for the requested curve.")
    groups = np.array(sorted(data["match_group"].unique()))
    group_index = {group: index for index, group in enumerate(groups)}
    years = np.array(sorted(data["follow_year"].unique()), dtype=int)
    year_index = {year: index for index, year in enumerate(years)}
    risk = np.zeros((len(groups), 2, len(years)), dtype=float)
    event = np.zeros_like(risk)
    competing = np.zeros_like(risk)
    for row in data.itertuples(index=False):
        g = group_index[row.match_group]
        arm = int(row.treated)
        h = year_index[int(row.follow_year)]
        weight = float(row.analysis_weight)
        risk[g, arm, h] += weight
        if kind == "msk":
            event[g, arm, h] += weight * int(row.event_type == 1)
            competing[g, arm, h] += weight * int(row.event_type == 2)
        elif kind == "mortality":
            event[g, arm, h] += weight * int(row.death_event == 1)
        else:
            raise ValueError(f"Unknown curve kind: {kind}")
    return groups, years, risk, np.stack([event, competing], axis=0)

def _cumulative_path_from_counts(
    risk: np.ndarray,
    events: np.ndarray,
    competing: np.ndarray | None,
) -> np.ndarray:
    n_years = risk.shape[1]
    survival = np.ones(2, dtype=float)
    cumulative = np.zeros((2, n_years), dtype=float)
    for year_index in range(n_years):
        for arm in (0, 1):
            if risk[arm, year_index] <= 0:
                cumulative[arm, year_index] = cumulative[arm, year_index - 1] if year_index else 0.0
                continue
            event_hazard = events[arm, year_index] / risk[arm, year_index]
            if competing is None:
                survival[arm] *= max(1.0 - event_hazard, 0.0)
                cumulative[arm, year_index] = 1.0 - survival[arm]
            else:
                competing_hazard = competing[arm, year_index] / risk[arm, year_index]
                prior = cumulative[arm, year_index - 1] if year_index else 0.0
                cumulative[arm, year_index] = prior + survival[arm] * event_hazard
                survival[arm] *= max(1.0 - event_hazard - competing_hazard, 0.0)
    return cumulative

def _bootstrap_curve_for_data(
    data: pd.DataFrame,
    kind: str,
    seed: int,
    n_replicates: int,
) -> dict[str, np.ndarray]:
    groups, years, risk_by_group, stacked = _curve_arrays_from_data(data, kind)
    event_by_group, competing_by_group = stacked[0], stacked[1]
    point_risk = risk_by_group.sum(axis=0)
    point = _cumulative_path_from_counts(
        point_risk,
        event_by_group.sum(axis=0),
        competing_by_group.sum(axis=0) if kind == "msk" else None,
    )
    rng = np.random.default_rng(seed)
    bootstrap = np.zeros((n_replicates, 2, len(years)), dtype=float)
    for replicate in range(n_replicates):
        sampled = rng.integers(0, len(groups), size=len(groups))
        counts = np.bincount(sampled, minlength=len(groups)).astype(float)
        risk = np.tensordot(counts, risk_by_group, axes=(0, 0))
        events = np.tensordot(counts, event_by_group, axes=(0, 0))
        competing = (
            np.tensordot(counts, competing_by_group, axes=(0, 0))
            if kind == "msk" else None
        )
        bootstrap[replicate] = _cumulative_path_from_counts(risk, events, competing)
    return {
        "years": years,
        "risk_set": point_risk,
        "point": point,
        "ci_low": np.quantile(bootstrap, 0.025, axis=0),
        "ci_high": np.quantile(bootstrap, 0.975, axis=0),
        "bootstrap": bootstrap,
    }

def build_pooled_curve_table(
    followup_path: str | Path,
    kind: str,
    output_path: str | Path,
    seed: int,
    n_replicates: int,
    effect_horizon: int | None = None,
) -> Path:
    data = pl.read_parquet(followup_path)
    if effect_horizon is not None:
        data = data.filter(pl.col("follow_year") <= effect_horizon)
    data = data.to_pandas()
    result = _bootstrap_curve_for_data(data, kind, seed, n_replicates)
    rows = []
    for arm in (0, 1):
        for j, year in enumerate(result["years"]):
            rows.append({
                "treated": arm,
                "follow_year": int(year),
                "estimate": float(result["point"][arm, j]),
                "ci_low": float(result["ci_low"][arm, j]),
                "ci_high": float(result["ci_high"][arm, j]),
                "n_at_risk": float(result["risk_set"][arm, j]),
            })
    path = Path(output_path)
    pl.DataFrame(rows).write_csv(path)
    return path

def build_sex_curve_and_heterogeneity(
    followup_path: str | Path,
    kind: str,
    curve_output_path: str | Path,
    heterogeneity_output_path: str | Path,
    seed: int,
    n_replicates: int,
    effect_horizon: int,
) -> dict[str, Path]:
    data = pl.read_parquet(followup_path).filter(
        pl.col("follow_year") <= effect_horizon
    ).to_pandas()
    if "lag1_ge_cat" not in data.columns:
        raise KeyError("Sex-specific analysis requires lag1_ge_cat in the follow-up file.")
    data["sex_code"] = data["lag1_ge_cat"].astype(str)
    rows: list[dict] = []
    sex_results: dict[str, dict[str, np.ndarray]] = {}
    skipped: list[str] = []
    for offset, sex_code in enumerate(("1", "2")):
        subset = data.loc[data["sex_code"] == sex_code].copy()
        if subset.empty:
            skipped.append(sex_code)
            log.warning("Skipping sex-specific %s curve: no observations for sex code %s", kind, sex_code)
            continue
        result = _bootstrap_curve_for_data(subset, kind, seed + offset * 10_000, n_replicates)
        sex_results[sex_code] = result
        for arm in (0, 1):
            for j, year in enumerate(result["years"]):
                rows.append({
                    "sex_code": sex_code,
                    "sex_label": SEX_LABELS[sex_code],
                    "treated": arm,
                    "follow_year": int(year),
                    "estimate": float(result["point"][arm, j]),
                    "ci_low": float(result["ci_low"][arm, j]),
                    "ci_high": float(result["ci_high"][arm, j]),
                    "n_at_risk": float(result["risk_set"][arm, j]),
                })
    if not rows:
        raise ValueError("No sex-specific follow-up observations are available.")
    curve_path = Path(curve_output_path)
    pl.DataFrame(rows).write_csv(curve_path)
    payload: dict[str, object] = {
        "outcome": kind,
        "effect_scale": f"cumulative-risk difference at follow-up year {effect_horizon}",
        "effect_horizon": effect_horizon,
        "skipped_sex_codes": skipped,
        "bootstrap_unit": "matched set, stratified by sex",
        "bootstrap_replicates": int(n_replicates),
        "interpretation": (
            "The heterogeneity contrast tests whether the divorce-associated absolute risk "
            "difference differs between women and men. Exact matching on sex makes the "
            "within-sex treated-control comparisons comparable; it does not prevent this test."
        ),
    }
    if {"1", "2"}.issubset(sex_results):
        male = sex_results["1"]
        female = sex_results["2"]
        male_rd = male["point"][1, -1] - male["point"][0, -1]
        female_rd = female["point"][1, -1] - female["point"][0, -1]
        male_boot = male["bootstrap"][:, 1, -1] - male["bootstrap"][:, 0, -1]
        female_boot = female["bootstrap"][:, 1, -1] - female["bootstrap"][:, 0, -1]
        difference = female_boot - male_boot
        p_value = min(1.0, 2.0 * min(float(np.mean(difference <= 0)), float(np.mean(difference >= 0))))
        payload.update({
            "male": {
                "risk_difference": float(male_rd),
                "risk_difference_per_1000": float(male_rd * 1000),
                "ci": [float(x) for x in np.quantile(male_boot, [0.025, 0.975])],
            },
            "female": {
                "risk_difference": float(female_rd),
                "risk_difference_per_1000": float(female_rd * 1000),
                "ci": [float(x) for x in np.quantile(female_boot, [0.025, 0.975])],
            },
            "female_minus_male": {
                "difference_in_risk_differences": float(female_rd - male_rd),
                "difference_per_1000": float((female_rd - male_rd) * 1000),
                "ci": [float(x) for x in np.quantile(difference, [0.025, 0.975])],
                "bootstrap_two_sided_p_value": p_value,
            },
        })
    else:
        payload["heterogeneity_test_status"] = "not_estimable_because_one_sex_stratum_is_empty"
    heterogeneity_path = Path(heterogeneity_output_path)
    heterogeneity_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    return {"curve": curve_path, "heterogeneity": heterogeneity_path}

def plot_pooled_curve(
    curve_path: str | Path,
    output_base: str | Path,
    title: str,
    ylabel: str,
) -> dict[str, str]:
    data = pl.read_csv(curve_path).to_pandas()
    fig, ax = plt.subplots(figsize=(7.5, 5.2))
    for arm, label in ((0, "Matched controls"), (1, "Divorced")):
        part = data.loc[data["treated"] == arm].sort_values("follow_year")
        x = part["follow_year"].to_numpy(float)
        estimate = part["estimate"].to_numpy(float)
        low = part["ci_low"].to_numpy(float)
        high = part["ci_high"].to_numpy(float)
        ax.plot(x, estimate, marker="o", label=label)
        ax.fill_between(x, low, high, alpha=0.18)
    ax.set_xlabel("Years after t0")
    ax.set_ylabel(ylabel)
    ax.set_title(title)
    ax.set_ylim(bottom=0)
    ax.legend()
    ax.grid(alpha=0.25)
    years = sorted(data["follow_year"].unique())
    risk_rows = []
    for arm in (0, 1):
        part = data.loc[data["treated"] == arm].set_index("follow_year")
        risk_rows.append([
            int(round(float(part.loc[year, "n_at_risk"]))) if year in part.index else 0
            for year in years
        ])
    ax.table(
        cellText=risk_rows, rowLabels=["Controls at risk", "Divorced at risk"],
        colLabels=[str(int(year)) for year in years], cellLoc="center",
        rowLoc="right", loc="bottom", bbox=[0.0, -0.42, 1.0, 0.24],
    )
    fig.subplots_adjust(bottom=0.32)
    return _save_figure(fig, output_base)

def plot_curve_by_sex(
    curve_path: str | Path,
    output_base: str | Path,
    title: str,
    ylabel: str,
) -> dict[str, str]:
    data = pl.read_csv(curve_path).to_pandas()
    available = [code for code in ("2", "1") if code in set(data["sex_code"].astype(str))]
    if not available:
        raise ValueError("The sex-specific curve file contains no plottable strata.")
    fig, axes = plt.subplots(1, len(available), figsize=(6.0 * len(available), 4.9), sharey=True)
    axes = np.atleast_1d(axes)
    for ax, sex_code in zip(axes, available):
        sex = data.loc[data["sex_code"].astype(str) == sex_code]
        for arm, label in ((0, "Matched controls"), (1, "Divorced")):
            part = sex.loc[sex["treated"] == arm].sort_values("follow_year")
            x = part["follow_year"].to_numpy(float)
            estimate = part["estimate"].to_numpy(float)
            low = part["ci_low"].to_numpy(float)
            high = part["ci_high"].to_numpy(float)
            ax.plot(x, estimate, marker="o", label=label)
            ax.fill_between(x, low, high, alpha=0.18)
        ax.set_title(SEX_LABELS[sex_code])
        ax.set_xlabel("Years after t0")
        ax.set_ylim(bottom=0)
        ax.grid(alpha=0.25)
    axes[0].set_ylabel(ylabel)
    axes[-1].legend()
    fig.suptitle(title)
    return _save_figure(fig, output_base)

def plot_pretrend_battery(
    pretrends: dict[str, dict],
    output_base: str | Path,
) -> dict[str, str]:
    labels = {
        "non_success_applications": "Unsuccessful rehabilitation applications",
        "earnings_amount": "Observed earnings amount (entgelt; zero when unobserved)",
        "pension_income_amount": "Observed pension income (rtzb; zero when unobserved)",
        "pension_income_missingness": "Pension-income field missing",
        "prior_rehabilitation_activity": "Any rehabilitation starts",
    }
    n_plots = len(pretrends)
    n_cols = 2
    n_rows = int(math.ceil(n_plots / n_cols))
    fig, axes = plt.subplots(n_rows, n_cols, figsize=(12.0, 4.1 * n_rows))
    axes = np.atleast_1d(axes).ravel()
    for ax, (key, result) in zip(axes, pretrends.items()):
        data = pl.read_csv(result["estimates_path"]).sort("event_time").to_pandas()
        _plot_point_estimates_with_intervals(
            ax,
            estimate=data["estimate"].to_numpy(dtype=float),
            ci_low=data["ci_low"].to_numpy(dtype=float),
            ci_high=data["ci_high"].to_numpy(dtype=float),
            positions=data["event_time"].to_numpy(dtype=float),
            orientation="y", marker="o", capsize=3, connect=True,
        )
        ax.axhline(0, linewidth=1)
        ax.axvline(-0.5, linestyle="--", linewidth=1)
        ax.set_title(labels.get(key, key))
        ax.set_xlabel("Years relative to t0")
        ax.set_ylabel("Matched treated-control difference")
        ax.grid(alpha=0.25)
    for ax in axes[n_plots:]:
        ax.set_visible(False)
    fig.suptitle("Appendix. Focused pre-divorce trajectory diagnostics")
    fig.tight_layout()
    return _save_figure(fig, output_base)

def plot_lag_comparison(
    comparison_csv: str | Path,
    output_base: str | Path,
) -> dict[str, str]:
    data = pl.read_csv(comparison_csv).to_pandas()
    outcomes = [name for name in ("msk", "mortality") if name in set(data["outcome"])]
    fig, axes = plt.subplots(1, len(outcomes), figsize=(7.0 * len(outcomes), 5.2), squeeze=False)
    order = ["lag1_full_window", "lag1_common_window", "lag3_common_window"]
    for ax, outcome in zip(axes.ravel(), outcomes):
        part = data.loc[data["outcome"] == outcome].copy()
        part["_order"] = part["specification"].map({name: i for i, name in enumerate(order)})
        part = part.sort_values("_order")
        y = np.arange(len(part))
        estimate = part["risk_difference_per_1000"].to_numpy(float)
        low = part["risk_difference_per_1000_ci_low"].to_numpy(float)
        high = part["risk_difference_per_1000_ci_high"].to_numpy(float)
        _plot_point_estimates_with_intervals(
            ax, estimate=estimate, ci_low=low, ci_high=high, positions=y,
            orientation="x", marker="o", capsize=4,
        )
        ax.axvline(0, linewidth=1)
        ax.set_yticks(y)
        ax.set_yticklabels(part["specification_label"].tolist())
        ax.set_xlabel("Risk difference per 1,000")
        ax.set_title("MSK rehabilitation" if outcome == "msk" else "Mortality")
        ax.grid(axis="x", alpha=0.25)
    fig.suptitle("Figure 4. Lag depth and common-window comparison")
    fig.tight_layout()
    return _save_figure(fig, output_base)

def plot_longitudinal_mediation_decomposition(
    mediation_result: dict,
    output_base: str | Path,
) -> dict[str, str]:
    keys = [
        ("interventional_total_effect_risk_difference", "Total effect"),
        ("interventional_direct_effect_risk_difference", "Direct effect"),
        ("interventional_indirect_effect_risk_difference", "Indirect effect through first MSK rehabilitation"),
    ]
    point = mediation_result["point_estimates"]
    intervals = mediation_result.get("bootstrap_intervals", {})
    estimates = np.array([point[key] * 1000 for key, _ in keys], dtype=float)
    y = np.arange(len(keys))
    fig, ax = plt.subplots(figsize=(8.5, 4.9))
    if all(key in intervals for key, _ in keys):
        low = np.array([intervals[key]["ci_low"] * 1000 for key, _ in keys], dtype=float)
        high = np.array([intervals[key]["ci_high"] * 1000 for key, _ in keys], dtype=float)
        _plot_point_estimates_with_intervals(
            ax, estimate=estimates, ci_low=low, ci_high=high, positions=y,
            orientation="x", marker="o", capsize=4,
        )
    else:
        ax.plot(estimates, y, "o")
    ax.axvline(0, linewidth=1)
    ax.set_yticks(y)
    ax.set_yticklabels([label for _, label in keys])
    ax.set_xlabel("Five-year mortality risk difference per 1,000")
    ax.set_title("Figure 5. Longitudinal interventional mediation decomposition")
    ax.grid(axis="x", alpha=0.25)
    fig.tight_layout()
    return _save_figure(fig, output_base)

from pathlib import Path
import json

import numpy as np
import pandas as pd
import polars as pl
from scipy import stats

SUPPORTED_OUTCOMES = {
    "non_success_app_this_year",
    "entgelt_value",
    "rtzb_value",
    "rtzb_missing",
    "rehab_starts_this_year",
}

def _pretrend_outcomes(config: PipelineConfig) -> list[str]:
    outcomes = [
        "non_success_app_this_year",
        "rtzb_value",
        "rtzb_missing",
        "rehab_starts_this_year",
    ]
    if config.source_has_entgelt:
        outcomes.insert(1, "entgelt_value")
    return outcomes

def build_pair_event_study_panel(
    config: PipelineConfig,
    panel_path: str | Path,
    matches_path: str | Path,
    pre_years: int = 3,
    post_years: int = 5,
    force: bool = False,
) -> Path:
    output = config.analysis_dir / f"pair_event_study_{config.control_pool}_lag{config.lag_depth}_pre{pre_years}_post{post_years}.parquet"
    if output.exists() and not force:
        return output
    matches = pl.scan_parquet(matches_path)
    assignment = pl.concat([
        matches.select([
            pl.col("t_id").alias("simple_id"), "t0", "match_group",
            pl.lit(1, dtype=pl.Int8).alias("treated"),
        ]),
        matches.select([
            pl.col("c_id").alias("simple_id"), "t0", "match_group",
            pl.lit(0, dtype=pl.Int8).alias("treated"),
        ]),
    ], how="vertical")
    outcomes = _pretrend_outcomes(config)
    panel = pl.scan_parquet(panel_path).select([
        "simple_id", "ja", *outcomes
    ])
    stacked = assignment.join(panel, on="simple_id", how="inner").with_columns(
        (pl.col("ja") - pl.col("t0")).cast(pl.Int16).alias("event_time")
    ).filter(pl.col("event_time").is_between(-pre_years, post_years, closed="both"))
    wide = stacked.group_by(["match_group", "t0", "event_time"]).agg([
        *[
            pl.col(outcome).filter(pl.col("treated") == 1).first().alias(f"treated_{outcome}")
            for outcome in outcomes
        ],
        *[
            pl.col(outcome).filter(pl.col("treated") == 0).first().alias(f"control_{outcome}")
            for outcome in outcomes
        ],
        pl.col("treated").n_unique().alias("n_arms_observed"),
    ]).filter(pl.col("n_arms_observed") == 2)
    wide = wide.with_columns([
        (pl.col(f"treated_{outcome}") - pl.col(f"control_{outcome}")).alias(f"pair_diff_{outcome}")
        for outcome in outcomes
    ])
    sink_parquet(wide, output, config.checkpoint_row_group_size)
    return output

def fit_pair_event_study(
    config: PipelineConfig,
    event_panel_path: str | Path,
    outcome: str,
    reference_period: int = -1,
) -> dict:
    if outcome not in SUPPORTED_OUTCOMES:
        raise ValueError(f"Unsupported event-study outcome: {outcome}")
    dependent = f"pair_diff_{outcome}"
    data = pl.read_parquet(
        event_panel_path, columns=["match_group", "event_time", dependent]
    ).drop_nulls().to_pandas()
    if reference_period not in set(data["event_time"]):
        raise ValueError(f"Reference event time {reference_period} is not observed.")
    levels = sorted(set(data["event_time"]))
    non_reference = [level for level in levels if level != reference_period]
    design = pd.DataFrame({"Intercept": np.ones(len(data), dtype=float)})
    for level in non_reference:
        design[f"event_time_{level}"] = (data["event_time"] == level).astype(float)
    x = design.to_numpy(float)
    y = data[dependent].to_numpy(float)
    model = LinearRegression(fit_intercept=False).fit(x, y)
    residual = y - model.predict(x)
    groups = data["match_group"].to_numpy()
    unique, inverse = np.unique(groups, return_inverse=True)
    bread_inv = np.linalg.pinv(x.T @ x, rcond=1e-10)
    row_scores = x * residual[:, None]
    cluster_scores = np.zeros((len(unique), x.shape[1]), dtype=float)
    np.add.at(cluster_scores, inverse, row_scores)
    correction = (len(unique) / max(len(unique) - 1, 1)) * ((len(y) - 1) / max(len(y) - x.shape[1], 1))
    covariance = correction * bread_inv @ (cluster_scores.T @ cluster_scores) @ bread_inv
    se = np.sqrt(np.clip(np.diag(covariance), 0.0, None))
    rows = [{
        "event_time": reference_period, "estimate": 0.0, "standard_error": 0.0,
        "ci_low": 0.0, "ci_high": 0.0,
        "n_pairs": int(data.loc[data["event_time"] == reference_period, "match_group"].nunique()),
    }]
    name_to_index = {name: index for index, name in enumerate(design.columns)}
    for event_time in non_reference:
        index = name_to_index[f"event_time_{event_time}"]
        estimate = float(model.coef_[index])
        standard_error = float(se[index])
        rows.append({
            "event_time": int(event_time), "estimate": estimate,
            "standard_error": standard_error,
            "ci_low": estimate - 1.96 * standard_error,
            "ci_high": estimate + 1.96 * standard_error,
            "n_pairs": int(data.loc[data["event_time"] == event_time, "match_group"].nunique()),
        })
    pre_levels = [level for level in non_reference if level < reference_period]
    joint = None
    if pre_levels:
        indices = [name_to_index[f"event_time_{level}"] for level in pre_levels]
        beta = model.coef_[indices]
        cov = covariance[np.ix_(indices, indices)]
        statistic = float(beta.T @ np.linalg.pinv(cov, rcond=1e-10) @ beta)
        joint = {
            "tested_event_times": pre_levels,
            "statistic": statistic,
            "degrees_of_freedom": len(indices),
            "p_value": float(stats.chi2.sf(statistic, len(indices))),
        }
    estimates_path = config.analysis_dir / f"event_study_{config.control_pool}_lag{config.lag_depth}_{outcome}.csv"
    pl.DataFrame(rows).sort("event_time").write_csv(estimates_path)
    output = {
        "outcome": outcome,
        "reference_period": reference_period,
        "estimator": "sklearn OLS on matched-pair differences with manual matched-set cluster covariance",
        "joint_pretrend_test": joint,
        "estimates_path": str(estimates_path),
    }
    (config.analysis_dir / f"event_study_{config.control_pool}_lag{config.lag_depth}_{outcome}.json").write_text(
        json.dumps(output, indent=2), encoding="utf-8"
    )
    return output

from pathlib import Path
import json
import logging
import warnings
import re

import numpy as np
import pandas as pd
import polars as pl

log = logging.getLogger(__name__)

_GCOMP_CANONICAL_HISTORY = {
    "continuous": ["entgelt_value", "rtzb_value"],
    "binary": ["non_success_app_this_year", "non_msk_rehab_this_year"],
    "categorical": ["income_source_status"],
}

def _gcomp_baseline_columns(frame_columns: list[str]) -> list[str]:
    return [
        column for column in frame_columns
        if re.match(r"lag[123]_", column) and not column.endswith("_source_year")
    ]

def _gcomp_history_columns(config: PipelineConfig, available: set[str]) -> dict[str, list[str]]:
    requested = {
        "continuous": list(config.gcomp_timevarying_continuous),
        "binary": list(config.gcomp_timevarying_binary),
        "categorical": list(config.gcomp_timevarying_categorical),
    }
    if not config.source_has_entgelt:
        requested["continuous"] = [
            column for column in requested["continuous"] if column != "entgelt_value"
        ]
    missing = sorted({column for values in requested.values() for column in values} - available)
    if missing:
        raise KeyError(
            "Longitudinal mediation requested post-divorce history columns that are not "
            f"available in the analysis panel: {missing}. No proxy substitution is allowed."
        )
    return requested

def build_longitudinal_mediation_data(
    config: PipelineConfig,
    panel_path: str | Path,
    matches_path: str | Path,
    treated_path: str | Path,
    controls_path: str | Path,
    force: bool = False,
) -> dict[str, Path]:
    horizon = int(config.gcomp_horizon_years)
    if config.year_cap is None:
        raise ValueError("Longitudinal mediation requires a fixed year_cap.")
    if config.year_cap + horizon > config.death_registry_end_year:
        raise ValueError(
            "Longitudinal mediation horizon extends beyond death registration for the "
            "latest treatment cohort."
        )
    panel_schema = set(pl.read_parquet_schema(panel_path))
    history = _gcomp_history_columns(config, panel_schema)
    spec = f"{config.control_pool}_lag{config.lag_depth}"
    output = config.analysis_dir / f"longitudinal_mediation_panel_{spec}.parquet"
    audit_path = config.diagnostics_dir / f"longitudinal_mediation_data_audit_{spec}.json"
    gap_path = config.diagnostics_dir / f"longitudinal_mediation_observation_gaps_{spec}.csv"
    cell_path = config.diagnostics_dir / f"longitudinal_mediation_event_cells_{spec}.csv"
    if all(path.exists() for path in (output, audit_path, gap_path, cell_path)) and not force:
        return {"panel": output, "audit": audit_path, "gaps": gap_path, "event_cells": cell_path}
    assignment = _assignment_frame(matches_path)
    baseline = _baseline_frame(treated_path, controls_path, matches_path)
    baseline_columns = _gcomp_baseline_columns(baseline.columns)
    assignment = assignment.join(
        baseline.select(["simple_id", "t0", *baseline_columns]),
        on=["simple_id", "t0"], how="left",
    )
    current_columns = [
        "simple_id", "ja", "rtwf_jjjj", "msk_starts_this_year",
        *history["continuous"], *history["binary"], *history["categorical"],
    ]
    current_columns = list(dict.fromkeys(current_columns))
    panel = pl.scan_parquet(panel_path).select(current_columns)
    death_years = panel.group_by("simple_id").agg(
        pl.col("rtwf_jjjj").drop_nulls().max().cast(pl.Int32).alias("death_year")
    )
    annual = panel.drop("rtwf_jjjj").with_columns(
        pl.lit(1, dtype=pl.Int8).alias("annual_panel_observed")
    )
    grid = (
        assignment.join(death_years, on="simple_id", how="left")
        .filter(pl.col("death_year").is_null() | (pl.col("death_year") > pl.col("t0")))
        .with_columns(pl.int_ranges(1, horizon + 1).alias("follow_year"))
        .explode("follow_year")
        .with_columns([
            (pl.col("t0") + pl.col("follow_year")).cast(pl.Int32).alias("ja"),
            pl.col("follow_year").cast(pl.Int8),
        ])
        .join(annual, on=["simple_id", "ja"], how="left")
        .with_columns([
            pl.col("annual_panel_observed").fill_null(0).cast(pl.Int8),
            (
                pl.col("death_year").is_null() | (pl.col("death_year") >= pl.col("ja"))
            ).cast(pl.Int8).alias("alive_at_start"),
            (
                pl.col("death_year").is_not_null() & (pl.col("death_year") == pl.col("ja"))
            ).cast(pl.Int8).alias("death_event"),
            pl.when(pl.col("annual_panel_observed") == 1)
            .then((pl.col("msk_starts_this_year").fill_null(0) > 0).cast(pl.Int8))
            .otherwise(None)
            .alias("msk_event_observed"),
        ])
        .sort(["simple_id", "t0", "follow_year"])
    )
    spell = ["simple_id", "t0"]
    grid = grid.with_columns([
        pl.when(
            (pl.col("alive_at_start") == 1) & (pl.col("annual_panel_observed") == 0)
        ).then(pl.col("follow_year")).otherwise(None)
        .min().over(spell).cast(pl.Int8).alias("first_gap_year"),
        pl.col("msk_event_observed").fill_null(0).cum_sum().over(spell)
        .cast(pl.Int16).alias("cum_observed_msk_through_year"),
    ]).with_columns([
        (
            pl.col("cum_observed_msk_through_year")
            - pl.col("msk_event_observed").fill_null(0)
            > 0
        ).cast(pl.Int8).alias("mediator_prev"),
        (
            pl.col("cum_observed_msk_through_year") > 0
        ).cast(pl.Int8).alias("mediator_current"),
        (
            (pl.col("msk_event_observed").fill_null(0) == 1)
            & (
                pl.col("cum_observed_msk_through_year")
                - pl.col("msk_event_observed").fill_null(0)
                == 0
            )
        ).cast(pl.Int8).alias("mediator_incident_current"),
        (
            pl.col("alive_at_start") == 1
        ).cast(pl.Int8).alias("in_survival_risk_set"),
        (
            (pl.col("alive_at_start") == 1)
            & (
                pl.col("first_gap_year").is_null()
                | (pl.col("follow_year") <= pl.col("first_gap_year"))
            )
        ).cast(pl.Int8).alias("in_observation_risk_set"),
        (
            (pl.col("alive_at_start") == 1)
            & (pl.col("annual_panel_observed") == 1)
            & (
                pl.col("first_gap_year").is_null()
                | (pl.col("follow_year") < pl.col("first_gap_year"))
            )
        ).cast(pl.Int8).alias("history_observed_for_analysis"),
    ])
    rename_exprs: list[pl.Expr] = []
    for column in history["continuous"] + history["binary"] + history["categorical"]:
        rename_exprs.append(pl.col(column).alias(f"current_{column}"))
    grid = grid.with_columns(rename_exprs)
    prior_exprs: list[pl.Expr] = []
    for column in history["continuous"] + history["binary"] + history["categorical"]:
        lag1_name = f"lag1_{column}"
        if lag1_name not in baseline_columns:
            raise KeyError(
                f"Longitudinal mediation needs {lag1_name} to initialize the year-1 history."
            )
        prior_exprs.append(
            pl.when(pl.col("follow_year") == 1)
            .then(pl.col(lag1_name))
            .otherwise(pl.col(f"current_{column}").shift(1).over(spell))
            .alias(f"prior_{column}")
        )
    grid = grid.with_columns(prior_exprs)
    keep_columns = [
        "simple_id", "t0", "match_group", "treated", "ja", "follow_year",
        "death_year", "alive_at_start", "death_event", "annual_panel_observed",
        "first_gap_year", "in_observation_risk_set", "history_observed_for_analysis",
        "mediator_prev", "mediator_incident_current", "mediator_current",
        *baseline_columns,
    ]
    for column in history["continuous"] + history["binary"] + history["categorical"]:
        keep_columns.extend([f"prior_{column}", f"current_{column}"])
    grid = grid.select(list(dict.fromkeys(keep_columns))).sort(
        ["match_group", "treated", "follow_year"]
    )
    sink_parquet(grid, output, config.checkpoint_row_group_size)
    saved = pl.scan_parquet(output)
    gap_detail = (
        saved.filter(pl.col("in_observation_risk_set") == 1)
        .group_by(["treated", "follow_year"])
        .agg([
            pl.len().alias("at_risk_person_years"),
            (pl.col("annual_panel_observed") == 0).sum().alias("first_gap_rows"),
            pl.col("simple_id").filter(pl.col("annual_panel_observed") == 0)
            .n_unique().alias("people_first_gapping"),
        ])
        .with_columns(
            (pl.col("first_gap_rows") / pl.col("at_risk_person_years"))
            .alias("gap_probability")
        )
        .sort(["treated", "follow_year"])
        .pipe(_safe_collect)
    )
    gap_detail.write_csv(gap_path)
    people = (
        saved.group_by(["simple_id", "t0", "match_group", "treated"])
        .agg([
            pl.col("mediator_incident_current")
            .filter(pl.col("history_observed_for_analysis") == 1)
            .max().fill_null(0).alias("observed_first_msk_by_horizon"),
            pl.col("death_event").max().alias("death_by_horizon"),
            (pl.col("annual_panel_observed") == 0)
            .filter(pl.col("in_observation_risk_set") == 1)
            .max().fill_null(False).cast(pl.Int8).alias("censored_at_record_gap"),
        ])
    )
    event_cells = (
        people.group_by(["treated", "observed_first_msk_by_horizon", "death_by_horizon"])
        .agg(pl.len().alias("people"))
        .sort(["treated", "observed_first_msk_by_horizon", "death_by_horizon"])
        .pipe(_safe_collect)
    )
    event_cells.write_csv(cell_path)
    same_year = saved.filter(
        (pl.col("history_observed_for_analysis") == 1)
        & (pl.col("mediator_incident_current") == 1)
        & (pl.col("death_event") == 1)
    ).select(pl.len()).pipe(_safe_collect).item()
    audit = {
        "estimator_data": "annual longitudinal histories for survival mediational g-computation",
        "target_followup_horizon_years": horizon,
        "temporal_order": (
            "At year t: use baseline and completed history through t-1 -> first MSK entry "
            "in t -> death in t -> update annual economic/health history in t for use at t+1."
        ),
        "same_year_msk_death_rule": (
            "MSK is ordered before death when both occur in the same calendar year because "
            "a recorded rehabilitation start implies survival to that start."
        ),
        "matched_people": int(saved.select(pl.col("simple_id").count()).pipe(_safe_collect).item() / horizon),
        "matched_pairs": int(saved.select(pl.col("match_group").n_unique()).pipe(_safe_collect).item()),
        "person_year_grid_rows": int(saved.select(pl.len()).pipe(_safe_collect).item()),
        "observed_history_rows_used_before_ipcw": int(
            saved.filter(pl.col("history_observed_for_analysis") == 1)
            .select(pl.len()).pipe(_safe_collect).item()
        ),
        "people_with_first_observation_gap": int(
            people.filter(pl.col("censored_at_record_gap") == 1)
            .select(pl.len()).pipe(_safe_collect).item()
        ),
        "observed_first_msk_events_before_gap": int(
            people.select(pl.col("observed_first_msk_by_horizon").sum()).pipe(_safe_collect).item()
        ),
        "deaths_within_horizon": int(
            people.select(pl.col("death_by_horizon").sum()).pipe(_safe_collect).item()
        ),
        "same_calendar_year_first_msk_and_death": int(same_year or 0),
        "death_measure": "person-level rtwf_jjjj; death does not require an annual record",
        "record_gap_rule": (
            "The mediation history is censored at the first missing annual record while alive. "
            "The estimator optionally uses inverse-probability-of-observation weights based "
            "only on history known before that gap."
        ),
        "post_divorce_history": history,
        "gap_detail_csv": str(gap_path),
        "event_cell_csv": str(cell_path),
    }
    audit_path.write_text(json.dumps(audit, indent=2), encoding="utf-8")
    return {"panel": output, "audit": audit_path, "gaps": gap_path, "event_cells": cell_path}

def _gcomp_feature_columns(config: PipelineConfig, columns: set[str]) -> FeatureColumns:
    return resolve_features(config, columns)

def _gcomp_preprocessor(
    numeric: list[str],
    binary: list[str],
    categorical: list[str],
    config: PipelineConfig,
) -> ColumnTransformer:
    transformers = []
    if numeric:
        transformers.append(("numeric", Pipeline([
            ("impute", SimpleImputer(strategy="median", add_indicator=True)),
            ("scale", StandardScaler()),
        ]), numeric))
    if binary:
        transformers.append(("binary", Pipeline([
            ("impute", SimpleImputer(strategy="most_frequent", add_indicator=True)),
            ("scale", StandardScaler()),
        ]), binary))
    if categorical:
        transformers.append(("categorical", Pipeline([
            ("impute", SimpleImputer(strategy="constant", fill_value="__MISSING__")),
            ("onehot", _make_one_hot_encoder(
                sparse_output=False,
                min_frequency=config.minimum_category_frequency,
            )),
        ]), categorical))
    return ColumnTransformer(transformers=transformers, sparse_threshold=0.0)

def _gcomp_fit_binary(
    data: pd.DataFrame,
    outcome: str,
    numeric: list[str],
    binary: list[str],
    categorical: list[str],
    weights: np.ndarray | None,
    config: PipelineConfig,
) -> dict:
    y = pd.to_numeric(data[outcome], errors="raise").astype(int).to_numpy()
    if len(y) == 0:
        raise ValueError(f"No rows available for binary model {outcome}.")
    if np.unique(y).size == 1:
        return {"kind": "binary_constant", "probability": float(y[0]), "outcome": outcome}
    predictors = list(dict.fromkeys([*numeric, *binary, *categorical]))
    pre = _gcomp_preprocessor(numeric, binary, categorical, config)
    x0 = pre.fit_transform(data[predictors])
    x = np.column_stack([np.ones(len(data)), np.asarray(x0, dtype=float)])
    model = _unpenalized_logistic_regression(
        x, y, sample_weight=weights,
        max_iter=config.gcomp_logit_max_iter, tol=config.gcomp_logit_tol,
        extra_fallbacks=True, accept_unconverged=True,
    )
    return {
        "kind": "binary", "preprocessor": pre, "model": model,
        "predictors": predictors, "outcome": outcome,
        "fit_method": getattr(model, "_pipeline_fit_method", "unknown"),
        "converged": bool(getattr(model, "_pipeline_converged", True)),
        "n_iter": getattr(model, "_pipeline_n_iter", None),
    }

def _gcomp_predict_binary(model: dict, data: pd.DataFrame) -> np.ndarray:
    if model["kind"] == "binary_constant":
        return np.full(len(data), float(model["probability"]), dtype=float)
    x0 = model["preprocessor"].transform(data[model["predictors"]])
    x = np.column_stack([np.ones(len(data)), np.asarray(x0, dtype=float)])
    return np.clip(model["model"].predict_proba(x)[:, 1], 1e-9, 1 - 1e-9)

def _gcomp_fit_multiclass(
    data: pd.DataFrame,
    outcome: str,
    numeric: list[str],
    binary: list[str],
    categorical: list[str],
    weights: np.ndarray | None,
    config: PipelineConfig,
) -> dict:
    y = data[outcome].astype("string").fillna("__MISSING__").astype(str).to_numpy()
    classes = np.unique(y)
    if len(y) == 0:
        raise ValueError(f"No rows available for categorical model {outcome}.")
    if len(classes) == 1:
        return {"kind": "categorical_constant", "value": str(classes[0]), "outcome": outcome}
    predictors = list(dict.fromkeys([*numeric, *binary, *categorical]))
    pre = _gcomp_preprocessor(numeric, binary, categorical, config)
    x = np.asarray(pre.fit_transform(data[predictors]), dtype=float)
    base_iter = int(config.gcomp_logit_max_iter)
    tol = float(config.gcomp_logit_tol)
    attempts = [
        {"penalty": None, "solver": "lbfgs", "max_iter": base_iter, "label": "unpenalized_none_lbfgs"},
        {"penalty": "none", "solver": "lbfgs", "max_iter": base_iter, "label": "unpenalized_string_lbfgs"},
        {"penalty": "l2", "C": 1e4, "solver": "lbfgs", "max_iter": 2 * base_iter, "label": "tiny_ridge_fallback_C1e4"},
        {"penalty": "l2", "C": 1e2, "solver": "lbfgs", "max_iter": 2 * base_iter, "label": "ridge_fallback_C1e2"},
        {"penalty": "l2", "C": 1e1, "solver": "lbfgs", "max_iter": 2 * base_iter, "label": "ridge_fallback_C1e1"},
        {"penalty": "l2", "C": 1.0, "solver": "lbfgs", "max_iter": 2 * base_iter, "label": "ridge_fallback_C1"},
    ]
    last_error = None
    fitted = None
    fit_label = None
    fallback = None
    fallback_label = None
    converged = False
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        for attempt in attempts:
            attempt = dict(attempt)
            label = attempt.pop("label")
            try:
                candidate = LogisticRegression(
                    fit_intercept=True, tol=tol, random_state=config.seed, **attempt
                )
                candidate.fit(x, y, sample_weight=weights)
                if int(np.max(candidate.n_iter_)) < candidate.max_iter:
                    fitted = candidate
                    fit_label = label
                    converged = True
                    break
                fallback, fallback_label = candidate, label
                last_error = RuntimeError(f"{label} reached max_iter={candidate.max_iter}")
            except (TypeError, ValueError, RuntimeError) as exc:
                last_error = exc
    if fitted is None and fallback is not None:
        log.warning(
            "Multinomial model for %s accepted without convergence (%s after %d iterations, "
            "tol=%g); recorded in the mediation diagnostics.",
            outcome, fallback_label, int(np.max(fallback.n_iter_)), tol,
        )
        fitted, fit_label = fallback, fallback_label
    if fitted is None:
        raise RuntimeError(f"All multinomial fitting routes failed for {outcome}: {last_error}")
    return {
        "kind": "categorical", "preprocessor": pre, "model": fitted,
        "predictors": predictors, "outcome": outcome, "fit_method": fit_label,
        "converged": bool(converged), "n_iter": int(np.max(fitted.n_iter_)),
    }

def _gcomp_sample_multiclass(model: dict, data: pd.DataFrame, rng: np.random.Generator) -> np.ndarray:
    if model["kind"] == "categorical_constant":
        return np.full(len(data), model["value"], dtype=object)
    x = np.asarray(model["preprocessor"].transform(data[model["predictors"]]), dtype=float)
    probabilities = np.asarray(model["model"].predict_proba(x), dtype=float)
    probabilities = probabilities / probabilities.sum(axis=1, keepdims=True)
    cumulative = np.cumsum(probabilities, axis=1)
    draws = rng.random(len(data))[:, None]
    positions = (cumulative < draws).sum(axis=1)
    positions = np.minimum(positions, len(model["model"].classes_) - 1)
    return model["model"].classes_[positions].astype(object)

def _gcomp_fit_continuous_log(
    data: pd.DataFrame,
    outcome: str,
    numeric: list[str],
    binary: list[str],
    categorical: list[str],
    weights: np.ndarray | None,
    config: PipelineConfig,
) -> dict:
    y_raw = pd.to_numeric(data[outcome], errors="coerce").fillna(0.0).to_numpy(float)
    y_raw = np.clip(y_raw, 0.0, None)
    y = np.log1p(y_raw)
    if len(y) == 0:
        raise ValueError(f"No rows available for continuous model {outcome}.")
    predictors = list(dict.fromkeys([*numeric, *binary, *categorical]))
    pre = _gcomp_preprocessor(numeric, binary, categorical, config)
    x0 = np.asarray(pre.fit_transform(data[predictors]), dtype=float)
    x = np.column_stack([np.ones(len(data)), x0])
    model = LinearRegression(fit_intercept=False)
    model.fit(x, y, sample_weight=weights)
    fitted = model.predict(x)
    residual = y - fitted
    if weights is None:
        residual_sd = float(np.std(residual, ddof=1)) if len(residual) > 1 else 0.0
    else:
        w = np.asarray(weights, dtype=float)
        w = w / max(w.sum(), 1e-12)
        mean_resid = float(np.sum(w * residual))
        residual_sd = float(np.sqrt(np.sum(w * (residual - mean_resid) ** 2)))
    observed_log_max = float(np.max(y)) if len(y) else 0.0
    log_value_cap = observed_log_max + float(config.gcomp_continuous_log_cap_headroom)
    return {
        "kind": "continuous_log", "preprocessor": pre, "model": model,
        "predictors": predictors, "outcome": outcome,
        "residual_sd": max(residual_sd, 0.0),
        "observed_log_max": observed_log_max,
        "log_value_cap": log_value_cap,
    }

def _gcomp_sample_continuous_log(
    model: dict,
    data: pd.DataFrame,
    rng: np.random.Generator,
) -> np.ndarray:
    x0 = np.asarray(model["preprocessor"].transform(data[model["predictors"]]), dtype=float)
    x = np.column_stack([np.ones(len(data)), x0])
    mean = model["model"].predict(x)
    if model["residual_sd"] > 0:
        value = mean + rng.normal(0.0, model["residual_sd"], size=len(data))
    else:
        value = mean
    cap = model.get("log_value_cap")
    if cap is not None:
        n_clipped = int(np.sum(value > cap))
        if n_clipped > 0:
            log.warning(
                "Continuous g-computation draw for %s exceeded the extrapolation cap "
                "(observed training log-max=%.3f, cap=%.3f) on %d of %d simulated rows; "
                "these draws were truncated to the cap before being converted back to "
                "the original scale.",
                model.get("outcome", "<unknown>"), model.get("observed_log_max", float("nan")),
                cap, n_clipped, len(value),
            )
        value = np.clip(value, None, cap)
    return np.clip(np.expm1(value), 0.0, None)

def _gcomp_model_specs(config: PipelineConfig, features: FeatureColumns) -> dict[str, list[str]]:
    baseline_numeric = list(features.numeric)
    baseline_binary = list(features.binary)
    baseline_categorical = list(dict.fromkeys(features.categorical + features.exact))
    dynamic_numeric = ["prior_rtzb_value"]
    if config.source_has_entgelt:
        dynamic_numeric.insert(0, "prior_entgelt_value")
    dynamic_binary = ["prior_non_success_app_this_year", "prior_non_msk_rehab_this_year"]
    dynamic_categorical = ["prior_income_source_status", "follow_year_cat"]
    return {
        "numeric": list(dict.fromkeys([*baseline_numeric, *dynamic_numeric])),
        "binary": list(dict.fromkeys([*baseline_binary, *dynamic_binary, "treated", "mediator_prev"])),
        "categorical": list(dict.fromkeys([*baseline_categorical, *dynamic_categorical])),
    }

def _gcomp_compute_ipcw(
    data: pd.DataFrame,
    config: PipelineConfig,
    features: FeatureColumns,
) -> tuple[pd.DataFrame, dict, dict]:
    result = data.copy()
    result["follow_year_cat"] = result["follow_year"].astype(int).astype(str)
    obs_risk = result.loc[
        (result["in_observation_risk_set"] == 1)
    ].copy()
    specs = _gcomp_model_specs(config, features)
    observation_model = _gcomp_fit_binary(
        obs_risk,
        "annual_panel_observed",
        specs["numeric"], specs["binary"], specs["categorical"],
        weights=None,
        config=config,
    )
    p_obs = _gcomp_predict_binary(observation_model, obs_risk)
    floor = float(config.gcomp_observation_probability_floor)
    p_obs_clipped = np.clip(p_obs, floor, 1.0)
    obs_risk["p_observed"] = p_obs
    obs_risk["p_observed_for_weight"] = p_obs_clipped
    obs_risk = obs_risk.sort_values(["match_group", "simple_id", "t0", "follow_year"]).copy()
    factor = np.where(
        obs_risk["annual_panel_observed"].to_numpy(int) == 1,
        1.0 / obs_risk["p_observed_for_weight"].to_numpy(float),
        1.0,
    )
    obs_risk["_ipcw_factor"] = factor
    obs_risk["ipcw_raw"] = (
        obs_risk.groupby(["match_group", "simple_id", "t0"], sort=False)["_ipcw_factor"].cumprod()
    )
    obs_risk = obs_risk.drop(columns=["_ipcw_factor"])
    if config.gcomp_use_observation_ipcw:
        obs_risk["ipcw"] = np.minimum(
            obs_risk["ipcw_raw"].to_numpy(float), float(config.gcomp_ipcw_cap)
        )
    else:
        obs_risk["ipcw"] = 1.0
    result = result.merge(
        obs_risk[["match_group", "simple_id", "t0", "follow_year", "p_observed", "ipcw_raw", "ipcw"]],
        on=["match_group", "simple_id", "t0", "follow_year"], how="left", validate="one_to_one",
    )
    observed_for_models = result.loc[
        (result["history_observed_for_analysis"] == 1)
    ].copy()
    observed_for_models["ipcw"] = observed_for_models["ipcw"].fillna(1.0)
    diagnostics = {
        "observation_model_fit_method": observation_model.get("fit_method", observation_model["kind"]),
        "observation_risk_rows": int(len(obs_risk)),
        "first_gap_rows": int((obs_risk["annual_panel_observed"] == 0).sum()),
        "p_observed_min": float(np.min(p_obs)) if len(p_obs) else None,
        "p_observed_p01": float(np.quantile(p_obs, 0.01)) if len(p_obs) else None,
        "p_observed_p99": float(np.quantile(p_obs, 0.99)) if len(p_obs) else None,
        "p_observed_max": float(np.max(p_obs)) if len(p_obs) else None,
        "probability_floor": floor,
        "raw_ipcw_max": float(obs_risk["ipcw_raw"].max()) if len(obs_risk) else None,
        "ipcw_cap": float(config.gcomp_ipcw_cap),
        "rows_at_ipcw_cap": int((obs_risk["ipcw"] >= float(config.gcomp_ipcw_cap) - 1e-12).sum()),
        "use_observation_ipcw": bool(config.gcomp_use_observation_ipcw),
    }
    return observed_for_models, observation_model, diagnostics

def _gcomp_fit_models(
    data: pd.DataFrame,
    config: PipelineConfig,
) -> tuple[dict, pd.DataFrame, dict]:
    available = set(data.columns)
    features = _gcomp_feature_columns(config, available)
    model_data, observation_model, observation_diagnostics = _gcomp_compute_ipcw(
        data, config, features
    )
    if model_data.empty:
        raise RuntimeError("No fully observed pre-gap person-years remain for longitudinal mediation.")
    specs = _gcomp_model_specs(config, features)
    weights = model_data["ipcw"].to_numpy(float)
    mediator_rows = model_data.loc[model_data["mediator_prev"] == 0].copy()
    mediator_model = _gcomp_fit_binary(
        mediator_rows,
        "mediator_incident_current",
        specs["numeric"], specs["binary"], specs["categorical"],
        mediator_rows["ipcw"].to_numpy(float), config,
    )
    death_binary = list(dict.fromkeys([
        *specs["binary"], "mediator_current", "treated_x_mediator_current"
    ]))
    model_data["treated_x_mediator_current"] = (
        model_data["treated"].astype(float) * model_data["mediator_current"].astype(float)
    )
    death_model = _gcomp_fit_binary(
        model_data,
        "death_event",
        specs["numeric"], death_binary, specs["categorical"],
        weights, config,
    )
    survivors = model_data.loc[model_data["death_event"] == 0].copy()
    if survivors.empty:
        raise RuntimeError("No survivors remain to fit post-year history models.")
    history_binary_predictors = list(dict.fromkeys([*specs["binary"], "mediator_current"]))
    history_categorical_predictors = list(specs["categorical"])
    history_numeric_predictors = list(specs["numeric"])
    status_model = _gcomp_fit_multiclass(
        survivors,
        "current_income_source_status",
        history_numeric_predictors,
        history_binary_predictors,
        history_categorical_predictors,
        survivors["ipcw"].to_numpy(float), config,
    )
    amount_numeric = list(history_numeric_predictors)
    amount_binary = list(history_binary_predictors)
    amount_categorical = list(dict.fromkeys([
        *history_categorical_predictors, "current_income_source_status"
    ]))
    continuous_models: dict[str, dict] = {}
    for variable in config.gcomp_timevarying_continuous:
        if variable == "entgelt_value" and not config.source_has_entgelt:
            continue
        continuous_models[variable] = _gcomp_fit_continuous_log(
            survivors,
            f"current_{variable}",
            amount_numeric, amount_binary, amount_categorical,
            survivors["ipcw"].to_numpy(float), config,
        )
    current_numeric_predictors = list(amount_numeric)
    for variable in config.gcomp_timevarying_continuous:
        if variable == "entgelt_value" and not config.source_has_entgelt:
            continue
        current_numeric_predictors.append(f"current_{variable}")
    binary_models: dict[str, dict] = {}
    previous_current_binary: list[str] = []
    for variable in config.gcomp_timevarying_binary:
        predictor_binary = list(dict.fromkeys([
            *amount_binary, *previous_current_binary
        ]))
        binary_models[variable] = _gcomp_fit_binary(
            survivors,
            f"current_{variable}",
            current_numeric_predictors,
            predictor_binary,
            amount_categorical,
            survivors["ipcw"].to_numpy(float), config,
        )
        previous_current_binary.append(f"current_{variable}")
    mediator_probability = _gcomp_predict_binary(mediator_model, mediator_rows)
    death_probability = _gcomp_predict_binary(death_model, model_data)
    diagnostics = {
        **observation_diagnostics,
        "analysis_person_years": int(len(model_data)),
        "mediator_risk_rows": int(len(mediator_rows)),
        "mediator_events": int(mediator_rows["mediator_incident_current"].sum()),
        "death_events": int(model_data["death_event"].sum()),
        "survivor_rows_for_history_models": int(len(survivors)),
        "mediator_model_fit_method": mediator_model.get("fit_method", mediator_model["kind"]),
        "mediator_probability_min": float(np.min(mediator_probability)) if len(mediator_probability) else None,
        "mediator_probability_p01": float(np.quantile(mediator_probability, 0.01)) if len(mediator_probability) else None,
        "mediator_probability_p99": float(np.quantile(mediator_probability, 0.99)) if len(mediator_probability) else None,
        "mediator_probability_max": float(np.max(mediator_probability)) if len(mediator_probability) else None,
        "death_model_fit_method": death_model.get("fit_method", death_model["kind"]),
        "death_probability_min": float(np.min(death_probability)) if len(death_probability) else None,
        "death_probability_p01": float(np.quantile(death_probability, 0.01)) if len(death_probability) else None,
        "death_probability_p99": float(np.quantile(death_probability, 0.99)) if len(death_probability) else None,
        "death_probability_max": float(np.max(death_probability)) if len(death_probability) else None,
        "income_status_model_fit_method": status_model.get("fit_method", status_model["kind"]),
        "income_status_model_converged": status_model.get("converged", True),
        "income_status_model_iterations": status_model.get("n_iter"),
        "mediator_model_converged": mediator_model.get("converged", True),
        "death_model_converged": death_model.get("converged", True),
        "observation_model_converged": observation_model.get("converged", True),
        "history_binary_model_fit": {
            name: {
                "fit_method": model.get("fit_method", model["kind"]),
                "converged": model.get("converged", True),
                "n_iter": model.get("n_iter"),
            }
            for name, model in binary_models.items()
        },
        "logit_iteration_budget": int(config.gcomp_logit_max_iter),
        "logit_tolerance": float(config.gcomp_logit_tol),
        "continuous_model_log_value_caps": {
            name: {
                "observed_log_max": model["observed_log_max"],
                "log_value_cap": model["log_value_cap"],
            }
            for name, model in continuous_models.items()
        },
        "post_divorce_history_models": {
            "continuous": list(continuous_models),
            "binary": list(binary_models),
            "categorical": ["income_source_status"],
        },
    }
    return {
        "features": features,
        "specs": specs,
        "observation": observation_model,
        "mediator": mediator_model,
        "death": death_model,
        "status": status_model,
        "continuous": continuous_models,
        "binary": binary_models,
    }, model_data, diagnostics

def _gcomp_base_treated_people(data: pd.DataFrame, features: FeatureColumns) -> pd.DataFrame:
    baseline_columns = list(dict.fromkeys([
        *features.numeric, *features.binary, *features.categorical, *features.exact
    ]))
    keys = ["simple_id", "t0", "match_group", "treated"]
    base = data.loc[data["treated"] == 1, keys + baseline_columns].drop_duplicates(keys)
    if base.empty:
        raise RuntimeError("No matched treated people are available for ATT standardization.")
    return base.reset_index(drop=True)

def _gcomp_initial_state(base: pd.DataFrame, config: PipelineConfig) -> pd.DataFrame:
    state = base.copy()
    def _numeric_series(name: str, default: float = 0.0) -> pd.Series:
        if name in state.columns:
            return pd.to_numeric(state[name], errors="coerce").fillna(default).astype(float)
        return pd.Series(default, index=state.index, dtype=float)
    if config.source_has_entgelt:
        state["prior_entgelt_value"] = _numeric_series("lag1_entgelt_value", 0.0)
    state["prior_rtzb_value"] = _numeric_series("lag1_rtzb_value", 0.0)
    state["prior_non_success_app_this_year"] = (
        _numeric_series("lag1_non_success_app_this_year", 0.0).astype(int)
    )
    state["prior_non_msk_rehab_this_year"] = (
        _numeric_series("lag1_non_msk_rehab_this_year", 0.0).astype(int)
    )
    if "lag1_income_source_status" in state.columns:
        state["prior_income_source_status"] = (
            state["lag1_income_source_status"].astype("string")
            .fillna("__MISSING__").astype(str)
        )
    else:
        state["prior_income_source_status"] = "__MISSING__"
    state["mediator_prev"] = 0
    return state

def _gcomp_simulation_frame(
    state: pd.DataFrame,
    treatment: int,
    follow_year: int,
    mediator_prev: np.ndarray,
    mediator_current: np.ndarray | None = None,
) -> pd.DataFrame:
    frame = state.copy()
    frame["treated"] = int(treatment)
    frame["follow_year"] = int(follow_year)
    frame["follow_year_cat"] = str(int(follow_year))
    frame["mediator_prev"] = np.asarray(mediator_prev, dtype=int)
    if mediator_current is not None:
        frame["mediator_current"] = np.asarray(mediator_current, dtype=int)
        frame["treated_x_mediator_current"] = (
            int(treatment) * np.asarray(mediator_current, dtype=int)
        )
    return frame

def _gcomp_simulate_history_update(
    models: dict,
    frame: pd.DataFrame,
    rng: np.random.Generator,
    config: PipelineConfig,
) -> pd.DataFrame:
    updated = frame.copy()
    updated["current_income_source_status"] = _gcomp_sample_multiclass(
        models["status"], updated, rng
    )
    for variable, model in models["continuous"].items():
        updated[f"current_{variable}"] = _gcomp_sample_continuous_log(model, updated, rng)
    status = updated["current_income_source_status"].astype(str)
    if "current_entgelt_value" in updated.columns:
        has_earnings = status.isin(["earnings_only", "earnings_and_pension"])
        updated.loc[~has_earnings, "current_entgelt_value"] = 0.0
    if "current_rtzb_value" in updated.columns:
        has_pension = status.isin(["pension_only", "earnings_and_pension"])
        updated.loc[~has_pension, "current_rtzb_value"] = 0.0
    for variable, model in models["binary"].items():
        probability = _gcomp_predict_binary(model, updated)
        updated[f"current_{variable}"] = (
            rng.random(len(updated)) < probability
        ).astype(int)
    if "current_entgelt_value" in updated.columns:
        updated["prior_entgelt_value"] = updated["current_entgelt_value"].to_numpy(float)
    updated["prior_rtzb_value"] = updated["current_rtzb_value"].to_numpy(float)
    updated["prior_income_source_status"] = updated["current_income_source_status"].astype(str)
    updated["prior_non_success_app_this_year"] = updated[
        "current_non_success_app_this_year"
    ].to_numpy(int)
    updated["prior_non_msk_rehab_this_year"] = updated[
        "current_non_msk_rehab_this_year"
    ].to_numpy(int)
    return updated

def _gcomp_simulate_source_event_times(
    models: dict,
    base: pd.DataFrame,
    treatment: int,
    config: PipelineConfig,
    rng: np.random.Generator,
) -> np.ndarray:
    horizon = int(config.gcomp_horizon_years)
    state = _gcomp_initial_state(base, config)
    n = len(state)
    mediator_prev = np.zeros(n, dtype=int)
    event_time = np.full(n, horizon + 1, dtype=np.int16)
    for follow_year in range(1, horizon + 1):
        frame = _gcomp_simulation_frame(state, treatment, follow_year, mediator_prev)
        at_risk = mediator_prev == 0
        incident = np.zeros(n, dtype=int)
        if np.any(at_risk):
            probability = _gcomp_predict_binary(models["mediator"], frame.loc[at_risk])
            draws = (rng.random(np.sum(at_risk)) < probability).astype(int)
            incident[np.flatnonzero(at_risk)] = draws
            newly = np.flatnonzero(at_risk)[draws == 1]
            event_time[newly] = np.int16(follow_year)
        mediator_current = np.maximum(mediator_prev, incident)
        if follow_year < horizon:
            history_frame = _gcomp_simulation_frame(
                state, treatment, follow_year, mediator_prev, mediator_current
            )
            state = _gcomp_simulate_history_update(models, history_frame, rng, config)
        mediator_prev = mediator_current
    return event_time

def _gcomp_survival_risk_with_event_times(
    models: dict,
    base: pd.DataFrame,
    treatment: int,
    assigned_event_time: np.ndarray,
    config: PipelineConfig,
    rng: np.random.Generator,
) -> tuple[float, float]:
    horizon = int(config.gcomp_horizon_years)
    state = _gcomp_initial_state(base, config)
    assigned_event_time = np.asarray(assigned_event_time, dtype=int)
    if len(assigned_event_time) != len(state):
        raise ValueError("assigned_event_time must have one value per ATT baseline row")
    survival_probability = np.ones(len(state), dtype=float)
    for follow_year in range(1, horizon + 1):
        mediator_prev = (assigned_event_time < follow_year).astype(int)
        mediator_current = (assigned_event_time <= follow_year).astype(int)
        death_frame = _gcomp_simulation_frame(
            state, treatment, follow_year, mediator_prev, mediator_current
        )
        death_probability = _gcomp_predict_binary(models["death"], death_frame)
        survival_probability *= (1.0 - death_probability)
        if follow_year < horizon:
            history_frame = _gcomp_simulation_frame(
                state, treatment, follow_year, mediator_prev, mediator_current
            )
            state = _gcomp_simulate_history_update(models, history_frame, rng, config)
    mortality_risk = 1.0 - float(np.mean(survival_probability))
    first_msk_risk = float(np.mean(assigned_event_time <= horizon))
    return mortality_risk, first_msk_risk

def _gcomp_estimate_q_values(
    models: dict,
    base: pd.DataFrame,
    config: PipelineConfig,
    n_simulations: int,
    seed: int,
) -> dict:
    rng = np.random.default_rng(seed)
    rows: list[dict] = []
    for repetition in range(n_simulations):
        source0 = _gcomp_simulate_source_event_times(models, base, 0, config, rng)
        source1 = _gcomp_simulate_source_event_times(models, base, 1, config, rng)
        intervention0 = rng.permutation(source0)
        intervention1 = rng.permutation(source1)
        q00, m00 = _gcomp_survival_risk_with_event_times(
            models, base, 0, intervention0, config, rng
        )
        q10, m10 = _gcomp_survival_risk_with_event_times(
            models, base, 1, intervention0, config, rng
        )
        q11, m11 = _gcomp_survival_risk_with_event_times(
            models, base, 1, intervention1, config, rng
        )
        q01, m01 = _gcomp_survival_risk_with_event_times(
            models, base, 0, intervention1, config, rng
        )
        rows.append({
            "repetition": repetition,
            "risk_q00": q00,
            "risk_q10": q10,
            "risk_q11": q11,
            "risk_q01": q01,
            "msk_q00": m00,
            "msk_q10": m10,
            "msk_q11": m11,
            "msk_q01": m01,
        })
    simulation = pd.DataFrame(rows)
    means = simulation.mean(numeric_only=True).to_dict()
    q00 = float(means["risk_q00"])
    q10 = float(means["risk_q10"])
    q11 = float(means["risk_q11"])
    total = q11 - q00
    direct = q10 - q00
    indirect = q11 - q10
    proportion = indirect / total if abs(total) > 1e-12 else np.nan
    return {
        "risk_q00": q00,
        "risk_q10": q10,
        "risk_q11": q11,
        "risk_q01": float(means["risk_q01"]),
        "interventional_total_effect_risk_difference": total,
        "interventional_direct_effect_risk_difference": direct,
        "interventional_indirect_effect_risk_difference": indirect,
        "proportion_mediated": float(proportion) if np.isfinite(proportion) else None,
        "simulated_first_msk_risk_q00": float(means["msk_q00"]),
        "simulated_first_msk_risk_q11": float(means["msk_q11"]),
        "monte_carlo_repetitions": int(n_simulations),
        "simulation_rows": rows,
    }

def _fit_longitudinal_mediation_once(
    data: pd.DataFrame,
    config: PipelineConfig,
    n_simulations: int,
    seed: int,
) -> dict:
    models, model_data, diagnostics = _gcomp_fit_models(data, config)
    base = _gcomp_base_treated_people(model_data, models["features"])
    estimates = _gcomp_estimate_q_values(
        models, base, config, n_simulations=n_simulations, seed=seed
    )
    simulation_rows = estimates.pop("simulation_rows")
    return {
        **estimates,
        "target_population": "baseline covariate distribution of the matched treated individuals (ATT standardization)",
        "estimator": (
            "parametric survival mediational g-formula with fixed divorce exposure, "
            "an absorbing first-MSK event-time process randomized from the source-treatment "
            "joint mediator distribution, annually updated lagged history, "
            "interventional direct/indirect effects, and optional observation IPCW"
        ),
        "history_order": (
            "L(t-1) -> first MSK at t -> death at t -> L(t) for use at t+1"
        ),
        "model_diagnostics": diagnostics,
        "simulation_diagnostics": simulation_rows,
    }

_MEDIATION_WORKER_STATE: dict = {}

def _mediation_worker_init(panel_path: str, config_dict: dict) -> None:


    import warnings as _warnings
    _warnings.simplefilter("ignore")
    data = pl.read_parquet(panel_path).to_pandas()
    groups = np.array(sorted(data["match_group"].unique()))
    match_group_values = data["match_group"].to_numpy()
    _MEDIATION_WORKER_STATE["data"] = data
    _MEDIATION_WORKER_STATE["groups"] = groups
    _MEDIATION_WORKER_STATE["group_indices"] = {
        group: np.flatnonzero(match_group_values == group) for group in groups
    }
    _MEDIATION_WORKER_STATE["config"] = PipelineConfig(**config_dict)

def _mediation_bootstrap_replicate(
    replicate: int,
    sampled: np.ndarray,
    n_simulations: int,
    seed: int,
    state: dict | None = None,
) -> dict:


    state = state if state is not None else _MEDIATION_WORKER_STATE
    data = state["data"]
    group_indices = state["group_indices"]
    n_groups = len(state["groups"])
    config = state["config"]
    pieces = []
    for new_group, old_group in enumerate(sampled, start=1):
        piece = data.iloc[group_indices[old_group]].copy()
        piece["match_group"] = np.int64(replicate * (n_groups + 1) + new_group)
        pieces.append(piece)
    boot = pd.concat(pieces, ignore_index=True)
    try:
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            estimate = _fit_longitudinal_mediation_once(
                boot, config, n_simulations=n_simulations, seed=seed,
            )
        return {
            "replicate": replicate,
            "risk_q00": estimate["risk_q00"],
            "risk_q10": estimate["risk_q10"],
            "risk_q11": estimate["risk_q11"],
            "interventional_total_effect_risk_difference": estimate[
                "interventional_total_effect_risk_difference"
            ],
            "interventional_direct_effect_risk_difference": estimate[
                "interventional_direct_effect_risk_difference"
            ],
            "interventional_indirect_effect_risk_difference": estimate[
                "interventional_indirect_effect_risk_difference"
            ],
            "proportion_mediated": estimate["proportion_mediated"],
        }
    except Exception as exc:
        return {
            "replicate": replicate,
            "error": f"{type(exc).__name__}: {exc}",
        }

def _mediation_bootstrap_worker_count(config: PipelineConfig, panel_bytes: int) -> int:
    if config.mediation_bootstrap_workers > 0:
        return int(config.mediation_bootstrap_workers)
    cores = os.cpu_count() or 1
    workers = max(1, min(cores - 1, 8))
    if panel_bytes > (1 << 30):


        workers = min(workers, 2)
    return workers

def _mediation_checkpoint_fingerprint(config: PipelineConfig, panel_path: Path, n_bootstrap: int) -> dict:
    settings = config.to_dict()
    keys = sorted(key for key in settings if key.startswith("gcomp_")) + [
        "seed", "minimum_category_frequency", "source_has_entgelt", "lag_depth", "control_pool",
    ]
    return {
        "panel": _file_identity(panel_path),
        "n_bootstrap": int(n_bootstrap),
        "settings": {key: settings.get(key) for key in keys},
    }

def _load_mediation_checkpoint(path: Path, fingerprint: dict) -> dict[int, dict]:
    if not path.exists():
        return {}
    rows: dict[int, dict] = {}
    try:
        with path.open("r", encoding="utf-8") as stream:
            header = json.loads(stream.readline() or "null")
            if header != {"fingerprint": fingerprint}:
                return {}
            for line in stream:
                line = line.strip()
                if not line:
                    continue
                row = json.loads(line)
                rows[int(row["replicate"])] = row
    except (OSError, ValueError, KeyError):
        return {}
    return rows

def fit_longitudinal_mediation(
    config: PipelineConfig,
    panel_path: str | Path,
    n_bootstrap: int = 200,
) -> dict:
    import time
    from concurrent.futures import ProcessPoolExecutor, as_completed
    import multiprocessing
    panel_path = Path(panel_path)
    spec = f"{config.control_pool}_lag{config.lag_depth}"
    data = pl.read_parquet(panel_path).to_pandas()
    panel_bytes = int(data.memory_usage(deep=True).sum())
    fingerprint = _mediation_checkpoint_fingerprint(config, panel_path, n_bootstrap)
    checkpoint_path = config.analysis_dir / f"longitudinal_mediation_bootstrap_checkpoint_{spec}.jsonl"
    point_checkpoint_path = config.analysis_dir / f"longitudinal_mediation_point_checkpoint_{spec}.json"


    rng = np.random.default_rng(config.seed + 71_000)
    groups = np.array(sorted(data["match_group"].unique()))
    draws = [rng.choice(groups, size=len(groups), replace=True) for _ in range(n_bootstrap)]
    completed = _load_mediation_checkpoint(checkpoint_path, fingerprint)
    point = None
    if completed and point_checkpoint_path.exists():
        try:
            stored = json.loads(point_checkpoint_path.read_text(encoding="utf-8"))
            if stored.get("fingerprint") == fingerprint:
                point = stored["point"]
        except (OSError, ValueError, KeyError):
            point = None
    if completed:
        log.info(
            "Longitudinal mediation bootstrap: resuming with %d/%d replicates already checkpointed in %s",
            len(completed), n_bootstrap, checkpoint_path,
        )
    else:
        checkpoint_path.unlink(missing_ok=True)
        point_checkpoint_path.unlink(missing_ok=True)
    if point is None:
        started = time.perf_counter()
        point = _fit_longitudinal_mediation_once(
            data,
            config,
            n_simulations=config.gcomp_simulation_repetitions,
            seed=config.seed + 70_000,
        )
        log.info(
            "Longitudinal mediation point estimate (%d simulation repetitions) took %.1f min",
            config.gcomp_simulation_repetitions, (time.perf_counter() - started) / 60.0,
        )
        point_checkpoint_path.write_text(
            json.dumps({"fingerprint": fingerprint, "point": point}, indent=2), encoding="utf-8",
        )
    pending = [r for r in range(n_bootstrap) if r not in completed]
    n_workers = _mediation_bootstrap_worker_count(config, panel_bytes) if pending else 1
    n_workers = max(1, min(n_workers, len(pending))) if pending else 1
    with checkpoint_path.open("a" if completed else "w", encoding="utf-8") as checkpoint:
        if not completed:
            checkpoint.write(json.dumps({"fingerprint": fingerprint}) + "\n")
            checkpoint.flush()
        progress_step = max(1, n_bootstrap // 10)
        n_done = len(completed)
        def note(row: dict) -> None:
            nonlocal n_done
            completed[int(row["replicate"])] = row
            checkpoint.write(json.dumps(row, default=_json_default) + "\n")
            checkpoint.flush()
            n_done += 1
            if n_done % progress_step == 0 or n_done == n_bootstrap:
                n_success = sum("error" not in r for r in completed.values())
                log.info(
                    "Longitudinal mediation bootstrap: %s/%s replications completed (%s successful)",
                    n_done, n_bootstrap, n_success,
                )
        if pending and n_workers == 1:
            state = {
                "data": data,
                "groups": groups,
                "group_indices": {
                    group: np.flatnonzero(data["match_group"].to_numpy() == group) for group in groups
                },
                "config": config,
            }
            for replicate in pending:
                note(_mediation_bootstrap_replicate(
                    replicate, draws[replicate],
                    config.gcomp_bootstrap_simulation_repetitions,
                    config.seed + 100_000 + replicate,
                    state=state,
                ))
        elif pending:
            log.info(
                "Longitudinal mediation bootstrap: %d replicates across %d worker processes "
                "(mediation panel %.2f GB in memory per worker; set mediation_bootstrap_workers to override)",
                len(pending), n_workers, panel_bytes / (1 << 30),
            )


            thread_vars = ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "POLARS_MAX_THREADS")
            saved = {name: os.environ.get(name) for name in thread_vars}
            for name in thread_vars:
                os.environ[name] = "1"
            try:
                context = multiprocessing.get_context("spawn")
                with ProcessPoolExecutor(
                    max_workers=n_workers,
                    mp_context=context,
                    initializer=_mediation_worker_init,
                    initargs=(str(panel_path), config.to_dict()),
                ) as executor:
                    futures = {
                        executor.submit(
                            _mediation_bootstrap_replicate,
                            replicate, draws[replicate],
                            config.gcomp_bootstrap_simulation_repetitions,
                            config.seed + 100_000 + replicate,
                        ): replicate
                        for replicate in pending
                    }
                    for future in as_completed(futures):
                        note(future.result())
            finally:
                for name, value in saved.items():
                    if value is None:
                        os.environ.pop(name, None)
                    else:
                        os.environ[name] = value
    bootstrap_rows = [completed[r] for r in sorted(completed)]
    successful = pd.DataFrame([row for row in bootstrap_rows if "error" not in row])
    minimum = max(20, n_bootstrap // 2)
    if len(successful) < minimum:
        raise RuntimeError(
            f"Only {len(successful)}/{n_bootstrap} longitudinal mediation bootstrap fits succeeded."
        )
    intervals: dict[str, dict[str, float]] = {}
    for key in (
        "interventional_total_effect_risk_difference",
        "interventional_direct_effect_risk_difference",
        "interventional_indirect_effect_risk_difference",
        "proportion_mediated",
    ):
        values = pd.to_numeric(successful[key], errors="coerce").dropna()
        if len(values) < minimum:
            continue
        intervals[key] = {
            "ci_low": float(values.quantile(0.025)),
            "ci_high": float(values.quantile(0.975)),
        }
    point_for_json = dict(point)
    simulation_diagnostics = point_for_json.pop("simulation_diagnostics")
    result = {
        "horizon_years": int(config.gcomp_horizon_years),
        "target_population": point_for_json["target_population"],
        "estimand": (
            "ATT-standardized five-year interventional total, direct and indirect risk "
            "differences for divorce, with the indirect effect operating through the "
            "incidence and timing of first MSK rehabilitation."
        ),
        "identification_warning": (
            "The mediation decomposition requires sequential exchangeability: conditional "
            "on baseline matching variables and observed prior post-divorce history, there "
            "must be no remaining unmeasured mediator-outcome or prior-survival-mediator "
            "confounding. Defining the longitudinal mediator distribution for a survival "
            "outcome also uses the survival-mediational-g-formula intervention that sets "
            "prior survival to one in the source mediator simulation. Observation IPCW "
            "additionally assumes record-gap censoring is independent conditional on "
            "measured prior history. Positivity, consistency and correct specification of "
            "the longitudinal parametric models are also required."
        ),
        "point_estimates": point_for_json,
        "bootstrap_intervals": intervals,
        "successful_bootstrap_replicates": int(len(successful)),
        "requested_bootstrap_replicates": int(n_bootstrap),
        "bootstrap_worker_processes": int(n_workers),
        "point_estimate_simulation_diagnostics": simulation_diagnostics,
    }
    output = config.analysis_dir / f"longitudinal_mediation_results_{spec}.json"
    output.write_text(json.dumps(result, indent=2), encoding="utf-8")
    pd.DataFrame(bootstrap_rows).to_csv(
        config.analysis_dir / f"longitudinal_mediation_bootstrap_{spec}.csv",
        index=False,
    )
    return result

from pathlib import Path
import json
import logging

log = logging.getLogger(__name__)

def run_main_pipeline(
    config: PipelineConfig,
    force: bool = False,
    reporting: PaperReportingConfig | None = None,
) -> dict:
    config.validate()
    _require_pandas_arrow_roundtrip()
    reporting = reporting or PaperReportingConfig(**PAPER_REPORTING_CONFIG)
    reporting.validate()
    initialize_run(config, force=force)
    config.write(config.run_dir / "resolved_config.json")
    reporting.write(config.run_dir / "resolved_paper_reporting_config.json")
    panel = build_analysis_panel(config, force=force)
    panel = relabel_panel_rehab_codes(config, panel)
    coverage = build_panel_coverage_diagnostics(config, panel, force=force)
    risksets = build_risk_sets(config, panel, force=force)
    matching = fit_and_match(config, risksets["treated"], risksets["controls"], force=force)
    rehab_definition_audit = audit_matched_sample_rehab_definition(
        config, panel, matching["matches"], force=force
    )
    balance = build_balance_tables(
        config, risksets["treated"], risksets["controls"], matching["matches"], force=force
    )
    marital = build_marital_status_tables(
        config,
        panel,
        risksets["treated"],
        risksets["controls"],
        matching["matches"],
        force=force,
    )
    paper_summaries = build_paper_summary_tables(
        config,
        reporting,
        panel,
        risksets["treated"],
        risksets["controls"],
        matching["matches"],
        matching["scores"],
        risksets["audit"],
        balance["summary"],
        force=force,
    )
    event_panel = build_pair_event_study_panel(
        config, panel, matching["matches"], pre_years=3,
        post_years=config.followup_years, force=force,
    )
    pretrends = {
        "non_success_applications": fit_pair_event_study(
            config, event_panel, "non_success_app_this_year"
        ),
        "pension_income_amount": fit_pair_event_study(config, event_panel, "rtzb_value"),
        "pension_income_missingness": fit_pair_event_study(config, event_panel, "rtzb_missing"),
        "prior_rehabilitation_activity": fit_pair_event_study(
            config, event_panel, "rehab_starts_this_year"
        ),
    }
    if config.source_has_entgelt:
        pretrends = {
            "non_success_applications": pretrends["non_success_applications"],
            "earnings_amount": fit_pair_event_study(config, event_panel, "entgelt_value"),
            **{key: value for key, value in pretrends.items() if key != "non_success_applications"},
        }
    msk_followup = build_msk_followup(
        config, panel, matching["matches"], risksets["treated"], risksets["controls"],
        force=force,
    )
    mortality_followup = build_mortality_followup(
        config, panel, matching["matches"], risksets["treated"], risksets["controls"],
        force=force,
    )
    msk_dropout_sensitivity: dict[str, object] = {}
    if config.run_msk_dropout_sensitivity:
        sensitivity_data = build_msk_pair_censored_sensitivity(
            config, msk_followup, force=force
        )
        msk_dropout_sensitivity = {
            "followup": str(sensitivity_data["followup"]),
            "audit": str(sensitivity_data["audit"]),
            "models": {
                "unadjusted": fit_discrete_time_model(
                    config,
                    sensitivity_data["followup"],
                    "msk_event",
                    f"msk_pair_censored_{config.control_pool}_lag{config.lag_depth}",
                    adjusted=False,
                ),
                "adjusted": fit_discrete_time_model(
                    config,
                    sensitivity_data["followup"],
                    "msk_event",
                    f"msk_pair_censored_{config.control_pool}_lag{config.lag_depth}",
                    adjusted=True,
                    balance_summary_path=balance["summary"],
                ),
            },
        }
    models = {
        "msk_unadjusted": fit_discrete_time_model(
            config, msk_followup, "msk_event",
            f"msk_{config.control_pool}_lag{config.lag_depth}", adjusted=False,
        ),
        "msk_adjusted": fit_discrete_time_model(
            config, msk_followup, "msk_event",
            f"msk_{config.control_pool}_lag{config.lag_depth}", adjusted=True,
            balance_summary_path=balance["summary"],
        ),
        "mortality_unadjusted": fit_discrete_time_model(
            config, mortality_followup, "death_event",
            f"mortality_{config.control_pool}_lag{config.lag_depth}", adjusted=False,
        ),
        "mortality_adjusted": fit_discrete_time_model(
            config, mortality_followup, "death_event",
            f"mortality_{config.control_pool}_lag{config.lag_depth}", adjusted=True,
            balance_summary_path=balance["summary"],
        ),
    }
    msk_cif = cumulative_incidence_msk(
        msk_followup, config.analysis_dir / "msk_cumulative_incidence_competing_death.csv"
    )
    mortality_curve = cumulative_mortality(
        mortality_followup, config.analysis_dir / "cumulative_mortality.csv"
    )
    msk_curve_ci = build_pooled_curve_table(
        msk_followup, "msk", config.analysis_dir / "msk_curve_ci_pooled.csv",
        config.seed, config.absolute_effect_bootstrap_replicates,
        effect_horizon=config.followup_years,
    )
    mortality_curve_ci = build_pooled_curve_table(
        mortality_followup, "mortality", config.analysis_dir / "mortality_curve_ci_pooled.csv",
        config.seed + 1, config.absolute_effect_bootstrap_replicates,
        effect_horizon=5,
    )
    msk_sex = build_sex_curve_and_heterogeneity(
        msk_followup, "msk",
        config.analysis_dir / "msk_curve_ci_by_sex.csv",
        config.analysis_dir / "msk_sex_heterogeneity.json",
        config.seed + 10, config.absolute_effect_bootstrap_replicates,
        effect_horizon=config.followup_years,
    )
    mortality_sex = build_sex_curve_and_heterogeneity(
        mortality_followup, "mortality",
        config.analysis_dir / "mortality_curve_ci_by_sex.csv",
        config.analysis_dir / "mortality_sex_heterogeneity.json",
        config.seed + 20, config.absolute_effect_bootstrap_replicates,
        effect_horizon=5,
    )
    absolute_effects = summarize_absolute_effects(
        msk_followup, mortality_followup,
        config.analysis_dir / "absolute_effect_magnitudes.json",
        seed=config.seed,
        n_replicates=config.absolute_effect_bootstrap_replicates,
        msk_horizon_year=config.followup_years,
        mortality_horizon_year=5,
    )
    mediation: dict[str, dict] = {}
    if config.run_longitudinal_mediation:
        mediation_data = build_longitudinal_mediation_data(
            config, panel, matching["matches"], risksets["treated"], risksets["controls"],
            force=force,
        )
        longitudinal_result = fit_longitudinal_mediation(
            config, mediation_data["panel"],
            n_bootstrap=config.mediation_bootstrap_replicates,
        )
        longitudinal_result["data_paths"] = {
            key: str(value) for key, value in mediation_data.items()
        }
        mediation["longitudinal_gcomp"] = longitudinal_result
    figures: dict[str, object] = {}
    if config.generate_figures:
        figures["figure_1_balance"] = plot_balance_love(
            balance["detail"], config.figures_dir / "figure_1_balance_after_matching",
            threshold=config.smd_threshold,
        )
        figures["figure_2a_msk_pooled"] = plot_pooled_curve(
            msk_curve_ci, config.figures_dir / "figure_2a_msk_cumulative_incidence_pooled",
            "Figure 2A. First MSK rehabilitation after divorce",
            "Cumulative incidence of first MSK rehabilitation",
        )
        figures["figure_2b_msk_by_sex"] = plot_curve_by_sex(
            msk_sex["curve"], config.figures_dir / "figure_2b_msk_cumulative_incidence_by_sex",
            "Figure 2B. First MSK rehabilitation by sex",
            "Cumulative incidence of first MSK rehabilitation",
        )
        figures["figure_3a_mortality_pooled"] = plot_pooled_curve(
            mortality_curve_ci, config.figures_dir / "figure_3a_cumulative_mortality_pooled",
            "Figure 3A. Mortality after divorce", "Cumulative mortality",
        )
        figures["figure_3b_mortality_by_sex"] = plot_curve_by_sex(
            mortality_sex["curve"], config.figures_dir / "figure_3b_cumulative_mortality_by_sex",
            "Figure 3B. Mortality after divorce by sex", "Cumulative mortality",
        )
        figures["appendix_pretrend_battery"] = plot_pretrend_battery(
            pretrends, config.figures_dir / "appendix_pretrend_battery",
        )
        if mediation:
            figures["figure_5_longitudinal_mediation"] = plot_longitudinal_mediation_decomposition(
                mediation["longitudinal_gcomp"],
                config.figures_dir / "figure_5_longitudinal_mediation_decomposition",
            )
    result = {
        "estimand": (
            "Effect of experiencing a first observed divorce from the earliest observed "
            f"marriage spell between {config.year_start} and {config.year_cap}, with "
            "treatment assignment fixed after t0."
        ),
        "source_profile": {
            "data_profile": config.data_profile,
            "source_has_entgelt": config.source_has_entgelt,
            "first_marriage_source": config.first_marriage_source,
            "playdata_warning": (
                "Code-execution test only: first_marriage_start is used for first-marriage "
                "validation; entgelt is unavailable in playdata, so only earnings-derived "
                "covariates are omitted. All design and estimator settings are unchanged."
                if config.data_profile == "playdata" else None
            ),
        },
        "run_policy": "total_rebuild" if config.total_rebuild else "checkpoint_reuse_allowed",
        "paper_reporting_config": reporting.to_dict(),
        "panel": str(panel),
        "panel_coverage_diagnostics": str(coverage),
        "rehab_code_definition": _rehab_code_definition(config),
        "rehab_code_definition_eligibility_audit": str(rehab_definition_audit),
        "marital_tables": {key: str(value) for key, value in marital.items()},
        "paper_summary_tables": {key: str(value) for key, value in paper_summaries.items()},
        "risksets": {key: str(value) for key, value in risksets.items()},
        "matching": {key: str(value) for key, value in matching.items()},
        "balance": {key: str(value) for key, value in balance.items()},
        "pretrends": pretrends,
        "msk_followup": str(msk_followup),
        "mortality_followup": str(mortality_followup),
        "msk_dropout_sensitivity": msk_dropout_sensitivity,
        "msk_cumulative_incidence": str(msk_cif),
        "cumulative_mortality": str(mortality_curve),
        "msk_curve_ci_pooled": str(msk_curve_ci),
        "mortality_curve_ci_pooled": str(mortality_curve_ci),
        "msk_sex_outputs": {key: str(value) for key, value in msk_sex.items()},
        "mortality_sex_outputs": {key: str(value) for key, value in mortality_sex.items()},
        "absolute_effect_magnitudes": str(absolute_effects),
        "models": models,
        "mediation": mediation,
        "figures": figures,
    }
    (config.run_dir / "run_outputs.json").write_text(
        json.dumps(result, indent=2), encoding="utf-8"
    )
    return result

def _run_secondary_specification_from_panel(
    config: PipelineConfig,
    panel: str | Path,
    *,
    force: bool,
    reporting: PaperReportingConfig | None = None,
) -> dict:
    panel = Path(panel)
    if not panel.exists():
        raise FileNotFoundError(panel)
    reporting = reporting or PaperReportingConfig(**PAPER_REPORTING_CONFIG)
    reporting.validate()


    if config.total_rebuild and not config.reuse_existing_outputs:
        clear_run_directory(config)
        initialize_run(config, force=True)
    else:
        initialize_run(config, force=force)
    config.write(config.run_dir / "resolved_config.json")
    reporting.write(config.run_dir / "resolved_paper_reporting_config.json")
    (config.run_dir / "parent_panel_reference.json").write_text(
        json.dumps(
            {
                "panel": str(panel),
                "panel_size_bytes": panel.stat().st_size,
                "panel_mtime": panel.stat().st_mtime,
                "reason": "Shared canonical analysis panel; only risk-set lag/window changes.",
            },
            indent=2,
        ),
        encoding="utf-8",
    )
    panel = relabel_panel_rehab_codes(config, panel)
    risksets = build_risk_sets(config, panel, force=force)
    matching = fit_and_match(
        config, risksets["treated"], risksets["controls"], force=force
    )
    audit_matched_sample_rehab_definition(config, panel, matching["matches"], force=force)
    balance = build_balance_tables(
        config,
        risksets["treated"],
        risksets["controls"],
        matching["matches"],
        force=force,
    )
    marital = build_marital_status_tables(
        config,
        panel,
        risksets["treated"],
        risksets["controls"],
        matching["matches"],
        force=force,
    )
    paper_summaries = build_paper_summary_tables(
        config,
        reporting,
        panel,
        risksets["treated"],
        risksets["controls"],
        matching["matches"],
        matching["scores"],
        risksets["audit"],
        balance["summary"],
        force=force,
    )
    event_panel = build_pair_event_study_panel(
        config,
        panel,
        matching["matches"],
        pre_years=3,
        post_years=config.followup_years,
        force=force,
    )
    pretrends = {
        "non_success_applications": fit_pair_event_study(
            config, event_panel, "non_success_app_this_year"
        ),
        "pension_income_amount": fit_pair_event_study(
            config, event_panel, "rtzb_value"
        ),
        "pension_income_missingness": fit_pair_event_study(
            config, event_panel, "rtzb_missing"
        ),
        "prior_rehabilitation_activity": fit_pair_event_study(
            config, event_panel, "rehab_starts_this_year"
        ),
    }
    if config.source_has_entgelt:
        pretrends = {
            "non_success_applications": pretrends["non_success_applications"],
            "earnings_amount": fit_pair_event_study(
                config, event_panel, "entgelt_value"
            ),
            **{
                key: value
                for key, value in pretrends.items()
                if key != "non_success_applications"
            },
        }
    msk_followup = build_msk_followup(
        config,
        panel,
        matching["matches"],
        risksets["treated"],
        risksets["controls"],
        force=force,
    )
    mortality_followup = build_mortality_followup(
        config,
        panel,
        matching["matches"],
        risksets["treated"],
        risksets["controls"],
        force=force,
    )
    msk_dropout_sensitivity: dict[str, object] = {}
    if config.run_msk_dropout_sensitivity:
        sensitivity_data = build_msk_pair_censored_sensitivity(
            config, msk_followup, force=force
        )
        msk_dropout_sensitivity = {
            "followup": str(sensitivity_data["followup"]),
            "audit": str(sensitivity_data["audit"]),
            "models": {
                "unadjusted": fit_discrete_time_model(
                    config,
                    sensitivity_data["followup"],
                    "msk_event",
                    f"msk_pair_censored_{config.control_pool}_lag{config.lag_depth}",
                    adjusted=False,
                ),
                "adjusted": fit_discrete_time_model(
                    config,
                    sensitivity_data["followup"],
                    "msk_event",
                    f"msk_pair_censored_{config.control_pool}_lag{config.lag_depth}",
                    adjusted=True,
                    balance_summary_path=balance["summary"],
                ),
            },
        }
    models = {
        "msk_unadjusted": fit_discrete_time_model(
            config,
            msk_followup,
            "msk_event",
            f"msk_{config.control_pool}_lag{config.lag_depth}",
            adjusted=False,
        ),
        "msk_adjusted": fit_discrete_time_model(
            config,
            msk_followup,
            "msk_event",
            f"msk_{config.control_pool}_lag{config.lag_depth}",
            adjusted=True,
            balance_summary_path=balance["summary"],
        ),
        "mortality_unadjusted": fit_discrete_time_model(
            config,
            mortality_followup,
            "death_event",
            f"mortality_{config.control_pool}_lag{config.lag_depth}",
            adjusted=False,
        ),
        "mortality_adjusted": fit_discrete_time_model(
            config,
            mortality_followup,
            "death_event",
            f"mortality_{config.control_pool}_lag{config.lag_depth}",
            adjusted=True,
            balance_summary_path=balance["summary"],
        ),
    }
    msk_cif = cumulative_incidence_msk(
        msk_followup,
        config.analysis_dir / "msk_cumulative_incidence_competing_death.csv",
    )
    mortality_curve = cumulative_mortality(
        mortality_followup,
        config.analysis_dir / "cumulative_mortality.csv",
    )
    msk_curve_ci = build_pooled_curve_table(
        msk_followup,
        "msk",
        config.analysis_dir / "msk_curve_ci_pooled.csv",
        config.seed,
        config.absolute_effect_bootstrap_replicates,
        effect_horizon=config.followup_years,
    )
    mortality_curve_ci = build_pooled_curve_table(
        mortality_followup,
        "mortality",
        config.analysis_dir / "mortality_curve_ci_pooled.csv",
        config.seed + 1,
        config.absolute_effect_bootstrap_replicates,
        effect_horizon=5,
    )
    msk_sex = build_sex_curve_and_heterogeneity(
        msk_followup,
        "msk",
        config.analysis_dir / "msk_curve_ci_by_sex.csv",
        config.analysis_dir / "msk_sex_heterogeneity.json",
        config.seed + 10,
        config.absolute_effect_bootstrap_replicates,
        effect_horizon=config.followup_years,
    )
    mortality_sex = build_sex_curve_and_heterogeneity(
        mortality_followup,
        "mortality",
        config.analysis_dir / "mortality_curve_ci_by_sex.csv",
        config.analysis_dir / "mortality_sex_heterogeneity.json",
        config.seed + 20,
        config.absolute_effect_bootstrap_replicates,
        effect_horizon=5,
    )
    absolute = summarize_absolute_effects(
        msk_followup,
        mortality_followup,
        config.analysis_dir / "absolute_effect_magnitudes.json",
        seed=config.seed + config.lag_depth * 30 + config.year_start,
        n_replicates=config.absolute_effect_bootstrap_replicates,
        msk_horizon_year=config.followup_years,
        mortality_horizon_year=5,
    )
    mediation: dict[str, dict] = {}
    if config.run_longitudinal_mediation:
        mediation_data = build_longitudinal_mediation_data(
            config, panel, matching["matches"], risksets["treated"], risksets["controls"],
            force=force,
        )
        longitudinal_result = fit_longitudinal_mediation(
            config, mediation_data["panel"],
            n_bootstrap=config.mediation_bootstrap_replicates,
        )
        longitudinal_result["data_paths"] = {
            key: str(value) for key, value in mediation_data.items()
        }
        mediation["longitudinal_gcomp"] = longitudinal_result
    figures: dict[str, object] = {}
    if config.generate_figures:
        specification_label = (
            f"lag {config.lag_depth}, {config.year_start}–{config.year_cap}"
        )
        figures["figure_1_balance"] = plot_balance_love(
            balance["detail"],
            config.figures_dir / "figure_1_balance_after_matching",
            threshold=config.smd_threshold,
        )
        figures["figure_2a_msk_pooled"] = plot_pooled_curve(
            msk_curve_ci,
            config.figures_dir / "figure_2a_msk_cumulative_incidence_pooled",
            f"Figure 2A. First MSK rehabilitation after divorce ({specification_label})",
            "Cumulative incidence of first MSK rehabilitation",
        )
        figures["figure_2b_msk_by_sex"] = plot_curve_by_sex(
            msk_sex["curve"],
            config.figures_dir / "figure_2b_msk_cumulative_incidence_by_sex",
            f"Figure 2B. First MSK rehabilitation by sex ({specification_label})",
            "Cumulative incidence of first MSK rehabilitation",
        )
        figures["figure_3a_mortality_pooled"] = plot_pooled_curve(
            mortality_curve_ci,
            config.figures_dir / "figure_3a_cumulative_mortality_pooled",
            f"Figure 3A. Mortality after divorce ({specification_label})",
            "Cumulative mortality",
        )
        figures["figure_3b_mortality_by_sex"] = plot_curve_by_sex(
            mortality_sex["curve"],
            config.figures_dir / "figure_3b_cumulative_mortality_by_sex",
            f"Figure 3B. Mortality after divorce by sex ({specification_label})",
            "Cumulative mortality",
        )
        figures["appendix_pretrend_battery"] = plot_pretrend_battery(
            pretrends,
            config.figures_dir / "appendix_pretrend_battery",
        )
        if mediation:
            figures["figure_5_longitudinal_mediation"] = (
                plot_longitudinal_mediation_decomposition(
                    mediation["longitudinal_gcomp"],
                    config.figures_dir / "figure_5_longitudinal_mediation_decomposition",
                )
            )
    result = {
        "specification": {
            "lag_depth": config.lag_depth,
            "year_start": config.year_start,
            "year_cap": config.year_cap,
            "sample_tag": config.sample_tag,
        },
        "panel_reference": str(panel),
        "marital_tables": {key: str(value) for key, value in marital.items()},
        "paper_reporting_config": reporting.to_dict(),
        "paper_summary_tables": {key: str(value) for key, value in paper_summaries.items()},
        "risksets": {key: str(value) for key, value in risksets.items()},
        "matching": {key: str(value) for key, value in matching.items()},
        "balance": {key: str(value) for key, value in balance.items()},
        "pretrends": pretrends,
        "msk_followup": str(msk_followup),
        "mortality_followup": str(mortality_followup),
        "msk_dropout_sensitivity": msk_dropout_sensitivity,
        "msk_cumulative_incidence": str(msk_cif),
        "cumulative_mortality": str(mortality_curve),
        "msk_curve_ci_pooled": str(msk_curve_ci),
        "mortality_curve_ci_pooled": str(mortality_curve_ci),
        "msk_sex_outputs": {key: str(value) for key, value in msk_sex.items()},
        "mortality_sex_outputs": {key: str(value) for key, value in mortality_sex.items()},
        "absolute_effect_magnitudes": str(absolute),
        "models": models,
        "mediation": mediation,
        "figures": figures,
    }
    (config.run_dir / "run_outputs.json").write_text(
        json.dumps(result, indent=2), encoding="utf-8"
    )
    return result

def run_lag1_vs_lag3_comparison(
    config: PipelineConfig,
    force: bool = False,
    reporting: PaperReportingConfig | None = None,
) -> dict:
    from dataclasses import replace
    reporting = reporting or PaperReportingConfig(**PAPER_REPORTING_CONFIG)
    reporting.validate()
    lag1_full_config = replace(
        config,
        lag_depth=1,
        run_lag1_vs_lag3=False,
    )
    lag1_full = run_main_pipeline(lag1_full_config, force=force, reporting=reporting)
    panel = Path(lag1_full["panel"])
    common_start = config.lag_comparison_common_year_start
    common_suffix = f"{common_start}_{config.year_cap}"
    lag1_common_config = replace(
        config,
        sample_tag=f"{config.sample_tag}__lag1_common_{common_suffix}",
        year_start=common_start,
        lag_depth=1,
        run_lag1_vs_lag3=False,
        run_longitudinal_mediation=True,
        generate_figures=True,
    )
    lag1_common = _run_secondary_specification_from_panel(
        lag1_common_config, panel, force=force, reporting=reporting
    )
    lag3_common_config = replace(
        config,
        sample_tag=f"{config.sample_tag}__lag3_common_{common_suffix}",
        year_start=common_start,
        lag_depth=3,
        run_lag1_vs_lag3=False,
        run_longitudinal_mediation=True,
        generate_figures=True,
    )
    lag3_common = _run_secondary_specification_from_panel(
        lag3_common_config, panel, force=force, reporting=reporting
    )
    specifications = [
        (
            "lag1_full_window",
            f"Lag 1, {config.year_start}–{config.year_cap}",
            config.year_start,
            1,
            lag1_full,
        ),
        (
            "lag1_common_window",
            f"Lag 1, {common_start}–{config.year_cap}",
            common_start,
            1,
            lag1_common,
        ),
        (
            "lag3_common_window",
            f"Lag 3, {common_start}–{config.year_cap}",
            common_start,
            3,
            lag3_common,
        ),
    ]
    rows: list[dict] = []
    for specification, label, year_start, lag_depth, spec in specifications:
        match_path = spec["matching"]["matches"]
        audit_path = spec["risksets"]["audit"]
        match_count = int(
            pl.scan_parquet(match_path)
            .select(pl.len())
            .pipe(_safe_collect)
            .item()
        )
        filter_audit = pl.read_csv(audit_path)
        treated_final = (
            filter_audit.filter(pl.col("group") == "treated")
            .tail(1)
            .row(0, named=True)
        )
        absolute = json.loads(
            Path(spec["absolute_effect_magnitudes"]).read_text(encoding="utf-8")
        )
        for outcome_name, absolute_key in (
            ("msk", "first_msk_rehabilitation_with_death_as_competing_event"),
            ("mortality", "mortality"),
        ):
            model = spec["models"][f"{outcome_name}_adjusted"]
            effect = absolute[absolute_key]
            rows.append(
                {
                    "specification": specification,
                    "specification_label": label,
                    "year_start": year_start,
                    "year_cap": config.year_cap,
                    "lag_depth": lag_depth,
                    "outcome": outcome_name,
                    "eligible_treated_after_filters": int(treated_final["n_persons"]),
                    "matched_pairs": match_count,
                    "risk_difference_per_1000": effect["risk_difference_per_1000"],
                    "risk_difference_per_1000_ci_low": effect[
                        "risk_difference_per_1000_ci"
                    ][0],
                    "risk_difference_per_1000_ci_high": effect[
                        "risk_difference_per_1000_ci"
                    ][1],
                    "odds_ratio": model["odds_ratio"],
                    "or_ci_low": model["ci_low"],
                    "or_ci_high": model["ci_high"],
                    "p_value": model["p_value"],
                    "selected_covariates": json.dumps(
                        [item["variable"] for item in model["selected_covariates"]]
                    ),
                }
            )
    comparison_csv = config.analysis_dir / "lag_depth_and_common_window_comparison.csv"
    pl.DataFrame(rows).write_csv(comparison_csv)
    figure = None
    if config.generate_figures:
        figure = plot_lag_comparison(
            comparison_csv,
            config.figures_dir / "figure_4_lag_depth_common_window_comparison",
        )
    result = {
        "lag1_full_window": lag1_full,
        "lag1_common_window": lag1_common,
        "lag3_common_window": lag3_common,
        "head_to_head_table": str(comparison_csv),
        "figure_4": figure,
        "interpretation_note": (
            "Compare lag1_common_window with lag3_common_window to assess sensitivity "
            "to deeper pre-treatment history while holding the 2014–2018 cohort window "
            "fixed. Compare lag1_full_window with lag1_common_window to assess the role "
            "of excluding the 2012–2013 cohorts."
        ),
    }
    (config.run_dir / "run_outputs_lag_comparison.json").write_text(
        json.dumps(result, indent=2), encoding="utf-8"
    )
    return result

def run_longitudinal_mediation_only(
    config: PipelineConfig,
    n_bootstrap: int = 100,
    force: bool = False,
) -> dict:
    config.validate()
    config.ensure_dirs()
    panel = config.panels_dir / "analysis_panel.parquet"
    treated = config.analysis_dir / f"riskset_treated_lag{config.lag_depth}.parquet"
    controls = config.analysis_dir / f"riskset_controls_{config.control_pool}_lag{config.lag_depth}.parquet"
    matches = config.analysis_dir / f"matched_pairs_{config.control_pool}_lag{config.lag_depth}.parquet"
    for path in (panel, treated, controls, matches):
        if not path.exists():
            raise FileNotFoundError(f"Run the main pipeline first; missing {path}")
    panel = relabel_panel_rehab_codes(config, panel)
    data = build_longitudinal_mediation_data(
        config, panel, matches, treated, controls, force=force
    )
    result = fit_longitudinal_mediation(
        config, data["panel"], n_bootstrap=n_bootstrap
    )
    result["data_paths"] = {key: str(value) for key, value in data.items()}
    return result

import argparse
import tempfile
from datetime import date

def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Standalone divorce–rehabilitation matched-cohort pipeline"
    )
    parser.add_argument(
        "--config",
        default=None,
        help=(
            "Optional YAML configuration. A nested paper_reporting block is supported; "
            "when omitted, USER_CONFIG and PAPER_REPORTING_CONFIG are used."
        ),
    )
    parser.add_argument(
        "--mode",
        choices=["main", "longitudinal-mediation"],
        default=DEFAULT_RUN_MODE,
    )
    parser.add_argument(
        "--reuse-existing",
        action="store_true",
        default=DEFAULT_REUSE_EXISTING,
        help=(
            "Opt out of the default total rebuild and allow signature-protected checkpoint "
            "reuse. Use this only deliberately; stale outputs are otherwise deleted."
        ),
    )
    parser.add_argument(
        "--force",
        action="store_true",
        default=DEFAULT_FORCE_REBUILD,
        help="Rebuild stage outputs when --reuse-existing is used.",
    )
    parser.add_argument("--bootstrap", type=int, default=DEFAULT_BOOTSTRAP_REPLICATIONS)
    parser.add_argument(
        "--self-test",
        action="store_true",
        help="Run the built-in synthetic end-to-end test instead of using real data.",
    )
    parser.add_argument(
        "--schema-check",
        action="store_true",
        help="Inspect the source schema and report required/optional variables without running the pipeline.",
    )
    parser.add_argument(
        "--check-signature",
        action="store_true",
        help=(
            "Compare the current settings with the run directory's stored signature and report "
            "which stage a --reuse-existing run would rebuild from, without touching any file."
        ),
    )
    parser.add_argument(
        "--environment-check",
        action="store_true",
        help=(
            "Report installed Python, Polars, scikit-learn, NumPy, pandas, and SciPy "
            "versions plus detected Polars streaming capabilities without reading data."
        ),
    )
    return parser

def _configure_logging(config: PipelineConfig) -> None:
    config.ensure_dirs()
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        handlers=[
            logging.FileHandler(config.logs_dir / "pipeline.log", encoding="utf-8"),
            logging.StreamHandler(),
        ],
        force=True,
    )

def _synthetic_rows() -> list[dict]:
    rows: list[dict] = []
    years = range(2011, 2022)
    for person in range(1, 241):
        treated = person % 6 == 0
        treated_rank = person // 6
        t0 = 2014 + ((treated_rank - 1) % 5) if treated else (2020 if 201 <= person <= 210 else None)
        birth = 1950 + (person % 12)
        sex = 1 + ((person // 6) % 2)
        first_marriage = date(1990 + person % 8, 6, 1)
        remarriage = treated and person % 60 == 0
        remarriage_year = t0 + 2 if remarriage else None
        prior_msk = treated and person in {6, 12}
        same_year_msk = treated and person in {18, 24}
        follow_msk_year = None
        if treated and treated_rank % 4 in (0, 1):
            follow_msk_year = t0 + (1 if treated_rank % 4 == 0 else 2)
        if not treated and person % 7 == 0:
            follow_msk_year = 2017
        death_year = None
        if treated and person % 66 == 0:
            death_year = min(t0 + 4, 2021)
        elif not treated and person % 29 == 0:
            death_year = 2019
        for year in years:
            current_marriage_start = first_marriage
            marriage_end = None
            court_decision = None
            if t0 is not None:
                if year <= t0:
                    marriage_end = date(t0, 7, 1)
                    court_decision = date(t0, 7, 1)
                elif remarriage and year >= remarriage_year:
                    current_marriage_start = date(remarriage_year, 5, 1)
                else:
                    marriage_end = date(t0, 7, 1)
                    court_decision = date(t0, 7, 1)
            pension_only = person > 180
            both = 161 <= person <= 180
            neither = person in {239, 240}
            entgelt = None if pension_only or neither else float(25_000 + person * 150 + (year - 2011) * 300)
            rtzb = None if (not pension_only and not both) or neither else float(12_000 + person * 80)
            msk_start = None
            msk_code = None
            msk_duration = None
            incapacity = None
            if prior_msk and year == t0 - 1:
                msk_start, msk_code, msk_duration, incapacity = date(year, 3, 1), 20, 28.0, "3-6"
            elif same_year_msk and year == t0:
                msk_start, msk_code, msk_duration, incapacity = date(year, 4, 1), 20, 35.0, "6-12"
            elif follow_msk_year == year:
                late_code = 56 if person % 24 == 0 else 53
                msk_start, msk_code, msk_duration, incapacity = (
                    date(year, 4, 1), late_code if year >= 2020 else 20, 30.0 + person % 10, "3-6"
                )
            elif person % 17 == 0 and year == 2012:
                msk_start, msk_code, msk_duration, incapacity = date(year, 5, 1), 30, 21.0, "1-3"
            elif person % 13 == 0 and year == 2012:
                msk_start, msk_code, msk_duration, incapacity = date(year, 5, 1), 10, 21.0, "1-3"
            fail_date = date(2012, 2, 1) if person == 5 else (
                date(year, 2, 1) if (person + year) % 17 == 0 else None
            )
            rows.append({
                "simple_id": person,
                "ja": year,
                "gbja": birth,
                "rtwf_jjjj": death_year,
                "ge": sex,
                "divorcing": int(t0 == year),
                "fmsd": 3 if (t0 is not None and year >= t0) else 2,
                "marriage_start": current_marriage_start,
                "marriage_end": marriage_end,
                "first_marriage_start": first_marriage,
                "first_marriage_end": date(t0, 7, 1) if t0 is not None else None,
                "court_decision": court_decision,
                "entgelt": entgelt,
                "rtzb": rtzb,
                "byvlgs": float(max(year - 1990, 0)) if entgelt is not None else None,
                "bygmgs": float(person % 4) if entgelt is not None else None,
                "rtbt": None,
                "whot_bland": 1 + person % 16,
                "whot_skt": 1 + person % 4,
                "ttsc1_kldb1988": 1000 + (person % 8) * 100,
                "ttsc2_kldb1988": None,
                "seg_start_rsd_1": msk_start,
                "seg_end_rsd_1": date(year, 4, 30) if msk_start else None,
                "rehab_start_1": msk_start,
                "rehab_end_1": date(year, 4, 30) if msk_start else None,
                "mcdggr_succeed_1": msk_code,
                "mcdams_succeed_1": msk_duration,
                "mcaiufzt_succeed_1": incapacity,
                "seg_start_rsd_2": None,
                "seg_end_rsd_2": None,
                "rehab_start_2": None,
                "rehab_end_2": None,
                "mcdggr_succeed_2": None,
                "mcdams_succeed_2": None,
                "mcaiufzt_succeed_2": None,
                "application_date_fail": fail_date,
                "decision_date_fail": fail_date,
                "application_date_withdrawn": None,
                "decision_date_withdrawn": None,
                "application_date_forward": None,
                "decision_date_forward": None,
            })
    return rows

def run_internal_self_test() -> dict:
    with tempfile.TemporaryDirectory(prefix="divorce_pipeline_test_") as temp:
        temp_path = Path(temp)
        raw = temp_path / "raw"
        raw.mkdir()
        data = pl.DataFrame(_synthetic_rows(), infer_schema_length=None)
        data = data.drop("entgelt")
        midpoint = data.height // 2
        data[:midpoint].write_parquet(raw / "part1.parquet")
        data[midpoint:].write_parquet(raw / "part2.parquet")
        config = PipelineConfig(
            raw_glob=str(raw / "*.parquet"),
            output_dir=str(temp_path / "runs"),
            sample_tag="synthetic_playdata",
            data_profile="playdata",
            source_has_entgelt=False,
            first_marriage_source="date_fields",
            year_cap=2018,
            followup_years=3,
            mortality_horizon=6,
            caliper=1.0,
            minimum_category_frequency=1,
            strict_main_run=True,
            max_propensity_fit_rows=100,
            propensity_score_batch_size=50,
            outcome_bootstrap_replicates=30,
            absolute_effect_bootstrap_replicates=30,
            mediation_bootstrap_replicates=20,
            gcomp_horizon_years=3,
            gcomp_simulation_repetitions=2,
            gcomp_bootstrap_simulation_repetitions=1,
            death_registry_end_year=2023,
            generate_figures=True,
            run_longitudinal_mediation=True,
            optimal_match_dense_max_entries=2_000_000,
            optimal_match_sparse_max_edges=2_000_000,
            run_lag1_vs_lag3=False,
        )
        reporting = PaperReportingConfig(
            minimum_cell_people=2,
            pool_small_diagnosis_codes=True,
            protect_matchability_cells=True,
            withhold_small_overlap_counts=True,
        )
        _configure_logging(config)
        results = run_main_pipeline(config, force=True, reporting=reporting)
        panel = pl.read_parquet(results["panel"])
        required = {
            "income_source_status", "fmsd", "first_marriage_start",
            "byvlgs_missing", "bygmgs_missing",
            "qualifying_first_divorce_this_year",
            "ever_mental_health_rehab_to_date",
            "msk_duration_days_this_year", "msk_incapacity_months_cat_this_year",
            "rehab_start_slot1", "rehab_start_slot2",
            "rehab_diagnosis_code_slot1_this_year",
            "rehab_diagnosis_code_slot2_this_year",
            "non_msk_rehab_this_year",
        }
        missing = required - set(panel.columns)
        assert not missing, f"Missing generated columns: {sorted(missing)}"
        assert panel.get_column("income_source_status").unique().to_list() == ["not_constructible_without_entgelt"]
        assert panel.get_column("first_marriage_definition_source").unique().to_list() == ["date_fields"]
        assert panel.filter((pl.col("simple_id") == 6) & (pl.col("ja") == 2013)).get_column("marriage_duration_years").item() == 17
        assert panel.filter(pl.col("simple_id") == 5).get_column("failed_app_this_year").sum() == 1
        matches = pl.read_parquet(results["matching"]["matches"])
        assert matches.height > 0
        assert matches.get_column("t_id").n_unique() == matches.height
        assert matches.get_column("c_id").n_unique() == matches.height
        assert matches.get_column("abs_ps_diff").max() <= config.caliper
        balance = pl.read_csv(results["balance"]["detail"])
        state_balance = balance.filter(
            (pl.col("variable") == "lag1_whot_bland_cat")
            & (pl.col("variable_type") == "categorical_level")
        )
        assert state_balance.height > 0 and state_balance.get_column("level").n_unique() > 1
        marital = pl.read_csv(results["marital_tables"]["composition"])
        assert {"eligible_treated", "eligible_controls", "matched_controls"}.issubset(
            set(marital.get_column("analysis_group").unique())
        )
        paper_summaries = results["paper_summary_tables"]
        assert all(Path(path).exists() for path in paper_summaries.values())
        sample_overview = pd.read_csv(paper_summaries["sample_overview"])
        assert {"person_year_rows", "unique_people", "completed_medical_rehabilitation_events"}.issubset(
            set(sample_overview["metric"])
        )
        matching_overall = pd.read_csv(paper_summaries["matching_overall"])
        assert {"matched_pairs", "overall_match_rate", "max_abs_ps_diff"}.issubset(
            set(matching_overall["metric"])
        )
        matched_vs_unmatched = pd.read_csv(paper_summaries["matched_vs_unmatched_treated"])
        assert {
            "variable", "level", "variable_type", "matched_value", "unmatched_value",
            "smd", "matched_count", "unmatched_count", "n_matched_treated",
            "n_unmatched_treated", "n_levels_pooled", "disclosure_note",
        }.issubset(set(matched_vs_unmatched.columns))
        summary_manifest = json.loads(
            Path(paper_summaries["manifest"]).read_text(encoding="utf-8")
        )
        matchability_internal = pd.read_csv(
            summary_manifest["related_sources_outside_this_folder"]
            ["matched_vs_unmatched_treated_internal_not_for_export"]
        )
        assert matchability_internal["matched_value"].notna().any()
        assert "t0" in set(matchability_internal["variable"])
        assert (matchability_internal["variable_type"] == "categorical_level").any()
        repeated_overlap = pd.read_csv(paper_summaries["repeated_person_overlap"])
        assert {
            "unique_people_across_both_roles",
            "people_appearing_as_control_and_treated",
            "people_with_multiple_control_assignments",
        }.issubset(set(repeated_overlap["metric"]))
        overlap_detail = pl.read_csv(
            summary_manifest["related_sources_outside_this_folder"]
            ["repeated_person_overlap_detail_internal_not_for_export"]
        )
        assert {
            "n_matched_assignments", "n_treated_assignments",
            "n_control_assignments", "appears_in_both_roles",
        }.issubset(set(overlap_detail.columns))
        fabricated = pl.DataFrame({
            "simple_id": list(range(1, 15)),
            "ja": [2015] * 14,
            "rehabilitation_diagnosis_code": ["A"] * 6 + ["B"] * 4 + ["C"] * 2 + ["D"] * 2,
        }).lazy()
        pooled = _pool_small_code_cells(fabricated, 3, key_columns=[], include_year_span=False)
        pooled_row = pooled.filter(
            pl.col("rehabilitation_diagnosis_code") == PAPER_POOLED_CODE_LABEL
        )
        assert pooled_row.height == 1
        assert pooled_row.get_column("unique_people").item() == 4
        assert pooled_row.get_column("n_codes_pooled").item() == 2
        assert set(pooled.get_column("rehabilitation_diagnosis_code").to_list()) == {
            "A", "B", PAPER_POOLED_CODE_LABEL
        }
        lone_small = pl.DataFrame({
            "simple_id": list(range(1, 12)),
            "ja": [2015] * 11,
            "rehabilitation_diagnosis_code": ["A"] * 6 + ["B"] * 4 + ["C"],
        }).lazy()
        pooled_lone = _pool_small_code_cells(lone_small, 3, key_columns=[], include_year_span=False)
        assert set(pooled_lone.get_column("rehabilitation_diagnosis_code").to_list()) == {
            "A", PAPER_POOLED_CODE_LABEL
        }
        lone_row = pooled_lone.filter(
            pl.col("rehabilitation_diagnosis_code") == PAPER_POOLED_CODE_LABEL
        )
        assert lone_row.get_column("unique_people").item() == 5
        assert lone_row.get_column("n_codes_pooled").item() == 2
        tiny = pl.DataFrame({
            "simple_id": list(range(1, 9)),
            "ja": [2015] * 8,
            "rehabilitation_diagnosis_code": ["A"] * 6 + ["C", "D"],
        }).lazy()
        pooled_tiny = _pool_small_code_cells(tiny, 4, key_columns=[], include_year_span=False)
        withheld_row = pooled_tiny.filter(
            pl.col("rehabilitation_diagnosis_code") == PAPER_POOLED_CODE_LABEL
        )
        assert withheld_row.get_column("unique_people").item() is None
        assert withheld_row.get_column("disclosure_note").item() is not None
        unpooled = _pool_small_code_cells(tiny, 0, key_columns=[], include_year_span=False)
        assert PAPER_POOLED_CODE_LABEL not in set(
            unpooled.get_column("rehabilitation_diagnosis_code").to_list()
        )
        assert unpooled.height == 3
        assert np.isfinite(results["models"]["msk_unadjusted"]["odds_ratio"])
        assert np.isfinite(results["models"]["mortality_unadjusted"]["odds_ratio"])
        assert "longitudinal_gcomp" in results["mediation"]
        assert np.isfinite(
            results["mediation"]["longitudinal_gcomp"]["point_estimates"]
            ["interventional_total_effect_risk_difference"]
        )
        msk_followup_test = pl.read_parquet(results["msk_followup"])
        post_event_rows = (
            msk_followup_test.sort(["simple_id", "t0", "follow_year"])
            .with_columns(
                (pl.col("event_type") > 0).cum_sum().over(["simple_id", "t0"]).alias("events_seen")
            )
            .filter(
                (pl.col("events_seen") > 1)
                | ((pl.col("events_seen") == 1) & (pl.col("event_type") == 0))
            )
        )
        assert post_event_rows.height == 0
        legacy_config = PipelineConfig(**{
            **config.to_dict(), "sample_tag": "synthetic_playdata_legacy_codes",
            "msk_diagnosis_codes": [20], "mental_health_diagnosis_codes": [30],
        })
        legacy_config.validate()
        legacy_config.ensure_dirs()
        initialize_run(legacy_config, force=True)
        legacy_panel_path = build_analysis_panel(legacy_config, force=True)
        legacy_panel = pl.read_parquet(legacy_panel_path)
        assert legacy_panel.get_column("msk_starts_this_year").sum() < panel.get_column("msk_starts_this_year").sum()
        marker_before = _read_rehab_code_marker(legacy_panel_path)
        assert marker_before is not None and _normalize_diagnosis_codes(marker_before["applied"]["msk_diagnosis_codes"]) == [20]
        relabel_config = PipelineConfig(**{**legacy_config.to_dict(), "msk_diagnosis_codes": [20, 53, 56]})
        relabelled_path = relabel_panel_rehab_codes(relabel_config, legacy_panel_path, batch_rows=37)
        relabelled = pl.read_parquet(relabelled_path).sort(["simple_id", "ja"])
        reference = panel.sort(["simple_id", "ja"])
        assert relabelled.height == reference.height
        for column in (
            "msk_starts_this_year", "mental_health_rehab_starts_this_year", "non_msk_rehab_this_year",
            "cum_msk_rehabs_by_year", "cum_mental_health_rehabs_by_year",
            "ever_msk_rehab_to_date", "ever_mental_health_rehab_to_date",
        ):
            assert relabelled.get_column(column).to_list() == reference.get_column(column).to_list(), column
            assert relabelled.schema[column] == reference.schema[column], column
        assert set(relabelled.columns) == set(reference.columns)
        marker_after = _read_rehab_code_marker(relabelled_path)
        assert marker_after["source"] == "in_place_relabel"
        assert _normalize_diagnosis_codes(marker_after["applied"]["msk_diagnosis_codes"]) == [20, 53, 56]
        assert marker_after["relabel_totals"]["msk_starts_new_definition"] > marker_after["relabel_totals"]["msk_starts_previous_definition"]
        assert Path(marker_after["relabel_totals"]["audit_by_year"]).exists()
        assert relabel_panel_rehab_codes(relabel_config, relabelled_path, batch_rows=37) == relabelled_path
        old_payload = {"config": {k: v for k, v in config.to_dict().items() if k not in LEGACY_CONFIG_DEFAULTS}}
        report = _signature_change_report(old_payload, {"config": config.to_dict()})
        assert report["first_stage_to_rebuild"] == STAGE_TIER_DOWNSTREAM, report
        assert "msk_diagnosis_codes" in report["changed_config_keys"]
        unchanged_report = _signature_change_report(old_payload, {"config": legacy_config.to_dict()})
        assert unchanged_report["first_stage_to_rebuild"] is None, unchanged_report
        eligibility_audit = json.loads(
            Path(results["rehab_code_definition_eligibility_audit"]).read_text(encoding="utf-8")
        )
        assert eligibility_audit["matched_sets_total"] == int(matches.height)
        mediation_diagnostics = results["mediation"]["longitudinal_gcomp"]["point_estimates"]["model_diagnostics"]
        assert "income_status_model_converged" in mediation_diagnostics
        assert "logit_iteration_budget" in mediation_diagnostics
        return {
            "status": "PASS",
            "rehab_code_relabel_verified": True,
            "legacy_signature_handling_verified": True,
            "synthetic_people": 240,
            "synthetic_person_years": int(data.height),
            "matched_pairs": int(matches.height),
            "main_models_finite": True,
            "sex_heterogeneity_outputs_created": True,
            "longitudinal_mediation_finite": True,
            "matched_vs_unmatched_treated_table_created": True,
            "small_cell_pooling_rules_verified": True,
        }

def standalone_main(argv: list[str] | None = None) -> int:
    args = _build_parser().parse_args(argv)
    if args.self_test:
        print(json.dumps(run_internal_self_test(), indent=2))
        return 0
    if args.environment_check:
        payload = {
            "target_python": TARGET_PYTHON_VERSION,
            "target_polars": TARGET_POLARS_VERSION,
            "python": sys.version,
            "python_executable": sys.executable,
            "platform": platform.platform(),
            **_polars_runtime_capabilities(),
            "numpy": getattr(np, "__version__", "unknown"),
            "pandas": getattr(pd, "__version__", "unknown"),
            "scikit_learn": getattr(__import__("sklearn"), "__version__", "unknown"),
            "scipy": getattr(__import__("scipy"), "__version__", "unknown"),
            **_pandas_arrow_roundtrip_status(),
        }
        print(json.dumps(payload, indent=2))
        return 0
    if args.config:
        config, reporting = load_pipeline_and_reporting_config(args.config)
    else:
        config = PipelineConfig(**USER_CONFIG)
        reporting = PaperReportingConfig(**PAPER_REPORTING_CONFIG)
    config.validate()
    reporting.validate()
    if args.check_signature:
        from dataclasses import replace
        print(json.dumps(describe_signature_change(replace(config, reuse_existing_outputs=True)), indent=2, default=str))
        return 0
    if args.schema_check:
        config.ensure_dirs()
        schema = schema_union(config.raw_glob)
        required = {"simple_id", "ja", "gbja", "divorcing", "fmsd", "marriage_start"}
        required.add(
            "first_marriage_start"
            if config.first_marriage_source == "date_fields"
            else "is_first_marriage"
        )
        if config.source_has_entgelt:
            required.add("entgelt")
        requested = set(CORE_RAW_COLUMNS)
        for candidates in INCAPACITY_CANDIDATES.values():
            requested.update(candidates)
        payload = {
            "runtime": {
                "python": sys.version,
                "python_executable": sys.executable,
                **_polars_runtime_capabilities(),
                "scikit_learn": getattr(__import__("sklearn"), "__version__", "unknown"),
            },
            "data_profile": config.data_profile,
            "raw_glob": config.raw_glob,
            "n_columns_in_union_schema": len(schema),
            "required_columns": sorted(required),
            "missing_required_columns": sorted(required - set(schema)),
            "optional_canonical_columns_absent": sorted(requested - set(schema)),
            "playdata_only_columns_detected": sorted(
                set(schema) & {
                    "is_first_marriage", "rtbt", "bzgs", "bzegptgs", "byfhzt",
                    "byfhegptgs", "auazgs", "ajazgs", "whot_ow",
                    "spell_no_rsd_1", "spell_no_rsd_2",
                }
            ),
            "incapacity_source_slot1": _incapacity_source(schema, 1),
            "incapacity_source_slot2": _incapacity_source(schema, 2),
        }
        output = config.diagnostics_dir / "source_schema_report.json"
        output.write_text(json.dumps(payload, indent=2), encoding="utf-8")
        payload["report_path"] = str(output)
        print(json.dumps(payload, indent=2))
        return 1 if payload["missing_required_columns"] else 0
    total_rebuild = bool(config.total_rebuild and not args.reuse_existing)
    if args.reuse_existing:
        from dataclasses import replace


        config = replace(config, reuse_existing_outputs=True)
    if total_rebuild:
        clear_run_directory(config)
    _configure_logging(config)
    effective_force = True if total_rebuild else bool(args.force)
    log.info(
        "Run policy: %s",
        "TOTAL REBUILD (no prior generated files reused)"
        if total_rebuild else
        "stage-aware checkpoint reuse (--reuse-existing)",
    )
    capabilities = _polars_runtime_capabilities()
    log.info(
        "Runtime: Python=%s; Polars=%s; collect=%s; collect_batches=%s (not needed: "
        "scoring streams per-year parquet files through pyarrow); script=%s",
        sys.version.split()[0],
        capabilities["polars_version"],
        capabilities["streaming_collect_mode"],
        capabilities["collect_batches_available"],
        Path(__file__).name if globals().get("__file__") else "psm_260908.py",
    )
    if args.mode == "main":
        result = (
            run_lag1_vs_lag3_comparison(
                config, force=effective_force, reporting=reporting
            )
            if config.run_lag1_vs_lag3 else
            run_main_pipeline(config, force=effective_force, reporting=reporting)
        )
    else:
        if total_rebuild:
            from dataclasses import replace
            base_config = replace(
                config, run_lag1_vs_lag3=False, run_longitudinal_mediation=False,
                generate_figures=False,
            )
            run_main_pipeline(base_config, force=True, reporting=reporting)
        result = run_longitudinal_mediation_only(
            config, n_bootstrap=args.bootstrap, force=effective_force
        )
    print(json.dumps(result, indent=2))
    return 0

if __name__ == "__main__":
    raise SystemExit(standalone_main())
