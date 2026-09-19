// Mario: The Cyber Heist - Interactive Forensic Challenge Workbench

document.addEventListener('DOMContentLoaded', () => {
    initFlagSubmission();
    initHintButtons();
    initChallengeTools();
});

// Flag Submission Handler
function initFlagSubmission() {
    const flagForm = document.getElementById('flag-form');
    if (!flagForm) return;

    flagForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        const input = document.getElementById('flag-input');
        const alertBox = document.getElementById('flag-alert');
        const submitBtn = document.getElementById('flag-submit-btn');

        const flag = input.value.trim();
        const challengeId = input.dataset.challengeId;

        if (!flag) return;

        submitBtn.disabled = true;
        submitBtn.innerText = "VERIFYING ENCRYPTED FLAG...";

        try {
            const resp = await fetch('/api/submit-flag', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ challenge_id: challengeId, flag: flag })
            });
            const data = await resp.json();

            alertBox.classList.remove('hidden', 'alert-success', 'alert-error');

            if (data.success) {
                alertBox.classList.add('alert-success');
                alertBox.innerHTML = `<strong>🌟 ${data.message}</strong>`;
                if (window.soundFx) window.soundFx.playSuccess();

                // Update HUD
                if (data.team) {
                    updateHUDStats(data.team);
                }

                // If boss challenge, reveal victory prompt on page
                const bossPrompt = document.getElementById('boss-victory-prompt');
                if (bossPrompt) {
                    bossPrompt.classList.remove('hidden');
                    bossPrompt.scrollIntoView({ behavior: 'smooth', block: 'center' });
                }

                // Show celebration popup
                showSolveModal(data);
            } else if (data.already_solved) {
                alertBox.classList.remove('alert-error');
                alertBox.classList.add('alert-success');
                alertBox.innerHTML = `<strong>✅ Challenge already solved by your team!</strong><br><span style="font-size: 0.85rem;">The Golden Star is already in your possession.</span>`;
                if (window.soundFx) window.soundFx.playPowerup();

                const bossPrompt = document.getElementById('boss-victory-prompt');
                if (bossPrompt) {
                    bossPrompt.classList.remove('hidden');
                    bossPrompt.scrollIntoView({ behavior: 'smooth', block: 'center' });
                }
            } else {
                alertBox.classList.add('alert-error');
                alertBox.innerHTML = `<strong>⚠️ ${data.message}</strong>`;
                if (window.soundFx) window.soundFx.playError();
            }
        } catch (err) {
            alertBox.classList.remove('hidden');
            alertBox.classList.add('alert-error');
            alertBox.innerText = "Network error communicating with investigation server.";
        } finally {
            submitBtn.disabled = false;
            submitBtn.innerText = "SUBMIT FLAG";
        }
    });
}

function showSolveModal(data) {
    const modal = document.getElementById('solve-modal');
    if (!modal) return;

    const starsEl = document.getElementById('solve-stars-earned');
    const coinsEl = document.getElementById('solve-coins-earned');
    const ptsEl = document.getElementById('solve-points-earned');
    const nextBtn = document.getElementById('solve-next-btn');
    const unlockNotice = document.getElementById('solve-unlock-notice');

    if (starsEl) starsEl.innerText = `+${data.stars_awarded || 1} ⭐`;
    if (coinsEl) coinsEl.innerText = `+${data.coins_awarded || 50} 🪙`;
    if (ptsEl) ptsEl.innerText = `+${data.points_awarded || 100} PTS`;

    if (unlockNotice) {
        if (data.next_world_unlocked && data.next_world_name) {
            unlockNotice.classList.remove('hidden');
            unlockNotice.innerHTML = `🌟 <strong>NEW SECTOR UNLOCKED: ${data.next_world_name.toUpperCase()}!</strong> 🌟`;
        } else {
            unlockNotice.classList.add('hidden');
        }
    }

    if (nextBtn) {
        if (data.next_challenge_url) {
            nextBtn.href = data.next_challenge_url;
            if (data.next_world_unlocked && data.next_world_name) {
                nextBtn.innerText = `ENTER ${data.next_world_name.toUpperCase()} 🚀`;
            } else if (data.next_challenge_id) {
                nextBtn.innerText = "PROCEED TO NEXT CASE ➡️";
            } else {
                nextBtn.innerText = "PROCEED TO WORLD MAP 🗺️";
            }
        } else {
            nextBtn.href = "/map";
            nextBtn.innerText = "PROCEED TO WORLD MAP 🗺️";
        }
    }

    modal.classList.remove('hidden');
}

