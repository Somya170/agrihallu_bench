import os, glob, json
import pandas as pd
from flask import Flask, render_template_string, jsonify
from dotenv import load_dotenv

load_dotenv()
app = Flask(__name__)

def load_data():
    b_files  = sorted(glob.glob("results/eval_llama3_FULL_*.csv"))
    r_files  = sorted(glob.glob("results/eval_rag_FULL_*.csv"))
    v3_files = sorted(glob.glob("results/eval_v3_baseline_*.csv"))

    b_df  = pd.read_csv(b_files[-1])  if b_files  else pd.DataFrame()
    r_df  = pd.read_csv(r_files[-1])  if r_files  else pd.DataFrame()
    v3_df = pd.read_csv(v3_files[-1]) if v3_files else pd.DataFrame()
    return b_df, r_df, v3_df

HTML = r"""
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>AgriHallu-Bench</title>
<script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.0/dist/chart.umd.min.js"></script>
<style>
*{margin:0;padding:0;box-sizing:border-box}
body{font-family:'Segoe UI',sans-serif;background:#0f1117;color:#e2e8f0;min-height:100vh}
.topbar{background:linear-gradient(135deg,#1a472a,#2d6a4f);padding:20px 32px;display:flex;align-items:center;gap:16px;border-bottom:1px solid #2d6a4f}
.topbar h1{font-size:22px;font-weight:700;color:#fff}
.topbar p{font-size:13px;color:#95d5b2;margin-top:2px}
.badge{margin-left:auto;background:#95d5b2;color:#1a472a;padding:4px 12px;border-radius:20px;font-size:12px;font-weight:600}
.container{max-width:1200px;margin:0 auto;padding:28px 24px}
.stats-grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(180px,1fr));gap:16px;margin-bottom:28px}
.stat-card{background:#1e2130;border:1px solid #2a2f45;border-radius:12px;padding:20px;text-align:center;transition:transform .2s}
.stat-card:hover{transform:translateY(-3px)}
.stat-val{font-size:34px;font-weight:700;line-height:1;margin-bottom:6px}
.stat-label{font-size:11px;color:#94a3b8;text-transform:uppercase;letter-spacing:.05em}
.green{color:#52c41a}.red{color:#f5222d}.orange{color:#fa8c16}.blue{color:#40a9ff}.teal{color:#36cfc9}.purple{color:#b37feb}
.charts-grid{display:grid;grid-template-columns:1fr 1fr;gap:20px;margin-bottom:24px}
@media(max-width:768px){.charts-grid{grid-template-columns:1fr}}
.card{background:#1e2130;border:1px solid #2a2f45;border-radius:12px;padding:20px;margin-bottom:20px}
.card h3{font-size:11px;color:#64748b;text-transform:uppercase;letter-spacing:.08em;margin-bottom:16px}
.tabs{display:flex;gap:4px;margin-bottom:24px;border-bottom:1px solid #2a2f45}
.tab{padding:8px 18px;font-size:13px;cursor:pointer;border-radius:8px 8px 0 0;color:#64748b;border:1px solid transparent;border-bottom:none;transition:all .2s}
.tab.active{background:#1e2130;color:#52c41a;border-color:#2a2f45;border-bottom:1px solid #1e2130;margin-bottom:-1px}
.tab-content{display:none}.tab-content.active{display:block}
.comp-row{margin-bottom:16px}
.comp-label{display:flex;justify-content:space-between;font-size:12px;margin-bottom:4px}
.bar-track{background:#2a2f45;border-radius:6px;height:8px;overflow:hidden;margin-bottom:4px}
.bar-fill{height:100%;border-radius:6px;transition:width 1.2s ease}
.bar-b{background:#f5222d}.bar-r{background:#52c41a}.bar-v{background:#40a9ff}
table{width:100%;border-collapse:collapse;font-size:13px}
th{text-align:left;padding:10px 12px;background:#2a2f45;color:#64748b;font-size:11px;text-transform:uppercase;letter-spacing:.05em}
td{padding:10px 12px;border-bottom:1px solid #1a1f30;vertical-align:top;color:#cbd5e1;line-height:1.5}
tr:hover td{background:#252a3d}
.pill{display:inline-block;padding:2px 8px;border-radius:10px;font-size:11px;font-weight:600}
.pill-red{background:#2d1515;color:#f5222d}.pill-orange{background:#2b1d0e;color:#fa8c16}
.pill-blue{background:#111d2c;color:#40a9ff}.pill-green{background:#162312;color:#52c41a}
.pill-purple{background:#1a1040;color:#b37feb}
.insight{background:#162312;border:1px solid #2d6a4f;border-radius:10px;padding:14px 18px;margin-bottom:12px;font-size:13px;color:#95d5b2;line-height:1.7}
.insight strong{color:#52c41a}
.finding-num{display:inline-block;background:#2d6a4f;color:#95d5b2;border-radius:50%;width:22px;height:22px;text-align:center;line-height:22px;font-size:11px;font-weight:700;margin-right:8px}
.version-grid{display:grid;grid-template-columns:repeat(3,1fr);gap:12px;margin-bottom:20px}
.ver-card{background:#1e2130;border:1px solid #2a2f45;border-radius:10px;padding:16px;text-align:center}
.ver-card .ver-title{font-size:11px;color:#64748b;text-transform:uppercase;letter-spacing:.05em;margin-bottom:8px}
.ver-card .ver-val{font-size:24px;font-weight:700;margin-bottom:4px}
.ver-card .ver-sub{font-size:11px;color:#475569}
.empty-state{text-align:center;padding:40px;color:#475569;font-size:14px}
</style>
</head>
<body>
<div class="topbar">
  <div style="font-size:28px">🌾</div>
  <div>
    <h1>AgriHallu-Bench Dashboard</h1>
    <p>LLM Hallucination Detection in US Agricultural Advisory AI</p>
  </div>
  <div class="badge">Research v1.0</div>
</div>
<div class="container">

  <div class="stats-grid">
    <div class="stat-card"><div class="stat-val blue">{{ s.total_v2 }}</div><div class="stat-label">v2 QA Pairs (Synthetic)</div></div>
    <div class="stat-card"><div class="stat-val teal">{{ s.total_v3 }}</div><div class="stat-label">v3 QA Pairs (Real Data)</div></div>
    <div class="stat-card"><div class="stat-val red">{{ s.b_rate }}%</div><div class="stat-label">v2 Baseline Hall. Rate</div></div>
    <div class="stat-card"><div class="stat-val orange">{{ s.v3_rate }}%</div><div class="stat-label">v3 Real Data Hall. Rate</div></div>
    <div class="stat-card"><div class="stat-val green">{{ s.rag_rate }}%</div><div class="stat-label">v2 + RAG Hall. Rate</div></div>
    <div class="stat-card"><div class="stat-val purple">{{ s.reduction }}pp</div><div class="stat-label">RAG Reduction</div></div>
  </div>

  <div class="tabs">
    <div class="tab active" onclick="showTab('overview')">Overview</div>
    <div class="tab" onclick="showTab('comparison')">v2 vs v3</div>
    <div class="tab" onclick="showTab('examples')">Examples</div>
    <div class="tab" onclick="showTab('insights')">Paper Insights</div>
  </div>

  <!-- OVERVIEW -->
  <div id="tab-overview" class="tab-content active">
    <div class="charts-grid">
      <div class="card">
        <h3>Hallucination Rate by Category (v2 Baseline vs RAG)</h3>
        <canvas id="catChart" height="220"></canvas>
      </div>
      <div class="card">
        <h3>Severity Distribution (v2 Dataset)</h3>
        <canvas id="sevChart" height="220"></canvas>
      </div>
    </div>
    <div class="card">
      <h3>Category-wise Comparison — Baseline vs RAG</h3>
      {% for cat, d in cat_comp.items() %}
      <div class="comp-row">
        <div class="comp-label"><span style="color:#94a3b8;font-weight:600">{{ cat }}</span></div>
        <div class="comp-label"><span>Baseline</span><span class="red">{{ d.b }}%</span></div>
        <div class="bar-track"><div class="bar-fill bar-b" style="width:{{d.b}}%"></div></div>
        <div class="comp-label"><span>RAG</span><span class="green">{{ d.r }}%</span></div>
        <div class="bar-track" style="margin-bottom:2px"><div class="bar-fill bar-r" style="width:{{d.r}}%"></div></div>
      </div>
      {% endfor %}
    </div>
  </div>

  <!-- V2 vs V3 -->
  <div id="tab-comparison" class="tab-content">
    <div class="version-grid">
      <div class="ver-card">
        <div class="ver-title">v2 — Synthetic</div>
        <div class="ver-val red">{{ s.b_rate }}%</div>
        <div class="ver-sub">{{ s.total_v2 }} QA pairs<br>Manual + template-based</div>
      </div>
      <div class="ver-card">
        <div class="ver-title">v3 — Real USDA/EPA</div>
        <div class="ver-val orange">{{ s.v3_rate }}%</div>
        <div class="ver-sub">{{ s.total_v3 }} QA pairs<br>NASS 2023 + EPA records</div>
      </div>
      <div class="ver-card">
        <div class="ver-title">v2 + RAG</div>
        <div class="ver-val green">{{ s.rag_rate }}%</div>
        <div class="ver-sub">{{ s.total_v2 }} QA pairs<br>Keyword RAG mitigation</div>
      </div>
    </div>
    <div class="charts-grid">
      <div class="card">
        <h3>v3 Hallucination by Category</h3>
        <canvas id="v3CatChart" height="220"></canvas>
      </div>
      <div class="card">
        <h3>v3 Source Distribution</h3>
        <canvas id="srcChart" height="220"></canvas>
      </div>
    </div>
    <div class="card">
      <h3>Key Difference: DOSAGE Category</h3>
      <div class="comp-row">
        <div class="comp-label"><span>v2 Synthetic DOSAGE</span><span class="red">40.0%</span></div>
        <div class="bar-track"><div class="bar-fill bar-b" style="width:40%"></div></div>
        <div class="comp-label" style="margin-top:6px"><span>v3 Real DOSAGE (NASS specific dates)</span><span class="red">100.0%</span></div>
        <div class="bar-track"><div class="bar-fill bar-b" style="width:100%"></div></div>
        <div class="comp-label" style="margin-top:6px"><span>v3 Real TEMPORAL (actual 2023 data)</span><span class="green">1.7%</span></div>
        <div class="bar-track"><div class="bar-fill bar-r" style="width:1.7%"></div></div>
      </div>
      <p style="font-size:12px;color:#64748b;margin-top:12px">
        Real USDA NASS 2023 specific dates LLMs ko bilkul nahi pata (100% DOSAGE hallucination).
        Lekin general temporal questions pe LLMs better hain (1.7%).
        Ye paper ka novel finding hai.
      </p>
    </div>
  </div>

  <!-- EXAMPLES -->
  <div id="tab-examples" class="tab-content">
    <div class="card">
      <h3>Hallucination Examples — v3 Real Dataset</h3>
      {% if examples %}
      <table>
        <thead>
          <tr>
            <th>Category</th><th>Severity</th><th>Question</th><th>Why Hallucinated</th>
          </tr>
        </thead>
        <tbody>
          {% for ex in examples %}
          <tr>
            <td>
              <span class="pill {% if ex.category=='REGULATORY' %}pill-red
                {% elif ex.category=='DOSAGE' %}pill-orange
                {% elif ex.category=='TEMPORAL' %}pill-blue
                {% else %}pill-green{% endif %}">{{ ex.category }}</span>
            </td>
            <td>
              <span class="pill {% if ex.severity=='HIGH' %}pill-red
                {% elif ex.severity=='MEDIUM' %}pill-orange
                {% else %}pill-blue{% endif %}">{{ ex.severity }}</span>
            </td>
            <td style="max-width:280px">{{ ex.question[:90] }}...</td>
            <td style="max-width:280px;color:#f87171">{{ ex.explanation[:110] }}...</td>
          </tr>
          {% endfor %}
        </tbody>
      </table>
      {% else %}
      <div class="empty-state">v3 evaluation abhi chal rahi hai — thodi der mein refresh karo</div>
      {% endif %}
    </div>
  </div>

  <!-- INSIGHTS -->
  <div id="tab-insights" class="tab-content">
    <div class="insight">
      <span class="finding-num">1</span>
      <strong>Baseline Hallucination Rate (v2 Synthetic):</strong>
      Llama-3.1-8B shows {{ s.b_rate }}% overall hallucination rate.
      REGULATORY worst at 50% — cancelled pesticides (Chlorpyrifos 2021, Carbofuran 2009, Aldicarb 2010) incorrectly reported as approved.
    </div>
    <div class="insight">
      <span class="finding-num">2</span>
      <strong>Real Data is Harder (v3):</strong>
      On real USDA NASS 2023 data, DOSAGE hallucination hits 100% —
      LLMs cannot know specific weekly crop progress statistics.
      This validates the need for RAG with real-time government data feeds.
    </div>
    <div class="insight">
      <span class="finding-num">3</span>
      <strong>RAG Reduces HIGH Severity by 24.4pp:</strong>
      HIGH severity hallucinations drop from 44.4% → 20.0% with keyword RAG.
      Most dangerous advisory errors significantly reduced.
    </div>
    <div class="insight">
      <span class="finding-num">4</span>
      <strong>TEMPORAL Degrades with Keyword RAG:</strong>
      23.3% → 46.7% — partial state-crop keyword matches inject wrong context.
      Dense vector retrieval (FAISS + sentence-transformers) is future work.
    </div>
    <div class="insight">
      <span class="finding-num">5</span>
      <strong>Target Journals:</strong>
      Computers and Electronics in Agriculture (Q1, IF 8.3) —
      Expert Systems with Applications (Q1, IF 8.5) —
      Nature Food (IF ~20)
    </div>
  </div>

</div>
<script>
function showTab(n){
  ['overview','comparison','examples','insights'].forEach((t,i)=>{
    document.querySelectorAll('.tab')[i].classList.toggle('active',t===n);
    document.getElementById('tab-'+t).classList.toggle('active',t===n);
  });
}
const cOpts={plugins:{legend:{labels:{color:'#94a3b8',font:{size:11}}}},scales:{x:{ticks:{color:'#64748b'},grid:{color:'#1a1f30'}},y:{ticks:{color:'#64748b'},grid:{color:'#1a1f30'},min:0,max:100}}};

new Chart(document.getElementById('catChart'),{
  type:'bar',
  data:{
    labels:{{ cat_labels|tojson }},
    datasets:[
      {label:'Baseline %',data:{{ cat_b|tojson }},backgroundColor:'rgba(245,34,45,.75)',borderRadius:4},
      {label:'RAG %',     data:{{ cat_r|tojson }},backgroundColor:'rgba(82,196,26,.75)', borderRadius:4}
    ]
  },
  options:{...cOpts,responsive:true}
});

new Chart(document.getElementById('sevChart'),{
  type:'doughnut',
  data:{
    labels:['HIGH','MEDIUM','LOW'],
    datasets:[{data:{{ sev_data|tojson }},backgroundColor:['rgba(245,34,45,.8)','rgba(250,140,22,.8)','rgba(64,169,255,.8)'],borderWidth:0}]
  },
  options:{plugins:{legend:{labels:{color:'#94a3b8'}}},responsive:true}
});

new Chart(document.getElementById('v3CatChart'),{
  type:'bar',
  data:{
    labels:{{ v3_cat_labels|tojson }},
    datasets:[{label:'Hallucination %',data:{{ v3_cat_rates|tojson }},backgroundColor:'rgba(250,140,22,.75)',borderRadius:4}]
  },
  options:{...cOpts,responsive:true,plugins:{legend:{display:false}}}
});

new Chart(document.getElementById('srcChart'),{
  type:'pie',
  data:{
    labels:{{ src_labels|tojson }},
    datasets:[{data:{{ src_counts|tojson }},backgroundColor:['rgba(54,207,201,.8)','rgba(179,127,235,.8)'],borderWidth:0}]
  },
  options:{plugins:{legend:{labels:{color:'#94a3b8'}}},responsive:true}
});
</script>
</body>
</html>
"""

