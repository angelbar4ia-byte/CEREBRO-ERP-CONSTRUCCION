"""Estabiliza un libro paramétrico (Zafiro u Oro): IDs de ruta únicos, rangos sin tope,
controles de integridad, ruta paramétrica en Hoja1 y catálogo de constantes.

Uso: python3 -I estabilizar_parametricos.py LIBRO_FUENTE.xlsx LIBRO_RECALCULADO.xlsx SALIDA.xlsx ZAFIRO|ORO

LIBRO_RECALCULADO es el mismo libro abierto y guardado por un motor de cálculo (para saber a qué
driver alimenta cada concepto de Hoja1). Los importes no cambian: lo prueba probar_parametricos.py.
"""
import sys,re,collections
import openpyxl
from copy import copy
from openpyxl.styles import Font,Alignment,PatternFill
from openpyxl.utils import get_column_letter as L

fuente,recalc,salida,modelo=sys.argv[1:5]
CFG={'ZAFIRO':dict(panel='PARAMÉTRICOS ZAFIRO',presup='PRESUPUESTO ZAFIRO',hdr=35,nota='LEEME ESTABILIDAD v46'),
     'ORO':dict(panel='PARAMÉTRICOS ORO',presup='PRESUPUESTO ORO',hdr=36,nota='LEEME ESTABILIDAD v22')}[modelo]
wb=openpyxl.load_workbook(fuente); wv=openpyxl.load_workbook(recalc,data_only=True)
R=wb['Rutas']; Rv=wv['Rutas']; P=wb[CFG['panel']]; H=wb['Hoja1']
hdr=CFG['hdr']; c0=hdr+1
filas=[r for r in range(c0,Rv.max_row+1) if Rv.cell(r,2).value]
ultima=max(filas)


# 0. Llave con capítulo: Capítulo|Clave|Ingeniería|Descripción(60)|Origen|Nivel|ocurrencia
#    (la llave anterior chocaba entre prototipos: un mismo código de ingeniería aparece en varios capítulos)
def num_txt(v):
    if v is None: return ""
    if isinstance(v,float) and v.is_integer(): v=int(v)
    return str(v)
def esc(t): return t.replace('"','""').replace('~','~~').replace('*','~*').replace('?','~?')
def unesc(t): return t.replace('~*','*').replace('~?','?').replace('~~','~').replace('""','"')
nrow=H.max_row; cnt={};cnt2={};old={};new={};cap=''
# conceptos que cobra cada driver (para desambiguar filas idénticas de Hoja1)
drv0=collections.defaultdict(set)
for r_ in range(hdr+1,Rv.max_row+1):
    if Rv.cell(r_,2).value and isinstance(Rv.cell(r_,14).value,(int,float)): drv0[int(Rv.cell(r_,14).value)].add(Rv.cell(r_,2).value)
base1={};cap=''
for r in range(2,nrow+1):
    b0=f"{num_txt(H.cell(r,6).value)}|{num_txt(H.cell(r,5).value)}|{num_txt(H.cell(r,8).value)[:60]}"
    cnt[b0]=cnt.get(b0,0)+1; old[f"{b0}|{cnt[b0]}"]=r
    if H.cell(r,1).value=='Capítulo': cap=num_txt(H.cell(r,5).value)
    base1[r]=f"{cap}|{b0}|{num_txt(H.cell(r,16).value)}|{num_txt(H.cell(r,23).value)}"
grupos=collections.defaultdict(list)
for r,b1 in base1.items(): grupos[b1].append(r)
desamb={};ndes=0
for b1,rs in grupos.items():
    if len(rs)>1 and any(drv0.get(r) for r in rs):
        usados=set()
        for r in rs:
            et=' + '.join(sorted(drv0.get(r,[]))) or 'SIN DRIVER'
            if et in usados: et=f'{et}-{len(usados)+1}'
            usados.add(et); desamb[r]=et; ndes+=1
for r in range(2,nrow+1):
    b1=f"{base1[r]}|{desamb.get(r,'')}"
    cnt2[b1]=cnt2.get(b1,0)+1; new[r]=f"{b1}|{cnt2[b1]}"
H.cell(1,31).value='LLAVE BASE (capítulo|clave|ing|desc|origen|nivel|desambiguador)'; H.cell(1,32).value='LLAVE (única)'
c=H.cell(1,33,'CAPÍTULO (auxiliar)'); c._style=copy(H.cell(1,32)._style); H.column_dimensions['AG'].width=14
c=H.cell(1,34,'DESAMBIGUADOR (solo si hay filas idénticas)'); c._style=copy(H.cell(1,32)._style); H.column_dimensions['AH'].width=22
for r in range(2,nrow+1):
    H.cell(r,33).value=f'=IF(A{r}="Capítulo",E{r},AG{r-1})'
    if r in desamb: H.cell(r,34).value=desamb[r]
    H.cell(r,31).value=f'=AG{r}&"|"&F{r}&"|"&E{r}&"|"&LEFT(H{r},60)&"|"&P{r}&"|"&W{r}&"|"&AH{r}'
    H.cell(r,32).value=f'=AE{r}&"|"&COUNTIF(AE$2:AE{r},AE{r})'
