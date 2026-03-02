from flask import Flask, render_template_string, request, jsonify
import csv
import os
import smtplib
from email.message import EmailMessage
from datetime import datetime

app = Flask(__name__)

# --- THE FOUNDER DASHBOARD (MERGED UI) ---
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Synq Studio | Founder's Desk</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <script>
        async function sendOnboarding(email, domain) {
            const btn = event.target;
            btn.innerText = "Sending...";
            const response = await fetch('/send_onboarding', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({email: email, domain: domain})
            });
            const result = await response.json();
            btn.innerText = result.status === "Onboarding Sent" ? "✅ Sent" : "❌ Error";
        }
    </script>
    <style>
        body { background-color: #020617; color: #e2e8f0; }
        .card { background: #0f172a; border: 1px solid #1e293b; border-radius: 1rem; }
        .gold-border { border: 2px solid #fbbf24 !important; }
    </style>
</head>
<body class="p-4 md:p-8">
    <div class="max-w-4xl mx-auto">
        <header class="mb-8 flex justify-between items-end">
            <div>
                <h1 class="text-2xl font-black italic text-white uppercase tracking-tighter">SYNQ <span class="text-blue-500">STUDIO</span></h1>
                <p class="text-[10px] text-slate-500 font-bold uppercase tracking-widest">Performance: {{ total_leads }} Captured | {{ high_ticket }} High-Value</p>
            </div>
            <span class="text-green-500 text-[10px] font-bold uppercase border border-green-500/30 px-2 py-1 rounded">● Live</span>
        </header>

        <div class="space-y-4">
            {% for row in leads %}
            <div class="card p-5 {{ 'gold-border' if row[7] == 'High-Ticket' }}">
                <div class="flex justify-between items-start mb-2">
                    <span class="text-[10px] font-mono text-slate-500">{{ row[0] }}</span>
                    <span class="text-[10px] font-bold px-2 py-0.5 rounded bg-blue-500/10 text-blue-500">{{ row[8] if row|length > 8 else 'Shopify' }}</span>
                </div>
                <h3 class="text-lg font-bold text-white mb-4">{{ row[1] }}</h3>
                <div class="flex gap-2">
                    <a href="https://wa.me/?text=Hi!%20Saw%20your%20site%20{{ row[1] }}!" target="_blank" 
                       class="flex-1 bg-green-600 text-white text-center py-2 rounded-lg text-xs font-bold uppercase">WhatsApp</a>
                    <button onclick="sendOnboarding('contact@{{ row[1] }}', '{{ row[1] }}')" 
                            class="flex-1 bg-blue-600 text-white py-2 rounded-lg text-xs font-bold uppercase">Onboard</button>
                </div>
            </div>
            {% endfor %}
        </div>
    </div>
</body>
</html>
"""

@app.route('/')
def index():
    leads = []
    total_leads = 0
    high_ticket = 0
    if os.path.exists('synq_leads.csv'):
        with open('synq_leads.csv', 'r') as f:
            reader = csv.reader(f)
            try:
                next(reader) 
                all_data = list(reader)
                total_leads = len(all_data)
                # MERGED FEATURE: Filter and Statistics
                processed = []
                for row in all_data:
                    if row[7] == "High-Ticket": high_ticket += 1
                    # Filter out 'Low' value leads to focus your time
                    if row[7] != "Low":
                        processed.append(row)
                leads = processed[::-1] 
            except: pass
    return render_template_string(HTML_TEMPLATE, leads=leads, total_leads=total_leads, high_ticket=high_ticket)

# ... (Keep existing add_lead and send_onboarding routes from previous update)
