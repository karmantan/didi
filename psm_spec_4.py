from __future__ import annotations

import argparse
import csv
from datetime import datetime, timezone
import gc
import hashlib
import importlib.util
import json
import logging
import math
import os
from pathlib import Path
import re
import sys
import traceback
import uuid


ROOT = Path(r"D:\gastwissenschaftler\gastw_20\DIDI\XPrivat\Tan\processed_data\pipeline_runs")
TAG = "20pct_firstmarriage_lag1_lag3_notyetdivorced_260929_extra_vars"
DEFAULT_RUN_ROOT = ROOT / (TAG + "__corrected_261027d")
SPECIFICATIONS = ("lag3_common", "main", "lag1_common")
LOG = logging.getLogger("baseline_adjusted")


def arguments(argv=None):
    parser = argparse.ArgumentParser(description="Add fixed pre-divorce adjustment to the saved corrected DIDI matches.")
    script = Path(globals().get("__file__", "psm_spec_4.py"))
    parser.add_argument("--code", type=Path, default=script.with_name("psm_261027.py"))
    parser.add_argument("--run-root", type=Path, default=DEFAULT_RUN_ROOT, help="The corrected workflow root containing lag3_common/main/lag1_common")
    parser.add_argument("--spec", choices=SPECIFICATIONS + ("all",), default="lag3_common")
    parser.add_argument("--history", choices=("matching", "lag1"), default="matching")
    parser.add_argument("--threads", type=int, default=1, help="CPU threads for this extra process only (default: 1)")
    parser.add_argument("--memory-gb", type=float, default=None, help="Optional model-memory ceiling; otherwise 40%% of currently available RAM")
    parser.add_argument("--output", type=Path, help="Separate output parent; each invocation creates a new dated subfolder")
    args = parser.parse_args(argv)
    if args.threads < 1 or (args.memory_gb is not None and args.memory_gb <= 0):
        parser.error("--threads and --memory-gb must be positive")
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


def check_stamps(stamps):
    for before in stamps:
        if stamp(before["path"]) != before:
            raise RuntimeError("Source changed while it was being read/fitted: " + before["path"])


def write_json(path, value):
    path = Path(path)
    temporary = path.with_suffix(path.suffix + ".writing")
    temporary.write_text(json.dumps(value, indent=2, allow_nan=False), encoding="utf-8")
    temporary.replace(path)


def load_source(path):
    path = Path(path).resolve()
    if not path.is_file():
        raise FileNotFoundError("Put this script beside psm_261027.py, or specify --code: " + str(path))
    
    sys.dont_write_bytecode = True
    name = "_didi_baseline_source"
    spec = importlib.util.spec_from_file_location(name, str(path))
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    for name in ("PipelineConfig", "_build_design_matrix", "_covariate_role",
                 "_unpenalized_logistic_regression", "_cluster_robust_logit_covariance"):
        if not hasattr(module, name):
            raise RuntimeError("Source module lacks the required interface: " + name)
    return module


def baseline_covariates(balance_path, schema, config, module, history):
    
    
    with Path(balance_path).open(newline="", encoding="utf-8-sig") as handle:
        rows = list(csv.DictReader(handle))
    required = {"sample", "variable", "in_matching", "variable_type"}
    if not rows or not required <= set(rows[0]):
        raise RuntimeError("Missing or incompatible matching-balance summary: " + str(balance_path))
    selected = []
    for row in rows:
        if row["sample"] != "post" or row["in_matching"].lower() not in {"true", "1"}:
            continue
        if row["variable_type"] == "binary_missingness":
            continue
        name = row["variable"]
        if not re.match(r"^lag[123]_", name) or name.endswith("_source_year"):
            raise RuntimeError("Unexpected variable in the baseline matching list: " + name)
        if history == "lag1" and not name.startswith("lag1_"):
            continue
        if name not in schema:
            raise KeyError("Saved follow-up lacks a matching covariate; no variable was silently omitted: " + name)
        if name not in selected:
            selected.append(name)
    if not selected or "lag1_entgelt_value" not in selected:
        raise RuntimeError("The full baseline adjustment list could not be established")
    
    roles = {"continuous": "numeric", "binary": "binary", "categorical_level": "categorical"}
    for row in rows:
        if row["sample"] == "post" and row["variable"] in selected:
            expected = roles.get(row["variable_type"])
            actual = module._covariate_role(config, row["variable"])
            
            
            exact_binary = (expected == "categorical" and actual == "binary"
                            and row["variable"] in config.exact_covariates)
            if expected and actual != expected and not exact_binary:
                raise RuntimeError("Variable role disagrees with the source audit: " + row["variable"])
    return sorted(selected)


