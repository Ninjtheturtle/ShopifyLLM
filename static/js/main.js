// AI Shopify Store Creator - JavaScript
class StoreCreator {
    constructor() {
        this.init();
        this.checkConnection();
        this.loadRecentStores();
        this.initSettings();
        this.initProductManagement();
        this.currentEditJob = null;
    }

    init() {
        // Get DOM elements
        this.form = document.getElementById('storeCreationForm');
        this.promptInput = document.getElementById('storePrompt');
        this.createBtn = document.getElementById('createBtn');
        this.progressSection = document.getElementById('progressSection');
        this.resultsSection = document.getElementById('resultsSection');
        this.recentStores = document.getElementById('recentStores');
        this.refreshBtn = document.getElementById('refreshRecent');

        // Settings elements
        this.settingsBtn = document.getElementById('settingsBtn');
        this.settingsModal = document.getElementById('settingsModal');
        this.modalOverlay = document.getElementById('modalOverlay');
        this.closeSettingsModal = document.getElementById('closeSettingsModal');
        this.saveSettings = document.getElementById('saveSettings');
        this.cancelSettings = document.getElementById('cancelSettings');

        // Bind event listeners
        this.form.addEventListener('submit', (e) => this.handleSubmit(e));
        this.refreshBtn.addEventListener('click', () => this.loadRecentStores());

        // Add auto-resize to textarea
        this.promptInput.addEventListener('input', this.autoResize);
    }

    initSettings() {
        // Settings modal event listeners
        this.settingsBtn.addEventListener('click', () => this.openSettings());
        this.closeSettingsModal.addEventListener('click', () => this.closeSettings());
        this.modalOverlay.addEventListener('click', () => this.closeSettings());
        this.saveSettings.addEventListener('click', () => this.saveStoreSettings());
        this.cancelSettings.addEventListener('click', () => this.closeSettings());

        // Tab switching
        const tabBtns = document.querySelectorAll('.tab-btn');
        tabBtns.forEach(btn => {
            btn.addEventListener('click', () => {
                const tabId = btn.dataset.tab;
                this.switchTab(tabId);
            });
        });

        // Color input synchronization
        this.initColorInputs();

        // Load settings when modal opens
        this.loadStoreSettings();
    }

    initColorInputs() {
        const colorInputs = ['primaryColor', 'secondaryColor', 'accentColor'];
        colorInputs.forEach(inputId => {
            const colorInput = document.getElementById(inputId);
            const textInput = colorInput.nextElementSibling;
            
            colorInput.addEventListener('input', (e) => {
                textInput.value = e.target.value;
            });
        });
    }

    async openSettings() {
        await this.loadStoreSettings();
        this.settingsModal.classList.add('active');
        this.modalOverlay.classList.add('active');
        document.body.style.overflow = 'hidden';
    }

    closeSettings() {
        this.settingsModal.classList.remove('active');
        this.modalOverlay.classList.remove('active');
        document.body.style.overflow = '';
    }

    switchTab(tabId) {
        // Remove active class from all tabs and contents
        document.querySelectorAll('.tab-btn').forEach(btn => btn.classList.remove('active'));
        document.querySelectorAll('.tab-content').forEach(content => content.classList.remove('active'));

        // Add active class to selected tab and content
        document.querySelector(`[data-tab="${tabId}"]`).classList.add('active');
        document.getElementById(`${tabId}-tab`).classList.add('active');
    }

    async loadStoreSettings() {
        try {
            const response = await fetch('/api/store-settings');
            const settings = await response.json();

            if (!response.ok) {
                throw new Error(settings.error || 'Failed to load settings');
            }

            // Populate form fields
            this.populateSettingsForm(settings);

        } catch (error) {
            console.error('Failed to load store settings:', error);
            this.showToast('Failed to load store settings', 'error');
        }
    }

    populateSettingsForm(settings) {
        // General settings
        document.getElementById('storeName').value = settings.store_name || '';
        document.getElementById('storeDomain').value = settings.domain || '';
        document.getElementById('storeDescription').value = settings.store_description || '';
        document.getElementById('currency').value = settings.currency || 'USD';
        document.getElementById('timezone').value = settings.timezone || 'America/Los_Angeles';

        // Contact settings
        document.getElementById('storeEmail').value = settings.email || '';
        document.getElementById('storePhone').value = settings.phone || '';
        
        // Address
        if (settings.address) {
            document.getElementById('street').value = settings.address.street || '';
            document.getElementById('city').value = settings.address.city || '';
            document.getElementById('state').value = settings.address.state || '';
            document.getElementById('zip').value = settings.address.zip || '';
            document.getElementById('country').value = settings.address.country || 'United States';
        }

        // Theme settings
        document.getElementById('themeName').value = settings.theme || 'Dawn';
        document.getElementById('logoUrl').value = settings.logo_url || '';
    }

