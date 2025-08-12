// Unified Dashboard JavaScript
class UnifiedDashboard {
    constructor() {
        this.currentJob = null;
        this.refreshInterval = null;
        this.init();
    }

    init() {
        this.setupEventListeners();
        this.loadDashboardStats();
        this.loadRecentStores();
        this.loadActiveExperiments();
        this.setupTabNavigation();
        
        // Auto-refresh every 30 seconds
        this.refreshInterval = setInterval(() => {
            this.loadDashboardStats();
        }, 30000);
    }

    setupEventListeners() {
        // Store creation
        document.getElementById('create-store-btn')?.addEventListener('click', () => {
            this.createStore();
        });

        // A/B testing
        document.getElementById('create-experiment-btn')?.addEventListener('click', () => {
            this.createExperiment();
        });

        document.getElementById('generate-variants-btn')?.addEventListener('click', () => {
            this.generateVariants();
        });

        // Products
        document.getElementById('refresh-products-btn')?.addEventListener('click', () => {
            this.loadProducts();
        });

        // Global refresh
        document.getElementById('refresh-btn')?.addEventListener('click', () => {
            this.refreshAll();
        });
    }

    setupTabNavigation() {
        const tabButtons = document.querySelectorAll('.tab-button');
        const tabContents = document.querySelectorAll('.tab-content');

        tabButtons.forEach(button => {
            button.addEventListener('click', () => {
                const targetTab = button.dataset.tab;

                // Update button states
                tabButtons.forEach(btn => btn.classList.remove('active'));
                button.classList.add('active');

                // Update content visibility
                tabContents.forEach(content => {
                    content.classList.remove('active');
                    if (content.id === targetTab) {
                        content.classList.add('active');
                        
                        // Load content based on tab
                        switch (targetTab) {
                            case 'products':
                                this.loadProducts();
                                break;
                            case 'analytics':
                                this.loadAnalytics();
                                break;
                            case 'ab-testing':
                                this.loadActiveExperiments();
                                break;
                        }
                    }
                });
            });
        });
    }

    async loadDashboardStats() {
        try {
            const response = await fetch('/api/dashboard-stats');
            const data = await response.json();

            if (data.error) {
                throw new Error(data.error);
            }

            // Update stats
            document.getElementById('stores-created').textContent = data.store_creation.completed_stores;
            document.getElementById('ab-tests-running').textContent = data.ab_testing.running_experiments;
            document.getElementById('total-products').textContent = data.products.total_products;
            document.getElementById('total-conversions').textContent = data.ab_testing.total_conversions;

        } catch (error) {
            console.error('Error loading dashboard stats:', error);
        }
    }

