"""
Knowledge Base Summarizer
Creates intelligent summaries of large PDF reports to reduce token usage.
"""
import os
from typing import Optional
from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage


def summarize_report_content(
    report_content: str, 
    max_tokens: int = 10000,
    api_key: Optional[str] = None,
    model_name: str = "gpt-4o"
) -> str:
    """
    Summarize large report content to reduce token usage.
    
    Args:
        report_content: The full report content to summarize
        max_tokens: Target maximum tokens for the summary (approximate)
        api_key: OpenAI API key (defaults to OPENAI_API_KEY env var)
        model_name: Model to use for summarization (default: gpt-4o)
    
    Returns:
        Summarized content that fits within token limits
    """
    # If content is already short enough, return as-is
    # Rough estimate: 1 token ≈ 4 characters
    estimated_tokens = len(report_content) // 4
    if estimated_tokens <= max_tokens:
        return report_content
    
    api_key = api_key or os.getenv("OPENAI_API_KEY")
    if not api_key:
        # If no API key, just truncate
        return truncate_content(report_content, max_tokens * 4)
    
    try:
        llm = ChatOpenAI(
            model=model_name,
            temperature=0.3,
            api_key=api_key
        )
        
        # Truncate input if too large (limit to ~50k chars = ~12.5k tokens for input)
        # This ensures we don't hit token limits during summarization
        max_input_chars = 50000
        if len(report_content) > max_input_chars:
            # Take first 60% and last 40% to preserve structure
            first_part = report_content[:int(max_input_chars * 0.6)]
            last_part = report_content[-int(max_input_chars * 0.4):]
            truncated_input = first_part + "\n\n[... MIDDLE CONTENT ...]\n\n" + last_part
        else:
            truncated_input = report_content
        
        # Create summarization prompt
        summary_prompt = f"""You are a report summarizer. Summarize the following report content, preserving ALL critical information including:
- Assessment scores (RRI, PRI, 7WPD, HRI, AntarBahya, etc.) - include exact numbers
- Key findings and insights
- Important data points and metrics
- Risk indicators and flags
- Recommendations
- Personality traits and behavioral patterns
- Health and medical information
- Family dynamics information
- Values and beliefs

Keep the summary comprehensive but concise. Target length: approximately {max_tokens * 4} characters.
Preserve all numerical scores, percentages, and specific assessments.

Report Content:
{truncated_input}
"""
        
        messages = [
            SystemMessage(content="You are an expert at summarizing detailed assessment reports while preserving all critical information."),
            HumanMessage(content=summary_prompt)
        ]
        
        response = llm.invoke(messages)
        return response.content
        
    except Exception as e:
        print(f"Error summarizing report: {e}. Using truncated version.")
        return truncate_content(report_content, max_tokens * 4)


def truncate_content(content: str, max_chars: int = 40000) -> str:
    """
    Truncate content intelligently, preserving structure.
    
    Args:
        content: Content to truncate
        max_chars: Maximum characters to keep
    
    Returns:
        Truncated content with beginning and end preserved
    """
    if len(content) <= max_chars:
        return content
    
    # Keep first 60% and last 40% to preserve structure
    first_part = content[:int(max_chars * 0.6)]
    last_part = content[-int(max_chars * 0.4):]
    
    return (
        first_part + 
        "\n\n[... MIDDLE CONTENT TRUNCATED TO REDUCE TOKEN USAGE ...]\n\n" +
        last_part
    )
