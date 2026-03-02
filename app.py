from flask import Flask, render_template_string, request, jsonify
import csv, os, smtplib
from email.message import EmailMessage
from datetime import datetime

app = Flask(__name__)

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Synq Studio | Command</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <script>
        async function sendOnboarding(email, domain) {
            const btn = event.target;
            btn.innerText = "Sending...";
            const res = await fetch('/send_onboarding', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({email: email, domain: domain})
            });
            const result = await res.json();
            btn.innerText = result.status === "Onboarding Sent" ? "✅ Done" : "❌ Error";
        }
    </script>
</head>
<body class="bg-slate-950 text-slate-200 p-4 font-sans">
    <div class="max-w-md mx-auto">
        <header class="mb-6 flex justify-between items-end border-b border-slate-800 pb-4">
            <div>
                <h1 class="text-xl font-black italic text-white">SYNQ STUDIO</h1>
                <p class="text-[10px] text-blue-400 font-bold uppercase tracking-widest">💰 Pipeline: ${{ pipeline }} | 🚀 {{ high_ticket }} High-Ticket</p>
            </div>
            <div class="text-[10px] text-green-500 font-bold uppercase tracking-widest">● Live</div>
        </header>

        <div class="space-y-4">
            {% for row in leads %}
            <div class="bg-slate-900 border {{ 'border-yellow-500/50' if row[7] == 'High-Ticket' else 'border-slate-800' }} p-4 rounded-xl">
                <div class="flex justify-between text-[10px] mb-2 font-mono text-slate-500">
                    <span>{{ row[0] }}</span>
                    <span class="text-blue-500 uppercase">{{ row[8] }}</span>
                </div>
                <h3 class="text-md font-bold text-white mb-4">{{ row[1] }}</h3>
                <div class="flex gap-2">
                    <a href="https://wa.me/?text=Hi!%20Saw%20your%20{{ row[8] }}%20store%20{{ row[1] }}..." class="flex-1 bg-green-600 text-[10px] font-bold text-center py-2 rounded-lg uppercase">WhatsApp</a>
                    <button onclick="sendOnboarding('contact@{{ row[1] }}', '{{ row[1] }}')" class="flex-1 bg-blue-600 text-[10px] font-bold py-2 rounded-lg uppercase">Onboard</button>
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
    leads, pipeline, high_ticket = [], 0, 0
    if os.path.exists('synq_leads.csv'):
        with open('synq_leads.csv', 'r') as f:
            data = list(csv.reader(f))
            if len(data) > 1:
                for row in data[1:]:
                    if row[7] == "High-Ticket":
                        high_ticket += 1
                        pipeline += 1200
                    elif row[7] == "Mid-Range": pipeline += 600
                    if row[7] != "Low": leads.append(row)
    return render_template_string(HTML_TEMPLATE, leads=leads[::-1], pipeline=pipeline, high_ticket=high_ticket)

@app.route('/add_lead', methods=['POST'])
def add_lead():
    data = request.json
    file_path = 'synq_leads.csv'
    with open(file_path, 'a', newline='') as f:
        writer = csv.writer(f)
        if not os.path.isfile(file_path):
            writer.writerow(['Date', 'Domain', 'Instagram', 'Facebook', 'Score', 'Issue', 'Revenue', 'Theme'])
        writer.writerow([datetime.now().strftime("%Y-%m-%d %H:%M"), data['domain'], data['insta'], data['fb'], data['score'], data['issue'], data.get('revenue', 'Low'), data.get('theme', 'Dawn')])
    return jsonify({"status": "success"}), 200

@app.route('/send_onboarding', methods=['POST'])
def send_onboarding():
    data = request.json
    msg = EmailMessage()
    msg.set_content(f"Hi! Let's build {data['domain']}.\\n\\nSteps:\\n1. Grant Staff Access to growthprofesors@gmail.com\\n2. Send Logo\\n3. Send Photos.\\n\\n- Sam, Synq Studio")
    msg['Subject'] = f"Next Steps: {data['domain']} x Synq Studio"
    msg['From'], msg['To'] = "growthprofesors@gmail.com", data['email']
    try:
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
            smtp.login("growthprofesors@gmail.com", "hthu cwcn smge mdch")
            smtp.send_message(msg)
        return jsonify({"status": "Onboarding Sent"}), 200
    except: return jsonify({"status": "Error"}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 5000)))
