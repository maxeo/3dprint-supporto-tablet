# Nervature da schiacciare (G015CR) sui lobi maschi dei Double Jigsaw V7.
# In Blender (Text Editor, Alt+P) oppure da riga di comando, dalla cartella "Supporto per Tablet":
#   blender -b blender/supporto_22cm.blend --python blender/nervature.py            -> prova, non modifica nulla
#   blender -b blender/supporto_22cm.blend --python blender/nervature.py -- --applica [--salva]
# Stessi parametri dei provini prove/tolleranze/V7_G015CR_*: 3 nervature per lobo (punta e fianchi),
# mezzo tondo Ø0,8 mm che sporge 0,25 mm (0,10 mm di interferenza sul gioco di 0,15), 5,3 mm pieni
# più 1,5 mm di invito. Per ogni lobo maschio si provano le due estremità e si tiene quella che,
# sfilando il giunto, tocca la sede solo negli ultimi PRESA_MAX mm e non tocca altri pezzi.
# Con --applica: unione ai moduli della scena Montaggio, copie Stampa rigenerate, STL in
# stl/pezzi_singoli, dati/nervature.json. Dopo, rigenerare le varianti con varianti.py.
import bpy, bmesh, json, math, os, struct, sys
from mathutils import Matrix, Vector
from mathutils.bvhtree import BVHTree

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(bpy.data.filepath)))
APPLICA = '--applica' in sys.argv or globals().get('APPLICA', False)
SALVA = '--salva' in sys.argv or globals().get('SALVA', False)
SPEC = json.load(open(os.path.join(ROOT, 'dati', 'specifiche_geometriche.json'), encoding='utf-8'))

R_LOBO, R_NERV, SPORGE = 2.949, 0.4, 0.25
RC_PIENO = R_LOBO + SPORGE - R_NERV     # centro della nervatura: sporge 0,25 mm dal lobo
RC_SEPOLTO = R_LOBO - 0.1 - R_NERV      # inizio dell'invito: tutta dentro il lobo
PIENO, INVITO, MARGINE = 5.3, 1.5, 0.2  # mm lungo lo scorrimento (X)
PRESA_MAX = 12.0
SEG = 24
PEZZI = ['B01', 'B03', 'B04', 'B05', 'S01', 'S02', 'S03', 'A01', 'A02']
ROT = Matrix(((0, 0, -1), (0, 1, 0), (1, 0, 0)))  # rotazione di stampa dei pezzi su un fianco
PIATTI = ('B01', 'B04', 'B05')

def mont(pid):
    return next(o for c in ('Base_montaggio', 'Schienale_montaggio', 'Appoggio_montaggio')
                for o in bpy.data.collections[c].objects if o.name.startswith(pid + '_'))

def giunto(J):
    # il gruppo arancione è inclinato: y = y_diritto - k (z - 220); si lavora nel profilo diritto
    J = dict(J); J['k'] = -J.get('shear_y_per_z', 0.0); J['piv'] = J.get('shear_pivot_z', 220)
    return J

def to_nu(p, J):
    y = p[1] - J['k'] * (p[2] - J['piv'])
    q = {1: y, 2: p[2]}
    return q[J['axis']], q[3 - J['axis']]

def from_nu(n, u, x, J):
    q = {J['axis']: n, 3 - J['axis']: u}
    return (x, q[1] + J['k'] * (q[2] - J['piv']), q[2])

def sezione_x(o, x, passo=0.05):
    bm = bmesh.new(); bm.from_mesh(o.data)
    r = bmesh.ops.bisect_plane(bm, geom=bm.verts[:] + bm.edges[:] + bm.faces[:], dist=1e-6, plane_co=(x, 0, 0), plane_no=(1, 0, 0))
    pts = []
    for e in r['geom_cut']:
        if not isinstance(e, bmesh.types.BMEdge): continue
        a, b = e.verts[0].co.copy(), e.verts[1].co.copy(); n = max(1, int((a - b).length / passo))
        pts += [a.lerp(b, i / n) for i in range(n)]
    bm.free(); return pts

