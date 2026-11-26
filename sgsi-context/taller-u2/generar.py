from pathlib import Path
import os, io, csv, json, re, zipfile, html, math
from PIL import Image, ImageDraw, ImageFont
from pypdf import PdfReader
from docx import Document
from docx.shared import Cm, Inches, Pt, RGBColor
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.opc.constants import RELATIONSHIP_TYPE as RT
from docx.enum.table import WD_TABLE_ALIGNMENT, WD_CELL_VERTICAL_ALIGNMENT
from docx.enum.text import WD_ALIGN_PARAGRAPH
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib.styles import ParagraphStyle
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import Paragraph, Table, TableStyle, Spacer, Image as RImage
from xml.sax.saxutils import escape, quoteattr

root=Path(__file__).resolve().parent
dld=Path(os.environ['USERPROFILE'])/'Downloads'
pages=json.loads((root/'data.json').read_text('utf8'))
risks=list(csv.reader((root/'risks.csv').open(encoding='utf8')))
assert len(risks)==12 and len({r[1] for r in risks})==12
levels=['ACEPTABLE','TOLERABLE','ALTO','EXTREMO']
before=[sum(r[14]==s for r in risks) for s in levels]
after=[sum(r[27]==s for r in risks) for s in levels]
assert before==[1,4,7,0] and after==[10,2,0,0]
ink='#17333C'; green='#006655'; muted='#48626B'; pale='#E7F2EF'; line='#C9DCD7'; soft='#F4F8F7'
fontdir=Path(r'C:\Windows\Fonts')
def f(s,b=False):
    return ImageFont.truetype(str(fontdir/('calibrib.ttf' if b else 'calibri.ttf')),s)
for name,file in [('Cal','calibri.ttf'),('CalB','calibrib.ttf'),('CalI','calibrii.ttf'),('CalBI','calibriz.ttf')]:
    pdfmetrics.registerFont(TTFont(name,str(fontdir/file)))
pdfmetrics.registerFontFamily('Cal',normal='Cal',bold='CalB',italic='CalI',boldItalic='CalBI')
def bars(name,labels,vals,maximum,marks,unit,fmt):
    w,h=1300,346
    im=Image.new('RGB',(w,h),'white'); d=ImageDraw.Draw(im)
    x0,x1=330,1155; y0,step=27,53
    for v in marks:
        xx=x0+int(v/maximum*(x1-x0)); d.line((xx,y0,xx,282),fill=line,width=2);d.text((xx,287),str(v),font=f(26),anchor='mt',fill=muted)
    for i,(s,v) in enumerate(zip(labels,vals)):
        yy=y0+step*i+3
        d.text((x0-15,yy+13),s,font=f(29),anchor='rm',fill=ink)
        xx=x0+int(v/maximum*(x1-x0));d.rounded_rectangle((x0,yy,xx,yy+28),radius=6,fill=green if i==0 else '#47968A')
        d.text((xx+10,yy+14),fmt(v),font=f(27,True),anchor='lm',fill=ink)
    d.text((x1,325),unit,font=f(21),anchor='rm',fill=muted);im.save(root/(name+'.png'))
bars('weights',['Integración con el SGSI','Valoración de activos','Viabilidad operativa','Trazabilidad','Acceso documental'],[30,25,20,15,10],30,[0,5,10,15,20,25,30],'Peso (%)',lambda v:str(v)+' %')
scores=[[5,4,4,5,2],[3,5,3,5,5],[3,4,5,3,5],[3,4,2,5,5],[3,2,4,3,2]]
total=[sum(a*b for a,b in zip(row,[30,25,20,15,10]))/100 for row in scores]
assert total==[4.25,4,3.85,3.55,2.85]
bars('scores',['ISO/IEC 27005','MAGERIT v3','OCTAVE Allegro','NIST SP 800-30¹','ISO 31000'],total,5,list(range(6)),'Adecuación al caso (puntos)',lambda v:f'{v:.2f}'.replace('.',','))
im=Image.new('RGB',(1300,392),'white');d=ImageDraw.Draw(im);x0,x1=225,1150
for j in range(0,11,2):
    x=x0+(x1-x0)*j/10;d.line((x,57,x,318),fill=line,width=2);d.text((x,326),str(j),font=f(26),anchor='mt',fill=muted)
for i,s in enumerate(['Aceptable','Tolerable','Alto','Extremo']):
    y=62+i*65;d.text((x0-15,y+23),s,font=f(29),anchor='rm',fill=ink)
    for j,(v,c) in enumerate([(before[i],green),(after[i],'#9FCBC3')]):
        yy=y+j*22;xx=x0+v*(x1-x0)/10
        if v: d.rectangle((x0,yy,xx,yy+16),fill=c)
        d.text((xx+9,yy+8),str(v),font=f(23,True),anchor='lm',fill=ink)
