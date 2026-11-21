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
# Natural grain (v2, FIX #13): the old single wave texture read as regular corduroy stripes in wide shots. Now: object coords stretched
# along x (long fibres), warped by a low-frequency noise so lines wander, a fine noise for fibre detail, and a broad noise for
# board-to-board colour variation. No two lines are evenly spaced.
tc = nt.nodes.new("ShaderNodeTexCoord"); mp = nt.nodes.new("ShaderNodeMapping"); mp.inputs["Scale"].default_value = (1.2, 26.0, 1.2)
nt.links.new(tc.outputs["Object"], mp.inputs["Vector"])
warp = nt.nodes.new("ShaderNodeTexNoise"); warp.inputs["Scale"].default_value = 1.6; warp.inputs["Detail"].default_value = 3; warp.inputs["Distortion"].default_value = 0.6
nt.links.new(tc.outputs["Object"], warp.inputs["Vector"])
wadd = nt.nodes.new("ShaderNodeVectorMath"); wadd.operation = "MULTIPLY_ADD"; wadd.inputs[1].default_value = (0.0, 2.2, 0.0)
nt.links.new(warp.outputs["Color"], wadd.inputs[0]); nt.links.new(mp.outputs["Vector"], wadd.inputs[2])
grain = nt.nodes.new("ShaderNodeTexNoise"); grain.inputs["Scale"].default_value = 2.4; grain.inputs["Detail"].default_value = 12; grain.inputs["Roughness"].default_value = 0.62; grain.inputs["Distortion"].default_value = 0.35
nt.links.new(wadd.outputs["Vector"], grain.inputs["Vector"])
cr = nt.nodes.new("ShaderNodeValToRGB"); el = cr.color_ramp.elements
el[0].position = 0.30; el[0].color = (0.085, 0.036, 0.014, 1); el[1].position = 0.72; el[1].color = (0.19, 0.088, 0.036, 1)
mid = el.new(0.52); mid.color = (0.13, 0.058, 0.022, 1)
nt.links.new(grain.outputs["Fac"], cr.inputs[0])
board = nt.nodes.new("ShaderNodeTexNoise"); board.inputs["Scale"].default_value = 0.9; board.inputs["Detail"].default_value = 1
nt.links.new(tc.outputs["Object"], board.inputs["Vector"])
tint = nt.nodes.new("ShaderNodeMix"); tint.data_type = "RGBA"; tint.blend_type = "MULTIPLY"
nt.links.new(board.outputs["Fac"], tint.inputs["Factor"]); tint.inputs["Factor"].default_value = 0.5
nt.links.new(cr.outputs[0], tint.inputs[6]); tint.inputs[7].default_value = (0.78, 0.74, 0.70, 1)
nt.links.new(tint.outputs[2], bs.inputs["Base Color"]); bs.inputs["Roughness"].default_value = 0.42
bp = nt.nodes.new("ShaderNodeBump"); bp.inputs["Strength"].default_value = 0.06; nt.links.new(grain.outputs["Fac"], bp.inputs["Height"]); nt.links.new(bp.outputs[0], bs.inputs["Normal"])
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

# ---- optional props, switched on per episode by the beat sheet header "props": [...]
PROPS = set(B.get("props", []))
def hide_all(objs, flag):
    for o in objs: o.hide_render = flag; o.hide_viewport = flag
# van with a fake mast that rises out of its roof (FIX #13, SMS blaster). Event "van": 0 = mast hidden in the roof, 1 = fully raised.
VAN = Vector((0.205, 0.10, 0.0))
vanm = mat("van", (0.78, 0.79, 0.80), 0.15, 0.45); glassm = mat("vanglass", (0.03, 0.04, 0.06), 0.1, 0.08); tyre = mat("tyre", (0.02, 0.02, 0.02), 0.0, 0.8)
van_objs = [box("van_body", (0.115, 0.05, 0.048), VAN + Vector((0.008, 0, 0.031)), vanm, bevel=0.004),
            box("van_cab", (0.03, 0.048, 0.034), VAN + Vector((-0.062, 0, 0.024)), vanm, bevel=0.005),
            box("van_wind", (0.002, 0.042, 0.016), VAN + Vector((-0.0775, 0, 0.032)), glassm),
            box("van_side_win", (0.022, 0.0505, 0.012), VAN + Vector((-0.062, 0, 0.033)), glassm)]
for wx in (-0.055, 0.04):
    for wy in (-0.026, 0.026):
        bpy.ops.mesh.primitive_cylinder_add(radius=0.011, depth=0.008, location=VAN + Vector((wx, wy, 0.011)), rotation=(math.pi / 2, 0, 0))
        o = bpy.context.active_object; o.data.materials.append(tyre); van_objs.append(o)
fake_root = empty("fake_root", VAN + Vector((0.02, 0, 0.055)))
fakem = mat("fakemast", (0.35, 0.36, 0.40), 0.6, 0.4); fakered = mat("fakered", (0.4, 0.02, 0.02), emit=(1.0, 0.1, 0.06), strength=3)
bpy.ops.mesh.primitive_cylinder_add(radius=0.0035, depth=0.12, location=(0, 0, 0.06)); fpole = bpy.context.active_object; fpole.data.materials.append(fakem); fpole.parent = fake_root
fake_objs = [fpole]
for k in range(3):
    ang = k * 2 * math.pi / 3; p_ = box(f"fpanel{k}", (0.009, 0.003, 0.03), (0.009 * math.cos(ang), 0.009 * math.sin(ang), 0.105), fakered); p_.rotation_euler.z = ang + math.pi / 2; p_.parent = fake_root; fake_objs.append(p_)
