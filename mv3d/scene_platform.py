"""《远去的列车》方向 C 风格测试：三维赛璐珞 + 墨线，黄昏空站台（歌曲 135.4–151.4 秒，L15–L16）。

    EGL_PLATFORM=surfaceless python scene_platform.py -- --frames 0-384 --out out/frames --res 1280x720
    ... --still 200 --out out/still.png

每一帧都是歌曲时间的函数。口型来自转换后的机器人人声分轨（口型_G07.mp3 的下颌曲线 jaw_G07.json）。
"""
import argparse, json, math, os, sys
import bpy
from mathutils import Vector
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import head_lib as HL

argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else sys.argv[1:]
ap = argparse.ArgumentParser()
ap.add_argument("--frames", default=""); ap.add_argument("--still", type=int); ap.add_argument("--out", default="out/frames")
ap.add_argument("--res", default="1280x720"); ap.add_argument("--blend")
A = ap.parse_args(argv)

HERE = os.path.dirname(os.path.abspath(__file__))
FPS = 24
T0 = 135.4                       # song time at frame 0
DUR = 16.0
JAW = json.load(open(os.path.join(HERE, "jaw_G07.json")))   # frames at 24 fps, from song time 137.4
JAW_T0 = 137.4

bpy.ops.wm.read_factory_settings(use_empty=True)
S = bpy.context.scene
COL = S.collection

# ------------------------------------------------------------------ cel materials
def toon(name, base, shade=0.42, mid=0.72, spec=0.0, spec_w=0.0, emit=None, emit_k=0.0, alpha=None, tex=None):
    """Diffuse -> Shader to RGB -> 3-step ramp (shadow / mid / lit) x base colour, + optional hard specular band."""
    m = bpy.data.materials.new(name); m.use_nodes = True; nt = m.node_tree; N = nt.nodes; L = nt.links
    N.clear()
    out = N.new("ShaderNodeOutputMaterial")
    dif = N.new("ShaderNodeBsdfDiffuse"); s2r = N.new("ShaderNodeShaderToRGB")
    ramp = N.new("ShaderNodeValToRGB"); cr = ramp.color_ramp; cr.interpolation = "CONSTANT"
    cr.elements[0].position = 0.0; cr.elements[0].color = (shade, shade, shade, 1)
    cr.elements[1].position = 0.10; cr.elements[1].color = (mid, mid, mid, 1)
    e = cr.elements.new(0.42); e.color = (1, 1, 1, 1)
    L.new(dif.outputs[0], s2r.inputs[0]); L.new(s2r.outputs["Color"], ramp.inputs[0])
    mul = N.new("ShaderNodeMix"); mul.data_type = "RGBA"; mul.blend_type = "MULTIPLY"; mul.inputs[0].default_value = 1.0
    L.new(ramp.outputs["Color"], mul.inputs[6])
    if tex:
        it = N.new("ShaderNodeTexImage"); it.image = bpy.data.images.load(tex); L.new(it.outputs["Color"], mul.inputs[7])
    else:
        mul.inputs[7].default_value = (*base, 1)
    col = mul.outputs[2]
    if spec:
        gl = N.new("ShaderNodeBsdfGlossy"); gl.inputs["Roughness"].default_value = 0.25
        s2 = N.new("ShaderNodeShaderToRGB"); r2 = N.new("ShaderNodeValToRGB"); r2.color_ramp.interpolation = "CONSTANT"
        r2.color_ramp.elements[0].color = (0, 0, 0, 1); r2.color_ramp.elements[1].position = 1 - spec_w; r2.color_ramp.elements[1].color = (spec, spec, spec, 1)
        L.new(gl.outputs[0], s2.inputs[0]); L.new(s2.outputs["Color"], r2.inputs[0])
        add = N.new("ShaderNodeMix"); add.data_type = "RGBA"; add.blend_type = "ADD"; add.inputs[0].default_value = 1.0
        L.new(col, add.inputs[6]); L.new(r2.outputs["Color"], add.inputs[7]); col = add.outputs[2]
    em = N.new("ShaderNodeEmission"); L.new(col, em.inputs["Color"]); em.inputs["Strength"].default_value = 1.0
    sh = em.outputs[0]
    if emit:
        e2 = N.new("ShaderNodeEmission"); e2.inputs["Color"].default_value = (*emit, 1); e2.inputs["Strength"].default_value = emit_k
        ad = N.new("ShaderNodeAddShader"); L.new(sh, ad.inputs[0]); L.new(e2.outputs[0], ad.inputs[1]); sh = ad.outputs[0]
    if alpha is not None:
        tr = N.new("ShaderNodeBsdfTransparent"); mx = N.new("ShaderNodeMixShader"); mx.inputs[0].default_value = alpha
        L.new(tr.outputs[0], mx.inputs[1]); L.new(sh, mx.inputs[2]); sh = mx.outputs[0]
        m.surface_render_method = "BLENDED"
    L.new(sh, out.inputs["Surface"])
    return m
