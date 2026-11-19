# Print the HH07 results (people per walking class, people in heat). Reads only, changes nothing.
# Run: Plugins > Python Console > Show Editor > open > Run

from qgis.core import QgsProject

L = None
for l in QgsProject.instance().mapLayers().values():
    if l.source().split("|")[0].endswith("walk_to_free_green_25832.gpkg"):
        L = l
        break
if L is None:
    raise Exception("New HH07 file (…walk_to_free_green_25832.gpkg) is not loaded")

F = list(L.getFeatures())
P = lambda fs: sum(f["pop_est"] or 0 for f in fs)
T = P(F)
C = ["<= 300 m", "300-600 m", "600-900 m", "> 900 m"]
NAMES = {"A": "free green >= 1 ha", "B": "any free cool place", "C": "doctor / clinic", "D": "pharmacy"}

print("\nFile:", L.source().split("|")[0])
print("Homes: %d   People: %.0f\n" % (len(F), T))
print("%-22s %10s %10s %10s %10s" % ("Destination", *C))
for k in "ABCD":
    row = [100 * P([f for f in F if f["class_" + k] == c]) / T for c in C]
    print("%-22s %9.0f%% %9.0f%% %9.0f%% %9.0f%%" % (k + " " + NAMES[k], *row))

H = [f for f in F if f["heat_class"] in ("Strong heat load", "Extreme heat load")]
print("\nPeople in strong or extreme heat: %.0f" % P(H))
FAR = {"A": C[1:], "B": C[1:], "C": C[2:], "D": C[2:]}
LIM = {"A": "> 300 m", "B": "> 300 m", "C": "> 600 m", "D": "> 600 m"}
for k in "ABCD":
    print("   of them %s from %-20s %.0f" % (LIM[k], NAMES[k], P([f for f in H if f["class_" + k] in FAR[k]])))