bpy.ops.mesh.primitive_uv_sphere_add(radius=0.0045, location=(0, 0, 0.123)); fblink = bpy.context.active_object; fblink.data.materials.append(mat("fblink", (1, 0.1, 0.1), emit=(1, 0.05, 0.03), strength=8)); fblink.parent = fake_root; fake_objs.append(fblink)
hide_all(van_objs + fake_objs, "van" not in PROPS)
# network filter: a ring around the real mast (the operator's spam filter). Event "netfilter": glow 0..1.
bpy.ops.mesh.primitive_torus_add(major_radius=0.026, minor_radius=0.0028, location=(-0.15, 0.33, 0.19)); nring = bpy.context.active_object; nring.name = "netfilter"
nringm = mat("netfilter", (0.05, 0.3, 0.12), emit=(0.15, 1.0, 0.35), strength=0.4); nring.data.materials.append(nringm); hide_all([nring], "netfilter" not in PROPS)
# signal links: thin beams from the phone's modem to the real mast (blue) and to the fake mast (red). Event "link": 0 real, 1 fake.
def beam(name, p0, p1, color):
    d = p1 - p0; bpy.ops.mesh.primitive_cylinder_add(radius=0.0011, depth=d.length, location=(p0 + p1) / 2); o = bpy.context.active_object; o.name = name
    o.rotation_euler = d.to_track_quat("Z", "Y").to_euler(); m = mat(name, (0, 0, 0), emit=color, strength=3); o.data.materials.append(m); o.visible_shadow = False; return o, m
PHONE_ANT = Vector((0.02, 0.06, PH[2] + 0.004))
link_real, link_real_m = beam("link_real", PHONE_ANT, Vector((-0.15, 0.33, 0.30)), (0.3, 0.6, 1.0))
link_fake, link_fake_m = beam("link_fake", PHONE_ANT, VAN + Vector((0.02, 0, 0.055 + 0.105)), (1.0, 0.12, 0.08))
hide_all([link_real, link_fake], "links" not in PROPS)


