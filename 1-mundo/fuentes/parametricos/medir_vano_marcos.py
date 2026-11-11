"""Parametriza VANO (perímetro interior) y MARCOS EXTERIORES en los 7 prototipos con la regla de Zafiro.

Lee Hoja1 del libro de Zafiro v45 (trae los siete capítulos) y escribe VANO_MARCOS_7_PROTOTIPOS.xlsx.
Uso: python3 -I medir_vano_marcos.py [libro.xlsx] [salida.xlsx]
"""
import sys,openpyxl,collections
from openpyxl.styles import Font,PatternFill,Alignment
from openpyxl.utils import get_column_letter as L
LIBRO=sys.argv[1] if len(sys.argv)>1 else 'CATALOGO_PARAMETRICO_con_MURO_ZAFIRO_CAPAS_v45.xlsx'
SALIDA=sys.argv[2] if len(sys.argv)>2 else 'VANO_MARCOS_7_PROTOTIPOS.xlsx'
PROTOS=['Zafiro 1.0','Rubí','Zafiro Plus','Jade','Diamante −','Diamante +','Oro 4.01']
H=list(openpyxl.load_workbook(LIBRO,read_only=True)['Hoja1'].iter_rows(values_only=True))
caps=[i for i,r in enumerate(H) if r[0]=='Capítulo']
sub=None;subp=None;C=[]
for i,r in enumerate(H):
    p=sum(1 for j in caps if j<=i)-1
    if r[0]=='Subcapítulo': sub=(r[7] or '').strip(); subp=p
    if r[0]=='Concepto': C.append(dict(p=p,sub=(sub if subp==p else None) or '',clave=r[5] or '',desc=r[7] or '',u=r[10],q=r[11] or 0,pu=r[12] or 0,imp=r[13] or 0))
GRUESAS=('ACA-01050','ACA-01051','ACA-01052')
filas=[]   # (p,driver,capa,concepto,clave,zona,u,q_cat,q_usada,pu,es_driver,nota)
def par(cs,usadas,fina_clave):
    """pares boquilla gruesa + fina: la fina define el tipo; la gruesa es la de misma zona y misma cantidad"""
    out=[]
    for f in [c for c in cs if c['clave']==fina_clave]:
        g=[c for c in cs if c['clave'] in GRUESAS and id(c) not in usadas and c['sub']==f['sub'] and abs(c['q']-f['q'])<0.01]
        if g: usadas.add(id(g[0]))
        out.append((g[0] if g else None,f))
    return out
