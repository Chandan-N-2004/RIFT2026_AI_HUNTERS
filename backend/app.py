from flask import Flask, request, jsonify
from flask_cors import CORS
from datetime import datetime
from risk_engine import evaluate_risk, recommendation
from llm_explain import explain
import os
import time
from werkzeug.exceptions import HTTPException

app = Flask(__name__)
CORS(app, resources={r"/api/*": {"origins": "*"}})

app.config['MAX_CONTENT_LENGTH'] = 5 * 1024 * 1024  # 5 MB limit for uploaded files

DRUG_GENE_MAP = {
    "CODEINE": ["CYP2D6"],
    "CLOPIDOGREL": ["CYP2C19"],
    "SIMVASTATIN": ["SLCO1B1"]
}

PHENO_MAP = {
    "Poor_Metabolizer": "PM",
    "Intermediate": "IM",
    "Normal": "NM",
    "Ultrarapid": "URM",
    None: "Unknown"
}


@app.route("/")
def home():
    return "Backend Running"

@app.route("/api/health")
def health():
    return jsonify({"status": "healthy"})

@app.route("/api/analyze", methods=["POST"])
def analyze():
    start = time.time()
    if 'file' not in request.files:
        return jsonify({"error": "No file uploaded"}), 400

    file = request.files.get('file')
    drug = request.form.get("drug")
    
    if not drug:
        return jsonify({"error": "Drug name missing"}), 400

    drug_upper = drug.upper()

    # 🚨 ADD HERE
    if drug_upper not in DRUG_GENE_MAP:
        return jsonify({
            "error": "Unsupported drug",
            "supported_drugs": list(DRUG_GENE_MAP.keys())
        }), 400


    if not file or file.filename == "":
        return jsonify({"error": "VCF file missing"}), 400

    if not file.filename.lower().endswith(".vcf"):
        return jsonify({"error": "Invalid file type. Upload .vcf"}), 400

    filepath = os.path.join("uploads", file.filename)
    os.makedirs("uploads", exist_ok=True)
    file.save(filepath)

    target_genes = DRUG_GENE_MAP.get(drug_upper, [])

    filtered_variants = parse_vcf(filepath, gene_filter=target_genes)

    response = build_response(drug, filtered_variants)


    # Step 3: return json
    response["processing_time_ms"] = int((time.time() - start) * 1000)
    return jsonify(response)


def parse_vcf(filepath, gene_filter=None):
    variants = []

    with open(filepath, "r") as f:
        for line in f:

            if line.startswith("#") or not line.strip():
                continue

            # 🔎 Extract INFO part reliably
            if "GENE=" not in line:
                continue

            info = line.split("GENE=", 1)[1]
            info = "GENE=" + info.strip()

            fields = {}
            for item in info.split(";"):
                if "=" in item:
                    k, v = item.split("=", 1)
                    fields[k.strip().upper()] = v.strip()

            gene = fields.get("GENE")
            allele = fields.get("ALLELE")
            phenotype = fields.get("PHENOTYPE")

            if gene_filter and gene and gene.upper() not in [g.upper() for g in gene_filter]:
                continue

            variants.append({
                "gene": gene,
                "allele": allele,
                "phenotype": phenotype
            })

    return variants


def build_response(drug, all_variants):

    drug_upper = drug.upper()
    relevant_genes = DRUG_GENE_MAP.get(drug_upper, [])

    filtered_variants = [
        v for v in all_variants
        if v["gene"] and v["gene"].upper() in relevant_genes
    ]

    # --- Risk Evaluation ---
    risk_data = evaluate_risk(filtered_variants, drug)
    advice = recommendation(risk_data["risk"])

    # --- Severity Mapping (STRICT ENUM) ---
    if risk_data["risk"] == "Toxic":
        severity = "high"
    elif risk_data["risk"] == "Adjust Dosage":
        severity = "moderate"
    elif risk_data["risk"] == "Safe":
        severity = "none"
    else:
        severity = "low"

    # --- Primary Variant ---
    primary_variant = filtered_variants[0] if filtered_variants else None

    if primary_variant:
        primary_gene = primary_variant["gene"]

        # Diplotype format "*X/*X"
        allele = primary_variant.get("allele")
        diplotype = f"{allele}/{allele}" if allele else None

        # Convert phenotype to PM/IM/NM
        phenotype_code = PHENO_MAP.get(primary_variant.get("phenotype"), "Unknown")

        explanation_text = explain(
            primary_variant["gene"],
            primary_variant.get("allele", ""),
            drug,
            risk_data["risk"]
        )

        detected_variants = [
            {
                "rsid": f"rs{i+1}",
                "gene": v["gene"],
                "allele": v["allele"],
                "phenotype": v["phenotype"]
            }
            for i, v in enumerate(filtered_variants)
        ]

    else:
        primary_gene = None
        diplotype = None
        phenotype_code = "Unknown"
        explanation_text = f"No pharmacogenomic markers relevant to {drug} detected."
        detected_variants = []

    return {
        "patient_id": "PATIENT_001",
        "drug": drug,
        "timestamp": datetime.utcnow().isoformat() + "Z",

        "risk_assessment": {
            "risk_label": risk_data["risk"],  # Must be Safe / Adjust Dosage / Toxic
            "confidence_score": risk_data["confidence"],
            "severity": severity
        },

        "pharmacogenomic_profile": {
            "primary_gene": primary_gene,
            "diplotype": diplotype,
            "phenotype": phenotype_code,
            "detected_variants": detected_variants  # ✔ REQUIRED KEY NAME
        },

        "clinical_recommendation": {
            "recommendation_text": advice
        },

        "llm_generated_explanation": {
            "summary": explanation_text
        },

        "quality_metrics": {
            "vcf_parsing_success": True,
            "relevant_variants_found": len(filtered_variants)
        },

        "analysis_status": "complete"
    }


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

 

# ALWAYS LAST
if __name__ == "__main__":
    app.run(debug=True)