def flat(name, color, k=1.0):
    m = bpy.data.materials.new(name); m.use_nodes = True; N = m.node_tree.nodes; N.clear()
    o = N.new("ShaderNodeOutputMaterial"); e = N.new("ShaderNodeEmission"); e.inputs["Color"].default_value = (*color, 1); e.inputs["Strength"].default_value = k
    m.node_tree.links.new(e.outputs[0], o.inputs["Surface"]); return m

YEL = (0.98, 0.74, 0.05); TEAL = (0.08, 0.62, 0.66); SIL = (0.74, 0.76, 0.80)
M = {
    "silver": toon("silver", SIL, 0.40, 0.70, spec=0.55, spec_w=0.12), "silver2": toon("silver2", (0.60, 0.62, 0.66), 0.38, 0.68, spec=0.35, spec_w=0.10),
    "yellow": toon("yellow", YEL, 0.50, 0.78, spec=0.35, spec_w=0.06), "teal": toon("teal", TEAL, 0.45, 0.75, spec=0.35, spec_w=0.06),
    "dark": toon("dark", (0.07, 0.07, 0.09), 0.6, 0.85), "rubber": toon("rubber", (0.04, 0.04, 0.05), 0.6, 0.85),
    "gold": toon("gold", (0.86, 0.60, 0.25), 0.45, 0.75, spec=0.4, spec_w=0.1), "red": toon("red", (0.55, 0.05, 0.05)),
    "glass": toon("glass", (0.55, 0.62, 0.85), 0.5, 0.8, spec=0.9, spec_w=0.08, alpha=0.25),
    "iris": toon("iris", (0.20, 0.25, 0.85), 0.7, 0.9, emit=(0.35, 0.45, 1.0), emit_k=2.2),
    "pupil": toon("pupil", (0.0, 0.0, 0.02)), "blade": toon("blade", (0.10, 0.10, 0.13)),
}
HL.M = M; HL.COL = COL

def obj(name, me, m, parent=None, loc=(0, 0, 0), rot=(0, 0, 0)):
    o = bpy.data.objects.new(name, me); COL.objects.link(o)
    if m: o.data.materials.append(m)
    o.parent = parent; o.location = loc; o.rotation_euler = rot
    return o
def prim(kind, name, m, parent=None, loc=(0, 0, 0), rot=(0, 0, 0), scale=(1, 1, 1), bevel=0.0, smooth=True, **kw):
    getattr(bpy.ops.mesh, f"primitive_{kind}_add")(**kw)
    o = bpy.context.object; o.name = name; o.data.materials.append(m)
    o.parent = parent; o.location = loc; o.rotation_euler = rot; o.scale = scale
    if bevel:
        b = o.modifiers.new("bev", "BEVEL"); b.width = bevel; b.segments = 2; b.limit_method = "ANGLE"
    if smooth:
        for p in o.data.polygons: p.use_smooth = True
    return o