for p in range(7):
    cs=[c for c in C if c['p']==p]; usadas=set()
    # VANO: boquilla interior (fina ACA-01060 + su gruesa)
    pares=par(cs,usadas,'ACA-01060')
    # la gruesa de Zafiro tiene 16 m más que su fina: va suelta
    sueltas=[c for c in cs if c['clave']=='ACA-01050' and id(c) not in usadas]
    for g,f in pares:
        if g: filas.append((p,'VANO','OBRA GRIS','Boquilla interior',g['clave'],g['sub'],'m',g['q'],g['q'],g['pu'],'sí',''))
        filas.append((p,'VANO','OBRA BLANCA','Boquilla fina interior',f['clave'],f['sub'],'m',f['q'],f['q'],f['pu'],'no','' if g else 'sin gruesa de la misma cantidad'))
    for g in sueltas:
        usadas.add(id(g)); filas.append((p,'VANO','OBRA GRIS','Boquilla interior',g['clave'],g['sub'],'m',g['q'],g['q'],g['pu'],'sí','la fina interior tiene menos metros que la gruesa'))
    mi=[c for c in cs if c['clave']=='ACA-07012']
    ext_marcos=sum(c['q'] for c in cs if c['clave']=='ACA-07011')
    sell=sorted([c for c in cs if c['clave']=='ACA-08030'],key=lambda c:c['q'])
    for c in mi:
        filas.append((p,'VANO','REVESTIMIENTO','Marco de cantera interior',c['clave'],c['sub'],'m',c['q'],c['q'],c['pu'],'no',''))
        # sellado interior = la línea del catálogo que no es la de los marcos exteriores; se cobra por los metros del marco (decisión de Zafiro: 21 m, no 14.4)
        otras=[s for s in sell if abs(s['q']-ext_marcos)>0.01]
        if otras: filas.append((p,'VANO','REVESTIMIENTO','Sellado de marco interior',otras[0]['clave'],otras[0]['sub'],'m',otras[0]['q'],c['q'],otras[0]['pu'],'no','excepción autorizada: se cobra el largo del marco (21 m) y no los 14.4 m del catálogo'))
    # MARCOS EXTERIORES: fina ACA-01071 + su gruesa
    for g,f in par(cs,usadas,'ACA-01071'):
        if g: filas.append((p,'MARCOS EXTERIORES','OBRA GRIS','Boquilla en fachada',g['clave'],g['sub'],'m',g['q'],g['q'],g['pu'],'no',''))
        filas.append((p,'MARCOS EXTERIORES','OBRA BLANCA','Boquilla fina en fachada',f['clave'],f['sub'],'m',f['q'],f['q'],f['pu'],'no','' if g else 'sin gruesa de la misma cantidad'))
    for c in cs:
        if c['clave']=='ACA-07011': filas.append((p,'MARCOS EXTERIORES','REVESTIMIENTO','Marco de cantera exterior',c['clave'],c['sub'],'m',c['q'],c['q'],c['pu'],'sí',''))
    if ext_marcos:
        ext=[s for s in sell if s['q']>=ext_marcos-0.01 or abs(s['q']-ext_marcos)<0.01]
        if mi: ext=[s for s in sell if abs(s['q']-ext_marcos)<0.01]
        for s in ext[:1]:
            q=min(s['q'],ext_marcos); nota='' if abs(s['q']-q)<0.01 else f"el catálogo trae {s['q']:g} m de sellado y {ext_marcos:g} m de marco: sobran {s['q']-q:.1f} m sin marco, no se cobran"
            filas.append((p,'MARCOS EXTERIORES','REVESTIMIENTO','Sellado de marco exterior',s['clave'],s['sub'],'m',s['q'],q,s['pu'],'no',nota))
wb=openpyxl.Workbook(); lee=wb.active; lee.title='LEEME'
res=wb.create_sheet('RESUMEN'); par_ws=wb.create_sheet('PARTIDAS')
HF=Font(bold=True,color='FFFFFF'); HB=PatternFill('solid',fgColor='305496')
def head(ws,r,vals):
    for i,v in enumerate(vals,1):
        c=ws.cell(r,i,v); c.font=HF; c.fill=HB; c.alignment=Alignment(wrap_text=True,vertical='center')
head(par_ws,1,['Prototipo','Driver','Capa','Concepto','Clave','Zona (subcapítulo)','Unidad','Cantidad en el catálogo','Cantidad que se cobra','Precio unitario','Importe','Es el driver','Ratio (cant. por m del driver)','Nota'])
n=len(filas)+1
for i,(p,d,capa,conc,cl,zona,u,qc,qu,pu,esd,nota) in enumerate(filas,2):
    for j,v in enumerate((PROTOS[p],d,capa,conc,cl,zona,u,qc,qu,pu),1): par_ws.cell(i,j,v)
    par_ws.cell(i,11,f'=I{i}*J{i}').number_format='#,##0.00'; par_ws.cell(i,12,esd)
    drv=f'SUMIFS($I$2:$I${n},$A$2:$A${n},$A{i},$B$2:$B${n},$B{i},$L$2:$L${n},"sí")'
    par_ws.cell(i,13,f'=IF({drv}=0,"",I{i}/{drv})').number_format='0.00'; par_ws.cell(i,14,nota)
