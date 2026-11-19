"""world.py: the Phoneverse 3D world (option A format). One set, every episode: a hero phone on a desk at night, a miniature phone mast,
the scammer's laptop, an 'Unknown Senders' tray, glowing data packets, and a phone that opens to show its circuit board.
The episode is driven by a beat sheet (data/beats_<ep>.json): camera moves, what the phone screen shows, packets, lid and filter switch.
Frame-driven: every frame's state is computed from the beat sheet, so any frame renders on its own (resumable, any order).

  .venv/bin/python render/world.py --beats data/beats_fix12.json --frames 0 1666            # full render -> build/frames/00000.png
  .venv/bin/python render/world.py --beats data/beats_fix12.json --test                     # one frame per beat -> build/test/
Writes build/anchors/<frame>.json (screen-space positions of named objects) so compose3d.py can pin crisp 2D labels to them."""
import argparse, json, math, os, sys, hashlib
import bpy
from mathutils import Vector
from bpy_extras.object_utils import world_to_camera_view

HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE); import pvui as U

ap = argparse.ArgumentParser()
ap.add_argument("--beats", required=True); ap.add_argument("--frames", nargs=2, type=int); ap.add_argument("--test", action="store_true"); ap.add_argument("--one", type=int, help="render just this frame")
ap.add_argument("--samples", type=int, default=24); ap.add_argument("--res", nargs=2, type=int, default=[720, 1280]); ap.add_argument("--out", default="build")
a = ap.parse_args(sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else None)
B = json.load(open(a.beats)); FPS = B.get("fps", 24); BEATS = B["beats"]
ease = lambda p: p * p * (3 - 2 * p)
clamp = lambda p: max(0.0, min(1.0, p))

# ------------------------------------------------------------------------------------------------ set dressing
bpy.ops.wm.read_factory_settings(use_empty=True); sc = bpy.context.scene; col = sc.collection

def mat(name, color=(0.5, 0.5, 0.5), metal=0.0, rough=0.5, emit=None, strength=1.0):
    m = bpy.data.materials.new(name); nt = m.node_tree if m.node_tree else None
    if nt is None: m.use_nodes = True; nt = m.node_tree
    b = nt.nodes.get("Principled BSDF"); b.inputs["Base Color"].default_value = (*color, 1); b.inputs["Metallic"].default_value = metal; b.inputs["Roughness"].default_value = rough
    if emit: b.inputs["Emission Color"].default_value = (*emit, 1); b.inputs["Emission Strength"].default_value = strength
    return m
def box(name, dims, loc, m, bevel=0.0):
    bpy.ops.mesh.primitive_cube_add(size=1, location=loc); o = bpy.context.active_object; o.name = name; o.scale = dims
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)       # scale only: keep the origin at the part (pivots, knob slide)
    if bevel: md = o.modifiers.new("bev", "BEVEL"); md.width = bevel; md.segments = 5
    o.data.materials.append(m); return o
def empty(name, loc, parent=None):
    e = bpy.data.objects.new(name, None); col.objects.link(e); e.location = loc
    if parent: e.parent = parent
    return e

# desk: procedural wood, warm
bpy.ops.mesh.primitive_plane_add(size=4, location=(0, 0.4, 0)); desk = bpy.context.active_object; desk.name = "desk"
dm = bpy.data.materials.new("wood"); dm.use_nodes = True; nt = dm.node_tree; bs = nt.nodes["Principled BSDF"]
wv = nt.nodes.new("ShaderNodeTexWave"); wv.inputs["Scale"].default_value = 60; wv.inputs["Distortion"].default_value = 6; wv.inputs["Detail"].default_value = 8
cr = nt.nodes.new("ShaderNodeValToRGB"); cr.color_ramp.elements[0].color = (0.10, 0.045, 0.018, 1); cr.color_ramp.elements[1].color = (0.17, 0.075, 0.03, 1)
nt.links.new(wv.outputs["Fac"], cr.inputs[0]); nt.links.new(cr.outputs[0], bs.inputs["Base Color"]); bs.inputs["Roughness"].default_value = 0.35
bp = nt.nodes.new("ShaderNodeBump"); bp.inputs["Strength"].default_value = 0.15; nt.links.new(wv.outputs["Fac"], bp.inputs["Height"]); nt.links.new(bp.outputs[0], bs.inputs["Normal"])
desk.data.materials.append(dm)

