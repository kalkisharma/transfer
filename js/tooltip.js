/**
 * The component callout: a DOM panel anchored to a point on the 3-D model.
 *
 * The tooltip owns presentation only. It is told which mesh to describe and
 * where it was clicked; it reads the specs straight off the manifest entry
 * carried in the mesh's userData, so adding a spec in the generator needs no
 * change here.
 */

import * as THREE from 'three';

/** Gap in pixels between the anchor point and the nearest edge of the box. */
const GAP = 18;

/** Minimum clearance between the box and the edge of the viewport. */
const MARGIN = 12;

/**
 * Format a three.js hex colour as a CSS colour string.
 * @param {number} hex
 * @returns {string}
 */
function toCssColor(hex) {
  return `#${hex.toString(16).padStart(6, '0')}`;
}

/**
 * Clamp a value into an inclusive range.
 * @param {number} value
 * @param {number} low
 * @param {number} high
 * @returns {number}
 */
function clamp(value, low, high) {
  return Math.min(Math.max(value, low), high);
}

/**
 * Create the tooltip controller.
 *
 * @param {object} elements
 * @param {HTMLElement} elements.element - the tooltip box
 * @param {HTMLElement} elements.nameEl - heading node
 * @param {HTMLElement} elements.specsEl - definition list node
 * @param {SVGElement} elements.leader - overlay holding the line and dot
 * @returns {{show: Function, hide: Function, update: Function}}
 */
export function createTooltip({ element, nameEl, specsEl, leader }) {
  const line = leader.querySelector('.leader__line');
  const dot = leader.querySelector('.leader__dot');

  const anchorLocal = new THREE.Vector3();
  const projected = new THREE.Vector3();
  let mesh = null;
  // Cached box size: the content only changes on show(), and reading layout
  // every frame would force a style recalculation for no benefit.
  let size = { width: 0, height: 0 };

  /**
   * Show or hide both overlay elements.
   *
   * The attribute is toggled rather than assigning `.hidden`, because the
   * leader is an SVGElement and `hidden` is an HTMLElement property: the
   * assignment would silently never reach the attribute the CSS matches.
   * @param {boolean} hidden
   */
  const setHidden = (hidden) => {
    element.toggleAttribute('hidden', hidden);
    leader.toggleAttribute('hidden', hidden);
  };

  /** Re-measure the tooltip box from the DOM. */
  const measure = () => {
    const rect = element.getBoundingClientRect();
    size = { width: rect.width, height: rect.height };
  };

  /**
   * Fill in the heading and spec rows for a component.
   * @param {object} component - manifest entry
   * @param {number} color - the component's base colour
   */
  const render = (component, color) => {
    const swatch = document.createElement('span');
    swatch.className = 'tooltip__swatch';
    swatch.style.background = toCssColor(color);

    const label = document.createElement('span');
    label.textContent = component.name;
    nameEl.replaceChildren(swatch, label);

    const specs = component.specs ?? [];
    if (specs.length === 0) {
      const empty = document.createElement('div');
      empty.className = 'tooltip__empty';
      empty.textContent = 'No specifications in the manifest';
      specsEl.replaceChildren(empty);
      return;
    }

    const rows = specs.flatMap((spec) => {
      const term = document.createElement('dt');
      term.className = 'tooltip__label';
      term.textContent = spec.label;

      const value = document.createElement('dd');
      value.className = 'tooltip__value';
      value.textContent = spec.value;
      return [term, value];
    });
    specsEl.replaceChildren(...rows);
  };

  window.addEventListener('resize', () => {
    if (mesh) measure();
  });

  return {
    /**
     * Describe a component, anchored to the point that was clicked.
     *
     * The anchor is converted to mesh-local space so it stays put on the
     * surface no matter how the mesh or its future parents are transformed.
     * @param {THREE.Mesh} target
     * @param {THREE.Vector3} worldPoint
     */
    show(target, worldPoint) {
      mesh = target;
      anchorLocal.copy(target.worldToLocal(worldPoint.clone()));

      const color = target.userData.color ?? 0x9aa2ab;
      render(target.userData.component, color);
      dot.style.fill = toCssColor(color);

      setHidden(false);
      measure();
    },

    /** Dismiss the tooltip. */
    hide() {
      mesh = null;
      setHidden(true);
    },

    /**
     * Reposition the box to track its anchor. Call once per frame.
     * @param {THREE.Camera} camera
     * @param {THREE.WebGLRenderer} renderer
     */
    update(camera, renderer) {
      if (!mesh) return;

      const rect = renderer.domElement.getBoundingClientRect();
      projected.copy(anchorLocal);
      mesh.localToWorld(projected).project(camera);

      // z > 1 means the anchor is behind the camera, where the projection
      // flips and the box would appear on the wrong side of the screen.
      const behind = projected.z > 1;
      element.style.visibility = behind ? 'hidden' : '';
      leader.style.visibility = behind ? 'hidden' : '';
      if (behind) return;

      const anchorX = (projected.x * 0.5 + 0.5) * rect.width;
      const anchorY = (-projected.y * 0.5 + 0.5) * rect.height;

      // Prefer the right of the anchor; flip when there is no room.
      const fitsRight = anchorX + GAP + size.width + MARGIN <= rect.width;
      const left = fitsRight ? anchorX + GAP : anchorX - GAP - size.width;
      const top = clamp(anchorY - size.height / 2,
        MARGIN, Math.max(MARGIN, rect.height - size.height - MARGIN));

      element.style.transform =
        `translate(${Math.round(left)}px, ${Math.round(top)}px)`;

      // The leader meets whichever edge faces the anchor, kept inside the
      // box's rounded corners.
      const edgeX = fitsRight ? left : left + size.width;
      const edgeY = clamp(anchorY, top + 14, top + size.height - 14);

      line.setAttribute('x1', anchorX);
      line.setAttribute('y1', anchorY);
      line.setAttribute('x2', edgeX);
      line.setAttribute('y2', edgeY);
      dot.setAttribute('cx', anchorX);
      dot.setAttribute('cy', anchorY);
    },
  };
}
