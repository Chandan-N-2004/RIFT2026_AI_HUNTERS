PHENOTYPE_RISK = {
    "Poor_Metabolizer": ("Toxic", 0.95),
    "Reduced_Function": ("Adjust Dosage", 0.90),
    "Intermediate": ("Adjust Dosage", 0.75),
    "Normal": ("Safe", 0.85),
    "Ultrarapid": ("Toxic", 0.90)
}

# risk_engine.py
# risk_engine.py

def evaluate_risk(variants, drug):
    if not variants:
        return {"risk": "Safe", "confidence": 0.85}

    # Use the first detected high-risk variant
    primary = variants[0]
    phenotype = primary.get("phenotype", "Normal")
    drug = drug.upper()

    # Logic for CLOPIDOGREL (CYP2C19)
    if drug == "CLOPIDOGREL":
        if phenotype == "Poor_Metabolizer":
            return {"risk": "Toxic", "confidence": 0.98}
        if phenotype == "Intermediate":
            return {"risk": "Adjust Dosage", "confidence": 0.90}

    # Logic for DPYD / FLUOROURACIL
    if drug == "FLUOROURACIL" and phenotype == "Poor_Metabolizer":
        return {"risk": "Toxic", "confidence": 0.99}

    return {"risk": "Safe", "confidence": 0.85}

def recommendation(risk_label):
    recommendations = {
        "Safe": "Standard dosing acceptable.",
        "Adjust Dosage": "Dose adjustment required. Monitor plasma levels or consider alternative.",
        "Toxic": "High risk of adverse drug reaction. Avoid this medication.",
        "Ineffective": "Drug likely ineffective due to metabolic profile. Switch therapy."
    }
    return recommendations.get(risk_label, "Consult CPIC guidelines for dosing.")
