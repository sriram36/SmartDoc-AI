import os
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
from dotenv import load_dotenv

load_dotenv()
SENDGRID_API_KEY = os.getenv("EMAIL_API_KEY")
EMAIL_FROM = os.getenv("EMAIL_FROM", "noreply@yourdomain.com")

def send_email(to_email: str, subject: str, html_content: str) -> int:
    message = Mail(
        from_email=EMAIL_FROM,
        to_emails=to_email,
        subject=subject,
        html_content=html_content
    )
    try:
        sg = SendGridAPIClient(SENDGRID_API_KEY)
        response = sg.send(message)
        return response.status_code
    except Exception as e:
        print(f"Email send error: {e}")
        return 500

def send_summary_notification(to_email: str, document_name: str, summary_text: str) -> int:
    """Send email notification when document summary is ready"""
    subject = "Your Document Summary is Ready! - SmartDoc AI"
    
    # Truncate summary for email if it's too long
    preview_summary = summary_text[:500] + "..." if len(summary_text) > 500 else summary_text
    
    html_content = f"""
    <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
        <h2 style="color: #2c3e50;">📄 Your Document Summary is Ready!</h2>
        
        <p>Hello!</p>
        
        <p>We've successfully analyzed your document and generated a comprehensive summary.</p>
        
        <div style="background-color: #f8f9fa; padding: 15px; border-left: 4px solid #3498db; margin: 20px 0;">
            <h3 style="margin-top: 0; color: #2c3e50;">Document: {document_name}</h3>
        </div>
        
        <div style="background-color: #ffffff; padding: 20px; border: 1px solid #dee2e6; border-radius: 5px; margin: 20px 0;">
            <h4 style="color: #495057;">Summary:</h4>
            <p style="line-height: 1.6; color: #6c757d;">{preview_summary}</p>
        </div>
        
        <p>Log in to your SmartDoc AI account to view the complete summary and manage your documents.</p>
        
        <div style="margin-top: 30px; padding-top: 20px; border-top: 1px solid #dee2e6;">
            <p style="color: #6c757d; font-size: 12px;">
                This is an automated notification from SmartDoc AI.<br>
                You can disable these notifications in your account settings.
            </p>
        </div>
    </div>
    """
    
    return send_email(to_email, subject, html_content)