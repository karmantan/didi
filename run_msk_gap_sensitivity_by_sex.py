from __future__ import annotations

import argparse
import csv
from dataclasses import replace
from datetime import datetime, timezone
import gc
import hashlib
import importlib.util
import json
import logging
import math
import os
from pathlib import Path
import sys
import traceback
import uuid


ROOT = Path(r"D:\gastwissenschaftler\gastw_20\DIDI\XPrivat\Tan\processed_data\pipeline_runs")
TAG = "20pct_firstmarriage_lag1_lag3_notyetdivorced_260929_extra_vars"
DEFAULT_RUN_ROOT = ROOT / (TAG + "__corrected_261027d")
SPECIFICATIONS = ("lag3_common", "lag1_common", "main")
SEXES = (("1", "Men"), ("2", "Women"))
LOG = logging.getLogger("msk_gap_by_sex")
FIELDS = ["simple_id", "t0", "ja", "match_group", "treated", "follow_year",
          "lag1_ge_cat", "analysis_weight", "annual_panel_observed", "msk_event"]


def arguments(argv=None):
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    script = Path(globals().get("__file__", "run_msk_gap_sensitivity_by_sex.py"))
    parser.add_argument("--code", type=Path, default=script.with_name("psm_261027.py"))
    parser.add_argument("--run-root", type=Path, default=DEFAULT_RUN_ROOT)
    parser.add_argument("--spec", choices=("all",) + SPECIFICATIONS, default="all")
    parser.add_argument("--output", type=Path, help="Separate output parent; a new dated subfolder is always created")
    parser.add_argument("--threads", type=int, default=1)
    args = parser.parse_args(argv)
    if args.threads < 1:
        parser.error("--threads must be positive")
    return args


def sha256(path):
    digest = hashlib.sha256()
    with Path(path).open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def stamp(path):
    path = Path(path).resolve()
    info = path.stat()
    return {"path": str(path), "size_bytes": info.st_size, "mtime_ns": info.st_mtime_ns}


def check_stamps(before):
    for item in before:
        if stamp(item["path"]) != item:
            raise RuntimeError("Source changed during this analysis: " + item["path"])


def write_json(path, value):
    path = Path(path)
    temporary = path.with_suffix(path.suffix + ".writing")
    temporary.write_text(json.dumps(value, indent=2, allow_nan=False), encoding="utf-8")
    temporary.replace(path)


def write_csv(path, rows):
    if rows:
        with Path(path).open("w", newline="", encoding="utf-8-sig") as handle:
            writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
            writer.writeheader()
            writer.writerows(rows)


def load_source(path):
    path = Path(path).resolve()
    if not path.is_file():
        raise FileNotFoundError("Put this script beside psm_261027.py, or set --code: " + str(path))
    sys.dont_write_bytecode = True
    name = "_didi_msk_gap_source"
    spec = importlib.util.spec_from_file_location(name, str(path))
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    for required in ("PipelineConfig", "build_msk_pair_censored_sensitivity", "_build_design_matrix",
                     "_unpenalized_logistic_regression", "_cluster_robust_logit_covariance"):
        if not hasattr(module, required):
            raise RuntimeError("Pipeline is missing required function: " + required)
    if module.SEX_LABELS != {"1": "Male", "2": "Female"}:
        raise RuntimeError("Unexpected sex coding; inspect the pipeline before running")
    return module


