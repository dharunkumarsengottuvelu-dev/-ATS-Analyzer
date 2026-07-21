import os
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib import colors
from backend.schemas.analysis import MatchMetrics

REPORTS_DIR = os.path.join(os.path.dirname(__file__), "../../reports")
os.makedirs(REPORTS_DIR, exist_ok=True)

def generate_pdf_report(filename: str, ats_score: dict, metrics: MatchMetrics, llm_feedback: dict) -> str:
    """
    Generates a professional PDF report containing the ATS score and feedback.
    Returns the file path of the generated PDF.
    """
    report_path = os.path.join(REPORTS_DIR, f"{filename}_ATS_Report.pdf")
    
    c = canvas.Canvas(report_path, pagesize=letter)
    width, height = letter
    
    # Title
    c.setFont("Helvetica-Bold", 20)
    c.drawString(50, height - 50, "ATS Resume Analysis Report")
    
    c.setFont("Helvetica", 12)
    c.drawString(50, height - 70, f"Generated for: {filename}")
    
    # Overall Score Section
    c.setFont("Helvetica-Bold", 16)
    c.drawString(50, height - 120, f"Overall ATS Score: {ats_score['overall_score']}%")
    
    c.setFont("Helvetica", 12)
    c.drawString(50, height - 140, f"Semantic Match: {ats_score['breakdown']['semantic_score']}%")
    c.drawString(50, height - 155, f"Keyword Coverage: {ats_score['breakdown']['keyword_score']}%")
    c.drawString(50, height - 170, f"Completeness: {ats_score['breakdown']['completeness_score']}%")
    
    # Strengths
    c.setFont("Helvetica-Bold", 14)
    c.setFillColor(colors.green)
    c.drawString(50, height - 210, "Strengths")
    c.setFillColor(colors.black)
    c.setFont("Helvetica", 11)
    y = height - 230
    for strength in llm_feedback.get("strengths", []):
        c.drawString(60, y, f"- {strength}")
        y -= 15
        
    # Weaknesses
    y -= 20
    c.setFont("Helvetica-Bold", 14)
    c.setFillColor(colors.red)
    c.drawString(50, y, "Areas for Improvement")
    c.setFillColor(colors.black)
    c.setFont("Helvetica", 11)
    y -= 20
    for weakness in llm_feedback.get("weaknesses", []):
        c.drawString(60, y, f"- {weakness}")
        y -= 15
        
    # Recommendations
    y -= 20
    c.setFont("Helvetica-Bold", 14)
    c.setFillColor(colors.blue)
    c.drawString(50, y, "Actionable Recommendations")
    c.setFillColor(colors.black)
    c.setFont("Helvetica", 11)
    y -= 20
    for rec in llm_feedback.get("recommendations", []):
        c.drawString(60, y, f"- {rec}")
        y -= 15
        
    # Feedback Summary
    y -= 20
    c.setFont("Helvetica-Bold", 14)
    c.drawString(50, y, "Recruiter Feedback Summary")
    c.setFont("Helvetica", 11)
    y -= 20
    
    # Handle text wrapping for feedback (basic implementation)
    feedback_text = llm_feedback.get("feedback", "")
    words = feedback_text.split()
    line = ""
    for word in words:
        if c.stringWidth(line + word + " ", "Helvetica", 11) < (width - 100):
            line += word + " "
        else:
            c.drawString(50, y, line)
            y -= 15
            line = word + " "
    c.drawString(50, y, line)

    c.save()
    return report_path