def centra_lobo(pts, u0, n0):
    best = (0, n0)
    for i in range(-400, 401):
        n = n0 + i * 0.02
        c = sum(1 for pn, pu in pts if abs(math.hypot(pn - n, pu - u0) - R_LOBO) < 0.02)
        if c > best[0]: best = (c, n)
    return best

_bvh = {}
def bvh(pid, dx=0.0):
    k = (pid, round(dx, 3))
    if k not in _bvh:
        o = mont(pid)
        _bvh[k] = BVHTree.FromPolygons([v.co + Vector((dx, 0, 0)) for v in o.data.vertices], [p.vertices[:] for p in o.data.polygons])
    return _bvh[k]

def dentro(pid, p):
    t, c, o, d = bvh(pid), 0, Vector(p), Vector((0.0123, 0.9871, 0.1597)).normalized()
    while True:
        h = t.ray_cast(o, d)
        if h[0] is None: return c % 2 == 1
        c += 1; o = h[0] + d * 1e-4

def lobi():
    out = []
    for J0 in SPEC['joints']:
        J = giunto(J0)
        for pid in (J['parent'], J['child']):
            for x0, x1 in J['male_x_ranges']:
                xm = (x0 + x1) / 2
                pts = [to_nu(p, J) for p in sezione_x(mont(pid), xm)]
                for u in J['lobe_centers_u_mm']:
                    c, n = centra_lobo(pts, u, J['plane'])
                    if c < 120: continue
                    s = {round(i / 10, 1) for i in range(int((x0 - 15) * 10), int((x1 + 15) * 10)) if dentro(pid, from_nu(n, u, i / 10, J))}
                    lo = hi = round(xm, 1)
                    while round(lo - 0.1, 1) in s: lo = round(lo - 0.1, 1)
                    while round(hi + 0.1, 1) in s: hi = round(hi + 0.1, 1)
                    out.append(dict(giunto=J['id'], pezzo=pid, n=n, u=u, x0=lo, x1=hi, punta=1 if n > J['plane'] else -1))
    return out

def nervatura(L, lato, ang):
    J = giunto(next(j for j in SPEC['joints'] if j['id'] == L['giunto']))
    if lato == 'hi':
        st = [(L['x1'] - MARGINE - PIENO - INVITO, RC_SEPOLTO), (L['x1'] - MARGINE - PIENO, RC_PIENO), (L['x1'] - MARGINE, RC_PIENO)]
    else:
        st = [(L['x0'] + MARGINE, RC_PIENO), (L['x0'] + MARGINE + PIENO, RC_PIENO), (L['x0'] + MARGINE + PIENO + INVITO, RC_SEPOLTO)]
    dn, du = L['punta'] * math.cos(ang), L['punta'] * math.sin(ang)
    V, F = [], []
    for x, rc in st:
        cn, cu = L['n'] + dn * rc, L['u'] + du * rc
        V += [from_nu(cn + R_NERV * math.cos(2 * math.pi * i / SEG), cu + R_NERV * math.sin(2 * math.pi * i / SEG), x, J) for i in range(SEG)]
    for s in range(len(st) - 1):
        F += [(s * SEG + i, s * SEG + (i + 1) % SEG, (s + 1) * SEG + (i + 1) % SEG, (s + 1) * SEG + i) for i in range(SEG)]
    F += [tuple(reversed(range(SEG))), tuple(range((len(st) - 1) * SEG, len(st) * SEG))]
    # facce verso l'esterno: con alcuni assi il verso di costruzione si inverte
    vol = 0.0
    for f in F:
        a = Vector(V[f[0]])
        for i in range(1, len(f) - 1): vol += a.dot(Vector(V[f[i]]).cross(Vector(V[f[i + 1]])))
    if vol < 0: F = [tuple(reversed(f)) for f in F]
    return V, F

def tocca(V, F, pid, dx=0.0):
    return BVHTree.FromPolygons([Vector(v) + Vector((dx, 0, 0)) for v in V], F).overlap(bvh(pid))

def sfilamento(J):
    # verso in cui il figlio si sfila (controllato sui pezzi senza nervature: coincide con entry_sign_x)
    return J['entry_sign_x']

