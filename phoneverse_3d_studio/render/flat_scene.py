"""flat_scene.py: "Cheers, Biscuit" from "Bike." to "JESS!" (L16-L31), Blender 5 / bpy, Cycles CPU. Continues street_scene.py
(which renders up to L16) with the same characters, faces and lip sync (shared helpers in rig.py). Global frame numbers.

Sets (each one closed in, far apart in one Blender scene, so no light leaks between them):
  BIKE   (x=600) her pink phone in a delivery box on the back of an e-bike, street lights streaming past      "Bike."
  VAN    (x=900) the phone is thrown in through a van's side door; the door slams shut (wipe to black)       "Van."
  YARD   (x=300) a warehouse near Heathrow at dusk; a plane roars low overhead                               "Some dodgy warehouse near Heathrow."
  DEN    (x=40)  inside: the box of glowing phones (hers drops in, flaps close, HONG KONG stamp), the padlock,
                 the phone in spare parts; later the hooded figure at the laptop (L23 cutaway, L30-L31 ending)
  FLAT   (x=0)   three months later: You and Jess on the sofa at night (L19-L29)
Timing: every shot and action is anchored to the measured voice timeline and word times, never re-timed.

  .venv/bin/python render/flat_scene.py --test                  # one still per shot -> build/flat_test/
  .venv/bin/python render/flat_scene.py --one 1100              # one frame
  .venv/bin/python render/flat_scene.py --frames 900 2300       # a range (resumable) -> build/ep/NNNN.png
"""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import rig
from rig import *          # noqa: F401,F403  (resets Blender to an empty scene)
import biscuit_ui as UI

ap = argparse.ArgumentParser()
ap.add_argument("--test", action="store_true"); ap.add_argument("--one", type=int); ap.add_argument("--frames", nargs=2, type=int)
ap.add_argument("--samples", type=int, default=16); ap.add_argument("--res", nargs=2, type=int, default=[540, 960])
ap.add_argument("--step", type=int, default=1); ap.add_argument("--out", default="build/ep"); ap.add_argument("--shots", nargs="*"); ap.add_argument("--threads", type=int, default=0)
a = ap.parse_args(sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else None)
TL = {r["id"]: r for r in json.load(open(os.path.join(EP, "timeline.json")))}
S = {k: v["start"] for k, v in TL.items()}; E = {k: v["end"] for k, v in TL.items()}
WORDS = json.load(open(os.path.join(EP, "words.json")))
def W(line, word, end=False):
    k = lambda x: x["word"].lower().strip(".,!?'\"…")
    w = next(x for x in WORDS if x["line"] == line and (k(x) == word or k(x).startswith(word + " ")))   # "Hong Kong" is one token
    return w["end"] if end else w["start"]
T_END = E["L31"] + 1.6
UIC = os.path.join(ROOT, "build", "ui_cache"); os.makedirs(UIC, exist_ok=True)
sc.world = bpy.data.worlds.new("w"); sc.world.use_nodes = True; sc.world.node_tree.nodes["Background"].inputs[0].default_value = (0, 0, 0, 1)

# extra faces for this half (same recipe format as rig.EXPR / rig.AU_ADD)
EXPR.update({
    "guilty": {"browInnerUp": 0.7, "mouthPressLeft": 0.4, "mouthPressRight": 0.4, "mouthRollLower": 0.3, "eyeLookDownLeft": 0.3, "eyeLookDownRight": 0.3},
    "dread": {"browInnerUp": 0.6, "browDownLeft": 0.3, "eyeWideLeft": 0.3, "eyeWideRight": 0.3, "mouthFrownLeft": 0.35, "mouthFrownRight": 0.35},
    "excited": {"mouthSmileLeft": 0.7, "mouthSmileRight": 0.7, "browInnerUp": 0.5, "browOuterUpLeft": 0.5, "browOuterUpRight": 0.5, "eyeWideLeft": 0.4, "eyeWideRight": 0.4, "jawOpen": 0.15},
    "suspicious": {"browDownLeft": 0.5, "browOuterUpRight": 0.5, "eyeSquintLeft": 0.4, "eyeSquintRight": 0.2, "mouthPressLeft": 0.3},
    "proud": {"mouthSmileLeft": 0.45, "mouthSmileRight": 0.45, "browOuterUpLeft": 0.3, "browOuterUpRight": 0.3, "cheekSquintLeft": 0.2},
    "beaming": {"mouthSmileLeft": 0.85, "mouthSmileRight": 0.85, "cheekSquintLeft": 0.5, "cheekSquintRight": 0.5, "browInnerUp": 0.3},
})
AU_ADD.update({
    "guilty": {"AU_01_InnerBrowRaiser": 0.8, "AU_15_LipCornerDepressor": 0.4, "AU_24_LipPressor": 0.5},
    "dread": {"AU_01_InnerBrowRaiser": 0.7, "AU_04_BrowLowerer": 0.3, "AU_15_LipCornerDepressor": 0.5},
    "excited": {"AU_06_CheekRaiser": 0.6, "AU_12_LipCornerPuller": 0.8, "AU_01_InnerBrowRaiser": 0.5, "AU_02_OuterBrowRaiser": 0.5},
    "suspicious": {"AU_04_BrowLowerer": 0.5, "AU_02_R_OuterBrowRaiser": 0.7, "AU_44_Squint": 0.4},
    "proud": {"AU_12_LipCornerPuller": 0.5, "AU_06_CheekRaiser": 0.3},
    "beaming": {"AU_06_CheekRaiser": 0.8, "AU_12_LipCornerPuller": 0.9},
})

# =====================================================================================================================
# shared props
def img_mat(name, strength=1.6):
    """emissive screen material driven by an image we swap per frame"""
    m = bpy.data.materials.new(name); m.use_nodes = True; nt = m.node_tree
    for nd in list(nt.nodes): nt.nodes.remove(nd)
    tx = nt.nodes.new("ShaderNodeTexImage"); em = nt.nodes.new("ShaderNodeEmission"); ou = nt.nodes.new("ShaderNodeOutputMaterial")
    im = bpy.data.images.new(name + "_img", 8, 8); tx.image = im
    nt.links.new(tx.outputs["Color"], em.inputs["Color"]); em.inputs["Strength"].default_value = strength; nt.links.new(em.outputs[0], ou.inputs[0])
    return m, tx
SCREEN_KEY = {}
def show(tx, key, make):
    """put a PIL screen on a texture node; `key` caches it (identical screens are drawn once)"""
    if SCREEN_KEY.get(tx.name) == key: return
    p = os.path.join(UIC, key.replace(" ", "_") + ".png")
    if not os.path.exists(p): make().resize((540, 960) if "lap" not in key and "label" not in key else make().size).save(p)
    if tx.image.filepath != p:
        tx.image = bpy.data.images.load(p, check_existing=True)
    SCREEN_KEY[tx.name] = key
def make_phone(name, case_rgb):
    body = box(name, (0.074, 0.152, 0.009), (0, 0, -80), mat(name + "_case", case_rgb, 0.45), bevel=0.003)
    m, tx = img_mat(name + "_scr"); bpy.ops.mesh.primitive_plane_add(size=1, location=(0, 0, 0.0047)); s = bpy.context.active_object
    s.name = name + "_screen"; s.scale = (0.066, 0.143, 1); bpy.ops.object.transform_apply(scale=True); s.data.materials.append(m); s.parent = body
    return body, tx
def aim_screen(phone, at):
    """turn a phone so its screen (local +Z) faces the point `at` (local +Y = up)"""
    n = (Vector(at) - phone.location).normalized(); phone.rotation_euler = n.to_track_quat("Z", "Y").to_euler()
def dome(center, radius, top, bottom, name):
    """a big emissive sky sphere around an open-air set (the world stays black, so other sets never see this sky)"""
    m = bpy.data.materials.new(name); m.use_nodes = True; nt = m.node_tree
    for nd in list(nt.nodes): nt.nodes.remove(nd)
    tc = nt.nodes.new("ShaderNodeTexCoord"); sep = nt.nodes.new("ShaderNodeSeparateXYZ"); mr = nt.nodes.new("ShaderNodeMapRange")
    mr.inputs["From Min"].default_value = -0.1; mr.inputs["From Max"].default_value = 0.6
    cr = nt.nodes.new("ShaderNodeValToRGB"); cr.color_ramp.elements[0].color = (*bottom, 1); cr.color_ramp.elements[1].color = (*top, 1)
    em = nt.nodes.new("ShaderNodeEmission"); em.inputs["Strength"].default_value = 1.0; ou = nt.nodes.new("ShaderNodeOutputMaterial")
    nt.links.new(tc.outputs["Normal"], sep.inputs[0]); nt.links.new(sep.outputs["Z"], mr.inputs["Value"]); nt.links.new(mr.outputs[0], cr.inputs["Fac"])
    nt.links.new(cr.outputs["Color"], em.inputs["Color"]); nt.links.new(em.outputs[0], ou.inputs[0])
    o = sphere(name, radius, center, m, seg=32); o.visible_shadow = False
    for f in o.data.polygons: f.use_smooth = True
    md = o.modifiers.new("flip", "SOLIDIFY"); md.thickness = 0.5; return o
