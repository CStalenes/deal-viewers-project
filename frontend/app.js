const API_URL = "http://127.0.0.1:8000";
let currentTemplateId = null;

function showSection(sectionId) {
    const sections = document.querySelectorAll('.app-section');
    sections.forEach(s => s.classList.add('hidden'));
    
    // reset transparency for main step
    document.getElementById('step-templates').classList.remove('opacity-40', 'pointer-events-none');
    document.getElementById(sectionId).classList.remove('hidden');
}

async function startApp() {
    try {
        const res = await fetch(`${API_URL}/templates/`);
        const data = await res.json();
        
        const listContainer = document.getElementById('template-list');
        listContainer.innerHTML = "";

        data.forEach(item => {
            const isAvailable = item.isActive !== false; 
            const card = document.createElement('div');
            
            card.className = `p-4 rounded-lg shadow border-2 transition-all ${isAvailable 
                ? 'bg-white border-transparent hover:border-blue-500 cursor-pointer' 
                : 'bg-gray-100 border-gray-200 opacity-60 cursor-not-allowed'}`;
            
            card.innerHTML = `
                <div class="flex justify-between items-start">
                    <h3 class="font-bold ${isAvailable ? 'text-blue-600' : 'text-gray-500'}">${item.name}</h3>
                    <span class="text-[10px] font-bold px-2 py-0.5 rounded-full ${isAvailable ? 'bg-green-100 text-green-700' : 'bg-red-100 text-red-700'}">
                        ${isAvailable ? 'ACTIVE' : 'INACTIVE'}
                    </span>
                </div>
                <p class="text-xs text-gray-500 mt-2">${item.description || 'No description provided'}</p>
                <p class="text-[10px] text-gray-400 uppercase mt-1">${item.code || ''}</p>
            `;

            if (isAvailable) {
                card.onclick = () => handleTemplateSelection(item.id || item._id);
            }
            listContainer.appendChild(card);
        });
    } catch (err) {
        console.error("Failed to load templates:", err);
    }
}

function handleTemplateSelection(id) {
    currentTemplateId = id;
    
    // grey out first step and show deals
    document.getElementById('step-templates').classList.add('opacity-40', 'pointer-events-none');
    showSection('step-deals');
    document.getElementById('step-templates').classList.remove('hidden'); 
    
    fetchAvailableDeals(); 
}

async function fetchAvailableDeals() {
    const client = document.getElementById('filter-client')?.value || "";
    const start = document.getElementById('filter-start')?.value || "";
    const end = document.getElementById('filter-end')?.value || "";

    // Build query params
    let endpoint = `${API_URL}/deals?`;
    if (client) endpoint += `client=${client}&`;
    if (start) endpoint += `startDate=${start}&`;
    if (end) endpoint += `endDate=${end}`;

    try {
        const res = await fetch(endpoint);
        const dealData = await res.json();
        
        const dealContainer = document.getElementById('deal-list');
        dealContainer.innerHTML = "";

        dealData.forEach(deal => {
            const row = document.createElement('div');
            row.className = "bg-white p-3 rounded border hover:bg-blue-50 cursor-pointer transition-colors flex justify-between items-center";
            row.innerHTML = `
                <span class="font-medium">${deal.title || deal.reference}</span>
                <span class="text-[10px] text-gray-300">${deal._id}</span>
            `;
            row.onclick = () => renderFinalView(deal.id || deal._id);
            dealContainer.appendChild(row);
        });
    } catch (err) {
        console.error("Error fetching deals:", err);
    }
}

async function renderFinalView(dealId) {
    showSection('step-view');
    try {
        const targetUrl = `${API_URL}/deals/${dealId}/view?templateId=${currentTemplateId}`;
        const res = await fetch(targetUrl);
        const projectedData = await res.json();

        const displayArea = document.getElementById('projected-content');
        let contentHtml = '<div class="divide-y border-t border-gray-100">';
        
        for (const [key, val] of Object.entries(projectedData)) {
            // clean up field names for display
            const prettyLabel = key.replace(/\./g, ' > ')
                                 .replace(/([A-Z])/g, ' $1')
                                 .trim();

            contentHtml += `
                <div class="py-4 flex justify-between items-start">
                    <span class="text-gray-500 font-medium text-sm capitalize">${prettyLabel}</span>
                    <span class="font-bold text-slate-800 text-right">${formatDisplayValue(val, key)}</span>
                </div>
            `;
        }
        contentHtml += '</div>';
        displayArea.innerHTML = contentHtml;
    } catch (err) {
        console.error("Projection failed:", err);
    }
}

document.getElementById('template-form').onsubmit = async (event) => {
    event.preventDefault();
    const tplName = document.getElementById('tpl-name').value;
    
    // map form to payload
    const newTemplate = {
        name: tplName,
        description: document.getElementById('tpl-desc').value,
        code: tplName.toUpperCase().replace(/\s+/g, '_'), 
        visibleFields: document.getElementById('tpl-fields').value.split(',').map(f => f.trim()).filter(f => f !== ""),
        isActive: document.getElementById('tpl-active').checked
    };

    const res = await fetch(`${API_URL}/templates/`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(newTemplate)
    });

    if (res.ok) {
        window.location.reload();
    } else {
        const errorData = await res.json();
        console.warn("Check payload:", errorData);
        alert("Validation error (422). Check console.");
    }
};

document.getElementById('deal-form').onsubmit = async (event) => {
    event.preventDefault();
    const newDeal = {
        title: document.getElementById('d-title').value,
        clientName: document.getElementById('d-client').value,
        financials: {
            totalExclTax: parseFloat(document.getElementById('d-amount').value) || 0,
            margin: parseFloat(document.getElementById('d-margin').value) || 0
        },
        commercial: {
            nextStep: document.getElementById('d-step').value
        },
        createdAt: new Date().toISOString()
    };

    await fetch(`${API_URL}/deals/`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(newDeal)
    });
    window.location.reload();
};

function formatDisplayValue(value, fieldKey = "") {
    if (value === null || value === undefined) return "N/A";
    
    // handle arrays 
    if (Array.isArray(value)) {
        if (value.length === 0) return "No records found";
        return value.map(item => {
            if (typeof item === 'object') {
                return `${item.firstName || ''} ${item.lastName || ''}`.trim() || "Unknown item";
            }
            return item;
        }).join(', ');
    }
    
    // Formatting for currencies and percentage
    if (typeof value === 'number') {
        const keyLower = fieldKey.toLowerCase();
        if (['tax', 'amount', 'margin', 'revenue', 'total'].some(word => keyLower.includes(word))) {
            return new Intl.NumberFormat('en-US', { style: 'currency', currency: 'USD' }).format(value);
        }
        if (keyLower.includes('probability')) return `${value}%`;
        return value.toLocaleString();
    }
    
    return value;
}

startApp();