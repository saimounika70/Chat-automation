import streamlit as st
import pywhatkit as pwk
from datetime import datetime
import time
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# UI setup
st.set_page_config(
    page_title="📧📱 Chat Automation Tool",
    page_icon="💬",
    layout="centered"
)

st.sidebar.title("Select your application")
app = st.sidebar.selectbox(
    "Select Application",
    options=["WhatsApp", "GMail"],
    index=0
)

with st.sidebar:
    st.header("📋 Instructions")
    st.write("""
    **WhatsApp:**
    - Login to WhatsApp Web first
    - Enter phone numbers with country code (+91...)
    - Set time at least 2 minutes ahead
    - Leave browser open and untouched

    **GMail:**
    - Use Gmail App Password (not your regular Gmail password)
    - Fill in all fields correctly
    """)

# --------------------------- WhatsApp Function --------------------------- #
def send_whatsapp_message():
    st.title("📱 WhatsApp Message Sender")
    
    st.info("📱 Make sure WhatsApp Web is logged in on your default browser before sending messages.")
    
    input_numbers = st.text_area(
        "Enter phone numbers (one per line, with country code, e.g., +1234567890):",
        placeholder="+1234567890\n+9876543210"
    )
    
    message = st.text_area("Enter your message:", placeholder="Hello! This is an automated message.")

    col1, col2 = st.columns(2)
    with col1:
        hour = st.number_input("Hour (24-hour format):", min_value=0, max_value=23, value=datetime.now().hour)
    with col2:
        minute = st.number_input("Minute:", min_value=0, max_value=59, value=(datetime.now().minute + 2) % 60)

    numbers_list = [num.strip() for num in input_numbers.splitlines() if num.strip()]

    if numbers_list:
        st.write(f"📞 Found {len(numbers_list)} phone number(s):")
        for i, num in enumerate(numbers_list, 1):
            st.write(f"{i}. {num}")

    if st.button("Send WhatsApp Message", type="primary"):
        if not numbers_list:
            st.error("❌ Please enter at least one phone number.")
        elif not message.strip():
            st.error("❌ Please enter a message.")
        else:
            current_time = datetime.now()
            scheduled_time = current_time.replace(hour=hour, minute=minute, second=0, microsecond=0)
            if scheduled_time <= current_time:
                st.warning("⚠️ Scheduled time should be at least 1-2 minutes in the future.")
                return

            progress_bar = st.progress(0)
            status_text = st.empty()
            success_count = 0
            error_count = 0

            for i, number in enumerate(numbers_list):
                try:
                    status_text.text(f"📤 Sending message to {number}...")

                    if not number.startswith('+'):
                        st.error(f"❌ Invalid format for {number}. Must start with country code (+)")
                        error_count += 1
                        continue

                    if i == 0:
                        pwk.sendwhatmsg(
                            phone_no=number,
                            message=message,
                            time_hour=hour,
                            time_min=minute,
                            wait_time=15,
                            tab_close=True,
                            close_time=3
                        )
                    else:
                        pwk.sendwhatmsg_instantly(
                            phone_no=number,
                            message=message,
                            wait_time=15,
                            tab_close=True,
                            close_time=3
                        )

                    st.success(f"✅ Message scheduled to {number} at {hour:02d}:{minute:02d}")
                    success_count += 1

                    if i < len(numbers_list) - 1:
                        time.sleep(2)

                except Exception as e:
                    st.error(f"❌ Error sending to {number}: {str(e)}")
                    error_count += 1

                progress_bar.progress((i + 1) / len(numbers_list))
                minute += 1
                if minute >= 60:
                    minute = 0
                    hour += 1

            status_text.text("✅ Process completed!")
            st.write("### Summary")
            st.write(f"✅ Sent: {success_count}")
            if error_count:
                st.write(f"❌ Failed: {error_count}")
            st.write("### Important Notes:")
            st.write("- Keep your browser open")
            st.write("- Do not use your system while messages are being sent")

# --------------------------- Gmail Function --------------------------- #
def send_gmail_message():
    st.title("📧 GMail Message Sender")
    recipient_email = st.text_input("Recipient's Email:")
    subject = st.text_input("Subject:")
    message = st.text_area("Message:")
    sender_email = st.text_input("Your Gmail Address:")
    sender_password = st.text_input("Gmail App Password:", type="password")

    if st.button("Send GMail Message"):
        if recipient_email and subject and message and sender_email and sender_password:
            try:
                msg = MIMEMultipart()
                msg['From'] = sender_email
                msg['To'] = recipient_email
                msg['Subject'] = subject
                msg.attach(MIMEText(message, 'plain'))
                
                server = smtplib.SMTP('smtp.gmail.com', 587)
                server.starttls()
                server.login(sender_email, sender_password)
                server.sendmail(sender_email, recipient_email, msg.as_string())
                server.quit()
                
                st.success(f"✅ Email sent to {recipient_email} with subject '{subject}'.")
            except Exception as e:
                st.error(f"❌ Error: {e}")
        else:
            st.error("❌ Please fill in all fields.")

# --------------------------- Route --------------------------- #
if app == "WhatsApp":
    send_whatsapp_message()
elif app == "GMail":
    send_gmail_message()

elif app == "GmailBulk":
    send_gmail_bulk_message()