def lamp(name, kind, loc, energy, color, size=0.5, aim=None, shadow=True):
    d = bpy.data.lights.new(name, kind); d.energy = energy; d.color = color; d.use_shadow = shadow
    if kind == "AREA": d.size = size
    elif kind in ("POINT", "SPOT"): d.shadow_soft_size = size
    o = bpy.data.objects.new(name, d); col.objects.link(o); o.location = loc
    if aim is not None: o.rotation_euler = (Vector(aim) - Vector(loc)).to_track_quat("-Z", "Y").to_euler()
    return o
def room(c, sx, sy, sz, wall_m, floor_m, ceil_m=None):
    cx, cy, cz = c
    box("floor", (sx, sy, 0.1), (cx, cy, cz - 0.05), floor_m); box("ceil", (sx, sy, 0.1), (cx, cy, cz + sz + 0.05), ceil_m or wall_m)
    for dx, dy, w_, d_ in ((sx / 2, 0, 0.1, sy), (-sx / 2, 0, 0.1, sy), (0, sy / 2, sx, 0.1), (0, -sy / 2, sx, 0.1)):
        box("wall", (w_, d_, sz), (cx + dx, cy + dy, cz + sz / 2), wall_m)

OLD, OLD_TX = make_phone("oldphone", (0.85, 0.28, 0.45))        # her stolen phone: the pink case from the street
NEW, NEW_TX = make_phone("newphone", (0.35, 0.75, 0.62))        # three months later: mint case
PARTS = []                                                      # the stolen phone again, as spare parts (J7)

# =====================================================================================================================
# BIKE (x=600): the back of an e-bike at night, street lights stream past (the world moves, the bike stays)
OB = Vector((600, 0, 0))
dome(OB, 90, (0.05, 0.07, 0.16), (0.012, 0.012, 0.02), "bike_sky")
box("bk_road", (200, 14, 0.1), OB + Vector((0, 0, -0.05)), noise_mat("bk_asphalt", (0.05, 0.05, 0.055), (0.09, 0.09, 0.1), 60))
bk_rig = empty("bk_stream", OB)
lampmat = emit_mat("bk_lamp", (1.0, 0.72, 0.4), 60); dash = emit_mat("bk_dash", (0.9, 0.9, 0.85), 0.6); post = mat("bk_post", (0.1, 0.1, 0.11), 0.5, 0.6)
for i in range(16):
    x = -60 + i * 8
    for side in (-1, 1):
        cyl(f"bk_post{i}{side}", 0.06, 5.5, (x, side * 5.5, 2.75), post, parent=bk_rig)
        sphere(f"bk_lamp{i}{side}", 0.22, (x, side * 5.0, 5.4), lampmat, seg=10, parent=bk_rig).visible_shadow = False
    box(f"bk_dash{i}", (2.5, 0.12, 0.01), (x, -1.5, 0.006), dash, parent=bk_rig)
    for k in range(4):   # lit windows of the buildings either side
        box(f"bk_win{i}{k}", (1.2, 0.05, 0.9), (x + rnd.uniform(-3, 3), 9.0 * (1 if k % 2 else -1), rnd.uniform(1.5, 7)),
            emit_mat(f"bk_w{i}{k}", rnd.choice([(1, 0.8, 0.5), (0.6, 0.75, 1.0), (1, 0.6, 0.3)]), rnd.uniform(1.5, 4)), parent=bk_rig)
yellow = mat("bk_yellow", (0.95, 0.75, 0.05), 0.4)
bike = empty("bk_bike", OB + Vector((0, 0, 0)))
box("bk_box_l", (0.42, 0.02, 0.3), (0, 0.2, 1.05), yellow, parent=bike); box("bk_box_r", (0.42, 0.02, 0.3), (0, -0.2, 1.05), yellow, parent=bike)
box("bk_box_f", (0.02, 0.42, 0.3), (0.2, 0, 1.05), yellow, parent=bike); box("bk_box_b", (0.02, 0.42, 0.3), (-0.2, 0, 1.05), yellow, parent=bike)
box("bk_box_bot", (0.42, 0.42, 0.02), (0, 0, 0.9), yellow, parent=bike)
box("bk_bag", (0.3, 0.3, 0.2), (0.02, 0.02, 1.0), mat("bk_bag", (0.2, 0.18, 0.16), 0.9), parent=bike)
bk_wheel = cyl("bk_wheel", 0.33, 0.06, OB + Vector((-0.05, 0, 0.33)), mat("bk_tyre", (0.02, 0.02, 0.02), 0.8), rot=(math.radians(90), 0, 0), verts=24)
box("bk_rack", (0.5, 0.04, 0.03), (0, 0.18, 0.88), post, parent=bike); box("bk_rack2", (0.5, 0.04, 0.03), (0, -0.18, 0.88), post, parent=bike)
lamp("bk_glow", "POINT", OB + Vector((0.1, 0, 1.25)), 14, (0.7, 0.8, 1.0), 0.05)
lamp("bk_key", "AREA", OB + Vector((-1.2, -1.0, 2.2)), 60, (1.0, 0.75, 0.45), 1.0, OB + Vector((0, 0, 1)))

# =====================================================================================================================
# VAN (x=900): inside a van, looking at its open side door; dusk street outside on a backdrop
OV = Vector((900, 0, 0))
vanm = mat("van_in", (0.5, 0.5, 0.52), 0.7, 0.2); vfloor = mat("van_floor", (0.12, 0.12, 0.13), 0.8)
box("van_floor", (3.2, 1.8, 0.05), OV + Vector((0, 0, 0.45)), vfloor); box("van_roof", (3.2, 1.8, 0.05), OV + Vector((0, 0, 1.9)), vanm)
box("van_back", (3.2, 0.05, 1.5), OV + Vector((0, 0.9, 1.18)), vanm); box("van_end1", (0.05, 1.8, 1.5), OV + Vector((1.6, 0, 1.18)), vanm)
box("van_end2", (0.05, 1.8, 1.5), OV + Vector((-1.6, 0, 1.18)), vanm)
box("van_side_a", (1.6, 0.05, 1.5), OV + Vector((-0.8 - 0.4, -0.9, 1.18)), vanm)     # the side wall left of the door gap (gap x -0.4..0.8)
box("van_side_b", (0.8, 0.05, 1.5), OV + Vector((1.2, -0.9, 1.18)), vanm)
van_door = box("van_door", (1.25, 0.05, 1.45), OV + Vector((-1.1, -0.96, 1.18)), mat("van_door", (0.85, 0.85, 0.87), 0.4, 0.3))
for i in range(5):  # junk on the floor: bags, a crate, a few other phones
    box(f"van_bag{i}", (rnd.uniform(0.25, 0.45), rnd.uniform(0.2, 0.35), rnd.uniform(0.15, 0.3)), OV + Vector((rnd.uniform(-1.4, 1.4), rnd.uniform(0.2, 0.7), 0.6)),
        mat(f"van_bag{i}", rnd.choice([(0.1, 0.1, 0.12), (0.25, 0.2, 0.15), (0.3, 0.05, 0.05)]), 0.9), rot=(0, 0, rnd.uniform(-0.5, 0.5)))
bd = bpy.data.materials.new("van_backdrop"); bd.use_nodes = True; nt = bd.node_tree
for nd in list(nt.nodes): nt.nodes.remove(nd)
br = nt.nodes.new("ShaderNodeTexBrick"); br.inputs["Color1"].default_value = (1.0, 0.75, 0.4, 1); br.inputs["Color2"].default_value = (0.25, 0.3, 0.5, 1)
br.inputs["Mortar"].default_value = (0.06, 0.06, 0.1, 1); br.inputs["Scale"].default_value = 3.0; br.inputs["Mortar Size"].default_value = 0.08
em = nt.nodes.new("ShaderNodeEmission"); em.inputs["Strength"].default_value = 2.2; ou = nt.nodes.new("ShaderNodeOutputMaterial")
nt.links.new(br.outputs["Color"], em.inputs["Color"]); nt.links.new(em.outputs[0], ou.inputs[0])
box("van_outside", (14, 0.05, 6), OV + Vector((0, -5, 2.0)), bd)
box("van_kerb", (14, 4, 0.05), OV + Vector((0, -3, 0.2)), mat("van_pav", (0.3, 0.3, 0.32), 0.9))
lamp("van_dusk", "AREA", OV + Vector((0.2, -2.5, 1.6)), 120, (1.0, 0.7, 0.45), 2.0, OV + Vector((0.2, 0, 0.8)))
van_light = lamp("van_ceil", "AREA", OV + Vector((0, 0, 1.85)), 45, (0.9, 0.95, 1.0), 0.6, OV + Vector((0, 0, 0)))

