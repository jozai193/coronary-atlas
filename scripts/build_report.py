"""Render the report's single Markdown source to a maximum-six-page PDF."""
from pathlib import Path
import re
from xml.sax.saxutils import escape
from reportlab.platypus import SimpleDocTemplate,Paragraph,Spacer,PageBreak,Table,TableStyle,Image,KeepTogether
from reportlab.lib.styles import getSampleStyleSheet,ParagraphStyle
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from PIL import Image as PILImage
from pypdf import PdfReader

ROOT=Path(__file__).resolve().parents[1]
source=ROOT/'docs/technical_report.md'
out=ROOT/'output/pdf/technical_report.pdf';out.parent.mkdir(parents=True,exist_ok=True)
styles=getSampleStyleSheet()
styles.add(ParagraphStyle('BodyAtlas',fontName='Helvetica',fontSize=9.5,leading=13.3,spaceAfter=9,textColor=colors.HexColor('#304b49')))
styles.add(ParagraphStyle('TitleAtlas',fontName='Helvetica-Bold',fontSize=25,leading=30,spaceAfter=13,textColor=colors.HexColor('#176e68')))
styles.add(ParagraphStyle('HeadAtlas',fontName='Helvetica-Bold',fontSize=13,leading=18,spaceBefore=9,spaceAfter=8,textColor=colors.HexColor('#176e68')))
styles.add(ParagraphStyle('CaptionAtlas',fontName='Helvetica',fontSize=8,leading=10.5,spaceAfter=10,textColor=colors.HexColor('#6e8179')))
styles.add(ParagraphStyle('CellAtlas',fontName='Helvetica',fontSize=7.3,leading=10,textColor=colors.HexColor('#304b49')))


def clean(text):
    text=text.replace('–','-').replace('—','-').replace('’',"'").replace('“','"').replace('”','"').replace('‑','-')
    text=text.replace('**','').replace('`','')
    return escape(text)


def footer(canvas,doc):
    canvas.saveState();w,h=A4
    canvas.setStrokeColor(colors.HexColor('#d9e5df'));canvas.line(44,43,w-44,43)
    canvas.setFont('Helvetica',7);canvas.setFillColor(colors.HexColor('#708378'))
    canvas.drawString(44,30,'CORONARY ATLAS  |  TRACK A  |  RESEARCH PROTOTYPE')
    canvas.drawRightString(w-44,30,str(doc.page));canvas.restoreState()


story=[];lines=source.read_text(encoding='utf-8').splitlines();i=0
while i<len(lines):
    line=lines[i].strip()
    if not line:i+=1;continue
    if line=='<!-- PAGEBREAK -->':story.append(PageBreak());i+=1;continue
    if line.startswith('# '):story.append(Paragraph(clean(line[2:]),styles['TitleAtlas']));i+=1;continue
    if line.startswith('## '):story.append(Paragraph(clean(line[3:]),styles['HeadAtlas']));i+=1;continue
    if line.startswith('!['):
        match=re.match(r'!\[(.*?)\]\((.*?)\)',line);caption,path=match.groups();path=source.parent/path
        with PILImage.open(path) as im:w,h=im.size
        width=507; height=width*h/w
        if height>347:width*=347/height;height=347
        story.append(Image(str(path),width=width,height=height));story.append(Spacer(1,6));story.append(Paragraph(clean(caption),styles['CaptionAtlas']));i+=1;continue
    if line.startswith('|'):
        rows=[]
        while i<len(lines) and lines[i].startswith('|'):
            cells=[s.strip() for s in lines[i].strip('|').split('|')]
            if not all(re.fullmatch(r'[-:]+',c) for c in cells):rows.append([Paragraph(clean(c),styles['CellAtlas']) for c in cells])
            i+=1
        table=Table(rows,colWidths=[507/len(rows[0])]*len(rows[0]),repeatRows=1)
        table.setStyle(TableStyle([('BACKGROUND',(0,0),(-1,0),colors.HexColor('#e9f2eb')),('LINEBELOW',(0,0),(-1,-1),.35,colors.HexColor('#dbe5dc')),('TOPPADDING',(0,0),(-1,-1),7),('BOTTOMPADDING',(0,0),(-1,-1),7),('VALIGN',(0,0),(-1,-1),'TOP')]))
        story.extend([table,Spacer(1,12)]);continue
    paragraph=[line];i+=1
    while i<len(lines) and lines[i].strip() and not lines[i].startswith(('#','|','![','<!--')):
        paragraph.append(lines[i].strip());i+=1
    story.append(Paragraph(clean(' '.join(paragraph)),styles['BodyAtlas']))
doc=SimpleDocTemplate(str(out),pagesize=A4,rightMargin=44,leftMargin=44,topMargin=39,bottomMargin=55,title='Coronary Atlas - Technical Report',author='Coronary Atlas',pageCompression=1)
doc.build(story,onFirstPage=footer,onLaterPages=footer)
count=len(PdfReader(out).pages)
if count>6:raise RuntimeError(f'Report is {count} pages; reduce layout before release.')
print(f'Rendered {out} ({count} pages)')
