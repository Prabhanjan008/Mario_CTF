// Mario: The Cyber Heist - Universal Live HUD Timer & Intelligent Timestamps

(function () {
    // 1. Live HUD Competition Timer
    function initHudTimer() {
        const timerPill = document.getElementById('hud-timer-pill');
        const timerVal = document.getElementById('hud-timer-val');

        let rawStarted = timerPill ? timerPill.dataset.startedAt : '';
        let rawFinished = timerPill ? timerPill.dataset.finishedAt : '';
        let totalTime = timerPill ? timerPill.dataset.totalTime : '';

        // Check sessionStorage sync
        if (!rawStarted && sessionStorage.getItem('mario_ctf_start_time')) {
            rawStarted = sessionStorage.getItem('mario_ctf_start_time');
        }
        if (!rawFinished && sessionStorage.getItem('mario_ctf_end_time')) {
            rawFinished = sessionStorage.getItem('mario_ctf_end_time');
        }
        if (!totalTime && sessionStorage.getItem('mario_ctf_total_time')) {
            totalTime = sessionStorage.getItem('mario_ctf_total_time');
        }

        let startTimestamp = null;
        if (rawStarted) {
            if (/^\d{4}-\d{2}-\d{2}/.test(rawStarted)) {
                const d = new Date(rawStarted.replace(' ', 'T'));
                startTimestamp = isNaN(d.getTime()) ? null : d.getTime();
            } else {
                const n = parseInt(rawStarted, 10);
                if (!isNaN(n)) startTimestamp = n;
            }
        }

        let showClockMode = false;

        if (timerPill) {
            timerPill.addEventListener('click', () => {
                if (rawFinished || totalTime) {
                    window.location.href = '/end';
                    return;
                }
                showClockMode = !showClockMode;
                updateDisplay();
                if (window.soundFx) window.soundFx.playCoin();
            });
        }

        function updateDisplay() {
            const now = new Date();

            if (timerVal) {
                if (showClockMode) {
                    // Display Local 24h Clock
                    const hrs = String(now.getHours()).padStart(2, '0');
                    const mins = String(now.getMinutes()).padStart(2, '0');
                    const secs = String(now.getSeconds()).padStart(2, '0');
                    timerVal.innerText = `${hrs}:${mins}:${secs}`;
                    if (timerPill) timerPill.title = "Local Clock (IST) • Click to toggle Mission Timer";
                } else if (rawFinished || totalTime) {
                    // STATE: Completed / Finished -> Frozen Elapsed Time!
                    const displayTime = totalTime || "00:00:00";
                    timerVal.innerHTML = `<span style="color: var(--cyber-gold); font-weight: bold;">🏆 ${displayTime}</span>`;
                    if (timerPill) {
                        timerPill.style.borderColor = "var(--cyber-gold)";
                        timerPill.style.boxShadow = "0 0 10px rgba(255, 215, 0, 0.4)";
                        timerPill.title = `CTF Investigation Completed! Locked Final Time: ${displayTime}`;
                    }
                } else if (!startTimestamp) {
                    // STATE: Not started yet / Standby!
                    timerVal.innerHTML = `<span style="color: #8da4d0;">00:00:00</span> <span style="font-size: 0.65rem; color: var(--cyber-cyan); border: 1px solid var(--cyber-cyan); border-radius: 3px; padding: 1px 3px; margin-left: 2px;">READY</span>`;
                    if (timerPill) {
                        timerPill.title = "CTF Timer on Standby • Starts automatically when entering World 1 investigation!";
                    }
                } else {
                    // STATE: Active investigation running!
                    const elapsedMs = Math.max(0, Date.now() - startTimestamp);
                    const totalSecs = Math.floor(elapsedMs / 1000);
                    const hrs = String(Math.floor(totalSecs / 3600)).padStart(2, '0');
                    const mins = String(Math.floor((totalSecs % 3600) / 60)).padStart(2, '0');
                    const secs = String(totalSecs % 60).padStart(2, '0');
                    timerVal.innerText = `${hrs}:${mins}:${secs}`;
                    if (timerPill) {
                        timerPill.style.borderColor = "var(--cyber-cyan)";
                        timerPill.title = `CTF Mission Active (${hrs}:${mins}:${secs}) • Click to toggle Local Clock`;
                    }
                }
            }

            // Sync with Admin Dashboard Live Clock widgets if present
            const adminClock = document.getElementById('admin-live-clock');
            const adminTimer = document.getElementById('admin-live-timer');
            if (adminClock) {
                adminClock.innerText = now.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', second: '2-digit', hour12: false });
            }
            if (adminTimer) {
                if (rawFinished || totalTime) {
                    adminTimer.innerText = `COMPLETED: ${totalTime || 'DONE'}`;
                    adminTimer.style.color = "var(--cyber-gold)";
                } else if (!startTimestamp) {
                    adminTimer.innerText = "STATUS: STANDBY (NOT STARTED)";
                    adminTimer.style.color = "#8da4d0";
                } else {
                    const elapsedMs = Math.max(0, Date.now() - startTimestamp);
                    const totalSecs = Math.floor(elapsedMs / 1000);
                    const hrs = String(Math.floor(totalSecs / 3600)).padStart(2, '0');
                    const mins = String(Math.floor((totalSecs % 3600) / 60)).padStart(2, '0');
                    const secs = String(totalSecs % 60).padStart(2, '0');
                    adminTimer.innerText = `ACTIVE RUNTIME: ${hrs}:${mins}:${secs}`;
                    adminTimer.style.color = "var(--cyber-cyan)";
                }
            }
        }

        updateDisplay();
        setInterval(updateDisplay, 1000);

        // Global exposed helper methods
        window.startCtfTimer = function (ts) {
            startTimestamp = ts || Date.now();
            sessionStorage.setItem('mario_ctf_start_time', startTimestamp);
            updateDisplay();
        };

        window.finishCtfTimer = function (timeStr) {
            totalTime = timeStr || "00:00:00";
            rawFinished = new Date().toISOString();
            sessionStorage.setItem('mario_ctf_end_time', rawFinished);
            sessionStorage.setItem('mario_ctf_total_time', totalTime);
            updateDisplay();
        };

        window.resetCtfTimer = function () {
            startTimestamp = null;
            rawFinished = '';
            totalTime = '';
            sessionStorage.removeItem('mario_ctf_start_time');
            sessionStorage.removeItem('mario_ctf_end_time');
            sessionStorage.removeItem('mario_ctf_total_time');
            updateDisplay();
        };
    }

    // 2. Relative time calculator
    function getRelativeTime(timestampDate) {
        const now = new Date();
        const diffMs = now.getTime() - timestampDate.getTime();
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

    // 3. Intelligent Timestamp Formatter
    function parseDate(raw) {
        if (!raw) return null;
        let str = String(raw).trim();
        if (!str) return null;

        // Check if string matches "YYYY-MM-DD HH:MM:SS"
        if (/^\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}$/.test(str)) {
            // Check if this was recorded in UTC by checking if it's in the past
            // If parsed as UTC vs Local:
            const asLocal = new Date(str.replace(' ', 'T'));
            const asUtc = new Date(str.replace(' ', 'T') + 'Z');

            const now = Date.now();
            // If asLocal is in the future compared to now, or asUtc is closer to reasonable time
            const diffLocal = Math.abs(now - asLocal.getTime());
            const diffUtc = Math.abs(now - asUtc.getTime());

            // If UTC difference is much smaller (within 24 hours) and local is > 4 hours ahead or in future
            if (diffUtc < diffLocal && asLocal.getTime() > now) {
                return asUtc;
            }
            return asLocal;
        }

        const d = new Date(str);
        return isNaN(d.getTime()) ? null : d;
    }

    function formatAllTimestamps() {
        const elements = document.querySelectorAll('.live-timestamp');
        elements.forEach(el => {
            const raw = el.dataset.timestamp || el.getAttribute('data-time') || el.innerText;
            const date = parseDate(raw);
            if (!date) return;

            // Preserve original in data attribute
            if (!el.dataset.timestamp) {
                el.dataset.timestamp = raw;
            }

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
            el.title = `Local Time: ${date.toLocaleString()} (Relative: ${rel})`;
        });
    }

    document.addEventListener('DOMContentLoaded', () => {
        initHudTimer();
        formatAllTimestamps();
        // Update relative time badges every 5 seconds
        setInterval(formatAllTimestamps, 5000);
    });
})();
