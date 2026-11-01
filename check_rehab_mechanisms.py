import os
for _name in ("POLARS_MAX_THREADS", "OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "NUMEXPR_NUM_THREADS"):
    os.environ[_name] = "1"

import argparse
import csv
import hashlib
import json
import math
import re
import sys
import uuid
from datetime import datetime, timezone
from glob import glob
from pathlib import Path

import numpy as np
import pandas as pd
import polars as pl
import pyarrow as pa
from scipy import sparse, stats

pa.set_cpu_count(1)
ROOT = Path(r"D:\gastwissenschaftler\gastw_20\DIDI\XPrivat\Tan\processed_data\pipeline_runs")
TAG = "20pct_firstmarriage_lag1_lag3_notyetdivorced_260929_extra_vars"
DEFAULT_RUN_ROOT = ROOT / (TAG + "__corrected_261027d")
RAW_GLOB = r"D:\gastwissenschaftler\gastw_20\DIDI\XPrivat\Tan\processed_data\parquet_files\df_20pct_processed\*.parquet"
SPECS = ("lag3_common", "main", "lag1_common")
INCOMES = ("earnings_only", "pension_only", "earnings_and_pension", "neither_observed", "unknown")
SEX = {"1": "Men", "2": "Women"}
MIN_N = 20
HORIZON = 5
CORE = ("simple_id", "match_group", "t0", "treated", "follow_year", "analysis_weight", "event_type")
CANDIDATE = re.compile(r"(^va($|_)|versorgung|ausgl|ausgleich|warte|waiting|qualif|eligib|pflicht|compulsory|beitrag|contribut|byvlgs|bygmgs|vsmo|zueg|abeg|zuab|zuschl|abschl|egpt|court|marriage|rechtskraft)", re.I)


def say(s):
    print(datetime.now().strftime("%H:%M:%S"), s, flush=True)


def stamp(path):
    path = Path(path).resolve()
    s = path.stat()
    return {"path": str(path), "size_bytes": s.st_size, "mtime_ns": s.st_mtime_ns}


def check_stamps(items):
    for before in items:
        if stamp(before["path"]) != before:
            raise RuntimeError("Input changed during this check: " + before["path"])


def clean(value):
    if isinstance(value, dict):
        return {str(k): clean(v) for k, v in value.items()}
    if isinstance(value, (list, tuple)):
        return [clean(v) for v in value]
    if isinstance(value, (np.integer,)):
        return int(value)
    if isinstance(value, (np.floating, float)):
        return float(value) if math.isfinite(value) else None
    return value


def write_json(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(json.dumps(clean(value), indent=2, allow_nan=False), encoding="utf-8")
    tmp.replace(path)


def write_csv(path, rows):
    if not rows:
        return
    path.parent.mkdir(parents=True, exist_ok=True)
    columns = list(dict.fromkeys(k for row in rows for k in row))
    tmp = path.with_suffix(path.suffix + ".tmp")
    with tmp.open("w", encoding="utf-8-sig", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=columns)
        writer.writeheader()
        writer.writerows([clean(row) for row in rows])
    tmp.replace(path)


def normal_sex(value):
    return {"1": "1", "1.0": "1", "2": "2", "2.0": "2"}.get(str(value), "unknown")


def optional_frame(path):
    if path is None:
        return None, []
    path = Path(path)
    before = stamp(path)
    data = pd.read_parquet(path) if path.suffix.lower() == ".parquet" else pd.read_csv(path)
    required = {"simple_id", "t0"}
    permitted = required | {"eligible15_pre", "va_net_drv_points", "va_added_waiting_months"}
    if not required <= set(data) or not (set(data) & (permitted - required)):
        raise ValueError("Verified baseline file needs simple_id, t0 and at least one documented optional field.")
    extra = set(data) - permitted
    if extra:
        data = data[[c for c in data if c in permitted]].copy()
    for c in ("simple_id", "t0"):
        x = pd.to_numeric(data[c], errors="raise")
        if x.isna().any() or not np.isfinite(x).all() or not x.eq(np.floor(x)).all():
            raise ValueError("Invalid verified-file key: " + c)
        data[c] = x.astype("int64")
    if data.duplicated(["simple_id", "t0"]).any():
        raise ValueError("Verified baseline input is not unique by simple_id and t0.")
    for c in sorted(set(data) - required):
        x = pd.to_numeric(data[c], errors="raise")
        if not np.isfinite(x.dropna()).all():
            raise ValueError("Non-finite optional field: " + c)
        if c == "eligible15_pre" and not set(x.dropna().unique()) <= {0, 1}:
            raise ValueError("eligible15_pre must be 0, 1 or missing.")
        if c == "va_added_waiting_months" and ((x.dropna() < 0).any() or not x.dropna().eq(np.floor(x.dropna())).all()):
            raise ValueError("va_added_waiting_months must contain nonnegative whole months or missing.")
        data[c] = x
    check_stamps([before])
    return data, [before]


def load_saved(root, name, verified):
    run = root / name
    lag = 3 if name == "lag3_common" else 1
    suffix = "not_yet_divorced_lag%d" % lag
    analysis = run / "analysis"
    paths = [run / "resolved_config.json", analysis / ("matched_pairs_" + suffix + ".parquet"),
             analysis / ("riskset_treated_lag%d.parquet" % lag),
             analysis / ("riskset_controls_not_yet_divorced_lag%d.parquet" % lag),
             analysis / ("msk_followup_" + suffix + "_fixed_assignment.parquet")]
    before = [stamp(p) for p in paths]
    config = json.loads(paths[0].read_text(encoding="utf-8"))
    if config.get("sample_tag") != name or config.get("lag_depth") != lag:
        raise ValueError("Resolved config does not describe the requested corrected specification.")
    if config.get("control_pool") != "not_yet_divorced":
        raise ValueError("This check requires the saved not-yet-divorced control pool.")
    matches = pl.read_parquet(paths[1], columns=["match_group", "t0", "t_id", "c_id"]).to_pandas()
    if matches.empty or matches.isna().any().any() or matches.match_group.duplicated().any():
        raise ValueError("Empty or nonunique saved matched pairs.")
    if not matches.t0.between(2012 if name == "main" else 2014, 2018).all():
        raise ValueError("Unexpected cohort years in saved matches.")
    matches = matches.sort_values("match_group").reset_index(drop=True)
    matches["pair_index"] = np.arange(len(matches))
    parts = []
    for arm, idcol, risk in ((1, "t_id", paths[2]), (0, "c_id", paths[3])):
        say("Reading saved baseline for " + ("divorcees" if arm else "controls"))
        roles = matches[["match_group", "t0", idcol, "pair_index"]].rename(columns={idcol: "simple_id"}).copy()
        if roles.duplicated(["simple_id", "t0"]).any():
            raise ValueError("A person has multiple matched assignments within an arm/cohort.")
        schema = pl.read_parquet_schema(risk)
        cols = ["simple_id", "t0", "lag1_ge_cat", "lag1_income_source_status"]
        if not set(cols) <= set(schema):
            raise KeyError("Risk set lacks saved sex or baseline income-source category: " + str(risk))
        wanted = pl.from_pandas(roles[["simple_id", "t0"]]).with_columns([
            pl.col("simple_id").cast(pl.Int64), pl.col("t0").cast(pl.Int32)])
        frame = (pl.scan_parquet(risk).select([
            pl.col("simple_id").cast(pl.Int64), pl.col("t0").cast(pl.Int32),
            pl.col("lag1_ge_cat").cast(pl.Utf8), pl.col("lag1_income_source_status").cast(pl.Utf8)])
            .join(wanted.lazy(), on=["simple_id", "t0"], how="inner").collect(streaming=True).to_pandas())
        if frame.duplicated(["simple_id", "t0"]).any():
            raise ValueError("Duplicate matched-baseline records in saved risk set.")
        roles = roles.merge(frame, on=["simple_id", "t0"], how="left", validate="one_to_one", indicator=True)
        if not roles.pop("_merge").eq("both").all():
            raise ValueError("A matched assignment has no baseline record.")
        roles["treated"] = arm
        roles["sex"] = roles.lag1_ge_cat.map(normal_sex)
        roles["income"] = roles.lag1_income_source_status.where(roles.lag1_income_source_status.isin(INCOMES[:-1]), "unknown")
        parts.append(roles)
    baseline = pd.concat(parts, ignore_index=True)
    if baseline.groupby("pair_index").sex.nunique().ne(1).any() or baseline.sex.eq("unknown").any():
        raise ValueError("Pairs must have the same known sex; refusing to silently discard unknown/mismatched sex.")
    if verified is not None:
        baseline = baseline.merge(verified, on=["simple_id", "t0"], how="left", validate="many_to_one")
    available = pl.read_parquet_schema(paths[4])
    if not set(CORE) <= set(available):
        raise KeyError("Saved MSK follow-up lacks required event or assignment columns.")
    say("Reading saved five-year MSK follow-up")
    follow = pl.read_parquet(paths[4], columns=list(CORE)).filter(pl.col("follow_year") <= HORIZON).to_pandas()
    if follow.empty or follow[list(CORE)].isna().any().any():
        raise ValueError("Empty follow-up or missing assignment/outcome/weight.")
    if not set(follow.event_type.unique()) <= {0, 1, 2} or not set(follow.treated.unique()) <= {0, 1}:
        raise ValueError("Invalid saved event/treatment coding.")
    if not follow.follow_year.between(1, HORIZON).all() or not follow.follow_year.eq(np.floor(follow.follow_year)).all():
        raise ValueError("Invalid follow-up years.")
    if follow.duplicated(["match_group", "treated", "follow_year"]).any():
        raise ValueError("Duplicate saved arm/pair/year rows.")
    if not np.isfinite(follow.analysis_weight).all() or not follow.analysis_weight.gt(0).all():
        raise ValueError("Invalid saved analysis weights.")
    keys = ["simple_id", "t0", "match_group", "treated"]
    follow = follow.merge(baseline[keys + ["pair_index"]], on=keys, how="left", validate="many_to_one")
    if follow.pair_index.isna().any():
        raise ValueError("Saved follow-up does not agree with matched assignments.")
    follow["pair_index"] = follow.pair_index.astype(int)
    span = follow.groupby(["pair_index", "treated"]).follow_year.agg(["min", "max", "size"])
    if span["min"].ne(1).any() or span["size"].ne(span["max"]).any():
        raise ValueError("Late entry or an internal follow-up gap requires separate handling.")
    terminal = follow.loc[follow.event_type.ne(0)].groupby(["pair_index", "treated"]).follow_year.agg(["max", "size"])
    if terminal["size"].gt(1).any() or not terminal["max"].eq(span.loc[terminal.index, "max"]).all():
        raise ValueError("Follow-up continues after a terminal event.")
    check_stamps(before)
    return matches, baseline, follow, before, config


def group_definitions(baseline, n):
    ordered = [baseline.loc[baseline.treated.eq(a)].sort_values("pair_index") for a in (0, 1)]
    sex = np.column_stack([d.sex.to_numpy() for d in ordered])
    income = np.column_stack([d.income.to_numpy() for d in ordered])
    definitions, masks = [], []
    def add(scheme, sexcode, level, mask, interpretation):
        definitions.append({"scheme": scheme, "sex": SEX[sexcode], "level": level, "interpretation": interpretation})
        masks.append(np.asarray(mask, dtype=bool))
    for s in SEX:
        smask = sex == s
        add("all_matched", s, "all", smask, "Saved matched-cohort association")
        for inc in INCOMES:
            add("own_baseline_income", s, inc, smask & (income == inc),
                "Own t0-1 recorded-income category; matching balance may differ within subgroup")
            both = (income[:, 0] == inc) & (income[:, 1] == inc)
            add("same_income_pairs", s, inc, smask & both[:, None],
                "Original pairs retained only when both members have this t0-1 category")
    optional_status = {}
    if "eligible15_pre" in baseline and baseline.eligible15_pre.notna().any():
        elig = np.column_stack([d.eligible15_pre.to_numpy(float) for d in ordered])
        for s in SEX:
            mask = (sex == s) & np.all(elig == 1, axis=1)[:, None]
            add("both_15y_qualified_pre", s, "both_confirmed_15y_pre", mask,
                "Both members met the 15-year insurance waiting period at t0-1; other requirements untested")
        optional_status["15_year_restriction"] = "run_using_user_verified_baseline_field"
    else:
        optional_status["15_year_restriction"] = "not_run_no_verified_dated_eligibility_field"
    for column, scheme, levels in (
        ("va_net_drv_points", "descriptive_divorcee_VA_points", ("net_gain", "zero_net", "net_loss", "unknown")),
        ("va_added_waiting_months", "descriptive_divorcee_VA_months", ("additional_months", "zero_additional_months", "unknown"))):
        if column not in baseline or not ordered[1][column].notna().any():
            optional_status[scheme] = "not_run_no_verified_index_divorce_VA_field"
            continue
        x = ordered[1][column].to_numpy(float)
        if column == "va_net_drv_points":
            labels = np.where(np.isnan(x), "unknown", np.where(x > 0, "net_gain", np.where(x < 0, "net_loss", "zero_net")))
        else:
            labels = np.where(np.isnan(x), "unknown", np.where(x > 0, "additional_months", "zero_additional_months"))
        for s in SEX:
            for label in levels:
                add(scheme, s, label, (sex == s) & (labels == label)[:, None],
                    "Descriptive post-divorce grouping by divorcee VA; original control partner retained; not a causal VA effect")
        optional_status[scheme] = "descriptive_comparison_run_using_user_verified_index_divorce_field"
    optional_status["VA_timing_and_eligibility_transition"] = "not_run_requires_credited_months_preexisting_months_effective_dates_and_application_dates"
    return definitions, masks, sex[:, 0], optional_status


def sufficient_matrix(follow, masks, n):
    p = follow.pair_index.to_numpy(int)
    a = follow.treated.to_numpy(int)
    y = follow.follow_year.to_numpy(int) - 1
    w = follow.analysis_weight.to_numpy(float)
    ev = follow.event_type.to_numpy(int)
    rr, cc, vv = [], [], []
    for g, mask in enumerate(masks):
        keep = mask[p, a]
        for component in range(3):
            take = keep if component == 0 else keep & (ev == component)
            rr.append((((g * 2 + a[take]) * HORIZON + y[take]) * 3 + component))
            cc.append(p[take])
            vv.append(w[take])
    matrix = sparse.coo_matrix((np.concatenate(vv), (np.concatenate(rr), np.concatenate(cc))),
                              shape=(len(masks) * 2 * HORIZON * 3, n)).tocsr()
    return matrix


def cif_from_counts(flat, k):
    x = np.asarray(flat).reshape(k, 2, HORIZON, 3)
    survival = np.ones((k, 2))
    incidence = np.zeros((k, 2))
    identified = np.ones((k, 2), dtype=bool)
    for year in range(HORIZON):
        risk, event, death = x[:, :, year, 0], x[:, :, year, 1], x[:, :, year, 2]
        if (event + death > risk + 1e-7).any():
            raise ValueError("Events exceed the saved weighted risk set.")
        identified &= (risk > 0) | (survival < 1e-12)
        h = np.divide(event, risk, out=np.zeros_like(event), where=risk > 0)
        d = np.divide(death, risk, out=np.zeros_like(death), where=risk > 0)
        incidence += survival * h
        survival *= np.clip(1 - h - d, 0, 1)
    incidence[~identified] = np.nan
    out = np.empty((k, 4))
    out[:, :2] = incidence
    out[:, 2] = incidence[:, 1] - incidence[:, 0]
    out[:, 3] = np.divide(incidence[:, 1], incidence[:, 0], out=np.full(k, np.nan), where=incidence[:, 0] > 0)
    return out


def bootstraps(matrix, sex, k, b, seed):
    rng = np.random.default_rng(seed)
    result = np.empty((b, k, 4))
    strata = [np.flatnonzero(sex == s) for s in SEX]
    strata = [x for x in strata if len(x)]
    n = len(sex)
    for i in range(b):
        sampled = np.concatenate([rng.choice(idx, size=len(idx), replace=True) for idx in strata])
        counts = np.bincount(sampled, minlength=n)
        result[i] = cif_from_counts(matrix.dot(counts), k)
        if (i + 1) % 100 == 0 or i + 1 == b:
            say("Matched-pair bootstrap %d/%d" % (i + 1, b))
    return result


def interval(values, minimum):
    finite = values[np.isfinite(values)]
    return list(np.quantile(finite, [.025, .975])) if len(finite) >= minimum else [None, None]


def summarize(defs, masks, baseline, follow, point, boot):
    rows, unsafe = [], set()
    has = np.zeros((len(baseline) // 2, 2), dtype=bool)
    obs = follow[["pair_index", "treated"]].drop_duplicates()
    has[obs.pair_index.to_numpy(int), obs.treated.to_numpy(int)] = True
    p, a = follow.pair_index.to_numpy(int), follow.treated.to_numpy(int)
    ev = follow.event_type.to_numpy(int)
    for g, (definition, mask) in enumerate(zip(defs, masks)):
        row = dict(definition, horizon_years=HORIZON, bootstrap_replicates=len(boot))
        for arm, label in ((0, "control"), (1, "divorced")):
            take = mask[p, a] & (a == arm)
            counts = {"assigned": int(mask[:, arm].sum()), "entered": int((mask[:, arm] & has[:, arm]).sum()),
                      "msk_events": int(np.sum(take & (ev == 1))), "competing_deaths": int(np.sum(take & (ev == 2)))}
            counts["without_terminal_event"] = counts["entered"] - counts["msk_events"] - counts["competing_deaths"]
            for name, value in counts.items():
                row[label + "_" + name + "_n"] = value
            if any(0 < value < MIN_N for name, value in counts.items() if name != "assigned"):
                unsafe.add(g)
            if counts["entered"] < MIN_N:
                unsafe.add(g)
        min_good = math.ceil(.95 * len(boot))
        labels = ("control_risk", "divorced_risk", "risk_difference", "risk_ratio")
        for j, label in enumerate(labels):
            row[label] = point[g, j]
            low, high = interval(boot[:, g, j], min_good)
            row[label + "_ci_low"], row[label + "_ci_high"] = low, high
        for suffix in ("", "_ci_low", "_ci_high"):
            value = row["risk_difference" + suffix]
            row["risk_difference_per_1000" + suffix] = None if value is None else value * 1000
        row["status"] = "estimated" if np.isfinite(point[g, :3]).all() and all(row[x + "_ci_low"] is not None for x in labels[:3]) else "not_estimable_at_five_years"
        if definition["level"] == "unknown":
            row["status"] = "unknown_baseline_or_VA_information_descriptive_only"
        rows.append(row)
    # Complementary suppression within the mutually exclusive income/VA
    # partitions of each sex, so their known parent total cannot reveal one cell.
    hidden = set(unsafe)
    families = {}
    for g, definition in enumerate(defs):
        if definition["scheme"] != "all_matched":
            families.setdefault((definition["scheme"], definition["sex"]), []).append(g)
    for indices in families.values():
        for label in ("control", "divorced"):
            for suffix in ("entered_n", "msk_events_n", "competing_deaths_n", "without_terminal_event_n"):
                col = label + "_" + suffix
                hidden_positive = [g for g in indices if g in hidden and rows[g][col] > 0]
                if len(hidden_positive) == 1:
                    available = [g for g in indices if g not in hidden and rows[g][col] > 0]
                    if available:
                        hidden.add(min(available, key=lambda g: rows[g][col]))
    return rows, hidden


def protect_effects(rows, hidden):
    output = []
    for i, original in enumerate(rows):
        row = dict(original)
        if i in hidden:
            for k in row:
                if k not in {"scheme", "sex", "level", "interpretation", "status", "horizon_years", "bootstrap_replicates"}:
                    row[k] = "withheld"
            row["disclosure_status"] = "withheld"
        else:
            row["disclosure_status"] = "reported"
            # Avoid publishing a small missing-entry count by subtraction.
            for label in ("control", "divorced"):
                gap = row[label + "_assigned_n"] - row[label + "_entered_n"]
                if 0 < gap < MIN_N:
                    row[label + "_assigned_n"] = "withheld"
                    row[label + "_entered_n"] = "withheld"
        output.append(row)
    return output


def contrast_rows(defs, point, boot, hidden):
    lookup = {(d["scheme"], d["sex"], d["level"]): i for i, d in enumerate(defs)}
    requests = []
    for scheme, level in sorted({(d["scheme"], d["level"]) for d in defs if d["level"] != "unknown"}):
        women, men = lookup.get((scheme, "Women", level)), lookup.get((scheme, "Men", level))
        if women is not None and men is not None:
            requests.append(("women_minus_men_RD", women, men))
    for scheme in ("own_baseline_income", "same_income_pairs"):
        for sex in SEX.values():
            reference = lookup[(scheme, sex, "earnings_only")]
            for level in INCOMES[1:-1]:
                requests.append(("income_RD_minus_earnings_only_RD", lookup[(scheme, sex, level)], reference))
    for scheme, left_level, right_level in (
        ("descriptive_divorcee_VA_points", "net_gain", "net_loss"),
        ("descriptive_divorcee_VA_points", "net_gain", "zero_net"),
        ("descriptive_divorcee_VA_months", "additional_months", "zero_additional_months")):
        for sex in SEX.values():
            left, right = lookup.get((scheme, sex, left_level)), lookup.get((scheme, sex, right_level))
            if left is not None and right is not None:
                requests.append(("descriptive_VA_RD_difference", left, right))
    rows = []
    for kind, left, right in requests:
        values = boot[:, left, 2] - boot[:, right, 2]
        finite = values[np.isfinite(values)]
        good = len(finite) >= math.ceil(.95 * len(boot))
        estimate = point[left, 2] - point[right, 2]
        se = float(np.std(finite, ddof=1)) if good else np.nan
        p = float(2 * stats.norm.sf(abs(estimate / se))) if se > 0 and np.isfinite(estimate) else None
        low, high = interval(values, math.ceil(.95 * len(boot)))
        row = {"test": kind, "scheme": defs[left]["scheme"], "left_sex": defs[left]["sex"],
               "left_level": defs[left]["level"], "right_sex": defs[right]["sex"], "right_level": defs[right]["level"],
               "RD_difference_per_1000": estimate * 1000, "ci_low": None if low is None else low * 1000,
               "ci_high": None if high is None else high * 1000, "bootstrap_standard_error_per_1000": se * 1000,
               "p_value": p, "p_value_Holm": None,
               "inference": "Exploratory bootstrap-SE Wald test; percentile CI; shared sex-stratified matched-pair draws",
               "status": "estimated" if p is not None else "not_estimable",
               "disclosure_status": "withheld" if left in hidden or right in hidden else "reported"}
        rows.append(row)
    # Treat all publishable nominal tests in this run as one exploratory family.
    valid = sorted([i for i,r in enumerate(rows) if r["p_value"] is not None and r["disclosure_status"] == "reported"], key=lambda i: rows[i]["p_value"])
    running = 0.
    for rank, i in enumerate(valid):
        running = max(running, min(1., (len(valid) - rank) * rows[i]["p_value"]))
        rows[i]["p_value_Holm"] = running
    protected = []
    for row in rows:
        r = dict(row)
        if r["disclosure_status"] == "withheld":
            for k in ("RD_difference_per_1000", "ci_low", "ci_high", "bootstrap_standard_error_per_1000", "p_value", "p_value_Holm"):
                r[k] = "withheld"
        protected.append(r)
    return rows, protected


def inventory(root, raw_glob, run_paths, limit=300):
    records, problems, files = [], [], set()
    for run in run_paths:
        for folder in (run / "analysis", run / "panels"):
            if folder.is_dir():
                files.update(folder.glob("*.parquet"))
    # Scan every processed shard's schema, never its person-level values.
    files.update(Path(p) for p in glob(raw_glob))
    # Extra source metadata: BASE/VA/VSKT etc.; skip analysis/output trees.
    extra = 0
    if root.is_dir():
        for parent, dirs, names in os.walk(root):
            dirs[:] = [d for d in dirs if d not in {"pipeline_runs", ".git", "__pycache__"}]
            for name in sorted(names):
                p = Path(parent) / name
                if p.suffix.lower() in {".dta", ".parquet"} and re.search(r"(^|[\\/_.-])(va|vskt|base|akvs|rtbn|ltvs)([\\/_.-]|$)", str(Path(root.name) / p.relative_to(root)), re.I):
                    if extra >= limit:
                        problems.append("Additional-source metadata limit reached; use --inventory-limit to increase it.")
                        break
                    files.add(p)
                    extra += 1
            if extra >= limit:
                break
    for i, path in enumerate(sorted(files, key=str)):
        try:
            before = stamp(path)
            if path.suffix.lower() == ".parquet":
                fields = list(pl.read_parquet_schema(path))
                labels = {}
            else:
                with pd.read_stata(path, iterator=True, convert_categoricals=False) as reader:
                    labels = reader.variable_labels()
                    fields = list(labels)
            check_stamps([before])
            for name in fields:
                label = str(labels.get(name, ""))
                if CANDIDATE.search(name + " " + label):
                    records.append({"source_file_INTERNAL": str(path), "variable": name, "label": label,
                                    "verification": "candidate_only_definition_timing_and_marriage_link_not_verified"})
        except Exception as exc:
            problems.append(str(path) + ": " + str(exc))
        if (i + 1) % 100 == 0:
            say("Metadata audit: %d/%d files" % (i + 1, len(files)))
    return records, problems, len(files)


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--run-root", type=Path, default=DEFAULT_RUN_ROOT)
    parser.add_argument("--spec", choices=SPECS + ("all",), default="lag3_common")
    parser.add_argument("--bootstrap", type=int, default=500)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--output", type=Path)
    parser.add_argument("--raw-glob", default=RAW_GLOB)
    parser.add_argument("--inventory-root", type=Path, default=ROOT.parent.parent)
    parser.add_argument("--inventory-limit", type=int, default=300)
    parser.add_argument("--skip-inventory", action="store_true")
    parser.add_argument("--verified-baseline-file", type=Path, help="Existing documented person/t0 file; see README contract. No guessed field mappings.")
    parser.add_argument("--verified-definition-note", help="Required with verified-baseline-file: source, definitions, measurement date and index-divorce linkage.")
    args = parser.parse_args(argv)
    if args.bootstrap < 100 or args.inventory_limit < 1:
        parser.error("Use at least 100 bootstrap draws and a positive inventory limit.")
    if args.verified_baseline_file and not args.verified_definition_note:
        parser.error("A verified baseline file requires --verified-definition-note documenting its construction.")
    if not args.run_root.is_dir():
        raise FileNotFoundError("Corrected workflow absent; use --run-root: " + str(args.run_root))
    parent = args.output or args.run_root.with_name(args.run_root.name + "__mechanism_checks")
    parent = parent.resolve()
    source = args.run_root.resolve()
    if parent == source or source in parent.parents or parent == source.parent:
        raise ValueError("Output must be separate from the running workflow.")
    output = parent / (datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ") + "_" + uuid.uuid4().hex[:6])
    output.mkdir(parents=True)
    say("Results: " + str(output))
    verified, verified_stamps = optional_frame(args.verified_baseline_file)
    manifest = {"status": "running", "created_utc": datetime.now(timezone.utc).isoformat(),
                "source_root": str(source), "script_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
                "bootstrap": args.bootstrap, "seed": args.seed, "horizon_years": HORIZON,
                "bootstrap_unit": "Original matched pair, stratified by exact-matched sex; same draws across every subgroup",
                "method": "Weighted annual competing-risk MSK CIF from saved fixed-assignment risk sets",
                "verified_definition_note": args.verified_definition_note, "verified_input": verified_stamps,
                "disclosure": "Candidate EXPORT files have n<20 primary/complementary masking; normal disclosure review remains necessary. No IDs written.",
                "scope": "Exploratory subgroup associations; does not establish mechanisms or underlying morbidity; existing weights/outcomes retained.",
                "runs": {}}
    write_json(output / "manifest_INTERNAL.json", manifest)
    names = SPECS if args.spec == "all" else (args.spec,)
    inventory_paths = []
    for number, name in enumerate(names):
        try:
            say("Loading " + name)
            matches, baseline, follow, stamps, config = load_saved(source, name, verified)
            defs, masks, sex, optional_status = group_definitions(baseline, len(matches))
            matrix = sufficient_matrix(follow, masks, len(matches))
            point = cif_from_counts(matrix.dot(np.ones(len(matches))), len(defs))
            boot = bootstraps(matrix, sex, len(defs), args.bootstrap, args.seed + 10000 * SPECS.index(name))
            rows, hidden = summarize(defs, masks, baseline, follow, point, boot)
            tests, tests_safe = contrast_rows(defs, point, boot, hidden)
            check_stamps(stamps + verified_stamps)
            write_csv(output / "INTERNAL_NOT_FOR_EXPORT" / (name + "_subgroup_effects_INTERNAL.csv"), rows)
            write_csv(output / "INTERNAL_NOT_FOR_EXPORT" / (name + "_heterogeneity_tests_INTERNAL.csv"), tests)
            write_csv(output / "EXPORT" / (name + "_subgroup_effects_EXPORT.csv"), protect_effects(rows, hidden))
            write_csv(output / "EXPORT" / (name + "_heterogeneity_tests_EXPORT.csv"), tests_safe)
            manifest["runs"][name] = {"status": "complete", "inputs": stamps, "matched_pairs": len(matches),
                "assignments_without_saved_MSK_followup": int(2 * len(matches) - follow[["pair_index", "treated"]].drop_duplicates().shape[0]),
                "optional_checks": optional_status, "group_definitions": defs}
            inventory_paths.append(source / name)
            del matches, baseline, follow, masks, matrix, boot
            say(name + " complete")
        except Exception as exc:
            import traceback
            manifest["runs"][name] = {"status": "failed_or_not_ready", "error": str(exc), "traceback": traceback.format_exc()}
            say(name + " unavailable/failed: " + str(exc))
        write_json(output / "manifest_INTERNAL.json", manifest)
    if not args.skip_inventory:
        say("Auditing existing source-file names, schemas and variable labels; no raw person records loaded")
        candidates, errors, count = inventory(args.inventory_root, args.raw_glob, inventory_paths, args.inventory_limit)
        write_csv(output / "INTERNAL_NOT_FOR_EXPORT" / "candidate_mechanism_fields_INTERNAL.csv", candidates)
        safe = sorted({(r["variable"], r["label"]) for r in candidates})
        write_csv(output / "EXPORT" / "candidate_mechanism_fields_EXPORT.csv", [
            {"variable": name, "label": label, "verification": "Candidate only; verify definition, reference date and index-divorce linkage"}
            for name,label in safe])
        manifest["metadata_audit"] = {"files_examined": count, "candidate_rows": len(candidates), "problems_INTERNAL": errors}
    statuses = [x["status"] for x in manifest["runs"].values()]
    manifest["status"] = "complete_available_analyses" if statuses and all(x == "complete" for x in statuses) else "partial"
    manifest["completed_utc"] = datetime.now(timezone.utc).isoformat()
    write_json(output / "manifest_INTERNAL.json", manifest)
    report = ["REHABILITATION MECHANISM CHECK", "", "Source: " + str(source),
              "Results: " + str(output), "", "These are exploratory associations from existing matched MSK follow-up.",
              "Income categories refer to recorded sources at t0-1, not proven insurance eligibility.",
              "Own-income subgroups may have different balance; same-income-pair results are a selected sensitivity sample.",
              "No source files, matching or mediation were changed. No person IDs were written.", ""]
    for name, result in manifest["runs"].items():
        report.append(name + ": " + result["status"])
        if "optional_checks" in result:
            report.extend("  " + k + ": " + v for k,v in result["optional_checks"].items())
        else:
            report.append("  " + result.get("error", ""))
    audit = manifest.get("metadata_audit")
    if audit is not None:
        report += ["", "Metadata audit: %d files examined; %d candidate field occurrences; %d problems." % (
            audit["files_examined"], audit["candidate_rows"], len(audit["problems_INTERNAL"])),
            "See manifest_INTERNAL.json for audit problems and candidate_mechanism_fields_INTERNAL.csv for source paths."]
    else:
        report += ["", "Metadata audit skipped by command-line option."]
    report += ["", "Candidate column names are metadata, not validated mechanism variables.",
               "A full VA timing/eligibility-transition test needs additional waiting months, pre-existing qualifying months,",
               "the effective decision date, and the rehabilitation application date. It is not inferred from net points alone.",
               "Only EXPORT files are candidates for normal disclosure review. Keep INTERNAL files in the secure environment."]
    (output / "CHECK_STATUS.txt").write_text("\n".join(report) + "\n", encoding="utf-8")
    say("Finished. Read " + str(output / "CHECK_STATUS.txt"))
    return 0 if manifest["status"] == "complete_available_analyses" else 2


if __name__ == "__main__":
    try:
        notebook_cell = "ipykernel" in sys.modules and Path(sys.argv[0]).name == "ipykernel_launcher.py"
        raise SystemExit(main([] if notebook_cell else None))
    except Exception as exc:
        print("Mechanism check stopped: " + str(exc), file=sys.stderr)
        raise SystemExit(2)
