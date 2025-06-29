import os
import json
import requests
import smtplib
import ssl
import subprocess
import logging
import re
from datetime import datetime
from pathlib import Path
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication
from getpass import getpass
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY, TA_LEFT

# Configuration
OLLAMA_URL = os.getenv("OLLAMA_URL", "http://localhost:11434/api/generate")
WORKING_DIR = Path(f"multi_agent_workspace_{datetime.now().strftime('%Y%m%d_%H%M%S')}")
WORKING_DIR.mkdir(exist_ok=True)

# Logging setup
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler(WORKING_DIR / "elite_consulting.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class EmailService:
    """Professional email service for AI agents"""
    
    def __init__(self, smtp_server="smtp.gmail.com", smtp_port=587):
        self.smtp_server = smtp_server
        self.smtp_port = smtp_port
        self.email_address = ""
        self.email_password = ""
        self.sender_name = "Elite AI Consulting Team"
        
    def setup_credentials(self, email, password):
        """Set up email credentials"""
        self.email_address = email
        self.email_password = password
        logger.info("Email credentials configured for %s", email)
        
    def send_project_report(self, recipient_email, recipient_name, project_title, agent_pdfs):
        """Send a complete project report with all agent PDFs"""
        if not re.match(r"[^@]+@[^@]+\.[^@]+", recipient_email):
            logger.error("Invalid recipient email: %s", recipient_email)
            return False, "Invalid email address"

        msg = MIMEMultipart()
        msg['From'] = f"{self.sender_name} <{self.email_address}>"
        msg['To'] = recipient_email
        msg['Subject'] = f"🎯 Elite Consulting Delivery: {project_title}"
        
        html_body = f"""
        <html>
        <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
            <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
                <header style="background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%); 
                              color: white; padding: 30px; text-align: center; border-radius: 10px;">
                    <h1 style="margin: 0; font-size: 28px;">🧠 Elite AI Consulting Team</h1>
                    <p style="margin: 10px 0 0 0; font-size: 16px; opacity: 0.9;">
                        Fortune 500-Level Multi-Agent Analysis
                    </p>
                </header>
                <main style="padding: 30px 0;">
                    <h2 style="color: #1e3c72;">Dear {recipient_name},</h2>
                    <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                                color: white; padding: 20px; border-radius: 8px; margin: 20px 0;">
                        <h3 style="margin-top: 0; color: white;">📋 Project Delivered:</h3>
                        <h2 style="margin: 10px 0; color: white;">{project_title}</h2>
                    </div>
                    <p style="margin-top: 30px; font-size: 16px;">
                        Thank you for choosing our Elite AI Consulting services.
                    </p>
                </main>
            </div>
        </body>
        </html>
        """
        
        msg.attach(MIMEText(html_body, 'html'))
        
        # Attach PDFs
        missing_pdfs = []
        for pdf_path in agent_pdfs:
            pdf_path = Path(pdf_path)
            if pdf_path.exists():
                with open(pdf_path, 'rb') as file:
                    attach = MIMEApplication(file.read(), _subtype='pdf')
                    attach.add_header('Content-Disposition', 'attachment', filename=pdf_path.name)
                    msg.attach(attach)
            else:
                missing_pdfs.append(pdf_path)
        
        if missing_pdfs:
            logger.warning("Missing PDF files: %s", missing_pdfs)
        
        # Send email
        try:
            context = ssl.create_default_context()
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls(context=context)
                server.login(self.email_address, self.email_password)
                server.send_message(msg)
            logger.info("Email sent successfully to %s", recipient_email)
            return True, "🎯 Elite consulting report delivered successfully!"
        except Exception as e:
            logger.error("Email delivery failed: %s", str(e))
            return False, f"❌ Email delivery failed: {str(e)}"

class PDFGenerator:
    """Utility class for generating professional PDFs"""
    
    @staticmethod
    def create_agent_pdf(agent_name, agent_role, content, filename, project_title=""):
        """Create a professional PDF for an agent's output"""
        try:
            filepath = WORKING_DIR / filename
            doc = SimpleDocTemplate(str(filepath), pagesize=A4)
            styles = getSampleStyleSheet()
            
            # Custom styles
            title_style = ParagraphStyle(
                'CustomTitle', parent=styles['Heading1'], fontSize=20, spaceAfter=30,
                alignment=TA_CENTER, textColor=colors.darkblue
            )
            subtitle_style = ParagraphStyle(
                'CustomSubtitle', parent=styles['Heading2'], fontSize=16, spaceAfter=20,
                alignment=TA_CENTER, textColor=colors.blue
            )
            agent_style = ParagraphStyle(
                'AgentInfo', parent=styles['Normal'], fontSize=12, spaceAfter=15,
                alignment=TA_CENTER, textColor=colors.grey
            )
            content_style = ParagraphStyle(
                'ContentStyle', parent=styles['Normal'], fontSize=11, spaceAfter=12,
                alignment=TA_JUSTIFY, leftIndent=20, rightIndent=20
            )
            
            story = [
                Paragraph("🧠 ELITE AI CONSULTING", title_style),
                Spacer(1, 20) if project_title else Spacer(1, 0),
                Paragraph(project_title, subtitle_style) if project_title else None,
                Spacer(1, 20),
                Paragraph(f"Report by: {agent_name}", subtitle_style),
                Paragraph(f"Role: {agent_role}", agent_style),
                Paragraph(f"AI Model: {'70B Intelligence' if '70b' in agent_name.lower() or agent_name in ['Dr. Research', 'Director AI'] else 'Specialist AI'}", agent_style),
                Paragraph(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", agent_style),
                Spacer(1, 30)
            ]
            
            # Content
            for para in content.split('\n\n'):
                if para.strip():
                    if (para.strip().startswith('#') or 
                        para.strip().startswith(('1.', '2.', '3.', '4.', '5.')) or
                        (len(para.strip()) < 50 and para.strip().isupper())):
                        story.append(Paragraph(para.strip().replace('#', '').strip(), styles['Heading3']))
                    else:
                        story.append(Paragraph(para.strip(), content_style))
                    story.append(Spacer(1, 12))
            
            story.extend([Spacer(1, 30), Paragraph("— Elite AI Consulting Report —", agent_style)])
            doc.build([s for s in story if s is not None])
            logger.info("PDF generated: %s", filepath)
            return filepath
        except Exception as e:
            logger.error("PDF generation failed for %s: %s", filename, str(e))
            raise

class BaseAgent:
    """Base class for all AI agents with enhanced capabilities"""
    
    def __init__(self, name, role, model="llama3.2:latest", personality=""):
        self.name = name
        self.role = role
        self.model = model
        self.personality = personality
        self.memory = []
        self.tasks_completed = 0
        
    def check_model_availability(self):
        """Check if the specified model is available in Ollama"""
        try:
            response = requests.get(f"{OLLAMA_URL.rsplit('/api/generate', 1)[0]}/api/tags")
            available_models = [m['name'] for m in response.json().get('models', [])]
            return self.model in available_models
        except Exception as e:
            logger.error("Failed to check model availability: %s", str(e))
            return False
    
    def think(self, prompt, context=""):
        """Core thinking method for the agent with enhanced prompting"""
        if not self.check_model_availability():
            logger.error("Model %s not available", self.model)
            return f"Error: Model {self.model} not available"
        
        full_prompt = f"""You are {self.name}, a {self.role} at an elite consulting firm.
{self.personality}
Context: {context}
Recent memory: {chr(10).join(self.memory[-3:]) if self.memory else 'No previous interactions'}
Current task: {prompt}
Respond with professional, data-driven analysis."""
        
        try:
            response = requests.post(OLLAMA_URL, json={"model": self.model, "prompt": full_prompt, "stream": False})
            response.raise_for_status()
            result = response.json().get('response', 'No response')
            self.memory.append(f"{self.name}: {result}")
            self.tasks_completed += 1
            logger.info("%s completed task: %s", self.name, prompt[:50])
            return result
        except Exception as e:
            logger.error("%s error: %s", self.name, str(e))
            return f"Error in {self.name}: {str(e)}"
    
    def generate_pdf_report(self, content, topic, project_title=""):
        """Generate a PDF report for this agent's work"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"{self.name.replace(' ', '_')}_{timestamp}.pdf"
        return PDFGenerator.create_agent_pdf(self.name, self.role, content, filename, project_title)

class ResearchAgent(BaseAgent):
    """70B-powered research specialist"""
    def __init__(self):
        super().__init__(
            name="Dr. Research", role="Senior Research Analyst (70B Intelligence)",
            model="llama3.3:70b", personality="World-class research analyst with comprehensive industry insights."
        )
    
    def analyze_topic(self, topic, project_title=""):
        content = self.think(f"Conduct comprehensive analysis of: {topic}")
        pdf_path = self.generate_pdf_report(content, topic, project_title)
        return content, pdf_path

class ManagerAgent(BaseAgent):
    """Strategic project coordination specialist"""
    def __init__(self):
        super().__init__(
            name="Alex Manager", role="Senior Project Coordinator",
            model="llama3.2:latest", personality="Elite project management consultant."
        )
    
    def plan_project(self, project_description, project_title=""):
        content = self.think(f"Create enterprise project plan for: {project_description}")
        pdf_path = self.generate_pdf_report(content, project_description, project_title)
        return content, pdf_path

class WriterAgent(BaseAgent):
    """Executive communication specialist"""
    def __init__(self):
        super().__init__(
            name="Maya Writer", role="Senior Content Strategist",
            model="llama3.2:latest", personality="Elite communications consultant."
        )
    
    def create_content(self, content_type, topic, audience="executive", project_title=""):
        content = self.think(f"Create {content_type} about {topic} for {audience} audience.")
        pdf_path = self.generate_pdf_report(content, f"{content_type}: {topic}", project_title)
        return content, pdf_path

class TechnicalAgent(BaseAgent):
    """Technical architecture and implementation specialist"""
    def __init__(self):
        super().__init__(
            name="Tech Oracle", role="Chief Technical Architect",
            model="codellama:latest", personality="Senior technical architect."
        )
    
    def solve_technical_problem(self, problem, project_title=""):
        content = self.think(f"Provide technical analysis for: {problem}")
        pdf_path = self.generate_pdf_report(content, f"Technical Analysis: {problem}", project_title)
        return content, pdf_path

class SupervisorAgent(BaseAgent):
    """70B-powered strategic oversight and coordination"""
    def __init__(self, email_service=None):
        super().__init__(
            name="Director AI", role="Chief Strategy Officer (70B Intelligence)",
            model="llama3.3:70b", personality="Senior executive consultant."
        )
        self.team = {
            'researcher': ResearchAgent(),
            'manager': ManagerAgent(),
            'writer': WriterAgent(),
            'technical': TechnicalAgent()
        }
        self.email_service = email_service
    
    def orchestrate_project_with_email(self, project_request, client_email=None, client_name="Valued Client"):
        """Orchestrate elite consulting project with 70B intelligence"""
        if not project_request:
            logger.error("Project request cannot be empty")
            return []
        
        logger.info("Initiating elite consulting engagement for: %s", project_request)
        project_title = f"Elite Consulting Project: {project_request}"
        all_pdfs = []
        
        # Strategic oversight
        analysis = self.think(f"Provide strategic assessment for: {project_request}")
        supervisor_pdf = self.generate_pdf_report(analysis, project_request, project_title)
        all_pdfs.append(supervisor_pdf)
        logger.info("Strategic Assessment: %s", supervisor_pdf.name)
        
        # Research intelligence
        _, research_pdf = self.team['researcher'].analyze_topic(project_request, project_title)
        all_pdfs.append(research_pdf)
        logger.info("Market Intelligence: %s", research_pdf.name)
        
        # Project coordination
        _, manager_pdf = self.team['manager'].plan_project(project_request, project_title)
        all_pdfs.append(manager_pdf)
        logger.info("Project Roadmap: %s", manager_pdf.name)
        
        # Technical architecture
        _, tech_pdf = self.team['technical'].solve_technical_problem(
            f"Technical architecture for: {project_request}", project_title
        )
        all_pdfs.append(tech_pdf)
        logger.info("Technical Architecture: %s", tech_pdf.name)
        
        # Executive communications
        _, writer_pdf = self.team['writer'].create_content(
            "executive strategic brief", f"Integrated analysis: {project_request}",
            "C-suite executives", project_title
        )
        all_pdfs.append(writer_pdf)
        logger.info("Executive Brief: %s", writer_pdf.name)
        
        logger.info("Generated %d professional deliverables", len(all_pdfs))
        
        # Email delivery
        if client_email and self.email_service:
            success, message = self.email_service.send_project_report(
                client_email, client_name, project_request, all_pdfs
            )
            logger.info(message)
        else:
            logger.info("Deliverables saved: %s", WORKING_DIR.absolute())
        
        return all_pdfs

def interactive_demo():
    """Interactive demo of elite AI consulting system"""
    logger.info("Starting Elite AI Consulting System")
    print("🧠 ELITE AI CONSULTING SYSTEM\n" + "="*60)
    
    email_service = None
    if input("\n📧 Configure email delivery? (y/n): ").strip().lower() == 'y':
        print("\n🔐 Elite Email Configuration")
        email = input("📧 Your email address: ").strip()
        password = getpass("🔑 Gmail app password: ")
        if email and password:
            email_service = EmailService()
            email_service.setup_credentials(email, password)
    
    supervisor = SupervisorAgent(email_service)
    
    while True:
        print("\n" + "="*60 + "\n🎯 ELITE CONSULTING OPTIONS:")
        for i, opt in enumerate([
            "Full Elite Project (70B + Email)", "Elite Project Analysis (PDFs Only)",
            "Individual Specialist Consultation", "Open Elite Workspace",
            "Test 70B Research Intelligence", "Exit Elite System"
        ], 1):
            print(f"{i}. {opt}")
        
        choice = input("\nSelect option (1-6): ").strip()
        if choice not in {'1', '2', '3', '4', '5', '6'}:
            print("❌ Invalid selection. Choose 1-6.")
            continue
        
        if choice == '6':
            logger.info("Shutting down Elite AI Consulting System")
            print("\n🎯 ELITE AI CONSULTING SYSTEM SHUTDOWN\n" + "="*45)
            break
        
        if choice == '1' and not email_service:
            print("❌ Email delivery not configured. Use option 2 for PDFs.")
            continue
        
        if choice in {'1', '2'}:
            project = input("📝 Strategic challenge description: ").strip()
            if not project:
                print("❌ Project description cannot be empty.")
                continue
            if choice == '1':
                client_email = input("📧 Client email: ").strip()
                client_name = input("👤 Client name: ").strip() or "Valued Client"
                if not client_email:
                    print("❌ Client email cannot be empty.")
                    continue
                supervisor.orchestrate_project_with_email(project, client_email, client_name)
            else:
                supervisor.orchestrate_project_with_email(project)
        
        elif choice == '3':
            print("\n👥 ELITE SPECIALIST CONSULTATIONS:")
            for i, (name, agent) in enumerate([
                ("Dr. Research (70B)", supervisor.team['researcher']),
                ("Alex Manager", supervisor.team['manager']),
                ("Maya Writer", supervisor.team['writer']),
                ("Tech Oracle", supervisor.team['technical']),
                ("Director AI (70B)", supervisor)
            ], 1):
                print(f"{i}. {name}")
            
            agent_choice = input("\nChoose specialist (1-5): ").strip()
            task = input("Consultation topic: ").strip()
            if not task:
                print("❌ Consultation topic cannot be empty.")
                continue
            
            if agent_choice == '1':
                _, pdf = supervisor.team['researcher'].analyze_topic(task)
            elif agent_choice == '2':
                _, pdf = supervisor.team['manager'].plan_project(task)
            elif agent_choice == '3':
                _, pdf = supervisor.team['writer'].create_content("strategic brief", task)
            elif agent_choice == '4':
                _, pdf = supervisor.team['technical'].solve_technical_problem(task)
            elif agent_choice == '5':
                analysis = supervisor.think(f"Provide strategic consultation on: {task}")
                pdf = supervisor.generate_pdf_report(analysis, task)
            else:
                print("❌ Invalid specialist choice.")
                continue
            print(f"📄 Report: {pdf}")
        
        elif choice == '4':
            if os.name == 'nt':
                subprocess.run(['explorer', str(WORKING_DIR)], shell=True)
            print(f"📂 Workspace: {WORKING_DIR.absolute()}")
        
        elif choice == '5':
            test_query = input("Research question for 70B model: ").strip()
            if test_query:
                result = supervisor.team['researcher'].think(f"Provide analysis of: {test_query}")
                print(f"🎯 70B Response:\n{'-'*40}\n{result}\n{'-'*40}")

if __name__ == "__main__":
    interactive_demo()