// Hint Unlock Handler
function initHintButtons() {
    const hintBtns = document.querySelectorAll('.btn-unlock-hint');
    hintBtns.forEach(btn => {
        btn.addEventListener('click', async () => {
            const challengeId = btn.dataset.challengeId;
            const hintNum = btn.dataset.hintNum;
            const cost = btn.dataset.cost;

            if (!confirm(`Unlock Forensic Hint ${hintNum} for ${cost} coins?`)) return;

            try {
                const resp = await fetch('/api/unlock-hint', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ challenge_id: challengeId, hint_num: hintNum })
                });
                const data = await resp.json();

                if (data.success) {
                    if (window.soundFx) window.soundFx.playPowerup();
                    const container = document.getElementById(`hint-${hintNum}-container`);
                    if (container) {
                        container.innerHTML = `
                            <div class="hint-unlocked-card">
                                <span class="hint-tag">💡 FORENSIC CLUE #${hintNum}</span>
                                <p>${data.hint}</p>
                            </div>
                        `;
                    }
                    btn.remove();

                    // Update HUD coins
                    const coinEl = document.getElementById('hud-coins-val');
                    if (coinEl && data.remaining_coins !== undefined) {
                        coinEl.innerText = data.remaining_coins;
                    }
                } else {
                    if (window.soundFx) window.soundFx.playError();
                    alert(data.message);
                }
            } catch (e) {
                alert("Error unlocking hint.");
            }
        });
    });
}

function updateHUDStats(team) {
    const scoreEl = document.getElementById('hud-score-val');
    const coinsEl = document.getElementById('hud-coins-val');
    const starsEl = document.getElementById('hud-stars-val');

    if (scoreEl) scoreEl.innerText = team.score;
    if (coinsEl) coinsEl.innerText = team.coins;
    if (starsEl) starsEl.innerText = team.stars;
}

