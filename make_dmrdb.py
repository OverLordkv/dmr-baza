#!/usr/bin/env python3
"""Pravi dmr.bin za hotspot iz radioid.net user.csv (ili DMRIds.dat).

Primeri:
  python make_dmrdb.py user.csv dmr.bin --prefix 220 219 218 293 294 297
  python make_dmrdb.py user.csv dmr.bin --country Serbia Croatia "Bosnia and Herzegovina"
  python make_dmrdb.py DMRIds.dat dmr.bin --prefix 220

--prefix  : prvi cifre DMR ID-a (MCC: 220 Srbija, 219 Hrvatska, 218 BiH, 293 Slovenija,
            294 S. Makedonija, 297 Crna Gora, 222 Italija, 262 Nemacka ...)
--ids     : tekstualni fajl sa ID-ovima (jedan po liniji) koji imaju prioritet (npr. aktivni na TG91)
--max     : najveci broj zapisa; kad se prekoraci, zadrzavaju se prvo --ids, pa redom --prefix
--country : filtriranje po polju COUNTRY (samo za radioid CSV sa zaglavljem)
Bez filtera ide celo - NE preporucuje se (fajl postaje prevelik za fles).
"""
import argparse, csv, struct, sys, unicodedata

MAP = {'đ':'dj','Đ':'Dj','đ':'dj','š':'s','Š':'S','č':'c','Č':'C','ć':'c','Ć':'C','ž':'z','Ž':'Z','ß':'ss','ø':'o','Ø':'O','æ':'ae','Æ':'Ae','ł':'l','Ł':'L'}
CYR = dict(zip('абвгдђежзијклљмнњопрстћуфхцчџш','a b v g d dj e z z i j k l lj m n nj o p r s t c u f h c c dz s'.split()))
CYR['ж']='z'; CYR['з']='z'

def ascii_only(s, n):
    out=[]
    for ch in s:
        if ch in MAP: out.append(MAP[ch]); continue
        low=ch.lower()
        if low in CYR:
            t=CYR[low]; out.append(t.capitalize() if ch!=low else t); continue
        d=unicodedata.normalize('NFKD',ch)
        d=''.join(c for c in d if ord(c)<128 and (c.isalnum() or c in " -.'"))
        out.append(d)
    return ''.join(out).strip()[:n]

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('src'); ap.add_argument('dst')
    ap.add_argument('--prefix',nargs='*',default=[])
    ap.add_argument('--country',nargs='*',default=[])
    ap.add_argument('--ids',default=None)
    ap.add_argument('--max',type=int,default=0)
    a=ap.parse_args()
    recs={}
    with open(a.src,encoding='utf-8-sig',errors='replace',newline='') as f:
        head=f.readline(); f.seek(0)
        delim=';' if head.count(';')>head.count(',') else ','
        rd=csv.reader(f,delimiter=delim)
        first=next(rd,None)
        has_header = first and not first[0].strip().lstrip('#').isdigit()
        cols={}
        if has_header:
            names=[c.strip().upper().lstrip('#') for c in first]
            cols={n:i for i,n in enumerate(names)}
            iid=cols.get('RADIO_ID',cols.get('ID',0)); ics=cols.get('CALLSIGN',1); ifn=cols.get('FIRST_NAME',cols.get('NAME',2)); ico=cols.get('COUNTRY')
        else:
            iid,ics,ifn,ico=0,1,2,None
            rows=[first]
        def rows_iter():
            if not has_header: yield first
            for r in rd: yield r
        for r in rows_iter():
            try:
                rid=int(r[iid].strip())
            except Exception: continue
            if a.prefix and not any(str(rid).startswith(p) for p in a.prefix): continue
            if a.country and ico is not None:
                if r[ico].strip().lower() not in [c.lower() for c in a.country]: continue
            cs=ascii_only(r[ics],8); nm=ascii_only(r[ifn].split(' ')[0] if len(r)>ifn else '',16)
            if cs: recs[rid]=(cs,nm)
    prio=set()
    if a.ids:
        for ln in open(a.ids,encoding='utf-8',errors='replace'):
            t=ln.strip().split(',')[0].split(';')[0].strip()
            if t.isdigit(): prio.add(int(t))
    ids=sorted(recs)
    if a.max and len(ids)>a.max:
        def rank(i):
            if i in prio: return (0,0,i)
            for k,p in enumerate(a.prefix): 
                if str(i).startswith(p): return (1,k,i)
            return (2,0,i)
        ids=sorted(sorted(ids,key=rank)[:a.max])
        print(f'Skraceno na {a.max} zapisa (prioritet: --ids, pa redom --prefix)')
    with open(a.dst,'wb') as o:
        o.write(b'DMRDB001'+struct.pack('<I',len(ids))+b'\0\0\0\0')
        for i in ids:
            cs,nm=recs[i]
            o.write(struct.pack('<I',i)+cs.encode().ljust(8,b'\0')+nm.encode().ljust(16,b'\0'))
    size=16+28*len(ids)
    print(f'{len(ids)} zapisa, {size/1024:.0f} KB -> {a.dst}')
    if size>1200*1024: print('UPOZORENJE: fajl > 1.2 MB, moze da ne stane u SPIFFS (default particija ~1.5 MB).')

if __name__=='__main__':
    main()
