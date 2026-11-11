"""Tabla de aparatos y salidas (PUNTOS, no áreas) de los 7 prototipos.

Lee Hoja1 del libro de Zafiro v45 (trae los siete capítulos) y curado_aparatos.json
(grupos y claves de los libros curados de Zafiro y Oro) y escribe TABLA_APARATOS_SALIDAS.xlsx.
Uso: python3 -I tabla_aparatos_salidas.py [libro.xlsx] [salida.xlsx]
"""
import sys,json,collections,statistics
import openpyxl
from openpyxl.styles import Font,PatternFill,Alignment
from openpyxl.utils import get_column_letter as L

LIBRO=sys.argv[1] if len(sys.argv)>1 else 'CATALOGO_PARAMETRICO_con_MURO_ZAFIRO_CAPAS_v45.xlsx'
SALIDA=sys.argv[2] if len(sys.argv)>2 else 'TABLA_APARATOS_SALIDAS.xlsx'
PROTOS=['Zafiro 1.0','Rubí','Zafiro Plus','Jade','Diamante −','Diamante +','Oro 4.01']
FAM={'HIDROSANITARIAS':('ISN','IHD','MSA','ACC-0101'),'GAS':('IGAS',),'ELÉCTRICAS':('IEC',),'EQUIPOS':('EQU',)}
cur=json.load(open('curado_aparatos.json'))

H=list(openpyxl.load_workbook(LIBRO,read_only=True)['Hoja1'].iter_rows(values_only=True))
caps=[i for i,r in enumerate(H) if r[0]=='Capítulo']
def proto(i):
    b=0
    for k,j in enumerate(caps):
        if j<=i: b=k
    return b
CON=[dict(p=proto(i),clave=r[5] or '',desc=(r[7] or '')[:100],u=r[10],q=r[11] or 0,imp=r[13] or 0) for i,r in enumerate(H) if r[0]=='Concepto']

# --- grupos de los libros curados
G=collections.OrderedDict()   # (sis,grupo) -> dict
for m in ('Z','O'):
    for g in cur[m]['grupos']:
        k=(g['sis'],g['grupo']); e=G.setdefault(k,dict(esc=g['esc'],anc={'Z':set(),'O':set()},base={}))
        e['anc'][m].update(g['anclas']); e['base'][m]=g['base']
        if 'salidas' in (g['esc'] or '').lower(): e['esc']='Por salidas'
DET=collections.defaultdict(lambda: collections.OrderedDict())  # (sis,grupo) -> {(etapa,clave):desc}
for m in ('Z','O'):
    for d in cur[m]['detalle']:
        DET[(d['sis'],d['grupo'])].setdefault((d['etapa'],d['clave']),d['desc'])
for (s,g),e in G.items():       # anclas de respaldo: etapa ACCESORIO del libro de Oro
    for m in ('Z','O'):
        if not e['anc'][m] and e['esc']=='Por salidas' and e['base'].get(m) is not None:
            e['anc'][m]={c for (et,c) in DET[(s,g)] if (et or '').upper().startswith('ACCES')}
# claves que ningún libro curado usaba, asignadas a su grupo (asignaciones_sin_grupo.json)
ASIG=json.load(open('asignaciones_sin_grupo.json'))
DESC0={c['clave']:c['desc'] for c in CON}
ASIGNADAS={}
for a in ASIG:
    k=(a['sis'],a['grupo']); assert k in G,k
    DET[k].setdefault((a['etapa'],a['clave']),DESC0.get(a['clave'],''))
    ASIGNADAS[(a['sis'],a['clave'])]=a
# anclas corregidas a mano: el ancla del libro curado es una tapa ciega agregada, no el punto
ANCLA_MANUAL={('ELÉCTRICAS','TV'):['IEC-01080']}
for k,cl in ANCLA_MANUAL.items():
    G[k]['anc']['Z']=set(cl); G[k]['anc']['O']=set(cl)
def cat_de(esc): 
    e=(esc or '').lower()
    return 'puntos' if 'salidas' in e else ('redes por m²' if 'm²' in e else 'fijo')
clave_cat={}   # (sis,clave)->categoria (puntos gana)
claves_grupos=collections.defaultdict(set)
for (s,g),e in G.items():
    c=cat_de(e['esc'])
    for (et,cl) in DET[(s,g)]:
        claves_grupos[(s,cl)].add(g)
        cur_c=clave_cat.get((s,cl))
        if cur_c is None or c=='puntos' or (c=='fijo' and cur_c=='redes por m²'): clave_cat[(s,cl)]=c