// Initialize Interactive Tools based on challenge type
function initChallengeTools() {
    // 1. Web DOM Inspector tool
    const domToggleBtn = document.getElementById('tool-dom-inspect-btn');
    if (domToggleBtn) {
        domToggleBtn.addEventListener('click', () => {
            const tree = document.getElementById('tool-dom-tree');
            if (tree) tree.classList.toggle('hidden');
        });
    }

    // 2. Cipher Stream ROT Tool
    const rotSlider = document.getElementById('rot-slider');
    const rotVal = document.getElementById('rot-val');
    const rotOutput = document.getElementById('rot-output');
    if (rotSlider && rotOutput) {
        const cipherText = rotSlider.dataset.original || "";
        rotSlider.addEventListener('input', (e) => {
            const shift = parseInt(e.target.value);
            if (rotVal) rotVal.innerText = shift;
            rotOutput.innerText = applyCaesar(cipherText, shift);
            if (shift === 13) {
                rotOutput.classList.add('glow-green');
            } else {
                rotOutput.classList.remove('glow-green');
            }
        });
    }

    // 3. Stego Bitplane Visualizer
    const stegoCanvas = document.getElementById('stego-canvas');
    if (stegoCanvas) {
        initStegoTool(stegoCanvas);
    }

    // 4. Directory Traversal / Robots.txt Explorer
    const pathInput = document.getElementById('traversal-path-input');
    const pathGoBtn = document.getElementById('traversal-go-btn');
    const pathOutput = document.getElementById('traversal-output');
    if (pathInput && pathGoBtn && pathOutput) {
        pathGoBtn.addEventListener('click', () => {
            const p = pathInput.value.trim();
            if (p === '/robots.txt' || p === 'robots.txt') {
                pathOutput.innerHTML = `<span class="text-info">HTTP/1.1 200 OK</span><br>User-agent: *<br>Disallow: /admin<br>Disallow: /secret_attic/<br># Note: ghost_manifesto.bak contains sector vault key`;
            } else if (p.includes('secret_attic/ghost_manifesto.bak') || p.includes('../../secret_attic')) {
                pathOutput.innerHTML = `<span class="text-success">HTTP/1.1 200 OK [RESTRICTED ACCESS GRANTED]</span><br>================================<br>GHOST MANIFESTO ARCHIVE v1.0<br>Sector 03 Clearance Key: <strong>FLAG{BOO_GHOST_PATH_DISCOVERED}</strong><br>================================`;
            } else {
                pathOutput.innerHTML = `<span class="text-error">HTTP/1.1 404 NOT FOUND</span><br>File "${p}" not found in current public root.`;
            }
        });
    }

    // 5. IDOR Locker API tester
    const idorSendBtn = document.getElementById('idor-send-btn');
    if (idorSendBtn) {
        idorSendBtn.addEventListener('click', () => {
            const lockerId = document.getElementById('idor-locker-id').value;
            const accessHdr = document.getElementById('idor-header-val').value;
            const respBox = document.getElementById('idor-response');

            if (lockerId === '1' && accessHdr === 'master_phantom') {
                respBox.innerHTML = `
                    <span class="text-success">HTTP/1.1 200 OK</span><br>
                    {<br>
                      &nbsp;&nbsp;"status": "AUTHORIZED",<br>
                      &nbsp;&nbsp;"locker": "VIP Vault #0001",<br>
                      &nbsp;&nbsp;"owner": "King Boo",<br>
                      &nbsp;&nbsp;"classified_flag": "<strong>FLAG{API_AUTH_BYPASS_OJAS}</strong>"<br>
                    }
                `;
            } else if (lockerId === '1') {
                respBox.innerHTML = `<span class="text-error">HTTP/1.1 403 FORBIDDEN</span><br>{"error": "Locker #0001 requires header 'X-Access-Level: master_phantom'"}`;
            } else {
                respBox.innerHTML = `<span class="text-info">HTTP/1.1 200 OK</span><br>{"locker": "${lockerId}", "owner": "Mansion Guest", "contents": "Old dusty Boo plush toy."}`;
            }
        });
    }

    // 6. JWT Token Forge tool
    const jwtRoleSelect = document.getElementById('jwt-role-select');
    const jwtAlgSelect = document.getElementById('jwt-alg-select');
    const jwtTokenOutput = document.getElementById('jwt-token-output');
    const jwtVerifyBtn = document.getElementById('jwt-verify-btn');
    const jwtResult = document.getElementById('jwt-result');
    if (jwtRoleSelect && jwtAlgSelect && jwtVerifyBtn) {
        const updateJwt = () => {
            const role = jwtRoleSelect.value;
            const alg = jwtAlgSelect.value;
            const header = btoa(JSON.stringify({ typ: "JWT", alg: alg })).replace(/=/g, '');
            const payload = btoa(JSON.stringify({ role: role, user: "inspector", realm: "haunted_mansion" })).replace(/=/g, '');
            const sig = (alg === 'none') ? '' : 'k8Xz9A7L_simulated_sig';
            jwtTokenOutput.innerText = `${header}.${payload}.${sig}`;
        };

        jwtRoleSelect.addEventListener('change', updateJwt);
        jwtAlgSelect.addEventListener('change', updateJwt);

        jwtVerifyBtn.addEventListener('click', () => {
            if (jwtRoleSelect.value === 'admin' && jwtAlgSelect.value === 'none') {
                jwtResult.innerHTML = `<span class="text-success">ACCESS LEVEL: MASTER ADMIN GRANTED!</span><br>Master Key Released: <strong>FLAG{SESSION_FORGERY_DETECTED_OJAS}</strong>`;
            } else if (jwtRoleSelect.value === 'admin') {
                jwtResult.innerHTML = `<span class="text-error">SIGNATURE VERIFICATION FAILED. Insecure key mismatch. Try alg: none.</span>`;
            } else {
                jwtResult.innerHTML = `<span class="text-info">Role is currently 'guest'. Privilege escalation required.</span>`;
            }
        });
    }

    // 7. SQL Injection Console
    const sqliInput = document.getElementById('sqli-input');
    const sqliBtn = document.getElementById('sqli-btn');
    const sqliOutput = document.getElementById('sqli-output');
    if (sqliInput && sqliBtn && sqliOutput) {
        sqliBtn.addEventListener('click', () => {
            const q = sqliInput.value.trim();
            if (q.includes("' OR '1'='1") || q.includes("' OR 1=1") || q.toLowerCase().includes("union select")) {
                sqliOutput.innerHTML = `
                    <span class="text-success">[+] SQL Query Evaluated True! Bypassing personnel filter...</span><br>
                    <table class="cyber-table">
                        <tr><th>ID</th><th>NAME</th><th>RANK</th><th>VAULT_SECRET</th></tr>
                        <tr><td>001</td><td>Commander Shellshock</td><td>General</td><td>[ENCRYPTED]</td></tr>
                        <tr><td>002</td><td>Elite Hammer Bro</td><td>Guard</td><td>[NONE]</td></tr>
                        <tr><td>999</td><td>Master Root Bypass</td><td>SYSTEM</td><td><strong>FLAG{SQLI_ARCHIVE_UNLOCKED_OJAS}</strong></td></tr>
                    </table>
                `;
            } else {
                sqliOutput.innerHTML = `<span class="text-error">[-] Query returned 0 rows: "SELECT * FROM officers WHERE badge_id = '${q}'"</span>`;
            }
        });
    }

    // 8. Boss Terminal Overrides (World 5)
    initBossOverrides();
}

