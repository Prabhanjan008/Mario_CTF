// Mario: The Cyber Heist - 3D Opening Cinematic Cutscene

class CinematicScene {
    constructor(overlayId, canvasId) {
        this.overlay = document.getElementById(overlayId);
        this.canvas = document.getElementById(canvasId);
        if (!this.canvas || !this.overlay) return;

        this.scene = new THREE.Scene();
        this.scene.background = new THREE.Color(0x04060f);
        this.scene.fog = new THREE.FogExp2(0x04060f, 0.03);

        this.camera = new THREE.PerspectiveCamera(50, window.innerWidth / window.innerHeight, 0.1, 1000);
        this.renderer = new THREE.WebGLRenderer({
            canvas: this.canvas,
            antialias: true
        });
        this.renderer.setSize(window.innerWidth, window.innerHeight);
        this.renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));

        this.clock = new THREE.Clock();
        this.isPlaying = false;
        this.sceneTime = 0;

        this.subtitleEl = document.getElementById('cinematic-subtitle');
        this.actionBtn = document.getElementById('cinematic-action-btn');

        this.initVault();
    }

    initVault() {
        // Vault Pedestal
        const pedGeom = new THREE.CylinderGeometry(2.5, 3.2, 1.8, 32);
        const pedMat = new THREE.MeshStandardMaterial({
            color: 0x111c33,
            roughness: 0.3,
            metalness: 0.8
        });
        this.pedestal = new THREE.Mesh(pedGeom, pedMat);
        this.pedestal.position.y = -0.9;
        this.scene.add(this.pedestal);

        // Pedestal ring
        const ringGeom = new THREE.TorusGeometry(2.6, 0.08, 16, 48);
        ringGeom.rotateX(Math.PI / 2);
        this.ringMat = new THREE.MeshBasicMaterial({ color: 0x00f0ff });
        this.pedRing = new THREE.Mesh(ringGeom, this.ringMat);
        this.pedRing.position.y = 0.02;
        this.scene.add(this.pedRing);

        // The Golden Star
        this.star = window.mario3D.createStar(1.6);
        this.star.position.set(0, 1.6, 0);
        this.scene.add(this.star);

        // Security Energy Shield
        const shieldGeom = new THREE.SphereGeometry(2.2, 32, 24);
        this.shieldMat = new THREE.MeshBasicMaterial({
            color: 0x00ffff,
            transparent: true,
            opacity: 0.35,
            wireframe: true
        });
        this.shield = new THREE.Mesh(shieldGeom, this.shieldMat);
        this.shield.position.set(0, 1.6, 0);
        this.scene.add(this.shield);

        // Lighting
        this.ambient = new THREE.AmbientLight(0x223355, 1.0);
        this.scene.add(this.ambient);

        this.alertLight = new THREE.PointLight(0x00ffff, 4, 30);
        this.alertLight.position.set(0, 7, 0);
        this.scene.add(this.alertLight);

        // Cyber Grid Floor
        this.grid = window.mario3D.createCyberGrid(80, 40, 0x0088ff);
        this.grid.position.y = -1.8;
        this.scene.add(this.grid);

        // Intruder Hologram Mesh (hidden initially)
        const intruderGeom = new THREE.CylinderGeometry(0.8, 1.2, 2.8, 16);
        this.intruderMat = new THREE.MeshBasicMaterial({
            color: 0xff0044,
            transparent: true,
            opacity: 0,
            wireframe: true
        });
        this.intruder = new THREE.Mesh(intruderGeom, this.intruderMat);
        this.intruder.position.set(0, 2.5, 0);
        this.scene.add(this.intruder);

        // Detective Mario (appears in final phase)
        this.mario = window.mario3D.createDetectiveAvatar();
        this.mario.position.set(0, -1.8, 8);
        this.mario.scale.set(0, 0, 0); // hidden
        this.scene.add(this.mario);
    }

    start() {
        this.overlay.classList.remove('hidden');
        this.isPlaying = true;
        this.sceneTime = 0;
        this.clock.start();

        if (window.soundFx) {
            window.soundFx.init();
        }

        this.animate();
    }

    setSubtitle(text, isAlert = false) {
        if (!this.subtitleEl) return;
        this.subtitleEl.innerHTML = text;
        if (isAlert) {
            this.subtitleEl.classList.add('subtitle-alert');
        } else {
            this.subtitleEl.classList.remove('subtitle-alert');
        }
    }

    animate() {
        if (!this.isPlaying) return;
        requestAnimationFrame(() => this.animate());

        const delta = Math.min(this.clock.getDelta(), 0.1);
        this.sceneTime += delta;
        const t = this.sceneTime;

        // Phase 1 (0s - 3s): Tranquil vault pan
        if (t < 3.2) {
            const angle = t * 0.45;
            this.camera.position.x = Math.sin(angle) * 7.5;
            this.camera.position.z = Math.cos(angle) * 7.5;
            this.camera.position.y = 2.4 + Math.sin(t) * 0.4;
            this.camera.lookAt(0, 1.4, 0);

            this.star.rotation.y += delta * 1.8;
            this.shield.rotation.y += delta * 0.5;

            if (t < 1.0) {
                this.setSubtitle("VAULT SECTOR 00: MUSHROOM KINGDOM MASTER SANCTUM");
            } else {
                this.setSubtitle("ALL QUANTUM CONTAINMENT PROTOCOLS NOMINAL. GOLDEN STAR SECURED.");
            }
        }
        // Phase 2 (3.2s - 6.5s): Red Alert & Breach!
        else if (t >= 3.2 && t < 7.0) {
            if (t < 3.4) {
                if (window.soundFx) window.soundFx.playAlert();
            }

            // Flashing red emergency lights
            const flash = (Math.sin(t * 14) > 0);
            this.alertLight.color.setHex(flash ? 0xff0033 : 0x220008);
            this.alertLight.intensity = flash ? 8 : 1;
            this.ringMat.color.setHex(flash ? 0xff0033 : 0x440011);

            this.setSubtitle("⚠️ CRITICAL ALARM: ROGUE QUANTUM INTRUDER BREACHING FIREWALL!", true);

            // Intruder materializes
            const breachT = (t - 3.2) / 3.8;
            this.intruderMat.opacity = Math.min(0.85, breachT * 1.5);
            this.intruder.rotation.y += delta * 6;

            // Shield shatters
            if (t > 4.8) {
                this.shield.scale.multiplyScalar(1.0 + delta * 3);
                this.shieldMat.opacity = Math.max(0, 0.4 - (t - 4.8) * 0.8);
                if (t < 5.0 && window.soundFx) {
                    window.soundFx.playError();
                }
            }

            // Intruder snatches Star
            if (t > 5.5) {
                this.star.position.y += delta * 4;
                this.star.scale.multiplyScalar(Math.max(0.01, 1.0 - delta * 2.5));
            }

            this.camera.position.set(0, 3.2, 8.5);
            this.camera.lookAt(0, 2.0, 0);
        }
        // Phase 3 (7.0s - 10.0s): Intruder warps away & leaves trace
        else if (t >= 7.0 && t < 10.5) {
            if (t < 7.2 && window.soundFx) {
                window.soundFx.playWarpPipe();
            }

            // Intruder vanishes
            this.intruderMat.opacity = Math.max(0, this.intruderMat.opacity - delta * 3);
            this.star.visible = false;

            this.setSubtitle("TRACE INTERCEPTED: INTRUDER SIGNATURE 'PHANTOM_SHROOM' ESCAPED TOWARDS SECTOR 01!");

            // Camera sweeps back to reveal Inspector Mario
            this.camera.position.x = 0;
            this.camera.position.y = 1.2;
            this.camera.position.z = 10.5;
            this.camera.lookAt(0, 1.2, 5);

            this.mario.scale.set(0.9, 0.9, 0.9);
            this.mario.position.z = Math.max(5.5, 8 - (t - 7.0) * 1.2);
        }
        // Phase 4 (10.5s+): Mario Investigation Call
        else {
            this.setSubtitle("INSPECTOR MARIO: 'The Golden Star has been compromised. Commencing Cyber Heist Investigation.'");
            if (this.actionBtn) {
                this.actionBtn.classList.remove('hidden');
            }
        }

        this.renderer.render(this.scene, this.camera);
    }

    skip() {
        this.isPlaying = false;
        window.location.href = '/briefing';
    }
}

window.addEventListener('DOMContentLoaded', () => {
    if (document.getElementById('cinematic-canvas')) {
        window.cinematicSceneInstance = new CinematicScene('cinematic-modal', 'cinematic-canvas');
    }
});
