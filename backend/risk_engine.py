"""
risk_engine.py — PharmaGuard
Complete risk evaluation for all 6 DRUG_GENE_MAP entries.

Drug → Gene → Phenotype → Risk mapping based on CPIC guidelines:
  CODEINE      → CYP2D6   → URM=Toxic, PM=Toxic, IM=Adjust, NM=Safe
  WARFARIN     → CYP2C9   → PM=Adjust, IM=Adjust, NM=Safe
  CLOPIDOGREL  → CYP2C19  → PM=Toxic, URM=Toxic, IM=Adjust, NM=Safe
  SIMVASTATIN  → SLCO1B1  → PM=Toxic, IM=Adjust, NM=Safe
  AZATHIOPRINE → TPMT     → PM=Toxic, IM=Adjust, NM=Safe
  FLUOROURACIL → DPYD     → PM=Toxic, IM=Adjust, NM=Safe
"""

# ──────────────────────────────────────────────
# Per-drug phenotype → (risk_label, confidence)
# ──────────────────────────────────────────────

DRUG_RISK_MAP = {

    # CODEINE: CYP2D6 converts codeine → morphine.
    # URM: excessive morphine → respiratory depression (Toxic)
    # PM:  no conversion → no analgesia AND toxic metabolite build-up (Toxic)
    # IM:  reduced conversion → reduced efficacy (Adjust Dosage)
    "CODEINE": {
        "Ultrarapid":      ("Toxic",         0.97),
        "Poor_Metabolizer":("Toxic",         0.95),
        "Intermediate":    ("Adjust Dosage", 0.80),
        "Normal":          ("Safe",          0.85),
        "Reduced_Function":("Adjust Dosage", 0.75),
    },

    # WARFARIN: CYP2C9 metabolises the S-enantiomer.
    # PM/IM: reduced clearance → bleeding risk → lower dose needed
    "WARFARIN": {
        "Poor_Metabolizer":("Adjust Dosage", 0.95),
        "Intermediate":    ("Adjust Dosage", 0.82),
        "Normal":          ("Safe",          0.85),
        "Ultrarapid":      ("Adjust Dosage", 0.70),
        "Reduced_Function":("Adjust Dosage", 0.80),
    },

    # CLOPIDOGREL: CYP2C19 activates the prodrug.
    # PM: no active metabolite → drug is ineffective AND thrombosis risk (Toxic/Ineffective)
    # URM: excessive activation → bleeding risk (Toxic)
    # IM: reduced activation → partial efficacy
    "CLOPIDOGREL": {
        "Poor_Metabolizer":("Toxic",         0.98),
        "Ultrarapid":      ("Toxic",         0.88),
        "Intermediate":    ("Adjust Dosage", 0.90),
        "Normal":          ("Safe",          0.85),
        "Reduced_Function":("Adjust Dosage", 0.78),
    },

    # SIMVASTATIN: SLCO1B1 transports the drug into hepatocytes.
    # PM: impaired uptake → high plasma levels → myopathy/rhabdomyolysis (Toxic)
    # IM: moderately elevated plasma → dose reduce
    "SIMVASTATIN": {
        "Poor_Metabolizer":("Toxic",         0.95),
        "Intermediate":    ("Adjust Dosage", 0.82),
        "Normal":          ("Safe",          0.85),
        "Reduced_Function":("Adjust Dosage", 0.80),
        "Ultrarapid":      ("Safe",          0.80),
    },

    # AZATHIOPRINE: TPMT converts toxic thiopurine nucleotides.
    # PM: accumulation of toxic metabolites → severe myelosuppression (Toxic)
    # IM: partial activity → dose reduction required
    "AZATHIOPRINE": {
        "Poor_Metabolizer":("Toxic",         0.99),
        "Intermediate":    ("Adjust Dosage", 0.88),
        "Normal":          ("Safe",          0.85),
        "Ultrarapid":      ("Safe",          0.78),
        "Reduced_Function":("Adjust Dosage", 0.80),
    },

    # FLUOROURACIL: DPYD catabolises 5-FU.
    # PM: severely impaired catabolism → life-threatening toxicity (Toxic)
    # IM: reduced catabolism → dose reduction required
    "FLUOROURACIL": {
        "Poor_Metabolizer":("Toxic",         0.99),
        "Intermediate":    ("Adjust Dosage", 0.90),
        "Normal":          ("Safe",          0.85),
        "Ultrarapid":      ("Safe",          0.78),
        "Reduced_Function":("Adjust Dosage", 0.82),
    },
}