def scegli():
    tenute, prove = [], []
    for L in lobi():
        J = next(j for j in SPEC['joints'] if j['id'] == L['giunto'])
        s = sfilamento(J)
        Q = J['child'] if L['pezzo'] == J['parent'] else J['parent']
        verso = s if L['pezzo'] == J['child'] else -s
        corsa = int(L['x1'] - L['x0']) + 15
        for lato in ('hi', 'lo'):
            ok, presa = True, 0.0
            for ang in (0, math.pi / 2, -math.pi / 2):
                V, F = nervatura(L, lato, ang)
                if not tocca(V, F, Q): ok = False; break
                ds = [0.25 * i for i in range(1, corsa * 4)]
                hit = [d for d in ds if tocca(V, F, Q, verso * d)]
                if hit and (max(hit) > PRESA_MAX or len(hit) != sum(1 for d in ds if d <= max(hit))): ok = False; break
                if any(tocca(V, F, o) for o in PEZZI if o not in (L['pezzo'], Q)): ok = False; break
                presa = max(presa, (max(hit) if hit else 0) + 0.25)
            prove.append(dict(L, lato=lato, ok=ok))
            if ok: tenute.append(dict(L, lato=lato, contro=Q, presa_mm=presa))
    return tenute

def misura(me):
    bm = bmesh.new(); bm.from_mesh(me)
    nm = sum(1 for e in bm.edges if not e.is_manifold)
    seen, comp = set(), 0
    for v in bm.verts:
        if v in seen: continue
        comp += 1; st = [v]; seen.add(v)
        while st:
            x = st.pop()
            for e in x.link_edges:
                w = e.other_vert(x)
                if w not in seen: seen.add(w); st.append(w)
    vol = bm.calc_volume(); bm.free()
    return dict(volume=round(vol, 2), nonmanifold=nm, componenti=comp)

def scrivi_stl(me, path, nome):
    me.calc_loop_triangles(); V = me.vertices
    with open(path, 'wb') as f:
        f.write(nome.encode()[:80].ljust(80, b' ')); f.write(struct.pack('<I', len(me.loop_triangles)))
        for t in me.loop_triangles:
            f.write(struct.pack('<3f', *t.normal))
            for i in t.vertices: f.write(struct.pack('<3f', *V[i].co))
            f.write(b'\0\0')

tenute = scegli()
for t in tenute:
    print('NERVATURE', t['giunto'], t['pezzo'], t['lato'], 'x %.1f-%.1f' % (t['x0'], t['x1']), 'presa ultimi %.2f mm' % t['presa_mm'])
print('lobi con nervature:', len(tenute), 'su', 2 * len(SPEC['joints']), 'attesi')

