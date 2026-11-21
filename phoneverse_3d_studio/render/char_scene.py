"""char_scene.py (FIX #15): character acting clips for format A, rendered with Blender 5 / bpy (Cycles CPU).
Two sets, two actors (Phoneverse Character Sheet):
  sofa : the lead ("You", Rocketbox Female_Adult_01, pink shirt) on a sofa at night, phone in both hands or at her ear.
  den  : the hooded figure (Rocketbox Male_Adult_18, hood up) seen from BEHIND at a laptop, red screen glow. Face never shown.
A clip is one beat of the beat sheet (beat key "char": <clip>); its length comes from the beat (t1 - t0). The clip's acting is in
the episode's char_clips.json (beat sheet header "chars"): expression keys, head moves, arm pose, talking, camera move.
  .venv/bin/python render/char_scene.py --beats data/beats_fix15.json --clip c04_deal --one 12    # one test frame
  .venv/bin/python render/char_scene.py --beats data/beats_fix15.json --clip c04_deal               # whole clip (resumable)
  .venv/bin/python render/char_scene.py --beats data/beats_fix15.json --test                        # middle frame of every clip
Output: build/chars/<clip>/0000.png ... (local frame index from the beat start); compose3d.py picks them up.
Arms are posed with IK (hand targets), so the hands meet the phone without hand-authored bone angles; the phone is a separate
object at the grip point. Faces use the approved expression recipes (data/face_recipes.json of the episode studio)."""
import argparse, json, math, os, random, sys
import bpy
from mathutils import Vector, Euler

ap = argparse.ArgumentParser()
ap.add_argument("--beats", required=True); ap.add_argument("--clip"); ap.add_argument("--one", type=int); ap.add_argument("--test", action="store_true")
ap.add_argument("--samples", type=int, default=14); ap.add_argument("--res", nargs=2, type=int, default=[540, 960]); ap.add_argument("--out", default="build/chars")
a = ap.parse_args(sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else None)
B = json.load(open(a.beats)); FPS = B.get("fps", 24)
CL = json.load(open(B["chars"])); R = json.load(open(CL["recipes"]))
CLIPS = {c["clip"]: c for c in CL["clips"]}
BEAT = {b["char"]: b for b in B["beats"] if b.get("char")}
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(HERE)
ease = lambda p: p * p * (3 - 2 * p)
clamp = lambda p: max(0.0, min(1.0, p))

