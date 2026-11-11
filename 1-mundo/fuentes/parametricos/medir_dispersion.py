"""Mide la dispersión de las tasas paramétricas en los 7 prototipos del catálogo.

Lee Hoja1 del libro paramétrico de Zafiro (que trae los siete capítulos) y escribe
DISPERSION_7_PROTOTIPOS.xlsx con el detalle de cada concepto usado, de modo que
cada tasa se pueda auditar. Uso:  python3 -I medir_dispersion.py [libro.xlsx] [salida.xlsx]
"""
import re,sys,openpyxl
from openpyxl.styles import Font,PatternFill,Alignment
from openpyxl.utils import get_column_letter as L

LIBRO=sys.argv[1] if len(sys.argv)>1 else 'CATALOGO_PARAMETRICO_con_MURO_ZAFIRO_CAPAS_v45.xlsx'
SALIDA=sys.argv[2] if len(sys.argv)>2 else 'DISPERSION_7_PROTOTIPOS.xlsx'
PROTOS=['Zafiro 1.0','Rubí','Zafiro Plus','Jade','Diamante −','Diamante +','Oro 4.01']

H=list(openpyxl.load_workbook(LIBRO,read_only=True)['Hoja1'].iter_rows(values_only=True))
capitulos=[(i,r[4],r[7]) for i,r in enumerate(H) if r[0]=='Capítulo']
def proto(i):
    b=0
    for k,(j,_,_) in enumerate(capitulos):
        if j<=i: b=k
    return b
C=[];sub=None;subp=None
for i,r in enumerate(H):
    p=proto(i)
    if r[0]=='Subcapítulo': sub=(r[7] or '').strip(); subp=p
    if r[0]=='Concepto':
        C.append(dict(p=p,sub=sub if subp==p else None,clave=r[5] or '',desc=r[7] or '',u=r[10],q=r[11] or 0,imp=r[13] or 0,ruta=r[16]))
M2_CONSTRUIDOS=[]
for _,_,nombre in capitulos:
    m=re.search(r'\(\s*([\d.]+)\s*m2\s*\)',nombre or '',re.I); M2_CONSTRUIDOS.append(float(m.group(1)))

def m2(d):
    m=re.search(r'\(\s*([\d.]+)\s*m\s*2\s*\)',d,re.I); return float(m.group(1)) if m else None