function initBossOverrides() {
    const codes = {
        1: ["SECRET"],
        2: ["PINES", "PINE"],
        3: ["BOO", "KING BOO", "KINGBOO"],
        4: ["INSIDER"]
    };

    for (let i = 1; i <= 4; i++) {
        const btn = document.getElementById(`boss-override-btn-${i}`);
        const input = document.getElementById(`boss-override-input-${i}`);
        const status = document.getElementById(`boss-override-status-${i}`);

        if (btn && input) {
            const handleCrack = () => {
                if (btn.disabled) return;
                const val = input.value.trim().toUpperCase();

                if (codes[i].includes(val)) {
                    if (status) {
                        status.className = "badge-tag badge-diff-easy";
                        status.innerHTML = `NEUTRALIZED ✅`;
                    }
                    btn.disabled = true;
                    btn.innerText = "CRACKED";
                    input.disabled = true;

                    // Trigger 3D Shield break in WebGL
                    if (window.bossSceneInstance) {
                        window.bossSceneInstance.breakShield(i - 1);
                    }

                    checkAllBossShields();
                } else {
                    if (status) {
                        status.className = "badge-tag badge-diff-hard";
                        status.innerHTML = `FAILED ❌`;
                    }
                    if (window.soundFx) window.soundFx.playError();
                    setTimeout(() => {
                        if (!btn.disabled && status) {
                            const badgeClasses = {
                                1: "badge-tag badge-diff-easy",
                                2: "badge-tag badge-category",
                                3: "badge-tag badge-diff-expert",
                                4: "badge-tag badge-diff-hard"
                            };
                            status.className = badgeClasses[i];
                            status.innerHTML = "ACTIVE 🔒";
                        }
                    }, 2500);
                }
            };

            btn.addEventListener('click', handleCrack);
            input.addEventListener('keydown', (e) => {
                if (e.key === 'Enter') {
                    e.preventDefault();
                    handleCrack();
                }
            });
        }
    }
}

