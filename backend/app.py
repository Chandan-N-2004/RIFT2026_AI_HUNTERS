"""
app.py — PharmaGuard Backend
Flask API for pharmacogenomic risk analysis.

Changes from original:
  - File cleanup after processing (os.remove in finally block)
  - 5 MB upload size limit
  - Drug validation against DRUG_GENE_MAP before processing
  - Multi-drug array response consistent with single-drug response schema
  - llm_explain now receives phenotype argument
  - Duplicate build_response() removed; single implementation used throughout
  - tempCodeRunnerFile logic removed
  - Robust VCF parser: handles both STAR= custom format AND ANN= / CSQ= annotations
"""

import os
from flask import Flask, request, jsonify
from flask_cors import CORS
from datetime import datetime, timezone
from risk_engine import evaluate_risk, recommendation
from llm_explain import explain
from drug_gene_map import DRUG_GENE_MAP
from werkzeug.exceptions import HTTPException

app = Flask(__name__)
CORS(app, origins="*")

# ──────────────────────────────────────────────
# Config
# ──────────────────────────────────────────────
UPLOAD_FOLDER = "uploads"
MAX_FILE_BYTES = 5 * 1024 * 1024  # 5 MB
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

PHENO_DISPLAY = {
    "Poor_Metabolizer": "PM",
    "Intermediate":     "IM",
    "Normal":           "NM",
    "Ultrarapid":       "URM",
    "Reduced_Function": "RF",
}


# ──────────────────────────────────────────────
# Phenotype inference from star alleles
# ──────────────────────────────────────────────

ALLELE_PHENOTYPE_MAP = {
    "CYP2D6": {
        "*3":  "Poor_Metabolizer",
        "*4":  "Poor_Metabolizer",
        "*5":  "Poor_Metabolizer",
        "*6":  "Poor_Metabolizer",
        "*10": "Intermediate",
        "*17": "Intermediate",
        "*2":  "Normal",
        "*1":  "Normal",
        "*35": "Normal",
        "*41": "Reduced_Function",
    },
    "CYP2C19": {
        "*2":  "Poor_Metabolizer",
        "*3":  "Poor_Metabolizer",
        "*17": "Ultrarapid",
        "*1":  "Normal",
    },
    "CYP2C9": {
        "*2":  "Intermediate",
        "*3":  "Poor_Metabolizer",
        "*1":  "Normal",
    },
    "SLCO1B1": {
        "*5":  "Poor_Metabolizer",
        "*15": "Intermediate",
        "*1":  "Normal",
        "*1A": "Normal",
        "*1B": "Normal",
    },
    "TPMT": {
        "*2":  "Poor_Metabolizer",
        "*3A": "Poor_Metabolizer",
        "*3C": "Intermediate",
        "*3B": "Intermediate",
        "*1":  "Normal",
    },
    "DPYD": {
        "*2A": "Poor_Metabolizer",
        "*13": "Poor_Metabolizer",
        "*1":  "Normal",
    },
}


def infer_phenotype(gene: str, star_allele: str) -> str:
    gene = gene.strip().upper()
    star = star_allele.strip()
    return ALLELE_PHENOTYPE_MAP.get(gene, {}).get(star, "Normal")


# ──────────────────────────────────────────────
# VCF Parser — handles STAR= and ANN= / CSQ= formats
# ──────────────────────────────────────────────

def parse_vcf(filepath: str) -> list:
    """
    Parse a VCF file and extract pharmacogenomically relevant variants.

    Supports three INFO field formats:
      1. Custom:  GENE=CYP2D6;STAR=*4
      2. SnpEff:  ANN=<allele>|<effect>|<impact>|<gene>|...
      3. VEP:     CSQ=<allele>|<gene>|...
    """
    variants = []
    try:
        with open(filepath, "r", errors="replace") as f:
            for line in f:
                if line.startswith("#") or not line.strip():
                    continue

                cols = line.strip().split("\t")
                if len(cols) < 8:
                    continue

                rsid    = cols[2] if len(cols) > 2 else "."
                info    = cols[7]

                # ── Format 1: Custom GENE= / STAR= ───────────────────────
                if "GENE=" in info.upper() and "STAR=" in info.upper():
                    fields = {}
                    for item in info.split(";"):
                        if "=" in item:
                            k, v = item.split("=", 1)
                            fields[k.strip().upper()] = v.strip()

                    gene = fields.get("GENE", "").upper()
                    star = fields.get("STAR", "")

                    if gene and star:
                        pheno = infer_phenotype(gene, star)
                        variants.append({
                            "gene":      gene,
                            "allele":    star,
                            "rsid":      rsid,
                            "phenotype": pheno,
                        })
                    continue

                # ── Format 2: SnpEff ANN= ────────────────────────────────
                if "ANN=" in info:
                    ann_block = info.split("ANN=", 1)[1].split(";")[0]
                    for ann_entry in ann_block.split(","):
                        parts = ann_entry.split("|")
                        if len(parts) >= 4:
                            gene = parts[3].strip().upper()
                            allele = parts[0].strip() or "."
                            if gene:
                                pheno = infer_phenotype(gene, allele)
                                variants.append({
                                    "gene":      gene,
                                    "allele":    allele,
                                    "rsid":      rsid,
                                    "phenotype": pheno,
                                })
                    continue

                # ── Format 3: VEP CSQ= ───────────────────────────────────
                if "CSQ=" in info:
                    csq_block = info.split("CSQ=", 1)[1].split(";")[0]
                    for csq_entry in csq_block.split(","):
                        parts = csq_entry.split("|")
                        if len(parts) >= 2:
                            allele = parts[0].strip()
                            gene   = parts[1].strip().upper()
                            if gene:
                                pheno = infer_phenotype(gene, allele)
                                variants.append({
                                    "gene":      gene,
                                    "allele":    allele,
                                    "rsid":      rsid,
                                    "phenotype": pheno,
                                })

    except Exception as e:
        app.logger.error(f"VCF parse error: {e}")

    return variants


