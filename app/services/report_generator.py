import io
import csv
from datetime import datetime
from typing import List, Dict, Any

from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
    HRFlowable,
    KeepTogether
)

class ReportGenerator:
    """Service to export candidates as CSV and generate executive PDF screening reports."""

    @staticmethod
    def generate_shortlist_csv(shortlist_name: str, job_title: str, candidates: List[Dict[str, Any]]) -> str:
        """Create CSV format string of candidates in a shortlist."""
        output = io.StringIO()
        writer = csv.writer(output)
        
        # Header info
        writer.writerow(["TalentMatch AI - Candidate Shortlist Export"])
        writer.writerow(["Shortlist Name", shortlist_name])
        writer.writerow(["Job Title", job_title])
        writer.writerow(["Generated At", datetime.now().strftime("%Y-%m-%d %H:%M:%S")])
        writer.writerow([])
        
        # Table headers
        writer.writerow([
            "Candidate ID",
            "Full Name",
            "Email Address",
            "Phone Number",
            "Match Score (%)",
            "Match Tier",
            "Experience (Years)",
            "Education Level",
            "Current Status",
            "Recruiter Notes"
        ])

        for c in candidates:
            writer.writerow([
                c.get("id"),
                c.get("name"),
                c.get("email") or "N/A",
                c.get("phone") or "N/A",
                c.get("match_score", "N/A"),
                c.get("match_tier", "N/A"),
                c.get("experience_years", 0.0),
                c.get("education", "Unavailable"),
                c.get("status", "Shortlisted"),
                c.get("notes", "")
            ])

        return output.getvalue()

    @staticmethod
    def generate_screening_pdf(
        job_info: Dict[str, Any],
        ranked_candidates: List[Dict[str, Any]],
        filter_summary: str = "All Processed Candidates"
    ) -> bytes:
        """Build professional multi-page executive PDF screening report using ReportLab."""
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(
            buffer,
            pagesize=letter,
            rightMargin=40,
            leftMargin=40,
            topMargin=40,
            bottomMargin=40
        )

        styles = getSampleStyleSheet()
        
        # Custom palette & typography
        title_style = ParagraphStyle(
            'DocTitle',
            parent=styles['Normal'],
            fontName='Helvetica-Bold',
            fontSize=22,
            leading=26,
            textColor=colors.HexColor('#0f172a')
        )
        subtitle_style = ParagraphStyle(
            'DocSubtitle',
            parent=styles['Normal'],
            fontName='Helvetica',
            fontSize=11,
            leading=15,
            textColor=colors.HexColor('#475569')
        )
        section_style = ParagraphStyle(
            'SectionHeader',
            parent=styles['Normal'],
            fontName='Helvetica-Bold',
            fontSize=14,
            leading=18,
            textColor=colors.HexColor('#1e293b'),
            spaceBefore=14,
            spaceAfter=6
        )
        cell_bold = ParagraphStyle(
            'CellBold',
            parent=styles['Normal'],
            fontName='Helvetica-Bold',
            fontSize=9,
            leading=12,
            textColor=colors.HexColor('#0f172a')
        )
        cell_regular = ParagraphStyle(
            'CellRegular',
            parent=styles['Normal'],
            fontName='Helvetica',
            fontSize=9,
            leading=12,
            textColor=colors.HexColor('#334155')
        )

        elements = []

        # 1. Header Banner
        elements.append(Paragraph("TALENTMATCH AI", ParagraphStyle('Logo', fontName='Helvetica-Bold', fontSize=10, textColor=colors.HexColor('#4f46e5'))))
        elements.append(Paragraph("Candidate Screening & Match Report", title_style))
        elements.append(Spacer(1, 4))
        elements.append(Paragraph(f"Generated on {datetime.now().strftime('%B %d, %Y at %H:%M')} | Scope: {filter_summary}", subtitle_style))
        elements.append(Spacer(1, 10))
        elements.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor('#e2e8f0'), spaceAfter=14))

        # 2. Job Overview Card
        job_data = [
            [
                Paragraph("<b>Job Title:</b> " + str(job_info.get("title", "N/A")), cell_regular),
                Paragraph("<b>Department:</b> " + str(job_info.get("department", "General")), cell_regular)
            ],
            [
                Paragraph("<b>Required Exp:</b> " + f"{job_info.get('min_experience_years', 0.0)} years", cell_regular),
                Paragraph("<b>Required Degree:</b> " + str(job_info.get("required_education_level", "Bachelor")), cell_regular)
            ],
            [
                Paragraph("<b>Location:</b> " + str(job_info.get("location", "Remote")), cell_regular),
                Paragraph("<b>Employment Type:</b> " + str(job_info.get("employment_type", "Full-time")), cell_regular)
            ]
        ]
        job_table = Table(job_data, colWidths=[260, 260])
        job_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#f8fafc')),
            ('BOX', (0, 0), (-1, -1), 1, colors.HexColor('#cbd5e1')),
            ('INNERGRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#e2e8f0')),
            ('TOPPADDING', (0, 0), (-1, -1), 6),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
            ('LEFTPADDING', (0, 0), (-1, -1), 10),
            ('RIGHTPADDING', (0, 0), (-1, -1), 10),
        ]))
        elements.append(job_table)
        elements.append(Spacer(1, 15))

        # 3. Candidate Rankings Table
        elements.append(Paragraph("Ranked Candidates Overview", section_style))
        
        table_rows = [
            [
                Paragraph("<b>Rank</b>", cell_bold),
                Paragraph("<b>Candidate Name</b>", cell_bold),
                Paragraph("<b>Match %</b>", cell_bold),
                Paragraph("<b>Tier</b>", cell_bold),
                Paragraph("<b>Experience</b>", cell_bold),
                Paragraph("<b>Education</b>", cell_bold),
                Paragraph("<b>Status</b>", cell_bold),
            ]
        ]

        for idx, c in enumerate(ranked_candidates[:25], start=1):
            score = c.get("overall_score", 0.0)
            tier = c.get("match_tier", "Low Match")
            tier_color = "#10b981" if score >= 90 else "#6366f1" if score >= 75 else "#f59e0b" if score >= 60 else "#64748b"
            
            table_rows.append([
                Paragraph(f"#{idx}", cell_regular),
                Paragraph(f"<b>{c.get('candidate_name', 'Candidate')}</b>", cell_regular),
                Paragraph(f"<b>{score:.1f}%</b>", ParagraphStyle('ScoreCol', fontName='Helvetica-Bold', fontSize=9, textColor=colors.HexColor(tier_color))),
                Paragraph(f"<font color='{tier_color}'>{tier}</font>", cell_regular),
                Paragraph(f"{c.get('total_experience_years', 0.0):.1f} yrs", cell_regular),
                Paragraph(str(c.get('highest_education_level', 'Unavailable')), cell_regular),
                Paragraph(str(c.get('current_status', 'New')), cell_regular),
            ])

        if len(table_rows) > 1:
            rank_table = Table(table_rows, colWidths=[35, 140, 55, 85, 65, 85, 65])
            rank_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#f1f5f9')),
                ('BOX', (0, 0), (-1, -1), 1, colors.HexColor('#cbd5e1')),
                ('INNERGRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#e2e8f0')),
                ('TOPPADDING', (0, 0), (-1, -1), 5),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
                ('ALIGN', (0, 0), (0, -1), 'CENTER'),
                ('ALIGN', (2, 0), (2, -1), 'CENTER'),
            ]))
            elements.append(rank_table)
        else:
            elements.append(Paragraph("No candidates evaluated for this role yet.", cell_regular))

        elements.append(Spacer(1, 20))

        # 4. Detailed Breakdown of Top Candidates (Top 3)
        if ranked_candidates:
            elements.append(Paragraph("Top Candidates Detailed Alignment", section_style))
            for top_c in ranked_candidates[:3]:
                cand_box = []
                cand_box.append(Paragraph(
                    f"<b>{top_c.get('candidate_name')}</b> – Match Score: <b>{top_c.get('overall_score', 0):.1f}%</b> ({top_c.get('match_tier')})",
                    cell_bold
                ))
                cand_box.append(Spacer(1, 3))
                
                matched_skills = top_c.get("matched_required_skills", [])
                missing_skills = top_c.get("missing_required_skills", [])
                
                m_text = ", ".join(matched_skills[:8]) if matched_skills else "None explicitly detected"
                g_text = ", ".join(missing_skills[:8]) if missing_skills else "None identified"
                
                cand_box.append(Paragraph(f"• <b>Matched Required Skills:</b> {m_text}", cell_regular))
                cand_box.append(Paragraph(f"• <b>Missing Skills / Gaps:</b> {g_text}", cell_regular))
                cand_box.append(Paragraph(f"• <b>Experience:</b> {top_c.get('total_experience_years', 0.0):.1f} years | <b>Education:</b> {top_c.get('highest_education_level')}", cell_regular))
                cand_box.append(Spacer(1, 8))

                elements.append(KeepTogether(cand_box))

        # Confidentiality footer
        elements.append(Spacer(1, 20))
        elements.append(HRFlowable(width="100%", thickness=0.5, color=colors.HexColor('#cbd5e1'), spaceAfter=8))
        elements.append(Paragraph(
            "Confidential & Proprietary. TalentMatch AI scoring is an assistive decision-support indicator, "
            "evaluated without regard to protected demographic characteristics. Hiring decisions remain the responsibility of human recruiters.",
            ParagraphStyle('Footer', fontName='Helvetica', fontSize=7.5, leading=10, textColor=colors.HexColor('#94a3b8'), alignment=1)
        ))

        doc.build(elements)
        buffer.seek(0)
        return buffer.getvalue()

report_generator = ReportGenerator()
