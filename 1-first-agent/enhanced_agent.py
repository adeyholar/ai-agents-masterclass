import os
import json
import requests
from datetime import datetime
import subprocess
import webbrowser
from pathlib import Path

# Local Ollama configuration
OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL = "llama3.2:latest"

# Set up working directory
WORKING_DIR = Path("agent_workspace")
WORKING_DIR.mkdir(exist_ok=True)  # Create if it doesn't exist

def chat_with_ollama(prompt):
    """Chat with your local Ollama AI"""
    data = {
        "model": MODEL,
        "prompt": prompt,
        "stream": False
    }
    
    try:
        response = requests.post(OLLAMA_URL, json=data)
        result = response.json()
        return result.get('response', 'No response')
    except Exception as e:
        return f"Error: {e}"

# ===== ENHANCED TOOL FUNCTIONS =====

def create_file(filename, content):
    """Create a file with specified content in the working directory"""
    try:
        # Ensure filename doesn't contain path separators for security
        filename = os.path.basename(filename)
        filepath = WORKING_DIR / filename
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        return f"✅ Successfully created file: {filepath}"
    except Exception as e:
        return f"❌ Error creating file: {e}"

def read_file(filename):
    """Read content from a file in the working directory"""
    try:
        filename = os.path.basename(filename)
        filepath = WORKING_DIR / filename
        
        if not filepath.exists():
            return f"❌ File not found: {filename} (searched in {WORKING_DIR})"
        
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        return f"📄 Content of {filename}:\n{'-'*40}\n{content}\n{'-'*40}"
    except Exception as e:
        return f"❌ Error reading file: {e}"

def list_files(directory=None):
    """List files in the working directory or specified subdirectory"""
    try:
        if directory and directory != ".":
            # If specific directory requested, check if it's within working dir
            target_dir = WORKING_DIR / directory
        else:
            target_dir = WORKING_DIR
        
        if not target_dir.exists():
            return f"❌ Directory not found: {target_dir}"
        
        files = [f.name for f in target_dir.iterdir() if f.is_file()]
        folders = [f.name for f in target_dir.iterdir() if f.is_dir()]
        
        result = f"📁 Directory: {target_dir}\n"
        result += f"📂 Folders ({len(folders)}): {', '.join(folders) if folders else 'None'}\n"
        result += f"📄 Files ({len(files)}): {', '.join(files) if files else 'None'}"
        return result
    except Exception as e:
        return f"❌ Error listing directory: {e}"

def delete_file(filename):
    """Delete a file from the working directory"""
    try:
        filename = os.path.basename(filename)
        filepath = WORKING_DIR / filename
        
        if not filepath.exists():
            return f"❌ File not found: {filename}"
        
        filepath.unlink()
        return f"🗑️ Successfully deleted file: {filename}"
    except Exception as e:
        return f"❌ Error deleting file: {e}"

def open_website(url):
    """Open a website in the default browser"""
    try:
        # Add protocol if missing
        if not url.startswith(('http://', 'https://')):
            url = 'https://' + url
        webbrowser.open(url)
        return f"🌐 Opened website: {url}"
    except Exception as e:
        return f"❌ Error opening website: {e}"

def get_current_time():
    """Get the current date and time"""
    now = datetime.now()
    return f"🕒 Current time: {now.strftime('%Y-%m-%d %H:%M:%S')}"

def open_working_directory():
    """Open the working directory in file explorer"""
    try:
        if os.name == 'nt':  # Windows
            os.startfile(WORKING_DIR)
        elif os.name == 'posix':  # macOS and Linux
            subprocess.run(['open', WORKING_DIR] if sys.platform == 'darwin' else ['xdg-open', WORKING_DIR])
        return f"📂 Opened working directory: {WORKING_DIR}"
    except Exception as e:
        return f"❌ Error opening directory: {e}"

