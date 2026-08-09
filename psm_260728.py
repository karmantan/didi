#!/usr/bin/env python3
"""Standalone divorce–rehabilitation–mortality matched-cohort pipeline.

This CANONICAL REAL-DATA file contains the full selection-on-observables matched-cohort
pipeline in one script. Treatment is first observed divorce from the earliest observed marriage spell,
validated by ``marriage_start == first_marriage_start``. Treatment assignment remains
fixed after t0.

The default main run estimates three specifications:

1. lag 1 for the full 2012–2018 treatment window;
2. lag 1 for the common 2014–2018 window; and
3. lag 3 for the same common 2014–2018 window.

The common-window comparison separates the effect of deeper pre-treatment history from
changes in treatment-cohort composition. Each specification generates its own figures and
landmark mediation outputs. The script performs a total rebuild by default.
It detects the installed Polars streaming API at runtime and does not require internet
access or a hard-coded Polars version. Matching writes a pre-solver edge-feasibility audit;
landmark mediation uses a full common counterfactual prediction grid and an indexed
matched-set bootstrap; and MSK follow-up includes an observation-gap sensitivity.
"""

# Target runtime is Python 3.9.1 (fixed; cannot be upgraded on the secure machine). This
# file's type hints use PEP 604 union syntax (`int | None`, `str | Path`, ...) throughout,
# which Python only evaluates natively from 3.10 onward. `from __future__ import
# annotations` defers all annotation evaluation to strings, so these hints never execute
# at runtime on 3.9 either. This does NOT cover `@dataclass(slots=True)`, since `slots` is
# a real keyword argument to `dataclass()`, not a type hint — that is handled separately
# where the `@dataclass` decorators appear. Must remain the first statement below the
# module docstring (PEP 236: only the docstring/comments may precede a future import).
from __future__ import annotations

# =============================================================================
# USER SETTINGS — EDIT THIS BLOCK BEFORE RUNNING YOUR REAL DATA
# =============================================================================

USER_CONFIG = {
    # Source paths/profile. These are the only design-relevant differences between the
    # canonical and playdata scripts; all specifications below are identical.
    "raw_glob": r"D:\gastwissenschaftler\gastw_20\DIDI\XPrivat\Tan\processed_data\parquet_files\df_4pct_processed\*.parquet",
    "output_dir": r"D:\gastwissenschaftler\gastw_20\DIDI\XPrivat\Tan\processed_data\pipeline_runs",
    "sample_tag": "4pct_firstmarriage_lag1_lag3_notyetdivorced",
    "data_profile": "canonical",
    "source_has_entgelt": True,
    "first_marriage_source": "date_fields",

    # Index cohorts and outcome horizons.
    "year_start": 2012,
    "year_cap": 2018,
    "followup_years": 5,
    "mortality_horizon": 10,
    "lag_depth": 1,
    "lag_comparison_common_year_start": 2014,

    # Main comparator and matching design.
    "control_pool": "not_yet_divorced",
    "caliper": 0.01,
    "controls_per_treated": 1,
    "reuse_controls_across_years": False,
    "seed": 42,
    "strict_main_run": True,
    "minimum_category_frequency": 10,

    # Memory controls. Every eligible observation is scored; only model fitting may use
    # a deterministic control subsample when the annual risk set exceeds the fit cap.
    "max_propensity_fit_rows": 500_000,
    "propensity_score_batch_size": 100_000,
    "checkpoint_row_group_size": 200_000,

    # Numerical optimization only. Actual iterations are recorded by treatment year.
    "propensity_max_iter": 10_000,
    "propensity_tol": 1e-4,

    # Residual-balance adjustment and matched-set bootstrap uncertainty.
    "smd_threshold": 0.10,
    "outcome_bootstrap_replicates": 200,
    "absolute_effect_bootstrap_replicates": 200,

    # Exact optimal matching safeguards; never fall back to greedy matching.
    "optimal_match_dense_max_entries": 5_000_000,
    "optimal_match_sparse_max_edges": 20_000_000,

    # Run lag 1 over 2012–2018 plus lag 1 and lag 3 over the common 2014–2018 window.
    "run_lag1_vs_lag3": True,

    # Figures and temporally ordered landmark mediation for every requested specification.
    "generate_figures": True,
    "run_landmark_mediation": True,
    "run_msk_dropout_sensitivity": True,
    "landmark_years": [1, 2],
    "mediation_bootstrap_replicates": 200,

    "death_registry_end_year": 2023,
    "total_rebuild": True,
}

# Paper/reporting settings are deliberately separate from the analytical design. Changing
# them regenerates only the paper-summary bundle; it does not define a new matched sample,
# propensity model, outcome model, or estimand. The threshold is provisional and must be
# confirmed with FDZ-RV before confidential-data export. No setting can guarantee release
# approval, because the RDC reviews the complete set of requested outputs jointly.
PAPER_REPORTING_CONFIG = {
    "minimum_cell_people": 20,
    "pool_small_diagnosis_codes": True,
    "protect_matchability_cells": True,
    "withhold_small_overlap_counts": True,
}

# Default behavior when the file is run without command-line arguments.
DEFAULT_RUN_MODE = "main"  # main runs lag1-vs-lag3 when USER_CONFIG requests it.
DEFAULT_FORCE_REBUILD = False  # Relevant only when total_rebuild is disabled.
DEFAULT_REUSE_EXISTING = False
DEFAULT_LANDMARK_YEAR = 1
DEFAULT_BOOTSTRAP_REPLICATIONS = 100

# Secure-machine compatibility target. These values are recorded in manifests and
# environment checks; the code still uses capability checks rather than assuming that a
# version string guarantees a particular Polars API.
TARGET_PYTHON_VERSION = "3.9.1"
TARGET_POLARS_VERSION = "0.20.16"

# =============================================================================
# END USER SETTINGS
# =============================================================================



# =============================================================================
# BEGIN variables.py
# =============================================================================

# Canonical raw-variable meanings supplied by the researcher.
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

# Both spellings have appeared. The panel builder picks the one that actually exists.
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

# END variables.py



# =============================================================================
# BEGIN config.py
# =============================================================================

from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any
import json
import sys

try:
    import yaml
except ImportError:
    yaml = None

# slots=True (real memory savings at this pipeline's control-pool scale, plus
# typo-safety) is only accepted by @dataclass() from Python 3.10 onward. On the target
# 3.9.1 runtime it raises `TypeError: __init__() got an unexpected keyword argument
# 'slots'` at class-definition time — i.e. at import, before anything else runs. Gate it
# rather than deleting it outright, so newer interpreters still get the benefit.
_DATACLASS_KWARGS = {"slots": True} if sys.version_info >= (3, 10) else {}


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
    run_landmark_mediation: bool = True
    run_msk_dropout_sensitivity: bool = True
    landmark_years: list[int] = field(default_factory=lambda: [1, 2])
    mediation_bootstrap_replicates: int = 200
    death_registry_end_year: int = 2023
    total_rebuild: bool = True
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
        # Keep the broad not-yet-divorced control pool, but account for the
        # observed annual marital-state composition at t0-1 in propensity scoring,
        # category-level balance, and SMD-driven residual adjustment.
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
        if not self.landmark_years:
            raise ValueError("landmark_years must contain at least one landmark")
        if len(set(self.landmark_years)) != len(self.landmark_years):
            raise ValueError("landmark_years must not contain duplicates")
        if any(year < 1 or year >= self.mortality_horizon for year in self.landmark_years):
            raise ValueError("every landmark year must be positive and smaller than mortality_horizon")
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
        # A nested reporting block is accepted for one-file configuration, but it is
        # not part of PipelineConfig and therefore does not alter the analysis signature.
        data = dict(data)
        data.pop("paper_reporting", None)
        cfg = cls(**data)
        cfg.validate()
        return cfg


@dataclass(**_DATACLASS_KWARGS)
class PaperReportingConfig:
    """Settings for disclosure-aware paper summaries, separate from the estimator.

    These settings control only derived CSV/JSON tables. They do not change treatment,
    controls, matching, outcomes, or inference. The threshold is provisional: FDZ-RV
    may require additional suppression after reviewing the complete requested export.
    """

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
    """Load a YAML file with an optional nested ``paper_reporting`` block."""
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

# END config.py



# =============================================================================
# BEGIN io.py
# =============================================================================

from functools import lru_cache
from glob import glob
from pathlib import Path
import hashlib
import json
import logging
import os
import platform
import sys

import polars as pl

log = logging.getLogger(__name__)