def build(clip):
    C = CLIPS[clip]; SET = C["set"]; ACT = "lead" if SET == "sofa" else "hood"
    bpy.ops.wm.read_factory_settings(use_empty=True); sc = bpy.context.scene; col = sc.collection
    fbx = os.path.join(ROOT, "assets/Female_Adult_01_facial.fbx" if ACT == "lead" else "assets/m18/Male_Adult_18.fbx")
    tex = os.path.join(ROOT, "assets/tex" if ACT == "lead" else "assets/m18/tex")
    bpy.ops.import_scene.fbx(filepath=fbx)
    arm = next(o for o in bpy.data.objects if o.type == "ARMATURE")
    meshes = [o for o in bpy.data.objects if o.type == "MESH"]
    for img in bpy.data.images:
        p = os.path.join(tex, os.path.basename(img.filepath))
        if os.path.exists(p): img.filepath = p
        if any(s in img.filepath for s in ("_normal", "_specular")): img.colorspace_settings.name = "Non-Color"
        try: img.reload()
        except Exception: pass
    face = next((o for o in meshes if o.data.shape_keys and len(o.data.shape_keys.key_blocks) > 40), None)
    KB = face.data.shape_keys.key_blocks if face else None

    def mat(name, color, rough=0.6, metal=0.0, emit=None, strength=0.0):
        m = bpy.data.materials.new(name); m.use_nodes = True; b = m.node_tree.nodes["Principled BSDF"]
        b.inputs["Base Color"].default_value = (*color, 1); b.inputs["Roughness"].default_value = rough; b.inputs["Metallic"].default_value = metal
        if emit: b.inputs["Emission Color"].default_value = (*emit, 1); b.inputs["Emission Strength"].default_value = strength
        return m
    def box(name, dims, loc, m, rot=(0, 0, 0), bevel=0.0):
        bpy.ops.mesh.primitive_cube_add(size=1, location=loc, rotation=rot); o = bpy.context.active_object; o.name = name; o.scale = dims
        bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
        if bevel: md = o.modifiers.new("bev", "BEVEL"); md.width = bevel; md.segments = 4
        o.data.materials.append(m); return o
    def empty(name, loc):
        e = bpy.data.objects.new(name, None); col.objects.link(e); e.location = loc; return e
    def light(name, kind, loc, energy, color, size=0.5, aim=None):
        d = bpy.data.lights.new(name, kind); d.energy = energy; d.color = color
        if kind == "AREA": d.size = size
        else: d.shadow_soft_size = size
        o = bpy.data.objects.new(name, d); col.objects.link(o); o.location = loc
        if aim is not None: o.rotation_euler = (Vector(aim) - Vector(loc)).to_track_quat("-Z", "Y").to_euler()
        return o
    def emit_mat(name, color, strength):
        m = bpy.data.materials.new(name); m.use_nodes = True; nt = m.node_tree
        for nd in list(nt.nodes): nt.nodes.remove(nd)
        em = nt.nodes.new("ShaderNodeEmission"); em.inputs["Color"].default_value = (*color, 1); em.inputs["Strength"].default_value = strength
        ou = nt.nodes.new("ShaderNodeOutputMaterial"); nt.links.new(em.outputs[0], ou.inputs[0]); return m

    pb = arm.pose.bones
    head_b = pb.get("Bip01 Head"); eyes = (arm.matrix_world @ head_b.bone.head_local) + Vector((0, -0.06, 0.07))
    # ------------------------------------------------------------------ arms: analytic two-bone IK (see solve_arm). Biped bones are not
    # connected and their tails do not point at the next joint, so Blender's IK constraint aimed at the wrong point.
    tgt = {"L": [Vector(), Vector((0.5, 0.3, 0.9))], "R": [Vector(), Vector((-0.5, 0.3, 0.9))]}
    # fingers: curl into a grip (Biped finger bones bend around their local z)
    def curl(amount):
        for side in ("L", "R"):
            for f in range(5):
                for k in ("", "1", "2"):
                    b = pb.get(f"Bip01 {side} Finger{f}{k}")
                    if b: b.rotation_mode = "XYZ"; b.rotation_euler = (0, 0, math.radians((-1 if side == "L" else -1) * amount * (0.5 if f == 0 else 1.0)))
    # ------------------------------------------------------------------ sets
    W_ = bpy.data.worlds.new("w"); sc.world = W_; W_.use_nodes = True
    rnd = random.Random(5)
    phone = None; phone_scr = None
    if SET == "sofa":
        W_.node_tree.nodes["Background"].inputs[0].default_value = (0.02, 0.016, 0.03, 1)
        fabric = mat("sofa", (0.07, 0.22, 0.24), 0.9)
        box("sofa_back", (1.8, 0.28, 0.75), (0, 0.32, 0.86), fabric, bevel=0.06)
        box("cushion", (0.42, 0.14, 0.38), (0.42, 0.16, 1.16), mat("cushion", (0.55, 0.25, 0.2), 0.95), rot=(math.radians(-12), 0, math.radians(-14)), bevel=0.05)
        box("wall", (6, 0.05, 4), (0, 1.6, 1.5), mat("wall", (0.20, 0.17, 0.22), 0.95))
        # window with a blue night and a lamp-post glow; a warm floor lamp; fairy lights on a small tree (season: late Nov)
        box("window", (0.9, 0.02, 1.0), (-0.95, 1.56, 1.55), emit_mat("win", (0.10, 0.18, 0.45), 1.2))
        bpy.ops.mesh.primitive_cylinder_add(radius=0.14, depth=0.24, location=(0.95, 1.0, 1.62)); lamp = bpy.context.active_object; lamp.data.materials.append(emit_mat("shade", (1.0, 0.62, 0.3), 6))
        for i in range(70):
            bpy.ops.mesh.primitive_uv_sphere_add(radius=0.016, segments=10, ring_count=5, location=(-0.6 + rnd.uniform(-0.3, 0.3) * (1 - i / 80), 1.3 + rnd.uniform(-0.1, 0.1), 0.9 + i / 70 * 1.0))
            o = bpy.context.active_object; o.data.materials.append(emit_mat(f"fl{i}", rnd.choice([(1, 0.75, 0.3), (1, 0.4, 0.2), (0.4, 0.6, 1.0)]), 9)); o.visible_shadow = False
        light("key", "AREA", (0.9, -0.5, 1.9), 55, (1.0, 0.72, 0.45), 0.8, eyes)            # warm lamp side key
        light("rim", "AREA", (-0.8, 0.9, 1.9), 60, (0.55, 0.7, 1.0), 0.6, eyes)              # window rim
        light("fill", "AREA", (-0.4, -1.2, 1.4), 9, (0.9, 0.9, 1.0), 1.2, eyes)
        light("lamp_pt", "POINT", (0.95, 1.0, 1.62), 25, (1.0, 0.62, 0.3), 0.1)
        # the phone: graphite slab + emissive screen facing her (generic, no logo)
        phone = box("phone", (0.074, 0.008, 0.152), (0, 0, 0), mat("graphite", (0.05, 0.055, 0.065), 0.3, 0.85), bevel=0.004)
        bpy.ops.mesh.primitive_plane_add(size=1, location=(0, 0.0045, 0)); phone_scr = bpy.context.active_object
        phone_scr.scale = (0.068, 0.146, 1); phone_scr.rotation_euler = (math.radians(-90), 0, 0); bpy.ops.object.transform_apply(scale=True, rotation=True)
        phone_scr.data.materials.append(emit_mat("pscr", (0.75, 0.85, 1.0), 2.2)); phone_scr.parent = phone
        glow = light("phone_glow", "AREA", (0, 0, 0), 2.5, (0.7, 0.82, 1.0), 0.12); glow.parent = phone; glow.location = (0, 0.03, 0); glow.rotation_euler = (math.radians(-90), 0, 0)
    else:                                                                                    # den: the hooded figure from behind
        W_.node_tree.nodes["Background"].inputs[0].default_value = (0.012, 0.010, 0.02, 1)
        box("desk", (1.4, 0.7, 0.04), (0, -0.55, 0.74), mat("desk", (0.06, 0.05, 0.05), 0.6))
        box("lap_base", (0.34, 0.24, 0.018), (0, -0.48, 0.77), mat("lap", (0.05, 0.05, 0.06), 0.5, 0.4), bevel=0.004)
        box("lap_lid", (0.34, 0.012, 0.23), (0, -0.62, 0.89), mat("lap2", (0.05, 0.05, 0.06), 0.5, 0.4), rot=(math.radians(12), 0, 0), bevel=0.004)
        box("lap_scr", (0.31, 0.004, 0.2), (0, -0.613, 0.89), emit_mat("lapscr", (1.0, 0.12, 0.08), 3.0), rot=(math.radians(12), 0, 0))
        phone = box("phone", (0.074, 0.152, 0.008), (0.30, -0.42, 0.765), mat("graphite", (0.05, 0.055, 0.065), 0.3, 0.85), rot=(0, 0, math.radians(-15)), bevel=0.004)
        box("phone_scr", (0.068, 0.146, 0.001), (0.30, -0.42, 0.7695), emit_mat("pscr2", (1.0, 0.25, 0.2), 2.0), rot=(0, 0, math.radians(-15)))
        box("wall", (6, 0.05, 4), (0, -1.4, 1.5), mat("wall", (0.08, 0.07, 0.09), 0.95))
        light("lapglow", "AREA", (0, -0.6, 0.95), 30, (1.0, 0.15, 0.1), 0.35, eyes)
        light("rim", "AREA", (0.7, 0.9, 2.0), 40, (0.5, 0.6, 1.0), 0.6, eyes)
        light("kick", "AREA", (-0.9, 0.4, 1.4), 12, (0.6, 0.7, 1.0), 0.5, eyes)
        for i in range(30):                                                                   # cold blue code glow bokeh on the far wall
            bpy.ops.mesh.primitive_uv_sphere_add(radius=rnd.uniform(0.02, 0.05), segments=10, ring_count=5, location=(rnd.uniform(-1.4, 1.4), -1.35, rnd.uniform(0.9, 2.2)))
            o = bpy.context.active_object; o.data.materials.append(emit_mat(f"bk{i}", rnd.choice([(1, 0.15, 0.1), (0.3, 0.4, 1.0)]), 2)); o.visible_shadow = False
        arm.location.y += 0.05; arm.location.z -= 0.30                                                      # seated height (he faces -y, the laptop)
        box("chair", (0.5, 0.06, 0.62), (0, 0.24, 0.78), mat("chair", (0.03, 0.03, 0.035), 0.5), bevel=0.02)
        bpy.context.view_layer.update(); eyes = (arm.matrix_world @ head_b.bone.head_local) + Vector((0, -0.06, 0.07))
    # ------------------------------------------------------------------ camera
    cam = bpy.data.objects.new("cam", bpy.data.cameras.new("cam")); col.objects.link(cam); sc.camera = cam
    cam.data.sensor_fit = "VERTICAL"; cam.data.sensor_height = 36; cam.data.dof.use_dof = True; cam.data.dof.aperture_fstop = 2.4; cam.data.clip_start = 0.02
    sc.render.engine = "CYCLES"; sc.cycles.device = "CPU"; sc.cycles.samples = a.samples; sc.cycles.use_denoising = True
    sc.cycles.max_bounces = 6; sc.cycles.transparent_max_bounces = 12; sc.render.resolution_x, sc.render.resolution_y = a.res
    sc.view_settings.view_transform = "AgX"; sc.view_settings.look = "AgX - Medium High Contrast"
    return dict(C=C, SET=SET, sc=sc, arm=arm, KB=KB, face=face, tgt=tgt, curl=curl, cam=cam, eyes=eyes, phone=phone, phone_scr=phone_scr)

