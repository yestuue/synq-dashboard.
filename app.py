from flask import Flask, render_template_string, request, jsonify
import csv
import os
import smtplib
from email.message import EmailMessage
from datetime import datetime

app = Flask(__name__)

# --- 1. THE VISUAL INTERFACE (HTML) ---
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Synq Studio | Command Center</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <style>
        body { background-color: #020617; }
        .card { background: #0f172a; border: 1px solid #1e293b; transition: all 0.3s ease; }
        .gold-border { border: 2px solid #fbbf24 !important; }
    </style>
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
            btn.innerText = result.status === "Onboarding Sent" ? "✅ Sent" : "❌ Failed";
        }
    </script>
</head>
<body class="text-slate-200 p-4 md:p-8">
    <div class="max-w-6xl mx-auto">
        <header class="mb-6 flex justify-between items-center">
            <h1 class="text-3xl font-black text-white italic">SYNQ <span class="text-blue-500">STUDIO</span></h1>
            <span class="text-green-500 text-[10px] font-black uppercase tracking-widest">● Live Engine</span>
        </header>

        <div class="mobile-cards space-y-4">
            {% for row in leads %}
            <div class="card p-5 rounded-2xl shadow-lg {{ 'gold-border' if row[7] == 'High-Ticket' }}">
                <div class="flex justify-between items-start mb-3">
                    <span class="text-[10px] font-bold text-blue-400 uppercase tracking-tighter">{{ row[0] }}</span>
                    <span class="text-[10px] font-black px-2 py-0.5 rounded bg-blue-500/10 text-blue-500">{{ row[8] if row|length > 8 else 'Shopify' }}</span>
                </div>
                
                <h3 class="text-lg font-bold text-white mb-1">{{ row[1] }}</h3>
                <p class="text-[10px] text-slate-500 mb-4 uppercase font-bold tracking-widest">💰 {{ row[7] if row|length > 7 else 'Analysis Pending' }}</p>

                <div class="flex flex-col gap-2">
                    <div class="flex gap-2">
                        <a href="https://wa.me/?text=Hi!%20Saw%20your%20site%20{{ row[1] }}!" 
                           target="_blank" class="flex-1 bg-green-600 text-white text-center py-2 rounded-lg text-xs font-bold uppercase">WhatsApp Pitch</a>
                    </div>
                    <button onclick="sendOnboarding('contact@{{ row[1] }}', '{{ row[1] }}')" 
                            class="w-full bg-blue-600/20 text-blue-400 border border-blue-500/30 py-2 rounded-lg text-xs font-bold uppercase">
                        Send Welcome Pack
                    </button>
                </div>
            </div>
            {% endfor %}
        </div>
    </div>
</body>
</html>
"""

# --- 2. THE SERVER LOGIC (ROUTES) ---

@app.route('/')
def index():
    leads = []
    if os.path.exists('synq_leads.csv'):
        with open('synq_leads.csv', 'r') as f:
            reader = csv.reader(f)
            try:
                next(reader) # Skip header
                leads = list(reader)[::-1] # Show newest first
            except: pass
    return render_template_string(HTML_TEMPLATE, leads=leads)

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
    msg.set_content(f"Hi! We're excited to start the transformation of {domain}.\\n\\nTo begin, please provide:\\n1. Shopify Staff Access\\n2. Brand Logo\\n3. Product Photos\\n\\nBest,\\nSamuel Opeyemi\\nSynq Studio")
    msg['Subject'] = f"Onboarding: {domain} x Synq Studio"
    msg['From'] = "your-email@gmail.com" # Update to your email
    msg['To'] = target_email

    try:
        # Using your secure App Password: hthu cwcn smge mdch
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
            smtp.login("your-email@gmail.com", "hthu cwcn smge mdch")
            smtp.send_message(msg)
        return jsonify({"status": "Onboarding Sent"}), 200
    except Exception as e:
        return jsonify({"status": "Error", "message": str(e)}), 500

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
