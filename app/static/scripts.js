// Wrap all code in DOMContentLoaded to ensure elements exist
document.addEventListener('DOMContentLoaded', function() {
  console.log("DOM loaded, initializing app...");
  
  // Check if loading overlay exists
  const loadingOverlay = document.getElementById("loadingOverlay");
  const loadingText = document.getElementById("loadingText");
  console.log("Loading overlay found:", !!loadingOverlay);
  console.log("Loading text found:", !!loadingText);

async function loadItems() {
  const loadingOverlay = document.getElementById("loadingOverlay");
  const loadingText = document.getElementById("loadingText");
  
  if (!loadingOverlay || !loadingText) {
    console.error("Loading overlay elements not found!");
    // Fallback without loading indicator
    try {
      const res = await fetch("/items");
      const data = await res.json();
      renderItems(data);
    } catch (error) {
      console.error("Error loading items:", error);
    }
    return;
  }
  
  // Show loading only if container is empty (initial load)
  const container = document.getElementById("itemsContainer");
  if (!container.innerHTML.trim()) {
    loadingText.textContent = "Loading items...";
    loadingOverlay.classList.remove("hidden");
  }
  
  try {
    const res = await fetch("/items");
    const data = await res.json();
    renderItems(data);
  } catch (error) {
    console.error("Error loading items:", error);
    container.innerHTML = `
      <div class="col-span-full text-center py-12">
        <p class="text-red-500 text-lg">Failed to load items</p>
      </div>
    `;
  } finally {
    loadingOverlay.classList.add("hidden");
  }
}

function renderItems(items) {
  const container = document.getElementById("itemsContainer");
  const showScores = document.getElementById("showScores")?.checked || false;
  
  container.innerHTML = "";
  
  if (!items || items.length === 0) {
    container.innerHTML = `
      <div class="col-span-full text-center py-12">
        <p class="text-gray-500 text-lg">No items found</p>
      </div>
    `;
    return;
  }
  
  items.forEach(i => {
    const color = i.category === "Lost" ? "bg-red-500" : "bg-green-500";
    const badge = i.category === "Lost" 
      ? `<span class="inline-block bg-white text-red-600 px-2 py-1 rounded-full text-xs">LOST</span>` 
      : `<span class="inline-block bg-white text-green-600 px-2 py-1 rounded-full text-xs">FOUND</span>`;
    
    // Show similarity score if available and checkbox is checked
    const similarityBadge = (showScores && i.similarity !== undefined) 
      ? `<span class="inline-block bg-yellow-100 text-yellow-800 px-2 py-1 rounded-full text-xs ml-2">Match: ${Math.round(i.similarity * 100)}%</span>`
      : '';
    
    const adminControls = isAdmin() ? `
        <div class="flex space-x-2 mt-3">
          <button data-id="${i.id}" class="editBtn px-3 py-1 bg-yellow-400 text-sm rounded">Edit</button>
          <button data-id="${i.id}" class="deleteBtn px-3 py-1 bg-red-500 text-sm text-white rounded">Delete</button>
        </div>` : '';

    container.innerHTML += `
      <div class="bg-white rounded-lg shadow overflow-hidden hover:shadow-lg transition">
        ${i.image_path ? `<img src="/${i.image_path.replace(/^\/?uploads\/?/, 'uploads/') }" class="w-full h-48 object-cover">` : ""}
        <div class="p-4">
          <div class="flex items-center justify-between mb-2">
            ${badge}
            ${similarityBadge}
          </div>
          <h2 class="text-lg font-bold text-gray-800 mb-2">${i.title}</h2>
          <p class="text-sm text-gray-600 mb-3">${i.description}</p>
          ${i.location ? `<p class="text-xs text-gray-500">📍 ${i.location}</p>` : ''}
          ${i.phone ? `<p class="text-xs text-gray-700 mt-1">📞 ${i.phone}</p>` : ''}
          ${adminControls}
        </div>
      </div>`;
  });
}

// Improved search handler with loading indicators
document.getElementById("searchBtn").addEventListener("click", async () => {
  const text = document.getElementById("searchText").value.trim();
  const image = document.getElementById("searchImage").files[0];
  const searchInfo = document.getElementById("searchInfo");
  const loadingOverlay = document.getElementById("loadingOverlay");
  const loadingText = document.getElementById("loadingText");
  
  // Validate that at least one input is provided
  if (!text && !image) {
    searchInfo.classList.remove("hidden");
    searchInfo.innerHTML = `<span class="text-red-600">⚠️ Enter text or upload an image</span>`;
    return;
  }
  
  const form = new FormData();
  if (text) form.append("description", text);
  if (image) form.append("image", image);

  // Show loading overlay
  if (loadingOverlay && loadingText) {
    loadingText.textContent = "Searching with AI...";
    loadingOverlay.classList.remove("hidden");
    searchInfo.classList.add("hidden");
  }

  try {
    const res = await fetch("/search", { method: "POST", body: form });
    const data = await res.json();
    
    // Hide loading
    if (loadingOverlay) {
      loadingOverlay.classList.add("hidden");
    }
    
    if (!res.ok) {
      searchInfo.classList.remove("hidden");
      searchInfo.innerHTML = `<span class="text-red-600">❌ ${data.detail || "Search failed"}</span>`;
      return;
    }
    
    if (data.results && data.results.length > 0) {
      renderItems(data.results);
      searchInfo.classList.remove("hidden");
      searchInfo.innerHTML = `<span class="text-green-600">✅ Found ${data.results.length} item${data.results.length > 1 ? 's' : ''}</span>`;
    } else {
      renderItems([]);
      searchInfo.classList.remove("hidden");
      searchInfo.innerHTML = `<span class="text-yellow-600">⚠️ No matching items found</span>`;
    }
  } catch (error) {
    console.error("Search error:", error);
    if (loadingOverlay) {
      loadingOverlay.classList.add("hidden");
    }
    searchInfo.classList.remove("hidden");
    searchInfo.innerHTML = `<span class="text-red-600">❌ Search error occurred</span>`;
  }
});

// Clear search and reload all items
document.getElementById("clearBtn").addEventListener("click", () => {
  document.getElementById("searchText").value = "";
  document.getElementById("searchImage").value = "";
  document.getElementById("searchInfo").classList.add("hidden");
  loadItems();
});

// modal and add-item flow
const addBtn = document.getElementById("addBtn");
const modal = document.getElementById("modal");
const closeModal = document.getElementById("closeModal");
const addForm = document.getElementById("addForm");
const itemIdInput = document.getElementById('itemId');
const submitBtn = document.getElementById('addSubmitBtn');
const logoutLink = document.getElementById('logoutLink'); // removed loginLink

function showModal() { modal.classList.add('show'); }
function hideModal() { modal.classList.remove('show'); }

addBtn.addEventListener('click', () => { showModal(); });
closeModal.addEventListener('click', () => { hideModal(); });

// admin UI: show/hide logout link
function updateAuthLinks(){
  if(isAdmin()){
    logoutLink.classList.remove('hidden');
  } else {
    logoutLink.classList.add('hidden');
  }
}

function isAdmin(){
  return document.cookie.split(';').some(c=>c.trim().startsWith('admin_token='));
}

// listen for delegated edit/delete clicks
document.addEventListener('click', async (e) => {
  if(e.target.matches('.editBtn')){
    const id = e.target.getAttribute('data-id');
    const res = await fetch('/items');
    const items = await res.json();
    const it = items.find(x=>String(x.id)===String(id));
    if(!it) return alert('Item not found');
    itemIdInput.value = it.id;
    document.getElementById('title').value = it.title || '';
    document.getElementById('description').value = it.description || '';
    document.getElementById('category').value = it.category || 'Lost';
    document.getElementById('location').value = it.location || '';
    document.getElementById('phone').value = it.phone || ''; // updated
    submitBtn.textContent = 'Update Item';
    showModal();
  }

  if(e.target.matches('.deleteBtn')){
    const id = e.target.getAttribute('data-id');
    if(!confirm('Delete this item?')) return;
    
    const loadingOverlay = document.getElementById("loadingOverlay");
    const loadingText = document.getElementById("loadingText");
    loadingText.textContent = "Deleting item...";
    loadingOverlay.classList.remove("hidden");
    
    try {
      const res = await fetch(`/delete-item/${id}`, { method: 'DELETE' });
      loadingOverlay.classList.add("hidden");
      
      if(res.ok){
        await loadItems();
      } else {
        const err = await res.json().catch(()=>({}));
        alert('Failed to delete: ' + (err.detail || res.statusText));
      }
    } catch (error) {
      loadingOverlay.classList.add("hidden");
      alert('Failed to delete: ' + error.message);
    }
  }
});

addForm.addEventListener('submit', async (e) => {
  e.preventDefault();
  const loadingOverlay = document.getElementById("loadingOverlay");
  const loadingText = document.getElementById("loadingText");
  
  const form = new FormData();
  form.append('title', document.getElementById('title').value || 'Untitled');
  form.append('description', document.getElementById('description').value || '');
  form.append('category', document.getElementById('category').value || 'Lost');
  form.append('location', document.getElementById('location').value || '');
  form.append('phone', document.getElementById('phone').value || ''); // updated
  const img = document.getElementById('addImage').files[0];
  if (img) form.append('image', img);

  const editingId = itemIdInput.value;
  const endpoint = editingId ? `/update-item/${editingId}` : '/add-item';
  
  // Show loading overlay
  loadingText.textContent = editingId ? "Updating item..." : "Adding item with AI processing...";
  loadingOverlay.classList.remove("hidden");

  try {
    const res = await fetch(endpoint, { method: 'POST', body: form });
    loadingOverlay.classList.add("hidden");

    if (res.ok) {
      hideModal();
      addForm.reset();
      itemIdInput.value = '';
      submitBtn.textContent = 'Add Item';
      await loadItems();
    } else {
      const err = await res.json().catch(() => ({}));
      alert('Failed to save item: ' + (err.detail || res.statusText));
    }
  } catch (error) {
    loadingOverlay.classList.add("hidden");
    alert('Failed to save item: ' + error.message);
  }
});

// close modal when clicking outside content
modal.addEventListener('click', (e) => {
  if (e.target === modal) hideModal();
});

// initial load
updateAuthLinks();
loadItems();

}); // End of DOMContentLoaded
