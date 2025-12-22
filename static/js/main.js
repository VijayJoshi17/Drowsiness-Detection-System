// Chart Helpers
let liveChart = null;
let reportChart = null;
let pollingInterval = null;

function initLiveChart() {
    const ctx = document.getElementById('liveChart').getContext('2d');
    liveChart = new Chart(ctx, {
        type: 'line',
        data: {
            labels: Array(50).fill(''),
            datasets: [{
                label: 'EAR',
                borderColor: '#22c55e',
                data: Array(50).fill(0),
                tension: 0.4,
                pointRadius: 0
            }, {
                label: 'MAR',
                borderColor: '#eab308',
                data: Array(50).fill(0),
                tension: 0.4,
                pointRadius: 0
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            animation: false,
            scales: {
                y: {
                    beginAtZero: true,
                    max: 1.0,
                    grid: { color: 'rgba(255, 255, 255, 0.1)' }
                },
                x: { display: false }
            },
            plugins: {
                legend: { labels: { color: '#94a3b8' } }
            }
        }
    });
}

async function startSession() {
    try {
        const response = await fetch('/start_session');
        const data = await response.json();

        if (data.status === "started") {
            // UI Updates
            document.getElementById('video_feed').src = "/video_feed";
            document.getElementById('btn-start').disabled = true;
            document.getElementById('btn-start').style.opacity = 0.5;
            document.getElementById('btn-stop').disabled = false;
            document.getElementById('btn-stop').style.opacity = 1;

            // Start Polling
            startPolling();
        }
    } catch (e) {
        console.error("Failed to start session:", e);
        alert("Failed to start session. Check console.");
    }
}

async function stopSession() {
    if (!confirm("End current session and view report?")) return;

    try {
        // Stop Polling
        if (pollingInterval) clearInterval(pollingInterval);

        const response = await fetch('/stop_session');
        const report = await response.json();

        // Show Report View
        showReport(report);

    } catch (e) {
        console.error("Failed to stop session:", e);
    }
}

function startPolling() {
    if (pollingInterval) clearInterval(pollingInterval);
    pollingInterval = setInterval(async () => {
        try {
            const response = await fetch('/status');
            const data = await response.json();

            if (data.error) return; // Stopped

            // Update Text
            document.getElementById('ear-val').innerText = data.ear.toFixed(2);
            document.getElementById('mar-val').innerText = data.mar.toFixed(2);
            document.getElementById('pitch-val').innerText = data.pitch.toFixed(1);
            document.getElementById('yaw-val').innerText = data.yaw.toFixed(1);
            document.getElementById('bpm-val').innerText = data.bpm;
            document.getElementById('fps-val').innerText = data.fps.toFixed(1);

            // Update Status Indicators
            updateIndicator('status-drowsy', data.drowsy, 'drowsy');
            updateIndicator('status-yawn', data.yawning, 'yawn');
            updateIndicator('status-distracted', data.distracted, 'distracted');

            // Auth Indicator
            const authEl = document.getElementById('status-auth');
            if (data.authenticated) {
                authEl.innerText = "UNLOCKED";
                authEl.className = "status-indicator status-active auth";
                authEl.style.background = "var(--accent-green)";
                authEl.style.color = "#000";
            } else {
                authEl.innerText = "LOCKED";
                authEl.className = "status-indicator";
                authEl.style.background = "";
                authEl.style.color = "";
            }

            // Low Light Indicator
            updateIndicator('status-low-light', data.low_light, 'low-light');

            // Update Chart
            if (liveChart) {
                updateLiveChart(data.ear, data.mar);
            }

        } catch (e) {
            console.error("Error fetching status", e);
        }
    }, 500);
}

async function registerFace() {
    if (!document.getElementById('btn-start').disabled) {
        alert("Please START the session first to turn on the camera.");
        return;
    }

    document.getElementById('btn-register').innerText = "Scanning...";
    try {
        const response = await fetch('/register_face');
        const data = await response.json();
        alert(data.message);
    } catch (e) {
        alert("Registration failed.");
    }
    document.getElementById('btn-register').innerText = "Register Face";
}

function updateLiveChart(ear, mar) {
    const data = liveChart.data;
    data.datasets[0].data.shift();
    data.datasets[0].data.push(ear);
    data.datasets[1].data.shift();
    data.datasets[1].data.push(mar);
    liveChart.update();
}

function updateIndicator(id, isActive, className) {
    const el = document.getElementById(id);
    if (isActive) {
        el.classList.add('status-active', className);
    } else {
        el.classList.remove('status-active', className);
    }
}

function showReport(report) {
    // Hide Dashboard
    document.getElementById('dashboard-view').style.display = 'none';
    document.getElementById('live-chart-container').style.display = 'none';

    // Show Report
    document.getElementById('report-view').style.display = 'block';

    // Populate Data
    const summary = report.summary;
    if (summary) {
        document.getElementById('report-score').innerText = summary.score;

        // Format duration
        const mins = Math.floor(summary.duration_seconds / 60);
        const secs = summary.duration_seconds % 60;
        document.getElementById('report-duration').innerText = `${mins}:${secs < 10 ? '0' + secs : secs}`;

        document.getElementById('report-drowsy').innerText = summary.times.drowsy_str;
        document.getElementById('report-yawn').innerText = summary.times.yawn_str;
        document.getElementById('report-distracted').innerText = summary.times.distracted_str;
    }

    // Render Report Chart
    renderReportChart(report.events || [], summary.counts);
}

function renderReportChart(events, counts) {
    const ctx = document.getElementById('reportChart').getContext('2d');

    // Use the counts calculated in python for consistency, or we can recalculate relative distribution

    new Chart(ctx, {
        type: 'doughnut', // Doughnut is better for relative time distribution
        data: {
            labels: ['Drowsy Time', 'Distracted Time', 'Yawning Time', 'Focused (Est)'],
            datasets: [{
                label: 'Session Breakdown (Frames)',
                data: [
                    counts.drowsy,
                    counts.distracted,
                    counts.yawn,
                    // Estimate focused frames? Not critical, let's just show events
                ],
                backgroundColor: ['#ef4444', '#3b82f6', '#eab308', '#22c55e'],
                borderWidth: 0
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: { position: 'right', labels: { color: '#fff' } }
            }
        }
    });
}

// Init
initLiveChart();
