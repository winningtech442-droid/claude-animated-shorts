"""face_scene.py: renders ONE face clip for FIX #12 with Blender 5.0 as a Python module (bpy).
Setup (once):   uv venv -p 3.11 .venv && uv pip install -p .venv bpy pillow numpy      (never name a script inspect.py: it breaks bpy)
Assets (once):  Rocketbox Female_Adult_01 facial export + textures in assets/ and assets/tex/ (see BUILD_BRIEF.md).
  .venv/bin/python render/face_scene.py --clip kit_shock --frames 20 20 --out frames/kit_shock      # one test frame
  .venv/bin/python render/face_scene.py --clip kit_shock --frames 0 47 --out frames/kit_shock       # resumable
Steps: import FBX -> textures (already wired in the FBX; we fix colour spaces) -> pose -> key shape keys per data/face_recipes.json
-> camera aimed at the eyes (focus OBJECT on the eye line) -> render PNGs.
Fixes after the first run (v2):
 - key(): ARKit tokens resolve ONLY to the AK_nn_* key (the old suffix match also hit SR_* keys, doubling smiles); AU_nn resolves to the
   bilateral key only (the old prefix match also hit AU_nn_L and AU_nn_R, tripling it).
 - every recipe key is keyed at every keyframe (keys not in the current expression go to 0) so the previous look does not leak.
 - camera / focus aimed at the eye line found from the blink shape keys (the Head bone sits at the skull base, ~9 cm too low).
 - mouth light: the recipe 'mouth_light_w' is used as watts * 6 (0.4 -> 2.4 W point, 0.08 -> 0.5 W) placed 2.5 cm behind the lips;
   the old w*1000/4 gave 100 W and blew out the mouth.
 - a dim world colour per set, so the background is never pure black."""
import argparse, json, math, os, random, sys
import bpy
from mathutils import Vector

ap = argparse.ArgumentParser()
ap.add_argument("--clip", required=True); ap.add_argument("--frames", nargs=2, type=int, default=[0, 47]); ap.add_argument("--out", required=True)
ap.add_argument("--fbx", default="assets/Female_Adult_01_facial.fbx"); ap.add_argument("--tex", default="assets/tex")
ap.add_argument("--samples", type=int, default=14); ap.add_argument("--res", nargs=2, type=int, default=[712, 1267])
a = ap.parse_args(sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else None)
R = json.load(open("data/face_recipes.json")); C = {c["clip"]: c for c in json.load(open("data/face_clips.json"))["clips"]}[a.clip]
SET = C["set"]; EXPRS = {"hope -> relief": ["hope", "relief"]}.get(C["expr"], [C["expr"]])

bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.fbx(filepath=a.fbx)
arm = next(o for o in bpy.data.objects if o.type == "ARMATURE")
meshes = [o for o in bpy.data.objects if o.type == "MESH"]
face = next(o for o in meshes if o.data.shape_keys and len(o.data.shape_keys.key_blocks) > 40)
KB = face.data.shape_keys.key_blocks

def key(token):
    """Recipe token -> shape key(s). ARKit name -> AK_nn_<Name> only. AU_nn -> the bilateral AU_nn_<Name> only (not _L/_R)."""
    low = token.lower()
    if token.startswith("AU_"):
        return [k for k in KB if k.name.startswith(token + "_") and not k.name[len(token) + 1:].startswith(("L_", "R_"))][:1]
    if token.startswith("AK_"):
        return [k for k in KB if k.name.startswith(token + "_")][:1]
    return [k for k in KB if k.name.startswith("AK_") and k.name.lower().split("_", 2)[-1] == low][:1]

missing = sorted({t for e in R["expressions"].values() for t in e["keys"] if not key(t)})
if missing: print("WARNING unresolved recipe keys:", missing, flush=True)

# --- landmarks from shape-key deltas (world space)
def centre(name):
    k, B = KB[name], KB["Basis"]
    pts = [face.matrix_world @ B.data[i].co for i in range(len(B.data)) if (k.data[i].co - B.data[i].co).length > 1e-3]
    return sum(pts, Vector()) / len(pts)
eyes = (centre("AK_09_EyeBlinkLeft") + centre("AK_10_EyeBlinkRight")) / 2
mouth = centre("AK_25_JawOpen")

