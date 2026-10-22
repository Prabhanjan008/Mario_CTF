// Shared 3D helpers, lighting, and procedural models built with Three.js.

class Mario3DEngine {
    constructor() {
        this.textures = {};
    }

    // Helper: Generate dynamic canvas texture for 3D Question Block
    getQuestionBlockTexture() {
        if (this.textures.questionBlock) return this.textures.questionBlock;

        const canvas = document.createElement('canvas');
        canvas.width = 256;
        canvas.height = 256;
        const ctx = canvas.getContext('2d');

        // Cyber gold gradient background
        const grad = ctx.createLinearGradient(0, 0, 256, 256);
        grad.addColorStop(0, '#ffcc00');
        grad.addColorStop(0.5, '#e59400');
        grad.addColorStop(1, '#b26500');
        ctx.fillStyle = grad;
        ctx.fillRect(0, 0, 256, 256);

        // Dark bevel border
        ctx.strokeStyle = '#5a3000';
        ctx.lineWidth = 14;
        ctx.strokeRect(7, 7, 242, 242);

        // Inner glowing border
        ctx.strokeStyle = '#fff275';
        ctx.lineWidth = 6;
        ctx.strokeRect(18, 18, 220, 220);

        // 4 corner bolts
        const corners = [[32, 32], [224, 32], [32, 224], [224, 224]];
        corners.forEach(([x, y]) => {
            ctx.fillStyle = '#4a2500';
            ctx.beginPath();
            ctx.arc(x, y, 9, 0, Math.PI * 2);
            ctx.fill();
            ctx.fillStyle = '#fffae0';
            ctx.beginPath();
            ctx.arc(x - 2, y - 2, 4, 0, Math.PI * 2);
            ctx.fill();
        });

        // Question mark shadow
        ctx.font = 'bold 140px "Courier New", monospace';
        ctx.textAlign = 'center';
        ctx.textBaseline = 'middle';
        ctx.fillStyle = '#401f00';
        ctx.fillText('?', 132, 136);

        // Question mark foreground
        ctx.fillStyle = '#ffffff';
        ctx.fillText('?', 128, 130);

        const tex = new THREE.CanvasTexture(canvas);
        tex.colorSpace = THREE.SRGBColorSpace;
        this.textures.questionBlock = tex;
        return tex;
    }

    // Create 3D Question Mark Block
    createQuestionBlock(size = 2) {
        const group = new THREE.Group();
        const tex = this.getQuestionBlockTexture();

        const mat = new THREE.MeshStandardMaterial({
            map: tex,
            roughness: 0.35,
            metalness: 0.45,
            emissive: new THREE.Color(0x332200)
        });

        const geom = new THREE.BoxGeometry(size, size, size);
        const mesh = new THREE.Mesh(geom, mat);
        mesh.castShadow = true;
        mesh.receiveShadow = true;
        group.add(mesh);

        // Bounding box / interactive data
        group.userData = {
            mesh: mesh,
            baseY: 0,
            isBumping: false,
            bumpTime: 0,
            type: 'question_block'
        };

        return group;
    }

    // Create 3D Gold Coin
    createCoin(radius = 0.9, thickness = 0.22) {
        const group = new THREE.Group();

        const geom = new THREE.CylinderGeometry(radius, radius, thickness, 32);
        // Rotate so coin face stands vertically
        geom.rotateX(Math.PI / 2);

        const mat = new THREE.MeshStandardMaterial({
            color: 0xffcc00,
            roughness: 0.2,
            metalness: 0.85,
            emissive: 0x664400
        });

        const mesh = new THREE.Mesh(geom, mat);
        mesh.castShadow = true;
        group.add(mesh);

        // Inner ridge detailing
        const innerGeom = new THREE.TorusGeometry(radius * 0.72, 0.05, 16, 32);
        const innerMat = new THREE.MeshStandardMaterial({
            color: 0xffeb60,
            roughness: 0.3,
            metalness: 0.9
        });
        const ridge = new THREE.Mesh(innerGeom, innerMat);
        group.add(ridge);

        group.userData = {
            type: 'coin',
            spinSpeed: 2.5
        };

        return group;
    }

