import argparse
import hashlib
import json
import sys
from dataclasses import replace
from pathlib import Path

import numpy as np
import psm_261027 as p


ROOT = Path(r"D:\gastwissenschaftler\gastw_20\DIDI\XPrivat\Tan\processed_data\pipeline_runs")
TAG = "20pct_firstmarriage_lag1_lag3_notyetdivorced_260929_extra_vars"
DEFAULT_RUN_ROOT = ROOT / (TAG + "__corrected_261027d")
FOLDERS = ("lag3_common", "lag1_common")
ORIGINAL = (
    "entgelt_value",
    "rtzb_value",
    "rehab_starts_this_year",
    "non_success_app_this_year",
    "rtzb_missing",
)
EMPLOYMENT = ("emp_reg", "emp_unemp", "emp_marg", "emp_care")
OUTCOMES = ORIGINAL + EMPLOYMENT
UNITS = {
    "entgelt_value": (1.0, "euros", "euros"),
    "rtzb_value": (1.0, "euros", "euros"),
    "rehab_starts_this_year": (100.0, "starts per 100 people", "starts per 100 people"),
    "non_success_app_this_year": (100.0, "percent", "percentage points"),
    "rtzb_missing": (100.0, "percent", "percentage points"),
    **{outcome: (1.0, "days", "days") for outcome in EMPLOYMENT},
}


def file_identity(path):
    path = Path(path).resolve()
    stat = path.stat()
    return {"path": str(path), "size_bytes": stat.st_size, "mtime_ns": stat.st_mtime_ns}


def source_paths(run_root, run_dir):
    references = []
    parent_reference = run_dir / "parent_panel_reference.json"
    if parent_reference.is_file():
        panel = Path(json.loads(parent_reference.read_text(encoding="utf-8"))["panel"])
        references.append(parent_reference)
    else:
        panel = run_root / "panels" / "analysis_panel.parquet"
    family_reference = panel.parent / "reused_family_reference.json"
    if family_reference.is_file():
        family = Path(json.loads(family_reference.read_text(encoding="utf-8"))["family_path"])
        references.append(family_reference)
    else:
        family = panel.with_name("family_variables.parquet")
    return panel, family, references


def pair_means(panel, outcome):
    treated = "treated_" + outcome
    control = "control_" + outcome
    data = p.pl.read_parquet(
        panel, columns=["match_group", "t0", "event_time", treated, control]
    ).to_pandas()
    if data.duplicated(["match_group", "t0", "event_time"]).any():
        raise ValueError("Duplicate pair/year rows for " + outcome)
    data = data.dropna(subset=[treated, control])
    if not np.isfinite(data[[treated, control]].to_numpy(dtype=float)).all():
        raise ValueError("Non-finite outcome values for " + outcome)
    if not data["t0"].between(2014, 2018).all():
        raise ValueError("Unexpected treatment cohorts for " + outcome)
    grouped = data.groupby("event_time", sort=True)
    means = grouped[[treated, control]].mean().rename(
        columns={treated: "treated_mean", control: "control_mean"}
    )
    means["n_pairs"] = grouped.size()
    if list(means.index) != list(range(-3, 6)):
        raise ValueError("Incomplete event-time coverage for " + outcome)
    if (means["n_pairs"] < 20).any():
        raise ValueError("Fewer than 20 usable pairs for " + outcome)
    for arm in (treated, control):
        positive = grouped[arm].apply(lambda values: int((values > 0).sum()))
        zero = grouped[arm].apply(lambda values: int((values == 0).sum()))
        if positive.between(1, 19).any() or zero.between(1, 19).any():
            raise ValueError("A small contributing cell needs disclosure review for " + outcome)
    means["gap"] = means["treated_mean"] - means["control_mean"]
    return means


