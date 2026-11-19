# Build brief (Claude Code)

## Hard rules (rule book v7)
- Length 60-70 s (take is 69.45; the video must not exceed 70.0). Tail after last word <= 0.5 s.
- 1080x1920, 24 fps, H.264 yuv420p, AAC. Loudness -14 LUFS (+-0.5), true peak <= -1.5 dB, LRA >= 3.
- No shot over 2.5 s except the settings card 16a (3-4 s). No logos. No pure-black or frozen frames.
- Captions in the upper 62% safe zone only; one caption system (render/pvui.py caption()). The user adds the TikTok hook text and music by hand.
- Do not change voice timings: data/timings.json is measured. Do not re-time shots; data/shots.json follows it.

## Face assets (Microsoft Rocketbox, Female_Adult_01)
Base: https://raw.githubusercontent.com/microsoft/Microsoft-Rocketbox/master/Assets/Avatars/Adults/Female_Adult_01/
- Export/Female_Adult_01_facial.fbx
- Textures: f001_body_color.tga, f001_body_normal.tga, f001_body_specular.tga, f001_head_color.tga, f001_head_normal.tga, f001_head_specular.tga, f001_opacity_color.tga
Put them in assets/ before running render/face_scene.py. Check the licence file in the repo before using the character commercially.

## face_scene.py (untested)
Blender 5.0 (bpy), Cycles CPU. Reads data/face_recipes.json (ARKit shape-key weights per expression) and data/face_clips.json (clip -> expression keyframes, 48 frames each). Outputs frames/<clip>/0000.png.. . Known risks: the shape-key multipliers are ambiguous (check one clip first), depth of field needs a focus object, mouth interior can look dark (add a small mouth light). Keep samples low (32-48 + denoise) for CPU; 9 clips x 48 frames.
Clips: bus_hope, bus_dread, kit_dread, kit_shock, kit_hope_relief, kit_soft_relief, kit_relief, kit_hope.
Fallback if the face looks wrong after two attempts: keep compose.py's 2D stand-ins and tell the user. Do not spend more than that.

## Known weak spots to look at first
1. Shots 2b, 10a, 10b use 2D plates next to a photoreal face: may read as two worlds.
2. Captions are proportional-timed (+-0.25 s against the voice).
3. Real parcel texts can also land in Unknown Senders: the script says so; do not hide it in the visuals.