    // Create 3D Cyber Warp Pipe
    createWarpPipe(height = 3.5, radius = 1.3) {
        const group = new THREE.Group();

        // Main pipe body
        const bodyGeom = new THREE.CylinderGeometry(radius, radius, height, 32);
        const pipeMat = new THREE.MeshStandardMaterial({
            color: 0x00cc44,
            roughness: 0.3,
            metalness: 0.5,
            emissive: 0x003311
        });
        const bodyMesh = new THREE.Mesh(bodyGeom, pipeMat);
        bodyMesh.position.y = height / 2;
        bodyMesh.castShadow = true;
        group.add(bodyMesh);

        // Top collar / rim
        const lipHeight = height * 0.28;
        const lipRadius = radius * 1.25;
        const lipGeom = new THREE.CylinderGeometry(lipRadius, lipRadius, lipHeight, 32);
        const lipMesh = new THREE.Mesh(lipGeom, pipeMat);
        lipMesh.position.y = height - (lipHeight / 2);
        lipMesh.castShadow = true;
        group.add(lipMesh);

        // Cyber neon ring inside the rim
        const rimRingGeom = new THREE.TorusGeometry(radius * 1.05, 0.08, 16, 32);
        rimRingGeom.rotateX(Math.PI / 2);
        const rimMat = new THREE.MeshBasicMaterial({
            color: 0x00ff88
        });
        const rimRing = new THREE.Mesh(rimRingGeom, rimMat);
        rimRing.position.y = height + 0.02;
        group.add(rimRing);

        // Interior void cylinder
        const voidGeom = new THREE.CylinderGeometry(radius * 0.95, radius * 0.95, 0.3, 32);
        const voidMat = new THREE.MeshBasicMaterial({ color: 0x020a05 });
        const voidMesh = new THREE.Mesh(voidGeom, voidMat);
        voidMesh.position.y = height - 0.05;
        group.add(voidMesh);

        return group;
    }

    // Create 3D Golden Star
    createStar(size = 1.2) {
        const group = new THREE.Group();

        // Build 5-pointed star shape
        const shape = new THREE.Shape();
        const points = 5;
        const outerR = size;
        const innerR = size * 0.45;

        for (let i = 0; i < points * 2; i++) {
            const r = (i % 2 === 0) ? outerR : innerR;
            const a = (i / (points * 2)) * Math.PI * 2 - Math.PI / 2;
            const x = Math.cos(a) * r;
            const y = Math.sin(a) * r;
            if (i === 0) shape.moveTo(x, y);
            else shape.lineTo(x, y);
        }
        shape.closePath();

        const extrudeSettings = {
            depth: size * 0.3,
            bevelEnabled: true,
            bevelSegments: 3,
            steps: 1,
            bevelSize: size * 0.08,
            bevelThickness: size * 0.08
        };

        const geom = new THREE.ExtrudeGeometry(shape, extrudeSettings);
        geom.center();

        const mat = new THREE.MeshStandardMaterial({
            color: 0xffe600,
            emissive: 0xffaa00,
            emissiveIntensity: 0.7,
            roughness: 0.15,
            metalness: 0.8
        });

        const mesh = new THREE.Mesh(geom, mat);
        mesh.castShadow = true;
        group.add(mesh);

        // Eyes (Classic Mario star eyes)
        const eyeMat = new THREE.MeshBasicMaterial({ color: 0x000000 });
        const eyeGeom = new THREE.CylinderGeometry(0.06, 0.06, 0.28, 16);
        eyeGeom.rotateX(Math.PI / 2);

        const leftEye = new THREE.Mesh(eyeGeom, eyeMat);
        leftEye.position.set(-0.25, 0.1, (size * 0.3) / 2 + 0.06);
        group.add(leftEye);

        const rightEye = new THREE.Mesh(eyeGeom, eyeMat);
        rightEye.position.set(0.25, 0.1, (size * 0.3) / 2 + 0.06);
        group.add(rightEye);

        // Point light inside star
        const starLight = new THREE.PointLight(0xffe600, 1.5, 8);
        group.add(starLight);

        group.userData = {
            type: 'star',
            light: starLight
        };

        return group;
    }

