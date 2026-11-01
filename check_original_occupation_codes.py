import os
os.environ.setdefault("POLARS_MAX_THREADS", "1")

import argparse
import csv
import hashlib
import json
import math
import tempfile
from collections import Counter, defaultdict
from datetime import datetime, timezone
from glob import glob
from pathlib import Path

import polars as pl
import pyarrow.parquet as pq

ROOT = Path(r"D:\gastwissenschaftler\gastw_20\DIDI\XPrivat\Tan\processed_data\pipeline_runs")
TAG = "20pct_firstmarriage_lag1_lag3_notyetdivorced_260929_extra_vars"
RAW_GLOB = r"D:\gastwissenschaftler\gastw_20\DIDI\XPrivat\Tan\processed_data\parquet_files\df_20pct_processed\*.parquet"
RUN_NAMES = [TAG + "__lag3_common_2014_2018", TAG, TAG + "__lag1_common_2014_2018"]
CODE = "ttsc1_kldb1988"
MIN_N = 20

# These definitions reproduce the panel builder's pre-deduplication inputs.
CORE_RAW_COLUMNS = ['simple_id', 'ja', 'gbja', 'rtwf_jjjj', 'ge', 'divorcing', 'fmsd', 'marriage_start', 'marriage_end', 'court_decision', 'first_marriage_start', 'first_marriage_end', 'is_first_marriage', 'entgelt', 'rtzb', 'byvlgs', 'bygmgs', 'whot_bland', 'whot_skt', 'ttsc1_kldb1988', 'seg_start_rsd_1', 'seg_end_rsd_1', 'rehab_start_1', 'rehab_end_1', 'mcdggr_succeed_1', 'mcdams_succeed_1', 'seg_start_rsd_2', 'seg_end_rsd_2', 'rehab_start_2', 'rehab_end_2', 'mcdggr_succeed_2', 'mcdams_succeed_2', 'application_date_fail', 'decision_date_fail', 'application_date_withdrawn', 'decision_date_withdrawn', 'application_date_forward', 'decision_date_forward']
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
LABELS = {11: 'Farmers', 12: 'Winegrowers', 21: 'Animal breeders', 22: 'Fishermen', 31: 'Managers in agriculture and animal breeding', 32: 'Agricultural engineers, agriculture advisors', 41: 'Land workers', 42: 'Milkers', 43: 'Family-member land workers, n.e.c.', 44: 'Animal keepers and related occupations', 51: 'Gardeners, garden workers', 52: 'Garden architects, garden managers', 53: 'Florists', 61: 'Forestry managers, foresters, hunters', 62: 'Forest workers, forest cultivators', 71: 'Miners', 72: 'Mechanical, electrical, face workers, shot firers', 81: 'Stone crushers', 82: 'Earth, gravel, sand quarriers', 83: 'Oil, natural gas quarriers', 91: 'Mineral preparers, mineral burners', 101: 'Stone preparers', 102: 'Jewel preparers', 111: 'Stoneware, earthenware makers', 112: 'Shaped brick, concrete block makers', 121: 'Ceramics workers', 131: 'Frit makers', 132: 'Hollow glassware makers', 133: 'Flat glass makers', 134: 'Glass blowers (lamps)', 135: 'Glass processors, glass finishers', 141: 'Chemical plant operatives', 142: 'Chemical laboratory workers', 143: 'Rubber makers, processors', 144: 'Vulcanisers', 151: 'Plastics processors', 161: 'Paper, cellulose makers', 162: 'Packaging makers', 163: 'Book binding occupations', 164: 'Other paper products makers', 171: 'Type setters, compositors', 172: 'Printed goods makers', 173: 'Printers (letterpress)', 174: 'Printers (flat, gravure)', 175: 'Special printers, screeners', 176: 'Copiers', 177: "Printer's assistants", 181: 'Wood preparers', 182: 'Wood moulders and related occupations', 183: 'Wood products makers', 184: 'Basket and wicker products makers', 191: 'Iron, metal producers, melters', 192: 'Rollers', 193: 'Metal drawers', 201: 'Moulders, coremakers', 202: 'Mould casters', 203: 'Semi-finished product fettlers and other mould casting occupations', 211: 'Sheet metal pressers, drawers, stampers', 212: 'Wire moulders, processors', 213: 'Other metal moulders (non-cutting deformation)', 221: 'Turners', 222: 'Drillers', 223: 'Planers', 224: 'Borers', 225: 'Metal grinders', 226: 'Other metal-cutting occupations', 231: 'Metal polishers', 232: 'Engravers, chasers', 233: 'Metal finishers', 234: 'Galvanisers, metal colourers', 235: 'Enamellers, zinc platers and other metal surface finishers', 241: 'Welders, oxy-acetylene cutters', 242: 'Solderers', 243: 'Riveters', 244: 'Metal bonders and other metal connectors', 251: 'Steel smiths', 252: 'Container builders, coppersmiths and related occupations', 261: 'Sheet metal workers', 262: 'Plumbers', 263: 'Pipe, tubing fitters', 270: 'Locksmiths, not specified', 271: 'Building fitters', 272: 'Sheet metal, plastics fitters', 273: 'Engine fitters', 274: 'Plant fitters, maintenance fitters', 275: 'Steel structure fitters, metal shipbuilders', 281: 'Motor vehicle repairers', 282: 'Agricultural machinery repairers', 283: 'Aircraft mechanics', 284: 'Precision mechanics', 285: 'Other mechanics', 286: 'Watch-, clockmakers', 291: 'Toolmakers', 301: 'Precision fitters n.e.c.', 302: 'Precious metal smiths', 303: 'Dental technicians', 304: 'Opthalmic opticians', 305: 'Musical instrument makers', 306: 'Doll makers, model makers, taxidermists', 311: 'Electrical fitters, mechanics', 312: 'Telecommunications mechanics, craftsmen', 313: 'Electric motor, transformer fitters', 314: 'Electrical appliance fitters', 315: 'Radio, sound equipment mechanics', 321: 'Electrical appliance, electrical parts assemblers', 322: 'Other assemblers', 323: 'Metal workers (no further specification)', 331: 'Spinners, fibre preparers', 332: 'Spoolers, twisters, ropemakers', 341: 'Weaving preparers', 342: 'Weavers', 343: 'Tufted goods makers', 344: 'Machined goods makers', 345: 'Felt makers, hat body makers', 346: 'Textile processing operatives (braiders)', 351: 'Cutters', 352: 'Clothing sewers', 353: 'Laundry cutters, sewers', 354: 'Embroiderers', 355: 'Hat, cap makers', 356: 'Sewers, n.e.c.', 357: 'Other textile processing operatives', 361: 'Textile dyers', 362: 'Textile finishers', 371: 'Leather makers, catgut string makers', 372: 'Shoemakers', 373: 'Footwear makers', 374: 'Coarse leather goods finishers, truss makers', 375: 'Fine leather goods makers', 376: 'Leather clothing makers and other leather processing operatives', 377: 'Hand shoemakers', 378: 'Skin processing operatives', 391: 'Bakery goods makers', 392: 'Confectioners (pastry)', 401: 'Butchers', 402: 'Meat, sausage goods makers', 403: 'Fish processing operatives', 411: 'Cooks', 412: 'Ready-to-serve meals, fruit, vegetable preservers, preparers', 421: 'Wine coopers', 422: 'Brewers, maltsters', 423: 'Other beverage makers, tasters', 424: 'Tobacco goods makers', 431: 'Milk, fat processing operatives', 432: 'Flour, food processors', 433: 'Sugar, sweets, ice-cream makers', 441: 'Bricklayers', 442: 'Concrete workers', 451: 'Carpenters', 452: 'Roofers', 453: 'Scaffolders', 461: 'Paviors', 462: 'Road makers', 463: 'Tracklayers', 464: 'Explosives men (except shotfirers)', 465: 'Land improvement, hydraulic engineering workers', 466: 'Other civil engineering workers', 470: 'Building labourer, general', 471: 'Earth movers', 472: 'Other building labourers, building assistants, n.e.c.', 481: 'Stucco workers, plasterers, rough casters', 482: 'Insulators, proofers', 483: 'Tile setters', 484: 'Furnace setter, air heating installers', 485: 'Glaziers', 486: 'Screed, terrazzo layers', 491: 'Room equippers', 492: 'Upholsterers, mattress makers', 501: 'Carpenters', 502: 'Model, form carpenters', 503: 'Cartwrights, wheelwrights, coopers', 504: 'Other wood and sports equipment makers', 511: 'Painters, lacquerers (construction)', 512: 'Goods painters, lacquerers', 513: 'Wood surface finishers, veneerers', 514: 'Ceramics, glass painters', 521: 'Goods examiners, sorters, n.e.c.', 522: 'Packagers, goods receivers, despatchers', 531: 'Assistants (no further specification)', 541: 'Generator machinists', 542: 'Winding engine drivers, aerial ropeway machinists', 543: 'Other machinists', 544: 'Crane drivers', 545: 'Earthmoving plant drivers', 546: 'Construction machine attendants', 547: "Machine attendants, machinists' helpers", 548: 'Stokers', 549: 'Machine setters (no further specification)', 555: 'Disabled', 601: 'Mechanical, motor engineers', 602: 'Electrical engineers', 603: 'Architects, civil engineers', 604: 'Survey engineers', 605: 'Mining, metallurgy, foundry engineers', 606: 'Other manufacturing engineers', 607: 'Other engineers', 611: 'Chemists, chemical engineers', 612: 'Physicists, physics engineers, mathematicians', 621: 'Mechanical engineering technicians', 622: 'Electrical engineering technicians', 623: 'Building technicians', 624: 'Measurement technicians', 625: 'Mining, metallurgy, foundry technicians', 626: 'Chemistry, physics technicians', 627: 'Remaining manufacturing technicians', 628: 'Other technicians', 629: 'Foremen, master mechanics', 631: 'Biological specialists', 632: 'Physical and mathematical specialists', 633: 'Chemical laboratory assistants', 634: 'Photo laboratory assistants', 635: 'Technical draughtspersons', 666: 'Rehabilitants', 681: 'Wholesale and retail trade buyers, buyers', 682: 'Salespersons', 683: 'Publishing house dealers, booksellers', 684: 'Druggists/chemists (pharmacy)', 685: 'Pharmacy aids', 686: 'Service-station attendants', 687: 'Commercial agents, travellers', 688: 'Mobile traders', 691: 'Bank specialists', 692: 'Building society specialists', 693: 'Health insurance specialists (not social security)', 694: 'Life, property insurance specialists', 701: 'Forwarding business dealers', 702: 'Tourism specialists', 703: 'Publicity occupations', 704: 'Brokers, property managers', 705: 'Landlords, agents, auctioneers', 706: 'Cash collectors, cashiers, ticket sellers, inspectors', 711: 'Railway engine drivers', 712: 'Railway controllers, conductors', 713: 'Other traffic controllers, conductors', 714: 'Motor vehicle drivers', 715: 'Coachmen', 716: 'Street attendants', 721: 'Navigating ships officers', 722: 'Technical ships officers, ships engineers', 723: 'Deck seamen', 724: 'Inland boatmen', 725: 'Other water transport occupations', 726: 'Air transport occupations', 731: 'Post masters', 732: 'Postal deliverers', 733: 'Radio operators', 734: 'Telephonists', 741: 'Warehouse managers, warehousemen', 742: 'Transportation equipment drivers', 743: 'Stowers, furniture packers', 744: 'Stores, transport workers', 751: 'Entrepreneurs, managing directors, divisional managers', 752: 'Management consultants, organisors', 753: 'Chartered accountants, tax advisers', 761: 'Members of Parliament, Ministers, elected officials', 762: 'Senior government officials', 763: 'Association leaders, officials', 771: 'Cost accountants, valuers', 772: 'Accountants', 773: 'Cashiers', 774: 'Data processing specialists', 781: 'Office specialists', 782: 'Stenographers, shorthand-typists, typists', 783: 'Data typists', 784: 'Office auxiliary workers', 791: 'Factory guards, detectives', 792: 'Watchmen, custodians', 793: 'Doormen, caretakers', 794: 'Domestic and non-domestic servants', 801: 'Soldiers, border guards, police officers', 802: 'Firefighters', 803: 'Safety testers', 804: 'Chimney sweeps', 805: 'Health-protecting occupations', 811: 'Arbitrators', 812: 'Judicial administrators', 813: 'Legal representatives, advisors', 814: 'Judicial enforcers', 821: 'Journalists', 822: 'Interpreters, translators', 823: 'Librarians, archivists, museum specialists', 831: 'Musicians', 832: "Artists' agents", 833: 'Visual, commercial artists', 834: 'Scenery, sign painters', 835: 'Artistic and assisting occupations (stage, video and audio)', 836: 'Interior, exhibition designers, window dressers', 837: 'Photographers', 838: 'Performers, professional sportsmen, auxiliary artistic occupations', 841: 'Physicians', 842: 'Dentists', 843: 'Veterinary surgeons', 844: 'Pharmacists', 851: 'Non-medical practitioners', 852: 'Masseurs, physiotherapists and related occupations', 853: 'Nurses, midwives', 854: 'Nursing assistants', 855: 'Dietary assistants, pharmaceutical assistants', 856: 'Medical receptionists', 857: 'Medical laboratory assistants', 861: 'Social workers, care workers', 862: 'Home wardens, social work teachers', 863: 'Work, vocational advisers', 864: 'Nursery teachers, child nurses', 871: 'University teachers, lecturers at higher technical schools and academies', 872: 'Gymnasium teachers', 873: 'Primary, secondary (basic), special school teachers', 874: 'Technical, vocational, factory instructors', 875: 'Music teachers, n.e.c.', 876: 'Sports teachers', 877: 'Other teachers', 881: 'Economic and social scientists, statisticians', 882: 'Humanities specialists, n.e.c.', 883: 'Scientists n.e.c.', 888: 'Nursing staff', 891: 'Ministers of religion', 892: 'Members of religious orders without specific occupation', 893: 'Religious care helpers', 901: 'Hairdressers', 902: 'Other body care occupations', 911: 'Restaurant, inn, bar keepers, hotel proprietors, catering trade dealers', 912: 'Waiters, stewards', 913: 'Others attending on guests', 921: 'Housekeeping managers', 922: 'Consumer advisors', 923: 'Other housekeeping attendants', 924: 'Employees by household cheque procedure', 931: 'Laundry workers, pressers', 932: 'Textile cleaners, dyers and dry cleaners', 933: 'Household cleaners', 934: 'Glass, buildings cleaners', 935: 'Street cleaners, refuse disposers', 936: 'Vehicle cleaners, servicers', 937: 'Machinery, container cleaners and related occupations', 971: 'Non-agricultural family assistants, n.e.c.', 981: 'Trainees with recognised training occupation still to be specified', 982: 'Interns, unpaid trainees with recognised training occupation still to be specified', 983: 'Workforce (job seekers) with occupation still to be specified', 991: 'Workforce not further specified', 995: 'Recipients of early retirement pension', 996: 'Employees in partial retirement', 997: 'Recipients of compensations allowance', 999: 'No Information'}
SPECIAL = {555, 666, 888, 995, 996, 997}
UNSPECIFIED = {981, 982, 983, 991}