wb=openpyxl.Workbook(); lee=wb.active; lee.title='LEEME'
sis_ws=wb.create_sheet('SISTEMAS'); sg=wb.create_sheet('SIN_GRUPO'); asg=wb.create_sheet('ASIGNADAS'); gr=wb.create_sheet('GRUPOS'); et=wb.create_sheet('ETAPAS'); an=wb.create_sheet('ANCLAS'); im=wb.create_sheet('IMPORTES')
HF=Font(bold=True,color='FFFFFF'); HB=PatternFill('solid',fgColor='305496')
def head(ws,r,vals):
    for i,v in enumerate(vals,1):
        c=ws.cell(r,i,v); c.font=HF; c.fill=HB; c.alignment=Alignment(wrap_text=True,vertical='center')
# --- IMPORTES: una fila por prototipo, sistema y clave
head(im,1,['Prototipo','Sistema','Categoría','Clave','Descripción','Unidad','Cantidad','Importe'])
agg=collections.OrderedDict()
for c in CON:
    for s,pf in FAM.items():
        if c['clave'].startswith(pf):
            k=(c['p'],s,c['clave']); a=agg.setdefault(k,[c['desc'],c['u'],0,0]); a[2]+=c['q']; a[3]+=c['imp']
r=2
for (p,s,cl),(d,u,q,i) in sorted(agg.items(),key=lambda x:(x[0][0],x[0][1],x[0][2])):
    cat=clave_cat.get((s,cl),'sin grupo')
    for j,v in enumerate((PROTOS[p],s,cat,cl,d,u,q,i),1): im.cell(r,j,v)
    r+=1
nim=r-1
for col,w in zip('ABCDEFGH',(14,18,14,12,70,8,10,13)): im.column_dimensions[col].width=w
im.freeze_panes='A2'; im.auto_filter.ref=f'A1:H{nim}'
# --- SIN_GRUPO: claves que ningún libro curado asigna a un grupo
head(sg,1,['Sistema','Clave','Descripción']+['Importe '+p for p in PROTOS]+['Cantidad '+p for p in PROTOS])
sin=collections.OrderedDict()
for (p,s_,cl),(d,u,q,i) in agg.items():
    if clave_cat.get((s_,cl),'sin grupo')=='sin grupo':
        e=sin.setdefault((s_,cl),[d,[0]*7,[0]*7]); e[1][p]+=i; e[2][p]+=q
r=2
for (s_,cl),(d,imps,qs) in sorted(sin.items(),key=lambda kv:-sum(kv[1][1])):
    if sum(imps)<=0: continue
    sg.cell(r,1,s_);sg.cell(r,2,cl);sg.cell(r,3,d)
    for p in range(7): sg.cell(r,4+p,imps[p]).number_format='#,##0'; sg.cell(r,11+p,qs[p])
    r+=1
for col,w in zip('ABC',(18,12,70)): sg.column_dimensions[col].width=w
sg.freeze_panes='D2'
head(asg,1,['Sistema','Clave','Descripción','Grupo asignado','Etapa','Categoría del grupo','Motivo'])
r=2
for (s_,cl),a in ASIGNADAS.items():
    asg.cell(r,1,s_);asg.cell(r,2,cl);asg.cell(r,3,DESC0.get(cl,''));asg.cell(r,4,a['grupo']);asg.cell(r,5,a['etapa']);asg.cell(r,6,cat_de(G[(s_,a['grupo'])]['esc']));asg.cell(r,7,a['motivo']);r+=1
for col,w in zip('ABCDEFG',(18,12,70,44,14,16,70)): asg.column_dimensions[col].width=w
# --- ANCLAS
head(an,1,['Sistema','Grupo (aparato / accesorio)','Juego','Clave','Descripción']+PROTOS)
r=2
descr={(c['clave']):c['desc'] for c in CON}
for (s,g),e in G.items():
    if e['esc']!='Por salidas': continue
    for m in ('Z','O'):
        for cl in sorted(e['anc'][m]):
            an.cell(r,1,s);an.cell(r,2,g);an.cell(r,3,m);an.cell(r,4,cl);an.cell(r,5,descr.get(cl,''))
            for p in range(7):
                an.cell(r,6+p,f'=SUMIFS(IMPORTES!$G:$G,IMPORTES!$A:$A,{L(6+p)}$1,IMPORTES!$D:$D,$D{r})')
            r+=1
