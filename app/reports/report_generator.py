import os
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image as RLImage, PageBreak, KeepTogether
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

# Register Unicode TrueType font supporting Georgian (Sylfaen is native on Windows)
FONT_NAME = "Helvetica"
FONT_NAME_BOLD = "Helvetica-Bold"

font_candidates = [
    ("Sylfaen", "C:/Windows/Fonts/sylfaen.ttf", None),
    ("ArialUnicode", "C:/Windows/Fonts/arial.ttf", "C:/Windows/Fonts/arialbd.ttf"),
    ("SegoeUI", "C:/Windows/Fonts/segoeui.ttf", "C:/Windows/Fonts/segoeuib.ttf")
]

for name, regular_path, bold_path in font_candidates:
    if os.path.exists(regular_path):
        try:
            pdfmetrics.registerFont(TTFont(name, regular_path))
            FONT_NAME = name
            if bold_path and os.path.exists(bold_path):
                bold_name = f"{name}-Bold"
                pdfmetrics.registerFont(TTFont(bold_name, bold_path))
                FONT_NAME_BOLD = bold_name
            else:
                FONT_NAME_BOLD = name
            break
        except Exception:
            pass

class ReportGenerator:
    @staticmethod
    def generate_pdf_report(output_path: str, report_info: dict, errors_list: list, evidence_pixmaps=None):
        try:
            doc = SimpleDocTemplate(output_path, pagesize=letter, rightMargin=40, leftMargin=40, topMargin=40, bottomMargin=40)
            story = []
            styles = getSampleStyleSheet()

            title_style = ParagraphStyle(
                'ReportTitle', parent=styles['Heading1'], fontName=FONT_NAME_BOLD, fontSize=18, textColor=colors.HexColor('#0A192F'), spaceAfter=4, leading=22
            )
            subtitle_style = ParagraphStyle(
                'ReportSubtitle', parent=styles['Normal'], fontName=FONT_NAME, fontSize=10, textColor=colors.HexColor('#0284C7'), spaceAfter=12, leading=14
            )
            heading_style = ParagraphStyle(
                'SectionHeading', parent=styles['Heading2'], fontName=FONT_NAME_BOLD, fontSize=12, textColor=colors.HexColor('#1E293B'), spaceBefore=10, spaceAfter=6, leading=16
            )
            body_style = ParagraphStyle(
                'ReportBody', parent=styles['Normal'], fontName=FONT_NAME, fontSize=9, textColor=colors.HexColor('#0F172A'), spaceAfter=2, leading=13
            )
            table_header_style = ParagraphStyle(
                'TableHeader', parent=styles['Normal'], fontName=FONT_NAME_BOLD, fontSize=9, textColor=colors.white, leading=13
            )

            story.append(Paragraph("Aeronautical chart validation report", title_style))
            story.append(Paragraph("CHART QUALITY-CONTROL REVIEW REPORT", subtitle_style))
            story.append(Spacer(1, 5))

            reviewer_name = report_info.get('reviewer', 'Quality Controller')
            review_date = report_info.get('date', 'N/A')
            log_sheets = report_info.get('log_sheets', 'N/A')
            checked_charts = report_info.get('checked_charts', [])

            # 1. First main box: Quality Controller, Log Sheet number, Review Date
            meta_data = [
                [Paragraph(f"<b>Quality Controller:</b> {reviewer_name}", body_style),
                 Paragraph(f"<b>Review Date:</b> {review_date}", body_style)],
                [Paragraph(f"<b>Log Sheet No(s):</b> {log_sheets}", body_style),
                 Paragraph("", body_style)]
            ]
            meta_table = Table(meta_data, colWidths=[270, 270])
            meta_table.setStyle(TableStyle([
                ('BACKGROUND', (0,0), (-1,-1), colors.HexColor('#F8FAFC')),
                ('BOX', (0,0), (-1,-1), 1, colors.HexColor('#CBD5E1')),
                ('PADDING', (0,0), (-1,-1), 8),
                ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
                ('SPAN', (0, 1), (1, 1)),
                ('FONTNAME', (0,0), (-1,-1), FONT_NAME),
            ]))
            story.append(meta_table)
            story.append(Spacer(1, 10))

            # 2. Second separate box: List of checked charts
            charts_display_str = "<br/>".join([f"• {c}" for c in checked_charts]) if checked_charts else "• None specified"
            charts_box_data = [
                [Paragraph("<b>List of Checked Charts:</b>", body_style)],
                [Paragraph(charts_display_str, body_style)]
            ]
            charts_table = Table(charts_box_data, colWidths=[540])
            charts_table.setStyle(TableStyle([
                ('BACKGROUND', (0,0), (-1,-1), colors.HexColor('#F1F5F9')),
                ('BOX', (0,0), (-1,-1), 1, colors.HexColor('#CBD5E1')),
                ('PADDING', (0,0), (-1,-1), 8),
                ('VALIGN', (0,0), (-1,-1), 'TOP'),
                ('FONTNAME', (0,0), (-1,-1), FONT_NAME),
            ]))
            story.append(charts_table)
            story.append(Spacer(1, 15))

            # 3. Review summary section
            story.append(Paragraph("Review Summary", heading_style))
            total_errors = sum(1 for e in errors_list if not e.id.startswith("NT-"))
            total_notes = sum(1 for e in errors_list if e.id.startswith("NT-"))
            critical = sum(1 for e in errors_list if e.severity == "Critical")
            major = sum(1 for e in errors_list if e.severity == "Major")
            minor = sum(1 for e in errors_list if e.severity == "Minor")
            obs = sum(1 for e in errors_list if e.severity == "Observation")

            summary_data = [
                ["Total Errors", "Notes", "Critical", "Major", "Minor", "Observations"],
                [str(total_errors), str(total_notes), str(critical), str(major), str(minor), str(obs)]
            ]
            summary_table = Table(summary_data, colWidths=[90, 90, 90, 90, 90, 90])
            summary_table.setStyle(TableStyle([
                ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#0284C7')),
                ('TEXTCOLOR', (0,0), (-1,0), colors.white),
                ('ALIGN', (0,0), (-1,-1), 'CENTER'),
                ('FONTNAME', (0,0), (-1,0), FONT_NAME_BOLD),
                ('BACKGROUND', (0,1), (-1,1), colors.HexColor('#F1F5F9')),
                ('FONTNAME', (0,1), (-1,1), FONT_NAME),
                ('BOX', (0,0), (-1,-1), 1, colors.HexColor('#CBD5E1')),
                ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#CBD5E1')),
                ('PADDING', (0,0), (-1,-1), 6),
            ]))
            story.append(summary_table)
            story.append(Spacer(1, 15))

            # 4. Recorded error(s) and note(s) log section
            errors_only = [e for e in errors_list if not e.id.startswith("NT-")]
            notes_only = [e for e in errors_list if e.id.startswith("NT-")]

            story.append(Paragraph("Recorded Error(s) Log", heading_style))
            if errors_only:
                err_table_data = [[
                    Paragraph("ID", table_header_style),
                    Paragraph("Type", table_header_style),
                    Paragraph("Severity", table_header_style),
                    Paragraph("Chart", table_header_style),
                    Paragraph("Description & Comments", table_header_style)
                ]]
                for err in errors_only:
                    desc_comments = f"<b>Desc:</b> {err.description}"
                    if err.comments:
                        desc_comments += f"<br/><font color='#64748B'><b>Comments:</b> {err.comments}</font>"

                    err_table_data.append([
                        Paragraph(err.id, body_style),
                        Paragraph(err.type, body_style),
                        Paragraph(err.severity, body_style),
                        Paragraph(err.chart, body_style),
                        Paragraph(desc_comments, body_style)
                    ])
                
                err_table = Table(err_table_data, colWidths=[45, 80, 60, 85, 270])
                err_table.setStyle(TableStyle([
                    ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#1E293B')),
                    ('BOTTOMPADDING', (0,0), (-1,0), 6),
                    ('TOPPADDING', (0,0), (-1,0), 6),
                    ('BACKGROUND', (0,1), (-1,-1), colors.white),
                    ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#CBD5E1')),
                    ('VALIGN', (0,0), (-1,-1), 'TOP'),
                    ('PADDING', (0,0), (-1,-1), 5),
                    ('FONTNAME', (0,0), (-1,-1), FONT_NAME),
                ]))
                story.append(err_table)
            else:
                story.append(Paragraph("No errors recorded during this review session.", body_style))

            if notes_only:
                story.append(Spacer(1, 12))
                story.append(Paragraph("Chart Note(s) Log", heading_style))
                note_table_data = [[
                    Paragraph("ID", table_header_style),
                    Paragraph("Type", table_header_style),
                    Paragraph("Severity", table_header_style),
                    Paragraph("Chart", table_header_style),
                    Paragraph("Note Content", table_header_style)
                ]]
                for nt in notes_only:
                    note_table_data.append([
                        Paragraph(nt.id, body_style),
                        Paragraph("N/A", body_style),
                        Paragraph("N/A", body_style),
                        Paragraph(nt.chart, body_style),
                        Paragraph(nt.description, body_style)
                    ])
                
                note_table = Table(note_table_data, colWidths=[45, 80, 60, 85, 270])
                note_table.setStyle(TableStyle([
                    ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#0284C7')),
                    ('BOTTOMPADDING', (0,0), (-1,0), 6),
                    ('TOPPADDING', (0,0), (-1,0), 6),
                    ('BACKGROUND', (0,1), (-1,-1), colors.HexColor('#F8FAFC')),
                    ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#CBD5E1')),
                    ('VALIGN', (0,0), (-1,-1), 'TOP'),
                    ('PADDING', (0,0), (-1,-1), 5),
                    ('FONTNAME', (0,0), (-1,-1), FONT_NAME),
                ]))
                story.append(note_table)
            
            story.append(Spacer(1, 15))

            # 5. Annotated chart visual evidence section (Full Page per Screenshot stuck with Evidence#)
            temp_img_paths = []
            if evidence_pixmaps:
                for idx, pixmap in enumerate(evidence_pixmaps):
                    if pixmap and not pixmap.isNull():
                        temp_img_path = f"temp_evidence_{idx}.png"
                        temp_img_paths.append(temp_img_path)
                        pixmap.save(temp_img_path, "PNG")
                        
                        # Full page per screenshot
                        story.append(PageBreak())
                        
                        # Calculate proportional dimensions to fill whole page (letter: 612x792, margins 40)
                        max_w = 532.0
                        max_h = 665.0
                        aspect = pixmap.width() / max(1, pixmap.height())
                        
                        if aspect > (max_w / max_h):
                            target_w = max_w
                            target_h = max_w / aspect
                        else:
                            target_h = max_h
                            target_w = max_h * aspect
                            
                        img = RLImage(temp_img_path, width=target_w, height=target_h)
                        img.hAlign = 'CENTER'
                        
                        evidence_title = Paragraph(f"<b>Evidence #{idx + 1}</b>", heading_style)
                        
                        # Keep heading and image together on the same page
                        story.append(KeepTogether([
                            evidence_title,
                            Spacer(1, 6),
                            img
                        ]))

            doc.build(story)
            
            for path in temp_img_paths:
                if os.path.exists(path):
                    try:
                        os.remove(path)
                    except:
                        pass

            return True, ""
        except Exception as e:
            return False, str(e)