def run(run_root, folder):
    run_dir = run_root / folder
    config_path = run_dir / "resolved_config.json"
    base = p.PipelineConfig(**json.loads(config_path.read_text(encoding="utf-8")))
    expected_lag = 3 if folder == "lag3_common" else 1
    if base.sample_tag != folder or base.lag_depth != expected_lag:
        raise ValueError("Resolved configuration does not describe " + str(run_dir))
    config = replace(base, output_dir=str(run_dir), sample_tag="all_event_study_values")
    matches = run_dir / "analysis" / (
        "matched_pairs_%s_lag%s.parquet" % (base.control_pool, base.lag_depth)
    )
    panel, family, references = source_paths(run_root, run_dir)
    sources = [config_path, panel, family, matches, *references]
    before = [file_identity(path) for path in sources]
    matched = p.pl.read_parquet(matches, columns=["match_group", "t0"])
    if matched.get_column("match_group").n_unique() != matched.height:
        raise ValueError("Matched-pair identifiers are not unique in " + str(matches))
    if not matched.get_column("t0").is_between(2014, 2018, closed="both").all():
        raise ValueError("Unexpected treatment cohorts in " + str(matches))
    config.ensure_dirs()
    print("Results: " + str(config.analysis_dir), flush=True)
    p.SUPPORTED_OUTCOMES.update(OUTCOMES)
    event_panels = {}
    original_selector = p._pretrend_outcomes
    try:
        for label, outcomes, source in (
            ("original_outcomes", ORIGINAL, panel),
            ("employment_days", EMPLOYMENT, family),
        ):
            build_config = replace(
                config, output_dir=str(config.run_dir), sample_tag=label
            )
            build_config.ensure_dirs()
            p._pretrend_outcomes = lambda _, names=outcomes: list(names)
            event_panel = p.build_pair_event_study_panel(
                build_config, source, matches, pre_years=3, post_years=5, force=True
            )
            for outcome in outcomes:
                event_panels[outcome] = event_panel
    finally:
        p._pretrend_outcomes = original_selector
    all_means = []
    all_estimates = []
    for outcome in OUTCOMES:
        print(folder + ": " + outcome, flush=True)
        source = event_panels[outcome]
        means = pair_means(source, outcome)
        result = p.fit_pair_event_study(config, source, outcome)
        if p._has_failed_stage(result):
            raise RuntimeError(str(result))
        estimates = p.pd.read_csv(result["estimates_path"]).set_index("event_time").sort_index()
        if list(estimates.index) != list(means.index):
            raise ValueError("Estimate/mean event times differ for " + outcome)
        if not np.array_equal(estimates["n_pairs"].to_numpy(), means["n_pairs"].to_numpy()):
            raise ValueError("Estimate/mean pair counts differ for " + outcome)
        normalized = means["gap"] - means.loc[-1, "gap"]
        if not np.allclose(normalized, estimates["estimate"], rtol=1e-7, atol=1e-7):
            raise ValueError("Means do not reproduce the event study for " + outcome)
        multiplier, level_unit, difference_unit = UNITS[outcome]
        means[["treated_mean", "control_mean", "gap"]] *= multiplier
        means = means.reset_index().assign(outcome=outcome, unit=level_unit)
        estimates[["estimate", "standard_error", "ci_low", "ci_high"]] *= multiplier
        joint = result.get("joint_pretrend_test") or {}
        estimates = estimates.reset_index().assign(
            outcome=outcome, unit=difference_unit,
            joint_pretrend_statistic=joint.get("statistic", np.nan),
            joint_pretrend_p=joint.get("p_value", np.nan),
        )
        all_means.append(means)
        all_estimates.append(estimates)
    if before != [file_identity(path) for path in sources]:
        raise RuntimeError("An input changed during this export; rerun after the inputs are stable.")
    means_path = config.analysis_dir / "all_event_study_group_means_EXPORT.csv"
    estimates_path = config.analysis_dir / "all_event_study_estimates_EXPORT.csv"
    p.pd.concat(all_means, ignore_index=True).to_csv(means_path, index=False)
    p.pd.concat(all_estimates, ignore_index=True).to_csv(estimates_path, index=False)
    script = globals().get("__file__")
    manifest = {
        "source_workflow": str(run_root),
        "inputs": before,
        "pipeline_module": str(Path(p.__file__).resolve()),
        "pipeline_sha256": hashlib.sha256(Path(p.__file__).read_bytes()).hexdigest(),
        "export_script_sha256": hashlib.sha256(Path(script).read_bytes()).hexdigest() if script else None,
        "source_config": base.to_dict(),
        "matched_pairs": matched.height,
        "event_times": list(range(-3, 6)),
        "reference_period": -1,
        "outcomes": list(OUTCOMES),
        "estimator": "Existing matched-pair event-study estimator; pair-clustered standard errors",
        "means": "Both members usable for each outcome/year; no new imputation; existing income zeros retained",
        "income_definition": "Existing entgelt_value/rtzb_value fields, not income-recipient means",
        "employment_definition": "Observed days, not any-days indicators; nulls remain null",
        "export_units": {outcome: list(UNITS[outcome]) for outcome in OUTCOMES},
        "minimum_cell_size": 20,
        "event_panels": {outcome: str(event_panels[outcome]) for outcome in OUTCOMES},
        "outputs": [str(means_path), str(estimates_path)],
    }
    manifest_path = config.analysis_dir / "all_event_study_export_manifest.json"
    manifest_path.write_text(json.dumps(manifest, indent=2, default=str), encoding="utf-8")
    print(means_path, flush=True)
    print(estimates_path, flush=True)
    print(manifest_path, flush=True)


def main(argv=None):
    parser = argparse.ArgumentParser(description="Export all event-study values from the corrected DIDI workflow.")
    parser.add_argument("--run-root", type=Path, default=DEFAULT_RUN_ROOT)
    parser.add_argument("--spec", choices=FOLDERS + ("all",), default="all")
    args = parser.parse_args(argv)
    args.run_root = args.run_root.resolve()
    if not args.run_root.is_dir():
        raise FileNotFoundError("Corrected workflow not found; specify its actual location with --run-root: " + str(args.run_root))
    print("Reading corrected workflow: " + str(args.run_root), flush=True)
    for folder in FOLDERS if args.spec == "all" else (args.spec,):
        run(args.run_root, folder)


if __name__ == "__main__":
    notebook_cell = "ipykernel" in sys.modules and Path(sys.argv[0]).name == "ipykernel_launcher.py"
    main([] if notebook_cell else None)