for x,s,c in [(240,'Inherente',green),(580,'Residual objetivo','#9FCBC3')]:
    d.rectangle((x,16,x+28,34),fill=c);d.text((x+41,25),s,font=f(26,True),anchor='lm',fill=ink)
d.text((x1,371),'Número de escenarios',font=f(22),anchor='rm',fill=muted);im.save(root/'risks.png')
logo=PdfReader(str(dld/'32829_Investigacion1_Grupo5.pdf')).pages[0].images[0].image
logo=logo.convert('RGBA')
bg=Image.new('RGBA',logo.size,'white')
bg.alpha_composite(logo)
bg.convert('RGB').save(root/'banner.png')
with zipfile.ZipFile(dld/'TAREA_SIMPLERISK_JF_RIESGOS_RESPALDO.docx') as z:
    img=Image.open(io.BytesIO(z.read('word/media/image1.png')));img.convert('RGB').save(root/'docker.png')
for p in pages:
    p['blocks']=[(['table',[.088,.108,.384,.068,.068,.132,.152],[['Riesgo','Activo','Amenaza','P','I','Inherente','Meta']]+[[r[1],r[2],r[5],r[12],r[11],r[13],r[26]] for r in risks]] if b[0]=='risk_table' else b) for b in p['blocks']]
title='Selección de una metodología de gestión de riesgos para Omenius'
subtitle='Análisis comparativo y propuesta de mejora del SGSI'
fields=[('Asignatura','Gestión de la Seguridad Informática · NRC 32829'),('Integrantes','Aldo Saula y Joseph Andrés Franco Villagómez'),('Docente','Ing. Javier Cevallos'),('Nivel y grupo','Octavo · Grupo 5'),('Periodo','Septiembre 2026 – febrero 2027'),('Fecha','26 de noviembre de 2026')]
def plain(s):return s.replace('*','')
def rich(s):return ''.join(('<i>'+escape(v)+'</i>' if i%2 else escape(v)) for i,v in enumerate(s.split('*')))
def clr(s):return colors.HexColor(s)
def ps(n,sz,lead,c=ink,b=False,**extra):
    return ParagraphStyle(n,fontName='CalB' if b else 'Cal',fontSize=sz,leading=lead,textColor=clr(c),splitLongWords=1,**extra)
def par(s,style):return Paragraph(rich(s),style)
def picture(name,maxw,maxh):
    q=root/(name+'.png')
    with Image.open(q) as im:w,h=im.size
    factor=min(maxw/w,maxh/h);return str(q),w*factor,h*factor
def drawheader(c,idx,k):
    c.setFillColor(clr(green));c.rect(39,798,18,4,stroke=0,fill=1)
    c.setFont('CalB',9);c.drawString(66,797,'ESPE  /  GESTIÓN DE LA SEGURIDAD INFORMÁTICA')
    c.setFillColor(clr(muted));c.setFont('Cal',9);c.drawRightString(555,797,'UNIDAD 2  ·  GRUPO 5')
    c.setStrokeColor(clr(line));c.line(40,42,555,42)
    c.setFont('Cal',9);c.drawString(40,27,'Santo Domingo  /  Omenius');c.drawRightString(555,27,str(idx))
def smalltable(fr,rows,w):
    dense=len(fr)>5
    arr=[]
    for i,row in enumerate(rows):
        arr.append([par(c,ps('tc',8.9 if dense else 9.65,11 if dense else 12,'#FFFFFF' if i==0 else ink,i==0 or j==0)) for j,c in enumerate(row)])
    tab=Table(arr,colWidths=[v*w for v in fr])
    tab.setStyle(TableStyle([('VALIGN',(0,0),(-1,-1),'TOP'),('BACKGROUND',(0,0),(-1,0),clr(green)),('ROWBACKGROUNDS',(0,1),(-1,-1),[clr(soft),colors.white]),('LINEBELOW',(0,0),(-1,-1),.45,clr(line)),('LEFTPADDING',(0,0),(-1,-1),5),('RIGHTPADDING',(0,0),(-1,-1),5),('TOPPADDING',(0,0),(-1,-1),5),('BOTTOMPADDING',(0,0),(-1,-1),5)]))
    return tab