    async saveStoreSettings() {
        try {
            this.saveSettings.disabled = true;
            this.saveSettings.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Saving...';

            // Collect data from all forms
            const settingsData = this.collectSettingsData();

            // Save general and contact settings
            const response = await fetch('/api/store-settings', {
                method: 'PUT',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(settingsData)
            });

            const result = await response.json();

            if (!response.ok) {
                throw new Error(result.error || 'Failed to save settings');
            }

            // Save theme settings separately
            const themeData = this.collectThemeData();
            const themeResponse = await fetch('/api/store-theme', {
                method: 'PUT',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(themeData)
            });

            const themeResult = await themeResponse.json();

            if (!themeResponse.ok) {
                throw new Error(themeResult.error || 'Failed to save theme');
            }

            this.showToast('Settings saved successfully!', 'success');
            this.closeSettings();

        } catch (error) {
            console.error('Failed to save settings:', error);
            this.showToast(error.message, 'error');
        } finally {
            this.saveSettings.disabled = false;
            this.saveSettings.innerHTML = '<i class="fas fa-save"></i> Save Changes';
        }
    }

    collectSettingsData() {
        return {
            store_name: document.getElementById('storeName').value,
            store_description: document.getElementById('storeDescription').value,
            email: document.getElementById('storeEmail').value,
            phone: document.getElementById('storePhone').value,
            currency: document.getElementById('currency').value,
            timezone: document.getElementById('timezone').value,
            address: {
                street: document.getElementById('street').value,
                city: document.getElementById('city').value,
                state: document.getElementById('state').value,
                zip: document.getElementById('zip').value,
                country: document.getElementById('country').value
            }
        };
    }

    collectThemeData() {
        return {
            theme_name: document.getElementById('themeName').value,
            primary_color: document.getElementById('primaryColor').value,
            secondary_color: document.getElementById('secondaryColor').value,
            accent_color: document.getElementById('accentColor').value,
            logo_url: document.getElementById('logoUrl').value
        };
    }

    autoResize(e) {
        e.target.style.height = 'auto';
        e.target.style.height = e.target.scrollHeight + 'px';
    }

    async checkConnection() {
        const statusIndicator = document.getElementById('statusIndicator');
        const statusText = document.getElementById('statusText');

        try {
            statusIndicator.className = 'status-indicator checking';
            statusText.textContent = 'Checking connection...';

            const response = await fetch('/api/config');
            const config = await response.json();

            if (config.shopify_configured) {
                statusIndicator.className = 'status-indicator connected';
                statusText.textContent = `Connected to ${config.shop_domain} (${config.store_mode} mode)`;
            } else {
                statusIndicator.className = 'status-indicator disconnected';
                statusText.textContent = 'Shopify not configured - Demo mode only';
            }
        } catch (error) {
            statusIndicator.className = 'status-indicator disconnected';
            statusText.textContent = 'Connection failed';
            console.error('Connection check failed:', error);
        }
    }