# =====================================================================================================================
# YARD (x=300): a dodgy warehouse near Heathrow at dusk, a plane low overhead
OX = Vector((300, 0, 0))
dome(OX, 140, (0.05, 0.1, 0.3), (0.9, 0.42, 0.18), "yard_sky")
box("yd_ground", (200, 200, 0.1), OX + Vector((0, 0, -0.05)), noise_mat("yd_tarmac", (0.08, 0.08, 0.09), (0.16, 0.16, 0.17), 30))
corr = bpy.data.materials.new("yd_corr"); corr.use_nodes = True; nt = corr.node_tree; b = nt.nodes["Principled BSDF"]
wv = nt.nodes.new("ShaderNodeTexWave"); wv.inputs["Scale"].default_value = 18; cr = nt.nodes.new("ShaderNodeValToRGB")
cr.color_ramp.elements[0].color = (0.26, 0.29, 0.3, 1); cr.color_ramp.elements[1].color = (0.42, 0.45, 0.46, 1)
tc = nt.nodes.new("ShaderNodeTexCoord"); nt.links.new(tc.outputs["Object"], wv.inputs["Vector"]); nt.links.new(wv.outputs["Fac"], cr.inputs["Fac"])
nt.links.new(cr.outputs["Color"], b.inputs["Base Color"]); b.inputs["Metallic"].default_value = 0.5; b.inputs["Roughness"].default_value = 0.5
box("yd_shed", (22, 14, 7), OX + Vector((0, 10, 3.5)), corr); box("yd_roof", (22.6, 14.6, 0.4), OX + Vector((0, 10, 7.1)), mat("yd_roofm", (0.2, 0.21, 0.22), 0.6))
box("yd_door", (6, 0.1, 4.5), OX + Vector((-3, 2.98, 2.25)), mat("yd_rollerm", (0.55, 0.55, 0.57), 0.5, 0.4))
box("yd_sign", (4.2, 0.1, 0.9), OX + Vector((5, 2.96, 5.4)), mat("yd_signbg", (0.9, 0.9, 0.88), 0.6))
text("UNIT 7", OX + Vector((5, 2.88, 5.4)), 0.55, mat("yd_signtxt", (0.1, 0.1, 0.12), 0.6), extrude=0.01)
lamp("yd_secl", "SPOT", OX + Vector((2, 2.6, 5.0)), 900, (1.0, 0.85, 0.6), 0.2, OX + Vector((0, -3, 0)))
sphere("yd_bulb", 0.12, OX + Vector((2, 2.8, 5.0)), emit_mat("yd_bulbm", (1, 0.9, 0.7), 20))
for i in range(10):  # fence posts in the foreground
    cyl(f"yd_post{i}", 0.04, 2.2, OX + Vector((-12 + i * 2.6, -6, 1.1)), mat("yd_fence", (0.25, 0.27, 0.27), 0.5, 0.7))
box("yd_wire", (26, 0.02, 1.8), OX + Vector((0, -6, 1.2)), glass_mat("yd_wirem", (0.5, 0.5, 0.5)))
plane = empty("yd_plane", OX + Vector((-120, 20, 45)))
pm = mat("yd_planem", (0.85, 0.86, 0.88), 0.35, 0.3)
cyl("pl_body", 1.9, 38, (0, 0, 0), pm, rot=(0, math.radians(90), 0), verts=24, parent=plane)
box("pl_wing", (7, 36, 0.4), (1, 0, -0.6), pm, parent=plane); box("pl_tail", (4, 0.4, 6), (-17, 0, 3), pm, parent=plane)
box("pl_stab", (3.5, 12, 0.3), (-17, 0, 0.5), pm, parent=plane)
for nm, y, c in (("pl_navl", 18, (1, 0.1, 0.1)), ("pl_navr", -18, (0.1, 1, 0.2))):
    sphere(nm, 0.35, (1, y, -0.5), emit_mat(nm + "m", c, 80), seg=8, parent=plane)
pl_strobe = sphere("pl_strobe", 0.4, (0, 0, -2.0), emit_mat("pl_strobem", (1, 1, 1), 0), seg=8, parent=plane)
lamp("yd_sun", "SUN", OX, 1.2, (1.0, 0.6, 0.35)).rotation_euler = (math.radians(80), 0, math.radians(-40))

# =====================================================================================================================
# DEN (x=40): the warehouse inside. Bench along y=-0.75, the hooded figure faces -y. Box of phones, laptop, her old phone
OD = Vector((40, 0, 0))
room((40, 0, 0), 7, 7, 3.2, mat("dn_wall", (0.09, 0.085, 0.09), 0.95), noise_mat("dn_floor", (0.06, 0.06, 0.065), (0.11, 0.11, 0.115), 20))
wood = mat("dn_bench", (0.16, 0.11, 0.07), 0.7)
box("dn_bench", (2.6, 0.8, 0.05), OD + Vector((0, -0.75, 0.76)), wood)
for dx in (-1.2, 1.2):
    for dy in (-1.05, -0.45): box("dn_leg", (0.05, 0.05, 0.76), OD + Vector((dx, dy, 0.38)), wood)
