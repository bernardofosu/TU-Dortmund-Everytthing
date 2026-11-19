# HH07 reclass: walking classes 300 / 500 m only (no network rerun, takes seconds)
#   <= 300 m   : WHO indicator, green >= 1 ha within 300 m (Annerstedt van den Bosch et al. 2016)
#   300-500 m  : BfN / UBA green accessibility, 500 m walk (Grunewald et al. 2025)
#   > 500 m    : beyond both
# Overwrites class_A..class_D in the HH07 file from the walking metres (walk_m_A..D). Nothing else changes.
# Afterwards: run HH07_show_A_and_B.py (styles), then HH09 / HH08 again if you need their numbers.
# Run: Plugins > Python Console > Show Editor > open > Run

from qgis.core import QgsProject

CLASSES = ("<= 300 m", "300-500 m", "> 500 m")
def klass(m):
    return CLASSES[0] if m <= 300 else CLASSES[1] if m <= 500 else CLASSES[2]

L = next((l for l in QgsProject.instance().mapLayers().values()
          if l.type() == l.VectorLayer and l.source().split("|")[0].endswith("walk_to_free_green_25832.gpkg")), None)
if L is None:
    raise Exception("HH07 file (...walk_to_free_green_25832.gpkg) not loaded")

idx = {k: (L.fields().indexOf("walk_m_" + k), L.fields().indexOf("class_" + k)) for k in "ABCD"}
L.startEditing()
for f in L.getFeatures():
    for k, (im, ic) in idx.items():
        if im >= 0 and ic >= 0 and f[im] is not None:
            L.changeAttributeValue(f.id(), ic, klass(f[im]))
if not L.commitChanges():
    raise Exception("Could not save: " + "; ".join(L.commitErrors()))

# ---------- numbers ----------
F = list(L.getFeatures())
P = lambda fs: sum(x["pop_est"] or 0 for x in fs)
T = P(F) or 1
NAMES = {"A": "free green >= 1 ha", "B": "any free cool place", "C": "doctor / clinic", "D": "pharmacy"}
print("\n%-24s %10s %10s %10s" % ("Destination", *CLASSES))
for k in "ABCD":
    row = [100 * P([x for x in F if x["class_" + k] == c]) / T for c in CLASSES]
    print("%-24s %9.1f%% %9.1f%% %9.1f%%" % (k + " " + NAMES[k], *row))
H = [x for x in F if x["heat_class"] in ("Strong heat load", "Extreme heat load")]
TH = P(H) or 1
print("\nResidents in strong or extreme heat: %.0f" % P(H))
for k in "ABCD":
    n3 = P([x for x in H if x["class_" + k] == CLASSES[0]])
    n5 = P([x for x in H if x["class_" + k] != CLASSES[2]])
    print("   %-20s <= 300 m: %5.1f %%   <= 500 m: %5.1f %%" % (NAMES[k], 100 * n3 / TH, 100 * n5 / TH))
print("\nDone: class_A..D now <= 300 m / 300-500 m / > 500 m. Next: run HH07_show_A_and_B.py.")