    async handleSubmit(e) {
        e.preventDefault();
        
        const prompt = this.promptInput.value.trim();
        if (!prompt) {
            this.showToast('Please enter a store description', 'warning');
            return;
        }

        try {
            // Disable form and show progress
            this.setFormLoading(true);
            this.showProgress();

            // Create store
            const response = await fetch('/api/create-store', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ prompt })
            });

            const result = await response.json();

            if (!response.ok) {
                throw new Error(result.error || 'Failed to create store');
            }

            // Monitor job progress
            this.monitorJob(result.job_id);
            this.showToast('Store creation started!', 'success');

        } catch (error) {
            this.setFormLoading(false);
            this.hideProgress();
            this.showToast(error.message, 'error');
            console.error('Store creation failed:', error);
        }
    }

    async monitorJob(jobId) {
        const progressFill = document.getElementById('progressFill');
        const progressText = document.getElementById('progressText');

        const checkProgress = async () => {
            try {
                const response = await fetch(`/api/job-status/${jobId}`);
                const job = await response.json();

                if (!response.ok) {
                    throw new Error(job.error || 'Failed to check job status');
                }

                // Update progress
                progressFill.style.width = `${job.progress}%`;

                switch (job.status) {
                    case 'pending':
                        progressText.textContent = 'Preparing to create your store...';
                        break;
                    case 'running':
                        progressText.textContent = 'AI is creating your store...';
                        break;
                    case 'completed':
                        progressText.textContent = 'Store created successfully!';
                        this.showResults(job.result);
                        this.setFormLoading(false);
                        this.loadRecentStores(); // Refresh recent stores
                        return; // Stop monitoring
                    case 'failed':
                        throw new Error(job.error || 'Store creation failed');
                }

                // Continue monitoring
                setTimeout(checkProgress, 2000);

            } catch (error) {
                this.setFormLoading(false);
                this.hideProgress();
                this.showToast(error.message, 'error');
                console.error('Job monitoring failed:', error);
            }
        };

        // Start monitoring
        checkProgress();
    }

    showProgress() {
        this.progressSection.style.display = 'block';
        this.resultsSection.style.display = 'none';
        
        // Scroll to progress section
        this.progressSection.scrollIntoView({ behavior: 'smooth' });
    }

    hideProgress() {
        this.progressSection.style.display = 'none';
    }

    showResults(result) {
        this.hideProgress();
        this.resultsSection.style.display = 'block';

        // Populate store details
        const storeDetails = document.getElementById('storeDetails');
        const concept = result.concept || {};
        
        storeDetails.innerHTML = `
            <div class="detail-card">
                <h4><i class="fas fa-store"></i> Store Information</h4>
                <div class="store-summary">
                    <div class="summary-item">
                        <strong>Store Name:</strong> ${concept.store_name || 'Unknown Store'}
                    </div>
                    <div class="summary-item">
                        <strong>Tagline:</strong> ${concept.tagline || 'Premium Products'}
                    </div>
                    <div class="summary-item">
                        <strong>Products Created:</strong> ${result.products_created || 0}
                    </div>
                    <div class="summary-item">
                        <strong>Mode:</strong> 
                        <span class="mode-badge mode-${result.mode || 'demo'}">${result.mode || 'demo'}</span>
                    </div>
                </div>
            </div>
            
            ${concept.products && concept.products.length > 0 ? `
            <div class="detail-card">
                <h4><i class="fas fa-box"></i> Products</h4>
                <div class="product-grid">
                    ${concept.products.map(product => `
                        <div class="product-item">
                            <div class="product-name">${product.name}</div>
                            <div class="product-price">$${product.price}</div>
                            <div class="product-inventory">${product.inventory} in stock</div>
                        </div>
                    `).join('')}
                </div>
            </div>
            ` : ''}
            
            ${concept.blog_posts && concept.blog_posts.length > 0 ? `
            <div class="detail-card">
                <h4><i class="fas fa-blog"></i> Blog Posts</h4>
                <div class="blog-list">
                    ${concept.blog_posts.map(post => `<div class="blog-item">${post}</div>`).join('')}
                </div>
            </div>
            ` : ''}
        `;

        // Set up action buttons
        const viewBtn = document.getElementById('viewStoreBtn');
        const adminBtn = document.getElementById('adminBtn');

        if (result.store_url) {
            viewBtn.onclick = () => window.open(result.store_url, '_blank');
            viewBtn.style.display = 'flex';
        } else {
            viewBtn.style.display = 'none';
        }

        if (result.admin_url) {
            adminBtn.onclick = () => window.open(result.admin_url, '_blank');
            adminBtn.style.display = 'flex';
        } else {
            adminBtn.style.display = 'none';
        }

        // Scroll to results
        this.resultsSection.scrollIntoView({ behavior: 'smooth' });
    }

    setFormLoading(loading) {
        const btn = this.createBtn;
        const form = this.form;

        if (loading) {
            btn.disabled = true;
            btn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Creating Store...';
            form.classList.add('loading');
        } else {
            btn.disabled = false;
            btn.innerHTML = '<i class="fas fa-rocket"></i> Create Store with AI';
            form.classList.remove('loading');
        }
    }

    async loadRecentStores() {
        try {
            const response = await fetch('/api/recent-stores');
            const stores = await response.json();

            if (!response.ok) {
                throw new Error('Failed to load recent stores');
            }

            this.displayRecentStores(stores);

        } catch (error) {
            console.error('Failed to load recent stores:', error);
            this.recentStores.innerHTML = `
                <div class="error-message">
                    <i class="fas fa-exclamation-triangle"></i>
                    Failed to load recent stores
                </div>
            `;
        }
    }

    displayRecentStores(stores) {
        if (stores.length === 0) {
            this.recentStores.innerHTML = `
                <div class="empty-state">
                    <i class="fas fa-store"></i>
                    <p>No stores created yet. Create your first store above!</p>
                </div>
            `;
            return;
        }

        this.recentStores.innerHTML = stores.map(store => `
            <div class="recent-store">
                <div class="store-header">
                    <div class="store-info">
                        <h4>${store.store_name}</h4>
                        <p>${store.prompt.substring(0, 100)}${store.prompt.length > 100 ? '...' : ''}</p>
                        <div class="store-meta">
                            <span><i class="fas fa-box"></i> ${store.products_count} products</span>
                            <span><i class="fas fa-calendar"></i> ${this.formatDate(store.created_at)}</span>
                            <span class="mode-badge mode-${store.mode}">${store.mode}</span>
                        </div>
                    </div>
                    ${store.store_url ? `
                    <div class="store-actions">
                        <button class="action-btn view-btn" onclick="window.open('${store.store_url}', '_blank')">
                            <i class="fas fa-external-link-alt"></i>
                            View
                        </button>
                    </div>
                    ` : ''}
                </div>
            </div>
        `).join('');
    }

    formatDate(dateString) {
        if (!dateString) return 'Unknown';
        
        const date = new Date(dateString);
        const now = new Date();
        const diffMs = now - date;
        const diffHours = Math.floor(diffMs / (1000 * 60 * 60));
        const diffDays = Math.floor(diffHours / 24);

        if (diffHours < 1) return 'Just now';
        if (diffHours < 24) return `${diffHours}h ago`;
        if (diffDays < 7) return `${diffDays}d ago`;
        
        return date.toLocaleDateString();
    }

    showToast(message, type = 'info') {
        const container = document.getElementById('toastContainer');
        const toast = document.createElement('div');
        
        const icons = {
            success: 'fas fa-check-circle',
            error: 'fas fa-exclamation-circle',
            warning: 'fas fa-exclamation-triangle',
            info: 'fas fa-info-circle'
        };

        toast.className = `toast ${type}`;
        toast.innerHTML = `
            <i class="${icons[type] || icons.info}"></i>
            <span>${message}</span>
        `;

        container.appendChild(toast);

        // Auto remove after 5 seconds
        setTimeout(() => {
            if (toast.parentNode) {
                toast.parentNode.removeChild(toast);
            }
        }, 5000);

        // Remove on click
        toast.addEventListener('click', () => {
            if (toast.parentNode) {
                toast.parentNode.removeChild(toast);
            }
        });
    }
}

