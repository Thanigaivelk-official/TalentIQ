/**
 * TalentIQ - Cinematic 3D AI Recruitment Intelligence Visualizer
 * Built with Three.js & GSAP
 * Features:
 * 1. Glowing AI Neural Sphere (Multilayer icosahedron wireframe + inner volumetric pulsing sphere)
 * 2. Ingested Document Particles flowing toward the core and transforming into structured insight nodes
 * 3. 3D Floating Candidate Profile Cards orbiting the neural core
 * 4. Volumetric blue and violet point lighting
 * 5. Mouse parallax and smooth camera transitions
 * 6. WebGL support detection and fallback
 */

(function () {
  'use strict';

  function initTalentIQ3D() {
    const container = document.getElementById('hero-3d-canvas');
    if (!container) return;

    // Check for user reduced-motion preference
    const prefersReducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;

    // WebGL capability check
    function hasWebGL() {
      try {
        const canvas = document.createElement('canvas');
        return !!(window.WebGLRenderingContext && (canvas.getContext('webgl') || canvas.getContext('experimental-webgl')));
      } catch (e) {
        return false;
      }
    }

    if (!hasWebGL()) {
      container.innerHTML = `
        <div class="h-100 d-flex flex-column align-items-center justify-content-center text-center p-4">
          <div class="p-4 rounded-circle bg-info bg-opacity-10 border border-info border-opacity-25 mb-3">
            <i data-lucide="cpu" class="text-cyan" style="width: 48px; height: 48px;"></i>
          </div>
          <h5 class="text-white fw-bold mb-1">AI Intelligence Pipeline Active</h5>
          <p class="text-secondary small mb-0">Hardware-accelerated rendering disabled. System operating in ultra-stable mode.</p>
        </div>
      `;
      if (window.lucide) window.lucide.createIcons();
      return;
    }

    const width = container.clientWidth || 550;
    const height = container.clientHeight || 550;

    // 1. Scene, Camera, Renderer
    const scene = new THREE.Scene();
    const camera = new THREE.PerspectiveCamera(55, width / height, 0.1, 1000);
    camera.position.set(0, 0, 8.5);

    const renderer = new THREE.WebGLRenderer({ alpha: true, antialias: true, powerPreference: 'high-performance' });
    renderer.setSize(width, height);
    renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
    renderer.toneMapping = THREE.ACESFilmicToneMapping;
    renderer.toneMappingExposure = 1.2;
    container.innerHTML = '';
    container.appendChild(renderer.domElement);

    // Root Group for Mouse Parallax
    const worldGroup = new THREE.Group();
    scene.add(worldGroup);

    // 2. Central AI Neural Core
    const coreGroup = new THREE.Group();
    worldGroup.add(coreGroup);

    // A. Outer Geometric Neural Mesh (Cyan)
    const outerGeo = new THREE.IcosahedronGeometry(2.0, 2);
    const outerMat = new THREE.MeshStandardMaterial({
      color: 0x38BDF8,
      wireframe: true,
      transparent: true,
      opacity: 0.65,
      roughness: 0.2,
      metalness: 0.8
    });
    const outerMesh = new THREE.Mesh(outerGeo, outerMat);
    coreGroup.add(outerMesh);

    // B. Inner Glowing Volumetric Sphere (Violet)
    const innerGeo = new THREE.SphereGeometry(1.35, 32, 32);
    const innerMat = new THREE.MeshStandardMaterial({
      color: 0x8B5CF6,
      emissive: 0x8B5CF6,
      emissiveIntensity: 0.8,
      roughness: 0.3,
      metalness: 0.5,
      transparent: true,
      opacity: 0.5
    });
    const innerSphere = new THREE.Mesh(innerGeo, innerMat);
    coreGroup.add(innerSphere);

    // C. Concentric Orbital Rings (Candidate Evaluation Latency)
    const ringGeo = new THREE.RingGeometry(2.5, 2.53, 64);
    const ringMat = new THREE.MeshBasicMaterial({
      color: 0x38BDF8,
      side: THREE.DoubleSide,
      transparent: true,
      opacity: 0.35
    });
    const ring1 = new THREE.Mesh(ringGeo, ringMat);
    ring1.rotation.x = Math.PI / 2.3;
    coreGroup.add(ring1);

    const ring2 = new THREE.Mesh(ringGeo, ringMat);
    ring2.rotation.x = -Math.PI / 3;
    ring2.rotation.y = Math.PI / 4;
    coreGroup.add(ring2);

    // 3. Document Stream Particle Field (Flowing toward core)
    const particleCount = 260;
    const docParticlesGeo = new THREE.BufferGeometry();
    const particlePositions = new Float32Array(particleCount * 3);
    const particleVelocities = [];

    for (let i = 0; i < particleCount; i++) {
      const idx = i * 3;
      // Spawn particles distributed in a sphere perimeter
      const radius = 3.5 + Math.random() * 4.0;
      const theta = Math.random() * Math.PI * 2;
      const phi = Math.acos((Math.random() * 2) - 1);

      particlePositions[idx] = radius * Math.sin(phi) * Math.cos(theta);
      particlePositions[idx + 1] = radius * Math.sin(phi) * Math.sin(theta);
      particlePositions[idx + 2] = radius * Math.cos(phi);

      particleVelocities.push({
        origRadius: radius,
        speed: 0.008 + Math.random() * 0.012,
        theta: theta,
        phi: phi
      });
    }

    docParticlesGeo.setAttribute('position', new THREE.BufferAttribute(particlePositions, 3));
    const docParticlesMat = new THREE.PointsMaterial({
      color: 0x38BDF8,
      size: 0.09,
      transparent: true,
      opacity: 0.75,
      blending: THREE.AdditiveBlending
    });
    const particleCloud = new THREE.Points(docParticlesGeo, docParticlesMat);
    worldGroup.add(particleCloud);

    // 4. 3D Floating Candidate Profile Cards
    function create3DCandidateCard(name, score, role, skillText, colorHex) {
      const cardCanvas = document.createElement('canvas');
      cardCanvas.width = 380;
      cardCanvas.height = 190;
      const ctx = cardCanvas.getContext('2d');

      // Rounded background
      ctx.fillStyle = 'rgba(13, 21, 39, 0.92)';
      ctx.strokeStyle = colorHex;
      ctx.lineWidth = 4;
      ctx.beginPath();
      ctx.roundRect(10, 10, 360, 170, 16);
      ctx.fill();
      ctx.stroke();

      // Candidate Avatar Icon circle
      ctx.fillStyle = colorHex;
      ctx.beginPath();
      ctx.arc(45, 55, 22, 0, Math.PI * 2);
      ctx.fill();

      // Candidate Name
      ctx.fillStyle = '#FFFFFF';
      ctx.font = 'bold 22px Inter, sans-serif';
      ctx.fillText(name, 80, 52);

      // Role
      ctx.fillStyle = '#94A3B8';
      ctx.font = '16px Inter, sans-serif';
      ctx.fillText(role, 80, 76);

      // Score Pill
      ctx.fillStyle = colorHex;
      ctx.beginPath();
      ctx.roundRect(260, 35, 95, 34, 8);
      ctx.fill();

      ctx.fillStyle = '#070B16';
      ctx.font = 'bold 18px JetBrains Mono, monospace';
      ctx.fillText(score, 275, 58);

      // Skill tags
      ctx.fillStyle = 'rgba(56, 189, 248, 0.2)';
      ctx.strokeStyle = 'rgba(56, 189, 248, 0.5)';
      ctx.lineWidth = 1.5;
      ctx.beginPath();
      ctx.roundRect(25, 110, 330, 44, 8);
      ctx.fill();
      ctx.stroke();

      ctx.fillStyle = '#38BDF8';
      ctx.font = 'bold 15px JetBrains Mono, monospace';
      ctx.fillText(skillText, 40, 137);

      const texture = new THREE.CanvasTexture(cardCanvas);
      texture.minFilter = THREE.LinearFilter;
      const planeGeo = new THREE.PlaneGeometry(2.2, 1.1);
      const planeMat = new THREE.MeshBasicMaterial({
        map: texture,
        transparent: true,
        side: THREE.DoubleSide
      });
      return new THREE.Mesh(planeGeo, planeMat);
    }

    const card1 = create3DCandidateCard('Sarah Jenkins', '94% Match', 'Staff ML Engineer', 'Python • PyTorch • LLM', '#38BDF8');
    card1.position.set(2.8, 1.6, 1.2);
    worldGroup.add(card1);

    const card2 = create3DCandidateCard('David Chen', '88% Match', 'Backend Lead', 'Django • PostgreSQL • Docker', '#8B5CF6');
    card2.position.set(-2.8, -1.5, 0.8);
    worldGroup.add(card2);

    const card3 = create3DCandidateCard('Elena Rostova', '91% Match', 'Cloud Architect', 'AWS • Kubernetes • Terraform', '#10B981');
    card3.position.set(2.2, -2.0, -1.0);
    worldGroup.add(card3);

    // 5. Cinematic Volumetric Lighting
    const ambientLight = new THREE.AmbientLight(0xffffff, 0.75);
    scene.add(ambientLight);

    const cyanPointLight = new THREE.PointLight(0x38BDF8, 3.5, 30);
    cyanPointLight.position.set(5, 5, 6);
    scene.add(cyanPointLight);

    const violetPointLight = new THREE.PointLight(0x8B5CF6, 3.5, 30);
    violetPointLight.position.set(-5, -5, 6);
    scene.add(violetPointLight);

    // 6. Interactive Mouse Parallax
    let mouseX = 0;
    let mouseY = 0;
    let targetX = 0;
    let targetY = 0;

    window.addEventListener('mousemove', function (e) {
      const rect = container.getBoundingClientRect();
      const clientX = e.clientX - (rect.left + rect.width / 2);
      const clientY = e.clientY - (rect.top + rect.height / 2);
      mouseX = clientX * 0.0006;
      mouseY = clientY * 0.0006;
    });

    // 7. Responsive Resizing
    window.addEventListener('resize', function () {
      const newWidth = container.clientWidth;
      const newHeight = container.clientHeight || 550;
      camera.aspect = newWidth / newHeight;
      camera.updateProjectionMatrix();
      renderer.setSize(newWidth, newHeight);
    });

    // 8. Animation Render Loop
    let clock = new THREE.Clock();

    function renderLoop() {
      requestAnimationFrame(renderLoop);

      const delta = clock.getDelta();
      const elapsedTime = clock.getElapsedTime();

      if (!prefersReducedMotion) {
        // Rotate neural core
        outerMesh.rotation.y += 0.004;
        outerMesh.rotation.x += 0.002;

        innerSphere.rotation.y -= 0.003;
        ring1.rotation.z += 0.0025;
        ring2.rotation.z -= 0.0025;

        // Subtle pulsing of inner core
        const pulse = 1.0 + Math.sin(elapsedTime * 2.5) * 0.04;
        innerSphere.scale.set(pulse, pulse, pulse);

        // Orbit floating candidate cards
        card1.position.y = 1.6 + Math.sin(elapsedTime * 1.2) * 0.15;
        card1.rotation.y = Math.sin(elapsedTime * 0.5) * 0.12;

        card2.position.y = -1.5 + Math.cos(elapsedTime * 1.4) * 0.15;
        card2.rotation.y = -Math.sin(elapsedTime * 0.5) * 0.12;

        card3.position.y = -2.0 + Math.sin(elapsedTime * 1.1 + 1.0) * 0.12;

        // Flow particles continuously toward center
        const positions = docParticlesGeo.attributes.position.array;
        for (let i = 0; i < particleCount; i++) {
          const idx = i * 3;
          const v = particleVelocities[i];

          // Contract radius inward
          v.origRadius -= v.speed;
          if (v.origRadius < 1.4) {
            // Re-spawn on perimeter
            v.origRadius = 6.5 + Math.random() * 2.5;
            v.theta = Math.random() * Math.PI * 2;
            v.phi = Math.acos((Math.random() * 2) - 1);
          }

          positions[idx] = v.origRadius * Math.sin(v.phi) * Math.cos(v.theta);
          positions[idx + 1] = v.origRadius * Math.sin(v.phi) * Math.sin(v.theta);
          positions[idx + 2] = v.origRadius * Math.cos(v.phi);
        }
        docParticlesGeo.attributes.position.needsUpdate = true;
      }

      // Smooth parallax damping
      targetX += (mouseX - targetX) * 0.05;
      targetY += (mouseY - targetY) * 0.05;

      worldGroup.rotation.y = targetX;
      worldGroup.rotation.x = targetY;

      renderer.render(scene, camera);
    }

    renderLoop();
  }

  // Initialize on DOM load
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initTalentIQ3D);
  } else {
    initTalentIQ3D();
  }
})();
