"""Oro v22 -> v23: la escalera se cuenta por escalones (puntos), escala a lo largo y lleva spot cada 3 escalones.

Cambios (los importes de la escalera no cambian; solo los spots, que pasan de 6 a 8 por la regla):
- ESCALERA: escalones en PB y PA (puntos, editables) y largo del escalón (1.20 m, editable). El escalón forjado
  y su forrado escalan con (escalones del nivel × largo ÷ 1.20).
- ELÉCTRICAS, SPOT DE ESCALERA: un spot cada 3 escalones empezando en el 3.º de cada tramo = INT(escalones ÷ 3) por nivel.
Uso: python3 -I escalera_oro.py CATALOGO_PARAMETRICO_ORO_v22.xlsx CATALOGO_PARAMETRICO_ORO_v23.xlsx
"""
import sys,openpyxl
from openpyxl.styles import Font,PatternFill,Alignment
src,dst=sys.argv[1:3]
wb=openpyxl.load_workbook(src)
E=wb['Paramétrico ESCALERA']; EL=wb['Paramétrico ELÉCTRICAS']; P=wb['PARAMÉTRICOS ORO']; R=wb['Rutas']
amar=PatternFill('solid',fgColor='FFF2CC'); neg=Font(bold=True)
# --- parámetros de la escalera
E['I3']='Escalones en planta baja (puntos)'; E['L3']='=I16'; E['M3']='=L3'; E['M3'].fill=amar
E['I4']='Escalones en planta alta (puntos)'; E['L4']='=I17'; E['M4']='=L4'; E['M4'].fill=amar
E['I5']='Largo del escalón (m)'; E['L5']=1.2; E['M5']='=L5'; E['M5'].fill=amar
E['L2']='Base'; E['M2']='Proyecto (EDITABLE)'
for c in ('L2','M2'): E[c].font=neg
E['I6']='Un spot de escalera cada 3 escalones, desde el 3.º de cada tramo'; E['I6'].font=Font(italic=True)
E['A3']='Driver BASE de Oro (escalones, puntos)'; E['D3']='=L3+L4'; E['E3']='escalones (puntos)'
E['A4']='Escalones del PROYECTO (suma de PB y PA)'; E['D4']='=M3+M4'; E['E4']='se editan por nivel en M3 y M4; el largo en M5'
E['D4'].fill=PatternFill(fill_type=None)
E['A2']='Escalones forjados y su forrado, contados por escalón (punto) y escalables a lo largo (1.20 m de base). Cada capa tiene interruptor Sí/No.'
nom={16:'ESCALÓN FORJADO (1.20 M DE LARGO)',17:'ESCALÓN FORJADO (1.20 M DE LARGO)'}
niv={16:'$M$3/$L$3',17:'$M$4/$L$4',18:'$M$3/$L$3',19:'$M$4/$L$4'}
for r,f in niv.items():
    E.cell(r,13).value=f'=I{r}*({f})*($M$5/$L$5)'
    E.cell(r,16).value='Cantidad = base × escalones del nivel ÷ base × largo ÷ 1.20 m'
    if r in nom: E.cell(r,4).value=nom[r]
    E.cell(r,12).value=f'=IF(N($D$3)=0,0,I{r}/$D$3)'
# Rutas y panel: nombres y unidad
for r in range(30,R.max_row+1):
    if R.cell(r,2).value=='ESCALERA' and R.cell(r,7).value=='ESCALÓN FORJADO DE 1.00': R.cell(r,7).value='ESCALÓN FORJADO (1.20 M DE LARGO)'
for r in range(5,45):
    if R.cell(r,1).value=='ESCALERA' and R.cell(r,2).value in('pzas','escalones'): R.cell(r,2).value='escalones (puntos)'
# --- spots de escalera en ELÉCTRICAS
EL['D21']="=INT('Paramétrico ESCALERA'!L3/3)+INT('Paramétrico ESCALERA'!L4/3)"
EL['E21']="=INT('Paramétrico ESCALERA'!M3/3)+INT('Paramétrico ESCALERA'!M4/3)"
EL['I21']='Se calcula con los escalones de la hoja ESCALERA: un spot cada 3 escalones, desde el 3.º de cada tramo.'
pb="INT('Paramétrico ESCALERA'!$L$3/3)"; pa="INT('Paramétrico ESCALERA'!$L$4/3)"
npb="INT('Paramétrico ESCALERA'!$M$3/3)"; npa="INT('Paramétrico ESCALERA'!$M$4/3)"
for r,(b,n) in {172:(pb,npb),173:(pa,npa),174:(pb,npb),175:(pa,npa)}.items():
    assert EL.cell(r,1).value=='SPOT DE ESCALERA'
    EL.cell(r,9).value='='+b            # cantidad base
    EL.cell(r,13).value='='+n           # cantidad del proyecto
# --- hoja LEEME
L=wb.create_sheet('LEEME v23',0)
txt=['CATALOGO PARAMÉTRICO ORO v23: escalera por escalones','',
 '1. ESCALERA se cuenta por escalones (puntos): 18 en planta baja y 6 en planta alta. Se editan en M3 y M4 de la hoja ESCALERA.',
 '2. Cada escalón mide 1.20 m de largo (M5). El escalón forjado y su forrado escalan con escalones del nivel × largo ÷ 1.20.',
 '3. Los spots de escalera son uno cada 3 escalones, empezando en el 3.º de cada tramo: INT(escalones ÷ 3) por nivel = 6 en PB y 2 en PA = 8. Se cobran en ELÉCTRICAS (grupo SPOT DE ESCALERA), ligados a los escalones.',
 '',
 'Efecto: la escalera (forjado y forrado) queda en $28,301, igual que en v22. Los spots pasan de 6 a 8: +$860.70 (2 salidas de $150.39 y 2 luminarias de $279.96). El catálogo trae 8 salidas y 9 luminarias; el libro de v22 usaba 6 por un ajuste anterior (4 en PB y 2 en PA).',
 'La diferencia contra Hoja1 pasa de $19,250.97 a $20,111.67.']
for i,t in enumerate(txt,1):
    c=L.cell(i,1,t); c.alignment=Alignment(wrap_text=True,vertical='top')
    if i==1: c.font=Font(bold=True,size=13)
L.column_dimensions['A'].width=140
wb.calculation.fullCalcOnLoad=True
wb.save(dst)