// Example prompt functions
function useExample(prompt) {
    const promptInput = document.getElementById('storePrompt');
    promptInput.value = prompt;
    promptInput.focus();
    
    // Trigger auto-resize
    promptInput.style.height = 'auto';
    promptInput.style.height = promptInput.scrollHeight + 'px';
    
    // Scroll to form
    document.getElementById('storeCreationForm').scrollIntoView({ behavior: 'smooth' });
}

// Product Management Functionality
StoreCreator.prototype.initProductManagement = function() {
    // Get product management elements
    this.loadProductsBtn = document.getElementById('loadProductsBtn');
    this.productsContainer = document.getElementById('productsContainer');
    this.productsGrid = document.getElementById('productsGrid');
    this.productEditor = document.getElementById('productEditor');
    this.productEditForm = document.getElementById('productEditForm');
    this.editProgress = document.getElementById('editProgress');
    this.closeEditorBtn = document.getElementById('closeEditorBtn');
    this.cancelEditBtn = document.getElementById('cancelEditBtn');

    // Bind product management events
    this.loadProductsBtn.addEventListener('click', () => this.loadProducts());
    this.productEditForm.addEventListener('submit', (e) => this.handleProductEdit(e));
    this.closeEditorBtn.addEventListener('click', () => this.closeProductEditor());
    this.cancelEditBtn.addEventListener('click', () => this.closeProductEditor());
};