function checkAllBossShields() {
    let allSolved = true;
    for (let i = 1; i <= 4; i++) {
        const btn = document.getElementById(`boss-override-btn-${i}`);
        if (btn && !btn.disabled) {
            allSolved = false;
            break;
        }
    }

    if (allSolved) {
        // Show synthesized Master Flag box
        const finalBox = document.getElementById('boss-final-flag-box');
        if (finalBox) {
            finalBox.classList.remove('hidden');
        }

        // Automatically populate master flag into the submission terminal!
        const flagInput = document.getElementById('flag-input');
        if (flagInput) {
            flagInput.value = "FLAG{GOLDEN_STAR_RESTORED_OJAS_CHAMPION}";
            flagInput.focus();
        }

        // Scroll smoothly to submit button so player can submit with 1 click
        const submitBtn = document.getElementById('flag-submit-btn');
        if (submitBtn) {
            submitBtn.scrollIntoView({ behavior: 'smooth', block: 'center' });
        }

        if (window.soundFx) {
            window.soundFx.playPowerup();
        }
    }
}

function applyCaesar(str, shift) {
    return str.replace(/[A-Za-z]/g, (c) => {
        const code = c.charCodeAt(0);
        const base = code >= 65 && code <= 90 ? 65 : 97;
        return String.fromCharCode(((code - base + shift + 26) % 26) + base);
    });
}

function initStegoTool(canvas) {
    const ctx = canvas.getContext('2d');
    canvas.width = 400;
    canvas.height = 240;

    // Draw base pixel landscape
    const grad = ctx.createLinearGradient(0, 0, 400, 240);
    grad.addColorStop(0, '#001a33');
    grad.addColorStop(0.5, '#003344');
    grad.addColorStop(1, '#001122');
    ctx.fillStyle = grad;
    ctx.fillRect(0, 0, 400, 240);

    // Pine trees
    ctx.fillStyle = '#00ff88';
    ctx.font = '16px monospace';
    ctx.fillText("SECTOR 02: PINE RIDGE DRONE TELEMETRY", 20, 30);

    // Concealed LSB text
    ctx.fillStyle = '#00ffff';
    ctx.font = '18px monospace';
    ctx.fillText("LSB_LAYER >> FLAG{FOREST_PIXEL_STEGO_OJAS}", 20, 130);

    const filterBtns = document.querySelectorAll('.stego-filter-btn');
    filterBtns.forEach(btn => {
        btn.addEventListener('click', () => {
            const filter = btn.dataset.filter;
            filterBtns.forEach(b => b.classList.remove('active'));
            btn.classList.add('active');

            if (filter === 'lsb' || filter === 'green') {
                ctx.fillStyle = '#000000';
                ctx.fillRect(0, 0, 400, 240);
                ctx.fillStyle = '#00ff66';
                ctx.font = 'bold 18px monospace';
                ctx.fillText("BITPLANE 0 CONCEALED PAYLOAD:", 20, 80);
                ctx.fillText("FLAG{FOREST_PIXEL_STEGO_OJAS}", 20, 130);
            } else {
                ctx.fillStyle = grad;
                ctx.fillRect(0, 0, 400, 240);
                ctx.fillStyle = '#00ff88';
                ctx.font = '16px monospace';
                ctx.fillText("SECTOR 02: PINE RIDGE DRONE TELEMETRY", 20, 30);
                ctx.fillStyle = '#002233';
                ctx.fillText("FLAG{FOREST_PIXEL_STEGO_OJAS}", 20, 130);
            }
        });
    });
}
