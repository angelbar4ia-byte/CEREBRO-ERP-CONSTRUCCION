"""Parametriza el PRETIL en los 7 prototipos con la regla que se resolvió en Zafiro.

Lee Hoja1 del libro de Zafiro v45 (trae los siete capítulos) y escribe PRETIL_7_PROTOTIPOS.xlsx
con cada partida del pretil de cada prototipo: cantidad del catálogo, cantidad que toca al pretil,
precio, importe y ratio por m² de pretil. Uso: python3 -I medir_pretil.py [libro.xlsx] [salida.xlsx]
"""
import sys,openpyxl
from openpyxl.styles import Font,PatternFill,Alignment
from openpyxl.utils import get_column_letter as L
LIBRO=sys.argv[1] if len(sys.argv)>1 else 'CATALOGO_PARAMETRICO_con_MURO_ZAFIRO_CAPAS_v45.xlsx'
SALIDA=sys.argv[2] if len(sys.argv)>2 else 'PRETIL_7_PROTOTIPOS.xlsx'
PROTOS=['Zafiro 1.0','Rubí','Zafiro Plus','Jade','Diamante −','Diamante +','Oro 4.01']
H=list(openpyxl.load_workbook(LIBRO,read_only=True)['Hoja1'].iter_rows(values_only=True))
caps=[i for i,r in enumerate(H) if r[0]=='Capítulo']
sub=None;subp=None;C=[]
for i,r in enumerate(H):
    p=sum(1 for j in caps if j<=i)-1
    if r[0]=='Subcapítulo': sub=(r[7] or '').strip(); subp=p
    if r[0]=='Concepto':
        C.append(dict(p=p,sub=sub if subp==p else None,clave=r[5] or '',desc=(r[7] or ''),u=r[10],q=r[11] or 0,pu=r[12] or 0,imp=r[13] or 0,ubi=r[25]))
AZ=('AZOTEA','AZOTEA/ROOF')
# regla de Zafiro (hoja Paramétrico PRETIL): (capa, concepto, claves, dónde, regla)
#   'todo' = toda la cantidad del catálogo en la azotea; 'tope' = lo que no pasa de los m² del pretil
#   (la franja de fachada +3.00 se reparte: al pretil lo que mida el pretil, el resto va a MURO)
REGLAS=[
 ('OBRA NEGRA','Muro tabique de pretil',('EST-02010','EST-02011'),'az','todo','muro'),
 ('OBRA NEGRA','Castillo K-1',('EST-02110',),'az','todo',None),
 ('OBRA NEGRA','Cadena CD-1',('BAP-01100',),'az','todo',None),
 ('OBRA GRIS','Repellado 3.00',('ALB-01010',),'az','todo',None),
 ('OBRA GRIS','Repellado fachada +3.00',('ALB-01212',),'todas','tope',None),
 ('OBRA GRIS','Boquilla exterior',('ACA-01051',),'az','todo',None),
 ('OBRA BLANCA','Finas exteriores 3.00',('ACA-20012',),'az','todo',None),
 ('OBRA BLANCA','Boquilla fina exterior',('ACA-01072',),'az','todo',None),
 ('OBRA BLANCA','Finas fachada +3.00',('ACA-20020',),'az','tope',None),
]
filas=[]   # (p,capa,concepto,clave,desc,u,q_cat,pu,regla,nota)
for p in range(7):
    cs=[c for c in C if c['p']==p]
    for capa,conc,claves,donde,regla,_ in REGLAS:
        sel=[c for c in cs if c['clave'] in claves and (c['sub'] in AZ if donde=='az' else True)]
        if p in (4,5) and conc=='Finas fachada +3.00': sel=[c for c in cs if c['clave'] in claves and c['sub'] in AZ]
        for c in sel:
            filas.append((p,capa,conc,c['clave'],c['desc'][:90],c['u'],c['q'],c['pu'],regla,''))
    # pintura: línea de fachada con ubicación INTERIOR cuya cantidad se parece más al repellado del pretil
    rep=sum(c['q'] for c in cs if c['clave']=='ALB-01010' and c['sub'] in AZ)
    if p==0:
        for c in cs:
            if c['clave'] in('ACA-30031','ACA-30032') and c['ubi']=='INTERIOR':
                filas.append((p,'PINTURA',('Pintura fachada 2 manos' if c['clave'].endswith('1') else 'Pintura fachada 2 manos (2ª mano, Zafiro)'),c['clave'],c['desc'][:90],c['u'],c['q'],c['pu'],'todo','igual que el libro curado (filas 399-400)'))
    else:
        cand=[c for c in cs if c['clave']=='ACA-03047' and c['ubi']=='INTERIOR']
        if cand:
            c=min(cand,key=lambda c:abs(c['q']-rep))
            nota='línea INTERIOR de ACA-03047 más cercana al repellado del pretil ('+f'{rep:g}'+' m²)'
            if p in (4,5): nota+='; poca confianza: las dos líneas se parecen poco al pretil'
            filas.append((p,'PINTURA','Pintura fachada 2 manos',c['clave'],c['desc'][:90],c['u'],c['q'],c['pu'],'todo',nota))