# hero phone at the origin, lying flat, top edge towards +y
PH = (0.075, 0.155, 0.009)
body = box("phone_body", PH, (0, 0, PH[2] / 2), mat("graphite", (0.05, 0.055, 0.065), 0.85, 0.28), bevel=0.006)
rimm = mat("rimm", (0.05, 0.055, 0.065), 0.85, 0.28)                 # open side walls up to the raised screen
for dx_, dy_, w_, l_ in ((0, PH[1] / 2 - 0.0008, PH[0], 0.0016), (0, -PH[1] / 2 + 0.0008, PH[0], 0.0016), (PH[0] / 2 - 0.0008, 0, 0.0016, PH[1]), (-PH[0] / 2 + 0.0008, 0, 0.0016, PH[1])):
    box("wall", (w_, l_, 0.0034), (dx_, dy_, PH[2] + 0.0015), rimm)
pcb = box("pcb", (0.066, 0.146, 0.0006), (0, 0, PH[2] + 0.0002), mat("pcb", (0.02, 0.22, 0.13), 0.1, 0.45))
chipm = mat("chip", (0.02, 0.02, 0.025), 0.2, 0.3); gold = mat("gold", (0.9, 0.65, 0.2), 1.0, 0.25)
z0 = PH[2] + 0.0008
box("cpu", (0.02, 0.02, 0.0018), (0.004, 0.025, z0), chipm); box("modem", (0.013, 0.011, 0.0016), (0.02, 0.052, z0), chipm)
box("sim", (0.012, 0.016, 0.0012), (-0.019, 0.05, z0), gold); box("battery", (0.056, 0.056, 0.0022), (0, -0.038, z0), mat("batt", (0.25, 0.26, 0.3), 0.6, 0.4))
box("filter_track", (0.02, 0.006, 0.0012), (-0.016, 0.004, z0), mat("track", (0.08, 0.08, 0.1), 0.3, 0.4))
knob = box("filter_knob", (0.0065, 0.0065, 0.0028), (-0.022, 0.004, z0 + 0.0008), mat("knob", (0.9, 0.9, 0.92), 0.0, 0.3, emit=(1.0, 0.45, 0.05), strength=0.0), bevel=0.001)
# screen: an emissive plane showing the current UI (pvui), hinged at the top edge so it can lift away
SZ = PH[2] + 0.0032                                    # screen height: above the tallest part
hinge = empty("screen_hinge", (0, PH[1] / 2 - 0.004, SZ))
bpy.ops.mesh.primitive_plane_add(size=1, location=(0, -(PH[1] / 2 - 0.004) + 0.0005, 0.0)); scr = bpy.context.active_object; scr.name = "screen"
scr.scale = (0.069, 0.149, 1); bpy.ops.object.transform_apply(scale=True); scr.parent = hinge
sm = bpy.data.materials.new("screen"); sm.use_nodes = True; nt = sm.node_tree
for nd in list(nt.nodes): nt.nodes.remove(nd)
img_node = nt.nodes.new("ShaderNodeTexImage"); emi = nt.nodes.new("ShaderNodeEmission"); emi.inputs["Strength"].default_value = 1.6
glossy = nt.nodes.new("ShaderNodeBsdfGlossy"); glossy.inputs["Roughness"].default_value = 0.08; mix = nt.nodes.new("ShaderNodeMixShader"); mix.inputs[0].default_value = 0.06
out = nt.nodes.new("ShaderNodeOutputMaterial"); nt.links.new(img_node.outputs[0], emi.inputs[0]); nt.links.new(emi.outputs[0], mix.inputs[1]); nt.links.new(glossy.outputs[0], mix.inputs[2]); nt.links.new(mix.outputs[0], out.inputs[0])
scr.data.materials.append(sm)
glass_back = box("screen_back", (0.069, 0.149, 0.0006), (0, -(PH[1] / 2 - 0.004), -0.0004), mat("glassback", (0.02, 0.02, 0.025), 0.2, 0.2)); glass_back.parent = hinge

# miniature mast (the fake sender), scammer laptop, Unknown Senders tray
mastm = mat("mast", (0.75, 0.76, 0.8), 0.7, 0.35)
bpy.ops.mesh.primitive_cylinder_add(radius=0.005, depth=0.33, location=(-0.15, 0.33, 0.165)); bpy.context.active_object.data.materials.append(mastm)
for k in range(3):
    ang = k * 2 * math.pi / 3; p_ = box(f"panel{k}", (0.012, 0.004, 0.045), (-0.15 + 0.012 * math.cos(ang), 0.33 + 0.012 * math.sin(ang), 0.30), mastm); p_.rotation_euler.z = ang + math.pi / 2