StoreCreator.prototype.loadProducts = async function() {
    try {
        this.loadProductsBtn.disabled = true;
        this.loadProductsBtn.innerHTML = '<i class="fas fa-sync-alt fa-spin"></i> Loading...';
        
        // Show loading state
        this.productsGrid.innerHTML = `
            <div class="loading-products">
                <i class="fas fa-sync-alt fa-spin"></i>
                <p>Loading your products...</p>
            </div>
        `;
        this.productsContainer.style.display = 'block';

        const response = await fetch('/api/products');
        const data = await response.json();

        if (!response.ok) {
            throw new Error(data.error || 'Failed to load products');
        }

        this.displayProducts(data.products);
        this.showToast(`Loaded ${data.count} products`, 'success');

    } catch (error) {
        console.error('Error loading products:', error);
        this.showToast('Failed to load products: ' + error.message, 'error');
        this.productsGrid.innerHTML = `
            <div class="no-products">
                <i class="fas fa-exclamation-triangle"></i>
                <p>Failed to load products</p>
                <p style="font-size: 0.875rem; margin-top: 0.5rem;">${error.message}</p>
            </div>
        `;
    } finally {
        this.loadProductsBtn.disabled = false;
        this.loadProductsBtn.innerHTML = '<i class="fas fa-sync-alt"></i> Load Products';
    }
};

StoreCreator.prototype.displayProducts = function(products) {
    if (!products || products.length === 0) {
        this.productsGrid.innerHTML = `
            <div class="no-products">
                <i class="fas fa-box-open"></i>
                <p>No products found</p>
                <p style="font-size: 0.875rem; margin-top: 0.5rem;">Create your first store to see products here</p>
            </div>
        `;
        return;
    }

    this.productsGrid.innerHTML = products.map(product => {
        const price = product.variants && product.variants[0] ? 
            `$${parseFloat(product.variants[0].price).toFixed(2)}` : 'No price';
        
        const imageUrl = product.images && product.images[0] ? 
            product.images[0].src : '/static/images/no-image.png';
        
        const description = this.stripHtml(product.body_html || 'No description available');
        
        return `
            <div class="product-card" data-product-id="${product.id}">
                <div class="product-card-header">
                    <h3 class="product-title">${this.escapeHtml(product.title)}</h3>
                    <span class="product-price">${price}</span>
                </div>
                
                <img src="${imageUrl}" alt="${this.escapeHtml(product.title)}" class="product-image" 
                     onerror="this.src='/static/images/no-image.png'">
                
                <p class="product-description">${this.escapeHtml(description.substring(0, 150))}...</p>
                
                <div class="product-meta">
                    <span><i class="fas fa-tag"></i> ID: ${product.id}</span>
                    <span><i class="fas fa-calendar"></i> ${new Date(product.created_at).toLocaleDateString()}</span>
                </div>
                
                <div class="product-actions">
                    <button class="edit-product-btn" onclick="storeCreator.editProduct('${product.id}')">
                        <i class="fas fa-edit"></i>
                        Edit Product
                    </button>
                </div>
            </div>
        `;
    }).join('');
};

StoreCreator.prototype.editProduct = async function(productId) {
    try {
        // Load product details
        const response = await fetch(`/api/products/${productId}`);
        const data = await response.json();

        if (!response.ok) {
            throw new Error(data.error || 'Failed to load product');
        }

        this.showProductEditor(data.product);

    } catch (error) {
        console.error('Error loading product for editing:', error);
        this.showToast('Failed to load product: ' + error.message, 'error');
    }
};

StoreCreator.prototype.showProductEditor = function(product) {
    const price = product.variants && product.variants[0] ? 
        `$${parseFloat(product.variants[0].price).toFixed(2)}` : 'No price';
    
    const imageUrl = product.images && product.images[0] ? 
        product.images[0].src : '/static/images/no-image.png';

    // Store current product for editing
    this.currentProduct = product;

    // Populate current product display
    document.getElementById('currentProduct').innerHTML = `
        <div class="current-product-title">
            <i class="fas fa-box"></i>
            ${this.escapeHtml(product.title)}
        </div>
        <div class="current-product-details">
            <div class="current-product-detail">
                <i class="fas fa-dollar-sign"></i>
                <span>Price: ${price}</span>
            </div>
            <div class="current-product-detail">
                <i class="fas fa-tag"></i>
                <span>ID: ${product.id}</span>
            </div>
            <div class="current-product-detail">
                <i class="fas fa-calendar"></i>
                <span>Created: ${new Date(product.created_at).toLocaleDateString()}</span>
            </div>
            <div class="current-product-detail">
                <i class="fas fa-eye"></i>
                <span>Published: ${product.published ? 'Yes' : 'No'}</span>
            </div>
        </div>
        <img src="${imageUrl}" alt="${this.escapeHtml(product.title)}" class="product-image" 
             onerror="this.src='/static/images/no-image.png'" style="margin-top: 1rem;">
    `;

    // Clear edit form
    document.getElementById('editPrompt').value = '';

    // Show editor
    this.productEditor.style.display = 'block';
    this.productEditor.scrollIntoView({ behavior: 'smooth' });
};

