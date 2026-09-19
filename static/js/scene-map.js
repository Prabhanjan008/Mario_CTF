// Mario: The Cyber Heist - 3D Interactive World Map Engine

class WorldMapScene {
    constructor(canvasId, worldsData, initialWorldId = 1) {
        this.canvas = document.getElementById(canvasId);
        if (!this.canvas) return;

        this.worldsData = worldsData || [];
        this.currentWorldId = initialWorldId;

        this.scene = new THREE.Scene();
        this.scene.background = new THREE.Color(0x060914);
        this.scene.fog = new THREE.FogExp2(0x060914, 0.015);

        this.camera = new THREE.PerspectiveCamera(45, window.innerWidth / window.innerHeight, 0.5, 1000);
        this.camera.position.set(0, 35, 48);
        this.camera.lookAt(0, 0, 0);

        this.renderer = new THREE.WebGLRenderer({
            canvas: this.canvas,
            antialias: true
        });
        this.renderer.setSize(window.innerWidth, window.innerHeight);
        this.renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
        this.renderer.shadowMap.enabled = true;

        this.clock = new THREE.Clock();
        this.raycaster = new THREE.Raycaster();
        this.mouse = new THREE.Vector2();

        this.islands = {};
        this.islandMeshes = [];
        this.avatar = null;
        this.targetAvatarPos = new THREE.Vector3();

        // Island 3D Coordinates in the world
        this.sectorPositions = {
            1: new THREE.Vector3(-22, 0, 16),    // Mushroom Village (SW)
            2: new THREE.Vector3(-14, 2, -10),   // Dark Forest (NW)
            3: new THREE.Vector3(12, 3, -16),    // Haunted Mansion (N)
            4: new THREE.Vector3(22, 1, 6),      // Koopa HQ (SE)
            5: new THREE.Vector3(0, 7, -2)       // Final Fortress (Center High)
        };

        this.initLights();
        this.initEnvironment();
        this.initIslands();
        this.initCircuitPaths();
        this.initAvatar();
        this.initControls();
        this.animate();

        // Focus on current world
        this.selectSector(this.currentWorldId, false);
    }

    initLights() {
        const ambient = new THREE.AmbientLight(0x223355, 1.4);
        this.scene.add(ambient);

        const sun = new THREE.DirectionalLight(0x00f0ff, 2.0);
        sun.position.set(30, 40, 30);
        sun.castShadow = true;
        this.scene.add(sun);

        const rim = new THREE.DirectionalLight(0xff2a4d, 1.2);
        rim.position.set(-30, 20, -30);
        this.scene.add(rim);
    }

    initEnvironment() {
        // Deep background cyber grid
        const grid = window.mario3D.createCyberGrid(180, 60, 0x00ff66);
        grid.position.y = -10;
        this.scene.add(grid);

        // Ambient cyber floating data dust
        this.particles = window.mario3D.createMatrixParticles(600, 70);
        this.scene.add(this.particles);
    }

    initIslands() {
        this.worldsData.forEach(w => {
            const pos = this.sectorPositions[w.id];
            const group = new THREE.Group();
            group.position.copy(pos);

            // Base floating rock geometry
            const rockGeom = new THREE.CylinderGeometry(5.5, 3.8, 3.2, 7);
            const rockMat = new THREE.MeshStandardMaterial({
                color: 0x121a2d,
                roughness: 0.8,
                metalness: 0.2
            });
            const rock = new THREE.Mesh(rockGeom, rockMat);
            rock.position.y = -1.6;
            rock.receiveShadow = true;
            group.add(rock);

            // Themed surface plate
            let surfaceColor = 0x00ff66;
            if (w.id === 2) surfaceColor = 0x00e5ff;
            if (w.id === 3) surfaceColor = 0xbf00ff;
            if (w.id === 4) surfaceColor = 0xff3300;
            if (w.id === 5) surfaceColor = 0xffcc00;

            const surfGeom = new THREE.CylinderGeometry(5.6, 5.6, 0.4, 7);
            const surfMat = new THREE.MeshStandardMaterial({
                color: surfaceColor,
                roughness: 0.4,
                metalness: 0.3,
                emissive: surfaceColor,
                emissiveIntensity: 0.2
            });
            const surf = new THREE.Mesh(surfGeom, surfMat);
            surf.receiveShadow = true;
            group.add(surf);

            // Themed props on top of island
            this.buildIslandProps(w.id, group);

            // Lock Shield & Holographic Padlock if locked
            if (!w.is_unlocked) {
                const shieldGeom = new THREE.SphereGeometry(6.2, 16, 12);
                const shieldMat = new THREE.MeshBasicMaterial({
                    color: 0xff0044,
                    transparent: true,
                    opacity: 0.25,
                    wireframe: true
                });
                const shield = new THREE.Mesh(shieldGeom, shieldMat);
                shield.position.y = 2.0;
                group.add(shield);

                // Floating Lock icon mesh
                const lockGeom = new THREE.BoxGeometry(1.6, 1.4, 0.6);
                const lockMat = new THREE.MeshStandardMaterial({ color: 0xff2a4d, roughness: 0.3 });
                const lockBody = new THREE.Mesh(lockGeom, lockMat);
                lockBody.position.y = 5.0;

                const shackleGeom = new THREE.TorusGeometry(0.6, 0.15, 8, 16, Math.PI);
                const shackle = new THREE.Mesh(shackleGeom, lockMat);
                shackle.position.set(0, 0.7, 0);
                lockBody.add(shackle);

                group.add(lockBody);
                group.userData.lock = lockBody;
            }

            // Interactive tag
            group.userData.world = w;
            surf.userData.world = w;
            rock.userData.world = w;

            this.scene.add(group);
            this.islands[w.id] = group;
            this.islandMeshes.push(surf, rock);
        });
    }

