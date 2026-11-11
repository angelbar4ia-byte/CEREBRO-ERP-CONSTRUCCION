"""Asigna TODOS los conceptos de los 7 prototipos a un driver paramétrico y mide su dispersión.

Lee Hoja1 del libro de Zafiro v45 (trae los siete capítulos), mapa_aprendido.json (lo que los libros
curados de Zafiro y Oro hacen con cada clave) y curado_drivers.json (importes de esos libros, para validar).
Escribe PARAMETRICOS_7_PROTOTIPOS.xlsx.  Uso: python3 -I asignar_drivers.py [libro.xlsx] [salida.xlsx]
"""
import sys,re,json,collections,openpyxl
from openpyxl.styles import Font,PatternFill,Alignment
from openpyxl.utils import get_column_letter as L
LIBRO=sys.argv[1] if len(sys.argv)>1 else 'CATALOGO_PARAMETRICO_con_MURO_ZAFIRO_CAPAS_v45.xlsx'
SALIDA=sys.argv[2] if len(sys.argv)>2 else 'PARAMETRICOS_7_PROTOTIPOS.xlsx'
PROTOS=['Zafiro 1.0','Rubí','Zafiro Plus','Jade','Diamante −','Diamante +','Oro 4.01']
mapa=json.load(open('mapa_aprendido.json',encoding='utf-8')); curado=json.load(open('curado_drivers.json',encoding='utf-8'))
H=list(openpyxl.load_workbook(LIBRO,read_only=True)['Hoja1'].iter_rows(values_only=True))
caps=[i for i,r in enumerate(H) if r[0]=='Capítulo']
sub=None;subp=None;rows=[]
for i,r in enumerate(H,1):
    p=sum(1 for j in caps if j<=i-1)-1
    if r[0]=='Subcapítulo': sub=(r[7] or '').strip(); subp=p
    if r[0]=='Concepto':
        rows.append(dict(row=i,p=p,sub=(sub if subp==p else '') or '',clave=r[5] or '',desc=r[7] or '',u=r[10],q=r[11] or 0,pu=r[12] or 0,imp=r[13] or 0,ubi=r[25]))
def m2(d):
    m=re.search(r'\(\s*([\d.]+)\s*m\s*2\s*\)',d,re.I); return float(m.group(1)) if m else None
AZ=('AZOTEA','AZOTEA/ROOF'); GRUESAS=('ACA-01050','ACA-01051','ACA-01052')
asig={}    # row -> lista de (driver,capa,cantidad,origen,nota)
div={}     # row -> divisor
def poner(r,driver,capa,origen,nota='',q=None,d=None):
    asig.setdefault(r['row'],[]).append([driver,capa,r['q'] if q is None else q,origen,nota])
    if d is not None: div[(r['row'],driver)]=d
