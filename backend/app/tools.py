"""
Local File Retrieval Tools

Tools for reading and searching documents across different categories:
- Academic: Academic calendar, schedules, dates
- Administrative: University policies, procedures, contact info
- Educational: Course materials, educational resources

These tools are used by the LangGraph agent to retrieve
relevant information from the organized knowledge base.
"""

import re
from datetime import datetime
from pathlib import Path
from typing import Optional, List
from langchain_core.tools import tool
from app.config import ACADEMIC_DIR, ADMINISTRATIVE_DIR, EDUCATIONAL_DIR


def get_all_txt_files_in_category(category_dir: Path) -> List[Path]:
    """Get all .txt files in a category directory."""
    if not category_dir.exists():
        return []
    return list(category_dir.glob("*.txt"))


def read_file_content(file_path: Path) -> str:
    """Read entire content of a file."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return f.read()
    except FileNotFoundError:
        return f"Error: File not found at {file_path}"
    except Exception as e:
        return f"Error reading file: {str(e)}"


def search_file_content(file_path: Path, query: str, context_lines: int = 3) -> str:
    """
    Search for query in file and return matching sections with context.
    
    Args:
        file_path: Path to file to search
        query: Search query (can be keywords or phrases)
        context_lines: Number of lines of context around matches
        
    Returns:
        Matched sections with context
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        # Split query into keywords - keep numbers and month names
        keywords = []
        for kw in query.split():
            kw = kw.lower().strip().rstrip(',')
            # Keep numbers, month names, or words longer than 2 chars
            if kw.isdigit() or len(kw) > 2 or kw in ['jan', 'feb', 'mar', 'apr', 'may', 'jun', 'jul', 'aug', 'sep', 'oct', 'nov', 'dec']:
                keywords.append(kw)
        
        # If no keywords found, use the whole query
        if not keywords:
            keywords = [query.lower()]
        
        matched_sections = []
        matched_line_numbers = set()
        
        # Find all matching lines
        for i, line in enumerate(lines):
            line_lower = line.lower()
            if any(keyword in line_lower for keyword in keywords):
                matched_line_numbers.add(i)
        
        # Get context around matches
        if matched_line_numbers:
            matched_line_numbers = sorted(matched_line_numbers)
            
            # Group nearby matches and extract with context
            current_section = []
            last_line = -999
            
            for line_num in matched_line_numbers:
                # Start new section if far from last match
                if line_num - last_line > context_lines * 2:
                    if current_section:
                        matched_sections.append("".join(current_section))
                    current_section = []
                    
                    # Add context before match
                    start = max(0, line_num - context_lines)
                    for j in range(start, line_num + context_lines + 1):
                        if j < len(lines):
                            current_section.append(lines[j])
                else:
                    # Extend current section
                    for j in range(last_line + 1, line_num + context_lines + 1):
                        if j < len(lines) and j > last_line + context_lines:
                            current_section.append(lines[j])
                
                last_line = line_num
            
            if current_section:
                matched_sections.append("".join(current_section))
        
        if matched_sections:
            return "\n---\n".join(matched_sections)
        else:
            return f"No relevant information found in {file_path.name} for query: {query}"
            
    except Exception as e:
        return f"Error searching file: {str(e)}"


@tool
def search_university_info(query: str) -> str:
    """
    Search administrative information files for university policies, 
    procedures, programs, services, and contact information.
    
    Use this tool to answer questions about:
    - Tuition fee payments and deadlines
    - Academic programs and courses (e.g., SQL, Database Systems)
    - Admissions procedures
    - Student services (health, library, career center, housing)
    - Technical support and IT services
    - Academic policies (attendance, grading, withdrawals)
    - Contact information for university offices
    - Campus facilities
    - Research opportunities
    - Financial aid and scholarships
    
    Args:
        query: Search query describing what information is needed
        
    Returns:
        Relevant sections from administrative files
    """
    # Search all files in Administrative directory
    txt_files = get_all_txt_files_in_category(ADMINISTRATIVE_DIR)
    
    if not txt_files:
        return "No administrative information files found. The related data is not present in the system."
    
    results = []
    for file_path in txt_files:
        result = search_file_content(file_path, query, context_lines=5)
        if "No relevant information found" not in result:
            results.append(f"From {file_path.name}:\n{result}")
    
    if results:
        return "\n\n---\n\n".join(results)
    else:
        return f"No relevant administrative information found for query: {query}. The related data is not present in the system."


