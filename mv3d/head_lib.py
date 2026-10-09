"""ALPHA head as a reusable builder (from rig/blender/alpha_head.py), for the cel-shaded MV scene.

Set head_lib.M (material dict with keys silver, silver2, yellow, teal, dark, rubber, gold, red, glass, iris, pupil, blade)
and head_lib.COL (collection), then call build(parent) -> dict(root, head, jaw, neck, eyes, pose).
"""
import math, os
import bpy, bmesh
from mathutils import Vector, Matrix, Euler
M = None
COL = None
def obj(name, me, m=None, parent=None):
    o = bpy.data.objects.new(name, me); COL.objects.link(o)
    if m: o.data.materials.append(m)
    if parent: o.parent = parent
    return o
def empty(name, loc=(0, 0, 0), parent=None):
    o = bpy.data.objects.new(name, None); COL.objects.link(o); o.location = loc
    if parent: o.parent = parent
    return o
def mods(o, thick=0.012, bevel=0.0025, sub=0):
    if thick:
        s = o.modifiers.new("solid", "SOLIDIFY"); s.thickness = thick; s.offset = -1; s.use_even_offset = True
    if bevel:
        b = o.modifiers.new("bevel", "BEVEL"); b.width = bevel; b.segments = 2; b.limit_method = "ANGLE"; b.angle_limit = math.radians(35)
    if sub:
        d = o.modifiers.new("sub", "SUBSURF"); d.levels = d.render_levels = sub
    for p in o.data.polygons: p.use_smooth = True
    return o

# ------------------------------------------------------------------ the sculpted face surface (head height = 1)
def g(x, y, cx, cy, sx, sy):
    return math.exp(-(((x - cx) / sx) ** 2 + ((y - cy) / sy) ** 2))
def smooth(a, b, v):
    t = max(0.0, min(1.0, (v - a) / (b - a))); return t * t * (3 - 2 * t)
def F(x, y):
    w = 0.40 - 0.21 * smooth(-0.06, -0.48, y) - 0.05 * smooth(0.30, 0.50, y)
    d = 0.30 + 0.03 * smooth(0.2, -0.3, y)
    u = min(1.0, abs(x) / w)
    z = d * math.sqrt(max(0.0, 1 - u * u)) - 0.08
    ax = abs(x)
    z -= 0.050 * g(ax, y, 0.17, 0.075, 0.10, 0.055)                 # eye sockets
    z += 0.022 * g(ax, y, 0.17, 0.155, 0.16, 0.03)                  # brow ridge
    nose_h = 0.095 * smooth(0.11, -0.12, y) * (1 - smooth(-0.13, -0.17, y))
    z += nose_h * math.exp(-(x / (0.032 + 0.03 * smooth(0.0, -0.14, y))) ** 2)
    z += 0.028 * g(ax, y, 0.22, -0.03, 0.09, 0.07)                  # cheekbones
    z += 0.030 * g(x, y, 0.0, -0.232, 0.10, 0.020)                  # upper lip
    z += 0.026 * g(x, y, 0.0, -0.278, 0.09, 0.020)                  # lower lip
    z -= 0.012 * g(x, y, 0.0, -0.212, 0.012, 0.01)                  # philtrum
    z += 0.022 * g(x, y, 0.0, -0.40, 0.07, 0.05)                    # chin
    return z

def resample(poly, step=0.008):
    out = []
    for i in range(len(poly)):
        a, b = Vector(poly[i]), Vector(poly[(i + 1) % len(poly)])
        n = max(1, int((b - a).length / step))
        out += [a.lerp(b, k / n) for k in range(n)]
    return out
def inset(poly, d):
    c = sum((Vector(p) for p in poly), Vector((0, 0))) / len(poly)
    return [tuple(c + (Vector(p) - c) * (1 - d / max(1e-6, (Vector(p) - c).length))) for p in poly]
GRID = 1 / 640                                              # face surface sampling step (about 1 px at 1080p head height)
def inside(px, py, poly):
    c = False; n = len(poly)
    for i in range(n):
        x1, y1 = poly[i]; x2, y2 = poly[(i + 1) % n]
        if (y1 > py) != (y2 > py) and px < (x2 - x1) * (py - y1) / (y2 - y1) + x1: c = not c
    return c