def pdf_report():
    c=canvas.Canvas(str(root/'Taller_U2_Omenius.pdf'),pagesize=A4)
    c.setTitle(title);c.setAuthor('Grupo 5 · ESPE')
    x=43;w=509; fp,iw,ih=picture('banner',w,69);c.drawImage(fp,x,739,iw,ih,mask='auto')
    c.setFillColor(clr(green));c.setFont('CalB',13);c.drawString(x,687,'UNIVERSIDAD DE LAS FUERZAS ARMADAS ESPE')
    c.setFillColor(clr(muted));c.setFont('Cal',12);c.drawString(x,665,'Sede Santo Domingo · Departamento de Ciencias de la Computación')
    c.drawString(x,647,'Carrera de Ingeniería en Tecnologías de la Información')
    c.setFillColor(clr(green));c.rect(x,574,45,5,fill=1,stroke=0)
    el=par(title,ps('ct',35,39,ink,True));_,hh=el.wrap(w,200);el.drawOn(c,x,554-hh)
    c.setFont('Cal',17);c.setFillColor(clr(muted));c.drawString(x,554-hh-29,subtitle)
    y=320
    for a,b in fields:
        c.setFillColor(clr(green));c.setFont('CalB',11);c.drawString(x,y,a);c.setFillColor(clr(ink));c.setFont('Cal',12);c.drawString(x+121,y,b);c.setStrokeColor(clr(line));c.line(x,y-9,552,y-9);y-=30
    c.setFillColor(clr(green));c.setFont('CalB',11);c.drawString(x,110,'Abrir la presentación de resultados en Canva')
    c.linkURL('https://canva.link/z644vorel7v0ilp',(x,107,x+227,123),relative=0)
    c.setFillColor(clr(muted));c.setFont('Cal',11);c.drawString(x,65,'Santo Domingo, Ecuador');c.showPage()
    for i,page in enumerate(pages,2):
        drawheader(c,i,page['kicker']); els=[]
        def append(v,gap=7):els.extend([v,Spacer(1,gap)])
        append(par(page['kicker'].upper(),ps('k',10,13,green,True)),3)
        append(par(page['title'],ps('h1',25.5,29,ink,True)),15)
        for block in page['blocks']:
            k=block[0]
            if k=='h':append(par(block[1],ps('h',14,16.5,green,True)),4)
            if k=='p':append(par(block[1],ps('p',11.35,15)),9)
            if k=='note':append(par(block[1],ps('n',9.7,12.4,muted)),8)
            if k=='table':append(smalltable(block[1],block[2],w),10)
            if k=='fig':
                ff,ww,hh=picture(block[1],w,152 if block[1]!='docker' else 142)
                append(RImage(ff,width=ww,height=hh),3);append(par(block[2],ps('fig',9.4,12.3,muted)),10)
            if k=='ref':
                rs=ps('r',11,14,leftIndent=15,firstLineIndent=-15)
                s=rich(block[1])
                if block[2]:s+=' <link color="#006655" href='+quoteattr(block[2])+'>'+escape(block[2])+'</link>'
                append(Paragraph(s,rs),10)
        heights=[el.wrap(w,1200)[1] for el in els]
        ratio=min(1,709/sum(heights)); assert ratio>.79,(i,ratio)
        c.saveState();c.translate(x,767);c.scale(ratio,ratio);y=0
        for el,hh in zip(els,heights):
            y-=hh;el.drawOn(c,0,y)
        c.restoreState();c.showPage()
    c.save()
def font_run(r,sz=11,b=False,col=ink):
    r.font.name='Calibri';r.font.size=Pt(sz);r.bold=b;r.font.color.rgb=RGBColor.from_string(col[1:]);return r
def dp(container,txt='',sz=11,b=False,col=ink,after=5,lead=1.08,style=None):
    q=container.add_paragraph(style=style);q.paragraph_format.space_before=Pt(0);q.paragraph_format.space_after=Pt(after);q.paragraph_format.line_spacing=lead
    for j,part in enumerate(txt.split('*')):
        if part:font_run(q.add_run(part),sz,b,col).italic=bool(j%2)
    return q
def attr(tag,**attrs):
    e=OxmlElement('w:'+tag)
    for a,v in attrs.items():e.set(qn('w:'+a),str(v))
    return e
def link(q,url):
    hyper=OxmlElement('w:hyperlink');hyper.set(qn('r:id'),q.part.relate_to(url,RT.HYPERLINK,is_external=True))
    rr=OxmlElement('w:r');rp=OxmlElement('w:rPr');rp.append(attr('color',val='006655'));rp.append(attr('sz',val='19'));rr.append(rp)
    tt=OxmlElement('w:t');tt.text=url;rr.append(tt);hyper.append(rr);q._p.append(hyper)
