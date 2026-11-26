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

# ---- gold (FIX #16, "Gold in your iPhone"): the desk becomes a workbench in a sunny recycling yard, with a mountain of old phones behind it.
# The hero phone is the OLD generic phone (tossed in on frame 1). Events (all 0..1 unless noted):
#  "toss"  the phone flies in from the left and bounces flat     "goldglow" pins + chip bond wires glow     "hair" a hair lies across the chip
#  "battout" battery lifts out of the phone onto the bench        "battfire" the loose battery puffs up and flames (cutaway)
#  "dunk"  a board drops into the tub     "dissolve" it crumbles away     "liq" liquid colour 0 clear, 1 blue, 2 murky, 3 yellow (0..3)
#  "mud"   black mud layer     "sparkle" gold flecks glow in the mud     "bubble" bubbles rise     "rinse" 3 water pulses     "powder" white grains
#  "dust"  brown dust snows to the bottom     "torch" flame on     "heat" crucible contents glow     "pour" crucible tilts, molten stream
#  "fill"  molten gold fills the mould      "cool" it cools to polished gold      "lift" the bar rises out of the mould
#  "piles" phone pile vs rock pile appear    "drawer" a drawer of old phones slides in (its lit phone's screen = beat key "dscreen")
#  "gone"  the hero phone is cleared away (after the board went into the tub)
GOLD = "gold" in PROPS or "silicon" in PROPS          # FIX #17 "silicon" builds on the gold workbench
SIL = "silicon" in PROPS
MOLT = [float(v) for v in os.environ.get("PV_MOLT", "1.0,0.25,0.0").split(",")]   # molten gold: emission strength, green, blue (red = 1)
GOLD_ANCH = {}
if GOLD:
    import random as _rg; _rg.seed(16)
    hide_all([o for o in col.objects if o.name.startswith(("Cylinder", "panel", "Sphere", "laptop", "keyboard", "tray_"))] + [blink, lap_base, lid, lapscr], True)
    def cyl(name, r, depth, loc, m, fill="NGON", verts=48, rot=(0, 0, 0)):
        bpy.ops.mesh.primitive_cylinder_add(radius=r, depth=depth, location=loc, vertices=verts, end_fill_type=fill, rotation=rot); o = bpy.context.active_object; o.name = name
        if m: o.data.materials.append(m)
        bpy.ops.object.shade_smooth(); return o
    def glassm(name, color=(0.92, 0.96, 1.0), rough=0.02, ior=1.45, tw=1.0):
        m = mat(name, color, 0.0, rough); bs = m.node_tree.nodes["Principled BSDF"]; bs.inputs["Transmission Weight"].default_value = tw; bs.inputs["IOR"].default_value = ior; return m
    def emat(name, color, emit, strength=0.0, metal=0.0, rough=0.4): return mat(name, color, metal, rough, emit=emit, strength=strength)
    def bsdf(m): return m.node_tree.nodes["Principled BSDF"]
    # the hero phone becomes one tossable object: parent every part to phone_root (at the origin, so nothing moves on parenting)
    phone_root = empty("phone_root", (0, 0, 0))
    PHONE_PARTS = [o for o in col.objects if o.name.startswith(("phone_body", "wall", "pcb", "cpu", "modem", "sim", "battery", "filter_"))] + [hinge]
    for o in PHONE_PARTS: o.parent = phone_root
    batt = bpy.data.objects["battery"]; batt_m = batt.active_material; BATT0 = Vector(batt.location)
    # charging port + its gold pins on the bottom edge of the board; gold bond wires looping off the CPU's edges; one hair for scale
    gold_glow = emat("goldglow", (0.95, 0.68, 0.22), (1.0, 0.72, 0.2), 0.0, metal=1.0, rough=0.2)
    port = box("port", (0.013, 0.005, 0.0026), (0, -PH[1] / 2 + 0.0035, z0 + 0.0004), mat("porthouse", (0.55, 0.56, 0.6), 0.9, 0.3)); port.parent = phone_root
    PINS = []
    for k in range(8):
        pn = box(f"pin{k}", (0.0007, 0.0042, 0.0005), (-0.0045 + k * 0.0013, -PH[1] / 2 + 0.0072, z0 + 0.0006), gold_glow); pn.parent = phone_root; PINS.append(pn)
    WIRES = []
    for side in range(4):
        for k in range(5):
            u = -0.0076 + k * 0.0038; cx, cy = 0.004, 0.025
            loc = (cx + u, cy + 0.0108, z0 + 0.0006) if side == 0 else (cx + u, cy - 0.0108, z0 + 0.0006) if side == 1 else (cx + 0.0108, cy + u, z0 + 0.0006) if side == 2 else (cx - 0.0108, cy + u, z0 + 0.0006)
            bpy.ops.mesh.primitive_torus_add(major_radius=0.0014, minor_radius=0.00011, major_segments=14, minor_segments=4, location=loc,
                                             rotation=(math.pi / 2, 0, 0 if side < 2 else math.pi / 2))
            wv = bpy.context.active_object; wv.name = f"bondwire{side}{k}"; wv.data.materials.append(gold_glow); wv.parent = phone_root; WIRES.append(wv)
    hair = cyl("hair", 0.00028, 0.034, (0.002, 0.024, z0 + 0.0016), mat("hairm", (0.09, 0.05, 0.03), 0.0, 0.5), verts=8, rot=(0, math.pi / 2, math.radians(24))); hair.parent = phone_root
    # battery fire (cutaway): the loose battery swells and a flame licks up from it
    flame_m = emat("flame", (1.0, 0.25, 0.03), (1.0, 0.28, 0.02), 0.0)
    bpy.ops.mesh.primitive_cone_add(radius1=0.014, radius2=0.0, depth=0.05, vertices=24); flame = bpy.context.active_object; flame.name = "flame"; flame.data.materials.append(flame_m); flame.visible_shadow = False
    # AgX washes bright emission to white, so the flame is a dim, deep red-orange outer cone with a yellow-orange core in front
    fcore_m = emat("flamecore", (1.0, 0.5, 0.05), (1.0, 0.45, 0.02), 0.0)
    for _m in (flame_m, fcore_m):   # emission only: a lit base colour or a specular sheen next to the fire light blows out to white
        bsdf(_m).inputs["Base Color"].default_value = (0, 0, 0, 1); bsdf(_m).inputs["Specular IOR Level"].default_value = 0.0
    bpy.ops.mesh.primitive_cone_add(radius1=0.009, radius2=0.0, depth=0.034, vertices=24); fcore = bpy.context.active_object; fcore.name = "flamecore"; fcore.data.materials.append(fcore_m); fcore.visible_shadow = False
    fire_l = bpy.data.objects.new("fire_light", bpy.data.lights.new("fire_light", "POINT")); col.objects.link(fire_l); fire_l.data.color = (1.0, 0.3, 0.05); fire_l.data.energy = 0
    BATT_OUT = Vector((0.105, -0.115, 0.0011))
    # the tub (open glass), its liquid, mud, sparkle flecks, bubbles, rinse stream, powder and dust
    TUB = Vector((-0.17, 0.12, 0.0)); TR_, TH_ = 0.065, 0.11
    tub = cyl("tub", TR_, TH_, TUB + Vector((0, 0, TH_ / 2)), glassm("tubglass", ior=1.12), fill="NOTHING", verts=64)
    sd = tub.modifiers.new("solid", "SOLIDIFY"); sd.thickness = 0.0025
    cyl("tub_floor", TR_, 0.003, TUB + Vector((0, 0, 0.0015)), glassm("tubfloor"), verts=64)
    liq_m = glassm("liquid", (0.9, 0.95, 1.0), 0.04, 1.08); liq = cyl("liquid", TR_ - 0.003, 0.08, TUB + Vector((0, 0, 0.0035 + 0.04)), liq_m, verts=64)
    liq_glow = bsdf(liq_m)
    mud = cyl("mud", TR_ - 0.004, 0.02, TUB + Vector((0, 0, 0.004 + 0.01)), mat("mud", (0.03, 0.025, 0.02), 0.0, 0.85), verts=48)
    FLECK_M = [emat(f"fleck{k}", (1.0, 0.75, 0.25), (1.0, 0.72, 0.18), 0.0, metal=1.0, rough=0.2) for k in range(4)]; FLECKS = []
    for i in range(44):
        rr_ = (TR_ - 0.012) * math.sqrt(_rg.random()); th = _rg.uniform(0, 6.283)
        bpy.ops.mesh.primitive_ico_sphere_add(radius=_rg.uniform(0.0011, 0.0022), subdivisions=1, location=TUB + Vector((rr_ * math.cos(th), rr_ * math.sin(th), 0.0)))
        fo = bpy.context.active_object; fo.name = f"fleck{i}"; fo.data.materials.append(FLECK_M[i % 4]); FLECKS.append(fo)
    bub_m = glassm("bubble", (1, 1, 1), 0.0, 1.1); BUBS = []
    for i in range(22):
        bpy.ops.mesh.primitive_uv_sphere_add(radius=_rg.uniform(0.0018, 0.0035), segments=12, ring_count=6); bo = bpy.context.active_object; bo.name = f"bub{i}"; bo.data.materials.append(bub_m)
        rr_ = (TR_ - 0.01) * math.sqrt(_rg.random()); th = _rg.uniform(0, 6.283); BUBS.append((bo, rr_ * math.cos(th), rr_ * math.sin(th), _rg.random()))
    rinse = cyl("rinse", 0.0045, 0.2, TUB + Vector((0.012, 0, 0.08 + 0.1)), glassm("water", (0.85, 0.93, 1.0), 0.05, 1.33), verts=16)
    hose = cyl("hose", 0.007, 0.03, TUB + Vector((0.012, 0, 0.295)), mat("hosem", (0.1, 0.45, 0.2), 0.0, 0.5), verts=16)
    GRAIN_W = mat("grainw", (0.95, 0.95, 0.95), 0.0, 0.6); GRAIN_B = mat("grainb", (0.33, 0.17, 0.06), 0.1, 0.7); POWDER, DUST = [], []
    for i in range(30):
        bpy.ops.mesh.primitive_ico_sphere_add(radius=0.0012, subdivisions=1); g_ = bpy.context.active_object; g_.name = f"powder{i}"; g_.data.materials.append(GRAIN_W)
        POWDER.append((g_, _rg.uniform(-0.02, 0.02), _rg.uniform(-0.02, 0.02), _rg.random() * 0.5))
    for i in range(60):
        bpy.ops.mesh.primitive_ico_sphere_add(radius=_rg.uniform(0.0012, 0.002), subdivisions=1); g_ = bpy.context.active_object; g_.name = f"dust{i}"; g_.data.materials.append(GRAIN_B)
        rr_ = (TR_ - 0.012) * math.sqrt(_rg.random()); th = _rg.uniform(0, 6.283); DUST.append((g_, rr_ * math.cos(th), rr_ * math.sin(th), _rg.random() * 0.6))
    dustbed = cyl("dustbed", TR_ - 0.005, 0.004, TUB + Vector((0, 0, 0.006)), mat("dustbedm", (0.30, 0.15, 0.05), 0.1, 0.75), verts=48)
    # the board that goes into the tub (stands upright in the liquid)
    board_root = empty("board_root", TUB + Vector((0, 0, 0.3)))
    bb_ = box("tubboard", (0.055, 0.0016, 0.085), (0, 0, 0), mat("pcb2", (0.02, 0.22, 0.13), 0.1, 0.45)); bb_.parent = board_root
    for k, (bx, bz, bw) in enumerate(((0.0, 0.015, 0.018), (-0.012, -0.02, 0.01), (0.014, -0.022, 0.012))):
        c_ = box(f"tubchip{k}", (bw, 0.003, bw), (bx, -0.0015, bz), chipm); c_.parent = board_root
    for k in range(6):
        gp = box(f"tubpin{k}", (0.0016, 0.0032, 0.007), (-0.012 + k * 0.0048, -0.0005, -0.036), gold); gp.parent = board_root
    # crucible on a brick stand, torch, the mould and the bar
    CRU = Vector((0.17, 0.15, 0.045))
    brick = box("brick", (0.075, 0.075, 0.045), (0.17, 0.15, 0.0225), mat("brickm", (0.42, 0.16, 0.08), 0.0, 0.9), bevel=0.002)
    cru_root = empty("cru_root", CRU + Vector((0, -0.033, 0.036)))          # pivot on the front lip: it tilts forward (-y) to pour
    cru = cyl("crucible", 0.033, 0.036, (0, 0.033, -0.018), mat("ceramic", (0.78, 0.74, 0.68), 0.0, 0.85), fill="NOTHING"); cru.parent = cru_root
    sd = cru.modifiers.new("solid", "SOLIDIFY"); sd.thickness = 0.004
    crf = cyl("cru_floor", 0.033, 0.004, (0, 0.033, -0.034), mat("ceramic2", (0.78, 0.74, 0.68), 0.0, 0.85)); crf.parent = cru_root
    melt_m = emat("melt", (0.28, 0.14, 0.05), (1.0, 0.5, 0.1), 0.0, metal=0.3, rough=0.6)
    melt = cyl("melt", 0.028, 0.008, (0, 0.033, -0.027), melt_m); melt.parent = cru_root
    torch_body = cyl("torch", 0.008, 0.07, (0.27, 0.15, 0.075), mat("torchm", (0.75, 0.15, 0.1), 0.3, 0.4), verts=20, rot=(0, math.pi / 2, 0))
    tflame_m = emat("tflame", (0.3, 0.5, 1.0), (0.35, 0.6, 1.0), 0.0)
    bpy.ops.mesh.primitive_cone_add(radius1=0.008, radius2=0.0, depth=0.05, vertices=20, location=(0.211, 0.15, 0.075), rotation=(0, -math.pi / 2, 0))
    tflame = bpy.context.active_object; tflame.name = "torchflame"; tflame.data.materials.append(tflame_m); tflame.visible_shadow = False
    MOU = Vector((0.17, 0.035, 0.0)); steel = mat("steel", (0.55, 0.56, 0.6), 0.9, 0.35)
    for nm_, d_, l_ in (("mould_floor", (0.064, 0.112, 0.006), (0, 0, 0.003)), ("mould_w1", (0.064, 0.008, 0.026), (0, 0.052, 0.013)), ("mould_w2", (0.064, 0.008, 0.026), (0, -0.052, 0.013)),
                        ("mould_w3", (0.008, 0.096, 0.026), (0.028, 0, 0.013)), ("mould_w4", (0.008, 0.096, 0.026), (-0.028, 0, 0.013))):
        box(nm_, d_, MOU + Vector(l_), steel, bevel=0.0008)
    stream = cyl("stream", 0.0035, 0.06, (0, 0, 0), emat("streamm", (0.3, 0.08, 0.01), (1.0, MOLT[1], MOLT[2]), MOLT[0] * 1.2), verts=16); stream.visible_shadow = False
    bar_m = emat("barm", (1.0, 0.66, 0.16), (1.0, 0.36, 0.04), 0.0, metal=1.0, rough=0.2)
    bar_root = empty("bar_root", MOU + Vector((0, 0, 0.006)))
    bar = box("bar", (0.046, 0.094, 0.018), (0, 0, 0.009), bar_m, bevel=0.003); bar.parent = bar_root
    from PIL import Image as _Ig, ImageDraw as _Dg
    _st = _Ig.new("RGB", (460, 940), (232, 168, 60)); _ds = _Dg.Draw(_st)
    _ds.rounded_rectangle((26, 26, 434, 914), 40, outline=(150, 96, 22), width=10)
    for _y, _s, _z in ((300, "FINE GOLD", 62), (470, "999.9", 96), (640, "1 kg", 80)): _ds.text((230, _y), _s, font=U.font(_z), fill=(140, 88, 20), anchor="mm")
    _stp = os.path.join(a.out, "bar_stamp.png"); _st.save(_stp)
    bpy.ops.mesh.primitive_plane_add(size=1, location=(0, 0, 0.0181)); stamp = bpy.context.active_object; stamp.name = "stamp"; stamp.scale = (0.040, 0.088, 1)
    bpy.ops.object.transform_apply(scale=True); stamp.parent = bar_root
    st_m = bpy.data.materials.new("stampm"); st_m.use_nodes = True; _n = st_m.node_tree; _b = _n.nodes["Principled BSDF"]; _tx = _n.nodes.new("ShaderNodeTexImage")
    _tx.image = bpy.data.images.load(os.path.abspath(_stp)); _n.links.new(_tx.outputs[0], _b.inputs["Base Color"]); _b.inputs["Metallic"].default_value = 1.0; _b.inputs["Roughness"].default_value = 0.18
    stamp.data.materials.append(st_m)
    # phones: generic old slabs in mixed colours (no logos), used by the drawer, the comparison pile and the mountain behind the bench
    SLAB_COL = [(0.05, 0.055, 0.065), (0.75, 0.76, 0.78), (0.82, 0.68, 0.52), (0.12, 0.2, 0.42), (0.55, 0.08, 0.12), (0.9, 0.9, 0.88), (0.1, 0.35, 0.3)]
    SLAB_M = [mat(f"slab{k}", c, 0.7 if k < 3 else 0.2, 0.35) for k, c in enumerate(SLAB_COL)]; SCR_M = mat("deadscr", (0.01, 0.01, 0.015), 0.1, 0.12)
    def slab(name, loc, rot, k, bevel=0.004, parent=None):
        o = box(name, PH, (0, 0, 0), SLAB_M[k % len(SLAB_M)], bevel=bevel); o.location = loc; o.rotation_euler = rot
        s_ = box(name + "_scr", (PH[0] - 0.006, PH[1] - 0.008, 0.0008), (0, 0, PH[2] / 2 + 0.0003), SCR_M); s_.parent = o
        if parent: o.parent = parent
        return o
    MOUNT = []
    for i in range(520):                                              # a heap behind the bench: packed from the ground up, peaked in the middle
        r = 0.62 * math.sqrt(_rg.random()); th = _rg.uniform(0, math.pi); x = r * math.cos(th) * 1.5; y = 0.95 + r * math.sin(th) * 0.5
        top = 0.40 * max(0.0, 1 - (r / 0.62) ** 1.4); z = top * (1 - _rg.random() ** 2.2) + 0.005      # most slabs sit near the surface of the heap
        MOUNT.append(slab(f"heap{i}", (x, y, z), (_rg.uniform(-0.6, 0.6), _rg.uniform(-0.6, 0.6), _rg.uniform(0, 6.28)), _rg.randrange(7), bevel=0.0))
    bpy.ops.mesh.primitive_uv_sphere_add(radius=1.0, location=(0.0, 1.1, -0.02), segments=32, ring_count=16); core = bpy.context.active_object; core.name = "heapcore"
    core.scale = (0.72, 0.16, 0.27); core.data.materials.append(SLAB_M[0])                    # a dark core so no sky shows through the gaps
    drawer_root = empty("drawer_root", (-0.16, -0.16, 0.0)); wood2 = mat("drawerwood", (0.62, 0.45, 0.28), 0.0, 0.55)
    for nm_, d_, l_ in (("drw_floor", (0.20, 0.13, 0.004), (0, 0, 0.002)), ("drw_w1", (0.20, 0.008, 0.045), (0, 0.061, 0.0225)), ("drw_w2", (0.20, 0.012, 0.05), (0, -0.061, 0.025)),
                        ("drw_w3", (0.008, 0.13, 0.045), (0.096, 0, 0.0225)), ("drw_w4", (0.008, 0.13, 0.045), (-0.096, 0, 0.0225))):
        o = box(nm_, d_, l_, wood2, bevel=0.0015); o.parent = drawer_root
    knobd = cyl("drw_knob", 0.006, 0.012, (0, -0.072, 0.03), mat("brass", (0.8, 0.6, 0.3), 1.0, 0.3), verts=16, rot=(math.pi / 2, 0, 0)); knobd.parent = drawer_root
    for k, (x_, y_, rz, tilt) in enumerate(((-0.055, 0.02, 0.3, 0.12), (0.0, -0.01, -0.2, -0.15), (0.05, 0.025, 0.15, 0.2), (-0.04, -0.03, 1.4, -0.1), (0.055, -0.03, 1.7, 0.1))):
        slab(f"drw_phone{k}", (x_, y_, 0.014 + 0.004 * k), (tilt, 0.0, rz), k + 1, parent=drawer_root)
    dph = slab("drw_lit", (0.0, 0.0, 0.04), (0.0, 0.0, 0.0), 0, parent=drawer_root)                 # the one that lights up (lies on top)
    bpy.ops.mesh.primitive_plane_add(size=1, location=(0, 0, PH[2] / 2 + 0.0009)); dscr = bpy.context.active_object; dscr.name = "drw_screen"; dscr.scale = (0.069, 0.149, 1)
    bpy.ops.object.transform_apply(scale=True); dscr.parent = dph
    dsm = bpy.data.materials.new("drw_screen"); dsm.use_nodes = True; _n = dsm.node_tree
    for nd in list(_n.nodes): _n.nodes.remove(nd)
    dtx = _n.nodes.new("ShaderNodeTexImage"); _em = _n.nodes.new("ShaderNodeEmission"); _em.inputs["Strength"].default_value = 1.4; _o = _n.nodes.new("ShaderNodeOutputMaterial")
    _n.links.new(dtx.outputs[0], _em.inputs[0]); _n.links.new(_em.outputs[0], _o.inputs[0]); dscr.data.materials.append(dsm)
    # comparison: a little heap of phones (gold flecks all through it) next to a heap of rock (one fleck)
    piles_root = empty("piles_root", (0.0, 0.30, 0.0)); PFL = emat("pilefleck", (1.0, 0.75, 0.25), (1.0, 0.72, 0.18), 6.0, metal=1.0, rough=0.2)
    for i in range(16):
        o = slab(f"cmp_phone{i}", (-0.075 + _rg.uniform(-0.035, 0.035), _rg.uniform(-0.03, 0.03), 0.004 + 0.007 * (i // 4)), (_rg.uniform(-0.4, 0.4), _rg.uniform(-0.4, 0.4), _rg.uniform(0, 6.28)), i, bevel=0.0, parent=piles_root)
        o.scale = (0.55, 0.55, 0.55)
    for i in range(14):
        bpy.ops.mesh.primitive_ico_sphere_add(radius=0.0018, subdivisions=1, location=(-0.075 + _rg.uniform(-0.03, 0.03), _rg.uniform(-0.025, 0.025), _rg.uniform(0.006, 0.03)))
        o = bpy.context.active_object; o.data.materials.append(PFL); o.parent = piles_root
    rock_m = mat("rock", (0.38, 0.36, 0.34), 0.0, 0.9)
    for i in range(16):
        bpy.ops.mesh.primitive_ico_sphere_add(radius=_rg.uniform(0.010, 0.017), subdivisions=2, location=(0.075 + _rg.uniform(-0.035, 0.035), _rg.uniform(-0.03, 0.03), 0.008 + 0.009 * (i // 5)))
        o = bpy.context.active_object; o.data.materials.append(rock_m); o.parent = piles_root; o.scale = (1.0, _rg.uniform(0.7, 1.2), _rg.uniform(0.6, 0.9))
    bpy.ops.mesh.primitive_ico_sphere_add(radius=0.0018, subdivisions=1, location=(0.082, -0.012, 0.03)); o = bpy.context.active_object; o.data.materials.append(PFL); o.parent = piles_root
    GOLD_ANCH = {"pins": (phone_root, (0, -PH[1] / 2 + 0.0072, z0 + 0.001)), "chip": (phone_root, (0.004, 0.025, z0 + 0.002)), "hair": (phone_root, (0.012, 0.028, z0 + 0.0018)),
                 "battery": (batt, (0, 0, 0.0015)), "tub": (None, tuple(TUB + Vector((0, 0, 0.115)))), "mud": (None, tuple(TUB + Vector((0, -0.04, 0.02)))),
                 "crucible": (cru_root, (0, 0.033, 0.002)), "bar": (bar_root, (0, -0.02, 0.019)), "drawer": (drawer_root, (0.0, -0.06, 0.05)), "dphone": (dph, (0, 0, 0.005)),
                 "phonepile": (piles_root, (-0.075, 0, 0.035)), "rockpile": (piles_root, (0.075, 0, 0.035)), "heap": (None, (0.0, 0.95, 0.3))}

# ---- silicon (FIX #17, "Your phone is made of sand"): the gold workbench re-dressed. Builds on the gold props (tub, crucible, bar, torch).
# The phone mountain becomes a heap of white quartz lumps; the drawer, comparison piles and tub board are unused. Events (0..1 unless noted):
#  "sand"   grains rain onto the phone (hook; restarts at the end for the loop)    "brain"  the main chip glows
#  "charge" quartz lumps + coal drop into the arc furnace   "furnace" furnace glow   "metal" grey silicon-metal chunks appear beside it
#  "chunks" the chunks sit in the tub (cleaning)            "shine"  they turn glossy  "dip" the seed lowers to the melt  "grow" crystal grows (0..1)
#  "spin"   crystal and crucible turn opposite ways          "out"    the crystal lifts clear of the melt   "hot" it glows hot (fades as it cools)
#  "glare"  the melt flares white (hides the crystal during the follow line)          "snail" a snail crawls past the crucible
#  "slab"   the crystal now lies on the saw bed              "saw"    wires cut down through it   "fan" the slices spread out
#  "wafer"  one wafer stands up as a mirror                  "chips"  a grid of chips prints across it
#  "case"   the hero phone is in a case on a charger         "hot2"   the phone runs warm (red glow)   "caseoff" the case slides off
SIL_ANCH = {}
if SIL:
    import random as _rs; _rs.seed(17)
    hide_all(MOUNT + [c for m_ in MOUNT for c in m_.children] + [core, hair], True); hide_all(drawer_root.children_recursive + piles_root.children_recursive + board_root.children_recursive, True)
    QZ_M = [mat(f"quartz{k}", c, 0.0, r_) for k, (c, r_) in enumerate((((0.93, 0.93, 0.91), 0.35), ((0.86, 0.87, 0.88), 0.3), ((0.97, 0.95, 0.92), 0.45)))]
    QHEAP = []
    for i in range(340):                                              # the quartz heap behind the bench (same footprint as #16's phone mountain)
        r = 0.62 * math.sqrt(_rs.random()); th = _rs.uniform(0, math.pi); x = r * math.cos(th) * 1.5; y = 0.95 + r * math.sin(th) * 0.5
        top = 0.40 * max(0.0, 1 - (r / 0.62) ** 1.4); z = top * (1 - _rs.random() ** 2.2) + 0.01
        bpy.ops.mesh.primitive_ico_sphere_add(radius=_rs.uniform(0.022, 0.05), subdivisions=1, location=(x, y, z)); o = bpy.context.active_object; o.name = f"qheap{i}"
        o.scale = (1.0, _rs.uniform(0.6, 1.1), _rs.uniform(0.5, 0.9)); o.rotation_euler = (_rs.uniform(0, 3), _rs.uniform(0, 3), _rs.uniform(0, 3)); o.data.materials.append(QZ_M[i % 3]); QHEAP.append(o)
    bpy.ops.mesh.primitive_uv_sphere_add(radius=1.0, location=(0.0, 1.1, -0.02), segments=32, ring_count=16); qcore = bpy.context.active_object; qcore.name = "qcore"
    qcore.scale = (0.72, 0.16, 0.27); qcore.data.materials.append(QZ_M[1])
    # the main chip glows (the "brain"): give the cpu its own material
    cpu = bpy.data.objects["cpu"]; brain_m = emat("brain", (0.02, 0.02, 0.03), (0.35, 0.75, 1.0), 0.0, metal=0.2, rough=0.3); cpu.data.materials.clear(); cpu.data.materials.append(brain_m)
    SAND_M = mat("sand", (0.80, 0.66, 0.42), 0.0, 0.8); SANDG = []
    for i in range(150):
        bpy.ops.mesh.primitive_ico_sphere_add(radius=_rs.uniform(0.0016, 0.0028), subdivisions=1); g_ = bpy.context.active_object; g_.name = f"sandg{i}"; g_.data.materials.append(SAND_M)
        SANDG.append((g_, _rs.uniform(-0.03, 0.03), _rs.uniform(-0.06, 0.07), _rs.random() * 0.6))
    # arc furnace: a dark open pot, three graphite electrodes dropping in from above, a glow inside; quartz + coal fall in, grey metal comes out
    FUR = Vector((-0.16, -0.15, 0.0)); furm = mat("furnace", (0.10, 0.10, 0.11), 0.3, 0.6)
    fur = cyl("furnace", 0.055, 0.07, FUR + Vector((0, 0, 0.035)), furm, fill="NOTHING", verts=48); sd = fur.modifiers.new("solid", "SOLIDIFY"); sd.thickness = 0.006
    cyl("fur_floor", 0.055, 0.006, FUR + Vector((0, 0, 0.003)), furm)
    fglow_m = emat("furglow", (0.05, 0.02, 0.01), (1.0, 0.38, 0.06), 0.0); fglow = cyl("fur_glow", 0.048, 0.004, FUR + Vector((0, 0, 0.04)), fglow_m)
    graph = mat("graphite_e", (0.06, 0.06, 0.065), 0.5, 0.45)
    for k in range(3):
        ang = k * 2 * math.pi / 3; cyl(f"electrode{k}", 0.007, 0.16, FUR + Vector((0.022 * math.cos(ang), 0.022 * math.sin(ang), 0.12)), graph, verts=16)
    fur_l = bpy.data.objects.new("fur_light", bpy.data.lights.new("fur_light", "POINT")); col.objects.link(fur_l); fur_l.location = FUR + Vector((0, 0, 0.09)); fur_l.data.color = (1.0, 0.45, 0.12); fur_l.data.energy = 0
    COAL_M = mat("coal", (0.02, 0.02, 0.02), 0.1, 0.5); CHARGE = []
    for i in range(20):
        bpy.ops.mesh.primitive_ico_sphere_add(radius=_rs.uniform(0.006, 0.010), subdivisions=1); o = bpy.context.active_object; o.name = f"charge{i}"
        o.data.materials.append(COAL_M if i % 3 == 0 else QZ_M[i % 3]); CHARGE.append((o, _rs.uniform(-0.03, 0.03), _rs.uniform(-0.03, 0.03), _rs.random() * 0.5))
    METAL_M = mat("simetal", (0.20, 0.21, 0.23), 0.9, 0.6); MET = Vector((-0.08, -0.16, 0.0)); METAL = []
    SPECK_M = mat("speck", (0.06, 0.04, 0.03), 0.0, 0.9)
    for i in range(7):
        bpy.ops.mesh.primitive_ico_sphere_add(radius=_rs.uniform(0.008, 0.012), subdivisions=1, location=MET + Vector((_rs.uniform(-0.025, 0.025), _rs.uniform(-0.02, 0.02), 0.007)))
        o = bpy.context.active_object; o.name = f"metal{i}"; o.data.materials.append(METAL_M); o.scale = (1.0, 0.8, 0.7); METAL.append(o)
        for j in range(4):                                            # dark dirt specks on each chunk
            bpy.ops.mesh.primitive_ico_sphere_add(radius=0.0016, subdivisions=1, location=o.location + Vector((_rs.uniform(-0.007, 0.007), -0.007, _rs.uniform(-0.002, 0.006))))
            sp_ = bpy.context.active_object; sp_.data.materials.append(SPECK_M); sp_.parent = o; sp_.matrix_parent_inverse = o.matrix_world.inverted()
    TCH = []
    for i in range(6):                                                # chunks in the tub (cleaning)
        bpy.ops.mesh.primitive_ico_sphere_add(radius=_rs.uniform(0.009, 0.013), subdivisions=1, location=TUB + Vector((_rs.uniform(-0.03, 0.03), _rs.uniform(-0.03, 0.03), 0.012)))
        o = bpy.context.active_object; o.name = f"tubchunk{i}"; o.data.materials.append(METAL_M); o.scale = (1.0, 0.8, 0.7); TCH.append(o)
    # the crystal (ingot): body grows up from the melt surface; the shoulder cone, seed and pull cable ride on top
    MELT_Z = 0.058; IL, IR = 0.20, 0.024
    ingot_m = emat("ingot", (0.30, 0.31, 0.34), (1.0, 0.42, 0.1), 0.0, metal=1.0, rough=0.28)
    ibody_root = empty("ibody_root", (CRU.x, 0.15, MELT_Z)); ibody = cyl("ingot_body", IR, IL, (CRU.x, 0.15, MELT_Z + IL / 2), ingot_m, verts=48); ibody.parent = ibody_root
    ibody.matrix_parent_inverse = ibody_root.matrix_world.inverted()
    for k in range(4):                                                # 4 growth ridges along the crystal: show the spin
        ang = k * math.pi / 2; rg = box(f"ridge{k}", (0.0026, 0.0026, IL), (CRU.x + IR * math.cos(ang), 0.15 + IR * math.sin(ang), MELT_Z + IL / 2), ingot_m)
        rg.rotation_euler.z = ang + math.pi / 4; rg.parent = ibody_root; rg.matrix_parent_inverse = ibody_root.matrix_world.inverted()
    itop = empty("ingot_top", (CRU.x, 0.15, MELT_Z))
    bpy.ops.mesh.primitive_cone_add(radius1=IR, radius2=0.003, depth=0.03, vertices=48, location=(0, 0, 0.015)); shoulder = bpy.context.active_object; shoulder.name = "shoulder"
    shoulder.data.materials.append(ingot_m); bpy.ops.object.shade_smooth(); shoulder.parent = itop
    seed = cyl("seedrod", 0.0026, 0.04, (0, 0, 0.02), mat("seedm", (0.6, 0.62, 0.66), 1.0, 0.2), verts=12); seed.parent = itop
    cable = cyl("cable", 0.0009, 0.5, (0, 0, 0.29), mat("cablem", (0.2, 0.2, 0.22), 0.8, 0.4), verts=8); cable.parent = itop
    bpy.ops.mesh.primitive_cone_add(radius1=IR, radius2=0.004, depth=0.028, vertices=48, location=(0, 0, 0), rotation=(math.pi, 0, 0)); tail = bpy.context.active_object; tail.name = "tail"
    tail.data.materials.append(ingot_m); bpy.ops.object.shade_smooth()
    hring_m = emat("hotring", (0.2, 0.05, 0.01), (1.0, 0.4, 0.08), 0.0)
    bpy.ops.mesh.primitive_torus_add(major_radius=IR + 0.0006, minor_radius=0.0028, location=(CRU.x, 0.15, MELT_Z + 0.002)); hring = bpy.context.active_object; hring.name = "hotring"; hring.data.materials.append(hring_m)
    ing_l = bpy.data.objects.new("ingot_light", bpy.data.lights.new("ingot_light", "POINT")); col.objects.link(ing_l); ing_l.data.color = (1.0, 0.5, 0.15); ing_l.data.energy = 0
    # snail (slower than the crystal? no: much faster)
    snail_root = empty("snail_root", (0.105, 0.10, 0.0)); snm = mat("snailbody", (0.55, 0.45, 0.33), 0.0, 0.5); shm = mat("snailshell", (0.45, 0.25, 0.10), 0.1, 0.35)
    bpy.ops.mesh.primitive_uv_sphere_add(radius=0.006, location=(0, 0, 0.003)); sb = bpy.context.active_object; sb.scale = (2.0, 0.7, 0.5); sb.data.materials.append(snm); sb.parent = snail_root
    bpy.ops.mesh.primitive_torus_add(major_radius=0.0045, minor_radius=0.0028, location=(-0.002, 0, 0.0085), rotation=(math.pi / 2, 0, 0)); ss = bpy.context.active_object; ss.data.materials.append(shm); ss.parent = snail_root
    for dy in (-0.0018, 0.0018):
        st_ = cyl(f"stalk{dy}", 0.0005, 0.007, (0.011, dy, 0.007), snm, verts=8, rot=(0, math.radians(-25), 0)); st_.parent = snail_root
    # saw bed: the crystal lying down, saw wires above, the slices, a bank card for scale, then the hero wafer
    SAW = Vector((0.0, 0.30, 0.0)); bed = box("sawbed", (0.24, 0.05, 0.004), SAW + Vector((0, 0, 0.002)), mat("sawbedm", (0.25, 0.26, 0.3), 0.6, 0.4))
    ingot_h = cyl("ingot_h", IR, IL, SAW + Vector((0, 0, 0.004 + IR)), ingot_m, verts=48, rot=(0, math.pi / 2, 0))
    wire_m = emat("sawwire", (0.3, 0.3, 0.32), (0.6, 0.85, 1.0), 0.0, metal=0.8, rough=0.3); WIRES2 = []
    for k in range(9):
        w_ = cyl(f"sawwire{k}", 0.0007, 0.09, SAW + Vector((-0.08 + k * 0.02, 0, 0.07)), wire_m, verts=8, rot=(math.pi / 2, 0, 0)); WIRES2.append(w_)
    slice_m = mat("slicem", (0.72, 0.74, 0.78), 1.0, 0.08); SLICES = []
    for k in range(9):
        o = cyl(f"slice{k}", IR, 0.002, SAW + Vector((-0.08 + k * 0.02, 0, 0.004 + IR)), slice_m, verts=48, rot=(0, math.pi / 2, 0)); SLICES.append(o)
    card = box("bankcard", (0.002, 0.034, 0.0215), SAW + Vector((0.13, 0, 0.004 + 0.011)), mat("cardm", (0.05, 0.22, 0.55), 0.2, 0.35), bevel=0.0006)
    from PIL import Image as _Iw, ImageDraw as _Dw; import colorsys as _cs
    _wi = _Iw.new("RGB", (512, 512), (190, 195, 205)); _dw = _Dw.Draw(_wi); n_ = 22; c_ = 512 / n_
    for i_ in range(n_):
        for j_ in range(n_):
            x0_, y0_ = i_ * c_, j_ * c_; cx_, cy_ = x0_ + c_ / 2 - 256, y0_ + c_ / 2 - 256
            if cx_ * cx_ + cy_ * cy_ > (246 - c_ * 0.7) ** 2: continue
            h_ = ((i_ + j_) / (2 * n_) + 0.15 * math.sin(i_ * 0.5)) % 1.0; r_, g_, b_ = _cs.hsv_to_rgb(h_, 0.55, 0.95)
            _dw.rectangle((x0_ + 1.5, y0_ + 1.5, x0_ + c_ - 1.5, y0_ + c_ - 1.5), fill=(int(r_ * 255), int(g_ * 255), int(b_ * 255)))
    _wp = os.path.join(a.out, "wafer_chips.png"); _wi.save(_wp)
    WR = 0.05; wafer_root = empty("wafer_root", SAW + Vector((0, 0, 0.004 + WR)))
    wafer = cyl("wafer", WR, 0.0015, (0, 0, 0), None, verts=96, rot=(math.pi / 2, 0, 0)); wafer.parent = wafer_root
    wafer_m = bpy.data.materials.new("waferm"); wafer_m.use_nodes = True; _n = wafer_m.node_tree; _b = _n.nodes["Principled BSDF"]
    _b.inputs["Metallic"].default_value = 1.0; _b.inputs["Roughness"].default_value = 0.035
    _tc = _n.nodes.new("ShaderNodeTexCoord"); _mp = _n.nodes.new("ShaderNodeMapping"); _mp.inputs["Scale"].default_value = (1 / (2 * WR), 1 / (2 * WR), 1); _mp.inputs["Location"].default_value = (0.5, 0.5, 0)
    _n.links.new(_tc.outputs["Object"], _mp.inputs["Vector"]); _tw = _n.nodes.new("ShaderNodeTexImage"); _tw.image = bpy.data.images.load(os.path.abspath(_wp)); _tw.extension = "CLIP"
    _n.links.new(_mp.outputs["Vector"], _tw.inputs["Vector"])
    wmix = _n.nodes.new("ShaderNodeMix"); wmix.data_type = "RGBA"; wmix.inputs[6].default_value = (0.80, 0.82, 0.86, 1); _n.links.new(_tw.outputs[0], wmix.inputs[7])
    _n.links.new(wmix.outputs[2], _b.inputs["Base Color"]); _n.links.new(_tw.outputs[0], _b.inputs["Emission Color"]); _b.inputs["Emission Strength"].default_value = 0.0
    wafer.data.materials.append(wafer_m)
    # beach sand vs a lump of pure quartz (the honest twist), on the front of the bench
    CMP = Vector((0.30, -0.06, 0.0))
    bpy.ops.mesh.primitive_cone_add(radius1=0.03, radius2=0.002, depth=0.022, vertices=32, location=CMP + Vector((-0.035, 0, 0.011))); spile = bpy.context.active_object; spile.name = "sandpile"
    bsand = mat("beachsand", (0.40, 0.32, 0.21), 0.0, 0.95); spile.data.materials.append(bsand); bpy.ops.object.shade_smooth()
    BSG = [mat(f"bsg{k}", c, 0.0, 0.9) for k, c in enumerate(((0.35, 0.30, 0.25), (0.75, 0.65, 0.5), (0.2, 0.17, 0.15), (0.55, 0.35, 0.2)))]
    for i in range(40):                                               # mixed dark/brown grains: beach sand is dirty
        rr_ = 0.028 * math.sqrt(_rs.random()); th = _rs.uniform(0, 6.283); zz = 0.022 * (1 - rr_ / 0.03) * _rs.random()
        bpy.ops.mesh.primitive_ico_sphere_add(radius=0.0016, subdivisions=1, location=CMP + Vector((-0.035 + rr_ * math.cos(th), rr_ * math.sin(th), zz + 0.001)))
        bpy.context.active_object.data.materials.append(BSG[i % 4])
    bpy.ops.mesh.primitive_ico_sphere_add(radius=0.024, subdivisions=2, location=CMP + Vector((0.035, 0, 0.016))); qlump = bpy.context.active_object; qlump.name = "quartzlump"
    qlump.scale = (1.0, 0.85, 0.7); qlm = mat("qlumpm", (0.95, 0.95, 0.94), 0.0, 0.25); bsdf(qlm).inputs["Subsurface Weight"].default_value = 0.4; qlump.data.materials.append(qlm)
    # the phone case + charger (line 20)
    case_root = empty("case_root", (0, 0, 0)); casem = mat("casem", (0.12, 0.45, 0.42), 0.0, 0.5)
    for nm_, d_, l_ in (("case_floor", (0.081, 0.161, 0.002), (0, 0, -0.0004)), ("case_w1", (0.081, 0.003, 0.011), (0, 0.079, 0.0045)), ("case_w2", (0.081, 0.003, 0.011), (0, -0.079, 0.0045)),
                        ("case_w3", (0.003, 0.161, 0.011), (0.039, 0, 0.0045)), ("case_w4", (0.003, 0.161, 0.011), (-0.039, 0, 0.0045))):
        o = box(nm_, d_, l_, casem, bevel=0.001); o.parent = case_root
    cablec = cyl("chargecable", 0.0018, 0.16, (0, -0.16, 0.0025), mat("cablew", (0.92, 0.92, 0.92), 0.0, 0.5), verts=12, rot=(math.pi / 2, 0, 0))
    plug = box("plug", (0.008, 0.012, 0.004), (0, -0.083, 0.004), mat("plugm", (0.92, 0.92, 0.92), 0.0, 0.4))
    hot_l = bpy.data.objects.new("hot_light", bpy.data.lights.new("hot_light", "POINT")); col.objects.link(hot_l); hot_l.location = (0, -0.02, 0.03); hot_l.data.color = (1.0, 0.12, 0.05); hot_l.data.energy = 0
    SIL_ANCH = {"furnace": (None, tuple(FUR + Vector((0, 0, 0.075)))), "coal": (None, tuple(FUR + Vector((0.02, -0.02, 0.06)))), "metal": (None, tuple(MET + Vector((0, 0, 0.018)))),
                "dirt": (None, tuple(MET + Vector((0.0, -0.01, 0.012)))), "seed": (itop, (0, 0, 0.03)), "ingot": (ibody_root, (0, -IR, IL * 0.6)), "crystal_top": (itop, (0, 0, 0.02)),
                "melt": (None, (CRU.x, 0.15 - 0.02, MELT_Z + 0.004)), "snail": (snail_root, (0, 0, 0.012)), "wafer": (wafer_root, (0, -0.002, 0.02)), "slices": (None, tuple(SAW + Vector((0, -IR, 0.05)))),
                "card": (None, tuple(SAW + Vector((0.13, 0, 0.026)))), "sand": (None, tuple(CMP + Vector((-0.035, 0, 0.024)))), "quartz": (None, tuple(CMP + Vector((0.035, 0, 0.034)))),
                "phone": (None, (0, -0.04, PH[2] + 0.004)), "chip": (None, (0.004, 0.025, z0 + 0.002))}

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
if GOLD:
    for k in ("battery", "mast", "laptop", "tray", "van", "fakemast", "netfilter", "modem", "sim", "filter"):
        ANCH.pop(k, None); bpy.data.objects.remove(bpy.data.objects["anchor_" + k])
    for k, (par, v) in GOLD_ANCH.items(): empty("anchor_" + k, v, par); ANCH[k] = v
if SIL:
    for k, (par, v) in SIL_ANCH.items():
        if "anchor_" + k in bpy.data.objects: bpy.data.objects.remove(bpy.data.objects["anchor_" + k])
        empty("anchor_" + k, v, par); ANCH[k] = v
NODES ={"mast": Vector((-0.15, 0.33, 0.335)), "phone": Vector((0.02, 0.052, z0 + 0.006)), "laptop": Vector((0.16, 0.38, 0.06)), "tray": TR + Vector((0, 0, 0.012)),
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
if GOLD:                                                   # daylight: pale sky, warm low sun from the front-left, the night rim light toned down
    w.node_tree.nodes["Background"].inputs[0].default_value = (0.52, 0.66, 0.86, 1); w.node_tree.nodes["Background"].inputs[1].default_value = 0.9
    sun = bpy.data.objects.new("sun", bpy.data.lights.new("sun", "SUN")); col.objects.link(sun); sun.data.energy = 3.2; sun.data.color = (1.0, 0.9, 0.76); sun.data.angle = 0.06
    sun.rotation_euler = (math.radians(52), math.radians(-18), math.radians(-35))
    bpy.data.objects["rim"].data.energy = 12; bpy.data.objects["rim"].data.color = (1.0, 0.95, 0.9)

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
CAM.update({   # FIX #16 (gold): bench + phone mountain; tub at (-0.17, 0.12), crucible on its brick (0.17, 0.15), mould (0.17, 0.035), drawer (-0.16, -0.16)
       "g_drop": ((0.02, -0.26, 0.07), (0.0, 0.0, 0.04), 26), "g_hero": ((0.13, -0.30, 0.16), (0.0, 0.06, 0.02), 34), "g_wide": ((0.0, -0.62, 0.34), (0.0, 0.30, 0.08), 22),
       "g_open": ((0.0, -0.11, 0.22), (0.0, 0.0, 0.0), 42), "g_batt": ((0.15, -0.21, 0.10), (0.08, -0.08, 0.005), 34), "g_batt_close": ((0.13, -0.17, 0.05), (0.105, -0.115, 0.012), 38),
       "g_pins": ((0.0, -0.125, 0.042), (0.0, -0.072, 0.009), 36), "g_chip": ((0.022, -0.01, 0.055), (0.004, 0.025, 0.006), 38), "g_chip_close": ((0.012, 0.008, 0.03), (0.005, 0.025, 0.007), 40),
       "g_tub": ((-0.17, -0.13, 0.085), (-0.17, 0.12, 0.05), 34), "g_tub_top": ((-0.17, 0.05, 0.26), (-0.17, 0.12, 0.02), 34), "g_tub_low": ((-0.07, -0.08, 0.035), (-0.17, 0.12, 0.035), 30),
       "g_tub_macro": ((-0.15, -0.17, 0.05), (-0.17, 0.12, 0.028), 62), "g_tub_side": ((-0.38, 0.0, 0.10), (-0.17, 0.12, 0.05), 32),
       "g_cru": ((0.08, -0.04, 0.16), (0.17, 0.15, 0.07), 34), "g_cru_top": ((0.11, 0.0, 0.24), (0.17, 0.15, 0.06), 40), "g_cru_in": ((0.15, 0.07, 0.17), (0.17, 0.15, 0.055), 46), "g_pour": ((0.33, -0.06, 0.12), (0.17, 0.07, 0.05), 30), "g_bar": ((0.11, -0.13, 0.05), (0.17, 0.03, 0.025), 32),
       "g_bar_top": ((0.17, -0.06, 0.15), (0.17, 0.035, 0.0), 40), "g_bar_push": ((0.17, -0.03, 0.125), (0.17, 0.04, 0.03), 46), "g_pull": ((0.0, -1.05, 0.62), (0.0, 0.55, 0.20), 22), "g_cmp": ((0.0, 0.08, 0.17), (0.0, 0.30, 0.015), 30),
       "g_drawer": ((-0.10, -0.40, 0.20), (-0.16, -0.16, 0.0), 32), "g_drawer_close": ((-0.16, -0.24, 0.13), (-0.16, -0.16, 0.035), 40)})
CAM.update({   # FIX #17 (silicon): furnace (-0.16, -0.15), metal (-0.08, -0.16), crystal above the crucible (0.17, 0.15), saw bed (0, 0.30), sand vs quartz (0.30, -0.06)
       "s_furn": ((-0.05, -0.38, 0.18), (-0.16, -0.15, 0.06), 32), "s_furn_top": ((-0.16, -0.27, 0.28), (-0.16, -0.15, 0.04), 36),
       "s_metal": ((-0.03, -0.30, 0.08), (-0.08, -0.16, 0.012), 38), "s_metal_wide": ((-0.10, -0.42, 0.15), (-0.11, -0.16, 0.025), 32),
       "s_metal_macro": ((-0.065, -0.215, 0.035), (-0.08, -0.16, 0.010), 50),
       "s_seed_high": ((0.12, 0.0, 0.22), (0.17, 0.15, 0.12), 40), "s_seed": ((0.135, 0.06, 0.11), (0.17, 0.15, 0.065), 46),
       "s_ingot": ((0.03, -0.32, 0.17), (0.17, 0.15, 0.15), 28), "s_ingot_low": ((0.11, -0.08, 0.035), (0.17, 0.15, 0.15), 22),
       "s_ingot_orbit": ((0.36, -0.04, 0.20), (0.17, 0.15, 0.15), 26), "s_ingot_side": ((0.36, 0.32, 0.12), (0.17, 0.15, 0.15), 26),
       "s_snail": ((0.09, 0.00, 0.035), (0.12, 0.10, 0.006), 42), "s_snail2": ((0.15, 0.01, 0.03), (0.13, 0.10, 0.006), 44),
       "s_saw": ((0.0, 0.08, 0.16), (0.0, 0.30, 0.025), 30), "s_saw_side": ((0.22, 0.17, 0.08), (0.0, 0.30, 0.025), 30),
       "s_card": ((0.20, 0.19, 0.06), (0.10, 0.30, 0.028), 40), "s_card_close": ((0.16, 0.24, 0.04), (0.12, 0.30, 0.026), 50),
       "s_wafer": ((0.0, 0.14, 0.07), (0.0, 0.30, 0.055), 38), "s_wafer_close": ((0.02, 0.20, 0.06), (0.0, 0.30, 0.055), 44),
       "s_wafer_tilt": ((0.11, 0.17, 0.11), (0.0, 0.30, 0.055), 38),
       "s_cmp": ((0.30, -0.27, 0.12), (0.30, -0.06, 0.015), 30), "s_cmp_close": ((0.30, -0.20, 0.06), (0.30, -0.06, 0.016), 30),
       "s_case": ((0.11, -0.21, 0.11), (0.0, -0.01, 0.0), 34)})
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

LIQ_STOPS = [((0.92, 0.96, 1.0), 1.0), ((0.04, 0.22, 1.0), 0.85), ((0.09, 0.075, 0.06), 0.35), ((1.0, 0.76, 0.10), 0.85)]   # clear, blue, murky, yellow
DLAST = [None]
def toss_pose(u):
    """FIX #16 frame 1: tossed in from the left, tumbling, then the drop_pose bounces. -> (loc, rot)."""
    if u < 0.4:
        k = u / 0.4; return Vector((-0.28 * (1 - k), 0.05 * (1 - k), 0.15 * (1 - k * k) + 0.0001)), (0.7 * (1 - k), 4 * math.pi * (1 - k), 0.6 * (1 - k))
    hz, rx, ry = drop_pose(0.38 + (u - 0.4) / 0.6 * 0.62); return Vector((0, 0, hz + 0.0001)), (rx, ry, 0.0)
def apply_gold(t, b, p):
    loc, rot = toss_pose(track("toss", t, 1.0)); phone_root.location = loc; phone_root.rotation_euler = rot
    hide_all(phone_root.children_recursive, track("gone", t) > 0.5); hide_all([knob, bpy.data.objects["filter_track"]], True)   # FIX #12's filter switch has no place in a generic old phone
    gg = track("goldglow", t); bsdf(gold_glow).inputs["Emission Strength"].default_value = 7 * gg * (0.75 + 0.25 * math.sin(t * 6))
    hair.hide_render = track("hair", t) < 0.5 or track("gone", t) > 0.5
    bo = track("battout", t); bf = track("battfire", t)
    batt.location = BATT0.lerp(BATT_OUT, ease(bo)) + Vector((0, 0, 0.045 * math.sin(math.pi * bo))); batt.scale = (1 + 0.15 * bf, 1 + 0.15 * bf, 1 + 2.4 * bf)
    bsdf(batt_m).inputs["Emission Color"].default_value = (1.0, 0.12, 0.0, 1); bsdf(batt_m).inputs["Emission Strength"].default_value = 0.8 * bf
    bpy.context.view_layer.update()   # batt.matrix_world must be this frame's (stale in --one renders)
    flame.hide_render = fcore.hide_render = bf < 0.05; fl_ = bf * (0.85 + 0.2 * math.sin(t * 23) + 0.1 * math.sin(t * 41))
    flame.location = batt.matrix_world.translation + Vector((0, 0, 0.006 + 0.022 * fl_)); flame.scale = (fl_, fl_, fl_ * 1.2)
    fcore.location = flame.location + Vector((0, -0.008 * fl_, -0.007 * fl_)); fc_ = fl_ * (0.9 + 0.15 * math.sin(t * 37)); fcore.scale = (fc_, fc_, fc_ * 1.1)   # core sits in front of the outer flame (cameras are at -y)
    bsdf(flame_m).inputs["Emission Color"].default_value = (1.0, 0.13, 0.0, 1); bsdf(flame_m).inputs["Emission Strength"].default_value = 0.8 * bf
    bsdf(fcore_m).inputs["Emission Strength"].default_value = 1.3 * bf; fire_l.location = flame.location + Vector((0, 0, 0.02)); fire_l.data.energy = 1.2 * bf
    dk = track("dunk", t); dv = track("dissolve", t)
    board_root.location = TUB + Vector((0, 0, 0.30 - 0.245 * ease(dk) - 0.02 * dv)); board_root.rotation_euler.z = 0.3 * dk; board_root.scale = (1 - 0.3 * dv, 1, max(0.05, 1 - 0.9 * dv))
    hide_all(board_root.children_recursive, dk < 0.01 or dv > 0.97)
    lv = clamp(track("liq", t) / 3) * 3; i0 = min(2, int(lv)); f_ = lv - i0; (c0, w0), (c1, w1) = LIQ_STOPS[i0], LIQ_STOPS[i0 + 1]
    liq_glow.inputs["Base Color"].default_value = (*[c0[j] + (c1[j] - c0[j]) * f_ for j in range(3)], 1); liq_glow.inputs["Transmission Weight"].default_value = w0 + (w1 - w0) * f_
    m_ = track("mud", t); mud.hide_render = m_ < 0.02; mud.scale.z = max(0.02, m_)
    sp = track("sparkle", t); top = 0.004 + 0.02 * m_
    for fo in FLECKS: fo.location.z = top - 0.0006; fo.hide_render = sp < 0.02 or m_ < 0.1
    for k, fm in enumerate(FLECK_M): bsdf(fm).inputs["Emission Strength"].default_value = 11 * sp * (0.55 + 0.45 * math.sin(t * 8 + k * 1.7))
    bu = track("bubble", t)
    for bo_, x_, y_, ph in BUBS: bo_.hide_render = bu < 0.02; bo_.location = TUB + Vector((x_, y_, 0.012 + ((t * 0.7 + ph) % 1.0) * 0.07)); bo_.scale = (bu, bu, bu)
    rn = track("rinse", t); live = 0 < rn < 1; rinse.hide_render = not (live and int(rn * 6) % 2 == 0); hose.hide_render = not live
    pw = track("powder", t)
    for g_, x_, y_, d_ in POWDER:
        u = clamp((pw - d_) / 0.5); g_.hide_render = pw <= d_ or u >= 1 or pw >= 1; g_.location = TUB + Vector((x_, y_, 0.22 - (0.22 - 0.083) * u * u))
    du = track("dust", t)
    for g_, x_, y_, d_ in DUST:
        u = clamp((du - d_) / 0.4); g_.hide_render = du <= d_; g_.location = TUB + Vector((x_, y_, 0.08 - 0.071 * ease(u)))
    dustbed.hide_render = du < 0.25; dustbed.scale.z = max(0.05, clamp((du - 0.25) / 0.75))
    tc = track("torch", t); tflame.hide_render = tc < 0.02; torch_body.hide_render = tc < 0.02; tflame.scale = (tc, tc * (1 + 0.08 * math.sin(t * 31)), tc)
    bsdf(tflame_m).inputs["Emission Strength"].default_value = 3.5 * tc
    # molten gold: a deep orange-gold glow (16x clipped to white under AgX and lit the crucible white); it leaves the crucible as the mould fills
    h = track("heat", t) * (1 - track("fill", t)); melt.hide_render = track("fill", t) > 0.97
    # AgX turns bright saturated surfaces pastel (peach), so molten gold is a dark base lit from within by a saturated orange emission
    bsdf(melt_m).inputs["Emission Color"].default_value = (1.0, MOLT[1], MOLT[2], 1); bsdf(melt_m).inputs["Emission Strength"].default_value = MOLT[0] * h
    bsdf(melt_m).inputs["Base Color"].default_value = (0.28, 0.14 - 0.06 * h, 0.05 - 0.04 * h, 1)
    po = track("pour", t); cru_root.rotation_euler.x = math.radians(68) * ease(po)
    stream.hide_render = not (0.3 < po < 0.97); p0, p1 = Vector((0.17, 0.112, 0.078)), Vector((0.17, 0.075, 0.012 + 0.016 * track("fill", t)))
    d_ = p1 - p0; stream.location = (p0 + p1) / 2; stream.rotation_euler = d_.to_track_quat("Z", "Y").to_euler(); stream.scale = (1, 1, d_.length / 0.06)
    fl = track("fill", t); cl = track("cool", t); li = track("lift", t)
    hide_all(bar_root.children_recursive, fl < 0.01); bar_root.scale = (1, 1, max(0.03, fl)); stamp.hide_render = fl < 0.01 or cl < 0.6
    bsdf(bar_m).inputs["Emission Strength"].default_value = MOLT[0] * fl * (1 - cl); bsdf(bar_m).inputs["Roughness"].default_value = 0.6 - 0.42 * cl
    bsdf(bar_m).inputs["Emission Color"].default_value = (1.0, MOLT[1], MOLT[2], 1)
    bsdf(bar_m).inputs["Base Color"].default_value = (0.3 + 0.7 * cl, 0.08 + 0.58 * cl, 0.01 + 0.15 * cl, 1)
    bar_root.location = MOU + Vector((0, 0, 0.006 + 0.05 * ease(li))); bar_root.rotation_euler = (math.radians(10) * ease(li), 0, math.radians(-22) * ease(li))
    pv = track("piles", t); piles_root.scale = (max(0.001, ease(pv)),) * 3; hide_all(piles_root.children_recursive, pv < 0.02)
    dr = track("drawer", t); drawer_root.location.x = -0.16 - 0.42 * (1 - ease(dr)); hide_all(drawer_root.children_recursive, dr < 0.01)
    spec = b.get("dscreen") or "U.lock_plain()"; import re
    key = spec + (f"@{round(p * 48) / 48:.4f}" if re.search(r"\bp\b", spec) else "")
    if key != DLAST[0]:
        f = os.path.join(SCREEN_DIR, "drw_" + hashlib.md5(key.encode()).hexdigest()[:12] + ".png")
        if not os.path.exists(f): eval(spec, {"U": U, "p": round(p * 48) / 48, "ease": ease, "clamp": clamp}).convert("RGB").resize((540, 960)).save(f)
        dtx.image = bpy.data.images.load(f, check_existing=True); DLAST[0] = key
    lap_light.data.energy = 0

def apply_silicon(t, b, p):
    sv = track("sand", t)
    for g_, x_, y_, d_ in SANDG:
        u = clamp((sv - d_) / 0.4); g_.hide_render = sv <= d_ or u >= 1 or sv >= 1; g_.location = Vector((x_, y_, 0.26 - (0.26 - PH[2] - 0.004) * u * u))
    bsdf(brain_m).inputs["Emission Strength"].default_value = 4.0 * track("brain", t) * (0.8 + 0.2 * math.sin(t * 5))
    ch = track("charge", t)
    for o, x_, y_, d_ in CHARGE:
        u = clamp((ch - d_) / 0.5); o.hide_render = ch <= d_ or u >= 1; o.location = FUR + Vector((x_, y_, 0.25 - 0.21 * u * u))
    fv = track("furnace", t); fl_ = fv * (0.8 + 0.2 * math.sin(t * 27) + 0.1 * math.sin(t * 61))
    bsdf(fglow_m).inputs["Emission Strength"].default_value = 3.0 * fl_; fur_l.data.energy = 2.5 * fl_
    mv = track("metal", t)
    for o in METAL: o.hide_render = mv < 0.05; o.scale = (max(0.01, ease(mv)),) * 3
    for o in METAL:
        for c in o.children: c.hide_render = mv < 0.05
    cv = track("chunks", t); sh = track("shine", t)
    for o in TCH: o.hide_render = cv < 0.5
    bsdf(METAL_M).inputs["Roughness"].default_value = 0.55 - 0.45 * sh; bsdf(METAL_M).inputs["Base Color"].default_value = (0.20 + 0.22 * sh, 0.21 + 0.22 * sh, 0.23 + 0.24 * sh, 1)
    # molten silicon: brighter and paler than gold; "glare" flares it during the follow line
    h = track("heat", t); gl = track("glare", t)
    bsdf(melt_m).inputs["Emission Color"].default_value = (1.0, 0.28 + 0.2 * gl, 0.02 + 0.15 * gl, 1); bsdf(melt_m).inputs["Emission Strength"].default_value = 1.8 * h + 6.0 * gl
    bsdf(melt_m).inputs["Base Color"].default_value = (0.12, 0.04, 0.01, 1); melt.hide_render = False
    mk = track("murk", t); liq_glow.inputs["Base Color"].default_value = (0.92 + (0.18 - 0.92) * mk, 0.96 + (0.13 - 0.96) * mk, 1.0 + (0.08 - 1.0) * mk, 1)   # murky brown -> clear (no blue)
    liq_glow.inputs["Transmission Weight"].default_value = 1.0 - 0.8 * mk
    hide_all([o for o in col.objects if o.name.startswith("mould_")], track("fill", t) < 0.5)
    spn = track("spin", t); cru.rotation_euler.z = -1.1 * t * spn; crf.rotation_euler.z = cru.rotation_euler.z
    dp = track("dip", t); gr = track("grow", t); ou = track("out", t); sl = track("slab", t) > 0.5; hv = track("hot", t)
    lift = 0.035 * ease(ou); visible = (dp > 0.01) and not sl
    ibody_root.location.z = MELT_Z + lift; ibody_root.scale = (1, 1, max(0.002, gr)); ibody_root.rotation_euler.z = 1.6 * t * spn
    itop.location = (CRU.x, 0.15, MELT_Z + lift + IL * gr + 0.10 * (1 - ease(dp)) * (1 if gr < 0.01 else 0)); itop.rotation_euler.z = ibody_root.rotation_euler.z
    shoulder.scale = (max(0.05, min(1, gr * 8)),) * 2 + (max(0.05, min(1, gr * 8)),)
    hide_all([ibody] + [o for o in ibody_root.children], not visible or gr < 0.003); hide_all([shoulder], not visible or gr < 0.003); hide_all([seed, cable], not visible)
    tail.hide_render = not visible or ou < 0.05; tail.location = (CRU.x, 0.15, MELT_Z + lift - 0.014 * ease(ou)); tail.scale = (1, 1, max(0.05, ease(ou)))
    hring.hide_render = not visible or gr < 0.003; hring.location = (CRU.x, 0.15, MELT_Z + lift + 0.002)
    bsdf(hring_m).inputs["Emission Strength"].default_value = 5.0 * hv
    bsdf(ingot_m).inputs["Emission Strength"].default_value = 0.0; ing_l.location = (CRU.x, 0.15 - 0.05, MELT_Z + 0.03); ing_l.data.energy = 1.5 * hv * (0 if sl else 1)
    sn = track("snail", t); snail_root.location = (0.105 + 0.03 * sn, 0.10, 0.0); hide_all(snail_root.children_recursive, sn < 0.005 or sn > 0.999)
    hide_all([ingot_h], not sl or track("saw", t) > 0.97); hide_all([bed], track("slab", t) < 0.5 and track("wafer", t) < 0.5)
    sw = track("saw", t)
    for w_ in WIRES2: w_.hide_render = not sl or sw < 0.01 or sw > 0.99; w_.location.z = 0.07 - 0.068 * sw
    bsdf(wire_m).inputs["Emission Strength"].default_value = 2.0 * (0.6 + 0.4 * math.sin(t * 30))
    fa = track("fan", t); wv = track("wafer", t)
    for k, o in enumerate(SLICES):
        o.hide_render = not sl or sw < 0.97 or wv > 0.5; o.location.x = SAW.x + (-0.08 + k * 0.02) * (1 + 0.25 * ease(fa)); o.rotation_euler.x = math.radians(8) * ease(fa) * (1 if k % 2 else -1)
    card.hide_render = fa < 0.05 or wv > 0.5
    hide_all([wafer], wv < 0.02); wafer_root.location = SAW + Vector((0, 0, 0.004 + WR * ease(wv))); wafer_root.rotation_euler.x = math.radians(-90) * (1 - ease(wv))
    cp = track("chips", t); wmix.inputs[0].default_value = 0.85 * cp; bsdf(wafer_m).inputs["Emission Strength"].default_value = 0.25 * cp
    cs = track("case", t); co = track("caseoff", t)
    hide_all(case_root.children_recursive, cs < 0.5 or co > 0.98); case_root.location = Vector((-0.13 * ease(co), -0.02 * ease(co), 0)) + phone_root.location
    cablec.hide_render = plug.hide_render = track("charging", t) < 0.5
    hot_l.data.energy = 1.6 * track("hot2", t) * (0.85 + 0.15 * math.sin(t * 7))

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
    blink.hide_render = DUO or GOLD or int(t * 2) % 2 == 1  # the mast is hidden in Duo and gold episodes
    if GOLD: apply_gold(t, b, p)
    if SIL: apply_silicon(t, b, p)
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
if GOLD:                                                   # FIX #16: the glass tub + liquid make Cycles slow; cap bounces, no caustics
    cy = sc.cycles; cy.max_bounces = 6; cy.diffuse_bounces = 2; cy.glossy_bounces = 3; cy.transmission_bounces = 6; cy.volume_bounces = 0
    cy.transparent_max_bounces = 6; cy.caustics_reflective = False; cy.caustics_refractive = False; cy.blur_glossy = 1.0
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
