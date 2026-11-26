from pathlib import Path
import re
from docx import Document
from docx.shared import Inches, Pt, RGBColor
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.enum.text import WD_ALIGN_PARAGRAPH as Align
from docx.text.paragraph import Paragraph
from docx.enum.table import WD_TABLE_ALIGNMENT

root=Path(__file__).parent
out=root/'apa7'
out.mkdir(exist_ok=True)
name='Taller_U2_Omenius'
doc=Document(root/(name+'.docx'))
titles=['Caracterización de Omenius','Comparación de las investigaciones y del proyecto Omenius','Comparación de los cinco referentes de gestión de riesgos','Matriz multicriterio ponderada','Aplicación de ISO/IEC 27005 y MAGERIT en Omenius','Escenarios prioritarios y evidencia de cierre','Plan de mejora del SGSI','Escenarios de riesgo de Omenius','Correspondencia de campos en SimpleRisk']
mention={12:'La Tabla 1 resume la caracterización de la organización.',20:'La Tabla 2 compara los cuatro estudios con el proyecto de Omenius.',25:'La Tabla 3 presenta los cinco referentes evaluados.',32:'La Figura 1 muestra los pesos de decisión.',35:'La Tabla 4 presenta las puntuaciones por criterio.',44:'La Figura 2 muestra las puntuaciones finales.',46:'La Tabla 5 resume cómo aplicar la combinación.',54:'La Figura 3 compara la valoración inherente y la meta residual. La Tabla 6 detalla los escenarios prioritarios.',70:'La Tabla 7 reúne las acciones y los criterios de cierre.',99:'La Tabla A1 recoge los doce escenarios.',108:'La Figura B1 muestra el contenedor activo.',112:'La Tabla B1 detalla la correspondencia de los campos.'}
def setup(p, size=11, bold=False, indent=False, center=False, spacing=2, keep=False):
    f=p.paragraph_format
    f.line_spacing=spacing
    f.space_before=f.space_after=Pt(0)
    f.first_line_indent=Inches(.5 if indent else 0)
    f.left_indent=f.right_indent=Inches(0)
    f.keep_with_next=keep
    f.widow_control=True
    p.alignment=Align.CENTER if center else Align.LEFT
    for r in p.runs:
        r.font.name='Calibri'
        r.font.size=Pt(size)
        r.font.color.rgb=RGBColor(0,0,0)
        r.bold=bold
    for r in p._p.xpath('./w:hyperlink/w:r'):
        pr=r.find(qn('w:rPr'))
        size_el=pr.find(qn('w:sz'))
        if size_el is not None:size_el.set(qn('w:val'),str(size*2))

def add_before(e, text, italic=False):
    node=OxmlElement('w:p')
    e.addprevious(node)
    p=Paragraph(node,doc._body)
    r=p.add_run(text)
    setup(p,bold=not italic,keep=True)
    r.italic=italic
    return p

ps=doc.paragraphs
for i,p in enumerate(ps):
    if i in mention:p.add_run(' '+mention[i])
    if i==29:p.runs[0].text=p.runs[0].text.replace('ISO (2018, 2022)','International Organization for Standardization (2018, 2022)').replace('NIST (2024)','National Institute of Standards and Technology (2024)')
    if i==17:p.runs[0].text=p.runs[0].text.replace('2026a–c','2026a, 2026b, 2026c')
    for r in p.runs:
        if 'Grupo 5 (2026a–c)' in r.text:r.text=r.text.replace('2026a–c','2026a, 2026b, 2026c')
    p.paragraph_format.page_break_before=i in (10,78,97,104)
    cover=i<10
    heading=p.style.name.startswith('Heading')
    kicker=bool(p.text) and p.text.isupper() and i>=10
    drawing=bool(p._p.xpath('.//w:drawing'))
    is_reference=79<=i<=96 and i not in (89,90)
    setup(p,size=19 if i==5 else 11,bold=i in (1,4,5) or heading or kicker, indent=not (cover or heading or kicker or drawing or is_reference or not p.text or i in (121,122)),center=cover or kicker or p.style.name=='Heading 1',keep=heading or kicker or drawing)
    if i in (77,89,90,115) or (not p.text and not drawing):
        p._p.getparent().remove(p._p)
    if is_reference:
        p.paragraph_format.left_indent=Inches(.5)
        p.paragraph_format.first_line_indent=Inches(-.5)
        p.paragraph_format.keep_together=True
    if i in (73,74,75):
        p.paragraph_format.keep_with_next=True
    if heading and i not in (11,78,98,105):
        p.paragraph_format.space_before=Pt(8)
    if i in (34,43,53,110):
        label, caption=p.text.split('. ',1)
        p_prev=ps[i-1]
        title,mark,rest=caption.partition('. ')
        if i==34:title=caption.rstrip('.')
        add_before(p_prev._p,label)
        add_before(p_prev._p,title,True)
        if rest:
            p.clear()
            p.add_run('Nota. ').italic=True
            p.add_run(rest)
            setup(p)
        else:
            p_prev.paragraph_format.keep_with_next=False
            p._p.getparent().remove(p._p)
