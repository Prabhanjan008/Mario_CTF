// Mario: The Cyber Heist - 3D Final Boss Arena (Mecha-Shellshock)

class BossScene {
    constructor(canvasId) {
        this.canvas = document.getElementById(canvasId);
        if (!this.canvas) return;

        this.scene = new THREE.Scene();
        this.scene.background = new THREE.Color(0x0a0410);
        this.scene.fog = new THREE.FogExp2(0x0a0410, 0.02);

        this.camera = new THREE.PerspectiveCamera(50, window.innerWidth / window.innerHeight, 0.1, 1000);
        this.camera.position.set(0, 5, 16);

        this.renderer = new THREE.WebGLRenderer({
            canvas: this.canvas,
            antialias: true
        });
        this.renderer.setSize(window.innerWidth, window.innerHeight);
        this.renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));

        this.clock = new THREE.Clock();
        this.isSolved = (this.canvas.dataset.solved === 'true');
        this.shieldsActive = this.isSolved ? [false, false, false, false] : [true, true, true, true];
        this.shieldMeshes = [];

        this.initLights();
        this.initArena();
        this.initBoss();
        if (!this.isSolved) {
            this.initShields();
        } else {
            // Defenses offline: eyes dark, green glow, resting star
            if (this.visorMat) this.visorMat.color.setHex(0x111111);
            if (this.bossLight) this.bossLight.color.setHex(0x00ff66);
            const victoryStar = window.mario3D.createStar(2.2);
            victoryStar.position.set(0, 3.0, 0);
            this.scene.add(victoryStar);
            this.victoryStar = victoryStar;
        }
        this.animate();
    }

    initLights() {
        const ambient = new THREE.AmbientLight(0x331144, 1.2);
        this.scene.add(ambient);

        this.bossLight = new THREE.PointLight(0xff0044, 4.0, 25);
        this.bossLight.position.set(0, 4, 0);
        this.scene.add(this.bossLight);

        const keyLight = new THREE.DirectionalLight(0x00f0ff, 1.5);
        keyLight.position.set(10, 15, 10);
        this.scene.add(keyLight);
    }

    initArena() {
        // Octagonal cyber arena platform
        const arenaGeom = new THREE.CylinderGeometry(14, 15, 2, 8);
        const arenaMat = new THREE.MeshStandardMaterial({
            color: 0x180926,
            roughness: 0.4,
            metalness: 0.6
        });
        const arena = new THREE.Mesh(arenaGeom, arenaMat);
        arena.position.y = -1;
        this.scene.add(arena);

        // Surrounding cyber grid
        const grid = window.mario3D.createCyberGrid(90, 40, 0xbf00ff);
        grid.position.y = -2;
        this.scene.add(grid);

        // Core containment ring
        const coreRingGeom = new THREE.TorusGeometry(13.8, 0.15, 8, 32);
        coreRingGeom.rotateX(Math.PI / 2);
        const coreRingMat = new THREE.MeshBasicMaterial({ color: 0xff0055 });
        const coreRing = new THREE.Mesh(coreRingGeom, coreRingMat);
        coreRing.position.y = 0.05;
        this.scene.add(coreRing);
    }

    initBoss() {
        this.bossGroup = new THREE.Group();
        this.bossGroup.position.set(0, 2.5, 0);

        // Heavy Mecha Turtle Shell
        const shellGeom = new THREE.SphereGeometry(2.4, 24, 16);
        shellGeom.scale(1.2, 1.0, 0.9);
        const shellMat = new THREE.MeshStandardMaterial({
            color: 0x220500,
            roughness: 0.3,
            metalness: 0.8,
            emissive: 0x440800
        });
        this.shell = new THREE.Mesh(shellGeom, shellMat);
        this.bossGroup.add(this.shell);

        // Spikes on Shell
        const spikeCoords = [
            [0, 2.4, 0],
            [1.5, 1.8, 0.8],
            [-1.5, 1.8, 0.8],
            [1.5, 1.8, -0.8],
            [-1.5, 1.8, -0.8],
            [2.2, 0.5, 0],
            [-2.2, 0.5, 0]
        ];
        spikeCoords.forEach(([sx, sy, sz]) => {
            const spikeGeom = new THREE.ConeGeometry(0.35, 1.2, 8);
            const spikeMat = new THREE.MeshStandardMaterial({ color: 0xffddaa, metalness: 0.5 });
            const spike = new THREE.Mesh(spikeGeom, spikeMat);
            spike.position.set(sx, sy, sz);
            spike.lookAt(sx * 2, sy * 2, sz * 2);
            this.bossGroup.add(spike);
        });

        // Mecha Head & Optics
        const headGeom = new THREE.BoxGeometry(1.6, 1.4, 1.8);
        const headMat = new THREE.MeshStandardMaterial({ color: 0x333333, metalness: 0.8, roughness: 0.2 });
        const head = new THREE.Mesh(headGeom, headMat);
        head.position.set(0, 0.8, 2.2);

        // Glowing red cyber visor
        const visorGeom = new THREE.BoxGeometry(1.4, 0.3, 0.2);
        this.visorMat = new THREE.MeshBasicMaterial({ color: 0xff0022 });
        const visor = new THREE.Mesh(visorGeom, this.visorMat);
        visor.position.set(0, 0.2, 0.95);
        head.add(visor);

        this.bossGroup.add(head);

        // Heavy Plasma Cannons
        const cannonGeom = new THREE.CylinderGeometry(0.4, 0.45, 2.5, 16);
        cannonGeom.rotateX(Math.PI / 2);
        const cannonMat = new THREE.MeshStandardMaterial({ color: 0x111111, metalness: 0.9 });

        const leftCannon = new THREE.Mesh(cannonGeom, cannonMat);
        leftCannon.position.set(-2.6, 0.5, 1.0);
        const rightCannon = new THREE.Mesh(cannonGeom, cannonMat);
        rightCannon.position.set(2.6, 0.5, 1.0);

        this.bossGroup.add(leftCannon, rightCannon);
        this.scene.add(this.bossGroup);
    }

    initShields() {
        const shieldColors = [0x00ff66, 0x00f0ff, 0xbf00ff, 0xff3300];
        const radii = [4.2, 5.8, 7.4, 9.0];

        radii.forEach((r, i) => {
            const ringGeom = new THREE.TorusGeometry(r, 0.08, 8, 48);
            ringGeom.rotateX(Math.PI / 2);
            const ringMat = new THREE.MeshBasicMaterial({
                color: shieldColors[i],
                transparent: true,
                opacity: 0.75
            });
            const ring = new THREE.Mesh(ringGeom, ringMat);
            ring.position.y = 2.5;

            // Translucent sphere boundary
            const shellGeom = new THREE.SphereGeometry(r, 16, 12);
            const shellMat = new THREE.MeshBasicMaterial({
                color: shieldColors[i],
                transparent: true,
                opacity: 0.12,
                wireframe: true
            });
            const shieldShell = new THREE.Mesh(shellGeom, shellMat);
            shieldShell.position.y = 2.5;

            const shieldGroup = new THREE.Group();
            shieldGroup.add(ring, shieldShell);

            this.scene.add(shieldGroup);
            this.shieldMeshes.push(shieldGroup);
        });
    }

    breakShield(index) {
        if (!this.shieldsActive[index]) return;
        this.shieldsActive[index] = false;

        const shield = this.shieldMeshes[index];
        if (shield) {
            // Shatter animation
            shield.scale.multiplyScalar(1.5);
            shield.traverse(c => {
                if (c.material) c.material.opacity = 0;
            });
            this.scene.remove(shield);
        }

        if (window.soundFx) {
            window.soundFx.playPowerup();
        }

        // Boss recoil
        this.bossGroup.position.y += 0.8;

        // Check if all shields are broken
        if (this.shieldsActive.every(s => !s)) {
            this.triggerDefeat();
        }
    }

    triggerDefeat() {
        // Turn eyes black, collapse boss
        this.visorMat.color.setHex(0x111111);
        this.bossLight.color.setHex(0x00ff66);

        if (window.soundFx) {
            window.soundFx.playVictory();
        }

        // Spawn descending Golden Star
        const victoryStar = window.mario3D.createStar(2.2);
        victoryStar.position.set(0, 10, 0);
        this.scene.add(victoryStar);
        this.victoryStar = victoryStar;

        // Boss defeat WebGL animation: Eyes go dark, ambient light turns green, Golden Star descends
        // Note: The victory celebration action is strictly revealed after backend flag verification!
    }

    animate() {
        requestAnimationFrame(() => this.animate());

        const delta = Math.min(this.clock.getDelta(), 0.1);
        const time = this.clock.getElapsedTime();

        // Boss breathing float & tracking
        if (this.bossGroup) {
            this.bossGroup.position.y = 2.5 + Math.sin(time * 2.5) * 0.25;
            this.bossGroup.rotation.y = Math.sin(time * 0.8) * 0.35;
        }

        // Rotate active shields
        this.shieldMeshes.forEach((mesh, idx) => {
            if (this.shieldsActive[idx]) {
                mesh.rotation.y += delta * (0.8 + idx * 0.3) * (idx % 2 === 0 ? 1 : -1);
            }
        });

        // Descending victory star
        if (this.victoryStar) {
            this.victoryStar.rotation.y += delta * 2.5;
            if (this.victoryStar.position.y > 3.0) {
                this.victoryStar.position.y -= delta * 3.5;
            }
        }

        this.renderer.render(this.scene, this.camera);
    }
}

window.addEventListener('DOMContentLoaded', () => {
    if (document.getElementById('boss-canvas')) {
        window.bossSceneInstance = new BossScene('boss-canvas');
    }
});