# ------------------------------------------------------------------ acting (all keyed as functions of clip time, frame-independent)
def key(KB, token):
    if token.startswith("AU_"): return [k for k in KB if k.name.startswith(token + "_") and not k.name[len(token) + 1:].startswith(("L_", "R_"))][:1]
    if token.startswith("AK_"): return [k for k in KB if k.name.startswith(token + "_")][:1]
    low = token.lower(); return [k for k in KB if k.name.startswith("AK_") and k.name.lower().split("_", 2)[-1] == low][:1]
def expr_vals(KB, expr, w):
    if expr in ("neutral", None) or w <= 0: return {}
    mult = R["mult"].get(expr, R["mult"]["default"]); out = {}
    for tok, v in R["expressions"][expr]["keys"].items():
        for k in key(KB, tok): out[k.name] = v * mult * w
    return out
def interp(track, t, default):
    """track: [[t, value], ...] -> eased value at t (values: numbers or lists)."""
    if not track: return default
    if t <= track[0][0]: return track[0][1]
    for (t0, v0), (t1, v1) in zip(track, track[1:]):
        if t0 <= t <= t1:
            k = ease((t - t0) / max(1e-3, t1 - t0))
            return [x + (y - x) * k for x, y in zip(v0, v1)] if isinstance(v0, list) else v0 + (v1 - v0) * k
    return track[-1][1]