lit=re.compile(r'MATCH\("((?:[^"]|"")*)",Hoja1!\$AF:\$AF,0\)')
re_llaves=0
def sub_lit(m):
    global re_llaves
    r=old[unesc(m.group(1))]; re_llaves+=1
    return f'MATCH("{esc(new[r])}",Hoja1!$AF:$AF,0)'
for ws in wb:
    if ws.title in('Hoja1','Leyenda Q-Z','Catálogo Geometría'): continue
    for row in ws.iter_rows():
        for c in row:
            if isinstance(c.value,str) and c.value.startswith('=') and 'Hoja1!$AF:$AF' in c.value:
                c.value=lit.sub(sub_lit,c.value)

# 1. RUTA ID único y estable (no depende de la posición de la fila)
col=R.max_column+1; ID=L(col)
h=R.cell(hdr,col,'RUTA ID (estable)'); h._style=copy(R.cell(hdr,col-1)._style)
R.column_dimensions[ID].width=70
for r in filas:
    af=f'INDEX(Hoja1!$AF:$AF,$N{r})'
    occ=f'RIGHT({af},LEN({af})-FIND("§",SUBSTITUTE({af},"|","§",LEN({af})-LEN(SUBSTITUTE({af},"|","")))))'
    R.cell(r,col,f'=IF(OR($B{r}="",ISERROR($N{r})),"",$A{r}&" # "&INDEX(Hoja1!$F:$F,$N{r})&"-"&INDEX(Hoja1!$E:$E,$N{r})&"-"&{occ})')

# 2. Rangos sin tope: Rutas!$M$36:$M$700 -> Rutas!$M:$M
pat=re.compile(r'Rutas!\$([A-Z]+)\$\d+:\$([A-Z]+)\$\d+')
cambios=0
for ws in wb:
    if ws.title in('Hoja1','Leyenda Q-Z','Catálogo Geometría'): continue
    for row in ws.iter_rows():
        for c in row:
            v=c.value
            if isinstance(v,str) and v.startswith('=') and 'Rutas!$' in v:
                n=pat.sub(lambda m:f'Rutas!${m.group(1)}:${m.group(2)}',v)
                if n!=v: c.value=n; cambios+=1

# 3. Controles de integridad en el panel
tot=[r for r in range(1,P.max_row+1) if str(P.cell(r,1).value or '').startswith('TOTAL de los paramétricos')][0]
r0=P.max_row+2
P.cell(r0,1,'CONTROLES DE ESTABILIDAD (todos deben dar 0)').font=Font(bold=True)
ctrl=[
 ('Rutas cuya llave no se encuentra en Hoja1',f'=SUMPRODUCT(--ISERROR(Rutas!$N${c0}:$N$5000))'),
 ('Rutas con ID repetido',f'=SUMPRODUCT((Rutas!${ID}${c0}:${ID}$5000<>"")*(COUNTIF(Rutas!${ID}${c0}:${ID}$5000,Rutas!${ID}${c0}:${ID}$5000)>1))'),
 ('Importe en Rutas que ningún driver del panel recoge ($)',f'=ROUND(SUMIFS(Rutas!$M:$M,Rutas!$J:$J,"S*")-F{tot},2)'),
 ('Rutas más allá de la fila 2,000 (fuera de los controles)','=COUNTA(Rutas!$B$2000:$B$20000)'),
]
for i,(t,f) in enumerate(ctrl,1):
    P.cell(r0+i,1,t); P.cell(r0+i,6,f).number_format='#,##0.00'
P.cell(r0+len(ctrl)+1,1,'Hoja LEEME ESTABILIDAD: qué protege cada control y cómo regenerar el libro.')
FILA_CTRL=(r0+1,r0+len(ctrl))

# 4. Ruta paramétrica de cada concepto de Hoja1 (columna Q) = driver(s) que lo cobran
drivers=collections.defaultdict(set)
for r in filas:
    n=Rv.cell(r,14).value
    if isinstance(n,(int,float)): drivers[int(n)].add(Rv.cell(r,2).value)
qcol=17
assert H.cell(1,qcol).value=='Ruta paramétrica'
for n,ds in drivers.items(): H.cell(n,qcol).value=' + '.join(sorted(ds))