# ---- iPhone Duo (FIX #14): a book-style foldable that replaces the hero phone when "duo" is in props.
# duo_root carries the drop/bounce; the left half lies on the desk, the right half turns on a hinge along the long (y) edge at x = 0.
# Event "open": 0 = closed (right half folded on top), 1 = flat open. "lid": lifts both inner-screen panels to show the hinge.
# "hook": the hinge hook wiggles and glows (it catches on the screen as it opens). "drop": the fall + two bounces (0..1).
# "flash": camera-flash light. Inner / outer screens come from the beat's "inner" / "outer" pvui expressions.
DUO = "duo" in PROPS
DUO_ANCH = {}
if DUO:
    hide_all([o for o in col.objects if o.name.startswith(("phone_body", "wall", "pcb", "cpu", "modem", "sim", "battery", "filter_", "screen"))] + [scr, glass_back], True)
    hide_all([o for o in col.objects if o.name.startswith(("Cylinder", "panel", "Sphere", "laptop", "keyboard", "tray_"))] + [blink, lap_base, lid, lapscr], True)
    lap_light.data.energy = 0
    # v2 (user: "make it look like the real iPhone Duo"): Apple's product shot opens to a ~4:3 landscape screen with thin black bezels,
    # rounded corners, a titanium frame and hinge cover, Ceramic Shield back, dual 48MP cameras in the top corner. Each half 81 x 122 x 4.5 mm.
    DH = (0.081, 0.122, 0.0045)
    import bmesh
    def rbox(name, dims, loc, m, corner=0.0085, edge=0.0016, seam=0):
        """Box with rounded plan corners and softened rims. seam = -1 / +1: that x side is the fold, and stays square and sharp
        (no corner, no rim bevel) so the two halves join seamlessly like the real phone; 0 = round everything (fleet phones)."""
        bpy.ops.mesh.primitive_cube_add(size=1, location=loc); o = bpy.context.active_object; o.name = name; o.scale = dims
        bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
        bm = bmesh.new(); bm.from_mesh(o.data); hx = dims[0] / 2
        on_seam = lambda v: seam != 0 and abs(v.co.x - seam * hx) < 1e-6
        vert_edges = [e for e in bm.edges if abs((e.verts[0].co - e.verts[1].co).normalized().z) > 0.99 and not on_seam(e.verts[0])]
        bmesh.ops.bevel(bm, geom=vert_edges, offset=corner, segments=8, affect="EDGES", profile=0.5)
        bw = bm.edges.layers.float.get("bevel_weight_edge") or bm.edges.layers.float.new("bevel_weight_edge")
        for e in bm.edges: e[bw] = 0.0 if (on_seam(e.verts[0]) and on_seam(e.verts[1])) or (on_seam(e.verts[0]) or on_seam(e.verts[1])) and abs((e.verts[0].co - e.verts[1].co).normalized().x) < 0.5 and abs(e.verts[0].co.x - e.verts[1].co.x) < 1e-6 else 1.0
        bm.to_mesh(o.data); bm.free()
        md = o.modifiers.new("bev", "BEVEL"); md.width = edge; md.segments = 4; md.limit_method = "WEIGHT" if seam else "ANGLE"
        o.data.materials.append(m); bpy.ops.object.shade_smooth(); return o
    duo_root = empty("duo_root", (0, 0, 0))
    titan = mat("titan", (0.70, 0.69, 0.67), 1.0, 0.22)                         # brushed-grade titanium frame
    duo_back = mat("nightsky", (0.035, 0.045, 0.085), 0.25, 0.18)               # Night Sky ceramic back
    glass_blk = mat("bezel", (0.004, 0.004, 0.006), 0.0, 0.05)                  # black front glass around the screens
    lhalf = rbox("duo_left", DH, (-DH[0] / 2, 0, DH[2] / 2), titan, seam=1); lhalf.parent = duo_root
    rpiv = empty("duo_rpivot", (0, 0, DH[2]), duo_root)
    rhalf = rbox("duo_right", DH, (DH[0] / 2, 0, -DH[2] / 2), titan, seam=-1); rhalf.parent = rpiv
    for hb, par, x_, z_ in ((("duo_back_l"), duo_root, -DH[0] / 2, -0.00005), (("duo_back_r"), rpiv, DH[0] / 2, -DH[2] - 0.00005)):     # coloured back plates
        sd = 1 if par is duo_root else -1                                  # back plates also run square into the fold
        bk = rbox(hb, (DH[0] - 0.0008, DH[1] - 0.0016, 0.0004), (x_ + sd * 0.0004, 0, z_ + 0.0002), duo_back, corner=0.0078, edge=0.0001, seam=sd); bk.parent = par
    # dual camera plateau, top corner of the left half's back (faces the desk when open; shows when it falls or is closed upside down)
    cam_pl = rbox("duo_campl", (0.026, 0.030, 0.0014), (-DH[0] + 0.017, DH[1] / 2 - 0.019, -0.0007), duo_back, corner=0.006, edge=0.0004); cam_pl.parent = duo_root
    lensm = mat("lens", (0.01, 0.01, 0.015), 0.6, 0.05); ringm = mat("lensring", (0.75, 0.74, 0.72), 1.0, 0.2)
    for ly in (0.0075, -0.0075):
        bpy.ops.mesh.primitive_cylinder_add(radius=0.0058, depth=0.0016, vertices=32, location=(-DH[0] + 0.017, DH[1] / 2 - 0.019 + ly, -0.0013)); r_ = bpy.context.active_object; r_.data.materials.append(ringm); r_.parent = duo_root
        bpy.ops.mesh.primitive_cylinder_add(radius=0.0043, depth=0.0018, vertices=32, location=(-DH[0] + 0.017, DH[1] / 2 - 0.019 + ly, -0.0014)); l_ = bpy.context.active_object; l_.data.materials.append(lensm); l_.parent = duo_root
    # titanium hinge cover: the rounded spine you see when the phone is closed (hidden when open)
    bpy.ops.mesh.primitive_cylinder_add(radius=DH[2] * 0.99, depth=DH[1] - 0.006, vertices=32, location=(0, 0, DH[2]), rotation=(math.pi / 2, 0, 0)); hcov = bpy.context.active_object
    hcov.name = "duo_hingecover"; hcov.data.materials.append(titan); hcov.parent = duo_root; bpy.ops.object.shade_smooth()
    # hinge spine + gears + the hook, sitting in a channel at the seam (hidden under the screen panels until the lid lifts)
    bpy.ops.mesh.primitive_cylinder_add(radius=0.0021, depth=0.112, location=(0, 0, DH[2] + 0.0004), rotation=(math.pi / 2, 0, 0)); spine = bpy.context.active_object
    spine.name = "duo_spine"; spine.data.materials.append(mat("spine", (0.35, 0.36, 0.40), 1.0, 0.25)); spine.parent = duo_root
    gearm = mat("gear", (0.75, 0.62, 0.3), 1.0, 0.3)
    for gy in (-0.045, -0.015, 0.015, 0.045):
        bpy.ops.mesh.primitive_cylinder_add(radius=0.0034, depth=0.004, vertices=12, location=(0, gy, DH[2] + 0.0004), rotation=(math.pi / 2, 0, 0)); g_ = bpy.context.active_object
        g_.data.materials.append(gearm); g_.parent = duo_root
    HINGE_PARTS = [spine] + [o for o in col.objects if o.name.startswith("Cylinder") and o.parent is duo_root and o.data.materials and o.data.materials[0].name == "gear"]
    hook_m = mat("hook", (0.9, 0.5, 0.1), 0.6, 0.3, emit=(1.0, 0.45, 0.05), strength=0.0)
    hook_piv = empty("duo_hookpiv", (0, 0.0, DH[2] + 0.0018), duo_root)
    hk = box("duo_hook", (0.0028, 0.006, 0.0012), (0, 0.0, 0.0012), hook_m, bevel=0.0004); hk.parent = hook_piv
    hk2 = box("duo_hook_tip", (0.0028, 0.0022, 0.0022), (0, 0.0026, 0.0024), hook_m); hk2.parent = hook_piv
    # inner screen: two thin panels (one per half), each showing its half of the inner image; outer screen on the back of the right half
    def screen_panel(name, loc, parent, w=0.0795, l=0.1205):
        bpy.ops.mesh.primitive_plane_add(size=1, location=loc); o = bpy.context.active_object; o.name = name; o.scale = (w, l, 1); bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
        o.parent = parent; m = bpy.data.materials.new(name); m.use_nodes = True; nt = m.node_tree
        for nd in list(nt.nodes): nt.nodes.remove(nd)
        tx = nt.nodes.new("ShaderNodeTexImage"); em = nt.nodes.new("ShaderNodeEmission"); em.inputs["Strength"].default_value = 1.5
        gl = nt.nodes.new("ShaderNodeBsdfGlossy"); gl.inputs["Roughness"].default_value = 0.12; mx = nt.nodes.new("ShaderNodeMixShader"); mx.inputs[0].default_value = 0.015   # less glare: angled UI stays readable
        ou = nt.nodes.new("ShaderNodeOutputMaterial"); nt.links.new(tx.outputs[0], em.inputs[0]); nt.links.new(em.outputs[0], mx.inputs[1]); nt.links.new(gl.outputs[0], mx.inputs[2]); nt.links.new(mx.outputs[0], ou.inputs[0])
        o.data.materials.append(m); return o, tx
    lpan_piv = empty("duo_lpanpiv", (0.0, 0, DH[2] + 0.0013), duo_root); rpan_piv = empty("duo_rpanpiv", (0.0, 0, 0.0013), rpiv)
    lpan, ltx = screen_panel("duo_inner_l", (-0.081 / 2, 0, 0), lpan_piv, 0.081, 0.1205); rpan, rtx = screen_panel("duo_inner_r", (0.081 / 2, 0, 0), rpan_piv, 0.081, 0.1205)
    for pp, sx in ((lpan_piv, -1), (rpan_piv, 1)):
        bk = box("duo_panel_back", (0.081, 0.1205, 0.0012), (sx * 0.081 / 2, 0, -0.0007), glass_blk); bk.parent = pp
    opan, otx = screen_panel("duo_outer", (DH[0] / 2, 0, -DH[2] - 0.0005), rpiv, 0.0785, 0.119); opan.rotation_euler.y = math.pi   # faces down when open, up when closed
    flash_l = bpy.data.objects.new("flash", bpy.data.lights.new("flash", "POINT")); col.objects.link(flash_l); flash_l.location = (0.0, -0.12, 0.16); flash_l.data.energy = 0; flash_l.data.color = (1, 1, 1)
    DUO_ANCH = {"screen": (lpan_piv, (-0.02, 0.025, 0.0005)), "seam": (duo_root, (0, 0.025, DH[2] + 0.002)), "hinge": (duo_root, (0, -0.04, DH[2] + 0.0004)),
                "hook": (hook_piv, (0, 0.0026, 0.0035)), "phone": (duo_root, (-0.03, -0.05, DH[2]))}
    # fleet: closed Duos in a 4 x 2 grid at the back of the desk ("a small number of phones"); one has a red, faulty outer screen
    FLEET = Vector((0.0, 0.62, 0.0)); fleet_objs = []; fleet_red = None
    for i in range(4):
        for j in range(2):
            c = FLEET + Vector((-0.165 + i * 0.11, -0.08 + j * 0.16, 0.0))
            fb = rbox(f"fleet_{i}{j}", (0.081, 0.122, 0.009), c + Vector((0, 0, 0.0045)), titan); fleet_objs.append(fb)
            red = (i, j) == (2, 0); fm = mat(f"fleetscr{i}{j}", (0.02, 0.02, 0.03), emit=(1.0, 0.02, 0.01) if red else (0.10, 0.18, 0.75), strength=0.9 if red else 0.7)
            fs = rbox(f"fleet_scr_{i}{j}", (0.0765, 0.117, 0.0004), c + Vector((0, 0, 0.0091)), fm, corner=0.0075, edge=0.0001); fleet_objs.append(fs)
            if red: fleet_red = fm
    hide_all(fleet_objs, "fleet" not in PROPS)
    # pound coins (visual joke on "two thousand solid British pounds"): event "coins" 0..1 rains them onto the desk
    import random as _rc; _rc.seed(11); coin_m = mat("coin", (0.95, 0.72, 0.25), 1.0, 0.22); COINS = []
    for i in range(16):
        bpy.ops.mesh.primitive_cylinder_add(radius=0.0115, depth=0.0028, vertices=24); co = bpy.context.active_object; co.name = f"coin{i}"; co.data.materials.append(coin_m)
        x_ = _rc.uniform(-0.13, 0.13); y_ = _rc.uniform(-0.12, 0.13)
        if abs(x_) < 0.095 and abs(y_) < 0.07: x_ = math.copysign(0.10 + abs(x_) * 0.3, x_)       # land around the phone, not on it
        COINS.append((co, x_, y_, i * 0.045, _rc.uniform(0, 6.28), _rc.uniform(-0.25, 0.25))); co.hide_render = True
    DUO_ANCH["fleetred"] = (None, tuple(FLEET + Vector((0.055, -0.08, 0.0095))))