wb=openpyxl.Workbook(); lee=wb.active; lee.title='LEEME'
res=wb.create_sheet('RESUMEN'); par=wb.create_sheet('PARTIDAS')
HF=Font(bold=True,color='FFFFFF'); HB=PatternFill('solid',fgColor='305496')
def head(ws,r,vals):
    for i,v in enumerate(vals,1):
        c=ws.cell(r,i,v); c.font=HF; c.fill=HB; c.alignment=Alignment(wrap_text=True,vertical='center')
head(par,1,['Prototipo','Capa','Concepto','Clave','Descripción','Unidad','Cantidad en el catálogo','Regla','Cantidad del pretil','Precio unitario','Importe','Ratio (cant. por m² de pretil)','Nota'])
for i,(p,capa,conc,cl,d,u,q,pu,regla,nota) in enumerate(filas,2):
    par.cell(i,1,PROTOS[p]);par.cell(i,2,capa);par.cell(i,3,conc);par.cell(i,4,cl);par.cell(i,5,d);par.cell(i,6,u);par.cell(i,7,q);par.cell(i,8,regla);par.cell(i,10,pu);par.cell(i,13,nota)
    # m² del pretil del prototipo = suma de las partidas 'Muro tabique de pretil'
    topes=f'SUMIFS($I$2:$I${len(filas)+1},$A$2:$A${len(filas)+1},$A{i},$C$2:$C${len(filas)+1},"Muro tabique de pretil")'
    par.cell(i,9,f'=IF(H{i}="tope",MIN(G{i},{topes}),G{i})')
    par.cell(i,11,f'=I{i}*J{i}').number_format='#,##0.00'
    par.cell(i,12,f'=IF({topes}=0,"",I{i}/{topes})').number_format='0.00'
n=len(filas)+1
for col,w in zip('ABCDEFGHIJKLM',(13,14,26,11,56,7,12,8,12,11,12,12,58)): par.column_dimensions[col].width=w
par.freeze_panes='A2'; par.auto_filter.ref=f'A1:M{n}'
# RESUMEN
res['A1']='PRETIL EN LOS 7 PROTOTIPOS (regla resuelta en Zafiro)'; res['A1'].font=Font(bold=True,size=13)
res['A2']='Cada fila suma las partidas del pretil de la hoja PARTIDAS. $/m² = importe ÷ m² de muro de pretil. CV = desviación ÷ media. Confianza: ≤10 % utilizable · ≤25 % revisar · >25 % no usar.'
head(res,4,['Concepto','Unidad']+PROTOS+['n','Media','Desv. muestral','CV muestral','CV poblacional','Confianza','Libro curado Zafiro','Libro curado Oro'])
capas=['OBRA NEGRA','OBRA GRIS','OBRA BLANCA','PINTURA']
r=5
res.cell(r,1,'m² de muro de pretil (driver)');res.cell(r,2,'m²')
for p in range(7): res.cell(r,3+p,f'=SUMIFS(PARTIDAS!$I$2:$I${n},PARTIDAS!$A$2:$A${n},{L(3+p)}$4,PARTIDAS!$C$2:$C${n},"Muro tabique de pretil")').number_format='#,##0.00'
res.cell(r,16,62);res.cell(r,17,45)
bloque1=r+1
lab=[('Importe '+c.lower(),c) for c in capas]
for k,(t,c) in enumerate(lab):
    rr=bloque1+k; res.cell(rr,1,t);res.cell(rr,2,'$')
    for p in range(7): res.cell(rr,3+p,f'=SUMIFS(PARTIDAS!$K$2:$K${n},PARTIDAS!$A$2:$A${n},{L(3+p)}$4,PARTIDAS!$B$2:$B${n},"{c}")').number_format='#,##0'