StoreCreator.prototype.closeProductEditor = function() {
    this.productEditor.style.display = 'none';
    this.currentProduct = null;
    
    // Hide progress if showing
    this.editProgress.style.display = 'none';
    
    // Stop monitoring if active
    if (this.currentEditJob) {
        clearInterval(this.currentEditJob);
        this.currentEditJob = null;
    }
};

StoreCreator.prototype.handleProductEdit = async function(e) {
    e.preventDefault();

    if (!this.currentProduct) {
        this.showToast('No product selected for editing', 'error');
        return;
    }

    const formData = new FormData(e.target);
    const prompt = formData.get('prompt').trim();

    if (!prompt) {
        this.showToast('Please describe what you want to change', 'error');
        return;
    }

    try {
        // Disable form
        const editBtn = document.getElementById('editProductBtn');
        editBtn.disabled = true;
        editBtn.innerHTML = '<i class="fas fa-sync-alt fa-spin"></i> Starting...';

        // Start edit job
        const response = await fetch('/api/edit-product', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                product_id: this.currentProduct.id,
                prompt: prompt
            })
        });

        const data = await response.json();

        if (!response.ok) {
            throw new Error(data.error || 'Failed to start product editing');
        }

        // Start monitoring edit progress
        this.startEditProgressMonitoring(data.job_id);
        this.showToast('Product editing started!', 'info');

    } catch (error) {
        console.error('Error starting product edit:', error);
        this.showToast('Failed to start editing: ' + error.message, 'error');
        
        // Re-enable form
        const editBtn = document.getElementById('editProductBtn');
        editBtn.disabled = false;
        editBtn.innerHTML = '<i class="fas fa-save"></i> Update Product';
    }
};

StoreCreator.prototype.startEditProgressMonitoring = function(jobId) {
    this.editProgress.style.display = 'block';
    
    const progressFill = document.getElementById('editProgressFill');
    const progressText = document.getElementById('editProgressText');
    
    // Initial state
    progressFill.style.width = '0%';
    progressText.textContent = 'Starting product update...';

    this.currentEditJob = setInterval(async () => {
        try {
            const response = await fetch(`/api/job-status/${jobId}`);
            const status = await response.json();

            if (!response.ok) {
                throw new Error('Failed to get job status');
            }

            // Update progress
            progressFill.style.width = `${status.progress}%`;
            progressText.textContent = this.getEditProgressText(status.progress);

            if (status.status === 'completed') {
                clearInterval(this.currentEditJob);
                this.currentEditJob = null;
                
                progressFill.style.width = '100%';
                progressText.textContent = 'Product updated successfully!';
                
                this.showToast('Product updated successfully!', 'success');
                
                // Hide progress and editor after a delay
                setTimeout(() => {
                    this.editProgress.style.display = 'none';
                    this.closeProductEditor();
                    
                    // Reload products to show changes
                    this.loadProducts();
                }, 2000);
                
            } else if (status.status === 'failed') {
                clearInterval(this.currentEditJob);
                this.currentEditJob = null;
                
                progressText.textContent = 'Edit failed: ' + (status.error || 'Unknown error');
                this.showToast('Product edit failed: ' + (status.error || 'Unknown error'), 'error');
                
                // Re-enable form
                const editBtn = document.getElementById('editProductBtn');
                editBtn.disabled = false;
                editBtn.innerHTML = '<i class="fas fa-save"></i> Update Product';
            }

        } catch (error) {
            console.error('Error checking edit status:', error);
            clearInterval(this.currentEditJob);
            this.currentEditJob = null;
            
            progressText.textContent = 'Error checking progress';
            this.showToast('Error monitoring progress', 'error');
        }
    }, 2000);
};

StoreCreator.prototype.getEditProgressText = function(progress) {
    if (progress < 20) return 'Analyzing product changes...';
    if (progress < 40) return 'Loading current product data...';
    if (progress < 60) return 'Applying updates...';
    if (progress < 80) return 'Updating product in Shopify...';
    if (progress < 100) return 'Generating new images...';
    return 'Finalizing changes...';
};

// Utility functions for product management
StoreCreator.prototype.stripHtml = function(html) {
    const tmp = document.createElement('div');
    tmp.innerHTML = html;
    return tmp.textContent || tmp.innerText || '';
};

StoreCreator.prototype.escapeHtml = function(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
};

// Initialize when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    window.storeCreator = new StoreCreator();
});