def fit_one(module, config, path, matches, covariates, outcome, memory_gb=None):
    import numpy as np
    import pandas as pd
    from scipy import stats

    required = ["simple_id", "t0", "match_group", "treated", "follow_year", "analysis_weight", outcome]
    data = module.pl.read_parquet(path, columns=required + covariates).to_pandas().reset_index(drop=True)
    if data.empty or data[required].isna().any().any():
        raise RuntimeError("Empty follow-up or missing outcome/assignment/weight; no rows were deleted")
    if not set(data[outcome].unique()) <= {0, 1} or not set(data["treated"].unique()) == {0, 1}:
        raise RuntimeError("Treatment and event indicators must be binary with both treatment arms")
    if (data["follow_year"] < 1).any() or data.duplicated(["match_group", "treated", "follow_year"]).any():
        raise RuntimeError("Invalid or duplicated annual follow-up rows")
    weights = data["analysis_weight"].to_numpy(float)
    if not np.isfinite(weights).all() or not (weights > 0).all():
        raise RuntimeError("Invalid saved analysis weights")
    mapping = pd.concat([
        matches[["match_group", "t0", "t_id"]].rename(columns={"t_id": "expected_id"}).assign(treated=1),
        matches[["match_group", "t0", "c_id"]].rename(columns={"c_id": "expected_id"}).assign(treated=0),
    ], ignore_index=True)
    assignment = data[["match_group", "treated", "simple_id", "t0"]].drop_duplicates()
    verified = assignment.merge(mapping, on=["match_group", "treated", "t0"], how="outer", validate="one_to_one", indicator=True)
    if not verified["_merge"].eq("both").all() or not verified["simple_id"].eq(verified["expected_id"]).all():
        raise RuntimeError("Follow-up assignment does not exactly reproduce the saved matched pairs")
    hashes = pd.util.hash_pandas_object(data[covariates], index=False)
    constant = pd.DataFrame({"match_group": data["match_group"], "treated": data["treated"], "baseline": hashes})
    if constant.groupby(["match_group", "treated"], sort=False)["baseline"].nunique().gt(1).any():
        raise RuntimeError("A pre-divorce covariate changes during follow-up")
    del mapping, assignment, verified, hashes, constant


    columns = 2 + max(0, data["follow_year"].nunique() - 1)
    for name in covariates:
        if module._covariate_role(config, name) == "categorical":
            columns += max(0, data[name].astype("string").fillna("__MISSING__").nunique() - 1)
        else:
            columns += 1 + int(data[name].isna().any())
    estimate = int(data.memory_usage(index=True, deep=True).sum() + 6 * len(data) * columns * 8)
    available = getattr(module, "_available_memory_bytes", lambda: None)()
    budget = int(memory_gb * (1 << 30)) if memory_gb is not None else (int(.40 * available) if available else None)
    LOG.info("%s: %s rows; at most %s design columns; estimated working RAM %.2f GiB", outcome, len(data), columns, estimate / (1 << 30))
    if budget is not None and estimate > budget:
        raise MemoryError("Estimated design working RAM %.2f GiB exceeds available budget %.2f GiB. Retry when more RAM is free, or set --memory-gb explicitly." % (estimate / (1 << 30), budget / (1 << 30)))

    y, design, transformations, audit = module._build_design_matrix(data, config, covariates, outcome)
    x = design.to_numpy(float)
    model = module._unpenalized_logistic_regression(x, y, weights, max_iter=config.outcome_logit_max_iter)
    if getattr(model, "_pipeline_unpenalized_approximation", False) or not getattr(model, "_pipeline_converged", False):
        raise RuntimeError("A converged unpenalized model was not obtained; no penalized substitute was accepted")
    index = design.columns.get_loc("treated")
    beta = float(model.coef_[0, index])
    if not math.isfinite(beta) or abs(beta) > 10:
        raise RuntimeError("Treatment coefficient suggests separation; inspect the saved diagnostics")
    probabilities = np.clip(model.predict_proba(x)[:, 1], 1e-9, 1 - 1e-9)
    covariance = module._cluster_robust_logit_covariance(x, y, probabilities, data["match_group"].to_numpy(), weights)
    se = float(np.sqrt(covariance[index, index]))
    if not math.isfinite(se) or se <= 0:
        raise RuntimeError("Invalid matched-pair sandwich standard error; no inference fallback was used")
    arm_summary = []
    for treated in (0, 1):
        arm = data.loc[data["treated"] == treated]
        arm_summary.append({"treated": treated, "person_years": len(arm), "events": int(arm[outcome].sum())})
    result = {
        "status": "complete", "adjustment_mode": "fixed_predivorce_full",
        "outcome": outcome, "selected_covariates": covariates,
        "timing": "Covariates are frozen before assigned t0; none are updated after divorce",
        "smd_selection": "None: all actual matching covariates in the requested pre-divorce history are included",
        "estimator": "Unpenalized discrete-time logistic hazard, saved matched cohort and analysis weights",
        "inference": "Canonical matched-pair cluster-robust sandwich; no bootstrap",
        "n_person_years": len(data), "n_matched_sets": int(data["match_group"].nunique()),
        "events": int(y.sum()), "by_treatment": arm_summary,
        "follow_years": sorted(int(v) for v in data["follow_year"].unique()),
        "treatment_cohorts": sorted(int(v) for v in data["t0"].unique()),
        "log_odds": beta, "standard_error": se,
        "odds_ratio": math.exp(beta), "ci_low": math.exp(beta - 1.96 * se), "ci_high": math.exp(beta + 1.96 * se),
        "p_value": float(2 * stats.norm.sf(abs(beta / se))),
        "design_columns_used": design.columns.tolist(), "design_column_audit": audit,
        "transformations": transformations,
        "sklearn_fit_method": getattr(model, "_pipeline_fit_method", "unknown"),
        "sklearn_iterations": int(getattr(model, "_pipeline_n_iter", model.n_iter_.max())),
        "interpretation": "Conditional annual odds ratio after fixed pre-divorce adjustment; not a cumulative risk ratio or a test that unobserved confounding is absent",
        "unchanged": ["matched assignments", "follow-up rows", "outcome definitions", "risk sets", "saved analysis weights"],
        "memory_estimate_bytes": estimate,
    }
    return result


