// Mario: The Cyber Heist - High-Precision Authoritative Timer & Timestamp Engine
// Immune to Client Clock Skew, Timezone Offsets (IST/UTC), and Background Tab Throttling

(function () {
    'use strict';

    function formatDuration(totalSecs) {
        if (isNaN(totalSecs) || totalSecs < 0) totalSecs = 0;
        const hrs = String(Math.floor(totalSecs / 3600)).padStart(2, '0');
        const mins = String(Math.floor((totalSecs % 3600) / 60)).padStart(2, '0');
        const secs = String(totalSecs % 60).padStart(2, '0');
        return `${hrs}:${mins}:${secs}`;
    }

    function parseUtcDate(raw) {
        if (!raw) return null;
        let s = String(raw).trim();
        if (!s) return null;
        s = s.replace(' ', 'T');
        // Ensure UTC interpretation if timezone offset is absent
        if (!s.endsWith('Z') && !/[+-]\d{2}(:\d{2})?$/.test(s)) {
            s += 'Z';
        }
        const d = new Date(s);
        return isNaN(d.getTime()) ? null : d;
    }

    function initHudTimer() {
        const timerPill = document.getElementById('hud-timer-pill');
        const timerVal = document.getElementById('hud-timer-val');
        if (!timerPill || !timerVal) return;

        // Clean any obsolete sessionStorage relics from previous testing
        try {
            sessionStorage.removeItem('mario_ctf_start_time');
            sessionStorage.removeItem('mario_ctf_end_time');
            sessionStorage.removeItem('mario_ctf_total_time');
        } catch (e) {}

        let runState = timerPill.dataset.runState || 'STANDBY';
        let totalTime = timerPill.dataset.totalTime || '';
        let baseElapsed = parseInt(timerPill.dataset.elapsedSeconds, 10);
        if (isNaN(baseElapsed) || baseElapsed < 0) baseElapsed = 0;

        // Monotonic performance baseline (immune to OS clock tampering or drift)
        let anchorPerf = performance.now();
        let anchorElapsed = baseElapsed;

        let showClockMode = false;

        timerPill.addEventListener('click', () => {
            if (runState === 'COMPLETED' || totalTime) {
                window.location.href = '/end';
                return;
            }
            showClockMode = !showClockMode;
            renderTimer();
            if (window.soundFx) window.soundFx.playCoin();
        });

        function renderTimer() {
            const now = new Date();

            if (showClockMode) {
                // Local Clock Mode (24-hour)
                const hrs = String(now.getHours()).padStart(2, '0');
                const mins = String(now.getMinutes()).padStart(2, '0');
                const secs = String(now.getSeconds()).padStart(2, '0');
                timerVal.innerText = `${hrs}:${mins}:${secs}`;
                timerPill.title = "Local Device Clock • Click to return to Mission Timer";
                return;
            }

            if (runState === 'COMPLETED' || totalTime) {
                const display = totalTime || formatDuration(anchorElapsed);
                timerVal.innerHTML = `<span style="color: var(--cyber-gold); font-weight: bold;">🏆 ${display}</span>`;
                timerPill.style.borderColor = "var(--cyber-gold)";
                timerPill.style.boxShadow = "0 0 12px rgba(255, 215, 0, 0.4)";
                timerPill.title = `Investigation Concluded! Locked Time: ${display}`;
            } else if (runState === 'STANDBY' || (anchorElapsed === 0 && !timerPill.dataset.startedAt)) {
                timerVal.innerHTML = `<span style="color: #8da4d0;">00:00:00</span> <span style="font-size: 0.65rem; color: var(--cyber-cyan); border: 1px solid var(--cyber-cyan); border-radius: 3px; padding: 1px 4px; margin-left: 2px;">READY</span>`;
                timerPill.style.borderColor = "rgba(0, 240, 255, 0.3)";
                timerPill.title = "CTF Mission Clock on Standby • Awaiting Host Mission Dispatch";
            } else {
                // ACTIVE Run: High-precision monotonic elapsed progression
                const elapsedDeltaSec = Math.floor((performance.now() - anchorPerf) / 1000);
                const currentSecs = Math.max(0, anchorElapsed + elapsedDeltaSec);
                const formatted = formatDuration(currentSecs);
                timerVal.innerText = formatted;
                timerPill.style.borderColor = "var(--cyber-cyan)";
                timerPill.title = `CTF Mission Active (${formatted}) • Click to toggle Local Clock`;

                // Update modal timer if open
                const modalTimer = document.getElementById('modal-timer-val');
                if (modalTimer) modalTimer.innerText = formatted;
            }

            // Sync with Admin Dashboard Live Widgets
            const adminClock = document.getElementById('admin-live-clock');
            const adminTimer = document.getElementById('admin-live-timer');
            if (adminClock) {
                adminClock.innerText = now.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', second: '2-digit', hour12: false });
            }
            if (adminTimer) {
                if (runState === 'COMPLETED' || totalTime) {
                    adminTimer.innerText = `COMPLETED: ${totalTime || formatDuration(anchorElapsed)}`;
                    adminTimer.style.color = "var(--cyber-gold)";
                } else if (runState === 'STANDBY') {
                    adminTimer.innerText = "STATUS: STANDBY (AWAITING DISPATCH)";
                    adminTimer.style.color = "#8da4d0";
                } else {
                    const elapsedDeltaSec = Math.floor((performance.now() - anchorPerf) / 1000);
                    const currentSecs = Math.max(0, anchorElapsed + elapsedDeltaSec);
                    adminTimer.innerText = `ACTIVE RUNTIME: ${formatDuration(currentSecs)}`;
                    adminTimer.style.color = "var(--cyber-cyan)";
                }
            }
        }

        renderTimer();
        setInterval(renderTimer, 500); // 500ms heartbeat for sub-second smooth ticking

        // Resync with server telemetry periodically and when student returns to tab
        async function syncWithServer() {
            try {
                const res = await fetch('/api/competition/status', { credentials: 'same-origin' });
                if (!res.ok) return;
                const data = await res.json();
                if (data.team && data.team.run_info) {
                    const info = data.team.run_info;
                    runState = info.run_state || runState;
                    totalTime = info.total_time || totalTime;
                    anchorElapsed = info.elapsed_seconds || 0;
                    anchorPerf = performance.now();
                    renderTimer();
                } else if (data.status === 'LOBBY') {
                    runState = 'STANDBY';
                    anchorElapsed = 0;
                    anchorPerf = performance.now();
                    renderTimer();
                }
            } catch (e) {
                // Silent network resilience
            }
        }

        // Re-sync on tab focus and every 25 seconds
        window.addEventListener('focus', syncWithServer);
        setInterval(syncWithServer, 25000);

        // Global API methods for challenge workflows
        window.startCtfTimer = function () {
            runState = 'ACTIVE';
            anchorElapsed = 0;
            anchorPerf = performance.now();
            renderTimer();
            syncWithServer();
        };

        window.finishCtfTimer = function (timeStr) {
            runState = 'COMPLETED';
            totalTime = timeStr || formatDuration(anchorElapsed);
            renderTimer();
        };

        window.resetCtfTimer = function () {
            runState = 'STANDBY';
            anchorElapsed = 0;
            totalTime = '';
            renderTimer();
        };
    }

    // Relative Time Formatter
    function getRelativeTime(dateObj) {
        const now = Date.now();
        const diffMs = Math.max(0, now - dateObj.getTime());
        const diffSecs = Math.floor(diffMs / 1000);

        if (diffSecs < 5) return "Just now";
        if (diffSecs < 60) return `${diffSecs}s ago`;
        const diffMins = Math.floor(diffSecs / 60);
        if (diffMins < 60) return `${diffMins}m ago`;
        const diffHours = Math.floor(diffMins / 60);
        if (diffHours < 24) return `${diffHours}h ago`;
        const diffDays = Math.floor(diffHours / 24);
        return `${diffDays}d ago`;
    }

    // Format all .live-timestamp nodes
    function formatAllTimestamps() {
        const elements = document.querySelectorAll('.live-timestamp');
        elements.forEach(el => {
            const raw = el.dataset.timestamp || el.getAttribute('data-time') || el.innerText;
            const date = parseUtcDate(raw);
            if (!date) return;

            if (!el.dataset.timestamp) el.dataset.timestamp = raw;

            const hours = String(date.getHours()).padStart(2, '0');
            const mins = String(date.getMinutes()).padStart(2, '0');
            const secs = String(date.getSeconds()).padStart(2, '0');
            const timeStr = `${hours}:${mins}:${secs}`;

            const year = date.getFullYear();
            const month = String(date.getMonth() + 1).padStart(2, '0');
            const day = String(date.getDate()).padStart(2, '0');
            const dateStr = `${year}-${month}-${day}`;

            const rel = getRelativeTime(date);

            el.innerHTML = `
                <span style="color: #fff; font-family: monospace; font-size: 0.85rem;">${dateStr} ${timeStr}</span>
                <span class="badge-tag badge-category" style="font-size: 0.7rem; margin-left: 6px; padding: 2px 6px;">${rel}</span>
            `;
            el.title = `Local Time: ${date.toLocaleString()} (${rel})`;
        });
    }

    document.addEventListener('DOMContentLoaded', () => {
        initHudTimer();
        formatAllTimestamps();
        setInterval(formatAllTimestamps, 5000);
    });
})();