def box(name, size, m, parent=None, loc=(0, 0, 0), rot=(0, 0, 0), bevel=0.01):
    return prim("cube", name, m, parent, loc, rot, (size[0] / 2, size[1] / 2, size[2] / 2), bevel=bevel, smooth=False)
def cyl(name, r, h, m, parent=None, loc=(0, 0, 0), rot=(0, 0, 0), v=32, bevel=0.0):
    return prim("cylinder", name, m, parent, loc, rot, bevel=bevel, vertices=v, radius=r, depth=h)
def sph(name, s, m, parent=None, loc=(0, 0, 0), rot=(0, 0, 0)):
    return prim("uv_sphere", name, m, parent, loc, rot, s, segments=32, ring_count=16, radius=1)
def limb(name, a, b, r, m, parent=None, r2=None):
    """Capsule-ish limb from point a to b."""
    a, b = Vector(a), Vector(b); d = b - a
    o = cyl(name, r, d.length, m, parent, (a + b) / 2, v=24, bevel=0.0)
    if r2 is not None:
        o.scale = (1, 1, 1)
    o.rotation_mode = "QUATERNION"; o.rotation_quaternion = Vector((0, 0, 1)).rotation_difference(d)
    return o
def ext_poly(name, pts, depth, m, parent=None, loc=(0, 0, 0), rot=(0, 0, 0)):
    me = bpy.data.meshes.new(name); n = len(pts)
    vs = [(x, y, -depth / 2) for x, y in pts] + [(x, y, depth / 2) for x, y in pts]
    fs = [tuple(range(n))[::-1], tuple(range(n, 2 * n))] + [(i, (i + 1) % n, n + (i + 1) % n, n + i) for i in range(n)]
    me.from_pydata(vs, [], fs); me.update()
    o = obj(name, me, m, parent, loc, rot); b = o.modifiers.new("bev", "BEVEL"); b.width = 0.012; b.segments = 2
    return o

# ------------------------------------------------------------------ ALPHA (seated, facing -Y). Units: metres; standing height 3.5 m.
RIG = bpy.data.objects.new("ALPHA", None); COL.objects.link(RIG)
Y, T, Si, D, Gd = M["yellow"], M["teal"], M["silver"], M["dark"], M["gold"]
# base, pillar, hip saddle
cyl("base", 0.85, 0.12, D, RIG, (0, -0.25, 0.06), v=8, bevel=0.01)
cyl("base_top", 0.80, 0.02, M["silver2"], RIG, (0, -0.25, 0.13), v=8)
cyl("pillar", 0.10, 1.05, Si, RIG, (0, 0.05, 0.66), v=24)
for z in (0.30, 0.62, 0.95): cyl(f"pillar_ring_{z}", 0.14, 0.05, D, RIG, (0, 0.05, z), v=24)
saddle = prim("torus", "saddle", Si, RIG, (0, 0.0, 1.22), (math.radians(90), 0, 0), (1.0, 0.55, 1.0), major_radius=0.32, minor_radius=0.07)
box("saddle_plate", (0.62, 0.42, 0.06), M["silver2"], RIG, (0, -0.02, 1.19))
# pelvis + waist + torso
box("pelvis", (0.50, 0.36, 0.24), T, RIG, (0, 0.0, 1.36), bevel=0.05)
cyl("waist", 0.17, 0.26, Si, RIG, (0, 0.02, 1.58), v=24)
for k in range(6): cyl(f"waist_rib_{k}", 0.19, 0.018, D, RIG, (0, 0.02, 1.48 + k * 0.04), v=24)
sph("ribcage", (0.27, 0.19, 0.26), M["silver2"], RIG, (0, 0.03, 1.86))
for s in (-1, 1):
    sph(f"chest_{s}", (0.14, 0.12, 0.13), T, RIG, (s * 0.12, -0.12, 1.86))
    box(f"chest_trim_{s}", (0.14, 0.05, 0.03), Y, RIG, (s * 0.13, -0.17, 1.98), (0, 0, s * 0.3))
