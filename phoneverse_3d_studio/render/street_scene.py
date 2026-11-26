"""street_scene.py: "Cheers, Biscuit" scenes 1-2 (hook + snatch, 0 - 29.7 s) on Oxford Street, Blender 5 / bpy, Cycles CPU.

Cast (Phoneverse Character Sheet + this episode):
  YOU     Female_Adult_01 (pink shirt), walks scrolling her phone, gets robbed
  THIEF_A Male_Adult_18 (grey hoodie), yellow e-bike at the kerb, grabs the phone
  THIEF_B Male_Adult_07 scaled 1.18 + dark beanie ("the size of a fridge"), bus stop, bumps her, catches the phone
  OLD_MAN Male_Adult_03, SHOPPER Female_Adult_04 (point opposite ways), plus street extras
Motion: Rocketbox mocap clips are sampled once (bone matrices per clip frame) and copied onto any character (same Biped
skeleton); arms are then overridden with the studio's two-bone IK where hands must hit something (phone, handlebars, knees).
Faces: ARKit expression shapes (pushed ~1.5x) + Oculus visemes from audio/out/visemes.json (lip sync on the real voices).
Timing: every shot and action is anchored to the measured voice timeline (audio/out/timeline.json), never re-timed.

  .venv/bin/python render/street_scene.py --test                 # one still per shot -> build/street_test/ + contact sheet
  .venv/bin/python render/street_scene.py --one 120              # one frame (global frame number, 24 fps)
  .venv/bin/python render/street_scene.py --frames 0 712         # render a range (resumable) -> build/street/NNNN.png
"""
import argparse, json, math, os, random, sys, time
import bpy
from mathutils import Vector, Matrix, Euler, Quaternion

HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(HERE)
EP = os.path.join(ROOT, "..", "drafts", "phoneverse-found-text", "audio", "out")
ap = argparse.ArgumentParser()
ap.add_argument("--test", action="store_true"); ap.add_argument("--one", type=int); ap.add_argument("--frames", nargs=2, type=int)
ap.add_argument("--samples", type=int, default=16); ap.add_argument("--res", nargs=2, type=int, default=[540, 960])
ap.add_argument("--out", default="build/street"); ap.add_argument("--shots", nargs="*"); ap.add_argument("--dbg", type=float); ap.add_argument("--threads", type=int, default=0)
ap.add_argument("--list", nargs="*", type=int, help="render just these frames (checks)")
a = ap.parse_args(sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else None)
FPS = 24
TL = {r["id"]: r for r in json.load(open(os.path.join(EP, "timeline.json")))}
S = {k: v["start"] for k, v in TL.items()}; E = {k: v["end"] for k, v in TL.items()}
VIS = json.load(open(os.path.join(EP, "visemes.json")))
WORDS = json.load(open(os.path.join(EP, "words.json")))
def W(line, word, end=False):
    """start (or end) time of a word inside a line, from the measured word timings"""
    w = next(x for x in WORDS if x["line"] == line and x["word"].lower().strip(".,!?'\"") == word)
    return w["end"] if end else w["start"]
L02N = W("L02", "now") - 0.75      # "Now you judge this" (after the 1 s pause): the foreshadow beats keep their old offsets from here
T_LEAVE = W("L13", "size") - 0.05  # the camera leaves her on "...the size of a fridge"
A = os.path.join(ROOT, "assets", "rbx")
ease = lambda p: p * p * (3 - 2 * p)
clamp = lambda p, lo=0.0, hi=1.0: max(lo, min(hi, p))
def ramp(t, t0, t1): return ease(clamp((t - t0) / max(1e-4, t1 - t0)))
def lerp(x, y, k): return x + (y - x) * k
def track(keys, t):
    """keys [[t, value], ...] (numbers or tuples) -> eased value at t"""
    if t <= keys[0][0]: return keys[0][1]
    for (t0, v0), (t1, v1) in zip(keys, keys[1:]):
        if t0 <= t <= t1:
            k = ease((t - t0) / max(1e-4, t1 - t0))
            return tuple(lerp(x, y, k) for x, y in zip(v0, v1)) if isinstance(v0, (tuple, list)) else lerp(v0, v1, k)
    return keys[-1][1]
def fwd(h):  # heading (deg) -> forward vector (Rocketbox characters face -Y at heading 0)
    r = math.radians(h); return Vector((math.sin(r), -math.cos(r), 0))

# =====================================================================================================================
# scene + materials
bpy.ops.wm.read_factory_settings(use_empty=True)
sc = bpy.context.scene; col = sc.collection; rnd = random.Random(11)
def mat(name, color, rough=0.6, metal=0.0, emit=None, strength=0.0):
    m = bpy.data.materials.new(name); m.use_nodes = True; b = m.node_tree.nodes["Principled BSDF"]
    b.inputs["Base Color"].default_value = (*color, 1); b.inputs["Roughness"].default_value = rough; b.inputs["Metallic"].default_value = metal
    if emit: b.inputs["Emission Color"].default_value = (*emit, 1); b.inputs["Emission Strength"].default_value = strength
    return m
def emit_mat(name, color, strength):
    m = bpy.data.materials.new(name); m.use_nodes = True; nt = m.node_tree
    for nd in list(nt.nodes): nt.nodes.remove(nd)
    em = nt.nodes.new("ShaderNodeEmission"); em.inputs["Color"].default_value = (*color, 1); em.inputs["Strength"].default_value = strength
    ou = nt.nodes.new("ShaderNodeOutputMaterial"); nt.links.new(em.outputs[0], ou.inputs[0]); return m
def glass_mat(name, tint=(0.75, 0.85, 0.9)):
    m = bpy.data.materials.new(name); m.use_nodes = True; b = m.node_tree.nodes["Principled BSDF"]
    b.inputs["Base Color"].default_value = (*tint, 1); b.inputs["Roughness"].default_value = 0.05
    b.inputs["Transmission Weight"].default_value = 0.9; b.inputs["IOR"].default_value = 1.45; return m
def brick_mat(name, c1, c2, mortar, scale=6.0, rough=0.8):
    m = bpy.data.materials.new(name); m.use_nodes = True; nt = m.node_tree; b = nt.nodes["Principled BSDF"]
    br = nt.nodes.new("ShaderNodeTexBrick"); br.inputs["Color1"].default_value = (*c1, 1); br.inputs["Color2"].default_value = (*c2, 1)
    br.inputs["Mortar"].default_value = (*mortar, 1); br.inputs["Scale"].default_value = scale; br.inputs["Mortar Size"].default_value = 0.015
    tc = nt.nodes.new("ShaderNodeTexCoord"); nt.links.new(tc.outputs["Object"], br.inputs["Vector"])
    nt.links.new(br.outputs["Color"], b.inputs["Base Color"]); b.inputs["Roughness"].default_value = rough; return m
def noise_mat(name, c1, c2, scale=40.0, rough=0.85):
    m = bpy.data.materials.new(name); m.use_nodes = True; nt = m.node_tree; b = nt.nodes["Principled BSDF"]
    nz = nt.nodes.new("ShaderNodeTexNoise"); nz.inputs["Scale"].default_value = scale; nz.inputs["Detail"].default_value = 8
    cr = nt.nodes.new("ShaderNodeValToRGB"); cr.color_ramp.elements[0].color = (*c1, 1); cr.color_ramp.elements[1].color = (*c2, 1)
    tc = nt.nodes.new("ShaderNodeTexCoord"); nt.links.new(tc.outputs["Object"], nz.inputs["Vector"])
    nt.links.new(nz.outputs["Fac"], cr.inputs["Fac"]); nt.links.new(cr.outputs["Color"], b.inputs["Base Color"])
    b.inputs["Roughness"].default_value = rough; return m
def box(name, dims, loc, m, rot=(0, 0, 0), bevel=0.0, parent=None):
    bpy.ops.mesh.primitive_cube_add(size=1, location=loc, rotation=rot); o = bpy.context.active_object; o.name = name; o.scale = dims
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    if bevel: md = o.modifiers.new("bev", "BEVEL"); md.width = bevel; md.segments = 3
    o.data.materials.append(m)
    if parent: o.parent = parent
    return o
def cyl(name, r, depth, loc, m, rot=(0, 0, 0), verts=16, parent=None):
    bpy.ops.mesh.primitive_cylinder_add(radius=r, depth=depth, location=loc, rotation=rot, vertices=verts); o = bpy.context.active_object
    o.name = name; o.data.materials.append(m)
    if parent: o.parent = parent
    return o
def tube(name, p0, p1, r, m, parent=None):
    p0, p1 = Vector(p0), Vector(p1); d = p1 - p0
    o = cyl(name, r, d.length, (p0 + p1) / 2, m, verts=10, parent=parent)
    o.rotation_euler = d.to_track_quat("Z", "Y").to_euler(); return o
