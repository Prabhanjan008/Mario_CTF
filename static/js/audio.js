// Mario: The Cyber Heist - 8-Bit Web Audio API Sound Synthesizer
// 100% self-contained sound effects with zero external audio assets

class RetroAudioEngine {
    constructor() {
        this.ctx = null;
        this.muted = false;
        this.initialized = false;
    }

    init() {
        if (!this.initialized) {
            const AudioContext = window.AudioContext || window.webkitAudioContext;
            if (AudioContext) {
                this.ctx = new AudioContext();
                this.initialized = true;
            }
        }
        if (this.ctx && this.ctx.state === 'suspended') {
            this.ctx.resume();
        }
    }

    toggleMute() {
        this.muted = !this.muted;
        return this.muted;
    }

    playTone(freq, type, duration, gainStart = 0.2, gainEnd = 0.01) {
        if (this.muted) return;
        this.init();
        if (!this.ctx) return;

        try {
            const osc = this.ctx.createOscillator();
            const gain = this.ctx.createGain();

            osc.type = type;
            osc.frequency.setValueAtTime(freq, this.ctx.currentTime);

            gain.gain.setValueAtTime(gainStart, this.ctx.currentTime);
            gain.gain.exponentialRampToValueAtTime(gainEnd, this.ctx.currentTime + duration);

            osc.connect(gain);
            gain.connect(this.ctx.destination);

            osc.start();
            osc.stop(this.ctx.currentTime + duration);
        } catch (e) {
            console.warn("Audio playback error:", e);
        }
    }

    playCoin() {
        if (this.muted) return;
        this.init();
        if (!this.ctx) return;

        try {
            const now = this.ctx.currentTime;
            const osc = this.ctx.createOscillator();
            const gain = this.ctx.createGain();

            osc.type = 'square';
            osc.frequency.setValueAtTime(987.77, now); // B5
            osc.frequency.setValueAtTime(1318.51, now + 0.08); // E6

            gain.gain.setValueAtTime(0.2, now);
            gain.gain.setValueAtTime(0.2, now + 0.08);
            gain.gain.exponentialRampToValueAtTime(0.001, now + 0.45);

            osc.connect(gain);
            gain.connect(this.ctx.destination);

            osc.start(now);
            osc.stop(now + 0.45);
        } catch (e) { }
    }

    playJump() {
        if (this.muted) return;
        this.init();
        if (!this.ctx) return;

        try {
            const now = this.ctx.currentTime;
            const osc = this.ctx.createOscillator();
            const gain = this.ctx.createGain();

            osc.type = 'square';
            osc.frequency.setValueAtTime(150, now);
            osc.frequency.exponentialRampToValueAtTime(600, now + 0.18);

            gain.gain.setValueAtTime(0.18, now);
            gain.gain.exponentialRampToValueAtTime(0.01, now + 0.18);

            osc.connect(gain);
            gain.connect(this.ctx.destination);

            osc.start(now);
            osc.stop(now + 0.18);
        } catch (e) { }
    }

    playWarpPipe() {
        if (this.muted) return;
        this.init();
        if (!this.ctx) return;

        try {
            const now = this.ctx.currentTime;
            const notes = [300, 240, 180, 150];
            notes.forEach((freq, idx) => {
                const noteTime = now + idx * 0.06;
                const osc = this.ctx.createOscillator();
                const gain = this.ctx.createGain();

                osc.type = 'triangle';
                osc.frequency.setValueAtTime(freq, noteTime);

                gain.gain.setValueAtTime(0.25, noteTime);
                gain.gain.exponentialRampToValueAtTime(0.01, noteTime + 0.05);

                osc.connect(gain);
                gain.connect(this.ctx.destination);

                osc.start(noteTime);
                osc.stop(noteTime + 0.05);
            });
        } catch (e) { }
    }

    playPowerup() {
        if (this.muted) return;
        this.init();
        if (!this.ctx) return;

        try {
            const now = this.ctx.currentTime;
            const notes = [330, 392, 659, 523, 587, 784];
            notes.forEach((freq, idx) => {
                const noteTime = now + idx * 0.07;
                const osc = this.ctx.createOscillator();
                const gain = this.ctx.createGain();

                osc.type = 'square';
                osc.frequency.setValueAtTime(freq, noteTime);

                gain.gain.setValueAtTime(0.2, noteTime);
                gain.gain.exponentialRampToValueAtTime(0.01, noteTime + 0.09);

                osc.connect(gain);
                gain.connect(this.ctx.destination);

                osc.start(noteTime);
                osc.stop(noteTime + 0.09);
            });
        } catch (e) { }
    }

