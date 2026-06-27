import * as THREE from 'three';
import { OrbitControls } from 'three/addons/controls/OrbitControls.js';

const container = document.getElementById('preview-container');
if (!container) throw new Error('Preview container not found');

const w = container.clientWidth;
const h = container.clientHeight;

const scene = new THREE.Scene();
scene.background = new THREE.Color(0xf0f0f0);

const camera = new THREE.PerspectiveCamera(35, w / h, 0.1, 100);
camera.position.set(4, 2.5, 5);
camera.lookAt(0, 0.5, 0);

const renderer = new THREE.WebGLRenderer({ antialias: true });
renderer.setSize(w, h);
renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
renderer.shadowMap.enabled = true;
renderer.shadowMap.type = THREE.PCFSoftShadowMap;
container.appendChild(renderer.domElement);

const controls = new OrbitControls(camera, renderer.domElement);
controls.target.set(0, 0.5, 0);
controls.enableDamping = true;
controls.dampingFactor = 0.08;
controls.autoRotate = true;
controls.autoRotateSpeed = 1.5;
controls.minDistance = 2.5;
controls.maxDistance = 12;
controls.update();

const ambientLight = new THREE.AmbientLight(0xffffff, 0.6);
scene.add(ambientLight);

const mainLight = new THREE.DirectionalLight(0xffffff, 1.8);
mainLight.position.set(5, 8, 6);
mainLight.castShadow = true;
scene.add(mainLight);

const fillLight = new THREE.DirectionalLight(0xffffff, 0.4);
fillLight.position.set(-3, 2, -4);
scene.add(fillLight);

const rimLight = new THREE.DirectionalLight(0xffffff, 0.3);
rimLight.position.set(0, -1, -6);
scene.add(rimLight);

const groundGeom = new THREE.PlaneGeometry(12, 12);
const groundMat = new THREE.ShadowMaterial({ opacity: 0.15 });
const ground = new THREE.Mesh(groundGeom, groundMat);
ground.rotation.x = -Math.PI / 2;
ground.position.y = -0.3;
ground.receiveShadow = true;
scene.add(ground);

function makeFootprintShape(scaleX, scaleZ) {
  const s = new THREE.Shape();
  const w = 1.5 * scaleX;
  const l = 2.8 * scaleZ;
  s.moveTo(-w * 0.75, -l);
  s.bezierCurveTo(-w, -l * 0.6, -w, l * 0.3, -w * 0.8, l * 0.7);
  s.bezierCurveTo(-w * 0.35, l, 0, l * 0.92, w * 0.35, l);
  s.bezierCurveTo(w, l * 0.7, w, l * 0.3, w * 0.8, -l * 0.6);
  s.bezierCurveTo(w * 0.75, -l, w * 0.3, -l * 0.92, -w * 0.75, -l);
  return s;
}

