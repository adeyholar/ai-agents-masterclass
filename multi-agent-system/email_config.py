import smtplib
import ssl
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication
from pathlib import Path
import os

class EmailService:
    """Professional email service for AI agents"""
    
    def __init__(self):
        # Email configuration (you'll need to set these up)
        self.smtp_server = "smtp.gmail.com"  # Gmail SMTP
        self.smtp_port = 587
        self.email_address = ""  # Your email here
        self.email_password = ""  # Your app password here
        self.sender_name = "AI Consulting Team"
        
    def setup_credentials(self, email, password):
        """Set up email credentials"""
        self.email_address = email
        self.email_password = password
        
    def send_project_report(self, recipient_email, recipient_name, project_title, 
                          agent_reports, summary_pdf=None):
        """Send a complete project report with all agent PDFs"""
        
        # Create message
        msg = MIMEMultipart()
        msg['From'] = f"{self.sender_name} <{self.email_address}>"
        msg['To'] = recipient_email
        msg['Subject'] = f"Project Delivery: {project_title}"
        
        # Email body
        html_body = f"""
        <html>
        <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
            <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
                <header style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                              color: white; padding: 30px; text-align: center; border-radius: 10px;">
                    <h1 style="margin: 0; font-size: 28px;">🤖 AI Consulting Team</h1>
                    <p style="margin: 10px 0 0 0; font-size: 16px; opacity: 0.9;">
                        Professional Multi-Agent Analysis Delivery
                    </p>
                </header>
                
                <main style="padding: 30px 0;">
                    <h2 style="color: #667eea;">Dear {recipient_name},</h2>
                    
                    <p>We're excited to deliver your completed project analysis for:</p>
                    <h3 style="color: #764ba2; background: #f8f9fa; padding: 15px; border-radius: 8px; border-left: 4px solid #667eea;">
                        📋 {project_title}
                    </h3>
                    
                    <h3 style="color: #667eea;">📄 Deliverables Included:</h3>
                    <div style="background: #f8f9fa; padding: 20px; border-radius: 8px; margin: 20px 0;">
                        <ul style="list-style: none; padding: 0;">
                            <li style="padding: 8px 0; border-bottom: 1px solid #e9ecef;">
                                🔍 <strong>Research Analysis</strong> - Market research and competitive analysis
                            </li>
                            <li style="padding: 8px 0; border-bottom: 1px solid #e9ecef;">
                                👔 <strong>Project Management Plan</strong> - Timeline, resources, and milestones
                            </li>
                            <li style="padding: 8px 0; border-bottom: 1px solid #e9ecef;">
                                ⚙️ <strong>Technical Architecture</strong> - Implementation roadmap and specifications
                            </li>
                            <li style="padding: 8px 0; border-bottom: 1px solid #e9ecef;">
                                ✍️ <strong>Executive Summary</strong> - Strategic overview for stakeholders
                            </li>
                            <li style="padding: 8px 0;">
                                🎯 <strong>Strategic Overview</strong> - Comprehensive project coordination
                            </li>
                        </ul>
                    </div>
                    
                    <div style="background: #e8f5e8; border: 1px solid #4caf50; border-radius: 8px; padding: 20px; margin: 20px 0;">
                        <h4 style="color: #2e7d32; margin-top: 0;">✅ Project Completion Summary:</h4>
                        <p style="margin-bottom: 0;">Our multi-agent AI team has completed a comprehensive analysis 
                        of your project requirements. Each specialist has contributed their expertise to deliver 
                        actionable insights and implementation guidance.</p>
                    </div>
                    
                    <h3 style="color: #667eea;">🚀 Next Steps:</h3>
                    <ol style="background: #fff3cd; border: 1px solid #ffc107; border-radius: 8px; padding: 20px;">
                        <li><strong>Review</strong> each specialist report for detailed insights</li>
                        <li><strong>Prioritize</strong> recommendations based on your objectives</li>
                        <li><strong>Implement</strong> using our provided roadmaps and timelines</li>
                        <li><strong>Follow up</strong> with us for any clarifications or additional analysis</li>
                    </ol>
                    
                    <p style="margin-top: 30px;">
                        Thank you for choosing our AI consulting services. We're here to support your success!
                    </p>
                    
                    <div style="text-align: center; margin-top: 40px; padding-top: 30px; border-top: 2px solid #e9ecef;">
                        <p style="color: #6c757d; font-size: 14px; margin: 0;">
                            Best regards,<br>
                            <strong style="color: #667eea;">The AI Consulting Team</strong><br>
                            <em>Dr. Research • Alex Manager • Maya Writer • Tech Oracle • Director AI</em>
                        </p>
                    </div>
                </main>
            </div>
        </body>
        </html>
        """
        
        msg.attach(MIMEText(html_body, 'html'))
        
        # Attach PDF reports
        for agent_name, pdf_path in agent_reports.items():
            if pdf_path and Path(pdf_path).exists():
                with open(pdf_path, 'rb') as file:
                    attach = MIMEApplication(file.read(), _subtype='pdf')
                    attach.add_header('Content-Disposition', 'attachment', 
                                    filename=f"{agent_name}_Report.pdf")
                    msg.attach(attach)
        
        # Attach summary PDF if provided
        if summary_pdf and Path(summary_pdf).exists():
            with open(summary_pdf, 'rb') as file:
                attach = MIMEApplication(file.read(), _subtype='pdf')
                attach.add_header('Content-Disposition', 'attachment', 
                                filename="Project_Summary.pdf")
                msg.attach(attach)
        
        # Send email
        try:
            # Create secure connection and send
            context = ssl.create_default_context()
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls(context=context)
                server.login(self.email_address, self.email_password)
                server.send_message(msg)
            
            return True, "Email sent successfully!"
            
        except Exception as e:
            return False, f"Email failed: {str(e)}"
    
    def send_single_agent_report(self, recipient_email, agent_name, agent_role, 
                               report_topic, pdf_path):
        """Send a single agent report"""
        
        msg = MIMEMultipart()
        msg['From'] = f"{agent_name} - AI Specialist <{self.email_address}>"
        msg['To'] = recipient_email
        msg['Subject'] = f"{agent_role} Report: {report_topic}"
        
        html_body = f"""
        <html>
        <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
            <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
                <header style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                              color: white; padding: 20px; text-align: center; border-radius: 10px;">
                    <h1 style="margin: 0;">🤖 {agent_name}</h1>
                    <p style="margin: 5px 0 0 0; opacity: 0.9;">{agent_role}</p>
                </header>
                
                <main style="padding: 20px 0;">
                    <h2 style="color: #667eea;">Specialist Report Delivered</h2>
                    
                    <div style="background: #f8f9fa; padding: 20px; border-radius: 8px; border-left: 4px solid #667eea;">
                        <h3 style="margin-top: 0; color: #764ba2;">📋 {report_topic}</h3>
                        <p>Please find attached my detailed analysis and recommendations.</p>
                    </div>
                    
                    <p style="margin-top: 20px;">
                        This report contains my specialized insights and actionable recommendations 
                        based on my expertise as a {agent_role}.
                    </p>
                    
                    <div style="text-align: center; margin-top: 30px;">
                        <p style="color: #6c757d;">
                            Best regards,<br>
                            <strong style="color: #667eea;">{agent_name}</strong>
                        </p>
                    </div>
                </main>
            </div>
        </body>
        </html>
        """
        
        msg.attach(MIMEText(html_body, 'html'))
        
        # Attach PDF
        if pdf_path and Path(pdf_path).exists():
            with open(pdf_path, 'rb') as file:
                attach = MIMEApplication(file.read(), _subtype='pdf')
                attach.add_header('Content-Disposition', 'attachment', 
                                filename=f"{agent_name}_Report.pdf")
                msg.attach(attach)
        
        # Send email
        try:
            context = ssl.create_default_context()
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls(context=context)
                server.login(self.email_address, self.email_password)
                server.send_message(msg)
            
            return True, "Email sent successfully!"
            
        except Exception as e:
            return False, f"Email failed: {str(e)}"

def setup_email_service():
    """Interactive setup for email service"""
    print("📧 Email Service Setup")
    print("=" * 30)
    
    email_service = EmailService()
    
    print("\n🔐 For Gmail, you'll need an 'App Password' (not your regular password)")
    print("📝 How to get Gmail App Password:")
    print("   1. Go to Google Account settings")
    print("   2. Security → 2-Step Verification")
    print("   3. App passwords → Generate new")
    print("   4. Use that 16-character password here")
    
    email = input("\n📧 Your email address: ").strip()
    password = input("🔑 Your app password: ").strip()
    
    email_service.setup_credentials(email, password)
    
    # Test email
    test_email = input("\n📮 Test email address (or press Enter to skip test): ").strip()
    if test_email:
        print("📤 Sending test email...")
        success, message = email_service.send_single_agent_report(
            test_email, 
            "Test Agent", 
            "Email Test Specialist",
            "Email Integration Test",
            None
        )
        
        if success:
            print("✅ Test email sent successfully!")
        else:
            print(f"❌ Test failed: {message}")
    
    return email_service