POSES = {   # fingers/across: hand directions per side (world); pole: elbow hint relative to the eyes
   # hand targets (world), relative to the actor's eye point; "rotL/rotR" hand rotations (deg) when copy-rotation is on
    "phone":     {"L": (0.055, -0.30, -0.44), "R": (-0.055, -0.30, -0.44), "phone": ((0, -0.31, -0.40), (58, 0, 0)), "curl": 55,
                  "fL": (-0.6, -0.5, 0.6), "aL": (0, 0.85, -0.53), "fR": (0.6, -0.5, 0.6), "aR": (0, 0.85, -0.53), "pL": (0.45, 0.2, -0.75), "pR": (-0.45, 0.2, -0.75)},
    "phone_up":  {"L": (0.055, -0.33, -0.32), "R": (-0.055, -0.33, -0.32), "phone": ((0, -0.34, -0.28), (75, 0, 0)), "curl": 55,
                  "fL": (-0.6, -0.3, 0.75), "aL": (0, 0.97, -0.26), "fR": (0.6, -0.3, 0.75), "aR": (0, 0.97, -0.26), "pL": (0.45, 0.2, -0.75), "pR": (-0.45, 0.2, -0.75)},
    "call":      {"L": (0.16, -0.12, -0.70), "R": (-0.09, -0.03, -0.12), "phone": ((-0.078, -0.02, -0.03), (8, 0, -84)), "curl": 85,
                  "fL": (0, -0.4, -1), "aL": (0, 1, 0), "fR": (0.25, -0.15, 1), "aR": (0, 1, 0), "pL": (0.4, 0.1, -0.9), "pR": (-0.35, -0.25, -0.9)},
    "type":      {"L": (0.13, -0.33, -0.56), "R": (-0.13, -0.33, -0.56), "phone": None, "curl": 30,
                  "fL": (-0.15, -1, -0.35), "aL": (1, 0, 0), "fR": (0.15, -1, -0.35), "aR": (-1, 0, 0), "pL": (0.5, 0.3, -0.8), "pR": (-0.5, 0.3, -0.8)},
}
def solve_arm(arm, side, target, pole):
    """Two-bone IK on joint positions (UpperArm head = shoulder, Forearm head = elbow, Hand head = wrist), world space targets.
    The elbow goes towards 'pole' (out, back and down for a natural hold)."""
    from mathutils import Matrix
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
        M = Matrix.Translation(pivot) @ q.to_matrix().to_4x4() @ Matrix.Translation(-pivot); b.matrix = M @ b.matrix
    rot_about(ua, Sh, (El - Sh).rotation_difference(E2 - Sh)); bpy.context.view_layer.update()
    El, Wr = fa.head.copy(), hd.head.copy(); rot_about(fa, El, (Wr - El).rotation_difference(T - El)); bpy.context.view_layer.update()