# Fallback table used when a drug is not in DRUG_RISK_MAP
_GENERIC_PHENOTYPE_RISK = {
    "Poor_Metabolizer": ("Toxic",         0.90),
    "Reduced_Function": ("Adjust Dosage", 0.80),
    "Intermediate":     ("Adjust Dosage", 0.75),
    "Normal":           ("Safe",          0.85),
    "Ultrarapid":       ("Toxic",         0.88),
}


# ──────────────────────────────────────────────
# Public API
# ──────────────────────────────────────────────

def evaluate_risk(variants: list, drug: str) -> dict:
    """
    Evaluate pharmacogenomic risk for a drug given a list of detected variants.

    Each variant dict must contain at least:
        { "gene": str, "allele": str, "phenotype": str }

    Returns:
        { "risk": str, "confidence": float }
    """
    if not variants:
        return {"risk": "Safe", "confidence": 0.85}

    drug = drug.strip().upper()
    drug_table = DRUG_RISK_MAP.get(drug, _GENERIC_PHENOTYPE_RISK)

    # Walk all variants; escalate to the worst risk found.
    # Risk severity order: Toxic > Adjust Dosage > Ineffective > Safe
    severity_order = {"Toxic": 3, "Adjust Dosage": 2, "Ineffective": 1, "Safe": 0}

    best_risk = "Safe"
    best_confidence = 0.85

    for variant in variants:
        phenotype = variant.get("phenotype", "Normal")

        if isinstance(drug_table, dict) and phenotype in drug_table:
            # drug_table is a {phenotype: (risk, confidence)} mapping
            risk, confidence = drug_table[phenotype]
        elif isinstance(drug_table, dict) and "Poor_Metabolizer" in drug_table:
            # drug_table is the generic fallback
            risk, confidence = drug_table.get(phenotype, ("Safe", 0.85))
        else:
            risk, confidence = ("Safe", 0.85)

        if severity_order.get(risk, 0) > severity_order.get(best_risk, 0):
            best_risk = risk
            best_confidence = confidence

    return {"risk": best_risk, "confidence": best_confidence}


def recommendation(risk_label: str) -> str:
    """Return a clinical recommendation string for a given risk label."""
    recommendations = {
        "Safe": (
            "Standard dosing is acceptable based on the patient's pharmacogenomic profile. "
            "No dose adjustment required. Monitor for any unexpected responses."
        ),
        "Adjust Dosage": (
            "Dose adjustment is required due to altered drug metabolism. "
            "Consider reducing starting dose by 25–50% and titrate based on clinical response "
            "and therapeutic drug monitoring. Consult current CPIC guidelines."
        ),
        "Toxic": (
            "HIGH RISK of severe adverse drug reaction. This medication is contraindicated "
            "or requires extreme caution based on this patient's genetic profile. "
            "Avoid if possible and select an alternative agent. If no alternative is available, "
            "use the lowest possible dose with intensive monitoring."
        ),
        "Ineffective": (
            "This drug is likely to be ineffective due to the patient's metabolic profile. "
            "Consider switching to an alternative therapeutic agent. "
            "Consult CPIC guidelines for recommended substitutes."
        ),
    }
    return recommendations.get(
        risk_label,
        "Consult current CPIC guidelines for dosing recommendations specific to this genetic variant."
    )