for p in range(7):
    cs=[r for r in rows if r['p']==p]; hecho=set()
    # --- boquillas: la fina define el tipo y la gruesa es la de la misma zona y cantidad
    def pares(fina):
        out=[]
        for f in [c for c in cs if c['clave']==fina]:
            g=[c for c in cs if c['clave'] in GRUESAS and c['row'] not in hecho and c['sub']==f['sub'] and abs(c['q']-f['q'])<0.01]
            if g: hecho.add(g[0]['row'])
            hecho.add(f['row']); out.append((g[0] if g else None,f))
        return out
    for g,f in pares('ACA-01060'):
        if g: poner(g,'VANO','OBRA GRIS','boquilla fina define el tipo',d=g['q'])
        poner(f,'VANO','OBRA BLANCA','boquilla fina define el tipo')
    for g in [c for c in cs if c['clave']=='ACA-01050' and c['row'] not in hecho]:
        hecho.add(g['row']); poner(g,'VANO','OBRA GRIS','boquilla gruesa interior sin fina',d=g['q'])
    for g,f in pares('ACA-01071'):
        if g: poner(g,'MARCOS EXTERIORES','OBRA GRIS','boquilla fina define el tipo')
        poner(f,'MARCOS EXTERIORES','OBRA BLANCA','boquilla fina define el tipo')
    for g,f in pares('ACA-01072'):
        if g: poner(g,'PRETIL','OBRA GRIS','boquilla fina define el tipo')
        poner(f,'PRETIL','OBRA BLANCA','boquilla fina define el tipo')
    # --- franja de fachada +3.00: al pretil lo que mida su muro, el resto al muro
    muro_pretil=sum(c['q'] for c in cs if c['clave'] in('EST-02010','EST-02011') and c['sub'] in AZ)
    for c in cs:
        if c['clave'] in('ALB-01212','ACA-20020'):
            capa='OBRA GRIS' if c['clave']=='ALB-01212' else 'OBRA BLANCA'
            a=min(c['q'],muro_pretil); b=c['q']-a; hecho.add(c['row'])
            if a>0: poner(c,'PRETIL',capa,'franja +3.00 (regla de Zafiro)','al pretil le toca lo que mida su muro',q=a)
            if b>0.0001: poner(c,'MURO',capa,'franja +3.00 (regla de Zafiro)','el resto de la franja es de la fachada',q=b)
            if a<=0 and b<=0.0001: poner(c,'MURO',capa,'franja +3.00','')
    # --- pintura del pretil: línea de fachada INTERIOR más parecida al repellado del pretil
    rep=sum(c['q'] for c in cs if c['clave']=='ALB-01010' and c['sub'] in AZ)
    if p==0:
        for c in cs:
            if c['clave'] in('ACA-30031','ACA-30032') and c['ubi']=='INTERIOR': hecho.add(c['row']); poner(c,'PRETIL','PINTURA','pintura de pretil (filas 399-400 de Zafiro)')
    else:
        cand=[c for c in cs if c['clave']=='ACA-03047' and c['ubi']=='INTERIOR']
        if cand:
            c=min(cand,key=lambda c:abs(c['q']-rep)); hecho.add(c['row']); poner(c,'PRETIL','PINTURA','pintura de pretil: la línea más parecida al repellado')
    # --- sellado de marco: con marco interior, la línea que no es la de los marcos exteriores es del vano (se cobra el largo del marco)
    mi=sum(c['q'] for c in cs if c['clave']=='ACA-07012'); me=sum(c['q'] for c in cs if c['clave']=='ACA-07011')
    if mi:
        for c in cs:
            if c['clave']=='ACA-08030' and abs(c['q']-me)>0.01 and c['row'] not in hecho:
                hecho.add(c['row']); poner(c,'VANO','REVESTIMIENTO','sellado de marco interior','excepción autorizada: se cobra el largo del marco interior (%g m)'%mi,q=mi)
    # --- mármol: lo que va en piso se toma de la hoja MÁRMOL (editable); el resto queda en el muro
    for c in cs:
        if c['clave'] in('ACA-02040','ACA-08010','ACA-02050','ACA-10040') and c['row'] not in hecho:
            col='E' if c['clave'] in('ACA-02040','ACA-08010') else 'G'; ref=f"MÁRMOL!${col}${2+p}"
            tot=sum(x['q'] for x in cs if x['clave']==c['clave']) or 1   # si hay varias líneas, el piso se reparte en proporción
            hecho.add(c['row'])
            poner(c,'PISO','REVESTIMIENTO','mármol en piso (hoja MÁRMOL)','m² de mármol que va en piso: dato de la hoja MÁRMOL',q=f'={ref}*G#/{tot}')
            poner(c,'MURO','REVESTIMIENTO','mármol en muro (hoja MÁRMOL)','lo que no va en piso',q=f'=G#-{ref}*G#/{tot}')
    # --- el resto
    for c in cs:
        if c['row'] in hecho: continue
        sn='AZOTEA' if c['sub'] in AZ else c['sub']; cl=c['clave']; d=c['desc'].lower()
        k=f"{'EST-02010' if cl=='EST-02011' else cl}§{sn}"
        if k in mapa:
            a=mapa[k]; poner(c,a['driver'],a['capa'],'aprendido de los libros curados'+(' (ambigua)' if a['ambigua'] else '')); continue
        dr=capa=None
        if cl.startswith(('ISN','IHD','MSA','ACC-0101','ACC-0000')): dr,capa='HIDROSANITARIAS','INSTALACIÓN'
        elif cl.startswith('IGAS'): dr,capa='GAS','INSTALACIÓN'
        elif cl.startswith('IEC'): dr,capa='ELÉCTRICAS','INSTALACIÓN'
        elif cl.startswith('EQU'): dr,capa='EQUIPOS','EQUIPO'
        elif c['u']=='act' and d.startswith('losa') and c['sub']=='CIMENTACIÓN': dr,capa='PISO','OBRA NEGRA'
        elif c['u']=='act' and d.startswith('losa'): dr,capa='LOSA','OBRA NEGRA'
        elif cl.startswith('CAN'): dr,capa='CANCELERÍA','FIJO'
        elif c['sub']=='PERGOLADO COCHERA': dr,capa='COCHERA','PÉRGOLA'
        elif c['sub']=='ASADOR': dr,capa='ASADOR','FIJO'
        elif c['sub']=='BARDA PERIMETRAL': dr,capa='BARDA','OBRA NEGRA'
        elif 'escalera' in d or 'escalon' in d.replace('ó','o'): dr,capa='ESCALERA','FIJO'
        elif c['sub']=='HERRERÍA' or cl.startswith('HER'): dr,capa='HERRERÍA','FIJO'
        elif c['sub']=='CARPINTERÍA' or cl.startswith('CAR'): dr,capa='CARPINTERÍA','FIJO'
        elif c['sub']=='OBRAS EXTERIORES': dr,capa='OBRA EXTERIOR','FIJO'
        elif cl=='ACA-05010': dr,capa='MURO','REVESTIMIENTO'
        elif cl=='ACA-08041': dr,capa='MURO','REVESTIMIENTO'
        elif cl=='ACA-20012': dr,capa='MURO','OBRA BLANCA'
        elif cl.startswith('ALB-030'): dr,capa='LOSA','OBRA GRIS'
        elif cl.startswith(('ACA-11','ACA-10','ACA-07040','ACA-02512','ACA-02052','ICA-')) or not cl: dr,capa='OBRA COMPLEMENTARIA','FIJO'
        elif cl.startswith('EST') and c['sub'] in('PLANTA BAJA','PLANTA ALTA','CIMENTACIÓN'): dr,capa='MURO','OBRA NEGRA'
        elif c['sub'] in AZ: dr,capa='LOSA','OBRA GRIS'
        if dr: poner(c,dr,capa,'regla por clave o subcapítulo'); continue
        poner(c,'SIN ASIGNAR','','sin regla','revisar')
