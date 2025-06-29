import os
import json
import requests
from datetime import datetime
from pathlib import Path
import time
import random

# PDF generation imports
from reportlab.lib.pagesizes import letter, A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY, TA_LEFT

# Email imports
import smtplib
import ssl
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication

# Local Ollama configuration
OLLAMA_URL = "http://localhost:11434/api/generate"
WORKING_DIR = Path("multi_agent_workspace")
WORKING_DIR.mkdir(exist_ok=True)

class EmailService:
    """Professional email service for AI agents"""
    
    def __init__(self):
        self.smtp_server = "smtp.gmail.com"
        self.smtp_port = 587
        self.email_address = ""
        self.email_password = ""
        self.sender_name = "AI Consulting Team"
        
    def setup_credentials(self, email, password):
        """Set up email credentials"""
        self.email_address = email
        self.email_password = password
        
    def send_project_report(self, recipient_email, recipient_name, project_title, 
                          agent_pdfs, summary_pdf=None):
        """Send a complete project report with all agent PDFs"""
        
        msg = MIMEMultipart()
        msg['From'] = f"{self.sender_name} <{self.email_address}>"
        msg['To'] = recipient_email
        msg['Subject'] = f"🤖 Project Delivery: {project_title}"
        
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
                    
                    <p>We're excited to deliver your completed project analysis:</p>
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
                        <h4 style="color: #2e7d32; margin-top: 0;">✅ Project Completion:</h4>
                        <p style="margin-bottom: 0;">Our multi-agent AI team has completed comprehensive analysis 
                        with actionable insights and implementation guidance.</p>
                    </div>
                    
                    <h3 style="color: #667eea;">🚀 Next Steps:</h3>
                    <ol style="background: #fff3cd; border: 1px solid #ffc107; border-radius: 8px; padding: 20px;">
                        <li><strong>Review</strong> each specialist report for detailed insights</li>
                        <li><strong>Prioritize</strong> recommendations based on your objectives</li>
                        <li><strong>Implement</strong> using our provided roadmaps</li>
                        <li><strong>Follow up</strong> with us for additional analysis</li>
                    </ol>
                    
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
        
        # Attach all PDFs
        for pdf_path in agent_pdfs:
            if pdf_path and Path(pdf_path).exists():
                with open(pdf_path, 'rb') as file:
                    attach = MIMEApplication(file.read(), _subtype='pdf')
                    attach.add_header('Content-Disposition', 'attachment', 
                                    filename=Path(pdf_path).name)
                    msg.attach(attach)
        
        # Send email
        try:
            context = ssl.create_default_context()
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls(context=context)
                server.login(self.email_address, self.email_password)
                server.send_message(msg)
            
            return True, "📧 Project report emailed successfully!"
            
        except Exception as e:
            return False, f"❌ Email failed: {str(e)}"

