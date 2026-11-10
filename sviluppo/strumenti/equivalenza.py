"""Controllo di equivalenza dopo uno spostamento di testo: ogni riga non vuota della skill di prima
deve comparire identica, lo stesso numero di volte, nei file .md della skill di dopo."""
import pathlib,sys,collections
prima,dopo=map(pathlib.Path,sys.argv[1:3])
def righe(c):
    out=collections.Counter(); dove={}
    for p in sorted(c.rglob("*.md")):
        for l in p.read_text(encoding="utf-8").split("\n"):
            if l.strip(): out[l]+=1; dove.setdefault(l,[]).append(str(p.relative_to(c)))
    return out,dove
a,da=righe(prima); b,db=righe(dopo)
perse=[l for l in a if b[l]<a[l]]; nuove=[l for l in b if b[l]>a[l]]
spost=[(l,da[l],db[l]) for l in a if l in b and set(da[l])!=set(db[l]) and len(l)>80]
print("righe di prima: %d, tutte presenti dopo: %s"%(sum(a.values()),"SÌ" if not perse else "NO"))
for l in perse: print("  PERSA/CAMBIATA [%s]: %s"%(da[l][0],l[:110]))
print("\nparagrafi spostati: %d"%len(spost))
for l,x,y in spost: print("  %-28s -> %-32s %s"%(x[0],y[0],l[:60]))
print("\nrighe nuove: %d"%len(nuove))
for l in nuove: print("  [%s] %s"%(db[l][0],l[:150]))
