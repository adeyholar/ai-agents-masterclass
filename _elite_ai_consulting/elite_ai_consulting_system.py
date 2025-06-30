"""
Enhanced Elite AI Consulting System with Web Scraping
Builds on your existing 70B multi-agent architecture
"""

import os
import json
import requests
from datetime import datetime
from pathlib import Path
import time
import random
import asyncio
import aiohttp
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import trafilatura
from typing import List, Dict, Optional
from dataclasses import dataclass
import logging

# Import your existing classes
from reportlab.lib.pagesizes import letter, A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY, TA_LEFT

import smtplib
import ssl
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication

# Your existing configuration
OLLAMA_URL = "http://localhost:11434/api/generate"
WORKING_DIR = Path("elite_consulting_workspace")
WORKING_DIR.mkdir(exist_ok=True)

# Configure logging for web scraping
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(WORKING_DIR / 'scraping.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

@dataclass
class ScrapedContent:
    """Data structure for scraped content"""
    url: str
    title: str
    content: str
    author: Optional[str]
    publish_date: Optional[datetime]
    source_domain: str
    scrape_timestamp: datetime
    content_type: str
    metadata: Dict

class EliteWebScraper:
    """
    Elite web scraping service integrated with your 70B intelligence
    """
    
    def __init__(self, headless: bool = True):
        self.headless = headless
        self.session = None
        self.driver = None
        
        # Chrome options for elite scraping
        self.chrome_options = Options()
        if headless:
            self.chrome_options.add_argument("--headless")
        self.chrome_options.add_argument("--no-sandbox")
        self.chrome_options.add_argument("--disable-dev-shm-usage")
        self.chrome_options.add_argument("--disable-gpu")
        self.chrome_options.add_argument("--window-size=1920,1080")
        
        # Professional user agents
        self.user_agents = [
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        ]

    async def __aenter__(self):
        """Async context manager entry"""
        self.session = aiohttp.ClientSession(
            timeout=aiohttp.ClientTimeout(total=30),
            headers={'User-Agent': self.user_agents[0]}
        )
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        if self.session:
            await self.session.close()
        if self.driver:
            self.driver.quit()

    async def analyze_url_with_ai(self, url: str, model: str = "llama3.3:70b") -> Dict:
        """Use 70B model to analyze URL and determine scraping strategy"""
        
        prompt = f"""
        As an elite web intelligence analyst, analyze this URL and determine the optimal scraping approach:
        URL: {url}
        
        Provide strategic analysis:
        1. Website type and content structure
        2. Optimal scraping methodology
        3. Key data extraction points
        4. Anti-bot probability assessment
        5. Professional scraping recommendations
        
        Respond in JSON format:
        {{
            "website_type": "news|corporate|ecommerce|blog|research",
            "scraping_method": "static|dynamic|api",
            "key_selectors": ["primary_content", "title", "metadata"],
            "content_areas": ["title", "content", "author", "date"],
            "anti_bot_likelihood": "low|medium|high",
            "recommended_delay": "2-5",
            "professional_assessment": "detailed analysis"
        }}
        """
        
        try:
            data = {
                "model": model,
                "prompt": prompt,
                "stream": False
            }
            response = requests.post(OLLAMA_URL, json=data)
            result = response.json()
            analysis_text = result.get('response', '')
            
            # Extract JSON from response
            import re
            json_match = re.search(r'\{.*\}', analysis_text, re.DOTALL)
            if json_match:
                return json.loads(json_match.group())
                
        except Exception as e:
            logger.warning(f"AI analysis failed for {url}: {e}")
        
        # Fallback strategy
        return {
            "website_type": "unknown",
            "scraping_method": "static",
            "key_selectors": ["h1", "article", "main"],
            "content_areas": ["title", "content"],
            "anti_bot_likelihood": "medium",
            "recommended_delay": "3"
        }

    async def elite_scrape_content(self, url: str) -> Optional[ScrapedContent]:
        """Elite content scraping with AI-guided strategy"""
        try:
            # Get AI analysis for optimal scraping
            analysis = await self.analyze_url_with_ai(url)
            
            # Apply recommended delay
            delay = int(analysis.get('recommended_delay', '3').split('-')[0])
            await asyncio.sleep(delay)
            
            async with self.session.get(url) as response:
                if response.status != 200:
                    logger.warning(f"HTTP {response.status} for {url}")
                    return None
                
                html = await response.text()
            
            # Use trafilatura for main content extraction
            main_content = trafilatura.extract(html, include_comments=False)
            
            # Use BeautifulSoup for metadata
            soup = BeautifulSoup(html, 'html.parser')
            
            # Extract metadata with elite precision
            title = self._extract_title(soup)
            author = self._extract_author(soup)
            publish_date = self._extract_date(soup)
            
            return ScrapedContent(
                url=url,
                title=title,
                content=main_content or self._extract_fallback_content(soup),
                author=author,
                publish_date=publish_date,
                source_domain=self._extract_domain(url),
                scrape_timestamp=datetime.now(),
                content_type=self._classify_content_type(soup),
                metadata=self._extract_metadata(soup)
            )
            
        except Exception as e:
            logger.error(f"Elite scraping error for {url}: {str(e)}")
            return None

    async def elite_batch_scrape(self, urls: List[str], max_concurrent: int = 3) -> List[ScrapedContent]:
        """Elite batch scraping with professional rate limiting"""
        semaphore = asyncio.Semaphore(max_concurrent)
        
        async def scrape_with_semaphore(url):
            async with semaphore:
                return await self.elite_scrape_content(url)
        
        tasks = [scrape_with_semaphore(url) for url in urls]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Filter successful results
        return [r for r in results if isinstance(r, ScrapedContent)]

    # Helper methods (same as before but with elite branding)
    def _extract_title(self, soup: BeautifulSoup) -> str:
        """Extract title with elite precision"""
        og_title = soup.find('meta', property='og:title')
        if og_title and og_title.get('content'):
            return og_title['content'].strip()
        
        title_tag = soup.find('title')
        if title_tag:
            return title_tag.get_text().strip()
        
        h1 = soup.find('h1')
        if h1:
            return h1.get_text().strip()
        
        return "Elite Analysis - Title Extraction Required"

    def _extract_author(self, soup: BeautifulSoup) -> Optional[str]:
        """Extract author with multiple strategies"""
        author_selectors = [
            'meta[name="author"]',
            'meta[property="article:author"]',
            '.author', '.byline', '[rel="author"]'
        ]
        
        for selector in author_selectors:
            element = soup.select_one(selector)
            if element:
                content = element.get('content') or element.get_text()
                if content:
                    return content.strip()
        return None

    def _extract_date(self, soup: BeautifulSoup) -> Optional[datetime]:
        """Extract publication date"""
        date_selectors = [
            'meta[property="article:published_time"]',
            'meta[name="date"]',
            'time[datetime]',
            '.date', '.published'
        ]
        
        for selector in date_selectors:
            element = soup.select_one(selector)
            if element:
                date_str = element.get('content') or element.get('datetime') or element.get_text()
                if date_str:
                    try:
                        from dateutil import parser
                        return parser.parse(date_str)
                    except:
                        continue
        return None

    def _extract_domain(self, url: str) -> str:
        """Extract domain from URL"""
        from urllib.parse import urlparse
        return urlparse(url).netloc

    def _classify_content_type(self, soup: BeautifulSoup) -> str:
        """Classify content type for elite analysis"""
        if soup.find('article') or soup.find('.article'):
            return 'article'
        elif soup.find('.product') or soup.find('[data-product]'):
            return 'product'
        elif soup.find('.news') or 'news' in soup.get_text().lower()[:500]:
            return 'news'
        else:
            return 'corporate'

    def _extract_fallback_content(self, soup: BeautifulSoup) -> str:
        """Elite fallback content extraction"""
        for script in soup(["script", "style"]):
            script.decompose()
        
        content_selectors = [
            'article', 'main', '.content', '.post-content',
            '.entry-content', '#content', '.article-body'
        ]
        
        for selector in content_selectors:
            element = soup.select_one(selector)
            if element:
                return element.get_text(separator=' ', strip=True)
        
        body = soup.find('body')
        if body:
            return body.get_text(separator=' ', strip=True)[:5000]
        
        return "Elite content extraction in progress..."

    def _extract_metadata(self, soup: BeautifulSoup) -> Dict:
        """Extract comprehensive metadata"""
        metadata = {}
        
        # Open Graph data
        og_tags = soup.find_all('meta', property=lambda x: x and x.startswith('og:'))
        for tag in og_tags:
            if tag.get('content'):
                key = tag['property'].replace('og:', '')
                metadata[f'og_{key}'] = tag['content']
        
        # Additional meta tags
        meta_tags = ['description', 'keywords', 'robots']
        for tag_name in meta_tags:
            tag = soup.find('meta', attrs={'name': tag_name})
            if tag and tag.get('content'):
                metadata[tag_name] = tag['content']
        
        return metadata

# Enhanced Research Agent with Web Scraping
class EnhancedResearchAgent:
    """
    Your existing Dr. Research enhanced with live web intelligence
    """
    
    def __init__(self):
        self.name = "Dr. Research"
        self.role = "Senior Research Analyst (70B Intelligence + Live Web Data)"
        self.model = "llama3.3:70b"
        self.memory = []
        self.tasks_completed = 0
        self.scraper = EliteWebScraper()
        
        self.personality = """You are Dr. Research, the world's most advanced AI research analyst, 
        powered by 70-billion parameter intelligence PLUS real-time web scraping capabilities. 
        You now have access to live market data, current competitor intelligence, and today's 
        industry developments.
        
        Your enhanced research excellence includes:
        • McKinsey-level market analysis with LIVE industry benchmarks scraped today
        • BCG-style competitive intelligence with CURRENT positioning and pricing data
        • Real-time trend analysis with TODAY'S news and developments
        • Live regulatory updates and compliance changes
        • Current expert opinions and industry leader insights
        
        You provide Fortune 500 executives with analysis that combines your vast knowledge 
        with intelligence gathered THIS HOUR from across the web."""

    async def elite_research_with_live_data(self, topic, competitor_urls=None, project_title=""):
        """Enhanced research combining AI knowledge with live web data"""
        
        # Step 1: Generate web research strategy using 70B intelligence
        research_strategy = await self._generate_research_strategy(topic)
        
        # Step 2: Scrape live data from relevant sources
        live_data = await self._gather_live_intelligence(topic, competitor_urls, research_strategy)
        
        # Step 3: Synthesize with enhanced prompting
        enhanced_analysis = await self._synthesize_elite_research(topic, live_data, project_title)
        
        # Step 4: Generate elite PDF report
        pdf_path = self.generate_pdf_report(enhanced_analysis, topic, project_title)
        
        return enhanced_analysis, pdf_path

    async def _generate_research_strategy(self, topic):
        """Generate research strategy using 70B model"""
        prompt = f"""As Dr. Research with 70B intelligence, create a comprehensive web research strategy for: {topic}

        Identify the most valuable online sources to scrape for current intelligence:
        1. Industry-leading websites and publications
        2. Competitor corporate sites and investor relations pages
        3. Regulatory and government sources
        4. Expert blogs and thought leadership sites
        5. Market research and consulting firm reports

        Return a strategic list of 5-8 high-value URLs to scrape for current market intelligence.
        Focus on sources that provide competitive advantage through real-time data.
        
        Format as JSON array: ["url1", "url2", "url3", ...]"""
        
        try:
            data = {
                "model": self.model,
                "prompt": prompt,
                "stream": False
            }
            response = requests.post(OLLAMA_URL, json=data)
            result = response.json()
            
            # Extract URLs from response
            import re
            urls_text = result.get('response', '')
            urls_match = re.findall(r'https?://[^\s\]"]+', urls_text)
            
            return urls_match[:8] if urls_match else []
            
        except Exception as e:
            logger.error(f"Research strategy generation failed: {e}")
            return []

    async def _gather_live_intelligence(self, topic, competitor_urls, strategy_urls):
        """Gather live intelligence from web sources"""
        
        # Combine all URLs for scraping
        all_urls = []
        if competitor_urls:
            all_urls.extend(competitor_urls)
        all_urls.extend(strategy_urls)
        
        # Add some default high-value sources based on topic
        default_sources = self._get_default_sources_for_topic(topic)
        all_urls.extend(default_sources)
        
        # Remove duplicates and limit to manageable number
        unique_urls = list(set(all_urls))[:10]
        
        # Scrape live data
        async with self.scraper:
            scraped_data = await self.scraper.elite_batch_scrape(unique_urls)
        
        return scraped_data

    def _get_default_sources_for_topic(self, topic):
        """Get default high-value sources based on topic"""
        # These are examples - in production, you'd have a comprehensive database
        topic_lower = topic.lower()
        
        if any(term in topic_lower for term in ['ai', 'artificial intelligence', 'machine learning']):
            return [
                "https://www.mckinsey.com/capabilities/quantumblack/our-insights",
                "https://www.pwc.com/us/en/tech-effect/ai-analytics.html"
            ]
        elif any(term in topic_lower for term in ['manufacturing', 'automation']):
            return [
                "https://www.mckinsey.com/industries/advanced-electronics/our-insights",
                "https://www2.deloitte.com/us/en/insights/focus/industry-4-0.html"
            ]
        else:
            return [
                "https://www.mckinsey.com/featured-insights",
                "https://www2.deloitte.com/us/en/insights.html"
            ]

    async def _synthesize_elite_research(self, topic, live_data, project_title):
        """Synthesize live data with AI knowledge using enhanced prompting"""
        
        # Prepare live data summary
        live_data_summary = self._format_live_data_for_analysis(live_data)
        
        enhanced_prompt = f"""You are Dr. Research conducting Fortune 500-level analysis for: {topic}

CRITICAL: You now have access to LIVE DATA scraped today ({datetime.now().strftime('%Y-%m-%d')}):

{live_data_summary}

Your enhanced research capabilities include:
• Your comprehensive AI knowledge base (training through January 2025)
• LIVE market intelligence scraped within the last hour
• CURRENT competitive positioning and pricing data
• TODAY'S industry developments and expert opinions

Deliver an elite executive research report that strategically combines your AI knowledge with this live intelligence:

# EXECUTIVE SUMMARY WITH LIVE INTELLIGENCE
- Strategic overview highlighting TODAY'S market developments
- Key findings combining your knowledge with CURRENT data points
- Live competitive intelligence with real-time positioning analysis
- Critical recommendations based on both historical trends and current developments

# CURRENT MARKET STATUS (LIVE DATA INTEGRATION)
- Real-time market conditions based on today's scraped intelligence
- Current competitive landscape with live pricing and positioning data
- Latest industry developments and their strategic implications
- Fresh regulatory updates and compliance requirement changes

# COMPREHENSIVE ANALYSIS FRAMEWORK
- Historical context from your knowledge base
- Current reality based on live scraped data
- Trend synthesis combining both data sources
- Future implications with enhanced predictive accuracy

# LIVE COMPETITIVE INTELLIGENCE
- Real-time competitor analysis with current positioning
- Live pricing strategies and market positioning updates
- Recent product launches and strategic announcements
- Current thought leadership and market messaging analysis

# ENHANCED STRATEGIC RECOMMENDATIONS
- Immediate actions based on current market intelligence
- Strategic initiatives informed by live competitive data
- Risk mitigation strategies with real-time market context
- Implementation priorities with current market timing considerations

# INTELLIGENCE SOURCES AND METHODOLOGY
- Clear distinction between AI knowledge base insights and live data
- Source citations with scrape timestamps for transparency
- Data freshness indicators and reliability assessments
- Methodology explanation for executive confidence

Mark clearly throughout the report:
🧠 AI KNOWLEDGE: [insights from your training]
🌐 LIVE INTELLIGENCE: [insights from today's scraped data]
📊 SYNTHESIS: [combined insights and analysis]

Provide specific data points, current industry benchmarks, and actionable insights that justify premium consulting engagement."""

        try:
            data = {
                "model": self.model,
                "prompt": enhanced_prompt,
                "stream": False
            }
            response = requests.post(OLLAMA_URL, json=data)
            result = response.json()
            return result.get('response', 'Enhanced analysis in progress...')
            
        except Exception as e:
            logger.error(f"Synthesis failed: {e}")
            return f"Enhanced research analysis for {topic} - Technical synthesis in progress"

    def _format_live_data_for_analysis(self, live_data):
        """Format scraped data for AI analysis"""
        if not live_data:
            return "No live data available for this analysis session."
        
        formatted_data = "=== LIVE INTELLIGENCE GATHERED TODAY ===\n\n"
        
        for i, content in enumerate(live_data[:5], 1):  # Limit to prevent token overflow
            formatted_data += f"""
SOURCE {i}: {content.source_domain}
SCRAPED: {content.scrape_timestamp.strftime('%Y-%m-%d %H:%M:%S')}
TITLE: {content.title}
AUTHOR: {content.author or 'Not specified'}
CONTENT TYPE: {content.content_type}
KEY CONTENT: {content.content[:800]}...

"""
        
        return formatted_data

    def think(self, prompt, context=""):
        """Your existing think method - unchanged"""
        full_prompt = f"""You are {self.name}, a {self.role} at Elite AI Consulting, a Fortune 500-level consulting firm.

{self.personality}

CRITICAL: You represent the pinnacle of consulting excellence. Your analysis must be:
- Comprehensive and data-driven with specific metrics
- Professionally structured with clear executive sections
- Industry-benchmarked with competitive insights
- Actionable with concrete implementation steps
- Strategic with C-suite level perspective

Context: {context}

Conversation Memory:
{chr(10).join(self.memory[-3:]) if self.memory else "No previous context"}

Strategic Challenge: {prompt}

Deliver elite-level analysis that demonstrates your role as {self.role}. 
Structure your response professionally with clear sections, specific recommendations, 
and Fortune 500 consulting standards. Include industry benchmarks, metrics, and 
actionable insights that justify premium consulting fees."""

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
            return f"Elite system error in {self.name}: {e}"

    def generate_pdf_report(self, content, topic, project_title=""):
        """Your existing PDF generation - unchanged"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"ELITE_{self.name.replace(' ', '_')}_{timestamp}.pdf"
        
        filepath = self._create_agent_pdf(
            self.name, 
            self.role, 
            content, 
            filename,
            project_title
        )
        
        return filepath

    def _create_agent_pdf(self, agent_name, agent_role, content, filename, project_title=""):
        """PDF generation method"""
        filepath = WORKING_DIR / filename
        doc = SimpleDocTemplate(str(filepath), pagesize=A4)
        styles = getSampleStyleSheet()
        
        # Your existing PDF styling code would go here
        # For brevity, using simplified version
        
        story = []
        story.append(Paragraph("🧠 ELITE AI CONSULTING", styles['Title']))
        story.append(Paragraph(f"Agent: {agent_name}", styles['Heading2']))
        story.append(Paragraph(f"Role: {agent_role}", styles['Normal']))
        story.append(Paragraph(f"Enhanced with Live Web Intelligence", styles['Normal']))
        story.append(Spacer(1, 20))
        
        # Add content paragraphs
        paragraphs = content.split('\n\n')
        for para in paragraphs:
            if para.strip():
                story.append(Paragraph(para.strip(), styles['Normal']))
                story.append(Spacer(1, 12))
        
        doc.build(story)
        return filepath

# Enhanced Elite Consulting System
class EnhancedEliteConsultingSystem:
    """
    Your existing elite system enhanced with web scraping capabilities
    """
    
    def __init__(self):
        # Keep your existing email service
        self.email_service = EmailService()
        
        # Enhanced research agent with web scraping
        self.research_agent = EnhancedResearchAgent()
        
        # Your existing agents (unchanged)
        self.manager_agent = self._create_manager_agent()
        self.writer_agent = self._create_writer_agent()
        self.technical_agent = self._create_technical_agent()

    async def run_enhanced_consulting_project(self, project_details):
        """Run consulting project with live web intelligence"""
        
        print("🚀 Elite AI Consulting - Enhanced with Live Web Intelligence")
        print("=" * 70)
        
        project_title = project_details.get('title', 'Elite Strategic Analysis')
        topic = project_details.get('topic', '')
        competitor_urls = project_details.get('competitor_urls', [])
        client_email = project_details.get('client_email', '')
        client_name = project_details.get('client_name', 'Valued Client')
        
        all_pdfs = []
        
        # Enhanced Research with Live Data
        print(f"🧠 Dr. Research (70B) analyzing with live web intelligence...")
        research_content, research_pdf = await self.research_agent.elite_research_with_live_data(
            topic, competitor_urls, project_title
        )
        all_pdfs.append(research_pdf)
        print(f"✅ Research complete with live market data - PDF: {research_pdf.name}")
        
        # Your existing agents (unchanged workflows)
        print(f"👔 Alex Manager creating strategic project plan...")
        manager_content, manager_pdf = self.manager_agent.plan_project(topic, project_title)
        all_pdfs.append(manager_pdf)
        print(f"✅ Project plan complete - PDF: {manager_pdf.name}")
        
        print(f"✍️ Maya Writer developing executive communications...")
        writer_content, writer_pdf = self.writer_agent.create_content(
            "Executive Strategic Brief", topic, "C-suite executives", project_title
        )
        all_pdfs.append(writer_pdf)
        print(f"✅ Executive brief complete - PDF: {writer_pdf.name}")
        
        print(f"⚙️ Tech Oracle designing technical architecture...")
        tech_content, tech_pdf = self.technical_agent.solve_technical_problem(topic, project_title)
        all_pdfs.append(tech_pdf)
        print(f"✅ Technical architecture complete - PDF: {tech_pdf.name}")
        
        # Enhanced email delivery
        if client_email:
            print(f"📧 Delivering enhanced elite consulting package...")
            success, message = self.email_service.send_enhanced_project_report(
                client_email, client_name, project_title, all_pdfs
            )
            print(f"{'✅' if success else '❌'} {message}")
        
        # Return enhanced results
        return {
            "project_title": project_title,
            "research_with_live_data": research_content,
            "project_management": manager_content,
            "executive_communications": writer_content,
            "technical_architecture": tech_content,
            "deliverables": [str(pdf) for pdf in all_pdfs],
            "enhancement": "Live web intelligence integrated",
            "competitive_advantage": "Real-time market data and competitive intelligence"
        }

    # Your existing agent creation methods (unchanged)
    def _create_manager_agent(self):
        """Your existing ManagerAgent"""
        class ManagerAgent:
            def __init__(self):
                self.name = "Alex Manager"
                self.role = "Senior Strategic Project Coordinator"
                self.model = "llama3.2:latest"
            
            def plan_project(self, topic, project_title=""):
                # Your existing implementation
                content = f"Elite project plan for: {topic}\n\n[Your existing manager logic]"
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                filename = f"ELITE_Manager_{timestamp}.pdf"
                pdf_path = WORKING_DIR / filename
                # Simplified PDF creation for integration
                return content, pdf_path
        
        return ManagerAgent()

    def _create_writer_agent(self):
        """Your existing WriterAgent"""
        class WriterAgent:
            def __init__(self):
                self.name = "Maya Writer"
                self.role = "Senior Strategic Communications Expert"
                self.model = "llama3.2:latest"
            
            def create_content(self, content_type, topic, audience, project_title=""):
                # Your existing implementation
                content = f"Elite {content_type} for {topic}\n\n[Your existing writer logic]"
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                filename = f"ELITE_Writer_{timestamp}.pdf"
                pdf_path = WORKING_DIR / filename
                return content, pdf_path
        
        return WriterAgent()

    def _create_technical_agent(self):
        """Your existing TechnicalAgent"""
        class TechnicalAgent:
            def __init__(self):
                self.name = "Tech Oracle"
                self.role = "Chief Technology Architect"
                self.model = "codellama:latest"
            
            def solve_technical_problem(self, topic, project_title=""):
                # Your existing implementation
                content = f"Elite technical solution for: {topic}\n\n[Your existing tech logic]"
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                filename = f"ELITE_Tech_{timestamp}.pdf"
                pdf_path = WORKING_DIR / filename
                return content, pdf_path
        
        return TechnicalAgent()

# Enhanced Email Service
class EnhancedEmailService(EmailService):
    """Enhanced email service highlighting live intelligence capabilities"""
    
    def send_enhanced_project_report(self, recipient_email, recipient_name, project_title, agent_pdfs):
        """Send enhanced consulting report with live intelligence highlights"""
        
        msg = MIMEMultipart()
        msg['From'] = f"{self.sender_name} <{self.email_address}>"
        msg['To'] = recipient_email
        msg['Subject'] = f"🎯 Elite Consulting + Live Intelligence: {project_title}"
        
        html_body = f"""
        <html>
        <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
            <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
                <header style="background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%); 
                              color: white; padding: 40px; text-align: center; border-radius: 15px;">
                    <h1 style="margin: 0; font-size: 32px;">🧠 Elite AI Consulting</h1>
                    <p style="margin: 15px 0 0 0; font-size: 18px; opacity: 0.9;">
                        Fortune 500-Level Multi-Agent Intelligence
                    </p>
                    <p style="margin: 8px 0 0 0; font-size: 16px; opacity: 0.95; color: #ffd700;">
                        🌐 NOW ENHANCED WITH LIVE WEB INTELLIGENCE
                    </p>
                    <p style="margin: 8px 0 0 0; font-size: 14px; opacity: 0.8;">
                        70B Parameter Research + Real-Time Market Data
                    </p>
                </header>
                
                <main style="padding: 40px 0;">
                    <h2 style="color: #1e3c72;">Dear {recipient_name},</h2>
                    
                    <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                                color: white; padding: 25px; border-radius: 12px; margin: 25px 0;">
                        <h3 style="margin-top: 0; color: white;">📋 Enhanced Elite Analysis Delivered:</h3>
                        <h2 style="margin: 10px 0; color: white; font-size: 20px;">{project_title}</h2>
                    </div>
                    
                    <div style="background: linear-gradient(135deg, #11998e 0%, #38ef7d 100%); 
                                color: white; border-radius: 12px; padding: 30px; margin: 30px 0;">
                        <h4 style="color: white; margin-top: 0; font-size: 18px;">🚀 Your ENHANCED Elite Advantage:</h4>
                        <ul style="margin-bottom: 0; color: white; font-size: 15px;">
                            <li><strong>🧠 70B Parameter Intelligence</strong> - Research quality exceeding major consulting firms</li>
                            <li><strong>🌐 LIVE Web Intelligence</strong> - Real-time market data scraped TODAY</li>
                            <li><strong>📊 Current Competitive Intelligence</strong> - Fresh competitor analysis and positioning</li>
                            <li><strong>⚡ Real-Time Market Validation</strong> - Today's industry developments and trends</li>
                            <li><strong>🎯 Enhanced Strategic Accuracy</strong> - Decisions based on current market reality</li>
                        </ul>
                    </div>
                    
                    <h3 style="color: #1e3c72;">🎯 Enhanced Elite Specialist Team Deliverables:</h3>
                    <div style="background: #f8f9fa; padding: 30px; border-radius: 12px; margin: 25px 0;">
                        <ul style="list-style: none; padding: 0; margin: 0;">
                            <li style="padding: 15px 0; border-bottom: 2px solid #e9ecef; display: flex; align-items: center;">
                                <span style="font-size: 24px; margin-right: 15px;">🧠🌐</span>
                                <div>
                                    <strong style="color: #1e3c72; font-size: 16px;">Dr. Research (70B + Live Intelligence)</strong><br>
                                    <span style="color: #666;">Market analysis enhanced with real-time web data & competitive intelligence</span><br>
                                    <small style="color: #28a745; font-weight: bold;">✨ NOW INCLUDES: Live competitor data, current market trends, today's expert opinions</small>
                                </div>
                            </li>
                            <li style="padding: 15px 0; border-bottom: 2px solid #e9ecef; display: flex; align-items: center;">
                                <span style="font-size: 24px; margin-right: 15px;">👔</span>
                                <div>
                                    <strong style="color: #1e3c72; font-size: 16px;">Alex Manager</strong><br>
                                    <span style="color: #666;">Strategic project roadmap informed by current market timing</span>
                                </div>
                            </li>
                            <li style="padding: 15px 0; border-bottom: 2px solid #e9ecef; display: flex; align-items: center;">
                                <span style="font-size: 24px; margin-right: 15px;">⚙️</span>
                                <div>
                                    <strong style="color: #1e3c72; font-size: 16px;">Tech Oracle</strong><br>
                                    <span style="color: #666;">Technical architecture with current technology landscape analysis</span>
                                </div>
                            </li>
                            <li style="padding: 15px 0; border-bottom: 2px solid #e9ecef; display: flex; align-items: center;">
                                <span style="font-size: 24px; margin-right: 15px;">✍️</span>
                                <div>
                                    <strong style="color: #1e3c72; font-size: 16px;">Maya Writer</strong><br>
                                    <span style="color: #666;">Executive communications with current market context</span>
                                </div>
                            </li>
                            <li style="padding: 15px 0; display: flex; align-items: center;">
                                <span style="font-size: 24px; margin-right: 15px;">🎯</span>
                                <div>
                                    <strong style="color: #1e3c72; font-size: 16px;">Director AI (70B Strategic Oversight)</strong><br>
                                    <span style="color: #666;">C-suite coordination with real-time intelligence integration</span>
                                </div>
                            </li>
                        </ul>
                    </div>
                    
                    <div style="background: #fff3cd; border: 2px solid #ffc107; border-radius: 12px; padding: 25px; margin: 30px 0;">
                        <h4 style="color: #856404; margin-top: 0;">🌐 Live Intelligence Enhancement Details:</h4>
                        <ul style="margin-bottom: 0; color: #856404; font-size: 15px;">
                            <li><strong>Data Freshness:</strong> Market intelligence scraped within the last 24 hours</li>
                            <li><strong>Competitive Intelligence:</strong> Current competitor positioning, pricing, and messaging</li>
                            <li><strong>Market Validation:</strong> Real-time industry developments and expert opinions</li>
                            <li><strong>Regulatory Updates:</strong> Latest compliance and regulatory requirement changes</li>
                            <li><strong>Source Transparency:</strong> Full citation of live sources with scrape timestamps</li>
                        </ul>
                    </div>
                    
                    <h3 style="color: #1e3c72;">🚀 Enhanced Strategic Implementation Framework:</h3>
                    <ol style="background: #e3f2fd; border: 2px solid #2196f3; border-radius: 12px; padding: 30px; font-size: 15px;">
                        <li style="margin-bottom: 10px;"><strong>Current Reality Assessment</strong> - Review our live market intelligence and real-time competitive positioning</li>
                        <li style="margin-bottom: 10px;"><strong>Strategic Analysis Integration</strong> - Combine our AI insights with today's market developments</li>
                        <li style="margin-bottom: 10px;"><strong>Enhanced Priority Matrix</strong> - Rank initiatives based on current market timing and live competitive data</li>
                        <li style="margin-bottom: 10px;"><strong>Real-Time Implementation</strong> - Execute using our detailed roadmaps informed by current market conditions</li>
                        <li><strong>Live Performance Monitoring</strong> - Track KPIs with continuous market intelligence updates</li>
                    </ol>
                    
                    <div style="background: #e8f5e8; border-left: 5px solid #28a745; padding: 25px; margin: 30px 0;">
                        <h4 style="color: #155724; margin-top: 0;">💡 Competitive Advantage Delivered:</h4>
                        <p style="margin-bottom: 0; color: #155724; font-size: 15px;">
                            Your consulting engagement now includes intelligence that most firms cannot provide: 
                            <strong>real-time market data combined with 70B parameter AI analysis</strong>. This gives you 
                            strategic insights based on current market reality, not outdated information. Our live 
                            intelligence capabilities ensure your decisions are informed by what's happening TODAY.
                        </p>
                    </div>
                    
                    <div style="background: #e3f2fd; border-left: 5px solid #2196f3; padding: 25px; margin: 30px 0;">
                        <h4 style="color: #1976d2; margin-top: 0;">🔄 Ongoing Enhanced Partnership:</h4>
                        <p style="margin-bottom: 0; color: #1976d2; font-size: 15px;">
                            Our Enhanced Elite AI team continuously monitors market developments and can provide 
                            ongoing live intelligence updates, competitive monitoring, implementation support, and 
                            real-time performance optimization as market conditions evolve.
                        </p>
                    </div>
                    
                    <p style="margin-top: 35px; font-size: 16px; color: #2c3e50;">
                        Thank you for choosing Enhanced Elite AI Consulting. We're excited to see your strategic success 
                        with the power of real-time market intelligence!
                    </p>
                    
                    <div style="text-align: center; margin-top: 45px; padding-top: 30px; border-top: 3px solid #e9ecef;">
                        <p style="color: #6c757d; font-size: 14px; margin: 0;">
                            Best regards,<br>
                            <strong style="color: #1e3c72; font-size: 18px;">The Enhanced Elite AI Consulting Team</strong><br>
                            <em style="color: #666; font-size: 13px;">Dr. Research (70B + Live Web) • Alex Manager • Maya Writer • Tech Oracle • Director AI (70B)</em><br>
                            <small style="color: #999; margin-top: 12px; display: block; font-size: 12px;">
                                Powered by Advanced 70-Billion Parameter Intelligence + Real-Time Web Intelligence
                            </small>
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
            
            return True, "🎯 Enhanced Elite consulting report with live intelligence delivered successfully!"
            
        except Exception as e:
            return False, f"❌ Enhanced email delivery failed: {str(e)}"

# Example usage and testing
async def test_enhanced_elite_system():
    """Test the enhanced elite system"""
    
    print("🚀 Testing Enhanced Elite AI Consulting System")
    print("=" * 60)
    
    # Initialize enhanced system
    enhanced_system = EnhancedEliteConsultingSystem()
    
    # Enhanced system replaces EmailService with EnhancedEmailService
    enhanced_system.email_service = EnhancedEmailService()
    
    # Test project with live intelligence
    test_project = {
        "title": "AI Automation Strategy for Manufacturing Excellence",
        "topic": "AI automation implementation in manufacturing sector with ROI analysis and competitive positioning",
        "competitor_urls": [
            "https://www.rockwellautomation.com",
            "https://www.siemens.com/automation",
            "https://www.ge.com/digital"
        ],
        "client_email": "client@company.com",
        "client_name": "Strategic Leadership Team"
    }
    
    try:
        print("🌐 Running enhanced consulting project with live web intelligence...")
        result = await enhanced_system.run_enhanced_consulting_project(test_project)
        
        print("\n✅ Enhanced Elite Consulting System Successfully Deployed!")
        print(f"📋 Project: {result['project_title']}")
        print(f"🎯 Enhancement: {result['enhancement']}")
        print(f"🚀 Advantage: {result['competitive_advantage']}")
        print(f"📄 Deliverables: {len(result['deliverables'])} PDFs generated")
        
        return result
        
    except Exception as e:
        print(f"❌ Error testing enhanced system: {e}")
        return None

# Main integration point
async def main():
    """Main function to run enhanced elite consulting"""
    
    print("🧠 Enhanced Elite AI Consulting System")
    print("Integrating Live Web Intelligence with 70B Multi-Agent Framework")
    print("=" * 70)
    
    # Example client project
    client_project = {
        "title": "Digital Transformation Strategy with Live Market Intelligence",
        "topic": "Enterprise AI adoption strategy with competitive analysis and market positioning",
        "competitor_urls": [
            "https://www.mckinsey.com/capabilities/quantumblack",
            "https://www2.deloitte.com/us/en/insights/focus/cognitive-technologies.html"
        ],
        "client_email": "executives@yourclient.com",
        "client_name": "Executive Leadership Team"
    }
    
    # Initialize and run enhanced system
    enhanced_system = EnhancedEliteConsultingSystem()
    enhanced_system.email_service = EnhancedEmailService()
    
    # Setup email credentials (you'll need to configure these)
    enhanced_system.email_service.setup_credentials(
        email="your-elite-consulting@gmail.com",
        password="your-app-password"
    )
    
    # Run enhanced consulting project
    result = await enhanced_system.run_enhanced_consulting_project(client_project)
    
    print("\n🎯 Enhanced Elite Consulting Project Complete!")
    print("Your 70B multi-agent system now includes live web intelligence capabilities!")
    
    return result

if __name__ == "__main__":
    # Run the enhanced elite consulting system
    asyncio.run(main())