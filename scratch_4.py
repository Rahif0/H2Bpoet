import requests
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import json
import sqlite3
import time
from jinja2 import Environment, FileSystemLoader
import os


# Create templates directory and files
def setup_templates():
    os.makedirs("templates", exist_ok=True)

    # Create newsletter.html
    with open("templates/newsletter.html", "w") as f:
        f.write("""
        <html>
        <body>
            <h1>Newsletter</h1>
            <p>{{ content }}</p>
        </body>
        </html>
        """)

    # Create abandoned_cart.html
    with open("templates/abandoned_cart.html", "w") as f:
        f.write("""
        <html>
        <body>
            <h1>Complete Your Purchase</h1>
            <p>Items in your cart: {{ cart }}</p>
        </body>
        </html>
        """)

    # Create promo.html
    with open("templates/promo.html", "w") as f:
        f.write("""
        <html>
        <body>
            <h1>Special Offer</h1>
            <p>{{ content }}</p>
        </body>
        </html>
        """)


# WooCommerce API credentials
WC_API_URL = "http://rahifs.local//wp-json/wc/v3/"
WC_CONSUMER_KEY = "your_consumer_key"
WC_CONSUMER_SECRET = "your_consumer_secret"

# Email configuration
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587
EMAIL_USER = "joshikavar719@gmail.com"
EMAIL_PASS = "abcd-1234-efgh-5678"


# Database setup for subscribers
def init_db():
    conn = sqlite3.connect("subscribers.db")
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS subscribers 
                 (email TEXT PRIMARY KEY, subscribed_at TIMESTAMP)''')
    conn.commit()
    conn.close()


# Fetch customer data from WooCommerce
def get_customer_data():
    url = f"{WC_API_URL}customers"
    response = requests.get(url, auth=(WC_CONSUMER_KEY, WC_CONSUMER_SECRET))
    return response.json()


# Fetch abandoned carts (simplified logic)
def get_abandoned_carts():
    url = f"{WC_API_URL}orders?status=pending"
    response = requests.get(url, auth=(WC_CONSUMER_KEY, WC_CONSUMER_SECRET))
    return [order for order in response.json() if "cart" in order]


# Send email
def send_email(to_email, subject, html_content):
    msg = MIMEMultipart("alternative")
    msg["Subject"] = subject
    msg["From"] = EMAIL_USER
    msg["To"] = to_email
    msg.attach(MIMEText(html_content, "html"))

    with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
        server.starttls()
        server.login(EMAIL_USER, EMAIL_PASS)
        server.send_message(msg)


# Load email template
def render_template(template_name, **kwargs):
    env = Environment(loader=FileSystemLoader("templates"))
    template = env.get_template(template_name)
    return template.render(**kwargs)


# Handle newsletter subscriptions
def add_subscriber(email):
    conn = sqlite3.connect("subscribers.db")
    c = conn.cursor()
    c.execute("INSERT OR IGNORE INTO subscribers (email, subscribed_at) VALUES (?, ?)",
              (email, time.time()))
    conn.commit()
    conn.close()


# Send newsletter to subscribers
def send_newsletter(content):
    conn = sqlite3.connect("subscribers.db")
    c = conn.cursor()
    subscribers = c.execute("SELECT email FROM subscribers").fetchall()
    conn.close()

    html_content = render_template("newsletter.html", content=content)
    for subscriber in subscribers:
        send_email(subscriber[0], "Our Latest Newsletter", html_content)


# Abandoned cart reminder
def send_abandoned_cart_reminder():
    carts = get_abandoned_carts()
    for cart in carts:
        customer_email = cart.get("billing", {}).get("email")
        if customer_email:
            html_content = render_template("abandoned_cart.html", cart=cart)
            send_email(customer_email, "Complete Your Purchase!", html_content)


# Example A/B testing for email subject
def ab_test_email(to_email, content):
    subject_a = "Special Offer Just for You!"
    subject_b = "Don’t Miss Out on This Deal!"
    html_content = render_template("promo.html", content=content)

    subject = subject_a if time.time() % 2 == 0 else subject_b
    send_email(to_email, subject, html_content)


if __name__ == "__main__":
    setup_templates()  # Create templates before running
    init_db()
    # Example usage
    add_subscriber("rahifbinfaim@gmail.com")
    send_newsletter("Check out our new products!")
    send_abandoned_cart_reminder()