for col,w in zip('ABCDEFGHIJKLMN',(13,19,15,28,11,18,7,12,12,11,12,9,12,70)): par_ws.column_dimensions[col].width=w
par_ws.freeze_panes='A2'; par_ws.auto_filter.ref=f'A1:N{n}'
res['A1']='VANO Y MARCOS EXTERIORES EN LOS 7 PROTOTIPOS (regla de Zafiro)'; res['A1'].font=Font(bold=True,size=13)
res['A2']='Cada fila suma las partidas de la hoja PARTIDAS. $/m = importe ÷ metros del driver. Confianza: ≤10 % utilizable · ≤25 % revisar · >25 % no usar.'
r=4
curado={'VANO':(17550.08,13323.23),'MARCOS EXTERIORES':(21070.34,42539.53)}
filas_resumen={}
for drv,unid in (('VANO','perímetro interior (m de boquilla gruesa)'),('MARCOS EXTERIORES','m de marco de cantera exterior')):
    res.cell(r,1,drv).font=Font(bold=True,size=12); r+=1
    head(res,r,['Concepto','Unidad']+PROTOS+['n','Media','Desv. muestral','CV muestral','CV poblacional','Confianza','Libro curado Zafiro','Libro curado Oro']); hr=r; r+=1
    res.cell(r,1,'Driver: '+unid);res.cell(r,2,'m'); rd=r
    for p in range(7): res.cell(r,3+p,f'=SUMIFS(PARTIDAS!$I$2:$I${n},PARTIDAS!$A$2:$A${n},{L(3+p)}${hr},PARTIDAS!$B$2:$B${n},"{drv}",PARTIDAS!$L$2:$L${n},"sí")').number_format='#,##0.00'
    r+=1; ri=r
    for capa in ('OBRA GRIS','OBRA BLANCA','REVESTIMIENTO'):
        res.cell(r,1,'Importe '+capa.lower());res.cell(r,2,'$')
        for p in range(7): res.cell(r,3+p,f'=SUMIFS(PARTIDAS!$K$2:$K${n},PARTIDAS!$A$2:$A${n},{L(3+p)}${hr},PARTIDAS!$B$2:$B${n},"{drv}",PARTIDAS!$C$2:$C${n},"{capa}")').number_format='#,##0'
        r+=1
    res.cell(r,1,'Importe total');res.cell(r,2,'$'); rt=r
    for p in range(7): res.cell(r,3+p,f'=SUM({L(3+p)}{ri}:{L(3+p)}{ri+2})').number_format='#,##0'
    res.cell(r,16,curado[drv][0]); res.cell(r,17,curado[drv][1]); r+=2
    res.cell(r-1,1,'$ por metro del driver').font=Font(bold=True)
    labels=[('$/m obra gris',ri),('$/m obra blanca',ri+1),('$/m revestimiento',ri+2),('$/m TOTAL',rt)]
    if drv=='VANO': labels.append(('$/m SIN revestimiento (comparable: solo Zafiro lo trae)',None))
    for t,src in labels:
        res.cell(r,1,t);res.cell(r,2,'$/m')
        for p in range(7):
            cl=L(3+p)
            f=f'=IF(OR({cl}${rd}=0,{cl}{src}=0),"",{cl}{src}/{cl}${rd})' if src else f'=IF({cl}${rd}=0,"",({cl}{ri}+{cl}{ri+1})/{cl}${rd})'
            res.cell(r,3+p,f).number_format='#,##0.00'
        res.cell(r,10,f'=COUNT(C{r}:I{r})'); res.cell(r,11,f'=AVERAGE(C{r}:I{r})').number_format='#,##0.00'
        res.cell(r,12,f'=IF(J{r}<2,"",STDEV(C{r}:I{r}))').number_format='#,##0.00'
        res.cell(r,13,f'=IF(L{r}="","",L{r}/K{r})').number_format='0.0%'
        res.cell(r,14,f'=IF(J{r}<2,"",STDEVP(C{r}:I{r})/K{r})').number_format='0.0%'
        res.cell(r,15,f'=IF(M{r}="","",IF(OR(J{r}<5,K{r}=0),"insuficiente",IF(M{r}<=0.1,"utilizable",IF(M{r}<=0.25,"revisar","no usar")))&" (n="&J{r}&")")')
        if t.startswith('$/m TOTAL'): res.cell(r,16,round(curado[drv][0]/(127 if drv=='VANO' else 44.4),2)); res.cell(r,17,round(curado[drv][1]/(221.5 if drv=='VANO' else 89.9),2))
        r+=1
    r+=1
    res.cell(r,1,'RATIOS (m por m del driver): la parametrización de cada prototipo').font=Font(bold=True); r+=1
    head(res,r,['Concepto','Unidad']+PROTOS+['n','Media','Desv. muestral','CV muestral','CV poblacional']); r+=1
    conceptos=sorted({(f[2],f[3]) for f in filas if f[1]==drv},key=lambda x:(['OBRA GRIS','OBRA BLANCA','REVESTIMIENTO'].index(x[0]),x[1]))
    for capa,conc in conceptos:
        res.cell(r,1,conc);res.cell(r,2,'por m')
        for p in range(7):
            cl=L(3+p)
            res.cell(r,3+p,f'=IF({cl}${rd}=0,"",SUMIFS(PARTIDAS!$I$2:$I${n},PARTIDAS!$A$2:$A${n},{cl}${hr},PARTIDAS!$B$2:$B${n},"{drv}",PARTIDAS!$D$2:$D${n},$A{r})/{cl}${rd})').number_format='0.00'
        res.cell(r,10,f'=COUNTIF(C{r}:I{r},">0")'); res.cell(r,11,f'=IF(J{r}=0,"",AVERAGE(C{r}:I{r}))').number_format='0.00'
        res.cell(r,12,f'=IF(J{r}<2,"",STDEV(C{r}:I{r}))').number_format='0.00'
        res.cell(r,13,f'=IF(L{r}="","",L{r}/K{r})').number_format='0.0%'
        r+=1
    r+=2
