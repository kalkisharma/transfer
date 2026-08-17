/**
 * Camera input and camera motion.
 *
 * OrbitControls handles the dragging; the flight helper handles programmatic
 * moves (the opening fit, and later "zoom to component") with easing so the
 * view never teleports.
 */

import * as THREE from 'three';
import { OrbitControls } from 'three/addons/controls/OrbitControls.js';

/**
 * Create damped orbit controls for rotate / zoom / pan.
 * @param {THREE.PerspectiveCamera} camera
 * @param {HTMLElement} domElement
 * @returns {OrbitControls}
 */
export function createControls(camera, domElement) {
  const controls = new OrbitControls(camera, domElement);

  // Damping is what makes the view feel weighted rather than twitchy. It
  // requires controls.update() every frame -- see the render loop.
  controls.enableDamping = true;
  controls.dampingFactor = 0.075;

  controls.rotateSpeed = 0.85;
  controls.zoomSpeed = 0.9;
  controls.panSpeed = 0.85;

  // Screen-space panning keeps drag direction matching cursor direction at any
  // camera pitch; the alternative pans along the ground plane and feels wrong
  // when looking down at a model.
  controls.screenSpacePanning = true;
  return controls;
}

/**
 * Clamp orbit distances to the model's scale.
 *
 * Without this, the wheel either crawls or flies straight through the model,
 * depending on whether the geometry is millimetres or metres.
 * @param {OrbitControls} controls
 * @param {number} distance - the framing distance for the whole model
 */
export function setDistanceLimits(controls, distance) {
  controls.minDistance = distance * 0.05;
  controls.maxDistance = distance * 6;
}

/**
 * Ease-in-out cubic: slow at both ends, quick through the middle.
 * @param {number} t - normalised time in [0, 1]
 * @returns {number}
 */
function easeInOutCubic(t) {
  return t < 0.5 ? 4 * t * t * t : 1 - Math.pow(-2 * t + 2, 3) / 2;
}

/**
 * Create a helper that eases the camera between poses.
 *
 * User input is disabled for the duration of a flight, otherwise a drag
 * mid-flight fights the tween and the camera stutters.
 * @param {THREE.PerspectiveCamera} camera
 * @param {OrbitControls} controls
 * @returns {{flyTo: Function, update: Function, isFlying: Function}}
 */
export function createCameraFlight(camera, controls) {
  const fromPosition = new THREE.Vector3();
  const fromTarget = new THREE.Vector3();
  const toPosition = new THREE.Vector3();
  const toTarget = new THREE.Vector3();

  let elapsed = 0;
  let duration = 0;

  return {
    /**
     * Begin easing towards a pose. A duration of 0 snaps immediately.
     * @param {THREE.Vector3} position
     * @param {THREE.Vector3} target
     * @param {number} [seconds=1.1]
     */
    flyTo(position, target, seconds = 1.1) {
      toPosition.copy(position);
      toTarget.copy(target);

      if (seconds <= 0) {
        camera.position.copy(toPosition);
        controls.target.copy(toTarget);
        controls.update();
        duration = 0;
        return;
      }

      fromPosition.copy(camera.position);
      fromTarget.copy(controls.target);
      elapsed = 0;
      duration = seconds;
      controls.enabled = false;
    },

    /**
     * Advance the flight. Call once per frame before controls.update().
     * @param {number} delta - seconds since the previous frame
     * @returns {boolean} true while a flight is in progress
     */
    update(delta) {
      if (duration <= 0) return false;

      elapsed = Math.min(elapsed + delta, duration);
      const t = easeInOutCubic(elapsed / duration);
      camera.position.lerpVectors(fromPosition, toPosition, t);
      controls.target.lerpVectors(fromTarget, toTarget, t);

      if (elapsed >= duration) {
        duration = 0;
        controls.enabled = true;
      }
      return true;
    },

    /** @returns {boolean} whether a flight is currently running */
    isFlying() {
      return duration > 0;
    },
  };
}