nan=r-1
for col,w in zip('ABCDE',(18,40,7,12,70)): an.column_dimensions[col].width=w
an.freeze_panes='A2'
# --- GRUPOS (puntos)
head(gr,1,['Sistema','Grupo (aparato / accesorio)','Ancla Zafiro','Ancla Oro']+PROTOS+['Curado Zafiro','Curado Oro','Validación'])
r=2; fila_g={}
for (s,g),e in G.items():
    if e['esc']!='Por salidas': continue
    gr.cell(r,1,s);gr.cell(r,2,g);gr.cell(r,3,', '.join(sorted(e['anc']['Z'])));gr.cell(r,4,', '.join(sorted(e['anc']['O'])))
    for p in range(7):
        col=L(6+p)
        z=f'SUMIFS(ANCLAS!{col}$2:{col}${nan},ANCLAS!$A$2:$A${nan},$A{r},ANCLAS!$B$2:$B${nan},$B{r},ANCLAS!$C$2:$C${nan},"Z")'
        o=z[:-4]+'"O")'
        gr.cell(r,5+p,f'=MAX({z},{o})')
    bz,bo=e['base'].get('Z'),e['base'].get('O')
    if isinstance(bz,(int,float)): gr.cell(r,12,bz)
    if isinstance(bo,(int,float)): gr.cell(r,13,bo)
    gr.cell(r,14,f'=IF(AND(L{r}="",M{r}=""),"nuevo (no está en los libros curados)",IF(AND(OR(L{r}="",E{r}=L{r}),OR(M{r}="",K{r}=M{r})),"coincide","difiere: el libro curado ajusta a mano"))')
    fila_g[(s,g)]=r; r+=1
ng=r-1
for col,w in zip('ABCD',(18,40,24,34)): gr.column_dimensions[col].width=w
for c in range(5,15): gr.column_dimensions[L(c)].width=11
gr.column_dimensions['N'].width=44; gr.freeze_panes='C2'
# --- ETAPAS (aparato x etapa x clave)
head(et,1,['Sistema','Grupo (aparato / accesorio)','Etapa','Clave','Descripción','Clave compartida con otro grupo']+PROTOS+['Origen'])
r=2
for (s,g),e in G.items():
    if e['esc']!='Por salidas': continue
    for (etp,cl),d in DET[(s,g)].items():
        et.cell(r,1,s);et.cell(r,2,g);et.cell(r,3,etp);et.cell(r,4,cl);et.cell(r,5,d);et.cell(r,6,'sí' if len(claves_grupos[(s,cl)])>1 else 'no')
        for p in range(7):
            et.cell(r,7+p,f'=SUMIFS(IMPORTES!$G:$G,IMPORTES!$A:$A,{L(7+p)}$1,IMPORTES!$D:$D,$D{r})')
        et.cell(r,14,'asignada (antes sin grupo)' if (s,cl) in ASIGNADAS and ASIGNADAS[(s,cl)]['grupo']==g else 'libro curado')
        r+=1
for col,w in zip('ABCDEF',(18,40,14,12,60,12)): et.column_dimensions[col].width=w
et.freeze_panes='A2'; et.auto_filter.ref=f'A1:N{r-1}'
# --- SISTEMAS
sis_ws['A1']='SALIDAS POR SISTEMA Y COSTO POR SALIDA (PUNTOS, NO ÁREA)'; sis_ws['A1'].font=Font(bold=True,size=13)
sis_ws['A2']='Salidas = suma de los puntos de los grupos «por salidas» (hoja GRUPOS). $/salida = importe de las claves de esos grupos ÷ salidas. Las redes por m² y los conceptos fijos quedan fuera: no son puntos.'
sistemas=list(FAM); n=len(sistemas)
def bloque(top,titulo,col_header=True):
    sis_ws.cell(top-1,1,titulo).font=Font(bold=True); head(sis_ws,top,['Sistema','']+PROTOS)
t1=5; bloque(t1,'SALIDAS (puntos)')
t2=t1+n+3; bloque(t2,'IMPORTE de las claves de puntos ($)')
t3=t2+n+3; bloque(t3,'$ POR SALIDA')
t4=t3+n+3; bloque(t4,'Fuera de los puntos: IMPORTE de conceptos fijos ($)')
t5=t4+n+3; bloque(t5,'Fuera de los puntos: IMPORTE de redes por m² ($)')
t6=t5+n+3; bloque(t6,'Sin grupo asignado: IMPORTE de claves que los libros curados no usan ($)')
for k,s in enumerate(sistemas):
    for t in (t1,t2,t3,t4,t5,t6): sis_ws.cell(t+1+k,1,s)
    for p in range(7):
        col=L(3+p); gcol=L(5+p)
        sis_ws.cell(t1+1+k,3+p,f'=SUMIFS(GRUPOS!{gcol}$2:{gcol}${ng},GRUPOS!$A$2:$A${ng},$A{t1+1+k})').number_format='#,##0'
        for t,cat in ((t2,'puntos'),(t4,'fijo'),(t5,'redes por m²'),(t6,'sin grupo')):
            sis_ws.cell(t+1+k,3+p,f'=SUMIFS(IMPORTES!$H$2:$H${nim},IMPORTES!$A$2:$A${nim},{col}${t},IMPORTES!$B$2:$B${nim},$A{t+1+k},IMPORTES!$C$2:$C${nim},"{cat}")').number_format='#,##0'
        sis_ws.cell(t3+1+k,3+p,f'=IF({col}{t1+1+k}=0,"",{col}{t2+1+k}/{col}{t1+1+k})').number_format='#,##0.00'
