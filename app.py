from flask import Flask, render_template_string, request, jsonify
import csv
import os
import smtplib
from email.message import EmailMessage
from datetime import datetime

app = Flask(__name__)

# --- MERGED FEATURES: UI + CALCULATOR + ANALYTICS ---
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Synq Studio | Empire Command</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <script>
        // Feature 1: Multi-Action Onboarding
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

        // Feature 2: Instant Price Calculator
        function calculateQuote(tier) {
            const rates = { 'High-Ticket': 1200, 'Mid-Range': 600 };
            alert("Projected Quote for this Lead: $" + (rates[tier] || 300));
        }
    </script>
    <style>
        body { background-color: #020617; color: #f8fafc; font-family: 'Inter', sans-serif; }
        .card { background: #0f172a; border: 1px solid #1e293b; border-radius: 1.5rem; transition: 0.3s; }
        .gold-border { border: 2px solid #fbbf24 !important; background: linear-gradient(to bottom right, #0f172a, #1e1b4b); }
    </style>
</head>
<body class="p-4 md:p-8">
    <div class="max-w-4xl mx-auto">
        <header class="mb-10 flex justify-between items-start">
            <div>
                <h1 class="text-3xl font-black italic text-white uppercase tracking-tighter">SYNQ <span class="text-blue-500">STUDIO</span></h1>
                <div class="flex gap-4 mt-2">
                    <p class="text-[10px] text-slate-400 font-bold uppercase tracking-widest">💰 Pipeline: ${{ pipeline_value }}</p>
                    <p class="text-[10px] text-blue-400 font-bold uppercase tracking-widest">🚀 {{ high_ticket }} Prime Leads</p>
                </div>
            </div>
            <div class="bg-green-500/10 border border-green-500/20 px-3 py-1 rounded-full">
                <span class="text-green-500 text-[10px] font-black uppercase tracking-widest">● Active</span>
            </div>
        </header>

        <div class="space-y-6">
            {% for row in leads %}
            <div class="card p-6 {{ 'gold-border' if row[7] == 'High-Ticket' }}">
                <div class="flex justify-between items-center mb-4">
                    <span class="text-[10px] font-mono text-slate-500 uppercase">{{ row[0] }}</span>
                    <span class="text-[10px] font-black px-2 py-1 rounded bg-blue-600 text-white uppercase">{{ row[8] }}</span>
                </div>
                
                <h3 class="text-xl font-bold text-white mb-2">{{ row[1] }}</h3>
                <p class="text-xs text-slate-400 mb-6 italic">{{ "⚠️ Issues Detected" if row[5] == "Broken Links Found" else "✨ Clean Audit" }}</p>

                <div class="grid grid-cols-2 gap-3">
                    <button onclick="calculateQuote('{{ row[7] }}')" class="bg-slate-800 text-slate-300 py-3 rounded-xl text-[10px] font-bold uppercase">Get Quote</button>
                    <button onclick="sendOnboarding('contact@{{ row[1] }}', '{{ row[1] }}')" class="bg-blue-600 text-white py-3 rounded-xl text-[10px] font-bold uppercase">Onboard</button>
                </div>
                <a href="https://wa.me/?text=Hi!%20I%20saw%20your%20{{ row[8] }}%20store%20{{ row[1] }}..." target="_blank" 
                   class="block mt-3 text-center text-green-500 text-[10px] font-bold uppercase tracking-widest">WhatsApp Direct Pitch</a>
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
    pipeline_value = 0
    high_ticket = 0
    if os.path.exists('synq_leads.csv'):
        with open('synq_leads.csv', 'r') as f:
            reader = csv.reader(f)
            try:
                next(reader) 
                all_data = list(reader)
                processed = []
                for row in all_data:
                    # FEATURE 5: Direct Value Calculation
                    if row[7] == "High-Ticket": 
                        high_ticket += 1
                        pipeline_value += 1200
                    elif row[7] == "Mid-Range":
                        pipeline_value += 600
                    
                    # FEATURE 6: Auto-Filter Low Value Leads
                    if row[7] != "Low":
                        processed.append(row)
                leads = processed[::-1] 
            except: pass
    return render_template_string(HTML_TEMPLATE, leads=leads, pipeline_value=pipeline_value, high_ticket=high_ticket)

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
        writer.writerow([timestamp, data['domain'], data['insta'], data['fb'], data['score'], data['issue'], data.get('revenue', 'Low'), data.get('theme', 'Dawn')])
    return jsonify({"status": "success"}), 200

@app.route('/send_onboarding', methods=['POST'])
def send_onboarding():
    data = request.json
    target_email = data.get('email')
    domain = data.get('domain')
    msg = EmailMessage()
    msg.set_content(f"Hi! We're excited to start the transformation of {domain}.\\n\\nTo begin, please provide:\\n1. Shopify Staff Access (growthprofesors@gmail.com)\\n2. Brand Logo\\n3. Product Photos\\n\\nBest,\\nSamuel Opeyemi\\nSynq Studio")
    msg['Subject'] = f"Next Steps: {domain} x Synq Studio"
    msg['From'] = "growthprofesors@gmail.com"
    msg['To'] = target_email
    try:
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
            smtp.login("growthprofesors@gmail.com", "hthu cwcn smge mdch")
            smtp.send_message(msg)
        return jsonify({"status": "Onboarding Sent"}), 200
    except Exception as e:
        return jsonify({"status": "Error", "message": str(e)}), 500

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
