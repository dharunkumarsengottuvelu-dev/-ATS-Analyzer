import json
from ollama import AsyncClient
from backend.prompts.reviewer import REVIEWER_PROMPT, REWRITER_PROMPT

async def get_resume_review(resume_text: str, job_description: str = "") -> dict:
    """
    Calls the local Llama 3.2 model to review the resume and provide feedback.
    """
    prompt = REVIEWER_PROMPT.format(
        resume_text=resume_text,
        job_description=job_description if job_description else "None provided."
    )
    
    client = AsyncClient(host='http://localhost:11434')
    
    response = await client.chat(model='llama3.2', messages=[
        {
            'role': 'user',
            'content': prompt
        }
    ], options={'temperature': 0.3})
    
    # Attempt to parse the JSON response
    try:
        content = response['message']['content']
        # Very basic sanitization in case the model outputs markdown blocks
        if content.startswith("```json"):
            content = content[7:-3]
        return json.loads(content)
    except Exception as e:
        print(f"Failed to parse LLM response: {e}")
        return {
            "strengths": [],
            "weaknesses": ["Failed to generate review. Please try again."],
            "feedback": "LLM Parsing error.",
            "recommendations": []
        }

async def rewrite_section(section_name: str, section_text: str) -> dict:
    """
    Calls the local Llama 3.2 model to rewrite a specific section of the resume.
    """
    prompt = REWRITER_PROMPT.format(
        section_name=section_name,
        section_text=section_text
    )
    
    client = AsyncClient(host='http://localhost:11434')
    
    response = await client.chat(model='llama3.2', messages=[
        {
            'role': 'user',
            'content': prompt
        }
    ], options={'temperature': 0.5})
    
    try:
        content = response['message']['content']
        if content.startswith("```json"):
            content = content[7:-3]
        return json.loads(content)
    except Exception as e:
        print(f"Failed to parse LLM response: {e}")
        return {
            "rewritten_text": section_text,
            "changes_made": "Error during rewrite generation."
        }
