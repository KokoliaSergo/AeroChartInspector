import os
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image as RLImage
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors

class ReportGenerator:
    @staticmethod
    def generate_pdf_report(output_path: str, report_info: dict, errors_list: list, evidence_pixmaps=None):
        try:
            doc = SimpleDocTemplate(output_path, pagesize=letter, rightMargin=40, leftMargin=40, topMargin=40, bottomMargin=40)
            story = []
            styles = getSampleStyleSheet()

            title_style = ParagraphStyle(
                'ReportTitle', parent=styles['Heading1'], fontSize=18, textColor=colors.HexColor('#0A192F'), spaceAfter=4
            )
            subtitle_style = ParagraphStyle(
                'ReportSubtitle', parent=styles['Normal'], fontSize=10, textColor=colors.HexColor('#0284C7'), spaceAfter=12
            )
            heading_style = ParagraphStyle(
                'SectionHeading', parent=styles['Heading2'], fontSize=12, textColor=colors.HexColor('#1E293B'), spaceBefore=10, spaceAfter=6
            )
            body_style = ParagraphStyle(
                'ReportBody', parent=styles['Normal'], fontSize=9, textColor=colors.HexColor('#0F172A'), spaceAfter=2, leading=12
            )
            table_header_style = ParagraphStyle(
                'TableHeader', parent=styles['Normal'], fontSize=9, textColor=colors.white, fontName='Helvetica-Bold'
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
            ]))
            story.append(charts_table)
            story.append(Spacer(1, 15))

            # 3. Review summary section
            story.append(Paragraph("Review Summary", heading_style))
            total_errors = len(errors_list)
            critical = sum(1 for e in errors_list if e.severity == "Critical")
            major = sum(1 for e in errors_list if e.severity == "Major")
            minor = sum(1 for e in errors_list if e.severity == "Minor")
            obs = sum(1 for e in errors_list if e.severity == "Observation")

            summary_data = [
                ["Total Errors", "Critical", "Major", "Minor", "Observations"],
                [str(total_errors), str(critical), str(major), str(minor), str(obs)]
            ]
            summary_table = Table(summary_data, colWidths=[108, 108, 108, 108, 108])
            summary_table.setStyle(TableStyle([
                ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#0284C7')),
                ('TEXTCOLOR', (0,0), (-1,0), colors.white),
                ('ALIGN', (0,0), (-1,-1), 'CENTER'),
                ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
                ('BACKGROUND', (0,1), (-1,1), colors.HexColor('#F1F5F9')),
                ('BOX', (0,0), (-1,-1), 1, colors.HexColor('#CBD5E1')),
                ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#CBD5E1')),
                ('PADDING', (0,0), (-1,-1), 6),
            ]))
            story.append(summary_table)
            story.append(Spacer(1, 15))

            # 4. Recorded error(s) log section (including comments)
            story.append(Paragraph("Recorded Error(s) Log", heading_style))
            if errors_list:
                err_table_data = [[
                    Paragraph("ID", table_header_style),
                    Paragraph("Type", table_header_style),
                    Paragraph("Severity", table_header_style),
                    Paragraph("Chart", table_header_style),
                    Paragraph("Description & Comments", table_header_style)
                ]]
                for err in errors_list:
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
                ]))
                story.append(err_table)
            else:
                story.append(Paragraph("No errors recorded during this review session.", body_style))
            
            story.append(Spacer(1, 15))

            # 5. Annotated chart visual evidence section
            temp_img_paths = []
            if evidence_pixmaps:
                story.append(Paragraph("Annotated Chart Visual Evidence", heading_style))
                for idx, pixmap in enumerate(evidence_pixmaps):
                    if pixmap and not pixmap.isNull():
                        temp_img_path = f"temp_evidence_{idx}.png"
                        temp_img_paths.append(temp_img_path)
                        pixmap.save(temp_img_path, "PNG")
                        
                        img = RLImage(temp_img_path, width=500, height=350)
                        img.hAlign = 'CENTER'
                        story.append(Paragraph(f"Evidence #{idx + 1}", body_style))
                        story.append(Spacer(1, 2))
                        story.append(img)
                        story.append(Spacer(1, 10))

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