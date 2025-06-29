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

# Local Ollama configuration
OLLAMA_URL = "http://localhost:11434/api/generate"
WORKING_DIR = Path("multi_agent_workspace")
WORKING_DIR.mkdir(exist_ok=True)

class PDFGenerator:
    """Utility class for generating professional PDFs"""
    
    @staticmethod
    def create_agent_pdf(agent_name, agent_role, content, filename, project_title=""):
        """Create a professional PDF for an agent's output"""
        
        # Create full filepath
        filepath = WORKING_DIR / filename
        
        # Create document
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
        # Split content by paragraphs and format
        paragraphs = content.split('\n\n')
        for para in paragraphs:
            if para.strip():
                # Check if it looks like a heading (starts with #, numbers, or is short and uppercase)
                if (para.strip().startswith('#') or 
                    para.strip().startswith(('1.', '2.', '3.', '4.', '5.')) or
                    (len(para.strip()) < 50 and para.strip().isupper())):
                    # Format as heading
                    heading_text = para.strip().replace('#', '').strip()
                    story.append(Paragraph(heading_text, styles['Heading3']))
                else:
                    # Format as regular content
                    story.append(Paragraph(para.strip(), content_style))
                story.append(Spacer(1, 12))
        
        # Footer
        story.append(Spacer(1, 30))
        story.append(Paragraph("— End of Report —", agent_style))
        
        # Build PDF
        doc.build(story)
        
        return filepath

class BaseAgent:
    """Base class for all AI agents with PDF generation"""
    
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
            
            # Store in memory
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
        
        print(f"📄 {self.name} generated PDF: {filepath}")
        return filepath