    buildIslandProps(worldId, group) {
        if (worldId === 1) { // Mushroom Village
            const pipe = window.mario3D.createWarpPipe(2.4, 0.85);
            pipe.position.set(-2, 0.2, -1);
            group.add(pipe);

            const qb = window.mario3D.createQuestionBlock(1.4);
            qb.position.set(1.5, 2.0, 0);
            group.add(qb);

            const shroom = window.mario3D.createMushroom(0xff2a4d);
            shroom.scale.set(0.5, 0.5, 0.5);
            shroom.position.set(-0.5, 0.2, 2.0);
            group.add(shroom);
        } else if (worldId === 2) { // Dark Forest
            // Low-poly cyber pines
            const pineCoords = [[-2, 0, -2], [2, 0, -1], [0, 0, 2], [-1.5, 0, 1.5]];
            pineCoords.forEach(([px, py, pz]) => {
                const pineGeom = new THREE.ConeGeometry(1.3, 3.2, 5);
                const pineMat = new THREE.MeshStandardMaterial({ color: 0x005577, roughness: 0.4 });
                const pine = new THREE.Mesh(pineGeom, pineMat);
                pine.position.set(px, 1.6, pz);
                group.add(pine);
            });
        } else if (worldId === 3) { // Haunted Mansion
            // Spooky cyber tower
            const towerGeom = new THREE.BoxGeometry(2.4, 4.5, 2.4);
            const towerMat = new THREE.MeshStandardMaterial({ color: 0x330044, roughness: 0.5 });
            const tower = new THREE.Mesh(towerGeom, towerMat);
            tower.position.set(0, 2.25, 0);
            group.add(tower);

            const spireGeom = new THREE.ConeGeometry(1.8, 2.8, 4);
            const spireMat = new THREE.MeshStandardMaterial({ color: 0x8800bb });
            const spire = new THREE.Mesh(spireGeom, spireMat);
            spire.position.set(0, 5.8, 0);
            group.add(spire);
        } else if (worldId === 4) { // Koopa HQ
            // Industrial bastion
            const bastionGeom = new THREE.CylinderGeometry(2.2, 2.8, 3.5, 6);
            const bastionMat = new THREE.MeshStandardMaterial({ color: 0x331100, metalness: 0.7, roughness: 0.3 });
            const bastion = new THREE.Mesh(bastionGeom, bastionMat);
            bastion.position.set(0, 1.75, 0);
            group.add(bastion);

            const shellSigilGeom = new THREE.TorusGeometry(1.4, 0.15, 8, 24);
            const sigilMat = new THREE.MeshBasicMaterial({ color: 0xff3300 });
            const sigil = new THREE.Mesh(shellSigilGeom, sigilMat);
            sigil.position.set(0, 3.6, 0);
            sigil.rotation.x = Math.PI / 2;
            group.add(sigil);
        } else if (worldId === 5) { // Final Citadel
            // Grand central citadel with spinning quantum rings
            const baseCitadelGeom = new THREE.CylinderGeometry(2.8, 3.8, 5.5, 8);
            const citadelMat = new THREE.MeshStandardMaterial({
                color: 0x221144,
                roughness: 0.2,
                metalness: 0.8
            });
            const citadel = new THREE.Mesh(baseCitadelGeom, citadelMat);
            citadel.position.set(0, 2.75, 0);
            group.add(citadel);

            // Floating Golden Star beacon atop fortress
            const star = window.mario3D.createStar(1.8);
            star.position.set(0, 7.5, 0);
            group.add(star);
            group.userData.star = star;

            // Rotating quantum rings
            const ring1Geom = new THREE.TorusGeometry(4.0, 0.12, 16, 48);
            const ringMat = new THREE.MeshBasicMaterial({ color: 0xffcc00 });
            const r1 = new THREE.Mesh(ring1Geom, ringMat);
            r1.position.y = 5.0;
            group.add(r1);
            group.userData.ring1 = r1;
        }
    }