    async createStore() {
        const prompt = document.getElementById('store-prompt').value.trim();
        const enableAB = document.getElementById('enable-ab-testing').checked;

        if (!prompt) {
            alert('Please enter a store description');
            return;
        }

        try {
            this.showJobProgress();

            const response = await fetch('/api/create-store-with-ab', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    prompt: prompt,
                    enable_ab_testing: enableAB
                })
            });

            const data = await response.json();

            if (data.error) {
                throw new Error(data.error);
            }

            this.currentJob = data.job_id;
            this.trackJobProgress(data.job_id);

        } catch (error) {
            console.error('Error creating store:', error);
            alert('Error creating store: ' + error.message);
            this.hideJobProgress();
        }
    }

    async trackJobProgress(jobId) {
        const checkProgress = async () => {
            try {
                const response = await fetch(`/api/job-status/${jobId}`);
                const data = await response.json();

                if (data.error) {
                    throw new Error(data.error);
                }

                this.updateJobProgress(data.progress, data.status);

                if (data.status === 'completed') {
                    this.hideJobProgress();
                    this.showJobResult(data.result);
                    this.loadRecentStores();
                    this.loadDashboardStats();
                } else if (data.status === 'failed') {
                    this.hideJobProgress();
                    alert('Store creation failed: ' + data.error);
                } else {
                    // Continue tracking
                    setTimeout(checkProgress, 2000);
                }

            } catch (error) {
                console.error('Error tracking job progress:', error);
                this.hideJobProgress();
            }
        };

        checkProgress();
    }

    updateJobProgress(progress, status) {
        const progressBar = document.getElementById('progress-bar');
        const progressPercent = document.getElementById('progress-percent');
        const progressStatus = document.getElementById('progress-status');

        if (progressBar) progressBar.style.width = `${progress}%`;
        if (progressPercent) progressPercent.textContent = `${progress}%`;
        if (progressStatus) progressStatus.textContent = status;
    }

    showJobProgress() {
        const progressElement = document.getElementById('job-progress');
        if (progressElement) {
            progressElement.classList.remove('hidden');
        }
    }

    hideJobProgress() {
        const progressElement = document.getElementById('job-progress');
        if (progressElement) {
            progressElement.classList.add('hidden');
        }
    }

    showJobResult(result) {
        let message = `Store "${result.concept?.store_name || 'New Store'}" created successfully!\\n`;
        message += `Products created: ${result.products_created || 0}\\n`;
        
        if (result.ab_experiments_created) {
            message += `A/B experiments created: ${result.ab_experiments_created.length}`;
        }
        
        alert(message);
        
        // Clear the form
        document.getElementById('store-prompt').value = '';
    }

    async loadRecentStores() {
        try {
            const response = await fetch('/api/recent-stores');
            const stores = await response.json();

            const container = document.getElementById('recent-stores');
            if (!container) return;

            if (stores.length === 0) {
                container.innerHTML = '<p class="text-gray-500 text-sm">No stores created yet</p>';
                return;
            }

            container.innerHTML = stores.map(store => `
                <div class="p-4 border border-gray-200 rounded-lg hover:bg-gray-50 transition-colors">
                    <div class="flex items-center justify-between">
                        <div>
                            <h4 class="font-medium text-gray-800">${store.store_name}</h4>
                            <p class="text-sm text-gray-500">${store.products_count} products</p>
                        </div>
                        <div class="text-right">
                            <span class="inline-block px-2 py-1 text-xs bg-green-100 text-green-800 rounded-full">
                                ${store.mode}
                            </span>
                        </div>
                    </div>
                </div>
            `).join('');

        } catch (error) {
            console.error('Error loading recent stores:', error);
        }
    }

    async loadActiveExperiments() {
        try {
            const response = await fetch('/api/experiments?status=running&per_page=5');
            const data = await response.json();

            const container = document.getElementById('active-experiments');
            if (!container) return;

            if (!data.experiments || data.experiments.length === 0) {
                container.innerHTML = '<p class="text-gray-500 text-sm">No active experiments</p>';
                return;
            }

            container.innerHTML = data.experiments.map(exp => `
                <div class="p-4 border border-gray-200 rounded-lg hover:bg-gray-50 transition-colors">
                    <div class="flex items-center justify-between">
                        <div>
                            <h4 class="font-medium text-gray-800">${exp.name}</h4>
                            <p class="text-sm text-gray-500">${exp.experiment_type}</p>
                        </div>
                        <div class="text-right">
                            <span class="inline-block px-2 py-1 text-xs bg-blue-100 text-blue-800 rounded-full">
                                ${exp.variant_count} variants
                            </span>
                        </div>
                    </div>
                </div>
            `).join('');

        } catch (error) {
            console.error('Error loading active experiments:', error);
        }
    }

    async createExperiment() {
        // For now, just show an alert - this would open a modal in a full implementation
        alert('Create Experiment feature - would open a detailed form to create new A/B tests');
    }

    async generateVariants() {
        const variantType = document.getElementById('variant-type').value;
        
        try {
            this.showLoading();

            // Mock product data - in reality, this would come from selected product
            const mockProductData = {
                title: "Premium Wireless Bluetooth Headphones",
                category: "electronics",
                price: 199.99,
                features: ["Noise Cancellation", "30-hour Battery", "Quick Charge", "Premium Sound"]
            };

            const response = await fetch('/api/generate-ab-variants', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    product_data: mockProductData,
                    variant_type: variantType,
                    num_variants: 3
                })
            });

            const data = await response.json();
            this.hideLoading();

            if (data.error) {
                throw new Error(data.error);
            }

            this.showVariantsResult(data.variants);

        } catch (error) {
            console.error('Error generating variants:', error);
            this.hideLoading();
            alert('Error generating variants: ' + error.message);
        }
    }

    showVariantsResult(variants) {
        let message = "Generated Variants:\\n\\n";
        
        Object.entries(variants).forEach(([type, variantList]) => {
            message += `${type.toUpperCase()}:\\n`;
            variantList.forEach((variant, index) => {
                message += `${index + 1}. ${variant.name}\\n`;
                message += `   Content: ${variant.content.substring(0, 100)}...\\n\\n`;
            });
        });

        alert(message);
    }

    async loadProducts() {
        try {
            this.showLoading();

            const response = await fetch('/api/products');
            const data = await response.json();

            this.hideLoading();

            const container = document.getElementById('products-grid');
            if (!container) return;

            if (data.error) {
                container.innerHTML = `<div class="col-span-full text-center py-8">
                    <p class="text-red-500">${data.error}</p>
                </div>`;
                return;
            }

            if (!data.products || data.products.length === 0) {
                container.innerHTML = `<div class="col-span-full text-center py-8">
                    <p class="text-gray-500">No products found</p>
                </div>`;
                return;
            }

            container.innerHTML = data.products.map(product => `
                <div class="bg-white rounded-lg shadow-md overflow-hidden hover:shadow-lg transition-shadow">
                    <div class="p-4">
                        <h4 class="font-medium text-gray-800 mb-2">${product.title}</h4>
                        <p class="text-sm text-gray-600 mb-3">${product.body_html ? product.body_html.substring(0, 100) + '...' : 'No description'}</p>
                        <div class="flex items-center justify-between">
                            <span class="text-lg font-bold text-green-600">$${product.variants?.[0]?.price || 'N/A'}</span>
                            <button class="px-3 py-1 bg-blue-600 text-white text-sm rounded hover:bg-blue-700 transition-colors"
                                    onclick="dashboard.editProduct('${product.id}')">
                                Edit
                            </button>
                        </div>
                    </div>
                </div>
            `).join('');

        } catch (error) {
            console.error('Error loading products:', error);
            this.hideLoading();
        }
    }

    async editProduct(productId) {
        const prompt = window.prompt('What changes would you like to make to this product?');
        if (!prompt) return;

        try {
            this.showLoading();

            const response = await fetch('/api/edit-product', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    product_id: productId,
                    prompt: prompt
                })
            });

            const data = await response.json();
            this.hideLoading();

            if (data.error) {
                throw new Error(data.error);
            }

            alert('Product editing started! Check the job status for updates.');
            this.loadProducts(); // Refresh products

        } catch (error) {
            console.error('Error editing product:', error);
            this.hideLoading();
            alert('Error editing product: ' + error.message);
        }
    }

    loadAnalytics() {
        // Destroy existing charts if they exist
        if (this.performanceChart) {
            this.performanceChart.destroy();
        }
        if (this.funnelChart) {
            this.funnelChart.destroy();
        }
        
        // Load new charts
        this.loadPerformanceChart();
        this.loadFunnelChart();
        this.loadAnalyticsStats();
    }

    loadPerformanceChart() {
        const ctx = document.getElementById('performance-chart');
        if (!ctx) return;

        this.performanceChart = new Chart(ctx, {
            type: 'line',
            data: {
                labels: ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'],
                datasets: [{
                    label: 'Conversions',
                    data: [12, 19, 3, 5, 2, 3, 7],
                    borderColor: '#667eea',
                    backgroundColor: 'rgba(102, 126, 234, 0.1)',
                    tension: 0.4
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        display: true,
                        position: 'top'
                    }
                },
                scales: {
                    y: {
                        beginAtZero: true
                    }
                }
            }
        });
    }

    loadFunnelChart() {
        const ctx = document.getElementById('funnel-chart');
        if (!ctx) return;

        this.funnelChart = new Chart(ctx, {
            type: 'bar',
            data: {
                labels: ['Views', 'Clicks', 'Add to Cart', 'Purchase'],
                datasets: [{
                    label: 'Conversion Funnel',
                    data: [1000, 500, 200, 50],
                    backgroundColor: [
                        '#667eea',
                        '#764ba2',
                        '#f093fb',
                        '#f5576c'
                    ]
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        display: false
                    }
                },
                scales: {
                    y: {
                        beginAtZero: true
                    }
                }
            }
        });
    }

    async loadAnalyticsStats() {
        try {
            // Load analytics stats
            document.getElementById('total-experiments').textContent = '3';
            document.getElementById('active-tests').textContent = '1';
            document.getElementById('avg-conversion').textContent = '2.4%';

            // Load recent results
            const resultsContainer = document.getElementById('recent-results');
            if (resultsContainer) {
                resultsContainer.innerHTML = `
                    <div class="text-sm text-gray-600 p-3 bg-gray-50 rounded border-l-4 border-blue-500">
                        <strong>Product Title Test:</strong> Variant B showing 15% higher conversion rate
                    </div>
                    <div class="text-sm text-gray-600 p-3 bg-gray-50 rounded border-l-4 border-green-500">
                        <strong>CTA Button Test:</strong> "Buy Now" outperforming "Add to Cart" by 8%
                    </div>
                `;
            }
        } catch (error) {
            console.error('Error loading analytics stats:', error);
        }
    }

    showLoading() {
        const modal = document.getElementById('loading-modal');
        if (modal) {
            modal.classList.remove('hidden');
            modal.classList.add('flex');
        }
    }

    hideLoading() {
        const modal = document.getElementById('loading-modal');
        if (modal) {
            modal.classList.add('hidden');
            modal.classList.remove('flex');
        }
    }

    refreshAll() {
        this.loadDashboardStats();
        this.loadRecentStores();
        this.loadActiveExperiments();
        
        // Refresh current tab content
        const activeTab = document.querySelector('.tab-content.active');
        if (activeTab) {
            switch (activeTab.id) {
                case 'products':
                    this.loadProducts();
                    break;
                case 'analytics':
                    this.loadAnalytics();
                    break;
            }
        }
    }
}

// Initialize dashboard when page loads
let dashboard;
document.addEventListener('DOMContentLoaded', () => {
    dashboard = new UnifiedDashboard();
});