# ---- wallet hijack (FIX #15): your real bank card on the desk, a glowing copy of it ("ghost") that flies onto the scammer's phone,
# and the scammer's phone itself (lying by their laptop, its screen driven by the beat's "scam" pvui expression).
# Events: "ghost" 0 = copy sits on your card (hidden), 1 = landed on their phone; "freeze" 0..1 = the bank switches the copy off
# (it greys out and sinks away); "cardflip" 0..1 = your card turns over to show the number on the back.
WALLET = "wallet" in PROPS
WAL_ANCH = {}
if WALLET:
    hide_all([o for o in col.objects if o.name.startswith("tray_")], True)
    CARD0 = Vector((-0.112, -0.015, 0.0)); SCAM0 = Vector((0.035, 0.27, 0.0)); CD = (0.0856, 0.054, 0.0008)
    def plane_img(name, w, l, img_path, parent, z, flip=False, emit=0.0, alpha=None):
        bpy.ops.mesh.primitive_plane_add(size=1, location=(0, 0, z)); o = bpy.context.active_object; o.name = name; o.scale = (w, l, 1)
        if flip: o.rotation_euler.x = math.pi
        bpy.ops.object.transform_apply(scale=True, rotation=True); o.parent = parent
        m = bpy.data.materials.new(name); m.use_nodes = True; nt = m.node_tree; bs = nt.nodes["Principled BSDF"]
        tx = nt.nodes.new("ShaderNodeTexImage"); tx.image = bpy.data.images.load(os.path.abspath(img_path)); nt.links.new(tx.outputs[0], bs.inputs["Base Color"])
        bs.inputs["Roughness"].default_value = 0.35; bs.inputs["Specular IOR Level"].default_value = 0.6
        if emit: nt.links.new(tx.outputs[0], bs.inputs["Emission Color"]); bs.inputs["Emission Strength"].default_value = emit
        o.data.materials.append(m); return o, m
    cimg = os.path.join(a.out, "card_front.png"); bimg = os.path.join(a.out, "card_back.png")
    U.card_face().save(cimg); U.card_reverse().rotate(180).save(bimg)      # the flip turns the back plane by 180 deg
    card_root = empty("card_root", CARD0 + Vector((0, 0, CD[2] / 2))); card_root.rotation_euler.z = math.radians(9)
    cbody = box("card_body", CD, (0, 0, 0), mat("cardedge", (0.06, 0.08, 0.2), 0.2, 0.4), bevel=0.0003); cbody.parent = card_root
    plane_img("card_front", CD[0], CD[1], cimg, card_root, CD[2] / 2 + 0.00005, emit=0.15)
    plane_img("card_back", CD[0], CD[1], bimg, card_root, -CD[2] / 2 - 0.00005, flip=True, emit=0.15)
    # the copy: same card, glowing cyan, semi-transparent
    ghost_root = empty("ghost_root", CARD0)
    gm = bpy.data.materials.new("ghost"); gm.use_nodes = True; nt = gm.node_tree
    for nd in list(nt.nodes): nt.nodes.remove(nd)
    gtx = nt.nodes.new("ShaderNodeTexImage"); gtx.image = bpy.data.images.load(os.path.abspath(cimg))
    gmixc = nt.nodes.new("ShaderNodeMix"); gmixc.data_type = "RGBA"; gmixc.inputs[0].default_value = 0.35; gmixc.inputs[7].default_value = (0.3, 0.85, 1.0, 1)
    nt.links.new(gtx.outputs[0], gmixc.inputs[6])
    gem = nt.nodes.new("ShaderNodeEmission"); gem.inputs["Strength"].default_value = 3.0; nt.links.new(gmixc.outputs[2], gem.inputs[0])
    gtr = nt.nodes.new("ShaderNodeBsdfTransparent"); gmx = nt.nodes.new("ShaderNodeMixShader"); gmx.inputs[0].default_value = 0.8
    gout = nt.nodes.new("ShaderNodeOutputMaterial"); nt.links.new(gtr.outputs[0], gmx.inputs[1]); nt.links.new(gem.outputs[0], gmx.inputs[2]); nt.links.new(gmx.outputs[0], gout.inputs[0])
    bpy.ops.mesh.primitive_plane_add(size=1); ghost = bpy.context.active_object; ghost.name = "ghost"; ghost.scale = (CD[0], CD[1], 1)
    bpy.ops.object.transform_apply(scale=True); ghost.data.materials.append(gm); ghost.parent = ghost_root; ghost.visible_shadow = False
    md = ghost.modifiers.new("solid", "SOLIDIFY"); md.thickness = 0.001
    # the scammer's phone: graphite slab + emissive screen (image set per frame)
    scam_root = empty("scam_root", SCAM0); scam_root.rotation_euler.z = math.radians(-16)
    sb = box("scam_body", PH, (0, 0, PH[2] / 2), mat("graphite2", (0.05, 0.055, 0.065), 0.85, 0.28), bevel=0.006); sb.parent = scam_root
    bpy.ops.mesh.primitive_plane_add(size=1, location=(0, 0, PH[2] + 0.0002)); sscr = bpy.context.active_object; sscr.name = "scam_screen"
    sscr.scale = (0.069, 0.149, 1); bpy.ops.object.transform_apply(scale=True); sscr.parent = scam_root
    ssm = bpy.data.materials.new("scam_screen"); ssm.use_nodes = True; nt = ssm.node_tree
    for nd in list(nt.nodes): nt.nodes.remove(nd)
    scam_tx = nt.nodes.new("ShaderNodeTexImage"); sem = nt.nodes.new("ShaderNodeEmission"); sem.inputs["Strength"].default_value = 1.6
    sout = nt.nodes.new("ShaderNodeOutputMaterial"); nt.links.new(scam_tx.outputs[0], sem.inputs[0]); nt.links.new(sem.outputs[0], sout.inputs[0]); sscr.data.materials.append(ssm)
    scam_light = bpy.data.objects.new("scam_light", bpy.data.lights.new("scam_light", "POINT")); col.objects.link(scam_light); scam_light.location = SCAM0 + Vector((0, 0, 0.05))
    scam_light.data.color = (1.0, 0.3, 0.25); scam_light.data.energy = 0.6
    GHOST_A = CARD0 + Vector((0, 0, 0.004)); GHOST_B = SCAM0 + Vector((0, 0, PH[2] + 0.006))
    WAL_ANCH = {"card": tuple(CARD0 + Vector((0.0, 0.0, 0.002))), "scamphone": tuple(SCAM0 + Vector((0, -0.03, PH[2]))), "ghost": None}

