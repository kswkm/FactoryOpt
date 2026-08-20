"""
Machine Uptime Dashboard Server
Serves the factory machine uptime monitoring dashboard
"""
import os
import json
from pathlib import Path
from flask import Flask, render_template, jsonify
import pandas as pd

# Initialize Flask app
app = Flask(__name__, template_folder='templates')

# Get the directory where this script is located
BASE_DIR = Path(__file__).resolve().parent
CSV_FILE = BASE_DIR / 'machine_uptime_export.csv'

# Global variable to cache the data
_data_cache = None

def load_data():
    """Load and cache the CSV data"""
    global _data_cache
    if _data_cache is None:
        if not CSV_FILE.exists():
            raise FileNotFoundError(f"CSV file not found: {CSV_FILE}")
        _data_cache = pd.read_csv(CSV_FILE)
    return _data_cache

@app.route('/')
def index():
    """Serve the main dashboard page"""
    return render_template('machine_uptime_dashboard.html')

@app.route('/api/data')
def get_data():
    """API endpoint to get the full dataset"""
    try:
        df = load_data()
        return jsonify({
            'success': True,
            'data': df.to_dict('records'),
            'columns': df.columns.tolist()
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/summary')
def get_summary():
    """API endpoint to get summary statistics"""
    try:
        df = load_data()
        summary = {
            'total_records': len(df),
            'machines': df['machine_id'].nunique(),
            'avg_availability': df['availability'].mean(),
            'avg_defect_rate': df['defect_rate'].mean(),
            'total_downtime': df['downtime_min'].sum(),
            'date_range': {
                'start': df['date_str'].min(),
                'end': df['date_str'].max()
            }
        }
        return jsonify({'success': True, 'summary': summary})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors"""
    return jsonify({'error': 'Not found'}), 404

@app.errorhandler(500)
def server_error(error):
    """Handle 500 errors"""
    return jsonify({'error': 'Internal server error'}), 500

if __name__ == '__main__':
    print("=" * 60)
    print("🏭 Machine Uptime Dashboard Server")
    print("=" * 60)
    print(f"📁 Base Directory: {BASE_DIR}")
    print(f"📊 Data File: {CSV_FILE}")
    print(f"✅ Data File Exists: {CSV_FILE.exists()}")
    print()
    
    # Test data loading
    try:
        df = load_data()
        print(f"✅ Successfully loaded {len(df)} records from CSV")
        print(f"📅 Date Range: {df['date_str'].min()} to {df['date_str'].max()}")
        print(f"🤖 Machines: {', '.join(sorted(df['machine_id'].unique()))}")
        print()
    except Exception as e:
        print(f"❌ Error loading data: {e}")
        print()
    
    print("🚀 Starting server...")
    print("📱 Open http://127.0.0.1:5000 in your browser")
    print("💾 Press Ctrl+C to stop the server")
    print("=" * 60)
    print()
    
    # Run the Flask app
    app.run(debug=True, host='127.0.0.1', port=5000)
