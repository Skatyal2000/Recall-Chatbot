#app4.py 

## Importing Libraries
import streamlit as st
import pandas as pd
import plotly.express as px


## Importing Custom Pipeline
from pipeline.data_loader import load_data
from pipeline.embedder import get_embedder
from pipeline.vectorstore import build_vectorstore
from pipeline.rag_chain import build_rag_chain_manual
from pipeline.recall_categorizer import format_recall_for_display

# Page frontend config 
st.set_page_config(
    page_title="Recall Recon", 
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS style
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        font-weight: bold;
        color: white;
        margin-bottom: 1rem;
    }
    .subtitle {
        color: #888;
        font-size: 1.1rem;
        margin-bottom: 2rem;
    }
    .answer-section {
        background-color: #1e1e1e;
        padding: 1.5rem;
        border-radius: 10px;
        margin: 1rem 0;
        border-left: 4px solid #4CAF50;
    }
    .chart-container {
        background-color: #1e1e1e;
        padding: 1rem;
        border-radius: 10px;
        margin: 1rem 0;
    }
    .metric-card {
        background-color: #2d2d2d;
        padding: 1rem;
        border-radius: 8px;
        border-left: 4px solid #4CAF50;
        margin: 0.5rem 0;
    }
    .recall-details {
        color: #ccc;
        font-size: 0.9rem;
        line-height: 1.4;
    }
    .manufacturer { color: #4CAF50; font-weight: bold; }
    .recall-id { color: #2196F3; font-weight: bold; }
    .component { color: #FF9800; font-weight: bold; }
    .recall-date { color: #FFD700; font-weight: bold; }
</style>
""", unsafe_allow_html=True)


##Create visualizations from retrieved documents
def create_visualizations_from_docs(source_docs, query_context=""):
    
    if not source_docs:
        st.warning("No recall data found for visualization")
        return
    
    # Extract data from documents
    data = []
    for doc in source_docs:
        recall_data = format_recall_for_display(doc)
        data.append({
            'manufacturer': recall_data['manufacturer'],
            'component': recall_data['component'],
            'category': recall_data['category'],
            'severity': recall_data['severity'],
            'nhtsa_id': recall_data['nhtsa_id'],
            'recall_date': recall_data.get('recall_date', 'Unknown')
        })
    
    df = pd.DataFrame(data)
    
    # Convert date if possible
    if 'recall_date' in df.columns:
        try:
            df['recall_date'] = pd.to_datetime(df['recall_date'], errors='coerce')
        except:
            pass
    
    st.markdown(f"## 📊 Visualizations for: {query_context}")
    st.success(f"Found {len(df)} relevant recalls")
    
    # Create visualizations
    col1, col2 = st.columns(2)
    
    with col1:
        # Manufacturer distribution
        if len(df['manufacturer'].unique()) > 1:
            manufacturer_counts = df['manufacturer'].value_counts()
            fig_mfg = px.bar(
                x=manufacturer_counts.values,
                y=manufacturer_counts.index,
                orientation='h',
                title='Recalls by Manufacturer',
                labels={'x': 'Number of Recalls', 'y': 'Manufacturer'},
                template='plotly_dark',
                color=manufacturer_counts.values,
                color_continuous_scale='Viridis'
            )
            fig_mfg.update_layout(
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
                font_color='white',
                showlegend=False
            )
            st.plotly_chart(fig_mfg, use_container_width=True)
    
    with col2:
        # Severity distribution
        severity_counts = df['severity'].value_counts()
        colors = {'HIGH': '#ff4444', 'MEDIUM': '#ff9800', 'LOW': '#4caf50'}
        fig_severity = px.pie(
            values=severity_counts.values,
            names=severity_counts.index,
            title='Recall Severity Distribution',
            template='plotly_dark',
            color=severity_counts.index,
            color_discrete_map=colors
        )
        fig_severity.update_layout(
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font_color='white'
        )
        st.plotly_chart(fig_severity, use_container_width=True)
    
    # Component analysis
    if len(df['category'].unique()) > 1:
        component_counts = df['category'].value_counts().head(10)
        fig_components = px.bar(
            x=component_counts.index,
            y=component_counts.values,
            title='🔧 Most Common Components',
            labels={'x': 'Component Category', 'y': 'Number of Recalls'},
            template='plotly_dark',
            color=component_counts.values,
            color_continuous_scale='Plasma'
        )
        fig_components.update_layout(
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font_color='white',
            showlegend=False,
            xaxis_tickangle=-45
        )
        st.plotly_chart(fig_components, use_container_width=True)

def detect_chart_command(query):
    """Detect if the user wants to see charts/visualizations"""
    chart_keywords = [
        'chart', 'graph', 'plot', 'trend', 'visualization', 'stats', 'statistics',
        'show recalls', 'visualize', 'dashboard', 'analytics', 'data viz',
        'over time', 'trends', 'analysis'
    ]
    
    query_lower = query.lower()
    return any(keyword in query_lower for keyword in chart_keywords)

def show_system_info():
    """Display system information in sidebar"""  
    st.sidebar.markdown("## System Info")
    st.sidebar.info("Using semantic search with embeddings for intelligent recall matching")
    
    # Add basic controls
    st.sidebar.markdown("## Options")
    show_visualizations = st.sidebar.checkbox("Auto-show visualizations", value=False)
    max_results = st.sidebar.slider("Max results to display", 3, 20, 10)
    
    return show_visualizations, max_results

# Initialize RAG system
@st.cache_resource
def initialize_rag_system():
    with st.spinner("Initializing AI system..."):
        docs = load_data()
        embedder = get_embedder()
        vectorstore = build_vectorstore(docs, embedder)
        rag_chain = build_rag_chain_manual(vectorstore)
        return rag_chain

st.markdown('<div class="main-header"> Recall Recon</div>', unsafe_allow_html=True)
st.markdown('<div class="subtitle">Ask intelligent questions about vehicle recalls using AI-powered semantic search</div>', unsafe_allow_html=True)


rag_chain = initialize_rag_system()


show_visualizations, max_results = show_system_info()

# User Input
query = st.text_input(
    "", 
    placeholder="e.g., 'Toyota brake recalls', 'airbag safety issues', 'show me Ford engine problems'", 
    label_visibility="collapsed"
)


# Check if user wants charts
wants_charts = detect_chart_command(query) if query else False

if query:
    with st.spinner("Searching NHTSA database..."):
        rag_result = rag_chain({"question": query})
        rag_answer = rag_result.get("answer", "No answer generated.")
        source_docs = rag_result.get("source_documents", [])

    # Answer section
    st.markdown("## AI Analysis")
    st.markdown(f'<div class="answer-section">{rag_answer}</div>', unsafe_allow_html=True)

    # Show visualizations if requested or enabled
    if wants_charts or show_visualizations:
        create_visualizations_from_docs(source_docs, query)

    # Top Relevant Recalls section
    if source_docs:
        st.markdown("## Related Recalls")
        
        # Limit results based on user preference
        display_docs = source_docs[:max_results]
        
        # Process and group recalls by category
        recall_groups = {}
        
        for doc in display_docs:
            recall_data = format_recall_for_display(doc)
            category = recall_data['category']
            
            if category not in recall_groups:
                recall_groups[category] = []
            recall_groups[category].append(recall_data)
        
        # Display each category
        for category, recalls in recall_groups.items():
            has_high_severity = any(recall['severity'] == 'HIGH' for recall in recalls)
            expanded = len(recall_groups) == 1 or has_high_severity
            
            with st.expander(f"{category} ({len(recalls)} recalls)", expanded=expanded):
                for i, recall in enumerate(recalls):
                    severity_color = {
                        'HIGH':'#ff4444',
                        'MEDIUM': '#ff9800', 
                        'LOW': '#4caf50'
                    }
                    
                    severity_emoji = {
                        'HIGH': '🚨',
                        'MEDIUM': '⚠️',
                        'LOW': 'ℹ️'
                    }
                    
                    st.markdown(f"""
                    <div style="border-left: 4px solid {severity_color[recall['severity']]}; padding-left: 1rem; margin: 1rem 0;">
                        <div class="recall-details">
                            <p>{severity_emoji[recall['severity']]} <strong>Recall ID:</strong> <span class="recall-id">{recall['nhtsa_id']}</span> 
                            <span style="color: {severity_color[recall['severity']]}; font-size: 0.8rem; font-weight: bold;">({recall['severity']} RISK)</span></p>
                            <p><strong>Manufacturer:</strong> <span class="manufacturer">{recall['manufacturer']}</span></p>
                            <p><strong>Component:</strong> <span class="component">{recall['component']}</span></p>
                            <p><strong>Summary:</strong> {recall['summary']}</p>
                            <p><strong>Corrective Action:</strong> {recall['action']}</p>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    if i < len(recalls) - 1:
                        st.markdown('<hr style="margin: 1rem 0; border-color: #444;">', unsafe_allow_html=True)

# Example queries section
if not query:
    st.markdown("## 💡 Example Queries")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
        **Safety Issues:**
        - "What are the most dangerous brake recalls?"
        - "Show me airbag deployment problems"
        - "Toyota safety recalls with high severity"
        """)
    
    with col2:
        st.markdown("""
        **Component Analysis:**
        - "Ford engine recall trends"
        - "Windshield wiper motor issues"
        - "Electrical system failures by manufacturer"
        """)
    
    with col3:
        st.markdown("""
        **Visualizations:**
        - "Show tire recall statistics"
        - "Visualize Honda recall patterns"
        - "Chart brake system recalls over time"
        """)

# Quick action buttons
st.markdown("---")
st.markdown("### Quick Actions")

col1, col2, col3, col4 = st.columns(4)

with col1:
    if st.button("🚨 High Risk Recalls"):
        st.session_state['auto_query'] = "show me high severity recalls with potential for injury"

with col2:
    if st.button("🏭 Manufacturer Analysis"):
        st.session_state['auto_query'] = "compare recall patterns across manufacturers"

with col3:
    if st.button("🔧 Component Issues"):
        st.session_state['auto_query'] = "what are the most commonly recalled components"

with col4:
    if st.button("Show Analytics"):
        st.session_state['auto_query'] = "visualize recall trends and statistics"

# Handle auto queries
if 'auto_query' in st.session_state:
    query = st.session_state['auto_query']
    del st.session_state['auto_query']
    st.rerun()

# Footer
st.markdown("---")
st.markdown("""
<div style="text-align: center; color: #666; font-size: 0.8rem; margin-top: 2rem;">
    <p>Recall Recon - AI-Powered Vehicle Safety Analysis</p>
    <p>Powered by semantic search and intelligent document retrieval</p>
</div>
""", unsafe_allow_html=True)