for j,t in enumerate(doc.tables):
    if j==0:
        t.alignment=WD_TABLE_ALIGNMENT.CENTER
    else:
        label=f'Tabla {j}' if j<=7 else ['Tabla A1','Tabla B1'][j-8]
        add_before(t._tbl,label)
        add_before(t._tbl,titles[j-1],True)
    for j_col,col in enumerate(t.columns):
        col.width=int(col.width*16.0/17.35)
    for i,row in enumerate(t.rows):
        if i==0:row._tr.get_or_add_trPr().append(OxmlElement('w:tblHeader'))
        for j_col,cell in enumerate(row.cells):
            cell.width=t.columns[j_col].width
            pr=cell._tc.get_or_add_tcPr()
            for el in pr.findall(qn('w:shd')):pr.remove(el)
            borders=OxmlElement('w:tcBorders')
            for side in (['top','bottom'] if i==0 else ['bottom'] if i==len(t.rows)-1 else []):
                el=OxmlElement('w:'+side);el.set(qn('w:val'),'single');el.set(qn('w:sz'),'6');borders.append(el)
            pr.append(borders)
            for p in cell.paragraphs:
                for r in p.runs:
                    r.text=r.text.replace('Grupo 5 (2026a–c)','Grupo 5 (2026a, 2026b, 2026c)')
                setup(p,10 if j else 11,bold=i==0 or (j==0 and j_col==0),spacing=1.15,keep=i==0)
for k,shape in enumerate(doc.inline_shapes):
    if shape.width>Inches(6.18):
        shape.height=int(shape.height*Inches(6.18)/shape.width)
        shape.width=Inches(6.18)
for sec in doc.sections:
    sec.top_margin=sec.bottom_margin=sec.left_margin=sec.right_margin=Inches(1)
    sec.header_distance=Inches(.5)
    sec.different_first_page_header_footer=False
    h=sec.header.paragraphs[0];h.clear();setup(h);h.alignment=Align.RIGHT
    field=OxmlElement('w:fldSimple');field.set(qn('w:instr'),'PAGE');h._p.append(field)
    sec.footer.paragraphs[0].clear()
lang=OxmlElement('w:lang');lang.set(qn('w:val'),'es-EC')
doc.styles['Normal'].element.get_or_add_rPr().append(lang)
doc.save(out/(name+'.docx'))

from reportlab.platypus import SimpleDocTemplate, Paragraph as P, Table, TableStyle, Image, KeepTogether, Spacer, PageBreak
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from docx.table import Table as WordTable
from xml.sax.saxutils import escape, quoteattr
from io import BytesIO

fontfolder=Path(r'C:\Windows\Fonts')
for face,file in [('Calibri','calibri.ttf'),('CalibriB','calibrib.ttf'),('CalibriI','calibrii.ttf'),('CalibriBI','calibriz.ttf')]:
    pdfmetrics.registerFont(TTFont(face,str(fontfolder/file)))
pdfmetrics.registerFontFamily('Calibri',normal='Calibri',bold='CalibriB',italic='CalibriI',boldItalic='CalibriBI')
def rich(p):
    chunks=[]
    for r in p.runs:
        s=escape(r.text).replace('\n','<br/>')
        if r.bold:s='<b>'+s+'</b>'
        if r.italic:s='<i>'+s+'</i>'
        chunks.append(s)
    for h in p.hyperlinks:
        chunks.append('<link href='+quoteattr(h.url)+' color="#006655">'+escape(h.text)+'</link>')
    return ''.join(chunks)
def style(p, size, spacing=2):
    f=p.paragraph_format
    return ParagraphStyle('APA',fontName='Calibri',fontSize=size,leading=size*spacing,
         alignment=1 if p.alignment==Align.CENTER else 0,
         firstLineIndent=f.first_line_indent.pt if f.first_line_indent else 0,
         leftIndent=f.left_indent.pt if f.left_indent else 0,
         spaceBefore=f.space_before.pt if f.space_before else 0,
         keepWithNext=bool(f.keep_with_next),allowWidows=0,allowOrphans=0)
story=[]
for child in doc._body._body:
    if child.tag==qn('w:p'):
        p=Paragraph(child,doc._body)
        if p.paragraph_format.page_break_before:story.append(PageBreak())
        drawing=p._p.xpath('.//w:drawing')
        if drawing:
            pic=drawing[0]
            ext=pic.xpath('.//wp:extent')[0]
            blip=pic.xpath('.//a:blip')[0]
            stream=BytesIO(p.part.related_parts[blip.get(qn('r:embed'))].blob)
            im=Image(stream,width=int(ext.get('cx'))/12700,height=int(ext.get('cy'))/12700)
            im.keepWithNext=bool(p.paragraph_format.keep_with_next)
            story.append(im)
        elif p.text:
            size=next((r.font.size.pt for r in p.runs if r.font.size),11)
            item=P(rich(p),style(p,size))
            story.append(KeepTogether([item]) if p.paragraph_format.keep_together else item)
    elif child.tag==qn('w:tbl'):
        t=WordTable(child,doc._body)
        rows=[[P(rich(c.paragraphs[0]),style(c.paragraphs[0],10,1.15)) for c in row.cells] for row in t.rows]
        widths=[col.width.pt for col in t.columns]
        tb=Table(rows,colWidths=[w*444/sum(widths) for w in widths],repeatRows=1,hAlign='LEFT')
        tb.setStyle(TableStyle([('VALIGN',(0,0),(-1,-1),'TOP'),('LINEABOVE',(0,0),(-1,0),.65,colors.black),
           ('LINEBELOW',(0,0),(-1,0),.65,colors.black),('LINEBELOW',(0,-1),(-1,-1),.65,colors.black)]))
        story.extend([tb,Spacer(1,6)])
def page_number(canvas, pdf):
    canvas.setFont('Calibri',11)
    canvas.drawRightString(A4[0]-72,A4[1]-41,str(pdf.page))
pdf=SimpleDocTemplate(str(out/(name+'.pdf')),pagesize=A4,leftMargin=72,rightMargin=72,topMargin=72,bottomMargin=72,title=doc.core_properties.title,author=doc.core_properties.author)
pdf.build(story,onFirstPage=page_number,onLaterPages=page_number)