class PDFGenerator:
    """Utility class for generating professional PDFs"""
    
    @staticmethod
    def create_agent_pdf(agent_name, agent_role, content, filename, project_title=""):
        """Create a professional PDF for an agent's output"""
        
        filepath = WORKING_DIR / filename
        doc = SimpleDocTemplate(str(filepath), pagesize=A4)
        styles = getSampleStyleSheet()
        
        # Custom styles
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=18,
            spaceAfter=30,
            alignment=TA_CENTER,
            textColor=colors.darkblue
        )
        
        subtitle_style = ParagraphStyle(
            'CustomSubtitle',
            parent=styles['Heading2'],
            fontSize=14,
            spaceAfter=20,
            alignment=TA_CENTER,
            textColor=colors.blue
        )
        
        agent_style = ParagraphStyle(
            'AgentInfo',
            parent=styles['Normal'],
            fontSize=12,
            spaceAfter=15,
            alignment=TA_CENTER,
            textColor=colors.grey
        )
        
        content_style = ParagraphStyle(
            'ContentStyle',
            parent=styles['Normal'],
            fontSize=11,
            spaceAfter=12,
            alignment=TA_JUSTIFY,
            leftIndent=20,
            rightIndent=20
        )
        
        # Build document content
        story = []
        
        # Header
        if project_title:
            story.append(Paragraph(project_title, title_style))
            story.append(Spacer(1, 20))
        
        # Agent info
        story.append(Paragraph(f"Report by: {agent_name}", subtitle_style))
        story.append(Paragraph(f"Role: {agent_role}", agent_style))
        story.append(Paragraph(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", agent_style))
        story.append(Spacer(1, 30))
        
        # Content
        paragraphs = content.split('\n\n')
        for para in paragraphs:
            if para.strip():
                if (para.strip().startswith('#') or 
                    para.strip().startswith(('1.', '2.', '3.', '4.', '5.')) or
                    (len(para.strip()) < 50 and para.strip().isupper())):
                    heading_text = para.strip().replace('#', '').strip()
                    story.append(Paragraph(heading_text, styles['Heading3']))
                else:
                    story.append(Paragraph(para.strip(), content_style))
                story.append(Spacer(1, 12))
        
        # Footer
        story.append(Spacer(1, 30))
        story.append(Paragraph("— End of Report —", agent_style))
        
        doc.build(story)
        return filepath

class BaseAgent:
    """Base class for all AI agents with PDF and email capabilities"""
    
    def __init__(self, name, role, model="llama3.2:latest", personality=""):
        self.name = name
        self.role = role
        self.model = model
        self.personality = personality
        self.memory = []
        self.tasks_completed = 0
        
    def think(self, prompt, context=""):
        """Core thinking method for the agent"""
        full_prompt = f"""You are {self.name}, a {self.role}.
{self.personality}

Context: {context}

Recent memory:
{chr(10).join(self.memory[-3:]) if self.memory else "No previous interactions"}

Current task: {prompt}

Respond as {self.name} would, staying in character and focusing on your role as {self.role}.
Format your response professionally with clear sections and bullet points where appropriate."""

        try:
            data = {
                "model": self.model,
                "prompt": full_prompt,
                "stream": False
            }
            
            response = requests.post(OLLAMA_URL, json=data)
            result = response.json()
            response_text = result.get('response', 'No response')
            
            self.memory.append(f"{self.name}: {response_text}")
            self.tasks_completed += 1
            
            return response_text
            
        except Exception as e:
            return f"Error in {self.name}: {e}"
    
    def generate_pdf_report(self, content, topic, project_title=""):
        """Generate a PDF report for this agent's work"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"{self.name.replace(' ', '_')}_{timestamp}.pdf"
        
        filepath = PDFGenerator.create_agent_pdf(
            self.name, 
            self.role, 
            content, 
            filename,
            project_title
        )
        
        return filepath

class ResearchAgent(BaseAgent):
    def __init__(self):
        super().__init__(
            name="Dr. Research",
            role="Senior Research Analyst",
            personality="""You are methodical, thorough, and love diving deep into topics. 
You always provide well-structured analysis with multiple perspectives."""
        )
    
    def analyze_topic(self, topic, project_title=""):
        content = self.think(f"""Conduct comprehensive analysis of: {topic}

Provide a professional research report with these sections:

# EXECUTIVE SUMMARY
Brief overview of key findings

# METHODOLOGY  
Research approach and sources

# KEY CONCEPTS AND DEFINITIONS
Essential terms and concepts

# CURRENT TRENDS AND DEVELOPMENTS
What's happening now in this space

# MARKET ANALYSIS
Size, growth, key players (if applicable)

# CHALLENGES AND OPPORTUNITIES
Potential obstacles and advantages

# RECOMMENDATIONS
Actionable next steps

# CONCLUSION
Summary of insights and implications

Format each section clearly with bullet points and specific details.""")
        
        pdf_path = self.generate_pdf_report(content, topic, project_title)
        return content, pdf_path

class ManagerAgent(BaseAgent):
    def __init__(self):
        super().__init__(
            name="Alex Manager",
            role="Project Coordinator",
            personality="""You are organized, decisive, and excellent at breaking down complex projects."""
        )
    
    def plan_project(self, project_description, project_title=""):
        content = self.think(f"""Create detailed project plan for: {project_description}

Format as professional project management document:

# PROJECT OVERVIEW
Project goals, scope, and success criteria

# STAKEHOLDER ANALYSIS
Key stakeholders and their roles

# WORK BREAKDOWN STRUCTURE
Major phases and tasks

# TIMELINE AND MILESTONES
Project schedule with key dates

# RESOURCE REQUIREMENTS
Team, tools, and budget needed

# RISK ASSESSMENT
Potential risks and mitigation strategies

# COMMUNICATION PLAN
How progress will be tracked and reported

# SUCCESS METRICS
How success will be measured

Provide specific, actionable details for each section.""")
        
        pdf_path = self.generate_pdf_report(content, project_description, project_title)
        return content, pdf_path

class WriterAgent(BaseAgent):
    def __init__(self):
        super().__init__(
            name="Maya Writer",
            role="Content Specialist",
            personality="""You are creative, articulate, and skilled at adapting your writing style."""
        )
    
    def create_content(self, content_type, topic, audience="general", project_title=""):
        content = self.think(f"""Create professional {content_type} about {topic} for {audience} audience.

Structure your response as:

# CONTENT BRIEF
Purpose, audience, and objectives

# MAIN CONTENT
The primary deliverable formatted appropriately

# SUPPORTING MATERIALS
Additional elements (headlines, taglines, etc.)

# DISTRIBUTION STRATEGY
How this content should be used

# PERFORMANCE METRICS
How to measure success

Ensure content is engaging, professional, and appropriate for {audience} audience.""")
        
        pdf_path = self.generate_pdf_report(content, f"{content_type}: {topic}", project_title)
        return content, pdf_path

class TechnicalAgent(BaseAgent):
    def __init__(self):
        super().__init__(
            name="Tech Oracle",
            role="Senior Technical Specialist", 
            personality="""You are logical, precise, and excellent at solving technical problems."""
        )
    
    def solve_technical_problem(self, problem, project_title=""):
        content = self.think(f"""Analyze and solve this technical problem: {problem}

Provide comprehensive technical report:

# PROBLEM ANALYSIS
Detailed description and root cause analysis

# TECHNICAL REQUIREMENTS
System requirements and constraints

# PROPOSED SOLUTION
Step-by-step implementation approach

# ARCHITECTURE OVERVIEW
System design and component interactions

# IMPLEMENTATION PLAN
Detailed development phases

# TESTING STRATEGY
Quality assurance and validation approach

# DEPLOYMENT CONSIDERATIONS
Production deployment and monitoring

# MAINTENANCE AND SUPPORT
Ongoing support requirements

Include specific technical details and best practices.""")
        
        pdf_path = self.generate_pdf_report(content, f"Technical Analysis: {problem}", project_title)
        return content, pdf_path

class SupervisorAgent(BaseAgent):
    """Orchestrates the entire multi-agent system with email delivery"""
    
    def __init__(self, email_service=None):
        super().__init__(
            name="Director AI",
            role="Team Supervisor",
            personality="""You are wise, strategic, and excellent at seeing the big picture."""
        )
        
        self.team = {
            'researcher': ResearchAgent(),
            'manager': ManagerAgent(), 
            'writer': WriterAgent(),
            'technical': TechnicalAgent()
        }
        
        self.email_service = email_service
    
    def orchestrate_project_with_email(self, project_request, client_email=None, client_name="Valued Client"):
        """Orchestrate project and optionally email results"""
        
        print(f"\n🎯 {self.name}: Starting project orchestration...")
        project_title = f"Multi-Agent Project: {project_request}"
        
        all_pdfs = []
        
        # Step 1: Supervisor analysis
        analysis = self.think(f"""Create strategic overview for: {project_request}

Provide:
# STRATEGIC ANALYSIS
Project assessment and approach

# TEAM COORDINATION PLAN  
Which agents will be involved and how

# EXPECTED DELIVERABLES
What outputs we'll produce

# SUCCESS FACTORS
Key elements for project success""")
        
        supervisor_pdf = self.generate_pdf_report(analysis, project_request, project_title)
        all_pdfs.append(supervisor_pdf)
        print(f"📋 Strategic Analysis PDF: {supervisor_pdf.name}")
        
        # Step 2: Manager creates project plan
        print(f"\n👔 {self.team['manager'].name}: Creating project plan...")
        _, manager_pdf = self.team['manager'].plan_project(project_request, project_title)
        all_pdfs.append(manager_pdf)
        print(f"📊 Project Plan PDF: {manager_pdf.name}")
        
        # Step 3: Researcher conducts analysis
        print(f"\n🔍 {self.team['researcher'].name}: Conducting research...")
        _, research_pdf = self.team['researcher'].analyze_topic(project_request, project_title)
        all_pdfs.append(research_pdf)
        print(f"📚 Research PDF: {research_pdf.name}")
        
        # Step 4: Technical analysis
        print(f"\n⚙️ {self.team['technical'].name}: Technical analysis...")
        _, tech_pdf = self.team['technical'].solve_technical_problem(
            f"Technical requirements for: {project_request}", project_title
        )
        all_pdfs.append(tech_pdf)
        print(f"🔧 Technical PDF: {tech_pdf.name}")
        
        # Step 5: Writer creates executive summary
        print(f"\n✍️ {self.team['writer'].name}: Creating executive summary...")
        _, writer_pdf = self.team['writer'].create_content(
            "executive summary report",
            f"Multi-agent analysis of: {project_request}",
            "executive", 
            project_title
        )
        all_pdfs.append(writer_pdf)
        print(f"📄 Executive Summary PDF: {writer_pdf.name}")
        
        print(f"\n🏆 Project completed! Generated {len(all_pdfs)} PDF reports.")
        
        # Email delivery
        if client_email and self.email_service:
            print(f"\n📧 Sending project delivery email to {client_email}...")
            success, message = self.email_service.send_project_report(
                client_email, 
                client_name,
                project_request,
                all_pdfs
            )
            print(f"   {message}")
        else:
            print(f"📁 All PDFs saved to: {WORKING_DIR.absolute()}")
        
        return all_pdfs

def interactive_demo():
    """Interactive demo with email integration"""
    print("🤖 MULTI-AGENT AI SYSTEM WITH EMAIL DELIVERY!")
    print(f"📁 Working directory: {WORKING_DIR.absolute()}")
    print("\nYour AI consulting team can now EMAIL professional reports!")
    print("=" * 60)
    
    # Email setup
    email_service = None
    setup_email = input("\n📧 Set up email delivery? (y/n): ").strip().lower()
    
    if setup_email == 'y':
        print("\n🔐 Email Setup (Gmail recommended)")
        print("For Gmail: Enable 2FA, then create App Password")
        
        email = input("📧 Your email: ").strip()
        password = input("🔑 App password: ").strip()
        
        email_service = EmailService()
        email_service.setup_credentials(email, password)
        print("✅ Email service configured!")
    
    supervisor = SupervisorAgent(email_service)
    
    while True:
        print("\n" + "="*50)
        print("Choose an option:")
        print("1. 🚀 Full project with PDF + Email delivery")
        print("2. 📄 Full project (PDFs only)")
        print("3. 👤 Individual agent report")
        print("4. 📂 Open working directory")
        print("5. ❌ Quit")
        
        choice = input("\nYour choice (1-5): ").strip()
        
        if choice == '1' and email_service:
            project = input("\n📝 Project description: ").strip()
            client_email = input("📧 Client email address: ").strip()
            client_name = input("👤 Client name (optional): ").strip() or "Valued Client"
            
            if project and client_email:
                print("\n🚀 Starting multi-agent collaboration with email delivery...\n")
                supervisor.orchestrate_project_with_email(project, client_email, client_name)
        
        elif choice == '1' and not email_service:
            print("❌ Email not configured. Choose option 2 for PDFs only.")
            
        elif choice == '2':
            project = input("\n📝 Project description: ").strip()
            if project:
                print("\n🚀 Starting multi-agent collaboration...\n")
                supervisor.orchestrate_project_with_email(project)
        
        elif choice == '3':
            print("\nAvailable agents:")
            print("1. 🔍 Dr. Research")
            print("2. 👔 Alex Manager")
            print("3. ✍️ Maya Writer")
            print("4. ⚙️ Tech Oracle")
            
            agent_choice = input("Choose agent (1-4): ").strip()
            task = input("Task description: ").strip()
            
            if agent_choice == '1':
                _, pdf = supervisor.team['researcher'].analyze_topic(task)
                print(f"📄 Research PDF: {pdf}")
            elif agent_choice == '2':
                _, pdf = supervisor.team['manager'].plan_project(task)
                print(f"📄 Project Plan PDF: {pdf}")
            elif agent_choice == '3':
                _, pdf = supervisor.team['writer'].create_content("report", task)
                print(f"📄 Content PDF: {pdf}")
            elif agent_choice == '4':
                _, pdf = supervisor.team['technical'].solve_technical_problem(task)
                print(f"📄 Technical PDF: {pdf}")
        
        elif choice == '4':
            import subprocess
            if os.name == 'nt':
                subprocess.run(['explorer', str(WORKING_DIR)])
            print(f"📂 Opened: {WORKING_DIR.absolute()}")
        
        elif choice == '5':
            print("👋 AI consulting system shutting down!")
            break
        
        else:
            print("❌ Invalid choice. Please try again.")

if __name__ == "__main__":
    interactive_demo()