// 3D rotating island and floating question blocks on the home page.

class TitleScene {
    constructor(canvasId) {
        this.canvas = document.getElementById(canvasId);
        if (!this.canvas) return;

        this.scene = new THREE.Scene();
        this.scene.background = new THREE.Color(0x050711);
        this.scene.fog = new THREE.FogExp2(0x050711, 0.025);

        this.camera = new THREE.PerspectiveCamera(50, window.innerWidth / window.innerHeight, 0.1, 1000);
        this.camera.position.set(0, 4.5, 14);

        this.renderer = new THREE.WebGLRenderer({
            canvas: this.canvas,
            antialias: true,
            alpha: false
        });
        this.renderer.setSize(window.innerWidth, window.innerHeight);
        this.renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
        this.renderer.shadowMap.enabled = true;
        this.renderer.shadowMap.type = THREE.PCFSoftShadowMap;

        this.clock = new THREE.Clock();
        this.raycaster = new THREE.Raycaster();
        this.mouse = new THREE.Vector2();
        this.interactiveObjects = [];
        this.poppedCoins = [];

        this.initLights();
        this.initEnvironment();
        this.initInteractiveBlocks();
        this.initEvents();
        this.animate();
    }

    initLights() {
        const ambient = new THREE.AmbientLight(0x223855, 1.6);
        this.scene.add(ambient);

        // Cyber Cyan key light with soft shadow
        const keyLight = new THREE.DirectionalLight(0x00f0ff, 1.8);
        keyLight.position.set(8, 16, 12);
        keyLight.castShadow = true;
        keyLight.shadow.mapSize.width = 2048;
        keyLight.shadow.mapSize.height = 2048;
        keyLight.shadow.bias = -0.001;
        this.scene.add(keyLight);

        // Warm Gold rim light
        const rimLight = new THREE.DirectionalLight(0xffaa00, 1.2);
        rimLight.position.set(-10, 12, -8);
        this.scene.add(rimLight);

        // Soft center glow
        const goldLight = new THREE.PointLight(0xffcc00, 2.0, 16);
        goldLight.position.set(0, 3, 3);
        this.scene.add(goldLight);
        this.goldLight = goldLight;
    }

    initEnvironment() {
        // High-tech floating cyber platform (dark sleek slate)
        const islandGeom = new THREE.CylinderGeometry(8.5, 7.0, 2.2, 32);
        const islandMat = new THREE.MeshStandardMaterial({
            color: 0x0c1426,
            roughness: 0.5,
            metalness: 0.6
        });
        const island = new THREE.Mesh(islandGeom, islandMat);
        island.position.y = -1.1;
        island.receiveShadow = true;
        this.scene.add(island);

        // Sleek top surface with subtle dark grid
        const topGeom = new THREE.CylinderGeometry(8.52, 8.52, 0.15, 32);
        const topMat = new THREE.MeshStandardMaterial({
            color: 0x111c36,
            roughness: 0.3,
            metalness: 0.4
        });
        const topMesh = new THREE.Mesh(topGeom, topMat);
        topMesh.position.y = 0.05;
        topMesh.receiveShadow = true;
        this.scene.add(topMesh);

        // Glowing neon cyan rim ring
        const rimGeom = new THREE.TorusGeometry(8.54, 0.08, 16, 64);
        rimGeom.rotateX(Math.PI / 2);
        const rimMat = new THREE.MeshBasicMaterial({ color: 0x00f0ff });
        const rim = new THREE.Mesh(rimGeom, rimMat);
        rim.position.y = 0.12;
        this.scene.add(rim);

        // Cyber grid in deep background
        this.grid = window.mario3D.createCyberGrid(120, 50, 0x00f0ff);
        this.grid.position.y = -5.5;
        this.scene.add(this.grid);

        // Matrix falling particles
        this.particles = window.mario3D.createMatrixParticles(600, 45);
        this.scene.add(this.particles);

        // Symmetrically placed Cyber Warp Pipes
        const pipe1 = window.mario3D.createWarpPipe(2.8, 1.0);
        pipe1.position.set(-5.6, 0.08, -1.8);
        this.scene.add(pipe1);

        const pipe2 = window.mario3D.createWarpPipe(2.8, 1.0);
        pipe2.position.set(5.6, 0.08, -1.8);
        this.scene.add(pipe2);

        // Detective Mario standing on the left
        this.avatar = window.mario3D.createDetectiveAvatar();
        this.avatar.position.set(-4.0, 0.08, 1.0);
        this.avatar.rotation.y = 0.45;
        this.avatar.scale.set(0.75, 0.75, 0.75);
        this.scene.add(this.avatar);

        // Glowing Mushroom on the right
        const shroom = window.mario3D.createMushroom(0xff2a4d);
        shroom.position.set(4.2, 0.08, 1.0);
        shroom.rotation.y = -0.4;
        shroom.scale.set(0.55, 0.55, 0.55);
        this.scene.add(shroom);
    }

