"""Recommended four-panel figure combining reproductive and population targets."""
from pathlib import Path
import argparse
import csv
import math
import sys
import numpy as np
from reportlab.graphics.shapes import Drawing, Rect, Line, PolyLine, String, Group
from reportlab.graphics import renderPDF, renderSVG
from reportlab.lib.colors import Color, HexColor
import pypdfium2 as pdfium

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from models import reproductive_output as G, population_threshold

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('--output-dir', type=Path,
                    default=Path(__file__).resolve().parents[1] / 'results')
ROOT = parser.parse_args().output_dir.resolve()
ROOT.mkdir(parents=True, exist_ok=True)
D = Drawing(540, 496)
anchors = np.array([[68,1,84],[59,82,139],[33,145,140],[94,201,98],[253,231,37]]) / 255

def color(z):
    z = float(np.clip(z, 0, 1)) * 4
    i = min(int(z), 3)
    return Color(*(anchors[i] * (1-z+i) + anchors[i+1] * (z-i)))

def text(x,y,s,size=7,anchor='start',font='Helvetica',col='#161616'):
    D.add(String(x,y,s,fontName=font,fontSize=size,textAnchor=anchor,fillColor=HexColor(col)))

def line(x,y,xx,yy,col='#222222',width=.6,dash=None):
    D.add(Line(x,y,xx,yy,strokeColor=HexColor(col),strokeWidth=width,strokeDashArray=dash))

class Ax:
    def __init__(self,x,y,letter,title,subtitle,ylim,ylab):
        self.x=x;self.y=y;self.w=170;self.h=142;self.lo,self.hi=ylim;self.ylab=ylab
        text(x-28,y+176,letter,11,font='Helvetica-Bold')
        text(x,y+176,title,8.4,font='Helvetica-Bold')
        text(x,y+164,subtitle,6.5,col='#555B61')

    def X(self,c):return self.x+self.w*c
    def Y(self,v):return self.y+self.h*(v-self.lo)/(self.hi-self.lo)

    def heat(self,fn,panel,log=False):
        rows=[]
        for j in range(100):
            v=self.lo+(j+.5)*(self.hi-self.lo)/100
            for i in range(100):
                c=(i+.5)/100
                val=float(fn(c,v))
                z=(math.log10(val)/3 if log else val/100) if np.isfinite(val) else None
                D.add(Rect(self.X(i/100),self.Y(self.lo+j*(self.hi-self.lo)/100),
                           self.w/100+.03,self.h/100+.03,
                           fillColor=color(z) if z is not None else HexColor('#D8DADD'),
                           strokeColor=None))
                rows.append((c,v,val))
        with (ROOT/f'selected_panel_{panel}.csv').open('w',newline='') as f:
            w=csv.writer(f);w.writerow(['c','r' if panel=='A' else ('R0' if panel=='D' else 'f'),
                                       'required_ratio' if log else 'reproductive_reduction_percent']);w.writerows(rows)

    def axes(self,ticks):
        for c in [0,.25,.5,.75,1]:
            xx=self.X(c);line(xx,self.y,xx,self.y-3);text(xx,self.y-12,f'{c:g}',6.5,'middle')
        for v,label in ticks:
            yy=self.Y(v);line(self.x-3,yy,self.x,yy);text(self.x-6,yy-2,label,6.5,'end')
        line(self.x,self.y,self.x+self.w,self.y);line(self.x,self.y,self.x,self.y+self.h)
        text(self.x+self.w/2,self.y-27,'Relative mating competitiveness c',7,'middle')
        gr=Group(String(0,0,self.ylab,fontName='Helvetica',fontSize=7,textAnchor='middle'))
        gr.transform=(0,1,-1,0,self.x-32,self.y+self.h/2);D.add(gr)

    def path(self,c,v,dash=None):
        valid=np.isfinite(v)&(v>=self.lo)&(v<=self.hi)
        points=[]
        for cc,vv in zip(c[valid],v[valid]):points.extend([self.X(cc),self.Y(vv)])
        if len(points)>3:
            D.add(PolyLine(points,strokeColor=HexColor('#FFFFFF'),strokeWidth=.8,
                           strokeDashArray=dash,fillColor=None))

