/**
 * Dashboard Fog Véhiculaire - Logique JavaScript
 * Connexion WebSocket + Rendu Canvas + Graphiques Chart.js
 */

// Configuration
const NETWORK_BOUNDS = { minX: 0, maxX: 600, minY: 0, maxY: 600 };
const RSU_POSITIONS = {
    RSU_J4: { x: 200, y: 200 },
    RSU_J3: { x: 400, y: 200 },
    RSU_J2: { x: 200, y: 400 },
    RSU_J1: { x: 400, y: 400 }
};

// État global
let socket = null;
let latencyHistory = { labels: [], edge: [], fog: [], cloud: [] };
let processingChart = null;
let latencyChart = null;
let fogEnabled = true; // Variable globale pour savoir si fog est activé

// Initialisation
document.addEventListener('DOMContentLoaded', () => {
    initWebSocket();
    initCanvas();
    initProcessingChart();
});

// Connexion WebSocket
function initWebSocket() {
    socket = io(window.location.origin);

    socket.on('connect', () => {
        document.getElementById('syncIndicator').classList.remove('disconnected');
        console.log('[WebSocket] Connecté');
    });

    socket.on('disconnect', () => {
        document.getElementById('syncIndicator').classList.add('disconnected');
        console.log('[WebSocket] Déconnecté');
    });

    socket.on('update', (data) => {
        console.log('[WebSocket] Données reçues');
        updateDashboard(data);
    });

    // Fallback: polling API si WebSocket ne reçoit pas de données
    setTimeout(() => {
        startPolling();
    }, 2000);
}

// Polling API comme fallback
let pollingInterval = null;

function startPolling() {
    console.log('[Polling] Démarrage polling API');
    pollingInterval = setInterval(async () => {
        try {
            const response = await fetch('/api/status');
            const data = await response.json();
            if (data && data.time !== undefined) {
                updateDashboard(data);
            }
        } catch (err) {
            console.error('[Polling] Erreur:', err);
        }
    }, 500); // 2 Hz
}

// Mise à jour dashboard
function updateDashboard(data) {
    console.log('[DEBUG] updateDashboard called with:', {
        hasMode: !!data.mode,
        hasScootData: !!data.scootData,
        hasFogActions: !!data.fogActions,
        modeName: data.mode?.name,
        scootEnabled: data.scootData?.enabled,
        tlAdjusted: data.fogActions?.totalTlAdjusted
    });
    // Temps simulation et phase
    updateSimulationStatus(data.time, data.phase);

    // Panel 1: Carte trafic
    renderTrafficMap(data.vehicles, data.rsu);

    // Panel 2: Topologie
    renderTopology(data.vehicles, data.rsu, data.metrics);

    // Panel 3: Statistiques
    updateStats(data.metrics);

    // Panel 4: Distribution chart
    updateProcessingChart(data.metrics);

    // Fog Actions: compteurs et alerte incident
    if (data.fogActions) {
        const tlAdjusted = document.getElementById('totalTlAdjusted');
        const rerouted = document.getElementById('totalRerouted');
        const incidentAlert = document.getElementById('incidentAlert');

        if (tlAdjusted) tlAdjusted.textContent = data.fogActions.totalTlAdjusted || 0;
        if (rerouted) rerouted.textContent = data.fogActions.totalRerouted || 0;
        if (incidentAlert) {
            incidentAlert.style.display = data.fogActions.incidentActive ? 'block' : 'none';
        }
    }

    // Panel SCOOT: Données adaptatives
    if (data.scootData) {
        updateScootPanel(data.scootData);
    }

    // Mode display
    // Mode display
    console.log('[DEBUG] About to update mode display:', data.mode);
    if (data.mode) {
        fogEnabled = data.mode.fog_enabled || false;
        updateModeDisplay(data.mode);
    }
}