def create_task_list(tasks):
    """Create a formatted task list in the working directory"""
    try:
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"tasks_{timestamp}.txt"
        filepath = WORKING_DIR / filename
        
        content = f"Task List - Created: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
        content += "=" * 50 + "\n\n"
        
        # Handle both comma-separated and line-separated tasks
        task_list = []
        if ',' in tasks:
            task_list = [task.strip() for task in tasks.split(',')]
        else:
            task_list = [task.strip() for task in tasks.split('\n') if task.strip()]
        
        for i, task in enumerate(task_list, 1):
            content += f"{i}. [ ] {task}\n"
        
        with open(filepath, 'w') as f:
            f.write(content)
        
        return f"📝 Created task list: {filename} in {WORKING_DIR}"
    except Exception as e:
        return f"❌ Error creating task list: {e}"

def save_conversation_log():
    """Save the current conversation to a log file"""
    try:
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"conversation_log_{timestamp}.txt"
        filepath = WORKING_DIR / filename
        
        # This would need access to conversation history
        # For now, just create a placeholder
        content = f"Conversation Log - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
        content += "=" * 50 + "\n"
        content += "Conversation saved!\n"
        
        with open(filepath, 'w') as f:
            f.write(content)
        
        return f"💾 Saved conversation log: {filename}"
    except Exception as e:
        return f"❌ Error saving conversation: {e}"

# ===== TOOL DETECTION AND EXECUTION =====

AVAILABLE_TOOLS = {
    "create_file": create_file,
    "read_file": read_file,
    "list_files": list_files,
    "delete_file": delete_file,
    "open_website": open_website,
    "get_current_time": get_current_time,
    "open_working_directory": open_working_directory,
    "create_task_list": create_task_list,
    "save_conversation_log": save_conversation_log
}

def parse_and_execute_tools(ai_response, user_input):
    """Parse AI response for tool usage and execute them"""
    tools_used = []
    
    user_lower = user_input.lower()
    
    # File operations
    if any(phrase in user_lower for phrase in ["create file", "write file", "save to file", "make a file"]):
        filename, content = extract_file_info(user_input, ai_response)
        if filename:
            result = create_file(filename, content)
            tools_used.append(result)
    
    elif any(phrase in user_lower for phrase in ["read file", "show file", "open file", "view file"]):
        filename = extract_filename(user_input)
        if filename:
            result = read_file(filename)
            tools_used.append(result)
    
    elif any(phrase in user_lower for phrase in ["list files", "show files", "what files", "files in"]):
        directory = extract_directory(user_input)
        result = list_files(directory)
        tools_used.append(result)
    
    elif any(phrase in user_lower for phrase in ["delete file", "remove file", "delete"]):
        filename = extract_filename(user_input)
        if filename:
            result = delete_file(filename)
            tools_used.append(result)
    
    elif any(phrase in user_lower for phrase in ["open folder", "show folder", "open directory", "working directory"]):
        result = open_working_directory()
        tools_used.append(result)
    
    # Web operations
    elif any(phrase in user_lower for phrase in ["open website", "open url", "browse to", "go to"]):
        url = extract_url(user_input)
        if url:
            result = open_website(url)
            tools_used.append(result)
    
    # Time operations
    elif any(phrase in user_lower for phrase in ["time", "date", "current time", "what time"]):
        result = get_current_time()
        tools_used.append(result)
    
    # Task management
    elif any(phrase in user_lower for phrase in ["task list", "todo", "create tasks", "make a list"]):
        tasks = extract_tasks(user_input, ai_response)
        if tasks:
            result = create_task_list(tasks)
            tools_used.append(result)
    
    # Conversation logging
    elif any(phrase in user_lower for phrase in ["save conversation", "log conversation", "save chat"]):
        result = save_conversation_log()
        tools_used.append(result)
    
    return tools_used

def extract_file_info(user_input, ai_response):
    """Extract filename and content from user input and AI response"""
    # Default filename
    filename = f"document_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
    content = ai_response
    
    # Look for filename in user input
    words = user_input.split()
    for i, word in enumerate(words):
        if word.lower() in ["file", "called", "named", "as"] and i + 1 < len(words):
            potential_filename = words[i + 1].replace('"', '').replace("'", "")
            if '.' in potential_filename or len(potential_filename) > 2:
                if '.' not in potential_filename:
                    potential_filename += '.txt'
                filename = potential_filename
                break
    
    # Look for quoted filenames
    import re
    quoted_match = re.search(r'["\']([^"\']+\.[a-zA-Z]{2,4})["\']', user_input)
    if quoted_match:
        filename = quoted_match.group(1)
    
    return filename, content

