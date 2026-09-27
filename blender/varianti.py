# Varianti con meno pezzi: unisce moduli V7 già tarati eliminando i giunti interni.
# In Blender (Text Editor, Alt+P) oppure da riga di comando, dalla cartella "Supporto per Tablet":
#   blender -b blender/supporto_22cm.blend --python blender/varianti.py            -> STL + dati/varianti.json
#   blender -b blender/supporto_22cm.blend --python blender/varianti.py -- --salva -> salva anche il .blend
# I pezzi si uniscono nella posa di montaggio (scena Montaggio, collezione Standard_9_pezzi).
# Il gioco dei Double Jigsaw (0,15 mm per lato, 0,20 mm in battuta) lascerebbe due gusci separati:
# per ogni giunto interno si aggiunge l'unione di (A spostato di d) ∩ (B spostato di -d) su 26
# direzioni, che riempie solo le fessure fra i due pezzi e non sporge dalle superfici a filo.
# Risultato: collezione Montaggio > Varianti (esclusa dalla vista, una sottocollezione per pezzo)
# e Stampa > Varianti_stampa (orientati come gli STL, appoggiati su Z=0).
import bpy, bmesh, json, os, sys
from mathutils import Matrix, Vector

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(bpy.data.filepath)))
SALVA = '--salva' in sys.argv
D = 0.35  # spostamento per chiudere il gioco: 2 × 0,35 = 0,70 mm > gioco massimo

VARIANTI = [
    # sigla, pezzi uniti (il primo dà il nome), giunti interni, etichetta, file
    ('A03', ['S03', 'A01', 'A02'], ['G07', 'G08'], 'Appoggio unico', 'A03_appoggio_unico_x1.stl'),
    ('S04', ['S02', 'S03', 'A01', 'A02'], ['G06', 'G07', 'G08'], 'Testa unica', 'S04_testa_unica_x1.stl'),
    ('S05', ['S01', 'S02', 'S03', 'A01', 'A02'], ['G05', 'G06', 'G07', 'G08'], 'Schienale unico', 'S05_schienale_unico_x1.stl'),
    ('B06', ['B03', 'B01'], ['G01'], 'Raccordo con piede anteriore', 'B06_raccordo_con_piede_x1.stl'),
]
GIUNTI = {'G01': ('B03', 'B01'), 'G05': ('S01', 'S02'), 'G06': ('S02', 'S03'), 'G07': ('S03', 'A01'), 'G08': ('S03', 'A02')}
# rotazione di stampa (righe): come S0x/B03, su un fianco con la X del montaggio in alto
ROT = Matrix(((0, 0, -1), (0, 1, 0), (1, 0, 0)))

mont, stampa = bpy.data.scenes['Montaggio'], bpy.data.scenes['Stampa']

def pezzo(pid):
    return next(o for o in mont.objects if o.name.startswith(pid + '_') and o.type == 'MESH')

def collezione(parent, nome, tag='COLOR_06'):
    c = bpy.data.collections.get(nome) or bpy.data.collections.new(nome)
    if c.name not in parent.children: parent.children.link(c)
    c.color_tag = tag
    return c

def svuota(c):
    for ch in list(c.children):
        svuota(ch); bpy.data.collections.remove(ch)
    for o in list(c.objects):
        me = o.data; bpy.data.objects.remove(o, do_unlink=True)
        if me and me.users == 0: bpy.data.meshes.remove(me)

var_m = collezione(mont.collection, 'Varianti'); svuota(var_m)
var_s = collezione(stampa.collection, 'Varianti_stampa'); svuota(var_s)
lavoro = collezione(mont.collection, '_lavoro')

def copia(pid, nome, off=Vector()):
    s = pezzo(pid); o = s.copy(); o.data = s.data.copy(); o.name = nome
    o.data.transform(Matrix.Translation(off) @ s.matrix_world); o.matrix_world = Matrix.Identity(4)
    lavoro.objects.link(o); return o

def boolean(a, b, op):
    m = a.modifiers.new('b', 'BOOLEAN'); m.operation = op; m.object = b
    try: m.solver = 'MANIFOLD'
    except TypeError: m.solver = 'EXACT'
    dg = bpy.context.evaluated_depsgraph_get()
    me = bpy.data.meshes.new_from_object(a.evaluated_get(dg), preserve_all_data_layers=True, depsgraph=dg)
    a.modifiers.remove(m); old = a.data; a.data = me; bpy.data.meshes.remove(old)

def elimina(o):
    me = o.data; bpy.data.objects.remove(o, do_unlink=True)
    if me.users == 0: bpy.data.meshes.remove(me)

def scrivi_stl(me, path, nome):
    import struct
    me.calc_loop_triangles()
    V = me.vertices
    with open(path, 'wb') as f:
        f.write(('Supporto V7 variante ' + nome).encode()[:80].ljust(80, b' '))
        f.write(struct.pack('<I', len(me.loop_triangles)))
        for t in me.loop_triangles:
            f.write(struct.pack('<3f', *t.normal))
            for i in t.vertices: f.write(struct.pack('<3f', *V[i].co))
            f.write(b'\0\0')