def panel(name, poly, m, parent, thick=0.012, lift=0.0, gap=0.0045, mirror=False, dz=None):
    """Cut a plate out of the face surface: regular grid cells whose centre lies inside the inset outline."""
    pl = inset(poly, gap)
    if mirror: pl = [(-x, y) for x, y in reversed(pl)]
    x0 = math.floor(min(p[0] for p in pl) / GRID); x1 = math.ceil(max(p[0] for p in pl) / GRID)
    y0 = math.floor(min(p[1] for p in pl) / GRID); y1 = math.ceil(max(p[1] for p in pl) / GRID)
    vid, verts, faces = {}, [], []
    def v(i, j):
        k = (i, j)
        if k not in vid:
            x, y = i * GRID, j * GRID
            vid[k] = len(verts); verts.append((x, y, F(x, y) + lift + (dz(x, y) if dz else 0)))
        return vid[k]
    for i in range(x0, x1):
        for j in range(y0, y1):
            if inside((i + 0.5) * GRID, (j + 0.5) * GRID, pl):
                faces.append((v(i, j), v(i + 1, j), v(i + 1, j + 1), v(i, j + 1)))
    me = bpy.data.meshes.new(name); me.from_pydata(verts, [], faces); me.update()
    o = obj(name, me, m, parent); mods(o, thick=thick)
    return o
def both(name, poly, m, parent, **k):
    return [panel(name + "_R", poly, m, parent, **k), panel(name + "_L", poly, m, parent, mirror=True, **k)]

def cyl(name, r, h, m, parent, loc, rot=(0, 0, 0), verts=32, r2=None):
    bm = bmesh.new()
    bmesh.ops.create_cone(bm, cap_ends=True, segments=verts, radius1=r, radius2=r if r2 is None else r2, depth=h)
    me = bpy.data.meshes.new(name); bm.to_mesh(me); bm.free()
    o = obj(name, me, m, parent); o.location = loc; o.rotation_euler = rot; mods(o, thick=0, bevel=min(r, h) * 0.08); return o
def box(name, size, m, parent, loc, rot=(0, 0, 0), bevel=0.003):
    bm = bmesh.new(); bmesh.ops.create_cube(bm, size=1.0)
    for v in bm.verts: v.co = Vector((v.co.x * size[0], v.co.y * size[1], v.co.z * size[2]))
    me = bpy.data.meshes.new(name); bm.to_mesh(me); bm.free()
    o = obj(name, me, m, parent); o.location = loc; o.rotation_euler = rot; mods(o, thick=0, bevel=bevel); return o
def torus(name, R, r, m, parent, loc, rot=(0, 0, 0), scale=(1, 1, 1)):
    bpy.ops.mesh.primitive_torus_add(major_radius=R, minor_radius=r, major_segments=48, minor_segments=10)
    o = bpy.context.object; o.name = name; o.data.materials.append(m)
    o.parent = parent; o.location = loc; o.rotation_euler = rot; o.scale = scale
    for p in o.data.polygons: p.use_smooth = True
    return o
def ellipsoid(name, s, m, parent, loc, rot=(0, 0, 0)):
    bpy.ops.mesh.primitive_uv_sphere_add(radius=1, segments=48, ring_count=24)
    o = bpy.context.object; o.name = name; o.data.materials.append(m); o.parent = parent
    o.location = loc; o.scale = s; o.rotation_euler = rot
    for p in o.data.polygons: p.use_smooth = True
    return o

def arc(name, r, width, th0, th1, m, parent, nu=10, nv=24):
    """Curved plate in eye space: x across the eye, angle th from +z (toward camera) up to +y."""
    bm = bmesh.new(); grid = []
    for i in range(nu + 1):
        x = -width / 2 + width * i / nu; row = []
        for j in range(nv + 1):
            th = th0 + (th1 - th0) * j / nv; taper = 1 - 0.18 * (2 * i / nu - 1) ** 2
            row.append(bm.verts.new((x, r * math.sin(th) * taper, r * math.cos(th))))
        grid.append(row)
    for i in range(nu):
        for j in range(nv): bm.faces.new((grid[i][j], grid[i + 1][j], grid[i + 1][j + 1], grid[i][j + 1]))
    me = bpy.data.meshes.new(name); bm.to_mesh(me); bm.free()
    o = obj(name, me, m, parent); mods(o, thick=0.004, bevel=0.0012); return o