cardb = mat("dn_card", (0.62, 0.45, 0.28), 0.9)
for i in range(14):  # shelves of boxes on the wall he faces
    box(f"dn_shelfbox{i}", (rnd.uniform(0.4, 0.7), 0.4, rnd.uniform(0.3, 0.5)), OD + Vector((-2.5 + (i % 7) * 0.78, -2.95, 0.95 + (i // 7) * 0.75)), cardb, rot=(0, 0, rnd.uniform(-0.1, 0.1)))
for j in range(2): box("dn_shelf", (6, 0.5, 0.04), OD + Vector((0, -2.9, 0.72 + j * 0.75)), mat("dn_shelfm", (0.2, 0.2, 0.22), 0.5, 0.6))
lap_base = box("dn_lap_base", (0.36, 0.25, 0.018), OD + Vector((0.05, -0.62, 0.79)), mat("dn_lap", (0.06, 0.06, 0.07), 0.4, 0.5), bevel=0.004)
lap_lid = box("dn_lap_lid", (0.36, 0.012, 0.24), OD + Vector((0.05, -0.76, 0.905)), mat("dn_lap2", (0.06, 0.06, 0.07), 0.4, 0.5), rot=(math.radians(14), 0, 0), bevel=0.004)
lm_, LAP_TX = img_mat("dn_lapscr", 2.2); bpy.ops.mesh.primitive_plane_add(size=1, location=OD + Vector((0.05, -0.752, 0.905)), rotation=(math.radians(90 + 14), 0, 0))
lap_scr = bpy.context.active_object; lap_scr.scale = (0.33, 0.21, 1); lap_scr.data.materials.append(lm_)
# the open box of phones (left end of the bench): flaps hinge outwards; hers drops in on top
BX = OD + Vector((-0.75, -0.72, 0.785)); bw, bdp, bh = 0.46, 0.34, 0.2
box("bx_bot", (bw, bdp, 0.01), BX + Vector((0, 0, 0.005)), cardb)
for nm, dims, off in (("bx_n", (bw, 0.01, bh), (0, bdp / 2, bh / 2)), ("bx_s", (bw, 0.01, bh), (0, -bdp / 2, bh / 2)),
                      ("bx_e", (0.01, bdp, bh), (bw / 2, 0, bh / 2)), ("bx_w", (0.01, bdp, bh), (-bw / 2, 0, bh / 2))):
    box(nm, dims, BX + Vector(off), cardb)
FLAPS = []
for nm, dims, pivot, axis, sgn in (("fl_n", (bw, bdp / 2, 0.006), (0, bdp / 2, bh), "X", 1), ("fl_s", (bw, bdp / 2, 0.006), (0, -bdp / 2, bh), "X", -1),
                                   ("fl_e", (bw / 2, bdp, 0.006), (bw / 2, 0, bh), "Y", -1), ("fl_w", (bw / 2, bdp, 0.006), (-bw / 2, 0, bh), "Y", 1)):
    hinge = empty(nm + "_hinge", BX + Vector(pivot)); f = box(nm, dims, (0, 0, 0), cardb, parent=hinge)
    f.location = ((dims[0] / 2) * (1 if nm == "fl_e" else -1 if nm == "fl_w" else 0), (dims[1] / 2) * (1 if nm == "fl_n" else -1 if nm == "fl_s" else 0), 0)
    FLAPS.append((hinge, axis, sgn))
lbl_m, LBL_TX = img_mat("bx_label", 0.9); bpy.ops.mesh.primitive_plane_add(size=1, location=BX + Vector((0, 0, bh + 0.011)))
bx_label = bpy.context.active_object; bx_label.scale = (bw * 0.95, bdp * 0.95, 1); bx_label.data.materials.append(lbl_m)
stamp = empty("stamp", BX + Vector((0.05, -0.02, 0.9)))
cyl("stamp_handle", 0.03, 0.16, (0, 0, 0.12), mat("stamp_wood", (0.3, 0.17, 0.08), 0.6), parent=stamp)
box("stamp_base", (0.2, 0.08, 0.04), (0, 0, 0.02), mat("stamp_rubber", (0.12, 0.02, 0.02), 0.8), parent=stamp)
OTHERS = []
for i in range(36):  # other people's phones, screens glowing
    p, tx = make_phone(f"op{i}", rnd.choice([(0.05, 0.05, 0.06), (0.8, 0.8, 0.82), (0.2, 0.25, 0.45), (0.7, 0.55, 0.3), (0.1, 0.3, 0.2)]))
    gx, gy, gz = i % 6, (i // 6) % 3, i // 18
    p.location = BX + Vector((-0.17 + gx * 0.068 + rnd.uniform(-0.01, 0.01), -0.1 + gy * 0.1, 0.03 + gz * 0.05 + rnd.uniform(0, 0.03)))
    p.rotation_euler = (rnd.uniform(-0.5, 0.5), rnd.uniform(-0.4, 0.4), math.radians(90) + rnd.uniform(-0.4, 0.4))
    OTHERS.append((p, tx, rnd.choice(["lockB", "lockC", "dark", "lockB"])))   # only HER phone shows the purple lost-mode screen
# the hooded figure (back to us), seated on a stool
stool = cyl("dn_stool", 0.2, 0.5, OD + Vector((0, 0.15, 0.25)), mat("dn_stoolm", (0.04, 0.04, 0.045), 0.5), verts=20)
HOOD = load_char("Male_Adult_06", False, "tex")
hood_m = mat("hood_fabric", (0.035, 0.035, 0.04), 0.95)
for m_ in HOOD["meshes"]:
    for sl in m_.material_slots: sl.material = hood_m
hood = sphere("hood", 0.135, (0, 0, -60), hood_m, seg=32)
for f_ in hood.data.polygons: f_.use_smooth = True
lamp("dn_tube", "AREA", OD + Vector((0, 0.6, 3.0)), 70, (0.75, 0.9, 1.0), 1.4, OD + Vector((0, -0.6, 0.8)))
box("dn_tube_glow", (1.2, 0.08, 0.04), OD + Vector((0, 0.6, 3.12)), emit_mat("dn_tubem", (0.8, 0.95, 1.0), 6))
lap_glow = lamp("dn_lapglow", "AREA", OD + Vector((0.05, -0.68, 0.95)), 18, (1.0, 0.2, 0.15), 0.3, OD + Vector((0.05, 0.3, 1.2)))
lamp("dn_rim", "AREA", OD + Vector((1.4, 1.6, 2.0)), 45, (0.5, 0.6, 1.0), 0.8, OD + Vector((0, 0, 1.2)))
box_glow = lamp("dn_boxglow", "POINT", BX + Vector((0, 0, 0.16)), 3, (0.6, 0.75, 1.0), 0.1)
DEN_LIGHTS = [(o, o.data.energy) for o in bpy.data.objects if o.type == "LIGHT" and o.name in ("dn_tube", "dn_rim", "dn_lapglow")]
# her old phone as spare parts (J7): case, battery, board, screen (assembled = hidden; only used in the parts shot)
PART_SPECS = [("pt_case", (0.074, 0.152, 0.004), mat("pt_case", (0.85, 0.28, 0.45), 0.45), -0.006),
              ("pt_batt", (0.06, 0.09, 0.004), mat("pt_batt", (0.25, 0.26, 0.28), 0.4, 0.6), -0.002),
              ("pt_board", (0.064, 0.05, 0.002), mat("pt_board", (0.05, 0.35, 0.18), 0.5, 0.2), 0.001),
              ("pt_cam", (0.018, 0.018, 0.006), mat("pt_camm", (0.02, 0.02, 0.03), 0.2, 0.8), 0.003)]
parts_root = empty("parts_root", (0, 0, -90))
for nm, dims, m_, z in PART_SPECS:
    PARTS.append((box(nm, dims, (0, 0, z), m_, bevel=0.001, parent=parts_root), z))
pscr_m, PSCR_TX = img_mat("pt_screen", 1.8); bpy.ops.mesh.primitive_plane_add(size=1, location=(0, 0, 0.005)); pt_scr = bpy.context.active_object
pt_scr.scale = (0.068, 0.146, 1); bpy.ops.object.transform_apply(scale=True); pt_scr.data.materials.append(pscr_m); pt_scr.parent = parts_root
PARTS.append((pt_scr, 0.005))

# =====================================================================================================================
# FLAT (x=0): living room at night. Sofa along the back wall (y=+0.6), facing -y; TV glow from the front (off camera)
room((0, -0.6, 0), 6.4, 4.6, 2.7, mat("fl_wall", (0.32, 0.25, 0.3), 0.95), noise_mat("fl_floor", (0.25, 0.15, 0.08), (0.33, 0.2, 0.1), 8), mat("fl_ceil", (0.3, 0.28, 0.3), 0.95))
fab = mat("fl_sofa", (0.07, 0.24, 0.27), 0.92)
box("sofa_seat", (2.3, 0.85, 0.3), (0, 0.32, 0.17), fab, bevel=0.05); box("sofa_back", (2.3, 0.25, 0.75), (0, 0.78, 0.62), fab, bevel=0.06)
for x in (-1.2, 1.2): box("sofa_arm", (0.22, 0.85, 0.42), (x, 0.32, 0.38), fab, bevel=0.06)
for x in (-0.55, 0.55): box("sofa_cush", (1.1, 0.8, 0.12), (x, 0.3, 0.38), mat("fl_cush", (0.09, 0.28, 0.31), 0.95), bevel=0.04)
box("cushion1", (0.42, 0.14, 0.38), (-0.95, 0.62, 0.64), mat("fl_c1", (0.75, 0.42, 0.18), 0.95), rot=(math.radians(-12), 0, math.radians(14)), bevel=0.05)
box("cushion2", (0.4, 0.14, 0.36), (0.98, 0.62, 0.64), mat("fl_c2", (0.85, 0.75, 0.6), 0.95), rot=(math.radians(-12), 0, math.radians(-18)), bevel=0.05)
box("rug", (2.6, 1.8, 0.01), (0, -0.7, 0.005), mat("fl_rug", (0.65, 0.6, 0.52), 0.98))
box("table", (1.1, 0.55, 0.04), (0, -0.8, 0.4), mat("fl_table", (0.35, 0.22, 0.12), 0.5))
for x in (-0.5, 0.5):
    for y in (-1.02, -0.58): box("tleg", (0.04, 0.04, 0.38), (x, y, 0.19), mat("fl_table", (0.35, 0.22, 0.12), 0.5))
cyl("mug1", 0.045, 0.1, (-0.3, -0.75, 0.47), mat("fl_mug1", (0.9, 0.9, 0.88), 0.3)); cyl("mug2", 0.045, 0.1, (0.25, -0.88, 0.47), mat("fl_mug2", (0.85, 0.3, 0.3), 0.3))
box("remote", (0.05, 0.17, 0.02), (0.05, -0.7, 0.43), mat("fl_remote", (0.05, 0.05, 0.05), 0.4), rot=(0, 0, 0.4))
box("crisps", (0.16, 0.06, 0.22), (0.4, -0.72, 0.53), mat("fl_crisps", (0.85, 0.2, 0.25), 0.4), rot=(0.3, 0, -0.3))
box("window", (1.0, 0.03, 1.1), (-1.85, 1.66, 1.55), emit_mat("fl_win", (0.08, 0.15, 0.4), 1.4))
box("window_frame", (1.1, 0.04, 1.2), (-1.85, 1.68, 1.55), mat("fl_frame", (0.85, 0.85, 0.85), 0.5))
cyl("lamp_pole", 0.015, 1.5, (1.65, 1.2, 0.75), mat("fl_brass", (0.6, 0.45, 0.2), 0.3, 0.9))
cyl("lamp_shade", 0.2, 0.3, (1.65, 1.2, 1.55), emit_mat("fl_shade", (1.0, 0.62, 0.3), 5))
cyl("plant_pot", 0.16, 0.32, (-1.7, 1.1, 0.16), mat("fl_pot", (0.75, 0.4, 0.25), 0.7))
for i in range(9): sphere(f"leaf{i}", rnd.uniform(0.12, 0.2), (-1.7 + rnd.uniform(-0.2, 0.2), 1.1 + rnd.uniform(-0.15, 0.15), 0.5 + i * 0.09), mat("fl_leaf", (0.08, 0.3, 0.12), 0.7), seg=8)
fl_bulb = emit_mat("bulb", (1, 0.75, 0.35), 9)   # fairy lights along the back wall
for i in range(60): bsphere(0.014, (-2.6 + i * 0.09, 1.62, 2.25 - 0.12 * abs(math.sin(i * 0.35))), fl_bulb)
for i in range(4):  # framed pictures
    box(f"pic{i}", (0.42, 0.03, 0.32), (-0.9 + i * 0.6, 1.64, 1.55 + (i % 2) * 0.12), mat(f"fl_pic{i}", rnd.choice([(0.8, 0.5, 0.3), (0.3, 0.5, 0.7), (0.7, 0.7, 0.6), (0.6, 0.3, 0.5)]), 0.6))
flush_batches()
lamp("fl_lamp_key", "AREA", (1.4, 0.1, 1.9), 70, (1.0, 0.68, 0.4), 1.0, (0, 0.3, 1.1))
lamp("fl_lamp_pt", "POINT", (1.65, 1.2, 1.55), 30, (1.0, 0.62, 0.3), 0.15)
tv = lamp("fl_tv", "AREA", (0.2, -2.6, 1.0), 45, (0.55, 0.7, 1.0), 1.2, (0, 0.4, 1.0))
lamp("fl_rim", "AREA", (-1.8, 1.3, 2.1), 40, (0.55, 0.7, 1.0), 0.8, (0, 0.3, 1.1))
lamp("fl_ceil", "AREA", (0, -0.6, 2.6), 25, (1.0, 0.85, 0.7), 2.0, (0, -0.6, 0))

# =====================================================================================================================
# cast
C = {"YOU": load_char("Female_Adult_01", True, "tex"), "JESS": load_char("Female_Adult_15", True, "tex")}
SIT = "m_sit_chair_idle_neutral_01"
for clip in (SIT, "f_idle_neutral_01"): bake(clip)
SEAT_DZ = -0.40          # pelvis offset so the sitting clip rests on the cushions (calibrated with --dbg)
YOU_SEAT, JESS_SEAT = Vector((-0.42, 0.28, SEAT_DZ)), Vector((0.45, 0.26, SEAT_DZ))
OFFSTAGE = Vector((0, 0, -200))

# =====================================================================================================================
# shots: (name, t0, t1, set, fn(t) -> (cam_loc, target, lens, focus_point[, roll_deg]))
J_VAN, J_SOME, J_THEN, J_OFF = W("L16", "van"), W("L16", "some"), W("L16", "then"), W("L16", "off")
J_LOCK, J_WITHOUT = S["L17"] + 0.25, W("L17", "without")
T_PING = E["L19"] + 0.05
T_BOX, T_HONG, T_PADLOCK = W("L16", "box"), W("L16", "hong"), W("L17", "lock") + 0.15     # same anchors as the sound effects
F_YOUR, F_EASY = W("L20", "your"), W("L26", "easy")
def cam_of(loc, tgt, lens, foc=None, roll=0.0): return Vector(loc), Vector(tgt), lens, Vector(foc if foc is not None else tgt), roll
def sh_bike(t):
    u = ramp(t, S["L16"] - 0.2, J_VAN); c = OB + Vector((0.03, 0.02, 1.11))   # from behind-right, high: into the box + the street beyond
    return cam_of(OB + Vector((-0.5, -0.42, 1.72 - 0.04 * u)), c + Vector((0.22, 0.08, 0.06)), lerp(24, 28, u), c)
def sh_van(t):
    u = ramp(t, J_VAN, J_SOME); return cam_of(OV + Vector((0.3, 0.75, 0.75)), OV + Vector((0.2, -0.9, 1.0)), 18, OV + Vector((0.2, -0.3, 0.6)))
def sh_yard(t):
    u = ramp(t, J_SOME, J_THEN); return cam_of(OX + Vector((-6 + 3 * u, -13, 1.3)), OX + Vector((0, 3, 4.2 + 2.5 * u)), 18, OX + Vector((0, 3, 4)))
def sh_box(t):
    u = ramp(t, J_THEN, J_OFF); c = BX + Vector((0, 0, 0.12))
    return cam_of(c + Vector((0.2 - 0.04 * u, -0.3 + 0.04 * u, 0.48 - 0.1 * u)), c + Vector((0.02, 0, 0.02)), 32, c)
def sh_stamp(t):
    u = ramp(t, J_OFF, S["L17"] + 0.25); c = BX + Vector((0, 0, bh))
    return cam_of(c + Vector((0.06, -0.38, 0.62 - 0.1 * u)), c, 30, c)
def sh_lock(t):    # inside the dark box: her phone lights up with the padlock
    u = ramp(t, J_LOCK, J_WITHOUT); p = OLD.location
    return cam_of(p + Vector((0.02, -0.16 + 0.05 * u, 0.2 - 0.05 * u)), p, 40, p)
def sh_parts(t):
    u = ramp(t, J_WITHOUT, S["L19"] - 0.25); p = parts_root.location
    k = ramp(t, E["L18"] - 0.45, S["L19"])                                       # final push into the screen glow
    return cam_of(p + Vector((0.12 * (1 - u), -0.26 + 0.1 * u, 0.22 - 0.05 * u)).lerp(p + Vector((0, 0, 0.05)), k), p, lerp(38, 50, u), p)
def head_of(who): return bone_world(C[who]["arm"], "Bip01 Head")
def sh_two(t):     # wide two-shot, whip settle (L19)
    k = ramp(t, S["L19"], S["L19"] + 0.45); m = (head_of("YOU") + head_of("JESS")) / 2
    return cam_of(Vector((0.1, -2.25, 1.25)) + Vector((-1.6 * (1 - k), 0, 0)), m + Vector((0, 0, -0.32)), 24, m)
def sh_you_mcu(t, t0, t1, dx=0.0, push=0.25):
    u = ramp(t, t0, t1); h = head_of("YOU")
    return cam_of(h + Vector((0.42 + dx, -0.95 + push * u, -0.02)), h + Vector((0.02, 0, -0.08)), 40, h)
def sh_hold(t):    # Hold on: MCU on her face lit by the phone
    return sh_you_mcu(t, S["L20"], F_YOUR)
def sh_text(t):    # over the shoulder onto the screen
    u = ramp(t, F_YOUR, E["L20"]); p = NEW.location; h = head_of("YOU")
    eye = h + (p - h) * 0.25 + Vector((0.12, 0.05, 0.06))
    return cam_of(eye.lerp(p + (eye - p) * 0.55, u), p, 32, p)
def sh_jess(t):    # L21: two-shot favouring Jess bouncing
    hJ, hY = head_of("JESS"), head_of("YOU"); m = hJ * 0.65 + hY * 0.35
    return cam_of(Vector((-0.55, -1.35, 1.12)), m + Vector((0, 0, -0.18)), 30, hJ)
def sh_number(t):  # L22
    return sh_you_mcu(t, S["L22"], S["L23"], dx=-0.1, push=0.2)
def sh_den_lost(t):  # L23 cutaway: from behind the hood onto her old phone's lost-mode screen
    u = ramp(t, S["L23"], S["L24"]); p = OLD.location
    hh = bone_world(HOOD["arm"], "Bip01 Head"); start = hh + Vector((0.2, 0.72, 0.16)); end = p + Vector((0.05, 0.3, 0.32))
    return cam_of(start.lerp(end, ease(u)), p.lerp(OD + Vector((0.2, -0.7, 0.85)), 1 - u), lerp(28, 40, u), p)
def sh_babe(t):
    return sh_you_mcu(t, S["L24"], S["L25"], dx=0.05, push=0.3)
def sh_login(t):   # L25: her point of view onto the fake sign-in page (pushing in)
    u = ramp(t, S["L25"], S["L26"]); p = NEW.location; h = head_of("YOU")
    n = NEW.matrix_world.to_3x3() @ Vector((0, 0, 1)); up = NEW.matrix_world.to_3x3() @ Vector((0, 1, 0))   # straight onto the screen
    return cam_of(p + n * lerp(0.3, 0.2, u) + up * 0.02, p, 32, p)
def sh_rewatch(t):  # L26: past her shoulder (soft), Jess in focus behind, quietly typing on her phone
    hY, hJ = head_of("YOU"), head_of("JESS")
    return cam_of(hY + Vector((-0.55, -0.7, 0.05)), hJ + Vector((0, 0, -0.25)), 45, hJ)
def sh_easy(t):
    h = head_of("YOU"); return cam_of(h + Vector((0.25, -0.8, 0.0)), h + Vector((0, 0, -0.06)), 45, h)
def sh_late(t):    # L27: snap to Jess, guilty, phone up
    h = head_of("JESS"); u = ramp(t, S["L27"], S["L28"]); return cam_of(h + Vector((-0.2, -0.75 + 0.15 * u, 0.0)), h + Vector((0, 0, -0.12)), 45, h)
def sh_dread(t):   # L28: Dutch tilt, slow push as she turns
    h = head_of("YOU"); u = ramp(t, S["L28"], S["L29"])
    return cam_of(h + Vector((0.35, -0.85 + 0.25 * u, -0.05)), h + Vector((0, 0, -0.06)), 42, h, roll=lerp(4, 14, u))
def sh_biscuit(t):  # L29: two-shot, Jess beaming in front, You frozen
    hJ, hY = head_of("JESS"), head_of("YOU"); m = hJ * 0.6 + hY * 0.4
    return cam_of(Vector((0.95, -1.4, 1.1)), m + Vector((0, 0, -0.15)), 30, hJ)
def sh_den_end(t):  # L30-L31: behind the hood; her old phone flips to 'Hello'; he leans back
    u = ramp(t, S["L30"], E["L31"] + 1.0); p = OLD.location
    hh = bone_world(HOOD["arm"], "Bip01 Head")   # right behind him: the hood fills the frame, her phone glows past his shoulder
    return cam_of(hh + Vector((0.2 - 0.05 * u, 0.72 - 0.15 * u, 0.16)), hh.lerp(p, 0.55) + Vector((0, 0, -0.04)), 26, p)
SHOTS = [("bike", S["L16"] - 0.2, J_VAN, sh_bike), ("van", J_VAN, J_SOME, sh_van), ("yard", J_SOME, J_THEN, sh_yard), ("box", J_THEN, J_OFF, sh_box),
         ("stamp", J_OFF, J_LOCK, sh_stamp), ("lock", J_LOCK, J_WITHOUT, sh_lock), ("parts", J_WITHOUT, S["L19"], sh_parts),
         ("two", S["L19"], S["L20"], sh_two), ("hold", S["L20"], F_YOUR, sh_hold), ("text", F_YOUR, S["L21"], sh_text), ("jess", S["L21"], S["L22"], sh_jess),
         ("number", S["L22"], S["L23"], sh_number), ("den_lost", S["L23"], S["L24"], sh_den_lost), ("babe", S["L24"], S["L25"], sh_babe),
         ("login", S["L25"], S["L26"], sh_login), ("rewatch", S["L26"], F_EASY - 0.05, sh_rewatch), ("easy", F_EASY - 0.05, S["L27"], sh_easy),
         ("late", S["L27"], S["L28"], sh_late), ("dread", S["L28"], S["L29"], sh_dread), ("biscuit", S["L29"], S["L30"], sh_biscuit),
         ("den_end", S["L30"], T_END + 5, sh_den_end)]
def shot_at(t):
    for sh in SHOTS:
        if sh[1] <= t < sh[2]: return sh
    return SHOTS[0] if t < SHOTS[0][1] else SHOTS[-1]

# =====================================================================================================================
# per-frame action
VO = [(S["L16"] - 1, S["L20"]), (S["L23"], S["L24"])]          # her voice-over: mouth stays closed (lips only on lines spoken in scene)
def lips_on(t): return not any(t0 <= t < t1 for t0, t1 in VO)
def screen_new(t):
    if t < T_PING: return "new_lock", UI.new_lock
    if t < S["L25"]:
        p = round(min(1.0, (t - T_PING) / 0.35), 2); tap = round(clamp((t - S["L21"]) / 0.3) * (1 - clamp((t - S["L22"]) / 0.2)), 2)
        return f"found_{p}_{tap}", lambda: UI.found_text(p, tap)
    ty = 0.0 if t < S["L26"] else round(clamp((t - S["L26"] - 0.6) / max(0.5, F_EASY - S["L26"] - 1.0)), 2)
    sg = round(clamp((t - S["L27"] + 0.25) / 0.3), 2)
    return f"login_{ty}_{sg}", lambda: UI.fake_login(ty, sg)
def place_phone_in_hands(c, ph, dist=0.3, drop=-0.12, side_off=0.0, look=True, tilt_to=None):
    F, Rt = body_frame(c); chest = bone_world(c["arm"], "Bip01 Spine2"); h = bone_world(c["arm"], "Bip01 Head")
    p = chest + F * dist + Rt * side_off + Vector((0, 0, drop)); ph.location = p
    aim_screen(ph, tilt_to if tilt_to is not None else h + Vector((0, 0, 0.05)))
    R3 = ph.rotation_euler.to_matrix(); n = R3 @ Vector((0, 0, 1)); up = R3 @ Vector((0, 1, 0))
    axR = R3 @ Vector((1, 0, 0))             # from the phone centre toward the holder RIGHT hand (measured)
    # grip: each wrist just outside its edge and a little behind; fingers wrap behind the phone, index finger on top
    hand_to(c, "R", p + axR * 0.06 - n * 0.02 - up * 0.03, (0, 0, -0.6), fingers=-axR * 0.7 - n * 0.7 + up * 0.2, across=-up)
    hand_to(c, "L", p - axR * 0.06 - n * 0.02 - up * 0.03, (0, 0, -0.6), fingers=axR * 0.7 - n * 0.7 + up * 0.2, across=-up)
    curl(c["arm"], 40)
    return p
THIGH, CALF = float(os.environ.get("THIGH", "28")), float(os.environ.get("CALF", "-12"))
def sit_legs(c):
    """the chair clip sits upright with long legs: fold thighs forward and calves down so it reads as sitting on a sofa"""
    for s_ in "LR":
        rot_bone(c["arm"], f"Bip01 {s_} Thigh", (0, 0, THIGH)); rot_bone(c["arm"], f"Bip01 {s_} Calf", (0, 0, CALF))
    bpy.context.view_layer.update()
def set_frame(t):
    rig.T_NOW = t
    name = shot_at(t)[0]
    # ---------------- journey props
    bk_rig.location = OB + Vector(((t * 9.0) % 8.0, 0, 0)); bk_wheel.rotation_euler = (math.radians(90), t * 27.0, 0)
    if S["L16"] - 1 <= t < J_VAN:      # in the delivery box, screen glowing (still showing her lock screen)
        OLD.location = OB + Vector((0.02, 0.03, 1.11 + 0.004 * math.sin(t * 31))); OLD.rotation_euler = (math.radians(8), math.radians(-6), math.radians(80))
        show(OLD_TX, "old_lost", lambda: UI.lost_lock(0))
    elif t < J_SOME:                   # thrown into the van: an arc in through the door, then it skids to a stop
        u = clamp((t - J_VAN - 0.05) / 0.45); p0, p1 = OV + Vector((0.3, -2.2, 1.3)), OV + Vector((0.25, 0.2, 0.48))
        OLD.location = p0.lerp(p1, u) + Vector((0, 0, 0.6 * math.sin(math.pi * u))) + Vector((0, 0.12 * clamp((t - J_VAN - 0.5) / 0.25), 0))
        OLD.rotation_euler = (u * 9.0, u * 4.0, u * 2.0) if u < 1 else (0, 0, math.radians(30))
        door_k = ramp(t, J_SOME - 0.55, J_SOME - 0.12); van_door.location.x = OV.x - 1.1 + 1.25 * door_k
        van_light.data.energy = 45 * (1 - door_k)
    elif t < J_THEN:
        OLD.location = OFFSTAGE
    elif t < J_LOCK:                   # dropped into the box of phones
        u = clamp((t - max(J_THEN, T_BOX - 0.25)) / 0.4); OLD.location = BX + Vector((0.02, -0.01, lerp(0.75, 0.14, u * u)))
        OLD.rotation_euler = (math.radians(lerp(40, 4, u)), math.radians(lerp(-30, -3, u)), math.radians(lerp(120, 95, u)))
    elif t < J_WITHOUT:                # inside the closed box: it lights up with the padlock
        OLD.location = BX + Vector((0.02, -0.01, 0.14)); OLD.rotation_euler = (math.radians(4), math.radians(-3), math.radians(95))
    else:
        OLD.location = OFFSTAGE
    if J_THEN <= t < J_WITHOUT:
        pk = round(clamp((t - T_PADLOCK) / 0.25), 2)
        show(OLD_TX, "old_lockA" if t < T_PADLOCK else f"old_padlock_{pk}", (lambda: UI.lost_lock(0)) if t < T_PADLOCK else (lambda: UI.activation_lock(pk)))
    # flaps: open (folded out) until "off to Hong Kong", then close; the stamp slams after
    close = ramp(t, J_OFF - 0.45, J_OFF - 0.1)
    for hinge, axis, sgn in FLAPS:
        ang = lerp(-115, 0, close) * sgn; hinge.rotation_euler = (math.radians(ang), 0, 0) if axis == "X" else (0, math.radians(ang), 0)
    st = t - (T_HONG + 0.05 - 0.12); drop = 0.9 if st < 0 else (0.9 - 0.68 * clamp(st / 0.12) if st < 0.25 else 0.22 + 0.7 * clamp((st - 0.25) / 0.3))
    stamp.location = BX + Vector((0.05, -0.02, drop + bh))
    bx_label.location = BX + Vector((0, 0, bh + 0.011)) if st > 0.12 and t < S["L19"] else OFFSTAGE
    show(LBL_TX, "label_hk", UI.box_label)
    dark = ramp(t, J_LOCK - 0.1, J_LOCK + 0.3) * (1 - ramp(t, S["L19"] - 0.4, S["L19"]))
    box_glow.data.energy = 3 * (1 - dark) + 0.4 * dark
    inside = J_LOCK + 0.05 <= t < S["L19"]                     # "inside the box": lid off camera, the room almost dark
    for hinge, _, _ in FLAPS: hinge.hide_render = inside
    if inside: bx_label.location = OFFSTAGE
    for L_, e_ in DEN_LIGHTS: L_.data.energy = e_ * (0.06 if inside else 1.0)
    for p, tx, kind in OTHERS:
        show(tx, f"op_{kind}", (lambda: UI.lost_lock(0)) if kind == "lockA" else (lambda: UI.new_lock()) if kind == "lockB" else (lambda: UI.activation_lock(0.6)) if kind == "lockC" else (lambda: Image_black()))
    # spare parts (J7 + J8): drift apart along the stack axis, then snap back for the push in
    if J_WITHOUT <= t < S["L19"]:
        parts_root.location = BX + Vector((0.0, -0.01, 0.16)); parts_root.rotation_euler = (math.radians(-35), 0, math.radians(15 + 10 * (t - J_WITHOUT)))
        sp = ramp(t, J_WITHOUT + 0.1, J_WITHOUT + 0.7) * (1 - ramp(t, S["L18"] + 0.1, S["L18"] + 0.5))
        for k, (o, z) in enumerate(PARTS):
            o.location = (0.03 * sp * math.sin(k * 2.1), 0.02 * sp * math.cos(k * 1.7), z + sp * (k - 2) * 0.045)
            o.rotation_euler = (sp * 0.4 * math.sin(k + 1), sp * 0.3 * math.cos(k), 0)
        show(PSCR_TX, "old_padlock", lambda: UI.activation_lock(1.0))
    else:
        parts_root.location = Vector((0, 0, -90))
    # the plane over the yard (strobe blinks)
    plane.location = OX + Vector((-120 + 70 * (t - J_SOME + 0.6), 26, 42)); plane.rotation_euler = (0, math.radians(-4), 0)
    pl_strobe.active_material.node_tree.nodes["Emission"].inputs["Strength"].default_value = 200 if (t * 1.6) % 1.0 < 0.08 else 0
    # ---------------- the hooded figure (DEN): typing; leans back on "Cheers, Biscuit"
    show(LAP_TX, "lap_list", UI.laptop)
    lean = ramp(t, S["L30"] - 0.2, S["L30"] + 0.6)
    drive(HOOD, "HOOD", OD + Vector((0, 0.16, -0.3)), 0, SIT, t); sit_legs(HOOD)
    for b, ang in (("Bip01 Spine", -9 * lean), ("Bip01 Spine1", -9 * lean), ("Bip01 Spine2", 6 * (1 - lean))): rot_bone(HOOD["arm"], b, (0, 0, ang))
    bpy.context.view_layer.update()
    kb = OD + Vector((0.05, -0.55, 0.81)); F_, R_ = body_frame(HOOD)
    look_at(HOOD, (OD + Vector((0.45, -0.62, 0.79))) if S["L23"] <= t < S["L24"] or t >= S["L30"] else kb + Vector((0, -0.2, 0.15)), 0.7)
    for side, sx in (("L", 0.08), ("R", -0.08)):
        typing = Vector((0, 0.01 * math.sin(t * (23 if side == "L" else 19)), 0.012 * max(0, math.sin(t * (17 if side == "L" else 21)))))
        tgt = kb + Vector((sx, 0, 0)) + typing * (1 - lean)
        if side == "R" and lean > 0: tgt = tgt.lerp(OLD.location + Vector((0.02, 0.04, 0.03)), 0.0)
        hand_to(HOOD, side, tgt.lerp(bone_world(HOOD["arm"], "Bip01 Spine2") + F_ * 0.25 + Vector((0, 0, -0.15)) + R_ * (-sx * 2.5), lean), (0, 0, -0.5))
    hd = bone_world(HOOD["arm"], "Bip01 Head"); hm = HOOD["arm"].matrix_world @ HOOD["arm"].pose.bones["Bip01 Head"].matrix
    hood.matrix_world = Matrix.Translation(hd + hm.to_3x3() @ Vector((0.04, 0, 0)) + Vector((0, 0.03, 0.06))) @ Matrix.Diagonal((1.0, 1.1, 1.15, 1.0))
    if t >= S["L23"] - 0.5 and (S["L23"] - 0.5 <= t < S["L24"] or t >= S["L30"] - 0.5):   # her old phone on the bench
        OLD.location = OD + Vector((0.45, -0.62, 0.785)); OLD.rotation_euler = (0, 0, math.radians(-12))
        if t < S["L24"]:
            fl = round(clamp((t - W("L23", "lock") + 0.1) / 0.25) * (1 - clamp((t - W("L23", "lost", True) - 0.2) / 0.3)), 2)
            show(OLD_TX, f"old_lost_{fl}", lambda: UI.lost_lock(fl))
        else:
            hp = round(clamp((t - S["L30"] + 0.3) / 2.6), 2)           # flips to 'Hello' on the setup chime, just before "Cheers"
            if t < S["L30"] - 0.3: show(OLD_TX, "old_padlock", lambda: UI.activation_lock(1.0))
            else: show(OLD_TX, f"hello_{hp}", lambda: UI.hello(hp))
    # ---------------- the flat: You and Jess on the sofa
    Y, J = C["YOU"], C["JESS"]
    bounce = abs(math.sin((t - S["L21"]) * 8.5)) * 0.04 * ramp(t, S["L21"], S["L21"] + 0.2) * (1 - ramp(t, E["L21"] - 0.2, E["L21"] + 0.1))
    yh = 12 - 22 * ramp(t, S["L28"] - 0.1, S["L28"] + 0.9)                     # she turns to Jess on "Jess. What did you do?"
    drive(Y, "YOU", YOU_SEAT, yh, SIT, t * 0.6); sit_legs(Y)
    drive(J, "JESS", JESS_SEAT + Vector((0, 0, bounce)), -18 if t < S["L21"] else -30, SIT, t * 0.6 + 1.3); sit_legs(J)
    # who looks where: one look per character per frame, applied BEFORE the hands (the Biped's clavicles hang off the
    # neck, so a head turn after the IK would drag both arms off the phone)
    T_DOWN, T_PICK = S["L26"] - 0.15, S["L26"] + 0.35
    lookY = NEW.location.copy() if t < T_DOWN else None; lookJ = NEW.location.copy() if t >= T_PICK and t < S["L27"] - 0.1 else None; wY = wJ = 0.9
    if t < S["L20"]: lookJ, wJ = head_of("YOU") + Vector((0, 0, -0.25)), 0.4
    elif t < T_PICK: lookJ = NEW.location.copy() if t < S["L22"] else head_of("YOU")
    elif t >= S["L27"] - 0.1: lookJ = head_of("YOU")
    if S["L21"] <= t < S["L22"]: lookY, wY = head_of("JESS"), 0.5
    elif S["L24"] - 0.1 <= t < S["L25"] or S["L25"] + 2.2 <= t: lookY, wY = head_of("JESS"), (0.8 if t < S["L28"] else lerp(0.3, 1.0, ramp(t, S["L28"], S["L28"] + 0.9)))
    if lookY is not None: look_at(Y, lookY, wY)
    if lookJ is not None: look_at(J, lookJ, wJ)
    # You: the new phone in both hands (pulled back on "Hang on"); she puts it down on the cushion as L26 starts (to talk
    # with her hands) and Jess quietly picks it up behind her: the rewatch detail. Jess has it until the end of the scene.
    pull = ramp(t, S["L22"], S["L22"] + 0.4)
    if t < T_DOWN:
        place_phone_in_hands(Y, NEW, dist=0.3 + 0.05 * pull, drop=-0.08 + 0.04 * pull, side_off=-0.04 * pull)
        show(NEW_TX, *screen_new(t))
    else:
        F_, R_ = body_frame(Y); chest = bone_world(Y["arm"], "Bip01 Spine2")
        if t < S["L28"] - 0.3:      # talking with her hands, counting on her fingers
            g = math.sin(t * 5.0) * 0.04
            for side, s_ in (("L", 1), ("R", -1)): hand_to(Y, side, chest + F_ * 0.32 + R_ * (-0.12 * s_) + Vector((0, 0, -0.08 + g * s_)), (0, 0, -0.6))
        else:                      # frozen, hands dropping to her lap
            for side, s_ in (("L", 1), ("R", -1)): hand_to(Y, side, chest + F_ * 0.28 + R_ * (-0.1 * s_) + Vector((0, 0, -0.32)), (0, 0, -0.5))
    if T_DOWN <= t < T_PICK:        # lying on the cushion between them, screen up
        NEW.location = Vector((0.02, 0.12, 0.445)); NEW.rotation_euler = (0, 0, math.radians(20)); show(NEW_TX, *screen_new(t))
    jess_has = T_PICK <= t
    if jess_has:
        up = t >= S["L27"] - 0.1   # holds it up to show 'Signed in'
        place_phone_in_hands(J, NEW, dist=0.36 if up else 0.3, drop=-0.02 if up else -0.13, tilt_to=(head_of("YOU") if up else None))
        show(NEW_TX, *screen_new(t))
    elif S["L21"] <= t < S["L22"] + 0.3:   # grabbing at your phone, bouncing
        k = ramp(t, S["L21"] + 0.15, S["L21"] + 0.5) * (1 - ramp(t, S["L22"], S["L22"] + 0.3))
        hand_to(J, "L", bone_world(J["arm"], "Bip01 L Hand").lerp(NEW.location + Vector((0.06, -0.02, 0.02)), k), (0, 0, -0.5))
        F_, R_ = body_frame(J); hand_to(J, "R", bone_world(J["arm"], "Bip01 Spine2") + F_ * 0.34 + R_ * 0.18 + Vector((0, 0, -0.05 + 0.05 * math.sin(t * 9))), (0, 0, -0.6))
    set_face(Y, t, "YOU", [[0, "happy", 0.9], [S["L20"], "surprised", 1], [F_YOUR, "focused", 0.7], [S["L21"], "surprised", 0.5], [S["L22"], "suspicious", 1],
                           [S["L24"], "focused", 0.6], [S["L25"], "focused", 0.8], [S["L26"], "proud", 0.9], [F_EASY - 0.1, "smug", 1],
                           [S["L27"], "surprised", 0.8], [S["L28"], "dread", 1], [S["L29"], "shock", 1]], lips=lips_on(t))
    set_face(J, t, "JESS", [[0, "happy", 0.6], [S["L21"] - 0.1, "excited", 1], [S["L22"], "surprised", 0.6], [S["L24"], "helpful", 0.6],
                            [S["L26"] - 0.4, "focused", 0.7], [S["L27"] - 0.1, "guilty", 1], [S["L29"] - 0.1, "beaming", 1]], lips=True)
    tv.data.energy = 45 * (0.85 + 0.15 * math.sin(t * 7.3) * math.sin(t * 2.1))
    bpy.context.view_layer.update()
def Image_black():
    from PIL import Image
    return Image.new("RGB", (540, 960), (4, 4, 6))

# =====================================================================================================================
cam = bpy.data.objects.new("cam", bpy.data.cameras.new("cam")); col.objects.link(cam); sc.camera = cam
cam.data.sensor_fit = "VERTICAL"; cam.data.sensor_height = 36; cam.data.dof.use_dof = True; cam.data.dof.aperture_fstop = 2.4; cam.data.clip_start = 0.01
cam.data.clip_end = 1000.0      # the open-air sets have sky domes 90-140 m away
fill_d = bpy.data.lights.new("cam_fill", "AREA"); fill_d.energy = 25; fill_d.size = 1.0; fill_d.color = (1.0, 0.9, 0.82); fill_d.use_shadow = False
fill = bpy.data.objects.new("cam_fill", fill_d); col.objects.link(fill); fill.parent = cam; fill.location = (0.25, 0.3, 0.1)
def set_cam(t):
    name, t0, t1, fn = shot_at(t); r = fn(t); p, tg, lens, foc = r[:4]; roll = r[4] if len(r) > 4 else 0.0
    cam.location = p; cam.rotation_euler = (tg - p).to_track_quat("-Z", "Y").to_euler()
    if roll: cam.rotation_euler.rotate_axis("Z", math.radians(roll))
    cam.data.lens = lens; cam.data.dof.focus_distance = max(0.05, (foc - p).length)
    close = name in ("bike", "box", "stamp", "lock", "parts", "text", "login")
    cam.data.dof.aperture_fstop = 5.6 if close else (1.8 if name == "rewatch" else 2.4)
    fill_d.energy = (14 if name == "bike" else 4) if close else (3 if name in ("den_lost", "den_end") else 10 if name in ("yard", "van") else 25)
    return name

sc.render.engine = "CYCLES"; sc.cycles.device = "CPU"; sc.cycles.samples = a.samples; sc.cycles.use_denoising = True
sc.cycles.max_bounces = 4; sc.cycles.transparent_max_bounces = 8; sc.cycles.diffuse_bounces = 2; sc.cycles.glossy_bounces = 2
sc.render.resolution_x, sc.render.resolution_y = a.res; sc.render.fps = FPS
if a.threads: sc.render.threads_mode = "FIXED"; sc.render.threads = a.threads
sc.view_settings.view_transform = "AgX"; sc.view_settings.look = "AgX - Punchy"
sc.frame_set(1)

def render_frame(f, path):
    t = f / FPS; set_frame(t); shot = set_cam(t); sc.render.filepath = os.path.abspath(path)
    if os.environ.get("DBG"):
        for k_, c in list(C.items()) + [("HOOD", HOOD)]:
            arm = c["arm"]; pz = bone_world(arm, "Bip01 Pelvis").z; tz = min(bone_world(arm, f"Bip01 {s_} Toe0").z for s_ in "LR")
            kz = bone_world(arm, "Bip01 L Calf").z; print("DBG", k_, "pelvis", round(pz, 3), "knee", round(kz, 3), "toe", round(tz, 3), "arm z", round(arm.location.z, 3), "z0", round(c["z0"], 3))
        print("DBG OLD", tuple(round(v, 3) for v in OLD.matrix_world.translation), "hide", OLD.hide_render, "NEW", tuple(round(v, 3) for v in NEW.matrix_world.translation),
              "hood", tuple(round(v, 3) for v in hood.matrix_world.translation), "headH", tuple(round(v, 3) for v in bone_world(HOOD["arm"], "Bip01 Head")))
        Ya = C["YOU"]["arm"]; print("DBG hands R", tuple(round(v, 3) for v in bone_world(Ya, "Bip01 R Hand")), "L", tuple(round(v, 3) for v in bone_world(Ya, "Bip01 L Hand")),
              "chest", tuple(round(v, 3) for v in bone_world(Ya, "Bip01 Spine2")), "rotz", round(math.degrees(Ya.rotation_euler.z), 1), "F", tuple(round(v, 2) for v in body_frame(C["YOU"])[0]))
        Fy, Ry = body_frame(C["YOU"]); ch = bone_world(Ya, "Bip01 Spine2")
        print("DBG side: R wrist", round((bone_world(Ya, "Bip01 R Hand") - ch).dot(Ry), 3), "L wrist", round((bone_world(Ya, "Bip01 L Hand") - ch).dot(Ry), 3),
              "R shoulder", round((bone_world(Ya, "Bip01 R UpperArm") - ch).dot(Ry), 3), "phone", round((NEW.location - ch).dot(Ry), 3),
              "axR", round((-(NEW.rotation_euler.to_matrix() @ Vector((1, 0, 0)))).dot(Ry), 3))
        if os.environ.get("DBG") == "2": return
    t0 = time.time(); bpy.ops.render.render(write_still=True); print(f"rendered {path} shot={shot} t={t:.2f} {time.time() - t0:.1f}s", flush=True)

F_START = int(math.ceil(S["L16"] * FPS)); F_END = int(math.ceil(T_END * FPS))
if a.test:
    od = "build/flat_test"; os.makedirs(od, exist_ok=True)
    for name, t0, t1, fn in SHOTS:
        if a.shots and name not in a.shots: continue
        t1 = min(t1, T_END); f = int(round((t0 + (t1 - t0) * 0.6) * FPS)); rig.PREV.clear()
        render_frame(f, os.path.join(od, f"{f:04d}_{name}.png"))
elif a.one is not None:
    os.makedirs(a.out, exist_ok=True); render_frame(a.one, os.path.join(a.out, f"{a.one:04d}.png"))
else:
    os.makedirs(a.out, exist_ok=True); f0, f1 = a.frames
    print(f"episode part 2: frames {F_START}..{F_END} (this job {f0}..{f1})", flush=True)
    for f in range(max(f0, F_START), min(f1, F_END), a.step):
        p = os.path.join(a.out, f"{f:04d}.png")
        if os.path.exists(p): set_frame(f / FPS); continue
        render_frame(f, p)