# --- textures: the FBX already links color/normal/specular; make sure every image is loaded with the right colour space
for img in bpy.data.images:
    p = os.path.join(a.tex, os.path.basename(img.filepath))
    if os.path.exists(p): img.filepath = p
    if any(s in img.filepath for s in ("_normal", "_specular")): img.colorspace_settings.name = "Non-Color"
    try: img.reload()
    except Exception: pass

# --- animation
sc = bpy.context.scene; sc.render.fps = 24; sc.frame_start, sc.frame_end = 0, 47
ALL = sorted({k.name for e in R["expressions"].values() for t in e["keys"] for k in key(t)} | {k.name for t in ("eyeLookDownLeft", "eyeLookDownRight", "mouthSmileLeft", "mouthSmileRight") for k in key(t)})
def pose(bone, rot_deg, frame):
    pb = arm.pose.bones.get(bone)
    if pb: pb.rotation_mode = "XYZ"; pb.rotation_euler = [math.radians(v) for v in rot_deg]; pb.keyframe_insert("rotation_euler", frame=frame)
def setvals(vals, frame):
    for n in ALL: KB[n].value = min(1.7, vals.get(n, 0.0)); KB[n].keyframe_insert("value", frame=frame)
def expr_vals(expr, w):
    mult = R["mult"].get(expr, R["mult"]["default"]); out = {}
    for tok, v in R["expressions"][expr]["keys"].items():
        for k in key(tok): out[k.name] = v * mult * w
    return out
start = {"neutral": {}, "look down at phone": {"AK_11_EyeLookDownLeft": 0.55, "AK_12_EyeLookDownRight": 0.55, "AK_44_MouthSmileLeft": 0.15, "AK_45_MouthSmileRight": 0.15}}
s0 = start.get(C.get("from"), None)
if s0 is None: s0 = expr_vals(C["from"], 1.0) if C.get("from") in R["expressions"] else {}
setvals(s0, 0)
for bone in ("Bip01 Head", "Bip01 Neck", "Bip01 Spine2"): pose(bone, (0, 0, 0), 0)
snap = 10 if EXPRS[0] == "shock" else R["timing"]["snap_frame"][0]
for i, ex in enumerate(EXPRS):
    f0 = snap + i * 12; last = i == len(EXPRS) - 1
    setvals(expr_vals(ex, 0.55), f0 + 4); setvals(expr_vals(ex, 1.12), f0 + 8); setvals(expr_vals(ex, 1.0), f0 + 14)
    if last: setvals(expr_vals(ex, 1.0), 47)
    r = R["expressions"][ex]
    for bone, name in (("Bip01 Head", "head"), ("Bip01 Neck", "neck"), ("Bip01 Spine2", "spine2")):
        pose(bone, r.get(name, (0, 0, 0)), f0 + 8)
    if ex == "shock": pose("Bip01 Head", r["head_settle"], f0 + 16)

# --- camera: 70 mm, f/2, push-in 1.0 m -> 0.88 m, focus OBJECT on the eye line
aim = eyes + Vector((0, 0, -0.035))                 # between eyes and mouth, slightly above centre
foc = bpy.data.objects.new("focus", None); sc.collection.objects.link(foc); foc.location = eyes + Vector((0, -0.01, 0))
head_pb = arm.pose.bones.get("Bip01 Head")
if head_pb:                                          # focus follows the head when it nods
    c = foc.constraints.new("CHILD_OF"); c.target = arm; c.subtarget = "Bip01 Head"
    sc.frame_set(0); c.inverse_matrix = (arm.matrix_world @ head_pb.matrix).inverted()
cam = bpy.data.objects.new("cam", bpy.data.cameras.new("cam")); sc.collection.objects.link(cam); sc.camera = cam
cam.data.lens = 70; cam.data.sensor_fit = "VERTICAL"; cam.data.sensor_height = 36
cam.data.dof.use_dof = True; cam.data.dof.focus_object = foc; cam.data.dof.aperture_fstop = 2.0
for f, d in ((0, 1.0), (47, 0.88)):
    cam.location = aim + Vector((0.06, -d, 0.03)); direction = aim - cam.location
    cam.rotation_euler = direction.to_track_quat("-Z", "Y").to_euler(); cam.keyframe_insert("location", frame=f); cam.keyframe_insert("rotation_euler", frame=f)

