from copy import deepcopy
from io import BytesIO
from pathlib import Path
import os

from docx import Document
from docx.enum.text import WD_ALIGN_PARAGRAPH as Align
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Inches, Pt, RGBColor
from docx.text.paragraph import Paragraph

root=Path(__file__).parent
out=root/'formato_propio'
out.mkdir(exist_ok=True)
name='Taller_U2_Omenius_Formato_ESPE_APA7'
original=Document(root/'apa7'/'Taller_U2_Omenius.docx')
template=Document(Path(os.environ['USERPROFILE'])/'Downloads'/'DEBERES.docx')
doc=original
body=doc._body
old=doc.paragraphs
tables=doc.tables
cover_table=tables[0]
fields={r.cells[0].text:r.cells[1].text for r in cover_table.rows[1:]}
title=old[5].text
subtitle=old[6].text
first=old[9]._p
present=deepcopy(next(p._p for p in old[:9] if p.hyperlinks))

def format_text(p, size=12, bold=None, center=None, leading=None):
    for r in p.runs:
        r.font.name='Times New Roman'
        r.font.size=Pt(size)
        if bold is not None:r.bold=bold
        r.font.color.rgb=RGBColor(0,0,0)
    for h in p.hyperlinks:
        for r in h.runs:
            r.font.name='Times New Roman'
            r.font.size=Pt(size)
    if center is not None:
        p.alignment=Align.CENTER if center else Align.LEFT
    if leading is not None:
        p.paragraph_format.line_spacing=leading

def before(element, text, style=None):
    node=OxmlElement('w:p')
    element.addprevious(node)
    p=Paragraph(node,body)
    if style:p.style=style
    p.add_run(text)
    p.paragraph_format.line_spacing=2
    p.paragraph_format.space_before=Pt(0)
    p.paragraph_format.space_after=Pt(0)
    return p

def label(p, level, new=None):
    p.style=f'Heading {level}'
    if new:p.runs[0].text=new
    format_text(p,bold=True,center=level==1,leading=2)
    f=p.paragraph_format
    f.first_line_indent=Pt(0)
    f.keep_with_next=True
    f.space_before=Pt(10)
    f.space_after=Pt(0)

# Cover copies the original institutional banner and exact institutional wording.
logo=template.paragraphs[0]._p.xpath('.//a:blip')[0]
blob=template.part.related_parts[logo.get(qn('r:embed'))].blob
logo_para=before(first,'')
logo_para.paragraph_format.space_before=Pt(0)
logo_para.paragraph_format.space_after=Pt(20)
logo_para.paragraph_format.line_spacing=1
logo_para.alignment=Align.CENTER
logo_para.add_run().add_picture(BytesIO(blob),width=Inches(8.08))
# Center the banner relative to the whole Letter sheet.
logo_para.paragraph_format.left_indent=Inches(-.8)
logo_para.paragraph_format.right_indent=Inches(-.8)
logo_para.paragraph_format.first_line_indent=Pt(0)

for i in range(1,4):
    p=before(first,template.paragraphs[i].text)
    format_text(p,bold=True,center=True,leading=1.5)
    if i==3:p.paragraph_format.space_after=Pt(49)

cover_fields=[
('PERIODO', fields['Periodo']),
('ASIGNATURA', fields['Asignatura']),
('TEMA',title+'\n'+subtitle),
('NOMBRES',fields['Integrantes']),
('NIVEL-PARALELO',fields['Nivel y grupo']),
('DOCENTE',fields['Docente']),
('FECHA DE ENTREGA',fields['Fecha']),
]
for i,(key,value) in enumerate(cover_fields):
    p=before(first,'')
    f=p.paragraph_format
    f.left_indent=Inches(2.11)
    f.first_line_indent=Inches(-2)
    f.tab_stops.add_tab_stop(Inches(2.11))
    f.space_after=Pt(10)
    p.add_run(key).bold=True
    p.add_run('\t'+value)
    format_text(p,center=False,leading=1.5)

for i in (16,17):
    p=before(first,template.paragraphs[i].text)
    format_text(p,center=True,leading=1.5)
    if i==16:p.paragraph_format.space_before=Pt(40)

for p in old[:9]:
    p._p.getparent().remove(p._p)
cover_table._tbl.getparent().remove(cover_table._tbl)

by_text={p.text:p for p in old[9:]}
for p in old[9:]:
    format_text(p,size=12,center=None)
    if p.style.name.startswith('Heading'):
        label(p,2)
    if p.text in {'RESUMEN EJECUTIVO','MÉTODO Y EVIDENCIA COMPARADA','COMPARACIÓN METODOLÓGICA','ANÁLISIS MULTICRITERIO','RESULTADO DE LA SELECCIÓN','RESULTADOS DEL PROYECTO','DISCUSIÓN CIENTÍFICA','PROPUESTA PARA EL SGSI'}:
        p._p.getparent().remove(p._p)
    if p.text.startswith('ANEXO '):
        label(p,1)
    if not p.text and p._p.xpath('.//w:drawing'):
        p.alignment=Align.CENTER
    if p.text.startswith(("Criterios del archivo:","Fuentes del caso:")):
        p.paragraph_format.keep_together=True

