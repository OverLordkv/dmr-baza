#!/usr/bin/env python3
"""Pravi dmr_all.txt iz radioid user.csv: SVE kolone (ID;POZIVNI;IME;PREZIME;GRAD;DRZAVA_SAVEZNA;DRZAVA), razdvojene sa ';'.
Ispravno cita navodnike/zareze iz originalnog CSV-a. Cita ga web strana hotspota."""
import csv, sys

def clean(s):
    return ' '.join(str(s).replace(';', ',').split())

def main(src, dst):
    n = 0
    with open(src, encoding='utf-8-sig', errors='replace', newline='') as f, \
         open(dst, 'w', encoding='utf-8', newline='\n') as w:
        head = f.readline(); f.seek(0)
        delim = ';' if head.count(';') > head.count(',') else ','
        rd = csv.reader(f, delimiter=delim)
        first = next(rd, None)
        has_header = first and not first[0].strip().lstrip('#').isdigit()
        iid, ics, ifn, iln, icy, ist, ico = 0, 1, 2, 3, 4, 5, 6
        if has_header:
            cols = {c.strip().upper().lstrip('#'): i for i, c in enumerate(first)}
            iid = cols.get('RADIO_ID', cols.get('ID', 0)); ics = cols.get('CALLSIGN', 1)
            ifn = cols.get('FIRST_NAME', cols.get('NAME', 2)); iln = cols.get('LAST_NAME', -1)
            icy = cols.get('CITY', -1); ist = cols.get('STATE', -1); ico = cols.get('COUNTRY', -1)
        w.write("RADIO_ID;CALLSIGN;FIRST_NAME;LAST_NAME;CITY;STATE;COUNTRY\n")
        def get(r, i):
            return clean(r[i]) if 0 <= i < len(r) else ''
        def rows():
            if not has_header and first: yield first
            for r in rd: yield r
        for r in rows():
            try:
                rid = int(r[iid].strip())
            except Exception:
                continue
            cs = get(r, ics)
            if not cs:
                continue
            w.write(f"{rid};{cs};{get(r, ifn)};{get(r, iln)};{get(r, icy)};{get(r, ist)};{get(r, ico)}\n")
            n += 1
    print(n, "zapisa ->", dst)

if __name__ == '__main__':
    main(sys.argv[1], sys.argv[2])