function buildShoe() {
  const group = new THREE.Group();

  function createPart(name, geom, color, pos, opts = {}) {
    const mat = new THREE.MeshStandardMaterial({
      color,
      roughness: opts.roughness ?? 0.6,
      metalness: opts.metalness ?? 0.0,
      flatShading: opts.flatShading ?? true,
    });
    const mesh = new THREE.Mesh(geom, mat);
    mesh.name = name;
    mesh.castShadow = true;
    mesh.receiveShadow = true;
    if (pos) {
      mesh.position.x = pos.x ?? 0;
      mesh.position.y = pos.y ?? 0;
      mesh.position.z = pos.z ?? 0;
    }
    if (opts.rotation) {
      mesh.rotation.x = opts.rotation.x ?? 0;
      mesh.rotation.y = opts.rotation.y ?? 0;
      mesh.rotation.z = opts.rotation.z ?? 0;
    }
    return mesh;
  }

  const soleShape = makeFootprintShape(1, 1);
  const soleGeom = new THREE.ExtrudeGeometry(soleShape, {
    depth: 0.35,
    bevelEnabled: true,
    bevelThickness: 0.08,
    bevelSize: 0.04,
    bevelSegments: 3,
  });
  soleGeom.translate(0, 0, -0.175);
  const sole = createPart('sole', soleGeom, 0x333333, { y: -0.175 });
  group.add(sole);

  const upperShape = makeFootprintShape(0.85, 0.9);
  const upperGeom = new THREE.ExtrudeGeometry(upperShape, {
    depth: 1.3,
    bevelEnabled: true,
    bevelThickness: 0.12,
    bevelSize: 0.06,
    bevelSegments: 3,
  });
  upperGeom.translate(0, 0, -0.65);
  const upper = createPart('upper', upperGeom, 0x1a7a4a, { y: 0.55 });
  group.add(upper);

  const liningShape = makeFootprintShape(0.75, 0.75);
  const liningGeom = new THREE.ExtrudeGeometry(liningShape, {
    depth: 0.15,
    bevelEnabled: true,
    bevelThickness: 0.05,
    bevelSize: 0.03,
    bevelSegments: 2,
  });
  liningGeom.translate(0, 0, -0.075);
  const lining = createPart('lining', liningGeom, 0xf5f5f5, { y: 1.25 });
  group.add(lining);

  const heelGeom = new THREE.BoxGeometry(1.8, 0.7, 0.35);
  heelGeom.translate(0, 0.35, 0);
  const heel = createPart('heel', heelGeom, 0x222222, { y: 0.55, z: -2.55 });
  group.add(heel);

  const laceGroup = new THREE.Group();
  laceGroup.name = 'lace';
  const laceMat = new THREE.MeshStandardMaterial({
    color: 0x1a7a4a,
    roughness: 0.5,
    flatShading: true,
  });

  for (let i = 0; i < 4; i++) {
    const zPos = 2.1 - i * 0.32;
    const height = 1.25 + i * 0.08;

    const crossGeom = new THREE.CylinderGeometry(0.035, 0.035, 0.35, 4);
    const cross1 = new THREE.Mesh(crossGeom, laceMat);
    cross1.position.set(-0.55, height, zPos);
    cross1.rotation.x = 0.35;
    cross1.castShadow = true;
    laceGroup.add(cross1);

    const cross2 = new THREE.Mesh(crossGeom.clone(), laceMat);
    cross2.position.set(0.55, height, zPos);
    cross2.rotation.x = -0.35;
    cross2.castShadow = true;
    laceGroup.add(cross2);

    const eyeletGeom = new THREE.TorusGeometry(0.06, 0.025, 4, 6);
    const eyeletMat = new THREE.MeshStandardMaterial({
      color: 0x666666,
      roughness: 0.3,
      metalness: 0.4,
      flatShading: true,
    });
    const eyeletL = new THREE.Mesh(eyeletGeom, eyeletMat);
    eyeletL.position.set(-0.7, height - 0.05, zPos);
    eyeletL.rotation.x = Math.PI / 2;
    eyeletL.castShadow = true;
    laceGroup.add(eyeletL);

    const eyeletR = new THREE.Mesh(eyeletGeom.clone(), eyeletMat);
    eyeletR.position.set(0.7, height - 0.05, zPos);
    eyeletR.rotation.x = Math.PI / 2;
    eyeletR.castShadow = true;
    laceGroup.add(eyeletR);
  }

  group.add(laceGroup);

  const toeCapShape = makeFootprintShape(0.65, 0.55);
  const toeCapGeom = new THREE.ExtrudeGeometry(toeCapShape, {
    depth: 0.08,
    bevelEnabled: true,
    bevelThickness: 0.04,
    bevelSize: 0.02,
    bevelSegments: 2,
  });
  toeCapGeom.translate(0, 0, -0.04);
  const toeCap = createPart('upper', toeCapGeom, 0x1a7a4a, { y: 1.25, z: 1.65 });
  group.add(toeCap);

  return group;
}

const shoe = buildShoe();
scene.add(shoe);

const shoeParts = {};
shoe.traverse((child) => {
  if (child.isMesh && !shoeParts[child.name]) {
    shoeParts[child.name] = child;
  }
});

function setPartColor(partName, hexColor) {
  shoe.traverse((child) => {
    if (child.isMesh && child.name === partName) {
      child.material.color.set(hexColor);
    }
  });
}

function setPartTexture(partName, texture) {
  shoe.traverse((child) => {
    if (child.isMesh && child.name === partName) {
      child.material.map = texture;
      child.material.needsUpdate = true;
    }
  });
}

document.querySelectorAll('.color-picker').forEach((input) => {
  const partName = input.dataset.part;
  input.addEventListener('input', () => {
    setPartColor(partName, input.value);
    const hexLabel = input.closest('.color-row').querySelector('.color-row__hex');
    if (hexLabel) hexLabel.textContent = input.value;
  });
});