def say(message):
    print(datetime.now().strftime("%H:%M:%S"), message, flush=True)


def stamp(path):
    p = Path(path)
    st = p.stat()
    return {"path": str(p.resolve()), "size": st.st_size, "mtime_ns": st.st_mtime_ns}


def write_csv(path, rows, columns):
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".tmp")
    with temporary.open("w", newline="", encoding="utf-8-sig") as handle:
        writer = csv.DictWriter(handle, fieldnames=columns)
        writer.writeheader()
        writer.writerows(rows)
    temporary.replace(path)


def describe(value):
    """Keep original special values; never turn missing into an occupation."""
    if value is None or (isinstance(value, float) and math.isnan(value)):
        return "__MISSING__", "Missing value", "missing", "__MISSING__"
    text = str(value).strip()
    try:
        numeric = float(text)
    except (ValueError, TypeError):
        return text, "Unrecognised source value", "invalid_value", "__MISSING__"
    if not math.isfinite(numeric):
        return text, "Non-finite source value", "invalid_value", "__MISSING__"
    integer = int(numeric)
    # This reproduces the current pipeline's Int32 cast and first-digit grouping.
    old_group = str(integer).zfill(3)[0] if -(2**31) <= integer < 2**31 else "__MISSING__"
    if numeric != integer or not 0 <= integer <= 999:
        return text, "Outside the integer three-digit coding range", "invalid_width_or_value", old_group
    display = str(integer).zfill(3)
    if integer == 0:
        return display, "No occupation information (raw numeric zero)", "zero_no_information", old_group
    if integer == 999:
        return display, LABELS.get(integer, "No Information"), "no_information_999", old_group
    if integer in SPECIAL:
        return display, LABELS.get(integer, "Special administrative status"), "special_status", old_group
    if integer in UNSPECIFIED:
        return display, LABELS[integer], "occupation_unspecified", old_group
    if integer in LABELS:
        return display, LABELS[integer], "occupation", old_group
    return display, "Not in the supplied BIBB three-digit label list", "unrecognised_three_digit_code", old_group