# --- divisores
for r in rows:
    if r['row'] not in asig: continue
    cl=r['clave']
    for a in asig[r['row']]:
        drv=a[0]; v=None
        if drv=='MURO' and cl in('EST-02010','EST-02011') and r['sub'] in('PLANTA BAJA','PLANTA ALTA'): v=r['q']
        elif drv=='PRETIL' and cl in('EST-02010','EST-02011'): v=r['q']
        elif drv=='MARCOS EXTERIORES' and cl=='ACA-07011': v=r['q']
        elif drv=='LOSA' and r['u']=='act' and r['desc'].lower().startswith('losa'): v=m2(r['desc'])
        elif drv=='PISO' and r['u']=='act' and r['desc'].lower().startswith('losa'): v=m2(r['desc'])
        elif drv=='ASADOR' and cl=='ACA-02510': v=r['q']
        elif drv=='COCHERA' and r['desc'].lower().startswith('pergolado para cochera'): v=m2(r['desc'])
        elif drv=='SILLAR' and cl=='EST-02080' and r['sub']!='BARDA PERIMETRAL': v=r['q']
        elif drv=='BARDA' and cl=='BAP-03010': v=r['q']
        elif drv=='JARDÍN' and cl=='OBE-03210': v=r['q']
        elif drv=='CUBIERTA' and cl in('ACA-02032','ACA-02033'): v=r['q']
        elif drv=='PÓRFIDO' and cl=='OBE-02011': v=r['q']
        if v: div[(r['row'],drv)]=v