rt=bloque1+4; res.cell(rt,1,'Importe del pretil');res.cell(rt,2,'$')
for p in range(7): res.cell(rt,3+p,f'=SUM({L(3+p)}{bloque1}:{L(3+p)}{bloque1+3})').number_format='#,##0'
res.cell(rt,16,75537.12);res.cell(rt,17,108957.16)
tb=rt+2
res.cell(tb-1,1,'TASAS ($ por m² de muro de pretil)').font=Font(bold=True)
for k,(t,c) in enumerate(lab+[('TOTAL del pretil',None)]):
    rr=tb+k; res.cell(rr,1,t.replace('Importe ','$/m² '));res.cell(rr,2,'$/m²')
    src=bloque1+k if c else rt
    for p in range(7):
        cl=L(3+p); res.cell(rr,3+p,f'=IF({cl}$5=0,"",{cl}{src}/{cl}$5)').number_format='#,##0.00'
    res.cell(rr,10,f'=COUNT(C{rr}:I{rr})')
    res.cell(rr,11,f'=AVERAGE(C{rr}:I{rr})').number_format='#,##0.00'
    res.cell(rr,12,f'=STDEV(C{rr}:I{rr})').number_format='#,##0.00'
    res.cell(rr,13,f'=L{rr}/K{rr}').number_format='0.0%'
    res.cell(rr,14,f'=STDEVP(C{rr}:I{rr})/K{rr}').number_format='0.0%'
    res.cell(rr,15,f'=IF(J{rr}<5,"insuficiente",IF(M{rr}<=0.1,"utilizable",IF(M{rr}<=0.25,"revisar","no usar")))&" (n="&J{rr}&")"')
res.cell(tb+4,16,1218.34);res.cell(tb+4,17,2421.27)
# ratios clave
rb=tb+7
res.cell(rb-1,1,'RATIOS (cantidad por m² de pretil): la parametrización de cada prototipo').font=Font(bold=True)
head(res,rb,['Concepto','Unidad']+PROTOS+['n','Media','Desv. muestral','CV muestral','CV poblacional'])
conceptos=[(x[1],x[5]) for x in REGLAS]+[('Pintura fachada 2 manos','m²')]
for k,(cn,_) in enumerate(conceptos):
    rr=rb+1+k; res.cell(rr,1,cn);res.cell(rr,2,'por m²')
    for p in range(7):
        cl=L(3+p)
        res.cell(rr,3+p,f'=IF({cl}$5=0,"",SUMIFS(PARTIDAS!$I$2:$I${n},PARTIDAS!$A$2:$A${n},{cl}${4},PARTIDAS!$C$2:$C${n},$A{rr})/{cl}$5)').number_format='0.00'
    res.cell(rr,10,f'=COUNT(C{rr}:I{rr})')
    res.cell(rr,11,f'=IF(J{rr}=0,"",AVERAGE(C{rr}:I{rr}))').number_format='0.00'
    res.cell(rr,12,f'=IF(J{rr}<2,"",STDEV(C{rr}:I{rr}))').number_format='0.00'
    res.cell(rr,13,f'=IF(L{rr}="","",L{rr}/K{rr})').number_format='0.0%'
    res.cell(rr,14,f'=IF(J{rr}<2,"",STDEVP(C{rr}:I{rr})/K{rr})').number_format='0.0%'
# Oro tal como está en el libro curado
ro=rb+len(conceptos)+4
res.cell(ro-1,1,'ORO: LIBRO CURADO FRENTE A LA REGLA DE ZAFIRO').font=Font(bold=True)
head(res,ro,['Concepto','','Libro curado Oro v19','Regla de Zafiro','Diferencia'])
datos=[('Repellado fachada +3.00 (m²)',300,'=SUMIFS(PARTIDAS!$I$2:$I$%d,PARTIDAS!$A$2:$A$%d,"Oro 4.01",PARTIDAS!$C$2:$C$%d,"Repellado fachada +3.00")'%(n,n,n)),
       ('Finas fachada +3.00 (m²)',300,'=SUMIFS(PARTIDAS!$I$2:$I$%d,PARTIDAS!$A$2:$A$%d,"Oro 4.01",PARTIDAS!$C$2:$C$%d,"Finas fachada +3.00")'%(n,n,n)),
       ('Importe del pretil ($)',108957.16,'=I%d'%rt),
       ('$/m² de pretil',2421.27,'=I%d'%(tb+4))]