def load_run(run_dir):
    candidates = sorted((run_dir / "analysis").glob("matched_pairs_not_yet_divorced_lag*.parquet"))
    if len(candidates) != 1:
        raise RuntimeError("Expected exactly one matched-pairs file in " + str(run_dir / "analysis"))
    matches_path = candidates[0]
    lag = int(matches_path.stem.rsplit("lag", 1)[1])
    treated_path = run_dir / "analysis" / ("riskset_treated_lag%d.parquet" % lag)
    control_path = run_dir / "analysis" / ("riskset_controls_not_yet_divorced_lag%d.parquet" % lag)
    for p in (treated_path, control_path):
        if not p.exists():
            raise FileNotFoundError(str(p))
    paths = [matches_path, treated_path, control_path]
    before = [stamp(p) for p in paths]
    matches = pl.read_parquet(matches_path, columns=["t_id", "c_id", "t0"])
    if not matches.height:
        raise RuntimeError("Empty matched sample: " + str(run_dir))
    role_frames = []
    for name, id_column, risk_path in [("divorced", "t_id", treated_path), ("control", "c_id", control_path)]:
        roles = matches.select([
            pl.col(id_column).cast(pl.Int64).alias("simple_id"),
            pl.col("t0").cast(pl.Int32),
        ])
        if roles.select(pl.col("simple_id").n_unique()).item() != roles.height:
            raise RuntimeError("A person is reused within " + name + ". Counts would be assignments rather than people; this diagnostic refuses to relabel them as people.")
        risk = pl.scan_parquet(risk_path).select([
            pl.col("simple_id").cast(pl.Int64), pl.col("t0").cast(pl.Int32),
            pl.col("lag1_occ_l1_cat").cast(pl.Utf8).alias("saved_broad_group"),
        ]).join(roles.lazy(), on=["simple_id", "t0"], how="inner").collect(streaming=True)
        if risk.height != matches.height or risk.unique(subset=["simple_id", "t0"]).height != matches.height:
            raise RuntimeError("Matched baseline join is not one-to-one: " + name)
        role_frames.append(risk.with_columns([
            (pl.col("t0") - 1).cast(pl.Int32).alias("ja"), pl.lit(name).alias("group"),
        ]))
    if before != [stamp(p) for p in paths]:
        raise RuntimeError("A matching input changed while it was being read; retry after that stage finishes.")
    config_path = run_dir / "resolved_config.json"
    config = json.loads(config_path.read_text(encoding="utf-8")) if config_path.exists() else {}
    return {"directory": run_dir, "roles": pl.concat(role_frames), "n_pairs": matches.height,
            "lag": lag, "input_stamps": before, "config": config}


