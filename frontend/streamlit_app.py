import streamlit as st
import requests

API_URL = "http://localhost:8080/api"

st.set_page_config(page_title="ComplianceIQ", page_icon="⚖️", layout="wide")


st.markdown("""
<style>
.risk-badge-LOW { background:#22c55e; color:white; padding:4px 12px; border-radius:20px; font-weight:bold; }
.risk-badge-MEDIUM { background:#f59e0b; color:white; padding:4px 12px; border-radius:20px; font-weight:bold; }
.risk-badge-HIGH { background:#ef4444; color:white; padding:4px 12px; border-radius:20px; font-weight:bold; }
.risk-badge-CRITICAL { background:#7c3aed; color:white; padding:4px 12px; border-radius:20px; font-weight:bold; }
.risk-clause { border-left: 4px solid #ef4444; background:#fef2f2; padding:12px 16px; border-radius:4px; margin:8px 0; color:#1f2937; }
.recommendation { border-left: 4px solid #22c55e; background:#f0fdf4; padding:12px 16px; border-radius:4px; margin:8px 0; color:#1f2937; }
.key-term { background:#fef08a; color:#713f12; padding:4px 12px; border-radius:20px; margin:4px; display:inline-block; font-size:14px; }
.doc-info-row { display:flex; justify-content:space-between; padding:10px 0; border-bottom:1px solid #e5e7eb; }
.section-header { background:#1e3a5f; color:white; padding:12px 16px; border-radius:8px; font-weight:bold; margin:16px 0 8px 0; font-size:16px; }
</style>
""", unsafe_allow_html=True)

st.title("⚖️ ComplianceIQ — Intelligent Compliance Assistant")
st.caption("Upload regulatory documents and company policies. Ask compliance questions instantly.")


with st.sidebar:
    st.header("📁 Upload Documents")
    doc_type = st.selectbox("Document Type", ["regulation", "policy"])
    uploaded_file = st.file_uploader("Choose a file", type=["pdf", "txt", "png", "jpg"])

    if st.button("Upload & Index") and uploaded_file:
        with st.spinner("Indexing document..."):
            response = requests.post(
                f"{API_URL}/upload",
                files={"file": (uploaded_file.name, uploaded_file.getvalue(), uploaded_file.type)},
                data={"doc_type": doc_type}
            )
            if response.status_code == 200:
                data = response.json()
                st.success(f"✅ {data['chunks_stored']} chunks indexed from {data['doc_name']}")
                
                if "uploaded_docs" not in st.session_state:
                    st.session_state.uploaded_docs = []
                if {"name": data["doc_name"], "type": doc_type} not in st.session_state.uploaded_docs:
                    st.session_state.uploaded_docs.append({"name": data["doc_name"], "type": doc_type})
            else:
                st.error("Upload failed. Please try again.")

    
    if "uploaded_docs" in st.session_state and st.session_state.uploaded_docs:
        st.markdown("---")
        st.markdown("**📂 Indexed Documents:**")
        for doc in st.session_state.uploaded_docs:
            icon = "📜" if doc["type"] == "regulation" else "📋"
            st.markdown(f"{icon} `{doc['name']}` - *{doc['type']}*")


tab1, tab2, tab3 = st.tabs(["📊 Document Analysis", "💬 Ask a Question", "🔍 Gap Analysis"])


