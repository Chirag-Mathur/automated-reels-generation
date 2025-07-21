# Streamlit Dashboard for Automated Reels Generation

This dashboard allows you to view, filter, and sort articles from your MongoDB database.

## Setup & Usage

1. **Install dependencies:**
   ```bash
   pip install streamlit pandas
   ```
   (You should already have `pymongo` and your app dependencies installed.)

2. **Ensure MongoDB connection:**
   - The dashboard uses the same MongoDB connection settings as your main app (from `app/config/settings.py`).
   - Make sure your `.env` file is present and contains the correct `MONGO_URI`.

3. **Run the dashboard:**
   ```bash
   streamlit run dashboard/dashboard_app.py
   ```

4. **Access the dashboard:**
   - Open your browser and go to [http://localhost:8501](http://localhost:8501)

## Features
- **Multiselect status filter** (sidebar)
- **Sort by relevancy, created_at, or mod_at** (sidebar)
- **Full table view of articles**

---

If you encounter import errors, ensure you are running from the project root and that the `app/` directory is in your Python path. 