    initInteractiveBlocks() {
        this.blocks = [];
        // Evenly spaced Question Blocks with breathing room
        const positions = [
            [-3.2, 2.7, 0],
            [0, 3.2, 0.4],
            [3.2, 2.7, 0]
        ];

        positions.forEach((pos, idx) => {
            const block = window.mario3D.createQuestionBlock(1.6);
            block.position.set(pos[0], pos[1], pos[2]);
            block.userData.baseY = pos[1];
            block.userData.idx = idx;
            this.scene.add(block);
            this.blocks.push(block);
            this.interactiveObjects.push(block.userData.mesh);
        });

        // Floating spinning coins above each block
        this.idleCoins = [];
        positions.forEach(pos => {
            const coin = window.mario3D.createCoin(0.7, 0.16);
            coin.position.set(pos[0], pos[1] + 2.4, pos[2]);
            this.scene.add(coin);
            this.idleCoins.push(coin);
        });
    }

    initEvents() {
        window.addEventListener('resize', () => {
            if (!this.canvas) return;
            this.camera.aspect = window.innerWidth / window.innerHeight;
            this.camera.updateProjectionMatrix();
            this.renderer.setSize(window.innerWidth, window.innerHeight);
        });

        window.addEventListener('mousemove', (e) => {
            this.mouse.x = (e.clientX / window.innerWidth) * 2 - 1;
            this.mouse.y = -(e.clientY / window.innerHeight) * 2 + 1;
        });

        this.canvas.addEventListener('pointerdown', (e) => {
            const rect = this.canvas.getBoundingClientRect();
            const x = ((e.clientX - rect.left) / rect.width) * 2 - 1;
            const y = -((e.clientY - rect.top) / rect.height) * 2 + 1;

            this.raycaster.setFromCamera(new THREE.Vector2(x, y), this.camera);
            const intersects = this.raycaster.intersectObjects(this.interactiveObjects);

            if (intersects.length > 0) {
                const mesh = intersects[0].object;
                const parentBlock = mesh.parent;
                if (parentBlock && !parentBlock.userData.isBumping) {
                    this.triggerBlockHit(parentBlock);
                }
            }
        });
    }

    triggerBlockHit(block) {
        block.userData.isBumping = true;
        block.userData.bumpTime = 0;

        // Play coin audio
        if (window.soundFx) {
            window.soundFx.playCoin();
        }

        // Spawn flying coin
        this.spawnPoppedCoin(block.position.x, block.position.y + 1.2, block.position.z);

        // Update HUD coin count if available
        const coinElem = document.getElementById('hud-coins-val');
        if (coinElem) {
            let cur = parseInt(coinElem.innerText) || 100;
            coinElem.innerText = cur + 1;
            coinElem.classList.add('pulse-gold');
            setTimeout(() => coinElem.classList.remove('pulse-gold'), 400);
        }
    }

    spawnPoppedCoin(x, y, z) {
        const coin = window.mario3D.createCoin(0.8, 0.18);
        coin.position.set(x, y, z);
        this.scene.add(coin);

        this.poppedCoins.push({
            mesh: coin,
            vy: 8.5,
            life: 0,
            maxLife: 0.7
        });
    }

    animate() {
        requestAnimationFrame(() => this.animate());

        const delta = Math.min(this.clock.getDelta(), 0.1);
        const time = this.clock.getElapsedTime();

        // Parallax camera easing
        const targetCamX = this.mouse.x * 2.2;
        const targetCamY = 4.5 + this.mouse.y * 1.5;
        this.camera.position.x += (targetCamX - this.camera.position.x) * 0.05;
        this.camera.position.y += (targetCamY - this.camera.position.y) * 0.05;
        this.camera.lookAt(0, 2.5, 0);

        // Update Matrix Particles
        if (this.particles && this.particles.userData.update) {
            this.particles.userData.update(delta);
        }

        // Idle floating coins
        this.idleCoins.forEach((coin, i) => {
            coin.rotation.y += delta * 3.0;
            coin.position.y = (this.blocks[i] ? this.blocks[i].userData.baseY : 3.0) + 2.2 + Math.sin(time * 3 + i) * 0.18;
        });

        // Bouncing question blocks
        this.blocks.forEach(block => {
            if (block.userData.isBumping) {
                block.userData.bumpTime += delta * 9;
                const bumpProgress = block.userData.bumpTime;
                if (bumpProgress < Math.PI) {
                    block.position.y = block.userData.baseY + Math.sin(bumpProgress) * 0.65;
                } else {
                    block.position.y = block.userData.baseY;
                    block.userData.isBumping = false;
                }
            } else {
                // Subtle breathing float
                block.position.y = block.userData.baseY + Math.sin(time * 2 + block.userData.idx) * 0.08;
            }
        });

        // Popped coins update
        for (let i = this.poppedCoins.length - 1; i >= 0; i--) {
            const p = this.poppedCoins[i];
            p.life += delta;
            p.mesh.position.y += p.vy * delta;
            p.vy -= 16.0 * delta; // Gravity
            p.mesh.rotation.y += delta * 18;

            if (p.life >= p.maxLife) {
                this.scene.remove(p.mesh);
                p.mesh.traverse(child => {
                    if (child.geometry) child.geometry.dispose();
                });
                this.poppedCoins.splice(i, 1);
            }
        }

        this.renderer.render(this.scene, this.camera);
    }
}

window.addEventListener('DOMContentLoaded', () => {
    if (document.getElementById('title-canvas')) {
        window.titleSceneInstance = new TitleScene('title-canvas');
    }
});