# anchors for 2D labels (compose3d.py pins tags to these)
ANCH = {"screen": (0, 0, PH[2] + 0.004), "modem": (0.02, 0.052, z0), "sim": (-0.019, 0.05, z0), "filter": (-0.016, 0.004, z0 + 0.002), "cpu": (0.004, 0.025, z0),
        "battery": (0, -0.038, z0 + 0.001), "mast": (-0.15, 0.33, 0.33), "laptop": (0.16, 0.407, 0.09), "tray": tuple(TR + Vector((0, 0, 0.02))), "phone": (0, -0.06, PH[2]),
        "van": tuple(VAN + Vector((0.0, -0.025, 0.04))), "fakemast": tuple(VAN + Vector((0.02, 0, 0.055 + 0.125))), "netfilter": (-0.15, 0.33 - 0.026, 0.19)}
for k, v in ANCH.items(): empty("anchor_" + k, v)
if DUO:
    for k in ("screen", "phone"): ANCH.pop(k); bpy.data.objects.remove(bpy.data.objects["anchor_" + k])
    for k, (par, v) in DUO_ANCH.items(): empty("anchor_" + k, v, par); ANCH[k] = v
if WALLET:
    for k, v in WAL_ANCH.items():
        if v is not None: empty("anchor_" + k, v); ANCH[k] = v
    empty("anchor_ghost", (0, 0, 0), ghost_root); ANCH["ghost"] = (0, 0, 0)
NODES = {"mast": Vector((-0.15, 0.33, 0.335)), "phone": Vector((0.02, 0.052, z0 + 0.006)), "laptop": Vector((0.16, 0.38, 0.06)), "tray": TR + Vector((0, 0, 0.012)),
         "van": VAN + Vector((0.02, 0, 0.055 + 0.125)), "netfilter": Vector((-0.15, 0.33, 0.19))}