def validate_followup(module, follow, matches, config):
    """Validate assignments without deleting people missing from original follow-up."""
    pl = module.pl
    if follow.is_empty() or matches.is_empty():
        raise RuntimeError("Saved follow-up or matching is empty")
    if any(follow.null_count().row(0)) or any(matches.null_count().row(0)):
        raise RuntimeError("Missing assignment, event, sex, observation indicator or weight; no rows deleted")
    if matches["match_group"].n_unique() != matches.height or matches.filter(pl.col("t_id") == pl.col("c_id")).height:
        raise RuntimeError("Invalid or duplicated matched-pair assignments")
    for name in ("treated", "annual_panel_observed", "msk_event"):
        if not set(follow[name].unique().to_list()) <= {0, 1}:
            raise RuntimeError("Nonbinary follow-up field: " + name)
    if set(follow["treated"].unique().to_list()) != {0, 1}:
        raise RuntimeError("Both treatment arms are required")
    if set(follow["lag1_ge_cat"].cast(pl.Utf8).unique().to_list()) != {"1", "2"}:
        raise RuntimeError("Expected both sexes coded 1 and 2; no alternative mapping inferred")
    if follow.filter(~pl.col("analysis_weight").is_finite() | (pl.col("analysis_weight") <= 0)).height:
        raise RuntimeError("Saved analysis weights must be finite and positive")
    if follow.filter((pl.col("follow_year") < 1) | (pl.col("follow_year") > config.followup_years)
                     | (pl.col("ja") != pl.col("t0") + pl.col("follow_year"))
                     | (pl.col("t0") < config.year_start) | (pl.col("t0") > config.year_cap)
                     | (pl.col("ja") > config.death_registry_end_year)).height:
        raise RuntimeError("Invalid outcome-year indexing or follow-up horizon")
    keys = ["match_group", "treated", "follow_year"]
    if follow.select(keys).unique().height != follow.height:
        raise RuntimeError("Duplicated matched-arm-year follow-up rows")
    sex = follow.group_by("match_group").agg(pl.col("lag1_ge_cat").n_unique().alias("n_sexes"))
    if sex.filter(pl.col("n_sexes") != 1).height:
        raise RuntimeError("A saved matched pair contains different sexes")
    if follow.group_by(["match_group", "treated"]).agg(pl.col("msk_event").sum().alias("n_events")).filter(pl.col("n_events") > 1).height:
        raise RuntimeError("More than one first MSK event in a matched assignment")
    mapping = pl.concat([
        matches.select(["match_group", "t0", pl.col("t_id").alias("expected_id"), pl.lit(1).alias("treated")]),
        matches.select(["match_group", "t0", pl.col("c_id").alias("expected_id"), pl.lit(0).alias("treated")]),
    ]).with_columns(pl.col("treated").cast(follow.schema["treated"]))
    assignments = follow.select(["match_group", "t0", "treated", "simple_id"]).unique()
    checked = assignments.join(mapping, on=["match_group", "t0", "treated"], how="left")
    if checked.filter(pl.col("expected_id").is_null() | (pl.col("simple_id") != pl.col("expected_id"))).height:
        raise RuntimeError("Follow-up assignment disagrees with the saved matched pairs")
    missing_slots = mapping.join(assignments, on=["match_group", "t0", "treated"], how="anti")
    # Some saved assignments never entered the original follow-up. Record them;
    # adding them here would silently change the original risk sets.
    return {"saved_matched_pairs": matches.height, "original_followup_pairs": follow["match_group"].n_unique(),
            "saved_assignments_without_original_followup": missing_slots.height,
            "missing_control_assignments": missing_slots.filter(pl.col("treated") == 0).height,
            "missing_divorced_assignments": missing_slots.filter(pl.col("treated") == 1).height,
            "observed_cohorts": sorted(follow["t0"].unique().to_list()),
            "observed_outcome_years": sorted(follow["ja"].unique().to_list())}


def fit_model(module, config, follow, sex_code):
    """Use the canonical design, solver and matched-pair sandwich, with no fallback."""
    import numpy as np
    from scipy import stats

    data = follow.filter(module.pl.col("lag1_ge_cat").cast(module.pl.Utf8) == sex_code).to_pandas().reset_index(drop=True)
    if data.empty or set(data["treated"].unique()) != {0, 1}:
        raise RuntimeError("Both treatment arms are required after censoring for sex " + sex_code)
    y, design, transformations, audit = module._build_design_matrix(data, config, [], "msk_event")
    if set(np.unique(y)) != {0, 1}:
        raise RuntimeError("Both MSK events and nonevents are required for estimation")
    x = design.to_numpy(float)
    weights = data["analysis_weight"].to_numpy(float)
    fitted = module._unpenalized_logistic_regression(x, y, weights, max_iter=config.outcome_logit_max_iter)
    if getattr(fitted, "_pipeline_unpenalized_approximation", True) or not getattr(fitted, "_pipeline_converged", False):
        raise RuntimeError("Converged unpenalized model unavailable; a penalized or unconverged substitute was rejected")
    index = design.columns.get_loc("treated")
    beta = float(fitted.coef_[0, index])
    if not math.isfinite(beta) or abs(beta) > 10:
        raise RuntimeError("Treatment coefficient suggests separation; no clipped estimate reported")
    probabilities = np.clip(fitted.predict_proba(x)[:, 1], 1e-9, 1 - 1e-9)
    covariance = module._cluster_robust_logit_covariance(x, y, probabilities, data["match_group"].to_numpy(), weights)
    variance = float(covariance[index, index])
    if not math.isfinite(variance) or variance <= 0:
        raise RuntimeError("Invalid pair-clustered standard error; no inference fallback used")
    se = math.sqrt(variance)
    counts = {}
    for arm, label in ((0, "controls"), (1, "divorced")):
        at = data.loc[data["treated"] == arm]
        counts["people_" + label] = int(at[["match_group", "treated"]].drop_duplicates().shape[0])
        counts["events_" + label] = int(at["msk_event"].sum())
    return {"status": "complete", "adjustment_mode": "unadjusted", "sex_code": sex_code,
            "model": "divorce indicator + follow-up-year dummies",
            "inference": "canonical matched-pair cluster-robust sandwich; no bootstrap",
            "n_matched_sets": int(data["match_group"].nunique()), "n_person_years": len(data),
            "events": int(y.sum()), **counts,
            "odds_ratio": math.exp(beta), "ci_low": math.exp(beta - 1.96 * se),
            "ci_high": math.exp(beta + 1.96 * se), "p_value": float(2 * stats.norm.sf(abs(beta / se))),
            "log_odds": beta, "standard_error": se, "design_columns": design.columns.tolist(),
            "design_audit": audit, "transformations": transformations,
            "fit_method": fitted._pipeline_fit_method, "iterations": int(fitted.n_iter_.max())}


