import re, math
STR={
'en':{'htitle':'Leshy2 - two-board clamshell (antennas by processor, thin mezzanine)',
 'r1':'Row 1 - MAIN board (ESP32-S3)','r2':'Row 2 - C5 board (co-processor)','r3':'Row 3 - side view + antennas',
 't1':'MAIN - OUTER (front)','t2':'MAIN - INNER','t3':'C5 - INNER','t4':'C5 - OUTER (back)',
 's1':'display + controls','s2':'S3 + all wired radios','s3':'C5 + radios + power','s4':'batteries',
 'disp':'DISPLAY 4.0" + touch','dpad':'D-pad','spk':'SPK','mic':'MIC','jack':'JACK','mezz':'mezzanine','ufl':'u.FL -> outer SMA x5',
 'holder':'plain 2x 18650 holder','holder2':'cells clip in - no lid','pack':'-> BT1 batt conn (3-pin)','master':'master',
 'powerA':'charger + power (buck/LDO/2S-prot)','buses':'buses 138 / PCA','lcddrv':'LCD drv','si':'Si4732+audio',
 'zarea':'component area','zstage':'placed in PCB layout (stage 8)','zmain':'S3 · SA868 · LoRa · CC1101 · GPS','zmain2':'Si4732 + audio · buses · LCD drv','zc5':'C5 · 3x nRF24 · charger / power','zc5b':'IR driver · 74HC139 · PCA9555','lg_silk':'silkscreen (on the PCB)','lg_zone':'component area (stage 8)',
 'xtitle':'Side view (thickness)','front':'FRONT','back':'BACK','outer':'outer','elec':'electronics','mainb':'MAIN board','c5b':'C5 board','batt':'2x 18650','thick':'~36 mm','gap':'gap 11 mm >= nRF ~6',
 'edgettl':'Antennas on the outer faces','allup':'all whips up','depth':'front + back on','nocol':'opposite outer faces -> clear',
 'atitle':'Top-edge interfaces - each on its driving MCU board','acol':['#','interface','band','board'],
 'l_disp':'Display','l_mcu':'MCU','l_rf':'RF','l_batt':'Battery','l_ctrl':'Controls','l_pwr':'Power','l_bus':'Buses','l_io':'I/O','l_mez':'Mezz','l_sma':'SMA / ant',
 'lg_if':'interface (touch)','lg_comp':'component','lg_tx':'TX-live LED','lg_rgb':'RGB status','lg_dir':'port direction','lg_batt2':'battery','antnote':'Antennas sit on the outer faces of both boards (front + back), so the two banks never overlap.'},
'ru':{'htitle':'Leshy2 - двухплатная раковина (антенны по процессору, тонкая межплата)',
 'r1':'Ряд 1 - ГЛАВНАЯ плата (ESP32-S3)','r2':'Ряд 2 - плата C5 (сопроцессор)','r3':'Ряд 3 - вид сбоку + антенны',
 't1':'ГЛАВНАЯ - СНАРУЖИ (перёд)','t2':'ГЛАВНАЯ - ВНУТРИ','t3':'C5 - ВНУТРИ','t4':'C5 - СНАРУЖИ (зад)',
 's1':'дисплей + управление','s2':'S3 + все проводные радио','s3':'C5 + радио + питание','s4':'батареи',
 'disp':'ДИСПЛЕЙ 4.0" + тач','dpad':'D-pad','spk':'ДИН','mic':'МИК','jack':'ДЖЕК','mezz':'межплата','ufl':'u.FL -> внешние SMA x5',
 'holder':'обычный холдер 2x 18650','holder2':'банки защёлкиваются','pack':'-> BT1 разъём батареи (3-пин)','master':'мастер',
 'powerA':'зарядник + питание (buck/LDO/2S)','buses':'шины 138 / PCA','lcddrv':'драйв LCD','si':'Si4732+аудио',
 'zarea':'область компонентов','zstage':'размещается в PCB layout (этап 8)','zmain':'S3 · SA868 · LoRa · CC1101 · GPS','zmain2':'Si4732 + аудио · шины · драйв LCD','zc5':'C5 · 3x nRF24 · зарядник / питание','zc5b':'драйвер IR · 74HC139 · PCA9555','lg_silk':'шелкография (на плате)','lg_zone':'область компонентов (этап 8)',
 'xtitle':'Вид сбоку (толщина)','front':'ПЕРЁД','back':'ЗАД','outer':'снаружи','elec':'электроника','mainb':'ГЛАВНАЯ','c5b':'плата C5','batt':'2x 18650','thick':'~36 мм','gap':'зазор 11 мм >= nRF ~6',
 'edgettl':'Антенны на внешних гранях','allup':'все хлысты вверх','depth':'перёд + зад на','nocol':'противоположных гранях -> не мешают',
 'atitle':'Верхняя кромка - каждый на плате своего МК','acol':['#','интерфейс','диапазон','плата'],
 'lg_if':'интерфейс (контакт)','lg_comp':'компонент','lg_tx':'TX-live LED','lg_rgb':'RGB-статус','lg_dir':'направление порта','lg_batt2':'батарея','antnote':'Антенны — на внешних гранях обеих плат (перёд + зад), поэтому два банка не пересекаются.',
 'l_disp':'Дисплей','l_mcu':'МК','l_rf':'РЧ','l_batt':'Батарея','l_ctrl':'Управл.','l_pwr':'Питание','l_bus':'Шины','l_io':'I/O','l_mez':'Межпл','l_sma':'SMA / ант'}}
