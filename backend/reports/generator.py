import os
import re
from datetime import datetime
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.lib import colors
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, 
    PageBreak, Flowable, KeepTogether
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.graphics.shapes import Drawing
from reportlab.graphics.barcode.qr import QrCodeWidget
from backend.schemas.analysis import MatchMetrics

REPORTS_DIR = os.path.join(os.path.dirname(__file__), "../../reports")
os.makedirs(REPORTS_DIR, exist_ok=True)

# Custom Flowable for Progress Bar
class ProgressBar(Flowable):
    def __init__(self, width, height, percentage, color=colors.HexColor("#3498DB")):
        Flowable.__init__(self)
        self.width = width
        self.height = height
        self.percentage = max(0, min(100, percentage))
        self.color = color

    def wrap(self, availWidth, availHeight):
        return self.width, self.height

    def draw(self):
        # Background
        self.canv.setFillColor(colors.HexColor("#ECF0F1"))
        self.canv.roundRect(0, 0, self.width, self.height, 4, fill=1, stroke=0)
        # Foreground
        fill_width = (self.percentage / 100.0) * self.width
        if fill_width > 0:
            self.canv.setFillColor(self.color)
            self.canv.roundRect(0, 0, fill_width, self.height, 4, fill=1, stroke=0)

# Custom Flowable for Circular Score (approximated with full circle and score)
class CircularScore(Flowable):
    def __init__(self, size, score, color):
        Flowable.__init__(self)
        self.size = size
        self.score = score
        self.color = color

    def wrap(self, availWidth, availHeight):
        return self.size, self.size

    def draw(self):
        c = self.canv
        cx = self.size / 2.0
        cy = self.size / 2.0
        r = self.size / 2.0
        
        c.setStrokeColor(self.color)
        c.setLineWidth(4)
        c.setFillColor(colors.white)
        c.circle(cx, cy, r, fill=1, stroke=1)
        
        c.setFillColor(self.color)
        c.setFont("Helvetica-Bold", self.size * 0.4)
        c.drawCentredString(cx, cy - (self.size * 0.15), f"{int(self.score)}")

def get_score_color(score):
    if score >= 80: return colors.HexColor("#27AE60") # Green
    if score >= 60: return colors.HexColor("#F39C12") # Orange
    return colors.HexColor("#E74C3C") # Red

def get_hiring_probability(score):
    if score >= 85: return "Very High"
    if score >= 70: return "High"
    if score >= 50: return "Moderate"
    return "Low"

def get_verdict(score):
    if score >= 85: return "Excellent match. Highly likely to pass ATS."
    if score >= 70: return "Good match. Minor optimizations recommended."
    if score >= 50: return "Fair match. Needs significant improvements."
    return "Poor match. Rewrite strongly recommended."