// Mise à jour affichage du mode de simulation
function updateModeDisplay(mode) {
    const banner = document.getElementById('modeBanner');
    const modeName = document.getElementById('modeName');
    const fogStatus = document.getElementById('fogStatus');
    const cloudStatus = document.getElementById('cloudStatus');
    const scootStatus = document.getElementById('scootBadge');

    if (!banner || !modeName) return;

    // Mettre à jour le nom du mode
    modeName.textContent = mode.name || 'Mode inconnu';

    // Mettre à jour la classe CSS du bandeau
    banner.className = 'mode-banner';
    if (mode.id === 'edge_only') {
        banner.classList.add('edge-only');
    } else if (mode.id === 'edge_cloud') {
        banner.classList.add('edge-cloud');
    } else {
        banner.classList.add('full-fog');
    }

    // Mettre à jour les badges de fonctionnalités
    if (fogStatus) {
        fogStatus.classList.toggle('enabled', mode.fog_enabled);
    }
    if (cloudStatus) {
        cloudStatus.classList.toggle('enabled', mode.cloud_enabled);
    }
    if (scootStatus) {
        scootStatus.classList.toggle('enabled', mode.scoot_enabled);
    }
}

// Mise à jour status simulation
function updateSimulationStatus(time, phase) {
    document.getElementById('simTime').textContent = `T=${time.toFixed(1)}s`;

    const phaseEl = document.getElementById('phase');
    // Phase unique: Congestion
    phaseEl.textContent = 'Congestion';
    phaseEl.className = 'phase-badge congestion';
}