for k,(t,a,f) in enumerate(datos):
    rr=ro+1+k; res.cell(rr,1,t); res.cell(rr,3,a).number_format='#,##0.00'; res.cell(rr,4,f).number_format='#,##0.00'; res.cell(rr,5,f'=D{rr}-C{rr}').number_format='#,##0.00'
res.column_dimensions['A'].width=42
for c in range(2,18): res.column_dimensions[L(c)].width=13
res.column_dimensions['O'].width=22; res.freeze_panes='C5'
txt=['PRETIL EN LOS 7 PROTOTIPOS','',
 'Qué es: la parametrización del pretil que se resolvió en Zafiro (hoja Paramétrico PRETIL, 62 m², $75,537, $1,218/m²) aplicada con la misma regla a Rubí, Zafiro Plus, Jade, Diamante − y +, y Oro. El driver es el m² de muro de pretil (tabique de 14 cm en la azotea).',
 '',
 'La regla de Zafiro, tal como se aplica aquí:',
 '1. Obra negra: muro tabique, castillo K-1 y cadena CD-1 de la azotea, completos.',
 '2. Obra gris: repellado 3.00 y boquilla exterior de la azotea, completos; repellado de fachada +3.00 con tope en los m² del pretil.',
 '3. Obra blanca: finas exteriores 3.00 y boquilla fina de la azotea, completas; finas de fachada +3.00 con tope en los m² del pretil.',
 '4. Pintura: la línea de pintura de fachada con ubicación INTERIOR que más se parece al repellado del pretil (en Zafiro, las filas 399-400 del libro curado).',
 '5. El tope de la franja +3.00 es lo que Zafiro resolvió: de 73 m² de fachada +3.00, 62 van al pretil (= su muro) y 11 al muro. La parte que pasa del tope pertenece a MURO FACHADA, no al pretil.',
 '6. Sin chapeo de piedra (revestimiento) y sin lijado y sellado (Zafiro no lo trae en el catálogo), igual que el libro curado.',
 '',
 'Validación: la regla reproduce el libro curado de Zafiro al centavo ($75,537.12 en las cuatro capas).',
 '',
 'Hallazgo en Oro: el libro curado (v19) pone en el pretil los 300 m² de repellado y 300 m² de finas de fachada +3.00 que el catálogo trae en la azotea. Con la regla de Zafiro al pretil le tocan 45 m² (su muro) y los otros 255 m² van a MURO FACHADA. Eso explica que su $/m² fuera casi el doble (2,421 contra 1,218): 255 m² × $159.03 de repellado + 255 m² × $79.71 de finas + una boquilla de 18.2 m del libro curado suman $61,804 de diferencia. La sección «Oro: libro curado frente a la regla» lo cuantifica. El libro de Oro no se modificó.',
 '',
 'Límites:',
 '- Diamante − y + tienen un pretil de 19.2 m² (tercer nivel) y su línea de pintura de pretil es una suposición de poca confianza.',
 '- Zafiro Plus y Diamante usan la clave EST-02011 (muro del 3er nivel) como muro de pretil.',
 '- El catálogo no etiqueta la pintura de pretil; se infiere por cantidad (nota de cada fila en PARTIDAS). Es la capa menos estable (CV de 65 %) y no se debe usar sola.',
 '- Zafiro cobra la pintura en dos conceptos (1ª y 2ª mano); los demás prototipos en un concepto de 2 manos. El ratio por m² usa solo la primera mano.',
 '','Reproducir: python3 -I medir_pretil.py (usa el libro de Zafiro v45).']
for i,t in enumerate(txt,1):
    c=lee.cell(i,1,t); c.alignment=Alignment(wrap_text=True,vertical='top')
    if i==1: c.font=Font(bold=True,size=13)
lee.column_dimensions['A'].width=140
wb.calculation.fullCalcOnLoad=True
wb.save(SALIDA); print('partidas',len(filas))