    initCircuitPaths() {
        // Paths from 1 -> 2 -> 3 -> 4 -> 5
        const connections = [
            [1, 2],
            [2, 3],
            [3, 4],
            [4, 5],
            [1, 5]
        ];

        connections.forEach(([fromId, toId]) => {
            const p1 = this.sectorPositions[fromId].clone();
            const p2 = this.sectorPositions[toId].clone();
            p1.y += 0.2;
            p2.y += 0.2;

            // Curved 3D spline
            const mid = new THREE.Vector3().addVectors(p1, p2).multiplyScalar(0.5);
            mid.y += 3.0;

            const curve = new THREE.QuadraticBezierCurve3(p1, mid, p2);
            const points = curve.getPoints(30);
            const pathGeom = new THREE.BufferGeometry().setFromPoints(points);
            const pathMat = new THREE.LineBasicMaterial({
                color: 0x00f0ff,
                transparent: true,
                opacity: 0.5,
                linewidth: 2
            });
            const line = new THREE.Line(pathGeom, pathMat);
            this.scene.add(line);
        });
    }

    initAvatar() {
        this.avatar = window.mario3D.createDetectiveAvatar();
        const startPos = this.sectorPositions[this.currentWorldId].clone();
        startPos.y += 0.5;
        this.avatar.position.copy(startPos);
        this.targetAvatarPos.copy(startPos);
        this.scene.add(this.avatar);
    }

    initControls() {
        window.addEventListener('resize', () => {
            if (!this.canvas) return;
            this.camera.aspect = window.innerWidth / window.innerHeight;
            this.camera.updateProjectionMatrix();
            this.renderer.setSize(window.innerWidth, window.innerHeight);
        });

        this.canvas.addEventListener('pointerdown', (e) => {
            const rect = this.canvas.getBoundingClientRect();
            const x = ((e.clientX - rect.left) / rect.width) * 2 - 1;
            const y = -((e.clientY - rect.top) / rect.height) * 2 + 1;

            this.raycaster.setFromCamera(new THREE.Vector2(x, y), this.camera);
            const hits = this.raycaster.intersectObjects(this.islandMeshes, true);

            if (hits.length > 0) {
                let current = hits[0].object;
                while (current && !current.userData.world) {
                    current = current.parent;
                }
                if (current && current.userData.world) {
                    this.selectSector(current.userData.world.id, true);
                }
            }
        });
    }

    selectSector(worldId, playAudio = true) {
        this.currentWorldId = worldId;
        const targetPos = this.sectorPositions[worldId].clone();
        targetPos.y += 0.5;
        this.targetAvatarPos.copy(targetPos);

        if (playAudio && window.soundFx) {
            window.soundFx.playJump();
        }

        // Camera target lerp
        this.targetCamLookAt = this.sectorPositions[worldId].clone();
        this.targetCamPos = new THREE.Vector3(
            this.sectorPositions[worldId].x,
            this.sectorPositions[worldId].y + 14,
            this.sectorPositions[worldId].z + 24
        );

        // Update UI Panel
        this.updateHUD(worldId);
    }

