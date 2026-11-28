"""part2_scene.py: "Cheers, Biscuit" Part 2 (the finale), Blender 5 / bpy, Cycles CPU. Same characters, sets, faces and lip
sync as Part 1's flat_scene.py (shared helpers in rig.py), timed to Part 2's own voice timeline (drafts/phoneverse-cheers-
biscuit-part2/audio/out). Global frame numbers from 0.

Sets (far apart in one Blender scene, so no light leaks between them):
  FLAT (x=0)   You and Jess on the sofa at night, seconds after "JESS!"
  DEN  (x=40)  the hooded figure at his laptop (face never shown)
The camera "dives" between them through the screens (her phone <-> his laptop); compose_part2.py hides each cut with a
short glitch and adds the CLICKS TO ERASE counter.

  .venv/bin/python render/part2_scene.py --test                 # one still per shot -> build/p2_test/
  .venv/bin/python render/part2_scene.py --one 500              # one frame
  .venv/bin/python render/part2_scene.py --frames 0 900         # a range (resumable) -> build/p2/NNNN.png
"""
import os, sys
HERE_ = os.path.dirname(os.path.abspath(__file__))
os.environ["PV_EP"] = os.path.join(HERE_, "..", "..", "drafts", "phoneverse-cheers-biscuit-part2", "audio", "out")
sys.path.insert(0, HERE_)
import rig
from rig import *          # noqa: F401,F403  (resets Blender to an empty scene)
import part2_ui as UI
import biscuit_ui as BUI

ap = argparse.ArgumentParser()
ap.add_argument("--test", action="store_true"); ap.add_argument("--one", type=int); ap.add_argument("--frames", nargs=2, type=int)
ap.add_argument("--list", nargs="*", type=int)
ap.add_argument("--samples", type=int, default=16); ap.add_argument("--res", nargs=2, type=int, default=[540, 960])
ap.add_argument("--step", type=int, default=1); ap.add_argument("--out", default="build/p2"); ap.add_argument("--shots", nargs="*"); ap.add_argument("--threads", type=int, default=0)
a = ap.parse_args(sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else None)
TL = {r["id"]: r for r in json.load(open(os.path.join(EP, "timeline.json")))}
S = {k: v["start"] for k, v in TL.items()}; E = {k: v["end"] for k, v in TL.items()}
WORDS = json.load(open(os.path.join(EP, "words.json")))
def W(line, word, nth=0, end=False):
    k = lambda x: x["word"].lower().strip(".,!?'\"…")
    hits = [x for x in WORDS if x["line"] == line and k(x) == word]
    return hits[nth]["end"] if end else hits[nth]["start"]
T_END = E["L27"] + 1.6
UIC = os.path.join(ROOT, "build", "ui_cache"); os.makedirs(UIC, exist_ok=True)
sc.world = bpy.data.worlds.new("w"); sc.world.use_nodes = True; sc.world.node_tree.nodes["Background"].inputs[0].default_value = (0, 0, 0, 1)

EXPR.update({
    "guilty": {"browInnerUp": 0.7, "mouthPressLeft": 0.4, "mouthPressRight": 0.4, "mouthRollLower": 0.3, "eyeLookDownLeft": 0.3, "eyeLookDownRight": 0.3},
    "dread": {"browInnerUp": 0.6, "browDownLeft": 0.3, "eyeWideLeft": 0.3, "eyeWideRight": 0.3, "mouthFrownLeft": 0.35, "mouthFrownRight": 0.35},
    "excited": {"mouthSmileLeft": 0.7, "mouthSmileRight": 0.7, "browInnerUp": 0.5, "browOuterUpLeft": 0.5, "browOuterUpRight": 0.5, "eyeWideLeft": 0.4, "eyeWideRight": 0.4, "jawOpen": 0.15},
    "proud": {"mouthSmileLeft": 0.45, "mouthSmileRight": 0.45, "browOuterUpLeft": 0.3, "browOuterUpRight": 0.3, "cheekSquintLeft": 0.2},
    "beaming": {"mouthSmileLeft": 0.85, "mouthSmileRight": 0.85, "cheekSquintLeft": 0.5, "cheekSquintRight": 0.5, "browInnerUp": 0.3},
    "worried": {"browInnerUp": 0.75, "mouthFrownLeft": 0.25, "mouthFrownRight": 0.25, "mouthPressLeft": 0.2, "mouthPressRight": 0.2},
    "deadpan": {"eyeBlinkLeft": 0.1, "eyeBlinkRight": 0.1, "mouthPressLeft": 0.35, "mouthPressRight": 0.35, "browDownLeft": 0.15, "browDownRight": 0.15},
    "outraged": {"browInnerUp": 0.5, "browDownLeft": 0.4, "browDownRight": 0.4, "eyeWideLeft": 0.5, "eyeWideRight": 0.5, "jawOpen": 0.15, "noseSneerLeft": 0.3},
})
AU_ADD.update({
    "guilty": {"AU_01_InnerBrowRaiser": 0.8, "AU_15_LipCornerDepressor": 0.4, "AU_24_LipPressor": 0.5},
    "dread": {"AU_01_InnerBrowRaiser": 0.7, "AU_04_BrowLowerer": 0.3, "AU_15_LipCornerDepressor": 0.5},
    "excited": {"AU_06_CheekRaiser": 0.6, "AU_12_LipCornerPuller": 0.8, "AU_01_InnerBrowRaiser": 0.5, "AU_02_OuterBrowRaiser": 0.5},
    "proud": {"AU_12_LipCornerPuller": 0.5, "AU_06_CheekRaiser": 0.3},
    "beaming": {"AU_06_CheekRaiser": 0.8, "AU_12_LipCornerPuller": 0.9},
    "worried": {"AU_01_InnerBrowRaiser": 0.9, "AU_15_LipCornerDepressor": 0.3, "AU_24_LipPressor": 0.3},
    "deadpan": {"AU_41_LidDroop": 0.2, "AU_24_LipPressor": 0.4},
    "outraged": {"AU_01_InnerBrowRaiser": 0.5, "AU_04_BrowLowerer": 0.6, "AU_05_UpperLidRaiser": 0.6, "AU_09_NoseWrinkler": 0.3},
})

# =====================================================================================================================
# props and set helpers (as in flat_scene.py)
def img_mat(name, strength=1.6):
    m = bpy.data.materials.new(name); m.use_nodes = True; nt = m.node_tree
    for nd in list(nt.nodes): nt.nodes.remove(nd)
    tx = nt.nodes.new("ShaderNodeTexImage"); em = nt.nodes.new("ShaderNodeEmission"); ou = nt.nodes.new("ShaderNodeOutputMaterial")
    tx.image = bpy.data.images.new(name + "_img", 8, 8)
    nt.links.new(tx.outputs["Color"], em.inputs["Color"]); em.inputs["Strength"].default_value = strength; nt.links.new(em.outputs[0], ou.inputs[0])
    return m, tx