bpy.ops.mesh.primitive_uv_sphere_add(radius=0.006, location=(-0.15, 0.33, 0.335)); blink = bpy.context.active_object; blink.data.materials.append(mat("blink", (1, 0.1, 0.1), emit=(1, 0.08, 0.05), strength=6))
lap_base = box("laptop_base", (0.13, 0.09, 0.006), (0.16, 0.36, 0.003), mat("lapbody", (0.05, 0.05, 0.06), 0.4, 0.5), bevel=0.002)
lid = box("laptop_lid", (0.13, 0.005, 0.088), (0.16, 0.407, 0.047), mat("lapbody2", (0.05, 0.05, 0.06), 0.4, 0.5), bevel=0.002); lid.rotation_euler.x = math.radians(-12)
lapscr = box("laptop_screen", (0.118, 0.001, 0.076), (0.16, 0.4035, 0.047), mat("lapscr", (0.02, 0, 0), emit=(1.0, 0.12, 0.1), strength=1)); lapscr.rotation_euler.x = math.radians(-12)
from PIL import Image as _I, ImageDraw as _D; import random as _r
_im = _I.new("RGB", (472, 304), (8, 4, 6)); _d = _D.Draw(_im); _r.seed(4)
for _y in range(18, 300, 22): _d.rectangle((16, _y, 16 + _r.randint(60, 420), _y + 9), fill=(255, 50, 40) if _r.random() < 0.3 else (120, 30, 30))
_p = os.path.join(a.out, "laptop_screen.png"); os.makedirs(a.out, exist_ok=True); _im.save(_p)
_nt = lapscr.active_material.node_tree; _tx = _nt.nodes.new("ShaderNodeTexImage"); _tx.image = bpy.data.images.load(os.path.abspath(_p))
_nt.links.new(_tx.outputs[0], _nt.nodes["Principled BSDF"].inputs["Emission Color"])
_tc = _nt.nodes.new("ShaderNodeTexCoord"); _sp = _nt.nodes.new("ShaderNodeSeparateXYZ"); _cb = _nt.nodes.new("ShaderNodeCombineXYZ")   # map the image onto the x/z face, not the cube cross
_mx = _nt.nodes.new("ShaderNodeMath"); _mx.operation = "MULTIPLY_ADD"; _mx.inputs[1].default_value = 1 / 0.118; _mx.inputs[2].default_value = 0.5
_mz = _nt.nodes.new("ShaderNodeMath"); _mz.operation = "MULTIPLY_ADD"; _mz.inputs[1].default_value = 1 / 0.076; _mz.inputs[2].default_value = 0.5
_nt.links.new(_tc.outputs["Object"], _sp.inputs[0]); _nt.links.new(_sp.outputs[0], _mx.inputs[0]); _nt.links.new(_sp.outputs[2], _mz.inputs[0])
_nt.links.new(_mx.outputs[0], _cb.inputs[0]); _nt.links.new(_mz.outputs[0], _cb.inputs[1]); _nt.links.new(_cb.outputs[0], _tx.inputs[0])
box("keyboard", (0.11, 0.05, 0.0008), (0.16, 0.355, 0.0062), mat("keys", (0.015, 0.015, 0.02), 0.1, 0.7))
lap_light = bpy.data.objects.new("lap_light", bpy.data.lights.new("lap_light", "POINT")); col.objects.link(lap_light); lap_light.location = (0.16, 0.32, 0.08); lap_light.data.color = (1, 0.15, 0.1); lap_light.data.energy = 3
traym = mat("tray", (0.12, 0.2, 0.42), 0.3, 0.4)
TR = Vector((0.13, -0.15, 0.0))
for nm_, d_, l_ in (("tray_floor", (0.08, 0.06, 0.003), (0, 0, 0.0015)), ("tray_w1", (0.08, 0.003, 0.018), (0, 0.0285, 0.009)), ("tray_w2", (0.08, 0.003, 0.018), (0, -0.0285, 0.009)),
                    ("tray_w3", (0.003, 0.06, 0.018), (0.0385, 0, 0.009)), ("tray_w4", (0.003, 0.06, 0.018), (-0.0385, 0, 0.009))):
    box(nm_, d_, TR + Vector(l_), traym)

# anchors for 2D labels (compose3d.py pins tags to these)
ANCH = {"screen": (0, 0, PH[2] + 0.004), "modem": (0.02, 0.052, z0), "sim": (-0.019, 0.05, z0), "filter": (-0.016, 0.004, z0 + 0.002), "cpu": (0.004, 0.025, z0),
        "mast": (-0.15, 0.33, 0.33), "laptop": (0.16, 0.407, 0.09), "tray": tuple(TR + Vector((0, 0, 0.02))), "phone": (0, -0.06, PH[2])}
