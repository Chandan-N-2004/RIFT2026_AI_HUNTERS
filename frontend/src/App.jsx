import { useState } from "react";

function App() {
  const [file, setFile] = useState(null);
  const [drug, setDrug] = useState("");
  const [dragActive, setDragActive] = useState(false);
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [darkMode, setDarkMode] = useState(false);
  const [themeFade, setThemeFade] = useState(false);
  const [expanded, setExpanded] = useState(false);
  const [activeSection, setActiveSection] = useState(null);
  
  const handleDrag = (e) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.type === "dragenter" || e.type === "dragover") {
      setDragActive(true);
    } else {
      setDragActive(false);
    }
  };

  const handleDrop = (e) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);
    if (e.dataTransfer.files?.[0]) {
      setFile(e.dataTransfer.files[0]);
    }
  };

  const getRiskColor = (label) => {
    if (!label) return "#999";
    const l = label.toLowerCase();
    if (l.includes("safe")) return "#4caf50";
    if (l.includes("adjust")) return "#ff9800";
    if (l.includes("toxic") || l.includes("ineffective")) return "#f44336";
    return "#999";
  };

  const downloadJSON = () => {
    if (!result) return;
    const blob = new Blob([JSON.stringify(result, null, 2)], { type: "application/json" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = "Pharma_Guard_result.json";
    a.click();
  };

  const handleAnalyze = async () => {
    if (!file || !drug) {
      alert("Upload VCF file and enter drug name");
      return;
    }
    const formData = new FormData();
    formData.append("file", file);
    formData.append("drug", drug);
    try {
      setLoading(true);
      const response = await fetch("http://localhost:5000/api/analyze", {
        method: "POST",
        body: formData,
      });
      if (!response.ok) {
        const errorData = await response.json();
        alert(errorData.error || "Backend error");
        return;
      }
      const data = await response.json();
      setResult(data);
    } catch (error) {
      alert("Unable to analyze file. Check if backend is running.");
      console.error(error);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div
      style={{
        fontFamily: "Poppins, sans-serif",
        overflowX: "hidden",
        minHeight: "100vh",
        background: darkMode
          ? "linear-gradient(135deg, #0f2027, #203a43, #2c5364)"
          : "linear-gradient(135deg,#eef2f7,#dfe8f3)",
        color: darkMode ? "#ffffff" : "#000000",
        transition: "background 0.8s ease, color 0.6s ease",
      }}
    >
      {/* Fade Animation Wrapper - Corrected Scope */}
      <div
        style={{
          opacity: themeFade ? 0.4 : 1,
          transform: themeFade ? "scale(0.98)" : "scale(1)",
          transition: "all 0.4s ease",
        }}
      >
        {/* NAVBAR */}
        <div
          style={{
            width: "100%",
            padding: "20px 30px",
            display: "flex",
            flexWrap: "wrap",
            justifyContent: "space-between",
            alignItems: "center",
            background: darkMode ? "#1e1e1e" : "white",
            boxShadow: "0 2px 8px rgba(0,0,0,0.05)",
          }}
        >
          <h2 style={{ display: "flex", alignItems: "center", gap: "10px" }}>
            <span style={{ fontSize: "50px" }}>🧬</span>
            Pharma Guard
          </h2>
          <div style={{ display: "flex", alignItems: "center", gap: "20px" }}>
           <div style={{ display: "flex", gap: "20px" }}>
              {["home", "about", "contact"].map((item) => (
                <span
                  key={item}
                  onClick={() =>
                    setActiveSection(
                      activeSection === item ? null : item
                    )
                  }
                  style={{
                    cursor: "pointer",
                    fontWeight: "500",
                    textTransform: "capitalize"
                  }}
                >
                  {item}
                </span>
              ))}
            </div>
            <button
              onClick={() => {
                setThemeFade(true);
                setTimeout(() => {
                  setDarkMode(!darkMode);
                  setThemeFade(false);
                }, 200);
              }}
              style={{
                padding: "8px 16px",
                borderRadius: "25px",
                border: "none",
                cursor: "pointer",
                background: darkMode ? "#ffffff" : "#121212",
                color: darkMode ? "#121212" : "#ffffff",
                fontWeight: "bold",
                transition: "all 0.4s ease",
              }}
            >
              {darkMode ? "☀ Light" : "🌙 Dark"}
            </button>
          </div>
        </div>

        {/* Animated Slide Section */}
<div
  style={{
    maxHeight: activeSection ? "300px" : "0px",
    overflow: "hidden",
    textAlign: "center",
    transition: "all 0.5s ease",
    background: darkMode ? "#111827" : "#f9fafb",
    padding: activeSection ? "30px" : "0px 30px"
  }}
>
  {activeSection === "home" && (
    <div>
      <h3>Welcome to PharmaGuard</h3>
      <p>
        PharmaGuard is an AI-powered pharmacogenomic
        risk prediction platform helping clinicians
        make safer, personalized medication decisions.
      </p>
    </div>
  )}

  {activeSection === "about" && (
    <div>
      <h3>About Us</h3>
      <p>
        Built for RIFT 2026 Hackathon, Pharma Guard
        integrates genomics, AI risk modeling, and
        explainable clinical recommendations to enable
        precision medicine.
      </p>
    </div>
  )}

     <span
  onMouseEnter={(e) =>
    (e.target.style.color = "#3b82f6")
  }
  onMouseLeave={(e) =>
    (e.target.style.color = darkMode ? "#fff" : "#000")
  }
>
  Home
</span>

        {activeSection === "contact" && (
          <div>
            <h3>Contact</h3>
            <p>
              📧 Email: pharmaguard@rift2026.ai  
              <br />
              📍 Bengaluru, India  
              <br />
              🤖 Built by AI Hunters Team
            </p>
          </div>
        )}
      </div>

        {/* HERO SECTION */}
        <div
          style={{
            width: "100%",
            padding: "100px 20px",
            textAlign: "center",
            position: "relative",
            overflow: "hidden",
            background: darkMode
              ? "linear-gradient(135deg,#1e1e1e,#2c2c2c)"
              : "linear-gradient(135deg,#eef2f7,#dfe8f3)",
          }}
        >
          <div
            style={{
              position: "absolute",
              top: "-200px",
              left: "50%",
              transform: "translateX(-50%)",
              width: "600px",
              height: "600px",
              background: "radial-gradient(circle, rgba(30,136,229,0.25) 0%, transparent 70%)",
              filter: "blur(70px)",
              zIndex: 0,
            }}
          />
          <div style={{ position: "relative", zIndex: 1 }}>
            <h1 style={{ fontSize: "clamp(32px,6vw,64px)" }}>Pharma Guard</h1>
            <p
              style={{
                fontSize: "clamp(16px,3vw,22px)",
                color: darkMode ? "#ccc" : "#555",
                maxWidth: "700px",
                margin: "0 auto",
              }}
            >
              AI-Powered pharmacogenomic risk prediction platform for precision medicine and safer
              prescriptions.
            </p>
          </div>
        </div>

        {/* UPLOAD CARD */}
        <div
          style={{ display: "flex", justifyContent: "center", marginTop: "5px", padding: "0 20px" }}
        >
          <div
            style={{
              width: "100%",
              maxWidth: "600px",
              background: darkMode ? "#1e1e1e" : "white",
              color: darkMode ? "#ffffff" : "#000000",
              padding: "40px",
              borderRadius: "28px",
              boxShadow: "0 20px 50px rgba(0,0,0,0.10)",
              transition: "all 0.3s ease",
              overflow: "hidden",
            }}
          >
            <h2>🧬 Upload Genetic File (.VCF)</h2>
            <label
              onDragEnter={handleDrag}
              onDragLeave={handleDrag}
              onDragOver={handleDrag}
              onDrop={handleDrop}
              style={{
                display: "block",
                padding: "40px",
                borderRadius: "22px",
                border: dragActive
                  ? "2px dashed #1e88e5"
                  : darkMode
                  ? "2px dashed #555"
                  : "2px dashed #ccc",
                background: dragActive ? "#1e88e520" : darkMode ? "#2a2a2a" : "#fafafa",
                color: darkMode ? "#ffffff" : "#000000",
                textAlign: "center",
                cursor: "pointer",
                marginBottom: "20px",
                transition: "all 0.4s ease",
              }}
            >
              {file ? file.name : "Drag & Drop VCF File Here or click"}
              <input
                type="file"
                accept=".vcf"
                onChange={(e) => setFile(e.target.files[0])}
                style={{ display: "none" }}
              />
            </label>
            <h3>Drug Name</h3>
            <input
              type="text"
              placeholder="CODEINE, WARFARIN..."
              value={drug}
              onChange={(e) => setDrug(e.target.value)}
              style={{
                width: "100%",
                padding: "14px",
                borderRadius: "10px",
                border: "1px solid #ccc",
              }}
            />
            <button
              onClick={handleAnalyze}
              disabled={loading}
              style={{
                width: "100%",
                marginTop: "20px",
                padding: "20px",
                borderRadius: "10px",
                border: "none",
                background: "linear-gradient(90deg,#1e88e5,#1565c0)",
                color: "white",
                fontWeight: "bold",
                cursor: loading ? "not-allowed" : "pointer",
                transition: "0.3s",
              }}
            >
              {loading ? "Analyzing..." : "Analyze"}
            </button>

            {result && (
              <div
                style={{
                  marginTop: "20px",
                  padding: "20px",
                  borderRadius: "15px",
                  background: darkMode ? "#2a2a2a" : "#f8fbff",
                }}
              >
                <h3>Drug Risk Assessment</h3>
                <p><b>Drug:</b> {result.drug}</p>
                <p>
                  <b>Risk:</b>{" "}
                  <span
                    style={{
                      color: getRiskColor(result.risk_assessment?.risk_label),
                      fontWeight: "bold",
                    }}
                  >
                    {result.risk_assessment?.risk_label || "Unknown"}
                  </span>
                </p>
                <p><b>Confidence:</b> {result.risk_assessment?.confidence_score}</p>
                <p><b>Severity:</b> {result.risk_assessment?.severity}</p>
                <hr />

                {/* DASHBOARD GRAPH */}
<div style={{ marginTop: 25 }}>
  <h4>Risk Visualization</h4>

  <div
    style={{
      height: "14px",
      borderRadius: "10px",
      background: "#e5e7eb",
      overflow: "hidden",
      marginTop: "8px"
    }}
  >
    <div
      style={{
        width:
          result.risk_assessment?.risk_label === "Safe"
            ? "30%"
            : result.risk_assessment?.risk_label === "Adjust Dosage"
            ? "60%"
            : "90%",
        height: "100%",
        background: getRiskColor(
          result.risk_assessment?.risk_label
        ),
        transition: "width 0.6s ease"
      }}
    />
  </div>

  <p style={{ fontSize: "13px", marginTop: 6 , textAlign: "right", color: darkMode ? "#ccc" : "#555" }}>
    Risk intensity indicator
  </p>
</div>

                {expanded && (
                  <div style={{ marginTop: "20px" }}>
                    <h4>🧬 Pharmacogenomic Profile</h4>
                    <p><b>Primary Gene:</b> {result.pharmacogenomic_profile?.primary_gene || "N/A"}</p>
                    <p><b>Phenotype:</b> {result.pharmacogenomic_profile?.phenotype || "N/A"}</p>
                    <hr />
                    <h4>💊 Clinical Recommendation</h4>
                    <p>{result.clinical_recommendation?.recommendation_text || "N/A"}</p>
                    <hr />
                    <h4>🤖 AI Explanation</h4>
                    <p>{result.llm_generated_explanation?.summary || "N/A"}</p>
                  </div>
                )}
                <div style={{ display: "flex", justifyContent: "center", gap: "10px", marginTop: "20px", flexWrap: "wrap" }}>
                  <button
                    onClick={() => setExpanded(!expanded)}
                    style={{ padding: "10px 15px", borderRadius: "20px", border: "none", cursor: "pointer", background: "#e5e7eb" }}
                  >
                    {expanded ? "Hide Details" : "Show Details"}
                  </button>
                  <button
                    onClick={() => {
                      navigator.clipboard.writeText(JSON.stringify(result, null, 2));
                      alert("Results copied to clipboard! ✅");
                    }}
                    style={{ padding: "10px 15px", borderRadius: "20px", border: "none", cursor: "pointer", background: "#333", color: "white" }}
                  >
                    📋 Copy Results
                  </button>
                  <button
                    onClick={downloadJSON}
                    style={{ padding: "10px 15px", borderRadius: "20px", border: "none", cursor: "pointer", background: "green", color: "white" }}
                  >
                    Download JSON
                  </button>
                </div>
              </div>
            )}
          </div>
        </div>

        {/* FEATURES - With Fixed Animations */}
        <div
          style={{ padding: "80px 20px", textAlign: "center", background: darkMode ? "#222" : "white" }}
        >
          <h2 style={{ fontSize: "40px", marginBottom: "20px" }}> Why Pharma Guard? </h2>
          <div
            style={{
              display: "flex",
              justifyContent: "center",
              flexWrap: "wrap",
              gap: "40px",
              marginTop: "50px",
            }}
          >
            {[
              { title: "🤖 AI Prediction", text: "Advanced machine learning models analyze genomic variants to predict drug response risks, helping clinicians avoid adverse reactions before treatment begins." },
              { title: "🧬 Precision Medicine", text: "PharmaGuard tailors medication recommendations based on individual genetic profiles, enabling safer, more effective personalized healthcare decisions." },
              { title: "📊 Clinical Insights", text: "Actionable pharmacogenomic insights support clinical decision-making with clear risk assessment, dosage guidance, and evidence-based recommendations." },
            ].map((item, i) => (
              <div
                key={i}
                style={{
                  width: "300px",
                  padding: "30px",
                  borderRadius: "20px",
                  background: darkMode ? "rgba(255,255,255,0.05)" : "#ffffff",
                  boxShadow: "0 10px 30px rgba(0,0,0,0.08)",
                  transition: "transform 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275), box-shadow 0.4s ease",
                  cursor: "pointer",
                }}

                
                onMouseEnter={(e) => {
                  e.currentTarget.style.transform = "translateY(-10px) scale(1.03)";
                  e.currentTarget.style.boxShadow = "0 20px 40px rgba(0,0,0,0.15)";
                }}
                onMouseLeave={(e) => {
                  e.currentTarget.style.transform = "translateY(0) scale(1)";
                  e.currentTarget.style.boxShadow = "0 10px 30px rgba(0,0,0,0.08)";
                }}
              >
                
                <h3 style={{ fontSize: "22px", color: "#1e88e5", marginBottom: "10px" }}>{item.title}</h3>
                <p style={{ color: darkMode ? "#ccc" : "#555" }}>{item.text}</p>
              </div>
            ))}
          </div>
        </div>

        {/* FOOTER */}
        <div style={{ padding: "30px", textAlign: "center", background: darkMode ? "#181818" : "#f5f5f5" }}>
          Built for RIFT 2026 Hackathon
        </div>
        


      </div>
    </div>
  );
}

export default App;