box("collar_plate", (0.46, 0.22, 0.10), T, RIG, (0, 0.02, 2.06), bevel=0.04)
box("sternum", (0.10, 0.06, 0.28), Y, RIG, (0, -0.15, 1.80), bevel=0.02)
# legs: thighs forward, shins down, big yellow feet on the base
for s in (-1, 1):
    hip = (s * 0.16, 0.0, 1.32); knee = (s * 0.22, -0.78, 1.26); ankle = (s * 0.23, -0.86, 0.26)
    limb(f"thigh_{s}", hip, knee, 0.13, T, RIG)
    limb(f"thigh_stripe_{s}", (hip[0] + s * 0.12, hip[1] - 0.05, hip[2] + 0.04), (knee[0] + s * 0.11, knee[1] + 0.08, knee[2] + 0.04), 0.025, Y, RIG)
    sph(f"knee_{s}", (0.13, 0.12, 0.12), Y, RIG, (knee[0], knee[1] - 0.04, knee[2]))
    limb(f"shin_{s}", knee, ankle, 0.12, T, RIG)
    limb(f"shin_stripe_{s}", (knee[0] + s * 0.10, knee[1] - 0.06, knee[2] - 0.1), (ankle[0] + s * 0.10, ankle[1] - 0.06, ankle[2] + 0.12), 0.024, Y, RIG)
    sph(f"ankle_{s}", (0.09, 0.09, 0.09), Si, RIG, ankle)
    box(f"foot_{s}", (0.22, 0.40, 0.16), Y, RIG, (ankle[0], ankle[1] - 0.10, 0.22), bevel=0.04)
    cyl(f"heel_wheel_{s}", 0.09, 0.06, D, RIG, (ankle[0], ankle[1] + 0.10, 0.22), (0, math.radians(90), 0))
# arms (her right = -X strums at the body; her left = +X holds the neck)
SH_R, SH_L = (-0.34, 0.02, 2.02), (0.34, 0.02, 2.02)
for nm, sh in (("R", SH_R), ("L", SH_L)):
    sph(f"shoulder_{nm}", (0.16, 0.15, 0.13), Y, RIG, (sh[0], sh[1], sh[2] + 0.02))
EL_R, HA_R = (-0.42, -0.10, 1.66), (-0.12, -0.36, 1.50)
EL_L, HA_L = (0.50, -0.16, 1.74), (0.62, -0.48, 1.82)
limb("uparm_R", SH_R, EL_R, 0.08, T, RIG); limb("forearm_R", EL_R, HA_R, 0.075, Y, RIG); sph("elbow_R", (0.08, 0.08, 0.08), Si, RIG, EL_R)
limb("uparm_L", SH_L, EL_L, 0.08, T, RIG); limb("forearm_L", EL_L, HA_L, 0.075, Y, RIG); sph("elbow_L", (0.08, 0.08, 0.08), Si, RIG, EL_L)
HAND_R = sph("hand_R", (0.075, 0.06, 0.10), T, RIG, HA_R); HAND_L = sph("hand_L", (0.07, 0.07, 0.09), T, RIG, HA_L)
# yellow electric guitar: angular body, silver gear hub, black neck with yellow fret marks
GT = bpy.data.objects.new("guitar", None); COL.objects.link(GT); GT.parent = RIG
GT.location = (-0.02, -0.40, 1.48); GT.rotation_euler = (math.radians(90), math.radians(-24), 0)
ext_poly("gtr_body", [(-0.42, -0.10), (-0.20, -0.30), (0.10, -0.22), (0.26, -0.06), (0.22, 0.10), (0.02, 0.20), (-0.30, 0.16), (-0.48, 0.06)], 0.08, Y, GT)
cyl("gtr_hub", 0.11, 0.10, Si, GT, (-0.05, 0.0, 0.0), v=24)
for k in range(12): box(f"gtr_tooth_{k}", (0.035, 0.03, 0.09), Si, GT, (-0.05 + math.cos(k * math.pi / 6) * 0.125, math.sin(k * math.pi / 6) * 0.125, 0), (0, 0, k * math.pi / 6), bevel=0.003)
box("gtr_neck", (1.05, 0.07, 0.04), M["dark"], GT, (0.72, 0.03, 0.02))
for k in range(9): box(f"gtr_fret_{k}", (0.012, 0.072, 0.045), Y, GT, (0.30 + k * 0.10, 0.03, 0.022), bevel=0.0)
box("gtr_head", (0.16, 0.11, 0.05), Si, GT, (1.30, 0.04, 0.02), bevel=0.01)
# head (reuse the mechanical head rig), scale 0.42, on the neck
NECKP = bpy.data.objects.new("neck_mount", None); COL.objects.link(NECKP); NECKP.parent = RIG; NECKP.location = (0, -0.02, 2.47); NECKP.scale = (0.40, 0.40, 0.40)
H = HL.build(NECKP)
for o in bpy.data.objects:                                     # the head rig's own camera/lights are not built in the lib; drop leftovers
    pass