wb=openpyxl.Workbook(); lee=wb.active; lee.title='LEEME'; mar=wb.create_sheet('MÁRMOL')
res=wb.create_sheet('RESUMEN'); val=wb.create_sheet('VALIDACIÓN'); aw=wb.create_sheet('ASIGNACIÓN')
HF=Font(bold=True,color='FFFFFF'); HB=PatternFill('solid',fgColor='305496')
def head(ws,r,vals):
    for i,v in enumerate(vals,1):
        c=ws.cell(r,i,v); c.font=HF; c.fill=HB; c.alignment=Alignment(wrap_text=True,vertical='center')

# --- hoja MÁRMOL: cuánto mármol va en piso (editable)
head(mar,1,['Prototipo','Travertino en el catálogo (m²)','Tomboleado en el catálogo (m²)','Renivelación de charolas (m²)','Tomboleado en PISO (m²)','% del travertino en piso (editable)','Travertino en PISO (m²)','De dónde sale'])
trav=collections.defaultdict(float); tomb=collections.defaultdict(float); ren=collections.defaultdict(float)
for r in rows:
    if r['clave']=='ACA-02050': trav[r['p']]+=r['q']
    if r['clave']=='ACA-02040': tomb[r['p']]+=r['q']
    if r['clave']=='ACA-01090': ren[r['p']]+=r['q']
for p in range(7):
    rr=2+p; mar.cell(rr,1,PROTOS[p]); mar.cell(rr,2,round(trav[p],2)); mar.cell(rr,3,round(tomb[p],2)); mar.cell(rr,4,round(ren[p],2))
    if p==0:
        mar.cell(rr,5,'=D2'); mar.cell(rr,7,17.52); mar.cell(rr,6,'=G2/B2'); mar.cell(rr,8,'Dato del usuario: piso = renivelación de charolas (4.81) y travertino de piso 17.52 m²')
    elif p==6:
        mar.cell(rr,5,8.04); mar.cell(rr,7,32.88); mar.cell(rr,6,'=G8/B8'); mar.cell(rr,8,'Dato del usuario en el libro de Oro: tomboleado 1.8 + 6.24, travertino 13.24 + 19.64 (la renivelación de Hoja1 trae 0.1 + 4.5)')
    else:
        mar.cell(rr,5,f'=D{rr}'); mar.cell(rr,6,'=AVERAGE($F$2,$F$8)'); mar.cell(rr,7,f'=B{rr}*F{rr}')
        mar.cell(rr,8,'ESTIMADO: tomboleado = renivelación de charolas (criterio de Zafiro); travertino = promedio de la fracción de Zafiro y de Oro. Confirmar con los m² de piso.')
    for c in (2,3,4,5,7): mar.cell(rr,c).number_format='#,##0.00'
    mar.cell(rr,6).number_format='0.0%'
mar.cell(10,1,'Sobrescribir la columna F (o G) con el dato real; ASIGNACIÓN y RESUMEN se recalculan. Mover mármol de muro a piso no cambia el total del prototipo, solo cuánto cuesta el muro y cuánto el piso.')
for col,w in zip('ABCDEFGH',(14,16,16,16,16,18,16,110)): mar.column_dimensions[col].width=w
head(aw,1,['Prototipo','Fila Hoja1','Subcapítulo','Clave','Descripción','Unidad','Cantidad en el catálogo','Precio unitario','Driver (editable)','Capa (editable)','Cantidad que se cobra','Importe','Divisor del driver','Cómo se asignó','Nota'])
fila=2; pos={r['row']:r for r in rows}
for r in sorted(rows,key=lambda x:x['row']):
    for a in asig[r['row']]:
        drv,capa,q,orig,nota=a
        q=q.replace('#',str(fila)) if isinstance(q,str) else q
        vals=[PROTOS[r['p']],r['row'],r['sub'],r['clave'],r['desc'][:90],r['u'],r['q'],r['pu'],drv,capa,q]
        for j,v in enumerate(vals,1): aw.cell(fila,j,v)
        aw.cell(fila,12,f'=K{fila}*H{fila}').number_format='#,##0.00'
        if (r['row'],drv) in div: aw.cell(fila,13,div[(r['row'],drv)])
        aw.cell(fila,14,orig); aw.cell(fila,15,nota); fila+=1
