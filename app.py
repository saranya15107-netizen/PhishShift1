import json
from pathlib import Path
import pandas as pd
import streamlit as st
from risk_cues import extract_risk_cues, normalize_template
from train_model import ensure_artifacts, predict_message

ROOT=Path(__file__).parent
DATA=ROOT/"data"; MODELS=ROOT/"models"
st.set_page_config(page_title="PhishShift | Message Risk Scanner",page_icon="🛡️",layout="wide")
st.markdown("""<style>
.stApp{background:#f5f8fc;color:#152b4a}
section[data-testid="stSidebar"]{background:#14243e}
section[data-testid="stSidebar"] *{color:#f4f8ff!important}
.block-container{padding-top:1.4rem;max-width:1500px}
.hero{padding:1.1rem 1.3rem;border-radius:16px;background:linear-gradient(120deg,#eaf2ff,#e9fbf7);border:1px solid #d7e6f6;margin-bottom:1rem}
</style>""",unsafe_allow_html=True)
with st.sidebar:
    st.markdown("## 🛡️ PhishShift")
    st.caption("Message Risk Scanner")
    page=st.radio("NAVIGATION",["Live Message Scanner","Model Performance","Dataset Info","About"])
    st.divider(); st.success("App interface ready"); st.caption("Smarter detection. Safer inbox.")
st.markdown('<div class="hero"><h1 style="margin:0;color:#163b70">PhishShift — Message Risk Scanner</h1><p style="margin:.35rem 0 0;color:#526a87">Rule-based risk cues + machine-learning models for phishing awareness</p></div>',unsafe_allow_html=True)
@st.cache_resource
def get_models(): return ensure_artifacts(str(DATA),str(MODELS))
models=get_models()
if page=="Live Message Scanner":
    left,right=st.columns([1,1.05],gap="large")
    examples={
      "Phishing — account locked":"URGENT: Your bank account is locked. Verify your identity immediately to restore access: http://secure-account-verify.example.com/login",
      "Legitimate — payroll update":"Hello team, the monthly payroll statement is available in the employee portal. Please review it during office hours if you have questions.",
      "Phishing — parcel fee":"Your parcel is on hold. Pay a delivery fee now to avoid return: http://parcel-fee-check.example.com/pay",
      "Legitimate — class announcement":"Reminder: the database systems lecture begins at 10 AM tomorrow in Room 204. Please bring your notes."
    }
    with left:
        st.subheader("✉️ Scan a Message")
        preset=st.selectbox("Preset examples",["Custom message"]+list(examples))
        msg=st.text_area("Message text",value=examples.get(preset,""),height=200,placeholder="Paste a message here...")
        scan=st.button("🔎 Scan Message",type="primary",use_container_width=True)
        if scan:
            if not msg.strip(): st.warning("Please enter a message first.")
            else: st.session_state["scan"]={"message":msg,"result":predict_message(msg,models)}
    with right:
        st.subheader("📊 Risk Result")
        saved=st.session_state.get("scan")
        if saved:
            r=saved["result"]
            if r["label"]=="PHISHING": st.error("🚨 "+r["label"])
            elif r["label"]=="REVIEW": st.warning("⚠️ REVIEW — uncertain message")
            else: st.success("✅ "+r["label"])
            c1,c2,c3=st.columns(3)
            c1.metric("Risk score",f'{r["risk_score"]:.2f} / 1.00')
            c2.metric("Model",r["model"])
            c3.metric("Rule cues",r["cue_count"])
            st.progress(float(r["risk_score"]))
            st.caption("Prototype estimate only; this is not a guarantee that a message is safe.")
            st.markdown("#### Key Indicators")
            cues=extract_risk_cues(saved["message"])
            if cues:
                st.dataframe(pd.DataFrame([{"Risk cue":x["category"].replace("_"," ").title(),"Severity":x["severity"],"Evidence":x["snippet"],"Weight":x["weight"]} for x in cues]),use_container_width=True,hide_index=True)
            else: st.info("No configured cues detected. This does not guarantee safety.")
            st.markdown("#### Message Information")
            st.write(f'**Length:** {len(saved["message"])} characters')
            st.write("**Normalized template:**")
            st.code(normalize_template(saved["message"])[:1000])
        else:
            st.info("Choose a preset or paste a message, then click Scan Message.")
            st.write("The result will include a risk label, score, model summary, detected cues, and normalized template.")
    st.divider(); st.subheader("💡 How It Works")
    a,b,c=st.columns(3)
    a.info("**1. Inspect**\n\nRules look for urgency, credential requests, suspicious links and threats.")
    b.info("**2. Compare**\n\nTF-IDF features are evaluated by two machine-learning models.")
    c.info("**3. Explain**\n\nDetected cues help users review a message more carefully.")
elif page=="Model Performance":
    st.subheader("📈 Model Performance")
    p=MODELS/"evaluation_metrics.json"
    if p.exists():
        m=json.loads(p.read_text(encoding="utf-8"))
        df=pd.DataFrame([{"Model":n,**v} for n,v in m.items()])
        for col in ["accuracy","precision","recall","f1"]: df[col]=df[col].map(lambda x:f"{x:.1%}")
        st.dataframe(df,use_container_width=True,hide_index=True)
        st.caption("Scores use a small synthetic demonstration dataset; they are not real-world benchmarks.")
    else: st.warning("Metrics not generated yet. Refresh the page.")
elif page=="Dataset Info":
    st.subheader("🗂️ Dataset Information")
    mp=DATA/"dataset_metadata.json"; dp=DATA/"synthetic_phishing_dataset.csv"
    if mp.exists(): st.json(json.loads(mp.read_text(encoding="utf-8")))
    if dp.exists():
        df=pd.read_csv(dp); st.write(f"Dataset rows: **{len(df)}**"); st.dataframe(df.head(20),use_container_width=True,hide_index=True)
    st.warning("The included dataset is synthetic and for education/demo use only.")
else:
    st.subheader("About PhishShift")
    st.write("An educational prototype that identifies potential phishing-message risk cues in email and SMS text.")
    st.markdown("**Technology stack:** Python, Streamlit, pandas, scikit-learn, TF-IDF, Logistic Regression, Multinomial Naive Bayes.")
    st.warning("Do not enter passwords, confidential messages, or sensitive personal information. Always verify suspicious messages using an official channel.")