# ------------------------------------------------------------------ the platform at dusk
CONC = toon("concrete", (0.30, 0.34, 0.42), 0.55, 0.8, spec=0.25, spec_w=0.04)
box("platform", (40, 9, 0.6), CONC, None, (0, -1.0, -0.30), bevel=0.0)
box("platform_edge", (40, 0.25, 0.02), toon("edge", (0.95, 0.80, 0.25)), None, (0, 3.35, 0.005), bevel=0.0)
RAIL = toon("rail", (0.25, 0.26, 0.30), 0.5, 0.8, spec=0.6, spec_w=0.03)
for yy in (4.6, 6.0): box(f"rail_{yy}", (80, 0.08, 0.12), RAIL, None, (0, yy, -0.80), bevel=0.0)
for k in range(-40, 41): box(f"sleeper_{k}", (0.25, 2.4, 0.08), toon("sleeper", (0.16, 0.13, 0.12)), None, (k * 1.0, 5.3, -0.90), bevel=0.0)
box("ballast", (80, 4, 0.4), toon("ballast", (0.22, 0.22, 0.25)), None, (0, 5.3, -1.15), bevel=0.0)
ROOF = toon("roof", (0.18, 0.22, 0.28))
box("canopy", (40, 4.6, 0.12), ROOF, None, (0, 0.6, 5.0), bevel=0.0)
LAMPM = toon("lamp", (1, 0.85, 0.6), emit=(1.0, 0.72, 0.38), emit_k=6.0)
for k in range(-3, 4):
    x = k * 6.0
    cyl(f"col_{k}", 0.12, 5.0, ROOF, None, (x, 2.4, 2.5), v=12)
    if k != 0:
        sph(f"bulb_{k}", (0.16, 0.16, 0.12), LAMPM, None, (x, 2.1, 4.6))
# distant hills + poles (flat silhouettes)
HILL = flat("hill", (0.06, 0.07, 0.12), 1.0)
ext_poly("hills", [(-60, 0), (-40, 5), (-25, 3), (-10, 7), (5, 4), (20, 8), (40, 3), (60, 6), (60, 0)], 0.5, HILL, None, (0, 40, -2), (math.radians(90), 0, 0))
POLE = flat("pole", (0.05, 0.05, 0.08), 1.0)
for k in range(-6, 7):
    cyl(f"pole_{k}", 0.08, 9, POLE, None, (k * 9 + 3, 9.0, 3.0), v=8); box(f"pole_x_{k}", (1.6, 0.08, 0.08), POLE, None, (k * 9 + 3, 9.0, 7.0), bevel=0)