na=fila-1
for col,w in zip('ABCDEFGHIJKLMNO',(13,9,20,11,60,7,11,10,22,16,11,12,11,42,40)): aw.column_dimensions[col].width=w
aw.freeze_panes='A2'; aw.auto_filter.ref=f'A1:O{na}'
DR=[('MURO','m² de tabique','DRIVER'),('PRETIL','m² de pretil','DRIVER'),('VANO','m de boquilla interior','DRIVER'),('MARCOS EXTERIORES','m de marco exterior','DRIVER'),
    ('LOSA','m² de losa de nivel','DRIVER'),('PISO','m² de desplante','DRIVER'),('ESCALERA','piezas (sin divisor común)','FIJO'),
    ('ASADOR','m² de piso','DRIVER'),('PÓRFIDO','m²','DRIVER'),('COCHERA','m² de pérgola','DRIVER'),('SILLAR','m²','DRIVER'),('BARDA','ml','DRIVER'),
    ('JARDÍN','m² de sello','DRIVER'),('CUBIERTA','ml','DRIVER'),('CISTERNA','L','CTE'),
    ('HIDROSANITARIAS','por salidas (TABLA_APARATOS_SALIDAS)','SALIDAS'),('GAS','por salidas','SALIDAS'),('ELÉCTRICAS','por salidas','SALIDAS'),('EQUIPOS','por salidas','SALIDAS'),
    ('CARPINTERÍA','fijo','FIJO'),('CANCELERÍA','fijo','FIJO'),('HERRERÍA','fijo','FIJO'),('OBRA EXTERIOR','fijo','FIJO'),('OBRA COMPLEMENTARIA','fijo','FIJO'),('SIN ASIGNAR','—','FIJO')]
nd=len(DR)
res['A1']='LOS 7 PROTOTIPOS ASIGNADOS A SUS DRIVERS'; res['A1'].font=Font(bold=True,size=13)
res['A2']='Importe, divisor y tasa por driver, sumados de la hoja ASIGNACIÓN con SUMIFS (se puede reasignar un concepto cambiando su driver). CV = desviación ÷ media. Confianza: ≤10 % utilizable · ≤25 % revisar · >25 % no usar.'
b1=5; b2=b1+nd+4; b3=b2+nd+4
for t,top in (('IMPORTE ($)',b1),('DIVISOR',b2),('TASA ($ por unidad del divisor)',b3)):
    res.cell(top-1,1,t).font=Font(bold=True)
head(res,b1,['Driver','Divisor']+PROTOS+['Total 7']); head(res,b2,['Driver','Divisor']+PROTOS)
head(res,b3,['Driver','Divisor']+PROTOS+['n','Media','Desv. muestral','CV muestral','CV poblacional','Confianza'])
for k,(d,u,tipo) in enumerate(DR):
    ri=b1+1+k; rd=b2+1+k; rt=b3+1+k
    for rr in (ri,rd,rt): res.cell(rr,1,d); res.cell(rr,2,u)
    for p in range(7):
        cl=L(3+p)
        res.cell(ri,3+p,f'=SUMIFS(ASIGNACIÓN!$L$2:$L${na},ASIGNACIÓN!$A$2:$A${na},{cl}${b1},ASIGNACIÓN!$I$2:$I${na},$A{ri})').number_format='#,##0'
        if tipo=='CTE': res.cell(rd,3+p,3000)
        elif tipo=='DRIVER': res.cell(rd,3+p,f'=SUMIFS(ASIGNACIÓN!$M$2:$M${na},ASIGNACIÓN!$A$2:$A${na},{cl}${b2},ASIGNACIÓN!$I$2:$I${na},$A{rd})').number_format='#,##0.00'
        if tipo in('DRIVER','CTE'): res.cell(rt,3+p,f'=IF(OR({cl}{rd}=0,{cl}{ri}=0),"",{cl}{ri}/{cl}{rd})').number_format='#,##0.00'
    res.cell(ri,10,f'=SUM(C{ri}:I{ri})').number_format='#,##0'
    if tipo in('DRIVER','CTE'):
        res.cell(rt,10,f'=COUNT(C{rt}:I{rt})'); res.cell(rt,11,f'=IF(J{rt}=0,"",AVERAGE(C{rt}:I{rt}))').number_format='#,##0.00'
        res.cell(rt,12,f'=IF(J{rt}<2,"",STDEV(C{rt}:I{rt}))').number_format='#,##0.00'
        res.cell(rt,13,f'=IF(L{rt}="","",L{rt}/K{rt})').number_format='0.0%'
        res.cell(rt,14,f'=IF(J{rt}<2,"",STDEVP(C{rt}:I{rt})/K{rt})').number_format='0.0%'
        res.cell(rt,15,f'=IF(M{rt}="","",IF(J{rt}<5,"insuficiente",IF(M{rt}<=0.1,"utilizable",IF(M{rt}<=0.25,"revisar","no usar")))&" (n="&J{rt}&")")')