def build(parent=None):
    # ------------------------------------------------------------------ rig hierarchy (Y up in head space -> rotate into Blender Z-up)
    ROOT = empty("ALPHA_root", parent=parent); ROOT.rotation_euler = (math.pi / 2, 0, 0)       # head space: x right, y up, z toward camera
    NECK = empty("neck_yaw", parent=ROOT)
    HEAD = empty("head", parent=NECK)
    JAW = empty("jaw_pivot", (0, -0.225, -0.10), HEAD)                          # hinge axis behind the cheeks
    def to_jaw(o):                                                              # re-parent keeping the world transform
        o.parent = JAW; o.location = Vector(o.location) - Vector(JAW.location); return o

    # --- face panels: drawn as seam lines (like the real head's panel lines); plates fill the regions between ----
    # right-side seams (x > 0) are mirrored; centre seams are given whole. Units: head height = 1.
    SEAMS_R = [
        [(0.068, 0.172), (0.072, 0.50)],                                          # crown plate edge
        [(0.068, 0.185), (0.20, 0.19), (0.335, 0.175)],                           # top of brow plate
        [(0.20, 0.19), (0.25, 0.33), (0.30, 0.179)],                              # forehead "A" recess
        [(0.335, 0.175), (0.35, 0.34), (0.28, 0.50)],                             # temple seam
        [(0.040, 0.172), (0.040, -0.075)],                                        # nose bridge side
        [(0.040, -0.075), (0.068, -0.078), (0.058, -0.152), (0.0, -0.170)],       # nose tip outline
        [(0.040, 0.010), (0.18, 0.012), (0.345, 0.030)],                          # under-eye band, top
        [(0.040, -0.060), (0.20, -0.050), (0.355, -0.085)],                       # under-eye band, bottom
        [(0.335, 0.175), (0.345, 0.03), (0.36, -0.14), (0.31, -0.28)],            # outer cheek seam
        [(0.058, -0.152), (0.12, -0.19), (0.16, -0.232)],                         # nasolabial
        [(0.16, -0.232), (0.20, -0.30), (0.21, -0.42)],                           # jaw-side seam
        [(0.125, -0.243), (0.158, -0.262), (0.165, -0.33), (0.14, -0.40), (0.10, -0.49)],    # jaw boundary (moving part inside)
        [(0.046, -0.300), (0.042, -0.49)],                                        # chin centre plate edge
    ]
    SEAMS_C = [
        [(-0.125, -0.243), (-0.05, -0.207), (-0.014, -0.211), (0, -0.219), (0.014, -0.211), (0.05, -0.207), (0.125, -0.243)],   # upper lip top
        [(-0.125, -0.243), (-0.05, -0.255), (0, -0.252), (0.05, -0.255), (0.125, -0.243)],      # mouth line (lip contact)
        [(-0.125, -0.243), (-0.08, -0.290), (-0.03, -0.305), (0.03, -0.305), (0.08, -0.290), (0.125, -0.243)],   # lower lip bottom
        [(-0.068, 0.172), (0.068, 0.172)], [(-0.040, -0.075), (0.040, -0.075)],                                 # crown bottom, nose bridge bottom
    ]
    EYE_HOLES = [((0.17, 0.075), (0.108, 0.054)), ((-0.17, 0.075), (0.108, 0.054))]
    SEAM_W = 0.0042                                                               # seam gap width
    REGIONS = {  # seed point -> (name, material, lift, on_jaw)
        (0.0, 0.30): ("crown_plate", "silver2", 0.014, False),
        (0.0, 0.05): ("nose_bridge", "silver", 0.008, False), (0.0, -0.11): ("nose_tip", "silver", 0.010, False),
        (0.0, -0.232): ("upper_lip", "teal", 0.006, False), (0.0, -0.278): ("lower_lip", "teal", 0.004, True),
        (0.0, -0.38): ("chin_center", "silver", 0.007, True),
        (0.09, -0.36): ("chin_side_R", "silver2", 0.004, True), (-0.09, -0.36): ("chin_side_L", "silver2", 0.004, True),
        (0.15, 0.16): ("brow_plate_R", "silver2", 0.006, False), (-0.15, 0.16): ("brow_plate_L", "silver2", 0.006, False),
        (0.15, -0.02): ("under_eye_R", "silver2", 0.003, False), (-0.15, -0.02): ("under_eye_L", "silver2", 0.003, False),
        (0.25, 0.25): ("forehead_A_R", "yellow", 0.002, False), (-0.25, 0.25): ("forehead_A_L", "yellow", 0.002, False),
    }
    def build_face():
        xs, ys = -0.42, -0.47; nx, ny = int(0.84 / GRID), int(0.96 / GRID)
        def wdt(y): return 0.40 - 0.21 * smooth(-0.06, -0.48, y) - 0.05 * smooth(0.30, 0.50, y)
        cell = bytearray(nx * ny)                                                 # 0 void, 1 face
        for j in range(ny):
            y = ys + (j + 0.5) * GRID; w = wdt(y) - 0.015
            i0 = max(0, int((-w - xs) / GRID)); i1 = min(nx, int((w - xs) / GRID))
            for i in range(i0, i1): cell[j * nx + i] = 1
        for (cx, cy), (rx, ry) in EYE_HOLES:
            for j in range(int((cy - ry - ys) / GRID), int((cy + ry - ys) / GRID) + 1):
                for i in range(int((cx - rx - xs) / GRID), int((cx + rx - xs) / GRID) + 1):
                    x = xs + (i + 0.5) * GRID; y = ys + (j + 0.5) * GRID
                    if ((x - cx) / rx) ** 2 + ((y - cy) / ry) ** 2 <= 1 and 0 <= i < nx and 0 <= j < ny: cell[j * nx + i] = 0
        def ext(sl, d=0.008):
            sl = [Vector(p) for p in sl]
            a = sl[0] + (sl[0] - sl[1]).normalized() * d; b = sl[-1] + (sl[-1] - sl[-2]).normalized() * d
            return [tuple(a)] + [tuple(p) for p in sl] + [tuple(b)]
        SR = [ext(s) for s in SEAMS_R]; SC = [ext(s) for s in SEAMS_C]
        segs = []
        for sl in SR: segs += [(sl[k], sl[k + 1]) for k in range(len(sl) - 1)]; segs += [((-a[0], a[1]), (-b[0], b[1])) for a, b in zip(sl, sl[1:])]
        for sl in SC: segs += [(sl[k], sl[k + 1]) for k in range(len(sl) - 1)]
        hw = SEAM_W / 2
        for (x1, y1), (x2, y2) in segs:
            dx, dy = x2 - x1, y2 - y1; L2 = dx * dx + dy * dy or 1e-9
            for j in range(int((min(y1, y2) - hw - ys) / GRID) - 1, int((max(y1, y2) + hw - ys) / GRID) + 2):
                for i in range(int((min(x1, x2) - hw - xs) / GRID) - 1, int((max(x1, x2) + hw - xs) / GRID) + 2):
                    if not (0 <= i < nx and 0 <= j < ny): continue
                    x = xs + (i + 0.5) * GRID; y = ys + (j + 0.5) * GRID
                    u = max(0.0, min(1.0, ((x - x1) * dx + (y - y1) * dy) / L2))
                    if (x - x1 - u * dx) ** 2 + (y - y1 - u * dy) ** 2 <= hw * hw: cell[j * nx + i] = 0
        # connected regions
        lab = [0] * (nx * ny); n = 0
        for start in range(nx * ny):
            if cell[start] and not lab[start]:
                n += 1; lab[start] = n; stack = [start]
                while stack:
                    c = stack.pop(); i, j = c % nx, c // nx
                    for d, ok in ((c - 1, i > 0), (c + 1, i < nx - 1), (c - nx, j > 0), (c + nx, j < ny - 1)):
                        if ok and cell[d] and not lab[d]: lab[d] = n; stack.append(d)
        seed = {}
        for (sx, sy), info in REGIONS.items():
            k = lab[int((sy - ys) / GRID) * nx + int((sx - xs) / GRID)]
            if k: seed[k] = info
        regions = {}
        for c, k in enumerate(lab):
            if k: regions.setdefault(k, []).append(c)
        out = []
        for k, cs in regions.items():
            if len(cs) < 60: continue
            name, mname, lift, onjaw = seed.get(k, (f"plate_{k}", "silver" if k % 3 else "silver2", 0.002 * (k % 3), False))
            if os.environ.get("FACE_DEBUG"):
                xs_ = [xs + (c % nx) * GRID for c in cs]; ys_ = [ys + (c // nx) * GRID for c in cs]
                print("REGION", name, mname, len(cs), f"x {min(xs_):.2f}..{max(xs_):.2f} y {min(ys_):.2f}..{max(ys_):.2f}")
            vid, verts, faces = {}, [], []
            def v(i, j):
                if (i, j) not in vid: vid[(i, j)] = len(verts); verts.append([xs + i * GRID, ys + j * GRID])
                return vid[(i, j)]
            for c in cs:
                i, j = c % nx, c // nx
                faces.append((v(i, j), v(i + 1, j), v(i + 1, j + 1), v(i, j + 1)))
            # smooth the stair-stepped outline: relax boundary vertices along the boundary only
            ec = {}
            for f in faces:
                for a_, b_ in zip(f, f[1:] + f[:1]): e = (min(a_, b_), max(a_, b_)); ec[e] = ec.get(e, 0) + 1
            nb = {}
            for (a_, b_), cnt in ec.items():
                if cnt == 1: nb.setdefault(a_, []).append(b_); nb.setdefault(b_, []).append(a_)
            for _ in range(6):
                new = {q: [sum(verts[r][0] for r in nb[q]) / len(nb[q]), sum(verts[r][1] for r in nb[q]) / len(nb[q])] for q in nb if len(nb[q]) == 2}
                for q, (x, y) in new.items(): verts[q] = [verts[q][0] * 0.5 + x * 0.5, verts[q][1] * 0.5 + y * 0.5]
            v3 = [(x, y, F(x, y) + lift) for x, y in verts]
            me = bpy.data.meshes.new(name); me.from_pydata(v3, [], faces); me.update()
            o = obj(name, me, M[mname], HEAD); mods(o, thick=0.016 if "lip" in name else 0.012)
            if onjaw: to_jaw(o)
            out.append(o)
        return out
    FACE = build_face()
    corners = []
    box("chin_slot", (0.006, 0.05, 0.01), M["dark"], JAW, Vector((0, -0.43, F(0, -0.43) + 0.012)) - Vector(JAW.location))
    for s in (-1, 1):                                                            # jaw arms running back to the hinge
        box(f"jaw_arm_{s}", (0.03, 0.03, 0.30), M["dark"], JAW, (s * 0.12, -0.06, 0.12))
    box("mouth_floor", (0.20, 0.012, 0.16), M["dark"], JAW, (0, -0.045, 0.21))
    # --- mouth interior: dark cavity, gear motors, servos, pistons ----------------------------------------
    box("cavity", (0.22, 0.09, 0.20), M["dark"], HEAD, (0, -0.258, 0.04), bevel=0.01)
    for s in (-1, 1):
        cyl(f"gearmotor_{s}", 0.017, 0.05, M["gold"], HEAD, (s * 0.028, -0.252, 0.13), rot=(math.pi / 2, 0, 0), verts=20)
        box(f"servo_{s}", (0.055, 0.045, 0.035), M["red"], HEAD, (s * 0.085, -0.25, 0.10))
        # piston: cylinder on the head aimed at a point on the jaw (Damped Track keeps it attached while the jaw moves)
        p = cyl(f"piston_{s}", 0.008, 0.11, M["silver2"], HEAD, (s * 0.15, -0.17, 0.02), verts=12)
        tgt = empty(f"piston_tgt_{s}", (s * 0.14, -0.06, 0.13), JAW)
        c = p.constraints.new("DAMPED_TRACK"); c.target = tgt; c.track_axis = "TRACK_Z"
    # --- eyes: lens, iris + aperture blades, lens rings, shutter lids, chain eyebrow -----------------------
    EYES = []
    for s in (-1, 1):
        c = Vector((s * 0.17, 0.075, F(0.17, 0.075) + 0.005))
        eye = empty(f"eye_{s}", c, HEAD); eye.rotation_euler = (0, math.radians(s * 14), 0)
        torus(f"socket_{s}", 0.088, 0.010, M["silver2"], eye, (0, 0, 0.004), scale=(1.12, 0.62, 1))
        ellipsoid(f"lens_{s}", (0.090, 0.050, 0.030), M["glass"], eye, (0, 0, 0.0))
        ring1 = torus(f"lensring_{s}", 0.050, 0.004, M["silver"], eye, (0, 0, -0.012), scale=(1, 0.9, 1))
        cyl(f"iris_{s}", 0.040, 0.004, M["iris"], eye, (0, 0, -0.022), verts=40)
        cyl(f"pupil_{s}", 0.011, 0.005, M["pupil"], eye, (0, 0, -0.019), verts=24)
        blades = []
        for k in range(8):                                                        # aperture blades around the pupil
            piv = empty(f"blade_piv_{s}_{k}", (0, 0, -0.017), eye); piv.rotation_euler = (0, 0, k * math.pi / 4)
            b = box(f"blade_{s}_{k}", (0.036, 0.022, 0.0012), M["blade"], piv, (0.034, 0, 0), rot=(0, 0, math.radians(28)), bevel=0.0004)
            blades.append(b)
        cyl(f"eye_back_{s}", 0.075, 0.03, M["dark"], eye, (0, 0, -0.05))
        lid_up, lid_dn = [], []
        for k in range(3):                                                        # upper shutter plates (arcs around the eye's x axis)
            pv = empty(f"lid_up_{s}_{k}", (0, 0, -0.012), eye); lid_up.append(pv)
            arc(f"lidplate_up_{s}_{k}", 0.074 + k * 0.006, 0.19 - k * 0.014, 0.78 + k * 0.10, 1.55 + k * 0.12, M["silver"] if k == 0 else M["silver2"], pv)
        for k in range(2):                                                        # lower shutter plates
            pv = empty(f"lid_dn_{s}_{k}", (0, 0, -0.012), eye); lid_dn.append(pv)
            arc(f"lidplate_dn_{s}_{k}", 0.072 + k * 0.006, 0.18 - k * 0.014, -1.35 - k * 0.12, -0.80 - k * 0.08, M["silver2"], pv)
        brow = empty(f"brow_{s}", (s * 0.18, 0.168, F(0.18, 0.168) + 0.03), HEAD); brow.rotation_euler = (0, math.radians(s * 14), 0)
        links = []
        for k in range(13):
            u = k / 12 * 2 - 1
            x = u * 0.15; y = 0.022 * (1 - u * u) - (0.008 if s * u > 0 else 0)
            ln = box(f"brow_{s}_{k}", (0.022, 0.012, 0.012), M["silver"], brow, (x, y, -0.004 * u * u), rot=(0, 0, -u * 0.32 * s * s), bevel=0.0015)
            links.append(ln)
        EYES.append(dict(blades=blades, ring=ring1, up=lid_up, dn=lid_dn, brow=brow, links=links, s=s))
    # --- helmet: yellow shell, crown ridge, fins, ear turbines --------------------------------------------
    ellipsoid("skull", (0.42, 0.50, 0.34), M["dark"], HEAD, (0, 0.06, -0.24))
    ellipsoid("helmet", (0.45, 0.34, 0.38), M["yellow"], HEAD, (0, 0.27, -0.27))
    box("crown_ridge", (0.13, 0.06, 0.46), M["yellow"], HEAD, (0, 0.50, -0.06), rot=(math.radians(-14), 0, 0), bevel=0.012)
    box("crown_front", (0.15, 0.20, 0.05), M["yellow"], HEAD, (0, 0.43, 0.15), rot=(math.radians(-18), 0, 0), bevel=0.012)
    for s in (-1, 1):
        box(f"helmet_side_{s}", (0.05, 0.30, 0.34), M["yellow"], HEAD, (s * 0.40, 0.24, -0.10), rot=(0, 0, math.radians(-s * 8)), bevel=0.01)
        fin = cyl(f"fin_{s}", 0.045, 0.30, M["yellow"], HEAD, (s * 0.40, 0.50, -0.06), rot=(math.radians(-20), 0, math.radians(-s * 38)), verts=6, r2=0.004)
        ear = empty(f"ear_{s}", (s * 0.445, 0.05, -0.10), HEAD); ear.rotation_euler = (0, math.radians(s * 90), 0)
        torus(f"ear_ring_{s}", 0.105, 0.028, M["yellow"], ear, (0, 0, 0.02))
        cyl(f"ear_housing_{s}", 0.11, 0.06, M["silver2"], ear, (0, 0, -0.02), verts=40)
        fan = empty(f"fan_{s}", (0, 0, 0.02), ear)
        for k in range(14):
            box(f"fanblade_{s}_{k}", (0.075, 0.016, 0.004), M["silver"], fan, (math.cos(k * 2 * math.pi / 14) * 0.05, math.sin(k * 2 * math.pi / 14) * 0.05, 0),
                rot=(math.radians(25), 0, k * 2 * math.pi / 14), bevel=0.001)
        cyl(f"fan_hub_{s}", 0.025, 0.03, M["dark"], ear, (0, 0, 0.03))
        EYES[0 if s < 0 else 1]["fan"] = fan
    # --- neck --------------------------------------------------------------------------------------------
    cyl("neck_core", 0.10, 0.36, M["dark"], NECK, (0, -0.62, -0.18), rot=(math.pi / 2, 0, 0))
    for k in range(8):
        a = k * math.pi / 4
        cyl(f"neck_rod_{k}", 0.012, 0.36, M["silver2"] if k % 2 else M["gold"], NECK, (math.cos(a) * 0.12, -0.62, -0.18 + math.sin(a) * 0.12), rot=(math.pi / 2, 0, 0), verts=12)
    ellipsoid("collar", (0.30, 0.06, 0.22), M["teal"], NECK, (0, -0.80, -0.16))

    # ------------------------------------------------------------------ expressions
    EXPR = {  # brow_in, brow_out (lift), lid_up (0 open .. 1 closed), lid_dn, iris (0 closed .. 1 open), corner (lip-corner plate drop)
        "neutral": (0.0, 0.0, 0.18, 0.10, 0.7, 0.0),
        "tender":  (0.55, 0.0, 0.38, 0.15, 0.45, 0.25),
        "high":    (0.9, 0.7, 0.10, 0.05, 0.85, 0.1),
        "closing": (0.3, 0.0, 0.62, 0.25, 0.6, 0.15),
    }
    def pose(jaw_deg, ex, t=0.0, yaw=0.0, tilt=0.0):
        bi, bo, lu, ld, ir, co = ex
        JAW.rotation_euler = (math.radians(jaw_deg), 0, 0)
        NECK.rotation_euler = (math.radians(tilt), math.radians(yaw), 0)
        for e in EYES:
            s = e["s"]
            for k, pv in enumerate(e["up"]): pv.rotation_euler = (math.radians(58 * lu * (1 - 0.10 * k)), 0, 0)      # + closes downward
            for k, pv in enumerate(e["dn"]): pv.rotation_euler = (math.radians(-40 * ld * (1 - 0.12 * k)), 0, 0)
            for b in e["blades"]: b.location.x = 0.024 + 0.022 * ir
            e["ring"].rotation_euler = (0, 0, t * 0.4 + ir)
            for k, ln in enumerate(e["links"]):
                u = k / 12 * 2 - 1; inner = (1 - s * u) / 2           # 1 at the inner end (toward the nose)
                ln.location.y = 0.022 * (1 - u * u) - (0.008 if s * u > 0 else 0) + 0.020 * bi * inner + 0.018 * bo * (1 - inner)
            e["fan"].rotation_euler = (0, 0, t * 3.0)
        for c in corners: c.location = (0, -0.006 * co, 0)
    return dict(root=ROOT, head=HEAD, jaw=JAW, neck=NECK, eyes=EYES, pose=pose, EXPR=EXPR)