pre=lambda *x:(lambda c:c['clave'].startswith(x))
losa=lambda c:c['u']=='act' and c['desc'].lower().startswith('losa')
# driver -> (unidad de la tasa, filtro de importe, filtro de divisor, tipo de divisor)
#   tipo 'q' = suma de cantidades; 'm2' = m² leídos de la descripción; 'k' = m² construidos del capítulo; ('c',n) = constante
D=[
 ('LOSA DE CIMENTACIÓN','$/m² de desplante',lambda c:c['sub']=='CIMENTACIÓN' and losa(c),lambda c:c['sub']=='CIMENTACIÓN' and losa(c),'m2'),
 ('CIMENTACIÓN COMPLETA (losa + instalaciones + muros de cimentación)','$/m² de desplante',lambda c:c['sub']=='CIMENTACIÓN',lambda c:c['sub']=='CIMENTACIÓN' and losa(c),'m2'),
 ('LOSAS DE NIVEL (entrepiso y azotea, solo estructura)','$/m² de losa',lambda c:c['sub']!='CIMENTACIÓN' and losa(c),lambda c:c['sub']!='CIMENTACIÓN' and losa(c),'m2'),
 ('ESTRUCTURA DE MURO (tabique, castillos y cadenas de PB y PA)','$/m² de tabique',lambda c:c['sub'] in('PLANTA BAJA','PLANTA ALTA') and c['clave'].startswith('EST-02') and not c['clave'].startswith('EST-0208'),lambda c:c['sub'] in('PLANTA BAJA','PLANTA ALTA') and c['clave']=='EST-02010','q'),
 ('PISO COLOCADO (loseta, zoclo y complementos)','$/m² colocado',pre('ACA-0201','ACA-0202','ACA-0203'),pre('ACA-0201','ACA-0202','ACA-0203'),'q'),
 ('PÓRFIDO','$/m²',lambda c:c['ruta']=='PORFIDO',pre('OBE-02011'),'q'),
 ('BARDA PERIMETRAL','$/ml',lambda c:c['sub']=='BARDA PERIMETRAL',pre('BAP-03010'),'q'),
 ('ASADOR (subcapítulo completo)','$/m² de piso',lambda c:c['sub']=='ASADOR',pre('ACA-02510'),'q'),
 ('PÉRGOLA DE COCHERA','$/m² de pérgola',lambda c:c['desc'].lower().startswith('pergolado para cochera'),lambda c:c['desc'].lower().startswith('pergolado para cochera'),'m2'),
 ('CUBIERTA DE MÁRMOL','$/ml',lambda c:c['ruta']=='CUBIERTA',pre('ACA-02032','ACA-02033'),'q'),
 ('CISTERNA (mismo concepto en los 7: precio, no dispersión)','$/L',lambda c:c['ruta']=='CISTERNA',None,('c',3000)),
 ('ELÉCTRICAS (referencia por m²; la tasa por salida no se puede medir)','$/m² construido',pre('IEC'),None,'k'),
 ('HIDROSANITARIAS Y MUEBLES (referencia por m²)','$/m² construido',pre('ISN','IHD','MSA'),None,'k'),
 ('GAS (referencia por m²)','$/m² construido',pre('IGAS'),None,'k'),
]
# tasas del libro curado a mano (panel de v45 / v19) para validar: (Zafiro, Oro, nota)
CURADO={
 'LOSA DE CIMENTACIÓN':(756.42,771.44,'Reproduce'),
 'BARDA PERIMETRAL':(1752.62,1828.98,'Reproduce'),
 'PÓRFIDO':(541.34,602.39,'Reproduce'),
 'CISTERNA (mismo concepto en los 7: precio, no dispersión)':(7.37,7.37,'Reproduce'),
 'ASADOR (subcapítulo completo)':(3888.11,4071.83,'Definición distinta: el libro curado excluye instalaciones del asador'),
 'PÉRGOLA DE COCHERA':(2060.60,2175.83,'Definición distinta: el libro curado suma chaflán y columnas'),
 'CUBIERTA DE MÁRMOL':(3180.85,5738.32,'Definición distinta: el libro curado suma poyos'),
 'ESTRUCTURA DE MURO (tabique, castillos y cadenas de PB y PA)':(694.18,None,'Definición distinta: el libro curado de Zafiro es solo obra negra de 18 partidas'),
}

wb=openpyxl.Workbook(); lee=wb.active; lee.title='LEEME'
det=wb.create_sheet('DETALLE'); tas=wb.create_sheet('TASAS',1)
HF=Font(bold=True,color='FFFFFF'); HB=PatternFill('solid',fgColor='305496')
def head(ws,r,vals):
    for i,v in enumerate(vals,1):
        c=ws.cell(r,i,v); c.font=HF; c.fill=HB; c.alignment=Alignment(wrap_text=True,vertical='center')
