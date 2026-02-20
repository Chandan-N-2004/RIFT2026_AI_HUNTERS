from flask import Flask, request, jsonify
from flask_cors import CORS
from datetime import datetime
from risk_engine import evaluate_risk, recommendation
from llm_explain import explain
import os
from drug_gene_map import DRUG_GENE_MAP
from werkzeug.exceptions import HTTPException
import time

app = Flask(__name__)
CORS(app, origins="*")


# At the top of app.py
PHENO_DISPLAY = {
    "Poor_Metabolizer": "PM", 
    "Intermediate": "IM", 
    "Normal": "NM", 
    "Ultrarapid": "URM", 
    "Reduced_Function": "RF"
}
# ==============================
# PHENOTYPE TRANSLATION LAYER
# ==============================
def infer_phenotype(gene, star_allele):
    """
    Maps Star Alleles to clinical phenotypes for the risk engine.
    Covers the 6 critical genes required by the project specifications.
    """
    gene = gene.upper()
    star = star_allele.strip()

    mapping = {
        "CYP2D6": {"*3": "Poor_Metabolizer", "*4": "Poor_Metabolizer", "*5": "Poor_Metabolizer", "*6": "Poor_Metabolizer"},
        "CYP2C19": {"*2": "Poor_Metabolizer", "*3": "Poor_Metabolizer", "*17": "Ultrarapid"},
        "CYP2C9": {"*2": "Intermediate", "*3": "Poor_Metabolizer"},
        "SLCO1B1": {"*5": "Poor_Metabolizer", "*15": "Intermediate"},
        "TPMT": {"*2": "Poor_Metabolizer", "*3A": "Poor_Metabolizer", "*3C": "Intermediate"},
        "DPYD": {"*2A": "Poor_Metabolizer", "*13": "Poor_Metabolizer"}
    }

    return mapping.get(gene, {}).get(star, "Normal")

# ==============================
# UPDATED VCF PARSING (Industry Standard)
# ==============================
def parse_vcf_authentic(filepath):
    variants = []
    print(f"DEBUG: Opening file {filepath}")
    try:
        with open(filepath, "r") as f:
            for line in f:
                if line.startswith("#") or not line.strip(): continue
                
                # Split line and force everything to uppercase for matching
                cols = line.strip().split("\t")
                info_text = cols[7].upper()
                
                # DEBUG: See what the parser sees
                print(f"DEBUG: Processing Line -> {info_text}")

                # Extraction logic
                gene = None
                star = None
                
                # Manual split to handle different VCF styles
                for item in info_text.split(";"):
                    if "GENE=" in item: gene = item.split("=")[1]
                    if "STAR=" in item: star = item.split("=")[1]

                if gene and star:
                    pheno = infer_phenotype(gene, star)
                    print(f"DEBUG: Found {gene} {star} -> Phenotype: {pheno}")
                    variants.append({
                        "gene": gene,
                        "allele": star,
                        "rsid": cols[2],
                        "phenotype": pheno
                    })
        
        print(f"DEBUG: Total variants found: {len(variants)}")
    except Exception as e:
        print(f"DEBUG: Parser crashed with error: {e}")
    return variants

@app.route("/")
def home():
    return {"status": "PharmaGuard Backend is Running"}, 200

@app.route("/api/analyze", methods=["POST"])
def analyze():
    
    if 'file' not in request.files: return jsonify({"error": "No VCF"}), 400
    
    # Handle multiple drugs (comma-separated)
    drug_input = request.form.get("drug", "").upper()
    target_drugs = [d.strip() for d in drug_input.split(",") if d.strip()]
    
    file = request.files['file']
    filepath = os.path.join("uploads", file.filename)
    file.save(filepath)
    
    all_detected = parse_vcf_authentic(filepath)
    results = []

    for drug in target_drugs:
        relevant_genes = DRUG_GENE_MAP.get(drug, [])
        v_subset = [v for v in all_detected if v["gene"] in relevant_genes]
        
        risk_data = evaluate_risk(v_subset, drug)
        primary = v_subset[0] if v_subset else None
        
        # EXACT SCHEMA REQUIRED
        results.append({
            "patient_id": "PATIENT_001",
            "drug": drug,
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "risk_assessment": {
                "risk_label": risk_data["risk"],
                "confidence_score": risk_data["confidence"],
                "severity": "high" if risk_data["risk"] == "Toxic" else "none"
            },
            "pharmacogenomic_profile": {
                "primary_gene": primary["gene"] if primary else relevant_genes[0],
                "diplotype": f"{primary['allele']}/wt" if primary else "wt/wt",
                "phenotype": PHENO_DISPLAY.get(primary["phenotype"] if primary else "Normal", "NM"),
                "detected_variants": v_subset
            },
            "clinical_recommendation": {"recommendation_text": recommendation(risk_data["risk"])},
            "llm_generated_explanation": {
                "summary": explain(primary["gene"], primary["allele"], drug, risk_data["risk"]) if primary 
                           else f"No variants found for {drug}."
            },
            "quality_metrics": {"vcf_parsing_success": True}
        })

    if len(results) == 1:
        return jsonify(results[0])
    return jsonify(results)

def build_response(drug, variants, target_genes):
    risk_data = evaluate_risk(variants, drug)
    advice = recommendation(risk_data["risk"])
    
    severity_map = {"Toxic": "high", "Adjust Dosage": "moderate", "Safe": "none"}
    primary = variants[0] if variants else None
    
    # Get the display code (e.g., "NM") based on the phenotype
    pheno_code = PHENO_DISPLAY.get(primary["phenotype"] if primary else "Normal", "NM")

    return {
        "patient_id": "PATIENT_001",
        "drug": drug,
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "risk_assessment": {
            "risk_label": risk_data["risk"],
            "confidence_score": risk_data["confidence"],
            "severity": severity_map.get(risk_data["risk"], "none")
        },
        "pharmacogenomic_profile": {
            "primary_gene": primary["gene"] if primary else target_genes[0],
            "diplotype": f"{primary['allele']}/wt" if primary else "wt/wt",
            "phenotype": pheno_code,
            "detected_variants": variants
        },
        "clinical_recommendation": {
            "recommendation_text": advice
        },
        "llm_generated_explanation": {
            "summary": explain(primary["gene"], primary["allele"], drug, risk_data["risk"]) if primary 
                       else f"No high-risk variants found for {drug}. Standard metabolic function expected."
        },
        "analysis_status": "complete"
    }

# ==============================
# ERROR HANDLING
# ==============================

@app.errorhandler(HTTPException)
def handle_http_error(e):
    return jsonify({
        "error": e.name,
        "details": e.description
    }), e.code


@app.errorhandler(Exception)
def handle_server_error(e):
    return jsonify({
        "error": "Internal server error",
        "details": str(e)
    }), 500


# ==============================
# RUN APP
# ==============================


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
