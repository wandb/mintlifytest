// Mintlify Tab Fade Animations - Universal Approach
(function() {
  'use strict';
  
  // Enhanced CSS for smooth tab animations
  const animationCSS = `
    /* Tab content fade animations with ultra-specific selectors */
    div.tabs.tab-container [data-component-part="tab-content"].prose.dark\\:prose-dark.overflow-x-auto.mintlify-tab-fade-out {
      opacity: 0 !important;
      transition: opacity 0.25s cubic-bezier(0.4, 0, 0.2, 1) !important;
    }
    
    div.tabs.tab-container [data-component-part="tab-content"].prose.dark\\:prose-dark.overflow-x-auto.mintlify-tab-fade-in {
      opacity: 1 !important;
      transition: opacity 0.25s cubic-bezier(0.4, 0, 0.2, 1) !important;
    }
    
    /* Ensure content starts visible */
    div.tabs.tab-container [data-component-part="tab-content"].prose.dark\\:prose-dark.overflow-x-auto {
      opacity: 1;
    }
  `;
  
  // Inject CSS
  const style = document.createElement('style');
  style.textContent = animationCSS;
  document.head.appendChild(style);
  
  // Global state to track ongoing animations
  let isAnimating = false;
  let animationTimeout = null;
  
  function findTabContainers() {
    const containers = [];
    
    // Look for ARIA-based tabs
    const ariaTabLists = document.querySelectorAll('[role="tablist"]');
    
    // Look for .tabs elements (Mintlify style)
    const tabsElements = document.querySelectorAll('.tabs');
    
    // Process each potential container
    [...ariaTabLists, ...tabsElements].forEach(container => {
      const allButtons = container.querySelectorAll('button');
      const tabButtons = container.querySelectorAll('button[data-component-part="tab-button"]');
      
      // Check if this looks like a tab container
      const hasTabButtons = tabButtons.length > 0;
      const buttonTexts = Array.from(tabButtons).map(btn => btn.textContent.trim());
      const hasTabLikeText = buttonTexts.some(text => 
        text.length > 0 && text.length < 50 && 
        !text.includes('Copy') && !text.includes('Show') && !text.includes('Hide')
      );
      
      if (hasTabButtons && hasTabLikeText) {
        containers.push(container);
      }
    });
    
    return containers;
  }
  
  function getCurrentTabContent(container) {
    // Find the current visible tab content
    const contentDiv = container.querySelector('[data-component-part="tab-content"]');
    return contentDiv;
  }
  
  function handleTabClick(clickedButton, isProgrammatic = false) {
    // If this is a programmatic click from our own code, let it pass through
    if (isProgrammatic) {
      return true;
    }
    
    if (isAnimating) {
      return false; // Block the click
    }
    
    isAnimating = true;
    
    // Clear any existing timeout
    if (animationTimeout) {
      clearTimeout(animationTimeout);
    }
    
    // Find the tab container
    const container = clickedButton.closest('.tabs.tab-container');
    if (!container) {
      isAnimating = false;
      return true;
    }
    
    // Get current content before the switch
    const currentContent = getCurrentTabContent(container);
    
    if (currentContent) {
      // Start fade out
      currentContent.classList.add('mintlify-tab-fade-out');
      currentContent.classList.remove('mintlify-tab-fade-in');
      
      // Wait for fade out to complete, then allow the tab switch
      animationTimeout = setTimeout(() => {
        // Create a programmatic click event with our custom flag
        const event = new MouseEvent('click', {
          bubbles: true,
          cancelable: true,
          view: window
        });
        
        // Mark this as a programmatic click to avoid our handler intercepting it
        event._isProgrammatic = true;
        
        isAnimating = false; // Allow the programmatic click to proceed
        clickedButton.dispatchEvent(event);
        
        // Wait for Mintlify to switch content, then fade in
        setTimeout(() => {
          // Find the new content (might be in a different container now)
          const newContainer = document.querySelector('.tabs.tab-container') || container;
          const newContent = getCurrentTabContent(newContainer) || 
                           document.querySelector('[data-component-part="tab-content"]');
          
          if (newContent) {
            // Ensure it starts invisible
            newContent.classList.add('mintlify-tab-fade-out');
            newContent.classList.remove('mintlify-tab-fade-in');
            
            // Force a reflow
            newContent.offsetHeight;
            
            // Start fade in
            setTimeout(() => {
              newContent.classList.remove('mintlify-tab-fade-out');
              newContent.classList.add('mintlify-tab-fade-in');
              
              // Clean up after animation
              setTimeout(() => {
                newContent.classList.remove('mintlify-tab-fade-in', 'mintlify-tab-fade-out');
              }, 300);
            }, 10);
          }
        }, 50);
      }, 250); // Wait for fade out duration
      
      return false; // Prevent the immediate click
    } else {
      isAnimating = false;
      return true; // Allow normal click
    }
  }
  
  // Use event delegation to handle all tab button clicks
  document.addEventListener('click', function(e) {
    // Check if the clicked element is a Mintlify tab button
    if (e.target.matches('button[data-component-part="tab-button"]')) {
      // Check if this is a programmatic click from our own code
      const isProgrammatic = e._isProgrammatic === true;
      
      const shouldPrevent = !handleTabClick(e.target, isProgrammatic);
      
      if (shouldPrevent) {
        e.preventDefault();
        e.stopPropagation();
        return false;
      }
    }
  }, true); // Use capture phase to intercept before other handlers
  
  // Debug function to check page structure
  function debugPageStructure() {
    // Check for different tab structures
    const tabLists = document.querySelectorAll('[role="tablist"]');
    const tabsElements = document.querySelectorAll('.tabs');
    const allButtons = document.querySelectorAll('button');
    
    tabLists.forEach((el, i) => el);
    
    tabsElements.forEach((el, i) => el);
    
    allButtons.forEach((btn, i) => {
      const text = btn.textContent.trim();
      if (text && text.length < 50 && (
        text.includes('Command') || text.includes('Python') || text.includes('notebook') ||
        btn.hasAttribute('data-component-part') || btn.closest('.tabs')
      )) {
        // Tab-like button found
      }
    });
    
    // Check for potential tab content
    const allDivs = document.querySelectorAll('div');
    
    let contentCount = 0;
    allDivs.forEach((div, i) => {
      if (contentCount < 10 && (
        div.hasAttribute('data-component-part') ||
        div.classList.contains('tab-content') ||
        div.classList.contains('prose') ||
        div.textContent.includes('pip install') ||
        div.textContent.includes('import wandb')
      )) {
        contentCount++;
      }
    });
  }
  
  // Run debug on tab clicks for troubleshooting
  document.addEventListener('click', (e) => {
    if (e.target.matches('button[data-component-part="tab-button"]') && !e._isProgrammatic) {
      setTimeout(debugPageStructure, 100);
    }
  });
  
})(); 