if WALLET: NODES["scamphone"] = SCAM0 + Vector((0, 0, PH[2] + 0.006)); NODES["card"] = CARD0 + Vector((0, 0, 0.004))

# packets: a glowing head + 5 trail beads per slot, 4 slots
PCOL = {"text": (1.0, 0.75, 0.1), "card": (1.0, 0.1, 0.15), "call": (0.25, 0.55, 1.0)}
# v2 (FIX #13): the old trail (6 beads, 3% apart, strength 12) bloomed into one white blob. Now 5 beads spaced 7% of the path apart,
# shrinking, with emission falling off bead by bead (head 5, tail 1.2) so AgX keeps the colour and each bead reads on its own.
NBEAD, BEAD_GAP = 5, 0.07
PM = {(k, j): mat(f"pk_{k}_{j}", tuple(0.25 * x for x in c), emit=c, strength=5.0 * (0.7 ** j)) for k, c in PCOL.items() for j in range(NBEAD)}
SLOTS = []
for s_ in range(4):
    beads = []
    for j in range(NBEAD):
        bpy.ops.mesh.primitive_uv_sphere_add(radius=0.0068 * (1 - j * 0.15), segments=16, ring_count=8); o = bpy.context.active_object; o.name = f"pk{s_}_{j}"; beads.append(o)
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
       "laptop": ((0.08, 0.14, 0.12), (0.16, 0.39, 0.06), 35), "laptop_close": ((0.11, 0.19, 0.105), (0.16, 0.395, 0.058), 36), "wide": ((0.0, -0.52, 0.40), (0.0, 0.14, 0.08), 28), "tray": ((0.08, -0.34, 0.15), (0.12, -0.13, 0.01), 40),
       "top": ((0.0, 0.06, 0.82), (0.0, 0.10, 0), 28),
       # FIX #13 additions: the van, the network filter ring, and a street-wide view that holds phone, real mast and van in one frame
       "street": ((0.03, -0.56, 0.42), (0.03, 0.15, 0.06), 22), "van": ((0.09, -0.07, 0.11), (0.205, 0.10, 0.06), 35),
       "van_close": ((0.12, -0.05, 0.10), (0.21, 0.10, 0.075), 35), "van_top": ((0.16, 0.0, 0.30), (0.215, 0.10, 0.10), 30),
       "netfilter": ((-0.07, 0.16, 0.25), (-0.15, 0.33, 0.20), 35), "masts": ((0.0, -0.28, 0.14), (0.02, 0.26, 0.13), 24),
       "macro_top": ((0.0, -0.01, 0.13), (0.0, 0.012, 0.0), 40),
       # FIX #14 (Duo, open width 0.146 m)
       "drop": ((0.0, -0.23, 0.07), (-0.04, 0.0, 0.08), 28), "drop_low": ((-0.09, -0.21, 0.035), (0.0, 0.0, 0.02), 28),
       "duo_hero": ((0.13, -0.24, 0.17), (0.0, 0.0, 0.0), 42), "duo_top": ((0.0, -0.04, 0.40), (0.0, 0.0, 0.0), 45),
       "duo_tilt": ((-0.09, -0.20, 0.19), (0.0, 0.005, 0.0), 45), "duo_seam": ((0.0, -0.055, 0.10), (0.0, 0.015, 0.006), 40),
       "duo_crack": ((0.03, -0.03, 0.07), (0.0, 0.02, 0.006), 35), "hinge": ((0.0, -0.11, 0.10), (0.0, -0.005, 0.006), 35),
       "hinge_low": ((-0.05, -0.10, 0.05), (0.0, -0.01, 0.006), 32), "hook_macro": ((0.012, -0.03, 0.034), (0.0, 0.002, 0.007), 35),
       "fleet": ((0.0, 0.30, 0.40), (0.0, 0.62, 0.0), 35), "fleet_red": ((0.10, 0.44, 0.17), (0.055, 0.54, 0.0), 40),
       "duo_side": ((0.30, -0.14, 0.11), (0.0, 0.0, 0.01), 38), "duo_wide": ((0.0, -0.42, 0.30), (0.0, 0.03, 0.0), 32),
       # FIX #15 (wallet hijack): your card, the path the copy flies, the scammer's phone
       "card_macro": ((-0.10, -0.13, 0.075), (-0.105, -0.01, 0.0), 40), "card_top": ((-0.112, -0.03, 0.17), (-0.112, -0.012, 0.0), 45),
       "path_wide": ((-0.05, -0.40, 0.30), (-0.02, 0.13, 0.03), 30), "path_side": ((-0.30, -0.10, 0.22), (-0.03, 0.14, 0.03), 30),
       "scam": ((0.02, 0.08, 0.17), (0.035, 0.27, 0.0), 40), "scam_close": ((0.035, 0.205, 0.12), (0.035, 0.27, 0.0), 42),
       "scam_tilt": ((0.12, 0.15, 0.12), (0.035, 0.27, 0.0), 40)}
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

