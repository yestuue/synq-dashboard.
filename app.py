from flask import Flask, render_template_string, request, jsonify
import smtplib
from email.message import EmailMessage

# ... (Keep your existing imports and routes)

@app.route('/send_onboarding', methods=['POST'])
def send_onboarding():
    data = request.json
    target_email = data.get('email')
    domain = data.get('domain')
    
    msg = EmailMessage()
    msg.set_content(f"""
    Hi! We're excited to start the transformation of {domain}.
    
    To begin, please provide:
    1. Shopify Staff Access (sam@synqstudio.com)
    2. High-resolution Brand Logo
    3. Product Photography folder
    
    Best,
    Samuel Opeyemi
    Synq Studio
    """)
    
    msg['Subject'] = f"Onboarding: {domain} x Synq Studio"
    msg['From'] = "your-email@gmail.com" # Use your SENDER_EMAIL
    msg['To'] = target_email

    try:
        # Use your existing APP_PASSWORD: hthu cwcn smge mdch
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
            smtp.login("your-email@gmail.com", "hthu cwcn smge mdch")
            smtp.send_message(msg)
        return jsonify({"status": "Onboarding Sent"}), 200
    except Exception as e:
        return jsonify({"status": "Error", "message": str(e)}), 500