def fit_spec(module, root, name, output, args):
    import pandas as pd

    source = root / name
    config_path = source / "resolved_config.json"
    settings = json.loads(config_path.read_text(encoding="utf-8"))
    config = module.PipelineConfig(**settings)
    expected_lag = 3 if name == "lag3_common" else 1
    if config.lag_depth != expected_lag or config.sample_tag != name:
        raise RuntimeError("Resolved configuration does not describe the requested corrected-run specification")
    spec = "%s_lag%d" % (config.control_pool, config.lag_depth)
    analysis = source / "analysis"
    match_path = analysis / ("matched_pairs_" + spec + ".parquet")
    balance_path = source / "diagnostics" / ("balance_summary_" + spec + ".csv")
    fixed = [config_path, match_path, balance_path]
    before = [stamp(p) for p in fixed]
    matches = module.pl.read_parquet(match_path, columns=["match_group", "t0", "t_id", "c_id"]).to_pandas()
    if matches.empty or matches.isna().any().any() or matches["match_group"].duplicated().any():
        raise RuntimeError("Saved matched-pair assignments are empty or invalid")
    destination = output / name
    destination.mkdir()
    manifest = {"status": "running", "source_run": str(source), "source_config": settings,
                "history": args.history, "source_files": before,
                "matching_sha256": sha256(match_path), "balance_sha256": sha256(balance_path),
                "source_config_sha256": sha256(config_path), "outcomes": {}}
    write_json(destination / "manifest_INTERNAL.json", manifest)
    summaries, failed = [], False
    for label, event in (("msk", "msk_event"), ("mortality", "death_event")):
        path = analysis / (label + "_followup_" + spec + "_fixed_assignment.parquet")
        try:
            stamps = before + [stamp(path)]
            covariates = baseline_covariates(balance_path, set(module.pl.read_parquet_schema(path)), config, module, args.history)
            LOG.info("%s / %s: adjusting for %s fixed pre-divorce variables", name, label, len(covariates))
            result = fit_one(module, config, path, matches, covariates, event, args.memory_gb)
            check_stamps(stamps)
            result["source_followup"] = stamp(path)
            baseline_model = analysis / ("model_" + label + "_" + spec + "_unadjusted.json")
            comparison = {"status": "not_available"}
            if baseline_model.exists():
                original_stamp = stamp(baseline_model)
                old = json.loads(baseline_model.read_text(encoding="utf-8"))
                check_stamps([original_stamp])
                if any(old.get(k) != result[k] for k in ("n_person_years", "n_matched_sets", "events")):
                    raise RuntimeError("Existing unadjusted model describes different follow-up; refusing an inconsistent comparison")
                comparison = {"status": "available", "source": str(baseline_model),
                              **{k: old[k] for k in ("odds_ratio", "ci_low", "ci_high", "p_value")}}
            result["existing_unadjusted_comparison"] = comparison
            for model_name, values in (("fixed_predivorce_full", result), ("existing_unadjusted", comparison)):
                if values["status"] not in {"complete", "available"}:
                    continue
                summaries.append({"specification": name, "outcome": label, "model": model_name,
                                  "history": args.history, "n_pairs": result["n_matched_sets"],
                                  "person_years": result["n_person_years"], "events": result["events"],
                                  **{k: values[k] for k in ("odds_ratio", "ci_low", "ci_high", "p_value")}})
            LOG.info("%s / %s: OR %.4f [%.4f, %.4f]", name, label, result["odds_ratio"], result["ci_low"], result["ci_high"])
        except Exception as exc:
            failed = True
            result = {"status": "failed", "error": str(exc), "traceback": traceback.format_exc()}
            LOG.error("%s / %s FAILED: %s", name, label, exc)
        write_json(destination / (label + "_baseline_adjusted_INTERNAL.json"), result)
        manifest["outcomes"][label] = {"status": result["status"], "source_followup": str(path)}
        write_json(destination / "manifest_INTERNAL.json", manifest)
        gc.collect()
    check_stamps(before)
    manifest["status"] = "partial" if failed else "complete"
    write_json(destination / "manifest_INTERNAL.json", manifest)
    if summaries:
        pd.DataFrame(summaries).to_csv(destination / "model_comparison_INTERNAL.csv", index=False)
    return not failed