def source_schema(files):
    schema = {}
    for file in files:
        for name, dtype in pl.read_parquet_schema(file).items():
            schema.setdefault(name, dtype)
    required = {"simple_id", "ja", CODE}
    if not required.issubset(schema):
        raise KeyError("Processed source lacks required columns: " + str(sorted(required - set(schema))))
    return schema


def recover_original_codes(files, keys, batch_rows):
    """Resolve only requested baselines using the panel's exact row-selection rule.

    Read the same columns and perform the same casts as the original panel build.
    Fewest nulls wins; the first physical row wins ties, including across shards.
    """
    schema = source_schema(files)
    score_columns = [c for c in CORE_RAW_COLUMNS if c in schema]
    for slot in (1, 2):
        for candidate in ("maciufzt_succeed_%d" % slot, "mcaiufzt_succeed_%d" % slot):
            if candidate in schema:
                score_columns.append(candidate)
                break
    value_columns = [c for c in score_columns if c not in {"simple_id", "ja"}]
    all_columns = score_columns
    best, occurrences, first_values, conflicts = {}, Counter(), {}, set()
    offset = 0
    initial_stamps = [stamp(p) for p in files]
    for number, file in enumerate(files, 1):
        file_schema = pl.read_parquet_schema(file)
        present = [c for c in all_columns if c in file_schema]
        say("Reading processed shard %d/%d" % (number, len(files)))
        for batch in pq.ParquetFile(file).iter_batches(batch_size=batch_rows, columns=present):
            length = batch.num_rows
            data = pl.from_arrow(batch).with_row_index("__physical_order", offset=offset)
            offset += length
            expressions = []
            for c in all_columns:
                target = DTYPE_OVERRIDES.get(c, schema[c])
                expressions.append((pl.col(c).cast(target, strict=False) if c in file_schema else pl.lit(None, dtype=target)).alias(c))
            data = data.select(expressions + [pl.col("__physical_order")])
            data = data.join(keys, on=["simple_id", "ja"], how="semi")
            if not data.height:
                continue
            data = data.with_columns(pl.sum_horizontal([pl.col(c).is_null().cast(pl.Int32) for c in value_columns]).alias("__nulls"))
            wanted = ["simple_id", "ja", "__nulls", "__physical_order", CODE]
            for row in data.select(wanted).iter_rows():
                pid, year, nulls, order, raw = row[:5]
                key = (pid, year)
                occurrences[key] += 1
                # Compare the diagnostic category and label, not float/string storage.
                raw_key = describe(raw)[:3]
                if key in first_values and first_values[key] != raw_key:
                    conflicts.add(key)
                first_values.setdefault(key, raw_key)
                rank = (nulls, order)
                if key not in best or rank < best[key][:2]:
                    best[key] = (nulls, order, raw)
    if initial_stamps != [stamp(p) for p in files]:
        raise RuntimeError("Processed source files changed during the scan; no EXPORT tables were written.")
    missing = keys.height - len(best)
    if missing:
        raise RuntimeError("%d requested matched-baseline keys were absent from the processed source; refusing incomplete counts." % missing)
    audit = {"source_rows_scanned": offset, "requested_baseline_keys": keys.height,
             "recovered_baseline_keys": len(best), "baseline_keys_with_duplicate_rows": sum(n > 1 for n in occurrences.values()),
             "baseline_keys_with_disagreeing_raw_codes": len(conflicts), "score_columns": score_columns,
             "row_rule": "Fewest nulls in the canonical panel-input columns; first source row breaks ties.",
             "source_files": initial_stamps}
    return best, audit


