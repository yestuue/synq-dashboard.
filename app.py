from flask import Flask, render_template_string, request
import csv
import os
from datetime import datetime, timedelta

app = Flask(__name__)

# Helper function to show relative time (e.g., "2 mins ago")
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
    except:
        return "New"

# Enhanced HTML with Search, Stats, and Launch Timers
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Synq Studio | Live Intel</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <style>
        body { background-color: #020617; }
        .card { background: #0f172a; border: 1px solid #1e293b; }
        .timer-badge { background: #1e293b; color: #3b82f6; border: 1px solid #334155; }
    </style>
</head>
<body class="text-slate-200 p-8">
    <div class="max-w-6xl mx-auto">
        <header class="flex flex-col md:flex-row justify-between items-center mb-10 gap-6">
            <div class="text-center md:text-left">
                <h1 class="text-5xl font-black text-white tracking-tighter italic">SYNQ <span class="text-blue-500">STUDIO</span></h1>
                <p class="text-slate-500 text-xs font-mono uppercase tracking-[0.3em] mt-2">Merchant Discovery Engine</p>
            </div>
            
            <form action="/" method="get" class="w-full max-w-lg">
                <div class="relative">
                    <input type="text" name="q" placeholder="Search by niche or domain..." 
                           value="{{ query }}"
                           class="w-full bg-slate-900 border border-slate-800 rounded-2xl px-6 py-4 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500/50 transition-all">
                    <button type="submit" class="absolute right-4 top-4 text-slate-500 hover:text-white">🔍</button>
                </div>
            </form>
        </header>

        <div class="grid grid-cols-1 md:grid-cols-3 gap-6 mb-10">
            <div class="card p-6 rounded-2xl shadow-xl">
                <p class="text-slate-500 text-[10px] font-black uppercase tracking-widest mb-1">Global Database</p>
                <p class="text-4xl font-bold text-white">{{ total_count }}</p>
            </div>
            <div class="card p-6 rounded-2xl shadow-xl border-b-4 border-b-blue-600">
                <p class="text-slate-500 text-[10px] font-black uppercase tracking-widest mb-1">Results Found</p>
                <p class="text-4xl font-bold text-blue-500">{{ leads|length }}</p>
            </div>
            <div class="card p-6 rounded-2xl shadow-xl">
                <p class="text-slate-500 text-[10px] font-black uppercase tracking-widest mb-1">Outreach Status</p>
                <p class="text-4xl font-bold text-green-500">ACTIVE</p>
            </div>
        </div>

        <div class="card rounded-3xl overflow-hidden shadow-2xl">
            <table class="w-full text-left">
                <thead class="bg-slate-900/50 text-slate-500 text-[10px] uppercase font-black tracking-widest border-b border-slate-800">
                    <tr>
                        <th class="p-6">Launch Timer</th>
                        <th class="p-6">Merchant Identity</th>
                        <th class="p-6">Social Intelligence</th>
                        <th class="p-6">Action Hub</th>
                    </tr>
                </thead>
                <tbody class="divide-y divide-slate-800/50">
                    {% for row in leads %}
                    <tr class="hover:bg-slate-800/30 transition-all group">
                        <td class="p-6">
                            <span class="timer-badge px-3 py-1.5 rounded-full text-[10px] font-black uppercase">
                                ⏱ {{ row[4] }}
                            </span>
                        </td>
                        <td class="p-6">
                            <div class="font-bold text-slate-200 group-hover:text-blue-400 text-lg transition-colors">{{ row[1] }}</div>
                            <div class="text-[10px] text-slate-600 font-mono">{{ row[0] }}</div>
                        </td>
                        <td class="p-6">
                            {% if row[2] != "N/A" %}
                            <a href="{{ row[2] }}" target="_blank" class="text-pink-500 hover:text-pink-300 text-xs font-black uppercase">Instagram</a>
                            {% else %}
                            <span class="text-slate-800 text-[10px] font-bold italic uppercase">Pending...</span>
                            {% endif %}
                        </td>
                        <td class="p-6">
                            <a href="https://wa.me/?text=Hello!%20I%20just%20saw%20your%20new%20store%20at%20{{ row[1] }}!" 
                               target="_blank" class="bg-green-600 hover:bg-green-500 text-white px-6 py-2.5 rounded-xl text-[10px] font-black uppercase shadow-lg shadow-green-900/20 transition-all">
                               WhatsApp Pitch
                            </a>
                        </td>
                    </tr>
                    {% else %}
                    <tr><td colspan="4" class="p-24 text-center text-slate-700 italic font-medium">Scanning the global internet... new brands appear instantly.</td></tr>
                    {% endfor %}
                </tbody>
            </table>
        </div>
    </div>
</body>
</html>
"""

@app.route('/')
def index():
    query = request.args.get('q', '').lower()
    leads = []
    total_count = 0
    
    if os.path.exists('synq_leads.csv'):
        with open('synq_leads.csv', 'r') as f:
            reader = csv.reader(f)
            try:
                next(reader)
                all_data = list(reader)
                total_count = len(all_data)
                
                # Add the relative time (Launch Timer) to each row
                processed_data = []
                for row in all_data:
                    row_with_timer = list(row)
                    row_with_timer.append(time_ago(row[0]))
                    processed_data.append(row_with_timer)
                
                if query:
                    leads = [row for row in processed_data if query in row[1].lower()]
                else:
                    leads = processed_data
            except: pass
            
    return render_template_string(HTML_TEMPLATE, leads=leads[::-1], total_count=total_count, query=query)

if __name__ == '__main__':
    app.run(debug=True, port=5000)