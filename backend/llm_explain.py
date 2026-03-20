"""
llm_explain.py — PharmaGuard
Generates detailed clinical pharmacogenomic explanations using
structured templates — no external API required.

Each explanation is drug-specific, phenotype-aware, and clinically
meaningful. Templates are based on CPIC guideline language.
"""

# ──────────────────────────────────────────────
# Gene mechanism descriptions
# ──────────────────────────────────────────────

_GENE_ROLE = {
    "CYP2D6": (
        "CYP2D6 is a liver enzyme responsible for metabolising approximately 25% of "
        "commonly prescribed drugs, including codeine, tramadol, and several antidepressants."
    ),
    "CYP2C19": (
        "CYP2C19 is a hepatic enzyme that activates or metabolises several important drugs, "
        "including the antiplatelet prodrug clopidogrel and proton pump inhibitors."
    ),
    "CYP2C9": (
        "CYP2C9 is the primary enzyme responsible for metabolising the active S-enantiomer "
        "of warfarin, as well as several NSAIDs and oral hypoglycaemics."
    ),
    "SLCO1B1": (
        "SLCO1B1 encodes a hepatic uptake transporter (OATP1B1) that carries statins "
        "from the bloodstream into liver cells where they exert their cholesterol-lowering effect."
    ),
    "TPMT": (
        "TPMT (thiopurine S-methyltransferase) is the key enzyme that inactivates "
        "thiopurine drugs such as azathioprine, 6-mercaptopurine, and thioguanine "
        "by converting them to non-toxic methylated metabolites."
    ),
    "DPYD": (
        "DPYD (dihydropyrimidine dehydrogenase) is responsible for catabolising "
        "up to 85% of administered fluorouracil (5-FU) and capecitabine. "
        "It is the rate-limiting step in fluoropyrimidine elimination."
    ),
}

# ──────────────────────────────────────────────
# Phenotype descriptions
# ──────────────────────────────────────────────

_PHENOTYPE_DESC = {
    "Poor_Metabolizer": (
        "poor metaboliser",
        "The enzyme encoded by this gene has greatly reduced or absent activity."
    ),
    "Intermediate": (
        "intermediate metaboliser",
        "The enzyme has partially reduced activity, approximately 50% of normal."
    ),
    "Normal": (
        "normal metaboliser",
        "The enzyme functions within the expected population range."
    ),
    "Ultrarapid": (
        "ultrarapid metaboliser",
        "The enzyme has increased activity, often due to gene duplication, "
        "processing the drug significantly faster than normal."
    ),
    "Reduced_Function": (
        "reduced-function metaboliser",
        "The enzyme has lower-than-normal activity, though not as severe as a poor metaboliser."
    ),
}

# ──────────────────────────────────────────────
# Per-drug, per-phenotype clinical consequence
# ──────────────────────────────────────────────

