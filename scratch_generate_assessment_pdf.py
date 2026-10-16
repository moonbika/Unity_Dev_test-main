import os
import sys
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, KeepTogether, HRFlowable
)
from reportlab.pdfgen import canvas

# Modern Palette
C_PRIMARY = colors.HexColor("#0F172A")       # Slate 900
C_PRIMARY_LIGHT = colors.HexColor("#1E293B") # Slate 800
C_ACCENT = colors.HexColor("#2563EB")        # Blue 600
C_ACCENT_TEAL = colors.HexColor("#0D9488")   # Teal 600
C_TEXT = colors.HexColor("#1E293B")          # Slate 800
C_TEXT_MUTED = colors.HexColor("#64748B")    # Slate 500
C_BG_LIGHT = colors.HexColor("#F8FAFC")      # Slate 50
C_BG_ALT = colors.HexColor("#F1F5F9")        # Slate 100
C_BORDER = colors.HexColor("#CBD5E1")        # Slate 300
C_BORDER_LIGHT = colors.HexColor("#E2E8F0")  # Slate 200
C_WARNING = colors.HexColor("#D97706")       # Amber 600
C_DANGER = colors.HexColor("#DC2626")        # Red 600
C_SUCCESS = colors.HexColor("#16A34A")       # Green 600