    updateHUD(worldId) {
        const world = this.worldsData.find(w => w.id === worldId);
        if (!world) return;

        const titleEl = document.getElementById('sector-hud-title');
        const subtitleEl = document.getElementById('sector-hud-subtitle');
        const descEl = document.getElementById('sector-hud-desc');
        const badgeEl = document.getElementById('sector-hud-badge');
        const actionBtn = document.getElementById('sector-hud-action');

        if (titleEl) titleEl.innerText = `${world.icon} ${world.name}`;
        if (subtitleEl) subtitleEl.innerText = world.subtitle;
        if (descEl) descEl.innerText = world.description;

        if (badgeEl) {
            if (world.is_unlocked) {
                badgeEl.className = 'sector-badge badge-unlocked';
                badgeEl.innerText = `ACCESS GRANTED (${world.solved_count}/${world.total_challenges} SOLVED)`;
            } else {
                badgeEl.className = 'sector-badge badge-locked';
                badgeEl.innerText = `🔒 ENCRYPTED (REQUIRES ${world.required_stars} STARS)`;
            }
        }

        const listEl = document.getElementById('sector-hud-challenges');
        if (listEl) listEl.innerHTML = '';

        if (actionBtn) {
            if (world.is_unlocked) {
                actionBtn.classList.remove('btn-disabled');
                
                if (world.id === 5) {
                    actionBtn.innerText = "CONFRONT FINAL BOSS ⚔️";
                    actionBtn.onclick = () => window.location.href = '/challenge/12';
                } else {
                    actionBtn.innerText = "LOADING SECTOR CASES...";
                    fetch(`/api/world/${world.id}/challenges`)
                        .then(r => r.json())
                        .then(challenges => {
                            if (challenges.length > 0) {
                                // Find first unsolved challenge
                                const targetChallenge = challenges.find(c => !c.is_solved) || challenges[0];
                                const targetIdx = challenges.indexOf(targetChallenge);
                                
                                if (targetChallenge.is_solved) {
                                    actionBtn.innerText = "REVIEW INVESTIGATION 🔎";
                                } else {
                                    actionBtn.innerText = `ENTER CASE 0${targetIdx + 1} 🔎`;
                                }
                                actionBtn.onclick = () => {
                                    window.location.href = `/challenge/${targetChallenge.id}`;
                                };

                                // Render cases inside HUD card
                                if (listEl) {
                                    listEl.innerHTML = '';
                                    challenges.forEach((c, idx) => {
                                        const item = document.createElement('a');
                                        item.href = `/challenge/${c.id}`;
                                        item.style.cssText = 'display: flex; justify-content: space-between; align-items: center; background: rgba(255,255,255,0.05); padding: 8px 12px; border-radius: 4px; text-decoration: none; color: #fff; font-size: 0.85rem; border: 1px solid rgba(0, 240, 255, 0.2); transition: all 0.2s;';
                                        item.onmouseenter = () => item.style.borderColor = 'var(--cyber-cyan)';
                                        item.onmouseleave = () => item.style.borderColor = 'rgba(0, 240, 255, 0.2)';
                                        item.innerHTML = `
                                            <span style="font-weight: 600;">Case ${idx + 1}: ${c.title}</span>
                                            <span>${c.is_solved ? '<span style="color: var(--cyber-green); font-size: 0.75rem; font-weight: bold;">SOLVED ✅</span>' : '<span style="color: var(--cyber-cyan); font-size: 0.75rem; font-weight: bold;">START ➡️</span>'}</span>
                                        `;
                                        listEl.appendChild(item);
                                    });
                                }
                            }
                        });
                }
            } else {
                actionBtn.classList.add('btn-disabled');
                actionBtn.innerText = `LOCKED (${world.required_stars} STARS NEEDED)`;
                actionBtn.onclick = () => {
                    if (window.soundFx) window.soundFx.playError();
                };
            }
        }
    }

    animate() {
        requestAnimationFrame(() => this.animate());

        const delta = Math.min(this.clock.getDelta(), 0.1);
        const time = this.clock.getElapsedTime();

        // Update Matrix Particles
        if (this.particles && this.particles.userData.update) {
            this.particles.userData.update(delta);
        }

        // Camera smooth ease
        if (this.targetCamPos) {
            this.camera.position.lerp(this.targetCamPos, delta * 3.5);
        }
        if (this.targetCamLookAt) {
            this.camera.lookAt(this.targetCamLookAt);
        }

        // Avatar glide movement towards target sector
        if (this.avatar) {
            const dist = this.avatar.position.distanceTo(this.targetAvatarPos);
            if (dist > 0.15) {
                this.avatar.position.lerp(this.targetAvatarPos, delta * 5.0);
                // Turn towards target
                this.avatar.lookAt(this.targetAvatarPos.x, this.avatar.position.y, this.targetAvatarPos.z);
                // Walking bob
                this.avatar.userData.walkCycle += delta * 14;
                this.avatar.position.y = this.targetAvatarPos.y + Math.abs(Math.sin(this.avatar.userData.walkCycle)) * 0.4;
            } else {
                this.avatar.position.y = this.targetAvatarPos.y + Math.sin(time * 3) * 0.08;
            }
        }

        // Sector 5 Citadel animations
        const fort = this.islands[5];
        if (fort) {
            if (fort.userData.star) fort.userData.star.rotation.y += delta * 1.5;
            if (fort.userData.ring1) {
                fort.userData.ring1.rotation.z += delta * 0.8;
                fort.userData.ring1.rotation.x += delta * 0.5;
            }
        }

        // Bob locked island padlocks
        Object.values(this.islands).forEach(isl => {
            if (isl.userData.lock) {
                isl.userData.lock.rotation.y += delta * 1.5;
                isl.userData.lock.position.y = 5.0 + Math.sin(time * 3) * 0.3;
            }
        });

        this.renderer.render(this.scene, this.camera);
    }
}
