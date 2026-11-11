"""Pruebas de estabilidad de un libro paramétrico.

Uso:
  python3 -I probar_parametricos.py LIBRO.xlsx ZAFIRO|ORO              # prueba base
  python3 -I probar_parametricos.py LIBRO.xlsx ZAFIRO|ORO --completo   # + Hoja1 barajada + drivers duplicados
  python3 -I probar_parametricos.py LIBRO.xlsx ZAFIRO|ORO --guardar    # escribe estado_esperado_<MODELO>.json con lo que da hoy

Necesita LibreOffice (soffice) para recalcular. La prueba base verifica: ningún error de fórmula,
importes por driver y controles iguales a estado_esperado_<MODELO>.json, controles de estabilidad en 0 e IDs de ruta únicos.
"""
import sys,os,json,shutil,subprocess,tempfile,random,collections
import openpyxl
libro,modelo=sys.argv[1],sys.argv[2]; opts=set(sys.argv[3:])
PANEL={'ZAFIRO':'PARAMÉTRICOS ZAFIRO','ORO':'PARAMÉTRICOS ORO'}[modelo]
ESP=os.path.join(os.path.dirname(os.path.abspath(libro)),f'estado_esperado_{modelo}.json')
tmp=tempfile.mkdtemp(prefix='parametricos_')
def recalcular(src):
    d=tempfile.mkdtemp(dir=tmp)
    subprocess.run(['soffice','--headless','--convert-to','xlsx:Calc MS Excel 2007 XML','--outdir',d,src],stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL,timeout=900)
    return os.path.join(d,os.path.basename(src))
def leer(path):
    wb=openpyxl.load_workbook(path,data_only=True); P=wb[PANEL]; est={}
    for r in range(4,P.max_row+1):
        a=P.cell(r,1).value
        if isinstance(a,str) and isinstance(P.cell(r,6).value,(int,float)): est[a]=round(P.cell(r,6).value,2)
    errores=sum(1 for ws in wb for row in ws.iter_rows() for c in row if isinstance(c.value,str) and c.value.startswith(('#','Err:')))
    R=wb['Rutas']; col=[c.column for c in R[35 if modelo=='ZAFIRO' else 36] if c.value=='RUTA ID (estable)']
    ids=[R.cell(r,col[0]).value for r in range(1,R.max_row+1) if col and R.cell(r,col[0]).value and R.cell(r,col[0]).value!='RUTA ID (estable)']
    return est,errores,ids
fallos=[]
def ok(c,m):
    print(('  ✔ ' if c else '  ✘ ')+m)
    if not c: fallos.append(m)
print('Recalculando',libro); est,err,ids=leer(recalcular(os.path.abspath(libro)))
if '--guardar' in opts:
    json.dump(est,open(ESP,'w',encoding='utf-8'),ensure_ascii=False,indent=1); print('estado guardado en',ESP); sys.exit(0)
esp=json.load(open(ESP,encoding='utf-8'))
ok(err==0,f'sin errores de fórmula ({err})')
dif=[(k,esp[k],est.get(k)) for k in esp if est.get(k) is None or abs(est[k]-esp[k])>0.01]
ok(not dif,f'importes y controles iguales a estado_esperado_<MODELO>.json ({len(esp)} valores)'+(f' — difieren: {dif[:3]}' if dif else ''))
for k in est:
    if k.startswith(('Rutas cuya llave','Rutas con ID','Importe en Rutas','Rutas más allá')): ok(est[k]==0,f'{k} = {est[k]}')
ok(len(ids)==len(set(ids)),f'{len(ids)} IDs de ruta, todos únicos')
if '--completo' in opts:
    random.seed(11); d=tempfile.mkdtemp(dir=tmp); p=os.path.join(d,'barajado.xlsx')
    wb=openpyxl.load_workbook(libro); h=wb['Hoja1']
    # se barajan las filas dentro de cada capítulo (el capítulo se queda en su sitio)
    bloques=[];ini=None
    for r in range(2,h.max_row+2):
        es_cap=(r>h.max_row) or h.cell(r,1).value=='Capítulo'
        if es_cap and ini is not None and r-1>=ini: bloques.append((ini,r-1))
        ini=r+1 if es_cap else ini
    for a,b in bloques:
        filas=list(range(a,b+1)); COLS=list(range(1,31))+[34]   # A:AD y el desambiguador (AH) viajan con su fila
        datos={r:[h.cell(r,c).value for c in COLS] for r in filas}
        perm=filas[:]; random.shuffle(perm)
        for r,s_ in zip(filas,perm):
            for k,c in enumerate(COLS): h.cell(r,c).value=datos[s_][k]
    wb.save(p); e2,er2,_=leer(recalcular(p))
    drv=[k for k in esp if k.startswith('Paramétrico ')] if modelo=='ORO' else [k for k in esp if 'Paramétrico' in k]
    drv=[k for k in esp if k.startswith('Paramétrico') or k.startswith('TOTAL')]
    malos=[k for k in drv if e2.get(k) is None or abs(e2[k]-esp[k])>0.01]
    ok(er2==0 and not malos,f'Hoja1 barajada dentro de cada capítulo ({len(bloques)} bloques): {len(drv)-len(malos)} de {len(drv)} importes no cambian'+(f' — {malos[:3]}' if malos else ''))
    # driver duplicado: cada hoja con D4 editable al doble
    wb=openpyxl.load_workbook(libro); n=0
    for ws in wb:
        if ws.title.startswith('Paramétrico') and 'EDITABLE' in str(ws['A4'].value or '') and str(ws['D4'].value).startswith('=D3'):
            ws['D4']='=D3*2'; n+=1
    p2=os.path.join(tempfile.mkdtemp(dir=tmp),'doble.xlsx'); wb.save(p2); e3,er3,_=leer(recalcular(p2))
    tot=[k for k in esp if k.startswith('TOTAL')][0]
    ok(er3==0 and e3[tot]>esp[tot],f'{n} drivers al doble: sin errores y el total sube de {esp[tot]:,.0f} a {e3[tot]:,.0f}')
    for k in e3:
        if k.startswith(('Rutas cuya llave','Rutas con ID','Importe en Rutas','Rutas más allá')): ok(e3[k]==0,f'con drivers al doble: {k} = {e3[k]}')
shutil.rmtree(tmp,ignore_errors=True)
print('\nRESULTADO:','TODO BIEN' if not fallos else f'{len(fallos)} FALLO(S)'); sys.exit(1 if fallos else 0)
