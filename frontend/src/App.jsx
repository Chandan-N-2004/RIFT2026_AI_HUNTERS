import { useState } from "react";

function App() {
  const [file, setFile] = useState(null);
  const [drug, setDrug] = useState("");
  const [dragActive, setDragActive] = useState(false);
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [darkMode, setDarkMode] = useState(false);
  const [themeFade, setThemeFade] = useState(false);


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

  const handleAnalyze = () => {
    if (!file || !drug) {
      alert("Upload file and enter drug name");
      return;
    }

    setLoading(true);

    setTimeout(() => {
      setResult({
        drug,
        risk: "Adjust Dosage",
        confidence: "92%",
        recommendation:
          "Based on detected genetic variants, dosage adjustment recommended."
      });
      setLoading(false);
    }, 2000);
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
        transition: "background 0.8s ease, color 0.6s ease"
      }}
     >
      {/* Fade Animation Wrapper */}
      <div
        style={{
          opacity: themeFade ? 0.4 : 1,
          transform: themeFade ? "scale(0.98)" : "scale(1)",
          transition: "all 0.4s ease"
        }}
      >
        
      </div>
      
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
          boxShadow: "0 2px 8px rgba(0,0,0,0.05)"
        }}
      >
        <h2 style={{ display: "flex", alignItems: "center", gap: "10px" }}>
          <span style={{ fontSize: "50px" }}>🧬</span>
          Pharma Guard
        </h2>


        <div style={{ display: "flex", alignItems: "center", gap: "20px" }}>
          <span style={{ cursor: "pointer" }}>Home</span>
          <span style={{ cursor: "pointer" }}>About</span>
          <span style={{ cursor: "pointer" }}>Contact</span>

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
              transition: "all 0.4s ease"
            }}
          >
            {darkMode ? "☀ Light" : "🌙 Dark"}
          </button>
        </div>

      </div>

      {/* HERO */}
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
            : "linear-gradient(135deg,#eef2f7,#dfe8f3)"

        }}
      >

        {/* Glow Background */}
        <div
          style={{
            position: "absolute",
            top: "-200px",
            left: "50%",
            transform: "translateX(-50%)",
            width: "600px",
            height: "600px",
            background:
              "radial-gradient(circle, rgba(30,136,229,0.25) 0%, transparent 70%)",
            filter: "blur(70px)",
            zIndex: 0
          }}
        />

        {/* Content Layer */}
        <div style={{ position: "relative", zIndex: 1 }}>

          <h1 style={{ fontSize: "clamp(32px,6vw,64px)" }}>
            PharmaGuard
          </h1>

          <p
            style={{
              fontSize: "clamp(16px,3vw,22px)",
              color: darkMode ? "#ccc" : "#555",
              maxWidth: "700px",
              margin: "0 auto"
            }}
          >
            AI-powered pharmacogenomic risk prediction platform
            for precision medicine and safer prescriptions.
          </p>

          {/* <img
            src="https://images.unsplash.com/photo-1581094794329-c8112a89af12"
            alt="AI Healthcare"
            style={{
              width: "100%",
              maxWidth: "600px",
              marginTop: "30px",
              borderRadius: "20px",
              boxShadow: "0 15px 30px rgba(0,0,0,0.1)"
            }}
          /> */}

        </div>
      </div>


      {/* UPLOAD CARD */}
      <div
        style={{
          display: "flex",
          justifyContent: "center",
          marginTop: "5px",
          padding: "0 20px"
        }}
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
            transition: "all 0.3s ease, box-shadow 0.3s ease",
            overflow: "hidden"
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
              background: dragActive
                ? "#1e88e520"
                : darkMode
                  ? "#2a2a2a"
                  : "#fafafa",
              color: darkMode ? "#ffffff" : "#000000",
              textAlign: "center",
              cursor: "pointer",
              marginBottom: "20px",
              transition: "all 0.4s ease"
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
              border: "1px solid #ccc"
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
              transition: "0.3s"
            }}
          >
            {loading ? "Analyzing..." : "Analyze"}
          </button>


          {result && (
            <div
              style={{
                marginTop: "20px",
                padding: "18px",
                borderRadius: "10px",
                background: "#f8fbff",
                border: "1px solid #dbeafe"
              }}
            >
              <h3>Drug Risk Assessment</h3>
              <p><b>Drug:</b> {result.drug}</p>
              <p><b>Risk:</b> {result.risk}</p>
              <p><b>Confidence:</b> {result.confidence}</p>
              <p>{result.recommendation}</p>
            </div>
          )}
        </div>
      </div>

      {/* FEATURES */}
      <div
        style={{
          padding: "80px 20px",
          textAlign: "center",
          background: darkMode ? "#222" : "white"

        }}
      >
        <h2 style={{ fontSize: "40px", marginBottom: "20px" }}> Why Pharma Guard ? </h2>


        <div
          style={{
            display: "flex",
            justifyContent: "center",
            flexWrap: "wrap",
            gap: "60px",
            marginTop: "50px"
          }}
        >
          {[
            {
              title: "🤖 AI Prediction",
              text: "ML-based genomic risk assessment."
            },
            {
              title: "🧬 Precision Medicine",
              text: "Personalized drug recommendations."
            },
            {
              title: "📊 Clinical Insights",
              text: "Reliable healthcare analytics."
            }
          ].map((item, i) => (
            <div
              key={i}
              style={{
                width: "360px",
                padding: "45px",
                borderRadius: "20px",
                background: darkMode ? "#1e1e1e" : "white",
                boxShadow: "0 12px 30px rgba(0,0,0,0.08)",
                transition: "all 0.3s ease",
                cursor: loading ? "not-allowed" : "pointer",
                transition: "all 0.3s ease, box-shadow 0.3s ease"
              }}
              onMouseEnter={(e) =>{
                e.currentTarget.style.transform = "translateY(-8px)";
                e.currentTarget.style.boxShadow =
                  "0 20px 50px rgba(0,0,0,0.15)";
              }}
              onMouseLeave={(e) =>{
                e.currentTarget.style.transform = "translateY(0)";
                e.currentTarget.style.boxShadow =
                  "0 12px 30px rgba(0,0,0,0.08)";
              }}
            >
              <h3 style={{
                fontSize: "26px",
                color: "#1565c0",
                marginBottom: "15px"
              }} >{item.title}</h3>
              <p style={{
                fontSize: "18px",
                color: darkMode ? "#ccc" : "#555",
                marginTop: "15px",
                lineHeight: "1.6"
              }}>{item.text}</p>
            </div>
          ))}
        </div>
      </div>

      {/* FOOTER */}
      <div
        style={{
          padding: "30px",
          textAlign: "center",
          background: darkMode ? "#181818" : "#f5f5f5"
        }}
      >
        Built for RIFT 2026 Hackathon
      </div>
    </div>
  );
}

export default App;
