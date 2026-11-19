# Hectares per habitat / green class, Innenstadt-Ost (Habitat project). Reads only, changes nothing.
# Uses H05_innenstadt_ost_habitat_patches_dissolve (classes from its legend) and the boundary.
# Run: Plugins > Python Console > Show Editor > open > Run

from qgis.core import QgsProject, QgsGeometry, QgsCategorizedSymbolRenderer

prj = QgsProject.instance()

def find(part):
    for l in prj.mapLayers().values():
        if l.type() == l.VectorLayer and part.lower() in l.name().lower():
            return l
    raise Exception("Layer not found: " + part)

h05 = find("H05_innenstadt_ost_habitat_patches_dissolve")
bnd = find("00_innenstadt_ost_boundary_25832")
district = QgsGeometry.unaryUnion([f.geometry() for f in bnd.getFeatures()]).area() / 10000

r = h05.renderer()
if not isinstance(r, QgsCategorizedSymbolRenderer):
    raise Exception("H05 must be categorized (Woodland, Urban green ...)")
fld = r.classAttribute()
label_of = {str(c.value()): c.label() for c in r.categories()}

ha, parts = {}, {}
for f in h05.getFeatures():
    lab = label_of.get(str(f[fld]), str(f[fld]))
    ha[lab] = ha.get(lab, 0) + f.geometry().area() / 10000
    parts[lab] = parts.get(lab, 0) + max(1, f.geometry().constGet().numGeometries() if f.geometry().isMultipart() else 1)

GREEN = ["Woodland", "Urban green", "Open land", "Wetland", "Bare / pioneer land"]
print("\n=== Hectares per class, Innenstadt-Ost (H05) ===")
print("District area: %.1f ha\n" % district)
print("%-22s %9s %9s" % ("Class", "ha", "% dist."))
for lab in sorted(ha, key=lambda k: -ha[k]):
    print("%-22s %9.1f %8.1f%%" % (lab, ha[lab], 100 * ha[lab] / district))
g = sum(ha.get(k, 0) for k in GREEN)
w = ha.get("Water", 0)
print("-" * 42)
print("%-22s %9.1f %8.1f%%" % ("Green (5 classes)", g, 100 * g / district))
print("%-22s %9.1f %8.1f%%" % ("Green + water", g + w, 100 * (g + w) / district))