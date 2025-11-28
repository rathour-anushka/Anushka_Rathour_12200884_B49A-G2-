const scene = new THREE.Scene();
const camera = new THREE.PerspectiveCamera(75, window.innerWidth/window.innerHeight, 0.1, 1000);
const renderer = new THREE.WebGLRenderer({ canvas: document.getElementById('bgCanvas'), alpha: true });
renderer.setSize(window.innerWidth, window.innerHeight);

// Lighting
const ambientLight = new THREE.AmbientLight(0xffffff, 0.6);
scene.add(ambientLight);

const directionalLight = new THREE.DirectionalLight(0xffffff, 0.8);
directionalLight.position.set(5, 5, 5);
scene.add(directionalLight);

// Geometry (slightly smaller)
const geometry = new THREE.SphereGeometry(0.6, 32, 32);

// Create more spheres in a tighter space
const spheres = [];
for (let i = 0; i < 50; i++) {
  const color = new THREE.Color(Math.random(), Math.random(), Math.random());
  const material = new THREE.MeshPhongMaterial({ color, shininess: 80, specular: 0xffffff });
  const sphere = new THREE.Mesh(geometry, material);
  sphere.position.set(
    (Math.random() - 0.5) * 10,  // tighter spread
    (Math.random() - 0.5) * 10,
    (Math.random() - 0.5) * 10
  );
  sphere.userData = {
    velocity: {
      x: (Math.random() - 0.5) * 0.01,
      y: (Math.random() - 0.5) * 0.01,
      z: (Math.random() - 0.5) * 0.01
    }
  };
  spheres.push(sphere);
  scene.add(sphere);
}

camera.position.z = 10;

// Animate
function animate() {
  requestAnimationFrame(animate);
  spheres.forEach(s => {
    s.rotation.x += 0.005;
    s.rotation.y += 0.005;
    s.position.x += s.userData.velocity.x;
    s.position.y += s.userData.velocity.y;
    s.position.z += s.userData.velocity.z;

    ['x', 'y', 'z'].forEach(axis => {
      if (Math.abs(s.position[axis]) > 10) {
        s.userData.velocity[axis] *= -1;
      }
    });
  });
  renderer.render(scene, camera);
}
animate();

window.addEventListener('resize', () => {
  camera.aspect = window.innerWidth/window.innerHeight;
  camera.updateProjectionMatrix();
  renderer.setSize(window.innerWidth, window.innerHeight);
});