def misura(me, M=Matrix.Identity(4)):
    bm = bmesh.new(); bm.from_mesh(me); bm.transform(M)
    vol = bm.calc_volume(signed=True)
    nm = sum(1 for e in bm.edges if not e.is_manifold)
    bm.verts.ensure_lookup_table(); seen = set(); comp = 0
    for v in bm.verts:
        if v.index in seen: continue
        comp += 1; st = [v]
        while st:
            x = st.pop()
            if x.index in seen: continue
            seen.add(x.index); st.extend(e.other_vert(x) for e in x.link_edges)
    z0 = min(v.co.z for v in bm.verts)
    # sbalzi oltre 45° non appoggiati sul piatto (mm²)
    sb = sum(f.calc_area() for f in bm.faces if f.normal.z < -0.7071 and f.calc_center_median().z > z0 + 0.3)
    b = [(min(v.co[i] for v in bm.verts), max(v.co[i] for v in bm.verts)) for i in range(3)]
    bm.free()
    return dict(volume=vol, nonmanifold=nm, componenti=comp, sbalzi=sb, bounds=b, dims=[b[i][1] - b[i][0] for i in range(3)])

def misura_obj(o, M=Matrix.Identity(4)):
    return misura(o.data, M @ o.matrix_world)

dirs = [Vector((x, y, z)).normalized() * D for x in (-1, 0, 1) for y in (-1, 0, 1) for z in (-1, 0, 1) if (x, y, z) != (0, 0, 0)]
os.makedirs(os.path.join(ROOT, 'stl', 'varianti'), exist_ok=True)
out, x_stampa = {}, 0.0
for vid, pezzi, giunti, etichetta, nome_file in VARIANTI:
    nome = nome_file.replace('_x1.stl', '')
    base = copia(pezzi[0], nome)
    for p in pezzi[1:]:
        o = copia(p, 'tmp'); boolean(base, o, 'UNION'); elimina(o)
    for g in giunti:
        a, b = GIUNTI[g]
        for d in dirs:
            fa = copia(a, 'tmp_a', d); fb = copia(b, 'tmp_b', -d)
            boolean(fa, fb, 'INTERSECT'); elimina(fb)
            if len(fa.data.polygons): boolean(base, fa, 'UNION')
            elimina(fa)
    base.data.name = base.name
    # un solo colore: è un unico pezzo da stampare (gruppo del primo pezzo, A03 resta arancione)
    mat = bpy.data.materials.get({'A03': 'Appoggio', 'B06': 'Raccordo'}.get(vid, 'Schienale')) or bpy.data.materials['Schienale']
    base.data.materials.clear(); base.data.materials.append(mat)
    for f in base.data.polygons: f.material_index = 0
    lavoro.objects.unlink(base); collezione(var_m, nome).objects.link(base)
    m = misura_obj(base)
    somma = sum(misura_obj(pezzo(p))['volume'] for p in pezzi)
    ref = [(min(misura_obj(pezzo(p))['bounds'][i][0] for p in pezzi), max(misura_obj(pezzo(p))['bounds'][i][1] for p in pezzi)) for i in range(3)]
    sporge = max(max(ref[i][0] - m['bounds'][i][0], m['bounds'][i][1] - ref[i][1]) for i in range(3))
    R = ROT.to_4x4()
    st = misura_obj(base, R)
    sb_prima = sum(misura_obj(pezzo(p), R if p != 'B01' else Matrix.Identity(4))['sbalzi'] for p in pezzi)
    # copia di stampa: ruotata, su Z=0, in fila davanti ai moduli (Base 0, Schienale -260, Appoggio -520)
    ps = base.copy(); ps.data = base.data.copy(); ps.name = ps.data.name = nome + '_stampa'
    ps.data.transform(R); mn = [min(v.co[i] for v in ps.data.vertices) for i in range(3)]
    ps.data.transform(Matrix.Translation(Vector(mn) * -1)); ps.location = (x_stampa, -820, 0)
    x_stampa += st['dims'][0] + 40
    var_s.objects.link(ps)
    # STL della copia di stampa (in millimetri, origine sul piatto), scritto a mano:
    # l'esportatore di Blender dipende dalla selezione e dalla scena attiva
    scrivi_stl(ps.data, os.path.join(ROOT, 'stl', 'varianti', nome_file), nome)
    out[vid] = dict(pezzi=pezzi, giunti_eliminati=giunti, label=etichetta, file='stl/varianti/' + nome_file,
                    volume=round(m['volume'], 1), volume_pezzi=round(somma, 1), riempimento_mm3=round(m['volume'] - somma, 1),
                    componenti=m['componenti'], nonmanifold=m['nonmanifold'], sporgenza_mm=round(sporge, 3),
                    dimensions_mm=[round(x, 3) for x in st['dims']], bounds=[[round(a, 3), round(b, 3)] for a, b in m['bounds']],
                    sbalzi_mm2=round(st['sbalzi']), sbalzi_pezzi_separati_mm2=round(sb_prima))
    print('VARIANTE', vid, json.dumps(out[vid]))

bpy.data.collections.remove(lavoro)
# le varianti restano fuori dalla vista: si accendono dall'Outliner
for vl in mont.view_layers:
    vl.layer_collection.children['Varianti'].exclude = True
with open(os.path.join(ROOT, 'dati', 'varianti.json'), 'w', encoding='utf-8') as f:
    json.dump(out, f, indent=1, ensure_ascii=False)
if SALVA:
    bpy.ops.wm.save_mainfile()