rtot=b1+nd+1
res.cell(rtot,1,'TOTAL asignado').font=Font(bold=True)
res.cell(rtot+1,1,'Presupuesto del prototipo en Hoja1').font=Font(bold=True)
res.cell(rtot+2,1,'Diferencia (debe ser 0)').font=Font(bold=True)
tot_h=collections.defaultdict(float)
for r in rows: tot_h[r['p']]+=r['imp']
for p in range(7):
    cl=L(3+p)
    res.cell(rtot,3+p,f'=SUM({cl}{b1+1}:{cl}{b1+nd})').number_format='#,##0'
    res.cell(rtot+1,3+p,round(tot_h[p],2)).number_format='#,##0'
    res.cell(rtot+2,3+p,f'=ROUND({cl}{rtot}-{cl}{rtot+1},2)').number_format='#,##0.00'
# VANO sin la capa de revestimiento (solo Zafiro la trae): la tasa comparable
rv=b3+nd+2
res.cell(rv,1,'VANO sin revestimiento (comparable)').font=Font(bold=True); res.cell(rv,2,'m de boquilla interior')
rvano=b1+1+[d for d,_,_ in DR].index('VANO'); rdv=b2+1+[d for d,_,_ in DR].index('VANO')
for p in range(7):
    cl=L(3+p)
    res.cell(rv,3+p,f'=IF({cl}{rdv}=0,"",({cl}{rvano}-SUMIFS(ASIGNACIÓN!$L$2:$L${na},ASIGNACIÓN!$A$2:$A${na},{cl}${b1},ASIGNACIÓN!$I$2:$I${na},"VANO",ASIGNACIÓN!$J$2:$J${na},"REVESTIMIENTO"))/{cl}{rdv})').number_format='#,##0.00'
res.cell(rv,10,f'=COUNT(C{rv}:I{rv})'); res.cell(rv,11,f'=AVERAGE(C{rv}:I{rv})').number_format='#,##0.00'
res.cell(rv,12,f'=STDEV(C{rv}:I{rv})').number_format='#,##0.00'; res.cell(rv,13,f'=L{rv}/K{rv}').number_format='0.0%'
res.cell(rv,14,f'=STDEVP(C{rv}:I{rv})/K{rv}').number_format='0.0%'
res.cell(rv,15,f'=IF(J{rv}<5,"insuficiente",IF(M{rv}<=0.1,"utilizable",IF(M{rv}<=0.25,"revisar","no usar")))&" (n="&J{rv}&")"')
res.column_dimensions['A'].width=26; res.column_dimensions['B'].width=36
for c in range(3,16): res.column_dimensions[L(c)].width=13
res.column_dimensions['O'].width=22; res.freeze_panes='C5'
# VALIDACIÓN: la regla automática contra los libros curados
head(val,1,['Driver','Zafiro: regla','Zafiro: libro curado','Diferencia','%','Oro: regla','Oro: libro curado','Diferencia','%'])
for k,(d,u,tipo) in enumerate(DR[:-1]):
    r=2+k; ri=b1+1+k
    val.cell(r,1,d); val.cell(r,2,f'=RESUMEN!C{ri}'); val.cell(r,6,f'=RESUMEN!I{ri}')
    cz=curado['Z'].get(d); co=curado['O'].get(d)
    if cz is not None: val.cell(r,3,cz)
    if co is not None: val.cell(r,7,co)
    val.cell(r,4,f'=IF(C{r}="","",B{r}-C{r})'); val.cell(r,5,f'=IF(OR(C{r}="",C{r}=0),"",D{r}/C{r})').number_format='0.0%'
    val.cell(r,8,f'=IF(G{r}="","",F{r}-G{r})'); val.cell(r,9,f'=IF(OR(G{r}="",G{r}=0),"",H{r}/G{r})').number_format='0.0%'
    for c in (2,3,4,6,7,8): val.cell(r,c).number_format='#,##0'
