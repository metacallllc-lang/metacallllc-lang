"""Original VEXO motion graphic. Pillow + NumPy; no external image assets."""
from pathlib import Path
import math,json,hashlib,argparse
import numpy as np
from PIL import Image,ImageDraw,ImageFont,ImageFilter,ImageChops

parser=argparse.ArgumentParser();parser.add_argument('--output',type=Path,default=Path(__file__).resolve().parents[1]/'assets');args=parser.parse_args()
OUT=args.output
OUT.mkdir(parents=True,exist_ok=True)
W,H=1200,440;S=1.5;N=64;DURATION=80
CYAN=(80,235,240);PURPLE=(140,107,255);WHITE=(238,247,255)
FONT=Path('C:/Windows/Fonts')
def font(n,bold=False,mono=False):
 name=FONT/('consola.ttf' if mono else 'segoeuib.ttf' if bold else 'segoeui.ttf')
 return ImageFont.truetype(str(name) if name.is_file() else ('DejaVuSansMono.ttf' if mono else 'DejaVuSans-Bold.ttf' if bold else 'DejaVuSans.ttf'),int(n*S))
def xy(p):return tuple(int(v*S) for v in p)
def line(draw,pts,fill,width=1):draw.line([xy(p) for p in pts],fill=fill,width=max(1,int(width*S)),joint='curve')
def text(draw,p,t,n,color=WHITE,bold=False,mono=False):draw.text(xy(p),t,font=font(n,bold,mono),fill=color,stroke_width=0)
def ellipse(draw,b,fill=None,outline=None,width=1):draw.ellipse(xy(b),fill=fill,outline=outline,width=max(1,int(width*S)))
def tracked(draw,p,t,n,spacing=3,color=WHITE):
 x,y=p;f=font(n)
 for char in t:
  draw.text(xy((x,y)),char,font=f,fill=color);x+=draw.textlength(char,font=f)/S+spacing

y,x=np.mgrid[0:int(H*S),0:int(W*S)]
x=x/S;y=y/S
a=np.exp(-(((x-930)/350)**2+((y-180)/220)**2))
b=np.exp(-(((x-240)/560)**2+((y-10)/260)**2))
bg=np.stack([5+8*a+2*b,9+17*a+5*b,19+32*a+12*b],axis=-1)
bg+=np.random.default_rng(42).normal(0,.35,bg.shape)
BACKGROUND=Image.fromarray(np.uint8(np.clip(bg,0,255)),'RGB').convert('RGBA')
static=ImageDraw.Draw(BACKGROUND)
for xx in range(0,W,48):line(static,[(xx,0),(xx,H)],(13,27,43,255),.5)
for yy in range(0,H,48):line(static,[(0,yy),(W,yy)],(13,27,43,255),.5)
# Draw the permanent typography at full resolution; motion never disrupts reading.
tracked(static,(65,38),'VEXO  /  METABOT',13,2.5,(119,169,191))
text(static,(59,80),'VEXO',112,WHITE,True)
tracked(static,(65,218),'AUTONOMOUS COMPANY SYSTEMS',13,2.1,CYAN)
text(static,(64,253),'Building companies that can act.',25,WHITE,True)
text(static,(65,292),'Designed for people to direct, inspect and trust.',18,(154,178,199))
line(static,[(65,356),(1135,356)],(48,69,91),1)
for i,(label,title) in enumerate([('01','THINK'),('02','DELEGATE'),('03','EXECUTE'),('04','VERIFY')]):
 xx=66+i*275
 text(static,(xx,382),label,11,(113,139,162),mono=True)
 tracked(static,(xx+31,376),title,13,1.9,(195,212,230))
 if i<3:line(static,[(xx+157,389),(xx+239,389)],(45,68,90),1)

def project(v,phase):
 X,Y,Z=v
 co,si=math.cos(phase),math.sin(phase)
 X,Z=X*co+Z*si,-X*si+Z*co
 tilt=.24;Y,Z=Y*math.cos(tilt)-Z*math.sin(tilt),Y*math.sin(tilt)+Z*math.cos(tilt)
 scale=1+Z*.0011
 return (939+X*scale,200+Y*scale,Z)

