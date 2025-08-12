/**
 * ShopifyLLM A/B Testing Client
 * Client-side JavaScript for Theme App Extensions
 * Handles variant assignment and event tracking
 */

class ShopifyABClient {
  constructor(config = {}) {
    this.apiBaseUrl = config.apiBaseUrl || '/api'
    this.userId = config.userId || this.generateUserId()
    this.debugMode = config.debug || false
    this.assignmentCache = new Map()
    this.eventQueue = []
    this.initialized = false
    
    // Auto-initialize
    this.init()
  }

  /**
   * Initialize the A/B testing client
   */
  async init() {
    try {
      this.log('Initializing ShopifyAB Client...')
      
      // Store user ID in localStorage for consistency
      if (!localStorage.getItem('shopify_ab_user_id')) {
        localStorage.setItem('shopify_ab_user_id', this.userId)
      } else {
        this.userId = localStorage.getItem('shopify_ab_user_id')
      }
      
      // Process any queued events
      await this.processEventQueue()
      
      this.initialized = true
      this.log('ShopifyAB Client initialized successfully')
      
      // Trigger custom event for other scripts
      window.dispatchEvent(new CustomEvent('shopify-ab:initialized', {
        detail: { userId: this.userId }
      }))
      
    } catch (error) {
      console.error('Failed to initialize ShopifyAB Client:', error)
    }
  }

  /**
   * Generate a unique user ID
   */
  generateUserId() {
    return 'user_' + Math.random().toString(36).substr(2, 9) + '_' + Date.now()
  }