def export_rows(rows):
    exported = []
    for row in rows:
        cells = [row["people_controls"], row["people_divorced"], row["events_controls"], row["events_divorced"],
                 row["people_controls"] - row["events_controls"], row["people_divorced"] - row["events_divorced"]]
        small = min(cells) < 20
        item = dict(row)
        if small:
            for key in item:
                if key not in {"specification", "sex", "followup_rule", "status"}:
                    item[key] = "withheld"
            item["status"] = "withheld_small_cell"
        exported.append(item)
    return exported


def run_spec(module, root, output, name):
    pl = module.pl
    source = root / name
    config_path = source / "resolved_config.json"
    settings = json.loads(config_path.read_text(encoding="utf-8"))
    config = module.PipelineConfig(**settings)
    expected_lag = 3 if name == "lag3_common" else 1
    expected_start = 2012 if name == "main" else 2014
    if (config.sample_tag != name or config.lag_depth != expected_lag
            or config.year_start != expected_start or config.year_cap != 2018
            or config.control_pool != "not_yet_divorced" or config.followup_years != 5):
        raise RuntimeError("Resolved configuration does not describe the requested corrected-run specification: " + name)
    token = "%s_lag%d" % (config.control_pool, config.lag_depth)
    followup_path = source / "analysis" / ("msk_followup_" + token + "_fixed_assignment.parquet")
    matches_path = source / "analysis" / ("matched_pairs_" + token + ".parquet")
    before = [stamp(path) for path in (config_path, followup_path, matches_path)]
    missing = set(FIELDS) - set(pl.read_parquet_schema(followup_path))
    if missing:
        raise KeyError("Saved follow-up lacks required fields: " + str(sorted(missing)))
    follow = pl.read_parquet(followup_path, columns=FIELDS)
    matches = pl.read_parquet(matches_path, columns=["match_group", "t0", "t_id", "c_id"])
    validation = validate_followup(module, follow, matches, config)
    destination = output / name
    destination.mkdir()
    manifest = {"status": "running", "source_config": settings, "source_files": before,
                "source_sha256": {str(p): sha256(p) for p in (config_path, matches_path, followup_path)},
                "validation": validation, "matching_repeated": False,
                "explicit_reuse_reason": "additional sex-specific sensitivity on the identical saved matched assignments",
                "models": {}}
    write_json(destination / "manifest_INTERNAL.json", manifest)
    working = replace(config, output_dir=str(output), sample_tag=name)
    working.analysis_dir.mkdir()
    working.diagnostics_dir.mkdir()
    compact = working.analysis_dir / "ordinary_followup_INTERNAL.parquet"
    follow.write_parquet(compact)
    # Invoke the same censoring function used by psm_261027.py on a compact
    # copy. Censor at the PAIR level before separating men and women.
    paths = module.build_msk_pair_censored_sensitivity(working, compact, force=True)
    censored = pl.read_parquet(paths["followup"])
    for key in ("followup", "audit"):
        path = Path(paths[key])
        internal = path.with_name(path.stem + "_INTERNAL" + path.suffix)
        path.rename(internal)
        paths[key] = internal
    check_stamps(before)
    gap_pairs = follow.filter(pl.col("annual_panel_observed") == 0).select("match_group").unique()
    rows, diagnostics = [], []
    try:
        for code, sex in SEXES:
            original_sex = follow.filter(pl.col("lag1_ge_cat").cast(pl.Utf8) == code)
            censored_sex = censored.filter(pl.col("lag1_ge_cat").cast(pl.Utf8) == code)
            diagnostics.append({"sex": sex, "original_pairs": original_sex["match_group"].n_unique(),
                "pairs_with_a_record_gap": original_sex.select("match_group").unique().join(gap_pairs, on="match_group").height,
                "retained_pairs": censored_sex["match_group"].n_unique(),
                "original_person_years": original_sex.height, "retained_person_years": censored_sex.height,
                "original_msk_events": int(original_sex["msk_event"].sum()),
                "retained_msk_events": int(censored_sex["msk_event"].sum())})
            for rule, data in (("ordinary_followup", original_sex), ("pair_censored_first_gap", censored_sex)):
                LOG.info("%s / %s / %s: fitting %s person-years", name, sex, rule, data.height)
                result = fit_model(module, working, data, code)
                check_stamps(before)
                write_json(destination / (sex.lower() + "_" + rule + "_INTERNAL.json"), result)
                manifest["models"][sex + "/" + rule] = {"status": "complete"}
                write_json(destination / "manifest_INTERNAL.json", manifest)
                rows.append({"specification": name, "sex": sex, "followup_rule": rule,
                             "status": "estimated", **{k: result[k] for k in (
                                 "odds_ratio", "ci_low", "ci_high", "p_value", "n_matched_sets",
                                 "n_person_years", "events", "people_controls", "people_divorced",
                                 "events_controls", "events_divorced")}})
                LOG.info("%s / %s / %s: OR %.4f [%.4f, %.4f]", name, sex, rule,
                         result["odds_ratio"], result["ci_low"], result["ci_high"])
                gc.collect()
        check_stamps(before)
        write_csv(destination / "gap_counts_by_sex_INTERNAL.csv", diagnostics)
        write_csv(destination / "model_comparison_INTERNAL.csv", rows)
        manifest.update(status="complete", censoring_outputs={k: str(v) for k, v in paths.items()})
        write_json(destination / "manifest_INTERNAL.json", manifest)
        return rows
    except Exception as exc:
        manifest.update(status="failed", error=str(exc), traceback=traceback.format_exc())
        write_json(destination / "manifest_INTERNAL.json", manifest)
        raise


