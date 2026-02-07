let currentMode = 'youtube';

function switchMode(mode) {
    currentMode = mode;

    // Update Tabs
    document.querySelectorAll('.tab-btn').forEach(btn => btn.classList.remove('active'));
    if (mode === 'youtube') {
        document.getElementById('tabYT').classList.add('active');
        document.getElementById('urlInput').placeholder = "Paste YouTube Video URL here...";
        document.body.classList.remove('spotify-mode');
    } else {
        document.getElementById('tabSpotify').classList.add('active');
        document.getElementById('urlInput').placeholder = "Paste Spotify Track URL here...";
        document.body.classList.add('spotify-mode');
    }

    // Reset UI
    document.getElementById('resultCard').style.display = 'none';
    document.getElementById('urlInput').value = '';
    setStatus('');
}

async function fetchInfo() {
    const url = document.getElementById('urlInput').value.trim();
    if (!url) return alert("Please enter a URL");

    setLoading(true);
    setStatus('Fetching metadata...');
    document.getElementById('resultCard').style.display = 'none';

    try {
        const response = await fetch(`/api/info?url=${encodeURIComponent(url)}`);
        const data = await response.json();

        if (!response.ok) throw new Error(data.detail || 'Failed to fetch info');

        renderResults(data);
        setStatus('');

    } catch (e) {
        setStatus(e.message, true);
        console.error(e);
    } finally {
        setLoading(false);
    }
}

let selectedFormat = null;
let currentMediaUrl = null;

function renderResults(data) {
    const card = document.getElementById('resultCard');
    const title = document.getElementById('mediaTitle');
    const thumb = document.getElementById('thumbImg');
    const duration = document.getElementById('mediaDuration');
    const spotifyBadge = document.getElementById('spotifyBadge');
    const formatsGrid = document.getElementById('formatsGrid');
    const downloadAction = document.getElementById('downloadAction');

    // Reset Selection
    selectedFormat = null;
    currentMediaUrl = null;
    downloadAction.style.display = 'none';

    // Determine data source
    let info = data.youtube_match || data;
    let isSpotify = data.type === 'spotify';

    currentMediaUrl = info.original_url;

    title.textContent = info.title;
    thumb.src = info.thumbnail;
    duration.innerHTML = `<i class="fa-regular fa-clock"></i> ${formatTime(info.duration)}`;

    if (isSpotify) {
        spotifyBadge.style.display = 'inline-block';
        title.innerHTML = `${data.spotify_meta.title} <span style="font-size:0.8em; color:var(--text-secondary); display:block; margin-top:5px;">by ${data.spotify_meta.artist}</span>`;
    } else {
        spotifyBadge.style.display = 'none';
    }

    // Formats
    formatsGrid.innerHTML = '';

    // Add Best Audio Option First
    addFormatCard(formatsGrid, {
        resolution: 'Audio Only',
        ext: 'mp3',
        filesize: 'Best Quality'
    }, info.original_url, 'audio');

    // Add Video Options
    if (!isSpotify && info.formats) {
        info.formats.forEach(fmt => {
            addFormatCard(formatsGrid, fmt, info.original_url, fmt.format_id);
        });
    }

    card.style.display = 'block';

    // Setup Download Button Listener
    document.getElementById('startDownloadBtn').onclick = () => {
        if (selectedFormat && currentMediaUrl) {
            downloadMedia(currentMediaUrl, selectedFormat, document.getElementById('startDownloadBtn'));
        }
    };
}

function addFormatCard(container, fmt, url, formatId) {
    const card = document.createElement('div');
    const isAudio = formatId === 'audio';

    card.className = `format-card ${isAudio ? 'audio' : 'video'}`;
    card.innerHTML = `
        <i class="icon fa-solid ${isAudio ? 'fa-music' : 'fa-film'}"></i>
        <span class="res">${fmt.resolution}</span>
        <span class="size">${fmt.filesize ? formatSize(fmt.filesize) : fmt.filesize || ''}</span>
    `;

    card.onclick = () => {
        // Deselect others
        container.querySelectorAll('.format-card').forEach(c => c.classList.remove('active'));
        // Select this
        card.classList.add('active');
        // Store
        selectedFormat = formatId;
        // Show Download Button
        document.getElementById('downloadAction').style.display = 'block';
    };

    container.appendChild(card);
}

async function downloadMedia(url, formatId, btnElement) {
    // Visual Feedback
    const originalContent = btnElement.innerHTML;
    btnElement.innerHTML = `<div class="loader-spinner" style="display:inline-block; border-color: rgba(255,255,255,0.3); border-top-color:#fff;"></div>`;
    btnElement.style.pointerEvents = 'none';

    setStatus('Generating download link...');

    try {
        const response = await fetch(`/api/download?url=${encodeURIComponent(url)}&format_id=${formatId}`);
        const data = await response.json();

        if (!response.ok || !data.success) throw new Error(data.detail || data.error || 'Failed to generate link');

        setStatus('Link generated! Starting download...');

        // Clean Direct Download
        if (data.url) {
            window.open(data.url, '_blank');
        } else {
            throw new Error("No download URL returned");
        }

        setStatus('Done!', false);

    } catch (e) {
        setStatus(e.message, true);
    } finally {
        // Reset Button
        btnElement.innerHTML = originalContent;
        btnElement.style.pointerEvents = 'auto';
    }
}

// Helpers
function setLoading(loading) {
    const btn = document.getElementById('fetchBtn');
    const spinner = btn.querySelector('.loader-spinner');
    const txt = btn.querySelector('.btn-txt');

    if (loading) {
        spinner.style.display = 'block';
        txt.style.display = 'none';
        btn.disabled = true;
    } else {
        spinner.style.display = 'none';
        txt.style.display = 'block';
        btn.disabled = false;
    }
}

function setStatus(msg, isError = false) {
    const el = document.getElementById('statusMsg');
    el.style.display = msg ? 'block' : 'none';
    el.textContent = msg;
    el.style.color = isError ? '#ff4d4d' : 'var(--text-secondary)';
}

function formatTime(seconds) {
    if (!seconds) return "00:00";
    const m = Math.floor(seconds / 60);
    const s = seconds % 60;
    return `${m}:${s.toString().padStart(2, '0')}`;
}

function formatSize(bytes) {
    if (!bytes) return '';
    if (typeof bytes === 'string') return bytes;
    const mb = bytes / (1024 * 1024);
    return `${mb.toFixed(1)} MB`;
}