DUO_LAST = {}
def duo_screen(spec, p, which, tx, size, crop=None, mirror=False):
    import re
    key = f"{which}|{spec}" + (f"@{round(p * 48) / 48:.4f}" if re.search(r"\bp\b", spec) else "")
    if DUO_LAST.get(which) == key: return
    f = os.path.join(SCREEN_DIR, which + "_" + hashlib.md5(key.encode()).hexdigest()[:12] + ".png")
    if not os.path.exists(f):
        im = U.bezel(eval(spec, {"U": U, "p": round(p * 48) / 48, "ease": ease, "clamp": clamp}).convert("RGB"))
        if crop == "L": im = im.crop((0, 0, im.width // 2, im.height))
        if crop == "R": im = im.crop((im.width // 2, 0, im.width, im.height))
        if mirror: im = im.transpose(0)
        im.resize(size).save(f)
    tx.image = bpy.data.images.load(f, check_existing=True); DUO_LAST[which] = key
def drop_pose(u):
    """Fall + two bounces, u 0..1 -> (height, tilt x, tilt y). Stylised slow motion; lands flat and still."""
    if u < 0.38: k = u / 0.38; return 0.17 * (1 - k * k), math.radians(55) * (1 - k), math.radians(-25) * (1 - k)
    if u < 0.68: k = (u - 0.38) / 0.30; return 0.045 * 4 * k * (1 - k), math.radians(14) * math.sin(math.pi * k), 0.0
    if u < 0.86: k = (u - 0.68) / 0.18; return 0.012 * 4 * k * (1 - k), math.radians(-5) * math.sin(math.pi * k), 0.0
    return 0.0, 0.0, 0.0
def apply_duo(t, b, p):
    ov = track("open", t); rpiv.rotation_euler.y = -math.pi * (1 - ov); hcov.hide_render = ov > 0.5
    dv = track("drop", t, 1.0); hz, rx, ry = drop_pose(dv); duo_root.location = (0, 0, hz + 0.0001); duo_root.rotation_euler = (rx, ry, 0)
    lv = track("lid", t)                          # cutaway: the two screen panels slide apart and up, the seam (hinge + hook) shows between them
    lpan_piv.location = (-0.036 * lv, 0, DH[2] + 0.0013 + 0.03 * lv); lpan_piv.rotation_euler.y = math.radians(-18) * lv
    rpan_piv.location = (0.036 * lv, 0, 0.0013 + 0.03 * lv); rpan_piv.rotation_euler.y = math.radians(18) * lv
    for o in HINGE_PARTS + [hk, hk2]: o.hide_render = lv < 0.05            # hinge internals only in the cutaway (they poked through the screen)
    hv = track("hook", t); hook_piv.rotation_euler.x = math.radians(35) * hv * math.sin(t * 9); hook_m.node_tree.nodes["Principled BSDF"].inputs["Emission Strength"].default_value = 8 * hv
    flash_l.data.energy = 20 * track("flash", t)
    if fleet_red: fleet_red.node_tree.nodes["Principled BSDF"].inputs["Emission Strength"].default_value = 0.6 + 0.8 * (int(t * 4) % 2)
    cv = track("coins", t)
    for co, x_, y_, d_, rz, tilt in COINS:
        u = clamp((cv - d_) / 0.4); co.hide_render = cv <= d_
        if u < 0.55: k = u / 0.55; z = 0.26 * (1 - k * k); spin = (1 - k) * 7
        elif u < 0.8: k = (u - 0.55) / 0.25; z = 0.02 * 4 * k * (1 - k); spin = 0.0
        else: z = 0.0; spin = 0.0
        co.location = (x_, y_, z + 0.0014); co.rotation_euler = (spin + tilt * (1 - u), tilt * (1 - u), rz)
    inner = b.get("inner") or "U.duo_home()"; outer = b.get("outer") or "U.duo_outer()"
    duo_screen(inner, p, "innerL", ltx, (720, 1080), "L"); duo_screen(inner, p, "innerR", rtx, (720, 1080), "R"); duo_screen(outer, p, "outer", otx, (713, 1080), None, False)

SCAM_LAST = [None]
def apply_wallet(t, b, p):
    gv = track("ghost", t); fz = track("freeze", t)
    pos = bez(GHOST_A, GHOST_B, 0.16, gv); ghost_root.location = pos + Vector((0, 0, -0.03 * fz))
    ghost_root.rotation_euler = (math.radians(25) * math.sin(math.pi * gv), 0, math.radians(9) + (math.radians(-25) - math.radians(9)) * gv + 2 * math.pi * ease(gv) * (1 if 0 < gv < 1 else 0))
    ghost.hide_render = gv < 0.02 or gv > 0.985 or fz > 0.98          # only in flight: once landed it IS the card on their screen
    gmixc.inputs[0].default_value = 0.35 + 0.65 * fz; gmixc.inputs[7].default_value = (0.3 + 0.2 * fz, 0.85 - 0.45 * fz, 1.0 - 0.6 * fz, 1)
    gem.inputs["Strength"].default_value = 1.7 * (1 - 0.8 * fz) * (1 + 0.6 * math.sin(math.pi * gv)); gmx.inputs[0].default_value = 0.8 * (1 - fz)
    cf = track("cardflip", t); card_root.rotation_euler = (0, math.pi * ease(cf), math.radians(9)); card_root.location.z = CD[2] / 2 + 0.035 * math.sin(math.pi * cf)
    spec = b.get("scam") or "U.scam_wallet('home')"; import re
    key = spec + (f"@{round(p * 48) / 48:.4f}" if re.search(r"\bp\b", spec) else "")
    if key != SCAM_LAST[0]:
        f = os.path.join(SCREEN_DIR, "scam_" + hashlib.md5(key.encode()).hexdigest()[:12] + ".png")
        if not os.path.exists(f): eval(spec, {"U": U, "p": round(p * 48) / 48, "ease": ease, "clamp": clamp}).convert("RGB").resize((540, 960)).save(f)
        scam_tx.image = bpy.data.images.load(f, check_existing=True); SCAM_LAST[0] = key

def apply(t):
    b = beat_at(t); p = clamp((t - b["t0"]) / max(1e-3, b["t1"] - b["t0"]))
    ca, cb = b["cam"] if isinstance(b["cam"], list) else (b["cam"], b["cam"]); A, Bc = CAM[ca], CAM[cb]; k = ease(p)
    loc = Vector(A[0]).lerp(Vector(Bc[0]), k); tgt = Vector(A[1]).lerp(Vector(Bc[1]), k); cam.data.lens = A[2] + (Bc[2] - A[2]) * k
    cam.location = loc; cam.rotation_euler = (tgt - loc).to_track_quat("-Z", "Y").to_euler(); cam.data.dof.focus_distance = (tgt - loc).length; cam.data.dof.use_dof = bool(b.get("dof", False))
    set_screen(b.get("screen"), p)
    if DUO: apply_duo(t, b, p)
    if WALLET: apply_wallet(t, b, p)
    lidv = track("lid", t); hinge.rotation_euler.x = math.radians(-75) * lidv; hinge.location.z = SZ + 0.012 * lidv
    fv = track("filter", t); knob.location.x = -0.022 + 0.012 * fv; knob.active_material.node_tree.nodes["Principled BSDF"].inputs["Emission Strength"].default_value = 6 * fv
    lv = track("laptop", t, 0.4); lapscr.active_material.node_tree.nodes["Principled BSDF"].inputs["Emission Strength"].default_value = 1.0 + 2.0 * lv; lap_light.data.energy = 0.08 + 0.4 * lv
    blink.hide_render = DUO or int(t * 2) % 2 == 1          # the mast is hidden in Duo episodes
    if "van" in PROPS:
        vv = track("van", t); fake_root.location.z = 0.055 - 0.12 * (1 - vv); hide_all(fake_objs, vv < 0.02)
        fblink.hide_render = vv < 0.02 or int(t * 3) % 2 == 1
    if "netfilter" in PROPS: nringm.node_tree.nodes["Principled BSDF"].inputs["Emission Strength"].default_value = 0.4 + 7 * track("netfilter", t)
    if "links" in PROPS:
        lk = track("link", t); on = track("linkon", t)
        link_real_m.node_tree.nodes["Principled BSDF"].inputs["Emission Strength"].default_value = 3 * (1 - lk) * on; link_real.hide_render = (1 - lk) * on < 0.03
        link_fake_m.node_tree.nodes["Principled BSDF"].inputs["Emission Strength"].default_value = 4 * lk * on; link_fake.hide_render = lk * on < 0.03
    active = [e for bb in BEATS for e in bb.get("events", []) if e["type"] == "packet" and e["t0"] <= t < e["t1"]]
    pk_pos = None
    for s_, beads in enumerate(SLOTS):
        e = active[s_] if s_ < len(active) else None
        for j, o in enumerate(beads):
            o.hide_render = e is None
            if e is None: continue
            frm, to = e["path"].split(">"); raw = (t - e["t0"]) / (e["t1"] - e["t0"]) * (1 + (NBEAD - 1) * BEAD_GAP) - j * BEAD_GAP
            if raw < 0 or raw > 1: o.hide_render = True; continue        # not launched yet / already arrived: no pile-up at either end
            uu = e["bounce"] * (1 - abs(1 - 2 * raw)) if e.get("bounce") else ease(raw)    # bounce: goes part-way, then back (blocked)
            pos = bez(NODES[frm], NODES[to], e.get("arc", 0.18), uu); o.location = pos; o.data.materials.clear(); o.data.materials.append(PM[(e["kind"], j)])
            if j == 0 and s_ == 0: pk_pos = pos
    return b, pk_pos

def anchors(pk_pos):
    out = {}
    for k in ANCH:
        v = world_to_camera_view(sc, cam, bpy.data.objects["anchor_" + k].matrix_world.translation)
        out[k] = [round(v.x, 4), round(1 - v.y, 4), round(v.z, 4)]
    if pk_pos is not None: v = world_to_camera_view(sc, cam, pk_pos); out["packet"] = [round(v.x, 4), round(1 - v.y, 4), round(v.z, 4)]
    out["_lid"] = round(track("lid", CUR_T[0]), 3)                       # compose3d.py adds part labels while the lid is open
    if DUO:
        sv = world_to_camera_view(sc, cam, lpan.matrix_world @ Vector((0, 0.076, 0))); sv0 = world_to_camera_view(sc, cam, lpan.matrix_world @ Vector((0, -0.076, 0)))
        out["_screen_px"] = round(abs(sv.y - sv0.y), 4); return out
    sv = world_to_camera_view(sc, cam, scr.matrix_world @ Vector((0.0345, 0.0745, 0))); sv0 = world_to_camera_view(sc, cam, scr.matrix_world @ Vector((-0.0345, -0.0745, 0)))
    out["_screen_px"] = round(abs(sv.y - sv0.y), 4)                        # screen height as a fraction of the frame: compose adds an inset when it is small
    return out
CUR_T = [0.0]

# ------------------------------------------------------------------------------------------------ render
sc.render.engine = "CYCLES"; sc.cycles.device = "CPU"; sc.cycles.samples = a.samples; sc.cycles.use_denoising = True; sc.render.use_persistent_data = True
sc.render.resolution_x, sc.render.resolution_y = a.res; sc.view_settings.view_transform = "AgX"; sc.view_settings.look = "AgX - Medium High Contrast"
total = int(round(B["length_s"] * FPS))
if a.one is not None: frames = [a.one]; sub = "one"
elif a.test: frames = [int(((b["t0"] + b["t1"]) / 2) * FPS) for b in BEATS if not (b.get("face") or b.get("char"))]; sub = "test"
else: frames = [f for f in range(a.frames[0], min(a.frames[1] + 1, total)) if not (beat_at(f / FPS).get("face") or beat_at(f / FPS).get("char"))]; sub = "frames"
os.makedirs(os.path.join(a.out, sub), exist_ok=True); os.makedirs(os.path.join(a.out, "anchors"), exist_ok=True)
for f in frames:
    pth = os.path.join(a.out, sub, f"{f:05d}.png")
    if os.path.exists(pth): continue
    CUR_T[0] = f / FPS; b, pk = apply(f / FPS); bpy.context.view_layer.update()
    json.dump(anchors(pk), open(os.path.join(a.out, "anchors", f"{f:05d}.json"), "w"))
    sc.render.filepath = os.path.abspath(pth); bpy.ops.render.render(write_still=True); print("rendered", pth, flush=True)
