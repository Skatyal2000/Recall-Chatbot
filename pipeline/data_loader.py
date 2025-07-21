# pipeline/data_loader.py - Clean version without duplicated functions
from langchain_core.documents import Document
import pandas as pd
import streamlit as st
from pipeline.recall_categorizer import format_recall_date



@st.cache_data(show_spinner="Loading and preparing recall documents...")
def load_data(path="data/vehicle_recalls_clean.csv"):
    """Load CSV data and convert to LangChain documents"""
    df = pd.read_csv(path)
    df = df.fillna("Unknown")

    documents = []
    for _, row in df.iterrows():
        # Include date information if available
        # date_info = ""
        raw_date = row.get('report_received_date', None)
        if pd.notna(raw_date):
            formatted_date = format_recall_date(str(raw_date))
            # date_info = f"Recall Date: {formatted_date}\n"
        
        # Creating text to embedd into vectors
        text = f"""[{row['manufacturer']}] issued recall ID {row['nhtsa_id']} on \
            {formatted_date if pd.notna(raw_date) else 'an unknown date'} related to the {row['component']} component.

            Issue: {row['subject']}
            Summary: {row['defect_summary']}
            Consequence: {row['consequence_summary']}
            Corrective Action: {row['corrective_action']}
            Affected Vehicles: {row['potentially_affected']}
            Recall Type: {row['recall_type']} | Year: {row['year']} | Month: {row['year_month']}"""


        
        # Creating metadata to help in retrieval, filtering, and UI rendering
        metadata = {
            "nhtsa_id": str(row['nhtsa_id']),
            "manufacturer": row['manufacturer'],
            "component": row['component'],
            "recall_date": str(raw_date) if pd.notna(raw_date) else 'Unknown',
            "recall_type": row['recall_type'],
            "do_not_drive": row['do_not_drive'],
            "fire_risk_when_parked": row['fire_risk_when_parked'],
            "year": row['year'],
            "year_month": row['year_month']
        }


        doc = Document(page_content=text, metadata=metadata)
        # Wraps text and metadata into a LangChain Document
        documents.append(doc)
    st.markdown(f"Successfully created {len(documents)} documents with metadata")
    print(f"Successfully created {len(documents)} documents with metadata")
    return documents
