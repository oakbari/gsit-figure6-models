"""Recommended four-panel figure combining reproductive and population targets."""
from pathlib import Path
import argparse
import csv
import math
import sys
import numpy as np
from reportlab.graphics.shapes import Drawing, Rect, Line, PolyLine, String, Group, Circle
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
D = Drawing(705, 550)
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
        self.x=x;self.y=y;self.w=215;self.h=160;self.lo,self.hi=ylim;self.ylab=ylab
        text(x-28,y+self.h+30,letter,16,font='Helvetica-Bold')
        for i,title_line in enumerate(title.split('\n')):
            text(x,y+self.h+30-16*i,title_line,14,font='Helvetica-Bold')
        text(x,y+self.h+12,subtitle,10,col='#555B61')

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
            xx=self.X(c);line(xx,self.y,xx,self.y-3);text(xx,self.y-15,f'{c:g}',10,'middle')
        for v,label in ticks:
            yy=self.Y(v);line(self.x-3,yy,self.x,yy);text(self.x-6,yy-3,label,10,'end')
        line(self.x,self.y,self.x+self.w,self.y);line(self.x,self.y,self.x,self.y+self.h)
        text(self.x+self.w/2,self.y-34,'Relative mating competitiveness, c',11,'middle')
        gr=Group(String(0,0,self.ylab,fontName='Helvetica',fontSize=11,textAnchor='middle'))
        gr.transform=(0,1,-1,0,self.x-36,self.y+self.h/2);D.add(gr)

    def path(self,c,v,dash=None):
        valid=np.isfinite(v)&(v>=self.lo)&(v<=self.hi)
        points=[]
        for cc,vv in zip(c[valid],v[valid]):points.extend([self.X(cc),self.Y(vv)])
        if len(points)>3:
            D.add(PolyLine(points,strokeColor=HexColor('#FFFFFF'),strokeWidth=.8,
                           strokeDashArray=dash,fillColor=None))

def bar(ax,log=False):
    x=ax.x+ax.w+12;y=ax.y
    for i in range(150):
        D.add(Rect(x,y+i*ax.h/150,7,ax.h/150+.04,fillColor=color((i+.5)/150),strokeColor=None))
    vals=[(0,'≤1:1'),(1/3,'10:1'),(2/3,'100:1'),(1,'≥1,000:1')] if log else [(0,'0'),(.25,'25'),(.5,'50'),(.75,'75'),(1,'100')]
    for v,label in vals:
        yy=y+v*ax.h;line(x+7,yy,x+10,yy,width=.4);text(x+12,yy-3,label,9)
    if log:
        text(x+3,y+ax.h+7,'Required ratio',9,'middle')
    else:
        text(x+3,y+ax.h+6,'Reduction (%)',9,'middle')

c=np.linspace(.001,1,1500)
A=Ax(55,330,'A','Reproductive reduction','Complete sterility (f = 0)',(0,50),'Released:wild male ratio, r')
A.heat(lambda c,r:100*(1-G(c,r,0)),'A')
A.axes([(v,str(v)) for v in [0,10,20,30,40,50]]);bar(A)
for target,cc in [(.9,.25),(.95,.5)]:
    A.path(c,target/((1-target)*c))
    text(A.X(cc),A.Y(target/((1-target)*cc))+8,f'{int(100*target)}%',10,col='#FFFFFF')

B=Ax(390,330,'B','Reproductive reduction','Male ratio = 10:1',(0,.2),'Relative fertility f (%)')
B.heat(lambda c,f:100*(1-G(c,10,f)),'B')
B.axes([(v,f'{100*v:g}') for v in [0,.05,.1,.15,.2]]);bar(B)
for target,cc in [(.5,.135),(.75,.5)]:
    B.path(c,1-target-target/(10*c))
    text(B.X(cc)+8,B.Y(1-target-target/(10*cc))+(3 if target==.5 else -10),f'{int(100*target)}%',10,col='#FFFFFF')

C=Ax(55,60,'C','99% adult suppression','R0 = 4; 0–1% fertile males',(0,.01),'Fully fertile release males (%)')
C.heat(lambda c,f:population_threshold(c,f,4,.01),'C',True)
C.axes([(v,f'{100*v:g}') for v in [0,.002,.004,.006,.008,.01]]);bar(C,True)
for ratio,flabel in [(10,.005),(50,.0025)]:
    ff=np.linspace(0,.01,300)
    curve_c=2.97/(ratio*(1-3.97*ff));C.path(curve_c,ff,[2,1])
    cc=2.97/(ratio*(1-3.97*flabel))
    text(C.X(cc)+7,C.Y(flabel),f'{ratio}:1',10,col='#FFFFFF')

# Mark the analytic example at the exact upper fertility endpoint.
example_c=.5;example_f=.01
example_r=float(population_threshold(example_c,example_f,4,.01))
px,py=C.X(example_c),C.Y(example_f)
line(px,py,198,194,col='#FFFFFF',width=1.2)
D.add(Circle(px,py,3.4,fillColor=HexColor('#FFFFFF'),strokeColor=HexColor('#151515'),strokeWidth=.8))
D.add(Rect(149,161,117,33,fillColor=HexColor('#FFFFFF'),strokeColor=HexColor('#DBDFE3'),strokeWidth=.5))
text(156,180,f'≈{example_r:.2f}:1',12,font='Helvetica-Bold')
text(156,167,'c = 0.5; 1% fertile',9,col='#45494D')

E=Ax(390,60,'D','99% adult suppression','Complete sterility (f = 0)',(2,10),'Population growth, R0')
E.heat(lambda c,R0:population_threshold(c,0,R0,.01),'D',True)
E.axes([(v,str(v)) for v in [2,4,6,8,10]]);bar(E,True)
for ratio,cc in [(5,.7),(10,.65),(20,.3)]:
    E.path(c,1+ratio*c/.99,[2,1])
    point=1+ratio*cc/.99
    if 2<point<10:text(E.X(cc)-6,E.Y(point)+8,f'{ratio}:1',10,anchor='end',col='#FFFFFF')

renderPDF.drawToFile(D,str(ROOT/'Figure_6.pdf'))
renderSVG.drawToFile(D,str(ROOT/'Figure_6.svg'))
pdf=pdfium.PdfDocument(str(ROOT/'Figure_6.pdf'));page=pdf[0]
page.render(scale=600/72).to_pil().save(ROOT/'Figure_6.png')
page.render(scale=140/72).to_pil().save(ROOT/'Figure_6_preview.png')

assert np.isclose(population_threshold(.5,0,4,.01),5.94)
assert np.isclose(population_threshold(.5,0,10,.01),17.82)
assert np.isinf(population_threshold(.5,1/3.97,4,.01))
print('Created recommended four-panel Figure 6; analytic target checks passed')