    // Create 3D Cyber Mushroom
    createMushroom(color = 0xff2a4d) {
        const group = new THREE.Group();

        // Stem
        const stemGeom = new THREE.CylinderGeometry(0.7, 0.9, 1.1, 24);
        const stemMat = new THREE.MeshStandardMaterial({
            color: 0xfff3db,
            roughness: 0.5,
            metalness: 0.1
        });
        const stem = new THREE.Mesh(stemGeom, stemMat);
        stem.position.y = 0.55;
        group.add(stem);

        // Cap hemisphere
        const capGeom = new THREE.SphereGeometry(1.25, 24, 16, 0, Math.PI * 2, 0, Math.PI / 2);
        const capMat = new THREE.MeshStandardMaterial({
            color: color,
            roughness: 0.3,
            metalness: 0.2,
            emissive: 0x330011
        });
        const cap = new THREE.Mesh(capGeom, capMat);
        cap.position.y = 1.05;
        group.add(cap);

        // Spots on cap
        const spotMat = new THREE.MeshBasicMaterial({ color: 0xffffff });
        const spotCoords = [
            [0, 2.25, 0, 0.45],
            [0.85, 1.6, 0.6, 0.35],
            [-0.85, 1.6, 0.6, 0.35],
            [0.85, 1.6, -0.6, 0.35],
            [-0.85, 1.6, -0.6, 0.35]
        ];

        spotCoords.forEach(([x, y, z, r]) => {
            const spotGeom = new THREE.SphereGeometry(r, 12, 12);
            const spot = new THREE.Mesh(spotGeom, spotMat);
            spot.position.set(x, y, z);
            group.add(spot);
        });

        return group;
    }

    // Create 3D Detective Mario Character Avatar
    createDetectiveAvatar() {
        const group = new THREE.Group();

        // Body / Blue overalls
        const bodyGeom = new THREE.BoxGeometry(0.9, 1.0, 0.6);
        const overallMat = new THREE.MeshStandardMaterial({ color: 0x0044cc, roughness: 0.4 });
        const body = new THREE.Mesh(bodyGeom, overallMat);
        body.position.y = 1.1;
        group.add(body);

        // Red shirt underneath
        const shirtGeom = new THREE.BoxGeometry(1.05, 0.5, 0.65);
        const shirtMat = new THREE.MeshStandardMaterial({ color: 0xcc0011, roughness: 0.4 });
        const shirt = new THREE.Mesh(shirtGeom, shirtMat);
        shirt.position.y = 1.25;
        group.add(shirt);

        // Head
        const headGeom = new THREE.BoxGeometry(0.8, 0.75, 0.75);
        const skinMat = new THREE.MeshStandardMaterial({ color: 0xffc499, roughness: 0.6 });
        const head = new THREE.Mesh(headGeom, skinMat);
        head.position.y = 1.95;
        group.add(head);

        // Mario Red Detective Cap
        const capGeom = new THREE.BoxGeometry(0.95, 0.35, 0.95);
        const cap = new THREE.Mesh(capGeom, shirtMat);
        cap.position.y = 2.4;
        group.add(cap);

        // Cap Visor
        const visorGeom = new THREE.BoxGeometry(0.85, 0.08, 0.4);
        const visor = new THREE.Mesh(visorGeom, shirtMat);
        visor.position.set(0, 2.25, 0.55);
        group.add(visor);

        // Moustache
        const stacheGeom = new THREE.BoxGeometry(0.55, 0.15, 0.15);
        const hairMat = new THREE.MeshBasicMaterial({ color: 0x221105 });
        const stache = new THREE.Mesh(stacheGeom, hairMat);
        stache.position.set(0, 1.85, 0.42);
        group.add(stache);

        // Nose
        const noseGeom = new THREE.SphereGeometry(0.18, 12, 12);
        const nose = new THREE.Mesh(noseGeom, skinMat);
        nose.position.set(0, 1.98, 0.45);
        group.add(nose);

        // Legs & Shoes
        const legGeom = new THREE.BoxGeometry(0.35, 0.6, 0.45);
        const shoeGeom = new THREE.BoxGeometry(0.38, 0.25, 0.6);
        const shoeMat = new THREE.MeshStandardMaterial({ color: 0x4a2500, roughness: 0.5 });

        const leftLeg = new THREE.Mesh(legGeom, overallMat);
        leftLeg.position.set(-0.25, 0.45, 0);
        const leftShoe = new THREE.Mesh(shoeGeom, shoeMat);
        leftShoe.position.set(-0.25, 0.12, 0.08);
        group.add(leftLeg, leftShoe);

        const rightLeg = new THREE.Mesh(legGeom, overallMat);
        rightLeg.position.set(0.25, 0.45, 0);
        const rightShoe = new THREE.Mesh(shoeGeom, shoeMat);
        rightShoe.position.set(0.25, 0.12, 0.08);
        group.add(rightLeg, rightShoe);

        // Holographic Magnifying Glass
        const lensRimGeom = new THREE.TorusGeometry(0.28, 0.04, 16, 24);
        const rimMat = new THREE.MeshStandardMaterial({ color: 0x00ffff, metalness: 0.8 });
        const lensRim = new THREE.Mesh(lensRimGeom, rimMat);
        lensRim.position.set(0.65, 1.5, 0.4);

        const glassGeom = new THREE.CircleGeometry(0.26, 24);
        const glassMat = new THREE.MeshBasicMaterial({
            color: 0x00f0ff,
            transparent: true,
            opacity: 0.45,
            side: THREE.DoubleSide
        });
        const glass = new THREE.Mesh(glassGeom, glassMat);
        glass.position.copy(lensRim.position);

        const handleGeom = new THREE.CylinderGeometry(0.04, 0.04, 0.35);
        const handle = new THREE.Mesh(handleGeom, shoeMat);
        handle.position.set(0.8, 1.3, 0.4);
        handle.rotation.z = -Math.PI / 4;

        group.add(lensRim, glass, handle);

        // Scale & tag
        group.scale.set(0.85, 0.85, 0.85);
        group.userData = {
            type: 'mario_avatar',
            walkCycle: 0
        };

        return group;
    }

