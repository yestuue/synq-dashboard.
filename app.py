from flask import Flask, render_template_string, request, jsonify
import csv
import os
from datetime import datetime

app = Flask(__name__)

def time_ago(timestamp_str):
    try:
        past_time = datetime.strptime(timestamp_str, "%Y-%m-%d %H:%M")
        diff = datetime.now() - past_time
        minutes = int(diff.total_seconds() / 60)
        if minutes < 1: return "Just Now"
        if minutes < 60: return f"{minutes}m ago"
        hours = int(minutes / 60)
        if hours < 24: return f"{hours}h ago"
        return past_time.strftime("%b %d")
    except: return "New"

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Synq Studio | Intelligence</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <style>
        body { background-color: #020617; }
        .card { background: #0f172a; border: 1px solid #1e293b; transition: all 0.3s ease; }
        .gold-border { border: 2px solid #fbbf24 !important; }
    </style>
</head>
<body class="text-slate-200 p-4 md:p-8">
    <div class="max-w-6xl mx-auto">
        <header class="mb-6">
            <h1 class="text-3xl font-black text-white italic">SYNQ <span class="text-blue-500">STUDIO</span></h1>
            <p class="text-slate-500 text-[10px] font-mono tracking-widest uppercase">Intelligence Dashboard</p>
        </header>

        <div class="mobile-cards space-y-4">
            {% for row in leads %}
            <div class="card p-5 rounded-2xl shadow-lg {{ 'gold-border' if row[7] == 'High-Ticket' }}">
                <div class="flex justify-between items-start mb-3">
                    <span class="px-2 py-0.5 rounded bg-slate-800 text-[10px] font-bold text-blue-400 uppercase">⏱ {{ row[4] }}</span>
                    <span class="text-[10px] font-black px-2 py-0.5 rounded bg-blue-500/10 text-blue-500 uppercase">
                        Theme: {{ row[8] }}
                    </span>
                </div>
                
                <h3 class="text-lg font-bold text-white mb-1">{{ row[1] }}</h3>
                <div class="flex items-center gap-2 mb-4">
                    <span class="text-[10px] font-black px-2 py-0.5 rounded {{ 'bg-yellow-500/20 text-yellow-500' if row[7] == 'High-Ticket' else 'bg-slate-800 text-slate-400' }}">
                        💰 {{ row[7] }}
                    </span>
                    <span class="text-[10px] text-slate-500 font-bold uppercase">{{ row[5] }} Items</span>
                </div>

                <div class="flex gap-3">
                    <a href="https://wa.me/?text=Hi!%20Saw%20your%20site%20{{ row[1] }}!%20I%20noticed%20you%20are%20using%20the%20{{ row[8] }}%20theme." 
                       target="_blank" class="flex-1 bg-green-600 text-white text-center py-2 rounded-lg text-xs font-bold">WhatsApp Pitch</a>
                </div>
            </div>
            {% endfor %}
        </div>
    </div>
</body>
</html>
"""

@app.route('/add_lead', methods=['POST'])
def add_lead():
    data = request.json
    file_path = 'synq_leads.csv'
    file_exists = os.path.isfile(file_path)
    with open(file_path, 'a', newline='') as f:
        writer = csv.writer(f)
        if not file_exists:
            writer.writerow(['Date', 'Domain', 'Instagram', 'Facebook', 'Score', 'Issue', 'Revenue', 'Theme'])
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")
        writer.writerow([timestamp, data['domain'], data['insta'], data['fb'], data['score'], data['issue'], data.get('revenue', 'Low'), data.get('theme', 'Unknown')])
    return jsonify({"status": "success"}), 200

@app.route('/')
def index():
    leads = []
    if os.path.exists('synq_leads.csv'):
        with open('synq_leads.csv', 'r') as f:
            reader = csv.reader(f)
            try:
                next(reader)
                all_data = list(reader)
                processed = []
                for row in all_data:
                    r = list(row)
                    r.insert(4, time_ago(row[0])) # Index 4 becomes display time
                    processed.append(r)
                
                # Sort: High-Ticket first
                priority = {"High-Ticket": 3, "Mid-Range": 2, "Low": 1}
                processed.sort(key=lambda x: priority.get(x[7], 0), reverse=True)
                leads = processed
            except: pass
    return render_template_string(HTML_TEMPLATE, leads=leads)

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