def sphere(name, r, loc, m, seg=12, parent=None):
    bpy.ops.mesh.primitive_uv_sphere_add(radius=r, location=loc, segments=seg, ring_count=max(4, seg // 2)); o = bpy.context.active_object
    o.name = name; o.data.materials.append(m)
    if parent: o.parent = parent
    return o
import bmesh
BATCH = {}
def bbox(dims, loc, m, rot=(0, 0, 0)):
    """add a box to a per-material batch (one mesh object per material: much faster than thousands of objects)"""
    bm = BATCH.setdefault(m.name, (bmesh.new(), m))[0]
    M = Matrix.LocRotScale(Vector(loc), Euler(rot).to_quaternion(), Vector(dims)); bmesh.ops.create_cube(bm, size=1.0, matrix=M)
def bsphere(r, loc, m, seg=8):
    bm = BATCH.setdefault(m.name, (bmesh.new(), m))[0]
    bmesh.ops.create_uvsphere(bm, u_segments=seg, v_segments=max(4, seg // 2), radius=r, matrix=Matrix.Translation(Vector(loc)))
def flush_batches():
    for nm, (bm, m) in BATCH.items():
        me = bpy.data.meshes.new(f"batch_{nm}"); bm.to_mesh(me); bm.free(); o = bpy.data.objects.new(f"batch_{nm}", me); col.objects.link(o)
        me.materials.append(m)
        if nm in ("bulb", "bauble_g", "bauble_r"): o.visible_shadow = False
    BATCH.clear()
def empty(name, loc=(0, 0, 0)):
    e = bpy.data.objects.new(name, None); col.objects.link(e); e.location = loc; return e
def text(body, loc, size, m, rot=(math.radians(90), 0, 0), extrude=0.02):
    bpy.ops.object.text_add(location=loc, rotation=rot); o = bpy.context.active_object; o.data.body = body
    o.data.size = size; o.data.extrude = extrude; o.data.align_x = "CENTER"; o.data.align_y = "CENTER"; o.data.materials.append(m); return o

# =====================================================================================================================
# Oxford Street: road along X. Kerb at y=1.5, near pavement y 1.5..5.6, shop fronts at y=5.6 facing -Y; road y -5..1.5,
# far pavement y -8.4..-5, far buildings at y=-8.4 facing +Y. Late afternoon in late November: low warm sun + the Christmas lights.
W = bpy.data.worlds.new("w"); sc.world = W; W.use_nodes = True
bg = W.node_tree.nodes["Background"]; bg.inputs[0].default_value = (0.42, 0.55, 0.78, 1); bg.inputs[1].default_value = 0.9
sun = bpy.data.lights.new("sun", "SUN"); sun.energy = 3.6; sun.color = (1.0, 0.82, 0.62); sun.angle = math.radians(2.5)
so = bpy.data.objects.new("sun", sun); col.objects.link(so); so.rotation_euler = Euler((math.radians(62), 0, math.radians(-115)))  # from -x, low, a little from the road side

asphalt = noise_mat("asphalt", (0.05, 0.05, 0.055), (0.12, 0.12, 0.125), 60, 0.9)
slabs = brick_mat("slabs", (0.55, 0.53, 0.5), (0.48, 0.47, 0.45), (0.32, 0.31, 0.3), scale=1.4, rough=0.85)
kerbm = mat("kerb", (0.6, 0.6, 0.58), 0.8)
box("road", (120, 13.4, 0.1), (0, -1.7, -0.05), asphalt)
box("pave_n", (120, 4.1, 0.14), (0, 3.55, 0.07), slabs); box("pave_s", (120, 3.4, 0.14), (0, -6.7, 0.07), slabs)
box("kerb_n", (120, 0.15, 0.16), (0, 1.5, 0.08), kerbm); box("kerb_s", (120, 0.15, 0.16), (0, -5.0, 0.08), kerbm)
buslane = mat("buslane", (0.42, 0.07, 0.06), 0.85)
box("buslane", (120, 3.1, 0.004), (0, -0.1, 0.002), buslane)
white = mat("paint", (0.85, 0.85, 0.82), 0.6); yellow = mat("ypaint", (0.9, 0.7, 0.1), 0.6)
box("lane_line", (120, 0.2, 0.006), (0, -1.75, 0.003), white)
for x in range(-60, 60, 6): bbox((3.0, 0.12, 0.006), (x, -3.4, 0.003), white)
text("BUS LANE", (-14, -0.1, 0.006), 0.9, white, rot=(0, 0, math.radians(90)), extrude=0.0)

FACADES = [((0.86, 0.80, 0.68), "stone"), ((0.55, 0.22, 0.15), "brick"), ((0.78, 0.76, 0.72), "stone"), ((0.35, 0.36, 0.38), "dark"),
           ((0.88, 0.84, 0.76), "stone"), ((0.62, 0.28, 0.2), "brick"), ((0.92, 0.9, 0.86), "white")]
SIGNS = [("CAFE", (0.05, 0.3, 0.22)), ("SHOES", (0.08, 0.08, 0.1)), ("BOOKS", (0.4, 0.06, 0.08)), ("PHONES", (0.05, 0.12, 0.4)),
         ("BAKERY", (0.55, 0.32, 0.08)), ("GIFTS", (0.35, 0.05, 0.35)), ("OPTICIAN", (0.06, 0.06, 0.08)), ("DESIGN", (0.12, 0.3, 0.45))]
win_dark = mat("win_dark", (0.05, 0.07, 0.1), 0.05, 0.3); win_lit = emit_mat("win_lit", (1.0, 0.78, 0.5), 2.5)
shopglass = emit_mat("shop_glow", (1.0, 0.8, 0.6), 1.6); shopwin = glass_mat("shopwin", (0.85, 0.9, 0.95))
shelfm = mat("shelf", (0.55, 0.45, 0.35), 0.6)
GOODS = [mat(f"good{i}", c, 0.5) for i, c in enumerate([(0.8, 0.1, 0.1), (0.1, 0.35, 0.7), (0.9, 0.75, 0.1), (0.1, 0.5, 0.25), (0.85, 0.85, 0.85), (0.6, 0.2, 0.6), (0.15, 0.15, 0.15)])]; signtxt = emit_mat("sign_txt", (1.0, 0.95, 0.85), 4.0)
def building(x0, width, y_face, facing, k):
    color, kind = FACADES[k % len(FACADES)]; h = rnd.uniform(15, 21); depth = 8.0
    yc = y_face + facing * -depth / 2 * -1 if False else y_face + (depth / 2) * (1 if facing < 0 else -1)
    fm = brick_mat(f"fac{k}", color, tuple(c * 0.92 for c in color), tuple(min(1, c * 1.15) for c in color), 3.0) if kind == "brick" else mat(f"fac{k}", color, 0.85)
    box(f"bld{k}", (width - 0.15, depth, h), (x0 + width / 2, yc, h / 2), fm)
    yf = y_face + 0.02 * facing  # faces toward the street
    # shop front: lit glass + sign board with a generic word (no brands)
    box(f"shop{k}", (width - 1.0, 0.03, 2.6), (x0 + width / 2, yf + 0.03 * facing, 1.45), shopwin)
    yi = yf - 1.4 * facing                      # interior: warm back wall + shelves of colourful goods
    bbox((width - 1.0, 0.05, 2.8), (x0 + width / 2, yi, 1.45), shopglass)
    for g in range(int(width * 1.6)):
        gx = x0 + 0.7 + rnd.uniform(0, width - 1.4); gz = rnd.choice([0.55, 1.15, 1.75]); gm = GOODS[rnd.randrange(len(GOODS))]
        bbox((rnd.uniform(0.15, 0.35), 0.2, rnd.uniform(0.18, 0.45)), (gx, yi + 0.35 * facing, gz), gm)
    for sz in (0.4, 1.0, 1.6): bbox((width - 1.2, 0.5, 0.03), (x0 + width / 2, yi + 0.3 * facing, sz), shelfm)
    word, scol = SIGNS[k % len(SIGNS)]
    box(f"signb{k}", (width - 0.8, 0.12, 0.7), (x0 + width / 2, yf + 0.08 * facing, 3.2), mat(f"sb{k}", scol, 0.5))
    t = text(word, (x0 + width / 2, yf + 0.16 * facing, 3.2), 0.42, signtxt, rot=(math.radians(90), 0, 0 if facing < 0 else math.radians(180)))
    # upper windows
    n = max(2, int(width / 2.2)); sillm = mat(f"sill{k}", tuple(min(1, c * 1.1) for c in color), 0.8)
    for fl in range(int((h - 4.5) / 3.2)):
        for i in range(n):
            wx = x0 + (i + 0.5) * width / n; wz = 5.2 + fl * 3.2
            bbox((1.1, 0.08, 1.7), (wx, yf + 0.02 * facing, wz), win_lit if rnd.random() < 0.28 else win_dark)
            bbox((1.3, 0.18, 0.08), (wx, yf + 0.06 * facing, wz - 0.9), sillm)
    box(f"corn{k}", (width - 0.1, 0.35, 0.3), (x0 + width / 2, yf + 0.12 * facing, h - 0.3), mat(f"cn{k}", tuple(min(1, c * 1.08) for c in color), 0.8))
x = -60.0; k = 0
while x < 60:
    w_ = rnd.choice([7.0, 8.5, 10.0, 12.0]); building(x, w_, 5.6, -1, k); x += w_; k += 1
x = -60.0
while x < 60:
    w_ = rnd.choice([7.0, 8.5, 10.0, 12.0]); building(x, w_, -8.4, +1, k); x += w_; k += 1

# street furniture: lamp posts, bus stop, post box, bollards, a phone box
black = mat("black_metal", (0.02, 0.02, 0.025), 0.4, 0.6); red = mat("pillar_red", (0.7, 0.02, 0.02), 0.35)
lampglow = emit_mat("lamp", (1.0, 0.85, 0.6), 6)
for x in range(-54, 60, 16):
    for y, s in ((1.85, 1), (-5.35, -1)):
        cyl(f"lp{x}{y}", 0.07, 7.0, (x, y, 3.5), black); tube(f"lpa{x}{y}", (x, y, 6.9), (x, y - 0.9 * s, 6.9), 0.04, black)
        sphere(f"lpl{x}{y}", 0.16, (x, y - 0.9 * s, 6.75), lampglow)
# bus stop shelter (Thief B waits here): x 7..10, near the kerb
shelter = empty("shelter", (8.5, 2.35, 0))
for dx in (-1.5, 1.5):
    box(f"sh_post{dx}", (0.06, 0.06, 2.5), (dx, 0.55, 1.25), black, parent=shelter)
box("sh_roof", (3.2, 1.5, 0.08), (0, 0.3, 2.52), black, parent=shelter)
box("sh_back", (3.0, 0.03, 1.9), (0, 0.95, 1.3), glass_mat("sh_glass"), parent=shelter)
box("sh_ad", (1.1, 0.06, 1.7), (1.55, 0.3, 1.2), emit_mat("ad", (0.95, 0.85, 0.7), 2.5), parent=shelter)
cyl("stop_pole", 0.04, 3.0, (6.6, 1.8, 1.5), black); cyl("stop_flag", 0.28, 0.04, (6.6, 1.8, 3.0), mat("flag", (0.85, 0.1, 0.1), 0.4), rot=(math.radians(90), 0, 0))
cyl("post_box", 0.24, 1.3, (-9.0, 2.0, 0.65), red); cyl("post_cap", 0.27, 0.1, (-9.0, 2.0, 1.33), red)
pb_ = box("phone_box", (0.95, 0.95, 2.5), (19.0, 2.1, 1.25), red, bevel=0.03)
for x in range(-50, 60, 3):
    if abs(x) > 14: bbox((0.11, 0.11, 0.9), (x + 0.5, 1.72, 0.45), black)
# far-pavement trees (bare, late November) for depth
bark = mat("bark", (0.12, 0.09, 0.07), 0.9)
for x in range(-56, 60, 11):
    tube(f"tr{x}", (x, -6.2, 0), (x + 0.2, -6.2, 5.0), 0.16, bark)
    for j in range(6):
        ang = rnd.uniform(0, 6.28); L = rnd.uniform(1.2, 2.2); z0 = rnd.uniform(3.0, 4.8)
        p0_, p1_ = Vector((x + 0.1, -6.2, z0)), Vector((x + 0.1 + L * math.cos(ang), -6.2 + L * math.sin(ang), z0 + rnd.uniform(0.8, 1.6)))
        bbox((0.08, 0.08, (p1_ - p0_).length), (p0_ + p1_) / 2, bark, (p1_ - p0_).to_track_quat("Z", "Y").to_euler())

# Christmas lights across the street (strings of warm bulbs + big gold / red baubles)
bulb = emit_mat("bulb", (1.0, 0.82, 0.45), 14); gold = emit_mat("bauble_g", (1.0, 0.7, 0.25), 6); redb = emit_mat("bauble_r", (1.0, 0.15, 0.12), 6)
for x in range(-52, 60, 9):
    for z_off in (0.0, 0.7):
        y0, y1 = 5.6, -8.4
        for i in range(0, 45):
            u = i / 44; y = lerp(y0, y1, u); z = 10.5 + z_off - 1.6 * math.sin(math.pi * u)
            bsphere(0.06, (x, y, z), bulb, seg=6)
    for i, u in enumerate((0.3, 0.5, 0.7)):
        y = lerp(5.6, -8.4, u); z = 10.5 - 1.6 * math.sin(math.pi * u) - 0.8
        bsphere(0.38, (x, y, z), gold if i != 1 else redb, seg=14)
flush_batches()

# red double-decker bus (no logos), moves along the bus lane
bus = empty("bus", (-200, -0.1, 0))
busred = mat("busred", (0.72, 0.03, 0.03), 0.3, 0.1); busglass = mat("busglass", (0.04, 0.05, 0.07), 0.05, 0.4)
box("bus_body", (11.0, 2.5, 4.0), (0, 0, 2.3), busred, bevel=0.15, parent=bus)
for z in (1.9, 3.6):
    for side in (-1, 1): box(f"bus_win{z}{side}", (9.6, 0.05, 0.85), (0.3, side * 1.27, z), busglass, parent=bus)
for side in (-1, 1): box(f"bus_front{side}", (0.05, 2.2, 0.9 if side > 0 else 0.7), (side * 5.52, 0, 2.0 if side > 0 else 3.6), busglass, parent=bus)
box("bus_dest", (0.06, 1.6, 0.35), (5.53, 0, 3.1), emit_mat("dest", (1, 0.75, 0.2), 4), parent=bus)
box("bus_stripe", (11.05, 2.55, 0.12), (0, 0, 1.25), mat("bus_stripe", (0.9, 0.85, 0.75), 0.4), parent=bus)
tyre = mat("tyre", (0.02, 0.02, 0.02), 0.9)
for wx in (-3.6, 3.4):
    for side in (-1, 1): cyl(f"bus_wh{wx}{side}", 0.5, 0.3, (wx, side * 1.15, 0.5), tyre, rot=(math.radians(90), 0, 0), verts=20, parent=bus)
def bus_x(t):  # passes the split-shot camera (1.2 m to its right) just after B has charged past, then overtakes A; +x at 14 m/s
    t0 = S["L09"] + 0.62; x = (SPLIT_CAM_X - 5.5) + 14.0 * (t - t0)
    return -200 if x < -60 or x > 60 else x

# the yellow e-bike (Thief A)
ebike = empty("ebike", (0, 0, 0))
ylw = mat("bike_yellow", (0.95, 0.72, 0.03), 0.35, 0.2)
for wx in (-0.55, 0.55):
    bpy.ops.mesh.primitive_torus_add(major_radius=0.33, minor_radius=0.03, location=(wx, 0, 0.36), rotation=(math.radians(90), 0, 0))
    o = bpy.context.active_object; o.data.materials.append(tyre); o.parent = ebike; o.name = f"bwh{wx}"
    cyl(f"hub{wx}", 0.05, 0.06, (wx, 0, 0.36), black, rot=(math.radians(90), 0, 0), parent=ebike)
for p0, p1 in [((-0.55, 0, 0.36), (-0.05, 0, 0.42)), ((-0.05, 0, 0.42), (-0.18, 0, 0.82)), ((-0.18, 0, 0.82), (0.42, 0, 0.88)),
               ((-0.05, 0, 0.42), (0.42, 0, 0.88)), ((0.42, 0, 0.88), (0.55, 0, 0.36)), ((0.42, 0, 0.88), (0.38, 0, 1.08)), ((-0.55, 0, 0.36), (-0.18, 0, 0.82))]:
    tube("bf", p0, p1, 0.028, ylw, parent=ebike)
box("bike_batt", (0.38, 0.1, 0.12), (0.17, 0, 0.73), black, rot=(0, math.radians(-8), 0), parent=ebike)
box("bike_seat", (0.26, 0.13, 0.05), (-0.2, 0, 0.86), black, bevel=0.02, parent=ebike)
tube("bars", (0.38, -0.28, 1.08), (0.38, 0.28, 1.08), 0.022, black, parent=ebike)
box("delivery_box", (0.42, 0.42, 0.4), (-0.52, 0, 1.12), mat("dbox", (0.12, 0.12, 0.13), 0.6), bevel=0.02, parent=ebike)

# the phone (generic: graphite slab + lit screen)
phone = box("phone", (0.074, 0.152, 0.009), (0, 0, -50), mat("pinkcase", (0.85, 0.28, 0.45), 0.45), bevel=0.003)
scr = box("phone_scr", (0.068, 0.144, 0.001), (0, 0, 0.0048), emit_mat("pscr", (0.75, 0.85, 1.0), 2.5), parent=phone)

# =====================================================================================================================
# characters
def load_char(name, facial, tex_dir, scale=1.0):
    before = set(bpy.data.objects)
    bpy.ops.import_scene.fbx(filepath=os.path.join(A, name, f"{name}{'_facial' if facial else ''}.fbx"))
    new = [o for o in bpy.data.objects if o not in before]
    arm = next(o for o in new if o.type == "ARMATURE"); meshes = [o for o in new if o.type == "MESH"]
    for o in new:
        if o.type == "EMPTY": o.hide_render = True
    for m_ in meshes:
        for sl in m_.material_slots:
            if not sl.material or not sl.material.use_nodes: continue
            for nd in sl.material.node_tree.nodes:
                if nd.type == "TEX_IMAGE" and nd.image:
                    p = os.path.join(A, name, "tex", os.path.basename(nd.image.filepath))
                    if os.path.exists(p): nd.image.filepath = p
                    if any(s in nd.image.filepath for s in ("_normal", "_specular")): nd.image.colorspace_settings.name = "Non-Color"
                    try: nd.image.reload()
                    except Exception: pass
    for o in new: o.animation_data_clear()   # imported takes would re-key the rig on every frame change and undo our posing
    z0 = arm.location.z * scale; arm.scale = (0.01 * scale,) * 3   # the importer lifts the Biped root to hip height via the object
    face = next((o for o in meshes if o.data.shape_keys and len(o.data.shape_keys.key_blocks) > 40), None)
    return dict(name=name, arm=arm, meshes=meshes, face=face, scale=scale, z0=z0,
                KB={k.name: k for k in face.data.shape_keys.key_blocks} if face else {})

CLIPS = {}
def bake(clip):
    """Sample a mocap clip once: list of {bone: matrix_basis} per clip frame (the clips are 30 fps)."""
    if clip in CLIPS: return CLIPS[clip]
    before = set(bpy.data.objects); acts_before = set(bpy.data.actions)
    bpy.ops.import_scene.fbx(filepath=os.path.join(A, "anim", f"{clip}.fbx"))
    new = [o for o in bpy.data.objects if o not in before]
    arm = next(o for o in new if o.type == "ARMATURE" and o.animation_data and o.animation_data.action)
    act = arm.animation_data.action; f0, f1 = int(act.frame_range[0]), int(act.frame_range[1])
    frames = []
    for f in range(f0, f1 + 1):
        sc.frame_set(f); d = {pb.name: pb.matrix.copy() for pb in arm.pose.bones}   # armature space (retargeted by orientation)
        d["__pelvis"] = arm.pose.bones["Bip01 Pelvis"].head.copy()   # hip height in armature space (the clip's own ground = 0)
        frames.append(d)
    for o in new: bpy.data.objects.remove(o, do_unlink=True)
    for ac in set(bpy.data.actions) - acts_before: bpy.data.actions.remove(ac)
    CLIPS[clip] = frames; return frames

def clip_pose(clip, t, loop=True):
    fr = bake(clip); n = len(fr); x = t * 30.0
    x = x % (n - 1) if loop else min(x, n - 1.001)
    i = int(x); k = x - i; A_, B_ = fr[i], fr[min(i + 1, n - 1)]
    P = {b: blend_m(A_[b], B_[b], k) for b in A_ if b != "__pelvis"}; P["__pelvis"] = A_["__pelvis"].lerp(B_["__pelvis"], k); return P
def blend_m(Ma, Mb, k):
    la, ra, sa = Ma.decompose(); lb, rb, sb = Mb.decompose()
    return Matrix.LocRotScale(la.lerp(lb, k), ra.slerp(rb, k), sa.lerp(sb, k))
def blend_pose(P, Q, k):
    if k <= 0: return P
    if k >= 1: return Q
    out = {b: blend_m(P[b], Q[b], k) if b in Q else P[b] for b in P if b != "__pelvis"}
    out["__pelvis"] = P["__pelvis"].lerp(Q["__pelvis"], k); return out

# ---- two-bone IK + hand orientation (from char_scene.py)
def solve_arm(arm, side, target, pole):
    pb = arm.pose.bones; ua, fa, hd = pb[f"Bip01 {side} UpperArm"], pb[f"Bip01 {side} Forearm"], pb[f"Bip01 {side} Hand"]
    for b in (ua, fa, hd): b.matrix_basis = Matrix.Identity(4)
    bpy.context.view_layer.update()
    inv = arm.matrix_world.inverted(); T = inv @ Vector(target); P = inv @ Vector(pole)
    Sh, El, Wr = ua.head.copy(), fa.head.copy(), hd.head.copy(); l1, l2 = (El - Sh).length, (Wr - El).length
    d = min((T - Sh).length, (l1 + l2) * 0.999); n = (T - Sh).normalized(); T = Sh + n * d
    a_ = (l1 * l1 - l2 * l2 + d * d) / (2 * d); h = math.sqrt(max(0.0, l1 * l1 - a_ * a_))
    v = (P - Sh) - (P - Sh).dot(n) * n; v = v.normalized() if v.length > 1e-6 else Vector((0, 0, -1))
    E2 = Sh + n * a_ + v * h
    def rot_about(b, pivot, q):
        b.matrix = Matrix.Translation(pivot) @ q.to_matrix().to_4x4() @ Matrix.Translation(-pivot) @ b.matrix
    rot_about(ua, Sh, (El - Sh).rotation_difference(E2 - Sh)); bpy.context.view_layer.update()
    El, Wr = fa.head.copy(), hd.head.copy(); rot_about(fa, El, (Wr - El).rotation_difference(T - El)); bpy.context.view_layer.update()
def orient_hand(arm, side, fingers, across):
    pb = arm.pose.bones; hd = pb[f"Bip01 {side} Hand"]; mw = arm.matrix_world; R3 = mw.to_3x3().normalized()
    Wp = mw @ hd.head; f = (mw @ pb[f"Bip01 {side} Finger2"].head - Wp).normalized()
    k = (mw @ pb[f"Bip01 {side} Finger4"].head - mw @ pb[f"Bip01 {side} Finger1"].head)
    def frame(f_, a_):
        f_ = Vector(f_).normalized(); a_ = (Vector(a_) - Vector(a_).dot(f_) * f_).normalized(); return Matrix((f_, a_, f_.cross(a_))).transposed()
    Rw = frame(fingers, across) @ frame(f, k).inverted(); Ra = (R3.inverted() @ Rw @ R3).to_4x4(); piv = hd.head.copy()
    hd.matrix = Matrix.Translation(piv) @ Ra @ Matrix.Translation(-piv) @ hd.matrix; bpy.context.view_layer.update()
def curl(arm, amount, sides=("L", "R")):
    for side in sides:
        for f in range(5):
            for kk in ("", "1", "2"):
                b = arm.pose.bones.get(f"Bip01 {side} Finger{f}{kk}")
                if b: b.matrix_basis = b.matrix_basis @ Euler((0, 0, math.radians(-amount * (0.5 if f == 0 else 1.0)))).to_matrix().to_4x4()
def bone_world(arm, bone, attr="head"):
    b = arm.pose.bones[bone]; return arm.matrix_world @ getattr(b, attr)
def rot_bone(arm, bone, deg_xyz):
    b = arm.pose.bones.get(bone)
    if b: b.matrix_basis = b.matrix_basis @ Euler([math.radians(v) for v in deg_xyz]).to_matrix().to_4x4()

# ---- faces: ARKit recipes (values before the 1.5x push), visemes, blinks
EXPR = {
    "neutral": {},
    "cheeky": {"mouthSmileLeft": 0.55, "mouthSmileRight": 0.4, "browOuterUpLeft": 0.5, "browInnerUp": 0.2, "cheekSquintLeft": 0.3},
    "happy": {"mouthSmileLeft": 0.55, "mouthSmileRight": 0.55, "cheekSquintLeft": 0.3, "cheekSquintRight": 0.3, "browInnerUp": 0.15},
    "sweet": {"mouthSmileLeft": 0.5, "mouthSmileRight": 0.5, "browInnerUp": 0.5, "eyeSquintLeft": 0.2, "eyeSquintRight": 0.2},
    "smug": {"mouthSmileLeft": 0.5, "mouthSmileRight": 0.15, "browDownRight": 0.35, "eyeSquintLeft": 0.3, "eyeSquintRight": 0.3},
    "surprised": {"browInnerUp": 0.6, "browOuterUpLeft": 0.5, "browOuterUpRight": 0.5, "eyeWideLeft": 0.5, "eyeWideRight": 0.5, "jawOpen": 0.12},
    "shock": {"browInnerUp": 0.7, "browOuterUpLeft": 0.6, "browOuterUpRight": 0.6, "eyeWideLeft": 0.7, "eyeWideRight": 0.7, "jawOpen": 0.25, "mouthStretchLeft": 0.25, "mouthStretchRight": 0.25},
    "angry": {"browDownLeft": 0.7, "browDownRight": 0.7, "noseSneerLeft": 0.4, "noseSneerRight": 0.4, "eyeSquintLeft": 0.3, "eyeSquintRight": 0.3, "mouthPressLeft": 0.3, "mouthPressRight": 0.3},
    "strain": {"browDownLeft": 0.6, "browDownRight": 0.6, "eyeSquintLeft": 0.5, "eyeSquintRight": 0.5, "mouthStretchLeft": 0.5, "mouthStretchRight": 0.5, "noseSneerLeft": 0.3, "noseSneerRight": 0.3},
    "panic": {"browInnerUp": 0.8, "eyeWideLeft": 0.7, "eyeWideRight": 0.7, "mouthStretchLeft": 0.4, "mouthStretchRight": 0.4, "jawOpen": 0.2},
    "tired": {"browInnerUp": 0.45, "eyeBlinkLeft": 0.25, "eyeBlinkRight": 0.25, "mouthFrownLeft": 0.3, "mouthFrownRight": 0.3, "jawOpen": 0.1},
    "incredulous": {"browInnerUp": 0.5, "browOuterUpLeft": 0.7, "browOuterUpRight": 0.3, "mouthFrownLeft": 0.2, "jawOpen": 0.1},
    "helpful": {"browInnerUp": 0.35, "browOuterUpLeft": 0.35, "browOuterUpRight": 0.35, "mouthSmileLeft": 0.2, "mouthSmileRight": 0.2},
    "focused": {"browDownLeft": 0.35, "browDownRight": 0.35, "eyeSquintLeft": 0.25, "eyeSquintRight": 0.25},
}
PUSH = 2.0
AU_ADD = {  # FACS action units layered on each expression (these shapes move the Rocketbox faces much more)
    "shock": {"AU_01_InnerBrowRaiser": 0.8, "AU_02_OuterBrowRaiser": 0.7, "AU_05_UpperLidRaiser": 0.7, "AU_26_JawDrop": 0.35},
    "panic": {"AU_01_InnerBrowRaiser": 0.9, "AU_05_UpperLidRaiser": 0.6, "AU_20_LipStretcher": 0.6, "AU_26_JawDrop": 0.25},
    "angry": {"AU_04_BrowLowerer": 0.9, "AU_07_LidTightener": 0.6, "AU_09_NoseWrinkler": 0.4, "AU_23_LipTightener": 0.4},
    "strain": {"AU_04_BrowLowerer": 0.8, "AU_07_LidTightener": 0.7, "AU_20_LipStretcher": 0.6, "AU_09_NoseWrinkler": 0.4},
    "surprised": {"AU_01_InnerBrowRaiser": 0.6, "AU_02_OuterBrowRaiser": 0.5, "AU_05_UpperLidRaiser": 0.4},
    "happy": {"AU_06_CheekRaiser": 0.6, "AU_12_LipCornerPuller": 0.7}, "cheeky": {"AU_12_L_LipCornerPuller": 0.8, "AU_06_L_CheekRaiser": 0.5, "AU_02_L_OuterBrowRaiser": 0.6},
    "sweet": {"AU_12_LipCornerPuller": 0.6, "AU_01_InnerBrowRaiser": 0.5, "AU_06_CheekRaiser": 0.3},
    "smug": {"AU_12_L_LipCornerPuller": 0.7, "AU_44_Squint": 0.3, "AU_04_BrowLowerer": 0.2},
    "tired": {"AU_41_LidDroop": 0.6, "AU_01_InnerBrowRaiser": 0.5, "AU_15_LipCornerDepressor": 0.4, "AU_25_LipsPart": 0.5},
    "incredulous": {"AU_01_InnerBrowRaiser": 0.6, "AU_02_L_OuterBrowRaiser": 0.9, "AU_15_LipCornerDepressor": 0.3},
    "helpful": {"AU_01_InnerBrowRaiser": 0.5, "AU_02_OuterBrowRaiser": 0.4, "AU_12_LipCornerPuller": 0.3},
    "focused": {"AU_04_BrowLowerer": 0.4, "AU_44_Squint": 0.3},
}
VIS_KEYS = ["AA_VI_00_Sil", "AA_VI_01_PP", "AA_VI_02_FF", "AA_VI_03_TH", "AA_VI_04_DD", "AA_VI_05_KK", "AA_VI_06_CH", "AA_VI_07_SS",
            "AA_VI_08_nn", "AA_VI_09_RR", "AA_VI_10_aa", "AA_VI_11_E", "AA_VI_12_I", "AA_VI_13_O", "AA_VI_14_U"]
def ak(KB, low):
    for n_, k_ in KB.items():
        if n_.startswith("AK_") and n_.split("_", 2)[-1].lower() == low.lower(): return k_
def set_face(C, t, who, expr_keys, lips=True, wink=None):
    KB = C["KB"]
    if not KB: return
    vals = {}
    # expression track with a 0.25 s cross-fade
    i = max([j for j, e in enumerate(expr_keys) if e[0] <= t], default=0)
    a_, b_ = expr_keys[max(0, i - 1)], expr_keys[i]; u = ramp(t, b_[0], b_[0] + 0.25) if i else 1.0
    au = {}
    for ex, w in ((a_[1], (1 - u) * a_[2]), (b_[1], u * b_[2])):
        for kn, v in EXPR[ex].items(): vals[kn] = vals.get(kn, 0) + v * w * PUSH
        for kn, v in AU_ADD.get(ex, {}).items(): au[kn] = au.get(kn, 0) + v * w * 1.5
    blink = 1.0 if ((t + 0.7 + hash(who) % 7 * 0.3) % 3.3) < 0.11 and t > 0.3 else 0.0
    for s in ("eyeBlinkLeft", "eyeBlinkRight"): vals[s] = max(vals.get(s, 0), blink)
    if wink and wink[0] <= t <= wink[1]: vals["eyeBlinkLeft"] = 1.0; vals["cheekSquintLeft"] = vals.get("cheekSquintLeft", 0) + 0.5
    for k_ in KB.values():
        if k_.name.startswith(("AK_", "AU_")): k_.value = 0.0
    for kn, v in vals.items():
        k_ = ak(KB, kn)
        if k_: k_.slider_max = 2.0; k_.value = min(1.6, v)
    for kn, v in au.items():
        if kn in KB: KB[kn].slider_max = 2.0; KB[kn].value = min(1.6, v)
    # visemes (lip sync from the real voice); a little extra jaw on loud syllables
    V = VIS["chars"].get(who); f = int(round(t * FPS))
    for vk in VIS_KEYS:
        if vk in KB: KB[vk].value = 0.0
    if lips and V and 0 <= f < len(V["visemes"]):
        w = V["visemes"][f]; env = V["env"][f]; gain = 0.55 + 0.55 * min(1.0, env)
        for vi, vv in enumerate(w):
            if vv > 0 and VIS_KEYS[vi] in KB: KB[VIS_KEYS[vi]].value = min(1.0, vv * gain)
        jk = ak(KB, "jawOpen")
        if jk: jk.value = min(1.0, jk.value + 0.18 * env)

# =====================================================================================================================
# cast + extras
C = {
    "YOU": load_char("Female_Adult_01", True, "tex"),
    "THIEF_A": load_char("Male_Adult_18", True, "tex"),
    "THIEF_B": load_char("Male_Adult_07", True, "tex", scale=1.18),
    "OLD_MAN": load_char("Male_Adult_03", True, "tex"),
    "SHOPPER": load_char("Female_Adult_04", True, "tex"),
}
beanie = sphere("beanie", 0.098, (0, 0, -50), mat("beanie", (0.04, 0.04, 0.05), 0.95), seg=16)
EXTRAS = []
ext_specs = [("Male_Adult_01", "m_walk_neutral", 1, 4.4, 1.25), ("Female_Adult_02", "f_walk_neutral_01", -1, 4.0, 1.15),
             ("Male_Adult_06", "m_walk_stroll_01", 1, 4.9, 1.0), ("Female_Adult_08", "f_walk_stroll_01", -1, 4.6, 1.0),
             ("Male_Adult_09", "m_walk_neutral", -1, 4.2, 1.2), ("Female_Adult_12", "f_walk_neutral", 1, 3.9, 1.15),
             ("Male_Adult_16", "m_walk_cool_01", -1, 5.0, 1.1), ("Female_Adult_17", "f_walk_stroll_01", 1, 4.5, 1.0)]
for i, (nm, clip, dirn, y, sp) in enumerate(ext_specs):
    c = load_char(nm, False, "tex"); c.update(clip=clip, dirn=dirn, y=y, speed=sp, x0=rnd.uniform(-22, 22)); EXTRAS.append(c)

# =====================================================================================================================
# choreography (all times from the voice timeline)
X0, VY, VSPD = 4.0, 2.9, 0.8                     # YOU: walks -x along y=2.9, strolling while scrolling
T_BUMP = S["L04"] - 0.08
def you_x(t): return X0 - VSPD * min(t, T_BUMP) + 0.28 * ramp(t, T_BUMP, T_BUMP + 0.35)   # stops at the bump, staggers back
BUMP_X = X0 - VSPD * T_BUMP
B_START, B_Y, B_SPD = L02N + 0.95, 3.45, None  # THIEF_B leaves the bus stop right after "judge this"
B_STOP = (8.3, 2.95)
B_PASS_X = BUMP_X - 0.15
B_SPD = (B_STOP[0] - B_PASS_X) / (T_BUMP - B_START)
T_RIP = S["L08"] - 0.02; T_CATCH = T_RIP + 0.75
B_END = (BUMP_X - 1.35, 3.25)                     # where he turns back ("Ooh, sorry, love!") and later catches the phone
A_KERB = (7.4, 1.75); A_ARRIVE = S["L06"] - 0.05; A_Y = 1.78
OLD_POS, SHOP_POS = (BUMP_X - 1.25, 3.85), (BUMP_X + 1.2, 3.8)
SPLIT_CAM_X, SPLIT_CAM_Y = BUMP_X - 3.3, 2.75               # split shot: B brushes past ~0.6 m to its left, the bus ~1.6 m to its right

def you_state(t):
    x = you_x(t); y = VY + 0.06 * ramp(t, T_BUMP, T_BUMP + 0.35)
    if t < T_BUMP: h = -90; clip, ct = "f_walk_stroll_01", t * 0.95
    elif t < S["L06"] - 0.2: h = lerp(-90, -70, ramp(t, T_BUMP, T_BUMP + 0.4)); clip, ct = "f_idle_neutral_01", t
    elif t < T_RIP + 0.2: h = lerp(-70, 0, ramp(t, S["L06"] - 0.2, S["L06"] + 0.25)); clip, ct = "f_idle_nervous_01", t
    elif t < S["L10"]:
        sw = math.sin((t - T_RIP) * 4.2) * ramp(t, S["L09"] - 0.1, S["L09"] + 0.2) * (1 - ramp(t, E["L09"] - 0.2, E["L09"] + 0.1))
        h = 0 + 55 * sw; clip, ct = "f_idle_nervous_02", t
    elif t < S["L13"]: h = 0; clip, ct = "f_idle_breathe_01", t
    else: h = lerp(0, -25, ramp(t, S["L14"], S["L14"] + 0.4)); clip, ct = "f_gestic_talk_excited_01", t - S["L13"]
    return Vector((x, y, 0)), h, clip, ct
def b_state(t):
    if t < B_START: return Vector((*B_STOP, 0)), 0, "m_idle_neutral_01", t
    if t < T_BUMP + 0.55:
        x = B_STOP[0] - B_SPD * (t - B_START); y = lerp(B_STOP[1], B_Y, ramp(t, B_START, B_START + 0.8))
        return Vector((x, y, 0)), -90, "m_walk_fast_01", (t - B_START) * 1.25
    if t < S["L09"] + 0.05:  # turned back toward her, waits, then catches
        p = Vector((lerp(B_PASS_X - 0.55 * 1.0, B_END[0], ramp(t, T_BUMP + 0.55, T_BUMP + 1.0)), lerp(B_Y, B_END[1], ramp(t, T_BUMP + 0.55, T_BUMP + 1.0)), 0))
        h = lerp(-90, 70, ramp(t, T_BUMP + 0.25, T_BUMP + 0.6)); return p, h, "m_idle_neutral_01", t
    tr = t - (S["L09"] + 0.05)                      # runs off -x: sprint 2 s, a jog, then (once the camera has caught up) a smug walk
    tw = T_LEAVE + 1.9 - (S["L09"] + 0.05)          # when he slows to a walk
    dx = 3.6 * min(tr, 2.0) + 2.6 * max(0.0, min(tr, tw) - 2.0) + 1.6 * max(0.0, tr - tw)
    clip = "m_run_fast_01" if tr < 2.0 else ("m_run_neutral" if tr < tw else "m_walk_fast_01")
    return Vector((B_END[0] - dx, B_END[1] + 0.3 * min(tr, 1), 0)), -90, clip, tr
def a_state(t):
    if t < T_BUMP: return Vector((*A_KERB, 0)), -90, 0.0
    if t < A_ARRIVE:
        u = ramp(t, T_BUMP, A_ARRIVE); return Vector((lerp(A_KERB[0], BUMP_X + 0.15, u), lerp(A_KERB[1], A_Y, u), 0)), -90, 0.0
    if t < S["L09"]: return Vector((BUMP_X + 0.15 + 0.12 * math.sin((t - A_ARRIVE) * 5) * (t < T_RIP), A_Y, 0)), -90, 0.0
    tr = t - S["L09"]; return Vector((BUMP_X + 0.15 + 1.2 * tr * tr + 1.2 * tr, A_Y - 0.4 * min(tr, 1), 0)), 90 * ramp(t, S["L09"], S["L09"] + 0.4) * 2 - 90, tr

def phone_state(t):
    """world location + rotation of the phone, and who holds it"""
    if t < S["L06"]:
        return "YOU_R", None
    if t < T_RIP:  # tug of war between her hands and A's hand
        pA = a_state(t)[0]; pY = you_state(t)[0]
        mid = Vector(((pA.x + pY.x) / 2, lerp(pY.y, pA.y, 0.42), 1.12))
        pull = math.sin((t - S["L06"]) * 7.5) * 0.09 + math.sin((t - S["L06"]) * 13.0) * 0.03
        return "TUG", (mid + Vector((0, -pull, 0.02 * math.sin(t * 9))), Euler((math.radians(80), 0, math.radians(10 * math.sin(t * 6)))))
    if t < T_CATCH:  # flies, spinning, up into B's hand
        u = (t - T_RIP) / (T_CATCH - T_RIP); pA = a_state(T_RIP)[0]; pY = you_state(T_RIP)[0]
        p0 = Vector(((pA.x + pY.x) / 2, lerp(pY.y, pA.y, 0.42), 1.12)); p1 = b_state(T_CATCH)[0] + Vector((0.1, -0.25, 2.25))
        p = p0.lerp(p1, u) + Vector((0, 0, 0.9 * math.sin(math.pi * u)))
        return "AIR", (p, Euler((u * 13.0, u * 7.0, u * 4.0)))
    return "B_R", None

# ---- per-frame posing
def place_arm(c, loc, heading):
    c["arm"].location = loc + Vector((0, 0, c["z0"])); r0 = c.setdefault("rot0", c["arm"].rotation_euler.copy())
    c["arm"].rotation_euler = (r0.x, r0.y, math.radians(heading - 90))   # the models face +x at rotation 0
def rig_info(c):
    if "order" not in c:
        bones = c["arm"].data.bones
        depth = lambda b: 0 if b.parent is None else 1 + depth(b.parent)
        c["order"] = [b.name for b in sorted(bones, key=depth)]
        c["rest"] = {b.name: b.matrix_local.copy() for b in bones}
        c["par"] = {b.name: (b.parent.name if b.parent else None) for b in bones}
    return c
def pose(c, P):
    """Retarget: each bone takes the clip's armature-space ORIENTATION; its position comes from the character's own
    skeleton (parent pose x rest offset). The root (pelvis) also takes the clip's position. Rest-pose differences
    between the clip rig (T-pose) and the model (A-pose) cancel out this way."""
    rig_info(c); pb = c["arm"].pose.bones; posed = {}
    one = Vector((1, 1, 1))
    for b in c["order"]:
        Rb = c["rest"][b]; p = c["par"][b]
        base = Rb if p is None else posed[p] @ c["rest"][p].inverted() @ Rb
        if b in P:
            M = P[b]; loc = M.to_translation() if p is None else base.to_translation()
            posed[b] = Matrix.LocRotScale(loc, M.to_quaternion(), one)
        else:
            posed[b] = base
        pb[b].matrix_basis = base.inverted() @ posed[b]
    bpy.context.view_layer.update()
def head(c): return bone_world(c["arm"], "Bip01 Head")
def head_est(who, t):
    """where a character's head will be this frame (their pose may not be set yet when someone else looks at them)"""
    if who == "THIEF_B": return b_state(t)[0] + Vector((0, 0, 1.92))
    if who == "THIEF_A": return a_state(t)[0] + Vector((0, 0, 1.72))
    if who == "YOU": return you_state(t)[0] + Vector((0, 0, 1.55))
def look(c, yaw=0.0, down=0.0, tilt=0.0):
    rot_bone(c["arm"], "Bip01 Neck", (tilt * 0.4, yaw * 0.4, down * 0.4)); rot_bone(c["arm"], "Bip01 Head", (tilt * 0.6, yaw * 0.6, down * 0.6))
def face_dir(c):
    arm = c["arm"]; bpy.context.view_layer.update(); H = bone_world(arm, "Bip01 Head")
    if arm.pose.bones.get("Bip01 LEye"):
        return H, ((bone_world(arm, "Bip01 LEye") + bone_world(arm, "Bip01 REye")) / 2 - H).normalized()
    return H, body_frame(c)[0]
def turn_bone_world(c, bone, q):
    """rotate a pose bone by a WORLD-space rotation q about its own head"""
    arm = c["arm"]; R3 = arm.matrix_world.to_3x3().normalized(); pb = arm.pose.bones[bone]
    Ra = (R3.inverted() @ q.to_matrix() @ R3).to_4x4(); piv = pb.head.copy()
    pb.matrix = Matrix.Translation(piv) @ Ra @ Matrix.Translation(-piv) @ pb.matrix; bpy.context.view_layer.update()
def gaze_bias(c):
    """elevation of (eyes - head joint) when the head is level (rest pose): the eyes sit forward AND up from the joint"""
    if "bias" in c: return c["bias"]
    arm = c["arm"]; pb = arm.pose.bones
    if not pb.get("Bip01 LEye"): c["bias"] = 0.0; return 0.0
    keep = {b.name: b.matrix_basis.copy() for b in pb}
    for b in pb: b.matrix_basis = Matrix.Identity(4)
    bpy.context.view_layer.update(); H = bone_world(arm, "Bip01 Head"); f = ((bone_world(arm, "Bip01 LEye") + bone_world(arm, "Bip01 REye")) / 2 - H).normalized()
    c["bias"] = math.asin(max(-1, min(1, f.z)))
    for b in pb: b.matrix_basis = keep[b.name]
    bpy.context.view_layer.update(); print("GAZE BIAS", c["name"], round(math.degrees(c["bias"]), 1)); return c["bias"]
def aim_quat(f, g, max_yaw=70, max_pitch=35, frac=1.0, bias=0.0):
    """world rotation turning direction f toward g: yaw about world Z, then pitch about the horizontal axis (no roll)"""
    fh, gh = Vector((f.x, f.y, 0)), Vector((g.x, g.y, 0))
    if fh.length < 1e-4 or gh.length < 1e-4: return Quaternion()
    fh.normalize(); gh.normalize()
    yaw = math.atan2(fh.cross(gh).z, fh.dot(gh)); yaw = max(-math.radians(max_yaw), min(math.radians(max_yaw), yaw)) * frac
    qy = Quaternion((0, 0, 1), yaw); f2 = qy @ f
    pf, pg = math.asin(max(-1, min(1, f2.normalized().z))) - bias, math.asin(max(-1, min(1, g.normalized().z)))
    dp = max(-math.radians(max_pitch), min(math.radians(max_pitch), pg - pf)) * frac
    ax = Vector((f2.x, f2.y, 0)).normalized().cross(Vector((0, 0, 1)))
    return Quaternion(ax, dp) @ qy
def look_at(c, point, w=1.0, max_yaw=70, max_pitch=35):
    """neck takes 40% of the turn, the head the rest; all in world space, so there is never a roll"""
    if os.environ.get("LOOKOFF"): return
    for bone, frac in (("Bip01 Neck", 0.4 * w), ("Bip01 Head", 1.0 * w)):
        H, f = face_dir(c); g = (Vector(point) - H).normalized()
        turn_bone_world(c, bone, aim_quat(f, g, max_yaw, max_pitch, frac, gaze_bias(c)))
def look_axes(c, yaw_left=0.0, down=0.0):
    """turn the head by angles relative to where it faces now (left +, down +), in world space"""
    if os.environ.get("LOOKOFF"): return
    H, f = face_dir(c); b = gaze_bias(c); fh = Vector((f.x, f.y, 0)).normalized()
    el = math.asin(max(-1, min(1, f.z))) - b - math.radians(down)              # true gaze elevation after the nod
    g = Quaternion((0, 0, 1), math.radians(yaw_left)) @ fh; g = Vector((g.x * math.cos(el), g.y * math.cos(el), math.sin(el)))
    look_at(c, H + g * 2.0)
def body_frame(c):
    mw = c["arm"].matrix_world; R3 = mw.to_3x3().normalized()
    f = (R3 @ Vector((0, -1, 0)) if False else None)
    h = c["arm"].rotation_euler.z + math.pi / 2; F = Vector((math.sin(h), -math.cos(h), 0)); Rt = F.cross(Vector((0, 0, 1)))
    return F, Rt  # forward, character's right
def hand_to(c, side, target, pole_off=(0, 0, -0.6), fingers=None, across=None):
    arm = c["arm"]; sh = bone_world(arm, f"Bip01 {side} UpperArm"); F, Rt = body_frame(c)
    pole = sh + Vector(pole_off) + (Rt * (0.5 if side == "R" else -0.5))
    solve_arm(arm, side, target, pole)
    if fingers: orient_hand(arm, side, fingers, across)

PREV = {}
def drive(c, key, loc, heading, clip, ct, loop=True):
    P = clip_pose(clip, ct, loop)
    last = PREV.get(key)
    if last and last[0] != clip:  # 0.3 s blend when the clip changes
        if "since" not in last[2]: last[2]["since"] = T_NOW; last[2]["from"] = last[1]
        k = ramp(T_NOW, last[2]["since"], last[2]["since"] + 0.3)
        P = blend_pose(last[2]["from"], P, k)
        if k >= 1: PREV[key] = (clip, P, {})
    else:
        PREV[key] = (clip, P, {})
    place_arm(c, loc, heading); pose(c, P); bpy.context.view_layer.update()

def set_frame(t):
    global T_NOW; T_NOW = t
    # ---------- YOU
    Y = C["YOU"]; loc, h, clip, ct = you_state(t); drive(Y, "YOU", loc, h, clip, ct)
    F, Rt = body_frame(Y); chest = bone_world(Y["arm"], "Bip01 Spine2")
    st, ph = phone_state(t)
    if st == "YOU_R":     # scrolling: phone in the right hand in front of her chest; eyes down on it until the bump
        tgt = chest + F * 0.30 + Rt * 0.06 + Vector((0, 0, -0.08))
        hand_to(Y, "R", tgt, (0, 0, -0.7), fingers=F * 0.3 + Vector((0, 0, 1)), across=-Rt)
        curl(Y["arm"], 45, ("R",))
        down = 22 * (1 - ramp(t, S["L01"] + 0.1, S["L01"] + 0.4)) if t < S["L03"] else 18 * (1 - ramp(t, T_BUMP, T_BUMP + 0.2))
        if t < S["L03"] + 0.6: look_at(Y, loc + F * 2.4 + Vector((0, 0, 1.5)))          # talking to the camera
        elif t < T_BUMP: look_axes(Y, down=18)                                                # scrolling
        else: look_at(Y, head_est("THIEF_B", t))
        hw = Y["arm"].matrix_world @ Y["arm"].pose.bones["Bip01 R Hand"].head
        phone.location = hw + F * 0.05 + Vector((0, 0, 0.05)); phone.rotation_euler = Euler((math.radians(60), 0, Y["arm"].rotation_euler.z))
    elif st == "TUG":
        p, r = ph; phone.location = p; phone.rotation_euler = r
        hand_to(Y, "R", p + Rt * 0.04 + F * -0.03, (0, 0, -0.6)); hand_to(Y, "L", p - Rt * 0.05 + F * -0.03, (0, 0, -0.6))
        curl(Y["arm"], 55); look_at(Y, head_est("THIEF_A", t))
    elif st == "AIR":
        p, r = ph; phone.location = p; phone.rotation_euler = r
        u = ramp(t, T_RIP, T_RIP + 0.35)
        hand_to(Y, "R", chest + F * 0.45 + Vector((0, 0, 0.35 * u)), (0, 0, -0.6)); hand_to(Y, "L", chest + F * 0.4 - Rt * 0.2 + Vector((0, 0, 0.3 * u)), (0, 0, -0.6))
        look_axes(Y, down=-25 * u)
    else:
        if S["L12"] <= t < S["L13"]:   # out of breath: hands on knees
            k = ramp(t, S["L12"], S["L12"] + 0.4) * (1 - ramp(t, S["L13"] - 0.35, S["L13"]))
            for b, ang in (("Bip01 Spine", 14), ("Bip01 Spine1", 16), ("Bip01 Spine2", 12)): rot_bone(Y["arm"], b, (0, 0, ang * k))
            bpy.context.view_layer.update()
            for side in ("L", "R"):
                knee = bone_world(Y["arm"], f"Bip01 {side} Calf")
                if k > 0.05: hand_to(Y, side, knee.lerp(bone_world(Y["arm"], f"Bip01 {side} Hand"), 1 - k) + F * 0.06, (0, 0, -0.5))
            look_axes(Y, down=-18 * k)
        elif S["L14"] <= t:            # shouting after the camera, arm up
            k = ramp(t, S["L14"], S["L14"] + 0.3); sh = bone_world(Y["arm"], "Bip01 R UpperArm")
            hand_to(Y, "R", sh + (F * 0.35 + Rt * 0.25 + Vector((0, 0, 0.55))) * k + Vector((0, 0, -0.5)) * (1 - k), (0, 0, -0.3))
        if t >= T_CATCH and t < S["L10"]: look_axes(Y, yaw_left=30 * math.sin((t - T_CATCH) * 4.2))
    set_face(Y, t, "YOU", [[0, "cheeky", 1], [S["L02"], "cheeky", 1], [S["L03"], "happy", 0.8], [T_BUMP, "surprised", 1],
                           [S["L05"], "sweet", 0.7], [S["L06"], "shock", 1], [S["L06"] + 0.5, "angry", 1], [T_RIP, "panic", 1],
                           [S["L10"], "panic", 0.6], [S["L12"], "tired", 1], [S["L13"], "incredulous", 1], [S["L14"], "angry", 1]],
             wink=(S["L02"] + 1.0, S["L02"] + 1.3))
    # ---------- THIEF_B (+ beanie)
    B = C["THIEF_B"]; loc, h, clip, ct = b_state(t); drive(B, "B", loc, h, clip, ct)
    F, Rt = body_frame(B); chest = bone_world(B["arm"], "Bip01 Spine2")
    if t < L02N + 0.75:            # looking at his own phone at the bus stop
        hand_to(B, "R", chest + F * 0.3 + Vector((0, 0, -0.05)), (0, 0, -0.7)); look_axes(B, down=15)
    elif t < B_START:                   # pockets it, nods to A
        nod = math.sin((t - L02N - 0.8) * 9) * 8 if t < L02N + 1.4 else 0; look_axes(B, yaw_left=35, down=nod)
    if st == "AIR" or (st == "B_R" and t < S["L09"] + 0.05):
        p = phone.location if st == "AIR" else b_state(T_CATCH)[0] + Vector((0.1, -0.25, 2.25))
        hand_to(B, "R", p, (0, 0, -0.4)); curl(B["arm"], 50 if st == "B_R" else 15, ("R",))
        if st == "B_R": phone.location = p; phone.rotation_euler = Euler((math.radians(70), 0, 0))
    elif st == "B_R":
        hand_to(B, "R", chest + F * 0.22 + Vector((0, 0, -0.05)), (0, 0, -0.7)); curl(B["arm"], 55, ("R",))
        hw = B["arm"].matrix_world @ B["arm"].pose.bones["Bip01 R Hand"].head; phone.location = hw; phone.rotation_euler = Euler((math.radians(70), 0, B["arm"].rotation_euler.z))
    hd = B["arm"].matrix_world @ B["arm"].pose.bones["Bip01 Head"].matrix
    beanie.matrix_world = hd @ Matrix.Translation((0.0, 0.0, 0.0)); beanie.matrix_world = Matrix.Translation(hd.to_translation() + Vector((0, 0, 0.165 * 1.18))) @ Matrix.Scale(1.18, 4) @ Matrix.Diagonal((1.0, 1.05, 0.72, 1.0))
    if T_BUMP - 0.2 <= t < S["L09"]: look_at(B, head(C["YOU"]) if st != "AIR" else phone.location)
    set_face(B, t, "THIEF_B", [[0, "neutral", 0], [L02N + 0.8, "smug", 0.8], [T_BUMP, "sweet", 1], [S["L06"], "smug", 1], [T_RIP, "focused", 1]])
    # ---------- THIEF_A on the e-bike
    Aa = C["THIEF_A"]; loc, h, tr = a_state(t)
    ebike.location = loc; ebike.rotation_euler = (0, 0, math.radians(h + 270))   # bike's own forward is +x; rider heading -90 = riding -x
    bpy.context.view_layer.update()
    bf =Vector((math.cos(ebike.rotation_euler.z), math.sin(ebike.rotation_euler.z), 0))  # bike forward (+x local)
    drive(Aa, "A", loc - bf * 0.22 + Vector((0, 0, 0.32)), h, "m_sit_chair_idle_neutral_01", t)
    bars = ebike.matrix_world
    gl, gr = bars @ Vector((0.38, 0.22, 1.08)), bars @ Vector((0.38, -0.22, 1.08))
    F, Rt = body_frame(Aa)
    if st == "TUG" and A_ARRIVE <= t < T_RIP:
        hand_to(Aa, "R", phone.location + Rt * 0.02, (0, 0, -0.5)); curl(Aa["arm"], 55, ("R",))
        hand_to(Aa, "L", gl if (gl - bone_world(Aa["arm"], "Bip01 L UpperArm")).length < (gr - bone_world(Aa["arm"], "Bip01 L UpperArm")).length else gr, (0, 0, -0.5))
    else:
        for side, g in (("L", gl), ("R", gr)):
            sh = bone_world(Aa["arm"], f"Bip01 {side} UpperArm"); g2 = gl if (gl - sh).length < (gr - sh).length else gr
            hand_to(Aa, side, g2, (0, 0, -0.5))
        curl(Aa["arm"], 50)
    if A_ARRIVE - 0.3 <= t < T_RIP: look_at(Aa, head(C["YOU"]))
    elif t < L02N + 0.6: look_at(Aa, head(C["YOU"]), 0.7)
    elif t < L02N + 1.5: look_axes(Aa, yaw_left=20, down=math.sin((t - L02N - 0.9) * 9) * 7)
    set_face(Aa, t, "THIEF_A", [[0, "focused", 0.5], [S["L06"], "strain", 1], [T_RIP, "smug", 0.8]])
    # ---------- bystanders
    O = C["OLD_MAN"]; drive(O, "O", Vector((*OLD_POS, 0)), -20, "m_idle_look_around_01", t)
    Sh = C["SHOPPER"]; drive(Sh, "S", Vector((*SHOP_POS, 0)), 15, "f_idle_look_around_01", t)
    for c, side, dirn, t0, t1 in ((O, "R", Vector((-1, 0, 0.25)), S["L10"] - 0.15, S["L12"] + 0.3), (Sh, "L", Vector((1, 0, 0.25)), S["L11"] - 0.15, S["L12"] + 0.5)):
        k = ramp(t, t0, t0 + 0.3) * (1 - ramp(t, t1, t1 + 0.4))
        if k > 0.02:
            shp = bone_world(c["arm"], f"Bip01 {side} UpperArm"); rest = bone_world(c["arm"], f"Bip01 {side} Hand")
            hand_to(c, side, rest.lerp(shp + dirn.normalized() * 0.62, k), (0, 0, -0.3))
    if t > S["L09"]: look_at(O, head(Y) if S["L10"] - 0.3 < t < S["L10"] + 0.4 else head(Y) + Vector((-6, 0, 0)), 0.8)
    if t > S["L09"]: look_at(Sh, head(Y) if t < S["L11"] or t > S["L11"] + 0.8 else head(Y) + Vector((6, 0, 0)), 0.8)
    set_face(O, t, "OLD_MAN", [[0, "neutral", 0], [S["L10"] - 0.2, "helpful", 1]])
    set_face(Sh, t, "SHOPPER", [[0, "neutral", 0], [S["L11"] - 0.2, "angry", 0.6]])
    # ---------- extras walking on the building side of the pavement
    for i, c in enumerate(EXTRAS):
        x = c["x0"] + c["dirn"] * c["speed"] * t
        x = (x + 30) % 60 - 30
        drive(c, f"X{i}", Vector((x, c["y"], 0)), 90 if c["dirn"] > 0 else -90, c["clip"], t * c["speed"] / 1.15 + i * 0.37)
    bus.location.x = bus_x(t)
    bpy.context.view_layer.update()

# =====================================================================================================================
# camera: shots anchored to lines. Each shot: (name, t0, t1, fn(t) -> (cam_loc, target, lens, focus_point))
cam = bpy.data.objects.new("cam", bpy.data.cameras.new("cam")); col.objects.link(cam); sc.camera = cam
cam.data.sensor_fit = "VERTICAL"; cam.data.sensor_height = 36; cam.data.dof.use_dof = True; cam.data.dof.aperture_fstop = 2.8; cam.data.clip_start = 0.05
fill_d = bpy.data.lights.new("cam_fill", "AREA"); fill_d.energy = 90; fill_d.size = 2.0; fill_d.color = (1.0, 0.9, 0.82)
fill = bpy.data.objects.new("cam_fill", fill_d); col.objects.link(fill); fill.parent = cam; fill.location = (0.35, 0.45, 0.2)   # soft key that travels with the camera: faces always read
fill_d.use_shadow = False
def shake(t, amp):
    return Vector((amp * math.sin(t * 13.1) * 0.6 + amp * 0.4 * math.sin(t * 29.3), amp * 0.5 * math.sin(t * 17.7), amp * math.sin(t * 11.3 + 1)))
def sh_vlog(t):   # walking backwards in front of her; background: A on the bike, the bus stop with B
    hY = head(C["YOU"]); p = Vector((you_x(t) - 2.4, VY - 0.35, 1.5)); return p, hY + Vector((0.2, 0, -0.16)), 34, hY
def sh_rack(t):
    p, tg, lens, foc = sh_vlog(t); k = ramp(t, L02N + 0.55, L02N + 0.85) * (1 - ramp(t, L02N + 1.45, L02N + 1.75))
    return p, tg, lens, foc.lerp(head(C["THIEF_B"]), k)
def sh_side(t):   # arcs from the front to her street side: reveals B closing in from behind
    hY = head(C["YOU"]); u = ramp(t, S["L03"], S["L03"] + 1.8)
    p0 = Vector((you_x(t) - 2.4, VY - 0.35, 1.5)); p1 = Vector((you_x(t) - 0.4, VY - 3.0, 1.45))
    return p0.lerp(p1, u), hY.lerp(hY + Vector((1.0, 0.2, -0.15)), u), lerp(34, 26, u), hY
def sh_bump(t):   # low angle two-shot from the kerb: his size
    m = (head(C["YOU"]) + head(C["THIEF_B"])) / 2; return Vector((BUMP_X - 0.6, 0.85, 0.85)), m + Vector((0, 0, -0.25)), 26, m
def sh_turn(t):
    hY = head(C["YOU"]); return Vector((BUMP_X - 1.0, 0.2, 1.4)) + shake(t, 0.01), hY + Vector((0.9, 0, -0.35)), 24, hY
def sh_struggle(t):
    hY = head(C["YOU"]); hA = head(C["THIEF_A"]); m = (hY + hA) / 2; u = ramp(t, S["L06"], S["L08"])
    p = Vector((m.x - lerp(2.7, 2.1, u), m.y - 0.15, 1.45)) + shake(t, 0.025)
    return p, m + Vector((0, -0.1, -0.25)), 24, m
def sh_rip(t):    # low angle up at the phone in the air; the bus wipes through at the end
    pp = phone.location.copy(); base = Vector((BUMP_X - 0.5, -0.9, 0.75))
    return base, Vector((BUMP_X - 0.6, 3.0, 1.75)).lerp(pp, 0.5), 22, Vector((BUMP_X - 0.6, 3.0, 1.6))
def sh_split(t):  # eye level on the pavement, looking along the street: B charges straight past the lens (one way), A bikes off
    # into the distance (the other way) with the bus overtaking him, and she spins between them. Nothing crosses the lens.
    hY = head(C["YOU"]); u = ramp(t, E["L08"] + 0.15, S["L10"])
    p = Vector((SPLIT_CAM_X - 0.25 * u, SPLIT_CAM_Y, 1.55)) + shake(t, 0.012)
    return p, hY + Vector((0, -0.3, -0.25)), lerp(34, 29, u), hY
def sh_bystanders(t):
    hY = head(C["YOU"]); u = ramp(t, S["L10"], S["L12"])
    return Vector((BUMP_X - 0.05, -0.3 - 0.25 * u, 1.5)), hY + Vector((0, 0.6, -0.35)), 24, hY
def sh_breath(t): # medium on her; B's back far down the street behind her
    hY = head(C["YOU"]); u = ramp(t, S["L12"], T_LEAVE)
    return Vector((BUMP_X + 2.1, VY - 1.4 + 0.2 * u, 1.25)), hY + Vector((-0.6, 0.1, -0.25)), lerp(30, 34, u), hY
def sh_leave(t):  # on "size of a fridge" the camera whips off her onto B (long lens), then flies after him and follows his
    # huge back down the street; she shrinks behind it, shouting (L14), and sulks in voice-over (L15)
    hY = head(C["YOU"]); hB = head(C["THIEF_B"]); w = ramp(t, T_LEAVE, T_LEAVE + 0.3)
    p0 = Vector((BUMP_X + 1.6, VY - 1.6, 1.4)).lerp(Vector((BUMP_X - 0.5, 2.4, 1.7)), w)
    bl = b_state(t)[0]; follow = Vector((bl.x + 3.2, bl.y - 0.9, 2.1))
    p = p0.lerp(follow, ramp(t, T_LEAVE + 0.55, T_LEAVE + 2.2))
    lens = lerp(lerp(30, 75, ramp(t, T_LEAVE + 0.1, T_LEAVE + 0.5)), 32, ramp(t, T_LEAVE + 0.9, T_LEAVE + 2.2))
    return p + shake(t, 0.03 * ramp(t, T_LEAVE + 0.55, T_LEAVE + 1.0)), hY.lerp(hB, w) + Vector((0, 0, -0.25 * ramp(t, T_LEAVE + 1.5, T_LEAVE + 2.2))), lens, hY.lerp(hB, w)
SHOTS = [("vlog", 0.0, S["L02"], sh_vlog), ("rack", S["L02"], S["L03"], sh_rack), ("side", S["L03"], T_BUMP - 0.05, sh_side),
         ("bump", T_BUMP - 0.05, S["L05"], sh_bump), ("turn", S["L05"], S["L06"] - 0.05, sh_turn), ("struggle", S["L06"] - 0.05, T_RIP - 0.05, sh_struggle),
         ("rip", T_RIP - 0.05, E["L08"] + 0.15, sh_rip), ("split", E["L08"] + 0.15, S["L10"], sh_split), ("bystanders", S["L10"], S["L12"], sh_bystanders),
         ("breath", S["L12"], T_LEAVE, sh_breath), ("leave", T_LEAVE, S["L16"], sh_leave)]
def set_cam(t):
    for name, t0, t1, fn in SHOTS:
        if t0 <= t < t1 or (name == SHOTS[-1][0] and t >= t0):
            p, tg, lens, foc = fn(t); cam.location = p; cam.rotation_euler = (tg - p).to_track_quat("-Z", "Y").to_euler()
            cam.data.lens = lens; cam.data.dof.focus_distance = max(0.3, (foc - p).length); return name

# =====================================================================================================================
sc.render.engine = "CYCLES"; sc.cycles.device = "CPU"; sc.cycles.samples = a.samples; sc.cycles.use_denoising = True
sc.cycles.max_bounces = 4; sc.cycles.transparent_max_bounces = 8; sc.cycles.diffuse_bounces = 2; sc.cycles.glossy_bounces = 2
sc.render.resolution_x, sc.render.resolution_y = a.res; sc.render.fps = FPS
if a.threads: sc.render.threads_mode = "FIXED"; sc.render.threads = a.threads
sc.view_settings.view_transform = "AgX"; sc.view_settings.look = "AgX - Punchy"
for name in list(CLIPS): pass
for clip in {"f_walk_stroll_01", "f_idle_neutral_01", "f_idle_nervous_01", "f_idle_nervous_02", "f_idle_breathe_01", "f_gestic_talk_excited_01",
             "m_idle_neutral_01", "m_walk_fast_01", "m_run_fast_01", "m_sit_chair_idle_neutral_01", "m_idle_look_around_01", "f_idle_look_around_01"} | {c["clip"] for c in EXTRAS}:
    bake(clip)
sc.frame_set(1)

def render_frame(f, path):
    t = f / FPS
    # warm up the clip blends with the previous frames' state so a single still matches the moving render
    set_frame(t); shot = set_cam(t); sc.render.filepath = os.path.abspath(path)
    t0 = time.time(); bpy.ops.render.render(write_still=True); print(f"rendered {path} shot={shot} t={t:.2f} {time.time() - t0:.1f}s", flush=True)

if a.dbg is not None:
    set_frame(a.dbg); print("CAM", set_cam(a.dbg), tuple(round(v, 2) for v in cam.location))
    for k_, c in C.items():
        arm = c["arm"]; hb = bone_world(arm, "Bip01 Head"); pv = bone_world(arm, "Bip01 Pelvis")
        mn = c["meshes"][0]; bb = [mn.matrix_world @ Vector(v) for v in mn.bound_box]
        print("DBG", k_, "arm", tuple(round(v, 2) for v in arm.location), "rot", tuple(round(math.degrees(v), 1) for v in arm.rotation_euler),
              "scale", tuple(round(v, 4) for v in arm.scale), "head", tuple(round(v, 2) for v in hb), "pelvis", tuple(round(v, 2) for v in pv),
              "mesh parent", mn.parent.name if mn.parent else None, "bbox z", round(min(v.z for v in bb), 2), round(max(v.z for v in bb), 2))
    Yc = C["YOU"]; arm = Yc["arm"]
    L_, R_ = bone_world(arm, "Bip01 LEye"), bone_world(arm, "Bip01 REye"); d = L_ - R_
    print("TILT eye-line deg", round(math.degrees(math.asin(d.z / d.length)), 1))
    for clip in ("f_idle_neutral_01", "f_idle_nervous_01", "f_walk_stroll_01"):
        P = clip_pose(clip, a.dbg); pose(Yc, P); L_, R_ = bone_world(arm, "Bip01 LEye"), bone_world(arm, "Bip01 REye"); d = L_ - R_
        print("TILT clip only", clip, round(math.degrees(math.asin(d.z / d.length)), 1))
    raise SystemExit
if a.test:
    od = "build/street_test"; os.makedirs(od, exist_ok=True); outs = []
    for name, t0, t1, fn in SHOTS:
        if a.shots and name not in a.shots: continue
        f = int(round((t0 + (t1 - t0) * {"rip": 0.22, "split": 0.25}.get(name, 0.55)) * FPS)); p = os.path.join(od, f"{name}_{f:04d}.png"); PREV.clear(); render_frame(f, p); outs.append((name, f, p))
    json.dump(outs, open(os.path.join(od, "index.json"), "w"))
elif a.one is not None:
    os.makedirs(a.out, exist_ok=True); render_frame(a.one, os.path.join(a.out, f"{a.one:04d}.png"))
elif a.list:
    os.makedirs(a.out, exist_ok=True)
    for f in a.list: PREV.clear(); render_frame(f, os.path.join(a.out, f"{f:04d}.png"))
else:
    os.makedirs(a.out, exist_ok=True)
    for f in range(a.frames[0], a.frames[1]):
        p = os.path.join(a.out, f"{f:04d}.png")
        if os.path.exists(p): set_frame(f / FPS); continue
        render_frame(f, p)