def count_run(run, best):
    counts = defaultdict(Counter)
    mismatches = 0
    for pid, year, group, saved in run["roles"].select(["simple_id", "ja", "group", "saved_broad_group"]).iter_rows():
        entry = best[(pid, year)]
        info = describe(entry[2])
        counts[info][group] += 1
        if str(saved) != info[3]:
            mismatches += 1
    if mismatches:
        raise RuntimeError("%d recovered baseline values disagree with the saved broad occupation group. Source/version mismatch: no export will be produced." % mismatches)
    # Include zero counts for every supplied label. No missing source value is
    # imputed to any code.
    for value in [None, 0] + sorted(LABELS):
        counts.setdefault(describe(value), Counter())
    rows = []
    for (code, label, status, broad), n in sorted(counts.items()):
        d, c = n["divorced"], n["control"]
        rows.append({"original_code": code, "label": label, "code_status": status, "pipeline_broad_group": broad,
                     "divorced_n": d, "control_n": c,
                     "divorced_pct": round(100.0*d/run["n_pairs"], 6), "control_pct": round(100.0*c/run["n_pairs"], 6)})
    for name in ("divorced", "control"):
        assert sum(r[name + "_n"] for r in rows) == run["n_pairs"]
    return rows


def protect(rows, threshold=MIN_N):
    """Primary and complementary suppression, also within known broad totals.

    A small cell masks both groups' counts and percentages for that code.
    At least two code rows are masked within its broad group, where possible.
    No extra raw-code totals or percentages are exported elsewhere.
    """
    output = [dict(r) for r in rows]
    hidden = {i for i,r in enumerate(rows) if any(0 < r[g + "_n"] < threshold for g in ("divorced", "control"))}
    broad = defaultdict(list)
    for i,r in enumerate(rows):
        broad[r["pipeline_broad_group"]].append(i)
    for indices in broad.values():
        for group in ("divorced", "control"):
            column = group + "_n"
            primary = any(0 < rows[i][column] < threshold for i in indices)
            positive_hidden = [i for i in indices if i in hidden and rows[i][column] > 0]
            if primary and len(positive_hidden) == 1:
                available = [i for i in indices if i not in hidden and rows[i][column] > 0]
                if available:
                    hidden.add(min(available, key=lambda i: rows[i][column]))
    for i,r in enumerate(output):
        r["disclosure_status"] = "withheld" if i in hidden else "reported"
        if i in hidden:
            for column in ("divorced_n", "control_n", "divorced_pct", "control_pct"):
                r[column] = "withheld"
    return output