r=2+nd; val.cell(r,1,'TOTAL').font=Font(bold=True)
for c in (2,3,4,6,7,8): val.cell(r,c,f'=SUM({L(c)}2:{L(c)}{r-1})').number_format='#,##0'
val.cell(r+2,1,'La regla suma el pretil, el vano y los marcos con las reglas de PRETIL_7, VANO_MARCOS_7 y TABLA_APARATOS_SALIDAS. Las diferencias de MURO, PISO y LOSA vienen de los repartos manuales de los libros curados (mármol entre muro y piso, losa de cimentación convertida a m², sellado interior de 21 m); ver LEEME.')
val.column_dimensions['A'].width=26
for c in 'BCDEFGHI': val.column_dimensions[c].width=15
cnt=collections.Counter(a[3].split(' (')[0] for v in asig.values() for a in v)
sinasig=[(PROTOS[r['p']],r['sub'],r['clave'],round(r['imp'])) for r in rows if any(a[0]=='SIN ASIGNAR' for a in asig[r['row']])]
txt=['TODOS LOS CONCEPTOS DE LOS 7 PROTOTIPOS EN SU DRIVER','',
 'Qué es: Zafiro y Oro tienen su presupuesto repartido en drivers paramétricos (con cuadre contra Hoja1). Los otros cinco prototipos no. Aquí cada concepto de los siete (2,452) se asigna a un driver, de modo que el total de cada prototipo cuadra y se pueden medir las tasas con una misma regla.',
 '',
 'Cómo se asigna, en este orden:',
 '1. Boquillas: la fina define el tipo (VANO, MARCOS EXTERIORES o PRETIL) y la gruesa es la de la misma zona y cantidad.',
 '2. Franja de fachada +3.00 (repellado y finas): al pretil lo que mida su muro, el resto a MURO (regla de Zafiro).',
 '3. Pintura del pretil: la línea de fachada INTERIOR más parecida al repellado del pretil.',
 '3b. Mármol (tomboleado y travertino, con su sellado y limpieza): lo que va en piso sale de la hoja MÁRMOL; el resto se queda en el muro. Para Zafiro y Oro son los datos de sus libros; para los otros cinco el tomboleado es la renivelación de charolas y el travertino un ESTIMADO (42.6 %) por confirmar.',
 '4. Lo aprendido de los libros curados: la misma clave en el mismo subcapítulo va al mismo driver y capa (mapa_aprendido.json).',
 '5. Reglas por clave y subcapítulo para lo propio de cada prototipo (losas, cocinas, cancelerías, pérgolas, herrería).',
 '6. Lo que no cae en nada queda en SIN ASIGNAR (hoy: %d concepto(s)).'%len(sinasig),
 '',
 'Para corregir: cambiar el driver o la capa de un concepto en la hoja ASIGNACIÓN; RESUMEN se recalcula.',
 '',
 'Qué NO hace:',
 '- No reproduce todos los repartos manuales de los libros curados: la losa de cimentación convertida de pieza global a m², el sellado interior de 21 m. VALIDACIÓN muestra la diferencia por driver.',
 '- Instalaciones, equipos y fijos (carpintería, cancelería, herrería, obra exterior) solo traen importe; su tasa por salida está en TABLA_APARATOS_SALIDAS.xlsx.',
 '- Cisterna y barda repiten el mismo concepto en los 7: su CV bajo es precio.',
 '','Reproducir: python3 -I asignar_drivers.py (usa mapa_aprendido.json y curado_drivers.json).']
for i,t in enumerate(txt,1):
    c=lee.cell(i,1,t); c.alignment=Alignment(wrap_text=True,vertical='top')
    if i==1: c.font=Font(bold=True,size=13)
lee.column_dimensions['A'].width=140
wb.calculation.fullCalcOnLoad=True
wb.save(SALIDA); print('filas asignación',na-1,'| cómo:',dict(cnt),'| sin asignar:',len(sinasig),sinasig[:10])