_DRUG_CONSEQUENCE = {
    "CODEINE": {
        "Poor_Metabolizer": (
            "Codeine is a prodrug that must be converted to morphine by CYP2D6 to produce "
            "analgesia. In poor metabolisers, this conversion is absent or negligible, "
            "meaning the patient receives little to no pain relief. "
            "Additionally, the parent compound accumulates, which can contribute to side effects. "
            "Codeine is ineffective and potentially unsafe for this patient."
        ),
        "Ultrarapid": (
            "Ultrarapid CYP2D6 metabolisers convert codeine to morphine extremely rapidly "
            "and at higher-than-normal concentrations. This can lead to life-threatening "
            "morphine toxicity — including respiratory depression — even at standard doses. "
            "Several fatalities have been reported in ultrarapid metabolisers prescribed codeine. "
            "This drug is contraindicated for this patient."
        ),
        "Intermediate": (
            "Intermediate CYP2D6 metabolisers convert codeine to morphine at a reduced rate, "
            "resulting in lower morphine exposure and potentially reduced analgesic efficacy. "
            "A dose adjustment or alternative opioid with a different metabolic pathway "
            "(e.g. tramadol or oxycodone) should be considered."
        ),
        "Normal": (
            "This patient is a normal CYP2D6 metaboliser. Codeine is converted to morphine "
            "at the expected rate, and standard analgesic efficacy is anticipated. "
            "Standard dosing is appropriate with routine monitoring."
        ),
        "Reduced_Function": (
            "Reduced CYP2D6 function leads to lower morphine conversion from codeine, "
            "which may result in suboptimal pain control. "
            "Consider a dose adjustment or an alternative analgesic with a different "
            "metabolic pathway."
        ),
    },

    "WARFARIN": {
        "Poor_Metabolizer": (
            "CYP2C9 poor metabolisers have significantly impaired clearance of the active "
            "S-warfarin enantiomer. This leads to higher plasma warfarin concentrations, "
            "a prolonged anticoagulant effect, and a substantially elevated risk of "
            "serious bleeding events. CPIC guidelines recommend a starting dose reduction "
            "of 25-50% compared to standard dosing, with close INR monitoring."
        ),
        "Intermediate": (
            "Intermediate CYP2C9 metabolisers clear warfarin more slowly than normal, "
            "resulting in elevated plasma levels and an increased bleeding risk at standard doses. "
            "A moderate dose reduction of 10-25% is recommended, with more frequent "
            "INR checks during the initiation period."
        ),
        "Normal": (
            "This patient has normal CYP2C9 activity and is expected to metabolise "
            "warfarin at a standard rate. Standard weight-based dosing algorithms apply. "
            "Routine INR monitoring is sufficient."
        ),
        "Ultrarapid": (
            "Ultrarapid CYP2C9 metabolism leads to faster warfarin clearance and potentially "
            "subtherapeutic anticoagulation at standard doses. "
            "Higher starting doses may be required, with close INR monitoring to ensure "
            "the therapeutic range is achieved."
        ),
        "Reduced_Function": (
            "Reduced CYP2C9 function moderately impairs warfarin clearance, increasing "
            "bleeding risk. A dose reduction and more frequent INR monitoring are advised, "
            "particularly during the first 30 days of therapy."
        ),
    },

    "CLOPIDOGREL": {
        "Poor_Metabolizer": (
            "Clopidogrel is an inactive prodrug that requires activation by CYP2C19 to "
            "inhibit platelet aggregation. CYP2C19 poor metabolisers produce inadequate "
            "amounts of the active thiol metabolite, resulting in insufficient platelet "
            "inhibition and a significantly increased risk of major adverse cardiovascular "
            "events (MACE), including stent thrombosis. "
            "CPIC guidelines recommend an alternative antiplatelet agent (prasugrel or "
            "ticagrelor) for this patient."
        ),
        "Ultrarapid": (
            "CYP2C19 ultrarapid metabolisers generate elevated levels of the active "
            "clopidogrel metabolite. While this enhances antiplatelet efficacy, it is "
            "also associated with an increased bleeding risk. "
            "Standard dosing with close monitoring for bleeding complications is advised."
        ),
        "Intermediate": (
            "Intermediate CYP2C19 metabolisers produce reduced levels of the active "
            "clopidogrel metabolite, resulting in diminished platelet inhibition. "
            "Consideration should be given to alternative antiplatelet agents, particularly "
            "in high-risk cardiovascular situations such as acute coronary syndrome or "
            "recent stent placement."
        ),
        "Normal": (
            "This patient has normal CYP2C19 activity. Clopidogrel activation is expected "
            "to proceed at a standard rate, and adequate antiplatelet efficacy is anticipated. "
            "Standard dosing is appropriate."
        ),
        "Reduced_Function": (
            "Reduced CYP2C19 function leads to suboptimal clopidogrel activation. "
            "The degree of platelet inhibition may be insufficient in high-risk patients. "
            "An alternative antiplatelet agent should be considered."
        ),
    },

    "SIMVASTATIN": {
        "Poor_Metabolizer": (
            "SLCO1B1 poor metabolisers have severely impaired hepatic uptake of simvastatin "
            "via the OATP1B1 transporter. This results in high systemic plasma drug "
            "concentrations and inadequate hepatic concentrations. "
            "Elevated plasma simvastatin is strongly associated with simvastatin-induced "
            "myopathy and rhabdomyolysis, a potentially life-threatening muscle breakdown condition. "
            "CPIC guidelines recommend switching to an alternative statin with lower SLCO1B1 "
            "sensitivity such as rosuvastatin at a reduced dose, or pravastatin."
        ),
        "Intermediate": (
            "Intermediate SLCO1B1 function leads to moderately elevated plasma simvastatin levels "
            "and a moderately increased myopathy risk. "
            "Consider using a lower simvastatin dose (20 mg/day or less) or switching to an "
            "alternative statin with lower SLCO1B1 sensitivity."
        ),
        "Normal": (
            "Normal SLCO1B1 function ensures adequate hepatic uptake of simvastatin. "
            "Plasma drug levels are expected to remain within the normal range, "
            "and the risk of simvastatin-induced myopathy is not elevated. "
            "Standard dosing is appropriate."
        ),
        "Reduced_Function": (
            "Reduced SLCO1B1 transporter activity moderately impairs hepatic uptake of simvastatin. "
            "This may lead to elevated plasma concentrations and a somewhat increased myopathy risk. "
            "Using the lowest effective simvastatin dose or considering an alternative statin "
            "is recommended."
        ),
        "Ultrarapid": (
            "Increased SLCO1B1 transporter activity may lead to enhanced hepatic uptake of simvastatin. "
            "Standard dosing is considered safe. Monitor for efficacy as expected."
        ),
    },

    "AZATHIOPRINE": {
        "Poor_Metabolizer": (
            "TPMT poor metabolisers are unable to adequately inactivate the cytotoxic "
            "thioguanine nucleotide (TGN) metabolites produced from azathioprine. "
            "This leads to a rapid and severe accumulation of TGNs in haematopoietic cells, "
            "causing life-threatening myelosuppression including neutropenia, "
            "thrombocytopenia, and anaemia. "
            "CPIC guidelines strongly recommend avoiding thiopurines in TPMT poor metabolisers "
            "or using dramatically reduced doses (10% of standard) with intensive monitoring."
        ),
        "Intermediate": (
            "Intermediate TPMT activity results in higher-than-normal TGN accumulation. "
            "The risk of myelosuppression is significantly elevated at standard doses. "
            "CPIC recommends starting at 30-70% of the standard dose, with complete blood "
            "count monitoring every 1-2 weeks for the first month."
        ),
        "Normal": (
            "Normal TPMT activity ensures adequate inactivation of cytotoxic thiopurine "
            "metabolites. The patient is expected to tolerate azathioprine at standard doses "
            "without an elevated risk of myelosuppression. "
            "Routine blood count monitoring applies."
        ),
        "Ultrarapid": (
            "Ultrarapid TPMT activity leads to rapid inactivation of thiopurine metabolites, "
            "potentially reducing the therapeutic efficacy of azathioprine. "
            "Higher doses may be needed to achieve the desired immunosuppressive effect, "
            "with therapeutic drug monitoring guiding dose titration."
        ),
        "Reduced_Function": (
            "Reduced TPMT function leads to moderately elevated TGN levels and an increased "
            "myelosuppression risk. A starting dose reduction of approximately 30-50% is "
            "recommended, with regular complete blood count monitoring."
        ),
    },

    "FLUOROURACIL": {
        "Poor_Metabolizer": (
            "DPYD poor metabolisers are unable to adequately catabolise fluorouracil (5-FU). "
            "Since DPYD eliminates the vast majority of administered 5-FU, its deficiency "
            "causes a massive and prolonged accumulation of the active drug and its toxic "
            "metabolites. This results in severe, potentially fatal toxicities including "
            "mucositis, diarrhoea, neutropenia, and neurotoxicity even at the first dose. "
            "CPIC guidelines recommend avoiding fluorouracil and capecitabine entirely, "
            "or using alternative chemotherapy regimens."
        ),
        "Intermediate": (
            "Intermediate DPYD activity leads to significantly higher 5-FU exposure than normal. "
            "CPIC recommends a 50% dose reduction as a starting point, with dose escalation "
            "only if the reduced dose is tolerated and there is no unacceptable toxicity. "
            "Close monitoring for gastrointestinal and haematological toxicities is essential."
        ),
        "Normal": (
            "This patient has normal DPYD activity. Fluorouracil is expected to be catabolised "
            "at a standard rate, and the drug can be administered at full therapeutic doses. "
            "Standard toxicity monitoring protocols apply."
        ),
        "Reduced_Function": (
            "Reduced DPYD function moderately impairs 5-FU catabolism, leading to higher drug "
            "exposure and an elevated toxicity risk. A dose reduction of 25-50% is recommended "
            "as a starting point, with careful clinical and laboratory monitoring."
        ),
        "Ultrarapid": (
            "Ultrarapid DPYD activity leads to faster-than-normal 5-FU catabolism, potentially "
            "reducing drug exposure and therapeutic efficacy. "
            "Standard dosing should be used initially, with response monitoring to assess "
            "whether dose escalation is warranted."
        ),
    },
}

