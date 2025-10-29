from django.shortcuts import render
from pathlib import Path
import pandas as pd
import re

# ---------- HYDROGEN (with End-Use filter data) ----------
def hydrogen(request):
    data_path = Path(__file__).resolve().parent.parent / "data" / "data_final.xlsx"

    try:
        df = pd.read_excel(data_path, sheet_name="Hydrogen")
    except Exception:
        df = pd.DataFrame()

    rename_map = {
        "ID": "id",
        "Project name": "project_name",
        "Date online": "date_online",
        "Decomission date": "decom_date",
        "Status": "status",
        "Technology": "technology",
        "Technology_details": "technology_details",
        "Technology_electricity": "technology_elec",
        "Technology_electricity_details": "technology_elec_details",
        "Product": "product",
        "Announced Size": "announced_size_text",
        "Capacity_Mwel": "capacity_mwel",
        "Capacity_Nm³ H₂/h": "capacity_nm3ph",
        "Capacity_kt H2/y": "capacity_ktpy",
        "Capacity_t CO₂ captured/y": "capacity_tco2py",
        "IEA zero-carbon estimated normalized capacity [Nm³ H₂/hour]": "iea_norm_nm3ph",
        "Location": "location_name",
        "Country": "country",
        "Latitude": "lat",
        "Longitude": "lng",
        "Comments": "comments",
        # End-use columns
        "End use Refining": "eu_refining",
        "End use Ammonia": "eu_ammonia",
        "End use Methanol": "eu_methanol",
        "End use Iron&Steel": "eu_iron_steel",
        "End use Other Ind": "eu_other_ind",
        "End use Mobility": "eu_mobility",
        "End use Power": "eu_power",
        "End use Grid inj.": "eu_grid_inj",
        "End use CHP": "eu_chp",
        "End use Domestic heat": "eu_domestic_heat",
        "End use Biofuels": "eu_biofuels",
        "End use Synfuels": "eu_synfuels",
        "End use CH4 grid inj.": "eu_ch4_grid_inj",
        "End use CH4 mobility": "eu_ch4_mobility",
    }
    df = df.rename(columns=rename_map)

    # coords
    for col in ("lat", "lng"):
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")
    if {"lat", "lng"}.issubset(df.columns):
        df = df.dropna(subset=["lat", "lng"])
    else:
        df = df.iloc[0:0]

    # parse "Announced Size" MW
    mw_re = re.compile(r'(\d+(?:\.\d+)?)\s*MW', re.IGNORECASE)
    def parse_mw(x):
        if pd.isna(x): return None
        m = mw_re.search(str(x))
        return float(m.group(1)) if m else None

    # numeric capacities
    for c in ["capacity_mwel", "capacity_nm3ph", "capacity_ktpy"]:
        if c in df.columns:
            df[c] = pd.to_numeric(df[c], errors="coerce")

    def clean(v):
        if pd.isna(v): return "No data"
        s = str(v).strip()
        return s if s else "No data"

    # end-use bools: 1/positive => True; empty/0/NaN => False
    def eu_bool(v):
        if pd.isna(v) or v == "": return False
        try:
            return float(str(v).strip()) > 0
        except Exception:
            return False

    eu_cols = [
        "eu_refining","eu_ammonia","eu_methanol","eu_iron_steel","eu_other_ind",
        "eu_mobility","eu_power","eu_grid_inj","eu_chp","eu_domestic_heat",
        "eu_biofuels","eu_synfuels","eu_ch4_grid_inj","eu_ch4_mobility",
    ]

    projects = []
    for _, r in df.iterrows():
        projects.append({
            "id": clean(r.get("id")),
            "name": clean(r.get("project_name")),
            "status": clean(r.get("status")),
            "country": clean(r.get("country")),
            "location_name": clean(r.get("location_name")),
            "lat": float(r["lat"]),
            "lng": float(r["lng"]),
            "announced_mw": parse_mw(r.get("announced_size_text")),
            "capacity_mwel": None if pd.isna(r.get("capacity_mwel")) else float(r["capacity_mwel"]),
            "capacity_nm3ph": None if pd.isna(r.get("capacity_nm3ph")) else float(r["capacity_nm3ph"]),
            "capacity_ktpy": None if pd.isna(r.get("capacity_ktpy")) else float(r["capacity_ktpy"]),
            "date_online": clean(r.get("date_online")),
            "decom_date": clean(r.get("decom_date")),
            "technology": clean(r.get("technology")),
            "comments": clean(r.get("comments")),
            "eu": {k: eu_bool(r.get(k)) for k in eu_cols},
        })

    # statuses (first-seen order)
    statuses, seen = [], set()
    for s in df.get("status", []):
        lab = clean(s)
        if lab not in seen:
            seen.add(lab)
            statuses.append(lab)

    return render(request, "maps/hydrogen.html", {"projects": projects, "statuses": statuses})

# ---------- STEEL (same as before) ----------
def steel(request):
    """
    Reads map_project/data/data_final.xlsx (sheet 'Steel'),
    converts NaN/empty fields to 'No data', and renders markers.
    """
    data_path = Path(__file__).resolve().parent.parent / "data" / "data_final.xlsx"

    try:
        df = pd.read_excel(data_path, sheet_name="Steel")
    except Exception:
        df = pd.DataFrame()

    rename_map = {
        "Production company": "production_company",
        "Capacity": "capacity",
        "Order company": "order_company",
        "Production years": "production_years",
        "Technology": "technology",
        "capex": "capex",
        "expected date online": "expected_date_online",
        "current status of the project": "status",
        "страна": "country",
        "longitide of the project": "lng",
        "latitutde of the project": "lat",
        "additional comments (description and useful facts)": "notes",
    }
    df = df.rename(columns=rename_map)

    for col in ("lat", "lng"):
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")
    if {"lat", "lng"}.issubset(df.columns):
        df = df.dropna(subset=["lat", "lng"])
    else:
        df = df.iloc[0:0]

    def clean(v):
        if pd.isna(v): return "No data"
        s = str(v).strip()
        return s if s else "No data"

    projects = []
    for _, r in df.iterrows():
        projects.append({
            "name": clean(r.get("production_company")),
            "capacity": clean(r.get("capacity")),
            "order_company": clean(r.get("order_company")),
            "production_years": clean(r.get("production_years")),
            "technology": clean(r.get("technology")),
            "capex": clean(r.get("capex")),
            "expected_date_online": clean(r.get("expected_date_online")),
            "status": clean(r.get("status")),
            "country": clean(r.get("country")),
            "lat": float(r["lat"]),
            "lng": float(r["lng"]),
            "notes": clean(r.get("notes")),
        })

    return render(request, "maps/steel.html", {"projects": projects})