# the departing train: green carriages with warm windows, moving +X away along the far track
TRAIN = bpy.data.objects.new("train", None); COL.objects.link(TRAIN)
GREEN = toon("green", (0.10, 0.30, 0.22), 0.45, 0.75, spec=0.3, spec_w=0.05); WIN = toon("win", (1.0, 0.75, 0.40), emit=(1.0, 0.65, 0.30), emit_k=4.0)
for c in range(6):
    x0 = c * 26.5
    box(f"car_{c}", (25.5, 3.1, 3.6), GREEN, TRAIN, (x0, 5.3, 1.3), bevel=0.08)
    box(f"car_stripe_{c}", (25.5, 3.12, 0.10), toon("cream", (0.85, 0.80, 0.62)), TRAIN, (x0, 5.3, 1.8), bevel=0.0)
    for w in range(10): box(f"win_{c}_{w}", (1.4, 3.14, 0.9), WIN, TRAIN, (x0 - 11 + w * 2.45, 5.3, 2.35), bevel=0.02)
# wind-blown scraps + the memory card (old photo of 老周 waving from the train window)
PAPER = toon("paper", (0.92, 0.90, 0.84), 0.6, 0.85)
SCRAPS = [box(f"scrap_{k}", (0.10 + 0.05 * (k % 3), 0.002, 0.08), PAPER, None, (0, 0, 0), bevel=0.0) for k in range(26)]
CARD = box("memory_card", (0.74, 0.004, 0.66), toon("card", (1, 1, 1), 0.7, 0.9, tex=os.path.join(HERE, "memory_card.png")), None, (0, 0, -50), bevel=0.0)
CARD.data.uv_layers.new() if not CARD.data.uv_layers else None
# the tear: a bright drop that slides along the cheek seam on "滑落"
TEAR = sph("tear", (0.012, 0.010, 0.018), toon("tearm", (0.75, 0.85, 1.0), 0.8, 0.95, emit=(0.7, 0.85, 1.0), emit_k=3.0), H["head"], (0, -50, 0))

# ------------------------------------------------------------------ world, light, line art, look
W = bpy.data.worlds.new("dusk"); S.world = W; W.use_nodes = True; N = W.node_tree.nodes; L = W.node_tree.links
bg = N["Background"]; tc = N.new("ShaderNodeTexCoord"); sep = N.new("ShaderNodeSeparateXYZ"); ramp = N.new("ShaderNodeValToRGB")
L.new(tc.outputs["Generated"], sep.inputs[0]); L.new(sep.outputs["Z"], ramp.inputs[0]); L.new(ramp.outputs["Color"], bg.inputs["Color"])
cr = ramp.color_ramp; cr.elements[0].position = 0.48; cr.elements[0].color = (0.10, 0.08, 0.10, 1)
e = cr.elements.new(0.505); e.color = (1.0, 0.45, 0.16, 1); e = cr.elements.new(0.53); e.color = (0.55, 0.32, 0.35, 1)
cr.elements[1].position = 0.70; cr.elements[1].color = (0.05, 0.08, 0.20, 1)
bg.inputs["Strength"].default_value = 1.0
def lamp(name, kind, loc, energy, color, rot=(0, 0, 0), size=1.0):
    ld = bpy.data.lights.new(name, kind); ld.energy = energy; ld.color = color
    if kind == "AREA": ld.size = size
    if kind == "SUN": ld.angle = math.radians(2)
    o = bpy.data.objects.new(name, ld); COL.objects.link(o); o.location = loc; o.rotation_euler = rot; return o
