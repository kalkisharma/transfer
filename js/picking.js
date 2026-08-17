/**
 * Pointer hit-testing against the component graph.
 *
 * This module answers one question -- "what did the user click, if anything?"
 * -- and knows nothing about selection state or how it is presented.
 */

import * as THREE from 'three';

/**
 * How far the pointer may travel between press and release and still count as
 * a click. Without a threshold, every orbit that happens to end over a surface
 * would register as a selection.
 */
const CLICK_SLOP_PX = 5;

/**
 * Wire up click and hover picking on the renderer's canvas.
 *
 * @param {object} options
 * @param {THREE.Camera} options.camera
 * @param {THREE.WebGLRenderer} options.renderer
 * @param {THREE.Object3D} options.root - the assembly whose parts are pickable
 * @param {(hit: {mesh: THREE.Mesh, point: THREE.Vector3}|null) => void}
 *   options.onPick - called with the nearest hit, or null for a miss
 * @returns {{dispose: Function}}
 */
export function createPicker({ camera, renderer, root, onPick }) {
  const canvas = renderer.domElement;
  const raycaster = new THREE.Raycaster();
  const ndc = new THREE.Vector2();

  const pressedAt = { x: 0, y: 0 };
  let pressed = false;
  let hoverEvent = null;
  let hoverQueued = false;

  /**
   * Convert a pointer event to normalised device coordinates.
   * @param {PointerEvent} event
   */
  const toNdc = (event) => {
    const rect = canvas.getBoundingClientRect();
    ndc.x = ((event.clientX - rect.left) / rect.width) * 2 - 1;
    ndc.y = -((event.clientY - rect.top) / rect.height) * 2 + 1;
  };

  /**
   * Return the nearest component under the pointer, or null.
   *
   * Traversal is recursive so picking keeps working once the manifest nests
   * components; the grid and lights are not in `root`, so they cannot be hit.
   * @param {PointerEvent} event
   * @returns {{mesh: THREE.Mesh, point: THREE.Vector3}|null}
   */
  const pick = (event) => {
    toNdc(event);
    raycaster.setFromCamera(ndc, camera);
    const hit = raycaster.intersectObjects(root.children, true)[0];
    if (!hit || !hit.object.userData.component) return null;
    return { mesh: hit.object, point: hit.point };
  };

  const onPointerDown = (event) => {
    if (event.button !== 0) return;
    pressed = true;
    pressedAt.x = event.clientX;
    pressedAt.y = event.clientY;
  };

  const onPointerUp = (event) => {
    if (!pressed || event.button !== 0) return;
    pressed = false;

    const travelled = Math.hypot(
      event.clientX - pressedAt.x, event.clientY - pressedAt.y);
    if (travelled > CLICK_SLOP_PX) return;

    onPick(pick(event));
  };

  // Hovering raycasts too, but at most once per frame: pointermove can fire
  // far more often than the display refreshes.
  const onPointerMove = (event) => {
    hoverEvent = event;
    if (hoverQueued) return;
    hoverQueued = true;
    requestAnimationFrame(() => {
      hoverQueued = false;
      if (!hoverEvent || pressed) return;
      canvas.style.cursor = pick(hoverEvent) ? 'pointer' : '';
    });
  };

  const onPointerLeave = () => {
    pressed = false;
    hoverEvent = null;
    canvas.style.cursor = '';
  };

  canvas.addEventListener('pointerdown', onPointerDown);
  canvas.addEventListener('pointerup', onPointerUp);
  canvas.addEventListener('pointermove', onPointerMove);
  canvas.addEventListener('pointerleave', onPointerLeave);

  return {
    /** Remove every listener this picker installed. */
    dispose() {
      canvas.removeEventListener('pointerdown', onPointerDown);
      canvas.removeEventListener('pointerup', onPointerUp);
      canvas.removeEventListener('pointermove', onPointerMove);
      canvas.removeEventListener('pointerleave', onPointerLeave);
      canvas.style.cursor = '';
    },
  };
}
