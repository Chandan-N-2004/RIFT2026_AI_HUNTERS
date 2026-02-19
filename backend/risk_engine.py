PHENOTYPE_RISK = {
    "Poor_Metabolizer": ("Toxic", 0.95),
    "Reduced_Function": ("Adjust Dosage", 0.90),
    "Intermediate": ("Adjust Dosage", 0.75),
    "Normal": ("Safe", 0.85),
    "Ultrarapid": ("Toxic", 0.90)
}

def evaluate_risk(variants, drug):

    # IMPORTANT: prevent crash when no variants
    if not variants:
        return {
            "risk": "Safe",
            "confidence": 0.5
        }

    phenotype = variants[0].get("phenotype")

    risk, confidence = PHENOTYPE_RISK.get(
        phenotype,
        ("Safe", 0.3)
    )

    return {
        "risk": risk,
        "confidence": confidence
    }


def recommendation(risk):
    if risk == "Toxic":
        return "Avoid drug — high adverse reaction risk."
    if risk == "Adjust Dosage":
        return "Dose adjustment recommended."
    return "Standard dosing acceptable."
