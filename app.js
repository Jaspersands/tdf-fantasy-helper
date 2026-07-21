// Shared logic for Fantasy TdF Helper
const APP_STATE = {
    riders: [],
    currentRace: 'tdf',
    races: {
        'tdf': 'Tour de France 2026',
        'tdf2025': 'Tour de France 2025',
        'vuelta': 'Vuelta 2025'
    }
};

// Map nationality flag emoji to ISO codes
const EMOJI_TO_COUNTRY = {
    '🇸🇮': 'SI', '🇩🇰': 'DK', '🇮🇹': 'IT', '🇧🇪': 'BE', '🇳🇱': 'NL', '🇬🇧': 'GB',
    '🇵🇹': 'PT', '🇦🇺': 'AU', '🇪🇸': 'ES', '🇩🇪': 'DE', '🇫🇷': 'FR', '🇺🇸': 'US',
    '🇪🇨': 'EC', '🇪🇷': 'ER', '🇦🇹': 'AT', '🇨🇴': 'CO', '🇮🇪': 'IE', '🇳🇴': 'NO',
    '🇨🇭': 'CH', '🇷🇺': 'RU', '🇨🇦': 'CA', '🇰🇿': 'KZ', '🇳🇿': 'NZ', '🇨🇿': 'CZ',
    '🇱🇺': 'LU', '🇪🇪': 'EE', '🇱🇻': 'LV', '🇻🇪': 'VE', '🇸🇰': 'SK', '🇲🇽': 'MX',
    '🇿🇦': 'ZA', '🇵🇱': 'PL', '🇦🇷': 'AR'
};

// Format utilities
function formatPrice(price) {
    return price + ' credits';
}

function formatPoints(points) {
    return Math.round(points).toLocaleString();
}

function getCategoryBadgeClass(category) {
    const classes = {
        'Leaders': 'category-badge-leaders',
        'Sprinters': 'category-badge-sprinters', 
        'Climbers': 'category-badge-climbers',
        'All-rounders': 'category-badge-all-rounders'
    };
    return classes[category] || 'bg-secondary';
}

function getFlagEmoji(countryCode) {
    if (!countryCode) return '🏳️';
    // Reverse lookup or mapping
    const flagMap = {
        'SI': '🇸🇮', 'DK': '🇩🇰', 'IT': '🇮🇹', 'BE': '🇧🇪', 'NL': '🇳🇱', 'GB': '🇬🇧',
        'PT': '🇵🇹', 'AU': '🇦🇺', 'ES': '🇪🇸', 'DE': '🇩🇪', 'FR': '🇫🇷', 'US': '🇺🇸',
        'EC': '🇪🇨', 'ER': '🇪🇷', 'AT': '🇦🇹', 'CO': '🇨🇴', 'IE': '🇮🇪', 'NO': '🇳🇴',
        'CH': '🇨🇭', 'RU': '🇷🇺', 'CA': '🇨🇦', 'KZ': '🇰🇿', 'NZ': '🇳🇿', 'CZ': '🇨🇿',
        'LU': '🇱🇺', 'EE': '🇪🇪', 'LV': '🇱🇻', 'VE': '🇻🇪', 'SK': '🇸🇰', 'MX': '🇲🇽',
        'ZA': '🇿🇦', 'PL': '🇵🇱', 'AR': '🇦🇷'
    };
    return flagMap[countryCode.toUpperCase()] || '🏳️';
}

// Parse URL Query parameters
function getQueryParam(name) {
    const params = new URLSearchParams(window.location.search);
    return params.get(name);
}

// Get array query parameters (e.g. ?riders=A&riders=B)
function getQueryParamArray(name) {
    const params = new URLSearchParams(window.location.search);
    return params.getAll(name);
}

// Load dataset and initialize page
async function initApp() {
    // 1. Detect current race from URL, default to 'tdf'
    const raceParam = getQueryParam('race');
    if (raceParam && APP_STATE.races[raceParam]) {
        APP_STATE.currentRace = raceParam;
    } else {
        APP_STATE.currentRace = 'tdf';
    }

    // 2. Fetch the JSON data
    try {
        const response = await fetch('riders_data.json');
        const data = await response.json();
        APP_STATE.riders = data[APP_STATE.currentRace] || [];
        console.log(`Loaded ${APP_STATE.riders.length} riders for race ${APP_STATE.currentRace}`);
    } catch (e) {
        console.error('Error loading riders database:', e);
    }

    // 3. Sync all navbar links to keep the active race parameter
    syncNavbarLinks();

    // 4. Update the active race name display in header
    updateRaceSelectorDisplay();
}

// Update race selector active class and text label
function updateRaceSelectorDisplay() {
    const dropdownBtnText = document.querySelector('#raceDropdown span');
    if (dropdownBtnText) {
        dropdownBtnText.textContent = APP_STATE.races[APP_STATE.currentRace] || 'Select Race';
    }

    // Set active link highlight in dropdown menu
    document.querySelectorAll('.race-option').forEach(link => {
        const race = link.getAttribute('data-race');
        if (race === APP_STATE.currentRace) {
            link.classList.add('active');
        } else {
            link.classList.remove('active');
        }
        // Update the href dynamically to point to the current page with new race
        const currentPath = window.location.pathname.split('/').pop() || 'index.html';
        // Preserve any custom query params like riders if we are on compare page
        const params = new URLSearchParams(window.location.search);
        params.set('race', race);
        link.href = `${currentPath}?${params.toString()}`;
    });
}

