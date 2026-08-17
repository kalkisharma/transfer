/**
 * Scene setup: renderer, camera, lighting, ground grid and view framing.
 *
 * This module owns everything that describes *how the world is drawn*.  It
 * knows nothing about STL files or user input.
 */

import * as THREE from 'three';

const BACKGROUND = 0x101215;
const GRID_LINE = 0x2a2f37;
const GRID_SUBLINE = 0x1c2027;
const FOV = 42;

/**
 * Create a renderer bound to an existing canvas.
 * @param {HTMLCanvasElement} canvas
 * @returns {THREE.WebGLRenderer}
 */
export function createRenderer(canvas) {
  const renderer = new THREE.WebGLRenderer({ canvas, antialias: true });
  // Cap the device pixel ratio: past 2x the extra fragments buy nothing
  // visible but cost a lot on high-DPI laptops.
  renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
  renderer.setSize(canvas.clientWidth, canvas.clientHeight, false);
  return renderer;
}

/**
 * Create the scene with its background colour.
 * @returns {THREE.Scene}
 */
export function createScene() {
  const scene = new THREE.Scene();
  scene.background = new THREE.Color(BACKGROUND);
  return scene;
}

/**
 * Create the perspective camera. Near/far are placeholders until the model
 * bounds are known -- see frameBox().
 * @param {number} aspect
 * @returns {THREE.PerspectiveCamera}
 */
export function createCamera(aspect) {
  return new THREE.PerspectiveCamera(FOV, aspect, 0.1, 1000);
}

/**
 * Add neutral three-point lighting: key, fill, rim, plus a soft ambient wash.
 *
 * All lights are white on purpose. Tinted lighting reads as "product render";
 * a CAD tool wants the surface colour to be the only colour.
 * @param {THREE.Scene} scene
 */
export function addLighting(scene) {
  const ambient = new THREE.HemisphereLight(0xffffff, 0x30343a, 0.7);

  const key = new THREE.DirectionalLight(0xffffff, 2.4);
  key.position.set(1, 1.4, 1.1);

  const fill = new THREE.DirectionalLight(0xffffff, 0.9);
  fill.position.set(-1.2, 0.4, 0.8);

  const rim = new THREE.DirectionalLight(0xffffff, 1.3);
  rim.position.set(-0.4, 0.7, -1.4);

  scene.add(ambient, key, fill, rim);
}

/**
 * Add a ground grid sized to the model and sunk to the bottom of its bounds.
 * @param {THREE.Scene} scene
 * @param {THREE.Box3} box - bounds of all loaded geometry
 * @returns {THREE.GridHelper}
 */
export function addGrid(scene, box) {
  const size = box.getSize(new THREE.Vector3());
  const center = box.getCenter(new THREE.Vector3());
  const extent = Math.max(size.x, size.z, 1) * 2;
  const divisions = 20;

  const grid = new THREE.GridHelper(extent, divisions, GRID_LINE, GRID_SUBLINE);
  grid.position.set(center.x, box.min.y - size.y * 0.35, center.z);
  grid.material.transparent = true;
  grid.material.opacity = 0.45;
  scene.add(grid);
  return grid;
}

/**
 * Work out the camera pose that frames a bounding box, and retune the clip
 * planes to suit the model's scale.
 *
 * Returns the pose rather than applying it, so the caller can either snap to
 * it or ease into it.
 * @param {THREE.PerspectiveCamera} camera
 * @param {THREE.Box3} box
 * @param {number} [margin=1.35] - fraction of extra room around the model
 * @returns {{position: THREE.Vector3, target: THREE.Vector3}}
 */
export function frameBox(camera, box, margin = 1.35) {
  const size = box.getSize(new THREE.Vector3());
  const target = box.getCenter(new THREE.Vector3());

  const maxExtent = Math.max(size.x, size.y, size.z);
  let distance = (maxExtent / 2) / Math.tan((FOV / 2) * THREE.MathUtils.DEG2RAD);
  // A portrait viewport is limited by horizontal FOV, not vertical.
  if (camera.aspect < 1) distance /= camera.aspect;
  distance *= margin;

  camera.near = Math.max(distance / 500, 0.01);
  camera.far = distance * 100;
  camera.updateProjectionMatrix();

  // Three-quarter view from above and off the port side: the standard way a
  // CAD tool opens a part, and it reads depth better than an axis-aligned one.
  const direction = new THREE.Vector3(1, 0.62, 0.85).normalize();
  const position = target.clone().addScaledVector(direction, distance);
  return { position, target };
}

/**
 * Resize the renderer and camera to the canvas's current CSS size.
 * @param {THREE.WebGLRenderer} renderer
 * @param {THREE.PerspectiveCamera} camera
 */
export function resizeToDisplay(renderer, camera) {
  const canvas = renderer.domElement;
  const width = canvas.clientWidth;
  const height = canvas.clientHeight;
  if (canvas.width === width && canvas.height === height) return;

  renderer.setSize(width, height, false);
  camera.aspect = width / Math.max(height, 1);
  camera.updateProjectionMatrix();
}