# --- lights and background (data/face_clips.json background_sets)
def light(kind, loc, energy, color=(1, 1, 1), size=0.6):
    d = bpy.data.lights.new(kind, "AREA" if kind != "mouth" else "POINT"); d.energy = energy; d.color = color
    if kind != "mouth": d.size = size
    else: d.shadow_soft_size = 0.005
    o = bpy.data.objects.new(kind, d); sc.collection.objects.link(o); o.location = loc
    if kind != "mouth":
        o.rotation_euler = (aim - Vector(loc)).to_track_quat("-Z", "Y").to_euler()
    return o
warm, cool = (1.0, 0.72, 0.45), (0.55, 0.7, 1.0)
if SET == "kitchen":
    light("key", aim + Vector((-0.7, -0.8, 0.35)), 110, warm, 0.7); light("rim", aim + Vector((0.6, 0.7, 0.25)), 80, cool, 0.5); light("fill", aim + Vector((0.5, -0.9, 0.0)), 18, (1, 0.95, 0.9), 1.2)
else:
    light("key", aim + Vector((0.0, -0.6, -0.25)), 9, (0.75, 0.85, 1.0), 0.25)     # phone-screen glow from below
    light("rim", aim + Vector((-0.6, 0.6, 0.3)), 90, warm, 0.5); light("fill", aim + Vector((0.5, -0.9, 0.2)), 10, cool, 1.2); light("street", aim + Vector((0.9, -0.2, 0.2)), 40, warm, 0.3)
world = bpy.data.worlds.new("w"); sc.world = world; world.use_nodes = True
world.node_tree.nodes["Background"].inputs[0].default_value = ((0.035, 0.022, 0.016, 1) if SET == "kitchen" else (0.010, 0.014, 0.032, 1))
random.seed(7 if SET == "bus" else 9)
n = 90 if SET == "bus" else 14
for i in range(n):                                   # emissive bokeh: moving amber street lights on the bus, a few practicals in the kitchen
    bpy.ops.mesh.primitive_uv_sphere_add(radius=random.uniform(0.04, 0.10) * (1 if SET == "bus" else 1.8), segments=12, ring_count=6,
        location=(aim.x + random.uniform(-1.6, 1.6), aim.y + random.uniform(1.8, 3.2), aim.z + random.uniform(-0.6, 0.9)))
    o = bpy.context.active_object; m = bpy.data.materials.new(f"bk{i}"); m.use_nodes = True; nt = m.node_tree
    for nd in list(nt.nodes): nt.nodes.remove(nd)
    em = nt.nodes.new("ShaderNodeEmission"); em.inputs["Color"].default_value = (*random.choice([warm, (1, 0.85, 0.6), cool]), 1); em.inputs["Strength"].default_value = random.uniform(0.8, 1.8)
    out = nt.nodes.new("ShaderNodeOutputMaterial"); nt.links.new(em.outputs[0], out.inputs[0]); o.data.materials.append(m)
    o.visible_shadow = False; o.visible_diffuse = False                     # bokeh only to camera, does not light the face
    if SET == "bus": o.keyframe_insert("location", frame=0); o.location.x += 1.6; o.keyframe_insert("location", frame=47)
w = max(R["expressions"][e].get("mouth_light_w", 0.0) for e in EXPRS)
if w > 0:
    ml = light("mouth", mouth + Vector((0, 0.025, -0.004)), w * 6, (1, 0.8, 0.6))
    if arm.pose.bones.get("Bip01 MJaw"):
        jb = arm.pose.bones["Bip01 MJaw"]; c = ml.constraints.new("CHILD_OF"); c.target = arm; c.subtarget = "Bip01 MJaw"
        sc.frame_set(0); c.inverse_matrix = (arm.matrix_world @ jb.matrix).inverted()

# --- render
sc.render.engine = "CYCLES"; sc.cycles.device = "CPU"; sc.cycles.samples = a.samples; sc.cycles.use_denoising = True
sc.cycles.max_bounces = 6; sc.cycles.transparent_max_bounces = 12
sc.render.resolution_x, sc.render.resolution_y = a.res; sc.render.film_transparent = False
sc.view_settings.view_transform = "AgX"; sc.view_settings.look = "AgX - Medium High Contrast"
os.makedirs(a.out, exist_ok=True)
for f in range(a.frames[0], a.frames[1] + 1):
    p = os.path.join(a.out, f"{f:04d}.png")
    if os.path.exists(p): continue                    # resumable
    sc.frame_set(f); sc.render.filepath = os.path.abspath(p); bpy.ops.render.render(write_still=True); print("rendered", p, flush=True)
