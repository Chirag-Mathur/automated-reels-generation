import streamlit as st
import pandas as pd
import sys
import os
from datetime import datetime
from pymongo import UpdateOne

# Ensure app directory is in sys.path for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.database.mongo import get_collection
from app.database.models import STATUS_SUCCESS, STATUS_ERROR

# --- CONFIG ---
COLLECTION_NAME = 'news'  # Change if your collection name is different

# --- DATA FETCHING ---
def fetch_articles():
    collection = get_collection(COLLECTION_NAME)
    if collection is None:
        st.error('Could not connect to MongoDB.')
        return pd.DataFrame([])
    docs = list(collection.find())
    if not docs:
        return pd.DataFrame([])
    # Convert ObjectId to string and datetime to str for DataFrame
    for doc in docs:
        # Fix: Always use str(doc['_id']) if present, else ''
        doc['_id'] = str(doc['_id']) if '_id' in doc else ''
        for dt_field in ['created_at', 'mod_at', 'error_at']:
            if doc.get(dt_field):
                doc[dt_field] = doc[dt_field].strftime('%Y-%m-%d %H:%M:%S') if isinstance(doc[dt_field], datetime) else str(doc[dt_field])
    df = pd.DataFrame(docs)
    df['_id'] = df['_id'].fillna('')  # Ensure no NaN in _id
    return df

# --- STREAMLIT UI ---
st.set_page_config(page_title='Articles Dashboard', layout='wide')
st.title('Automated Reels Generation - Articles Dashboard')

# Load data
df = fetch_articles()

if df.empty:
    st.warning('No articles found in the database.')
    st.stop()

# --- FILTERS ---
status_options = sorted(df['status'].dropna().unique().tolist())
default_status = ['VIDEO_GENERATED'] if 'VIDEO_GENERATED' in status_options else status_options
status_multiselect = st.sidebar.multiselect('Filter by Status', options=status_options, default=default_status)

filtered_df = df[df['status'].isin(status_multiselect)] if status_multiselect else df

# --- SORTING ---
sort_fields = ['relevancy', 'created_at', 'mod_at']
sort_by = st.sidebar.selectbox('Sort by', options=sort_fields, index=0)  # Default to 'relevancy'
sort_order = st.sidebar.radio('Order', options=['Descending', 'Ascending'], index=0)  # Default to 'Descending'
ascending = sort_order == 'Ascending'

if sort_by in filtered_df.columns:
    # Convert date fields to datetime for sorting if needed
    if sort_by in ['created_at', 'mod_at']:
        filtered_df[sort_by] = pd.to_datetime(filtered_df[sort_by], errors='coerce')
    filtered_df = filtered_df.sort_values(by=sort_by, ascending=ascending)  # type: ignore

# --- DISPLAY AS TILES ---
fields_to_show = [
    "_id", "caption", "created_at", "domain", "headline", "relevancy", "sentiment", "status", "video_url"
]

def show_articles_as_tiles(df, tiles_per_row=3):
    if df.empty:
        st.info("No articles to display.")
        return
    for i in range(0, len(df), tiles_per_row):
        cols = st.columns(tiles_per_row)
        for j, row in enumerate(df.iloc[i:i+tiles_per_row].itertuples()):
            with cols[j]:
                video_url = str(getattr(row, 'video_url', '') or '')
                id = str(row._asdict().get('_1', ''))
                status = getattr(row, 'status', '')
                link_html = f'<a href="{video_url}" target="_blank">Watch Video</a>' if video_url else ''
                st.markdown(
                    f'''
                    <div style="border:1px solid #222; border-radius:10px; padding:16px; margin-bottom:16px; background:#222; color:#f1f1f1;">
                        <h4 style="margin-bottom:8px; color:#fff;">{getattr(row, 'headline', '')}</h4>
                        <p><b>Status:</b> {status}</p>
                        <p><b>Relevancy:</b> {getattr(row, 'relevancy', '')}</p>
                        <p><b>Date:</b> {getattr(row, 'created_at', '')}</p>
                        <p><b>Domain:</b> {getattr(row, 'domain', '')}</p>
                        <p><b>Sentiment:</b> {getattr(row, 'sentiment', '')}</p>
                        <p><b>Caption:</b> {getattr(row, 'caption', '')}</p>
                        <p><b>ID:</b> {id}</p>
                        {link_html}
                    </div>
                    ''',
                    unsafe_allow_html=True
                )
                # Show button if status is VIDEO_GENERATED
                if status == 'VIDEO_GENERATED' and id:
                    if st.button('Mark as POSTED', key=f'post_{id}_{i}_{j}'):
                        # Update status in MongoDB
                        collection = get_collection(COLLECTION_NAME)
                        if collection is not None:
                            collection.update_one({'_id': __import__('bson').ObjectId(id)}, {'$set': {'status': 'POSTED'}})
                        st.rerun()

show_articles_as_tiles(filtered_df[fields_to_show]) 