# ──────────────────────────────────────────────
# Risk action summary
# ──────────────────────────────────────────────

_RISK_ACTION = {
    "Toxic": (
        "This drug carries a HIGH RISK of serious adverse reaction for this patient "
        "based on their genetic profile. Avoid use if possible and select an alternative agent. "
        "If no alternative exists, use the lowest possible dose with intensive clinical monitoring."
    ),
    "Adjust Dosage": (
        "Dose adjustment is required. Initiate at a reduced dose and titrate based on "
        "clinical response and therapeutic drug monitoring. Consult current CPIC guidelines "
        "for specific dose recommendations."
    ),
    "Safe": (
        "Standard dosing is appropriate for this patient. "
        "No pharmacogenomic-based dose adjustment is required. "
        "Apply routine clinical monitoring protocols."
    ),
    "Ineffective": (
        "This drug is likely to be ineffective for this patient due to their metabolic profile. "
        "Consider switching to a therapeutically equivalent alternative agent."
    ),
}


# ──────────────────────────────────────────────
# Public API
# ──────────────────────────────────────────────

def explain(gene: str, variant: str, drug: str, risk: str, phenotype: str = "Normal") -> str:
    """
    Return a detailed clinical pharmacogenomic explanation.

    Parameters
    ----------
    gene      : str  e.g. "CYP2D6"
    variant   : str  e.g. "*4"
    drug      : str  e.g. "CODEINE"
    risk      : str  "Safe" | "Adjust Dosage" | "Toxic" | "Ineffective"
    phenotype : str  metaboliser phenotype key

    Returns
    -------
    str  multi-sentence clinical explanation
    """
    drug_upper = drug.strip().upper()
    gene_upper = gene.strip().upper()

    # Phenotype label and one-liner description
    pheno_label, pheno_desc = _PHENOTYPE_DESC.get(
        phenotype,
        (phenotype.replace("_", " ").lower(), "")
    )

    # Gene role sentence
    gene_sentence = _GENE_ROLE.get(
        gene_upper,
        f"{gene_upper} is a key pharmacogene involved in drug metabolism."
    )

    # Drug + phenotype specific consequence
    drug_pheno_map = _DRUG_CONSEQUENCE.get(drug_upper, {})
    consequence = drug_pheno_map.get(
        phenotype,
        (
            f"The {pheno_label} phenotype alters how this patient processes {drug_upper}, "
            f"resulting in a {risk.lower()} outcome. "
            f"Clinical monitoring and possible dose adjustment are recommended."
        )
    )

    # Action recommendation
    action = _RISK_ACTION.get(
        risk,
        "Consult current CPIC guidelines for dosing recommendations."
    )

    # Assemble and return
    parts = [
        f"The patient carries the {gene_upper} {variant} allele, "
        f"resulting in a {pheno_label} phenotype. "
        f"{pheno_desc}",
        gene_sentence,
        consequence,
        action,
    ]
    return " ".join(p.strip() for p in parts if p.strip())