head(det,1,['Prototipo','Driver','Rol','Clave','Descripción','Unidad','Cantidad','Importe','Valor del divisor'])
r=2
for name,u,fi,fd,kd in D:
    for p in range(7):
        for c in [c for c in C if c['p']==p and fi(c)]:
            det.cell(r,1,PROTOS[p]);det.cell(r,2,name);det.cell(r,3,'importe');det.cell(r,4,c['clave']);det.cell(r,5,c['desc'][:110]);det.cell(r,6,c['u']);det.cell(r,7,c['q']);det.cell(r,8,c['imp']);r+=1
        if kd=='m2':
            for c in [c for c in C if c['p']==p and fd(c)]:
                v=m2(c['desc'])
                if v: det.cell(r,1,PROTOS[p]);det.cell(r,2,name);det.cell(r,3,'divisor');det.cell(r,4,c['clave']);det.cell(r,5,c['desc'][:110]);det.cell(r,6,'m²');det.cell(r,9,v);r+=1
        elif kd=='q':
            for c in [c for c in C if c['p']==p and fd(c)]:
                det.cell(r,1,PROTOS[p]);det.cell(r,2,name);det.cell(r,3,'divisor');det.cell(r,4,c['clave']);det.cell(r,5,c['desc'][:110]);det.cell(r,6,c['u']);det.cell(r,9,c['q']);r+=1
        elif kd=='k':
            det.cell(r,1,PROTOS[p]);det.cell(r,2,name);det.cell(r,3,'divisor');det.cell(r,4,'CAPÍTULO');det.cell(r,5,'m² construidos del nombre del capítulo');det.cell(r,6,'m²');det.cell(r,9,M2_CONSTRUIDOS[p]);r+=1
        else:
            det.cell(r,1,PROTOS[p]);det.cell(r,2,name);det.cell(r,3,'divisor');det.cell(r,4,'CONSTANTE');det.cell(r,5,'Capacidad de la cisterna prefabricada');det.cell(r,6,'L');det.cell(r,9,kd[1]);r+=1
for col,w in zip('ABCDEFGHI',(14,48,9,12,70,8,10,13,14)): det.column_dimensions[col].width=w
det.freeze_panes='A2'; det.auto_filter.ref=f'A1:I{r-1}'
nd=len(D); top=5; imp0=top+nd+4; div0=imp0+nd+3
tas['A1']='TASAS PARAMÉTRICAS EN LOS 7 PROTOTIPOS Y SU DISPERSIÓN'; tas['A1'].font=Font(bold=True,size=13)
tas['A2']='Cada tasa = importe ÷ divisor, ambos sumados de la hoja DETALLE con SUMIFS (auditables). CV = desviación ÷ media. Confianza: ≤10 % utilizable · ≤25 % revisar · >25 % no usar (regla de CONOCIMIENTO.md §5.7).'
head(tas,top,['Driver','Unidad de la tasa']+PROTOS+['n','Media','Desv. muestral','CV muestral','CV poblacional','Confianza','Tasa Zafiro (libro curado)','Tasa Oro (libro curado)','Validación contra el libro curado'])
tas.cell(imp0-1,1,'IMPORTES ($) por driver y prototipo').font=Font(bold=True)
head(tas,imp0,['Driver','']+PROTOS)
tas.cell(div0-1,1,'DIVISORES por driver y prototipo').font=Font(bold=True)
head(tas,div0,['Driver','']+PROTOS)
for k,(name,u,fi,fd,kd) in enumerate(D):
    ra=top+1+k; ri=imp0+1+k; rd=div0+1+k
    for rr in (ra,ri,rd): tas.cell(rr,1,name)
    tas.cell(ra,2,u)
    for p in range(7):
        col=L(3+p)
        tas.cell(ri,3+p,f'=SUMIFS(DETALLE!$H:$H,DETALLE!$A:$A,{col}${imp0},DETALLE!$B:$B,$A{ri},DETALLE!$C:$C,"importe")').number_format='#,##0'
        tas.cell(rd,3+p,f'=SUMIFS(DETALLE!$I:$I,DETALLE!$A:$A,{col}${div0},DETALLE!$B:$B,$A{rd},DETALLE!$C:$C,"divisor")').number_format='#,##0.00'
        tas.cell(ra,3+p,f'=IF(OR({col}{rd}=0,{col}{ri}=0),"",{col}{ri}/{col}{rd})').number_format='#,##0.00'
    tas.cell(ra,10,f'=COUNT(C{ra}:I{ra})')
    tas.cell(ra,11,f'=IF(J{ra}=0,"",AVERAGE(C{ra}:I{ra}))').number_format='#,##0.00'
    tas.cell(ra,12,f'=IF(J{ra}<2,"",STDEV(C{ra}:I{ra}))').number_format='#,##0.00'
    tas.cell(ra,13,f'=IF(L{ra}="","",L{ra}/K{ra})').number_format='0.0%'
    tas.cell(ra,14,f'=IF(J{ra}<2,"",STDEVP(C{ra}:I{ra})/K{ra})').number_format='0.0%'
    tas.cell(ra,15,f'=IF(J{ra}<5,"insuficiente (n="&J{ra}&")",IF(M{ra}<=0.1,"utilizable",IF(M{ra}<=0.25,"revisar","no usar"))&" (n="&J{ra}&")")')
    cur=CURADO.get(name)
    if cur:
        if cur[0] is not None: tas.cell(ra,16,cur[0]).number_format='#,##0.00'
        if cur[1] is not None: tas.cell(ra,17,cur[1]).number_format='#,##0.00'
        tas.cell(ra,18,cur[2])