intro=by_text['Decisión y alcance']
major=before(intro._p,'1. Introducción')
label(major,1)
major.paragraph_format.page_break_before=True
major.paragraph_format.space_before=Pt(0)

objective=by_text['Objetivo y unidad de análisis']
label(objective,1,'2. Sistema de objetivos')
obj=next(p for p in old if p.text.startswith('Determinar qué método'))
obj_text=obj.text
general,sep,scope=obj_text.partition('. ')
label(before(obj._p,'2.1. Objetivo general'),2)
obj.runs[0].text=general+'.'
specific=by_text['Qué aportan los cuatro estudios']
source=next(p for p in old if p.text.startswith('Fuentes del caso:'))
anchor=source._p
label(before(anchor,'2.2. Objetivos específicos'),2)
for item in [
    'Comparar los enfoques aplicados en las cuatro investigaciones y en el proyecto de Omenius.',
    'Evaluar los cinco referentes con la matriz multicriterio ponderada.',
    'Definir acciones y evidencias de cierre para los riesgos prioritarios.',
]:
    p=before(anchor,'•  '+item)
    p.paragraph_format.left_indent=Inches(.5)
    p.paragraph_format.first_line_indent=Inches(-.2)
    format_text(p)
label(before(anchor,'Unidad de análisis'),2)
p=before(anchor,scope)
p.paragraph_format.first_line_indent=Inches(.5)
format_text(p)
label(before(specific._p,'3. Desarrollo'),1)
for i,section in enumerate([
    'Qué aportan los cuatro estudios','Cinco referentes, cinco usos','Cómo se tomó la decisión',
    'Qué método conviene a Omenius','Qué riesgos requieren atención',
    'Qué se puede concluir de la comparación','Plan de mejora y decisiones de cierre'
],1):
    label(by_text[section],2,f'3.{i}. {section}')
label(by_text['Conclusiones y recomendaciones'],1,'4. Conclusiones y recomendaciones')
label(by_text['Referencias'],1)
by_text['Referencias'].paragraph_format.space_before=Pt(0)
# Place the existing Canva link next to the academic identification on the cover.
major._p.addprevious(present)
link_para=Paragraph(present,body)
link_para.paragraph_format.first_line_indent=Pt(0)
format_text(link_para)
link_para.alignment=Align.CENTER
link_para.paragraph_format.space_before=Pt(13)
link_para.paragraph_format.space_after=Pt(0)
for t in doc.tables:
    for r in t.rows:
        for c in r.cells:
            for p in c.paragraphs:format_text(p,10)
for sec in doc.sections:
    sec.page_width=Inches(8.5)
    sec.page_height=Inches(11)
    sec.left_margin=sec.right_margin=sec.top_margin=sec.bottom_margin=Inches(1)
    for p in sec.header.paragraphs:p.style='Normal'
normal=doc.styles['Normal']
normal.font.name='Times New Roman'
normal.font.size=Pt(12)
doc.save(out/(name+'.docx'))

# Export both formats from the same paragraph, table, figure, and link content.
from reportlab.platypus import BaseDocTemplate, Frame, PageTemplate, Paragraph as PdfParagraph, Table, TableStyle, Image, KeepTogether, Spacer, PageBreak
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.styles import ParagraphStyle
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from docx.table import Table as WordTable
from xml.sax.saxutils import escape, quoteattr
from reportlab.lib.utils import ImageReader

fontfolder=Path(r'C:\Windows\Fonts')
for face,file in [('Times','times.ttf'),('TimesB','timesbd.ttf'),('TimesI','timesi.ttf'),('TimesBI','timesbi.ttf')]:
    pdfmetrics.registerFont(TTFont(face,str(fontfolder/file)))
pdfmetrics.registerFontFamily('Times',normal='Times',bold='TimesB',italic='TimesI',boldItalic='TimesBI')

def rich(p):
    chunks=[]
    for r in p.runs:
        text=escape(r.text).replace('\n','<br/>')
        if r.bold:text='<b>'+text+'</b>'
        if r.italic:text='<i>'+text+'</i>'
        chunks.append(text)
    for h in p.hyperlinks:
        chunks.append('<link href='+quoteattr(h.url)+' color="#006655">'+escape(h.text)+'</link>')
    return ''.join(chunks)