    playAlert() {
        if (this.muted) return;
        this.init();
        if (!this.ctx) return;

        try {
            const now = this.ctx.currentTime;
            for (let i = 0; i < 3; i++) {
                const burstTime = now + i * 0.18;
                const osc = this.ctx.createOscillator();
                const gain = this.ctx.createGain();

                osc.type = 'sawtooth';
                osc.frequency.setValueAtTime(880, burstTime);
                osc.frequency.linearRampToValueAtTime(440, burstTime + 0.14);

                gain.gain.setValueAtTime(0.25, burstTime);
                gain.gain.exponentialRampToValueAtTime(0.01, burstTime + 0.14);

                osc.connect(gain);
                gain.connect(this.ctx.destination);

                osc.start(burstTime);
                osc.stop(burstTime + 0.14);
            }
        } catch (e) { }
    }

    playError() {
        if (this.muted) return;
        this.init();
        if (!this.ctx) return;

        try {
            const now = this.ctx.currentTime;
            const osc = this.ctx.createOscillator();
            const gain = this.ctx.createGain();

            osc.type = 'sawtooth';
            osc.frequency.setValueAtTime(140, now);
            osc.frequency.linearRampToValueAtTime(110, now + 0.25);

            gain.gain.setValueAtTime(0.3, now);
            gain.gain.exponentialRampToValueAtTime(0.01, now + 0.28);

            osc.connect(gain);
            gain.connect(this.ctx.destination);

            osc.start(now);
            osc.stop(now + 0.28);
        } catch (e) { }
    }

    playSuccess() {
        if (this.muted) return;
        this.init();
        if (!this.ctx) return;

        try {
            const now = this.ctx.currentTime;
            const notes = [
                { f: 523.25, t: 0.0 },   // C5
                { f: 659.25, t: 0.1 },   // E5
                { f: 783.99, t: 0.2 },   // G5
                { f: 1046.50, t: 0.32 }  // C6
            ];

            notes.forEach(n => {
                const noteTime = now + n.t;
                const osc = this.ctx.createOscillator();
                const gain = this.ctx.createGain();

                osc.type = 'triangle';
                osc.frequency.setValueAtTime(n.f, noteTime);

                gain.gain.setValueAtTime(0.25, noteTime);
                gain.gain.exponentialRampToValueAtTime(0.005, noteTime + 0.35);

                osc.connect(gain);
                gain.connect(this.ctx.destination);

                osc.start(noteTime);
                osc.stop(noteTime + 0.35);
            });
        } catch (e) { }
    }

    playVictory() {
        if (this.muted) return;
        this.init();
        if (!this.ctx) return;

        try {
            const now = this.ctx.currentTime;
            // Fanfare sequence
            const fanfare = [
                { f: 523.25, d: 0.12 }, // C
                { f: 659.25, d: 0.12 }, // E
                { f: 783.99, d: 0.12 }, // G
                { f: 1046.50, d: 0.25 }, // High C
                { f: 783.99, d: 0.12 }, // G
                { f: 1046.50, d: 0.5 }  // High C held
            ];

            let offset = 0;
            fanfare.forEach(note => {
                const noteTime = now + offset;
                const osc = this.ctx.createOscillator();
                const gain = this.ctx.createGain();

                osc.type = 'square';
                osc.frequency.setValueAtTime(note.f, noteTime);

                gain.gain.setValueAtTime(0.25, noteTime);
                gain.gain.exponentialRampToValueAtTime(0.01, noteTime + note.d);

                osc.connect(gain);
                gain.connect(this.ctx.destination);

                osc.start(noteTime);
                osc.stop(noteTime + note.d);

                offset += note.d + 0.03;
            });
        } catch (e) { }
    }
}

// Global instance
window.soundFx = new RetroAudioEngine();

// Auto-bind sound triggers to document clicks
document.addEventListener('click', () => {
    if (!window.soundFx.initialized) {
        window.soundFx.init();
    }
}, { once: true });