tas.column_dimensions['A'].width=62; tas.column_dimensions['B'].width=18
for c in range(3,18): tas.column_dimensions[L(c)].width=13
tas.column_dimensions['O'].width=24; tas.column_dimensions['R'].width=70; tas.freeze_panes=tas.cell(top+1,3)
txt=['MEDICIÓN DE DISPERSIÓN EN LOS 7 PROTOTIPOS','',
 'Qué es: las tasas paramétricas medidas con una misma regla en Zafiro 1.0, Rubí, Zafiro Plus, Jade, Diamante −, Diamante + y Oro 4.01, para obtener la dispersión que pide CONOCIMIENTO.md §5.7 («un precio sin su dispersión es un número disfrazado de certeza»).',
 '',
 'Método: cada driver es un filtro sobre Hoja1 (por subcapítulo, prefijo de clave o ruta) y un divisor que sale de la cantidad de un concepto ancla o de los m² escritos en la descripción. No se parametrizó un libro por prototipo: eso exigiría las decisiones manuales de capas, divisiones y fijos que hoy solo existen para Zafiro y Oro.',
 'Validación: la regla reproduce el libro curado a mano donde las definiciones coinciden (losa de cimentación, barda, pórfido, cisterna). Donde no coinciden, la columna R dice por qué.',
 'Reproduce D-312: la cimentación completa da CV 6.0 % poblacional contra el desplante (6.5 % muestral), igual que la prueba del cerebro.',
 '',
 'Límites:',
 '1. Los drivers medidos usan clasificación por clave y subcapítulo; no sustituyen el reparto por capas del libro curado.',
 '2. Instalaciones: la tasa por salida se mide en TABLA_APARATOS_SALIDAS.xlsx (CV de 3 a 7 %). Aquí queda solo la referencia por m² construido: sale estable en eléctricas (CV ~9 %) y revisable en hidrosanitarias (~11 %) y gas (~20 %), más de lo que el cerebro suponía. No prueba que el m² sea el parámetro correcto: para eso hace falta contar las salidas de los 5 prototipos.',
 '3. Pretil, vano, jardín, fachada y herrería no se midieron: el divisor no existe en todos los prototipos o es el precio unitario de un solo concepto.',
 '4. Coladera, cochera y asador no están en todos los prototipos: el n de cada fila lo dice.',
 '5. Cisterna y barda repiten el mismo concepto: su CV bajo es precio, no estabilidad del diseño.',
 '',
 'Reproducir: python3 -I medir_dispersion.py (usa el libro de Zafiro v45 y regenera este archivo).']
for i,t in enumerate(txt,1):
    c=lee.cell(i,1,t); c.alignment=Alignment(wrap_text=True,vertical='top')
    if i==1: c.font=Font(bold=True,size=13)
lee.column_dimensions['A'].width=140
wb.calculation.fullCalcOnLoad=True
wb.save(SALIDA); print('filas detalle',r-1)