// Appends current race parameter to all navigation tabs
function syncNavbarLinks() {
    document.querySelectorAll('.nav-link, .navbar-brand').forEach(link => {
        const hrefAttr = link.getAttribute('href');
        if (!hrefAttr || hrefAttr.startsWith('http') || hrefAttr === '#') return;

        try {
            const urlParts = hrefAttr.split('?');
            const path = urlParts[0];
            const linkParams = new URLSearchParams(urlParts[1] || '');
            
            // Set the race query parameter
            linkParams.set('race', APP_STATE.currentRace);
            
            link.setAttribute('href', `${path}?${linkParams.toString()}`);
        } catch (e) {
            console.error('Error syncing navbar link:', hrefAttr, e);
        }
    });
}

// Compare List Storage Manager
const CompareManager = {
    get() {
        const saved = localStorage.getItem(`compare_${APP_STATE.currentRace}`);
        return saved ? JSON.parse(saved) : [];
    },
    save(list) {
        localStorage.setItem(`compare_${APP_STATE.currentRace}`, JSON.stringify(list));
        // Trigger global page updates if necessary
        if (window.updateComparePanel) {
            window.updateComparePanel();
        }
    },
    add(riderName) {
        const list = this.get();
        if (!list.includes(riderName) && list.length < 5) {
            list.push(riderName);
            this.save(list);
            return true;
        }
        return false;
    },
    remove(riderName) {
        let list = this.get();
        list = list.filter(name => name !== riderName);
        this.save(list);
    },
    clear() {
        this.save([]);
    }
};

// Team Squad Storage Manager
const TeamManager = {
    get() {
        const saved = localStorage.getItem(`team_${APP_STATE.currentRace}`);
        return saved ? JSON.parse(saved) : [];
    },
    save(team) {
        localStorage.setItem(`team_${APP_STATE.currentRace}`, JSON.stringify(team));
    },
    clear() {
        this.save([]);
    }
};

// Shared Comparison Panel Draw logic (exists on bottom of riders page)
function initComparePanelUI() {
    // Create comparison panel HTML if it doesn't exist
    let panel = document.getElementById('comparePanel');
    if (!panel) {
        panel = document.createElement('div');
        panel.id = 'comparePanel';
        panel.className = 'compare-panel card shadow-lg';
        panel.style.display = 'none';
        panel.innerHTML = `
            <div class="card-header bg-dark text-white d-flex justify-content-between align-items-center py-2">
                <h6 class="mb-0"><i class="fas fa-balance-scale"></i> Compare Riders (<span id="compareCount">0</span>/5)</h6>
                <button type="button" class="btn-close btn-close-white" onclick="clearCompare()"></button>
            </div>
            <div class="card-body py-2 px-3">
                <div id="compareList" class="d-flex flex-wrap gap-1 mb-2"></div>
                <div class="d-flex justify-content-end gap-2">
                    <button class="btn btn-sm btn-outline-secondary" onclick="clearCompare()">Clear</button>
                    <button class="btn btn-sm btn-primary" onclick="goToCompare()">Compare Side-by-Side</button>
                </div>
            </div>
        `;
        document.body.appendChild(panel);
    }
    updateComparePanel();
}

function updateComparePanel() {
    const list = CompareManager.get();
    const panel = document.getElementById('comparePanel');
    const countSpan = document.getElementById('compareCount');
    const listDiv = document.getElementById('compareList');
    
    if (!panel) return;
    
    if (countSpan) countSpan.textContent = list.length;
    
    if (list.length > 0) {
        panel.style.display = 'block';
        if (listDiv) {
            listDiv.innerHTML = list.map(name => `
                <span class="badge bg-secondary d-inline-flex align-items-center gap-1">
                    ${name} 
                    <i class="fas fa-times-circle cursor-pointer" onclick="removeFromCompare('${name.replace(/'/g, "\\'")}')"></i>
                </span>
            `).join('');
        }
    } else {
        panel.style.display = 'none';
    }
}

function addToCompare(name) {
    const added = CompareManager.add(name);
    if (!added) {
        const list = CompareManager.get();
        if (list.includes(name)) {
            alert("Rider is already added to comparison!");
        } else if (list.length >= 5) {
            alert("You can compare up to 5 riders at once.");
        }
    }
    updateComparePanel();
}

function removeFromCompare(name) {
    CompareManager.remove(name);
    updateComparePanel();
}

function clearCompare() {
    CompareManager.clear();
    updateComparePanel();
}

function goToCompare() {
    const list = CompareManager.get();
    if (list.length < 2) {
        alert("Please select at least 2 riders to compare.");
        return;
    }
    const params = list.map(name => `riders=${encodeURIComponent(name)}`).join('&');
    window.location.href = `compare.html?race=${APP_STATE.currentRace}&${params}`;
}
