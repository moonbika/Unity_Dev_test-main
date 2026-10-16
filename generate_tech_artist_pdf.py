import os
import sys
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, KeepTogether
)
from reportlab.pdfgen import canvas

# Palette tailored for Tech Art Assessment (Deep Slate + Vibrant Purple/Violet Accent)
C_PRIMARY = colors.HexColor("#0F172A")       # Slate 900
C_PRIMARY_LIGHT = colors.HexColor("#1E293B") # Slate 800
C_ACCENT = colors.HexColor("#7C3AED")        # Violet 600 (Creative / Tech Art)
C_ACCENT_HOVER = colors.HexColor("#6D28D9")  # Violet 700
C_ACCENT_CYAN = colors.HexColor("#0284C7")   # Sky 600
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
            header_text = "TOPDOWN TANK | TECHNICAL ARTIST PRACTICAL TEST"
            category_text = "SHADERS - VFX - LIGHTING - PERFORMANCE"
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
        footer_left = "TECHNICAL ARTIST PRACTICAL ASSESSMENT | CONFIDENTIAL"
        footer_right = f"Page {self._pageNumber} of {page_count}"

        self.drawString(margin, 22, footer_left)
        self.drawRightString(width - margin, 22, footer_right)

        self.restoreState()


def build_pdf(filename="Unity_Technical_Artist_Assessment_TopDownTank.pdf"):
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
        textColor=colors.HexColor("#DDD6FE"), # Soft Light Purple
        spaceAfter=1
    )
    style_cover_tag = ParagraphStyle(
        'CoverTag',
        fontName='Helvetica-Bold',
        fontSize=7.5,
        leading=10,
        textColor=colors.HexColor("#FCD34D"), # Amber Accent
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

    story = []

    # =========================================================================
    # PAGE 1: TITLE BANNER, 2-DAY SCHEDULE & VISUAL AUDIT
    # =========================================================================
    
    banner_content = [
        [
            Paragraph("TECHNICAL ARTIST PRACTICAL TEST", style_cover_title),
            Paragraph("CANDIDATE PRACTICAL TEST<br/><b>TIME LIMIT: 2 DAYS MAX</b>", style_cover_tag)
        ],
        [
            Paragraph("Project: <b>TopDown Tank Battleground</b> &mdash; Shaders, VFX, Lighting &amp; Performance", style_cover_subtitle),
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
            Paragraph("<b>Target Role:</b> Technical Artist (Unity)", style_td),
            Paragraph("<b>Allowed Time:</b> <b>2 Days Max</b> (Approx. 6 &ndash; 8 hours of work)", style_td)
        ],
        [
            Paragraph("<b>Starting Baseline:</b> Unity 2021.3 Built-in RP (Flat Prototype)", style_td),
            Paragraph("<b>Target Pipeline:</b> Universal Render Pipeline (URP) on modern LTS", style_td)
        ],
        [
            Paragraph("<b>Core Focus:</b> Shaders, Lighting, Post-Processing, VFX, Profiling", style_td),
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
        "<b>Candidate Mission Brief:</b> You are handed an early prototype of a top-down arcade tank game (<i>TopDownTank-main</i>). "
        "Mechanically the game works, but visually it is completely unpolished: flat greybox prototype cubes, default uncalibrated lighting, "
        "no post-processing volume, zero stylized shaders, and bare particle explosions that lack impact and cause fill-rate spikes. "
        "Your task over the next <b>2 days</b> is to transform this greybox prototype into a vibrant, stylized, arcade combat arena. "
        "You will upgrade to URP, build custom shaders for tanks and arena geometry, establish mood through lighting and post-processing, "
        "overhaul weapon and impact VFX, and optimize the rendering pipeline for rock-solid framerates.",
        style_body
    )
    story.append(intro_p)
    story.append(Spacer(1, 4))

    # Section 1: Codebase Visual Audit & Technical Gaps
    story.append(Paragraph("1. Current Visual State & Technical Art Gaps", style_h1))
    story.append(Paragraph(
        "An inspection of the assets and rendering configuration in <code>TopDownTank-main</code> highlights several key areas needing your expertise:",
        style_body
    ))

    audit_headers = [
        Paragraph("Visual Area", style_th),
        Paragraph("Current State in Project", style_th),
        Paragraph("Technical Art Problem & Goal", style_th),
        Paragraph("Priority", style_th)
    ]
    audit_rows = [
        audit_headers,
        [
            Paragraph("<b>Render Pipeline</b>", style_td_bold),
            Paragraph("Legacy Built-in RP with standard materials in <code>Assets/</code>.", style_td),
            Paragraph("Missing modern Universal Render Pipeline (URP) features: SRP Batcher, volume-based post-processing, and flexible Shader Graph workflows.", style_td),
            Paragraph("<font color='#DC2626'><b>HIGH</b></font>", style_td)
        ],
        [
            Paragraph("<b>Vehicle Shading</b>", style_td_bold),
            Paragraph("Generic standard diffuse materials on tank hull and turret.", style_td),
            Paragraph("Lacks stylized character. Needs custom shaders (e.g. Toon/Cel shading, rim lighting, team color tinting, and damage flash feedback).", style_td),
            Paragraph("<font color='#DC2626'><b>HIGH</b></font>", style_td)
        ],
        [
            Paragraph("<b>Environment Art</b>", style_td_bold),
            Paragraph("Flat grey prototype cubes (<code>Ciathyza/Gridbox</code>) and floor.", style_td),
            Paragraph("Arena looks like an untextured test map. Needs stylized surface shading (tactical grid, hex outlines, or stylized textures) and arena framing.", style_td),
            Paragraph("<font color='#2563EB'><b>MEDIUM</b></font>", style_td)
        ],
        [
            Paragraph("<b>Weapon & Impact VFX</b>", style_td_bold),
            Paragraph("Basic projectile sphere; single generic explosion particle.", style_td),
            Paragraph("No muzzle flash, no shell tracer/trail, no dust kick-up when driving, and impacts lack energy, punch, and visual hierarchy.", style_td),
            Paragraph("<font color='#DC2626'><b>HIGH</b></font>", style_td)
        ],
        [
            Paragraph("<b>Lighting & Mood</b>", style_td_bold),
            Paragraph("1 default directional light; no shadows or color tuning.", style_td),
            Paragraph("Scene feels washed out and flat. Needs atmospheric directional lighting, ambient contrast, and a tuned Post-Processing Volume.", style_td),
            Paragraph("<font color='#2563EB'><b>MEDIUM</b></font>", style_td)
        ],
        [
            Paragraph("<b>Rendering Budget</b>", style_td_bold),
            Paragraph("Unbatched materials, potential particle overdraw spikes.", style_td),
            Paragraph("Materials not configured for GPU Instancing or SRP Batcher; unoptimized particle blending can cause frame rate drops on low-end hardware.", style_td),
            Paragraph("<font color='#D97706'><b>HIGH</b></font>", style_td)
        ]
    ]

    audit_table = Table(audit_rows, colWidths=[75, 120, 285, 60])
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
    # PAGE 2: TASKS 1 & 2 (PIPELINE, LIGHTING & SHADERS)
    # =========================================================================
    story.append(Paragraph("2. Candidate Tasks &amp; Requirements", style_h1))
    story.append(Paragraph(
        "Below are the primary technical art tasks to complete over the 2-day period. Balance visual flair with clean performance.",
        style_body
    ))
    story.append(Spacer(1, 3))

    # TASK 1: Pipeline & Lighting
    t1_box = [
        [
            Paragraph("<b>TASK 1: URP Pipeline Upgrade, Lighting &amp; Post-Processing</b>", style_td_bold),
            Paragraph("<font color='#7C3AED'><b>PIPELINE &amp; MOOD</b></font>", style_td)
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
        "<b>Goal:</b> Upgrade the project to Universal Render Pipeline (URP) on modern Unity LTS and establish a cohesive visual atmosphere.<br/>"
        "&bull; <b>URP Configuration:</b> Set up a clean URP Asset with balanced settings (HDR, Anti-Aliasing, appropriate Shadow Cascades &amp; Distance).<br/>"
        "&bull; <b>Material Conversion:</b> Convert existing materials cleanly to URP (ensure zero broken magenta shaders in the scene).<br/>"
        "&bull; <b>Lighting Setup:</b><br/>"
        "  - Directional Key Light with warm sunlight/moonlight and clean contact shadows.<br/>"
        "  - Colored ambient/rim fill to give 3D forms depth from the top-down camera angle.<br/>"
        "&bull; <b>Global Post-Processing Volume:</b><br/>"
        "  - <i>Bloom:</i> Tuned threshold for energetic glowing projectiles, lasers, and explosions without blinding blowouts.<br/>"
        "  - <i>Tonemapping &amp; Color Adjustments:</i> ACES or Neutral tonemapper with vibrant, rich contrast.<br/>"
        "  - <i>Vignette &amp; Ambient Occlusion:</i> Subtle vignette to frame the arena and SSAO to ground obstacles and tanks on the floor.",
        style_body
    )
    story.append(t1_desc)
    story.append(Spacer(1, 6))

    # TASK 2: Custom Shaders
    t2_box = [
        [
            Paragraph("<b>TASK 2: Custom Shaders (Stylized Tanks &amp; Arena Floor)</b>", style_td_bold),
            Paragraph("<font color='#0284C7'><b>SHADER CREATION</b></font>", style_td)
        ]
    ]
    t2_header = Table(t2_box, colWidths=[420, 120])
    t2_header.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), C_BG_ALT),
        ('BOX', (0, 0), (-1, -1), 1, C_ACCENT_CYAN),
        ('PADDING', (0, 0), (-1, -1), 3.5),
        ('ALIGN', (1, 0), (1, 0), 'RIGHT'),
    ]))
    story.append(t2_header)
    story.append(Spacer(1, 2))

    t2_desc = Paragraph(
        "<b>Goal:</b> Author custom shaders (using Shader Graph or HLSL) that give the game an intentional, stylized visual identity.<br/>"
        "&bull; <b>1. Stylized Vehicle Shader (Player &amp; Enemy Tanks):</b><br/>"
        "  - <i>Toon / Stylized Shading:</i> Stepped diffuse lighting or stylized ramp texture for clean, non-photorealistic look.<br/>"
        "  - <i>Dynamic Team Color Tint:</i> Expose properties to tint player (e.g. vibrant green/cyan) and enemy (e.g. orange/crimson).<br/>"
        "  - <i>Fresnel / Rim Lighting:</i> Subtle rim glow to make vehicles pop against the ground plane from top-down angles.<br/>"
        "  - <i>Hit-Flash / Damage Feedback:</i> A shader parameter (e.g. <code>_HitFlashAmount</code>) that smoothly pulses white or red when taking damage.<br/>"
        "&bull; <b>2. Stylized Arena Ground / Grid Shader:</b><br/>"
        "  - Procedural tactical grid, honeycomb/hex pattern, or stylized tiled surface that replaces flat prototype cubes.<br/>"
        "  - World-space UV mapping or triplanar projection to eliminate texture stretching across arena barriers.<br/>"
        "&bull; <i>(Bonus):</i> Dissolve or burn-away effect when tanks or obstacles are destroyed.",
        style_body
    )
    story.append(t2_desc)
    story.append(Spacer(1, 6))

    # Shader Specification Reference Table
    story.append(Paragraph("<b>Shader Architecture &amp; Parameter Matrix</b>", style_h2))

    shader_spec_data = [
        [
            Paragraph("Shader Target", style_th),
            Paragraph("Visual Techniques Used", style_th),
            Paragraph("Exposed Material Properties", style_th)
        ],
        [
            Paragraph("<b>Stylized Tank</b>", style_td_bold),
            Paragraph("Toon Ramp, Fresnel Rim Light, Hit Flash, Specular Cutoff", style_td),
            Paragraph("<code>_BaseColor</code>, <code>_RampThreshold</code>, <code>_RimColor</code>, <code>_HitFlash</code>", style_td)
        ],
        [
            Paragraph("<b>Arena Floor &amp; Grid</b>", style_td_bold),
            Paragraph("World-Space UVs, Procedural Grid Lines, Subtle Edge Fade", style_td),
            Paragraph("<code>_GridSize</code>, <code>_GridLineWidth</code>, <code>_GridColor</code>, <code>_GroundTint</code>", style_td)
        ],
        [
            Paragraph("<b>Projectile Energy</b>", style_td_bold),
            Paragraph("Additive/Alpha Glow, Fresnel Core, UV Pulse Animation", style_td),
            Paragraph("<code>_EnergyColor</code>, <code>_GlowIntensity</code>, <code>_PulseSpeed</code>", style_td)
        ]
    ]
    shader_table = Table(shader_spec_data, colWidths=[110, 210, 220])
    shader_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), C_PRIMARY_LIGHT),
        ('BOX', (0, 0), (-1, -1), 0.75, C_BORDER),
        ('INNERGRID', (0, 0), (-1, -1), 0.5, C_BORDER_LIGHT),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, C_BG_LIGHT]),
        ('PADDING', (0, 0), (-1, -1), 4),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
    ]))
    story.append(shader_table)

    story.append(PageBreak())

    # =========================================================================
    # PAGE 3: TASKS 3, 4, 5, 6 (VFX, JUICE, PROFILING & BUILD)
    # =========================================================================
    story.append(Paragraph("2. Candidate Tasks (Continued)", style_h1))
    story.append(Spacer(1, 3))

    # TASK 3: VFX & Particles
    t3_box = [
        [
            Paragraph("<b>TASK 3: Complete Visual Effects (VFX) Overhaul</b>", style_td_bold),
            Paragraph("<font color='#D97706'><b>VFX &amp; PARTICLES</b></font>", style_td)
        ]
    ]
    t3_header = Table(t3_box, colWidths=[420, 120])
    t3_header.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), C_BG_ALT),
        ('BOX', (0, 0), (-1, -1), 1, C_WARNING),
        ('PADDING', (0, 0), (-1, -1), 3.5),
        ('ALIGN', (1, 0), (1, 0), 'RIGHT'),
    ]))
    story.append(t3_header)
    story.append(Spacer(1, 2))

    t3_desc = Paragraph(
        "<b>Goal:</b> Build a responsive, readable visual effects suite for shooting, projectile flight, impacts, and vehicle motion.<br/>"
        "&bull; <b>1. Cannon Muzzle Flash:</b> Bright instant flash, expanding smoke puff, and shell ejection spark at the barrel tip.<br/>"
        "&bull; <b>2. Projectile Flight:</b> Energetic projectile model with a ribbon/trail renderer and emissive HDR glow that leaves a glowing wake.<br/>"
        "&bull; <b>3. Multi-Layered Impact Explosion:</b><br/>"
        "  - Core flash &amp; shockwave ring expanding along the ground plane.<br/>"
        "  - Secondary flying embers / sparks with gravity and bounce.<br/>"
        "  - Lingering dissipation smoke puff (with soft particles to prevent harsh clipping into the floor).<br/>"
        "&bull; <b>4. Driving Dust / Tread VFX:</b> Particle dust kicks up from the tracks when the tank turns or accelerates.<br/>"
        "&bull; <b>Performance Note:</b> Control particle lifetime and maximum counts to avoid particle overdraw spikes.",
        style_body
    )
    story.append(t3_desc)
    story.append(Spacer(1, 5))

    # TASK 4: Visual Polish & Motion
    t4_box = [
        [
            Paragraph("<b>TASK 4: Visual Juice, Motion &amp; Screen Feedback</b>", style_td_bold),
            Paragraph("<font color='#16A34A'><b>JUICE &amp; MOTION</b></font>", style_td_success)
        ]
    ]
    t4_header = Table(t4_box, colWidths=[420, 120])
    t4_header.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), C_BG_ALT),
        ('BOX', (0, 0), (-1, -1), 1, C_SUCCESS),
        ('PADDING', (0, 0), (-1, -1), 3.5),
        ('ALIGN', (1, 0), (1, 0), 'RIGHT'),
    ]))
    story.append(t4_header)
    story.append(Spacer(1, 2))

    t4_desc = Paragraph(
        "<b>Goal:</b> Bring the gameplay alive through animation principles, secondary motion, and dynamic visual feedback.<br/>"
        "&bull; <b>Turret Barrel Kickback:</b> Procedural kickback or animation on the cannon barrel when firing (quick snap backward, smooth spring forward).<br/>"
        "&bull; <b>Screen Shake Integration:</b> Wire Cinemachine Impulse to trigger satisfying screen shake on cannon shots and heavy explosions.<br/>"
        "&bull; <b>Stylized Aiming Reticle:</b> Polished in-world reticle with smooth lead indicator or target acquisition animation.<br/>"
        "&bull; <b>Damage Feedback:</b> Red hit-flash vignette or screen glitch when the player takes damage.",
        style_body
    )
    story.append(t4_desc)
    story.append(Spacer(1, 5))

    # TASK 5: Optimization & Report
    t5_box = [
        [
            Paragraph("<b>TASK 5: Tech Art Profiling &amp; Optimization Report</b>", style_td_bold),
            Paragraph("<font color='#DC2626'><b>PERFORMANCE BUDGET</b></font>", style_td_danger)
        ]
    ]
    t5_header = Table(t5_box, colWidths=[420, 120])
    t5_header.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), C_BG_ALT),
        ('BOX', (0, 0), (-1, -1), 1, C_DANGER),
        ('PADDING', (0, 0), (-1, -1), 3.5),
        ('ALIGN', (1, 0), (1, 0), 'RIGHT'),
    ]))
    story.append(t5_header)
    story.append(Spacer(1, 2))

    t5_desc = Paragraph(
        "<b>Goal:</b> Ensure the enhanced visuals run smoothly at 60+ FPS without hitching, and document performance budgets.<br/>"
        "&bull; <b>SRP Batcher &amp; GPU Instancing:</b> Verify that all custom shaders are compatible with the SRP Batcher and GPU Instancing.<br/>"
        "&bull; <b>Overdraw Audit:</b> Check the Scene View Overdraw mode to ensure particle systems do not create opaque fill-rate bottlenecks.<br/>"
        "&bull; <b>Texture Compression &amp; Atlasing:</b> Configure proper texture formats (e.g. BC7/ASTC) and power-of-two resolutions.<br/>"
        "&bull; <b>Written Tech Art Report (<code>TECH_ART_OPTIMIZATION.md</code>):</b><br/>"
        "  Provide a concise 1-page summary covering: Draw call count before/after, shader instruction count, lighting/shadow budget, and profile screenshots from the Unity Frame Debugger.",
        style_body
    )
    story.append(t5_desc)
    story.append(Spacer(1, 5))

    # TASK 6: Playable Build & Beauty Shots
    t6_box = [
        [
            Paragraph("<b>TASK 6: Playable Standalone Build &amp; Beauty Renders</b>", style_td_bold),
            Paragraph("<font color='#7C3AED'><b>FINAL DELIVERABLE</b></font>", style_td)
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
        "<b>Goal:</b> Export a working Windows 64-bit standalone build demonstrating the complete visual overhaul.<br/>"
        "&bull; Export a standalone executable (.exe) and verify lighting, post-processing, and shaders compile cleanly outside the editor.<br/>"
        "&bull; Include 3 to 4 high-resolution beauty screenshots (Before vs. After) or a short gameplay GIF in the repository.",
        style_body
    )
    story.append(t6_desc)

    story.append(PageBreak())

    # =========================================================================
    # PAGE 4: EVALUATION RUBRIC, SUBMISSION CHECKLIST & FAQ
    # =========================================================================
    story.append(Paragraph("3. Scoring Rubric &amp; Submission Checklist", style_h1))
    story.append(Paragraph(
        "Submissions are evaluated on a 100-point rubric focused on visual quality, technical execution, and rendering performance.",
        style_body
    ))
    story.append(Spacer(1, 3))

    rubric_headers = [
        Paragraph("Category", style_th),
        Paragraph("Points", style_th),
        Paragraph("Evaluation Criteria", style_th)
    ]

    rubric_rows = [
        rubric_headers,
        [
            Paragraph("<b>1. Pipeline &amp; Lighting</b>", style_td_bold),
            Paragraph("20 pts", style_td),
            Paragraph("Clean URP setup with zero magenta shaders. Cohesive lighting mood and well-balanced post-processing (Bloom, Color Grading, AO).", style_td)
        ],
        [
            Paragraph("<b>2. Custom Shaders</b>", style_td_bold),
            Paragraph("25 pts", style_td),
            Paragraph("Stylized tank shader (toon ramp, rim glow, hit-flash pulse) + arena floor shader. Clean Shader Graph / HLSL with exposed properties.", style_td)
        ],
        [
            Paragraph("<b>3. VFX &amp; Particle Feel</b>", style_td_bold),
            Paragraph("20 pts", style_td),
            Paragraph("Impactful cannon fire, glowing shell trail, multi-layered explosion (shockwave, sparks, smoke), and track dust. Good visual hierarchy.", style_td)
        ],
        [
            Paragraph("<b>4. Motion &amp; Juice</b>", style_td_bold),
            Paragraph("15 pts", style_td),
            Paragraph("Barrel kickback recoil, screen shake integration, stylized reticle, and clear damage feedback.", style_td)
        ],
        [
            Paragraph("<b>5. Tech Art Optimization</b>", style_td_bold),
            Paragraph("20 pts", style_td),
            Paragraph("SRP Batcher compatibility, minimal particle overdraw, proper texture compression, and concise <code>TECH_ART_OPTIMIZATION.md</code> report.", style_td)
        ],
        [
            Paragraph("<b>Total Score</b>", style_td_bold),
            Paragraph("<b>100 pts</b>", style_td_bold),
            Paragraph("<b>Passing score: 75+ points.</b> <i>(Bonus: +5 points for tank tread decal marks, dissolve effect, or animated track UVs).</i>", style_td_bold)
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
            Paragraph("<b>3. Tech Art Report</b>", style_td_bold),
            Paragraph("A short <code>TECH_ART_OPTIMIZATION.md</code> detailing draw calls, shader complexity, and Frame Debugger notes.", style_td),
            Paragraph("[  ] Done", style_td_bold)
        ],
        [
            Paragraph("<b>4. Beauty Screenshots</b>", style_td_bold),
            Paragraph("3 to 4 high-res screenshots showing off the upgraded lighting, shaders, and combat VFX.", style_td),
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
        "<b>Q: May I use Shader Graph or must I write code in HLSL?</b><br/>"
        "<i>A:</i> Either is completely acceptable. Unity Shader Graph is encouraged for fast iteration and readability. If you write HLSL directly, ensure it is cleanly structured with URP Core support.<br/><br/>"
        "<b>Q: Can I use third-party particle textures or meshes?</b><br/>"
        "<i>A:</i> Yes, you may use free textures, smoke sprites, or noise textures for your VFX. However, all shaders, materials, and particle system configurations must be authored by you.<br/><br/>"
        "<b>Q: What is the most important evaluation criteria?</b><br/>"
        "<i>A:</i> Visual cohesion and game feel! We want to see how you turn a flat, sterile prototype into a punchy, stylized experience while keeping rendering performance under control.",
        style_body
    )
    story.append(faq_content)

    doc.build(story, canvasmaker=NumberedCanvas)
    print(f"Document successfully created: {filename}")

if __name__ == "__main__":
    output_filename = "c:/Users/PC/Downloads/TopDownTank-main/TopDownTank-main/Unity_Technical_Artist_Assessment_TopDownTank.pdf"
    build_pdf(output_filename)