if APPLICA:
    scena = bpy.data.scenes['Montaggio']
    col = bpy.data.collections.get('Nervature_G015CR') or bpy.data.collections.new('Nervature_G015CR')
    if col.name not in scena.collection.children: scena.collection.children.link(col)
    col.color_tag = 'COLOR_01'
    for o in list(col.objects):
        me = o.data; bpy.data.objects.remove(o); bpy.data.meshes.remove(me)
    mat = bpy.data.materials.get('Nervature') or bpy.data.materials.new('Nervature'); mat.diffuse_color = (0.9, 0.1, 0.1, 1)
    per_pezzo = {}
    for t in tenute:
        for ang in (0, math.pi / 2, -math.pi / 2):
            per_pezzo.setdefault(t['pezzo'], []).append(nervatura(t, t['lato'], ang))
    report = dict(parametri=dict(diametro_mm=2 * R_NERV, sporgenza_mm=SPORGE, interferenza_mm=round(SPORGE - 0.15, 3),
                                 pieno_mm=PIENO, invito_mm=INVITO, per_lobo=3, presa_max_mm=PRESA_MAX),
                  lobi=[{k: (round(v, 3) if isinstance(v, float) else v) for k, v in t.items()} for t in tenute], pezzi={})
    for pid, geoms in per_pezzo.items():
        V, F = [], []
        for v, f in geoms:
            o = len(V); V += v; F += [tuple(i + o for i in ff) for ff in f]
        rm = bpy.data.meshes.new(pid + '_nervature'); rm.from_pydata(V, [], F); rm.validate(); rm.update()
        bm = bmesh.new(); bm.from_mesh(rm); bmesh.ops.recalc_face_normals(bm, faces=bm.faces[:]); bm.to_mesh(rm); bm.free()
        rm.materials.append(mat)
        ro = bpy.data.objects.new(pid + '_nervature', rm); col.objects.link(ro)
        o = mont(pid)
        # triangoli uguali a quelli degli STL: S02 ha poligoni non piani e il booleano li
        # triangolerebbe a modo suo, cambiando il volume lontano dalle nervature
        old = o.data; old.calc_loop_triangles()
        tri = bpy.data.meshes.new(old.name)
        tri.from_pydata([v.co.copy() for v in old.vertices], [], [t.vertices[:] for t in old.loop_triangles])
        for mt in old.materials: tri.materials.append(mt)
        for p, t in zip(tri.polygons, old.loop_triangles): p.material_index = t.material_index
        tri.update(); o.data = tri; bpy.data.meshes.remove(old)
        prima = misura(o.data)
        m = o.modifiers.new('nervature', 'BOOLEAN'); m.operation = 'UNION'; m.object = ro
        try: m.solver = 'MANIFOLD'
        except TypeError: m.solver = 'EXACT'
        dg = bpy.context.evaluated_depsgraph_get()
        me = bpy.data.meshes.new_from_object(o.evaluated_get(dg), preserve_all_data_layers=True, depsgraph=dg)
        o.modifiers.remove(m); old = o.data; o.data = me; bpy.data.meshes.remove(old); me.name = o.name
        # il booleano può lasciare vertici a pochi nm: nell'STL diventerebbero spigoli aperti
        bm = bmesh.new(); bm.from_mesh(me); bmesh.ops.remove_doubles(bm, verts=bm.verts[:], dist=1e-5); bm.to_mesh(me); bm.free()
        dopo = misura(me)
        # copia di stampa e STL: stessa rotazione e centratura degli STL esistenti
        st = bpy.data.objects[o.name + '_stampa']
        R = Matrix.Identity(4) if pid in PIATTI else ROT.to_4x4()
        sm = me.copy(); sm.transform(R); old = st.data; st.data = sm; bpy.data.meshes.remove(old); sm.name = st.name
        stl = sm.copy(); b = [(min(v.co[i] for v in stl.vertices), max(v.co[i] for v in stl.vertices)) for i in range(3)]
        stl.transform(Matrix.Translation((-(b[0][0] + b[0][1]) / 2, -(b[1][0] + b[1][1]) / 2, -b[2][0])))
        f = next(x for x in os.listdir(os.path.join(ROOT, 'stl', 'pezzi_singoli')) if x.startswith(pid + '_'))
        scrivi_stl(stl, os.path.join(ROOT, 'stl', 'pezzi_singoli', f), 'Supporto V7 G015CR ' + pid)
        dims = [round(b[i][1] - b[i][0], 3) for i in range(3)]; bpy.data.meshes.remove(stl)
        report['pezzi'][pid] = dict(file='stl/pezzi_singoli/' + f, prima=prima, dopo=dopo, nervature=len(geoms), dimensions_mm=dims)
        print('PEZZO', pid, prima, '->', dopo, dims)
    # verifica: sovrapposizione fra i pezzi montati (solo le nervature) e sfilamento libero oltre PRESA_MAX
    _bvh.clear(); ver = {}
    for J in SPEC['joints']:
        s = sfilamento(J)
        ver[J['id']] = {str(d): bool(bvh(J['child'], s * d).overlap(bvh(J['parent']))) for d in (0, 5, 12.5, 20, 40)}
    report['verifica_sfilamento'] = ver
    print('VERIFICA', json.dumps(ver))
    for vl in scena.view_layers:
        vl.layer_collection.children['Nervature_G015CR'].exclude = True
    with open(os.path.join(ROOT, 'dati', 'nervature.json'), 'w', encoding='utf-8') as f:
        json.dump(report, f, indent=1, ensure_ascii=False)
    if SALVA:
        bpy.ops.wm.save_mainfile()
