#!/usr/bin/env python3
"""Pravi dmr_all.txt (ID;POZIVNI;Ime) za sve korisnike iz radioid user.csv. Cita ga web strana hotspota."""
import csv, sys
from make_dmrdb import ascii_only

def main(src, dst):
    out = []
    with open(src, encoding='utf-8-sig', errors='replace', newline='') as f:
        head = f.readline(); f.seek(0)
        delim = ';' if head.count(';') > head.count(',') else ','
        rd = csv.reader(f, delimiter=delim)
        first = next(rd, None)
        has_header = first and not first[0].strip().lstrip('#').isdigit()
        iid, ics, ifn = 0, 1, 2
        if has_header:
            names = [c.strip().upper().lstrip('#') for c in first]
            cols = {n: i for i, n in enumerate(names)}
            iid = cols.get('RADIO_ID', cols.get('ID', 0)); ics = cols.get('CALLSIGN', 1); ifn = cols.get('FIRST_NAME', cols.get('NAME', 2))
        def rows():
            if not has_header: yield first
            for r in rd: yield r
        for r in rows():
            try:
                rid = int(r[iid].strip())
            except Exception:
                continue
            cs = ascii_only(r[ics], 8)
            nm = ascii_only(r[ifn].split(' ')[0] if len(r) > ifn else '', 16)
            if cs:
                out.append((rid, cs, nm))
    out.sort()
    with open(dst, 'w', encoding='ascii', errors='replace', newline='\n') as w:
        for rid, cs, nm in out:
            w.write(f"{rid};{cs};{nm}\n")
    print(len(out), "zapisa ->", dst)

if __name__ == '__main__':
    main(sys.argv[1], sys.argv[2])