ANT=[('1','Wi-Fi 2.4','2.4 GHz','MAIN'),('2','CC1101','315-915','MAIN'),('3','SA868','433/446','MAIN'),
 ('4','LoRa','868/915','MAIN'),('5','Si4732','HF-FM RX','MAIN'),('6','nRF24 #1','2.4 GHz','C5'),
 ('7','nRF24 #2','2.4 GHz','C5'),('8','nRF24 #3','2.4 GHz','C5'),('9','C5 5 GHz','5 GHz','C5'),
 ('*','IR TX/RX','38 kHz','C5 R-side'),('-','GPS','L1','MAIN patch')]
COL={'display':('#dbeafe','#3b82f6'),'mcu':('#fecaca','#dc2626'),'rf':('#fed7aa','#ea580c'),
     'batt':('#bbf7d0','#16a34a'),'ctrl':('#e9d5ff','#7c3aed'),'edge':('#e5e7eb','#6b7280'),
     'stop':('#fca5a5','#b91c1c'),'pwr':('#cffafe','#0891b2'),'bus':('#f5f5f4','#78716c'),
     'mez':('#fbcfe8','#db2777'),'svc':('#ede9fe','#6d28d9'),'io':('#fef9c3','#ca8a04'),'sma':('#d1d5db','#4b5563')}