def dt(doc,fr,rows):
    t=doc.add_table(rows=0,cols=len(fr));t.autofit=False;t.alignment=WD_TABLE_ALIGNMENT.CENTER;size=17.35
    for j,frac in enumerate(fr):t.columns[j].width=Cm(size*frac)
    mar=OxmlElement('w:tblCellMar')
    for k,v in [('top',42),('bottom',42),('left',56),('right',56)]:mar.append(attr(k,w=v,type='dxa'))
    t._tbl.tblPr.append(mar)
    for i,row in enumerate(rows):
        tr=t.add_row();tr._tr.get_or_add_trPr().append(attr('cantSplit'));cells=tr.cells
        for j,(c,txt) in enumerate(zip(cells,row)):
            c.width=Cm(size*fr[j]);c.vertical_alignment=WD_CELL_VERTICAL_ALIGNMENT.TOP
            shade=green if i==0 else soft if i%2 else '#FFFFFF';c._tc.get_or_add_tcPr().append(attr('shd',fill=shade[1:]))
            q=c.paragraphs[0];q.paragraph_format.space_after=Pt(1);q.paragraph_format.line_spacing=1.0
            font_run(q.add_run(txt),8.7 if len(fr)>5 else 9.4,i==0 or j==0,'#FFFFFF' if i==0 else ink)
    dp(doc,'',3,after=1)
def doc_report():
    doc=Document();sec=doc.sections[0];sec.page_width=Cm(21);sec.page_height=Cm(29.7);sec.left_margin=Cm(1.82);sec.right_margin=Cm(1.82);sec.top_margin=Cm(1.90);sec.bottom_margin=Cm(1.75);sec.header_distance=Cm(.78);sec.footer_distance=Cm(.8)
    sec.different_first_page_header_footer=True
    norm=doc.styles['Normal'];norm.font.name='Calibri';norm.font.size=Pt(11)
    hdr=sec.header.paragraphs[0];font_run(hdr.add_run('ESPE   /   GESTIÓN DE LA SEGURIDAD INFORMÁTICA                                      UNIDAD 2   ·   GRUPO 5'),9,True,green)
    footer=sec.footer.paragraphs[0];footer.alignment=WD_ALIGN_PARAGRAPH.RIGHT;font_run(footer.add_run('Omenius   /   Santo Domingo       ·       '),9,False,muted);fld=attr('fldSimple',instr='PAGE');footer._p.append(fld)
    doc.add_picture(str(root/'banner.png'),width=Cm(17.15))
    dp(doc,'UNIVERSIDAD DE LAS FUERZAS ARMADAS ESPE',17,True,green,4);dp(doc,'Sede Santo Domingo · Departamento de Ciencias de la Computación',12,after=2);dp(doc,'Carrera de Ingeniería en Tecnologías de la Información',12,after=45)
    dp(doc,'GESTIÓN DE LA SEGURIDAD INFORMÁTICA  /  UNIDAD 2',10,True,green,10);dp(doc,title,31,True,after=8);dp(doc,subtitle,17,False,muted,38)
    dt(doc,[.25,.75],[['Ficha académica','Grupo 5']]+[list(i) for i in fields]);q=dp(doc,'Presentación de resultados en Canva  ·  ',10,True,green,8);link(q,'https://canva.link/z644vorel7v0ilp')
    dp(doc,'Santo Domingo, Ecuador',11,False,muted,0)
    for pg in pages:
        head=dp(doc,pg['kicker'].upper(),10,True,green,2);head.paragraph_format.page_break_before=True
        dp(doc,pg['title'],23,True,ink,9,1.03,'Heading 1')
        for b in pg['blocks']:
            k=b[0]
            if k=='h':dp(doc,b[1],14,True,green,3,1.0,'Heading 2')
            if k=='p':dp(doc,b[1],11.2,after=7)
            if k=='note':dp(doc,b[1],9.5,False,muted,6)
            if k=='table':dt(doc,b[1],b[2])
            if k=='fig':
                name,ww,hh=picture(b[1],480,142 if b[1]!='docker' else 133)
                q=doc.add_paragraph();q.paragraph_format.space_after=Pt(1);q.add_run().add_picture(name,width=Pt(ww),height=Pt(hh))
                dp(doc,b[2],9.4,False,muted,7)
            if k=='ref':
                q=dp(doc,b[1],10.9,after=8);q.paragraph_format.left_indent=Cm(.65);q.paragraph_format.first_line_indent=Cm(-.65)
                if b[2]:q.add_run(' ');link(q,b[2])
    cp=doc.core_properties;cp.title=title;cp.author='Grupo 5 · ESPE';cp.subject=subtitle
    doc.save(root/'Taller_U2_Omenius.docx')
pdf_report();doc_report()
print('PDF:',len(PdfReader(str(root/'Taller_U2_Omenius.pdf')).pages),'páginas. DOCX y PDF generados.')