# 5. Constantes escritas dentro de fórmulas (para que se vean)
quitar=[re.compile(r'"[^"]*"'),re.compile(r"'[^']*'!"),re.compile(r'\$?[A-Z]{1,3}\$?\d+'),re.compile(r'Hoja1!\$?[A-Z]+:\$?[A-Z]+')]
const=[]
for ws in wb:
    if not ws.title.startswith('Paramétrico'): continue
    for row in ws.iter_rows():
        for c in row:
            v=c.value
            if not(isinstance(v,str) and v.startswith('=')) or 'MATCH(' in v and 'INDEX(Hoja1' in v and len(re.findall(r'\d+\.\d+|\*\d+/\d+',re.sub(r'MATCH\("[^)]*\)','',v)))==0: 
                continue
            t=v
            t=re.sub(r'MATCH\("(?:[^"]|"")*",Hoja1!\$AF:\$AF,0\)','',t)
            for p in quitar: t=p.sub('',t)
            nums=[x for x in re.findall(r'(?<![A-Za-z])\d+(?:\.\d+)?',t) if x not in('0','1','2','0.0001','0.5','100') and not x.startswith('0.00')]
            if nums:
                quien=ws.cell(c.row,4).value or ws.cell(c.row,1).value or ''
                const.append((ws.title,c.coordinate,str(quien)[:50],v[:120],', '.join(nums)))
S=wb.create_sheet('CONSTANTES EN FÓRMULAS')
for i,t in enumerate(['Hoja','Celda','Concepto o grupo','Fórmula','Constantes escritas'],1):
    c=S.cell(1,i,t); c.font=Font(bold=True,color='FFFFFF'); c.fill=PatternFill('solid',fgColor='305496')
for i,fila in enumerate(const,2):
    for j,v in enumerate(fila,1):
        c=S.cell(i,j,v)
        if isinstance(v,str) and v.startswith('='): c.data_type='s'
for k,w in zip('ABCDE',(34,9,44,100,24)): S.column_dimensions[k].width=w
S.freeze_panes='A2'
# 6. LEEME
L2=wb.create_sheet(CFG['nota'],0)
txt=['ESTABILIDAD DEL LIBRO PARAMÉTRICO','',
 'Qué se hizo (los importes no cambian; lo comprueba probar_parametricos.py):',
 f'0. LLAVES: Hoja1 trae la columna AG (capítulo auxiliar) y las llaves AE/AF ahora incluyen el capítulo, el origen, el nivel y, solo donde hay filas idénticas, el desambiguador (columna AH, con el driver que cobra la fila); todas las llaves de las hojas se reescribieron. Esto reemplaza lo que dice la hoja LEEME anterior sobre la llave.',
 f'1. RUTA ID (Rutas, columna {ID}): identificador único de cada partida = ruta + clave + código de ingeniería + ocurrencia en Hoja1. No depende de la posición de la fila.',
 '2. Los rangos de Rutas en el panel y en PRESUPUESTO ya no tienen tope (antes $36:$700 o $37:$828): una ruta nueva no queda fuera de los totales.',
 f'3. Cuatro controles de estabilidad en el panel (filas {FILA_CTRL[0]} a {FILA_CTRL[1]}): llaves que no se encuentran, IDs repetidos, importe de Rutas que el panel no recoge y rutas fuera de rango. Todos deben dar 0.',
 '4. Hoja1, columna Q (Ruta paramétrica): ahora dice el driver que de verdad cobra cada concepto (antes era una etiqueta inferida). Si un concepto lo cobran dos drivers, van unidos con +.',
 '5. Hoja CONSTANTES EN FÓRMULAS: todas las cantidades escritas a mano dentro de fórmulas (repartos como *9/21, conteos como =3). No se tocaron; ahora se ven.',
 '',
 'Cómo agregar una partida sin romper nada:',
 '- En la hoja del driver, copiar una fila de partida completa y cambiar su llave (columna Fila Hoja1) y su concepto.',
 '- Agregar su fila en Rutas copiando una del mismo driver; la columna RUTA ID se calcula sola.',
 '- Si cambia la clave, la ingeniería, el origen, el nivel o los primeros 60 caracteres de la descripción de un concepto de Hoja1, hay que actualizar su llave en la hoja del driver.',
 '- Revisar que los controles de estabilidad den 0 y que «Conceptos SIN paramétrico» siga en 0.',
 '',
 'Cómo reordenar o reemplazar Hoja1: se puede ordenar filas dentro de cada capítulo; los paramétricos buscan por llave (columna AF = capítulo|clave|ingeniería|descripción|origen|nivel|desambiguador|ocurrencia). La llave anterior no incluía el capítulo y se confundía entre prototipos.',
 'Pruebas: python3 -I probar_parametricos.py (recalcula el libro, compara con estado_esperado.json y verifica los controles).',
 'Regenerar este libro: python3 -I estabilizar_parametricos.py.']
for i,t in enumerate(txt,1):
    c=L2.cell(i,1,t); c.alignment=Alignment(wrap_text=True,vertical='top')
    if i==1: c.font=Font(bold=True,size=13)
L2.column_dimensions['A'].width=140
wb.calculation.fullCalcOnLoad=True
wb.save(salida)
print('llaves reescritas',re_llaves,'| filas desambiguadas',ndes,'| rangos cambiados',cambios,'| rutas',len(filas),'| conceptos con ruta',len(drivers),'| constantes',len(const),'| controles en filas',FILA_CTRL,'| ID en',ID)