def bar(ax,log=False):
    x=ax.x+182;y=ax.y
    for i in range(150):
        D.add(Rect(x,y+i*ax.h/150,7,ax.h/150+.04,fillColor=color((i+.5)/150),strokeColor=None))
    vals=[(0,'≤1'),(1/3,'10'),(2/3,'100'),(1,'≥1000')] if log else [(0,'0'),(.25,'25'),(.5,'50'),(.75,'75'),(1,'100')]
    for v,label in vals:
        yy=y+v*ax.h;line(x+7,yy,x+10,yy,width=.4);text(x+12,yy-2,label,6)
    text(x+3,y+ax.h+6,'Ratio r (log)' if log else 'Reduction (%)',6,'middle')

c=np.linspace(.001,1,1500)
A=Ax(51,306,'A','Reproductive-output reduction','Vary competitiveness and ratio; f = 0',(0,50),'Released / wild male ratio r')
A.heat(lambda c,r:100*(1-G(c,r,0)),'A')
A.axes([(v,str(v)) for v in [0,10,20,30,40,50]]);bar(A)
for target,cc in [(.9,.25),(.95,.5)]:
    A.path(c,target/((1-target)*c))
    text(A.X(cc),A.Y(target/((1-target)*cc))+3,f'{int(100*target)}%',6.5,col='#FFFFFF')

B=Ax(316,306,'B','Reproductive-output reduction','Vary competitiveness and fertility; r = 10',(0,.2),'Relative fertility f (%)')
B.heat(lambda c,f:100*(1-G(c,10,f)),'B')
B.axes([(v,f'{100*v:g}') for v in [0,.05,.1,.15,.2]]);bar(B)
for target,cc in [(.5,.135),(.75,.5)]:
    B.path(c,1-target-target/(10*c))
    text(B.X(cc),B.Y(1-target-target/(10*cc))+3,f'{int(100*target)}%',6.5,col='#FFFFFF')

C=Ax(51,67,'C','Ratio for 90% adult suppression','Illustrative R0 = 4; no immigration',(0,.4),'Relative fertility f (%)')
C.heat(lambda c,f:population_threshold(c,f,4,.1),'C',True)
C.axes([(v,f'{100*v:g}') for v in [0,.1,.2,.3,.4]]);bar(C,True)
boundary=1/3.7
line(C.x,C.Y(boundary),C.x+C.w,C.Y(boundary),'#FFFFFF',.8,[3,2])
text(C.x+C.w/2,C.Y(.35),'No finite release ratio',6.8,'middle',col='#45494D')
for ratio,cc in [(10,.65),(50,.38)]:
    ff=(1-2.7/(ratio*c))/3.7;C.path(c,ff,[2,1])
    point=(1-2.7/(ratio*cc))/3.7
    text(C.X(cc),C.Y(point)+3,f'r = {ratio}',6,col='#FFFFFF')

E=Ax(316,67,'D','Effect of population growth','90% adult suppression; complete sterility',(2,10),'Low-density daughter multiplier R0')
E.heat(lambda c,R0:population_threshold(c,0,R0,.1),'D',True)
E.axes([(v,str(v)) for v in [2,4,6,8,10]]);bar(E,True)
for ratio,cc in [(5,.7),(10,.65),(20,.3)]:
    E.path(c,1+ratio*c/.9,[2,1])
    point=1+ratio*cc/.9
    if 2<point<10:text(E.X(cc),E.Y(point)+3,f'r = {ratio}',6,col='#FFFFFF')

text(51,17,'A–B: reproductive output in one cohort. C–D: equilibrium population model with maintained effective male ratios.',6.4,col='#50555A')
text(51,6,'All parameters are illustrative. Population panels assume no immigration and do not establish extinction or field release schedules.',6.4,col='#50555A')
renderPDF.drawToFile(D,str(ROOT/'Figure_6.pdf'))
renderSVG.drawToFile(D,str(ROOT/'Figure_6.svg'))
pdf=pdfium.PdfDocument(str(ROOT/'Figure_6.pdf'));page=pdf[0]
page.render(scale=600/72).to_pil().save(ROOT/'Figure_6.png')
page.render(scale=140/72).to_pil().save(ROOT/'Figure_6_preview.png')

assert np.isclose(population_threshold(.5,0,4,.1),5.4)
assert np.isclose(population_threshold(.5,0,10,.1),16.2)
assert np.isinf(population_threshold(.5,1/3.7,4,.1))
print('Created recommended four-panel Figure 6; analytic target checks passed')