for k, v in ANCH.items(): empty("anchor_" + k, v)
NODES = {"mast": Vector((-0.15, 0.33, 0.335)), "phone": Vector((0.02, 0.052, z0 + 0.006)), "laptop": Vector((0.16, 0.38, 0.06)), "tray": TR + Vector((0, 0, 0.012))}

# packets: a glowing head + 5 trail beads per slot, 4 slots
PCOL = {"text": (1.0, 0.75, 0.1), "card": (1.0, 0.1, 0.15), "call": (0.25, 0.55, 1.0)}
PM = {k: mat("pk_" + k, (0, 0, 0), emit=c, strength=12) for k, c in PCOL.items()}
SLOTS = []
for s_ in range(4):
    beads = []
    for j in range(6):
        bpy.ops.mesh.primitive_uv_sphere_add(radius=0.0075 * (1 - j * 0.14), segments=16, ring_count=8); o = bpy.context.active_object; o.name = f"pk{s_}_{j}"; beads.append(o)
        o.visible_shadow = False
    SLOTS.append(beads)

# lights + world
def area(name, loc, energy, color, size):
    d = bpy.data.lights.new(name, "AREA"); d.energy = energy; d.color = color; d.size = size; o = bpy.data.objects.new(name, d); col.objects.link(o); o.location = loc
    o.rotation_euler = (Vector((0, 0.1, 0)) - Vector(loc)).to_track_quat("-Z", "Y").to_euler(); return o
area("key", (-0.5, -0.4, 0.8), 30, (1.0, 0.78, 0.55), 0.6); area("rim", (0.5, 0.9, 0.5), 45, (0.5, 0.65, 1.0), 0.6); area("fill", (0.6, -0.6, 0.4), 10, (0.8, 0.85, 1.0), 1.0)
w = bpy.data.worlds.new("w"); sc.world = w; w.use_nodes = True; w.node_tree.nodes["Background"].inputs[0].default_value = (0.012, 0.014, 0.03, 1)

# camera presets: (location, target, lens mm). Portrait 9:16, vertical sensor 36 mm.
CAM = {"hero": ((0.15, -0.28, 0.19), (0, 0.01, 0), 42), "screen": ((0.0, -0.045, 0.27), (0, 0.0, 0), 50), "screen_close": ((0.0, -0.03, 0.19), (0, 0.005, 0), 50),
       "screen_tilt": ((0.06, -0.19, 0.2), (0, 0.01, 0), 50), "macro": ((0.03, -0.055, 0.065), (-0.005, 0.02, 0.004), 35),
       "macro_filter": ((-0.005, -0.03, 0.045), (-0.016, 0.006, 0.004), 35), "mast": ((-0.05, 0.02, 0.16), (-0.15, 0.33, 0.25), 35),
       "laptop": ((0.08, 0.14, 0.12), (0.16, 0.39, 0.06), 35), "wide": ((0.0, -0.52, 0.40), (0.0, 0.14, 0.08), 28), "tray": ((0.08, -0.34, 0.15), (0.12, -0.13, 0.01), 40),
       "top": ((0.0, 0.06, 0.82), (0.0, 0.10, 0), 28)}
cam = bpy.data.objects.new("cam", bpy.data.cameras.new("cam")); col.objects.link(cam); sc.camera = cam
cam.data.sensor_fit = "VERTICAL"; cam.data.sensor_height = 36; cam.data.dof.use_dof = True; cam.data.dof.aperture_fstop = 5.6; cam.data.clip_start = 0.005

# ------------------------------------------------------------------------------------------------ state from the beat sheet
def beat_at(t): return next((b for b in BEATS if b["t0"] <= t < b["t1"]), BEATS[-1])
def track(kind, t, default=0.0):
    """Persistent value for 'lid' / 'filter' / 'laptop': the latest event of that kind at or before t, eased from 'from' to 'to'."""
    v = default
    for b in BEATS:
        for e in b.get("events", []):
            if e["type"] == kind and e["t0"] <= t: v = e["from"] + (e["to"] - e["from"]) * ease(clamp((t - e["t0"]) / max(1e-3, e["t1"] - e["t0"])))
    return v
def bez(p0, p2, h, u):
    p1 = (p0 + p2) / 2 + Vector((0, 0, h)); return (1 - u) ** 2 * p0 + 2 * (1 - u) * u * p1 + u * u * p2