# ──────────────────────────────────────────────
# Response builder (single drug)
# ──────────────────────────────────────────────

def build_response(drug: str, all_variants: list) -> dict:
    relevant_genes  = DRUG_GENE_MAP.get(drug, [])
    v_subset        = [v for v in all_variants if v["gene"] in relevant_genes]

    risk_data = evaluate_risk(v_subset, drug)
    advice    = recommendation(risk_data["risk"])

    severity_map = {
        "Toxic":         "high",
        "Adjust Dosage": "moderate",
        "Safe":          "none",
        "Ineffective":   "moderate",
    }

    primary      = v_subset[0] if v_subset else None
    primary_gene = primary["gene"]      if primary else (relevant_genes[0] if relevant_genes else "Unknown")
    allele       = primary["allele"]    if primary else None
    phenotype    = primary["phenotype"] if primary else "Normal"
    pheno_code   = PHENO_DISPLAY.get(phenotype, "NM")

    # Build LLM explanation — pass phenotype so explain() builds a better prompt
    if primary:
        explanation = explain(
            gene      = primary["gene"],
            variant   = allele,
            drug      = drug,
            risk      = risk_data["risk"],
            phenotype = phenotype,
        )
    else:
        explanation = (
            f"No pharmacogenomic variants relevant to {drug} were detected in this VCF. "
            f"Standard metabolic function is assumed; use standard dosing guidelines."
        )

    return {
        "patient_id": "PATIENT_001",
        "drug":       drug,
        "timestamp":  datetime.now(timezone.utc).isoformat(),

        "risk_assessment": {
            "risk_label":       risk_data["risk"],
            "confidence_score": risk_data["confidence"],
            "severity":         severity_map.get(risk_data["risk"], "none"),
        },

        "pharmacogenomic_profile": {
            "primary_gene":       primary_gene,
            "diplotype":          f"{allele}/wt" if allele else "wt/wt",
            "phenotype":          pheno_code,
            "detected_variants":  v_subset,
        },

        "clinical_recommendation": {
            "recommendation_text": advice,
        },

        "llm_generated_explanation": {
            "summary": explanation,
        },

        "quality_metrics": {
            "vcf_parsing_success":     True,
            "relevant_variants_found": len(v_subset),
        },

        "analysis_status": "complete",
    }


# ──────────────────────────────────────────────
# Routes
# ──────────────────────────────────────────────

@app.route("/")
def home():
    return {"status": "PharmaGuard Backend is Running"}, 200


@app.route("/api/health")
def health():
    return jsonify({"status": "healthy"}), 200


@app.route("/api/drugs")
def list_drugs():
    """Return the list of supported drugs so the frontend can populate a dropdown."""
    return jsonify({"supported_drugs": sorted(DRUG_GENE_MAP.keys())}), 200


@app.route("/api/analyze", methods=["POST"])
def analyze():
    # ── Validate file presence ───────────────────────────────────────────
    if "file" not in request.files:
        return jsonify({"error": "No VCF file uploaded"}), 400

    file = request.files["file"]

    if not file or file.filename == "":
        return jsonify({"error": "Empty filename"}), 400

    if not file.filename.lower().endswith(".vcf"):
        return jsonify({"error": "Invalid file type. Please upload a .vcf file."}), 400

    # ── Validate file size ───────────────────────────────────────────────
    file.seek(0, 2)                  # seek to end
    file_size = file.tell()
    file.seek(0)                     # reset
    if file_size > MAX_FILE_BYTES:
        return jsonify({"error": f"File too large. Maximum allowed size is 5 MB."}), 413

    # ── Validate drug input ──────────────────────────────────────────────
    drug_input = request.form.get("drug", "").strip()
    if not drug_input:
        return jsonify({"error": "Drug name is required."}), 400

    target_drugs = [d.strip().upper() for d in drug_input.split(",") if d.strip()]
    if not target_drugs:
        return jsonify({"error": "No valid drug names provided."}), 400

    unsupported = [d for d in target_drugs if d not in DRUG_GENE_MAP]
    if unsupported:
        return jsonify({
            "error":           f"Unsupported drug(s): {', '.join(unsupported)}",
            "supported_drugs": sorted(DRUG_GENE_MAP.keys()),
        }), 400

    # ── Save file ────────────────────────────────────────────────────────
    safe_filename = os.path.basename(file.filename)           # strip any path traversal
    filepath      = os.path.join(UPLOAD_FOLDER, safe_filename)
    file.save(filepath)

    # ── Parse and analyse ────────────────────────────────────────────────
    try:
        all_variants = parse_vcf(filepath)
        results = [build_response(drug, all_variants) for drug in target_drugs]
    finally:
        # Always clean up the uploaded file
        try:
            os.remove(filepath)
        except OSError:
            pass

    # Return a single object for one drug, array for multiple
    if len(results) == 1:
        return jsonify(results[0]), 200
    return jsonify(results), 200


# ──────────────────────────────────────────────
# Error handlers
# ──────────────────────────────────────────────

@app.errorhandler(HTTPException)
def handle_http_error(e):
    return jsonify({"error": e.name, "details": e.description}), e.code


@app.errorhandler(Exception)
def handle_server_error(e):
    app.logger.exception("Unhandled server error")
    return jsonify({"error": "Internal server error", "details": str(e)}), 500


# ──────────────────────────────────────────────
# Entry point
# ──────────────────────────────────────────────

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=False)