// Rendu carte trafic
function renderTrafficMap(vehicles, rsus) {
    const canvas = document.getElementById('trafficCanvas');
    const ctx = canvas.getContext('2d');

    // Conversion coordonnées SUMO → Canvas
    // SUMO: réseau ~600x600, Canvas: 600x600
    // Mais l'axe Y SUMO est inversé et les coordonnées sont différentes
    const scaleX = canvas.width / 600;
    const scaleY = canvas.height / 600;

    function toCanvasX(x) { return x * scaleX; }
    function toCanvasY(y) { return canvas.height - (y * scaleY); } // Inverser Y

    // Clear - fond clair
    ctx.fillStyle = '#fafafa';
    ctx.fillRect(0, 0, canvas.width, canvas.height);

    // Grille routes - Architecture SUMO avec losange
    ctx.strokeStyle = '#9ca3af';  // Gris clair
    ctx.lineWidth = 10;
    ctx.lineCap = 'round';
    ctx.lineJoin = 'round';

    // Points clés du réseau (coordonnées SUMO)
    const J3 = { x: toCanvasX(200), y: toCanvasY(400) }; // Haut gauche
    const J4 = { x: toCanvasX(400), y: toCanvasY(400) }; // Haut droite
    const J1 = { x: toCanvasX(200), y: toCanvasY(200) }; // Bas gauche
    const J2 = { x: toCanvasX(400), y: toCanvasY(200) }; // Bas droite

    // Points externes
    const leftPoint = { x: toCanvasX(0), y: toCanvasY(300) };    // Pointe gauche
    const rightPoint = { x: toCanvasX(600), y: toCanvasY(300) }; // Pointe droite
    const topJ3 = { x: toCanvasX(200), y: 0 };                   // Haut J3
    const topJ4 = { x: toCanvasX(400), y: 0 };                   // Haut J4
    const botJ1 = { x: toCanvasX(200), y: canvas.height };       // Bas J1
    const botJ2 = { x: toCanvasX(400), y: canvas.height };       // Bas J2

    // Routes verticales (haut)
    ctx.beginPath();
    ctx.moveTo(topJ3.x, topJ3.y);
    ctx.lineTo(J3.x, J3.y);
    ctx.stroke();

    ctx.beginPath();
    ctx.moveTo(topJ4.x, topJ4.y);
    ctx.lineTo(J4.x, J4.y);
    ctx.stroke();

    // Routes verticales (bas)
    ctx.beginPath();
    ctx.moveTo(J1.x, J1.y);
    ctx.lineTo(botJ1.x, botJ1.y);
    ctx.stroke();

    ctx.beginPath();
    ctx.moveTo(J2.x, J2.y);
    ctx.lineTo(botJ2.x, botJ2.y);
    ctx.stroke();

    // Route horizontale centrale entre J3-J4 et J1-J2
    ctx.beginPath();
    ctx.moveTo(J3.x, J3.y);
    ctx.lineTo(J4.x, J4.y);
    ctx.stroke();

    ctx.beginPath();
    ctx.moveTo(J1.x, J1.y);
    ctx.lineTo(J2.x, J2.y);
    ctx.stroke();

    // Routes verticales entre intersections
    ctx.beginPath();
    ctx.moveTo(J3.x, J3.y);
    ctx.lineTo(J1.x, J1.y);
    ctx.stroke();

    ctx.beginPath();
    ctx.moveTo(J4.x, J4.y);
    ctx.lineTo(J2.x, J2.y);
    ctx.stroke();

    // Routes diagonales formant le losange
    // Gauche: pointe vers J3 et J1
    ctx.beginPath();
    ctx.moveTo(leftPoint.x, leftPoint.y);
    ctx.lineTo(J3.x, J3.y);
    ctx.stroke();

    ctx.beginPath();
    ctx.moveTo(leftPoint.x, leftPoint.y);
    ctx.lineTo(J1.x, J1.y);
    ctx.stroke();

    // Droite: pointe vers J4 et J2
    ctx.beginPath();
    ctx.moveTo(rightPoint.x, rightPoint.y);
    ctx.lineTo(J4.x, J4.y);
    ctx.stroke();

    ctx.beginPath();
    ctx.moveTo(rightPoint.x, rightPoint.y);
    ctx.lineTo(J2.x, J2.y);
    ctx.stroke();

    // RSUs avec zone de couverture
    for (const rsu of rsus) {
        const cx = toCanvasX(rsu.x);
        const cy = toCanvasY(rsu.y);

        // Zone de couverture
        const congestionColor = getCongestionColor(rsu.congestion);
        ctx.fillStyle = congestionColor + '30';
        ctx.beginPath();
        ctx.arc(cx, cy, 120, 0, Math.PI * 2);
        ctx.fill();

        // RSU marker - violet distinct
        ctx.fillStyle = '#7e22ce';
        ctx.fillRect(cx - 12, cy - 12, 24, 24);

        // Bordure blanche pour meilleure visibilité
        ctx.strokeStyle = '#ffffff';
        ctx.lineWidth = 2;
        ctx.strokeRect(cx - 12, cy - 12, 24, 24);

        ctx.fillStyle = '#fff';
        ctx.font = '500 9px system-ui';
        ctx.textAlign = 'center';
        ctx.fillText(rsu.id.replace('RSU_', ''), cx, cy + 3);
    }

    // Véhicules
    for (const veh of vehicles) {
        const vx = toCanvasX(veh.x);
        const vy = toCanvasY(veh.y);

        // Couleur selon type et état - couleurs claires et distinctes
        let color = '#3b82f6'; // Bleu vif (voitures normales)

        // Appliquer couleurs fog UNIQUEMENT si fog est activé
        if (fogEnabled && veh.isFog) {
            // Véhicule fog-capable (bus, truck, fog_capable)
            if (veh.isOffloading && veh.rsu) {
                // Fog node en offloading = orange vif
                color = '#f97316';
            } else {
                color = '#22c55e'; // Vert vif pour fog nodes actifs
            }
        }
        // Si fog désactivé, tous les véhicules restent BLEUS

        ctx.fillStyle = color;
        ctx.beginPath();
        ctx.arc(vx, vy, 5, 0, Math.PI * 2);
        ctx.fill();

        // Bordure pour meilleure visibilité
        ctx.strokeStyle = '#ffffff';
        ctx.lineWidth = 1;
        ctx.stroke();
    }

    // Légende véhicules actifs
    ctx.fillStyle = '#4a4a4a';
    ctx.font = '11px "Segoe UI", sans-serif';
    ctx.textAlign = 'left';
    ctx.fillText(`${vehicles.length} vehicules`, 10, 20);
}