SCREEN_DIR = os.path.join(a.out, "screens"); os.makedirs(SCREEN_DIR, exist_ok=True); _last = [None]
def set_screen(spec, p):
    if not spec: spec = "U.canvas((5, 5, 8))"
    import re; key = spec + (f"@{round(p * 48) / 48:.4f}" if re.search(r"\bp\b", spec) else "")
    if key == _last[0]: return
    f = os.path.join(SCREEN_DIR, hashlib.md5(key.encode()).hexdigest()[:12] + ".png")
    if not os.path.exists(f):
        im = eval(spec, {"U": U, "p": round(p * 48) / 48, "ease": ease, "clamp": clamp}); im.convert("RGB").resize((540, 960)).save(f)
    img = bpy.data.images.load(f, check_existing=True); img_node.image = img; _last[0] = key

def apply(t):
    b = beat_at(t); p = clamp((t - b["t0"]) / max(1e-3, b["t1"] - b["t0"]))
    ca, cb = b["cam"] if isinstance(b["cam"], list) else (b["cam"], b["cam"]); A, Bc = CAM[ca], CAM[cb]; k = ease(p)
    loc = Vector(A[0]).lerp(Vector(Bc[0]), k); tgt = Vector(A[1]).lerp(Vector(Bc[1]), k); cam.data.lens = A[2] + (Bc[2] - A[2]) * k
    cam.location = loc; cam.rotation_euler = (tgt - loc).to_track_quat("-Z", "Y").to_euler(); cam.data.dof.focus_distance = (tgt - loc).length
    set_screen(b.get("screen"), p)
    lidv = track("lid", t); hinge.rotation_euler.x = math.radians(-75) * lidv; hinge.location.z = SZ + 0.012 * lidv
    fv = track("filter", t); knob.location.x = -0.022 + 0.012 * fv; knob.active_material.node_tree.nodes["Principled BSDF"].inputs["Emission Strength"].default_value = 6 * fv
    lv = track("laptop", t, 0.4); lapscr.active_material.node_tree.nodes["Principled BSDF"].inputs["Emission Strength"].default_value = 1.0 + 2.0 * lv; lap_light.data.energy = 0.08 + 0.4 * lv
    blink.hide_render = int(t * 2) % 2 == 1
    active = [e for bb in BEATS for e in bb.get("events", []) if e["type"] == "packet" and e["t0"] <= t < e["t1"]]
    pk_pos = None
    for s_, beads in enumerate(SLOTS):
        e = active[s_] if s_ < len(active) else None
        for j, o in enumerate(beads):
            o.hide_render = e is None
            if e is None: continue
            frm, to = e["path"].split(">"); u = clamp((t - e["t0"]) / (e["t1"] - e["t0"]) - j * 0.03)
            pos = bez(NODES[frm], NODES[to], e.get("arc", 0.18), ease(u)); o.location = pos; o.data.materials.clear(); o.data.materials.append(PM[e["kind"]])
            if j == 0 and s_ == 0: pk_pos = pos
    return b, pk_pos

def anchors(pk_pos):
    out = {}
    for k in ANCH:
        v = world_to_camera_view(sc, cam, bpy.data.objects["anchor_" + k].location)
        out[k] = [round(v.x, 4), round(1 - v.y, 4), round(v.z, 4)]
    if pk_pos is not None: v = world_to_camera_view(sc, cam, pk_pos); out["packet"] = [round(v.x, 4), round(1 - v.y, 4), round(v.z, 4)]
    return out

# ------------------------------------------------------------------------------------------------ render
sc.render.engine = "CYCLES"; sc.cycles.device = "CPU"; sc.cycles.samples = a.samples; sc.cycles.use_denoising = True; sc.render.use_persistent_data = True
sc.render.resolution_x, sc.render.resolution_y = a.res; sc.view_settings.view_transform = "AgX"; sc.view_settings.look = "AgX - Medium High Contrast"
total = int(round(B["length_s"] * FPS))
if a.one is not None: frames = [a.one]; sub = "one"
elif a.test: frames = [int(((b["t0"] + b["t1"]) / 2) * FPS) for b in BEATS if not b.get("face")]; sub = "test"
else: frames = [f for f in range(a.frames[0], min(a.frames[1] + 1, total)) if not beat_at(f / FPS).get("face")]; sub = "frames"
os.makedirs(os.path.join(a.out, sub), exist_ok=True); os.makedirs(os.path.join(a.out, "anchors"), exist_ok=True)
for f in frames:
    pth = os.path.join(a.out, sub, f"{f:05d}.png")
    if os.path.exists(pth): continue
    b, pk = apply(f / FPS); bpy.context.view_layer.update()
    json.dump(anchors(pk), open(os.path.join(a.out, "anchors", f"{f:05d}.json"), "w"))
    sc.render.filepath = os.path.abspath(pth); bpy.ops.render.render(write_still=True); print("rendered", pth, flush=True)