def gen(lang):
    T=STR[lang]; S=2.7; BW,BH=75,150; HOLES=[(5,5),(70,5),(5,145),(70,145)]; out=[]
    def esc(t): return t.replace('&','and')
    IFACE={'display','ctrl','io','svc','edge','stop','sma','batt'}  # a human contacts these: plug / press / insert / screw / slide / touch
    def box(X,Y,W,H,label,cat,fs=7):
        if cat=='batt': f,st,sw='#dcfce7','#2563eb',2      # battery holder = interface (insert cells), but green so it reads as a battery
        elif cat in IFACE: f,st,sw='#eff6ff','#2563eb',2   # interface -> blue frame
        else: f,st,sw='#f3f4f6','#9ca3af',1.1              # internal component -> grey frame
        s=f'<rect x="{X:.1f}" y="{Y:.1f}" width="{W:.1f}" height="{H:.1f}" fill="{f}" stroke="{st}" stroke-width="{sw}" rx="1.5"/>'
        if label:
            iface=cat in IFACE or cat=='batt'  # interface labels = the PCB silkscreen (mono, teal); component labels = plain
            lc,lf=('#0f766e','ui-monospace,Menlo,monospace') if iface else ('#111','sans-serif')
            s+=f'<text x="{X+W/2:.1f}" y="{Y+H/2+fs*0.35:.1f}" font-size="{fs}" text-anchor="middle" fill="{lc}" font-family="{lf}">{esc(label)}</text>'
        return s
    def txt(X,Y,t,fs=10,col='#111',anc='start',w='normal'):
        return f'<text x="{X:.1f}" y="{Y:.1f}" font-size="{fs}" text-anchor="{anc}" fill="{col}" font-family="sans-serif" font-weight="{w}">{esc(t)}</text>'
    def silk(X,Y,t,fs,anc='middle'):  # a PCB silkscreen label — printed on the board (mono + teal so it reads as on-board legend)
        return f'<text x="{X:.1f}" y="{Y:.1f}" font-size="{fs}" text-anchor="{anc}" fill="#0f766e" font-family="ui-monospace,Menlo,monospace">{esc(t)}</text>'
    def speaker(ox,oy,cx,cy,r,lab):  # round speaker (interface) with a grille + silkscreen label
        X=ox+cx*S; Y=oy+cy*S; R=r*S
        out.append(f'<circle cx="{X:.1f}" cy="{Y:.1f}" r="{R:.1f}" fill="#eff6ff" stroke="#2563eb" stroke-width="2"/>')
        for rr in (0.62,0.34): out.append(f'<circle cx="{X:.1f}" cy="{Y:.1f}" r="{R*rr:.1f}" fill="none" stroke="#93b4f5" stroke-width="0.8"/>')
        out.append(f'<circle cx="{X:.1f}" cy="{Y:.1f}" r="1.4" fill="#2563eb"/>')
        out.append(silk(X,Y+R+4.5,lab,3.6))
    def zone(ox,oy,x,y,w,h,lines):  # a placement AREA for the internal components — exact positions are decided later in PCB layout (stage 8)
        out.append(f'<rect x="{ox+x*S:.1f}" y="{oy+y*S:.1f}" width="{w*S:.1f}" height="{h*S:.1f}" fill="#fafaf9" stroke="#a8a29e" stroke-width="1.2" stroke-dasharray="5 3" rx="2"/>')
        cy0=oy+(y+h/2)*S-(len(lines)-1)*4.3
        for i,l in enumerate(lines): out.append(txt(ox+(x+w/2)*S,cy0+i*8.6,l,5,'#78716c','middle','bold' if i==0 else 'normal'))
    def rgbled(ox,oy,xl,yl,r=2.7):  # RGB status WS2812 — drawn as an R/G/B pie so it never reads as a plain button
        X=ox+xl*S; Y=oy+yl*S
        for i,c in enumerate(('#ef4444','#22c55e','#3b82f6')):
            a0=math.radians(i*120-90); a1=math.radians(i*120+30)
            out.append(f'<path d="M{X:.1f} {Y:.1f} L{X+r*math.cos(a0):.1f} {Y+r*math.sin(a0):.1f} A{r} {r} 0 0 1 {X+r*math.cos(a1):.1f} {Y+r*math.sin(a1):.1f} Z" fill="{c}"/>')
        out.append(f'<circle cx="{X:.1f}" cy="{Y:.1f}" r="{r}" fill="none" stroke="#111" stroke-width="0.6"/>')
    arrows=[]; antc=[]  # direction-arrow bboxes ; antenna centres (mm, board frame) for the mounting-hole check
    def portdir(ox,oy,cx,cy,d,L=6,mir=False):  # red arrow in the margin just outside a port, pointing OUT (from the component); mir mirrors it with the inner face; bbox recorded so the checker confirms it never lands on a label
        if mir: cx=BW-cx; d={'L':'R','R':'L'}.get(d,d)
        X=ox+cx*S; Y=oy+cy*S; dx,dy={'L':(-1,0),'R':(1,0),'U':(0,-1),'D':(0,1)}[d]
        x2=X+dx*L; y2=Y+dy*L
        out.append(f'<path d="M{X:.1f} {Y:.1f} L{x2:.1f} {y2:.1f}" stroke="#dc2626" stroke-width="1.5" marker-end="url(#arr)"/>')
        arrows.append((min(X,x2)-3,min(Y,y2)-3,max(X,x2)+3,max(Y,y2)+3))
    def antface(ox,oy,ants):  # SMA (round, 6.35 mm) mounted ON the outer face, whip up; IR = a small emitter, not an SMA; centers clear of the corner holes, nRF never adjacent
        for lab,cx,isir in ants:
            ax=ox+cx*S; yc=oy+3.5*S
            out.append(f'<path d="M{ax:.1f} {oy-6*S:.1f} l-3 5 M{ax:.1f} {oy-6*S:.1f} l3 5 M{ax:.1f} {oy-6*S:.1f} V{yc:.1f}" stroke="#4b5563" stroke-width="1" fill="none"/>')
            if isir:
                out.append(f'<rect x="{ax-2*S:.1f}" y="{yc-1.8*S:.1f}" width="{4*S:.1f}" height="{3.6*S:.1f}" fill="#fef9c3" stroke="#2563eb" stroke-width="1.4" rx="1"/>')
            else:
                out.append(f'<circle cx="{ax:.1f}" cy="{yc:.1f}" r="{3.175*S:.1f}" fill="#dbeafe" stroke="#2563eb" stroke-width="1.4"/>')
                out.append(f'<circle cx="{ax:.1f}" cy="{yc:.1f}" r="{1.3*S:.1f}" fill="none" stroke="#2563eb" stroke-width="0.7"/>')
            out.append(silk(ax,oy+10*S,lab,4.6)); antc.append((cx,3.5))  # record the SMA/emitter centre for the hole check
    def led(ox,oy,xl,yl,cat,r=1.9):
        f,st=COL[cat]; out.append(f'<circle cx="{ox+xl*S:.1f}" cy="{oy+yl*S:.1f}" r="{r:.1f}" fill="{f}" stroke="{st}" stroke-width="0.8"/>')
    def dpad(ox,oy,cx,cy,rr):
        X=ox+cx*S; Y=oy+cy*S; R=rr*S; f,st='#eff6ff','#2563eb'
        out.append(f'<rect x="{X-R:.1f}" y="{Y-R:.1f}" width="{2*R:.1f}" height="{2*R:.1f}" rx="{R*0.3:.1f}" fill="{f}" stroke="{st}" stroke-width="1.3"/>')
        a=R*0.62
        out.append(f'<path d="M{X:.1f} {Y-a:.1f} l-2.6 3.6 h5.2 z M{X:.1f} {Y+a:.1f} l-2.6 -3.6 h5.2 z M{X-a:.1f} {Y:.1f} l3.6 -2.6 v5.2 z M{X+a:.1f} {Y:.1f} l-3.6 -2.6 v5.2 z" fill="{st}"/>')
        out.append(f'<circle cx="{X:.1f}" cy="{Y:.1f}" r="{R*0.3:.1f}" fill="none" stroke="{st}" stroke-width="1"/>')
        out.append(silk(X,Y+1.6,'OK',4.2))
    def antexit(ox,oy):  # device seen end-on: left = front outer face, right = back outer face; SMA on the two outer faces, whips up
        out.append(txt(ox,oy-8,T['edgettl'],9.5,'#111','start','bold'))
        W=74; Hh=13; y0=oy+26
        out.append(f'<rect x="{ox:.1f}" y="{y0:.1f}" width="{W}" height="{Hh}" fill="#f3f4f6" stroke="#111" stroke-width="1"/>')
        out.append(f'<rect x="{ox+2:.1f}" y="{y0+2:.1f}" width="16" height="{Hh-4}" fill="#dbeafe" stroke="#3b82f6" stroke-width="0.7"/>')
        out.append(f'<rect x="{ox+W-18:.1f}" y="{y0+2:.1f}" width="16" height="{Hh-4}" fill="#bbf7d0" stroke="#16a34a" stroke-width="0.7"/>')
        out.append(f'<line x1="{ox+W/2:.1f}" y1="{y0-2:.1f}" x2="{ox+W/2:.1f}" y2="{y0+Hh+2:.1f}" stroke="#db2777" stroke-width="1" stroke-dasharray="2 2"/>')
        out.append(txt(ox+W/2,y0+Hh+20,T['mezz'],5.5,'#db2777','middle'))
        def ant(axx):
            out.append(f'<rect x="{axx-3:.1f}" y="{y0-3:.1f}" width="6" height="5" fill="#d1d5db" stroke="#4b5563" stroke-width="0.8"/>')
            out.append(f'<path d="M{axx:.1f} {y0-19:.1f} l-3 5 M{axx:.1f} {y0-19:.1f} l3 5 M{axx:.1f} {y0-19:.1f} V{y0-3:.1f}" stroke="#4b5563" stroke-width="1.3" fill="none"/>')
        ant(ox+9); ant(ox+W-9)
        out.append(txt(ox+9,y0+Hh+11,T['front'],6.5,'#1e40af','middle','bold'))
        out.append(txt(ox+W-9,y0+Hh+11,T['back'],6.5,'#166534','middle','bold'))
        out.append(txt(ox,y0+Hh+32,T['allup']+' · '+T['depth']+' '+T['nocol'],6.8,'#555','start'))
    def board(ox,oy,title,sub,tcol,parts,notes,smas,tdy=-17,mir=False):  # mir=True -> inner face: a true back view, mirrored left<->right
        out.append(f'<rect x="{ox:.1f}" y="{oy:.1f}" width="{BW*S:.1f}" height="{BH*S:.1f}" fill="#fafafa" stroke="#111" stroke-width="1.8"/>')
        out.append(txt(ox+BW*S/2,oy+tdy,title,12,tcol,'middle','bold'))
        if sub: out.append(txt(ox+BW*S/2,oy-5,sub,8.5,'#555','middle'))
        for hx,hy in HOLES:
            out.append(f'<circle cx="{ox+hx*S:.1f}" cy="{oy+hy*S:.1f}" r="{2.2*S:.1f}" fill="none" stroke="#6b7280" stroke-width="1.2"/>')
            out.append(f'<circle cx="{ox+hx*S:.1f}" cy="{oy+hy*S:.1f}" r="1.6" fill="#6b7280"/>')
        for x,y,w,h,lab,cat,fs in parts:
            xx=(BW-x-w) if mir else x
            out.append(box(ox+xx*S,oy+y*S,w*S,h*S,lab,cat,fs))
        for x,y,t,fs,c in notes: out.append(txt(ox+((BW-x) if mir else x)*S,oy+y*S,t,fs,c,'middle'))
    W,H=720,1470
    out.append(f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">')
    out.append(f'<rect width="{W}" height="{H}" fill="white"/>')
    out.append('<defs><marker id="ar" markerWidth="8" markerHeight="8" refX="6" refY="3" orient="auto"><path d="M0,0 L6,3 L0,6 Z" fill="#1e40af"/></marker>'
               '<marker id="arr" markerWidth="7" markerHeight="7" refX="5" refY="2.5" orient="auto"><path d="M0,0 L5,2.5 L0,5 Z" fill="#dc2626"/></marker></defs>')
    out.append(txt(30,26,T['htitle'],13.5,'#111','start','bold'))
    col1=45; col2=45+BW*S+55; ry1=110; ry2=ry1+BH*S+95
    out.append(txt(30,ry1-38,T['r1'],11,'#1e40af','start','bold'))
    # MAIN OUTER (front): the 62x99 display + a CENTRED D-pad with BACK/OPT flanking it + the LED row. Encoder, F-keys, PTT/STOP moved to the inner side edges; speaker/mic to the C5 board.
    aout=[(6.5,12,62,99,'','display',6),
     (22,130,6,6,'BACK','ctrl',3.8),(47,130,6,6,'OPT','ctrl',3.8)]
    board(col1,ry1,T['t1'],'','#1e40af',aout,[(37.5,64,T['disp'],7,'#1e40af')],[])
    out.append(f'<rect x="{col1+9.5*S:.1f}" y="{ry1+19*S:.1f}" width="{56*S:.1f}" height="{84*S:.1f}" fill="#cfe3fb" stroke="#3b82f6" stroke-width="0.8" rx="1"/>')  # active area 56x84
    antface(col1,ry1,[('Wi-Fi',13,False),('CC1101',25.5,False),('SA868',38,False),('LoRa',50.5,False),('Si4732',63,False)])
    LEDLAB=['nRF1','nRF2','nRF3','CC1101','SA868','LoRa','IR']  # the 7 discrete-radio TX chains (3x nRF + CC1101 + SA868 + LoRa + IR); WiFi/5G are internal to the ESP modules
    for i,xx in enumerate((8,16.5,25,33.5,42,50.5,59)):
        led(col1,ry1,xx,115,'io',1.7); out.append(silk(col1+xx*S,ry1+121*S,LEDLAB[i],3.2))
    rgbled(col1,ry1,68,115,2.3); out.append(silk(col1+68*S,ry1+121*S,'RGB',3.2))
    dpad(col1,ry1,37.5,133,6)
    # MAIN INNER (mirrored back view): component area; connectors here — jack + 2x Grove on the device-RIGHT edge (jack above Grove), and mic/microSD/RESET/BOOT on the bottom. device-LEFT is kept free (the C5 IR folds onto it)
    ain=[(69,56,6,12.5,T['jack'],'io',4),(69,72,6,9,'Grv','io',4.5),(69,85,6,9,'Grv','io',4.5),
     (23,115,28,7,T['mezz'],'mez',6),
     (35.5,143,4,6,T['mic'],'io',3.2),(18,133,15,15,'microSD','svc',4.5),(42,143,6,6,'RESET','svc',3.4),(50,143,6,6,'BOOT','svc',3.4)]  # mic centred on the bottom edge; microSD left, RESET/BOOT right
    board(col2,ry1,T['t2'],'','#9a3412',ain,[],[],tdy=-27,mir=True)
    zone(col2,ry1,8,14,59,89,[T['zarea'],T['zstage'],T['zmain'],T['zmain2']])
    portdir(col2,ry1,76.5,62,'R',mir=True)   # jack -> main RIGHT edge, above the Grove (device-right; the C5 IR folds onto device-left, so this edge is single-board)
    portdir(col2,ry1,76.5,76.5,'R',mir=True); portdir(col2,ry1,76.5,89.5,'R',mir=True)  # 2x Grove -> device-right edge
    portdir(col2,ry1,37.5,151.5,'D',mir=True); portdir(col2,ry1,25.5,151.5,'D',mir=True); portdir(col2,ry1,45,151.5,'D',mir=True); portdir(col2,ry1,53,151.5,'D',mir=True)  # mic(centre) + microSD + RESET + BOOT down
    out.append(txt(30,ry2-38,T['r2'],11,'#0891b2','start','bold'))
    # C5 INNER (mirrored back view): C5 + 3x nRF (grouped; antennas spread on the outer) + power + IR/CS at real size; USB x2 + master + RST + BOOT on the bottom edge
    binn=[(69,84,6,6,'IR TX','io',3),(69,93,6,6,'IR RX','io',3),
     (24,115,28,7,T['mezz'],'mez',6),  # same device X+Y as the main mezz half so they mate after the fold (check 7)
     (11,143,9,7,'USB J1','io',4),(24,143,9,7,'USB J2','io',4),(37,143,9,5,T['master'],'edge',3.6),(49,143,6,6,'RST','svc',3.6),(58,143,6,6,'BOOT','svc',3.6)]
    board(col1,ry2,T['t3'],'','#0891b2',binn,[],[],tdy=-27,mir=True)
    zone(col1,ry2,5,14,65,68,[T['zarea'],T['zstage'],T['zc5'],T['zc5b']])
    speaker(col1,ry2,37.5,99,8,T['spk'])  # centred on the C5 inner face
    portdir(col1,ry2,76.5,87,'R',mir=True); portdir(col1,ry2,76.5,96,'R',mir=True)  # IR TX/RX fire out the device-right side (DIV-style)
    for px in (15.5,28.5,41.5,52,61): portdir(col1,ry2,px,151.5,'D',mir=True)
    # C5 OUTER (back): 4 SMA + IR on top + a real 2x 18650 holder (40x78) with the two cells (18.6x65 cylinders). BT1 + all electronics are on the inner face.
    # C5 OUTER (back): battery centred, with the encoder above it and the side buttons flanking it (frees the crowded main inner; ergonomic back/side controls)
    # F1/F2 + PTT/STOP are face buttons (like BACK/OPT — pressed from the back face, not side-actuated), inset from the board edge, flanking the battery
    bout=[(17.5,40,40,78,'','batt',7),
     (30,20,15,13,'ENC','ctrl',4.5),(7,55,6,6,'F1','ctrl',3.6),(7,66,6,6,'F2','ctrl',3.6),(62,55,6,6,'PTT','edge',3.6),(62,66,6,6,'STOP','stop',3.4)]
    board(col2,ry2,T['t4'],'','#166534',bout,[(37.5,128,'holder 40 x 78 mm',6,'#166534')],[])
    for i,cxm in enumerate((28,47)):
        out.append(f'<rect x="{col2+(cxm-9.3)*S:.1f}" y="{ry2+44*S:.1f}" width="{18.6*S:.1f}" height="{65*S:.1f}" rx="{9*S:.1f}" fill="#dcfce7" stroke="#16a34a" stroke-width="1.1"/>')
        out.append(txt(col2+cxm*S,ry2+78*S,'18650',6,'#166534','middle','bold'))
    antface(col2,ry2,[('nRF1',13,False),('5GHz',25.5,False),('nRF2',38,False),('nRF3',63,False)])  # 5-slot grid (13/25.5/38/50.5/63) with slot-4 skipped -> the 3 nRF sit at 13/38/63, maximally spread
    # ROW 3: cross-section (left) + antenna table (right)
    ry3=ry2+BH*S+70
    out.append(txt(30,ry3-24,T['r3'],11,'#166534','start','bold'))
    cx=70; cy=ry3; sx=1.15; sz=2.5; rgt=cx+BW*sx+7  # sx = width scale, sz = thickness scale (mm -> px)
    def gl(y,lab):
        out.append(f'<rect x="{cx:.1f}" y="{y:.1f}" width="{BW*sx:.1f}" height="3" fill="#9ca3af" stroke="#111" stroke-width="0.6"/>'); out.append(txt(rgt,y+3,lab,6.8,'#111','start','bold'))
    out.append(txt(cx+BW*sx/2,cy-8,T['front'],8,'#1e40af','middle','bold'))
    y=cy
    dh=3*sz; out.append(box(cx,y,BW*sx,dh,T['disp'],'display',6)); y+=dh
    gl(y,T['mainb']); y+=3
    gaph=11*sz; gt=y; cHm=int(3*sz); cHc=int(6*sz)  # gap 11 mm; main-inner parts ~3 mm (top), C5 nRF ~6 mm (bottom) -> 3+6 < 11, they clear
    for xx in (6,30,54): out.append(box(cx+xx*sx,gt+1.5,10*sx,cHm,'','mcu',5))
    for xx in (18,42,63): out.append(box(cx+xx*sx,gt+gaph-1.5-cHc,10*sx,cHc,'','rf',5))
    out.append(txt(rgt,gt+gaph/2,T['gap'],6.5,'#9a3412','start')); y+=gaph
    gl(y,T['c5b']); y+=3
    bh=18.6*sz; out.append(box(cx+1*sx,y,73*sx,bh,T['batt'],'batt',8)); out.append(txt(rgt,y+bh/2,T['outer'],6.8,'#166534','start')); y+=bh
    out.append(txt(cx+BW*sx/2,y+13,T['back'],8,'#166534','middle','bold'))
    bx0=cx-13
    out.append(f'<line x1="{bx0}" y1="{cy}" x2="{bx0}" y2="{y}" stroke="#111"/>'); out.append(f'<line x1="{bx0-3}" y1="{cy}" x2="{bx0+3}" y2="{cy}" stroke="#111"/>'); out.append(f'<line x1="{bx0-3}" y1="{y}" x2="{bx0+3}" y2="{y}" stroke="#111"/>')
    out.append(f'<text x="{bx0-5:.1f}" y="{(cy+y)/2:.1f}" font-size="8.5" text-anchor="middle" fill="#111" font-family="sans-serif" font-weight="bold" transform="rotate(-90 {bx0-5:.1f} {(cy+y)/2:.1f})">{esc(T["thick"])}</text>')
    out.append(txt(70,ry3+178,T['edgettl'],9.5,'#111','start','bold'))
    out.append(txt(70,ry3+195,T['antnote'],7.5,'#555','start'))
    # antenna table (right of cross-section)
    tx0=330; tw=[26,120,110,130]
    out.append(txt(tx0,ry3-8,T['atitle'],10,'#111','start','bold'))
    hy=ry3+8; cxs=[tx0];
    for w in tw: cxs.append(cxs[-1]+w)
    for k,c in enumerate(T['acol']): out.append(txt(cxs[k]+3,hy,c,8,'#555','start','bold'))
    for i,(n,a,b,brd) in enumerate(ANT):
        ry=hy+14+i*15
        if i%2==0: out.append(f'<rect x="{tx0}" y="{ry-11:.1f}" width="{sum(tw)}" height="14" fill="#f8fafc"/>')
        bc='#dc2626' if brd.startswith('C5') else '#166534'
        out.append(txt(cxs[0]+3,ry,n,8.5,'#111','start','bold')); out.append(txt(cxs[1]+3,ry,a,8.5)); out.append(txt(cxs[2]+3,ry,b,8.5,'#555')); out.append(txt(cxs[3]+3,ry,brd,8.5,bc,'start','bold'))
    # legend: interface (blue) vs component (grey) + indicators + port-direction arrow, two rows
    ly=H-30; lx=30
    for f,st,sw,lab in [('#eff6ff','#2563eb',2,T['lg_if']),('#f3f4f6','#9ca3af',1.1,T['lg_comp']),('#dcfce7','#2563eb',2,T['lg_batt2'])]:
        out.append(f'<rect x="{lx}" y="{ly}" width="15" height="10" fill="{f}" stroke="{st}" stroke-width="{sw}" rx="1.5"/>'); out.append(txt(lx+19,ly+8.5,lab,8.5)); lx+=19+len(lab)*6+26
    out.append(f'<rect x="{lx}" y="{ly}" width="15" height="10" fill="#fafaf9" stroke="#a8a29e" stroke-width="1.2" stroke-dasharray="4 2.5" rx="1.5"/>'); out.append(txt(lx+19,ly+8.5,T['lg_zone'],8.5))
    ly2=ly+16; lx=30
    out.append(f'<circle cx="{lx+7}" cy="{ly2+5}" r="3.2" fill="#fef9c3" stroke="#ca8a04"/>'); out.append(txt(lx+15,ly2+8.5,T['lg_tx'],8.5)); lx+=15+len(T['lg_tx'])*6+24
    for i,c in enumerate(('#ef4444','#22c55e','#3b82f6')):
        a0=math.radians(i*120-90); a1=math.radians(i*120+30)
        out.append(f'<path d="M{lx+7} {ly2+5} L{lx+7+3.2*math.cos(a0):.1f} {ly2+5+3.2*math.sin(a0):.1f} A3.2 3.2 0 0 1 {lx+7+3.2*math.cos(a1):.1f} {ly2+5+3.2*math.sin(a1):.1f} Z" fill="{c}"/>')
    out.append(txt(lx+15,ly2+8.5,T['lg_rgb'],8.5)); lx+=15+len(T['lg_rgb'])*6+24
    out.append(f'<path d="M{lx} {ly2+5} L{lx+11} {ly2+5}" stroke="#dc2626" stroke-width="1.5" marker-end="url(#arr)"/>'); out.append(txt(lx+17,ly2+8.5,T['lg_dir'],8.5)); lx+=17+len(T['lg_dir'])*6+24
    out.append(silk(lx+2,ly2+8.5,'Abc',10,'start')); out.append(txt(lx+26,ly2+8.5,T['lg_silk'],8.5))
    out.append('</svg>'); svg='\n'.join(out)
    rc=[]
    for m in re.finditer(r'<rect\b([^>]*?)/?>',svg):
        a=m.group(1)
        def g(n):
            mm=re.search(n+r'="(-?[\d.]+)"',a); return float(mm.group(1)) if mm else None
        x,yy,w,h=g(' x'),g(' y'),g('width'),g('height')
        if None not in (x,yy,w,h): rc.append((x,yy,x+w,yy+h))
    txb=[]
    for m in re.finditer(r'<text\b([^>]*)>([^<]*)</text>',svg):
        a,c=m.group(1),m.group(2).strip()
        if 'transform=' in a or not c: continue
        def gs(n,d=None):
            mm=re.search(n+r'="([^"]*)"',a); return mm.group(1) if mm else d
        x=float(gs(' x','0')); yy=float(gs(' y','0')); fs=float(gs('font-size','10')); anc=gs('text-anchor','start')
        w=len(c)*fs*0.55; x0=x-w/2 if anc=='middle' else (x-w if anc=='end' else x); txb.append((x0,yy-fs*0.82,x0+w,yy+fs*0.2,c))
    def cont(a,b): return a[0]<=b[0]+0.5 and a[1]<=b[1]+0.5 and a[2]>=b[2]-0.5 and a[3]>=b[3]-0.5
    def ov(a,b,th): return min(a[2],b[2])-max(a[0],b[0])>th and min(a[3],b[3])-max(a[1],b[1])>th
    n=0
    for i in range(len(rc)):
        for j in range(i+1,len(rc)):
            if ov(rc[i],rc[j],3) and not(cont(rc[i],rc[j]) or cont(rc[j],rc[i])): n+=1; print('  RECT',rc[i],rc[j])
    for i in range(len(txb)):
        for j in range(i+1,len(txb)):
            if ov(txb[i],txb[j],2): n+=1; print('  TEXT',repr(txb[i][4]),repr(txb[j][4]))
    # direction arrows must not land on any label (arrow points OUT from the component, into the margin)
    for a in arrows:
        for t in txb:
            if ov(a,t,1): n+=1; print('  ARROW-on-LABEL',repr(t[4]))
    # accessibility check: every interface on an INNER face must sit at a board edge (a buried connector/switch/button can't reach the case slot)
    def near_edge(x,y,w,h,m=8): return x<=m or y<=m or (x+w)>=BW-m or (y+h)>=BH-m
    for parts,name in [(ain,'MAIN-inner'),(binn,'C5-inner')]:
        for x,y,w,h,lab,cat,fs in parts:
            if cat in IFACE and lab!=T['spk'] and not near_edge(x,y,w,h): n+=1; print('  ACCESS',name,repr(lab),'- interface buried, not at an edge')
    # cross-board (clamshell) conflict: the C5 board folds X-MIRRORED onto the main board -- device_X of a C5 part = BW - part_x, so its interval [x,x+w] flips to [BW-x-w, BW-x].
    # A C5 RIGHT-edge exit therefore lands on the device's LEFT edge, sharing that case-slot band with a main LEFT-edge exit (spec 2a / check 6).
    #   SIDE edges (L/R): both exits fire into the narrow ~11 mm gap window -> overlap is HARD (counted). BOTTOM edge: the two boards' exits sit ~11 mm apart in depth on the ~36 mm-deep bottom face -> overlap is allowed via staggered cutouts (reported as info, not counted). ONLY the round speaker is a forward grille (exempt); the mic exits the bottom edge and is a normal port.
    def dev_exits(parts,flip):
        side,bot=[],[]
        for x,y,w,h,lab,cat,fs in parts:
            if cat not in IFACE or lab==T['spk']: continue  # interfaces only; the round speaker is a forward grille (exempt); the mic now exits the bottom edge, so it is a normal edge part
            dx0,dx1=(BW-(x+w),BW-x) if flip else (x,x+w)                  # fold C5 into the device frame (interval inversion)
            if (y+h)>=BH-8: bot.append((dx0,dx1,lab))                     # bottom-edge exit -> compare on X
            else:
                s='L' if dx0<=8 else ('R' if dx1>=BW-8 else None)
                if s: side.append((s,y,y+h,lab))                          # side-edge exit -> compare on Y
        return side,bot
    ms,mb=dev_exits(ain,False); cs,cb=dev_exits(binn,True)  # device frame = main board; C5 folds X-mirrored
    for s1,ya0,ya1,la in ms:                                # HARD: two side exits fight for the same narrow gap window
        for s2,yb0,yb1,lb in cs:
            if s1==s2 and min(ya1,yb1)-max(ya0,yb0)>1: n+=1; print('  CROSS-BOARD(side)',s1,'MAIN',repr(la),'vs C5',repr(lb),'- folds onto the same case slot, Y-overlap')
    for xa0,xa1,la in mb:                                   # SOFT/info: bottom exits are depth-staggered, allowed; report so the PCB gives each its own staggered cutout
        for xb0,xb1,lb in cb:
            if min(xa1,xb1)-max(xa0,xb0)>1: print('  cross-board(bottom, ok via ~11mm depth-stagger): MAIN',repr(la),'vs C5',repr(lb),'- give each its own cutout')
    # no part may overlap a corner M2.5 mounting hole (part boxes + the antenna SMA / emitters drawn by antface)
    for parts,name in [(aout,'MAIN-out'),(ain,'MAIN-in'),(binn,'C5-in'),(bout,'C5-out')]:
        for x,y,w,h,lab,cat,fs in parts:
            for hx,hy in HOLES:
                if x<hx+2.6 and x+w>hx-2.6 and y<hy+2.6 and y+h>hy-2.6: n+=1; print('  HOLE-HIT',name,repr(lab))
    for cx,cy in antc:
        for hx,hy in HOLES:
            if math.hypot(cx-hx,cy-hy)<3.175+2.6: n+=1; print('  HOLE-HIT antenna @x=',cx)
    # mezzanine mate (check 7): the two board-to-board halves must land on the SAME device X and Y after the fold, else they cannot connect
    def mezz_dev(parts,flip):
        for x,y,w,h,lab,cat,fs in parts:
            if cat=='mez': return (BW-(x+w),BW-x,y,y+h) if flip else (x,x+w,y,y+h)
    md_a,md_c=mezz_dev(ain,False),mezz_dev(binn,True)
    if md_a and md_c and any(abs(a-b)>0.5 for a,b in zip(md_a,md_c)): n+=1; print('  MEZZ-MATE main',md_a,'vs C5',md_c,'- halves misaligned after the fold')
    # mezzanine gap check: the cross-section gap must clear the two boards' opposing inner parts (main ~3 mm + C5 nRF ~6 mm) <= 11 mm
    GAP,H_MAIN,H_C5=11,3,6
    if H_MAIN+H_C5>GAP: n+=1; print('  GAP',H_MAIN,'+',H_C5,'>',GAP)
    return svg,n
import os
DST=os.path.dirname(os.path.abspath(__file__))+'/'  # write the SVGs next to this script (docs/img/)
for lang in ('en','ru'):
    svg,n=gen(lang)
    if n: raise SystemExit(f'{lang}: {n} check failure(s) -- render NOT written')  # gate: never ship a render that fails a check (spec 8)
    open(DST+f'layout-clamshell.{lang}.svg','w').write(svg); print(lang,'overlaps=',n)
print('ok')