def main(argv=None):
    args = arguments(argv)
    
    for name in ("POLARS_MAX_THREADS", "OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS",
                 "MKL_NUM_THREADS", "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
        os.environ[name] = str(args.threads)
    module = load_source(args.code)
    root = args.run_root.resolve()
    if not root.is_dir():
        raise FileNotFoundError("Corrected workflow not found; specify its actual --destination with --run-root: " + str(root))
    parent = (args.output if args.output is not None else root.with_name(root.name + "__baseline_adjusted")).resolve()
    if parent == root or root in parent.parents or parent == root.parent:
        raise ValueError("The output parent must be a separate directory outside the running workflow")
    output = parent / (datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ") + "_" + args.history + "_" + uuid.uuid4().hex[:6])
    output.mkdir(parents=True)
    print("Reading corrected workflow: " + str(root), flush=True)
    print("Results: " + str(output), flush=True)
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(message)s",
                        handlers=[logging.StreamHandler(sys.stdout), logging.FileHandler(output / "baseline_adjusted.log", encoding="utf-8")])
    import numpy as np
    import pandas as pd
    import scipy
    import sklearn
    script = globals().get("__file__")
    manifest = {"status": "running", "source_root": str(root), "output": str(output),
                "script_sha256": sha256(script) if script else None, "pipeline_code": str(args.code.resolve()),
                "pipeline_code_sha256": sha256(args.code), "history": args.history, "threads": args.threads,
                "python": sys.version, "numpy": np.__version__, "pandas": pd.__version__,
                "polars": module.pl.__version__, "scipy": scipy.__version__, "sklearn": sklearn.__version__,
                "source_access": "read-only; existing matched follow-up explicitly reused for an additional outcome specification",
                "results": {}}
    write_json(output / "run_manifest_INTERNAL.json", manifest)
    for name in (SPECIFICATIONS if args.spec == "all" else (args.spec,)):
        try:
            ok = fit_spec(module, root, name, output, args)
            manifest["results"][name] = {"status": "complete" if ok else "partial"}
        except Exception as exc:
            manifest["results"][name] = {"status": "failed", "error": str(exc), "traceback": traceback.format_exc()}
            LOG.error("%s FAILED: %s", name, exc)
        write_json(output / "run_manifest_INTERNAL.json", manifest)
    success = all(v["status"] == "complete" for v in manifest["results"].values())
    manifest["status"] = "complete" if success else "partial"
    manifest["completed_at_utc"] = datetime.now(timezone.utc).isoformat()
    write_json(output / "run_manifest_INTERNAL.json", manifest)
    LOG.info("%s. Results: %s", manifest["status"].upper(), output)
    return 0 if success else 2


if __name__ == "__main__":
    try:
        notebook_cell = "ipykernel" in sys.modules and Path(sys.argv[0]).name == "ipykernel_launcher.py"
        raise SystemExit(main([] if notebook_cell else None))
    except Exception as error:
        print("Baseline adjustment stopped: " + str(error), file=sys.stderr)
        raise SystemExit(2)