def frame(index):
 phase=2*math.pi*index/N
 im=BACKGROUND.copy();layer=Image.new('RGBA',im.size);g=ImageDraw.Draw(layer)
 # A slowly turning wire globe: an abstract operating system, never fake live telemetry.
 for j in range(8):
  lon=2*math.pi*j/8
  pts=[project((106*math.cos(t)*math.cos(lon),106*math.sin(t),106*math.cos(t)*math.sin(lon)),phase*.5) for t in np.linspace(-math.pi/2,math.pi/2,65)]
  for p,q in zip(pts,pts[1:]):
   z=(p[2]+q[2])/2;v=int(55+105*(z+110)/220)
   line(g,[p[:2],q[:2]],(int(v*.32),int(v*.8),v,150),.8)
 for lat in [-.85,-.45,0,.45,.85]:
  rr=106*math.sqrt(1-lat*lat)
  pts=[project((rr*math.cos(t),106*lat,rr*math.sin(t)),phase*.5) for t in np.linspace(0,2*math.pi,100)]
  for p,q in zip(pts,pts[1:]):line(g,[p[:2],q[:2]],(58,114,158,140),.8)
 # Continuous circulating light, soft enough to preserve readable text.
 glow=Image.new('RGBA',im.size);gd=ImageDraw.Draw(glow)
 ellipse(gd,(827,88,1051,312),outline=(64,213,239,95),width=3)
 glow=glow.filter(ImageFilter.GaussianBlur(18*S));im=Image.alpha_composite(im,glow)
 center=(939,200)
 for offset in [0,math.pi]:
  pts=[(center[0]+130*math.cos(t),center[1]+112*math.sin(t)) for t in np.linspace(phase+offset,phase+offset+.65,28)]
  line(g,pts,CYAN if offset==0 else PURPLE,2)
 # Monogram: a precise vector V and split lower stroke.
 line(g,[(899,172),(929,235),(986,152)],(90,230,244),8)
 line(g,[(912,173),(932,214),(974,154)],(225,249,255),2)
 line(g,[(932,235),(949,235),(989,175)],(140,107,255),3)
 labels=[('CEO',-math.pi/2),('CFO',-math.pi/6),('COO',math.pi/6),('CRO',math.pi/2),('CMO',5*math.pi/6),('CTO',7*math.pi/6)]
 for i,(label,angle) in enumerate(labels):
  nx=939+155*math.cos(angle);ny=200+134*math.sin(angle)
  pulse=.5+.5*math.sin(phase-angle)
  line(g,[(939+111*math.cos(angle),200+98*math.sin(angle)),(nx,ny)],(61,108,143,130),.8)
  g.rounded_rectangle(xy((nx-29,ny-13,nx+29,ny+13)),radius=int(8*S),fill=(11,25,43,255),outline=(50,int(98+90*pulse),int(137+60*pulse),255),width=1)
  text(g,(nx-17,ny-9),label,11,(182,224,239),mono=True)
 # A few faint moving particles and footer pulses; no flashes or strobing.
 rng=np.random.default_rng(17)
 for i in range(33):
  px=float(rng.uniform(720,1170));py=float(rng.uniform(20,340));theta=float(rng.uniform(0,2*math.pi))
  px+=3*math.sin(phase+theta);py+=2*math.cos(phase+theta)
  alpha=int(28+28*(1+math.sin(phase+theta))/2)
  ellipse(g,(px,py,px+1,py+1),fill=(116,180,222,alpha))
 for j in range(3):
  xx=223+j*275+82*((index/N+j/3)%1)
  ellipse(g,(xx-2,387,xx+2,391),fill=CYAN)
 im=Image.alpha_composite(im,layer)
 return im.convert('RGB').resize((W,H),Image.Resampling.LANCZOS)

poster=frame(0);poster.save(OUT/'vexo-company-poster.png',optimize=True)
palette=poster.quantize(colors=256,method=Image.Quantize.MEDIANCUT)
frames=[]
for i in range(N):frames.append(frame(i).quantize(palette=palette,dither=Image.Dither.NONE))
gif=OUT/'vexo-company.gif'
frames[0].save(gif,save_all=True,append_images=frames[1:],duration=DURATION,loop=0,optimize=True,disposal=1)
sheet=Image.new('RGB',(W,3*H))
for j,i in enumerate([0,N//3,2*N//3]):sheet.paste(frame(i),(0,j*H))
sheet.resize((960,1056),Image.Resampling.LANCZOS).save(OUT/'vexo-contact-sheet.png')
check=Image.open(gif);durations=[]
for i in range(check.n_frames):check.seek(i);check.load();durations.append(check.info.get('duration'))
qa={'dimensions':check.size,'frames':check.n_frames,'duration_ms':sum(durations),'loop':check.info.get('loop'),
 'bytes':gif.stat().st_size,'sha256':hashlib.sha256(gif.read_bytes()).hexdigest(),
 'motion_verified':ImageChops.difference(frames[0].convert('RGB'),frames[N//3].convert('RGB')).getbbox() is not None,
 'source':'Original deterministic vector geometry, typography and procedural animation; no third-party image asset.',
 'static_fallback':'vexo-company-poster.png'}
assert qa['frames']==N and qa['loop']==0 and qa['motion_verified'] and qa['bytes']<5_000_000
(OUT/'asset-verification.json').write_text(json.dumps(qa,indent=2),encoding='utf-8')
print(json.dumps(qa))