def self_test():
    assert describe(11)[0] == "011" and describe(11)[3] == "0"
    assert describe(781)[3] == "7" and describe(853)[3] == "8"
    assert describe(0)[2] == "zero_no_information"
    assert describe(555)[2] == "special_status" and describe(666)[2] == "special_status"
    assert describe(999)[2] == "no_information_999"
    assert describe(None)[3] == "__MISSING__"
    assert describe(12345)[2] == "invalid_width_or_value"
    with tempfile.TemporaryDirectory() as temp:
        root = Path(temp)
        # Physical first row wins ties; the less-missing row wins otherwise.
        one = pl.DataFrame({"simple_id": [1,1,2,3], "ja": [2013]*4,
                            CODE: [781,853,555,None], "entgelt": [None,10.0,10.0,10.0]})
        two = pl.DataFrame({"simple_id": [1,2], "ja": [2013]*2,
                            CODE: [911,666], "entgelt": [10.0,None]})
        one.write_parquet(root / "a.parquet")
        two.write_parquet(root / "b.parquet")
        keys = pl.DataFrame({"simple_id": [1,2,3], "ja": [2013]*3}).with_columns([
            pl.col("simple_id").cast(pl.Int64), pl.col("ja").cast(pl.Int32)])
        best, audit = recover_original_codes(sorted(root.glob("*.parquet")), keys, 2)
        assert best[(1,2013)][2] == 853 and best[(2,2013)][2] == 555
        assert audit["baseline_keys_with_disagreeing_raw_codes"] == 2
    demo = [{"original_code": "701", "pipeline_broad_group": "7", "divorced_n": 3, "control_n": 40, "divorced_pct": 1, "control_pct": 2},
            {"original_code": "781", "pipeline_broad_group": "7", "divorced_n": 100, "control_n": 100, "divorced_pct": 2, "control_pct": 2},
            {"original_code": "853", "pipeline_broad_group": "8", "divorced_n": 50, "control_n": 50, "divorced_pct": 3, "control_pct": 3}]
    protected = protect(demo)
    assert protected[0]["control_n"] == "withheld" and protected[1]["divorced_n"] == "withheld"
    assert protected[2]["divorced_n"] == 50
    say("SELF-TEST PASS: source-row reconciliation, code handling, totals and suppression.")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--run-dir", action="append", help="Existing run folder; repeat to inspect several runs.")
    parser.add_argument("--raw-glob", default=RAW_GLOB)
    parser.add_argument("--output", default=str(ROOT / "occupation_code_check_261101"))
    parser.add_argument("--batch-rows", type=int, default=200000)
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    if args.self_test:
        self_test()
        return
    if args.batch_rows < 1:
        raise ValueError("batch-rows must be positive")
    output = Path(args.output)
    export_dir = output / "EXPORT"
    if export_dir.exists() and any(export_dir.iterdir()):
        raise FileExistsError("EXPORT already contains results. Use a new --output folder to avoid mixing diagnostic runs.")
    pq_import = __import__("pyarrow")
    pq_import.set_cpu_count(1)
    directories = [Path(p) for p in args.run_dir] if args.run_dir else [ROOT / n for n in RUN_NAMES]
    runs = []
    for directory in directories:
        if not directory.exists() and not args.run_dir:
            say("Optional run folder absent: " + str(directory))
            continue
        run = load_run(directory)
        configured = run["config"].get("raw_glob")
        if configured and os.path.normcase(str(configured)) != os.path.normcase(args.raw_glob):
            raise RuntimeError("Run's resolved raw_glob differs from the diagnostic source: " + str(directory))
        runs.append(run)
        say("Loaded %s: %s matched pairs" % (directory.name, format(run["n_pairs"], ",")))
    if not runs:
        raise FileNotFoundError("No existing matched run was found. Supply its exact folder with --run-dir.")
    files = sorted(glob(args.raw_glob))
    if not files:
        raise FileNotFoundError("No processed source files match " + args.raw_glob)
    keys = pl.concat([r["roles"].select(["simple_id", "ja"]) for r in runs]).unique()
    best, source_audit = recover_original_codes(files, keys, args.batch_rows)
    # Validate every run before writing any EXPORT result.
    tables = [(r, count_run(r, best)) for r in runs]
    output.mkdir(parents=True, exist_ok=True)
    columns = ["original_code", "label", "code_status", "pipeline_broad_group", "divorced_n", "control_n", "divorced_pct", "control_pct"]
    summaries = []
    for run, rows in tables:
        name = run["directory"].name
        write_csv(output / "INTERNAL_NOT_FOR_EXPORT" / (name + "_original_occupation_codes_INTERNAL.csv"), rows, columns)
        safe = protect(rows)
        write_csv(export_dir / (name + "_original_occupation_codes_EXPORT.csv"), safe, columns + ["disclosure_status"])
        special = [r for r in safe if r["code_status"] != "occupation"]
        write_csv(export_dir / (name + "_special_and_unrecognised_codes_EXPORT.csv"), special, columns + ["disclosure_status"])
        summaries.append({"run": str(run["directory"]), "n_pairs": run["n_pairs"], "lag": run["lag"],
                          "baseline": "t0-1", "occupation_field": CODE, "original_code_rows": len(rows),
                          "saved_broad_group_mismatches": 0, "input_stamps": run["input_stamps"]})
        say("Written occupation counts for " + name)
    manifest = {"created_utc": datetime.now(timezone.utc).isoformat(), "script_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
                "source_audit": source_audit, "runs": summaries, "min_n": MIN_N,
                "scope": "Existing matched people at t0-1. This does not recover original AKVS/RTBN values before BASE assembly and carry-forward.",
                "labels_source": "BIBB-FDZ KldB88 English Stata labels supplied on 2026-11-01; https://metadaten.bibb.de/en/classification/detail/5",
                "disclosure": "No IDs written. Primary and complementary suppression apply to EXPORT counts and shares; INTERNAL_NOT_FOR_EXPORT contains unsuppressed aggregate counts."}
    (output / "occupation_diagnostic_manifest_INTERNAL.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    say("Done. Files for disclosure review: " + str(export_dir))


if __name__ == "__main__":
    main()