def extract_filename(user_input):
    """Extract filename from user input"""
    import re
    
    # Look for quoted filenames first
    quoted_match = re.search(r'["\']([^"\']+)["\']', user_input)
    if quoted_match:
        return quoted_match.group(1)
    
    # Look for words with extensions
    words = user_input.split()
    for word in words:
        if '.' in word and len(word) > 3:
            return word.replace('"', '').replace("'", "")
    
    return None

def extract_directory(user_input):
    """Extract directory from user input"""
    if "in " in user_input.lower():
        parts = user_input.lower().split("in ")
        if len(parts) > 1:
            return parts[1].strip().split()[0]
    return None

def extract_url(user_input):
    """Extract URL from user input"""
    import re
    
    # Look for URLs with protocols
    url_match = re.search(r'https?://[^\s]+', user_input)
    if url_match:
        return url_match.group()
    
    # Look for www. domains
    www_match = re.search(r'www\.[^\s]+', user_input)
    if www_match:
        return www_match.group()
    
    # Look for domain names
    domain_match = re.search(r'\b[a-zA-Z0-9-]+\.[a-zA-Z]{2,}\b', user_input)
    if domain_match:
        return domain_match.group()
    
    return None

def extract_tasks(user_input, ai_response):
    """Extract tasks from user input or AI response"""
    # Remove the command part to get just the tasks
    task_text = user_input
    for phrase in ["create task list", "make a list", "todo", "tasks"]:
        if phrase in user_input.lower():
            task_text = user_input.lower().replace(phrase, "").replace("with:", "").replace(":", "").strip()
            break
    
    if ',' in task_text:
        return task_text
    elif '\n' in ai_response and any(char in ai_response for char in ['1.', '2.', '-']):
        return ai_response
    
    return task_text if task_text != user_input else None

def main():
    print("🤖 Enhanced AI Assistant with Function Calling!")
    print(f"📁 Working directory: {WORKING_DIR.absolute()}")
    print("\nI can help you with:")
    print("  📄 File operations (create, read, list, delete)")
    print("  🌐 Open websites")
    print("  🕒 Get current time/date")
    print("  📝 Create task lists")
    print("  📂 Open working directory")
    print("  💾 Save conversation logs")
    print("Type 'quit' to exit\n")
    
    conversation_history = []
    
    # Create initial working directory info
    list_result = list_files()
    print(f"📋 {list_result}\n")
    
    while True:
        user_input = input("You: ").strip()
        
        if user_input.lower() in ['quit', 'q', 'exit']:
            print("👋 Goodbye!")
            break
        
        # Build conversation context with tool capabilities
        context = f"""You are a helpful AI assistant with function calling capabilities. Current date: {datetime.now().date()}
Working directory: {WORKING_DIR}

Available tools:
- create_file(filename, content): Create files in working directory
- read_file(filename): Read file contents from working directory
- list_files(directory): List files in working directory
- delete_file(filename): Delete files from working directory
- open_website(url): Open websites in browser
- get_current_time(): Get current time
- create_task_list(tasks): Create formatted task lists
- open_working_directory(): Open the working folder
- save_conversation_log(): Save conversation to file

Recent conversation:
"""
        for msg in conversation_history[-4:]:
            context += f"{msg}\n"
        context += f"Human: {user_input}\nAssistant:"
        
        print("🤖 Thinking...")
        ai_response = chat_with_ollama(context)
        
        # Check if we should execute any tools
        tools_used = parse_and_execute_tools(ai_response, user_input)
        
        print(f"AI: {ai_response}")
        
        # Show tool results
        if tools_used:
            print("\n🛠️ Tool Results:")
            for result in tools_used:
                print(f"   {result}")
        
        print()  # Empty line for readability
        
        # Store conversation
        conversation_history.append(f"Human: {user_input}")
        conversation_history.append(f"Assistant: {ai_response}")
        if tools_used:
            conversation_history.append(f"Tools executed: {'; '.join(tools_used)}")

if __name__ == "__main__":
    main()