class NumberedCanvas(canvas.Canvas):
    """
    Two-pass canvas for exact total page count and clean running header/footer.
    Uses pure ASCII strings to prevent any font encoding artifacts.
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._saved_page_states = []

    def showPage(self):
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        num_pages = len(self._saved_page_states)
        for state in self._saved_page_states:
            self.__dict__.update(state)
            self.draw_page_decorations(num_pages)
            canvas.Canvas.showPage(self)
        canvas.Canvas.save(self)

    def draw_page_decorations(self, page_count):
        self.saveState()
        self.setFont("Helvetica-Bold", 7.5)
        self.setFillColor(C_TEXT_MUTED)

        width, height = letter
        margin = 36

        # Running header on pages 2+
        if self._pageNumber > 1:
            header_text = "TOPDOWN TANK | UNITY DEVELOPER PRACTICAL TEST"
            category_text = "GAMEPLAY & SYSTEMS"
            self.drawString(margin, height - 26, header_text)
            self.drawRightString(width - margin, height - 26, category_text)
            
            self.setStrokeColor(C_BORDER_LIGHT)
            self.setLineWidth(0.75)
            self.line(margin, height - 30, width - margin, height - 30)

        # Running footer on all pages
        self.setStrokeColor(C_BORDER_LIGHT)
        self.setLineWidth(0.75)
        self.line(margin, 34, width - margin, 34)

        self.setFont("Helvetica", 7.5)
        self.setFillColor(C_TEXT_MUTED)
        footer_left = "CANDIDATE PRACTICAL ASSESSMENT | CONFIDENTIAL"
        footer_right = f"Page {self._pageNumber} of {page_count}"

        self.drawString(margin, 22, footer_left)
        self.drawRightString(width - margin, 22, footer_right)

        self.restoreState()


def build_pdf(filename="Unity_Developer_Assessment_TopDownTank.pdf"):
    doc = SimpleDocTemplate(
        filename,
        pagesize=letter,
        leftMargin=36,
        rightMargin=36,
        topMargin=38,
        bottomMargin=40
    )

    styles = getSampleStyleSheet()

    style_cover_title = ParagraphStyle(
        'CoverTitle',
        fontName='Helvetica-Bold',
        fontSize=17,
        leading=21,
        textColor=colors.white,
        spaceAfter=3
    )
    style_cover_subtitle = ParagraphStyle(
        'CoverSubtitle',
        fontName='Helvetica',
        fontSize=9.5,
        leading=13.5,
        textColor=colors.HexColor("#93C5FD"),
        spaceAfter=1
    )
    style_cover_tag = ParagraphStyle(
        'CoverTag',
        fontName='Helvetica-Bold',
        fontSize=7.5,
        leading=10,
        textColor=colors.HexColor("#FCD34D"),
        alignment=2
    )

    style_h1 = ParagraphStyle(
        'SectionH1',
        fontName='Helvetica-Bold',
        fontSize=12,
        leading=15,
        textColor=C_PRIMARY,
        spaceBefore=7,
        spaceAfter=4,
        keepWithNext=True
    )

    style_h2 = ParagraphStyle(
        'SectionH2',
        fontName='Helvetica-Bold',
        fontSize=9.5,
        leading=12.5,
        textColor=C_ACCENT,
        spaceBefore=6,
        spaceAfter=3,
        keepWithNext=True
    )

    style_body = ParagraphStyle(
        'BodyDark',
        fontName='Helvetica',
        fontSize=8,
        leading=11,
        textColor=C_TEXT,
        spaceAfter=3
    )

    style_th = ParagraphStyle(
        'TableHead',
        fontName='Helvetica-Bold',
        fontSize=7.5,
        leading=9.5,
        textColor=colors.white,
        alignment=0
    )

    style_td = ParagraphStyle(
        'TableCell',
        fontName='Helvetica',
        fontSize=7.2,
        leading=9.5,
        textColor=C_TEXT,
        alignment=0
    )

    style_td_bold = ParagraphStyle(
        'TableCellBold',
        fontName='Helvetica-Bold',
        fontSize=7.2,
        leading=9.5,
        textColor=C_TEXT,
        alignment=0
    )

    style_td_success = ParagraphStyle(
        'TableCellSuccess',
        fontName='Helvetica-Bold',
        fontSize=7.2,
        leading=9.5,
        textColor=C_SUCCESS,
        alignment=0
    )

    style_td_danger = ParagraphStyle(
        'TableCellDanger',
        fontName='Helvetica-Bold',
        fontSize=7.2,
        leading=9.5,
        textColor=C_DANGER,
        alignment=0
    )

    style_header_white = ParagraphStyle(
        'HeaderWhite',
        fontName='Helvetica-Bold',
        fontSize=7.8,
        leading=10,
        textColor=colors.white,
        alignment=0
    )

    style_header_white_right = ParagraphStyle(
        'HeaderWhiteRight',
        fontName='Helvetica-Bold',
        fontSize=7.5,
        leading=10,
        textColor=colors.HexColor("#FCD34D"),
        alignment=2
    )

    story = []

    # =========================================================================
    # PAGE 1: TITLE BANNER, 2-DAY SCHEDULE & PROJECT AUDIT
    # =========================================================================
    
    banner_content = [
        [
            Paragraph("UNITY GAME DEVELOPER PRACTICAL TEST", style_cover_title),
            Paragraph("CANDIDATE PRACTICAL TEST<br/><b>TIME LIMIT: 2 DAYS MAX</b>", style_cover_tag)
        ],
        [
            Paragraph("Project: <b>TopDown Tank Battleground</b> &mdash; Unity Upgrade, Cinemachine, Gamepad &amp; Performance", style_cover_subtitle),
            Paragraph("", style_cover_subtitle)
        ]
    ]
    banner_table = Table(banner_content, colWidths=[395, 145])
    banner_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), C_PRIMARY),
        ('PADDING', (0, 0), (-1, -1), 9),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 2),
        ('TOPPADDING', (0, 1), (-1, 1), 2),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('LINEBELOW', (0, -1), (-1, -1), 3, C_ACCENT),
    ]))
    story.append(banner_table)
    story.append(Spacer(1, 6))

    # Test Metadata Table
    meta_data = [
        [
            Paragraph("<b>Target Role:</b> Unity Game Developer", style_td),
            Paragraph("<b>Allowed Time:</b> <b>2 Days Max</b> (Approx. 6 &ndash; 8 hours of work)", style_td)
        ],
        [
            Paragraph("<b>Starting Unity Version:</b> Unity 2021.3.33f1 (Built-in RP)", style_td),
            Paragraph("<b>Target Unity Version:</b> Latest Unity LTS (Unity 6 or 2022.3 LTS)", style_td)
        ],
        [
            Paragraph("<b>Controls:</b> Full Gamepad Support + Keyboard/Mouse Fallback", style_td),
            Paragraph("<b>Deliverables:</b> Source Repo + Playable Build ZIP + Optimization Notes", style_td)
        ]
    ]
    meta_table = Table(meta_data, colWidths=[270, 270])
    meta_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), C_BG_LIGHT),
        ('BOX', (0, 0), (-1, -1), 0.75, C_BORDER),
        ('INNERGRID', (0, 0), (-1, -1), 0.5, C_BORDER_LIGHT),
        ('PADDING', (0, 0), (-1, -1), 5),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
    ]))
    story.append(meta_table)
    story.append(Spacer(1, 6))

    # Overview Callout
    intro_p = Paragraph(
        "<b>Candidate Mission Brief:</b> You are provided with a prototype Unity project (<i>TopDownTank-main</i>). "
        "It includes basic tank driving, turret aiming, projectile firing, and a simple enemy in a flat sandbox scene. "
        "However, the project has outdated engine files, mouse-only controls, a rigid camera, zero level progression, and noticeable lag caused by unoptimized code. "
        "Your task over the next <b>2 days</b> is to update the Unity version, replace the camera with Cinemachine, add full gamepad support, create a few playable levels, "
        "code a debug panel to track FPS, fix key performance bottlenecks, and output a playable standalone build.",
        style_body
    )
    story.append(intro_p)
    story.append(Spacer(1, 4))

    # Section 1: Code Review & Existing Flaws
    story.append(Paragraph("1. Existing Codebase Review & Known Issues", style_h1))
    story.append(Paragraph(
        "Before writing new code, review the key flaws already identified in the project files that you need to resolve:",
        style_body
    ))

    audit_headers = [
        Paragraph("Area", style_th),
        Paragraph("Current File & Location", style_th),
        Paragraph("Observed Issue & What to Fix", style_th),
        Paragraph("Priority", style_th)
    ]
    audit_rows = [
        audit_headers,
        [
            Paragraph("<b>Unity Version</b>", style_td_bold),
            Paragraph("<code>ProjectSettings/<br/>ProjectVersion.txt</code>", style_td),
            Paragraph("Project is on older Unity <b>2021.3.33f1</b>. Needs to be updated to the latest Unity LTS build (Unity 6 or 2022.3 LTS) with clean package setup.", style_td),
            Paragraph("<font color='#DC2626'><b>HIGH</b></font>", style_td)
        ],
        [
            Paragraph("<b>Camera Script</b>", style_td_bold),
            Paragraph("<code>Assets/Scripts/<br/>TopDownCamera.cs</code>", style_td),
            Paragraph("Script name mismatch (class is <code>TopDownCameraFollow</code>). Rigid follow with no screen shake, framing deadzones, or arena boundaries.", style_td),
            Paragraph("<font color='#2563EB'><b>MEDIUM</b></font>", style_td)
        ],
        [
            Paragraph("<b>Input Controls</b>", style_td_bold),
            Paragraph("<code>Tank_Inputs.cs:50<br/>ThrowProjectile.cs:25</code>", style_td),
            Paragraph("Aiming is locked to <code>Input.mousePosition</code> and firing to <code>Input.GetMouseButtonDown(0)</code>. <b>Controllers/Gamepads do not work</b>.", style_td),
            Paragraph("<font color='#DC2626'><b>CRITICAL</b></font>", style_td)
        ],
        [
            Paragraph("<b>Console Spam</b>", style_td_bold),
            Paragraph("<code>Assets/Scripts/<br/>EnemyTankAi.cs:160</code>", style_td),
            Paragraph("Calls <code>Debug.Log(distance);</code> in <code>FixedUpdate()</code> every physics tick. Causes console flood and garbage collection (GC) micro-stutter.", style_td),
            Paragraph("<font color='#DC2626'><b>CRITICAL</b></font>", style_td)
        ],
        [
            Paragraph("<b>Bullet Spawning</b>", style_td_bold),
            Paragraph("<code>Projectile.cs:11,22<br/>ThrowProjectile.cs:41</code>", style_td),
            Paragraph("Every bullet and particle effect is constantly spawned with <code>Instantiate()</code> and removed with <code>Destroy()</code>. No object pooling.", style_td),
            Paragraph("<font color='#DC2626'><b>HIGH</b></font>", style_td)
        ],
        [
            Paragraph("<b>Physics & Tagging</b>", style_td_bold),
            Paragraph("<code>Projectile.cs:13,18<br/>TankController.cs:41</code>", style_td),
            Paragraph("Uses string comparison <code>tag == 'PlayerTank'</code> instead of <code>CompareTag()</code>. <code>FixedUpdate()</code> uses <code>Time.deltaTime</code> instead of <code>Time.fixedDeltaTime</code>.", style_td),
            Paragraph("<font color='#2563EB'><b>MEDIUM</b></font>", style_td)
        ],
        [
            Paragraph("<b>Levels & Flow</b>", style_td_bold),
            Paragraph("<code>Assets/Scenes/<br/>Test.unity</code>", style_td),
            Paragraph("Only one flat test scene exists. No level progression, objective conditions, victory/loss screens, or menu.", style_td),
            Paragraph("<font color='#2563EB'><b>MEDIUM</b></font>", style_td)
        ]
    ]

    audit_table = Table(audit_rows, colWidths=[75, 115, 290, 60])
    audit_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), C_PRIMARY_LIGHT),
        ('BOX', (0, 0), (-1, -1), 0.75, C_BORDER),
        ('INNERGRID', (0, 0), (-1, -1), 0.5, C_BORDER_LIGHT),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, C_BG_LIGHT]),
        ('PADDING', (0, 0), (-1, -1), 4),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('ALIGN', (3, 0), (3, -1), 'CENTER'),
    ]))
    story.append(audit_table)

    story.append(PageBreak())

    # =========================================================================
    # PAGE 2: TASKS 1, 2, 3, 4 (UPGRADE, CINEMACHINE, GAMEPAD, LEVELS)
    # =========================================================================
    story.append(Paragraph("2. Candidate Tasks &amp; Requirements", style_h1))
    story.append(Paragraph(
        "Below are the primary gameplay tasks to complete. Focus on clean code, good control feel, and solid execution within the 2-day timeframe.",
        style_body
    ))
    story.append(Spacer(1, 3))

    # TASK 1
    t1_box = [
        [
            Paragraph("<b>TASK 1: Update Game Version to Latest Unity LTS Build</b>", style_td_bold),
            Paragraph("<font color='#16A34A'><b>ENGINE UPGRADE</b></font>", style_td_success)
        ]
    ]
    t1_header = Table(t1_box, colWidths=[420, 120])
    t1_header.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), C_BG_ALT),
        ('BOX', (0, 0), (-1, -1), 1, C_ACCENT),
        ('PADDING', (0, 0), (-1, -1), 3.5),
        ('ALIGN', (1, 0), (1, 0), 'RIGHT'),
    ]))
    story.append(t1_header)
    story.append(Spacer(1, 2))

    t1_desc = Paragraph(
        "<b>Goal:</b> Upgrade the project from Unity <code>2021.3.33f1</code> to the latest official Unity LTS build (Unity 6 or 2022.3 LTS).<br/>"
        "&bull; Ensure all packages in <code>Packages/manifest.json</code> resolve cleanly.<br/>"
        "&bull; Fix any obsolete Unity APIs or deprecated calls so the console shows <b>zero compiler errors and zero warnings</b>.<br/>"
        "&bull; Briefly note any package changes in your submission <code>README.md</code>.",
        style_body
    )
    story.append(t1_desc)
    story.append(Spacer(1, 5))

    # TASK 2
    t2_box = [
        [
            Paragraph("<b>TASK 2: Use Cinemachine to Update the Camera</b>", style_td_bold),
            Paragraph("<font color='#2563EB'><b>CAMERA &amp; GAME FEEL</b></font>", style_td)
        ]
    ]
    t2_header = Table(t2_box, colWidths=[420, 120])
    t2_header.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), C_BG_ALT),
        ('BOX', (0, 0), (-1, -1), 1, C_ACCENT),
        ('PADDING', (0, 0), (-1, -1), 3.5),
        ('ALIGN', (1, 0), (1, 0), 'RIGHT'),
    ]))
    story.append(t2_header)
    story.append(Spacer(1, 2))

    t2_desc = Paragraph(
        "<b>Goal:</b> Remove the old <code>TopDownCamera.cs</code> script and implement a polished Unity Cinemachine camera.<br/>"
        "&bull; Install Cinemachine (<code>com.unity.cinemachine</code>) and create a Virtual Camera targeting the player tank.<br/>"
        "&bull; Configure smooth follow damping and an isometric top-down angle that gives clear sight of the battlefield.<br/>"
        "&bull; Add <b>Camera Shake</b> (Cinemachine Impulse) when the player fires the cannon and when projectiles explode.<br/>"
        "&bull; Add a <b>Cinemachine Confiner</b> or bounding area so the camera never shows empty grey space outside the arena.",
        style_body
    )
    story.append(t2_desc)
    story.append(Spacer(1, 5))

    # TASK 3
    t3_box = [
        [
            Paragraph("<b>TASK 3: Make the Game Fully Playable with a Gamepad</b>", style_td_bold),
            Paragraph("<font color='#D97706'><b>GAMEPAD &amp; CONTROLS</b></font>", style_td)
        ]
    ]
    t3_header = Table(t3_box, colWidths=[420, 120])
    t3_header.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), C_BG_ALT),
        ('BOX', (0, 0), (-1, -1), 1, C_ACCENT),
        ('PADDING', (0, 0), (-1, -1), 3.5),
        ('ALIGN', (1, 0), (1, 0), 'RIGHT'),
    ]))
    story.append(t3_header)
    story.append(Spacer(1, 2))

    t3_desc = Paragraph(
        "<b>Goal:</b> Overhaul player controls so the game feels great on an Xbox or PlayStation controller, while keeping keyboard &amp; mouse working.<br/>"
        "&bull; <b>Dual-Stick Controls:</b><br/>"
        "  - <i>Left Stick:</i> Drives tank hull forward/backward and turns the chassis.<br/>"
        "  - <i>Right Stick:</i> Aims the turret smoothly in 360 degrees (with a reasonable deadzone so it doesn't drift).<br/>"
        "  - <i>Right Trigger (RT) or Bumper (RB):</i> Fires cannon shells at the normal fire-rate cadence.<br/>"
        "&bull; <b>Keyboard &amp; Mouse Fallback:</b> WASD to drive, Mouse to aim reticle, Left Mouse Button to fire.<br/>"
        "&bull; <b>Seamless Switching:</b> Picking up the controller or touching the mouse should swap seamlessly without pausing or restarting.<br/>"
        "&bull; You may use Unity's New Input System or clean code on the legacy input manager.",
        style_body
    )
    story.append(t3_desc)
    story.append(Spacer(1, 5))

    # TASK 4
    t4_box = [
        [
            Paragraph("<b>TASK 4: Create Multiple Levels &amp; Game Flow</b>", style_td_bold),
            Paragraph("<font color='#16A34A'><b>LEVELS &amp; PROGRESSION</b></font>", style_td_success)
        ]
    ]
    t4_header = Table(t4_box, colWidths=[420, 120])
    t4_header.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), C_BG_ALT),
        ('BOX', (0, 0), (-1, -1), 1, C_ACCENT),
        ('PADDING', (0, 0), (-1, -1), 3.5),
        ('ALIGN', (1, 0), (1, 0), 'RIGHT'),
    ]))
    story.append(t4_header)
    story.append(Spacer(1, 2))

    t4_desc = Paragraph(
        "<b>Goal:</b> Expand beyond the single test scene into a mini-campaign with at least <b>2 to 3 playable levels</b>.<br/>"
        "&bull; <b>Level Variety:</b><br/>"
        "  - <i>Level 1 (Warmup):</i> Open arena, stationary or low-health target enemies, destructible blocks.<br/>"
        "  - <i>Level 2 (Tactical):</i> Barricades, narrow alleys, patrolling enemy tanks that hunt the player.<br/>"
        "  - <i>Level 3 (Showdown):</i> Multiple enemy tanks, defensive layout, higher difficulty.<br/>"
        "&bull; <b>Simple Game Loop:</b><br/>"
        "  - Main Menu or Start Screen with a Play button.<br/>"
        "  - Win condition: Destroy all enemy tanks -&gt; Victory screen with a 'Next Level' button.<br/>"
        "  - Lose condition: Player health reaches 0 -&gt; Game Over screen with a 'Retry' button.",
        style_body
    )
    story.append(t4_desc)

    story.append(PageBreak())

    # =========================================================================
    # PAGE 3: TASKS 5, 6, 7 (DEBUG PANEL, OPTIMIZATION TIPS, BUILD)
    # =========================================================================
    story.append(Paragraph("2. Candidate Tasks (Continued)", style_h1))
    story.append(Spacer(1, 3))

    # TASK 5
    t5_box = [
        [
            Paragraph("<b>TASK 5: Code an In-Game Debug Panel (FPS Counter &amp; QA Tools)</b>", style_td_bold),
            Paragraph("<font color='#2563EB'><b>DEBUGGING TOOLS</b></font>", style_td)
        ]
    ]
    t5_header = Table(t5_box, colWidths=[420, 120])
    t5_header.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), C_BG_ALT),
        ('BOX', (0, 0), (-1, -1), 1, C_ACCENT),
        ('PADDING', (0, 0), (-1, -1), 3.5),
        ('ALIGN', (1, 0), (1, 0), 'RIGHT'),
    ]))
    story.append(t5_header)
    story.append(Spacer(1, 2))

    t5_desc = Paragraph(
        "<b>Goal:</b> Build a toggleable UI debug overlay so testers can monitor framerate and test features quickly.<br/>"
        "&bull; <b>Toggle Hotkey:</b> Easily opened/closed using a key (e.g. <code>F3</code> / Backquote) and a controller shortcut (e.g. <code>Select/View</code> button).<br/>"
        "&bull; <b>Performance Metrics Displayed:</b><br/>"
        "  - <b>Live FPS:</b> Show Current FPS, Smoothed Average FPS, and 1% Low / Min FPS.<br/>"
        "  - <b>Frame Time:</b> Frame delta in milliseconds (e.g. <code>16.6 ms</code>).<br/>"
        "  - <b>Memory Usage:</b> Current allocated heap memory.<br/>"
        "  - <b>Entity Counter:</b> Count of active enemies and active bullets currently in the scene.<br/>"
        "&bull; <b>Quick QA Cheats:</b><br/>"
        "  - <i>God Mode:</i> Toggle player tank invincibility.<br/>"
        "  - <i>Spawn Enemy:</i> Button to spawn an extra enemy tank for testing.<br/>"
        "  - <i>Win / Skip Level:</i> Instantly triggers level completion to jump to the next stage.<br/>"
        "  - <i>Game Speed (TimeScale):</i> Slider or buttons for Slow Motion (0.5x) and Fast (1.5x).<br/>"
        "&bull; <b>Efficiency:</b> Ensure the debug panel updates without generating garbage strings every frame.",
        style_body
    )
    story.append(t5_desc)
    story.append(Spacer(1, 5))

    # TASK 6
    t6_box = [
        [
            Paragraph("<b>TASK 6: Performance Optimization &amp; Optimization Tips</b>", style_td_bold),
            Paragraph("<font color='#DC2626'><b>OPTIMIZATION</b></font>", style_td_danger)
        ]
    ]
    t6_header = Table(t6_box, colWidths=[420, 120])
    t6_header.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), C_BG_ALT),
        ('BOX', (0, 0), (-1, -1), 1, C_ACCENT),
        ('PADDING', (0, 0), (-1, -1), 3.5),
        ('ALIGN', (1, 0), (1, 0), 'RIGHT'),
    ]))
    story.append(t6_header)
    story.append(Spacer(1, 2))

    t6_desc = Paragraph(
        "<b>Goal:</b> Fix the existing lag sources in the codebase and write down clear optimization recommendations.<br/>"
        "&bull; <b>In-Code Fixes Required:</b><br/>"
        "  1. Delete the <code>Debug.Log(distance);</code> call inside <code>EnemyTankAi.cs:160</code>.<br/>"
        "  2. Implement a simple <b>Object Pool</b> for bullets and explosion particle effects instead of calling <code>Instantiate</code> and <code>Destroy</code> every shot.<br/>"
        "  3. Replace string comparisons (<code>tag == 'PlayerTank'</code>) with <code>CompareTag()</code>.<br/>"
        "  4. In <code>TankController.cs</code> and <code>EnemyTankAi.cs</code>, replace <code>Time.deltaTime</code> inside <code>FixedUpdate()</code> with <code>Time.fixedDeltaTime</code>.<br/>"
        "  5. Add a <code>LayerMask</code> to the aiming raycast so it only hits the ground plane, not the tank itself.<br/>"
        "&bull; <b>Written Optimization Tips (<code>OPTIMIZATION_TIPS.md</code>):</b><br/>"
        "  Provide a concise 1-page document proposing practical tips for how this game can run at locked high FPS (Draw calls, static batching, light baking, physics collision layer matrix, texture compression).",
        style_body
    )
    story.append(t6_desc)
    story.append(Spacer(1, 5))

    # TASK 7
    t7_box = [
        [
            Paragraph("<b>TASK 7: Make a Playable Standalone Build</b>", style_td_bold),
            Paragraph("<font color='#16A34A'><b>FINAL BUILD</b></font>", style_td_success)
        ]
    ]
    t7_header = Table(t7_box, colWidths=[420, 120])
    t7_header.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), C_BG_ALT),
        ('BOX', (0, 0), (-1, -1), 1, C_ACCENT),
        ('PADDING', (0, 0), (-1, -1), 3.5),
        ('ALIGN', (1, 0), (1, 0), 'RIGHT'),
    ]))
    story.append(t7_header)
    story.append(Spacer(1, 2))

    t7_desc = Paragraph(
        "<b>Goal:</b> Export a working standalone Windows build so the game can be tested directly outside Unity.<br/>"
        "&bull; Target platform: <b>Windows Standalone (x86_64)</b>.<br/>"
        "&bull; Set product name to 'Tank Battleground' and configure default windowed/fullscreen options.<br/>"
        "&bull; Verify that both gamepad controls and keyboard/mouse work properly in the compiled build.<br/>"
        "&bull; Package the executable and data files into a single ZIP file for submission.",
        style_body
    )
    story.append(t7_desc)

    story.append(PageBreak())

    # =========================================================================
    # PAGE 4: EVALUATION RUBRIC, SUBMISSION CHECKLIST & FAQ
    # =========================================================================
    story.append(Paragraph("3. Scoring Rubric &amp; Submission Checklist", style_h1))
    story.append(Paragraph(
        "Submissions are evaluated on a 100-point rubric. We look for good control feel, clean readable code, and working features.",
        style_body
    ))
    story.append(Spacer(1, 3))

    # Rubric Table
    rubric_headers = [
        Paragraph("Category", style_th),
        Paragraph("Points", style_th),
        Paragraph("Evaluation Criteria", style_th)
    ]

    rubric_rows = [
        rubric_headers,
        [
            Paragraph("<b>1. Unity LTS Upgrade</b>", style_td_bold),
            Paragraph("15 pts", style_td),
            Paragraph("Project opens in the target Unity LTS with zero errors and zero warnings. Packages resolve cleanly.", style_td)
        ],
        [
            Paragraph("<b>2. Cinemachine Camera</b>", style_td_bold),
            Paragraph("15 pts", style_td),
            Paragraph("Smooth top-down follow, camera shake on firing/explosions, and confiner bounds preventing view clipping.", style_td)
        ],
        [
            Paragraph("<b>3. Gamepad &amp; Controls</b>", style_td_bold),
            Paragraph("20 pts", style_td),
            Paragraph("Dual-stick drive &amp; 360&deg; aim feels natural on controller with deadzones. Triggers fire. KBM fallback works.", style_td)
        ],
        [
            Paragraph("<b>4. Levels &amp; Game Loop</b>", style_td_bold),
            Paragraph("15 pts", style_td),
            Paragraph("2 to 3 playable levels with obstacle variety, enemy tanks, win/loss UI, and smooth scene transitions.", style_td)
        ],
        [
            Paragraph("<b>5. FPS Debug Panel</b>", style_td_bold),
            Paragraph("15 pts", style_td),
            Paragraph("Working in-game overlay showing live FPS, frame ms, memory, and functional cheats (God Mode, Spawner, Skip).", style_td)
        ],
        [
            Paragraph("<b>6. Optimization &amp; Build</b>", style_td_bold),
            Paragraph("20 pts", style_td),
            Paragraph("Log spam removed, bullet pooling working, tag check fixed, written optimization tips, and playable Windows build.", style_td)
        ],
        [
            Paragraph("<b>Total Score</b>", style_td_bold),
            Paragraph("<b>100 pts</b>", style_td_bold),
            Paragraph("<b>Passing score: 75+ points.</b> <i>(Bonus: +5 points for extra audio polish, particle effects, or controller rumble).</i>", style_td_bold)
        ]
    ]

    rubric_table = Table(rubric_rows, colWidths=[130, 45, 365])
    rubric_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), C_PRIMARY_LIGHT),
        ('BOX', (0, 0), (-1, -1), 0.75, C_BORDER),
        ('INNERGRID', (0, 0), (-1, -1), 0.5, C_BORDER_LIGHT),
        ('ROWBACKGROUNDS', (0, 1), (-1, -2), [colors.white, C_BG_LIGHT]),
        ('BACKGROUND', (0, -1), (-1, -1), C_BG_ALT),
        ('PADDING', (0, 0), (-1, -1), 4),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('ALIGN', (1, 0), (1, -1), 'CENTER'),
    ]))
    story.append(rubric_table)
    story.append(Spacer(1, 6))

    # Submission Checklist
    story.append(Paragraph("<b>Submission Procedure &amp; Checklist (2-Day Window)</b>", style_h2))

    check_data = [
        [
            Paragraph("Deliverable", style_th),
            Paragraph("Details", style_th),
            Paragraph("Status", style_th)
        ],
        [
            Paragraph("<b>1. Git Repository</b>", style_td_bold),
            Paragraph("GitHub/GitLab repository link (exclude <code>Library/</code>, <code>Temp/</code>, and <code>Logs/</code>).", style_td),
            Paragraph("[  ] Done", style_td_bold)
        ],
        [
            Paragraph("<b>2. Standalone Build</b>", style_td_bold),
            Paragraph("Playable Windows 64-bit build (.exe) zipped and shared via Google Drive or GitHub release.", style_td),
            Paragraph("[  ] Done", style_td_bold)
        ],
        [
            Paragraph("<b>3. Optimization Tips</b>", style_td_bold),
            Paragraph("A short <code>OPTIMIZATION_TIPS.md</code> explaining the fixes made and future optimization ideas.", style_td),
            Paragraph("[  ] Done", style_td_bold)
        ],
        [
            Paragraph("<b>4. Readme Notes</b>", style_td_bold),
            Paragraph("Quick <code>README.md</code> explaining control mappings, Unity version used, and debug panel hotkey.", style_td),
            Paragraph("[  ] Done", style_td_bold)
        ]
    ]

    check_table = Table(check_data, colWidths=[120, 340, 80])
    check_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), C_PRIMARY_LIGHT),
        ('BOX', (0, 0), (-1, -1), 0.75, C_BORDER),
        ('INNERGRID', (0, 0), (-1, -1), 0.5, C_BORDER_LIGHT),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, C_BG_LIGHT]),
        ('PADDING', (0, 0), (-1, -1), 4),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('ALIGN', (2, 0), (2, -1), 'CENTER'),
    ]))
    story.append(check_table)
    story.append(Spacer(1, 6))

    # Practical FAQ
    story.append(Paragraph("<b>Practical FAQ for Candidates</b>", style_h2))

    faq_content = Paragraph(
        "<b>Q: Can I use Unity's New Input System?</b><br/>"
        "<i>A:</i> Yes. You may use either Unity's New Input System package or write clean custom input code using the Input Manager. Whichever you choose, ensure the gamepad dual-stick controls feel smooth and responsive.<br/><br/>"
        "<b>Q: What if I run out of time on 3 levels?</b><br/>"
        "<i>A:</i> 2 well-designed levels with working win/loss flow and good combat feel is better than 3 rushed broken scenes. Focus on quality and smooth gameplay feel first.<br/><br/>"
        "<b>Q: Can I use free sound effects or particle assets?</b><br/>"
        "<i>A:</i> Yes, you are welcome to use free assets to improve game feel, but all game logic (gamepad input, camera shake, pooling, debug panel) should be written by you.",
        style_body
    )
    story.append(faq_content)

    doc.build(story, canvasmaker=NumberedCanvas)
    print(f"Document successfully created: {filename}")

if __name__ == "__main__":
    output_filename = "c:/Users/PC/Downloads/TopDownTank-main/TopDownTank-main/Unity_Developer_Assessment_TopDownTank.pdf"
    build_pdf(output_filename)
