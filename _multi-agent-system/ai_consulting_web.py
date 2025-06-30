from flask import Flask, render_template, request, jsonify, send_file, redirect, url_for
import os
import json
import requests
from datetime import datetime
from pathlib import Path
import threading
import time

# Import your existing system
from elite_ai_consulting_system import SupervisorAgent, EmailService

app = Flask(__name__)
app.secret_key = 'elite-ai-consulting-2025'

# Global variables
WORKING_DIR = Path("web_projects")
WORKING_DIR.mkdir(exist_ok=True)

supervisor = SupervisorAgent()
projects_db = {}  # Simple in-memory database

@app.route('/')
def home():
    """Professional landing page"""
    return '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Elite AI Consulting - Fortune 500 Intelligence</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        
        body {
            font-family: 'Arial', sans-serif;
            line-height: 1.6;
            color: #333;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
        }
        
        .container {
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
        }
        
        .hero {
            text-align: center;
            padding: 80px 0;
            color: white;
        }
        
        .hero h1 {
            font-size: 3.5rem;
            margin-bottom: 20px;
            text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
        }
        
        .hero p {
            font-size: 1.3rem;
            margin-bottom: 40px;
            opacity: 0.9;
        }
        
        .cta-button {
            display: inline-block;
            background: linear-gradient(45deg, #ff6b6b, #ee5a24);
            color: white;
            padding: 18px 40px;
            text-decoration: none;
            border-radius: 50px;
            font-size: 1.2rem;
            font-weight: bold;
            transition: transform 0.3s ease;
            box-shadow: 0 8px 25px rgba(0,0,0,0.2);
        }
        
        .cta-button:hover {
            transform: translateY(-3px);
            box-shadow: 0 12px 35px rgba(0,0,0,0.3);
        }
        
        .features {
            background: white;
            margin: 60px 0;
            padding: 60px 40px;
            border-radius: 20px;
            box-shadow: 0 20px 60px rgba(0,0,0,0.1);
        }
        
        .features-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 40px;
            margin-top: 40px;
        }
        
        .feature {
            text-align: center;
            padding: 30px;
            border-radius: 15px;
            background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
        }
        
        .feature-icon {
            font-size: 3rem;
            margin-bottom: 20px;
        }
        
        .feature h3 {
            color: #2c3e50;
            margin-bottom: 15px;
        }
        
        .team-section {
            background: rgba(255,255,255,0.95);
            margin: 40px 0;
            padding: 50px 40px;
            border-radius: 20px;
            backdrop-filter: blur(10px);
        }
        
        .team-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 30px;
            margin-top: 30px;
        }
        
        .team-member {
            text-align: center;
            padding: 25px;
            background: white;
            border-radius: 15px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.1);
        }
        
        .member-icon {
            font-size: 2.5rem;
            margin-bottom: 15px;
        }
        
        .pricing {
            background: rgba(255,255,255,0.95);
            padding: 50px 40px;
            border-radius: 20px;
            text-align: center;
            margin: 40px 0;
        }
        
        .price-tag {
            font-size: 3rem;
            color: #27ae60;
            font-weight: bold;
            margin: 20px 0;
        }
        
        footer {
            text-align: center;
            padding: 40px;
            color: white;
            opacity: 0.8;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="hero">
            <h1>🧠 Elite AI Consulting</h1>
            <p>Fortune 500-Level Intelligence • 70B Parameter Research • Multi-Agent Specialists</p>
            <a href="/request" class="cta-button">Start Your Project</a>
        </div>
        
        <div class="features">
            <h2 style="text-align: center; color: #2c3e50; margin-bottom: 20px;">
                Why Choose Elite AI Consulting?
            </h2>
            
            <div class="features-grid">
                <div class="feature">
                    <div class="feature-icon">🧠</div>
                    <h3>70B Intelligence</h3>
                    <p>Powered by cutting-edge 70-billion parameter AI models that deliver research quality rivaling top consulting firms.</p>
                </div>
                
                <div class="feature">
                    <div class="feature-icon">👥</div>
                    <h3>Multi-Agent Team</h3>
                    <p>Specialized AI agents work together like a real consulting team - research, strategy, technical, and communications experts.</p>
                </div>
                
                <div class="feature">
                    <div class="feature-icon">📊</div>
                    <h3>Professional Deliverables</h3>
                    <p>Receive comprehensive PDF reports and executive summaries delivered directly to your inbox.</p>
                </div>
                
                <div class="feature">
                    <div class="feature-icon">⚡</div>
                    <h3>Lightning Fast</h3>
                    <p>Complete Fortune 500-level analysis in minutes, not weeks. Get strategic insights when you need them.</p>
                </div>
                
                <div class="feature">
                    <div class="feature-icon">🔒</div>
                    <h3>100% Private</h3>
                    <p>All analysis runs locally. Your sensitive business data never leaves our secure environment.</p>
                </div>
                
                <div class="feature">
                    <div class="feature-icon">💰</div>
                    <h3>Unbeatable Value</h3>
                    <p>Get $50,000+ consulting quality for a fraction of traditional consulting costs.</p>
                </div>
            </div>
        </div>
        
        <div class="team-section">
            <h2 style="text-align: center; color: #2c3e50; margin-bottom: 20px;">
                Meet Your AI Consulting Team
            </h2>
            
            <div class="team-grid">
                <div class="team-member">
                    <div class="member-icon">🔍</div>
                    <h4>Dr. Research</h4>
                    <p><strong>70B Intelligence</strong></p>
                    <p>Market analysis, competitive intelligence, industry benchmarks</p>
                </div>
                
                <div class="team-member">
                    <div class="member-icon">👔</div>
                    <h4>Alex Manager</h4>
                    <p><strong>Project Coordinator</strong></p>
                    <p>Strategic planning, timelines, resource optimization</p>
                </div>
                
                <div class="team-member">
                    <div class="member-icon">⚙️</div>
                    <h4>Tech Oracle</h4>
                    <p><strong>Chief Architect</strong></p>
                    <p>Technical solutions, system design, implementation</p>
                </div>
                
                <div class="team-member">
                    <div class="member-icon">✍️</div>
                    <h4>Maya Writer</h4>
                    <p><strong>Communications Expert</strong></p>
                    <p>Executive summaries, strategic communications</p>
                </div>
                
                <div class="team-member">
                    <div class="member-icon">🎯</div>
                    <h4>Director AI</h4>
                    <p><strong>70B Strategic Oversight</strong></p>
                    <p>C-suite strategy, coordination, quality assurance</p>
                </div>
            </div>
        </div>
        
        <div class="pricing">
            <h2 style="color: #2c3e50; margin-bottom: 20px;">Elite Consulting Package</h2>
            <div class="price-tag">Contact for Pricing</div>
            <p style="font-size: 1.2rem; margin-bottom: 30px;">
                Complete multi-agent analysis with professional PDF deliverables
            </p>
            <a href="/request" class="cta-button">Request Your Analysis</a>
        </div>
    </div>
    
    <footer>
        <p>&copy; 2025 Elite AI Consulting • Powered by Advanced AI Intelligence</p>
    </footer>
</body>
</html>
    '''

@app.route('/request')
def request_form():
    """Project request form"""
    return '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Request Analysis - Elite AI Consulting</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        
        body {
            font-family: 'Arial', sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
        }
        
        .container {
            max-width: 800px;
            margin: 0 auto;
            background: white;
            border-radius: 20px;
            padding: 50px;
            box-shadow: 0 20px 60px rgba(0,0,0,0.2);
        }
        
        h1 {
            text-align: center;
            color: #2c3e50;
            margin-bottom: 30px;
            font-size: 2.5rem;
        }
        
        .form-group {
            margin-bottom: 25px;
        }
        
        label {
            display: block;
            margin-bottom: 8px;
            color: #2c3e50;
            font-weight: bold;
        }
        
        input, textarea, select {
            width: 100%;
            padding: 15px;
            border: 2px solid #e0e0e0;
            border-radius: 10px;
            font-size: 16px;
            transition: border-color 0.3s ease;
        }
        
        input:focus, textarea:focus, select:focus {
            outline: none;
            border-color: #667eea;
        }
        
        textarea {
            height: 120px;
            resize: vertical;
        }
        
        .submit-btn {
            background: linear-gradient(45deg, #667eea, #764ba2);
            color: white;
            padding: 18px 40px;
            border: none;
            border-radius: 50px;
            font-size: 1.2rem;
            font-weight: bold;
            cursor: pointer;
            transition: transform 0.3s ease;
            width: 100%;
        }
        
        .submit-btn:hover {
            transform: translateY(-2px);
        }
        
        .back-link {
            display: inline-block;
            margin-bottom: 20px;
            color: #667eea;
            text-decoration: none;
            font-weight: bold;
        }
        
        .back-link:hover {
            text-decoration: underline;
        }
        
        .project-examples {
            background: #f8f9fa;
            padding: 20px;
            border-radius: 10px;
            margin-bottom: 30px;
        }
        
        .project-examples h3 {
            color: #2c3e50;
            margin-bottom: 15px;
        }
        
        .project-examples ul {
            color: #666;
            line-height: 1.8;
        }
    </style>
</head>
<body>
    <div class="container">
        <a href="/" class="back-link">← Back to Home</a>
        
        <h1>🎯 Request Elite Analysis</h1>
        
        <div class="project-examples">
            <h3>💡 Example Projects We Excel At:</h3>
            <ul>
                <li>Digital transformation strategies for traditional industries</li>
                <li>Market entry analysis for new products or regions</li>
                <li>Competitive intelligence and benchmarking studies</li>
                <li>Technology implementation roadmaps</li>
                <li>Customer retention and growth strategies</li>
                <li>Operational efficiency optimization</li>
            </ul>
        </div>
        
        <form id="projectForm">
            <div class="form-group">
                <label for="client_name">Your Name *</label>
                <input type="text" id="client_name" name="client_name" required>
            </div>
            
            <div class="form-group">
                <label for="client_email">Email Address *</label>
                <input type="email" id="client_email" name="client_email" required>
            </div>
            
            <div class="form-group">
                <label for="company">Company/Organization</label>
                <input type="text" id="company" name="company">
            </div>
            
            <div class="form-group">
                <label for="project_type">Project Type *</label>
                <select id="project_type" name="project_type" required>
                    <option value="">Select project type...</option>
                    <option value="market_analysis">Market Analysis & Research</option>
                    <option value="digital_transformation">Digital Transformation Strategy</option>
                    <option value="competitive_intelligence">Competitive Intelligence</option>
                    <option value="technology_roadmap">Technology Implementation</option>
                    <option value="business_strategy">Business Strategy Development</option>
                    <option value="operational_optimization">Operational Optimization</option>
                    <option value="custom">Custom Analysis</option>
                </select>
            </div>
            
            <div class="form-group">
                <label for="project_description">Project Description *</label>
                <textarea id="project_description" name="project_description" 
                         placeholder="Describe your strategic challenge, objectives, and what you hope to achieve..." required></textarea>
            </div>
            
            <div class="form-group">
                <label for="timeline">Desired Timeline</label>
                <select id="timeline" name="timeline">
                    <option value="immediate">Immediate (within 24 hours)</option>
                    <option value="urgent">Urgent (within 3 days)</option>
                    <option value="standard">Standard (within 1 week)</option>
                    <option value="flexible">Flexible</option>
                </select>
            </div>
            
            <button type="submit" class="submit-btn">
                🚀 Request Elite Analysis
            </button>
        </form>
    </div>
    
    <script>
        document.getElementById('projectForm').addEventListener('submit', function(e) {
            e.preventDefault();
            
            // Collect form data
            const formData = new FormData(this);
            const data = Object.fromEntries(formData);
            
            // Show loading state
            const submitBtn = document.querySelector('.submit-btn');
            const originalText = submitBtn.innerHTML;
            submitBtn.innerHTML = '🧠 Initiating Elite Analysis...';
            submitBtn.disabled = true;
            
            // Submit to backend
            fetch('/submit_project', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(data)
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    window.location.href = '/status/' + data.project_id;
                } else {
                    alert('Error: ' + data.message);
                    submitBtn.innerHTML = originalText;
                    submitBtn.disabled = false;
                }
            })
            .catch(error => {
                alert('Error submitting project. Please try again.');
                submitBtn.innerHTML = originalText;
                submitBtn.disabled = false;
            });
        });
    </script>
</body>
</html>
    '''

@app.route('/submit_project', methods=['POST'])
def submit_project():
    """Handle project submission"""
    try:
        data = request.get_json()
        
        # Generate project ID
        project_id = f"ELITE_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        # Store project data
        projects_db[project_id] = {
            'id': project_id,
            'client_name': data['client_name'],
            'client_email': data['client_email'],
            'company': data.get('company', ''),
            'project_type': data['project_type'],
            'description': data['project_description'],
            'timeline': data.get('timeline', 'standard'),
            'status': 'processing',
            'created_at': datetime.now().isoformat(),
            'pdfs': []
        }
        
        # Start processing in background
        threading.Thread(
            target=process_project_background,
            args=(project_id, data)
        ).start()
        
        return jsonify({
            'success': True,
            'project_id': project_id,
            'message': 'Elite analysis initiated successfully!'
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        })

def process_project_background(project_id, data):
    """Process project in background"""
    try:
        # Update status
        projects_db[project_id]['status'] = 'analyzing'
        
        # Setup email service if configured
        email_service = EmailService()
        # You would set up email credentials here
        
        # Create supervisor with email
        supervisor_with_email = SupervisorAgent(email_service)
        
        # Process the project
        pdfs = supervisor_with_email.orchestrate_project_with_email(
            data['project_description'],
            data['client_email'],
            data['client_name']
        )
        
        # Update project with results
        projects_db[project_id]['status'] = 'completed'
        projects_db[project_id]['pdfs'] = [str(pdf) for pdf in pdfs]
        projects_db[project_id]['completed_at'] = datetime.now().isoformat()
        
    except Exception as e:
        projects_db[project_id]['status'] = 'error'
        projects_db[project_id]['error'] = str(e)

@app.route('/status/<project_id>')
def project_status(project_id):
    """Show project status"""
    project = projects_db.get(project_id)
    if not project:
        return "Project not found", 404
    
    status_messages = {
        'processing': '🧠 Deploying Elite AI Team...',
        'analyzing': '📊 70B Intelligence Analyzing...',
        'completed': '✅ Elite Analysis Complete!',
        'error': '❌ Analysis Error Occurred'
    }
    
    return f'''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Project Status - Elite AI Consulting</title>
    <meta http-equiv="refresh" content="10">
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        
        body {{
            font-family: 'Arial', sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            display: flex;
            align-items: center;
            justify-content: center;
            padding: 20px;
        }}
        
        .status-container {{
            background: white;
            border-radius: 20px;
            padding: 50px;
            text-align: center;
            box-shadow: 0 20px 60px rgba(0,0,0,0.2);
            max-width: 600px;
        }}
        
        .status-icon {{
            font-size: 4rem;
            margin-bottom: 20px;
        }}
        
        .status-message {{
            font-size: 1.8rem;
            color: #2c3e50;
            margin-bottom: 30px;
        }}
        
        .project-info {{
            background: #f8f9fa;
            padding: 30px;
            border-radius: 15px;
            margin: 30px 0;
        }}
        
        .progress-bar {{
            width: 100%;
            height: 10px;
            background: #e0e0e0;
            border-radius: 5px;
            overflow: hidden;
            margin: 20px 0;
        }}
        
        .progress-fill {{
            height: 100%;
            background: linear-gradient(45deg, #667eea, #764ba2);
            transition: width 0.3s ease;
        }}
        
        .back-link {{
            display: inline-block;
            margin-top: 20px;
            color: #667eea;
            text-decoration: none;
            font-weight: bold;
        }}
    </style>
</head>
<body>
    <div class="status-container">
        <div class="status-icon">
            {"🧠" if project['status'] in ['processing', 'analyzing'] else "✅" if project['status'] == 'completed' else "❌"}
        </div>
        
        <div class="status-message">
            {status_messages.get(project['status'], 'Unknown status')}
        </div>
        
        <div class="progress-bar">
            <div class="progress-fill" style="width: {'25%' if project['status'] == 'processing' else '75%' if project['status'] == 'analyzing' else '100%' if project['status'] == 'completed' else '0%'}"></div>
        </div>
        
        <div class="project-info">
            <h3>Project Details</h3>
            <p><strong>ID:</strong> {project_id}</p>
            <p><strong>Client:</strong> {project['client_name']}</p>
            <p><strong>Type:</strong> {project['project_type'].replace('_', ' ').title()}</p>
            <p><strong>Status:</strong> {project['status'].title()}</p>
        </div>
        
        {f'<p style="color: #27ae60; font-weight: bold; font-size: 1.2rem;">Elite analysis complete! Check your email for deliverables.</p>' if project['status'] == 'completed' else ''}
        {f'<p style="color: #e74c3c;">Error: {project.get("error", "Unknown error")}</p>' if project['status'] == 'error' else ''}
        
        <a href="/" class="back-link">← Return to Home</a>
    </div>
</body>
</html>
    '''

if __name__ == '__main__':
    print("🚀 LAUNCHING ELITE AI CONSULTING WEB INTERFACE!")
    print("🌐 Access your consulting firm at: http://localhost:5000")
    print("🎯 Professional client interface ready!")
    
    app.run(debug=True, host='0.0.0.0', port=5000)