# estadísticos del $ por salida
sh=t3; extra=['n','Media','Desv. muestral','CV muestral','CV poblacional','Confianza']
for i,t in enumerate(extra): 
    c=sis_ws.cell(sh,10+i,t); c.font=HF; c.fill=HB
for k in range(n):
    rr=t3+1+k
    sis_ws.cell(rr,10,f'=COUNT(C{rr}:I{rr})')
    sis_ws.cell(rr,11,f'=AVERAGE(C{rr}:I{rr})').number_format='#,##0.00'
    sis_ws.cell(rr,12,f'=STDEV(C{rr}:I{rr})').number_format='#,##0.00'
    sis_ws.cell(rr,13,f'=L{rr}/K{rr}').number_format='0.0%'
    sis_ws.cell(rr,14,f'=STDEVP(C{rr}:I{rr})/K{rr}').number_format='0.0%'
    sis_ws.cell(rr,15,f'=IF(J{rr}<5,"insuficiente",IF(M{rr}<=0.1,"utilizable",IF(M{rr}<=0.25,"revisar","no usar")))&" (n="&J{rr}&")"')
sis_ws.column_dimensions['A'].width=22
for c in range(3,16): sis_ws.column_dimensions[L(c)].width=14
sis_ws.column_dimensions['O'].width=22
txt=['TABLA DE APARATOS Y SALIDAS DE LOS 7 PROTOTIPOS (POR PUNTOS)','',
 'Qué es: cuántos aparatos y salidas lleva cada prototipo, contados como puntos (piezas y salidas), nunca como área. Cierra el pendiente de la medición de dispersión: ahora sí se puede medir el costo por salida en los siete.',
 '',
 'Cómo se cuenta: cada grupo de los libros curados (WC, lavamanos, apagador sencillo, estufa, etc.) tiene un concepto ancla, el que trae una unidad por punto. El conteo de un prototipo es la suma de las cantidades de esas claves en su capítulo de Hoja1. Si Zafiro y Oro anclan el grupo en claves distintas (variantes del mismo punto) se toma el mayor de los dos juegos, no la suma.',
 'Validación: en Zafiro la tabla reproduce los salidas base del libro curado en todos los grupos «por salidas». En Oro difiere donde el libro curado ajusta a mano (excepciones autorizadas): la columna N de GRUPOS lo marca.',
 '',
 'Hojas: SISTEMAS (resumen, $/salida y CV) · GRUPOS (conteo por aparato) · ETAPAS (conteo por aparato y etapa: sanitaria, hidráulica, mueble, cimentación, muros, cableado, accesorio) · ANCLAS (claves que se cuentan) · SIN_GRUPO (claves por asignar; hoy vacía) · ASIGNADAS (las 19 claves asignadas y por qué) · IMPORTES (cada clave de los 4 sistemas por prototipo).',
 '',
 'Límites:',
 '1. Las redes principales por m² de losa y los conceptos fijos NO son puntos: se muestran aparte (SISTEMAS, bloques «fuera de los puntos») y no entran en el $/salida.',
 '2. Hay claves que los libros curados no usan y que otros prototipos sí traen (bloque «sin grupo»). Su importe no entra en el $/salida; revisarlas puede asignarlas a un grupo nuevo.',
 '3. Una clave de cimentación o de muros compartida por varios grupos (columna F de ETAPAS) se cuenta completa en cada uno; por eso ETAPAS no se suma entre grupos, solo GRUPOS.',
 '4. Hay 3 grupos de Oro cuyo libro curado trae el conteo escrito a mano (USB, intemperie, spot de escalera); su ancla es la clave de accesorio. La ancla de TV se corrigió a la salida de TV de cimentación (IEC-01080): la del libro curado es una tapa ciega agregada.',
 '4b. Las 19 claves que ningún libro curado usaba se asignaron a su grupo (hoja ASIGNADAS, con el motivo de cada una); SIN_GRUPO queda para lo que aparezca después.',
 '5. Herrería, carpintería y cancelería no entran: son piezas fijas, no salidas de instalación.',
 '','Reproducir: python3 -I tabla_aparatos_salidas.py (usa curado_aparatos.json y el libro de Zafiro v45).']
for i,t in enumerate(txt,1):
    c=lee.cell(i,1,t); c.alignment=Alignment(wrap_text=True,vertical='top')
    if i==1: c.font=Font(bold=True,size=13)
lee.column_dimensions['A'].width=140
wb.calculation.fullCalcOnLoad=True
wb.save(SALIDA); print('IMPORTES',nim-1,'ANCLAS',nan-1,'GRUPOS',ng-1)
