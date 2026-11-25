import docx
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.oxml import OxmlElement, parse_xml
from docx.oxml.ns import nsdecls, qn
import shutil
import os

def create_manual_v1_1():
    print("Loading Manual_v1.0.docx...")
    doc = docx.Document('Manual_v1.0.docx')

    # 1. Update Title and Version on Cover Page
    # P7 is "User Manual & Operational Guide — Version 1.0"
    for r in doc.paragraphs[7].runs:
        if "Version 1.0" in r.text:
            r.text = r.text.replace("Version 1.0", "Version 1.1")
        elif "1.0" in r.text:
            r.text = r.text.replace("1.0", "1.1")
    if "1.1" not in doc.paragraphs[7].text:
        doc.paragraphs[7].text = "User Manual & Operational Guide — Version 1.1"

    # P39 is "Application is Designed and Developed by: Sergo Kokolia  |  Version 1.0 (Official Release)"
    for r in doc.paragraphs[39].runs:
        if "Version 1.0" in r.text:
            r.text = r.text.replace("Version 1.0 (Official Release)", "Version 1.1 (Updated Release)")
        elif "1.0" in r.text:
            r.text = r.text.replace("1.0", "1.1")
    if "1.1" not in doc.paragraphs[39].text:
        doc.paragraphs[39].text = "Application is Designed and Developed by: Sergo Kokolia  |  Version 1.1 (Updated Release)"

    # 2. Update Chapter 1 System Overview
    # P61: Mention v1.1 precision rotation, notes, in-situ error pinning, and report enhancements
    doc.paragraphs[61].text = (
        "Designed and developed by Sergo Kokolia, the application's core operational mandate is to streamline the visual "
        "verification of updated aeronautical charts against legacy baseline charts. Rather than relying on manual, side-by-side "
        "paper inspections or general-purpose graphic viewers, the software enables quality controllers to overlay high-resolution "
        "digital chart revisions, perform precision spatial registration and multi-angle micro-rotations, highlight visual discrepancies, "
        "place interactive chart notes, log categorized safety errors in-situ directly on chart coordinates, and generate standardized, "
        "multi-page PDF validation reports with full international Unicode and Georgian character support."
    )

    # 3. Update Chapter 2 Interface Reference & Button Guide
    # 2.1 Import Tab
    doc.paragraphs[66].text = (
        "The Import tab manages bulk uploading of PDF charts and pairs each Updated chart with its corresponding Old baseline chart. "
        "Opening an updated chart automatically populates the List of Checked Charts in the Report tab for streamlined tracking."
    )

    # 2.2 Chart Comparison Tab
    # Update P80 (Browse Updated)
    doc.paragraphs[80].text = (
        "Browse... (Updated chart): Selects a single Updated PDF chart directly from disk. If the selected file was already paired "
        "in the Import tab, the corresponding Old chart is automatically mapped and loaded. Loading an updated chart also automatically "
        "registers it in the List of Checked Charts in the Report tab."
    )

    # Update P86, P87, P88 (Drag Mode & Rotation)
    doc.paragraphs[86].text = "Drag Mode: OFF / ON: Toggles manual chart alignment and rotation mode."
    doc.paragraphs[87].text = (
        "When ON (blue button, toggled from green), interactive canvas controls are enabled: Left-click dragging on the canvas shifts "
        "the spatial position of the Old chart relative to the Updated chart to align shifted borders or coordinate grids. "
        "Right-click dragging dynamically rotates the Old chart on the fly. Alignment and rotation offsets remain strictly locked "
        "across all zoom magnifications and flicker cycles."
    )

    # Update P89, P90 (Flicker Mode & Yellow/Green styling)
    doc.paragraphs[89].text = (
        "Start Flicker / Pause Flicker: Starts an automated timer that alternates visibility between the Updated chart and the Old chart. "
        "Any changes (moved obstacles, revised altitudes, text shifts, or missing symbols) immediately \"pop\" visually. "
        "The button features dynamic color-coded state indication: styled in Yellow (#F59E0B) when Idle or Paused, and turns vibrant Green "
        "(#10B981) while actively running. Starting flicker automatically turns off Drag Mode."
    )

    # Update P93 (Reset Alignment & Rotation Buttons)
    doc.paragraphs[93].text = (
        "Reset Alignment: Located immediately next to the Drag Mode button. Snaps a manually dragged and rotated Old chart back to its "
        "original centered origin (0, 0) and 0.0° angle.\n"
        "↺ -1° / ↻ +1° / ⟳ 90° (Rotation Buttons): Precision micro-rotation controls. Clicking ↺ -1° rotates the Old chart 1.0° counter-clockwise, "
        "↻ +1° rotates 1.0° clockwise, and ⟳ 90° rotates 90.0° clockwise. The active angular offset is displayed live via the Angle: X.X° readout."
    )

    # Update P94, P95 (Draw Highlight & Clear Drawings repositioning and preserving notes/errors)
    doc.paragraphs[94].text = (
        "Draw Highlight: OFF / ON: Toggles freehand annotation mode. When ON, the cursor changes to a crosshair, allowing you to draw "
        "crimson highlight circles, arrows, or underlines directly over chart discrepancies."
    )
    doc.paragraphs[95].text = (
        "Clear Drawings: Placed immediately adjacent to the Draw Highlight button on the toolbar. Removes all freehand highlight strokes "
        "currently drawn on the canvas while strictly preserving all Chart Notes and pinned Error Discrepancy markers.\n"
        "Add Note: OFF / ON: Toggles interactive chart note mode. When active, clicking anywhere on the chart canvas opens a dedicated text editor dialog "
        "(with automatic word-wrapping fitting the window) to place an aeronautical callout pin, dashed leader line, ID badge (📝 NT-00x), and yellow callout box. "
        "Notes feature intelligent boundary clamping and auto-flipping, ensuring the note bubble never extends off chart edges or screenshot boundaries. "
        "Notes can be dragged to reposition, edited via double-click or right-click menu, and deleted individually via Remove Note. Notes automatically sync with the Errors tab and final PDF report.\n"
        "Record Error: OFF / ON: Toggles in-situ discrepancy pinning. Clicking directly on a chart error location launches the Record New Error dialog pre-filled "
        "with the next sequential Error ID (ERR-00x) and chart name. Pinned crimson discrepancy badges (⚠️ ERR-00x with crosshair pin) appear directly at coordinates, "
        "can be moved via click-and-drag, edited in-place, and synchronized across tabs.\n"
        "Floating Overlay Control Panel (Blue Theme): Semi-transparent quick-access panel positioned on the left edge of the chart canvas featuring "
        "monochrome technical glyphs: ✥ (Drag/Rotate Mode), ↻ (Rotate 90°), ✎ (Draw Highlight), 🗈 (Add Note), ⨂ (Record Error), and ⌫ (Clear Drawings)."
    )

    # Update P96 (Save Annotated Chart to Report)
    doc.paragraphs[96].text = (
        "Save Annotated Chart to Report: Captures a high-resolution snapshot strictly of the Updated chart, freehand highlights, chart notes, and "
        "pinned error badges (completely ignoring the Old chart, opacity overlay, and viewport margins). Appends the clean image to the visual "
        "evidence queue for the PDF report. Multiple snapshots can be saved per session."
    )

    # 2.3 Errors Tab (Discrepancy Logging)
    # Update P107, P108, P113, P114
    doc.paragraphs[107].text = (
        "Main Tab Buttons & Table Controls:\n"
        "ⓘ Severity Guide Button: Located at the top of the Errors tab. Displays an interactive reference guide explaining the safety criteria "
        "for Critical, Major, Minor, and Observation severities upon mouse hover or click.\n"
        "Table Column Sorting: Clicking any column header (including ID) automatically sorts the discrepancies table. All edit and delete actions "
        "securely track entries by their unique identifier, preventing row index mismatch when sorted.\n"
        "Chart Notes Integration: Notes placed on the chart appear in the discrepancies table with ID NT-00x, Type N/A, Severity N/A, and Comments 'Chart Note'. "
        "Editing or deleting a note in the table immediately synchronizes with the chart canvas."
    )
    doc.paragraphs[112].text = (
        "Error ID: Auto-generated sequential identifier (e.g., ERR-001, ERR-002, NT-001). Features robust collision-free logic that gracefully "
        "handles deleted errors and prevents duplicate ID generation. Label is perfectly aligned with the ID badge."
    )
    doc.paragraphs[113].text = (
        "Error Type Dropdown: Categorizes the finding into one of 19 standardized aeronautical categories: Text, Altitude, Frequency, Navaid, "
        "Course / Bearing, Distance, Speed, Procedure, Route, Waypoint, Runway, Aerodrome, Obstacle, Terrain, Symbol, Geometry / Position, "
        "Missing Information, Formatting / Presentation, or Other (redundant 'Incorrect Information' removed for standard compliance)."
    )
    doc.paragraphs[114].text = "Severity Dropdown: Assigns safety impact (Critical, Major, Minor, Observation). Table column header displays clean 'Severity' label."

    # 2.4 Report Tab (Summary & PDF Generation)
    # Update P123, P125, P126, P127, P128-P133
    doc.paragraphs[123].text = (
        "Validation Date Field & Select Date... Button: Displays the validation date in standardized DD-MM-YYYY format. Clicking Select Date... "
        "opens an interactive calendar configured with weeks starting on Monday, clear active date highlighting, and hidden week numbers."
    )
    doc.paragraphs[125].text = (
        "List of Checked Charts: Automatically populated with charts loaded in the Comparison tab, and fully editable. Users can manually add charts "
        "via Add Chart(s)... or delete highlighted entries via Remove Selected Chart. The list box features crisp container borders with buttons "
        "neatly pinned to the bottom of the section."
    )
    doc.paragraphs[126].text = (
        "Captured Visual Evidence Management: Features an enlarged thumbnail list displaying every saved annotated chart screenshot. "
        "Users can preview full-size screenshots via Preview Selected Evidence or remove unneeded captures prior to compilation via Remove Selected Evidence. "
        "Includes a dynamic status counter ('X evidence(s) available for report')."
    )
    doc.paragraphs[127].text = (
        "Validation Review Summary Box: Formatted container that cleanly fits the section without text clipping or truncated counters, displaying "
        "active session details, total checked charts, error metrics, and saved annotation counts."
    )
    doc.paragraphs[128].text = (
        "Generate PDF Report Button: Styled in prominent Emerald Green (#10B981). Automatically prompts to save the report using the standardized naming "
        "convention LogSheetNumber_NameSurname.pdf (e.g., 234_SergoKokolia.pdf). The compiled PDF report includes full international Unicode and Georgian "
        "language support and is structured in six sequential sections:"
    )
    doc.paragraphs[129].text = "1. Main Metadata Box: Quality Controller full name, Validation Date (DD-MM-YYYY), and Log Sheet Number(s)."
    doc.paragraphs[130].text = "2. Checked Charts Box: Bordered section listing all verified aeronautical charts."
    doc.paragraphs[131].text = "3. Review Summary Table: Standardized 5-column error summary (Total Errors, Critical, Major, Minor, Observations)."
    doc.paragraphs[132].text = "4. Recorded Error(s) Log Table: Detailed discrepancy log including ID, Type, Severity, Chart, Description, and Comments."
    doc.paragraphs[133].text = (
        "5. Chart Note(s) Log Table: Dedicated table listing all chart notes (NT-00x) with description and chart reference.\n"
        "6. Annotated Chart Visual Evidence: Full-page presentation per saved screenshot, proportionally scaled to fill page margins, firmly locked "
        "with its Evidence #X heading."
    )

    # 4. Update Chapter 3 End-to-End Quality Control Process
    # Step 2 (P144, P145)
    doc.paragraphs[144].text = (
        "If the chart coordinate grids or borders are slightly offset between editions, click Drag Mode: OFF (turning it ON, blue). "
        "Left-click and drag on the canvas to shift spatial position, or Right-click and drag to rotate the Old chart. "
        "Alternatively, use the ↺ -1°, ↻ +1°, or ⟳ 90° buttons for precise angular alignment, monitoring the live Angle: X.X° readout. "
        "Click Reset Alignment if you need to snap back to origin. Click Drag Mode again to lock alignment."
    )
    doc.paragraphs[145].text = (
        "Select an interval (e.g., 0.5s or 1.0s) and click Start Flicker (button turns Green while active). "
        "Click Pause Flicker (button reverts to Yellow) when inspecting details."
    )

    # Step 3 (P150, P151, P152)
    doc.paragraphs[150].text = (
        "Click Draw Highlight: OFF (turning it ON) to draw red highlight circles or arrows over discrepancies, or click Add Note: OFF (or floating 🗈) "
        "to type an explanatory text annotation directly onto the chart with an auto-clamped, draggable aeronautical callout pin."
    )
    doc.paragraphs[151].text = (
        "Click Save Annotated Chart to Report to capture an evidence screenshot containing only the updated chart, drawings, notes, and error badges."
    )
    doc.paragraphs[152].text = (
        "Click Clear Drawings (located directly next to Draw Highlight) to clear drawing strokes while safely keeping your notes and error markers intact."
    )

    # Step 4 (P154, P155, P157, P160)
    doc.paragraphs[154].text = (
        "Discrepancies can be logged either by clicking Add Error in the Errors tab, or directly from the Chart Comparison tab by clicking Record Error: OFF "
        "(or floating ⨂) and clicking the error location on the map to pin an interactive ⚠️ ERR-00x badge."
    )
    doc.paragraphs[155].text = (
        "Hover over Severity or click ⓘ Severity Guide to review safety impact definitions. Select the appropriate Error Type and Severity."
    )
    doc.paragraphs[157].text = "The system provides 19 domain-specific categories covering all aspects of aeronautical publication:"
    doc.paragraphs[160].text = "Cartographic Drafting & Standards: Text, Symbol, Geometry / Position, Missing Information, Formatting / Presentation, Other"

    # Step 5 (P166, P167, P169)
    doc.paragraphs[166].text = (
        "Enter your full name in Name and Surname, choose the Validation Date via Select Date... (Monday-first calendar in DD-MM-YYYY format), "
        "and enter the Log Sheet Number(s)."
    )
    doc.paragraphs[167].text = (
        "Review the List of Checked Charts (automatically populated from comparison sessions) and use Add Chart(s)... or Remove Selected Chart as needed. "
        "In Captured Visual Evidence, preview screenshots or remove unneeded ones."
    )
    doc.paragraphs[169].text = (
        "Click Generate PDF Report (green button). The system automatically formats the output filename as LogSheetNumber_NameSurname.pdf "
        "and generates the official QC document with full Georgian and multi-language Unicode fidelity."
    )

    # 5. Update Chapter 5 Packaging & Build Automation
    doc.paragraphs[173].text = (
        "AeroChart Inspector Version 1.1 is engineered as a zero-dependency, standalone desktop utility for Microsoft Windows. "
        "The distribution includes an automated build pipeline that compiles the full application into a single portable executable."
    )

    # 6. Update Table 1 (Chapter 4 Control and Functions Table)
    table1 = doc.tables[1]
    
    # We will build an expanded, comprehensive set of rows for Table 1
    new_table_rows = [
        # Import Tab
        ["Import Tab", "Upload Updated PDFs", "Button", "Opens a file browser to select one or more revised PDF charts.", "Click to select and upload revised PDF charts to the Updated Charts list."],
        ["Import Tab", "Upload Old PDFs", "Button", "Opens a file browser to select one or more baseline/legacy PDF charts.", "Click to select and upload baseline/legacy PDF charts to the Old Charts list."],
        ["Import Tab", "Updated / Old Dropdown Menus", "Dropdown", "Allow manual selection of a specific updated chart and its corresponding old chart for pairing.", "Select an updated chart and a corresponding old chart from the respective dropdown menus."],
        ["Import Tab", "Link Selected Pair", "Button", "Pairs the currently selected Updated and Old charts from the dropdown menus.", "Click after selecting a pair from the dropdowns to add the connection to the Active Mappings List."],
        ["Import Tab", "Active Mappings List", "Interactive Box", "Displays all linked chart pairs.", "Double-clicking any row automatically loads both charts into the Chart Comparison tab."],
        ["Import Tab", "Remove Selected Mapping", "Button", "Deletes the highlighted chart pair from the Active Mappings List.", "Highlight a chart pair in the Active Mappings List and click to delete the mapping without deleting the uploaded files."],
        
        # Chart Comparison Tab - File Bar
        ["Chart Comparison Tab", "Browse... (Updated chart)", "Button", "Selects a single Updated PDF chart directly from file. Auto-maps paired old chart and auto-populates checked charts list.", "Click to select an Updated PDF chart. If previously paired, the corresponding Old chart is automatically mapped and loaded."],
        ["Chart Comparison Tab", "Browse... (Old chart)", "Button", "Selects a single Old PDF chart from file.", "Click to select an Old PDF chart directly from disk."],
        ["Chart Comparison Tab", "Load Charts", "Button", "Renders high-resolution views of both charts onto the canvas and unlocks comparison toolbar and floating controls.", "Click after both an Updated and Old chart are selected."],
        ["Chart Comparison Tab", "Reset Session", "Button", "Clears currently loaded charts, drawings, and saved annotations from the comparison view.", "Click to clear the current comparison session while keeping previously logged entries in the Errors tab intact."],
        
        # Chart Comparison Tab - Toolbar
        ["Chart Comparison Tab", "Drag Mode: OFF / ON", "Button", "Toggles manual chart alignment and rotation mode. Green when OFF, turns blue when ON.", "When ON (blue), Left-click drag to pan the Old chart; Right-click drag to rotate the Old chart."],
        ["Chart Comparison Tab", "Reset Alignment", "Button", "Snaps a manually panned and rotated Old chart back to its centered origin (0, 0) and 0.0° angle.", "Click to instantly reset positioning and angular offset back to default. Located right next to Drag Mode."],
        ["Chart Comparison Tab", "↺ -1° / ↻ +1°", "Button", "Rotates the Old chart 1.0° counter-clockwise or clockwise for fine precision alignment.", "Click ↺ -1° or ↻ +1° to micro-adjust rotation angle."],
        ["Chart Comparison Tab", "⟳ 90°", "Button", "Rotates the Old chart 90.0° clockwise.", "Click to quickly change chart orientation by 90 degrees."],
        ["Chart Comparison Tab", "Angle: X.X°", "Label", "Displays real-time angular rotation offset of the Old chart.", "Monitored during rotation adjustments."],
        ["Chart Comparison Tab", "Start Flicker / Pause Flicker", "Button", "Starts or pauses automated visibility alternation between charts. Yellow when idle/paused, turns green while running.", "Click to start flickering (automatically turns off Drag Mode); click again to pause."],
        ["Chart Comparison Tab", "Interval", "Dropdown", "Controls how fast the view switches between charts during Flicker mode.", "Select a time interval (0.2s, 0.5s, 1.0s, 2.0s, or 3.0s) from the dropdown list."],
        ["Chart Comparison Tab", "Show Updated", "Button", "Pauses flicker and displays 100% of the Updated chart only.", "Click to pause flicker and view only the Updated chart."],
        ["Chart Comparison Tab", "Show Old", "Button", "Pauses flicker and displays 100% of the Old chart only.", "Click to pause flicker and view only the Old chart."],
        ["Chart Comparison Tab", "Draw Highlight: OFF / ON", "Button", "Toggles freehand drawing mode.", "When ON, drag the crosshair cursor to draw red highlight circles, arrows, or underlines on the canvas."],
        ["Chart Comparison Tab", "Clear Drawings", "Button", "Removes all freehand drawing strokes on the canvas while strictly preserving all Chart Notes and Discrepancy Error markers.", "Click to erase freehand highlight strokes. Placed right next to Draw Highlight."],
        ["Chart Comparison Tab", "Add Note: OFF / ON", "Button", "Toggles interactive chart note placement mode.", "When ON, click anywhere on the chart canvas to enter note text via a dedicated auto-wrapping dialog. Callout includes smart boundary clamping and drag-and-drop movement."],
        ["Chart Comparison Tab", "Remove Note", "Button", "Removes the currently selected note, or prompts to select a note to remove one by one.", "Click to delete selected note from the canvas and the Errors tab log."],
        ["Chart Comparison Tab", "Record Error: OFF / ON", "Button", "Toggles direct in-situ discrepancy pinning on the chart.", "When ON, click directly on an error location on the chart to open Record New Error and pin a crimson ⚠️ ERR-00x badge at the coordinates."],
        ["Chart Comparison Tab", "Save Annotated Chart to Report", "Button", "Captures an evidence snapshot strictly of the Updated chart, drawing strokes, notes, and error markers (ignoring old chart and margins).", "Click to save an annotated screenshot to the report evidence queue (enabled once annotations/notes/errors exist)."],
        
        # Chart Comparison Tab - Floating Panel & Navigation
        ["Chart Comparison Tab", "Floating Overlay Panel (✥, ↻, ✎, 🗈, ⨂, ⌫)", "Overlay Buttons", "Semi-transparent quick-access buttons on the left canvas edge (Drag, Rotate 90°, Draw, Add Note, Record Error, Clear Drawings).", "Click any floating button for rapid tool switching without moving to the top toolbar."],
        ["Chart Comparison Tab", "Overlay Balance (Updated/Old)", "Slider", "Adjusts the transparency (alpha opacity) of the Old chart from 0% to 100% when viewing both charts simultaneously.", "Slide to adjust the relative opacity between the Updated and Old charts."],
        ["Chart Comparison Tab", "- (Zoom Out) & + (Zoom In)", "Button", "Decreases or increases chart magnification by 20% per click (25% to 500% range).", "Click - to zoom out or + to zoom in, or scroll the mouse wheel directly over the canvas."],
        ["Chart Comparison Tab", "Fit", "Button", "Resets the zoom level back to 100%.", "Click to reset magnification back to 100%."],
        ["Chart Comparison Tab", "Vertical & Horizontal Scroll Bars", "Scroll Bar", "Scales with zoomed chart dimensions to enable panning across high-zoom charts.", "Drag the scroll bars to pan to the extreme edges of the chart."],
        
        # Errors Tab
        ["Errors Tab", "ⓘ Severity Guide", "Button", "Displays an interactive popup guide explaining safety severity definitions and regulatory criteria.", "Hover mouse over the button or table Severity header to view full severity guidelines."],
        ["Errors Tab", "Add Error", "Button", "Opens the Record New Error pop-up dialog to log a discrepancy.", "Click to launch the Record New Error pop-up dialog."],
        ["Errors Tab", "Edit Selected Error", "Button", "Opens the edit dialog pre-filled with the highlighted row details to update severity, description, or comments.", "Highlight an error row and click to edit."],
        ["Errors Tab", "Delete Selected Error", "Button", "Permanently deletes the highlighted error row from the log after confirmation.", "Highlight an error row and click to delete it."],
        ["Errors Tab", "Table Header Sort", "Header Control", "Enables sorting of discrepancies table by any column including sequential ID (ERR-001, ERR-002, NT-001, etc.).", "Click on any column header to sort table rows."],
        ["Errors Tab (Pop-Up Dialog)", "Error ID", "Text Field", "Displays an auto-generated, collision-free sequential identifier (e.g., ERR-001, ERR-002).", "Automatically generated by the system, gracefully handling deleted IDs."],
        ["Errors Tab (Pop-Up Dialog)", "Error Type", "Dropdown", "Categorizes the finding into specific cartographic types.", "Select from 19 standardized aeronautical categories (Text, Altitude, Frequency, Navaid, Course / Bearing, Distance, Speed, Procedure, Route, Waypoint, Runway, Aerodrome, Obstacle, Terrain, Symbol, Geometry / Position, Missing Information, Formatting / Presentation, or Other)."],
        ["Errors Tab (Pop-Up Dialog)", "Severity", "Dropdown", "Assigns safety impact level to the error.", "Select a severity level from the dropdown menu (Critical, Major, Minor, or Observation)."],
        ["Errors Tab (Pop-Up Dialog)", "Affected Chart", "Text Field", "Specifies the chart name affected by the discrepancy.", "Pre-populated with the currently loaded Updated chart name, or edit manually to specify any chart name."],
        ["Errors Tab (Pop-Up Dialog)", "Description", "Text Box", "Required field describing the exact nature of the cartographic error.", "Type the detailed error description into the text box."],
        ["Errors Tab (Pop-Up Dialog)", "Comments", "Text Box", "Optional field for corrective instructions, source document references, or reviewer notes.", "Type optional notes or references into the text box (appears under the description in the PDF report)."],
        
        # Report Tab
        ["Report Tab", "Name and Surname", "Text Field", "Mandatory text input for the Quality Controller's full name.", "Enter the full name of the Quality Controller into the text field."],
        ["Report Tab", "Validation Date & Select Date...", "Text Field / Button", "Displays validation date in DD-MM-YYYY format and opens an interactive calendar.", "Click Select Date... to open calendar starting on Monday, with selected date indicator and hidden week numbers."],
        ["Report Tab", "Log Sheet Number(s)", "Text Field", "Text input for recording internal QC tracking or log sheet numbers.", "Enter the internal QC tracking or log sheet numbers into the text field."],
        ["Report Tab", "List of Checked Charts", "Interactive Box", "Container displaying verified charts, auto-populated from comparison sessions.", "View auto-populated charts or use Add Chart(s)... / Remove Selected Chart to modify the list."],
        ["Report Tab", "Add Chart(s)...", "Button", "Opens a multi-file browser allowing selection of all PDF charts verified during the session.", "Click to select and add PDF charts to the List of Checked Charts."],
        ["Report Tab", "Remove Selected Chart", "Button", "Removes the highlighted chart(s) from the List of Checked Charts.", "Highlight chart(s) in the list and click to remove them."],
        ["Report Tab", "Captured Visual Evidence", "Interactive Box", "Thumbnail list displaying all saved annotated chart screenshots with status counter.", "Scroll through evidence thumbnails; double-click or click Preview to inspect."],
        ["Report Tab", "Preview Selected Evidence", "Button", "Opens the full-size high-resolution screenshot in a preview viewer.", "Select an evidence item and click to view full-scale details."],
        ["Report Tab", "Remove Selected Evidence", "Button", "Removes unneeded or duplicate screenshot evidence prior to generating the PDF report.", "Select an evidence item and click to remove it from the report."],
        ["Report Tab", "Validation Review Summary", "Interactive Box", "Displays total checked charts, error breakdown by severity, and saved annotation counts.", "Cleanly fitted container updating in real time."],
        ["Report Tab", "Generate PDF Report", "Button", "Compiles session data into official PDF report with auto-naming (LogSheetNumber_NameSurname.pdf) and full-page evidence.", "Click to compile official report. Button styled in green (#10B981). Fully supports Georgian and Unicode text."]
    ]

    # Clear existing rows in table1 beyond header
    header_tr = table1.rows[0]._tr
    for row in table1.rows[1:]:
        table1._tbl.remove(row._tr)

    # Re-populate table1 with new rows
    for row_data in new_table_rows:
        new_row = table1.add_row()
        for c_idx, text in enumerate(row_data):
            cell = new_row.cells[c_idx]
            cell.text = text
            # Format text nicely
            for p in cell.paragraphs:
                p.paragraph_format.space_before = Pt(3)
                p.paragraph_format.space_after = Pt(3)
                for r in p.runs:
                    r.font.name = 'Arial'
                    r.font.size = Pt(8.5)

    # Format header row
    for p in table1.rows[0].cells:
        for r in p.paragraphs[0].runs:
            r.font.name = 'Arial'
            r.font.size = Pt(9)
            r.font.bold = True

    # Save outputs
    out_path_v1_1 = 'Manual_v1.1.docx'
    doc.save(out_path_v1_1)
    print(f"Successfully created {out_path_v1_1}!")

    # Also copy to Full package/Manual.docx
    full_pkg_manual = os.path.join('Full package', 'Manual.docx')
    if os.path.exists('Full package'):
        shutil.copy2(out_path_v1_1, full_pkg_manual)
        print(f"Successfully updated {full_pkg_manual}!")

    # Also update root Manual.docx
    shutil.copy2(out_path_v1_1, 'Manual.docx')
    print("Successfully updated root Manual.docx!")

if __name__ == '__main__':
    create_manual_v1_1()