with tab1:
    st.subheader("Document Analysis")
    st.caption("Select an indexed document to get full AI analysis - risk score, key terms, risky clauses and recommendations.")

    if "uploaded_docs" not in st.session_state or not st.session_state.uploaded_docs:
        st.info("Upload and index a document first using the sidebar.")
    else:
        doc_options = [f"{d['name']} ({d['type']})" for d in st.session_state.uploaded_docs]
        selected = st.selectbox("Select document to analyze", doc_options)
        selected_idx = doc_options.index(selected)
        selected_doc = st.session_state.uploaded_docs[selected_idx]

        if st.button("🔍 Analyze Document"):
            with st.spinner("Analyzing document..."):
                response = requests.post(
                    f"{API_URL}/analyze",
                    json={"doc_name": selected_doc["name"], "doc_type": selected_doc["type"]}
                )
                if response.status_code == 200:
                    d = response.json()

                    
                    st.markdown('<div class="section-header">Document Information</div>', unsafe_allow_html=True)
                    col1, col2 = st.columns(2)
                    with col1:
                        st.markdown(f'<div class="doc-info-row"><span>File name:</span><span><b>{d["doc_name"]}</b></span></div>', unsafe_allow_html=True)
                        st.markdown(f'<div class="doc-info-row"><span>Word Count:</span><span><b>{d["word_count"]}</b></span></div>', unsafe_allow_html=True)
                    with col2:
                        st.markdown(f'<div class="doc-info-row"><span>Document Type:</span><span><b>{d["doc_category"]}</b></span></div>', unsafe_allow_html=True)
                        risk_color = {"LOW": "🟢", "MEDIUM": "🟡", "HIGH": "🔴", "CRITICAL": "🟣"}.get(d["risk_level"], "⚪")
                        st.markdown(f'<div class="doc-info-row"><span>Risk Level:</span><span><b>{risk_color} {d["risk_level"]}</b></span></div>', unsafe_allow_html=True)

                    
                    st.markdown('<div class="section-header">Risk Score</div>', unsafe_allow_html=True)
                    st.progress(d["risk_score"] / 100)
                    st.markdown(f"**{d['risk_score']}/100**")

                    
                    st.markdown('<div class="section-header">AI Summary</div>', unsafe_allow_html=True)
                    st.write(d["summary"])

                    
                    st.markdown('<div class="section-header">Key Legal Terms Found</div>', unsafe_allow_html=True)
                    terms_html = " ".join([f'<span class="key-term">{t}</span>' for t in d["key_terms"]])
                    st.markdown(terms_html, unsafe_allow_html=True)

                    
                    st.markdown('<div class="section-header">Risk Analysis</div>', unsafe_allow_html=True)
                    if d["risk_clauses"]:
                        for clause in d["risk_clauses"]:
                            st.markdown(f"""
                            <div class="risk-clause">
                                <b>{clause['title']}</b><br>
                                <span style="color:#6b7280">{clause['description']}</span>
                            </div>
                            """, unsafe_allow_html=True)
                    else:
                        st.success("No significant risk clauses detected.")

                    
                    st.markdown('<div class="section-header">Recommendations</div>', unsafe_allow_html=True)
                    for rec in d["recommendations"]:
                        st.markdown(f'<div class="recommendation">{rec}</div>', unsafe_allow_html=True)

                else:
                    st.error("Analysis failed. Please try again.")


with tab2:
    st.subheader("Ask a Compliance Question")
    question = st.text_area("Enter your question", placeholder="Does our leave policy comply with the new labour code?")

    if st.button("Get Answer") and question:
        with st.spinner("Searching documents..."):
            response = requests.post(f"{API_URL}/query", json={"question": question})
            if response.status_code == 200:
                data = response.json()
                st.markdown("### 📋 Answer")
                st.write(data["answer"])
                st.markdown("### 📌 Sources")
                for source in data["sources"]:
                    st.info(f"📄 {source['doc_name']} | Type: {source['doc_type']} | Chunk: {source['chunk_index']}")
            else:
                st.error("Query failed. Please try again.")


with tab3:
    st.subheader("Policy vs Regulation Gap Analysis")
    topic = st.text_input("Enter compliance topic", placeholder="Employee leave entitlement")

    if st.button("Run Gap Analysis") and topic:
        with st.spinner("Analyzing compliance gaps..."):
            response = requests.post(f"{API_URL}/gap-analysis", json={"topic": topic})
            if response.status_code == 200:
                data = response.json()
                st.markdown("### 📊 Gap Analysis Report")
                st.write(data["gap_analysis"])
                st.markdown("### 📌 Documents Analyzed")
                for source in data["sources"]:
                    st.info(f"📄 {source}")
            else:
                st.error("Analysis failed. Please try again.")