// Couleur selon congestion - palette académique
function getCongestionColor(level) {
    if (level < 0.3) return '#276749'; // vert forêt
    if (level < 0.6) return '#975a16'; // ambre
    return '#9b2c2c'; // rouge brique
}

// Rendu topologie fog
function renderTopology(vehicles, rsus, metrics) {
    const canvas = document.getElementById('topologyCanvas');
    const ctx = canvas.getContext('2d');

    ctx.fillStyle = '#fafafa';
    ctx.fillRect(0, 0, canvas.width, canvas.height);

    const centerX = canvas.width / 2;

    // Cloud
    ctx.fillStyle = '#2c5282';
    ctx.fillRect(centerX - 35, 20, 70, 35);
    ctx.fillStyle = '#fff';
    ctx.font = '500 11px "Segoe UI", sans-serif';
    ctx.textAlign = 'center';
    ctx.fillText('Cloud', centerX, 42);

    // Lignes Cloud -> RSUs
    ctx.strokeStyle = '#d4d4d4';
    ctx.lineWidth = 1;

    const rsuY = 110;
    const rsuSpacing = 75;
    const startX = centerX - (rsus.length - 1) * rsuSpacing / 2;

    rsus.forEach((rsu, i) => {
        const x = startX + i * rsuSpacing;

        // Ligne vers cloud
        ctx.beginPath();
        ctx.moveTo(centerX, 55);
        ctx.lineTo(x, rsuY);
        ctx.stroke();

        // RSU node
        const load = rsu.vehicles / 30;
        ctx.fillStyle = getCongestionColor(load);
        ctx.fillRect(x - 22, rsuY, 44, 26);

        ctx.fillStyle = '#fff';
        ctx.font = '500 9px "Segoe UI", sans-serif';
        ctx.fillText(rsu.id.replace('RSU_', 'RSU '), x, rsuY + 16);
        ctx.fillStyle = '#6b6b6b';
        ctx.fillText(`${rsu.vehicles} veh`, x, rsuY + 40);
    });

    // Fog nodes (afficher 0 si fog désactivé)
    const fogVehicles = vehicles.filter(v => v.isFog);
    const displayFogCount = fogEnabled ? fogVehicles.length : 0;
    const vehicleY = 200;

    ctx.fillStyle = '#276749';
    ctx.font = '500 10px "Segoe UI", sans-serif';
    ctx.fillText(`${displayFogCount} Fog Nodes`, centerX, vehicleY);

    // Legende niveaux
    ctx.fillStyle = '#6b6b6b';
    ctx.font = '9px "Segoe UI", sans-serif';
    ctx.textAlign = 'right';
    ctx.fillText('~125ms', canvas.width - 8, 42);
    ctx.fillText('~22ms', canvas.width - 8, rsuY + 14);
    ctx.fillText('~5ms', canvas.width - 8, vehicleY);

    // Mise à jour stats topologie (afficher 0 si fog désactivé)
    document.getElementById('fogNodeCount').textContent = displayFogCount;
    document.getElementById('rsuCount').textContent = rsus.length;
    document.getElementById('cloudLoad').textContent =
        `${Math.round(metrics.processing?.cloud || 5)}%`;
}