def main(argv=None):
    args = arguments(argv)
    for name in ("POLARS_MAX_THREADS", "OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
                 "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
        os.environ[name] = str(args.threads)
    module = load_source(args.code)
    root = args.run_root.resolve()
    if not root.is_dir():
        raise FileNotFoundError("Corrected workflow not found; set --run-root to the actual destination: " + str(root))
    parent = (args.output if args.output is not None else root.with_name(root.name + "__msk_gap_by_sex")).resolve()
    if parent == root or root in parent.parents or parent in root.parents:
        raise ValueError("Use a separate output directory outside the source workflow")
    output = parent / (datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ") + "_" + uuid.uuid4().hex[:6])
    output.mkdir(parents=True)
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(message)s", handlers=[
        logging.StreamHandler(sys.stdout), logging.FileHandler(output / "msk_gap_by_sex_INTERNAL.log", encoding="utf-8")])
    import numpy as np
    import pandas as pd
    import scipy
    import sklearn

    script = globals().get("__file__")
    manifest = {"status": "running", "source_root": str(root), "output": str(output),
                "script_sha256": sha256(script) if script else None,
                "pipeline_code": str(args.code.resolve()), "pipeline_sha256": sha256(args.code),
                "threads": args.threads, "python": sys.version, "polars": module.pl.__version__,
                "numpy": np.__version__, "pandas": pd.__version__, "scipy": scipy.__version__,
                "sklearn": sklearn.__version__, "requested_specifications": list(SPECIFICATIONS if args.spec == "all" else (args.spec,)),
                "source_access": "read-only", "results": {}}
    manifest_path = output / "run_manifest_INTERNAL.json"
    write_json(manifest_path, manifest)
    LOG.info("Reading corrected workflow: %s", root)
    LOG.info("Results: %s", output)
    all_rows = []
    for name in manifest["requested_specifications"]:
        try:
            rows = run_spec(module, root, output, name)
            all_rows.extend(rows)
            manifest["results"][name] = {"status": "complete"}
        except Exception as exc:
            manifest["results"][name] = {"status": "failed", "error": str(exc), "traceback": traceback.format_exc()}
            LOG.error("%s FAILED: %s", name, exc)
        write_json(manifest_path, manifest)
        gc.collect()
    write_csv(output / "msk_gap_by_sex_INTERNAL.csv", all_rows)
    write_csv(output / "msk_gap_by_sex_EXPORT.csv", export_rows(all_rows))
    success = all(item["status"] == "complete" for item in manifest["results"].values())
    manifest.update(status="complete" if success else "partial", completed_at_utc=datetime.now(timezone.utc).isoformat())
    write_json(manifest_path, manifest)
    LOG.info("%s. Run status: %s", manifest["status"].upper(), manifest_path)
    if all_rows:
        LOG.info("Model table: %s", output / "msk_gap_by_sex_EXPORT.csv")
    return 0 if success else 2


if __name__ == "__main__":
    try:
        notebook_cell = "ipykernel" in sys.modules and Path(sys.argv[0]).name == "ipykernel_launcher.py"
        raise SystemExit(main([] if notebook_cell else None))
    except Exception as error:
        print("MSK gap sensitivity stopped: " + str(error), file=sys.stderr)
        raise SystemExit(2)