    // Create 3D Cyber Matrix Particle Field
    createMatrixParticles(count = 700, range = 40) {
        const geom = new THREE.BufferGeometry();
        const positions = new Float32Array(count * 3);
        const colors = new Float32Array(count * 3);

        const palette = [
            new THREE.Color(0x00ff66), // Cyber Green
            new THREE.Color(0x00f0ff), // Cyan
            new THREE.Color(0xffcc00), // Gold
            new THREE.Color(0xff2a4d)  // Mario Red
        ];

        for (let i = 0; i < count; i++) {
            positions[i * 3] = (Math.random() - 0.5) * range;
            positions[i * 3 + 1] = Math.random() * (range * 0.7) - 2;
            positions[i * 3 + 2] = (Math.random() - 0.5) * range;

            const col = palette[Math.floor(Math.random() * palette.length)];
            colors[i * 3] = col.r;
            colors[i * 3 + 1] = col.g;
            colors[i * 3 + 2] = col.b;
        }

        geom.setAttribute('position', new THREE.BufferAttribute(positions, 3));
        geom.setAttribute('color', new THREE.BufferAttribute(colors, 3));

        const mat = new THREE.PointsMaterial({
            size: 0.22,
            vertexColors: true,
            transparent: true,
            opacity: 0.85,
            blending: THREE.AdditiveBlending
        });

        const points = new THREE.Points(geom, mat);
        points.userData = {
            update: (delta) => {
                const pos = geom.attributes.position.array;
                for (let i = 0; i < count; i++) {
                    pos[i * 3 + 1] -= delta * 3.5;
                    if (pos[i * 3 + 1] < -2) {
                        pos[i * 3 + 1] = range * 0.7;
                    }
                }
                geom.attributes.position.needsUpdate = true;
            }
        };

        return points;
    }

    // Create Cyber Grid Plane
    createCyberGrid(size = 100, divisions = 50, color = 0x00ff66) {
        const grid = new THREE.GridHelper(size, divisions, color, 0x003318);
        grid.position.y = -0.01;
        return grid;
    }
}

// Global 3D Engine factory instance
window.mario3D = new Mario3DEngine();