def orient_hand(arm, side, fingers, across):
    """Turn the hand about the wrist so the middle finger points along 'fingers' and the knuckle line (index -> pinky)
    runs along 'across' (both world directions)."""
    from mathutils import Matrix
    pb = arm.pose.bones; hd = pb[f"Bip01 {side} Hand"]; mw = arm.matrix_world; R3 = mw.to_3x3().normalized()
    W = mw @ hd.head; f = (mw @ pb[f"Bip01 {side} Finger2"].head - W).normalized(); k = (mw @ pb[f"Bip01 {side} Finger4"].head - mw @ pb[f"Bip01 {side} Finger1"].head)
    def frame(f_, a_):
        f_ = Vector(f_).normalized(); a_ = (Vector(a_) - Vector(a_).dot(f_) * f_).normalized(); return Matrix((f_, a_, f_.cross(a_))).transposed()
    Rw = frame(fingers, across) @ frame(f, k).inverted()                  # world rotation
    Ra = (R3.inverted() @ Rw @ R3).to_4x4(); piv = hd.head.copy()          # same rotation in armature space
    hd.matrix = Matrix.Translation(piv) @ Ra @ Matrix.Translation(-piv) @ hd.matrix; bpy.context.view_layer.update()

def act(S, t):
    C, KB, arm = S["C"], S["KB"], S["arm"]; E = S["eyes"]
    # pose blend: C["pose"] is either a name or [[t, name], ...] with 0.35 s blends
    seq = C["pose"] if isinstance(C["pose"], list) else [[0, C["pose"]]]
    cur = seq[0][1]; prev = cur; blend = 1.0
    for i, (ts, nm) in enumerate(seq):
        if t >= ts: prev = seq[i - 1][1] if i else nm; cur = nm; blend = clamp((t - ts) / 0.35) if i else 1.0
    P0, P1 = POSES[prev], POSES[cur]; k = ease(blend)
    off = Vector(C.get("hand_off", (0, 0, 0)))
    for side in ("L", "R"):
        p = Vector(P0[side]).lerp(Vector(P1[side]), k) + off
        if cur == "type": p += Vector((0.0, 0.012 * math.sin(t * (23 if side == "L" else 19)), 0.01 * max(0, math.sin(t * (17 if side == "L" else 21)))))
        S["tgt"][side][0] = E + p
        S["tgt"][side][1] = E + Vector(P0["p" + side]).lerp(Vector(P1["p" + side]), k)
        S["tgt"][side].append(None) if len(S["tgt"][side]) < 3 else None
        S["tgt"][side][2] = (Vector(P0["f" + side]).lerp(Vector(P1["f" + side]), k), Vector(P0["a" + side]).lerp(Vector(P1["a" + side]), k))
    S["curl"](P0["curl"] + (P1["curl"] - P0["curl"]) * k)
    if S["phone"] is not None and C["set"] == "sofa":
        ph0, ph1 = P0["phone"], P1["phone"]
        loc = Vector(ph0[0]).lerp(Vector(ph1[0]), k) + off; rot = [x + (y - x) * k for x, y in zip(ph0[1], ph1[1])]
        if C.get("phone_bob"): loc.z += 0.006 * math.sin(t * 5)
        S["phone"].location = E + loc; S["phone"].rotation_euler = Euler([math.radians(v) for v in rot])
    # head / neck / spine (degrees, Biped: z positive = looking down, y = turn, x = tilt)
    hd = interp(C.get("head"), t, [0, 0, 0]); nk = [v * 0.5 for v in hd]
    if C.get("shake") and C["shake"][0] <= t <= C["shake"][1]:
        u = (t - C["shake"][0]) / (C["shake"][1] - C["shake"][0]); hd = [hd[0], hd[1] + 14 * math.sin(u * math.pi * 4) * math.sin(u * math.pi), hd[2]]
    if C.get("nod") and C["nod"][0] <= t <= C["nod"][1]:
        u = (t - C["nod"][0]) / (C["nod"][1] - C["nod"][0]); hd = [hd[0], hd[1], hd[2] + 7 * math.sin(u * math.pi * 4) * math.sin(u * math.pi)]
    for bn, v in (("Bip01 Head", hd), ("Bip01 Neck", nk), ("Bip01 Spine2", interp(C.get("spine"), t, [0, 0, 0]))):
        b = arm.pose.bones.get(bn)
        if b: b.rotation_mode = "XYZ"; b.rotation_euler = [math.radians(x) for x in v]
    bpy.context.view_layer.update()
    for side in ("L", "R"): solve_arm(arm, side, S["tgt"][side][0], S["tgt"][side][1]); orient_hand(arm, side, *S["tgt"][side][2])
    if KB is None: return
    # face: expression track [[t, expr, w], ...]; between keys cross-fade over 0.25 s with a small overshoot on the snap
    ex = C.get("expr", [[0, "neutral", 0]]); vals = {}
    i = max(j for j, e in enumerate(ex) if e[0] <= t) if t >= ex[0][0] else 0
    a_, b_ = ex[max(0, i - 1)], ex[i]; u = clamp((t - b_[0]) / 0.25) if i else 1.0
    over = 1 + 0.12 * math.sin(math.pi * clamp((t - b_[0]) / 0.5)) if i and b_[1] in ("shock", "hope") else 1.0
    for n, v in expr_vals(KB, a_[1], a_[2] * (1 - ease(u))).items(): vals[n] = vals.get(n, 0) + v
    for n, v in expr_vals(KB, b_[1], b_[2] * ease(u) * over).items(): vals[n] = vals.get(n, 0) + v
    look = interp(C.get("look_down"), t, 0.0)                                                   # eyes on the phone
    for tok in ("eyeLookDownLeft", "eyeLookDownRight"):
        for kk in key(KB, tok): vals[kk.name] = vals.get(kk.name, 0) + look
    if C.get("talk"):                                                                            # reading the code out: jaw flaps per syllable
        for t0, t1 in C["talk"]:
            if t0 <= t <= t1:
                s = abs(math.sin(t * 15.0)) * (0.55 + 0.45 * math.sin(t * 3.7)) * 0.42
                for tok, w in (("jawOpen", 1.0), ("mouthFunnel", 0.25), ("mouthLowerDownLeft", 0.4), ("mouthLowerDownRight", 0.4)):
                    for kk in key(KB, tok): vals[kk.name] = vals.get(kk.name, 0) + s * w
    blink = 1.0 if ((t + 1.4) % 3.1) < 0.12 else 0.0                                            # a blink every ~3 s, never on a clip's first frames
    for tok in ("eyeBlinkLeft", "eyeBlinkRight"):
        for kk in key(KB, tok): vals[kk.name] = max(vals.get(kk.name, 0), blink)
    for k in KB:
        if k.name.startswith(("AK_", "AU_")): k.value = min(1.7, vals.get(k.name, 0.0))