  /**
   * Get variant assignment for a user in an experiment
   */
  async getVariant(experimentId) {
    try {
      // Check cache first
      const cacheKey = `${this.userId}_${experimentId}`
      if (this.assignmentCache.has(cacheKey)) {
        return this.assignmentCache.get(cacheKey)
      }

      // Get assignment from server
      const response = await fetch(`${this.apiBaseUrl}/assignments/assign`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          user_id: this.userId,
          experiment_id: experimentId
        })
      })

      if (!response.ok) {
        throw new Error(`Assignment failed: ${response.status}`)
      }

      const data = await response.json()
      const assignment = data.assignment

      // Cache the assignment
      this.assignmentCache.set(cacheKey, assignment)
      
      this.log(`User assigned to variant: ${assignment.variant_name}`, assignment)
      
      return assignment
      
    } catch (error) {
      console.error('Error getting variant assignment:', error)
      return null
    }
  }

  /**
   * Track an event for the current user
   */
  async trackEvent(experimentId, eventType, eventData = {}, revenue = null) {
    const event = {
      user_id: this.userId,
      experiment_id: experimentId,
      event_type: eventType,
      event_data: eventData,
      revenue: revenue,
      timestamp: new Date().toISOString()
    }

    if (!this.initialized) {
      // Queue event if not initialized yet
      this.eventQueue.push(event)
      return
    }

    try {
      const response = await fetch(`${this.apiBaseUrl}/events`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(event)
      })

      if (!response.ok) {
        throw new Error(`Event tracking failed: ${response.status}`)
      }

      this.log(`Event tracked: ${eventType}`, event)
      
      // Trigger custom event
      window.dispatchEvent(new CustomEvent('shopify-ab:event-tracked', {
        detail: { event, experimentId, eventType }
      }))

    } catch (error) {
      console.error('Error tracking event:', error)
      // Optionally queue for retry
      this.eventQueue.push(event)
    }
  }

  /**
   * Process queued events
   */
  async processEventQueue() {
    if (this.eventQueue.length === 0) return

    try {
      const events = [...this.eventQueue]
      this.eventQueue = []

      const response = await fetch(`${this.apiBaseUrl}/events/bulk`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ events })
      })

      if (!response.ok) {
        throw new Error(`Bulk event tracking failed: ${response.status}`)
      }

      this.log(`Processed ${events.length} queued events`)

    } catch (error) {
      console.error('Error processing event queue:', error)
    }
  }

  /**
   * Apply variant content to the page
   */
  async applyVariant(experimentId, targetSelector) {
    try {
      const assignment = await this.getVariant(experimentId)
      
      if (!assignment || !assignment.variant_config) {
        this.log(`No variant assignment for experiment ${experimentId}`)
        return null
      }

      const targetElement = document.querySelector(targetSelector)
      if (!targetElement) {
        console.warn(`Target element not found: ${targetSelector}`)
        return assignment
      }

      const config = assignment.variant_config
      
      // Apply content based on variant type
      if (config.content) {
        // For text content (descriptions, titles, etc.)
        if (targetElement.tagName === 'INPUT' || targetElement.tagName === 'TEXTAREA') {
          targetElement.value = config.content
        } else {
          targetElement.innerHTML = config.content
        }
      }

      // Apply styling if specified
      if (config.styles) {
        Object.assign(targetElement.style, config.styles)
      }

      // Apply attributes if specified
      if (config.attributes) {
        Object.entries(config.attributes).forEach(([key, value]) => {
          targetElement.setAttribute(key, value)
        })
      }

      // Track view event
      await this.trackEvent(experimentId, 'view', {
        variant_id: assignment.variant_id,
        target_selector: targetSelector
      })

      this.log(`Applied variant ${assignment.variant_name} to ${targetSelector}`)
      
      return assignment

    } catch (error) {
      console.error('Error applying variant:', error)
      return null
    }
  }

  /**
   * Set up click tracking for elements
   */
  setupClickTracking(experimentId, selector, eventType = 'click') {
    const elements = document.querySelectorAll(selector)
    
    elements.forEach(element => {
      element.addEventListener('click', async (event) => {
        await this.trackEvent(experimentId, eventType, {
          element_id: element.id,
          element_class: element.className,
          element_text: element.textContent?.trim(),
          page_url: window.location.href
        })
      })
    })

    this.log(`Set up click tracking for ${elements.length} elements`)
  }

  /**
   * Track purchase/conversion events
   */
  async trackPurchase(experimentId, orderValue, orderData = {}) {
    await this.trackEvent(experimentId, 'purchase', {
      ...orderData,
      page_url: window.location.href
    }, orderValue)
  }

  /**
   * Track add to cart events
   */
  async trackAddToCart(experimentId, productData = {}) {
    await this.trackEvent(experimentId, 'add_to_cart', {
      ...productData,
      page_url: window.location.href
    })
  }

  /**
   * Get user's assignment for multiple experiments
   */
  async getUserAssignments() {
    try {
      const response = await fetch(`${this.apiBaseUrl}/assignments/user/${this.userId}`)
      
      if (!response.ok) {
        throw new Error(`Failed to get user assignments: ${response.status}`)
      }

      const data = await response.json()
      return data.assignments

    } catch (error) {
      console.error('Error getting user assignments:', error)
      return []
    }
  }

  /**
   * Debug logging
   */
  log(message, data = null) {
    if (this.debugMode) {
      console.log(`[ShopifyAB] ${message}`, data || '')
    }
  }

  /**
   * Utility method to wait for DOM element
   */
  waitForElement(selector, timeout = 5000) {
    return new Promise((resolve, reject) => {
      const element = document.querySelector(selector)
      if (element) {
        resolve(element)
        return
      }

      const observer = new MutationObserver((mutations, obs) => {
        const element = document.querySelector(selector)
        if (element) {
          obs.disconnect()
          resolve(element)
        }
      })

      observer.observe(document.body, {
        childList: true,
        subtree: true
      })

      setTimeout(() => {
        observer.disconnect()
        reject(new Error(`Element ${selector} not found within ${timeout}ms`))
      }, timeout)
    })
  }
}

// Auto-initialize with global instance
window.ShopifyAB = new ShopifyABClient({
  debug: window.location.search.includes('ab_debug=true')
})

// Convenience functions for Shopify themes
window.shopifyAB = {
  // Test product descriptions
  testProductDescription: async (experimentId, selector = '.product-description') => {
    return await window.ShopifyAB.applyVariant(experimentId, selector)
  },

  // Test product titles
  testProductTitle: async (experimentId, selector = '.product-title') => {
    return await window.ShopifyAB.applyVariant(experimentId, selector)
  },

  // Test CTA buttons
  testCTAButton: async (experimentId, selector = '.product-form button[type="submit"]') => {
    const assignment = await window.ShopifyAB.applyVariant(experimentId, selector)
    
    // Set up click tracking for CTA
    window.ShopifyAB.setupClickTracking(experimentId, selector, 'cta_click')
    
    return assignment
  },

  // Track cart additions
  onAddToCart: (experimentId, productData) => {
    window.ShopifyAB.trackAddToCart(experimentId, productData)
  },

  // Track purchases (call on thank you page)
  onPurchase: (experimentId, orderValue, orderData) => {
    window.ShopifyAB.trackPurchase(experimentId, orderValue, orderData)
  }
}

// Export for module systems
if (typeof module !== 'undefined' && module.exports) {
  module.exports = ShopifyABClient
}