lamp("sun", "SUN", (0, 0, 10), 3.2, (1.0, 0.62, 0.34), rot=(math.radians(78), 0, math.radians(-125)))        # low warm sun from back-right
lamp("sky", "SUN", (0, 0, 10), 0.9, (0.45, 0.58, 1.0), rot=(math.radians(25), 0, math.radians(30)))         # cool sky fill from front-left
lamp("lampglow", "POINT", (0.6, 1.6, 4.4), 900, (1.0, 0.72, 0.40))
lamp("rim", "AREA", (1.5, 2.2, 3.4), 600, (0.65, 0.80, 1.0), rot=(math.radians(-60), 0, math.radians(160)), size=2.0)

S.render.engine = "BLENDER_EEVEE"
rx, ry = (int(v) for v in A.res.split("x")); S.render.resolution_x, S.render.resolution_y = rx, ry
S.render.fps = FPS
S.eevee.taa_render_samples = 16
S.view_settings.view_transform = "Standard"; S.view_settings.look = "None"
S.render.use_freestyle = True; S.render.line_thickness_mode = "ABSOLUTE"; S.render.line_thickness = 1.25 * rx / 1280
ls = S.view_layers[0].freestyle_settings.linesets[0] if S.view_layers[0].freestyle_settings.linesets else S.view_layers[0].freestyle_settings.linesets.new("ink")
ls.select_by_visibility = True; ls.select_silhouette = True; ls.select_border = True; ls.select_crease = True; ls.select_material_boundary = True
if ls.linestyle is None: ls.linestyle = bpy.data.linestyles.new("ink")
ls.linestyle.color = (0.03, 0.03, 0.07); ls.linestyle.thickness = 1.25 * rx / 1280
S.view_layers[0].freestyle_settings.crease_angle = math.radians(130)
# glow and grain are added in post (ffmpeg)

# ------------------------------------------------------------------ cameras: three shots
CAM = bpy.data.objects.new("cam", bpy.data.cameras.new("cam")); COL.objects.link(CAM); S.camera = CAM
CAM.data.sensor_width = 36
AIM = bpy.data.objects.new("aim", None); COL.objects.link(AIM)
c = CAM.constraints.new("TRACK_TO"); c.target = AIM; c.track_axis = "TRACK_NEGATIVE_Z"; c.up_axis = "UP_Y"
def lerp(a, b, u): return a + (b - a) * u
def ease(u): u = max(0.0, min(1.0, u)); return u * u * (3 - 2 * u)
def V(*a): return Vector(a)
def shot(t):
    """Song time -> camera (loc, aim, focal)."""
    if t < 137.70:                                    # S1 wide: low behind-left, train lights receding
        u = (t - 135.4) / 2.3
        return V(-6.5 + 0.6 * u, -7.5, 1.2), V(1.0, 2.0, 1.9), 24
    if t < 144.36:                                    # S2 medium-wide 3/4 front, slow drift right as the wind passes
        u = ease((t - 137.70) / 6.66)
        return V(lerp(-3.4, -2.6, u), -5.2, 2.0), V(0.0, -0.3, lerp(1.9, 2.0, u)), 35
    u = ease((t - 144.36) / 7.04)                       # S3 slow push-in to the face, 3/4 from her right
    return V(lerp(-1.6, -0.95, u), lerp(-3.0, -1.75, u), lerp(2.45, 2.55, u)), V(0.0, -0.10, lerp(2.40, 2.52, u)), lerp(50, 70, u)

# ------------------------------------------------------------------ performance: jaw from the vocal stem, attention from the phrasing
EX = H["EXPR"]
def mix(a, b, u): return tuple(x + (y - x) * u for x, y in zip(a, b))
def jaw_at(t):
    i = (t - JAW_T0) * JAW["fps"]
    if i < 0 or i >= len(JAW["frames"]) - 1: return 0.0
    i0 = int(i); f = i - i0; return JAW["frames"][i0] * (1 - f) + JAW["frames"][i0 + 1] * f
