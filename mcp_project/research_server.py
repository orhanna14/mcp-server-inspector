import json
import os
import arxiv
from typing import List, Dict, Any
from fastmcp import FastMCP  # Changed from mcp import FastMCP

# Constants
PAPER_DIR = "papers"

# Initialize FastMCP
mcp = FastMCP("research-server")

@mcp.tool()
def search_papers(topic: str, max_results: int = 5) -> str:
    """Search for academic papers on arXiv based on a topic."""
    try:
        # Search for papers
        search = arxiv.Search(
            query=topic,
            max_results=max_results,
            sort_by=arxiv.SortCriterion.Relevance
        )
        
        results = []
        for result in search.results():
            paper_info = {
                "title": result.title,
                "authors": [author.name for author in result.authors],
                "published": result.published.strftime("%Y-%m-%d"),
                "summary": result.summary,
                "pdf_url": result.pdf_url,
                "arxiv_id": result.entry_id.split('/')[-1]
            }
            results.append(paper_info)
        
        # Save results to file
        os.makedirs(PAPER_DIR, exist_ok=True)
        topic_dir = topic.lower().replace(" ", "_")
        topic_path = os.path.join(PAPER_DIR, topic_dir)
        os.makedirs(topic_path, exist_ok=True)
        
        papers_file = os.path.join(topic_path, "papers_info.json")
        papers_data = {}
        
        for paper in results:
            papers_data[paper["arxiv_id"]] = paper
        
        with open(papers_file, 'w') as f:
            json.dump(papers_data, f, indent=2)
        
        # Return summary
        summary = f"Found {len(results)} papers on '{topic}':\n\n"
        for i, paper in enumerate(results, 1):
            summary += f"{i}. **{paper['title']}**\n"
            summary += f"   - Authors: {', '.join(paper['authors'])}\n"
            summary += f"   - Published: {paper['published']}\n"
            summary += f"   - ID: {paper['arxiv_id']}\n\n"
        
        return summary
        
    except Exception as e:
        return f"Error searching for papers: {str(e)}"

@mcp.tool()
def extract_info(paper_id: str) -> str:
    """Get detailed information about a specific paper by its arXiv ID."""
    try:
        search = arxiv.Search(id_list=[paper_id])
        result = next(search.results())
        
        info = f"**Paper Details for {paper_id}**\n\n"
        info += f"**Title**: {result.title}\n\n"
        info += f"**Authors**: {', '.join([author.name for author in result.authors])}\n\n"
        info += f"**Published**: {result.published.strftime('%Y-%m-%d')}\n\n"
        info += f"**PDF URL**: {result.pdf_url}\n\n"
        info += f"**Summary**: {result.summary}\n\n"
        
        return info
        
    except Exception as e:
        return f"Error extracting paper info: {str(e)}"

@mcp.resource("papers://folders")
def get_available_folders() -> str:
    """
    List all available topic folders in the papers directory.
    
    This resource provides a simple list of all available topic folders.
    """
    folders = []
    
    # Get all topic directories
    if os.path.exists(PAPER_DIR):
        for topic_dir in os.listdir(PAPER_DIR):
            topic_path = os.path.join(PAPER_DIR, topic_dir)
            if os.path.isdir(topic_path):
                papers_file = os.path.join(topic_path, "papers_info.json")
                if os.path.exists(papers_file):
                    folders.append(topic_dir)
    
    # Create a simple markdown list
    content = "# Available Topics\n\n"
    if folders:
        for folder in folders:
            content += f"- {folder}\n"
        content += f"\nUse @{folder} to access papers in that topic.\n"
    else:
        content += "No topics found.\n"
    
    return content

@mcp.resource("papers://{topic}")
def get_topic_papers(topic: str) -> str:
    """
    Get detailed information about papers on a specific topic.
    
    Args:
        topic: The research topic to retrieve papers for
    """
    topic_dir = topic.lower().replace(" ", "_")
    papers_file = os.path.join(PAPER_DIR, topic_dir, "papers_info.json")
    
    if not os.path.exists(papers_file):
        return f"# No papers found for topic: {topic}\n\nTry searching for papers on this topic first."
    
    try:
        with open(papers_file, 'r') as f:
            papers_data = json.load(f)
        
        # Create markdown content with paper details
        content = f"# Papers on {topic.replace('_', ' ').title()}\n\n"
        content += f"Total papers: {len(papers_data)}\n\n"
        
        for paper_id, paper_info in papers_data.items():
            content += f"## {paper_info['title']}\n"
            content += f"- **Paper ID**: {paper_id}\n"
            content += f"- **Authors**: {', '.join(paper_info['authors'])}\n"
            content += f"- **Published**: {paper_info['published']}\n"
            content += f"- **PDF URL**: [{paper_info['pdf_url']}]({paper_info['pdf_url']})\n\n"
            content += f"### Summary\n{paper_info['summary'][:500]}...\n\n"
            content += "---\n\n"
        
        return content
    except json.JSONDecodeError:
        return f"# Error reading papers data for {topic}\n\nThe papers data file is corrupted."

@mcp.prompt()
def generate_search_prompt(topic: str, num_papers: int = 5) -> str:
    """Generate a prompt for Claude to find and discuss academic papers on a specific topic."""
    return f"""Search for {num_papers} academic papers about '{topic}' using the search_papers tool. Follow these instructions:
    1. First, search for papers using search_papers(topic='{topic}', max_results={num_papers})
    2. For each paper found, extract and organize the following information:
       - Paper title
       - Authors
       - Publication date
       - Brief summary of the key findings
       - Main contributions or innovations
       - Methodologies used
       - Relevance to the topic '{topic}'
    
    3. Provide a comprehensive summary that includes:
       - Overview of the current state of research in '{topic}'
       - Common themes and trends across the papers
       - Key research gaps or areas for future investigation
       - Most impactful or influential papers in this area
    
    4. Organize your findings in a clear, structured format with headings and bullet points for easy readability.
    
    Please present both detailed information about each paper and a high-level synthesis of the research landscape in {topic}."""

if __name__ == "__main__":
    mcp.run() 