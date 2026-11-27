// src/kit/fitpose.ts  (damped version: stable on wide aerials and maps)
import * as THREE from "three";
type V3 = [number, number, number];
const W = 1080, H = 1920;
/** Aim a camera at `pos` so every point lands inside a screen window (fractions of the frame, y down).
 *  Default window = upper 62% of the frame, clear of the caption band. Returns {p, t, fov, ok}.
 *  ok = false means the points can't fit even at the 100-degree cap: move the camera back or up. */
export const fitPose = (pos: V3, points: V3[], o: { win?: [number, number, number, number]; margin?: number } = {}) => {
  const [x0, y0, x1, y1] = o.win ?? [0.08, 0.1, 0.92, 0.62];
  const margin = o.margin ?? 1.12;
  const P = new THREE.Vector3(...pos);
  const pts = points.map((p) => new THREE.Vector3(...p));
  const near = Math.min(...pts.map((p) => p.distanceTo(P)));
  const cam = new THREE.PerspectiveCamera(60, W / H, 0.01, 50000);
  cam.position.copy(P);
  const c = pts.reduce((a, p) => a.add(p), new THREE.Vector3()).divideScalar(pts.length);
  let target = P.clone().add(c.sub(P).normalize().multiplyScalar(near));
  const wx = x0 + x1 - 1, wy = 1 - (y0 + y1); // window centre in NDC
  let k = 1;
  for (let it = 0; it < 40; it++) {
    cam.lookAt(target); cam.updateProjectionMatrix(); cam.updateMatrixWorld(true);
    const n = pts.map((p) => p.clone().project(cam));
    const bx0 = Math.min(...n.map((v) => v.x)), bx1 = Math.max(...n.map((v) => v.x));
    const by0 = Math.min(...n.map((v) => v.y)), by1 = Math.max(...n.map((v) => v.y));
    // move the aim 70% of the way toward centring the points in the window
    const aim = new THREE.Vector3(0.7 * ((bx0 + bx1) / 2 - wx), 0.7 * ((by0 + by1) / 2 - wy), 0.5).unproject(cam);
    target = P.clone().add(aim.sub(P).normalize().multiplyScalar(near));
    // half a step (in log space) toward the field of view that fits
    k = Math.max((bx1 - bx0) / ((x1 - x0) * 2), (by1 - by0) / ((y1 - y0) * 2)) * margin;
    const half = Math.atan(Math.tan((cam.fov * Math.PI) / 360) * Math.sqrt(k));
    cam.fov = Math.min(100, Math.max(4, (half * 360) / Math.PI));
  }
  return { p: pos, t: target.toArray() as V3, fov: cam.fov, ok: k < 1.05 };
};
// For a straight-down shot, give the camera a different up vector (camera.up.set(0, 0, -1)) before lookAt,
// or tilt it slightly: looking exactly along the up axis makes lookAt unstable.