def perform(t):
    jd = jaw_at(t)
    # head: looks down toward the floor, lifts and turns toward the departing train on "一阵风", then turns back and lowers on the tear
    yaw = 0.0; tilt = 6.0
    if t >= 139.6: yaw = lerp(0, 22, ease((t - 139.6) / 1.4)); tilt = lerp(6, -2, ease((t - 139.6) / 1.4))
    if t >= 143.2: yaw = lerp(22, 6, ease((t - 143.2) / 1.6)); tilt = lerp(-2, 3, ease((t - 143.2) / 1.6))
    if t >= 148.9: tilt = lerp(3, 10, ease((t - 148.9) / 1.6))
    ex = EX["neutral"]
    if t >= 137.6: ex = mix(EX["neutral"], EX["tender"], ease((t - 137.6) / 0.8))
    if t >= 145.2: ex = mix(EX["tender"], EX["high"], ease((t - 145.2) / 0.6))
    if t >= 147.8: ex = mix(EX["high"], EX["closing"], ease((t - 147.8) / 1.6))
    H["pose"](jd * 0.85, ex, t=t, yaw=yaw, tilt=tilt)
    # strumming hand: small down-strokes on the beat (~70 bpm), fretting hand slides a little per phrase
    beat = (t - 135.4) * 70 / 60
    HAND_R.location = (HA_R[0], HA_R[1], HA_R[2] + 0.03 * math.sin(beat * math.pi * 2) ** 8)
    HAND_L.location = (HA_L[0] + (0.04 if t > 144.36 else 0.0), HA_L[1], HA_L[2])
    # train: pulls away to the right
    TRAIN.location = (lerp(-60, 40, ease((t - 135.4) / 16.0)) + 30 * max(0, (t - 140) / 16), 0, 0)
    # wind gust: 140.4 -> 143.5, scraps blow across right to left, the memory card tumbles through
    g = (t - 140.0) / 3.6
    for k, sc in enumerate(SCRAPS):
        ph = (k * 0.137) % 1.0
        u = g * (1.0 + 0.4 * ph) - ph * 0.5
        if 0 <= u <= 1:
            sc.location = (lerp(6, -7, u), lerp(-1.5, -4.5, ph), 0.4 + 2.6 * ph + 0.6 * math.sin(u * 9 + k))
            sc.rotation_euler = (u * 11 + k, u * 7, u * 13 + k * 0.3)
        else:
            sc.location = (0, 0, -50)
    cu = (t - 141.0) / 2.6
    if 0 <= cu <= 1:
        CARD.location = (lerp(3.5, -3.8, cu), lerp(-2.4, -3.6, cu), 2.2 + 0.5 * math.sin(cu * 3.1))
        CARD.rotation_euler = (0.25 * math.sin(cu * 5), 0.4 * math.sin(cu * 4), lerp(-0.4, 0.5, cu))
    else:
        CARD.location = (0, 0, -50)
    # tear: appears under her right eye at 147.6 and slides down the cheek seam until 149.4
    tu = (t - 147.6) / 1.8
    if 0 <= tu <= 1:
        TEAR.location = (-0.17 + 0.02 * tu, 0.02 - 0.32 * ease(tu), 0.19 - 0.03 * tu)
    else:
        TEAR.location = (0, -50, 0)

def frame(i, path):
    t = T0 + i / FPS
    perform(t)
    loc, aim, f = shot(t)
    CAM.location = loc; AIM.location = aim; CAM.data.lens = f
    S.render.filepath = path; bpy.ops.render.render(write_still=True)

if A.blend: bpy.ops.wm.save_as_mainfile(filepath=os.path.abspath(A.blend))
if A.still is not None:
    os.makedirs(os.path.dirname(os.path.abspath(A.out)), exist_ok=True); frame(A.still, os.path.abspath(A.out))
else:
    a, b = (int(v) for v in A.frames.split("-")) if A.frames else (0, int(DUR * FPS))
    os.makedirs(A.out, exist_ok=True)
    for i in range(a, b):
        p = os.path.join(os.path.abspath(A.out), f"f{i:04d}.png")
        if not os.path.exists(p): frame(i, p)