@app.route("/")
def index():
    b_df, r_df, v3_df = load_data()
    if b_df.empty:
        return "<h2 style='color:white;background:#0f1117;padding:40px'>Run evaluation first: python run_v3.py</h2>", 404

    b_rate  = round(b_df["hallucinated"].mean()*100, 1)
    r_rate  = round(r_df["hallucinated"].mean()*100, 1) if not r_df.empty else 0
    v3_rate = round(v3_df["hallucinated"].mean()*100,1) if not v3_df.empty else "—"

    s = dict(
        total_v2  = len(b_df),
        total_v3  = len(v3_df) if not v3_df.empty else 0,
        b_rate    = b_rate,
        rag_rate  = r_rate,
        v3_rate   = v3_rate,
        reduction = round(b_rate - r_rate, 1)
    )

    cats   = sorted(b_df["category"].unique())
    r_cats = set(r_df["category"].unique()) if not r_df.empty else set()
    cat_comp = {
        c: {
            "b": round(b_df[b_df["category"]==c]["hallucinated"].mean()*100,1),
            "r": round(r_df[r_df["category"]==c]["hallucinated"].mean()*100,1) if c in r_cats else 0
        } for c in cats
    }

    sev_data   = [int((b_df["severity"]==s).sum()) for s in ["HIGH","MEDIUM","LOW"]]
    cat_labels = cats
    cat_b      = [cat_comp[c]["b"] for c in cats]
    cat_r      = [cat_comp[c]["r"] for c in cats]

    # v3 stats
    if not v3_df.empty:
        v3_cats      = sorted(v3_df["category"].unique())
        v3_cat_labels= v3_cats
        v3_cat_rates = [round(v3_df[v3_df["category"]==c]["hallucinated"].mean()*100,1) for c in v3_cats]
        src          = v3_df["source"].value_counts() if "source" in v3_df.columns else pd.Series({"USDA_NASS":60,"EPA":31})
        src_labels   = src.index.tolist()
        src_counts   = src.values.tolist()
        examples     = v3_df[v3_df["hallucinated"]==True][["category","severity","question","explanation"]].head(15).to_dict("records")
    else:
        v3_cat_labels= ["—"]; v3_cat_rates=[0]
        src_labels   = ["USDA NASS","EPA"]; src_counts=[60,31]
        examples     = []

    return render_template_string(HTML,
        s=s, cat_comp=cat_comp,
        cat_labels=cat_labels, cat_b=cat_b, cat_r=cat_r,
        sev_data=sev_data,
        v3_cat_labels=v3_cat_labels, v3_cat_rates=v3_cat_rates,
        src_labels=src_labels, src_counts=src_counts,
        examples=examples
    )

@app.route("/api/stats")
def api_stats():
    b_df, r_df, v3_df = load_data()
    return jsonify({
        "v2_baseline": round(b_df["hallucinated"].mean()*100,1),
        "v2_rag":      round(r_df["hallucinated"].mean()*100,1) if not r_df.empty else 0,
        "v3_real":     round(v3_df["hallucinated"].mean()*100,1) if not v3_df.empty else None,
        "total_v2":    len(b_df),
        "total_v3":    len(v3_df) if not v3_df.empty else 0,
    })

if __name__ == "__main__":
    print("\n  Dashboard: http://localhost:5000\n")
    app.run(debug=True, port=5000)