def generate_pdf_report(filename: str, ats_score: dict, metrics: MatchMetrics, llm_feedback: dict, resume_data: dict = None) -> str:
    safe_filename = filename.replace(" ", "_")
    report_path = os.path.join(REPORTS_DIR, f"{safe_filename}_ATS_Report.pdf")
    
    doc = SimpleDocTemplate(
        report_path,
        pagesize=A4,
        rightMargin=20*mm, leftMargin=20*mm,
        topMargin=35*mm, bottomMargin=25*mm
    )
    
    styles = getSampleStyleSheet()
    
    brand_color = colors.HexColor("#2C3E50")
    
    # Define Typography
    title_style = ParagraphStyle('CoverTitle', parent=styles['Heading1'], fontName='Helvetica-Bold', fontSize=28, leading=34, alignment=1, textColor=brand_color, spaceAfter=20)
    subtitle_style = ParagraphStyle('CoverSubtitle', parent=styles['Normal'], fontName='Helvetica', fontSize=14, leading=20, alignment=1, textColor=colors.gray, spaceAfter=40)
    h1 = ParagraphStyle('H1', parent=styles['Heading1'], fontName='Helvetica-Bold', fontSize=18, leading=22, textColor=brand_color, spaceBefore=20, spaceAfter=15)
    h2 = ParagraphStyle('H2', parent=styles['Heading2'], fontName='Helvetica-Bold', fontSize=14, leading=18, textColor=brand_color, spaceBefore=15, spaceAfter=10)
    body = ParagraphStyle('Body', parent=styles['Normal'], fontName='Helvetica', fontSize=11, leading=16.5, spaceAfter=10, textColor=colors.HexColor("#333333"))
    body_bold = ParagraphStyle('BodyBold', parent=body, fontName='Helvetica-Bold')
    bullet = ParagraphStyle('Bullet', parent=body, leftIndent=15, firstLineIndent=-10)
    
    story = []
    overall = ats_score.get('overall_score', 0)
    breakdown = ats_score.get('breakdown', {})
    
    # --- 1. COVER PAGE ---
    story.append(Spacer(1, 40*mm))
    story.append(Paragraph("ATS Resume Analysis Report", title_style))
    story.append(Paragraph("Comprehensive ATS & AI Evaluation", subtitle_style))
    
    story.append(Spacer(1, 20*mm))
    score_color = get_score_color(overall)
    
    # Large Cover Score
    score_table = Table([
        [CircularScore(100, overall, score_color)],
        [Paragraph(f"<font color='{score_color.hexval()}'><b>OVERALL SCORE</b></font>", ParagraphStyle('c', parent=body, alignment=1, fontSize=12))]
    ], colWidths=[120], rowHeights=[110, 20])
    score_table.setStyle(TableStyle([('ALIGN', (0,0), (-1,-1), 'CENTER'), ('VALIGN', (0,0), (-1,-1), 'MIDDLE')]))
    story.append(score_table)
    
    story.append(Spacer(1, 30*mm))
    
    date_str = datetime.now().strftime("%B %d, %Y")
    info_data = [
        [Paragraph("<b>Candidate:</b>", body), Paragraph(filename, body)],
        [Paragraph("<b>Date:</b>", body), Paragraph(date_str, body)],
        [Paragraph("<b>Hiring Probability:</b>", body), Paragraph(f"<b><font color='{score_color.hexval()}'>{get_hiring_probability(overall)}</font></b>", body)],
        [Paragraph("<b>Verdict:</b>", body), Paragraph(get_verdict(overall), body)]
    ]
    info_t = Table(info_data, colWidths=[100, 300])
    info_t.setStyle(TableStyle([('VALIGN', (0,0), (-1,-1), 'TOP')]))
    story.append(info_t)
    
    story.append(PageBreak())
    
    # --- 2. EXECUTIVE SUMMARY & SCORE BREAKDOWN ---
    story.append(Paragraph("Executive Summary", h1))
    
    # Score Breakdown Bars
    story.append(Paragraph("Category Breakdown", h2))
    
    def make_bar_row(label, val):
        c = get_score_color(val)
        return [
            Paragraph(label, body_bold),
            ProgressBar(200, 10, val, c),
            Paragraph(f"<font color='{c.hexval()}'><b>{val}%</b></font>", body)
        ]
        
    bar_data = [
        make_bar_row("Semantic Match", breakdown.get('semantic_score', 0)),
        make_bar_row("Keyword Coverage", breakdown.get('keyword_score', 0)),
        make_bar_row("Completeness", breakdown.get('completeness_score', 0))
    ]
    bar_table = Table(bar_data, colWidths=[150, 220, 50])
    bar_table.setStyle(TableStyle([
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('BOTTOMPADDING', (0,0), (-1,-1), 8)
    ]))
    story.append(bar_table)
    
    # --- 3. SKILLS ANALYSIS ---
    story.append(Paragraph("Skills & Keyword Analysis", h1))
    
    matched = metrics.matched_skills if hasattr(metrics, 'matched_skills') else []
    missing = metrics.missing_skills if hasattr(metrics, 'missing_skills') else []
    
    # We will put matched and missing in a side-by-side table
    def build_list(items, color):
        lst = []
        for i in items:
            lst.append(Paragraph(f"<font color='{color}'>&bull;</font> {i}", bullet))
        if not lst:
            lst.append(Paragraph("<i>None</i>", body))
        return lst
        
    matched_flow = [Paragraph("<b>Matched Skills</b>", body)] + build_list(matched, "#27AE60")
    missing_flow = [Paragraph("<b>Missing Skills</b>", body)] + build_list(missing, "#E74C3C")
    
    skills_t = Table([[matched_flow, missing_flow]], colWidths=[A4[0]/2 - 25*mm, A4[0]/2 - 25*mm])
    skills_t.setStyle(TableStyle([
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ('BACKGROUND', (0,0), (0,0), colors.HexColor("#EAFAF1")),
        ('BACKGROUND', (1,0), (1,0), colors.HexColor("#FDEDEC")),
        ('BOX', (0,0), (0,0), 0.5, colors.HexColor("#27AE60")),
        ('BOX', (1,0), (1,0), 0.5, colors.HexColor("#E74C3C")),
        ('PADDING', (0,0), (-1,-1), 10)
    ]))
    story.append(KeepTogether(skills_t))
    
    # --- 4. RESUME SECTION ANALYSIS ---
    story.append(Paragraph("Resume Section Analysis", h1))
    story.append(Paragraph("Analysis of formatting, education, experience, and projects based on AI review.", body))
    
    def section_block(title, items, icon_color):
        block = [Paragraph(f"<b><font color='{icon_color}'>[+]</font> {title}</b>", body)]
        for it in items:
            # clean asterisks if llm returned markdown
            clean_it = it.replace("*", "")
            block.append(Paragraph(f"&bull; {clean_it}", bullet))
        if not items:
            block.append(Paragraph("<i>No specific remarks.</i>", body))
        return block
        
    strengths = llm_feedback.get("strengths", [])
    weaknesses = llm_feedback.get("weaknesses", [])
    recs = llm_feedback.get("recommendations", [])
    
    s_t = Table([[
        section_block("Strengths & Formatting", strengths, "#27AE60"),
        section_block("Areas for Improvement", weaknesses, "#E74C3C")
    ]], colWidths=[A4[0]/2 - 25*mm, A4[0]/2 - 25*mm])
    s_t.setStyle(TableStyle([
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ('PADDING', (0,0), (-1,-1), 10),
        ('BOX', (0,0), (-1,-1), 0.5, colors.lightgrey),
        ('INNERGRID', (0,0), (-1,-1), 0.5, colors.lightgrey)
    ]))
    story.append(s_t)
    
    # --- 5. ROADMAP & RECOMMENDATIONS ---
    story.append(Paragraph("AI Actionable Recommendations Roadmap", h1))
    
    for i, rec in enumerate(recs):
        clean_rec = rec.replace("*", "")
        # Add a step number
        step_text = f"<b>Step {i+1}:</b> {clean_rec}"
        story.append(Paragraph(step_text, body))
        
    feedback = llm_feedback.get("feedback", "")
    if feedback:
        story.append(Paragraph("Recruiter Summary", h2))
        for p in feedback.split('\n'):
            if p.strip():
                story.append(Paragraph(p.strip().replace("*",""), body))
                
    # --- 6. QR CODE (Portfolio/GitHub) ---
    github_url = None
    if resume_data and 'contact' in resume_data:
        github_url = resume_data['contact'].get('github') or resume_data['contact'].get('linkedin')
        
    if github_url:
        story.append(Spacer(1, 20))
        story.append(Paragraph("Candidate Profile Link", h2))
        
        qrw = QrCodeWidget(github_url)
        b = qrw.getBounds()
        w = b[2]-b[0]
        h = b[3]-b[1]
        d = Drawing(w, h, transform=[1,0,0,1,-b[0],-b[1]])
        d.add(qrw)
        
        qr_t = Table([[d, Paragraph(f"<a href='{github_url}'>{github_url}</a>", body)]], colWidths=[w + 20, 300])
        qr_t.setStyle(TableStyle([('VALIGN', (0,0), (-1,-1), 'MIDDLE')]))
        story.append(qr_t)
        
    # --- HEADER & FOOTER CALLBACK ---
    def header_footer(canvas, doc):
        canvas.saveState()
        
        # We don't draw on the first page (cover page)
        if doc.page > 1:
            # Header
            canvas.setFont('Helvetica-Bold', 10)
            canvas.setFillColor(brand_color)
            canvas.drawString(20*mm, A4[1] - 15*mm, "ATS Resume Analyzer Pro")
            
            canvas.setFont('Helvetica', 9)
            canvas.setFillColor(colors.gray)
            canvas.drawRightString(A4[0] - 20*mm, A4[1] - 15*mm, f"{filename} | Score: {int(overall)}")
            
            canvas.setStrokeColor(colors.lightgrey)
            canvas.line(20*mm, A4[1] - 18*mm, A4[0] - 20*mm, A4[1] - 18*mm)
            
            # Footer
            canvas.line(20*mm, 20*mm, A4[0] - 20*mm, 20*mm)
            canvas.drawString(20*mm, 15*mm, f"Generated on {date_str}")
            canvas.drawRightString(A4[0] - 20*mm, 15*mm, f"Page {doc.page}")
            
        canvas.restoreState()

    doc.build(story, onFirstPage=header_footer, onLaterPages=header_footer)
    return report_path
