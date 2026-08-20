"""
Machine Uptime Dashboard Server (Flask)
DB에 직접 접속하지 않고, api_server.py가 제공하는 API만 호출한다.
"""
import os
from pathlib import Path
from flask import Flask, render_template, jsonify
import requests
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__, template_folder='templates')

BASE_DIR = Path(__file__).resolve().parent

UPTIME_API_URL = os.environ.get("UPTIME_API_URL", "http://127.0.0.1:8000/api/machine-uptime")
UPTIME_API_SUMMARY_URL = os.environ.get("UPTIME_API_SUMMARY_URL", "http://127.0.0.1:8000/api/summary")

TIMEOUT_SEC = 5


@app.route('/')
def index():
    return render_template('machine_uptime_dashboard.html')


@app.route('/api/data')
def get_data():
    try:
        resp = requests.get(UPTIME_API_URL, timeout=TIMEOUT_SEC)
        resp.raise_for_status()
        payload = resp.json()
        rows = payload.get("data", [])
        columns = list(rows[0].keys()) if rows else []
        return jsonify({'success': True, 'data': rows, 'columns': columns})
    except requests.RequestException as e:
        return jsonify({'success': False, 'error': f'API unreachable: {e}'}), 502
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/summary')
def get_summary():
    try:
        resp = requests.get(UPTIME_API_SUMMARY_URL, timeout=TIMEOUT_SEC)
        resp.raise_for_status()
        return jsonify(resp.json())
    except requests.RequestException as e:
        return jsonify({'success': False, 'error': f'API unreachable: {e}'}), 502
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Not found'}), 404


@app.errorhandler(500)
def server_error(error):
    return jsonify({'error': 'Internal server error'}), 500


if __name__ == '__main__':
    print("=" * 60)
    print("🏭 Machine Uptime Dashboard Server (Flask -> API)")
    print("=" * 60)
    print(f"📁 Base Directory: {BASE_DIR}")
    print(f"🔗 Uptime API: {UPTIME_API_URL}")

    try:
        r = requests.get(UPTIME_API_URL.rsplit('/api', 1)[0] + '/health', timeout=3)
        print(f"✅ API health check: {r.json()}")
    except Exception as e:
        print(f"⚠️  API server not reachable yet ({e}). Start api_server.py first.")

    print()
    print("🚀 Starting server...")
    print("📱 Open http://127.0.0.1:5000 in your browser")
    print("=" * 60)

    app.run(debug=True, host='127.0.0.1', port=5000)
