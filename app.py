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
    <script>
        async function sendOnboarding(email, domain) {
            const btn = event.target;
            const originalText = btn.innerText;
            btn.innerText = "Sending...";
            try {
                const response = await fetch('/send_onboarding', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({email: email, domain: domain})
                });
                const result = await response.json();
                btn.innerText = result.status === "Onboarding Sent" ? "✅ Sent" : "❌ Error";
            } catch (e) {
                btn.innerText = "❌ Failed";
            }
            setTimeout(() => { btn.innerText = originalText; }, 3000);
        }
    </script>
    <style>
        body { background-color: #020617; color: #e2e8f0; font-family: sans-serif; }
        .card { background: #0f172a; border: 1px solid #1e293b; padding: 1.25rem; border-radius: 1rem; margin-bottom: 1rem; transition: all 0.2s; }
        .gold-border { border: 2px solid #fbbf24 !important; box-shadow: 0 0 15px rgba(251, 191, 36, 0.1); }
    </style>
</head>
<body class="p-4 md:p-8">
    <div class="max-w-4xl mx-auto">
        <header class="mb-8 flex justify-between items-center">
            <h1 class="text-2xl font-black italic text-white uppercase tracking-tighter">SYNQ <span class="text-blue-500">STUDIO</span></h1>
            <span class="text-green-500 text-[10px] font-bold uppercase tracking-widest">● Cloud Active</span>
        </header>

        <div class="space-y-4">
            {% for row in leads %}
            <div class="card {{ 'gold-border' if row[7] == 'High-Ticket' }}">
                <div class="flex justify-between items-start mb-2">
                    <span class="text-[10px] font-mono text-slate-500">{{ row[0] }}</span>
                    <span class="text-[10px] font-bold px-2 py-0.5 rounded bg-blue-500/10 text-blue-500">{{ row[8] if row|length > 8 else 'Shopify' }}</span>
                </div>
                <h3 class="text-lg font-bold text-white mb-4">{{ row[1] }}</h3>
                <div class="flex flex-col gap-2">
                    <a href="https://wa.me/?text=Hi!%20Saw%20your%20site%20{{ row[1] }}!%20I%20noticed%20you%20are%20using%20the%20{{ row[8] }}%20theme." 
                       target="_blank" class="w-full bg-green-600 text-white text-center py-2 rounded-lg text-xs font-bold uppercase">WhatsApp Pitch</a>
                    <button onclick="sendOnboarding('contact@{{ row[1] }}', '{{ row[1] }}')" 
                            class="w-full bg-slate-800 text-blue-400 border border-slate-700 py-2 rounded-lg text-xs font-bold uppercase">
                        Send Onboarding
                    </button>
                </div>
            </div>
            {% endfor %}
        </div>
    </div>
</body>
</html>
"""

# --- 2. THE SERVER LOGIC ---

@app.route('/')
def index():
    leads = []
    if os.path.exists('synq_leads.csv'):
        with open('synq_leads.csv', 'r') as f:
            reader = csv.reader(f)
            try:
                next(reader) 
                leads = list(reader)[::-1] 
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
    # Professional Agency Onboarding Content
    msg.set_content(f"Hi! We're excited to start the transformation of {domain}.\\n\\nTo begin our build process, please provide:\\n1. Shopify Staff Access (growthprofesors@gmail.com)\\n2. Your Brand Logo (High Resolution)\\n3. Product Photography Folder\\n\\nBest,\\nSamuel Opeyemi\\nSynq Studio")
    msg['Subject'] = f"Next Steps: {domain} x Synq Studio"
    msg['From'] = "growthprofesors@gmail.com"
    msg['To'] = target_email

    try:
        # Using your secure App Password
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
            smtp.login("growthprofesors@gmail.com", "hthu cwcn smge mdch")
            smtp.send_message(msg)
        return jsonify({"status": "Onboarding Sent"}), 200
    except Exception as e:
        return jsonify({"status": "Error", "message": str(e)}), 500

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
