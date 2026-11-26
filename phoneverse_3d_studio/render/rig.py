"""rig.py: shared helpers for the "Cheers, Biscuit" scenes after the street (flat_scene.py): materials and primitives,
Rocketbox characters (load, mocap retarget by orientation, two-bone IK, look-at without roll), faces (ARKit + FACS + visemes).
Copied from street_scene.py (which keeps its own copy, so the rendered street stays byte-identical).
Importing this module resets Blender to an empty scene."""
import argparse, json, math, os, random, sys, time
import bpy
from mathutils import Vector, Matrix, Euler, Quaternion

HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(HERE)
EP = os.path.join(ROOT, "..", "drafts", "phoneverse-found-text", "audio", "out")
FPS = 24
VIS = json.load(open(os.path.join(EP, "visemes.json")))
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

PREV = {}; T_NOW = 0.0
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
