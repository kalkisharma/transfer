/**
 * Manifest and STL loading, plus assembly of the component scene graph.
 *
 * The manifest (data/geometry.json) is the only place filenames live. This
 * module turns it into meshes and a parent/child hierarchy.
 */

import * as THREE from 'three';
import { STLLoader } from 'three/addons/loaders/STLLoader.js';

const SURFACE = {
  roughness: 0.55,
  metalness: 0.12,
  flatShading: false,
};

/**
 * Per-component colours: muted, near-equal in lightness so no single part
 * shouts, and desaturated enough to sit inside the dark UI rather than fight
 * it. Assigned by manifest order, wrapping past the twelfth component.
 */
const PALETTE = [
  0x6f93b8, // steel blue
  0x5f9490, // slate teal
  0x8aa06a, // sage
  0xc0a25c, // ochre
  0xbe8460, // clay
  0x9a7fa8, // mauve
  0x5d7fa8, // denim
  0x8c9257, // olive
  0xa8977f, // taupe
  0x9c6f88, // plum
  0xb0705c, // rust
  0x8b939c, // stone
];

/**
 * Fetch and validate the geometry manifest.
 * @param {string} url
 * @returns {Promise<{units: string, components: Array<object>}>}
 */
export async function loadManifest(url) {
  const response = await fetch(url);
  if (!response.ok) {
    throw new Error(`${url}: ${response.status} ${response.statusText}`);
  }

  const manifest = await response.json();
  if (!Array.isArray(manifest.components) || manifest.components.length === 0) {
    throw new Error(`${url}: no components listed`);
  }
  return manifest;
}

/**
 * Give each component its own material instance in its own colour.
 *
 * Separate instances are what make per-part colour and selection highlighting
 * possible; a shared material would tint every component at once.
 * @param {number} index - position in the manifest
 * @param {number|string} [override] - explicit colour from the manifest entry
 * @returns {THREE.MeshStandardMaterial}
 */
function createSurfaceMaterial(index, override) {
  const color = override ?? PALETTE[index % PALETTE.length];
  return new THREE.MeshStandardMaterial({ ...SURFACE, color });
}

/**
 * Load every component's STL into its own named mesh, in manifest order.
 *
 * Loads run concurrently; the returned order still follows the manifest so the
 * UI listing is stable regardless of which file finishes first.
 * @param {Array<object>} components - manifest entries
 * @param {(loaded: number, total: number, name: string) => void} [onProgress]
 * @returns {Promise<Map<string, THREE.Mesh>>} keyed by component name
 */
export async function loadComponents(components, onProgress) {
  const loader = new STLLoader();
  let loaded = 0;

  const meshes = await Promise.all(components.map(async (entry, index) => {
    const geometry = await loader.loadAsync(entry.file);
    geometry.computeBoundingBox();

    const material = createSurfaceMaterial(index, entry.color);
    const mesh = new THREE.Mesh(geometry, material);
    mesh.name = entry.name;
    // Keep the manifest entry on the object: picking and the outliner will
    // both want it, and it saves a lookup back through the manifest.
    mesh.userData.component = entry;
    mesh.userData.triangles = geometry.attributes.position.count / 3;
    // Base colour, kept separately so highlighting can restore it and the UI
    // can match its swatches to the 3D view.
    mesh.userData.color = material.color.getHex();

    onProgress?.(++loaded, components.length, entry.name);
    return mesh;
  }));

  return new Map(meshes.map((mesh) => [mesh.name, mesh]));
}

/**
 * Assemble meshes into a scene graph using each entry's `parent` field.
 *
 * Every parent is null today, so this produces a flat list under one root.
 * The traversal is written for the general case: once the manifest names
 * parents, transforms become relative and nothing here changes.
 * @param {Array<object>} components - manifest entries
 * @param {Map<string, THREE.Mesh>} meshes
 * @returns {THREE.Group} the assembly root
 */
export function buildSceneGraph(components, meshes) {
  const root = new THREE.Group();
  root.name = 'aircraft';

  for (const entry of components) {
    const mesh = meshes.get(entry.name);
    if (!mesh) continue;

    if (entry.parent == null) {
      root.add(mesh);
      continue;
    }

    const parent = meshes.get(entry.parent);
    if (parent) {
      parent.add(mesh);
    } else {
      // A dangling parent should not lose the part: attach it to the root and
      // say so, rather than silently dropping it from the view.
      console.warn(`"${entry.name}": unknown parent "${entry.parent}"`);
      root.add(mesh);
    }
  }

  return root;
}