@lru_cache(maxsize=1)
def _streaming_collect_kwargs() -> dict[str, object]:
    """Return the streaming collect syntax supported by installed Polars.

    Secure pension-fund computers may expose either the older ``streaming=True``
    argument or the newer ``engine="streaming"`` argument. A one-row lazy probe is
    more reliable than guessing from a version number and requires no internet access.
    """
    probe = pl.LazyFrame({"_polars_api_probe": [1]})
    errors: list[str] = []
    for kwargs in ({"engine": "streaming"}, {"streaming": True}):
        try:
            probe.collect(**kwargs)
            return kwargs
        except (TypeError, ValueError) as exc:
            errors.append(f"{kwargs}: {exc}")
    raise RuntimeError(
        "Installed Polars exposes neither supported streaming collect API. "
        + " | ".join(errors)
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
    """Collect a LazyFrame, falling back to the non-streaming engine if the streaming
    engine cannot handle this plan.

    On Polars 0.20.16 the streaming engine has been confirmed (not guessed) to mishandle
    plans built from pl.concat(how="vertical") over branches that alias differently-named
    source columns to a shared name -- the treated/control assignment pattern
    (t_id -> simple_id, c_id -> simple_id) used throughout this pipeline's matching,
    mortality/MSK followup, and landmark mediation code. Symptoms range from a spurious
    ColumnNotFoundError/InvalidOperationError/SchemaError to a Rust panic
    (pyo3_runtime.PanicException, a BaseException subclass ordinary except Exception
    cannot catch -- see _iter_lazy_batches_compat for the same underlying disease). The
    non-streaming engine handles the same plans correctly; we only pay its memory cost on
    the specific collects that actually trip the streaming engine, not on every collect
    in the file. Not used for the raw-data-scale scans, which are memory-bounded via
    _iter_lazy_batches_compat's own slicing instead.
    """
    try:
        return lf.collect(**_streaming_collect_kwargs(), **extra_kwargs)
    except BaseException as exc:
        if isinstance(exc, (KeyboardInterrupt, SystemExit)):
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
    except pl.exceptions.InvalidOperationError as exc:
        # Plan-shape-dependent, not a fixed capability of this Polars build: confirmed
        # directly that forward_fill().over(...) (and other window/list-agg-bearing
        # plans) are rejected by the streaming sink engine on 0.20.16 while a trivial
        # probe frame sinks fine, so a cached "does this Polars support sink_parquet"
        # flag would report success and then still crash on this exact write.
        log.warning(
            "Streaming sink_parquet rejected this plan (%s); falling back to an eager "
            "collect + write_parquet for %s.",
            exc, temporary,
        )
        # _safe_collect already handles the case where the eager collect itself hits the
        # streaming engine's concat/alias bug (see _safe_collect's docstring) or a Rust
        # panic, so this fallback is correct even if the sink failure and the collect
        # failure have different root causes.
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
    """Return a cheap but informative fingerprint of one pipeline specification.

    Raw administrative files are not hashed byte-for-byte because that would add a large
    I/O pass before every run. Paths, sizes, and modification times identify the inputs;
    the small Python source files are fully hashed so code changes invalidate the cache.
    """
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
    """Delete the entire generated run directory, but never touch raw input files.

    This is the strongest stale-file protection. It removes panels, matches, diagnostics,
    model outputs, logs, temporary files, and old signatures for exactly one ``sample_tag``.
    The parent ``output_dir`` and all raw Parquet shards remain untouched.
    """
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
        # Resolution can fail for unavailable network mounts. Structural checks above still
        # ensure that only output_dir/sample_tag is targeted.
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


def initialize_run(config, force: bool = False) -> Path:
    """Protect checkpoint reuse when total rebuild has been explicitly disabled.

    The standalone entry point normally deletes the entire run directory first. This
    signature check is a second line of defence for deliberate ``--reuse-existing`` runs.
    A changed input, configuration, or source file requires ``--force`` or a new sample tag.
    """
    import shutil

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

    if (changed or untracked_existing) and not force:
        reason = "the run signature changed" if changed else "untracked outputs already exist"
        raise RuntimeError(
            f"Refusing to reuse {config.run_dir} because {reason}. "
            "Choose a new sample_tag or rerun with --force so stale files cannot be mixed."
        )
    if (changed or untracked_existing) and force:
        for path in generated_dirs:
            shutil.rmtree(path, ignore_errors=True)
        config.ensure_dirs()

    signature_path.write_text(
        json.dumps({"signature": signature, "payload": payload}, indent=2),
        encoding="utf-8",
    )
    return signature_path

# END io.py



# =============================================================================
# BEGIN panels.py
# =============================================================================

from pathlib import Path
import logging

import polars as pl


log = logging.getLogger(__name__)

MSK_DIAGNOSIS_CODE = 20
MENTAL_HEALTH_REHAB_CODE = 30  # Researcher-proposed mcdggr category; verify against the data dictionary.


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


def build_analysis_panel(config: PipelineConfig, force: bool = False) -> Path:
    """Build the only compact panel used by the canonical pipeline.

    The old script built several overlapping panels. This version reads the raw shards
    once and writes one narrow person-year panel containing only variables needed by the
    main matching, outcomes, and diagnostics.
    """
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

    frame = scan_aligned(config.raw_glob, found)
    frame = _optional_nulls(frame, requested, schema)

    # Every downstream cumulative history and risk set assumes exactly one record per
    # person-year. Duplicates are surfaced (diagnostic CSV + JSON audit) but -- per
    # explicit decision -- resolved automatically rather than hard-stopping the run: keep
    # the row with the fewest missing values across all other available columns for that
    # (simple_id, ja) key. This is a real resolution rule (keeps whichever duplicate
    # record actually carries more information), not an arbitrary "first row wins" --
    # and ties are broken by original row order, not at random, so a rerun on the same
    # parquet reproduces exactly.
    duplicate_keys = (
        frame.group_by(["simple_id", "ja"])
        .agg(pl.len().alias("n_rows"))
        .filter(pl.col("n_rows") > 1)
    )
    duplicate_summary = duplicate_keys.select([
        pl.len().alias("n_duplicate_person_year_keys"),
        (pl.col("n_rows") - 1).sum().alias("n_excess_rows"),
    ]).pipe(_safe_collect).row(0, named=True)
    n_duplicate_keys = int(duplicate_summary["n_duplicate_person_year_keys"] or 0)
    if n_duplicate_keys > 0:
        n_excess_rows = int(duplicate_summary["n_excess_rows"] or 0)
        duplicate_path = config.diagnostics_dir / "duplicate_person_year_keys.csv"
        duplicate_keys.sort("n_rows", descending=True).limit(100_000).pipe(_safe_collect).write_csv(duplicate_path)
        log.warning(
            "Found %d duplicate (simple_id, ja) keys (%d excess rows) in the processed "
            "input. See %s. Resolving by keeping the least-missing row per key; see "
            "duplicate_person_year_keys_resolution.json for the exact rule and counts.",
            n_duplicate_keys, n_excess_rows, duplicate_path,
        )
        value_columns = [c for c in frame.columns if c not in ("simple_id", "ja")]
        frame = (
            frame.with_row_index("_dedup_orig_row_order")
            .with_columns(
                pl.sum_horizontal([
                    pl.col(c).is_null().cast(pl.Int32) for c in value_columns
                ]).alias("_dedup_n_missing_other_vars")
            )
            # Sort so the most-complete row (fewest nulls) sorts first within each key;
            # original row order is the final tiebreak so equally-complete duplicates
            # resolve deterministically rather than by whatever order the scan produced.
            .sort(["simple_id", "ja", "_dedup_n_missing_other_vars", "_dedup_orig_row_order"])
            .unique(subset=["simple_id", "ja"], keep="first", maintain_order=True)
            .sort("_dedup_orig_row_order")
            .drop(["_dedup_orig_row_order", "_dedup_n_missing_other_vars"])
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

    # rtwf_jjjj is treated as one person-level death year -- it is the terminal outcome
    # (mortality), not a covariate (guideline.md open question §14.2: confirm rtwf_jjjj
    # is the death year; don't let the code decide). Conflicting non-null values per
    # simple_id cannot be reconciled by silently choosing a minimum or maximum, so -- per
    # explicit decision -- affected people are excluded from the analysis entirely (every
    # person-year row, not just the rtwf_jjjj field) rather than the pipeline guessing a
    # resolution. Excluding the full history, not just nulling the field, matters because
    # rtwf_jjjj is also read row-by-row elsewhere (age masking, risk-set eligibility) --
    # a partially-defined death year left in place would keep feeding those filters.
    # This is a real analytic choice with a real threat attached, so the audit below also
    # checks whether exclusion is differential by the divorcing flag (a crude proxy for
    # treatment status here, before treatment/t0 are constructed): if the excluded and
    # retained groups differ a lot on this, dropping them isn't a free lunch even at a
    # small share of the sample, and that should be reported in the paper, not assumed
    # away.
    death_year_conflicts = (
        frame.filter(pl.col("rtwf_jjjj").is_not_null())
        .group_by("simple_id")
        .agg([
            pl.col("rtwf_jjjj").n_unique().alias("n_distinct_death_years"),
            pl.col("rtwf_jjjj").unique().sort().alias("observed_death_years"),
        ])
        .filter(pl.col("n_distinct_death_years") > 1)
    )
    n_death_conflicts = int(
        death_year_conflicts.select(pl.len()).pipe(_safe_collect).item()
    )
    if n_death_conflicts > 0:
        conflict_path = config.diagnostics_dir / "conflicting_person_death_years.csv"
        (
            death_year_conflicts.limit(100_000)
            .pipe(_safe_collect)
            # List-typed columns cannot be written to CSV on this Polars version
            # ("CSV format does not support nested data" -- confirmed directly) since
            # observed_death_years is produced by .unique().sort() inside .agg().
            .with_columns(pl.col("observed_death_years").cast(pl.List(pl.Utf8)).list.join(", "))
            .write_csv(conflict_path)
        )
        conflicted_ids = death_year_conflicts.select("simple_id")
        total_ids = int(frame.select(pl.col("simple_id").n_unique()).pipe(_safe_collect).item())
        excluded_divorcing_share = float(
            frame.join(conflicted_ids, on="simple_id", how="semi")
            .group_by("simple_id")
            .agg(pl.col("divorcing").fill_null(0).max().alias("any_divorcing"))
            .select(pl.col("any_divorcing").mean())
            .pipe(_safe_collect).item()
        )
        retained_divorcing_share = float(
            frame.join(conflicted_ids, on="simple_id", how="anti")
            .group_by("simple_id")
            .agg(pl.col("divorcing").fill_null(0).max().alias("any_divorcing"))
            .select(pl.col("any_divorcing").mean())
            .pipe(_safe_collect).item()
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
        frame = frame.join(conflicted_ids, on="simple_id", how="anti")

    # Normalize only date fields that are actually available.
    date_expressions = [normalize_date(column, schema[column]) for column in DATE_COLUMNS if column in schema]
    if date_expressions:
        frame = frame.with_columns(date_expressions)

    frame = frame.with_columns(
        pl.col("is_first_marriage").cast(pl.Int8, strict=False).alias("is_first_marriage")
    )
    if config.first_marriage_source == "is_first_marriage":
        # Playdata-only compatibility proxy. This preserves the canonical downstream
        # column names but does not claim that the underlying date fields were observed.
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
        # Duration is measured as of the current person-year. At t0-1 this does not
        # borrow the future divorce year to lengthen the baseline marriage duration.
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

    # Preserve informative missingness. In playdata, entgelt is genuinely absent from
    # the source schema; it is not replaced by rtbt, rtzb, zero, or an imputed earnings
    # amount. Compatibility columns remain null and are excluded from all models.
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

    # Rehabilitation/application activity by slot and year.
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
                & (pl.col(diagnosis) == MSK_DIAGNOSIS_CODE)
            ).then(1).otherwise(0).cast(pl.Int8).alias(f"msk_start_slot{slot}"),
            pl.when(
                pl.col(start).is_not_null()
                & (pl.col(start).dt.year() == pl.col("ja"))
                & (pl.col(diagnosis) == MENTAL_HEALTH_REHAB_CODE)
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
        pl.max_horizontal("failed_app_this_year", "withdrawn_app_this_year", "forwarded_app_this_year")
        .cast(pl.Int8).alias("non_success_app_this_year"),
        (
            pl.col("failed_app_this_year")
            + pl.col("withdrawn_app_this_year")
            + pl.col("forwarded_app_this_year")
            + (pl.col("rehab_starts_this_year") > 0).cast(pl.Int8)
        ).cast(pl.Int16).alias("n_application_activity_types_this_year"),
    ])

    # Person-level event histories. A disk checkpoint bounds memory before window functions.
    log.info("Writing pre-history checkpoint")
    checkpoint = config.panels_dir / "_analysis_pre_history.parquet"
    sink_parquet(
        frame.select([
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
            "msk_duration_days_this_year",
            "failed_app_this_year", "withdrawn_app_this_year", "forwarded_app_this_year",
            "non_success_app_this_year", "n_application_activity_types_this_year",
            "msk_incapacity_months_cat_slot1_this_year",
            "msk_incapacity_months_cat_slot2_this_year",
            "msk_incapacity_months_cat_this_year",
        ]).sort(["simple_id", "ja"]),
        checkpoint,
        config.checkpoint_row_group_size,
    )
    log.info("Pre-history checkpoint written")
    history = pl.scan_parquet(checkpoint).sort(["simple_id", "ja"])
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
    history = history.with_columns([
        pl.when(pl.col("divorcing") == 1).then(pl.col("ja")).otherwise(None)
        .min().over("simple_id").cast(pl.Int32).alias("first_divorce_year"),
        first_marriage_divorce_expr.cast(pl.Int8)
        .alias("divorce_from_first_marriage_this_year"),
        # One row per person-year is retained in the compact panel, so summing the
        # annual divorce flag counts distinct flagged years without accidentally
        # counting a null as an extra category.
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
        "msk_duration_days_this_year",
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
    log.info("Writing final analysis panel")
    sink_parquet(history.select(final_columns), output, config.checkpoint_row_group_size)
    log.info("Final analysis panel written")
    checkpoint.unlink(missing_ok=True)
    write_manifest(config, found, final_columns, manifest)
    log.info("Built analysis panel: %s", output)
    return output

# END panels.py



# =============================================================================
# BEGIN risksets.py
# =============================================================================

from pathlib import Path
import logging

import polars as pl


log = logging.getLogger(__name__)

BASELINE_COLUMNS = [
    "age", "age_band", "ge_cat", "fmsd_cat",
    "cum_rehabs_by_year", "years_since_last_rehab", "ever_rehab_to_date",
    "cum_mental_health_rehabs_by_year", "ever_mental_health_rehab_to_date",
    "ever_msk_rehab_to_date", "non_success_app_this_year",
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


def build_risk_sets(config: PipelineConfig, panel_path: str | Path, force: bool = False) -> dict[str, Path]:
    treated_path = config.analysis_dir / f"riskset_treated_lag{config.lag_depth}.parquet"
    controls_path = config.analysis_dir / f"riskset_controls_{config.control_pool}_lag{config.lag_depth}.parquet"
    audit_path = config.diagnostics_dir / f"filter_audit_{config.control_pool}_lag{config.lag_depth}.csv"
    if treated_path.exists() and controls_path.exists() and audit_path.exists() and not force:
        return {"treated": treated_path, "controls": controls_path, "audit": audit_path}

    panel = pl.scan_parquet(panel_path)
    index_panel = panel.filter(pl.col("ja") >= config.year_start)
    if config.year_cap is not None:
        index_panel = index_panel.filter(pl.col("ja") <= config.year_cap)

    lag1 = _lag_frame(panel, 1, BASELINE_COLUMNS)
    lag2 = _lag_frame(panel, 2, TREND_COLUMNS) if config.lag_depth == 3 else None
    lag3 = _lag_frame(panel, 3, TREND_COLUMNS) if config.lag_depth == 3 else None

    def attach_lags(base: pl.LazyFrame) -> pl.LazyFrame:
        result = base.join(lag1, on=["simple_id", "t0"], how="left")
        if config.lag_depth == 3:
            result = result.join(lag2, on=["simple_id", "t0"], how="left")
            result = result.join(lag3, on=["simple_id", "t0"], how="left")
        return result

    audit: list[dict] = []

    treated = index_panel.filter(pl.col("first_divorce_this_year") == 1)
    previous = _record(
        audit, "treated",
        "first observed divorce in 2012-2018 before first-marriage restriction",
        treated, None,
    )
    treated = treated.filter(pl.col("divorce_from_first_marriage_this_year") == 1)
    first_marriage_stage = (
        "restrict to marriage spell with marriage_start equal to first_marriage_start"
        if config.first_marriage_source == "date_fields"
        else "playdata proxy: require is_first_marriage equal to 1 on the divorce row"
    )
    previous = _record(
        audit, "treated", first_marriage_stage, treated, previous,
    )
    treated = treated.filter(
        pl.col("rtwf_jjjj").is_null() | (pl.col("rtwf_jjjj") > pl.col("ja"))
    )
    previous = _record(audit, "treated", "require alive at assigned t0", treated, previous)
    treated = treated.select([
        "simple_id", pl.col("ja").alias("t0"), pl.lit(1, dtype=pl.Int8).alias("treated"),
        "msk_starts_this_year",
    ])
    treated = treated.filter(pl.col("msk_starts_this_year") == 0)
    previous = _record(audit, "treated", "exclude MSK rehabilitation starting in t0", treated, previous)
    treated = attach_lags(treated)
    treated = treated.filter(pl.col("lag1_source_year").is_not_null())
    previous = _record(audit, "treated", "require an observed t0-1 record", treated, previous)
    treated = treated.filter(pl.col("lag1_age_band").is_not_null())
    previous = _record(audit, "treated", "require valid age at t0-1 for exact matching", treated, previous)
    treated = treated.filter(pl.col("lag1_ever_msk_rehab_to_date").fill_null(0) == 0)
    previous = _record(audit, "treated", "exclude prior MSK rehabilitation through t0-1", treated, previous)
    if config.lag_depth == 3:
        treated = treated.filter(
            pl.col("lag2_source_year").is_not_null() & pl.col("lag3_source_year").is_not_null()
        )
        _record(audit, "treated", "require observed t0-2 and t0-3 records", treated, previous)

    treatment_years = treated.select(pl.col("t0").alias("candidate_year")).unique()
    controls = index_panel.join(treatment_years, left_on="ja", right_on="candidate_year", how="inner")
    previous = _record(audit, "controls", "person-years in treated index years", controls, None)
    controls = controls.filter(
        pl.col("first_divorce_year").is_null() | (pl.col("first_divorce_year") > pl.col("ja"))
    )
    previous = _record(audit, "controls", "not yet divorced at candidate t0", controls, previous)
    controls = controls.filter(
        pl.col("rtwf_jjjj").is_null() | (pl.col("rtwf_jjjj") > pl.col("ja"))
    )
    previous = _record(audit, "controls", "require alive at assigned t0", controls, previous)
    controls = controls.filter(pl.col("msk_starts_this_year") == 0)
    previous = _record(audit, "controls", "exclude MSK rehabilitation starting in t0", controls, previous)
    controls = controls.select([
        "simple_id", pl.col("ja").alias("t0"), pl.lit(0, dtype=pl.Int8).alias("treated"),
        "msk_starts_this_year",
    ])
    controls = attach_lags(controls)
    controls = controls.filter(pl.col("lag1_source_year").is_not_null())
    previous = _record(audit, "controls", "require an observed t0-1 record", controls, previous)
    controls = controls.filter(pl.col("lag1_age_band").is_not_null())
    previous = _record(audit, "controls", "require valid age at t0-1 for exact matching", controls, previous)
    controls = controls.filter(pl.col("lag1_ever_msk_rehab_to_date").fill_null(0) == 0)
    previous = _record(audit, "controls", "exclude prior MSK rehabilitation through t0-1", controls, previous)
    if config.lag_depth == 3:
        controls = controls.filter(
            pl.col("lag2_source_year").is_not_null() & pl.col("lag3_source_year").is_not_null()
        )
        _record(audit, "controls", "require observed t0-2 and t0-3 records", controls, previous)

    # Prefix category names are already strings; missing category is explicit. No complete-case deletion.
    sink_parquet(treated.drop("msk_starts_this_year"), treated_path, config.checkpoint_row_group_size)
    sink_parquet(controls.drop("msk_starts_this_year"), controls_path, config.checkpoint_row_group_size)
    pl.DataFrame(audit).write_csv(audit_path)
    return {"treated": treated_path, "controls": controls_path, "audit": audit_path}

# END risksets.py



# =============================================================================
# BEGIN matching.py
# =============================================================================

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
    """Construct a version-compatible OneHotEncoder.

    Pension-fund environments may have an older scikit-learn release using ``sparse``
    rather than ``sparse_output``. Very old releases may also lack ``min_frequency``.
    The final fallback preserves correct categorical encoding but does not collapse rare
    levels; the run manifest records the installed scikit-learn version for replication.
    """
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

    # The playdata schema genuinely lacks entgelt. Keep every design and estimator
    # setting unchanged, but exclude only the earnings variables that cannot be defined.
    # No proxy variable is substituted and no complete-case deletion is introduced.
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
    # Exact-match variables need not also enter the propensity model; within each exact
    # stratum they are constant and would only duplicate columns.
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
    solver = "lbfgs" if len(data) <= 200_000 else "saga"
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




def _iter_lazy_batches_compat(
    frame: pl.LazyFrame,
    *,
    chunk_size: int,
    maintain_order: bool,
):
    """Yield memory-bounded batches across installed Polars APIs.

    Prefer native ``collect_batches`` when available. If the offline environment has an
    older Polars release without that method, repeatedly collect lazy slices instead of
    materializing the complete annual control pool. The slice fallback can be slower
    because the lazy query may be rescanned, but it preserves bounded memory and keeps the
    estimator and scored population unchanged.
    """
    collect_batches = getattr(frame, "collect_batches", None)
    if collect_batches is not None:
        streaming_kwargs = _streaming_collect_kwargs()
        attempts = [
            {"chunk_size": chunk_size, "maintain_order": maintain_order, **streaming_kwargs},
            {"batch_size": chunk_size, "maintain_order": maintain_order, **streaming_kwargs},
            {"chunk_size": chunk_size, "maintain_order": maintain_order},
            {"batch_size": chunk_size, "maintain_order": maintain_order},
            {"chunk_size": chunk_size},
            {"batch_size": chunk_size},
        ]
        errors: list[str] = []
        for kwargs in attempts:
            yielded = False
            try:
                for batch in collect_batches(**kwargs):
                    yielded = True
                    yield batch
                return
            except (TypeError, ValueError) as exc:
                if yielded:
                    raise RuntimeError(
                        "Polars collect_batches failed after yielding data; refusing to "
                        "restart with a different API signature because that could duplicate rows."
                    ) from exc
                errors.append(f"{kwargs}: {exc}")
        log.warning(
            "Native LazyFrame.collect_batches exists but no tested signature worked; "
            "using memory-bounded lazy slicing. Details: %s",
            " | ".join(errors),
        )
    else:
        log.warning(
            "Polars %s has no LazyFrame.collect_batches; using memory-bounded lazy "
            "slice collection. This may be slower but does not collect the full annual "
            "scoring frame into memory.",
            getattr(pl, "__version__", "unknown"),
        )

    offset = 0
    while True:
        # Do NOT use the streaming engine here. Confirmed on Polars 0.20.16: collecting a
        # sliced pl.concat(...)-built LazyFrame with streaming=True triggers a Rust-level
        # panic (pyo3_runtime.PanicException, a BaseException subclass) inside
        # polars_pipe::pipeline::convert::get_sink. This code path is exactly the annual
        # treated+control concat that _score_year_memory_bounded builds, so it is not an
        # edge case -- it fires on every treatment year of every specification. The
        # non-streaming engine handles the identical concat+slice plan correctly, and
        # .slice() (not the streaming flag) is what bounds memory per batch.
        batch = frame.slice(offset, chunk_size).collect()
        if batch.height == 0:
            break
        yield batch
        offset += batch.height
        if batch.height < chunk_size:
            break


def _score_year_memory_bounded(
    config: PipelineConfig,
    treated_path: str | Path,
    controls_path: str | Path,
    year: int,
    features: FeatureColumns,
    use_columns: list[str],
    output: Path,
) -> dict:
    treated_lf = (
        pl.scan_parquet(treated_path).filter(pl.col("t0") == year)
        .select(use_columns).with_columns(pl.lit(1, dtype=pl.Int8).alias("treated"))
    )
    controls_lf = (
        pl.scan_parquet(controls_path).filter(pl.col("t0") == year)
        .select(use_columns).with_columns(pl.lit(0, dtype=pl.Int8).alias("treated"))
    )
    n_treated = int(treated_lf.select(pl.len()).pipe(_safe_collect).item())
    n_controls = int(controls_lf.select(pl.len()).pipe(_safe_collect).item())
    if n_treated == 0 or n_controls == 0:
        raise RuntimeError(f"Year {year}: propensity model has {n_treated} treated and {n_controls} controls.")

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
    actual_control_fraction = len(sampled_controls) / n_controls
    # All treated are retained while controls may be sampled for fitting. Under random
    # control sampling the slope coefficients are unchanged; correcting the intercept by
    # log(sample fraction) restores population odds before every eligible control is scored.
    log_odds_offset = float(np.log(actual_control_fraction)) if actual_control_fraction < 1 else 0.0

    parts_dir = output.parent / f"_{output.stem}_parts"
    shutil.rmtree(parts_dir, ignore_errors=True)
    parts_dir.mkdir(parents=True)
    annual_lf = pl.concat([treated_lf, controls_lf], how="vertical")
    score_columns = ["simple_id", "t0", "treated", "pscore", *features.exact]
    part_count = 0
    for batch in _iter_lazy_batches_compat(
        annual_lf,
        chunk_size=config.propensity_score_batch_size,
        maintain_order=False,
    ):
        frame = batch.to_pandas()
        linear_predictor = pipeline.decision_function(frame[features.model]) + log_odds_offset
        frame["pscore"] = np.clip(expit(linear_predictor), 1e-6, 1 - 1e-6)
        part_path = parts_dir / f"part_{part_count:05d}.parquet"
        pl.from_pandas(frame[score_columns]).write_parquet(part_path, compression="zstd")
        part_count += 1
    if part_count == 0:
        raise RuntimeError(f"Year {year}: scoring produced no batches.")
    sink_parquet(pl.scan_parquet(str(parts_dir / "part_*.parquet")), output, config.checkpoint_row_group_size)
    shutil.rmtree(parts_dir, ignore_errors=True)
    return {
        "n_treated": n_treated,
        "n_controls": n_controls,
        "propensity_fit_rows": int(len(fit_data)),
        "controls_used_to_fit_propensity": int(len(sampled_controls)),
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
    """Small diagnostic only; never supplies the analysis matches."""
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
    """Count admissible treated-control edges without allocating the match matrix."""
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
    """Persist each stratum before solving, so diagnostics survive a deliberate stop."""
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
    """Exact 1:1 caliper matching without replacement.

    The objective is lexicographic: first maximize the number of real matches, then
    minimize total absolute propensity-score distance. Small strata use the dense
    Hungarian solver. Larger strata use SciPy's exact sparse bipartite solver. Every
    treated row receives either a real control or its own high-cost dummy control; dummy
    assignments are discarded. There is no greedy or with-replacement fallback.
    """
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

    # A dummy penalty greater than the maximum possible sum of all real distances makes
    # the solver maximize match count before minimizing distance among those matches.
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
    preflight_path.unlink(missing_ok=True)

    treated_schema = set(pl.read_parquet_schema(treated_path))
    control_schema = set(pl.read_parquet_schema(controls_path))
    common = treated_schema & control_schema
    features = resolve_features(config, common)
    use_columns = list(dict.fromkeys(["simple_id", "t0", *features.exact, *features.model]))

    years = (
        pl.scan_parquet(treated_path)
        .select("t0").unique().sort("t0").pipe(_safe_collect)
        .get_column("t0").to_list()
    )
    if not years:
        raise RuntimeError("No treated index years remain after risk-set filtering.")

    temp = config.run_dir / "_matching_temp"
    if temp.exists():
        shutil.rmtree(temp)
    temp.mkdir(parents=True)
    score_files: list[Path] = []
    match_files: list[Path] = []
    used_controls: set[int] = set()
    audits: list[dict] = []
    next_group = 1

    try:
        for year in years:
            score_file = temp / f"scores_{year}.parquet"
            score_diagnostic = _score_year_memory_bounded(
                config,
                treated_path,
                controls_path,
                int(year),
                features,
                use_columns,
                score_file,
            )
            score_files.append(score_file)

            matches, diagnostic = _match_scored_year_by_exact_strata(
                score_file, features, config, used_controls, preflight_path
            )
            if matches.empty and config.strict_main_run:
                raise RuntimeError(f"Year {year}: no treated cases could be matched.")
            if not matches.empty:
                matches["match_group"] = np.arange(next_group, next_group + len(matches), dtype=np.int64)
                next_group += len(matches)
                used_controls.update(matches["c_id"].astype(np.int64).tolist())
                match_file = temp / f"matches_{year}.parquet"
                pl.from_pandas(matches).write_parquet(match_file, compression="zstd")
                match_files.append(match_file)

            diagnostic.update(score_diagnostic)
            diagnostic.update({
                "t0": int(year),
                "match_rate": diagnostic["n_matched"] / max(diagnostic["n_treated"], 1),
                "mean_abs_ps_diff": float(matches["abs_ps_diff"].mean()) if not matches.empty else np.nan,
                "max_abs_ps_diff": float(matches["abs_ps_diff"].max()) if not matches.empty else np.nan,
            })
            audits.append(diagnostic)

        if not match_files:
            raise RuntimeError("Matching produced no matched pairs.")
        sink_parquet(pl.scan_parquet(str(temp / "matches_*.parquet")), matched_path, config.checkpoint_row_group_size)
        sink_parquet(pl.scan_parquet(str(temp / "scores_*.parquet")), scores_path, config.checkpoint_row_group_size)
        pl.DataFrame(audits).sort("t0").write_csv(audit_path)
    finally:
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

# END matching.py



# =============================================================================
# BEGIN diagnostics.py
# =============================================================================

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
            # Missingness is itself a binary covariate and receives its own SMD.
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



def select_imbalanced_covariates(
    config: PipelineConfig,
    balance_summary_path: str | Path,
    threshold: float | None = None,
) -> list[dict]:
    """Select residual adjustment variables from THIS matched sample.

    Categorical variables are selected using the maximum level-specific SMD. Numeric
    missingness components map back to their base amount variable, whose outcome design
    includes both an imputed value and an explicit missingness indicator. Exact-match
    variables are retained only if the diagnostic unexpectedly shows residual imbalance.
    """
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
    """Describe annual-record coverage and the relation between exit and death year.

    This table does not decide how censoring should be handled. It makes the structural
    data issue visible before mortality or competing-risk estimates are interpreted.
    """
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

# END diagnostics.py


# =============================================================================
# BEGIN paper_summaries.py
# =============================================================================

from pathlib import Path
import json

import numpy as np
import pandas as pd
import polars as pl


def _scalar(frame: pl.LazyFrame, expression: pl.Expr) -> int | float | None:
    """Collect one scalar without materialising the underlying person-year table."""
    value = frame.select(expression).pipe(_safe_collect).item()
    if value is None:
        return None
    if isinstance(value, (np.integer, int)):
        return int(value)
    if isinstance(value, (np.floating, float)):
        return float(value)
    return value


def _write_metric_table(rows: list[dict], path: Path) -> Path:
    # Metric tables intentionally mix numeric values and labels such as sample_tag.
    # pandas writes this heterogeneous column reliably across the fixed Python/Polars
    # environment, whereas older Polars versions may infer an overly narrow dtype.
    pd.DataFrame(rows).to_csv(path, index=False)
    return path


PAPER_POOLED_CODE_LABEL = "__POOLED_BELOW_THRESHOLD__"


def _pool_small_code_cells(
    rehab_long: pl.LazyFrame,
    threshold: int,
    key_columns: list[str],
    include_year_span: bool,
) -> pl.DataFrame:
    """Aggregate diagnosis-code cells, pooling those below the RDC disclosure threshold.

    This applies a provisional small-cell rule before FDZ-RV review. It reduces
    avoidable disclosure but does not guarantee release approval, because the complete
    set of requested outputs is reviewed jointly. Within each ``key_columns`` group
    (e.g. per calendar year), codes with
    fewer than ``threshold`` unique people are pooled into one labelled bucket. When
    exactly one code falls below the threshold, the smallest retained code is folded in
    as well, because a bucket holding a single code would reveal exactly that code.
    Pooled counts are recomputed exactly from person-level rows in one extra
    aggregation pass — summing per-code ``unique_people`` would double count people who
    appear under several codes. If the pooled bucket itself still holds fewer people
    than the threshold, its counts are withheld and the row is flagged rather than
    published. ``threshold`` <= 0 reproduces the unpooled table (synthetic self-test).
    """
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

    # Decide per key group which codes pool. The loop runs over a small collected
    # frame (calendar years x broad diagnosis groups); determinism matters for
    # replication, so ties break on events and then on the code label itself.
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
            # Complementary pooling: fold in the smallest retained code so the bucket
            # never consists of one identifiable category.
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

    # One exact re-aggregation pass under the final labels; retained rows reproduce the
    # naive table, pooled rows deduplicate people across their member codes correctly.
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
    """Fingerprint reporting settings and analytical inputs without hashing large parquet files."""
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
    """Conservative release rule for a binary proportion and its complement."""
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
    """Write disclosure-aware paper summaries plus exact internal diagnostics.

    The paper-facing files apply provisional threshold rules configured separately from
    the analytical design. They reduce avoidable small-cell disclosures but cannot
    guarantee FDZ-RV release approval. Exact internal diagnostics remain outside the
    paper-summary folder for secure-machine inspection and are named explicitly.
    """
    reporting.validate()
    output_dir = config.diagnostics_dir / "paper_summary_tables"
    output_dir.mkdir(parents=True, exist_ok=True)
    paths = {
        "sample_overview": output_dir / "paper_sample_overview.csv",
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

    # ------------------------------------------------------------------
    # 1. Overall source-panel and event counts.
    # ------------------------------------------------------------------
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

    # ------------------------------------------------------------------
    # 2. Annual source-panel counts, including divorce and rehabilitation.
    # ------------------------------------------------------------------
    annual = (
        panel.group_by("ja")
        .agg([
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
            (pl.col("rtwf_jjjj") == pl.col("ja")).sum().alias("recorded_deaths_in_year"),
        ])
        .sort("ja")
        .pipe(_safe_collect)
    )
    annual.write_csv(paths["annual_panel"])

    # ------------------------------------------------------------------
    # 3. Divorce cohorts, risk-set eligibility and matching by treatment year.
    # ------------------------------------------------------------------
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
    # Polars 0.20 joins are dtype-strict (no implicit upcast): the cohort spine is
    # Int64 from a Python range while t0 arrives as Int32 from the riskset/matches
    # parquet files. Upcasting every t0 to Int64 keeps this working on the pinned
    # 0.20.16 as well as on newer versions that would auto-cast.
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
                # Complementary suppression: publishing both eligible and matched would
                # reveal the below-threshold unmatched count by subtraction.
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

    # ------------------------------------------------------------------
    # 4. Broad rehabilitation diagnosis categories, counted as starts.
    # ------------------------------------------------------------------
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
    # Cells below the disclosure threshold are pooled before writing (see
    # _pool_small_code_cells); shares use the exact pre-pooling event total so retained
    # codes keep correct denominators even when the pooled bucket's count is withheld.
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

    # ------------------------------------------------------------------
    # 5. Paper-facing attrition table. Rows are t0 assignments; unique-person counts
    #    are also shown but are not additive across annual control risk sets.
    # ------------------------------------------------------------------
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

    # ------------------------------------------------------------------
    # 6. Aggregate matching diagnostics and exact annual audit.
    # ------------------------------------------------------------------
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

    # ------------------------------------------------------------------
    # 7. Matched versus unmatched treated individuals. Exact values are written to an
    #    internal diagnostic; the paper-facing version applies provisional cell rules.
    #    Treatment year is included because matchability can change across annual risk
    #    sets when cohort size, overlap, and the remaining control pool change.
    # ------------------------------------------------------------------
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

        # Missingness is a binary characteristic and is protected using both the
        # missing and observed cells, so a released rate cannot disclose its complement.
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

        # The internal table retains original level-specific counts and SMDs.
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
                # Complementary pooling ensures the pooled row never identifies one
                # original level. Choose the smallest retained joint cell deterministically.
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

    # ------------------------------------------------------------------
    # 8. Repeated-person overlap. Controls are not reused as controls, but annual risk-set
    #    sampling allows a person to serve as a control before later becoming treated.
    #    This is a dependence issue for inference, not a matching error.
    # ------------------------------------------------------------------
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

    # ------------------------------------------------------------------
    # 9. Propensity-score distributions and overlap by treatment year.
    # ------------------------------------------------------------------
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

    # ------------------------------------------------------------------
    # 10. Concise balance summary for manuscript prose; full variable/level tables remain
    #    in the original balance outputs (balance_detail is named in the manifest as the
    #    source for the manuscript's per-covariate baseline/balance table).
    # ------------------------------------------------------------------
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
            "recorded_deaths_in_year in paper_annual_panel_counts.csv counts person-year "
            "rows whose calendar year equals the person's death year (rtwf_jjjj). A death "
            "with no annual record in the death year is therefore not counted there "
            "(guideline open question 14.2: whether the register writes a row at the "
            "death year). Quantify the gap with deaths_recorded_after_last_annual_record "
            "in diagnostics/panel_coverage_diagnostics.csv before quoting annual death "
            "counts. Mortality follow-up and all mortality estimates are unaffected: the "
            "death year enters the outcome builders as a person-level attribute, not "
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
        # One-line definitions double as the documentation the RDC output review asks
        # for when releasing files from the secure machine.
        "definitions": {
            "sample_overview": "Headline counts of the processed source panel: people, person-years, observation window, divorce and rehabilitation totals.",
            "annual_panel": "Annual person-year rows, unique people, divorces, rehabilitation events and recorded deaths; the annual death-count definition in the limitations file constrains how deaths may be quoted.",
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
        # The manuscript needs these files too; naming them here keeps the export
        # request complete so nothing is stranded on the secure machine.
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
            # Secondary specifications share the parent run's canonical panel and do
            # not rebuild this file; the pointer says so instead of dangling.
            "panel_coverage_diagnostics": (
                str(config.diagnostics_dir / "panel_coverage_diagnostics.csv")
                if (config.diagnostics_dir / "panel_coverage_diagnostics.csv").exists()
                else (
                    "generated by the parent full-window run; see "
                    "parent_panel_reference.json in this specification's folder"
                )
            ),
            "landmark_mediation_audits": str(
                config.diagnostics_dir / "landmark<k>_mediation_audit.json"
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


# END paper_summaries.py


# =============================================================================
# BEGIN marital.py
# =============================================================================

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
    """Describe marriage order and annual marital state without inferring remarriage.

    The marriage-order output is deliberately limited to the treatment restriction used in
    sample construction. The fmsd outputs describe observed status around assigned t0 for
    treated people, all eligible controls, and controls selected by matching. They do not
    claim that later remarriage is completely observed.
    """
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

# END marital.py



# =============================================================================
# BEGIN outcomes.py
# =============================================================================

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
    """Build a fixed five-year first-MSK risk set with death as a competing event.

    The death year is taken directly from the person-level rtwf_jjjj field. A death does
    not require an annual panel row in the death year. The function creates the full
    follow-up grid through t0+5, joins recorded MSK starts, and records whether each annual
    panel row was present so any outcome-observation gaps remain visible in diagnostics.
    """
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
    # If MSK rehabilitation and death occur in the same calendar year, rehabilitation is
    # counted first because a recorded rehabilitation start implies survival to that start.
    followup = followup.with_columns([
        pl.when(pl.col("msk_event") == 1).then(1)
        .when(pl.col("death_event") == 1).then(2)
        .otherwise(0).cast(pl.Int8).alias("event_type"),
        ((pl.col("msk_event") == 1) & (pl.col("death_event") == 1))
        .cast(pl.Int8).alias("same_year_msk_and_death"),
    ]).sort(["match_group", "treated", "follow_year"])
    followup = followup.with_columns([
        # A person can legitimately appear in two spells under risk-set matching
        # (control before their own divorce, treated afterwards). First-event
        # accounting must therefore run within a spell (simple_id, t0), never
        # across a person's spells.
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
    """Censor both pair members before the first annual observation gap in either member.

    This is a selection-sensitive robustness specification, not a replacement for the main
    estimand. It tests whether treating an absent annual row as no recorded rehabilitation
    materially drives the MSK result.
    """
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
    """Build mortality person-years from the person-level rtwf_jjjj death year.

    Annual pension/employment rows are not required in the death year. Each matched person
    contributes from t0+1 through the earliest of death, the requested horizon, and the
    administrative death-registry end year. This avoids converting annual-record dropout
    into mortality censoring.
    """
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
    """Build a full-rank outcome design without complete-case deletion."""
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

    # Drop no-variation columns except treatment/intercept, then use pivoted QR to retain
    # a full-rank design while explicitly protecting the treatment coefficient.
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


def _unpenalized_logistic_regression(x: np.ndarray, y: np.ndarray, sample_weight: np.ndarray | None = None) -> LogisticRegression:
    """Fit an unpenalized sklearn logit, with an explicit rare-event fallback.

    The primary fit is unpenalized. If an old sklearn version lacks that option, or if a
    sparse/separated specification does not converge, the final fallback uses a tiny L2
    penalty (C=1e6). The model records which route was used so the result cannot be
    mistaken for an ordinary unpenalized MLE.
    """
    attempts = [
        {"penalty": None, "solver": "lbfgs", "max_iter": 500, "label": "unpenalized_none_lbfgs"},
        {"penalty": "none", "solver": "lbfgs", "max_iter": 500, "label": "unpenalized_string_lbfgs"},
        {"penalty": "l2", "C": 1e4, "solver": "liblinear", "max_iter": 1000, "label": "tiny_ridge_fallback_C1e4"},
    ]
    last_error = None
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        for attempt in attempts:
            label = attempt.pop("label")
            try:
                model = LogisticRegression(fit_intercept=False, tol=1e-7, **attempt)
                model.fit(x, y, sample_weight=sample_weight)
                if int(np.max(model.n_iter_)) < model.max_iter:
                    model._pipeline_fit_method = label
                    model._pipeline_unpenalized_approximation = label.startswith("tiny_ridge")
                    return model
                last_error = RuntimeError(f"{label} reached max_iter")
            except (TypeError, ValueError, RuntimeError) as exc:
                last_error = exc
                continue
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
) -> tuple[float, float, float, int]:
    rng = np.random.default_rng(seed)
    unique = np.unique(groups)
    group_indices = {group: np.flatnonzero(groups == group) for group in unique}
    coefficients: list[float] = []
    for _ in range(n_replicates):
        sampled = rng.choice(unique, size=len(unique), replace=True)
        indices = np.concatenate([group_indices[group] for group in sampled])
        try:
            model = _unpenalized_logistic_regression(x[indices], y[indices], weights[indices])
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
    model = _unpenalized_logistic_regression(x, y, weights)
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
            x, y, groups, weights, treated_index, config.seed, config.outcome_bootstrap_replicates
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
    """Reader-facing risks, risk differences, events per 1,000 and risk ratios."""
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

# END outcomes.py



# =============================================================================
# BEGIN figures.py
# =============================================================================

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
        ax.errorbar(
            data["event_time"], data["estimate"],
            yerr=[data["estimate"] - data["ci_low"], data["ci_high"] - data["estimate"]],
            marker="o", capsize=3,
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
        ax.errorbar(estimate, y, xerr=[estimate - low, high - estimate], fmt="o", capsize=4)
        ax.axvline(0, linewidth=1)
        ax.set_yticks(y)
        ax.set_yticklabels(part["specification_label"].tolist())
        ax.set_xlabel("Risk difference per 1,000")
        ax.set_title("MSK rehabilitation" if outcome == "msk" else "Mortality")
        ax.grid(axis="x", alpha=0.25)
    fig.suptitle("Figure 4. Lag depth and common-window comparison")
    fig.tight_layout()
    return _save_figure(fig, output_base)


def plot_mediation_decomposition(
    mediation_result: dict,
    output_base: str | Path,
) -> dict[str, str]:
    keys = [
        ("total_effect_risk_difference", "Total effect"),
        ("natural_direct_effect_risk_difference", "Direct effect"),
        ("natural_indirect_effect_risk_difference", "Indirect effect through MSK rehabilitation"),
    ]
    estimates = np.array([mediation_result["point_estimates"][key] * 1000 for key, _ in keys])
    low = np.array([mediation_result["bootstrap_intervals"][key]["ci_low"] * 1000 for key, _ in keys])
    high = np.array([mediation_result["bootstrap_intervals"][key]["ci_high"] * 1000 for key, _ in keys])
    y = np.arange(len(keys))
    fig, ax = plt.subplots(figsize=(8.2, 4.7))
    ax.errorbar(estimates, y, xerr=[estimates - low, high - estimates], fmt="o", capsize=4)
    ax.axvline(0, linewidth=1)
    ax.set_yticks(y)
    ax.set_yticklabels([label for _, label in keys])
    ax.set_xlabel("Mortality risk difference per 1,000")
    ax.set_title(
        f"Figure 5. Landmark mediation decomposition (landmark = year {mediation_result['landmark_year']})"
    )
    ax.grid(axis="x", alpha=0.25)
    return _save_figure(fig, output_base)


def plot_mediation_landmark_comparison(
    mediation_results: dict[str, dict],
    output_base: str | Path,
) -> dict[str, str]:
    """Compare one- and two-year landmark decompositions in one figure."""
    keys = [
        ("total_effect_risk_difference", "Total effect"),
        ("natural_direct_effect_risk_difference", "Direct effect"),
        ("natural_indirect_effect_risk_difference", "Indirect effect through MSK rehabilitation"),
    ]
    ordered = sorted(
        mediation_results.items(),
        key=lambda item: int(item[1]["landmark_year"]),
    )
    fig, axes = plt.subplots(1, len(ordered), figsize=(7.0 * len(ordered), 4.9), sharex=True)
    axes = np.atleast_1d(axes)
    for ax, (_, result) in zip(axes, ordered):
        estimates = np.array([result["point_estimates"][key] * 1000 for key, _ in keys])
        low = np.array([result["bootstrap_intervals"][key]["ci_low"] * 1000 for key, _ in keys])
        high = np.array([result["bootstrap_intervals"][key]["ci_high"] * 1000 for key, _ in keys])
        y = np.arange(len(keys))
        ax.errorbar(estimates, y, xerr=[estimates - low, high - estimates], fmt="o", capsize=4)
        ax.axvline(0, linewidth=1)
        ax.set_yticks(y)
        ax.set_yticklabels([label for _, label in keys])
        ax.set_title(f"Landmark after year {result['landmark_year']}")
        ax.set_xlabel("Mortality risk difference per 1,000")
        ax.grid(axis="x", alpha=0.25)
    fig.suptitle("Figure 5. Mediation through early MSK rehabilitation")
    fig.tight_layout()
    return _save_figure(fig, output_base)

# END figures.py



# =============================================================================
# BEGIN pretrends.py
# =============================================================================

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

    # Keep only pair-time cells where both matched members are observed. This makes every
    # plotted contrast a literal treated-minus-control difference inside a matched pair.
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

# END pretrends.py



# =============================================================================
# BEGIN mediation.py
# =============================================================================

from pathlib import Path
import json
import logging
import warnings
import re

import numpy as np
import pandas as pd
import polars as pl


log = logging.getLogger(__name__)


def build_landmark_mediation_data(
    config: PipelineConfig,
    panel_path: str | Path,
    matches_path: str | Path,
    treated_path: str | Path,
    controls_path: str | Path,
    landmark_year: int = 1,
    force: bool = False,
) -> dict[str, Path]:
    """Build a temporally ordered landmark mediation sample.

    Rehabilitation is measured during years 1..landmark_year. Mortality begins only after
    the mediator window. The outcome horizon is fixed across all 2012-2018 index cohorts:
    four years after a one-year landmark and three years after a two-year landmark when
    death registration ends in 2023.
    """
    if config.mortality_horizon <= landmark_year:
        raise ValueError("mortality_horizon must exceed landmark_year")
    if config.year_cap is None:
        raise ValueError("A fixed year_cap is required for common-horizon landmark mediation.")
    common_post_horizon = min(
        config.mortality_horizon - landmark_year,
        config.death_registry_end_year - config.year_cap - landmark_year,
    )
    if common_post_horizon < 1:
        raise ValueError(
            f"Landmark {landmark_year} leaves no common post-landmark mortality year."
        )

    cohort_path = config.analysis_dir / f"landmark{landmark_year}_mediation_cohort.parquet"
    outcome_path = config.analysis_dir / f"landmark{landmark_year}_mortality_followup.parquet"
    audit_path = config.diagnostics_dir / f"landmark{landmark_year}_mediation_audit.json"
    if all(path.exists() for path in (cohort_path, outcome_path, audit_path)) and not force:
        return {"cohort": cohort_path, "outcome": outcome_path, "audit": audit_path}

    assignment = _assignment_frame(matches_path)
    baseline = _baseline_frame(treated_path, controls_path, matches_path)
    # NOTE (fixes the lag-3 mediation baseline asymmetry flagged in
    # psm_20260724_guideline.md / psm_20260728_guideline.md, "open questions"): this must
    # match the column-selection pattern used in build_msk_followup and
    # build_mortality_followup, not a hardcoded lag1-only filter. Under lag_depth == 3,
    # _baseline_frame's schema also carries lag2_/lag3_ trend columns (see build_risk_sets'
    # attach_lags), and mediation is supposed to use the FULL available baseline set (see
    # the module note two functions below, "residual treatment balance is not a sufficient
    # rule for mediator-outcome confounding") -- not silently fall back to a weaker,
    # lag1-only adjustment set than the matching design it sits on top of. Under lag_depth
    # == 1 this is a no-op: build_risk_sets never attaches lag2_/lag3_ columns in that case,
    # so baseline.columns simply has nothing extra to match.
    baseline_columns = [
        column for column in baseline.columns
        if re.match(r"lag[123]_", column) and not column.endswith("_source_year")
    ]
    assignment = assignment.join(
        baseline.select(["simple_id", "t0", *baseline_columns]),
        on=["simple_id", "t0"], how="left",
    )
    panel = pl.scan_parquet(panel_path).select([
        "simple_id", "ja", "rtwf_jjjj", "msk_starts_this_year"
    ])
    death_years = panel.group_by("simple_id").agg(
        pl.col("rtwf_jjjj").drop_nulls().max().cast(pl.Int32).alias("death_year")
    )
    joined = assignment.join(panel, on="simple_id", how="inner").with_columns(
        (pl.col("ja") - pl.col("t0")).cast(pl.Int16).alias("relative_year")
    )

    mediator = (
        joined.filter(pl.col("relative_year").is_between(1, landmark_year, closed="both"))
        .group_by(["simple_id", "t0", "match_group", "treated"])
        .agg([
            (pl.col("msk_starts_this_year") > 0).max().cast(pl.Int8).alias("mediator_msk_by_landmark"),
            pl.col("relative_year").n_unique().alias("observed_mediator_years"),
        ])
    )
    landmark_observation = joined.filter(pl.col("relative_year") == landmark_year).select([
        "simple_id", "t0", "match_group", "treated",
        pl.lit(1, dtype=pl.Int8).alias("observed_at_landmark"),
    ])
    cohort = assignment.join(
        mediator, on=["simple_id", "t0", "match_group", "treated"], how="left"
    ).join(
        landmark_observation, on=["simple_id", "t0", "match_group", "treated"], how="left"
    ).join(death_years, on="simple_id", how="left")
    cohort = cohort.with_columns([
        pl.col("mediator_msk_by_landmark").fill_null(0).cast(pl.Int8),
        pl.col("observed_mediator_years").fill_null(0).cast(pl.Int16),
        pl.col("observed_at_landmark").fill_null(0).cast(pl.Int8),
    ])
    cohort = cohort.with_columns(
        (
            (pl.col("observed_at_landmark") == 1)
            & (pl.col("observed_mediator_years") == landmark_year)
            & (pl.col("death_year").is_null() | (pl.col("death_year") > pl.col("t0") + landmark_year))
        ).cast(pl.Int8).alias("eligible_landmark_survivor")
    ).filter(pl.col("eligible_landmark_survivor") == 1)
    # Preserve the matched-set design after landmark conditioning. A pair enters only when
    # both the treated person and matched control survive and complete the mediator window.
    complete_landmark_pairs = cohort.group_by("match_group").agg([
        pl.len().alias("n_people"),
        pl.col("treated").n_unique().alias("n_treatment_arms"),
    ]).filter(
        (pl.col("n_people") == 2) & (pl.col("n_treatment_arms") == 2)
    ).select("match_group")
    cohort = cohort.join(complete_landmark_pairs, on="match_group", how="inner")
    sink_parquet(cohort, cohort_path, config.checkpoint_row_group_size)

    outcomes = cohort.with_columns([
        (pl.col("t0") + landmark_year + common_post_horizon)
        .cast(pl.Int32).alias("planned_outcome_end_year"),
    ]).with_columns([
        pl.min_horizontal(
            pl.col("planned_outcome_end_year"),
            pl.coalesce([pl.col("death_year"), pl.col("planned_outcome_end_year")]),
        ).cast(pl.Int32).alias("outcome_end_year"),
    ]).with_columns(
        pl.int_ranges(
            pl.col("t0") + landmark_year + 1,
            pl.col("outcome_end_year") + 1,
        ).alias("ja")
    ).explode("ja").with_columns([
        (pl.col("ja") - pl.col("t0") - landmark_year)
        .cast(pl.Int8).alias("post_landmark_year"),
        (
            pl.col("death_year").is_not_null()
            & (pl.col("ja") == pl.col("death_year"))
        ).cast(pl.Int8).alias("death_event"),
        pl.lit(common_post_horizon, dtype=pl.Int8)
        .alias("common_post_landmark_horizon"),
        pl.lit(1.0).alias("analysis_weight"),
    ]).select([
        "simple_id", "t0", "match_group", "treated", "mediator_msk_by_landmark",
        *baseline_columns, "death_year", "ja", "post_landmark_year", "death_event",
        "common_post_landmark_horizon", "analysis_weight",
    ]).sort(["match_group", "treated", "post_landmark_year"])
    sink_parquet(outcomes, outcome_path, config.checkpoint_row_group_size)

    audit = {
        "landmark_year": landmark_year,
        "mediator_window": f"t0+1 through t0+{landmark_year}",
        "common_post_landmark_mortality_horizon_years": common_post_horizon,
        "death_measure": "person-level rtwf_jjjj used directly",
        "matched_people_before_landmark_restriction": int(
            assignment.select(pl.len()).pipe(_safe_collect).item()
        ),
        "eligible_landmark_people_in_complete_pairs": int(
            pl.scan_parquet(cohort_path).select(pl.len()).pipe(_safe_collect).item()
        ),
        "eligible_landmark_pairs": int(
            pl.scan_parquet(cohort_path).select(
                pl.col("match_group").n_unique()
            ).pipe(_safe_collect).item()
        ),
        "mediator_events": int(
            pl.scan_parquet(cohort_path).select(
                pl.col("mediator_msk_by_landmark").sum()
            ).pipe(_safe_collect).item()
        ),
        "post_landmark_deaths": int(
            pl.scan_parquet(outcome_path).select(
                pl.col("death_event").sum()
            ).pipe(_safe_collect).item()
        ),
    }
    audit_path.write_text(json.dumps(audit, indent=2), encoding="utf-8")
    return {"cohort": cohort_path, "outcome": outcome_path, "audit": audit_path}


def _mediation_feature_columns(config: PipelineConfig, columns: set[str]) -> FeatureColumns:
    # Mediation uses the full available baseline confounder set, not SMD selection alone:
    # residual treatment balance is not a sufficient rule for mediator-outcome confounding.
    return resolve_features(config, columns)


def _make_baseline_preprocessor(features: FeatureColumns, config: PipelineConfig) -> ColumnTransformer:
    transformers = []
    if features.numeric:
        transformers.append(("numeric", Pipeline([
            ("impute", SimpleImputer(strategy="median", add_indicator=True)),
            ("scale", StandardScaler()),
        ]), features.numeric))
    if features.binary:
        transformers.append(("binary", SimpleImputer(strategy="most_frequent", add_indicator=True), features.binary))
    categorical = list(dict.fromkeys(features.categorical + features.exact))
    if categorical:
        transformers.append(("categorical", Pipeline([
            ("impute", SimpleImputer(strategy="constant", fill_value="__MISSING__")),
            ("onehot", _make_one_hot_encoder(
                sparse_output=False,
                min_frequency=config.minimum_category_frequency,
            )),
        ]), categorical))
    return ColumnTransformer(transformers=transformers, sparse_threshold=0.0)


def _fit_landmark_once(
    cohort: pd.DataFrame,
    outcome: pd.DataFrame,
    config: PipelineConfig,
) -> dict[str, float]:
    cohort = cohort.copy()
    outcome = outcome.copy()
    key = ["simple_id", "t0", "match_group"]
    baseline_columns = [column for column in cohort.columns if re.match(r"lag[123]_", column)]
    available = set(baseline_columns)
    features = _mediation_feature_columns(config, available)
    model_columns = list(dict.fromkeys(features.model + features.exact))
    preprocessor = _make_baseline_preprocessor(features, config)
    baseline_matrix = preprocessor.fit_transform(cohort[model_columns]) if model_columns else np.empty((len(cohort), 0))

    treated = cohort["treated"].to_numpy(float)[:, None]
    mediator_x = np.column_stack([np.ones(len(cohort)), treated, baseline_matrix])
    mediator_y = cohort["mediator_msk_by_landmark"].to_numpy(np.int8)
    mediator_model = _unpenalized_logistic_regression(mediator_x, mediator_y)

    prepared = cohort[key + model_columns].drop_duplicates(key)
    outcome = outcome.drop(columns=[c for c in model_columns if c in outcome.columns], errors="ignore").merge(
        prepared, on=key, how="left", validate="many_to_one"
    )
    if "common_post_landmark_horizon" in outcome.columns:
        horizon_values = pd.to_numeric(
            outcome["common_post_landmark_horizon"], errors="raise"
        ).dropna().astype(int).unique()
        if len(horizon_values) != 1:
            raise ValueError(
                "Landmark outcome data must contain one common post-landmark horizon."
            )
        common_horizon = int(horizon_values[0])
    else:
        # Backward-compatible fallback for previously generated test files.
        common_horizon = int(outcome["post_landmark_year"].max())
    years = list(range(1, common_horizon + 1))

    outcome_baseline = preprocessor.transform(outcome[model_columns]) if model_columns else np.empty((len(outcome), 0))
    year_dummies = pd.get_dummies(
        pd.Categorical(outcome["post_landmark_year"], categories=years),
        prefix="post_landmark_year", drop_first=True, dtype=float,
    ).to_numpy(float)
    a = outcome["treated"].to_numpy(float)
    m = outcome["mediator_msk_by_landmark"].to_numpy(float)
    outcome_x = np.column_stack([
        np.ones(len(outcome)), a, m, a * m, year_dummies, outcome_baseline,
    ])
    outcome_model = _unpenalized_logistic_regression(
        outcome_x, outcome["death_event"].to_numpy(np.int8)
    )

    base_people = cohort.drop_duplicates(key).reset_index(drop=True)
    base_matrix = preprocessor.transform(base_people[model_columns]) if model_columns else np.empty((len(base_people), 0))
    mediator_probabilities = {}
    for treatment in (0, 1):
        x = np.column_stack([np.ones(len(base_people)), np.full(len(base_people), treatment), base_matrix])
        mediator_probabilities[treatment] = np.clip(mediator_model.predict_proba(x)[:, 1], 0.0, 1.0)

    # Fit the mortality model on the factual at-risk rows, but standardize every eligible
    # landmark survivor over the same complete post-landmark year grid. Counterfactual
    # predictions must not inherit truncation at a person's factual death year.
    n_people = len(base_people)
    prediction_year = np.tile(np.asarray(years, dtype=int), n_people)
    prediction_year_dummies = pd.get_dummies(
        pd.Categorical(prediction_year, categories=years),
        prefix="post_landmark_year", drop_first=True, dtype=float,
    ).to_numpy(float)
    prediction_baseline = (
        np.repeat(base_matrix, common_horizon, axis=0)
        if model_columns else np.empty((n_people * common_horizon, 0))
    )

    risk_by_scenario: dict[tuple[int, int], np.ndarray] = {}
    for treatment in (0, 1):
        for mediator in (0, 1):
            aa = np.full(n_people * common_horizon, treatment, dtype=float)
            mm = np.full(n_people * common_horizon, mediator, dtype=float)
            x = np.column_stack([
                np.ones(n_people * common_horizon), aa, mm, aa * mm,
                prediction_year_dummies, prediction_baseline,
            ])
            hazard = np.clip(outcome_model.predict_proba(x)[:, 1], 1e-9, 1 - 1e-9)
            hazard = hazard.reshape(n_people, common_horizon)
            risk_by_scenario[(treatment, mediator)] = 1.0 - np.prod(1.0 - hazard, axis=1)

    def standardized_risk(treatment: int, mediator_source_treatment: int) -> float:
        probability = mediator_probabilities[mediator_source_treatment]
        return float(np.mean(
            probability * risk_by_scenario[(treatment, 1)]
            + (1.0 - probability) * risk_by_scenario[(treatment, 0)]
        ))

    y_0_m0 = standardized_risk(0, 0)
    y_1_m0 = standardized_risk(1, 0)
    y_1_m1 = standardized_risk(1, 1)
    return {
        "risk_y0_m0": y_0_m0,
        "risk_y1_m0": y_1_m0,
        "risk_y1_m1": y_1_m1,
        "total_effect_risk_difference": y_1_m1 - y_0_m0,
        "natural_direct_effect_risk_difference": y_1_m0 - y_0_m0,
        "natural_indirect_effect_risk_difference": y_1_m1 - y_1_m0,
        "estimator": "temporally ordered landmark mediation; unpenalized sklearn logistic models; matched-set bootstrap",
        "counterfactual_prediction_grid": (
            f"all eligible landmark survivors predicted over the full common {common_horizon}-year post-landmark grid"
        ),
    }

def fit_landmark_mediation(
    config: PipelineConfig,
    cohort_path: str | Path,
    outcome_path: str | Path,
    landmark_year: int = 1,
    n_bootstrap: int = 100,
) -> dict:
    cohort = pl.read_parquet(cohort_path).to_pandas()
    outcome = pl.read_parquet(outcome_path).to_pandas()
    point = _fit_landmark_once(cohort, outcome, config)

    rng = np.random.default_rng(config.seed)
    groups = np.array(sorted(cohort["match_group"].unique()))
    cohort_groups = cohort["match_group"].to_numpy()
    outcome_groups = outcome["match_group"].to_numpy()
    cohort_group_indices = {
        group: np.flatnonzero(cohort_groups == group) for group in groups
    }
    outcome_group_indices = {
        group: np.flatnonzero(outcome_groups == group) for group in groups
    }
    missing_outcome_groups = [
        int(group) for group in groups if len(outcome_group_indices[group]) == 0
    ]
    if missing_outcome_groups:
        raise ValueError(
            "Some landmark cohort groups have no outcome rows: "
            f"{missing_outcome_groups[:10]}"
        )

    bootstrap_rows: list[dict] = []
    progress_step = max(1, n_bootstrap // 10)
    for replicate in range(n_bootstrap):
        sampled = rng.choice(groups, size=len(groups), replace=True)
        cohort_indices = np.concatenate([cohort_group_indices[group] for group in sampled])
        outcome_indices = np.concatenate([outcome_group_indices[group] for group in sampled])
        cohort_boot = cohort.iloc[cohort_indices].copy().reset_index(drop=True)
        outcome_boot = outcome.iloc[outcome_indices].copy().reset_index(drop=True)

        # A group sampled twice must become two distinct bootstrap clusters. Construct the
        # replacement identifiers vectorially rather than repeatedly scanning pandas tables.
        new_groups = np.arange(
            replicate * (len(groups) + 1) + 1,
            replicate * (len(groups) + 1) + len(groups) + 1,
            dtype=np.int64,
        )
        cohort_boot["match_group"] = np.concatenate([
            np.full(len(cohort_group_indices[group]), new_group, dtype=np.int64)
            for group, new_group in zip(sampled, new_groups)
        ])
        outcome_boot["match_group"] = np.concatenate([
            np.full(len(outcome_group_indices[group]), new_group, dtype=np.int64)
            for group, new_group in zip(sampled, new_groups)
        ])
        try:
            with warnings.catch_warnings():
                warnings.simplefilter("ignore")
                estimate = _fit_landmark_once(
                    cohort_boot,
                    outcome_boot,
                    config,
                )
            bootstrap_rows.append({"replicate": replicate, **estimate})
        except Exception as exc:  # explicit record; no silent discarding
            bootstrap_rows.append({"replicate": replicate, "error": f"{type(exc).__name__}: {exc}"})
        if (replicate + 1) % progress_step == 0 or replicate + 1 == n_bootstrap:
            n_success = sum("error" not in row for row in bootstrap_rows)
            log.info(
                "Landmark %s mediation bootstrap: %s/%s replications completed (%s successful)",
                landmark_year, replicate + 1, n_bootstrap, n_success,
            )

    successful = pd.DataFrame([row for row in bootstrap_rows if "error" not in row])
    if len(successful) < max(20, n_bootstrap // 2):
        raise RuntimeError(
            f"Only {len(successful)}/{n_bootstrap} landmark mediation bootstrap fits succeeded."
        )
    intervals = {}
    for key in (
        "total_effect_risk_difference",
        "natural_direct_effect_risk_difference",
        "natural_indirect_effect_risk_difference",
    ):
        intervals[key] = {
            "ci_low": float(successful[key].quantile(0.025)),
            "ci_high": float(successful[key].quantile(0.975)),
        }
    result = {
        "landmark_year": landmark_year,
        "target_population": (
            "complete matched pairs in which both people are alive and fully observed "
            "throughout the mediator window, with a common post-landmark mortality horizon"
        ),
        "identification_warning": (
            "Natural direct and indirect effects additionally require no unmeasured "
            "mediator-outcome confounding and no treatment-induced mediator-outcome confounder."
        ),
        "point_estimates": point,
        "bootstrap_intervals": intervals,
        "successful_bootstrap_replicates": int(len(successful)),
        "requested_bootstrap_replicates": int(n_bootstrap),
    }
    output = config.analysis_dir / f"landmark{landmark_year}_mediation_results.json"
    output.write_text(json.dumps(result, indent=2), encoding="utf-8")
    pl.DataFrame(bootstrap_rows, infer_schema_length=None).write_csv(
        config.analysis_dir / f"landmark{landmark_year}_mediation_bootstrap.csv"
    )
    return result

# END mediation.py



# =============================================================================
# BEGIN pipeline.py
# =============================================================================

from pathlib import Path
import json
import logging


log = logging.getLogger(__name__)


def run_main_pipeline(
    config: PipelineConfig,
    force: bool = False,
    reporting: PaperReportingConfig | None = None,
) -> dict:
    """Run one first-marriage-divorce matched-cohort specification.

    In both canonical and playdata profiles, treatment is validated by equality between
    ``marriage_start`` and ``first_marriage_start``. Assignment stays fixed after t0.
    Later marital transitions are neither required nor used for censoring.
    """
    config.validate()
    reporting = reporting or PaperReportingConfig(**PAPER_REPORTING_CONFIG)
    reporting.validate()
    initialize_run(config, force=force)
    config.write(config.run_dir / "resolved_config.json")
    reporting.write(config.run_dir / "resolved_paper_reporting_config.json")

    panel = build_analysis_panel(config, force=force)
    coverage = build_panel_coverage_diagnostics(config, panel, force=force)
    risksets = build_risk_sets(config, panel, force=force)
    matching = fit_and_match(config, risksets["treated"], risksets["controls"], force=force)
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

    # Plain curve files remain available for table construction. The CI tables below use
    # matched-set bootstrap intervals and are the direct inputs for Figures 2 and 3.
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
    if config.run_landmark_mediation:
        for landmark_year in sorted(config.landmark_years):
            mediation_data = build_landmark_mediation_data(
                config, panel, matching["matches"], risksets["treated"], risksets["controls"],
                landmark_year=landmark_year, force=force,
            )
            result_for_landmark = fit_landmark_mediation(
                config, mediation_data["cohort"], mediation_data["outcome"],
                landmark_year=landmark_year,
                n_bootstrap=config.mediation_bootstrap_replicates,
            )
            result_for_landmark["data_paths"] = {
                key: str(value) for key, value in mediation_data.items()
            }
            mediation[f"landmark_{landmark_year}"] = result_for_landmark

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
            figures["figure_5_mediation_landmarks_1_and_2"] = plot_mediation_landmark_comparison(
                mediation, config.figures_dir / "figure_5_landmark_mediation_comparison",
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
    """Run matching and outcomes for a secondary lag/window specification.

    Secondary specifications receive separate run directories, preventing lag-1 files
    from different cohort windows from overwriting one another. The canonical analysis
    panel is referenced rather than rebuilt, so source construction remains identical.
    """
    panel = Path(panel)
    if not panel.exists():
        raise FileNotFoundError(panel)
    reporting = reporting or PaperReportingConfig(**PAPER_REPORTING_CONFIG)
    reporting.validate()

    if config.total_rebuild:
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

    risksets = build_risk_sets(config, panel, force=True)
    matching = fit_and_match(
        config, risksets["treated"], risksets["controls"], force=True
    )
    balance = build_balance_tables(
        config,
        risksets["treated"],
        risksets["controls"],
        matching["matches"],
        force=True,
    )
    marital = build_marital_status_tables(
        config,
        panel,
        risksets["treated"],
        risksets["controls"],
        matching["matches"],
        force=True,
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
        force=True,
    )
    event_panel = build_pair_event_study_panel(
        config,
        panel,
        matching["matches"],
        pre_years=3,
        post_years=config.followup_years,
        force=True,
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
        force=True,
    )
    mortality_followup = build_mortality_followup(
        config,
        panel,
        matching["matches"],
        risksets["treated"],
        risksets["controls"],
        force=True,
    )
    msk_dropout_sensitivity: dict[str, object] = {}
    if config.run_msk_dropout_sensitivity:
        sensitivity_data = build_msk_pair_censored_sensitivity(
            config, msk_followup, force=True
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
    # Build the same descriptive curve tables used by the main specification so the
    # secondary lag/window runs exercise the complete outcome and plotting pipeline.
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
    if config.run_landmark_mediation:
        for landmark_year in sorted(config.landmark_years):
            mediation_data = build_landmark_mediation_data(
                config,
                panel,
                matching["matches"],
                risksets["treated"],
                risksets["controls"],
                landmark_year=landmark_year,
                force=True,
            )
            result_for_landmark = fit_landmark_mediation(
                config,
                mediation_data["cohort"],
                mediation_data["outcome"],
                landmark_year=landmark_year,
                n_bootstrap=config.mediation_bootstrap_replicates,
            )
            result_for_landmark["data_paths"] = {
                key: str(value) for key, value in mediation_data.items()
            }
            mediation[f"landmark_{landmark_year}"] = result_for_landmark

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
            figures["figure_5_mediation_landmarks_1_and_2"] = (
                plot_mediation_landmark_comparison(
                    mediation,
                    config.figures_dir / "figure_5_landmark_mediation_comparison",
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
    """Run the main lag-1 estimate and a common-window lag-depth comparison.

    The three outputs are:
    - lag 1, full 2012–2018 treatment window;
    - lag 1, common 2014–2018 treatment window; and
    - lag 3, common 2014–2018 treatment window.

    Comparing the latter two isolates the added history requirement from the loss of the
    2012–2013 treatment cohorts. All other matching and outcome settings are held fixed.
    """
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
        run_landmark_mediation=True,
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
        run_landmark_mediation=True,
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


def run_landmark_mediation(
    config: PipelineConfig,
    landmark_year: int = 1,
    n_bootstrap: int = 100,
    force: bool = False,
) -> dict:
    config.validate()
    initialize_run(config, force=False)
    panel = config.panels_dir / "analysis_panel.parquet"
    treated = config.analysis_dir / f"riskset_treated_lag{config.lag_depth}.parquet"
    controls = config.analysis_dir / f"riskset_controls_{config.control_pool}_lag{config.lag_depth}.parquet"
    matches = config.analysis_dir / f"matched_pairs_{config.control_pool}_lag{config.lag_depth}.parquet"
    for path in (panel, treated, controls, matches):
        if not path.exists():
            raise FileNotFoundError(f"Run the main pipeline first; missing {path}")
    data = build_landmark_mediation_data(
        config, panel, matches, treated, controls, landmark_year=landmark_year, force=force
    )
    return fit_landmark_mediation(
        config, data["cohort"], data["outcome"],
        landmark_year=landmark_year, n_bootstrap=n_bootstrap,
    )

# END pipeline.py



# =============================================================================
# STANDALONE COMMAND-LINE ENTRY POINT AND INTERNAL SMOKE TEST
# =============================================================================

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
        choices=["main", "landmark-mediation"],
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
    parser.add_argument("--landmark-year", type=int, default=DEFAULT_LANDMARK_YEAR)
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
    """Small panel covering the important filtering and modeling edge cases."""
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
                msk_start, msk_code, msk_duration, incapacity = date(year, 4, 1), 20, 30.0 + person % 10, "3-6"
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
    """Run an end-to-end test without needing the confidential administrative data."""
    with tempfile.TemporaryDirectory(prefix="divorce_pipeline_test_") as temp:
        temp_path = Path(temp)
        raw = temp_path / "raw"
        raw.mkdir()
        data = pl.DataFrame(_synthetic_rows(), infer_schema_length=None)
        # Exercise the current playdata branch: retain first_marriage_start/end and
        # remove only entgelt, which is the verified unavailable source variable.
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
            mediation_bootstrap_replicates=30,
            landmark_years=[1, 2],
            death_registry_end_year=2023,
            generate_figures=True,
            run_landmark_mediation=True,
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
        # The release-facing table may legitimately withhold every small synthetic cell.
        # Exact values are checked only in the explicitly internal diagnostic.
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

        # Deterministic checks of the RDC small-cell pooling rules on fabricated rows.
        # Rule 1: two below-threshold codes pool; people are recomputed exactly, not
        # summed per code.
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
        # Rule 2: a single below-threshold code never becomes its own bucket; the
        # smallest retained code folds in (complementary pooling).
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
        # Rule 3: a pooled bucket still below the threshold withholds its counts.
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
        # Rule 4: threshold 0 reproduces the unpooled table.
        unpooled = _pool_small_code_cells(tiny, 0, key_columns=[], include_year_span=False)
        assert PAPER_POOLED_CODE_LABEL not in set(
            unpooled.get_column("rehabilitation_diagnosis_code").to_list()
        )
        assert unpooled.height == 3

        assert np.isfinite(results["models"]["msk_unadjusted"]["odds_ratio"])
        assert np.isfinite(results["models"]["mortality_unadjusted"]["odds_ratio"])

        assert {"landmark_1", "landmark_2"}.issubset(results["mediation"])
        for result_for_landmark in results["mediation"].values():
            assert np.isfinite(
                result_for_landmark["point_estimates"]["total_effect_risk_difference"]
            )

        # First-event risk sets must never contain a person-year after the event row.
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

        return {
            "status": "PASS",
            "synthetic_people": 240,
            "synthetic_person_years": int(data.height),
            "matched_pairs": int(matches.height),
            "main_models_finite": True,
            "sex_heterogeneity_outputs_created": True,
            "landmark_1_and_2_mediation_finite": True,
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

    # A total rebuild is the default and is intentionally performed BEFORE logging is
    # configured, so Windows never has to delete an open log file. Optional modes first
    # rebuild the canonical main pipeline in the same process and then add their outputs.
    total_rebuild = bool(config.total_rebuild and not args.reuse_existing)
    if total_rebuild:
        clear_run_directory(config)
    _configure_logging(config)
    effective_force = True if total_rebuild else bool(args.force)
    log.info(
        "Run policy: %s",
        "TOTAL REBUILD (no prior generated files reused)"
        if total_rebuild else
        "signature-protected checkpoint reuse",
    )
    capabilities = _polars_runtime_capabilities()
    log.info(
        "Runtime: Python=%s; Polars=%s; collect=%s; collect_batches=%s; fallback=lazy-slice",
        sys.version.split()[0],
        capabilities["polars_version"],
        capabilities["streaming_collect_mode"],
        capabilities["collect_batches_available"],
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
                config, run_lag1_vs_lag3=False, run_landmark_mediation=False,
                generate_figures=False,
            )
            run_main_pipeline(base_config, force=True, reporting=reporting)
        result = run_landmark_mediation(
            config,
            landmark_year=args.landmark_year,
            n_bootstrap=args.bootstrap,
            force=effective_force,
        )
    print(json.dumps(result, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(standalone_main())