document.querySelectorAll('.size-pill').forEach((pill) => {
  pill.addEventListener('click', () => {
    document.querySelectorAll('.size-pill').forEach((p) => p.classList.remove('size-pill--active'));
    pill.classList.add('size-pill--active');
  });
});

function generatePattern(type, color1, color2) {
  const canvas = document.createElement('canvas');
  canvas.width = 256;
  canvas.height = 256;
  const ctx = canvas.getContext('2d');

  const c1 = color1 || '#1a7a4a';
  const c2 = color2 || '#444444';

  switch (type) {
    case 'solid': {
      ctx.fillStyle = c1;
      ctx.fillRect(0, 0, 256, 256);
      break;
    }
    case 'stripe': {
      ctx.fillStyle = c2;
      ctx.fillRect(0, 0, 256, 256);
      ctx.strokeStyle = c1;
      ctx.lineWidth = 18;
      for (let i = -256; i < 512; i += 32) {
        ctx.beginPath();
        ctx.moveTo(i, 0);
        ctx.lineTo(i + 256, 256);
        ctx.stroke();
      }
      break;
    }
    case 'dot': {
      ctx.fillStyle = c2;
      ctx.fillRect(0, 0, 256, 256);
      ctx.fillStyle = c1;
      for (let y = 0; y < 256; y += 24) {
        for (let x = 0; x < 256; x += 24) {
          ctx.beginPath();
          ctx.arc(x + 12, y + 12, 5, 0, Math.PI * 2);
          ctx.fill();
        }
      }
      break;
    }
    case 'checker': {
      const size = 32;
      for (let y = 0; y < 256; y += size) {
        for (let x = 0; x < 256; x += size) {
          ctx.fillStyle = (Math.floor(x / size) + Math.floor(y / size)) % 2 === 0 ? c1 : c2;
          ctx.fillRect(x, y, size, size);
        }
      }
      break;
    }
    case 'chevron': {
      ctx.fillStyle = c2;
      ctx.fillRect(0, 0, 256, 256);
      ctx.fillStyle = c1;
      for (let y = -32; y < 288; y += 32) {
        ctx.beginPath();
        ctx.moveTo(0, y + 16);
        ctx.lineTo(128, y);
        ctx.lineTo(256, y + 16);
        ctx.lineTo(256, y + 32);
        ctx.lineTo(128, y + 20);
        ctx.lineTo(0, y + 32);
        ctx.closePath();
        ctx.fill();
      }
      break;
    }
  }

  const tex = new THREE.CanvasTexture(canvas);
  tex.wrapS = tex.wrapT = THREE.RepeatWrapping;
  tex.repeat.set(1, 1);
  tex.anisotropy = 4;
  return tex;
}

const patternTextures = {};
['solid', 'stripe', 'dot', 'checker', 'chevron'].forEach((key) => {
  patternTextures[key] = generatePattern(key);
});
let activePattern = 'solid';
setPartTexture('upper', patternTextures['solid']);

document.querySelectorAll('.pattern-swatch').forEach((swatch) => {
  swatch.addEventListener('click', () => {
    document.querySelectorAll('.pattern-swatch').forEach((s) => s.classList.remove('pattern-swatch--active'));
    swatch.classList.add('pattern-swatch--active');
    const patternKey = swatch.dataset.pattern;
    activePattern = patternKey;
    setPartTexture('upper', patternTextures[patternKey]);
  });
});

document.getElementById('btn-add-cart').addEventListener('click', () => {
  alert('Cart coming soon — your design is saved for now.');
});

function animate() {
  requestAnimationFrame(animate);
  controls.update();
  renderer.render(scene, camera);
}
animate();

window.addEventListener('resize', () => {
  const cw = container.clientWidth;
  const ch = container.clientHeight;
  camera.aspect = cw / ch;
  camera.updateProjectionMatrix();
  renderer.setSize(cw, ch);
});

const resizeObserver = new ResizeObserver(() => {
  const cw = container.clientWidth;
  const ch = container.clientHeight;
  if (cw > 0 && ch > 0) {
    camera.aspect = cw / ch;
    camera.updateProjectionMatrix();
    renderer.setSize(cw, ch);
  }
});
resizeObserver.observe(container);