res.column_dimensions['A'].width=58
for c in range(2,18): res.column_dimensions[L(c)].width=13
res.column_dimensions['O'].width=22; res.freeze_panes='C4'
txt=['VANO Y MARCOS EXTERIORES EN LOS 7 PROTOTIPOS','',
 'Qué es: las hojas VANO (perímetro interior) y MARCOS EXTERIORES de Zafiro y Oro aplicadas con la misma regla a Rubí, Zafiro Plus, Jade y Diamante − y +.',
 '',
 'La regla:',
 '1. La boquilla fina define el tipo: ACA-01060 es interior (VANO), ACA-01071 es de fachada (MARCOS EXTERIORES), ACA-01072 es del pretil (ver PRETIL_7_PROTOTIPOS). Su boquilla gruesa es la de la misma zona y la misma cantidad, sea cual sea su clave (ACA-01050, 01051 o 01052; el catálogo las usa sin orden).',
 '2. Driver de VANO: los metros de boquilla gruesa interior. Driver de MARCOS EXTERIORES: los metros de marco de cantera exterior (ACA-07011).',
 '3. El marco de cantera interior (ACA-07012) y su sellado solo existen en Zafiro. El sellado interior se cobra por el largo del marco (21 m), no por los 14.4 m del catálogo: excepción autorizada del libro curado.',
 '4. Sellado exterior: los metros de marco; si el catálogo trae más sellado que marco, el sobrante no se cobra y queda anotado.',
 '',
 'Validación: la regla reproduce el libro curado de Zafiro en VANO ($17,550.08 con el marco interior) y en MARCOS EXTERIORES ($21,070.34), y el de Oro en MARCOS EXTERIORES ($42,539.53) y VANO ($13,323.23).',
 '',
 'Por qué VANO salía «no usar» con n = 2: Zafiro lleva una capa de revestimiento (marco de cantera interior) que ningún otro prototipo trae. Sin ella, Zafiro cuesta $59/m contra $60 de Oro. La fila «$/m SIN revestimiento» es la comparable.',
 '',
 'Hallazgos del catálogo:',
 '- Zafiro trae 127 m de boquilla gruesa interior y solo 111 m de fina: faltan 16 m de fina ($149) o sobran de gruesa.',
 '- Jade trae 59.2 m de sellado de marco contra 52.6 m de marco exterior: 6.6 m de sellado sin marco (los mismos 6.6 m que Zafiro ajustó a 21 m).',
 '- Diamante − y + codifican la boquilla gruesa de fachada como ACA-01051 (la del pretil) y no como ACA-01052; Oro también (su fila 319).',
 '- Zafiro Plus lleva la boquilla interior de la planta alta con la clave ACA-01051.',
 '','Reproducir: python3 -I medir_vano_marcos.py (usa el libro de Zafiro v45).']
for i,t in enumerate(txt,1):
    c=lee.cell(i,1,t); c.alignment=Alignment(wrap_text=True,vertical='top')
    if i==1: c.font=Font(bold=True,size=13)
lee.column_dimensions['A'].width=140
wb.calculation.fullCalcOnLoad=True
wb.save(SALIDA); print('partidas',len(filas))