SCREEN_KEY = {}
def show(tx, key, make):
    if SCREEN_KEY.get(tx.name) == key: return
    p = os.path.join(UIC, "p2_" + key.replace(" ", "_") + ".png")
    if not os.path.exists(p):
        im = make(); (im if "lap" in key else im.resize((540, 960))).save(p)
    tx.image = bpy.data.images.load(p, check_existing=True); SCREEN_KEY[tx.name] = key
def make_phone(name, case_rgb):
    body = box(name, (0.074, 0.152, 0.009), (0, 0, -80), mat(name + "_case", case_rgb, 0.45), bevel=0.003)
    m, tx = img_mat(name + "_scr"); bpy.ops.mesh.primitive_plane_add(size=1, location=(0, 0, 0.0047)); s = bpy.context.active_object
    s.name = name + "_screen"; s.scale = (0.066, 0.143, 1); bpy.ops.object.transform_apply(scale=True); s.data.materials.append(m); s.parent = body
    return body, tx
def aim_screen(phone, at, roll_up=None):
    n = (Vector(at) - phone.location).normalized(); phone.rotation_euler = n.to_track_quat("Z", "Y").to_euler()
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
NEW, NEW_TX = make_phone("newphone", (0.35, 0.75, 0.62))       # her new phone (mint case, as in Part 1)
JPH, JPH_TX = make_phone("jessphone", (0.92, 0.82, 0.3))       # Jess's own phone ("Just ring Apple!")

# =====================================================================================================================
# DEN (x=40): bench, laptop (screen faces HIM now: readable from behind his shoulder), shelves of boxes, the hooded figure
OD = Vector((40, 0, 0))
room((40, 0, 0), 7, 7, 3.2, mat("dn_wall", (0.09, 0.085, 0.09), 0.95), noise_mat("dn_floor", (0.06, 0.06, 0.065), (0.11, 0.11, 0.115), 20))
wood = mat("dn_bench", (0.16, 0.11, 0.07), 0.7)
box("dn_bench", (2.6, 0.8, 0.05), OD + Vector((0, -0.75, 0.76)), wood)
for dx in (-1.2, 1.2):
    for dy in (-1.05, -0.45): box("dn_leg", (0.05, 0.05, 0.76), OD + Vector((dx, dy, 0.38)), wood)