def style(p, size=12, spacing=None):
    f=p.paragraph_format
    return ParagraphStyle('ESPE',fontName='Times',fontSize=size,
        leading=size*(spacing or f.line_spacing or 2),
        alignment=1 if p.alignment==Align.CENTER else 0,
        firstLineIndent=f.first_line_indent.pt if f.first_line_indent else 0,
        leftIndent=f.left_indent.pt if f.left_indent else 0,
        spaceBefore=f.space_before.pt if f.space_before else 0,
        spaceAfter=f.space_after.pt if f.space_after else 0,
        keepWithNext=bool(f.keep_with_next),allowWidows=0,allowOrphans=0)

story=[]
cover=True
for child in body._body:
    if child.tag==qn('w:p'):
        p=Paragraph(child,body)
        if child==major._p:
            cover=False
        elif p.paragraph_format.page_break_before:
            story.append(PageBreak())
        if cover:continue
        drawings=p._p.xpath('.//w:drawing')
        if drawings:
            pic=drawings[0]
            ext=pic.xpath('.//wp:extent')[0]
            blip=pic.xpath('.//a:blip')[0]
            stream=BytesIO(p.part.related_parts[blip.get(qn('r:embed'))].blob)
            im=Image(stream,width=int(ext.get('cx'))/12700,height=int(ext.get('cy'))/12700)
            im.keepWithNext=bool(p.paragraph_format.keep_with_next)
            story.append(im)
        elif p.text:
            item=PdfParagraph(rich(p),style(p))
            story.append(KeepTogether([item]) if p.paragraph_format.keep_together else item)
    elif child.tag==qn('w:tbl'):
        t=WordTable(child,body)
        rows=[[PdfParagraph(rich(c.paragraphs[0]),style(c.paragraphs[0],10,1.15)) for c in row.cells] for row in t.rows]
        widths=[col.width.pt for col in t.columns]
        tb=Table(rows,colWidths=[w*468/sum(widths) for w in widths],repeatRows=1,hAlign='LEFT')
        tb.setStyle(TableStyle([
            ('VALIGN',(0,0),(-1,-1),'TOP'),('LINEABOVE',(0,0),(-1,0),.65,colors.black),
            ('LINEBELOW',(0,0),(-1,0),.65,colors.black),('LINEBELOW',(0,-1),(-1,-1),.65,colors.black),
            ('TOPPADDING',(0,0),(-1,-1),2),('BOTTOMPADDING',(0,0),(-1,-1),2),
        ]))
        story.extend([tb,Spacer(1,6)])

def numbered(canvas,number):
    canvas.setFont('Times',12)
    canvas.drawRightString(letter[0]-72,letter[1]-41,str(number))

def cover_page(canvas):
    width,height=letter
    image=ImageReader(BytesIO(blob))
    iw,ih=image.getSize()
    banner_w=8.08*72
    banner_h=banner_w*ih/iw
    canvas.drawImage(image,(width-banner_w)/2,height-72-banner_h,banner_w,banner_h,mask='auto')
    y=height-72-banner_h-20
    for i in range(1,4):
        p=PdfParagraph('<b>'+escape(template.paragraphs[i].text)+'</b>',style(template.paragraphs[i],spacing=1.5))
        _,h=p.wrap(468,200)
        p.drawOn(canvas,72,y-h)
        y-=h
    y-=49
    for key,value in cover_fields:
        canvas.setFont('TimesB',12)
        canvas.drawString(80,y-14,key)
        p=PdfParagraph(escape(value).replace('\n','<br/>'),ParagraphStyle('Campo',fontName='Times',fontSize=12,leading=18))
        _,h=p.wrap(316,200)
        p.drawOn(canvas,224,y-h)
        y-=h+10
    y-=40
    canvas.setFont('Times',12)
    for i in (16,17):
        canvas.drawCentredString(width/2,y-14,template.paragraphs[i].text)
        y-=18
    p=PdfParagraph(rich(link_para),style(link_para))
    _,h=p.wrap(468,100)
    p.drawOn(canvas,72,y-h-13)
    assert y-h-13>60
    numbered(canvas,1)

from reportlab.pdfgen import canvas
from pypdf import PdfReader, PdfWriter
first_pdf=BytesIO()
paper=canvas.Canvas(first_pdf,pagesize=letter)
cover_page(paper)
paper.showPage()
paper.save()
report=BytesIO()
pdf=BaseDocTemplate(report,pagesize=letter,leftMargin=72,rightMargin=72,topMargin=72,bottomMargin=72,title=title,author=fields['Integrantes'])
def body_number(cv, document):
    numbered(cv,document.page+1)
frame=Frame(72,72,468,648,leftPadding=0,rightPadding=0,topPadding=0,bottomPadding=0)
pdf.addPageTemplates(PageTemplate('ESPE',frames=[frame],onPage=body_number))
pdf.build(story)
result=PdfWriter()
result.append(PdfReader(first_pdf))
result.append(PdfReader(report))
result.add_metadata({'/Title':title,'/Author':fields['Integrantes']})
with (out/(name+'.pdf')).open('wb') as f:result.write(f)