@tool
def search_academic_calendar(query: str) -> str:
    """
    Search academic files for dates, holidays, deadlines, and academic events.
    
    Use this tool to answer questions about:
    - Holiday dates and observances
    - Semester start and end dates
    - Registration periods
    - Exam schedules
    - Break periods (Spring Break, Thanksgiving, etc.)
    - Important academic deadlines
    - University closures
    
    Args:
        query: Date query (e.g., "November 1", "Thanksgiving", "Fall semester start")
        
    Returns:
        Relevant dates and events from academic files
    """
    # Search all files in Academic directory
    txt_files = get_all_txt_files_in_category(ACADEMIC_DIR)
    
    if not txt_files:
        return "No academic calendar files found. The related data is not present in the system."
    
    results = []
    for file_path in txt_files:
        result = search_file_content(file_path, query, context_lines=3)
        if "No relevant information found" not in result:
            results.append(f"From {file_path.name}:\n{result}")
    
    if results:
        return "\n\n---\n\n".join(results)
    else:
        return f"No relevant academic information found for query: {query}. The related data is not present in the system."


@tool
def check_if_date_is_holiday(date_str: str) -> str:
    """
    Check if a specific date is a university holiday.
    
    Use this to find out if a date has no classes or is a holiday.
    
    Args:
        date_str: Date to check (e.g., "November 1", "Nov 1", "Thanksgiving")
        
    Returns:
        Information about whether the date is a holiday
    """
    # Search all files in Academic directory
    txt_files = get_all_txt_files_in_category(ACADEMIC_DIR)
    
    if not txt_files:
        return "No academic calendar files found. The related data is not present in the system."
    
    results = []
    for file_path in txt_files:
        result = search_file_content(file_path, date_str + " holiday", context_lines=2)
        if "No relevant information found" not in result:
            results.append(result)
    
    if results:
        return "\n\n---\n\n".join(results)
    else:
        return f"No holiday information found for {date_str}. The related data is not present in the system."


@tool
def get_university_contact_info(department: str) -> str:
    """
    Get contact information for a specific university department or office.
    
    Args:
        department: Name of department (e.g., "Bursar", "Admissions", "IT Help Desk")
        
    Returns:
        Contact information including email and phone number
    """
    # Search all files in Administrative directory
    txt_files = get_all_txt_files_in_category(ADMINISTRATIVE_DIR)
    
    if not txt_files:
        return "No administrative files found. The related data is not present in the system."
    
    for file_path in txt_files:
        content = read_file_content(file_path)
        
        # Search for contact information section
        lines = content.split('\n')
        contact_section = []
        in_contact = False
        
        for line in lines:
            if '[Contact Information]' in line:
                in_contact = True
            elif in_contact:
                if line.strip().startswith('['):
                    break
                contact_section.append(line)
        
        contact_text = '\n'.join(contact_section)
        
        # Search for specific department
        if department.lower() in contact_text.lower():
            relevant_lines = [line for line in contact_section if department.lower() in line.lower()]
            return '\n'.join(relevant_lines)
    
    return f"Contact information for '{department}' not found. The related data is not present in the system."


@tool
def search_educational_resources(query: str) -> str:
    """
    Search educational resource files for course materials, study guides, 
    and educational content.
    
    Use this tool to answer questions about:
    - Course materials and syllabi
    - Study guides and resources
    - Educational content and references
    - Learning materials
    
    Args:
        query: Search query for educational content
        
    Returns:
        Relevant sections from educational resource files
    """
    # Search all files in Educational directory
    txt_files = get_all_txt_files_in_category(EDUCATIONAL_DIR)
    
    if not txt_files:
        return "No educational resource files found. The related data is not present in the system."
    
    results = []
    for file_path in txt_files:
        result = search_file_content(file_path, query, context_lines=5)
        if "No relevant information found" not in result:
            results.append(f"From {file_path.name}:\n{result}")
    
    if results:
        return "\n\n---\n\n".join(results)
    else:
        return f"No relevant educational resources found for query: {query}. The related data is not present in the system."


# List of all available tools
available_tools = [
    search_university_info,
    search_academic_calendar,
    check_if_date_is_holiday,
    get_university_contact_info,
    search_educational_resources,
]