cardb = mat("dn_card", (0.62, 0.45, 0.28), 0.9)
for i in range(14):
    box(f"dn_shelfbox{i}", (rnd.uniform(0.4, 0.7), 0.4, rnd.uniform(0.3, 0.5)), OD + Vector((-2.5 + (i % 7) * 0.78, -2.95, 0.95 + (i // 7) * 0.75)), cardb, rot=(0, 0, rnd.uniform(-0.1, 0.1)))
for j in range(2): box("dn_shelf", (6, 0.5, 0.04), OD + Vector((0, -2.9, 0.72 + j * 0.75)), mat("dn_shelfm", (0.2, 0.2, 0.22), 0.5, 0.6))
for i in range(3):   # a few closed boxes on the bench (the HONG KONG lot from Part 1)
    box(f"dn_lot{i}", (0.42, 0.32, 0.22), OD + Vector((-0.95 - 0.05 * i, -0.8 + 0.02 * i, 0.895 + 0.22 * i)), cardb, rot=(0, 0, 0.08 * (i - 1)))
LAP_C = OD + Vector((0.05, -0.62, 0.79))
lapm = mat("dn_lap", (0.035, 0.035, 0.04), 0.65, 0.2)
box("dn_lap_base", (0.36, 0.25, 0.018), LAP_C, lapm, bevel=0.004)
box("dn_trackpad", (0.1, 0.065, 0.002), LAP_C + Vector((0.0, 0.075, 0.0095)), mat("dn_pad", (0.12, 0.12, 0.14), 0.3, 0.3))
LID_C = OD + Vector((0.05, -0.76, 0.905)); LID_R = Euler((math.radians(14), 0, 0))
box("dn_lap_lid", (0.36, 0.012, 0.24), LID_C, lapm, rot=tuple(LID_R), bevel=0.004)
SCR_N = (LID_R.to_matrix() @ Vector((0, 1, 0))).normalized()          # the screen faces him (+y) and a little up
SCR_C = LID_C + SCR_N * 0.0072
lm_, LAP_TX = img_mat("dn_lapscr", 2.0); bpy.ops.mesh.primitive_plane_add(size=1, location=SCR_C, rotation=(math.radians(76), 0, math.radians(180)))
lap_scr = bpy.context.active_object; lap_scr.scale = (0.33, 0.21, 1); lap_scr.data.materials.append(lm_)
TRACKPAD = LAP_C + Vector((0.0, 0.075, 0.012))
stool = cyl("dn_stool", 0.2, 0.5, OD + Vector((0, 0.15, 0.25)), mat("dn_stoolm", (0.04, 0.04, 0.045), 0.5), verts=20)
HOOD = load_char("Male_Adult_06", False, "tex")
hood_m = mat("hood_fabric", (0.035, 0.035, 0.04), 0.95)
for m_ in HOOD["meshes"]:
    for sl in m_.material_slots: sl.material = hood_m
hood = sphere("hood", 0.14, (0, 0, -60), hood_m, seg=32)
for f_ in hood.data.polygons: f_.use_smooth = True
lamp("dn_tube", "AREA", OD + Vector((0, 0.6, 3.0)), 70, (0.75, 0.9, 1.0), 1.4, OD + Vector((0, -0.6, 0.8)))
box("dn_tube_glow", (1.2, 0.08, 0.04), OD + Vector((0, 0.6, 3.12)), emit_mat("dn_tubem", (0.8, 0.95, 1.0), 6))
lap_glow = lamp("dn_lapglow", "AREA", SCR_C + SCR_N * 0.05, 14, (0.6, 0.7, 1.0), 0.3, SCR_C + SCR_N * 1.0)
lamp("dn_rim", "AREA", OD + Vector((1.4, 1.6, 2.0)), 45, (0.5, 0.6, 1.0), 0.8, OD + Vector((0, 0, 1.2)))

# =====================================================================================================================
# FLAT (x=0): same room as Part 1
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
fl_bulb = emit_mat("bulb", (1, 0.75, 0.35), 9)
for i in range(60): bsphere(0.014, (-2.6 + i * 0.09, 1.62, 2.25 - 0.12 * abs(math.sin(i * 0.35))), fl_bulb)
for i in range(4):
    box(f"pic{i}", (0.42, 0.03, 0.32), (-0.9 + i * 0.6, 1.64, 1.55 + (i % 2) * 0.12), mat(f"fl_pic{i}", rnd.choice([(0.8, 0.5, 0.3), (0.3, 0.5, 0.7), (0.7, 0.7, 0.6), (0.6, 0.3, 0.5)]), 0.6))
flush_batches()
lamp("fl_lamp_key", "AREA", (1.4, 0.1, 1.9), 70, (1.0, 0.68, 0.4), 1.0, (0, 0.3, 1.1))
lamp("fl_lamp_pt", "POINT", (1.65, 1.2, 1.55), 30, (1.0, 0.62, 0.3), 0.15)
tv = lamp("fl_tv", "AREA", (0.2, -2.6, 1.0), 45, (0.55, 0.7, 1.0), 1.2, (0, 0.4, 1.0))
lamp("fl_rim", "AREA", (-1.8, 1.3, 2.1), 40, (0.55, 0.7, 1.0), 0.8, (0, 0.3, 1.1))
lamp("fl_ceil", "AREA", (0, -0.6, 2.6), 25, (1.0, 0.85, 0.7), 2.0, (0, -0.6, 0))
ph_glow = lamp("ph_glow", "POINT", (0, 0, -50), 0.6, (0.75, 0.85, 1.0), 0.05, shadow=False)   # her screen lights her face

# =====================================================================================================================
# cast
C = {"YOU": load_char("Female_Adult_01", True, "tex"), "JESS": load_char("Female_Adult_15", True, "tex")}
SIT = "m_sit_chair_idle_neutral_01"
bake(SIT)
SEAT_DZ = -0.40
YOU_SEAT, JESS_SEAT = Vector((-0.42, 0.28, SEAT_DZ)), Vector((0.45, 0.26, SEAT_DZ))
OFFSTAGE = Vector((0, 0, -200))
def head_of(who): return bone_world((C[who] if who in C else HOOD)["arm"], "Bip01 Head")

# =====================================================================================================================
# key times (all from the voice timeline; the same anchors as the sound effects in sfx_part2.py)
T_DIVE1 = E["L07"] + 0.02                     # into her phone
T_DEN1 = S["L08"] - 0.25                      # glitch cut: out of his laptop
T_CLICK1 = S["L08"] - 0.12                    # Find Devices (no code)
T_LIST = S["L08"] + 0.25                      # the device list with her new phone
T_CNT = E["L08"] + 0.16                       # counter appears at 3
T_CLICK2 = W("L09", "parts") + 0.25           # Erase This Device -> 2
T_BACK = E["L09"] + 0.22                      # dive back: into his screen
T_FLAT2 = S["L10"] - 0.3                      # glitch cut: out of her phone
T_GONE = W("L17", "gone") - 0.28              # Remove Other Devices tap
T_DIVE2 = E["L19"] + 0.02
T_DEN2 = S["L20"] - 0.3
T_CLICK3 = W("L20", "sure", 1) - 0.05         # 'Are you sure?' -> Next -> 1
T_GLIDE = W("L20", "last") - 0.1
T_PRESS = E["L22"] + 0.2                      # her thumb (his click lands 0.04 s later)
T_KICK = T_PRESS + 0.15                       # he's signed out; counter cracks
T_TYPE, T_WRONG = E["L23"] + 0.1, E["L23"] + 0.95
T_TEXT = S["L25"] - 0.5
T_SHOT = W("L26", "screenshot") + 0.35
R0 = S["L21"]
RACE = [R0, R0 + 0.75, R0 + 1.3, R0 + 1.7, S["L22"], S["L22"] + 0.45, T_PRESS + 0.1]   # cut times inside the race (each shorter)
GLITCH_CUTS = [T_DEN1, T_FLAT2, T_DEN2]       # compose_part2.py hides these cuts with a short glitch

def cam_of(loc, tgt, lens, foc=None, roll=0.0): return Vector(loc), Vector(tgt), lens, Vector(foc if foc is not None else tgt), roll
def phone_nup(ph):
    M = ph.matrix_world.to_3x3(); return ph.matrix_world.translation.copy(), (M @ Vector((0, 0, 1))).normalized(), (M @ Vector((0, 1, 0))).normalized()
CAM_HOLD = YOU_SEAT + Vector((0.22, -0.95, 1.62))     # where the lens is when she holds the phone up to it (L07)

# ---------------------------------------------------------------- flat shots
def sh_open(t):     # low and tight on the phone glowing in her hands, tilting up to her face as the echo fades
    p, n, up = phone_nup(NEW); h = head_of("YOU"); u = ramp(t, 0.6, S["L02"] - 0.1)
    eye = (p + Vector((0.16, -0.32, -0.06))).lerp(h + Vector((0.3, -0.8, -0.05)), u)
    tgt = p.lerp(h + Vector((0.0, 0, -0.04)), u)
    return cam_of(eye, tgt, lerp(38, 42, u), tgt)
def sh_you(t, t0, t1, dx=0.0, push=0.2, lens=42, dz=0.0):
    u = ramp(t, t0, t1); h = head_of("YOU")
    return cam_of(h + Vector((0.32 + dx, -0.92 + push * u, -0.2 + dz)), h + Vector((0.02, 0, -0.1)), lens, h)
def sh_jess(t, t0, t1, push=0.15):
    u = ramp(t, t0, t1); hJ, hY = head_of("JESS"), head_of("YOU"); m = hJ * 0.7 + hY * 0.3
    return cam_of(Vector((-0.45 + 0.1 * u, -1.25 + push * u, 1.12)), m + Vector((0, 0, -0.16)), 32, hJ)
def sh_penny(t):    # slow push into her eyes as the penny drops
    u = ramp(t, S["L04"], S["L05"]); h = head_of("YOU")
    return cam_of(h + Vector((0.16, -0.9 + 0.25 * u, -0.08)), h + Vector((0.07, 0, -0.06)), lerp(42, 50, u), h)
def sh_outrage(t):  # Jess bounces up, outraged; two-shot favouring her
    return sh_jess(t, S["L05"], S["L06"], 0.2)
def sh_upright(t):  # she shoots forward to the edge of the seat: whip up into a wide two-shot
    k = ramp(t, S["L06"], S["L06"] + 0.35); m = (head_of("YOU") + head_of("JESS")) / 2
    return cam_of(Vector((0.1, -2.15, 1.0 + 0.25 * k)), m + Vector((0, 0, -0.3)), 26, m)
def sh_hold(t):     # "Oi, camera": she holds the phone up to the lens
    h = head_of("YOU"); p = NEW.matrix_world.translation
    return cam_of(CAM_HOLD, p.lerp(h, 0.45) + Vector((0, 0, -0.02)), 30, p.lerp(h, 0.5))
def sh_dive_phone(t, t0, t1, start):     # into her phone's screen until the map fills the frame
    u = ease(clamp((t - t0) / (t1 - t0))) ** 1.4; p, n, up = phone_nup(NEW)
    end = p + n * 0.035
    return cam_of(Vector(start).lerp(end, u), (Vector(start) + (p - Vector(start)) * 2).lerp(p, u) if u < 1 else p, lerp(30, 26, u), p)
def sh_dive1(t): return sh_dive_phone(t, T_DIVE1, T_DEN1, CAM_HOLD)
def sh_flat2(t):    # out of her phone: back past her shoulder, then round to the front of the sofa (L10-L11)
    p, n, up = phone_nup(NEW); hY, hJ = head_of("YOU"), head_of("JESS"); m = hY * 0.6 + hJ * 0.4
    u = ramp(t, T_FLAT2, T_FLAT2 + 0.55); v = ramp(t, T_FLAT2 + 0.45, S["L10"] + 1.3); w = ramp(t, S["L10"] + 1.3, S["L12"])
    ots = hY + (p - hY) * 0.25 + Vector((0.14, 0.04, 0.08))
    front = Vector((-0.75 + 0.35 * w, -1.45 + 0.1 * w, 1.15))
    eye = (p + n * 0.035).lerp(ots, u).lerp(front, v)
    tgt = p.lerp(p, u).lerp(m + Vector((0, 0, -0.14)), v)
    return cam_of(eye, tgt, lerp(26, 30, u), tgt.lerp(hY, v))
def sh_ots(t):      # over her shoulder onto her screen (Settings), Jess soft beside her
    u = ramp(t, S["L12"], S["L13"]); p, n, up = phone_nup(NEW); h = head_of("YOU")
    eye = h + (p - h) * 0.25 + Vector((0.13, 0.05, 0.07))
    return cam_of(eye.lerp(p + (eye - p) * 0.6, u), p, 32, p)
def sh_ring(t):     # Jess with her own phone at her ear, You beside her
    return sh_jess(t, S["L13"], S["L15"], 0.12)
def sh_fix(t):      # straight onto her screen: new password, Remove Other Devices
    u = ramp(t, S["L15"], S["L18"]); p, n, up = phone_nup(NEW)
    return cam_of(p + n * lerp(0.2, 0.15, u) + up * 0.01, p, 28, p)
def sh_out(t):      # two-shot; "Camera!" she points at the lens
    u = ramp(t, S["L18"], E["L19"]); hY, hJ = head_of("YOU"), head_of("JESS"); m = hY * 0.55 + hJ * 0.45
    return cam_of(Vector((-0.2, -1.55 + 0.25 * u, 1.13)), m + Vector((0, 0, -0.15)), 30, m)
CAM_OUT_END = Vector((-0.2, -1.30, 1.13))
def sh_dive2(t): return sh_dive_phone(t, T_DIVE2, T_DEN2, CAM_OUT_END)
def sh_thumb(t):    # race: her screen, her thumb hovering over Sign Out Of All Browsers
    p, n, up = phone_nup(NEW); k = (t * 7.0) % 1.0
    R3 = NEW.matrix_world.to_3x3(); side = (R3 @ Vector((1, 0, 0))).normalized()
    return cam_of(p + n * 0.17 - up * 0.06 + side * 0.03, p - up * 0.02, 34, p)
def sh_scream(t):   # Jess: "PRESS IT!"
    h = head_of("JESS"); return cam_of(h + Vector((-0.22, -0.75, -0.06)), h + Vector((0, 0, -0.1)), 42, h)
def sh_cheers(t):   # straight down the lens: "Cheers, Biscuit."
    u = ramp(t, S["L24"] - 0.05, S["L25"] - 0.5); h = head_of("YOU")
    return cam_of(h + Vector((0.05, -0.62 + 0.08 * u, 0.0)), h + Vector((0, 0, -0.04)), 50, h)
def sh_sting(t):    # tight on the phone as his text lands, pulling back to both faces
    u = ramp(t, T_TEXT + 0.9, S["L26"]); p, n, up = phone_nup(NEW); hY, hJ = head_of("YOU"), head_of("JESS"); m = hY * 0.6 + hJ * 0.4
    near = p + n * 0.2 + up * 0.01
    return cam_of(near.lerp(Vector((-0.3, -1.4, 1.1)), u), p.lerp(m + Vector((0, 0, -0.18)), u), lerp(30, 30, u), p.lerp(m, u))
def sh_shot(t):     # screenshot, unbothered; Jess worried beside her
    u = ramp(t, S["L26"], S["L27"]); hY, hJ = head_of("YOU"), head_of("JESS"); m = hY * 0.65 + hJ * 0.35
    return cam_of(Vector((-0.3, -1.4 + 0.12 * u, 1.1)), m + Vector((0, 0, -0.16)), 32, hY)
def sh_biscuit(t):  # Jess beaming in front, You turning slowly to her
    hJ, hY = head_of("JESS"), head_of("YOU"); m = hJ * 0.6 + hY * 0.4
    return cam_of(Vector((0.05, -1.6, 1.1)), m + Vector((0, 0, -0.16)), 30, hJ)
def sh_stare(t):    # the slow push in as she turns to camera: deadpan. Hard cut.
    u = ramp(t, E["L27"], T_END); h = head_of("YOU")
    return cam_of(h + Vector((0.08, -0.85 + 0.35 * u, -0.01)), h + Vector((0, 0, -0.04)), lerp(42, 52, u), h)
# ---------------------------------------------------------------- den shots
def hood_ots(): hh = head_of("HOOD"); return hh + Vector((0.32, 0.5, 0.2))
def sh_den_out(t, t0, t1):    # out of his laptop screen, back over his right shoulder
    u = ease(clamp((t - t0) / max(0.01, t1 - t0))); start = SCR_C + SCR_N * 0.03; end = hood_ots()
    mid = start.lerp(end, u) + Vector((0, 0, 0.12 * math.sin(math.pi * u)))
    return cam_of(mid, SCR_C.lerp(SCR_C + Vector((0, 0, -0.03)), u), lerp(26, 30, u), SCR_C)
def sh_den1(t):
    return sh_den_out(t, T_DEN1, T_DEN1 + 0.9)
def sh_back(t):     # dive back into his screen (the map pin)
    u = ease(clamp((t - T_BACK) / (T_FLAT2 - T_BACK))) ** 1.4; start = hood_ots(); end = SCR_C + SCR_N * 0.03
    return cam_of(start.lerp(end, u), SCR_C, lerp(30, 26, u), SCR_C)
def sh_den2(t):     # out of his laptop again, then down onto the gloved finger + cursor for "Last click, Biscuit"
    if t < T_GLIDE - 0.2: return sh_den_out(t, T_DEN2, T_DEN2 + 0.7)
    u = ramp(t, T_GLIDE - 0.2, S["L21"]); hand = bone_world(HOOD["arm"], "Bip01 R Hand")
    eye = hood_ots().lerp(TRACKPAD + Vector((-0.22, 0.2, 0.14)), u) + Vector((0, 0, 0.5 * math.sin(math.pi * u)))   # crane up over his head, not through it
    hh = head_of("HOOD"); d_ = eye - hh
    if d_.length < 0.33: eye = hh + d_.normalized() * 0.33                                                     # and never closer than 33 cm
    return cam_of(eye, SCR_C.lerp(TRACKPAD.lerp(SCR_C, 0.55), u), lerp(30, 34, u), TRACKPAD.lerp(SCR_C, 0.3 * u))
def sh_finger(t):   # race: his finger on the trackpad, the cursor creeping to Erase on the screen behind
    k = (t - R0) * 0.03
    return cam_of(TRACKPAD + Vector((-0.3 - k, 0.32, 0.22)), TRACKPAD.lerp(SCR_C, 0.4), 32, TRACKPAD.lerp(SCR_C, 0.2))
def sh_kicked(t):   # his screen: signed out, the old password, 'Incorrect password'
    u = ramp(t, RACE[-1], S["L24"]); return cam_of(SCR_C + SCR_N * lerp(0.42, 0.34, u) + Vector((0.06, 0, 0.05)), SCR_C, 32, SCR_C)

def race_shot(t):
    names = [("thumb", sh_thumb), ("finger", sh_finger), ("thumb", sh_thumb), ("finger", sh_finger), ("scream", sh_scream), ("thumb", sh_thumb)]
    for (nm, fn), t0, t1 in zip(names, RACE, RACE[1:]):
        if t0 <= t < t1: return nm, t0, t1, fn
SHOTS = [("open", -1, S["L02"], sh_open), ("hook", S["L02"], S["L03"], lambda t: sh_you(t, S["L02"], S["L03"], 0.0, 0.25)),
         ("jess", S["L03"], S["L04"], lambda t: sh_jess(t, S["L03"], S["L04"])), ("penny", S["L04"], S["L05"], sh_penny),
         ("outrage", S["L05"], S["L06"], sh_outrage), ("upright", S["L06"], S["L07"], sh_upright), ("hold", S["L07"], T_DIVE1, sh_hold),
         ("dive1", T_DIVE1, T_DEN1, sh_dive1), ("den1", T_DEN1, T_BACK, sh_den1), ("back", T_BACK, T_FLAT2, sh_back),
         ("flat2", T_FLAT2, S["L12"], sh_flat2), ("ots", S["L12"], S["L13"], sh_ots), ("ring", S["L13"], S["L15"], sh_ring),
         ("fix", S["L15"], S["L18"], sh_fix), ("out", S["L18"], T_DIVE2, sh_out), ("dive2", T_DIVE2, T_DEN2, sh_dive2),
         ("den2", T_DEN2, R0, sh_den2), ("race", R0, RACE[-1], None), ("kicked", RACE[-1], S["L24"] - 0.05, sh_kicked),
         ("cheers", S["L24"] - 0.05, T_TEXT, sh_cheers), ("sting", T_TEXT, S["L26"], sh_sting), ("shot", S["L26"], S["L27"], sh_shot),
         ("biscuit", S["L27"], E["L27"], sh_biscuit), ("stare", E["L27"], T_END + 5, sh_stare)]
def shot_at(t):
    for sh in SHOTS:
        if sh[1] <= t < sh[2]:
            return race_shot(t) if sh[0] == "race" else sh
    return SHOTS[0] if t < SHOTS[0][1] else SHOTS[-1]
DEN_SHOTS = ("den1", "back", "den2", "finger", "kicked")

# =====================================================================================================================
# screens
def screen_her(t):
    if t < S["L07"] - 0.3: return "lock", BUI.new_lock
    if t < T_DIVE1: pl = round(((t * 1.2) % 1.0), 1); return f"map_{pl}", lambda: UI.phone_map(pl)
    if t < T_DEN1 + 0.1: z = round(clamp((t - T_DIVE1) / (T_DEN1 - T_DIVE1)), 2); return f"dive_{z}", lambda: UI.map_dive(z, 0.3)
    if t < S["L12"]: pl = round(((t * 1.2) % 1.0), 1); return f"map_{pl}", lambda: UI.phone_map(pl)
    if t < S["L16"]:   # into Settings while Jess panics
        ty = 0.0; return "pw_0.0", lambda: UI.change_password(0.0)
    if t < S["L17"]: ty = round(clamp((t - S["L16"]) / (E["L16"] - S["L16"])), 2); return f"pw_{ty}", lambda: UI.change_password(ty)
    if t < T_GONE: return "rm_0_0", lambda: UI.remove_devices(0.0, 0.0)
    if t < S["L21"] - 0.2:
        g = round(clamp((t - T_GONE - 0.08) / 0.5), 2); return f"rm_{g}_1", lambda: UI.remove_devices(g, 1.0 if t < T_GONE + 0.3 else 0.0)
    if t < T_TEXT:
        hv = round(0.5 + 0.5 * math.sin(t * 9), 1); pr = 1.0 if t >= T_PRESS else 0.0
        return f"so_{hv}_{pr}", lambda: UI.signout_all(hv, pr)
    p = round(clamp((t - T_TEXT - 0.05) / 0.35), 2); return f"threat_{p}", lambda: UI.threat_text(p)
CUR = {"find": (800, 845), "erase_dev": (270, 800), "next": (960, 605), "erase": (800, 510)}
def screen_his(t):
    def glide(a_, b_, t0, t1): u = ramp(t, t0, t1); return (int(lerp(a_[0], b_[0], u)), int(lerp(a_[1], b_[1], u)))
    if t < T_LIST:
        ck = 1.0 if t >= T_CLICK1 else 0.0; cur = glide((640, 700), CUR["find"], T_DEN1, T_CLICK1 - 0.02)
        return f"lap_signin_{ck}_{cur}", lambda: UI.lap_signin(ck, cur)
    if t < T_CLICK2 + 0.1:
        hl = 1.0 if t >= T_CLICK2 - 0.25 else 0.0; cur = glide((900, 600), CUR["erase_dev"], T_LIST + 0.2, T_CLICK2 - 0.05)
        pl = round(((t * 1.2) % 1.0), 1); return f"lap_list_{hl}_{cur}_{pl}", lambda: UI.lap_list(hl, cur, pl)
    if t < T_CLICK3 + 0.1:
        ck = 1.0 if t >= T_CLICK3 else 0.0; cur = glide((640, 700), CUR["next"], T_DEN2, T_CLICK3 - 0.03)
        return f"lap_confirm_{ck}_{cur}", lambda: UI.lap_confirm(ck, cur)
    if t < T_KICK:
        # the cursor glides towards Erase on "Last click", then creeps the last bit during the race
        c1 = glide((960, 760), (900, 600), T_CLICK3 + 0.1, T_GLIDE); c2 = glide(c1, (845, 530), T_GLIDE, R0 + 0.2)
        cur = glide(c2, CUR["erase"], R0 + 0.2, T_PRESS + 0.04); ck = 1.0 if t >= T_PRESS + 0.04 else 0.0
        return f"lap_erase_{ck}_{cur}", lambda: UI.lap_erase(ck, cur)
    ty = round(clamp((t - T_TYPE) / 0.75), 2); wr = round(clamp((t - T_WRONG) / 0.45), 2) if t >= T_WRONG else 0.0
    return f"lap_out_{ty}_{wr}", lambda: UI.lap_out(ty, wr, (980, 700))

# =====================================================================================================================
# per-frame action
def place_phone_in_hands(c, ph, dist=0.3, drop=-0.12, side_off=0.0, tilt_to=None):
    F, Rt = body_frame(c); chest = bone_world(c["arm"], "Bip01 Spine2"); h = bone_world(c["arm"], "Bip01 Head")
    p = chest + F * dist + Rt * side_off + Vector((0, 0, drop)); ph.location = p
    aim_screen(ph, tilt_to if tilt_to is not None else h + Vector((0, 0, 0.05)))
    R3 = ph.rotation_euler.to_matrix(); n = R3 @ Vector((0, 0, 1)); up = R3 @ Vector((0, 1, 0)); axR = R3 @ Vector((1, 0, 0))
    hand_to(c, "R", p + axR * 0.06 - n * 0.02 - up * 0.03, (0, 0, -0.6), fingers=-axR * 0.7 - n * 0.7 + up * 0.2, across=-up)
    hand_to(c, "L", p - axR * 0.06 - n * 0.02 - up * 0.03, (0, 0, -0.6), fingers=axR * 0.7 - n * 0.7 + up * 0.2, across=-up)
    curl(c["arm"], 40)
    return p
def phone_in_left(c, ph, tilt_to=None):
    """one-handed (left), so the right hand is free to point"""
    F, Rt = body_frame(c); chest = bone_world(c["arm"], "Bip01 Spine2"); h = bone_world(c["arm"], "Bip01 Head")
    p = chest + F * 0.3 - Rt * 0.1 + Vector((0, 0, -0.14)); ph.location = p
    aim_screen(ph, tilt_to if tilt_to is not None else h)
    R3 = ph.rotation_euler.to_matrix(); n = R3 @ Vector((0, 0, 1)); up = R3 @ Vector((0, 1, 0)); axR = R3 @ Vector((1, 0, 0))
    hand_to(c, "L", p - axR * 0.05 - n * 0.025 - up * 0.04, (0, 0, -0.6), fingers=axR * 0.7 - n * 0.7 + up * 0.2, across=-up)
THIGH, CALF = 28.0, -12.0
def sit_legs(c):
    for s_ in "LR":
        rot_bone(c["arm"], f"Bip01 {s_} Thigh", (0, 0, THIGH)); rot_bone(c["arm"], f"Bip01 {s_} Calf", (0, 0, CALF))
    bpy.context.view_layer.update()
def osc(t, f, t0, t1, a=1.0): return math.sin((t - t0) * f) * a * ramp(t, t0, t0 + 0.15) * (1 - ramp(t, t1 - 0.15, t1))
def set_frame(t, cam_loc=None):
    rig.T_NOW = t
    # ---------------- DEN: the hooded figure, right hand on the trackpad (a dip on every click), left hand on the keys
    drive(HOOD, "HOOD", OD + Vector((0, 0.16, -0.3)), 0, SIT, t); sit_legs(HOOD)
    lean_in = ramp(t, T_CLICK3, T_GLIDE) * (1 - ramp(t, T_KICK, T_KICK + 0.3)); recoil = ramp(t, T_KICK, T_KICK + 0.25) * (1 - ramp(t, T_TYPE, T_TYPE + 0.3))
    for b, ang in (("Bip01 Spine1", 4 * lean_in - 7 * recoil), ("Bip01 Spine2", 6 + 3 * lean_in)): rot_bone(HOOD["arm"], b, (0, 0, ang))
    bpy.context.view_layer.update()
    look_at(HOOD, SCR_C + Vector((0, 0, -0.02)), 0.8)
    dip = sum(0.008 * max(0.0, 1 - abs(t - tc) / 0.06) for tc in (T_CLICK1, T_CLICK2, T_CLICK3, T_PRESS + 0.04))
    slide = Vector((0.02 * math.sin(t * 1.7), 0.01 * math.sin(t * 2.3), 0))
    typing = T_TYPE <= t < T_TYPE + 0.8
    if typing:
        for side, sx in (("L", 0.08), ("R", -0.08)):
            tp = Vector((0, 0.01 * math.sin(t * (23 if side == "L" else 19)), 0.012 * max(0, math.sin(t * (17 if side == "L" else 21)))))
            hand_to(HOOD, side, LAP_C + Vector((sx, -0.04, 0.03)) + tp, (0, 0, -0.5))
    else:
        hand_to(HOOD, "R", TRACKPAD + Vector((0.0, 0.08, 0.035 - dip)) + slide, (0, 0, -0.5))
        hand_to(HOOD, "L", LAP_C + Vector((0.12, -0.03, 0.035)), (0, 0, -0.5))
    hd = head_of("HOOD"); hm = HOOD["arm"].matrix_world @ HOOD["arm"].pose.bones["Bip01 Head"].matrix
    hood.matrix_world = Matrix.Translation(hd + hm.to_3x3() @ Vector((0.04, 0, 0)) + Vector((0, 0.03, 0.06))) @ Matrix.Diagonal((0.95, 1.22, 1.12, 1.0))
    show(LAP_TX, *screen_his(t))
    red_ = T_CLICK3 <= t < T_KICK; lap_glow.data.color = (1.0, 0.35, 0.3) if red_ else (0.6, 0.7, 1.0); lap_glow.data.energy = 7 if red_ else 14
    # ---------------- FLAT: You and Jess on the sofa
    Y, J = C["YOU"], C["JESS"]
    bounceJ = abs(math.sin((t - S["L05"]) * 8.5)) * 0.06 * ramp(t, S["L05"], S["L05"] + 0.15) * (1 - ramp(t, E["L05"] - 0.1, E["L05"] + 0.15))
    bounceJ += abs(math.sin((t - S["L22"]) * 9.0)) * 0.05 * ramp(t, S["L22"], S["L22"] + 0.1) * (1 - ramp(t, T_PRESS + 0.3, T_PRESS + 0.6))
    bounceJ += abs(math.sin((t - S["L27"]) * 6.0)) * 0.03 * ramp(t, S["L27"], S["L27"] + 0.2) * (1 - ramp(t, E["L27"] - 0.3, E["L27"]))
    drive(Y, "YOU", YOU_SEAT, 12, SIT, t * 0.6); sit_legs(Y)
    drive(J, "JESS", JESS_SEAT + Vector((0, 0, bounceJ)), -22, SIT, t * 0.6 + 1.3); sit_legs(J)
    # You sits forward on "So you can find your phone..." and stays forward (urgent) until she wins; smug lean back after
    fwd_ = ramp(t, S["L06"] - 0.05, S["L06"] + 0.3) * (1 - ramp(t, S["L24"] - 0.3, S["L24"] + 0.2))
    jolt = 4 * math.exp(-max(0.0, t - S["L06"]) / 0.15) * (t >= S["L06"])
    back = ramp(t, S["L24"] - 0.3, S["L24"] + 0.3) * (1 - ramp(t, T_TEXT, T_TEXT + 0.4))
    rot_bone(Y["arm"], "Bip01 Spine", (0, 0, 10 * fwd_ + jolt - 6 * back)); rot_bone(Y["arm"], "Bip01 Spine1", (0, 0, 6 * fwd_))
    rockJ = osc(t, 8.5, S["L05"], E["L05"] + 0.15, 5) + osc(t, 9.0, S["L22"], T_PRESS + 0.5, 6)
    if rockJ: rot_bone(J["arm"], "Bip01 Spine1", (0, 0, rockJ))
    bpy.context.view_layer.update()
    # looks first (the Biped clavicles hang off the neck), then the hands
    name = shot_at(t)[0]
    hY = head_of("YOU"); hJ = head_of("JESS"); camp = cam_loc
    lookY, wY = NEW.matrix_world.translation.copy() if NEW.location.z > -10 else None, 0.9
    if S["L03"] <= t < S["L04"] - 0.1: lookY, wY = hJ, 0.6
    if S["L04"] + 0.25 <= t < S["L05"] - 0.1: Fy, _ = body_frame(Y); lookY, wY = hY + Fy * 2.0 + Vector((0, 0, -0.1)), 0.9
    if S["L13"] <= t < S["L15"] - 0.1: lookY, wY = hJ, 0.6
    if S["L18"] <= t < W("L19", "camera") - 0.1: lookY, wY = hJ, 0.5
    if W("L19", "camera") - 0.1 <= t < T_DIVE2 and camp is not None: lookY, wY = camp, 1.0
    if S["L07"] - 0.1 <= t < T_DIVE1 and camp is not None: lookY, wY = camp, 1.0
    if S["L24"] - 0.1 <= t < T_TEXT and camp is not None: lookY, wY = camp, 1.0            # "Cheers, Biscuit." down the lens
    if S["L27"] + 0.3 <= t < E["L27"] + 0.2: lookY, wY = hJ, lerp(0.3, 1.0, ramp(t, S["L27"] + 0.3, S["L27"] + 1.6))   # the slow turn to Jess...
    if t >= E["L27"] + 0.2 and camp is not None: lookY, wY = camp, ramp(t, E["L27"] + 0.2, E["L27"] + 1.0)              # ...then to camera
    lookJ, wJ = hY + Vector((0, 0, -0.1)), 0.8
    if S["L13"] <= t < S["L15"]: lookJ, wJ = hY, 0.5
    if T_TEXT <= t < S["L26"] + 0.6: lookJ, wJ = NEW.matrix_world.translation.copy(), 0.8
    if t >= S["L27"] and camp is not None and name == "biscuit": lookJ, wJ = hY, 0.8
    if lookY is not None: look_at(Y, lookY, wY)
    look_at(J, lookJ, wJ)
    # You: the phone in both hands; up to the lens on "Oi, camera"; left hand only when she points ("Camera!")
    pointing = W("L19", "camera") - 0.15 <= t < T_DIVE2 + 0.6
    if S["L07"] - 0.2 <= t < T_DEN1 + 0.2 and camp is not None:
        up = ramp(t, S["L07"] - 0.2, S["L07"] + 0.25)
        place_phone_in_hands(Y, NEW, dist=lerp(0.3, 0.42, up), drop=lerp(-0.1, 0.12, up), tilt_to=(CAM_HOLD if up > 0.5 else None))
    elif pointing:
        phone_in_left(Y, NEW, tilt_to=(CAM_OUT_END if t >= T_DIVE2 - 0.05 else None))
        F_, R_ = body_frame(Y); sh_ = bone_world(Y["arm"], "Bip01 R UpperArm"); tgt = CAM_OUT_END if camp is None else camp
        chY = bone_world(Y["arm"], "Bip01 Spine2"); drop = ease(ramp(t, T_DIVE2 - 0.02, T_DIVE2 + 0.22))   # the pointing hand drops to her knee as the camera dives
        hand_to(Y, "R", (sh_ + (tgt - sh_).normalized() * 0.5).lerp(chY + F_ * 0.3 + R_ * 0.17 + Vector((0, 0, -0.36)), drop), (0, 0, -0.6))
    else:
        place_phone_in_hands(Y, NEW, dist=0.32, drop=-0.03)
    show(NEW_TX, *screen_her(t))
    pp, pn, _ = phone_nup(NEW); ph_glow.location = pp + pn * 0.12
    # Jess: hands up (sorry), outraged point, flapping, her own phone at her ear, hands clasped, fists, beaming
    F_, R_ = body_frame(J); chJ = bone_world(J["arm"], "Bip01 Spine2")
    JPH.location = OFFSTAGE
    def both(dz, fw, wide, wob=0.0):
        for side, s_ in (("L", 1), ("R", -1)):
            hand_to(J, side, chJ + F_ * fw + R_ * (-wide * s_) + Vector((0, 0, dz + wob * s_)), (0, 0, -0.6))
    if t < S["L03"] - 0.1: both(0.12, 0.25, 0.2, 0.02 * math.sin(t * 6))                     # hands up: "I'm so sorry"
    elif t < S["L05"]: both(-0.05 + 0.04 * math.sin(t * 4), 0.3, 0.17)                         # confident, explaining
    elif t < S["L06"] + 0.3:                                                                    # outraged: points at the phone
        hand_to(J, "R", chJ + F_ * 0.3 + R_ * 0.05 + Vector((0, 0, 0.0)), (0, 0, -0.6)); hand_to(J, "L", NEW.location.lerp(chJ, 0.45) + Vector((0, 0, 0.05)), (0, 0, -0.6))
    elif S["L11"] - 0.1 <= t < S["L12"]: both(0.02 + 0.1 * abs(math.sin(t * 11)), 0.28, 0.22)     # flapping: "Turn it off!"
    elif S["L13"] - 0.15 <= t < S["L15"] - 0.1:                                                # her own phone at her ear
        hh = hJ; ear = hh + R_ * (-0.11) + Vector((0, 0, -0.03)) + F_ * 0.02
        JPH.location = ear; aim_screen(JPH, ear - R_ * 0.3); JPH.rotation_euler.rotate_axis("Z", math.radians(80))
        hand_to(J, "L", ear + Vector((0, 0, -0.07)) - F_ * 0.02, (0, 0, -0.6)); hand_to(J, "R", chJ + F_ * 0.25 + R_ * 0.12 + Vector((0, 0, -0.2)), (0, 0, -0.5))
    elif S["L18"] - 0.1 <= t < E["L19"]: both(0.0, 0.26, 0.05)                                  # hands clasped, hopeful
    elif S["L22"] - 0.1 <= t < T_PRESS + 0.5: both(-0.06 + 0.04 * math.sin(t * 9), 0.3, 0.16)     # fists up: "PRESS IT!"
    elif t >= S["L27"] - 0.1: both(0.02, 0.24, 0.04)                                            # beaming, hands clasped
    else: both(-0.2, 0.26, 0.12)                                                               # hands in her lap
    # faces
    set_face(Y, t, "YOU", [[0, "worried", 1], [S["L02"], "worried", 0.7], [S["L04"], "shock", 0.8], [S["L05"], "focused", 0.5], [S["L06"], "panic", 0.5],
                           [S["L07"], "angry", 0.6], [S["L10"], "panic", 1], [S["L10"] + 1.3, "angry", 0.9], [S["L12"], "focused", 1], [S["L14"], "angry", 0.8],
                           [S["L15"], "focused", 1], [T_GONE, "smug", 0.5], [S["L18"] + 0.3, "focused", 0.8], [S["L19"], "panic", 0.5], [S["L21"], "focused", 1],
                           [T_PRESS + 0.1, "surprised", 0.6], [S["L24"] - 0.15, "smug", 1], [T_TEXT + 0.6, "focused", 0.4], [S["L26"], "smug", 0.6],
                           [S["L27"] + 0.4, "incredulous", 0.6], [E["L27"] + 0.1, "deadpan", 1]], lips=True)
    set_face(J, t, "JESS", [[0, "guilty", 1], [S["L03"] - 0.1, "proud", 0.9], [S["L04"] + 0.6, "surprised", 0.6], [S["L05"] - 0.1, "outraged", 1],
                            [S["L06"] + 0.5, "worried", 0.7], [S["L10"], "panic", 1], [S["L13"] - 0.1, "excited", 0.6], [S["L14"], "surprised", 0.6],
                            [S["L18"] - 0.1, "helpful", 0.8], [S["L20"], "worried", 0.8], [S["L22"] - 0.1, "panic", 1], [T_PRESS + 0.3, "surprised", 0.8],
                            [S["L24"], "happy", 0.8], [T_TEXT + 0.4, "worried", 1], [S["L27"] - 0.1, "beaming", 1]], lips=True)
    tv.data.energy = 45 * (0.85 + 0.15 * math.sin(t * 7.3) * math.sin(t * 2.1))
    bpy.context.view_layer.update()

# =====================================================================================================================
cam = bpy.data.objects.new("cam", bpy.data.cameras.new("cam")); col.objects.link(cam); sc.camera = cam
cam.data.sensor_fit = "VERTICAL"; cam.data.sensor_height = 36; cam.data.dof.use_dof = True; cam.data.dof.aperture_fstop = 2.4; cam.data.clip_start = 0.01
cam.data.clip_end = 200.0
fill_d = bpy.data.lights.new("cam_fill", "AREA"); fill_d.energy = 25; fill_d.size = 1.0; fill_d.color = (1.0, 0.9, 0.82); fill_d.use_shadow = False
fill = bpy.data.objects.new("cam_fill", fill_d); col.objects.link(fill); fill.parent = cam; fill.location = (0.25, 0.3, 0.1)
CLOSE = ("dive1", "dive2", "back", "thumb", "fix", "finger", "kicked", "ots")
ph_glow.visible_camera = False
MIN_HEAD = 0.17     # the camera must stay this far from You's head bone, or it ends up inside her face (her screen close-ups)
def clear_of_head(p, tg):
    hY = head_of("YOU")
    if (p - hY).length >= MIN_HEAD: return p, 1.0
    lo, hi = 0.15, 1.0      # slide the camera toward what it looks at until it is clear of her face
    for _ in range(24):
        mid = (lo + hi) / 2
        if (tg + (p - tg) * mid - hY).length >= MIN_HEAD: lo = mid
        else: hi = mid
    return tg + (p - tg) * lo, lo
def set_cam(t):
    name, t0, t1, fn = shot_at(t); r = fn(t); p, tg, lens, foc = r[:4]; roll = r[4] if len(r) > 4 else 0.0
    k = 1.0
    if name not in DEN_SHOTS: p, k = clear_of_head(p, tg); lens *= k ** 0.8     # wider lens keeps the framing
    cam.location = p; cam.rotation_euler = (tg - p).to_track_quat("-Z", "Y").to_euler()
    if roll: cam.rotation_euler.rotate_axis("Z", math.radians(roll))
    cam.data.lens = lens; cam.data.dof.focus_distance = max(0.03, (foc - p).length)
    cam.data.dof.aperture_fstop = (8.0 if k < 1.0 else 5.6) if name in CLOSE else 2.4
    fill_d.energy = 3 if name in DEN_SHOTS else (4 if name in CLOSE else 25)
    return name

sc.render.engine = "CYCLES"; sc.cycles.device = "CPU"; sc.cycles.samples = a.samples; sc.cycles.use_denoising = True
sc.cycles.max_bounces = 4; sc.cycles.transparent_max_bounces = 8; sc.cycles.diffuse_bounces = 2; sc.cycles.glossy_bounces = 2
sc.render.resolution_x, sc.render.resolution_y = a.res; sc.render.fps = FPS
if a.threads: sc.render.threads_mode = "FIXED"; sc.render.threads = a.threads
sc.view_settings.view_transform = "AgX"; sc.view_settings.look = "AgX - Punchy"
sc.frame_set(1)

def render_frame(f, path):
    t = f / FPS
    set_frame(t); set_cam(t); set_frame(t, cam.location.copy()); shot = set_cam(t)    # pass 2: looks/phone that aim at the lens
    sc.render.filepath = os.path.abspath(path)
    if os.environ.get("DBG") == "2":
        pp_, pn_, _ = phone_nup(NEW)
        print("DBG", f, shot, tuple(round(v, 3) for v in cam.location), "dYOU", round((cam.location - head_of("YOU")).length, 3),
              "dJESS", round((cam.location - head_of("JESS")).length, 3), "phone-headY", round((pp_ - head_of("YOU")).length, 3),
              "n.toHead", round(pn_.dot((head_of("YOU") - pp_).normalized()), 2), "dHOOD", round((cam.location - head_of("HOOD")).length, 3),
              "dHandR", round((cam.location - bone_world(C["YOU"]["arm"], "Bip01 R Hand")).length, 3), flush=True); return
    t0 = time.time(); bpy.ops.render.render(write_still=True); print(f"rendered {path} shot={shot} t={t:.2f} {time.time() - t0:.1f}s", flush=True)

F_END = int(math.ceil(T_END * FPS))
if a.test:
    od = "build/p2_test"; os.makedirs(od, exist_ok=True)
    pts = []
    for name, t0, t1, fn in SHOTS:
        if name == "race":
            pts += [(f"race{i}", (x + y) / 2) for i, (x, y) in enumerate(zip(RACE, RACE[1:]))]
        else:
            pts.append((name, max(0.05, t0) + (min(t1, T_END) - max(0.05, t0)) * 0.6))
    for name, tm in pts:
        if a.shots and not any(name.startswith(s_) for s_ in a.shots): continue
        f = int(round(tm * FPS)); rig.PREV.clear(); render_frame(f, os.path.join(od, f"{f:04d}_{name}.png"))
elif a.list:
    os.makedirs(a.out, exist_ok=True)
    for f in a.list: rig.PREV.clear(); render_frame(f, os.path.join(a.out, f"{f:04d}.png"))
elif a.one is not None:
    os.makedirs(a.out, exist_ok=True); render_frame(a.one, os.path.join(a.out, f"{a.one:04d}.png"))
else:
    os.makedirs(a.out, exist_ok=True); f0, f1 = a.frames
    print(f"Part 2: frames 0..{F_END} (this job {f0}..{f1})", flush=True)
    for f in range(max(f0, 0), min(f1, F_END), a.step):
        p = os.path.join(a.out, f"{f:04d}.png")
        if os.path.exists(p): set_frame(f / FPS); continue
        render_frame(f, p)