class ResearchAgent(BaseAgent):
    """Specialist in research and information gathering"""
    
    def __init__(self):
        super().__init__(
            name="Dr. Research",
            role="Senior Research Analyst",
            personality="""You are methodical, thorough, and love diving deep into topics. 
You always provide well-structured analysis with multiple perspectives. 
You format your reports professionally with clear sections."""
        )
    
    def analyze_topic(self, topic, generate_pdf=True, project_title=""):
        """Analyze a topic comprehensively and optionally generate PDF"""
        content = self.think(f"""Conduct a comprehensive analysis of: {topic}

Please provide a professional research report with these sections:

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
        
        if generate_pdf:
            self.generate_pdf_report(content, topic, project_title)
        
        return content

class ManagerAgent(BaseAgent):
    """Coordinates tasks and manages the team"""
    
    def __init__(self):
        super().__init__(
            name="Alex Manager",
            role="Project Coordinator",
            personality="""You are organized, decisive, and excellent at breaking down complex projects. 
You create detailed project plans with timelines and deliverables."""
        )
    
    def plan_project(self, project_description, generate_pdf=True, project_title=""):
        """Create a project plan and optionally generate PDF"""
        content = self.think(f"""Create a detailed project plan for: {project_description}

Format as a professional project management document:

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
        
        if generate_pdf:
            self.generate_pdf_report(content, project_description, project_title)
        
        return content

class WriterAgent(BaseAgent):
    """Specialist in content creation and communication"""
    
    def __init__(self):
        super().__init__(
            name="Maya Writer",
            role="Content Specialist",
            personality="""You are creative, articulate, and skilled at adapting your writing style. 
You create engaging, professional content tailored to specific audiences."""
        )
    
    def create_content(self, content_type, topic, audience="general", generate_pdf=True, project_title=""):
        """Create specific types of content and optionally generate PDF"""
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

Ensure the content is engaging, professional, and appropriate for the {audience} audience.""")
        
        if generate_pdf:
            self.generate_pdf_report(content, f"{content_type}: {topic}", project_title)
        
        return content

class TechnicalAgent(BaseAgent):
    """Handles technical tasks and code"""
    
    def __init__(self):
        super().__init__(
            name="Tech Oracle",
            role="Senior Technical Specialist", 
            personality="""You are logical, precise, and excellent at solving technical problems.
You provide detailed technical documentation with clear implementation steps."""
        )
    
    def solve_technical_problem(self, problem, generate_pdf=True, project_title=""):
        """Solve technical problems and optionally generate PDF"""
        content = self.think(f"""Analyze and solve this technical problem: {problem}

Provide a comprehensive technical report:

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

Include specific technical details, code examples where appropriate, and best practices.""")
        
        if generate_pdf:
            self.generate_pdf_report(content, f"Technical Analysis: {problem}", project_title)
        
        return content

class SupervisorAgent(BaseAgent):
    """Orchestrates the entire multi-agent system"""
    
    def __init__(self):
        super().__init__(
            name="Director AI",
            role="Team Supervisor",
            personality="""You are wise, strategic, and excellent at seeing the big picture.
You coordinate between different specialists and ensure quality outcomes."""
        )
        
        # Initialize the team
        self.team = {
            'researcher': ResearchAgent(),
            'manager': ManagerAgent(), 
            'writer': WriterAgent(),
            'technical': TechnicalAgent()
        }
    
    def orchestrate_project(self, project_request):
        """Orchestrate a complete project using the team with PDF outputs"""
        print(f"\n🎯 {self.name}: Starting project orchestration...")
        project_title = f"Multi-Agent Project: {project_request}"
        
        # Step 1: Supervisor analyzes the request
        analysis = self.think(f"""Analyze this project request and create a strategic overview: {project_request}

Provide:
# STRATEGIC ANALYSIS
Project assessment and approach

# TEAM COORDINATION PLAN
Which agents will be involved and how

# EXPECTED DELIVERABLES
What outputs we'll produce

# SUCCESS FACTORS
Key elements for project success""")
        
        # Generate supervisor PDF
        supervisor_pdf = self.generate_pdf_report(analysis, project_request, project_title)
        print(f"📋 Strategic Analysis PDF created: {supervisor_pdf.name}\n")
        
        # Step 2: Manager creates project plan
        print(f"👔 {self.team['manager'].name}: Creating project plan...")
        project_plan = self.team['manager'].plan_project(project_request, True, project_title)
        print("📊 Project Plan PDF generated\n")
        
        # Step 3: Researcher conducts analysis
        print(f"🔍 {self.team['researcher'].name}: Conducting research...")
        research = self.team['researcher'].analyze_topic(project_request, True, project_title)
        print("📚 Research Analysis PDF generated\n")
        
        # Step 4: Technical agent provides technical perspective
        print(f"⚙️ {self.team['technical'].name}: Technical analysis...")
        technical_analysis = self.team['technical'].solve_technical_problem(
            f"Technical requirements and implementation for: {project_request}", True, project_title
        )
        print("🔧 Technical Analysis PDF generated\n")
        
        # Step 5: Writer creates final deliverable
        print(f"✍️ {self.team['writer'].name}: Creating executive summary...")
        final_report = self.team['writer'].create_content(
            "executive summary report",
            f"Multi-agent analysis of: {project_request}",
            "executive", True, project_title
        )
        print("📄 Executive Summary PDF generated\n")
        
        # Step 6: Create consolidated project summary
        self.create_project_summary_pdf(project_request, {
            'analysis': analysis,
            'project_plan': project_plan,
            'research': research,
            'technical_analysis': technical_analysis,
            'final_report': final_report
        })
        
        print("🏆 Project completed! All PDFs generated in working directory.")
        print(f"📁 Check folder: {WORKING_DIR.absolute()}")
        
        return "Project completed successfully with PDF deliverables!"
    
    def create_project_summary_pdf(self, project_name, results):
        """Create a consolidated project summary PDF"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"PROJECT_SUMMARY_{timestamp}.pdf"
        
        summary_content = f"""# PROJECT SUMMARY
{project_name}

# TEAM DELIVERABLES OVERVIEW

## Strategic Analysis (Director AI)
High-level project assessment and coordination strategy.

## Project Management Plan (Alex Manager)  
Detailed project planning with timelines and resource allocation.

## Research Analysis (Dr. Research)
Comprehensive market and topic analysis with recommendations.

## Technical Implementation (Tech Oracle)
Technical architecture and implementation roadmap.

## Executive Summary (Maya Writer)
Professional summary for stakeholders and decision makers.

# PROJECT COMPLETION STATUS
✓ All agent deliverables completed
✓ Individual PDF reports generated
✓ Project coordination successful

# NEXT STEPS
Review individual agent PDFs for detailed insights and implementation guidance."""
        
        filepath = PDFGenerator.create_agent_pdf(
            "Multi-Agent Team",
            "Project Summary",
            summary_content,
            filename,
            f"Project Summary: {project_name}"
        )
        
        print(f"📋 Project Summary PDF created: {filepath}")

def interactive_demo():
    """Interactive demo of the multi-agent system with PDF generation"""
    print("🤖 MULTI-AGENT AI SYSTEM WITH PDF GENERATION!")
    print(f"📁 Working directory: {WORKING_DIR.absolute()}")
    print("\nMeet your AI team:")
    print("🔍 Dr. Research - Research Analyst (generates research PDFs)")
    print("👔 Alex Manager - Project Coordinator (generates project plan PDFs)")
    print("✍️ Maya Writer - Content Specialist (generates content PDFs)")
    print("⚙️ Tech Oracle - Technical Specialist (generates technical PDFs)")
    print("🎯 Director AI - Team Supervisor (generates summary PDFs)")
    print("\n🎯 NEW: Each agent creates professional PDF reports!")
    print("Type 'quit' to exit\n")
    
    supervisor = SupervisorAgent()
    
    while True:
        print("Choose an option:")
        print("1. Full project with PDF deliverables (RECOMMENDED)")
        print("2. Individual agent with PDF output")
        print("3. Open working directory")
        print("4. Quit")
        
        choice = input("\nYour choice (1-4): ").strip()
        
        if choice == '1':
            project = input("\n📝 Describe your project: ").strip()
            if project:
                print("\n🚀 Starting multi-agent collaboration with PDF generation...\n")
                supervisor.orchestrate_project(project)
                print(f"\n📂 All PDFs saved to: {WORKING_DIR.absolute()}")
        
        elif choice == '2':
            print("\nAvailable agents:")
            print("1. Dr. Research")
            print("2. Alex Manager")
            print("3. Maya Writer")
            print("4. Tech Oracle")
            
            agent_choice = input("Choose agent (1-4): ").strip()
            task = input("Describe the task: ").strip()
            
            if agent_choice == '1':
                supervisor.team['researcher'].analyze_topic(task)
            elif agent_choice == '2':
                supervisor.team['manager'].plan_project(task)
            elif agent_choice == '3':
                supervisor.team['writer'].create_content("report", task)
            elif agent_choice == '4':
                supervisor.team['technical'].solve_technical_problem(task)
        
        elif choice == '3':
            import subprocess
            if os.name == 'nt':  # Windows
                subprocess.run(['explorer', str(WORKING_DIR)])
            print(f"📂 Opened: {WORKING_DIR.absolute()}")
        
        elif choice == '4' or choice.lower() == 'quit':
            print("👋 Multi-agent system shutting down. Check your PDFs!")
            break
        
        else:
            print("❌ Invalid choice. Please try again.")

if __name__ == "__main__":
    interactive_demo()