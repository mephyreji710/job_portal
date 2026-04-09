import os

OUT = os.path.join(os.getcwd(), 'Project_Report.html')
open(OUT, 'w', encoding='utf-8').close()

def w(text):
    with open(OUT, 'a', encoding='utf-8') as f:
        f.write(text)

# ─── SVG Chen-notation ER diagram ────────────────────────────────
def er_svg(nodes, edges, vw=900, vh=460):
    ENT='#6d28d9'; ATT='#1d4ed8'; REL='#b45309'; WE='#059669'; LINE='#64748b'
    F="font-family='Segoe UI,Arial,sans-serif'"
    coords = {n[0]:(n[3],n[4]) for n in nodes}
    out = []
    out.append('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 %d %d" style="width:100%%;max-width:%dpx;display:block;margin:0 auto;">' % (vw,vh,vw))
    out.append('<rect width="%d" height="%d" fill="#f9fafb" rx="8"/>' % (vw,vh))
    for (a,b,lbl) in edges:
        if a in coords and b in coords:
            x1,y1=coords[a]; x2,y2=coords[b]
            out.append('<line x1="%d" y1="%d" x2="%d" y2="%d" stroke="%s" stroke-width="1.5"/>' % (x1,y1,x2,y2,LINE))
            if lbl:
                out.append('<text x="%d" y="%d" text-anchor="middle" %s font-size="9" fill="%s">%s</text>' % ((x1+x2)//2,(y1+y2)//2-4,F,LINE,lbl))
    for (nid,lbl,kind,cx,cy) in nodes:
        if kind=='E':
            out.append('<rect x="%d" y="%d" width="108" height="40" rx="4" fill="%s" stroke="white" stroke-width="1.5"/>' % (cx-54,cy-20,ENT))
            out.append('<text x="%d" y="%d" text-anchor="middle" %s font-size="11" font-weight="bold" fill="white">%s</text>' % (cx,cy+4,F,lbl))
        elif kind=='WE':
            out.append('<rect x="%d" y="%d" width="120" height="48" rx="4" fill="none" stroke="%s" stroke-width="2.5"/>' % (cx-60,cy-24,WE))
            out.append('<rect x="%d" y="%d" width="108" height="40" rx="4" fill="%s" stroke="white" stroke-width="1"/>' % (cx-54,cy-20,WE))
            out.append('<text x="%d" y="%d" text-anchor="middle" %s font-size="11" font-weight="bold" fill="white">%s</text>' % (cx,cy+4,F,lbl))
        elif kind=='A':
            out.append('<ellipse cx="%d" cy="%d" rx="44" ry="15" fill="%s" stroke="white" stroke-width="1"/>' % (cx,cy,ATT))
            out.append('<text x="%d" y="%d" text-anchor="middle" %s font-size="9" fill="white">%s</text>' % (cx,cy+3,F,lbl))
        elif kind=='R':
            pts='%d,%d %d,%d %d,%d %d,%d' % (cx,cy-28,cx+56,cy,cx,cy+28,cx-56,cy)
            out.append('<polygon points="%s" fill="%s" stroke="white" stroke-width="1.5"/>' % (pts,REL))
            out.append('<text x="%d" y="%d" text-anchor="middle" %s font-size="9" font-weight="bold" fill="white">%s</text>' % (cx,cy+3,F,lbl))
    out.append('</svg>')
    return '\n'.join(out)

LEGEND = '<div style="display:flex;gap:20px;flex-wrap:wrap;margin-bottom:12px;font-size:.78rem;color:#374151;"><span style="display:flex;align-items:center;gap:5px;"><svg width="20" height="14"><rect x="1" y="1" width="18" height="12" rx="3" fill="#6d28d9"/></svg>Entity</span><span style="display:flex;align-items:center;gap:5px;"><svg width="20" height="14"><ellipse cx="10" cy="7" rx="9" ry="6" fill="#1d4ed8"/></svg>Attribute</span><span style="display:flex;align-items:center;gap:5px;"><svg width="20" height="14"><polygon points="10,1 19,7 10,13 1,7" fill="#b45309"/></svg>Relationship</span><span style="display:flex;align-items:center;gap:5px;"><svg width="20" height="14"><rect x="1" y="1" width="18" height="12" rx="3" fill="#059669"/></svg>Weak Entity</span></div>'

def h(num,title,sub,col):
    return '<div class="ch-cover" style="border-left:6px solid %s;"><div class="ch-num" style="color:%s;">Chapter %s</div><div class="ch-title">%s</div><div class="ch-sub">%s</div></div>' % (col,col,num,title,sub)

def p(t): return '<p class="body-p">%s</p>' % t
def sh(t): return '<h3 class="sec-h">%s</h3>' % t
def sh2(t): return '<h4 class="sec-h2">%s</h4>' % t
def ul(*items): return '<ul class="body-ul">' + ''.join('<li>%s</li>'%i for i in items) + '</ul>'
def pg(content): return '<div class="page">%s</div>' % content
def er_pg(title,svg): return '<div class="er-landscape-page"><div class="er-page-title">%s &mdash; ER Diagram (Chen Notation)</div>%s%s</div>' % (title,LEGEND,svg)
def tbl(headers,rows,col='#1e293b'):
    th=''.join('<th>%s</th>'%h for h in headers)
    tr=''.join('<tr>'+''.join('<td>%s</td>'%c for c in r)+'</tr>' for r in rows)
    return '<table class="info-table"><thead style="background:%s;"><tr>%s</tr></thead><tbody>%s</tbody></table>' % (col,th,tr)

# ─── HTML HEAD + CSS ─────────────────────────────────────────────
CSS = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8"/>
<title>TalentBridge &#8212; Project Report</title>
<style>
*,*::before,*::after{box-sizing:border-box;margin:0;padding:0}
:root{--navy:#0f172a;--gray-900:#111827;--gray-700:#374151;--gray-500:#6b7280;
  --gray-200:#e5e7eb;--gray-100:#f3f4f6;--gray-50:#f9fafb;
  --c-accounts:#1d4ed8;--c-jobseeker:#059669;--c-resume:#7c3aed;
  --c-recruiter:#d97706;--c-jobs:#0891b2;--c-screening:#dc2626;
  --c-applications:#4f46e5;--c-feedback:#db2777;--c-interviews:#b45309;
  --c-notifications:#475569;}
body{font-family:'Segoe UI',Arial,sans-serif;background:#f0f4f8;color:#111827;font-size:11pt;line-height:1.65;}
.print-btn{position:fixed;bottom:24px;right:24px;background:#1d4ed8;color:#fff;border:none;
  padding:12px 24px;border-radius:10px;font-size:.9rem;font-weight:700;cursor:pointer;
  box-shadow:0 4px 16px rgba(0,0,0,.2);z-index:999;}
.print-btn:hover{background:#1e40af;}
.cover{background:linear-gradient(135deg,#0f172a,#1e3a5f);color:#fff;padding:80px 60px;
  text-align:center;min-height:100vh;display:flex;flex-direction:column;
  align-items:center;justify-content:center;page-break-after:always;}
.cover-badge{background:rgba(255,255,255,.1);border:1px solid rgba(255,255,255,.2);
  padding:6px 20px;border-radius:999px;font-size:.8rem;font-weight:600;
  letter-spacing:.08em;text-transform:uppercase;margin-bottom:24px;display:inline-block;}
.cover h1{font-size:3rem;font-weight:800;line-height:1.2;margin-bottom:12px;}
.cover h2{font-size:1.3rem;font-weight:400;opacity:.7;margin-bottom:40px;}
.cover-meta{background:rgba(255,255,255,.08);border-radius:16px;padding:28px 48px;
  display:inline-grid;grid-template-columns:1fr 1fr;gap:16px 48px;text-align:left;margin-top:20px;}
.meta-item label{font-size:.72rem;font-weight:700;text-transform:uppercase;
  letter-spacing:.1em;opacity:.5;display:block;margin-bottom:3px;}
.meta-item span{font-size:.95rem;font-weight:600;}
.cover-divider{width:80px;height:3px;background:linear-gradient(90deg,#3b82f6,#8b5cf6);
  border-radius:999px;margin:32px auto;}
.module-count-row{display:flex;gap:24px;margin-top:36px;flex-wrap:wrap;justify-content:center;}
.mc-chip{background:rgba(255,255,255,.12);border:1px solid rgba(255,255,255,.15);
  padding:10px 18px;border-radius:10px;text-align:center;}
.mc-chip .num{font-size:1.5rem;font-weight:800;display:block;}
.mc-chip .lbl{font-size:.68rem;opacity:.6;text-transform:uppercase;letter-spacing:.08em;}
.ch-cover{background:#fff;padding:64px 56px 48px;page-break-before:always;
  min-height:55vh;display:flex;flex-direction:column;justify-content:flex-end;}
.ch-num{font-size:.85rem;font-weight:700;text-transform:uppercase;letter-spacing:.12em;margin-bottom:8px;}
.ch-title{font-size:2rem;font-weight:800;color:#111827;line-height:1.2;margin-bottom:10px;}
.ch-sub{font-size:1rem;color:#6b7280;line-height:1.6;max-width:640px;}
.page{background:#fff;padding:48px 56px;page-break-before:always;}
.sec-h{font-size:1.15rem;font-weight:800;color:#0f172a;margin:32px 0 12px;
  padding-bottom:6px;border-bottom:2px solid #e5e7eb;}
.sec-h2{font-size:.97rem;font-weight:700;color:#1d4ed8;margin:20px 0 8px;}
.body-p{font-size:.9rem;color:#374151;line-height:1.75;margin-bottom:12px;}
.body-ul{margin:0 0 14px 24px;font-size:.88rem;color:#374151;line-height:1.8;}
.body-ul li{margin-bottom:5px;}
.info-table{width:100%;border-collapse:collapse;margin:16px 0;font-size:.82rem;
  background:#fff;border-radius:10px;overflow:hidden;box-shadow:0 1px 6px rgba(0,0,0,.06);}
.info-table thead th{color:#fff;font-size:.72rem;font-weight:700;text-transform:uppercase;
  letter-spacing:.07em;padding:10px 14px;text-align:left;}
.info-table tbody td{padding:9px 14px;border-bottom:1px solid #f3f4f6;vertical-align:top;color:#374151;}
.info-table tbody tr:last-child td{border-bottom:none;}
.info-table tbody tr:nth-child(even) td{background:#f9fafb;}
.er-landscape-page{background:#fff;padding:32px 40px;page-break-before:always;}
.er-page-title{font-size:1rem;font-weight:800;color:#0f172a;margin-bottom:14px;
  padding-bottom:8px;border-bottom:2px solid #e5e7eb;}
.section{padding:48px 40px;page-break-before:always;}
.section-header{margin-bottom:28px;}
.section-title{font-size:1.4rem;font-weight:800;color:#111827;display:flex;align-items:center;gap:10px;}
.section-title::before{content:'';display:inline-block;width:6px;height:22px;border-radius:3px;}
.section-sub{font-size:.82rem;color:#6b7280;margin-top:5px;}
.st-modules::before{background:#1d4ed8;}
.st-entities::before{background:#7c3aed;}
.st-relations::before{background:#4f46e5;}
.module-grid{display:grid;grid-template-columns:repeat(2,1fr);gap:16px;}
.mod-card{background:#fff;border-radius:14px;overflow:hidden;box-shadow:0 2px 12px rgba(0,0,0,.06);}
.mod-head{padding:14px 18px;display:flex;align-items:center;gap:12px;}
.mod-head h3{font-size:.93rem;font-weight:800;color:#fff;flex:1;}
.mod-head .mod-badge{background:rgba(255,255,255,.2);color:#fff;font-size:.68rem;font-weight:700;padding:3px 8px;border-radius:999px;}
.mod-body{padding:14px 18px;}
.mod-purpose{font-size:.8rem;color:#374151;line-height:1.55;margin-bottom:10px;}
.mod-models{display:flex;flex-wrap:wrap;gap:5px;}
.mod-model-chip{font-size:.7rem;font-weight:600;padding:3px 10px;border-radius:6px;border:1.5px solid;}
.m-accounts .mod-head{background:#1d4ed8;} .m-accounts .mod-model-chip{background:#dbeafe;color:#1d40af;border-color:#93c5fd;}
.m-jobseeker .mod-head{background:#059669;} .m-jobseeker .mod-model-chip{background:#d1fae5;color:#065f46;border-color:#6ee7b7;}
.m-resume .mod-head{background:#7c3aed;} .m-resume .mod-model-chip{background:#ede9fe;color:#5b21b6;border-color:#c4b5fd;}
.m-recruiter .mod-head{background:#d97706;} .m-recruiter .mod-model-chip{background:#fef3c7;color:#92400e;border-color:#fcd34d;}
.m-jobs .mod-head{background:#0891b2;} .m-jobs .mod-model-chip{background:#cffafe;color:#0e7490;border-color:#67e8f9;}
.m-screening .mod-head{background:#dc2626;} .m-screening .mod-model-chip{background:#fee2e2;color:#991b1b;border-color:#fca5a5;}
.m-applications .mod-head{background:#4f46e5;} .m-applications .mod-model-chip{background:#eef2ff;color:#3730a3;border-color:#a5b4fc;}
.m-feedback .mod-head{background:#db2777;} .m-feedback .mod-model-chip{background:#fce7f3;color:#9d174d;border-color:#f9a8d4;}
.m-interviews .mod-head{background:#b45309;} .m-interviews .mod-model-chip{background:#fef3c7;color:#78350f;border-color:#fcd34d;}
.m-notifications .mod-head{background:#475569;} .m-notifications .mod-model-chip{background:#f1f5f9;color:#334155;border-color:#cbd5e1;}
.entity-section{margin-bottom:36px;}
.entity-section-label{font-size:.72rem;font-weight:800;text-transform:uppercase;letter-spacing:.12em;color:#6b7280;margin-bottom:12px;padding-left:4px;}
.entities-row{display:grid;grid-template-columns:repeat(2,1fr);gap:16px;}
.entity-box{background:#fff;border-radius:12px;overflow:hidden;box-shadow:0 2px 10px rgba(0,0,0,.07);border:1px solid #e5e7eb;}
.entity-head{padding:11px 16px;display:flex;align-items:center;justify-content:space-between;}
.entity-name{font-size:.9rem;font-weight:800;color:#fff;}
.entity-app{font-size:.65rem;font-weight:600;color:rgba(255,255,255,.7);}
table.fields{width:100%;border-collapse:collapse;}
table.fields th{font-size:.65rem;font-weight:700;text-transform:uppercase;letter-spacing:.08em;color:#6b7280;padding:5px 14px;background:#f9fafb;border-bottom:1px solid #e5e7eb;}
table.fields td{font-size:.72rem;padding:5px 14px;border-bottom:1px solid #f3f4f6;vertical-align:top;}
table.fields tr:last-child td{border-bottom:none;}
.field-name{font-weight:600;color:#111827;font-family:'Consolas','Fira Code',monospace;}
.field-type{color:#6b7280;} .field-note{color:#9ca3af;font-size:.65rem;}
.badge-pk{display:inline-block;background:#fef9c3;color:#854d0e;border:1px solid #fde68a;font-size:.58rem;font-weight:700;padding:1px 5px;border-radius:4px;margin-left:4px;}
.badge-fk{display:inline-block;background:#dbeafe;color:#1d40af;border:1px solid #93c5fd;font-size:.58rem;font-weight:700;padding:1px 5px;border-radius:4px;margin-left:4px;}
.badge-o2o{display:inline-block;background:#ede9fe;color:#5b21b6;border:1px solid #c4b5fd;font-size:.58rem;font-weight:700;padding:1px 5px;border-radius:4px;margin-left:4px;}
.eh-accounts{background:#1d4ed8;} .eh-jobseeker{background:#059669;} .eh-resume{background:#7c3aed;}
.eh-recruiter{background:#d97706;} .eh-jobs{background:#0891b2;} .eh-screening{background:#dc2626;}
.eh-applications{background:#4f46e5;} .eh-feedback{background:#db2777;} .eh-interviews{background:#b45309;}
.eh-notifications{background:#475569;}
.rel-table{width:100%;border-collapse:collapse;background:#fff;border-radius:12px;overflow:hidden;box-shadow:0 2px 10px rgba(0,0,0,.07);}
.rel-table th{background:#1e293b;color:#fff;font-size:.72rem;font-weight:700;text-transform:uppercase;letter-spacing:.08em;padding:10px 16px;text-align:left;}
.rel-table td{padding:9px 16px;font-size:.78rem;border-bottom:1px solid #f3f4f6;vertical-align:middle;}
.rel-table tr:last-child td{border-bottom:none;}
.rel-table tr:nth-child(even) td{background:#f9fafb;}
.rel-type{display:inline-block;font-size:.65rem;font-weight:700;padding:2px 8px;border-radius:999px;white-space:nowrap;}
.rt-fk{background:#dbeafe;color:#1d40af;} .rt-o2o{background:#ede9fe;color:#5b21b6;} .rt-m2m{background:#d1fae5;color:#065f46;}
.t-from{font-weight:700;font-family:monospace;color:#111827;} .t-to{font-weight:700;font-family:monospace;color:#1d4ed8;} .t-desc{color:#6b7280;font-size:.72rem;}
.legend{display:flex;gap:20px;flex-wrap:wrap;background:#fff;border-radius:12px;padding:16px 20px;box-shadow:0 1px 6px rgba(0,0,0,.05);margin-bottom:24px;}
.legend-item{display:flex;align-items:center;gap:7px;font-size:.75rem;font-weight:600;color:#374151;}
.legend-dot{width:12px;height:12px;border-radius:3px;}
.toc-page{background:#fff;padding:60px 80px;page-break-after:always;}
.toc-h{font-size:1.5rem;font-weight:800;color:#0f172a;margin-bottom:32px;padding-bottom:10px;border-bottom:3px solid #e5e7eb;}
.toc-row{display:flex;justify-content:space-between;align-items:baseline;padding:8px 0;border-bottom:1px dotted #d1d5db;font-size:.9rem;}
.toc-ch{font-weight:700;color:#1d4ed8;min-width:100px;display:inline-block;}
.toc-pg{color:#9ca3af;font-size:.8rem;}
.abstract-page{background:#fff;padding:80px 80px;page-break-after:always;}
.hl-box{background:#f0f9ff;border-left:4px solid #0891b2;padding:16px 20px;margin:16px 0;border-radius:0 8px 8px 0;font-size:.88rem;color:#0c4a6e;line-height:1.6;}
.code-block{background:#1e293b;color:#e2e8f0;padding:16px 20px;border-radius:8px;font-family:'Consolas',monospace;font-size:.8rem;line-height:1.6;margin:12px 0;white-space:pre-wrap;}
@media print{
  body{background:#fff;}
  .print-btn{display:none!important;}
  @page{size:A4;margin:12mm;}
  .er-landscape-page{page:landscape-page;}
  @page landscape-page{size:A4 landscape;margin:10mm;}
}
</style>
</head>
<body>
<button class="print-btn" onclick="window.print()">&#128424; Save as PDF</button>
"""

w(CSS)
print("Head+CSS done")

# ─── COVER ──────────────────────────────────────────────────────
w("""<div class="cover">
<div class="cover-badge">Academic Project Report &mdash; 2026</div>
<h1>TalentBridge</h1>
<h2>Job Portal with Intelligent Resume Screening</h2>
<div class="cover-divider"></div>
<p style="opacity:.6;font-size:.9rem;max-width:560px;line-height:1.7;">A full-stack Django web application connecting job seekers with recruiters,
featuring AI-powered resume screening, automated skill matching, an integrated resume builder,
and a complete application lifecycle management system.</p>
<div class="cover-meta">
<div class="meta-item"><label>Framework</label><span>Django 5.2.4 (Python 3.11)</span></div>
<div class="meta-item"><label>Database</label><span>SQLite / PostgreSQL</span></div>
<div class="meta-item"><label>Frontend</label><span>HTML5 / CSS3 (No JS frameworks)</span></div>
<div class="meta-item"><label>Deployment</label><span>PythonAnywhere</span></div>
<div class="meta-item"><label>Total Modules</label><span>10 Django Applications</span></div>
<div class="meta-item"><label>Database Models</label><span>20 Models, 18 Relationships</span></div>
</div>
<div class="module-count-row">
<div class="mc-chip"><span class="num">10</span><span class="lbl">App Modules</span></div>
<div class="mc-chip"><span class="num">20</span><span class="lbl">DB Models</span></div>
<div class="mc-chip"><span class="num">18</span><span class="lbl">Relationships</span></div>
<div class="mc-chip"><span class="num">5</span><span class="lbl">Resume Templates</span></div>
<div class="mc-chip"><span class="num">3</span><span class="lbl">User Roles</span></div>
</div>
</div>
""")

# ─── ABSTRACT ───────────────────────────────────────────────────
w("""<div class="abstract-page">
<h2 style="font-size:1.6rem;font-weight:800;color:#0f172a;margin-bottom:24px;padding-bottom:10px;border-bottom:3px solid #e5e7eb;">Abstract</h2>
<p class="body-p">TalentBridge is a comprehensive, full-stack web application developed using the Django 5.2.4 framework and Python 3.11.
It addresses the critical challenge of efficiently connecting job seekers with recruiters while automating the traditionally time-consuming
process of resume screening and candidate evaluation.</p>
<p class="body-p">The system implements a multi-role architecture supporting three distinct user types: Administrators who manage the platform,
Recruiters who post jobs and screen candidates, and Job Seekers who search for opportunities and submit applications.
Each role has a dedicated dashboard and workflow optimised for their specific needs.</p>
<p class="body-p">The core innovation of TalentBridge is its intelligent resume screening engine (Module 6), which computes a weighted compatibility
score between a candidate's profile and a job posting using four dimensions: Skills Match (40%), Experience Alignment (25%),
Education Level (15%), and Keyword Relevance (20%). This automated scoring dramatically reduces recruiter workload and ensures
objective candidate evaluation.</p>
<p class="body-p">Beyond screening, the platform provides a complete job application lifecycle: from job discovery and one-click application
submission, through recruiter review, shortlisting, and interview scheduling, to final hiring decisions and bidirectional feedback.
The integrated resume builder generates professional, ATS-optimised resumes from structured profile data using five customisable templates.</p>
<p class="body-p">The project is implemented using Django's MVT (Model-View-Template) architecture with SQLite for development
and designed for PostgreSQL in production. The frontend uses pure HTML5 and CSS3 with no external JavaScript frameworks,
ensuring fast load times, accessibility, and ease of maintenance.</p>
<p class="body-p" style="margin-top:24px;"><strong>Keywords:</strong> Django, Job Portal, Resume Screening, NLP, Skill Matching, Web Application, Python, Full-Stack Development, Career Platform, Automated Recruitment</p>
</div>
""")

# ─── TABLE OF CONTENTS ──────────────────────────────────────────
def toc_row(ch, title, pg):
    return '<div class="toc-row"><span><span class="toc-ch">%s</span>%s</span><span class="toc-pg">%s</span></div>' % (ch, title, pg)

w('<div class="toc-page"><div class="toc-h">Table of Contents</div>')
toc_items = [
    ("Abstract","","2"),
    ("Chapter 1","Project Introduction &amp; Objectives","4"),
    ("Chapter 2","Technology Stack &amp; Architecture","7"),
    ("Chapter 3","Module 1: Authentication &amp; User Management (accounts)","10"),
    ("Chapter 4","Module 2: Job Seeker Profile Management (jobseeker)","14"),
    ("Chapter 5","Module 3: Resume Upload, Parsing &amp; Builder (resume)","18"),
    ("Chapter 6","Module 4: Company &amp; Recruiter Panel (recruiter)","23"),
    ("Chapter 7","Module 5: Job Posting &amp; Board (jobs)","27"),
    ("Chapter 8","Module 6: Intelligent Resume Screening (screening)","32"),
    ("Chapter 9","Module 7: Job Application Lifecycle (applications)","37"),
    ("Chapter 10","Module 8: Feedback &amp; Rating System (feedback)","42"),
    ("Chapter 11","Module 9: Interview Scheduling (interviews)","46"),
    ("Chapter 12","Module 10: Notification System (notifications)","50"),
    ("Chapter 13","Module Overview &mdash; All 10 Applications","54"),
    ("Chapter 14","Database Design &mdash; 20 Entity Tables","56"),
    ("Chapter 15","Entity-Relationship Diagrams (Chen Notation)","70"),
    ("Chapter 16","System Relationships &mdash; 18 Connections","74"),
    ("Chapter 17","Testing &amp; Verification","78"),
    ("Chapter 18","Security Implementation","82"),
    ("Chapter 19","Deployment &amp; Configuration","85"),
    ("Chapter 20","Conclusion &amp; Future Work","89"),
]
for (ch, title, pg_n) in toc_items:
    w(toc_row(ch, title, pg_n))
w('</div>')
print("Cover+Abstract+TOC done")

# ─── CHAPTER 1: INTRODUCTION ────────────────────────────────────
w(h("1","Project Introduction &amp; Objectives","Overview of TalentBridge, its purpose, scope, and the problems it solves","#1d4ed8"))
w(pg(
    sh("1.1  Background and Motivation") +
    p("In today's competitive job market, the process of matching job seekers with suitable employment opportunities remains highly manual, "
      "time-consuming, and prone to bias. Recruiters spend an average of 6 seconds reviewing each resume before deciding whether to proceed, "
      "leading to overlooked talent and inefficient hiring pipelines. At the same time, job seekers struggle to identify positions where their "
      "skills and experience genuinely align with employer requirements.") +
    p("TalentBridge was conceived to address these dual challenges by building a unified platform where intelligent automation handles "
      "the repetitive aspects of recruitment — resume parsing, skill extraction, compatibility scoring — while preserving the human "
      "element for final decision-making and interpersonal communication.") +

    sh("1.2  Problem Statement") +
    p("The following core problems were identified during the requirements analysis phase:") +
    ul("Manual resume screening is slow: A typical recruiter receives 250+ applications per job posting. Reading each one thoroughly is impractical.",
       "Subjective evaluation leads to bias: Without a standardised scoring framework, similar candidates are evaluated inconsistently.",
       "Job seekers lack feedback: Applicants rarely receive meaningful feedback explaining why they were rejected.",
       "Resume quality varies widely: Many candidates lack the skills to present their qualifications effectively.",
       "Application tracking is fragmented: Recruiters use spreadsheets and email threads to track candidate progress.",
       "Interview scheduling is manual: Coordinating interview times across multiple stakeholders wastes hours per hiring cycle.") +

    sh("1.3  Proposed Solution") +
    p("TalentBridge provides an integrated web platform with the following solution components:") +
    ul("Automated Resume Parsing: PDF/DOCX resumes are parsed using pdfplumber and python-docx to extract skills, experience, and education.",
       "Intelligent Scoring Engine: A four-dimensional weighted algorithm computes objective compatibility scores between candidates and jobs.",
       "Structured Profile System: Job seekers build detailed profiles with skills, education, experience, and certifications.",
       "Resume Builder: Five professionally designed, ATS-optimised templates allow candidates to generate polished resumes.",
       "Application Lifecycle Management: Full workflow from application submission through review, shortlisting, hiring, or rejection.",
       "Interview Scheduling Module: Recruiters schedule and manage video, phone, or on-site interviews with automated status tracking.",
       "Notification System: Real-time in-app notifications keep all parties informed of status changes and upcoming events.") +

    sh("1.4  Project Scope") +
    p("TalentBridge is scoped as a web-based application accessible via desktop and mobile browsers. It is built as an academic "
      "project demonstrating full-stack Django development with emphasis on clean architecture, database design, and user experience. "
      "The scope includes:") +
    ul("User registration, authentication, and role-based access control",
       "Job seeker profile creation with skills, education, work experience, and certifications",
       "Resume upload, automated parsing, and keyword extraction",
       "An integrated resume builder with five templates and customisation options",
       "Recruiter company profile management and HR team management",
       "Job posting creation with required skills, salary range, and deadline management",
       "Public job board with browsing and saved jobs functionality",
       "Automated resume-to-job matching with weighted scoring",
       "Job application submission, status tracking, and withdrawal",
       "Bidirectional feedback and ratings between candidates and companies",
       "Interview scheduling and management",
       "In-app notification system for key lifecycle events")
))
w(pg(
    sh("1.5  Project Objectives") +
    p("The primary objectives of the TalentBridge project are:") +
    ul("Design and implement a scalable, maintainable Django web application following MVT architecture best practices.",
       "Create a custom user model supporting multiple roles with role-based dashboard routing and access control.",
       "Develop an automated resume parsing system capable of extracting structured data from PDF and DOCX files.",
       "Implement an intelligent matching algorithm that objectively scores candidate-job compatibility.",
       "Build a full CRUD interface for job postings with status lifecycle management.",
       "Create a resume builder generating professional documents from structured profile data.",
       "Implement a complete application tracking system with recruiter workflow support.",
       "Design a normalised relational database schema with 20 models and proper foreign key relationships.",
       "Ensure the UI is responsive, accessible, and works without JavaScript dependencies.") +

    sh("1.6  Target Users") +
    tbl(["Role","Count (typical)","Primary Functions","Dashboard"],
        [["Job Seeker","Many (thousands)","Browse jobs, apply, build resume, track applications","Indigo-themed dashboard"],
         ["Recruiter","Moderate (hundreds)","Post jobs, screen candidates, schedule interviews","Green-themed company panel"],
         ["Admin","Few (system admins)","Manage users, content moderation, system oversight","Django Admin interface"]],
        "#1d4ed8") +

    sh("1.7  Academic Context") +
    p("This project is submitted as a final year academic project demonstrating proficiency in full-stack web development, "
      "database design, algorithm implementation, and software engineering principles. The project follows industry-standard "
      "practices including version control (Git), modular application architecture, and separation of concerns.") +
    p("The choice of Django as the framework was deliberate: its 'batteries-included' philosophy provides built-in solutions "
      "for authentication, ORM, admin interface, and form handling, allowing focus on domain-specific logic rather than "
      "infrastructure concerns. Python 3.11 provides improved performance and enhanced error messages compared to earlier versions.")
))

print("Chapter 1 done")

# ─── CHAPTER 2: TECHNOLOGY STACK ────────────────────────────────
w(h("2","Technology Stack &amp; Architecture","Frameworks, libraries, design patterns, and system architecture","#1d4ed8"))
w(pg(
    sh("2.1  Technology Stack Overview") +
    tbl(["Layer","Technology","Version","Purpose"],
        [["Backend Framework","Django","5.2.4","MVT web framework"],
         ["Programming Language","Python","3.11","Core language"],
         ["Database (Dev)","SQLite","3.x","File-based relational database"],
         ["Database (Prod)","PostgreSQL","15+","Production-grade RDBMS"],
         ["Resume Parsing","pdfplumber","0.9+","PDF text extraction"],
         ["Resume Parsing","python-docx","0.8+","DOCX text extraction"],
         ["Frontend","HTML5 / CSS3","—","Markup and styling (no frameworks)"],
         ["Deployment","PythonAnywhere","—","Cloud hosting platform"],
         ["Version Control","Git","2.x","Source code management"]],
        "#0891b2") +

    sh("2.2  Django MVT Architecture") +
    p("TalentBridge strictly follows Django's Model-View-Template (MVT) pattern:") +
    ul("<strong>Models</strong>: Python classes mapping to database tables. Each of the 10 apps defines its own models. "
       "Django's ORM handles SQL generation, migrations, and relationship management.",
       "<strong>Views</strong>: Python functions (function-based views) that handle HTTP requests, interact with models, "
       "apply business logic, and return rendered HTML responses.",
       "<strong>Templates</strong>: HTML files with Django template language for dynamic content rendering. "
       "All templates are stored in <code>jobportal/templates/{app_name}/</code>.",
       "<strong>URLs</strong>: Each app has its own <code>urls.py</code> with named URL patterns, "
       "included into the root URL configuration with namespaces.") +

    sh("2.3  Application Structure") +
    p("The project follows Django's recommended app-per-domain structure:") +
    tbl(["App","Responsibility","Key Files"],
        [["accounts","Authentication, user management","models.py, views.py, backends.py"],
         ["jobseeker","Candidate profile CRUD","models.py, views.py, forms.py"],
         ["resume","Upload, parsing, builder","models.py, views.py, parser.py"],
         ["recruiter","Company profile management","models.py, views.py"],
         ["jobs","Job posting management","models.py, views.py, forms.py"],
         ["screening","Match scoring engine","models.py, views.py, scorer.py"],
         ["applications","Application lifecycle","models.py, views.py, forms.py"],
         ["feedback","Ratings and reviews","models.py, views.py"],
         ["interviews","Interview scheduling","models.py, views.py"],
         ["notifications","In-app notifications","models.py, views.py"]],
        "#059669")
))
w(pg(
    sh("2.4  Database Design Principles") +
    p("The database follows third normal form (3NF) to minimise redundancy. Key design decisions include:") +
    ul("Custom User model extending AbstractUser to add a <code>role</code> field, avoiding the complexity of a separate Profile table for auth.",
       "One-to-One relationships for profile models (RecruiterProfile, JobSeekerProfile) allow extending User without modifying the auth model.",
       "Foreign Key relationships enforce referential integrity at the database level.",
       "Unique-together constraints prevent duplicate applications (one per user per job) and duplicate match scores.",
       "<code>auto_now_add=True</code> and <code>auto_now=True</code> fields for audit trails on all important models.",
       "ManyToMany relationships avoided where possible; junction table approach used instead for better control.") +

    sh("2.5  Authentication &amp; Security") +
    p("Security implementation follows Django best practices:") +
    ul("Custom email-based authentication backend replaces the default username-based login.",
       "CSRF protection on all POST forms via Django's built-in CSRF middleware.",
       "Login-required decorators on all authenticated views.",
       "Role-based access control: recruiters cannot access job seeker features and vice versa.",
       "Password hashing using Django's default PBKDF2 algorithm with SHA256.",
       "File upload validation restricts resume uploads to PDF and DOCX formats.",
       "Environment variables used for SECRET_KEY and database credentials.") +

    sh("2.6  URL Architecture") +
    tbl(["Prefix","Namespace","Description"],
        [["/accounts/","accounts","Login, register, logout, password reset, dashboards"],
         ["/jobseeker/","jobseeker","Profile CRUD (skills, education, experience, certs)"],
         ["/resume/","resume","Upload, parse, view, delete; builder CRUD"],
         ["/recruiter/","recruiter","Company panel, team management"],
         ["/jobs/","jobs","Job board, posting management, detail views"],
         ["/screening/","screening","Match score computation and result views"],
         ["/applications/","applications","Apply, withdraw, my-applications, recruiter applicant list"],
         ["/feedback/","feedback","Leave review, view feedback"],
         ["/interviews/","interviews","Schedule, view, update interview"],
         ["/notifications/","notifications","Notification list, mark read"]],
        "#7c3aed") +

    sh("2.7  Template Organisation") +
    p("All templates are stored under <code>jobportal/templates/</code> with one subdirectory per app. "
      "Templates use a base template inheritance hierarchy: <code>accounts/base.html</code> for general pages, "
      "<code>accounts/base_profile.html</code> for job seeker pages, and <code>recruiter/base_recruiter.html</code> for recruiter pages. "
      "CSS is embedded in templates rather than separate static files for simplicity and to reduce HTTP requests.")
))

print("Chapter 2 done")

# ─── CHAPTER 3: ACCOUNTS MODULE ─────────────────────────────────
w(h("3","Module 1: Authentication &amp; User Management","The accounts app — custom user model, email login, role-based routing","#1d4ed8"))
w(pg(
    sh("3.1  Module Overview") +
    p("The <strong>accounts</strong> app is the foundation of TalentBridge. It manages user registration, authentication, "
      "profile data, and role-based access control for the entire platform. Every other module depends on the User model "
      "defined here.") +
    tbl(["Property","Value"],
        [["Django App Name","accounts"],
         ["Models","User (custom AbstractUser), RecruiterProfile, JobSeekerProfile (basic)"],
         ["Authentication Backend","accounts.backends.EmailBackend"],
         ["Login Identifier","Email address (not username)"],
         ["Password Reset","Email-based token (console backend in dev)"],
         ["User Roles","admin, recruiter, job_seeker"]],
        "#1d4ed8") +

    sh("3.2  Custom User Model") +
    p("Django's default User model uses username as the login identifier. TalentBridge replaces this with a custom "
      "User model that extends <code>AbstractUser</code> and adds a <code>role</code> CharField. "
      "This is defined in <code>accounts/models.py</code> and referenced via <code>AUTH_USER_MODEL = 'accounts.User'</code> "
      "in settings.") +
    tbl(["Field","Type","Description"],
        [["id","AutoField (PK)","Auto-generated primary key"],
         ["username","CharField","Inherited from AbstractUser (unique)"],
         ["email","EmailField","Used as the login identifier"],
         ["first_name","CharField","Inherited from AbstractUser"],
         ["last_name","CharField","Inherited from AbstractUser"],
         ["phone","CharField(20)","Optional phone number"],
         ["role","CharField","admin | recruiter | job_seeker"],
         ["is_active","BooleanField","Account activation status (inherited)"],
         ["date_joined","DateTimeField","Registration timestamp (inherited)"],
         ["password","CharField","Hashed password (inherited)"]],
        "#374151") +

    sh("3.3  Email Authentication Backend") +
    p("The custom backend <code>accounts/backends.py</code> overrides Django's default authentication to look up users by "
      "email instead of username. This allows users to register once with an email and never need to remember a separate username. "
      "The backend is registered in settings via <code>AUTHENTICATION_BACKENDS</code>.")
))
w(pg(
    sh("3.4  Recruiter Profile Model") +
    p("When a user registers as a Recruiter, a <code>RecruiterProfile</code> is created via a post-save signal "
      "or explicitly in the registration view. This profile stores company information.") +
    tbl(["Field","Type","Notes"],
        [["user","OneToOneField(User)","Links to the User model"],
         ["company_name","CharField","Name of the recruiting company"],
         ["company_logo","ImageField","Uploaded company logo"],
         ["industry","CharField","e.g., Technology, Finance, Healthcare"],
         ["company_size","CharField","Employee count range"],
         ["website","URLField","Company website URL"],
         ["description","TextField","Rich company description"],
         ["tagline","CharField","Short marketing tagline"],
         ["founded_year","IntegerField","Year the company was founded"],
         ["location","CharField","Head office location"]],
        "#d97706") +

    sh("3.5  Role-Based Dashboard Routing") +
    p("After login, the view in <code>accounts/views.py</code> checks the user's role and redirects:") +
    ul("admin → Django admin panel (<code>/admin/</code>)",
       "recruiter → Company recruiter panel (<code>/recruiter/panel/</code>)",
       "job_seeker → Job seeker dashboard (<code>/accounts/jobseeker-dashboard/</code>)") +
    p("Each role's dashboard shows role-specific statistics, quick actions, and navigation. Role-checking decorators "
      "are applied to all sensitive views to prevent cross-role access.") +

    sh("3.6  Registration Workflow") +
    p("The registration process follows these steps:") +
    ul("User visits <code>/accounts/register/</code> and selects role (recruiter or job seeker)",
       "Form validates email uniqueness, password strength, and required fields",
       "On success: User object is created, role is assigned, basic profile is initialised",
       "User is automatically logged in and redirected to their role-specific dashboard",
       "A welcome message is displayed using Django's messages framework") +

    sh("3.7  Password Reset Flow") +
    p("Django's built-in password reset is configured with:") +
    ul("Token-based reset links sent via email (console backend in development)",
       "Custom email templates for the reset email and confirmation messages",
       "24-hour token expiry for security",
       "HTTPS-safe link generation for production deployment") +

    sh("3.8  Views Summary") +
    tbl(["View","URL","Method","Description"],
        [["register","accounts/register/","GET/POST","New user registration with role selection"],
         ["login_view","accounts/login/","GET/POST","Email + password authentication"],
         ["logout_view","accounts/logout/","POST","Secure logout with CSRF"],
         ["jobseeker_dashboard","accounts/dashboard/","GET","Job seeker home with stats"],
         ["password_reset","accounts/password-reset/","GET/POST","Email token reset flow"]],
        "#1d4ed8")
))

# ACCOUNTS ER Diagram
nodes_accounts = [
    ("user","User","E",220,120),
    ("rp","RecruiterProfile","E",540,120),
    ("jsp","JobSeekerProfile","E",540,300),
    ("u_email","email","A",80,60),
    ("u_role","role","A",80,180),
    ("u_name","first_name","A",220,40),
    ("u_phone","phone","A",360,40),
    ("rp_co","company","A",680,80),
    ("rp_ind","industry","A",780,160),
    ("jsp_head","headline","A",780,300),
    ("jsp_loc","location","A",680,360),
    ("rel_rp","has","R",380,120),
    ("rel_jsp","has","R",380,300),
]
edges_accounts = [
    ("user","u_email",""), ("user","u_role",""), ("user","u_name",""),("user","u_phone",""),
    ("user","rel_rp","1"), ("rel_rp","rp","1"),
    ("user","rel_jsp","1"), ("rel_jsp","jsp","1"),
    ("rp","rp_co",""), ("rp","rp_ind",""),
    ("jsp","jsp_head",""), ("jsp","jsp_loc",""),
]
w(er_pg("Module 1: accounts", er_svg(nodes_accounts, edges_accounts, 900, 440)))

print("Chapter 3 done")

# ─── CHAPTER 4: JOBSEEKER MODULE ────────────────────────────────
w(h("4","Module 2: Job Seeker Profile Management","The jobseeker app — detailed profile, skills, education, experience, certifications","#059669"))
w(pg(
    sh("4.1  Module Overview") +
    p("The <strong>jobseeker</strong> app provides a comprehensive profile management system for job seekers. "
      "It goes far beyond a basic profile by capturing structured professional data including multiple skills "
      "with proficiency levels, complete education history, detailed work experience with duration calculations, "
      "and professional certifications. This structured data is the foundation for the intelligent screening engine.") +
    tbl(["Property","Value"],
        [["Django App Name","jobseeker"],
         ["Models","JobSeekerProfile, Skill, Education, Experience, Certification"],
         ["Profile URL","jobseeker/profile/"],
         ["Features","CRUD for all profile sections, completeness score, profile picture"]],
        "#059669") +

    sh("4.2  JobSeekerProfile Model") +
    tbl(["Field","Type","Notes"],
        [["user","OneToOneField(User)","Links to the User model"],
         ["headline","CharField","Professional headline (e.g., 'Senior Python Developer')"],
         ["bio","TextField","Professional summary / about me"],
         ["location","CharField","City, Country"],
         ["profile_picture","ImageField","Uploaded profile photo"],
         ["linkedin_url","URLField","LinkedIn profile link"],
         ["github_url","URLField","GitHub profile link"],
         ["portfolio_url","URLField","Personal portfolio website"],
         ["desired_role","CharField","Target job title"],
         ["desired_salary","DecimalField","Expected salary"],
         ["availability","CharField","Immediate / 2 weeks / 1 month"],
         ["work_type","CharField","On-site / Remote / Hybrid"],
         ["is_public","BooleanField","Whether profile is visible to recruiters"]],
        "#059669") +

    sh("4.3  Skill Model") +
    p("The Skill model stores individual skills with proficiency levels. One job seeker can have many skills.") +
    tbl(["Field","Type","Notes"],
        [["id","AutoField (PK)","Auto-generated"],
         ["profile","ForeignKey(JobSeekerProfile)","Parent profile (CASCADE delete)"],
         ["name","CharField","Skill name (e.g., Python, Django, React)"],
         ["proficiency","IntegerField","1=Beginner, 2=Intermediate, 3=Advanced, 4=Expert"],
         ["years","DecimalField","Years of experience with this skill"],
         ["is_primary","BooleanField","Whether this is a primary/featured skill"]],
        "#374151")
))
w(pg(
    sh("4.4  Education Model") +
    tbl(["Field","Type","Notes"],
        [["id","AutoField (PK)","Auto-generated"],
         ["profile","ForeignKey(JobSeekerProfile)","Parent profile"],
         ["institution","CharField","University / College / School name"],
         ["degree","CharField","Bachelor's, Master's, PhD, Diploma, etc."],
         ["field_of_study","CharField","e.g., Computer Science"],
         ["start_year","IntegerField","Year education began"],
         ["end_year","IntegerField","Year of graduation (null if current)"],
         ["grade","CharField","GPA, percentage, or grade classification"],
         ["is_current","BooleanField","Currently studying here"],
         ["description","TextField","Achievements, thesis, relevant coursework"]],
        "#374151") +

    sh("4.5  Experience Model") +
    tbl(["Field","Type","Notes"],
        [["id","AutoField (PK)","Auto-generated"],
         ["profile","ForeignKey(JobSeekerProfile)","Parent profile"],
         ["company","CharField","Employer company name"],
         ["role","CharField","Job title held"],
         ["location","CharField","Office location"],
         ["start_date","DateField","Employment start date"],
         ["end_date","DateField","Employment end date (null if current)"],
         ["is_current","BooleanField","Currently employed here"],
         ["description","TextField","Responsibilities and achievements"],
         ["skills_used","CharField","Comma-separated skills used in this role"]],
        "#374151") +

    sh("4.6  Certification Model") +
    tbl(["Field","Type","Notes"],
        [["id","AutoField (PK)","Auto-generated"],
         ["profile","ForeignKey(JobSeekerProfile)","Parent profile"],
         ["name","CharField","Certification name"],
         ["issuer","CharField","Issuing organisation (e.g., Google, AWS)"],
         ["issued_date","DateField","Date certificate was awarded"],
         ["expiry_date","DateField","Expiry date (null if no expiry)"],
         ["credential_id","CharField","Unique credential identifier"],
         ["credential_url","URLField","Verification link"]],
        "#374151") +

    sh("4.7  Profile Completeness Scoring") +
    p("The profile view calculates a completeness percentage to encourage users to fill in all sections:") +
    ul("Has profile picture: +10%",
       "Has headline and bio: +10%",
       "Has at least one skill: +20%",
       "Has education history: +20%",
       "Has work experience: +20%",
       "Has at least one certification: +10%",
       "Has portfolio/LinkedIn URL: +10%") +
    p("This score is displayed as a progress bar on the profile page, motivating users to reach 100% completion "
      "for better visibility in recruiter searches.")
))

# JOBSEEKER ER Diagram
nodes_js = [
    ("jsp","JobSeekerProfile","E",220,200),
    ("sk","Skill","WE",520,100),
    ("ed","Education","WE",520,200),
    ("ex","Experience","WE",520,300),
    ("ce","Certification","WE",520,380),
    ("j_hl","headline","A",100,120),
    ("j_lo","location","A",80,260),
    ("sk_n","name","A",680,60),
    ("sk_p","proficiency","A",680,140),
    ("ed_d","degree","A",680,190),
    ("ed_f","field","A",680,250),
    ("ex_r","role","A",680,300),
    ("ex_c","company","A",680,360),
    ("ce_n","cert name","A",680,410),
    ("rel_sk","has","R",370,100),
    ("rel_ed","has","R",370,200),
    ("rel_ex","has","R",370,300),
    ("rel_ce","has","R",370,380),
]
edges_js = [
    ("jsp","j_hl",""),("jsp","j_lo",""),
    ("jsp","rel_sk","1"),("rel_sk","sk","N"),
    ("jsp","rel_ed","1"),("rel_ed","ed","N"),
    ("jsp","rel_ex","1"),("rel_ex","ex","N"),
    ("jsp","rel_ce","1"),("rel_ce","ce","N"),
    ("sk","sk_n",""),("sk","sk_p",""),
    ("ed","ed_d",""),("ed","ed_f",""),
    ("ex","ex_r",""),("ex","ex_c",""),
    ("ce","ce_n",""),
]
w(er_pg("Module 2: jobseeker", er_svg(nodes_js, edges_js, 900, 460)))

print("Chapter 4 done")

# ─── CHAPTER 5: RESUME MODULE ────────────────────────────────────
w(h("5","Module 3: Resume Upload, Parsing &amp; Builder","Automated resume parsing with pdfplumber / python-docx and 5-template builder","#7c3aed"))
w(pg(
    sh("5.1  Module Overview") +
    p("The <strong>resume</strong> app is a dual-purpose module that handles both resume file management and resume generation. "
      "Part one accepts uploaded PDF and DOCX resumes, parses them to extract structured information, and stores the results. "
      "Part two is an integrated resume builder that generates professional resumes from the job seeker's profile data.") +
    tbl(["Property","Value"],
        [["Django App Name","resume"],
         ["Models","Resume, ParsedResume, ExtractedKeyword, BuiltResume"],
         ["Parsing Libraries","pdfplumber (PDF), python-docx (DOCX)"],
         ["Templates","5 ATS-optimised resume templates"],
         ["Output Format","HTML (printable to PDF via browser)"]],
        "#7c3aed") +

    sh("5.2  Resume (Upload) Model") +
    tbl(["Field","Type","Notes"],
        [["id","AutoField (PK)","Auto-generated"],
         ["user","ForeignKey(User)","Owner of the resume"],
         ["file","FileField","Stored in media/resumes/"],
         ["original_filename","CharField","Original name of uploaded file"],
         ["file_type","CharField","pdf or docx"],
         ["file_size","IntegerField","Size in bytes"],
         ["uploaded_at","DateTimeField","Upload timestamp (auto_now_add)"],
         ["is_primary","BooleanField","Whether this is the active/default resume"]],
        "#374151") +

    sh("5.3  ParsedResume Model") +
    tbl(["Field","Type","Notes"],
        [["id","AutoField (PK)","Auto-generated"],
         ["resume","OneToOneField(Resume)","Parent uploaded resume"],
         ["raw_text","TextField","Full extracted text from file"],
         ["extracted_skills","JSONField","List of identified skill names"],
         ["education_level","CharField","high_school/bachelor/master/phd/other"],
         ["experience_years","FloatField","Total years of work experience detected"],
         ["has_email","BooleanField","Email found in resume"],
         ["has_phone","BooleanField","Phone number found"],
         ["parsed_at","DateTimeField","When parsing completed"]],
        "#374151")
))
w(pg(
    sh("5.4  Resume Parsing Logic") +
    p("The parsing pipeline (<code>resume/parser.py</code>) executes the following steps:") +
    ul("File type detection: checks the extension and MIME type to route to the correct parser",
       "Text extraction: pdfplumber reads PDF pages; python-docx reads paragraph and table text",
       "Skill extraction: text is compared against a master skill vocabulary list (~500 technology skills)",
       "Education detection: regex patterns identify degree mentions (B.Tech, B.Sc, M.Tech, MBA, PhD, etc.)",
       "Experience calculation: date ranges in the work history section are parsed and summed",
       "Contact info detection: regex identifies email addresses and phone number patterns",
       "Keyword extraction: high-frequency non-stopword terms are stored as ExtractedKeyword records") +

    sh("5.5  ExtractedKeyword Model") +
    tbl(["Field","Type","Notes"],
        [["id","AutoField (PK)","Auto-generated"],
         ["parsed_resume","ForeignKey(ParsedResume)","Parent parsed resume"],
         ["keyword","CharField","The extracted keyword"],
         ["frequency","IntegerField","How many times it appears"],
         ["is_skill","BooleanField","Whether this keyword is a known skill"]],
        "#374151") +

    sh("5.6  Resume Builder") +
    p("The resume builder generates professional resumes from structured profile data without requiring file uploads. "
      "It reads from the job seeker's profile (skills, education, experience, certifications) and renders a styled HTML "
      "page that can be printed to PDF.") +
    tbl(["Template","Style","Key Features"],
        [["Classic Professional","Dark navy header","Traditional layout, ATS-friendly"],
         ["Modern Minimal","White space focused","Clean lines, icon accents"],
         ["Creative Sidebar","Two-column layout","Skills panel on left"],
         ["Executive Bold","Strong typography","Large headings, impact-focused"],
         ["Tech Developer","Code-inspired","Monospace elements, GitHub link prominent"]],
        "#7c3aed") +

    sh("5.7  BuiltResume Model") +
    tbl(["Field","Type","Notes"],
        [["id","AutoField (PK)","Auto-generated"],
         ["user","ForeignKey(User)","Owner"],
         ["template_name","CharField","Which of 5 templates was used"],
         ["custom_color","CharField","Hex colour chosen by user"],
         ["font_choice","CharField","Font family selected"],
         ["include_photo","BooleanField","Whether profile picture is shown"],
         ["section_order","JSONField","Custom ordering of resume sections"],
         ["created_at","DateTimeField","When this version was created"],
         ["title","CharField","User-given name for this version"]],
        "#374151")
))

# RESUME ER Diagram
nodes_res = [
    ("user","User","E",120,200),
    ("res","Resume","E",320,120),
    ("pr","ParsedResume","WE",560,80),
    ("ek","ExtractedKeyword","WE",560,200),
    ("br","BuiltResume","WE",560,340),
    ("r_fn","filename","A",200,50),
    ("r_ft","file_type","A",320,40),
    ("pr_sk","skills","A",720,60),
    ("pr_ed","edu_level","A",720,130),
    ("pr_ex","exp_years","A",720,200),
    ("ek_kw","keyword","A",720,270),
    ("ek_fr","frequency","A",800,330),
    ("br_tp","template","A",720,380),
    ("br_cl","color","A",800,430),
    ("rel_r","uploads","R",220,120),
    ("rel_pr","parses to","R",440,80),
    ("rel_ek","extracts","R",440,200),
    ("rel_br","builds","R",440,340),
]
edges_res = [
    ("user","rel_r","1"),("rel_r","res","N"),
    ("res","r_fn",""),("res","r_ft",""),
    ("res","rel_pr","1"),("rel_pr","pr","1"),
    ("pr","pr_sk",""),("pr","pr_ed",""),("pr","pr_ex",""),
    ("pr","rel_ek","1"),("rel_ek","ek","N"),
    ("ek","ek_kw",""),("ek","ek_fr",""),
    ("user","rel_br","1"),("rel_br","br","N"),
    ("br","br_tp",""),("br","br_cl",""),
]
w(er_pg("Module 3: resume", er_svg(nodes_res, edges_res, 900, 460)))

print("Chapter 5 done")

# ─── CHAPTER 6: RECRUITER MODULE ────────────────────────────────
w(h("6","Module 4: Company &amp; Recruiter Panel","The recruiter app — company branding, team management, panel dashboard","#d97706"))
w(pg(
    sh("6.1  Module Overview") +
    p("The <strong>recruiter</strong> app provides the employer-facing side of TalentBridge. "
      "It manages company profile branding, HR team composition, and the recruiter dashboard "
      "that shows aggregated statistics on posted jobs, candidates, and applications.") +
    tbl(["Property","Value"],
        [["Django App Name","recruiter"],
         ["Models","RecruiterProfile (in accounts), HRMember"],
         ["Panel URL","recruiter/panel/"],
         ["Features","Company profile CRUD, logo upload, team management, stats dashboard"]],
        "#d97706") +

    sh("6.2  HRMember Model") +
    p("The HRMember model allows a recruiter to add multiple team members visible on their company profile "
      "page. This adds credibility and helps job seekers understand who they would be working with.") +
    tbl(["Field","Type","Notes"],
        [["id","AutoField (PK)","Auto-generated"],
         ["recruiter_profile","ForeignKey(RecruiterProfile)","Parent company profile (CASCADE)"],
         ["name","CharField","HR team member full name"],
         ["role","CharField","Job title (e.g., HR Manager, Talent Acquisition)"],
         ["email","EmailField","Contact email"],
         ["linkedin_url","URLField","LinkedIn profile (optional)"],
         ["photo","ImageField","Team member photo (optional)"],
         ["is_primary","BooleanField","Whether this is the primary contact"],
         ["joined_at","DateTimeField","When they joined the team listing"]],
        "#d97706") +

    sh("6.3  Recruiter Panel Dashboard") +
    p("The recruiter panel (<code>/recruiter/panel/</code>) provides a real-time summary dashboard:") +
    ul("Total Jobs Posted — count of all JobPost objects owned by this recruiter",
       "Active Jobs — count of JobPost objects with status='active'",
       "Total Applications Received — count of Applications across all their jobs",
       "Total Candidates Screened — count of MatchScore records for their jobs",
       "Pending Reviews — applications in 'pending' status",
       "Shortlisted Candidates — applications in 'shortlisted' status")
))
w(pg(
    sh("6.4  Company Profile Features") +
    p("The recruiter can edit their full company profile via <code>/recruiter/edit/</code>:") +
    ul("Company name, tagline, and description (rich text)",
       "Company logo upload (stored in media/company_logos/)",
       "Industry classification and company size range",
       "Founded year and website URL",
       "Head office location",
       "Social media links") +

    sh("6.5  Team Management") +
    p("Via <code>/recruiter/team/</code>, recruiters can manage their HR team listing:") +
    ul("Add new team members with photo, role, and contact details",
       "Mark one member as the primary contact for the company",
       "Edit or remove team members",
       "Team members appear on the public company profile page for job seekers") +

    sh("6.6  Job Management Integration") +
    p("The recruiter panel provides a direct link to <code>/jobs/manage/</code> where the recruiter "
      "can view all their job postings in a filterable table showing:") +
    ul("Job title and company",
       "Status badge (draft / active / paused / closed / expired)",
       "Number of applicants",
       "Number of candidates screened",
       "Posted date and deadline",
       "Quick action buttons: Edit, Toggle Status, Preview, View Applicants") +

    sh("6.7  Company Completeness Indicator") +
    p("Similar to job seeker profile completeness, the recruiter panel shows a company profile "
      "completeness score to encourage filling in all fields. Each section contributes to the score:") +
    ul("Company name and tagline: 15%",
       "Description: 20%",
       "Logo uploaded: 20%",
       "Industry and company size: 15%",
       "Website URL: 10%",
       "At least one HR team member: 20%") +

    sh("6.8  Views Summary") +
    tbl(["View","URL","Description"],
        [["company_panel","recruiter/panel/","Main dashboard with stats and quick links"],
         ["edit_profile","recruiter/edit/","Edit company profile form"],
         ["manage_team","recruiter/team/","Add/edit/remove HR team members"],
         ["add_team_member","recruiter/team/add/","Add individual HR member"],
         ["edit_team_member","recruiter/team/<pk>/edit/","Edit HR member"],
         ["delete_team_member","recruiter/team/<pk>/delete/","Remove HR member"]],
        "#d97706")
))

# RECRUITER ER Diagram
nodes_rec = [
    ("user","User","E",150,200),
    ("rp","RecruiterProfile","E",380,200),
    ("hr","HRMember","WE",640,200),
    ("jp","JobPost","WE",380,380),
    ("rp_co","company_name","A",280,80),
    ("rp_in","industry","A",430,80),
    ("rp_sz","size","A",550,80),
    ("hr_n","name","A",760,140),
    ("hr_r","role","A",760,220),
    ("hr_e","email","A",760,300),
    ("jp_t","title","A",280,430),
    ("jp_s","status","A",430,430),
    ("rel_rp","employs","R",265,200),
    ("rel_hr","has team","R",510,200),
    ("rel_jp","posts","R",380,290),
]
edges_rec = [
    ("user","rel_rp","1"),("rel_rp","rp","1"),
    ("rp","rp_co",""),("rp","rp_in",""),("rp","rp_sz",""),
    ("rp","rel_hr","1"),("rel_hr","hr","N"),
    ("hr","hr_n",""),("hr","hr_r",""),("hr","hr_e",""),
    ("rp","rel_jp","1"),("rel_jp","jp","N"),
    ("jp","jp_t",""),("jp","jp_s",""),
]
w(er_pg("Module 4: recruiter", er_svg(nodes_rec, edges_rec, 900, 480)))

print("Chapter 6 done")

# ─── CHAPTER 7: JOBS MODULE ─────────────────────────────────────
w(h("7","Module 5: Job Posting &amp; Job Board","The jobs app — create/manage job posts, public job board, saved jobs","#0891b2"))
w(pg(
    sh("7.1  Module Overview") +
    p("The <strong>jobs</strong> app handles job post creation, management, and browsing. "
      "Recruiters create detailed job listings; job seekers browse a public board. "
      "A saved jobs feature lets candidates bookmark interesting positions.") +
    tbl(["Property","Value"],
        [["Django App Name","jobs"],
         ["Models","JobPost, SavedJob"],
         ["Public Board","jobs/ (paginated, filterable)"],
         ["Manage URL","jobs/manage/ (recruiter only)"],
         ["Status Lifecycle","draft → active → paused / closed / expired"]],
        "#0891b2") +

    sh("7.2  JobPost Model") +
    tbl(["Field","Type","Notes"],
        [["id","AutoField (PK)","Auto-generated"],
         ["recruiter","ForeignKey(RecruiterProfile)","Owning company"],
         ["title","CharField","Job title"],
         ["description","TextField","Full job description"],
         ["required_skills","TextField","Comma-separated required skills"],
         ["nice_to_have","TextField","Optional preferred skills"],
         ["min_experience","FloatField","Minimum years of experience required"],
         ["education_required","CharField","high_school/bachelor/master/phd/any"],
         ["job_type","CharField","full_time/part_time/contract/internship/freelance"],
         ["work_mode","CharField","on_site/remote/hybrid"],
         ["salary_min","DecimalField","Minimum salary (optional)"],
         ["salary_max","DecimalField","Maximum salary (optional)"],
         ["currency","CharField","INR/USD/EUR/GBP"],
         ["location","CharField","Job location"],
         ["deadline","DateField","Application deadline"],
         ["status","CharField","draft/active/paused/closed/expired"],
         ["posted_at","DateTimeField","When first published (auto_now_add)"],
         ["updated_at","DateTimeField","Last modification timestamp"]],
        "#374151")
))
w(pg(
    sh("7.3  Job Status Lifecycle") +
    p("Job posts transition through states managed by the recruiter:") +
    ul("<strong>draft</strong>: Job is being written, not visible to job seekers",
       "<strong>active</strong>: Publicly visible on the job board, accepting applications",
       "<strong>paused</strong>: Temporarily hidden from board (recruiter choice)",
       "<strong>closed</strong>: No longer accepting applications (manual close)",
       "<strong>expired</strong>: Deadline has passed (auto-set by system check)") +

    sh("7.4  SavedJob Model") +
    tbl(["Field","Type","Notes"],
        [["id","AutoField (PK)","Auto-generated"],
         ["user","ForeignKey(User)","Job seeker who saved this job"],
         ["job","ForeignKey(JobPost)","The saved job post"],
         ["saved_at","DateTimeField","When it was bookmarked"]],
        "#374151") +

    sh("7.5  Public Job Board Features") +
    p("The job board at <code>/jobs/</code> provides:") +
    ul("Paginated listing of all active jobs (10 per page)",
       "Search by job title or keyword",
       "Filter by job type (full-time, part-time, contract, internship)",
       "Filter by work mode (on-site, remote, hybrid)",
       "Filter by education requirement",
       "Sort by: most recent, salary (high to low), deadline soonest",
       "Each job card shows: title, company, location, job type, work mode, salary range, deadline") +

    sh("7.6  Job Detail Page Features") +
    p("The job detail page (<code>/jobs/&lt;pk&gt;/</code>) shows:") +
    ul("Full job description with rich formatting",
       "Required and nice-to-have skills displayed as chips",
       "Salary range with currency",
       "Company information card with logo",
       "Match score button for logged-in job seekers (links to screening module)",
       "Apply Now button (links to applications module)",
       "Save/Unsave job toggle",
       "Application deadline countdown") +

    sh("7.7  Recruiter Job Management") +
    p("The recruiter's job management view (<code>/jobs/manage/</code>) provides a table listing of all their jobs "
      "with inline action buttons. Features:") +
    ul("Quick status toggle (active ↔ paused, draft → active)",
       "Applicant count per job",
       "Edit job post (full CRUD)",
       "Delete job post (with confirmation)",
       "Link to candidate screening results",
       "Link to applicants list") +

    sh("7.8  Views Summary") +
    tbl(["View","URL","Description"],
        [["job_board","jobs/","Public job listing with filters"],
         ["job_detail","jobs/<pk>/","Full job post detail (public)"],
         ["job_detail_recruiter","jobs/<pk>/preview/","Recruiter's own job preview"],
         ["create_job","jobs/new/","New job post form (recruiter)"],
         ["edit_job","jobs/<pk>/edit/","Edit existing job (recruiter)"],
         ["toggle_status","jobs/<pk>/status/","Toggle active/paused"],
         ["manage_jobs","jobs/manage/","Recruiter job management table"],
         ["save_job","jobs/<pk>/save/","Bookmark/unbookmark a job"]],
        "#0891b2")
))

# JOBS ER Diagram
nodes_jobs = [
    ("rp","RecruiterProfile","E",180,200),
    ("jp","JobPost","E",420,200),
    ("sj","SavedJob","WE",420,380),
    ("user","User","E",660,380),
    ("jp_ti","title","A",290,80),
    ("jp_st","status","A",420,80),
    ("jp_sk","req_skills","A",560,80),
    ("jp_ty","job_type","A",650,140),
    ("jp_wm","work_mode","A",730,200),
    ("jp_dl","deadline","A",650,260),
    ("sj_at","saved_at","A",420,460),
    ("rel_post","posts","R",300,200),
    ("rel_save","saves","R",540,380),
]
edges_jobs = [
    ("rp","rel_post","1"),("rel_post","jp","N"),
    ("jp","jp_ti",""),("jp","jp_st",""),("jp","jp_sk",""),
    ("jp","jp_ty",""),("jp","jp_wm",""),("jp","jp_dl",""),
    ("jp","rel_save","1"),("rel_save","sj","N"),("user","rel_save","1"),
    ("sj","sj_at",""),
]
w(er_pg("Module 5: jobs", er_svg(nodes_jobs, edges_jobs, 900, 490)))

print("Chapter 7 done")

# ─── CHAPTER 8: SCREENING MODULE ────────────────────────────────
w(h("8","Module 6: Intelligent Resume Screening","Weighted skill matching — Skills 40% + Experience 25% + Education 15% + Keywords 20%","#dc2626"))
w(pg(
    sh("8.1  Module Overview") +
    p("The <strong>screening</strong> app is the core intelligence layer of TalentBridge. "
      "It implements an automated resume-to-job matching algorithm that computes an objective compatibility "
      "score between a candidate's complete profile and a specific job posting. "
      "This replaces subjective recruiter judgement for initial shortlisting.") +
    tbl(["Property","Value"],
        [["Django App Name","screening"],
         ["Model","MatchScore"],
         ["Algorithm","Weighted multi-factor scoring"],
         ["Weight: Skills","40% (highest weight — most job-critical)"],
         ["Weight: Experience","25%"],
         ["Weight: Education","15%"],
         ["Weight: Keywords","20%"],
         ["Score Range","0–100 (percentage compatibility)"]],
        "#dc2626") +

    sh("8.2  MatchScore Model") +
    tbl(["Field","Type","Notes"],
        [["id","AutoField (PK)","Auto-generated"],
         ["candidate","ForeignKey(User)","The job seeker being evaluated"],
         ["job","ForeignKey(JobPost)","The job post being matched against"],
         ["total_score","FloatField","Overall weighted score (0–100)"],
         ["skill_score","FloatField","Skills component score (0–100)"],
         ["experience_score","FloatField","Experience component score (0–100)"],
         ["education_score","FloatField","Education component score (0–100)"],
         ["keyword_score","FloatField","Keyword relevance score (0–100)"],
         ["matched_skills","JSONField","List of skills that matched"],
         ["missing_skills","JSONField","Required skills not found in profile"],
         ["matched_keywords","JSONField","Keywords found in both resume and job"],
         ["computed_at","DateTimeField","When the score was last computed"],
         ["unique_together","—","(candidate, job) prevents duplicate scores"]],
        "#374151")
))
w(pg(
    sh("8.3  Scoring Algorithm — Detailed Breakdown") +

    sh2("Skills Score (40%)") +
    p("The skills component compares the job's <code>required_skills</code> (comma-separated) against "
      "the candidate's Skill model entries. The match is case-insensitive and uses partial matching:") +
    ul("For each required skill in the job post, check if the candidate has a matching skill",
       "Count matched skills vs total required skills",
       "Skill score = (matched_count / total_required) * 100",
       "Weighted contribution: skill_score * 0.40") +

    sh2("Experience Score (25%)") +
    p("Compares the job's <code>min_experience</code> field against the candidate's total work experience:") +
    ul("Calculate candidate's total experience from Experience model (sum of date ranges)",
       "If candidate_years >= required_years: experience_score = 100",
       "If candidate_years >= required_years * 0.75: experience_score = 75",
       "If candidate_years >= required_years * 0.5: experience_score = 50",
       "Otherwise: experience_score = (candidate_years / required_years) * 100",
       "Weighted contribution: experience_score * 0.25") +

    sh2("Education Score (15%)") +
    p("Maps education levels to numeric values and compares:") +
    tbl(["Education Level","Numeric Value"],
        [["PhD / Doctorate","5"],
         ["Master's Degree","4"],
         ["Bachelor's Degree","3"],
         ["Diploma / Associate","2"],
         ["High School","1"],
         ["Any (no requirement)","0 — always full score"]],
        "#374151") +
    p("Education score = 100 if candidate_level >= required_level, else (candidate_level / required_level) * 100. "
      "Weighted contribution: education_score * 0.15") +

    sh2("Keyword Score (20%)") +
    p("Keyword matching compares the job description text against keywords extracted from the candidate's resume:") +
    ul("Extract important words from job description (remove stopwords)",
       "Compare against candidate's ExtractedKeyword records",
       "keyword_score = (matched_keywords / total_job_keywords) * 100",
       "Weighted contribution: keyword_score * 0.20") +

    sh("8.4  Final Score Computation") +
    p("total_score = (skill_score × 0.40) + (experience_score × 0.25) + (education_score × 0.15) + (keyword_score × 0.20)") +
    p("Score interpretation used in the UI:") +
    tbl(["Score Range","Badge","Meaning"],
        [["85–100","Excellent Match","Highly recommended for interview"],
         ["70–84","Strong Match","Good candidate, worth interviewing"],
         ["55–69","Good Match","Meets core requirements"],
         ["40–54","Partial Match","Some gaps, needs consideration"],
         ["Below 40","Low Match","Significant skill or experience gaps"]],
        "#dc2626") +

    sh("8.5  Recruiter View — Ranked Candidates") +
    p("The view at <code>/screening/jobs/&lt;pk&gt;/candidates/</code> shows all MatchScore records for a job, "
      "ordered by total_score descending. Recruiters see: candidate name, score, a colour-coded progress bar, "
      "matched/missing skills chips, and a link to their full profile.")
))

# SCREENING ER Diagram
nodes_sc = [
    ("user","User","E",180,200),
    ("jp","JobPost","E",720,200),
    ("ms","MatchScore","E",450,200),
    ("ms_ts","total_score","A",350,80),
    ("ms_ss","skill_score","A",450,60),
    ("ms_es","exp_score","A",560,80),
    ("ms_ks","kw_score","A",650,120),
    ("ms_msk","matched_skills","A",350,340),
    ("ms_miss","missing_skills","A",450,370),
    ("ms_mkw","matched_kws","A",560,340),
    ("rel_c","evaluated","R",310,200),
    ("rel_j","for job","R",590,200),
]
edges_sc = [
    ("user","rel_c","1"),("rel_c","ms","N"),
    ("jp","rel_j","1"),("rel_j","ms","N"),
    ("ms","ms_ts",""),("ms","ms_ss",""),("ms","ms_es",""),("ms","ms_ks",""),
    ("ms","ms_msk",""),("ms","ms_miss",""),("ms","ms_mkw",""),
]
w(er_pg("Module 6: screening", er_svg(nodes_sc, edges_sc, 900, 430)))

print("Chapter 8 done")

# ─── CHAPTER 9: APPLICATIONS MODULE ─────────────────────────────
w(h("9","Module 7: Job Application Lifecycle","The applications app — apply, withdraw, status tracking, recruiter review","#4f46e5"))
w(pg(
    sh("9.1  Module Overview") +
    p("The <strong>applications</strong> app manages the formal job application process. "
      "Job seekers submit applications with an optional cover letter; recruiters review, "
      "shortlist, reject, or hire. The entire lifecycle is tracked with timestamps and status badges.") +
    tbl(["Property","Value"],
        [["Django App Name","applications"],
         ["Model","Application"],
         ["Constraint","One application per user per job (unique_together)"],
         ["Status Flow","pending → reviewed → shortlisted → rejected / hired"],
         ["Views","apply, withdraw, my_applications, job_applicants, update_status"]],
        "#4f46e5") +

    sh("9.2  Application Model") +
    tbl(["Field","Type","Notes"],
        [["id","AutoField (PK)","Auto-generated"],
         ["job","ForeignKey(JobPost)","The job being applied to"],
         ["applicant","ForeignKey(User)","The applying job seeker"],
         ["cover_letter","TextField","Optional cover letter text"],
         ["status","CharField","pending/reviewed/shortlisted/rejected/hired"],
         ["applied_at","DateTimeField","Submission timestamp (auto_now_add)"],
         ["updated_at","DateTimeField","Last status change (auto_now)"],
         ["recruiter_notes","TextField","Internal notes by recruiter (not shown to applicant)"],
         ["unique_together","—","(job, applicant) — prevents duplicate applications"]],
        "#4f46e5") +

    sh("9.3  Application Status Lifecycle") +
    p("Applications progress through the following states:") +
    tbl(["Status","Who Sets It","Meaning"],
        [["pending","System (on submit)","Application received, not yet reviewed"],
         ["reviewed","Recruiter","Recruiter has seen the application"],
         ["shortlisted","Recruiter","Candidate selected for further consideration"],
         ["rejected","Recruiter","Application declined"],
         ["hired","Recruiter","Candidate selected for the position"]],
        "#4f46e5")
))
w(pg(
    sh("9.4  Apply Workflow") +
    p("The application workflow from a job seeker's perspective:") +
    ul("Job seeker visits a job detail page and clicks 'Apply Now'",
       "They are directed to the apply form (/applications/jobs/&lt;pk&gt;/apply/)",
       "They optionally write a cover letter and submit",
       "If already applied: redirected to 'My Applications' with an existing application warning",
       "After submission: redirected back to job detail with 'Applied ✓ [date]' status shown",
       "Withdraw button appears if status is still 'pending'") +

    sh("9.5  My Applications View") +
    p("Job seekers access their full application history at <code>/applications/my-applications/</code>:") +
    ul("List of all applications ordered by applied_at descending",
       "Each entry shows: job title, company name, applied date, status badge",
       "Status badge is colour-coded: pending=yellow, reviewed=blue, shortlisted=green, rejected=red, hired=dark-green",
       "Withdraw button on pending applications",
       "Link to the job detail page") +

    sh("9.6  Recruiter Applicants View") +
    p("Recruiters access the applicant list for a specific job at <code>/applications/jobs/&lt;pk&gt;/applicants/</code>:") +
    ul("Header showing job title and total applicant count",
       "Stats strip: Total / Pending / Shortlisted / Hired counts",
       "List of applicant rows with: name, email, applied date, cover letter preview",
       "Status dropdown that auto-submits on change (pending / reviewed / shortlisted / rejected / hired)",
       "Recruiter notes field for private comments",
       "Link to candidate's screening score (MatchScore) if available") +

    sh("9.7  Views Summary") +
    tbl(["View","URL","Description"],
        [["apply","applications/jobs/<pk>/apply/","Show form and submit application"],
         ["withdraw","applications/<pk>/withdraw/","Delete application (pending only)"],
         ["my_applications","applications/my-applications/","Job seeker application history"],
         ["job_applicants","applications/jobs/<pk>/applicants/","Recruiter applicant list"],
         ["update_status","applications/<pk>/status/","Recruiter status + notes update"]],
        "#4f46e5") +

    sh("9.8  Dashboard Integration") +
    p("The job seeker dashboard shows the 'Jobs Applied' stat card using "
      "<code>Application.objects.filter(applicant=request.user).count()</code>. "
      "The recruiter panel's 'Total Applications' is also sourced from the Application model.")
))

# APPLICATIONS ER Diagram
nodes_app = [
    ("user","User","E",180,220),
    ("jp","JobPost","E",720,220),
    ("app","Application","E",450,220),
    ("ap_cl","cover_letter","A",340,90),
    ("ap_st","status","A",450,80),
    ("ap_at","applied_at","A",560,90),
    ("ap_rn","recruiter_notes","A",650,160),
    ("ap_ua","updated_at","A",340,360),
    ("rel_ap","applies","R",310,220),
    ("rel_jp","to job","R",590,220),
]
edges_app = [
    ("user","rel_ap","1"),("rel_ap","app","N"),
    ("jp","rel_jp","1"),("rel_jp","app","N"),
    ("app","ap_cl",""),("app","ap_st",""),("app","ap_at",""),
    ("app","ap_rn",""),("app","ap_ua",""),
]
w(er_pg("Module 7: applications", er_svg(nodes_app, edges_app, 900, 440)))

print("Chapter 9 done")

# ─── CHAPTER 10: FEEDBACK MODULE ─────────────────────────────────
w(h("10","Module 8: Feedback &amp; Rating System","Bidirectional ratings after terminal application status — candidate ↔ company","#db2777"))
w(pg(
    sh("10.1  Module Overview") +
    p("The <strong>feedback</strong> app implements a bidirectional rating and review system. "
      "After an application reaches a terminal status (shortlisted, rejected, or hired), "
      "both the candidate and the company can leave a 1–5 star rating with a written comment. "
      "This creates accountability and helps future applicants assess companies.") +
    tbl(["Property","Value"],
        [["Django App Name","feedback"],
         ["Model","Feedback"],
         ["Trigger","Application status reaches terminal state (shortlisted/rejected/hired)"],
         ["Rating Scale","1 (poor) to 5 (excellent) stars"],
         ["Direction","Candidate-to-Company OR Company-to-Candidate"],
         ["Constraint","One feedback per (application, direction) pair"]],
        "#db2777") +

    sh("10.2  Feedback Model") +
    tbl(["Field","Type","Notes"],
        [["id","AutoField (PK)","Auto-generated"],
         ["application","ForeignKey(Application)","The application this feedback relates to"],
         ["reviewer","ForeignKey(User)","Who wrote the feedback"],
         ["reviewee","ForeignKey(User)","Who is being reviewed"],
         ["direction","CharField","candidate_to_company or company_to_candidate"],
         ["rating","IntegerField","1–5 star rating"],
         ["comment","TextField","Written review text"],
         ["is_anonymous","BooleanField","Whether reviewer is shown anonymously"],
         ["created_at","DateTimeField","Submission timestamp (auto_now_add)"],
         ["unique_together","—","(application, reviewer, direction)"]],
        "#db2777") +

    sh("10.3  Review Workflow") +
    p("The feedback workflow is triggered automatically when an application's status changes:") +
    ul("When recruiter marks application as 'shortlisted', 'rejected', or 'hired', "
       "a notification is sent to the candidate with a link to leave feedback",
       "Both parties see a 'Leave Feedback' button on the application detail page",
       "A star rating widget (1–5) and comment textarea are presented",
       "After submission, the feedback is stored and displayed on the company/candidate profile",
       "Anonymous reviews show 'Anonymous Reviewer' instead of the actual name")
))
w(pg(
    sh("10.4  Rating Display") +
    p("Company ratings are aggregated and displayed:") +
    ul("Average rating calculated across all Feedback records where direction='candidate_to_company'",
       "Star display rendered with filled/empty star icons",
       "Total review count shown alongside average",
       "Individual reviews listed with date, comment, and optional reviewer name",
       "Company profile page shows the rating prominently to job seekers") +

    sh("10.5  Candidate Feedback") +
    p("Companies can also rate candidates, which is useful for:") +
    ul("Professional reference tracking — noting exceptional candidates for future roles",
       "Warning about unprofessional behaviour (no-shows, ghost interviews)",
       "Building a candidate reputation score visible to recruiter network",
       "These ratings are shown on the candidate's profile when applying to other jobs") +

    sh("10.6  Use Cases") +
    tbl(["Use Case","Actor","Outcome"],
        [["Rate company after rejection","Job Seeker","1-star + comment appears on company profile"],
         ["Rate candidate after hiring","Recruiter","5-star + comment on candidate profile"],
         ["Anonymous review","Job Seeker","Reviewer shown as 'Anonymous'"],
         ["View company reviews before applying","Job Seeker","Sees average rating and comments on job detail page"]],
        "#db2777") +

    sh("10.7  Views Summary") +
    tbl(["View","URL","Description"],
        [["leave_feedback","feedback/<app_pk>/leave/","Submit rating and comment form"],
         ["view_feedback","feedback/application/<pk>/","View all feedback for an application"],
         ["company_reviews","feedback/company/<pk>/","All reviews for a company"],
         ["my_feedback","feedback/mine/","Job seeker's received and given feedback"]],
        "#db2777")
))

# FEEDBACK ER Diagram
nodes_fb = [
    ("app","Application","E",230,200),
    ("fb","Feedback","E",520,200),
    ("reviewer","User(reviewer)","E",780,130),
    ("reviewee","User(reviewee)","E",780,280),
    ("fb_r","rating","A",440,80),
    ("fb_d","direction","A",560,80),
    ("fb_c","comment","A",620,140),
    ("fb_an","anonymous","A",620,260),
    ("fb_ca","created_at","A",440,340),
    ("rel_ap","from","R",370,200),
    ("rel_re","written by","R",650,130),
    ("rel_rv","about","R",650,280),
]
edges_fb = [
    ("app","rel_ap","1"),("rel_ap","fb","N"),
    ("fb","rel_re","N"),("rel_re","reviewer","1"),
    ("fb","rel_rv","N"),("rel_rv","reviewee","1"),
    ("fb","fb_r",""),("fb","fb_d",""),("fb","fb_c",""),("fb","fb_an",""),("fb","fb_ca",""),
]
w(er_pg("Module 8: feedback", er_svg(nodes_fb, edges_fb, 900, 420)))

print("Chapter 10 done")

# ─── CHAPTER 11: INTERVIEWS MODULE ───────────────────────────────
w(h("11","Module 9: Interview Scheduling","The interviews app — schedule, confirm, track video/phone/on-site interviews","#b45309"))
w(pg(
    sh("11.1  Module Overview") +
    p("The <strong>interviews</strong> app handles the scheduling and management of job interviews. "
      "Each interview is linked one-to-one with a job application and can be of three types: "
      "video call, phone call, or on-site. The status lifecycle tracks whether interviews are confirmed, "
      "completed, or cancelled.") +
    tbl(["Property","Value"],
        [["Django App Name","interviews"],
         ["Model","Interview"],
         ["Relationship","OneToOne with Application"],
         ["Interview Types","video / phone / on_site"],
         ["Status Lifecycle","scheduled → confirmed → completed / cancelled"],
         ["Trigger","Recruiter schedules after shortlisting"]],
        "#b45309") +

    sh("11.2  Interview Model") +
    tbl(["Field","Type","Notes"],
        [["id","AutoField (PK)","Auto-generated"],
         ["application","OneToOneField(Application)","Linked application"],
         ["interview_type","CharField","video / phone / on_site"],
         ["scheduled_at","DateTimeField","Date and time of the interview"],
         ["duration_minutes","IntegerField","Expected duration in minutes"],
         ["meeting_link","URLField","Video call URL (Zoom, Meet, Teams — for video type)"],
         ["venue","TextField","Physical address (for on_site type)"],
         ["interviewer_name","CharField","Name of the interviewer(s)"],
         ["status","CharField","scheduled / confirmed / completed / cancelled"],
         ["candidate_notes","TextField","Preparation instructions for candidate"],
         ["recruiter_notes","TextField","Private notes for recruiter"],
         ["created_at","DateTimeField","When the interview was scheduled"],
         ["updated_at","DateTimeField","Last status change timestamp"]],
        "#b45309")
))
w(pg(
    sh("11.3  Interview Lifecycle") +
    p("The interview status transitions:") +
    ul("<strong>scheduled</strong>: Recruiter has created the interview record; candidate notified",
       "<strong>confirmed</strong>: Candidate has confirmed their availability",
       "<strong>completed</strong>: Interview took place; recruiter marks as done",
       "<strong>cancelled</strong>: Either party cancelled; a notification is sent") +

    sh("11.4  Notification Integration") +
    p("The interviews module triggers the following notifications:") +
    ul("On creation (scheduled): Candidate receives 'Interview Scheduled' notification with date, time, and link",
       "On confirmation: Recruiter receives 'Interview Confirmed' notification",
       "On cancellation: Both parties receive 'Interview Cancelled' notification",
       "On completion: No automatic notification; recruiter manually updates status") +

    sh("11.5  Scheduling Constraints") +
    p("Business rules enforced by the system:") +
    ul("Only one interview can be linked to each application (OneToOne constraint)",
       "Interview can only be scheduled if application status is 'shortlisted' or 'reviewed'",
       "Scheduled_at must be in the future (validated in form clean method)",
       "Meeting link is required for video type; venue is required for on_site type",
       "Duration must be between 15 and 480 minutes") +

    sh("11.6  Calendar Display") +
    p("The interview list view shows upcoming interviews in chronological order. "
      "Past interviews are shown in a separate 'Past Interviews' section. "
      "Colour coding: scheduled=amber, confirmed=green, completed=gray, cancelled=red.") +

    sh("11.7  Views Summary") +
    tbl(["View","URL","Description"],
        [["schedule_interview","interviews/applications/<pk>/schedule/","Recruiter schedules interview"],
         ["view_interview","interviews/<pk>/","Interview detail (both parties)"],
         ["confirm_interview","interviews/<pk>/confirm/","Candidate confirms attendance"],
         ["cancel_interview","interviews/<pk>/cancel/","Either party cancels"],
         ["complete_interview","interviews/<pk>/complete/","Recruiter marks as done"],
         ["my_interviews","interviews/mine/","Job seeker's upcoming interviews"]],
        "#b45309")
))

# INTERVIEWS ER Diagram
nodes_iv = [
    ("app","Application","E",220,220),
    ("iv","Interview","E",500,220),
    ("iv_t","interview_type","A",380,80),
    ("iv_s","scheduled_at","A",500,80),
    ("iv_d","duration","A",620,80),
    ("iv_ml","meeting_link","A",730,150),
    ("iv_st","status","A",730,220),
    ("iv_v","venue","A",730,290),
    ("iv_in","interviewer","A",620,360),
    ("iv_cn","candidate_notes","A",500,370),
    ("rel_app","for","R",360,220),
]
edges_iv = [
    ("app","rel_app","1"),("rel_app","iv","1"),
    ("iv","iv_t",""),("iv","iv_s",""),("iv","iv_d",""),
    ("iv","iv_ml",""),("iv","iv_st",""),("iv","iv_v",""),
    ("iv","iv_in",""),("iv","iv_cn",""),
]
w(er_pg("Module 9: interviews", er_svg(nodes_iv, edges_iv, 900, 430)))

print("Chapter 11 done")

# ─── CHAPTER 12: NOTIFICATIONS MODULE ───────────────────────────
w(h("12","Module 10: Notification System","In-app notifications for all key lifecycle events across all modules","#475569"))
w(pg(
    sh("12.1  Module Overview") +
    p("The <strong>notifications</strong> app provides a centralised in-app notification system "
      "that keeps all users informed of important events across the platform. "
      "Notifications are generated programmatically when key actions occur in other modules.") +
    tbl(["Property","Value"],
        [["Django App Name","notifications"],
         ["Model","Notification"],
         ["Delivery","In-app (shown in navbar badge and notification page)"],
         ["State","read / unread"],
         ["Icon/Color","Varies by notification type"]],
        "#475569") +

    sh("12.2  Notification Model") +
    tbl(["Field","Type","Notes"],
        [["id","AutoField (PK)","Auto-generated"],
         ["recipient","ForeignKey(User)","Who receives the notification"],
         ["notification_type","CharField","application_received/status_changed/interview_scheduled/etc."],
         ["title","CharField","Short notification headline"],
         ["message","TextField","Detailed notification text"],
         ["link","URLField","URL to navigate to when notification is clicked"],
         ["icon","CharField","Emoji or icon class for visual indicator"],
         ["color","CharField","Colour theme: blue/green/red/amber/purple"],
         ["is_read","BooleanField","Whether user has read it (default=False)"],
         ["created_at","DateTimeField","When notification was generated (auto_now_add)"]],
        "#475569") +

    sh("12.3  Notification Types") +
    tbl(["Type","Trigger","Recipient","Icon"],
        [["application_received","Job seeker applies","Recruiter","📥"],
         ["application_status","Recruiter updates status","Job Seeker","📋"],
         ["shortlisted","Status → shortlisted","Job Seeker","⭐"],
         ["rejected","Status → rejected","Job Seeker","❌"],
         ["hired","Status → hired","Job Seeker","🎉"],
         ["interview_scheduled","Recruiter schedules","Job Seeker","📅"],
         ["interview_confirmed","Candidate confirms","Recruiter","✅"],
         ["interview_cancelled","Either party cancels","Both","🚫"],
         ["new_job_match","New job matches profile","Job Seeker","💼"],
         ["feedback_received","Feedback submitted","Both","💬"]],
        "#475569")
))
w(pg(
    sh("12.4  Notification Generation") +
    p("Notifications are created by a helper function <code>create_notification()</code> called "
      "from within views when key events occur:") +
    ul("In <code>applications/views.py apply()</code>: Creates 'application_received' for recruiter",
       "In <code>applications/views.py update_application_status()</code>: Creates status-change notification for candidate",
       "In <code>interviews/views.py schedule_interview()</code>: Creates 'interview_scheduled' for candidate",
       "In <code>interviews/views.py confirm_interview()</code>: Creates 'interview_confirmed' for recruiter",
       "In <code>interviews/views.py cancel_interview()</code>: Creates notifications for both parties") +

    sh("12.5  Unread Badge") +
    p("The base template includes an unread notification count in the navigation bar. "
      "The count is passed as context variable <code>unread_count</code> via a context processor, "
      "so it appears on every page without requiring each view to explicitly query it.") +

    sh("12.6  Mark as Read") +
    p("Clicking a notification marks it as read (is_read=True) and redirects to the linked URL. "
      "A 'Mark All as Read' button clears all unread notifications at once. "
      "Read notifications are shown with reduced opacity to distinguish from unread ones.") +

    sh("12.7  Context Processor") +
    p("A custom context processor in <code>notifications/context_processors.py</code> injects "
      "<code>unread_count</code> into every template context. This is registered in "
      "<code>settings.TEMPLATES['OPTIONS']['context_processors']</code>.") +

    sh("12.8  Views Summary") +
    tbl(["View","URL","Description"],
        [["notification_list","notifications/","List all notifications (newest first)"],
         ["mark_read","notifications/<pk>/read/","Mark one notification as read + redirect"],
         ["mark_all_read","notifications/read-all/","Mark all notifications as read"],
         ["delete_notification","notifications/<pk>/delete/","Remove a notification"]],
        "#475569")
))

# NOTIFICATIONS ER Diagram
nodes_nt = [
    ("user","User","E",200,200),
    ("nt","Notification","E",520,200),
    ("nt_t","type","A",400,80),
    ("nt_ti","title","A",520,60),
    ("nt_m","message","A",640,80),
    ("nt_l","link","A",740,150),
    ("nt_ic","icon","A",740,230),
    ("nt_cl","color","A",740,310),
    ("nt_r","is_read","A",640,340),
    ("nt_ca","created_at","A",400,340),
    ("rel_n","receives","R",360,200),
]
edges_nt = [
    ("user","rel_n","1"),("rel_n","nt","N"),
    ("nt","nt_t",""),("nt","nt_ti",""),("nt","nt_m",""),
    ("nt","nt_l",""),("nt","nt_ic",""),("nt","nt_cl",""),
    ("nt","nt_r",""),("nt","nt_ca",""),
]
w(er_pg("Module 10: notifications", er_svg(nodes_nt, edges_nt, 900, 420)))

print("Chapter 12 done")

# ─── CHAPTER 13: MODULE OVERVIEW GRID ──────────────────────────
w('''<div class="section">
<div class="section-header">
<div class="section-title st-modules">Chapter 13 &mdash; Module Overview: All 10 Django Applications</div>
<div class="section-sub">Each module is a self-contained Django application responsible for a specific domain of the system.</div>
</div>
<div class="module-grid">
<div class="mod-card m-accounts"><div class="mod-head"><h3>Module 1 &mdash; accounts</h3><span class="mod-badge">3 Models</span></div>
<div class="mod-body"><div class="mod-purpose">Handles user authentication, registration, login (email-based), and role management. Provides three roles: Admin, Recruiter, and Job Seeker. Includes password reset via email and per-role dashboard routing.</div>
<div class="mod-models"><span class="mod-model-chip">User</span><span class="mod-model-chip">RecruiterProfile</span><span class="mod-model-chip">JobSeekerProfile</span></div></div></div>

<div class="mod-card m-jobseeker"><div class="mod-head"><h3>Module 2 &mdash; jobseeker</h3><span class="mod-badge">5 Models</span></div>
<div class="mod-body"><div class="mod-purpose">Full job seeker profile management. Stores detailed professional information including skills with proficiency levels, education history, work experience with duration calculations, and certifications. Includes profile completeness scoring.</div>
<div class="mod-models"><span class="mod-model-chip">JobSeekerProfile</span><span class="mod-model-chip">Skill</span><span class="mod-model-chip">Education</span><span class="mod-model-chip">Experience</span><span class="mod-model-chip">Certification</span></div></div></div>

<div class="mod-card m-resume"><div class="mod-head"><h3>Module 3 &mdash; resume</h3><span class="mod-badge">4 Models</span></div>
<div class="mod-body"><div class="mod-purpose">Two-part module: (1) Resume Upload &amp; Parsing &mdash; accepts PDF/DOCX files, extracts text using pdfplumber and python-docx, identifies skills, keywords, education level, and experience years. (2) Resume Builder &mdash; creates formatted resumes from profile data with 5 ATS-optimised templates.</div>
<div class="mod-models"><span class="mod-model-chip">Resume</span><span class="mod-model-chip">ParsedResume</span><span class="mod-model-chip">ExtractedKeyword</span><span class="mod-model-chip">BuiltResume</span></div></div></div>

<div class="mod-card m-recruiter"><div class="mod-head"><h3>Module 4 &mdash; recruiter</h3><span class="mod-badge">1 Model</span></div>
<div class="mod-body"><div class="mod-purpose">Company/Recruiter panel for managing the company profile, branding (logo, tagline, description), industry, size, and team. Allows adding HR team members and provides a company completeness indicator.</div>
<div class="mod-models"><span class="mod-model-chip">HRMember</span></div></div></div>

<div class="mod-card m-jobs"><div class="mod-head"><h3>Module 5 &mdash; jobs</h3><span class="mod-badge">2 Models</span></div>
<div class="mod-body"><div class="mod-purpose">Job posting management. Recruiters create and manage job listings with required skills, experience level, education requirements, salary range, and deadline. Job seekers browse the public job board and can save jobs. Supports draft/active/paused/closed/expired status lifecycle.</div>
<div class="mod-models"><span class="mod-model-chip">JobPost</span><span class="mod-model-chip">SavedJob</span></div></div></div>

<div class="mod-card m-screening"><div class="mod-head"><h3>Module 6 &mdash; screening</h3><span class="mod-badge">1 Model</span></div>
<div class="mod-body"><div class="mod-purpose">Intelligent resume screening engine. Computes a weighted match score between a candidate\'s profile and a job post: Skills 40%, Experience 25%, Education 15%, Keywords 20%. Stores matched/missing skills and keywords. Recruiters see a ranked candidate list per job.</div>
<div class="mod-models"><span class="mod-model-chip">MatchScore</span></div></div></div>

<div class="mod-card m-applications"><div class="mod-head"><h3>Module 7 &mdash; applications</h3><span class="mod-badge">1 Model</span></div>
<div class="mod-body"><div class="mod-purpose">Job application lifecycle management. Job seekers submit applications with cover letter. Recruiters review and update status: Pending &rarr; Reviewed &rarr; Shortlisted &rarr; Rejected / Hired. One application per user per job enforced via unique_together constraint.</div>
<div class="mod-models"><span class="mod-model-chip">Application</span></div></div></div>

<div class="mod-card m-feedback"><div class="mod-head"><h3>Module 8 &mdash; feedback</h3><span class="mod-badge">1 Model</span></div>
<div class="mod-body"><div class="mod-purpose">Bidirectional feedback system. After an application reaches a terminal status, both the candidate and the company can leave a 1&ndash;5 star rating with a comment. Supports anonymous mode. Ensures one feedback per direction per application.</div>
<div class="mod-models"><span class="mod-model-chip">Feedback</span></div></div></div>

<div class="mod-card m-interviews"><div class="mod-head"><h3>Module 9 &mdash; interviews</h3><span class="mod-badge">1 Model</span></div>
<div class="mod-body"><div class="mod-purpose">Interview scheduling and management. Linked one-to-one with an application. Recruiters schedule video, phone, or on-site interviews with date/time, duration, meeting link or venue. Status lifecycle: Scheduled &rarr; Confirmed &rarr; Completed / Cancelled.</div>
<div class="mod-models"><span class="mod-model-chip">Interview</span></div></div></div>

<div class="mod-card m-notifications"><div class="mod-head"><h3>Module 10 &mdash; notifications</h3><span class="mod-badge">1 Model</span></div>
<div class="mod-body"><div class="mod-purpose">In-app notification system. Generates notifications for all key events: application received, status changes (shortlisted, rejected, hired), interview scheduled/confirmed/cancelled. Each notification links to the relevant page, supports read/unread state.</div>
<div class="mod-models"><span class="mod-model-chip">Notification</span></div></div></div>
</div>
</div>
''')

print("Chapter 13 done")

# ─── CHAPTER 14: ENTITY TABLES ──────────────────────────────────
w('''<div class="section">
<div class="section-header">
<div class="section-title st-entities">Chapter 14 &mdash; Database Design: 20 Entity Tables</div>
<div class="section-sub">All database tables with their fields, data types, and key annotations. PK = Primary Key &nbsp;|&nbsp; FK = Foreign Key &nbsp;|&nbsp; 1:1 = One-to-One</div>
</div>
<div class="legend">
<div class="legend-item"><div class="legend-dot" style="background:#fef9c3;border:1px solid #fde68a;"></div>Primary Key (PK)</div>
<div class="legend-item"><div class="legend-dot" style="background:#dbeafe;border:1px solid #93c5fd;"></div>Foreign Key (FK)</div>
<div class="legend-item"><div class="legend-dot" style="background:#ede9fe;border:1px solid #c4b5fd;"></div>One-to-One (1:1)</div>
</div>

<!-- accounts -->
<div class="entity-section">
<div class="entity-section-label">accounts app</div>
<div class="entities-row">
<div class="entity-box">
<div class="entity-head eh-accounts"><span class="entity-name">User</span><span class="entity-app">accounts.User (extends AbstractUser)</span></div>
<table class="fields"><tr><th>Field</th><th>Type</th><th>Notes</th></tr>
<tr><td><span class="field-name">id</span><span class="badge-pk">PK</span></td><td class="field-type">AutoField</td><td class="field-note">Auto-generated</td></tr>
<tr><td><span class="field-name">username</span></td><td class="field-type">CharField</td><td class="field-note">Inherited (unique)</td></tr>
<tr><td><span class="field-name">email</span></td><td class="field-type">EmailField</td><td class="field-note">Used for login</td></tr>
<tr><td><span class="field-name">first_name</span></td><td class="field-type">CharField</td><td class="field-note">Inherited</td></tr>
<tr><td><span class="field-name">last_name</span></td><td class="field-type">CharField</td><td class="field-note">Inherited</td></tr>
<tr><td><span class="field-name">phone</span></td><td class="field-type">CharField(20)</td><td class="field-note">Optional</td></tr>
<tr><td><span class="field-name">role</span></td><td class="field-type">CharField</td><td class="field-note">admin|recruiter|job_seeker</td></tr>
<tr><td><span class="field-name">is_active</span></td><td class="field-type">BooleanField</td><td class="field-note">Inherited</td></tr>
<tr><td><span class="field-name">date_joined</span></td><td class="field-type">DateTimeField</td><td class="field-note">Inherited</td></tr>
</table></div>

<div class="entity-box">
<div class="entity-head eh-accounts"><span class="entity-name">RecruiterProfile</span><span class="entity-app">accounts.RecruiterProfile</span></div>
<table class="fields"><tr><th>Field</th><th>Type</th><th>Notes</th></tr>
<tr><td><span class="field-name">id</span><span class="badge-pk">PK</span></td><td class="field-type">AutoField</td><td class="field-note">Auto-generated</td></tr>
<tr><td><span class="field-name">user</span><span class="badge-o2o">1:1</span></td><td class="field-type">OneToOneField(User)</td><td class="field-note">CASCADE</td></tr>
<tr><td><span class="field-name">company_name</span></td><td class="field-type">CharField</td><td class="field-note">Required</td></tr>
<tr><td><span class="field-name">company_logo</span></td><td class="field-type">ImageField</td><td class="field-note">Optional</td></tr>
<tr><td><span class="field-name">industry</span></td><td class="field-type">CharField</td><td class="field-note">Technology, Finance …</td></tr>
<tr><td><span class="field-name">company_size</span></td><td class="field-type">CharField</td><td class="field-note">1-10, 11-50 …</td></tr>
<tr><td><span class="field-name">website</span></td><td class="field-type">URLField</td><td class="field-note">Optional</td></tr>
<tr><td><span class="field-name">description</span></td><td class="field-type">TextField</td><td class="field-note">Company about text</td></tr>
<tr><td><span class="field-name">location</span></td><td class="field-type">CharField</td><td class="field-note">Head office</td></tr>
</table></div>
</div>
</div>

<!-- jobseeker -->
<div class="entity-section">
<div class="entity-section-label">jobseeker app</div>
<div class="entities-row">
<div class="entity-box">
<div class="entity-head eh-jobseeker"><span class="entity-name">JobSeekerProfile</span><span class="entity-app">jobseeker.JobSeekerProfile</span></div>
<table class="fields"><tr><th>Field</th><th>Type</th><th>Notes</th></tr>
<tr><td><span class="field-name">id</span><span class="badge-pk">PK</span></td><td class="field-type">AutoField</td><td class="field-note">Auto-generated</td></tr>
<tr><td><span class="field-name">user</span><span class="badge-o2o">1:1</span></td><td class="field-type">OneToOneField(User)</td><td class="field-note">CASCADE</td></tr>
<tr><td><span class="field-name">headline</span></td><td class="field-type">CharField</td><td class="field-note">Professional headline</td></tr>
<tr><td><span class="field-name">bio</span></td><td class="field-type">TextField</td><td class="field-note">About me</td></tr>
<tr><td><span class="field-name">location</span></td><td class="field-type">CharField</td><td class="field-note">City, Country</td></tr>
<tr><td><span class="field-name">profile_picture</span></td><td class="field-type">ImageField</td><td class="field-note">Uploaded photo</td></tr>
<tr><td><span class="field-name">desired_role</span></td><td class="field-type">CharField</td><td class="field-note">Target job title</td></tr>
<tr><td><span class="field-name">availability</span></td><td class="field-type">CharField</td><td class="field-note">Immediate/2wk/1mo</td></tr>
<tr><td><span class="field-name">is_public</span></td><td class="field-type">BooleanField</td><td class="field-note">Visible to recruiters</td></tr>
</table></div>

<div class="entity-box">
<div class="entity-head eh-jobseeker"><span class="entity-name">Skill</span><span class="entity-app">jobseeker.Skill</span></div>
<table class="fields"><tr><th>Field</th><th>Type</th><th>Notes</th></tr>
<tr><td><span class="field-name">id</span><span class="badge-pk">PK</span></td><td class="field-type">AutoField</td><td class="field-note">Auto-generated</td></tr>
<tr><td><span class="field-name">profile</span><span class="badge-fk">FK</span></td><td class="field-type">ForeignKey(JobSeekerProfile)</td><td class="field-note">CASCADE</td></tr>
<tr><td><span class="field-name">name</span></td><td class="field-type">CharField</td><td class="field-note">e.g. Python, Django</td></tr>
<tr><td><span class="field-name">proficiency</span></td><td class="field-type">IntegerField</td><td class="field-note">1=Beginner … 4=Expert</td></tr>
<tr><td><span class="field-name">years</span></td><td class="field-type">DecimalField</td><td class="field-note">Years of experience</td></tr>
<tr><td><span class="field-name">is_primary</span></td><td class="field-type">BooleanField</td><td class="field-note">Featured skill</td></tr>
</table></div>
</div>
<div class="entities-row" style="margin-top:16px;">
<div class="entity-box">
<div class="entity-head eh-jobseeker"><span class="entity-name">Education</span><span class="entity-app">jobseeker.Education</span></div>
<table class="fields"><tr><th>Field</th><th>Type</th><th>Notes</th></tr>
<tr><td><span class="field-name">id</span><span class="badge-pk">PK</span></td><td class="field-type">AutoField</td><td class="field-note">Auto-generated</td></tr>
<tr><td><span class="field-name">profile</span><span class="badge-fk">FK</span></td><td class="field-type">ForeignKey(JobSeekerProfile)</td><td class="field-note">CASCADE</td></tr>
<tr><td><span class="field-name">institution</span></td><td class="field-type">CharField</td><td class="field-note">University name</td></tr>
<tr><td><span class="field-name">degree</span></td><td class="field-type">CharField</td><td class="field-note">Bachelor\'s, Master\'s …</td></tr>
<tr><td><span class="field-name">field_of_study</span></td><td class="field-type">CharField</td><td class="field-note">e.g. Computer Science</td></tr>
<tr><td><span class="field-name">start_year</span></td><td class="field-type">IntegerField</td><td class="field-note">Year started</td></tr>
<tr><td><span class="field-name">end_year</span></td><td class="field-type">IntegerField</td><td class="field-note">Year completed</td></tr>
<tr><td><span class="field-name">grade</span></td><td class="field-type">CharField</td><td class="field-note">GPA or percentage</td></tr>
</table></div>

<div class="entity-box">
<div class="entity-head eh-jobseeker"><span class="entity-name">Experience</span><span class="entity-app">jobseeker.Experience</span></div>
<table class="fields"><tr><th>Field</th><th>Type</th><th>Notes</th></tr>
<tr><td><span class="field-name">id</span><span class="badge-pk">PK</span></td><td class="field-type">AutoField</td><td class="field-note">Auto-generated</td></tr>
<tr><td><span class="field-name">profile</span><span class="badge-fk">FK</span></td><td class="field-type">ForeignKey(JobSeekerProfile)</td><td class="field-note">CASCADE</td></tr>
<tr><td><span class="field-name">company</span></td><td class="field-type">CharField</td><td class="field-note">Employer name</td></tr>
<tr><td><span class="field-name">role</span></td><td class="field-type">CharField</td><td class="field-note">Job title</td></tr>
<tr><td><span class="field-name">start_date</span></td><td class="field-type">DateField</td><td class="field-note">Employment start</td></tr>
<tr><td><span class="field-name">end_date</span></td><td class="field-type">DateField</td><td class="field-note">End (null if current)</td></tr>
<tr><td><span class="field-name">is_current</span></td><td class="field-type">BooleanField</td><td class="field-note">Currently employed</td></tr>
<tr><td><span class="field-name">description</span></td><td class="field-type">TextField</td><td class="field-note">Responsibilities</td></tr>
</table></div>
</div>
</div>

<!-- resume -->
<div class="entity-section">
<div class="entity-section-label">resume app</div>
<div class="entities-row">
<div class="entity-box">
<div class="entity-head eh-resume"><span class="entity-name">Resume</span><span class="entity-app">resume.Resume</span></div>
<table class="fields"><tr><th>Field</th><th>Type</th><th>Notes</th></tr>
<tr><td><span class="field-name">id</span><span class="badge-pk">PK</span></td><td class="field-type">AutoField</td><td class="field-note">Auto-generated</td></tr>
<tr><td><span class="field-name">user</span><span class="badge-fk">FK</span></td><td class="field-type">ForeignKey(User)</td><td class="field-note">CASCADE</td></tr>
<tr><td><span class="field-name">file</span></td><td class="field-type">FileField</td><td class="field-note">Stored in media/resumes/</td></tr>
<tr><td><span class="field-name">file_type</span></td><td class="field-type">CharField</td><td class="field-note">pdf or docx</td></tr>
<tr><td><span class="field-name">file_size</span></td><td class="field-type">IntegerField</td><td class="field-note">Bytes</td></tr>
<tr><td><span class="field-name">uploaded_at</span></td><td class="field-type">DateTimeField</td><td class="field-note">auto_now_add</td></tr>
<tr><td><span class="field-name">is_primary</span></td><td class="field-type">BooleanField</td><td class="field-note">Active resume</td></tr>
</table></div>

<div class="entity-box">
<div class="entity-head eh-resume"><span class="entity-name">ParsedResume</span><span class="entity-app">resume.ParsedResume</span></div>
<table class="fields"><tr><th>Field</th><th>Type</th><th>Notes</th></tr>
<tr><td><span class="field-name">id</span><span class="badge-pk">PK</span></td><td class="field-type">AutoField</td><td class="field-note">Auto-generated</td></tr>
<tr><td><span class="field-name">resume</span><span class="badge-o2o">1:1</span></td><td class="field-type">OneToOneField(Resume)</td><td class="field-note">CASCADE</td></tr>
<tr><td><span class="field-name">raw_text</span></td><td class="field-type">TextField</td><td class="field-note">Extracted full text</td></tr>
<tr><td><span class="field-name">extracted_skills</span></td><td class="field-type">JSONField</td><td class="field-note">List of skill names</td></tr>
<tr><td><span class="field-name">education_level</span></td><td class="field-type">CharField</td><td class="field-note">bachelor/master/phd…</td></tr>
<tr><td><span class="field-name">experience_years</span></td><td class="field-type">FloatField</td><td class="field-note">Total years detected</td></tr>
<tr><td><span class="field-name">parsed_at</span></td><td class="field-type">DateTimeField</td><td class="field-note">Parse completion time</td></tr>
</table></div>
</div>
</div>

<!-- jobs -->
<div class="entity-section">
<div class="entity-section-label">jobs app</div>
<div class="entities-row">
<div class="entity-box">
<div class="entity-head eh-jobs"><span class="entity-name">JobPost</span><span class="entity-app">jobs.JobPost</span></div>
<table class="fields"><tr><th>Field</th><th>Type</th><th>Notes</th></tr>
<tr><td><span class="field-name">id</span><span class="badge-pk">PK</span></td><td class="field-type">AutoField</td><td class="field-note">Auto-generated</td></tr>
<tr><td><span class="field-name">recruiter</span><span class="badge-fk">FK</span></td><td class="field-type">ForeignKey(RecruiterProfile)</td><td class="field-note">CASCADE</td></tr>
<tr><td><span class="field-name">title</span></td><td class="field-type">CharField</td><td class="field-note">Job title</td></tr>
<tr><td><span class="field-name">required_skills</span></td><td class="field-type">TextField</td><td class="field-note">Comma-separated</td></tr>
<tr><td><span class="field-name">job_type</span></td><td class="field-type">CharField</td><td class="field-note">full_time/part_time…</td></tr>
<tr><td><span class="field-name">work_mode</span></td><td class="field-type">CharField</td><td class="field-note">on_site/remote/hybrid</td></tr>
<tr><td><span class="field-name">salary_min</span></td><td class="field-type">DecimalField</td><td class="field-note">Optional</td></tr>
<tr><td><span class="field-name">salary_max</span></td><td class="field-type">DecimalField</td><td class="field-note">Optional</td></tr>
<tr><td><span class="field-name">deadline</span></td><td class="field-type">DateField</td><td class="field-note">Application deadline</td></tr>
<tr><td><span class="field-name">status</span></td><td class="field-type">CharField</td><td class="field-note">draft/active/paused…</td></tr>
</table></div>

<div class="entity-box">
<div class="entity-head eh-jobs"><span class="entity-name">SavedJob</span><span class="entity-app">jobs.SavedJob</span></div>
<table class="fields"><tr><th>Field</th><th>Type</th><th>Notes</th></tr>
<tr><td><span class="field-name">id</span><span class="badge-pk">PK</span></td><td class="field-type">AutoField</td><td class="field-note">Auto-generated</td></tr>
<tr><td><span class="field-name">user</span><span class="badge-fk">FK</span></td><td class="field-type">ForeignKey(User)</td><td class="field-note">CASCADE</td></tr>
<tr><td><span class="field-name">job</span><span class="badge-fk">FK</span></td><td class="field-type">ForeignKey(JobPost)</td><td class="field-note">CASCADE</td></tr>
<tr><td><span class="field-name">saved_at</span></td><td class="field-type">DateTimeField</td><td class="field-note">auto_now_add</td></tr>
</table></div>
</div>
</div>

<!-- screening -->
<div class="entity-section">
<div class="entity-section-label">screening app</div>
<div class="entities-row">
<div class="entity-box">
<div class="entity-head eh-screening"><span class="entity-name">MatchScore</span><span class="entity-app">screening.MatchScore</span></div>
<table class="fields"><tr><th>Field</th><th>Type</th><th>Notes</th></tr>
<tr><td><span class="field-name">id</span><span class="badge-pk">PK</span></td><td class="field-type">AutoField</td><td class="field-note">Auto-generated</td></tr>
<tr><td><span class="field-name">candidate</span><span class="badge-fk">FK</span></td><td class="field-type">ForeignKey(User)</td><td class="field-note">CASCADE</td></tr>
<tr><td><span class="field-name">job</span><span class="badge-fk">FK</span></td><td class="field-type">ForeignKey(JobPost)</td><td class="field-note">CASCADE</td></tr>
<tr><td><span class="field-name">total_score</span></td><td class="field-type">FloatField</td><td class="field-note">0–100 weighted score</td></tr>
<tr><td><span class="field-name">skill_score</span></td><td class="field-type">FloatField</td><td class="field-note">Skills component</td></tr>
<tr><td><span class="field-name">experience_score</span></td><td class="field-type">FloatField</td><td class="field-note">Experience component</td></tr>
<tr><td><span class="field-name">education_score</span></td><td class="field-type">FloatField</td><td class="field-note">Education component</td></tr>
<tr><td><span class="field-name">keyword_score</span></td><td class="field-type">FloatField</td><td class="field-note">Keyword component</td></tr>
<tr><td><span class="field-name">matched_skills</span></td><td class="field-type">JSONField</td><td class="field-note">Skills that matched</td></tr>
<tr><td><span class="field-name">missing_skills</span></td><td class="field-type">JSONField</td><td class="field-note">Required but missing</td></tr>
<tr><td><span class="field-name">computed_at</span></td><td class="field-type">DateTimeField</td><td class="field-note">Last computed</td></tr>
</table></div>
<div style=""></div>
</div>
</div>

<!-- applications -->
<div class="entity-section">
<div class="entity-section-label">applications app</div>
<div class="entities-row">
<div class="entity-box">
<div class="entity-head eh-applications"><span class="entity-name">Application</span><span class="entity-app">applications.Application</span></div>
<table class="fields"><tr><th>Field</th><th>Type</th><th>Notes</th></tr>
<tr><td><span class="field-name">id</span><span class="badge-pk">PK</span></td><td class="field-type">AutoField</td><td class="field-note">Auto-generated</td></tr>
<tr><td><span class="field-name">job</span><span class="badge-fk">FK</span></td><td class="field-type">ForeignKey(JobPost)</td><td class="field-note">CASCADE</td></tr>
<tr><td><span class="field-name">applicant</span><span class="badge-fk">FK</span></td><td class="field-type">ForeignKey(User)</td><td class="field-note">CASCADE</td></tr>
<tr><td><span class="field-name">cover_letter</span></td><td class="field-type">TextField</td><td class="field-note">Optional</td></tr>
<tr><td><span class="field-name">status</span></td><td class="field-type">CharField</td><td class="field-note">pending/reviewed…</td></tr>
<tr><td><span class="field-name">applied_at</span></td><td class="field-type">DateTimeField</td><td class="field-note">auto_now_add</td></tr>
<tr><td><span class="field-name">recruiter_notes</span></td><td class="field-type">TextField</td><td class="field-note">Internal notes</td></tr>
</table></div>

<div class="entity-box">
<div class="entity-head eh-interviews"><span class="entity-name">Interview</span><span class="entity-app">interviews.Interview</span></div>
<table class="fields"><tr><th>Field</th><th>Type</th><th>Notes</th></tr>
<tr><td><span class="field-name">id</span><span class="badge-pk">PK</span></td><td class="field-type">AutoField</td><td class="field-note">Auto-generated</td></tr>
<tr><td><span class="field-name">application</span><span class="badge-o2o">1:1</span></td><td class="field-type">OneToOneField(Application)</td><td class="field-note">CASCADE</td></tr>
<tr><td><span class="field-name">interview_type</span></td><td class="field-type">CharField</td><td class="field-note">video/phone/on_site</td></tr>
<tr><td><span class="field-name">scheduled_at</span></td><td class="field-type">DateTimeField</td><td class="field-note">Interview date+time</td></tr>
<tr><td><span class="field-name">duration_minutes</span></td><td class="field-type">IntegerField</td><td class="field-note">Expected duration</td></tr>
<tr><td><span class="field-name">meeting_link</span></td><td class="field-type">URLField</td><td class="field-note">For video type</td></tr>
<tr><td><span class="field-name">status</span></td><td class="field-type">CharField</td><td class="field-note">scheduled/confirmed…</td></tr>
</table></div>
</div>
</div>

<!-- feedback & notifications -->
<div class="entity-section">
<div class="entity-section-label">feedback &amp; notifications apps</div>
<div class="entities-row">
<div class="entity-box">
<div class="entity-head eh-feedback"><span class="entity-name">Feedback</span><span class="entity-app">feedback.Feedback</span></div>
<table class="fields"><tr><th>Field</th><th>Type</th><th>Notes</th></tr>
<tr><td><span class="field-name">id</span><span class="badge-pk">PK</span></td><td class="field-type">AutoField</td><td class="field-note">Auto-generated</td></tr>
<tr><td><span class="field-name">application</span><span class="badge-fk">FK</span></td><td class="field-type">ForeignKey(Application)</td><td class="field-note">CASCADE</td></tr>
<tr><td><span class="field-name">reviewer</span><span class="badge-fk">FK</span></td><td class="field-type">ForeignKey(User)</td><td class="field-note">Reviewer</td></tr>
<tr><td><span class="field-name">reviewee</span><span class="badge-fk">FK</span></td><td class="field-type">ForeignKey(User)</td><td class="field-note">Reviewed person</td></tr>
<tr><td><span class="field-name">direction</span></td><td class="field-type">CharField</td><td class="field-note">candidate_to_company…</td></tr>
<tr><td><span class="field-name">rating</span></td><td class="field-type">IntegerField</td><td class="field-note">1–5 stars</td></tr>
<tr><td><span class="field-name">comment</span></td><td class="field-type">TextField</td><td class="field-note">Review text</td></tr>
<tr><td><span class="field-name">is_anonymous</span></td><td class="field-type">BooleanField</td><td class="field-note">Hide reviewer name</td></tr>
</table></div>

<div class="entity-box">
<div class="entity-head eh-notifications"><span class="entity-name">Notification</span><span class="entity-app">notifications.Notification</span></div>
<table class="fields"><tr><th>Field</th><th>Type</th><th>Notes</th></tr>
<tr><td><span class="field-name">id</span><span class="badge-pk">PK</span></td><td class="field-type">AutoField</td><td class="field-note">Auto-generated</td></tr>
<tr><td><span class="field-name">recipient</span><span class="badge-fk">FK</span></td><td class="field-type">ForeignKey(User)</td><td class="field-note">CASCADE</td></tr>
<tr><td><span class="field-name">notification_type</span></td><td class="field-type">CharField</td><td class="field-note">Type code</td></tr>
<tr><td><span class="field-name">title</span></td><td class="field-type">CharField</td><td class="field-note">Short headline</td></tr>
<tr><td><span class="field-name">message</span></td><td class="field-type">TextField</td><td class="field-note">Full text</td></tr>
<tr><td><span class="field-name">link</span></td><td class="field-type">URLField</td><td class="field-note">Click destination</td></tr>
<tr><td><span class="field-name">is_read</span></td><td class="field-type">BooleanField</td><td class="field-note">Read state</td></tr>
<tr><td><span class="field-name">created_at</span></td><td class="field-type">DateTimeField</td><td class="field-note">auto_now_add</td></tr>
</table></div>
</div>
</div>

</div>
''')

print("Chapter 14 done")

# ─── CHAPTER 15: FULL SYSTEM ER DIAGRAM ─────────────────────────
nodes_full = [
    ("user","User","E",450,80),
    ("rp","RecruiterProfile","E",200,200),
    ("jsp","JobSeekerProfile","E",700,200),
    ("jp","JobPost","E",200,380),
    ("ms","MatchScore","E",450,280),
    ("app","Application","E",450,460),
    ("iv","Interview","E",200,540),
    ("fb","Feedback","E",700,540),
    ("nt","Notification","E",700,380),
    ("sk","Skill","WE",820,200),
    ("sj","SavedJob","WE",330,520),
    ("rel_rp","has","R",325,130),
    ("rel_jsp","has","R",575,130),
    ("rel_post","posts","R",200,290),
    ("rel_ms_c","scores","R",560,180),
    ("rel_ms_j","scores","R",325,330),
    ("rel_app_u","applies","R",575,370),
    ("rel_app_j","to","R",325,420),
    ("rel_iv","scheduled","R",325,500),
    ("rel_fb","reviews","R",575,500),
    ("rel_nt","notifies","R",575,330),
    ("rel_sk","has","R",760,200),
    ("rel_sj","saves","R",330,450),
]
edges_full = [
    ("user","rel_rp","1"),("rel_rp","rp","1"),
    ("user","rel_jsp","1"),("rel_jsp","jsp","1"),
    ("rp","rel_post","1"),("rel_post","jp","N"),
    ("user","rel_ms_c","1"),("rel_ms_c","ms","N"),
    ("jp","rel_ms_j","1"),("rel_ms_j","ms","N"),
    ("user","rel_app_u","1"),("rel_app_u","app","N"),
    ("jp","rel_app_j","1"),("rel_app_j","app","N"),
    ("app","rel_iv","1"),("rel_iv","iv","1"),
    ("app","rel_fb","1"),("rel_fb","fb","N"),
    ("user","rel_nt","1"),("rel_nt","nt","N"),
    ("jsp","rel_sk","1"),("rel_sk","sk","N"),
    ("user","rel_sj","1"),("rel_sj","sj","N"),
    ("jp","rel_sj","1"),
]
w(er_pg("Full System — All 10 Modules (Chen Notation Overview)", er_svg(nodes_full, edges_full, 900, 600)))

print("Chapter 15 done")

# ─── CHAPTER 16: RELATIONSHIPS ──────────────────────────────────
w('''<div class="section">
<div class="section-header">
<div class="section-title st-relations">Chapter 16 &mdash; System Relationships: 18 Database Connections</div>
<div class="section-sub">All foreign key, one-to-one, and many-to-many relationships between the 20 models.</div>
</div>
<table class="rel-table">
<tr><th>#</th><th>From Model</th><th>Type</th><th>To Model</th><th>On Delete</th><th>Description</th></tr>
<tr><td>1</td><td><span class="t-from">RecruiterProfile</span></td><td><span class="rel-type rt-o2o">1:1</span></td><td><span class="t-to">User</span></td><td>CASCADE</td><td class="t-desc">Each recruiter has one user account</td></tr>
<tr><td>2</td><td><span class="t-from">JobSeekerProfile</span></td><td><span class="rel-type rt-o2o">1:1</span></td><td><span class="t-to">User</span></td><td>CASCADE</td><td class="t-desc">Each job seeker has one user account</td></tr>
<tr><td>3</td><td><span class="t-from">HRMember</span></td><td><span class="rel-type rt-fk">FK</span></td><td><span class="t-to">RecruiterProfile</span></td><td>CASCADE</td><td class="t-desc">Team members belong to a company</td></tr>
<tr><td>4</td><td><span class="t-from">Skill</span></td><td><span class="rel-type rt-fk">FK</span></td><td><span class="t-to">JobSeekerProfile</span></td><td>CASCADE</td><td class="t-desc">Skills belong to a profile</td></tr>
<tr><td>5</td><td><span class="t-from">Education</span></td><td><span class="rel-type rt-fk">FK</span></td><td><span class="t-to">JobSeekerProfile</span></td><td>CASCADE</td><td class="t-desc">Education history belongs to a profile</td></tr>
<tr><td>6</td><td><span class="t-from">Experience</span></td><td><span class="rel-type rt-fk">FK</span></td><td><span class="t-to">JobSeekerProfile</span></td><td>CASCADE</td><td class="t-desc">Work experience belongs to a profile</td></tr>
<tr><td>7</td><td><span class="t-from">Certification</span></td><td><span class="rel-type rt-fk">FK</span></td><td><span class="t-to">JobSeekerProfile</span></td><td>CASCADE</td><td class="t-desc">Certifications belong to a profile</td></tr>
<tr><td>8</td><td><span class="t-from">Resume</span></td><td><span class="rel-type rt-fk">FK</span></td><td><span class="t-to">User</span></td><td>CASCADE</td><td class="t-desc">Resume files belong to a user</td></tr>
<tr><td>9</td><td><span class="t-from">ParsedResume</span></td><td><span class="rel-type rt-o2o">1:1</span></td><td><span class="t-to">Resume</span></td><td>CASCADE</td><td class="t-desc">Each uploaded resume has one parsed result</td></tr>
<tr><td>10</td><td><span class="t-from">ExtractedKeyword</span></td><td><span class="rel-type rt-fk">FK</span></td><td><span class="t-to">ParsedResume</span></td><td>CASCADE</td><td class="t-desc">Keywords extracted from a parsed resume</td></tr>
<tr><td>11</td><td><span class="t-from">BuiltResume</span></td><td><span class="rel-type rt-fk">FK</span></td><td><span class="t-to">User</span></td><td>CASCADE</td><td class="t-desc">Builder-generated resumes belong to a user</td></tr>
<tr><td>12</td><td><span class="t-from">JobPost</span></td><td><span class="rel-type rt-fk">FK</span></td><td><span class="t-to">RecruiterProfile</span></td><td>CASCADE</td><td class="t-desc">Job posts are owned by a company</td></tr>
<tr><td>13</td><td><span class="t-from">SavedJob</span></td><td><span class="rel-type rt-fk">FK</span></td><td><span class="t-to">User</span></td><td>CASCADE</td><td class="t-desc">Bookmarked jobs belong to a user</td></tr>
<tr><td>14</td><td><span class="t-from">SavedJob</span></td><td><span class="rel-type rt-fk">FK</span></td><td><span class="t-to">JobPost</span></td><td>CASCADE</td><td class="t-desc">The job that was bookmarked</td></tr>
<tr><td>15</td><td><span class="t-from">MatchScore</span></td><td><span class="rel-type rt-fk">FK</span></td><td><span class="t-to">User (candidate)</span></td><td>CASCADE</td><td class="t-desc">Score computed for a candidate</td></tr>
<tr><td>16</td><td><span class="t-from">MatchScore</span></td><td><span class="rel-type rt-fk">FK</span></td><td><span class="t-to">JobPost</span></td><td>CASCADE</td><td class="t-desc">Score computed against a job</td></tr>
<tr><td>17</td><td><span class="t-from">Application</span></td><td><span class="rel-type rt-fk">FK</span></td><td><span class="t-to">JobPost</span></td><td>CASCADE</td><td class="t-desc">Application is for a specific job</td></tr>
<tr><td>18</td><td><span class="t-from">Application</span></td><td><span class="rel-type rt-fk">FK</span></td><td><span class="t-to">User (applicant)</span></td><td>CASCADE</td><td class="t-desc">Application submitted by a candidate</td></tr>
<tr><td>19</td><td><span class="t-from">Interview</span></td><td><span class="rel-type rt-o2o">1:1</span></td><td><span class="t-to">Application</span></td><td>CASCADE</td><td class="t-desc">One interview per application</td></tr>
<tr><td>20</td><td><span class="t-from">Feedback</span></td><td><span class="rel-type rt-fk">FK</span></td><td><span class="t-to">Application</span></td><td>CASCADE</td><td class="t-desc">Feedback linked to an application</td></tr>
<tr><td>21</td><td><span class="t-from">Feedback</span></td><td><span class="rel-type rt-fk">FK</span></td><td><span class="t-to">User (reviewer)</span></td><td>CASCADE</td><td class="t-desc">Who wrote the feedback</td></tr>
<tr><td>22</td><td><span class="t-from">Feedback</span></td><td><span class="rel-type rt-fk">FK</span></td><td><span class="t-to">User (reviewee)</span></td><td>CASCADE</td><td class="t-desc">Who is reviewed</td></tr>
<tr><td>23</td><td><span class="t-from">Notification</span></td><td><span class="rel-type rt-fk">FK</span></td><td><span class="t-to">User (recipient)</span></td><td>CASCADE</td><td class="t-desc">Notification delivered to a user</td></tr>
</table>
</div>
''')

print("Chapter 16 done")

# ─── CHAPTER 17: TESTING ────────────────────────────────────────
w(h("17","Testing &amp; Verification","Manual test cases, functional testing, and verification checklists","#059669"))
w(pg(
    sh("17.1  Testing Approach") +
    p("TalentBridge was tested using a combination of manual functional testing, Django's built-in system check "
      "framework, and end-to-end workflow testing. Each module was tested independently before integration testing "
      "across module boundaries.") +

    sh("17.2  System Check") +
    p("Django's system check framework (<code>python manage.py check</code>) was run after every major change "
      "to detect model errors, missing migrations, and configuration issues. Zero issues were maintained throughout development.") +

    sh("17.3  Authentication Module Tests") +
    tbl(["Test Case","Steps","Expected Result","Status"],
        [["Register as job seeker","Fill form, submit","User created, redirected to dashboard","Pass"],
         ["Register as recruiter","Fill form, submit","Recruiter profile created, redirected to panel","Pass"],
         ["Login with email","Enter email+password","Authenticated, role-based redirect","Pass"],
         ["Login with wrong password","Enter wrong password","Error message displayed","Pass"],
         ["Duplicate email registration","Register same email twice","Validation error shown","Pass"],
         ["Password reset flow","Enter email, click link","Password changed successfully","Pass"],
         ["Access recruiter page as job seeker","Direct URL access","Redirected with permission error","Pass"]],
        "#059669") +

    sh("17.4  Profile Module Tests") +
    tbl(["Test Case","Steps","Expected Result","Status"],
        [["Add skill","Fill skill form, submit","Skill appears in profile","Pass"],
         ["Delete skill","Click delete on skill","Skill removed, list updated","Pass"],
         ["Add education","Fill education form","Entry added to education list","Pass"],
         ["Upload profile picture","Choose image, submit","Image stored, displayed in profile","Pass"],
         ["Profile completeness","Fill all sections","100% completeness shown","Pass"]],
        "#059669")
))
w(pg(
    sh("17.5  Resume Module Tests") +
    tbl(["Test Case","Steps","Expected Result","Status"],
        [["Upload PDF resume","Choose PDF, submit","File stored, parsing triggered","Pass"],
         ["Upload DOCX resume","Choose DOCX, submit","File stored, parsing triggered","Pass"],
         ["View parsed skills","After upload, view parsed resume","Skills list extracted correctly","Pass"],
         ["Resume builder — classic template","Select template, submit","HTML resume rendered","Pass"],
         ["Resume builder — print PDF","Open built resume, Ctrl+P","A4 PDF generated correctly","Pass"],
         ["Upload invalid file type","Upload .txt file","Validation error shown","Pass"]],
        "#059669") +

    sh("17.6  Job Posting Tests") +
    tbl(["Test Case","Steps","Expected Result","Status"],
        [["Create job post","Fill form, submit as recruiter","Job created, status=active","Pass"],
         ["Edit job post","Edit title, save","Title updated in listing","Pass"],
         ["Toggle status active→paused","Click toggle","Job disappears from public board","Pass"],
         ["Browse job board","Visit /jobs/ as guest","All active jobs shown","Pass"],
         ["Search jobs","Enter keyword in search box","Filtered results shown","Pass"],
         ["Save job","Click bookmark on job","Job saved to my saved list","Pass"]],
        "#059669") +

    sh("17.7  Screening Module Tests") +
    tbl(["Test Case","Steps","Expected Result","Status"],
        [["Compute match score","Click Check Match on job detail","Score computed, stored, shown","Pass"],
         ["Score breakdown visible","View result page","All 4 components shown with percentages","Pass"],
         ["No duplicate score","Click Check Match twice","Existing score updated, not duplicated","Pass"],
         ["Recruiter ranked list","Recruiter views candidates","Sorted by total_score descending","Pass"],
         ["Missing skills shown","View score with missing skills","Missing skills chips displayed","Pass"]],
        "#059669") +

    sh("17.8  Application Lifecycle Tests") +
    tbl(["Test Case","Steps","Expected Result","Status"],
        [["Apply to job","Click Apply Now, submit form","Application created, status=pending","Pass"],
         ["Prevent duplicate","Apply to same job again","Redirected with 'already applied' message","Pass"],
         ["Withdraw application","Click Withdraw on pending app","Application deleted, removed from list","Pass"],
         ["Recruiter updates status","Change dropdown to shortlisted","Status updated, notification sent","Pass"],
         ["My applications page","Visit /applications/my-applications/","All applications listed with status","Pass"]],
        "#059669")
))

print("Chapter 17 done")

# ─── CHAPTER 18: SECURITY ───────────────────────────────────────
w(h("18","Security Implementation","CSRF, authentication, role-based access, file validation, and data protection","#dc2626"))
w(pg(
    sh("18.1  Authentication Security") +
    p("TalentBridge implements multiple layers of authentication security:") +
    ul("Custom email-based authentication backend using <code>AbstractBaseUser</code> interface",
       "PBKDF2 with SHA256 password hashing (Django default) — industry-standard key derivation",
       "Password minimum length validation enforced during registration",
       "Session-based authentication with Django's built-in session framework",
       "Session timeout configured to expire after user inactivity",
       "Login throttling can be added via django-axes (recommended for production)") +

    sh("18.2  CSRF Protection") +
    p("All POST forms include Django's CSRF token via the <code>{% csrf_token %}</code> template tag. "
      "Django's CsrfViewMiddleware is enabled in MIDDLEWARE settings and validates every non-GET/HEAD request. "
      "AJAX requests must include the CSRF token in headers.") +

    sh("18.3  Role-Based Access Control") +
    p("Access control is enforced at three levels:") +
    ul("URL level: <code>@login_required</code> decorator on all authenticated views",
       "Role level: Custom decorators check user.role before allowing access to recruiter or job-seeker specific views",
       "Object level: Views verify the logged-in user owns the object being accessed (e.g., recruiters can only edit their own jobs)",
       "Template level: Navigation links are conditionally shown based on user.role") +

    sh("18.4  File Upload Security") +
    p("Resume and image uploads are validated:") +
    ul("Allowed file types: .pdf, .docx for resumes; .jpg, .jpeg, .png, .gif for images",
       "File size limits enforced in form validation (typically 5MB for resumes, 2MB for images)",
       "Files stored outside the web root to prevent direct URL access",
       "Django's FileField does not execute uploaded files",
       "Content-type validation in addition to extension checking")
))
w(pg(
    sh("18.5  SQL Injection Prevention") +
    p("Django's ORM provides automatic SQL injection prevention by using parameterised queries for all database operations. "
      "Raw SQL is never used in TalentBridge. All user inputs are passed as parameters to ORM methods rather than interpolated into query strings.") +

    sh("18.6  XSS Prevention") +
    p("Django's template engine escapes HTML by default. All variables rendered in templates are automatically escaped "
      "unless explicitly marked safe with <code>|safe</code> filter (which is not used for user-generated content). "
      "User-provided text in comments, cover letters, and descriptions is escaped before rendering.") +

    sh("18.7  Secret Key Management") +
    p("The Django <code>SECRET_KEY</code> is stored as an environment variable and loaded via "
      "<code>os.environ.get('SECRET_KEY')</code>. It is never committed to the Git repository. "
      "The <code>.gitignore</code> file excludes <code>.env</code> files and the SQLite database.") +

    sh("18.8  Production Security Checklist") +
    tbl(["Setting","Dev Value","Production Value","Purpose"],
        [["DEBUG","True","False","Disable detailed error pages"],
         ["ALLOWED_HOSTS","['*']","['yourdomain.com']","Restrict valid hostnames"],
         ["SECRET_KEY","Any string","Random 50+ char string","Session and CSRF security"],
         ["EMAIL_BACKEND","Console","SMTP (Gmail/SendGrid)","Real email delivery"],
         ["DATABASES","SQLite","PostgreSQL","Production-grade RDBMS"],
         ["STATIC_ROOT","—","Set to /staticfiles/","Collected static files"],
         ["HTTPS","Off","On (via reverse proxy)","Encrypted transport"],
         ["SECURE_SSL_REDIRECT","False","True","Force HTTPS"],
         ["SESSION_COOKIE_SECURE","False","True","HTTPS-only cookies"]],
        "#dc2626")
))

print("Chapter 18 done")

# ─── CHAPTER 19: DEPLOYMENT ─────────────────────────────────────
w(h("19","Deployment &amp; Configuration","PythonAnywhere setup, settings, migrations, and go-live checklist","#0891b2"))
w(pg(
    sh("19.1  Development Setup") +
    p("To run TalentBridge locally, the following steps are required:") +
    ul("Python 3.11 and pip must be installed",
       "Create a virtual environment: <code>python -m venv env</code>",
       "Activate: <code>env\\Scripts\\activate</code> (Windows) or <code>source env/bin/activate</code> (Linux/Mac)",
       "Install dependencies: <code>pip install django pdfplumber python-docx Pillow</code>",
       "Navigate to project: <code>cd jobportal/</code>",
       "Run migrations: <code>python manage.py migrate</code>",
       "Create superuser: <code>python manage.py createsuperuser</code>",
       "Start dev server: <code>python manage.py runserver</code>",
       "Visit: http://127.0.0.1:8000/") +

    sh("19.2  Key Settings") +
    tbl(["Setting","Value","Location"],
        [["AUTH_USER_MODEL","accounts.User","settings.py"],
         ["INSTALLED_APPS","10 custom apps + django defaults","settings.py"],
         ["AUTHENTICATION_BACKENDS","accounts.backends.EmailBackend","settings.py"],
         ["MEDIA_ROOT","jobportal/media/","settings.py"],
         ["MEDIA_URL","/media/","settings.py"],
         ["TEMPLATES DIR","jobportal/templates/","settings.py"],
         ["EMAIL_BACKEND","ConsoleEmailBackend (dev)","settings.py"],
         ["DEFAULT_AUTO_FIELD","BigAutoField","settings.py"]],
        "#0891b2") +

    sh("19.3  Database Migrations") +
    p("Migrations are managed per-app:") +
    ul("Initial migration: <code>python manage.py makemigrations</code>",
       "Apply: <code>python manage.py migrate</code>",
       "Each app has its own <code>migrations/</code> directory",
       "Migration dependencies are tracked automatically by Django",
       "The <code>accounts</code> migration must run first due to AUTH_USER_MODEL dependency")
))
w(pg(
    sh("19.4  PythonAnywhere Deployment") +
    p("The production deployment on PythonAnywhere follows these steps:") +
    ul("Upload code via Git: <code>git clone https://github.com/user/talentbridge.git</code>",
       "Create a virtual environment on PythonAnywhere console",
       "Install requirements: <code>pip install -r requirements.txt</code>",
       "Set environment variables in the .env file (SECRET_KEY, DATABASE_URL)",
       "Configure WSGI file to point to <code>jobportal.wsgi</code>",
       "Run migrations on PythonAnywhere console",
       "Run <code>python manage.py collectstatic</code> for static files",
       "Configure static file serving in PythonAnywhere web dashboard",
       "Set ALLOWED_HOSTS to include the PythonAnywhere domain") +

    sh("19.5  Static Files") +
    p("TalentBridge uses no external static CSS or JavaScript files — all CSS is embedded in templates. "
      "The only static files that need serving are:") +
    ul("Admin CSS/JS (Django's built-in admin assets via collectstatic)",
       "User-uploaded media files (photos, resumes, company logos) via MEDIA_ROOT") +

    sh("19.6  File Structure") +
    tbl(["Path","Contents"],
        [["jobportal/","Main Django project directory"],
         ["jobportal/settings.py","All configuration"],
         ["jobportal/urls.py","Root URL configuration"],
         ["jobportal/templates/","All HTML templates organised by app"],
         ["jobportal/media/","Uploaded files (excluded from git)"],
         ["jobportal/static/","Static assets (empty — CSS embedded in templates)"],
         ["accounts/","Authentication app"],
         ["jobseeker/","Job seeker profile app"],
         ["resume/","Resume upload and builder app"],
         ["recruiter/","Recruiter panel app"],
         ["jobs/","Job posting app"],
         ["screening/","Resume screening app"],
         ["applications/","Application lifecycle app"],
         ["feedback/","Feedback and ratings app"],
         ["interviews/","Interview scheduling app"],
         ["notifications/","Notification system app"]],
        "#0891b2")
))

print("Chapter 19 done")

# ─── CHAPTER 20: CONCLUSION ─────────────────────────────────────
w(h("20","Conclusion &amp; Future Work","Summary of achievements, lessons learned, and planned enhancements","#1d4ed8"))
w(pg(
    sh("20.1  Project Summary") +
    p("TalentBridge successfully demonstrates that a well-architected, full-stack Django web application can "
      "significantly streamline the recruitment process for both job seekers and employers. The project achieves "
      "all stated objectives and delivers a functional, tested system ready for academic submission and real-world deployment.") +

    sh("20.2  Key Achievements") +
    ul("Implemented 10 Django applications with clean separation of concerns and a total of 20 database models",
       "Built an intelligent resume screening algorithm achieving objective, multi-dimensional candidate evaluation",
       "Developed a complete application lifecycle system from initial job discovery through hiring decision",
       "Created an integrated resume builder with 5 professional, ATS-optimised templates",
       "Implemented a bidirectional feedback system promoting accountability and transparency",
       "Designed a robust in-app notification system covering all key lifecycle events",
       "Maintained zero JavaScript framework dependencies while delivering a polished, responsive user interface",
       "Achieved clean Django system check output (zero errors/warnings) throughout development") +

    sh("20.3  Technical Lessons Learned") +
    ul("Custom AUTH_USER_MODEL must be set before the first migration — changing it later requires database reset",
       "OneToOneField profiles are preferred over extending User directly for maintainability",
       "Django's ORM makes complex queries readable but requires careful use of select_related() for performance",
       "Template inheritance is powerful but requires careful base template design to avoid duplication",
       "File uploads require robust validation at form level, view level, and storage level",
       "The screening algorithm's weight distribution (40/25/15/20) proved effective but could benefit from ML tuning",
       "Context processors are the right tool for global data like unread notification counts")
))
w(pg(
    sh("20.4  Future Enhancements") +
    p("The following features are planned for future iterations of TalentBridge:") +
    tbl(["Feature","Priority","Description"],
        [["Email Notifications","High","Send real emails for key events via SMTP (currently console only)"],
         ["Advanced Search","High","Full-text search with Elasticsearch or PostgreSQL FTS"],
         ["Mobile App","Medium","React Native or Flutter app consuming a Django REST API"],
         ["AI-Enhanced Matching","Medium","ML model trained on hiring outcomes to improve screening accuracy"],
         ["Video Interviews","Medium","Integrated WebRTC video calling for in-platform interviews"],
         ["Calendar Integration","Medium","Google Calendar / Outlook sync for interview scheduling"],
         ["Analytics Dashboard","Low","Recruiter analytics: time-to-hire, application funnel, source tracking"],
         ["Multi-Language Support","Low","i18n for Hindi, Arabic, French, Spanish"],
         ["Job Alerts","Low","Email/SMS alerts when new jobs match saved search criteria"],
         ["Company Reviews","Low","Glassdoor-style company review aggregation from Feedback model"]],
        "#1d4ed8") +

    sh("20.5  Academic Reflection") +
    p("This project provided hands-on experience with every layer of a production web application: "
      "database design and ORM, authentication and security, file handling, algorithm implementation, "
      "template design, and deployment. The modular Django architecture proved invaluable in managing "
      "the complexity of a 10-module application — each app could be developed and tested in isolation "
      "before integration.") +
    p("The most challenging aspect was the screening algorithm design. Determining the right weights "
      "for skill, experience, education, and keyword matching required careful consideration of what "
      "recruiters actually value. The chosen weights (40/25/15/20) are informed by industry research "
      "showing that skill match is the primary hiring criterion in technical roles.") +
    p("TalentBridge represents a complete, deployable solution that demonstrates the full stack of "
      "modern web development skills: from database modelling and server-side logic to template design "
      "and production deployment.") +

    sh("20.6  References") +
    ul("Django Documentation (5.2) — docs.djangoproject.com",
       "Python 3.11 Documentation — docs.python.org",
       "pdfplumber Library — github.com/jsvine/pdfplumber",
       "python-docx Library — python-docx.readthedocs.io",
       "OWASP Top 10 Security Guidelines — owasp.org",
       "PythonAnywhere Deployment Guide — help.pythonanywhere.com",
       "Django Best Practices — spellbookpress.com/books/twd-django",
       "Two Scoops of Django — Feldroy, A. & Greenfeld, D.")
))

# ─── CLOSING HTML ───────────────────────────────────────────────
w("""
<div style="background:#0f172a;color:rgba(255,255,255,.5);text-align:center;padding:40px 20px;margin-top:40px;font-size:.8rem;">
TalentBridge &mdash; Job Portal with Intelligent Resume Screening &nbsp;|&nbsp;
Academic Project Report &nbsp;|&nbsp; Django 5.2.4 &nbsp;|&nbsp;
10 Modules &bull; 20 Models &bull; 18 Relationships
</div>
</body>
</html>
""")
print("All done! Project_Report.html generated.")





















