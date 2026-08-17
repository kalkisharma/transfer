/**
 * Entry point: wire the manifest, the loaders, the scene, the controls and
 * component selection together, then run the render loop.
 */

import * as THREE from 'three';

import {
  createRenderer, createScene, createCamera,
  addLighting, addGrid, frameBox, resizeToDisplay,
} from './scene.js';
import { loadManifest, loadComponents, buildSceneGraph } from './loader.js';
import { createControls, setDistanceLimits, createCameraFlight } from './controls.js';
import { createPicker } from './picking.js';
import { createTooltip } from './tooltip.js';

const MANIFEST_URL = 'data/geometry.json';

/** How strongly the selected component lifts out of the scene. */
const HIGHLIGHT_INTENSITY = 0.28;

const canvas = document.getElementById('viewport');
const statusEl = document.getElementById('status');
const summaryEl = document.getElementById('summary');
const treeEl = document.getElementById('tree');

const tooltip = createTooltip({
  element: document.getElementById('tooltip'),
  nameEl: document.getElementById('tooltip-name'),
  specsEl: document.getElementById('tooltip-specs'),
  leader: document.getElementById('leader'),
});

/** The component currently selected, or null. @type {THREE.Mesh|null} */
let selected = null;

/**
 * Show a transient line in the corner status pill.
 * @param {string} message
 * @param {boolean} [isError=false]
 */
function setStatus(message, isError = false) {
  statusEl.textContent = message;
  statusEl.classList.toggle('status--visible', Boolean(message));
  statusEl.classList.toggle('status--error', isError);
}

/**
 * Format a three.js hex colour as a CSS colour string.
 * @param {number} hex
 * @returns {string}
 */
function toCssColor(hex) {
  return `#${hex.toString(16).padStart(6, '0')}`;
}

/**
 * Turn the selection highlight on or off for one mesh.
 *
 * The lift is emissive rather than a colour change, so the component keeps its
 * own hue and the palette stays readable while something is selected.
 * @param {THREE.Mesh} mesh
 * @param {boolean} on
 */
function setHighlight(mesh, on) {
  mesh.material.emissive.setHex(on ? mesh.userData.color : 0x000000);
  mesh.material.emissiveIntensity = on ? HIGHLIGHT_INTENSITY : 0;
}

/**
 * Select a component and open its tooltip, or clear the selection.
 *
 * Passing null -- a click on empty space, or Escape -- dismisses everything.
 * Clicking the already-selected part keeps it selected and simply re-anchors
 * the tooltip to the new point.
 * @param {THREE.Mesh|null} mesh
 * @param {THREE.Vector3} [point] - world-space point that was clicked
 */
function selectComponent(mesh, point) {
  if (selected && selected !== mesh) setHighlight(selected, false);

  if (!mesh) {
    selected = null;
    tooltip.hide();
    return;
  }

  setHighlight(mesh, true);
  selected = mesh;
  tooltip.show(mesh, point);
}

/**
 * Render the component outliner as nested lists mirroring the scene graph.
 *
 * Recursion is deliberate: the manifest's flat parent field can describe any
 * depth, and a two-level assumption would break the first time it does.
 * @param {Array<object>} components - manifest entries
 * @param {Map<string, THREE.Mesh>} meshes
 */
function renderTree(components, meshes) {
  const childrenOf = new Map([[null, []]]);
  for (const entry of components) {
    const key = entry.parent ?? null;
    if (!childrenOf.has(key)) childrenOf.set(key, []);
    childrenOf.get(key).push(entry);
  }

  const buildList = (parentName) => {
    const list = document.createElement('ul');
    list.className = 'tree';

    for (const entry of childrenOf.get(parentName) ?? []) {
      const mesh = meshes.get(entry.name);
      const item = document.createElement('li');

      const row = document.createElement('div');
      row.className = 'tree__item';

      const label = document.createElement('div');
      label.className = 'tree__label';

      const swatch = document.createElement('span');
      swatch.className = 'tree__swatch';
      if (mesh) swatch.style.background = toCssColor(mesh.userData.color);

      const name = document.createElement('span');
      name.className = 'tree__name';
      name.textContent = entry.name;
      label.append(swatch, name);

      const count = document.createElement('span');
      count.className = 'tree__count';
      count.textContent = `${(mesh?.userData.triangles ?? 0).toLocaleString()} tri`;

      row.append(label, count);
      item.append(row);

      if (childrenOf.has(entry.name)) item.append(buildList(entry.name));
      list.append(item);
    }
    return list;
  };

  // Move the generated rows into the existing #tree list rather than swapping
  // the element out, so the module's node reference stays valid on a reload.
  treeEl.replaceChildren(...buildList(null).childNodes);
}

/**
 * Load the model, frame it, and start rendering.
 */
async function init() {
  const renderer = createRenderer(canvas);
  const scene = createScene();
  const camera = createCamera(canvas.clientWidth / Math.max(canvas.clientHeight, 1));
  const controls = createControls(camera, renderer.domElement);
  const flight = createCameraFlight(camera, controls);

  addLighting(scene);

  setStatus('Loading manifest');
  const manifest = await loadManifest(MANIFEST_URL);
  const { components } = manifest;

  const meshes = await loadComponents(components, (loaded, total, name) => {
    setStatus(`Loaded ${loaded}/${total} — ${name}`);
  });

  const root = buildSceneGraph(components, meshes);
  scene.add(root);

  // Bounds come from the assembled graph, so any future parent transforms are
  // already baked into the world matrices by the time we measure.
  root.updateWorldMatrix(true, true);
  const bounds = new THREE.Box3().setFromObject(root);
  addGrid(scene, bounds);

  const { position, target } = frameBox(camera, bounds);
  setDistanceLimits(controls, position.distanceTo(target));

  // Start pulled further back along the same axis so the opening move is a
  // gentle push in rather than a jump from an unrelated pose.
  camera.position.copy(target).addScaledVector(
    position.clone().sub(target).normalize(),
    position.distanceTo(target) * 1.9,
  );
  controls.target.copy(target);
  flight.flyTo(position, target, 1.4);

  renderTree(components, meshes);

  createPicker({
    camera,
    renderer,
    root,
    onPick: (hit) => selectComponent(hit?.mesh ?? null, hit?.point),
  });

  window.addEventListener('keydown', (event) => {
    if (event.key === 'Escape') selectComponent(null);
  });

  // Overall extents come pre-formatted from the manifest: the model itself is
  // in metres, and unit conversion deliberately lives only in the generator.
  const triangles = [...meshes.values()]
    .reduce((sum, mesh) => sum + mesh.userData.triangles, 0);
  summaryEl.textContent = [
    `${components.length} components`,
    `${triangles.toLocaleString()} triangles`,
    manifest.extents,
  ].filter(Boolean).join(' · ');

  setStatus('');

  const clock = new THREE.Clock();
  const animate = () => {
    requestAnimationFrame(animate);
    resizeToDisplay(renderer, camera);
    flight.update(clock.getDelta());
    controls.update();
    tooltip.update(camera, renderer);
    renderer.render(scene, camera);
  };
  animate();
}

init().catch((error) => {
  console.error(error);
  setStatus(`Failed to load: ${error.message}`, true);
});