def camera(S, t, dur):
    C, cam, E = S["C"], S["cam"], S["eyes"]; cm = C["cam"]; p = ease(clamp(t / max(1e-3, dur)))
    A = Vector(cm["from"][0]); Bv = Vector(cm["to"][0]); At = Vector(cm["from"][1]); Bt = Vector(cm["to"][1])
    loc = E + A.lerp(Bv, p); tg = E + At.lerp(Bt, p); cam.location = loc; cam.rotation_euler = (tg - loc).to_track_quat("-Z", "Y").to_euler()
    cam.data.lens = cm["from"][2] + (cm["to"][2] - cm["from"][2]) * p
    if cm.get("roll"): cam.rotation_euler.rotate_axis("Z", math.radians(cm["roll"]))
    cam.data.dof.focus_distance = (E + Vector(cm.get("focus", (0, 0, 0))) - loc).length

def render(clip, frames):
    S = build(clip); b = BEAT[clip]; n = int(round((b["t1"] - b["t0"]) * FPS)); dur = n / FPS
    od = os.path.join(a.out, clip); os.makedirs(od, exist_ok=True)
    for f in frames(n):
        p = os.path.join(od, f"{f:04d}.png")
        if os.path.exists(p): continue
        t = f / FPS; act(S, t); camera(S, t, dur); bpy.context.view_layer.update()
        S["sc"].render.filepath = os.path.abspath(p); bpy.ops.render.render(write_still=True); print("rendered", p, flush=True)

if a.test:
    for c in BEAT: render(c, lambda n: [n // 2])
elif a.one is not None: render(a.clip, lambda n: [a.one])
else: render(a.clip, lambda n: range(n))