// Initialisation graphique Distribution
function initProcessingChart() {
    const ctx = document.getElementById('processingChart');
    if (!ctx) return;

    processingChart = new Chart(ctx.getContext('2d'), {
        type: 'doughnut',
        data: {
            labels: ['Edge', 'Fog', 'Cloud'],
            datasets: [{
                data: [70, 25, 5],
                backgroundColor: ['#276749', '#975a16', '#9b2c2c'],
                borderWidth: 2,
                borderColor: '#fff'
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            cutout: '55%',
            plugins: {
                legend: {
                    position: 'right',
                    labels: {
                        color: '#6b6b6b',
                        font: { size: 10 },
                        padding: 8,
                        boxWidth: 12
                    }
                }
            }
        }
    });
}

// Mise à jour graphique Distribution
function updateProcessingChart(metrics) {
    if (!processingChart) return;

    const edge = metrics.processing?.edge || 70;
    const fog = metrics.processing?.fog || 0;
    const cloud = metrics.processing?.cloud || 5;

    // Filtrer Fog si valeur = 0 (mode edge_cloud)
    if (fog === 0) {
        processingChart.data.labels = ['Edge', 'Cloud'];
        processingChart.data.datasets[0].data = [edge, cloud];
        processingChart.data.datasets[0].backgroundColor = ['#276749', '#9b2c2c'];
    } else {
        processingChart.data.labels = ['Edge', 'Fog', 'Cloud'];
        processingChart.data.datasets[0].data = [edge, fog, cloud];
        processingChart.data.datasets[0].backgroundColor = ['#276749', '#975a16', '#9b2c2c'];
    }
    processingChart.update('none');
}

// Mise à jour statistiques
function updateStats(metrics) {
    document.getElementById('vehicleCount').textContent = metrics.totalVehicles || 0;
    document.getElementById('activeFogNodes').textContent = fogEnabled ? (metrics.fogNodes || 0) : 0;
    document.getElementById('offloadingCount').textContent = metrics.offloadingCount || 0;
    document.getElementById('tasksProcessed').textContent =
        formatNumber(metrics.tasksProcessed || 0);

    // Latence moyenne pondérée
    const avgLatency = (
        (metrics.latency?.edge || 5) * (metrics.processing?.edge || 70) +
        (metrics.latency?.fog || 22) * (metrics.processing?.fog || 25) +
        (metrics.latency?.cloud || 125) * (metrics.processing?.cloud || 5)
    ) / 100;
    document.getElementById('avgLatency').textContent = `${avgLatency.toFixed(1)} ms`;

    // Comparaison Cloud vs Fog (avec vérifications null)
    const cloudLatency = metrics.latency?.cloud || 125;
    const cloudLatencyEl = document.getElementById('cloudLatency');
    const fogLatencyAvgEl = document.getElementById('fogLatencyAvg');
    const fogBarFillEl = document.getElementById('fogBarFill');

    if (cloudLatencyEl) cloudLatencyEl.textContent = `${cloudLatency} ms`;
    if (fogLatencyAvgEl) fogLatencyAvgEl.textContent = `${avgLatency.toFixed(0)} ms`;
    if (fogBarFillEl) fogBarFillEl.style.width = `${(avgLatency / cloudLatency) * 100}%`;

    // Énergie par tâche (mJ) — même formule que la présentation
    // E_local = 500 mJ, E_fog = 115 mJ, E_cloud = 185 mJ
    const edgePct = metrics.processing?.edge || 70;
    const fogPct = metrics.processing?.fog || 0;
    const cloudPct = metrics.processing?.cloud || 30;
    const energyPerTask = (edgePct / 100) * 500 + (fogPct / 100) * 115 + (cloudPct / 100) * 185;
    const energyEl = document.getElementById('energyPerTask');
    if (energyEl) {
        energyEl.textContent = `${energyPerTask.toFixed(0)} mJ`;
        // Color coding: green if < 250, yellow if < 350, red otherwise
        if (energyPerTask < 250) {
            energyEl.style.color = '#16A34A';
        } else if (energyPerTask < 350) {
            energyEl.style.color = '#CA8A04';
        } else {
            energyEl.style.color = '#DC2626';
        }
    }
}

// Canvas init
function initCanvas() {
    // Rendu initial vide
    renderTrafficMap([], Object.entries(RSU_POSITIONS).map(([id, pos]) => ({
        id, x: pos.x, y: pos.y, vehicles: 0, congestion: 0
    })));

    renderTopology([], Object.entries(RSU_POSITIONS).map(([id, pos]) => ({
        id, vehicles: 0
    })), {});
}

// Formatage nombres
function formatNumber(num) {
    if (num >= 1000000) return (num / 1000000).toFixed(1) + 'M';
    if (num >= 1000) return (num / 1000).toFixed(1) + 'K';
    return num.toString();
}

// Mise à jour panel SCOOT
function updateScootPanel(scootData) {
    // Status SCOOT
    const indicator = document.getElementById('scootIndicator');
    const statusText = document.getElementById('scootStatusText');
    const cycleTime = document.getElementById('scootCycleTime');

    if (scootData.enabled) {
        if (indicator) {
            indicator.classList.remove('off');
            indicator.classList.add('on');
        }
        if (statusText) statusText.textContent = 'Actif';
    } else {
        if (indicator) {
            indicator.classList.remove('on');
            indicator.classList.add('off');
        }
        if (statusText) statusText.textContent = 'Désactivé';
    }

    if (cycleTime) {
        cycleTime.textContent = scootData.globalCycleTime + 's';
    }

    // Mise à jour des intersections
    const intersections = ['J1', 'J2', 'J3', 'J4'];
    intersections.forEach(id => {
        const rsuId = 'RSU_' + id;
        const card = document.getElementById('scoot-' + id);

        // Splits
        const splits = scootData.splits[rsuId];
        if (splits && splits.length >= 4) {
            const ewSplit = document.getElementById('split-' + id + '-ew');
            const nsSplit = document.getElementById('split-' + id + '-ns');
            if (ewSplit) ewSplit.textContent = splits[0] + 's';
            if (nsSplit) nsSplit.textContent = splits[2] + 's';
        }

        // Offset
        const offset = scootData.offsets[rsuId];
        const offsetElem = document.getElementById('offset-' + id);
        if (offsetElem) {
            offsetElem.textContent = (offset !== undefined ? offset : 0) + 's';
        }

        // Performance Index
        const pi = scootData.performanceIndex[rsuId];
        const piElem = document.getElementById('pi-' + id);
        if (piElem) {
            const piValue = pi !== undefined ? pi.toFixed(2) : '1.00';
            piElem.textContent = piValue;

            // Changer couleur selon valeur PI
            if (pi > 1.5) {
                piElem.style.color = '#dc2626'; // Rouge si mauvais
            } else if (pi > 1.2) {
                piElem.style.color = '#f59e0b'; // Orange si modéré
            } else {
                piElem.style.color = '#22c55e'; // Vert si bon
            }
        }

        // Marquer comme actif si des décisions récentes
        if (card) {
            const hasRecentAction = scootData.actions.some(a =>
                a.rsu === rsuId || a.trafficLight === id
            );
            if (hasRecentAction) {
                card.classList.add('active');
            } else {
                card.classList.remove('active');
            }
        }
    });

    // Liste des actions SCOOT
    const actionsList = document.getElementById('scootActionsList');
    if (actionsList && scootData.actions) {
        const recentActions = scootData.actions.slice(-5); // 5 dernières actions

        if (recentActions.length === 0) {
            actionsList.innerHTML = '<div style="color: #94a3b8; font-size: 0.7rem;">Aucune décision récente</div>';
        } else {
            actionsList.innerHTML = recentActions.map(action => {
                let typeClass = 'split';
                let typeLabel = 'SPLIT';

                if (action.type === 'SCOOT_OFFSET') {
                    typeClass = 'offset';
                    typeLabel = 'OFFSET';
                } else if (action.type === 'SCOOT_CYCLE') {
                    typeClass = 'cycle';
                    typeLabel = 'CYCLE';
                }

                const target = action.trafficLight || action.rsu || 'NETWORK';
                const reason = action.reason || '';

                return `
                    <div class="scoot-action-item">
                        <span class="type ${typeClass}">${typeLabel}</span>
                        <span class="target">${target}</span>
                        <span class="reason">${reason}</span>
                    </div>
                `;
            }).join('');
        }
    }
}
