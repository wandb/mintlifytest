// Left-side navigation animations
(function() {
  
  // Function to check if an element is the sidebar toggle button
  function isSidebarToggleButton(element) {
    const button = element.closest('button');
    if (!button) return false;
    
    // Check for specific positioning classes that indicate this is the sidebar toggle
    const hasToggleClasses = button.matches('button[class*="absolute"][class*="top-5"][class*="right-5"]');
    
    // Check for arrow icons in the button
    const svg = button.querySelector('svg');
    const hasArrowIcon = svg && (
      (svg.style.maskImage && (svg.style.maskImage.includes('arrow-left-from-line') || svg.style.maskImage.includes('arrow-right-from-line') || svg.style.maskImage.includes('arrow-right-to-line'))) ||
      (svg.style.webkitMaskImage && (svg.style.webkitMaskImage.includes('arrow-left-from-line') || svg.style.webkitMaskImage.includes('arrow-right-from-line') || svg.style.webkitMaskImage.includes('arrow-right-to-line')))
    );
    
    // Only return true if it has BOTH the positioning classes AND the arrow icon
    return hasToggleClasses && hasArrowIcon;
  }
  
  // Function to find all navigation topics that are visually below a given element
  function getTopicsBelow(clickedElement) {
    // Look for the actual navigation content container
    const navContainer = document.querySelector('#sidebar-content') || 
                         document.querySelector('#navigation-items') ||
                         document.querySelector('aside, [class*="sidebar-content"], [id*="sidebar"]') || 
                         document.querySelector('[role="navigation"]') ||
                         document.body;
    
    // Get the Y position of the clicked element's parent container
    const clickedRect = clickedElement.getBoundingClientRect();
    const clickedBottom = clickedRect.bottom;
    
    // Find all navigation items - be more inclusive to catch all navigation elements
    const allTopics = navContainer.querySelectorAll('div[class*="group"], div[class*="cursor-pointer"], a[href], button, [class*="flex items-center"]');
    
    const topicsBelow = [];
    const processedTexts = new Set(); // Track processed text content to avoid duplicates
    
    Array.from(allTopics).forEach((topic, index) => {
      const topicRect = topic.getBoundingClientRect();
      const text = topic.textContent?.trim();
      
      // Skip if we've already processed an element with this text content
      if (processedTexts.has(text)) {
        return;
      }
      
      // If this topic is visually below the clicked element
      if (topicRect.top > clickedBottom && 
          topic !== clickedElement && 
          !clickedElement.contains(topic) &&
          !topic.contains(clickedElement)) {
        
        // Make sure this is a real navigation item with content
        if (text && text.length > 0 && text.length < 100) {
          // Find the appropriate container to animate - look for the parent group
          const containerToAnimate = topic.closest('div[class*="group"]') || topic;
          
          if (!topicsBelow.includes(containerToAnimate)) {
            topicsBelow.push(containerToAnimate);
            processedTexts.add(text);
          }
        }
      }
    });
    
    return topicsBelow;
  }
  
  // Function to slide topics down by a specific amount
  function slideTopicsDown(topics, slideDistance) {
    topics.forEach(topic => {
      // Clear any existing transforms first
      topic.style.transform = '';
      topic.style.transition = '';
      
      // Force a reflow
      topic.offsetHeight;
      
      // Apply the new transform with will-change for better performance
      topic.style.willChange = 'transform';
      topic.style.transition = 'transform 0.3s cubic-bezier(0.25, 0.46, 0.45, 0.94)';
      topic.style.transform = `translateY(${slideDistance}px)`;
    });
  }
  
  // Function to slide topics back to original position
  function slideTopicsUp(topics) {
    topics.forEach(topic => {
      topic.style.transition = 'transform 0.3s cubic-bezier(0.25, 0.46, 0.45, 0.94)';
      topic.style.transform = 'translateY(0)';
      
      // Clean up after animation
      setTimeout(() => {
        topic.style.transform = '';
        topic.style.transition = '';
        topic.style.willChange = '';
      }, 350);
    });
  }
  
  // Monitor for navigation clicks - use capture phase to catch before Mintlify processes
  document.addEventListener('click', function(e) {
    // Skip processing if this is the sidebar toggle button
    if (isSidebarToggleButton(e.target)) {
      return; // Let Mintlify handle the sidebar toggle
    }
    
    // Look for the actual clickable navigation element
    const clickedElement = e.target.closest('.flex-1, button, [role="button"]') || e.target;
    const navContainer = e.target.closest('nav, aside, [role="navigation"], [class*="sidebar"], #navigation-items');
    
    // Check if this is a navigation item that can expand
    const parentContainer = e.target.closest('div[class*="group"], li, [class*="cursor-pointer"]') || 
                           e.target.closest('div[class*="flex items-center"]');
    
    // Check for existing children or if this looks like an expandable item
    const hasChildren = parentContainer?.querySelector('ul, ol') || 
                       (parentContainer && (
                         parentContainer.textContent.includes('Models') || 
                         parentContainer.textContent.includes('Experiments') ||
                         parentContainer.textContent.includes('Guides')
                       ));
    
    // Only proceed if this looks like a navigation click AND it's not the sidebar toggle
    if (clickedElement && (navContainer || parentContainer) && !isSidebarToggleButton(clickedElement)) {
      // Get topics below this element BEFORE Mintlify changes anything
      const referenceElement = parentContainer || clickedElement;
      const topicsBelow = getTopicsBelow(referenceElement);
      
      if (topicsBelow.length > 0) {
        // Check if there's already a UL (meaning we're about to collapse)
        const existingContent = parentContainer?.querySelector('ul') || 
                               parentContainer?.querySelector('ol') ||
                               parentContainer?.parentElement?.querySelector('ul');
        
        // Also check if any of the topics below are actually children that were just expanded
        const hasExpandedChildren = topicsBelow.some(topic => {
          return parentContainer?.contains(topic) || 
                 topic.textContent?.includes('Overview') || 
                 topic.textContent?.includes('Experiments');
        });
        
        if ((existingContent && existingContent.offsetHeight > 0) || hasExpandedChildren) {
          // Filter out the child topics - we only want to animate topics that are truly below
          const realTopicsBelow = topicsBelow.filter(topic => {
            const text = topic.textContent?.trim();
            return !parentContainer?.contains(topic) && 
                   !text?.includes('Overview') && 
                   !text?.includes('Experiments');
          });
          
          if (realTopicsBelow.length > 0) {
            // Store the current position of topics below before collapse
            const firstTopicBelow = realTopicsBelow[0];
            const currentPosition = firstTopicBelow.getBoundingClientRect().top;
            
            // Measure the height that will be removed
            const contentHeight = existingContent?.offsetHeight || 68; // fallback height
            
            // Store collapse animation data for the mutation observer
            window.pendingCollapseTopics = realTopicsBelow;
            window.pendingCollapseHeight = contentHeight;
            window.pendingCollapseTimestamp = Date.now();
            window.originalCollapsePosition = currentPosition;
            
            // Start fading out the content if we found it
            if (existingContent) {
              existingContent.style.transition = 'opacity 0.15s ease-out';
              existingContent.style.opacity = '0';
            }
          }
          
        } else {
          // Store the current position of the first topic below
          const firstTopicBelow = topicsBelow[0];
          const currentPosition = firstTopicBelow.getBoundingClientRect().top;
          
          // Store topics and their original position for comparison
          window.pendingAnimationTopics = topicsBelow;
          window.pendingAnimationTimestamp = Date.now();
          window.originalTopicPosition = currentPosition;
          window.clickedParentContainer = parentContainer;
        }
      }
    }
  }, true); // USE CAPTURE PHASE!
  
  // Also monitor for DOM changes to detect when content is added/removed
  const observer = new MutationObserver(function(mutations) {
    mutations.forEach(function(mutation) {
      if (mutation.type === 'childList') {
        // Handle UL additions (expansion)
        if (mutation.addedNodes.length > 0) {
          mutation.addedNodes.forEach(node => {
            if (node.nodeType === 1 && node.tagName === 'UL') {
              // Check if we have pending animation topics from a recent click
              if (window.pendingAnimationTopics && window.pendingAnimationTimestamp && window.originalTopicPosition) {
                const timeSinceClick = Date.now() - window.pendingAnimationTimestamp;
                
                if (timeSinceClick < 500) { // Within 500ms of the click
                  // Store references locally to prevent them from being cleared during async operations
                  const topicsToAnimate = window.pendingAnimationTopics;
                  const originalPos = window.originalTopicPosition;
                  
                  // Hide the new content immediately to prevent visual jump
                  node.style.visibility = 'hidden';
                  node.style.opacity = '0';
                  
                  // Measure how much the topics below have been pushed down
                  const firstTopicBelow = topicsToAnimate[0];
                  const currentTopicPosition = firstTopicBelow.getBoundingClientRect().top;
                  const naturalDisplacement = currentTopicPosition - originalPos;
                  
                  if (naturalDisplacement > 0) {
                    // Immediately move topics back to their original position (without animation)
                    topicsToAnimate.forEach(topic => {
                      topic.style.transition = 'none';
                      topic.style.transform = `translateY(-${naturalDisplacement}px)`;
                      topic.style.willChange = 'transform';
                    });
                    
                    // Force a reflow to ensure the instant positioning takes effect
                    firstTopicBelow.offsetHeight;
                    
                    // Now animate them down to their final position
                    setTimeout(() => {
                      topicsToAnimate.forEach(topic => {
                        topic.style.transition = 'transform 0.3s cubic-bezier(0.25, 0.46, 0.45, 0.94)';
                        topic.style.transform = 'translateY(0)';
                      });
                      
                      // Show the content after animation starts
                      setTimeout(() => {
                        node.style.transition = 'opacity 0.2s ease-out, visibility 0.2s ease-out';
                        node.style.visibility = 'visible';
                        node.style.opacity = '1';
                        
                        // Clean up after everything is done
                        setTimeout(() => {
                          topicsToAnimate.forEach(topic => {
                            topic.style.transform = '';
                            topic.style.transition = '';
                            topic.style.willChange = '';
                          });
                          node.style.transition = '';
                        }, 200);
                      }, 50); // Small delay to let slide animation start
                      
                    }, 16); // One frame delay to ensure positioning is applied
                    
                  } else {
                    node.style.visibility = 'visible';
                    node.style.opacity = '1';
                  }
                  
                  // Clear the pending animation variables
                  window.pendingAnimationTopics = null;
                  window.pendingAnimationTimestamp = null;
                  window.originalTopicPosition = null;
                  window.clickedParentContainer = null;
                }
              }
            }
          });
        }
        
        // Handle UL removals (collapse)
        if (mutation.removedNodes.length > 0) {
          mutation.removedNodes.forEach(node => {
            if (node.nodeType === 1 && node.tagName === 'UL') {
              // Check if we have pending collapse animation data
              if (window.pendingCollapseTopics && window.pendingCollapseHeight && window.pendingCollapseTimestamp) {
                const timeSinceClick = Date.now() - window.pendingCollapseTimestamp;
                
                if (timeSinceClick < 1000) { // Within 1 second of the click
                  const topicsToSlide = window.pendingCollapseTopics;
                  const slideHeight = window.pendingCollapseHeight;
                  const originalPosition = window.originalCollapsePosition;
                  
                  // Measure how much topics have moved up due to DOM removal
                  const firstTopic = topicsToSlide[0];
                  const currentPosition = firstTopic.getBoundingClientRect().top;
                  const naturalUpMovement = originalPosition - currentPosition;
                  
                  if (naturalUpMovement > 0 && naturalUpMovement < 200 && currentPosition > 0) {
                    // Move topics back down to their original position instantly
                    topicsToSlide.forEach(topic => {
                      topic.style.transition = 'none';
                      topic.style.transform = `translateY(${naturalUpMovement}px)`;
                      topic.style.willChange = 'transform';
                    });
                    
                    // Force a reflow
                    firstTopic.offsetHeight;
                    
                    // Now animate them up to their final position
                    setTimeout(() => {
                      topicsToSlide.forEach(topic => {
                        topic.style.transition = 'transform 0.3s cubic-bezier(0.25, 0.46, 0.45, 0.94)';
                        topic.style.transform = 'translateY(0)';
                      });
                      
                      // Clean up after animation
                      setTimeout(() => {
                        topicsToSlide.forEach(topic => {
                          topic.style.transform = '';
                          topic.style.transition = '';
                          topic.style.willChange = '';
                        });
                      }, 350);
                      
                    }, 16); // One frame delay to ensure positioning is applied
                    
                  } else {
                    // Fallback: For complex nested cases where position measurement fails
                    topicsToSlide.forEach(topic => {
                      // First, clear any existing transforms
                      topic.style.transform = '';
                      topic.style.transition = '';
                      topic.offsetHeight; // Force reflow
                      
                      // Push the element down by the content height to counteract the snap
                      topic.style.transition = 'none';
                      topic.style.transform = `translateY(${slideHeight}px)`;
                      topic.style.willChange = 'transform';
                    });
                    
                    // Force reflow to ensure the positioning is applied
                    topicsToSlide[0].offsetHeight;
                    
                    // Now animate back up to the final position
                    setTimeout(() => {
                      topicsToSlide.forEach(topic => {
                        topic.style.transition = 'transform 0.3s cubic-bezier(0.25, 0.46, 0.45, 0.94)';
                        topic.style.transform = 'translateY(0)';
                      });
                      
                      // Clean up after animation
                      setTimeout(() => {
                        topicsToSlide.forEach(topic => {
                          topic.style.transform = '';
                          topic.style.transition = '';
                          topic.style.willChange = '';
                        });
                      }, 350);
                    }, 16); // One frame delay
                  }
                  
                  // Clear collapse animation data
                  window.pendingCollapseTopics = null;
                  window.pendingCollapseHeight = null;
                  window.pendingCollapseTimestamp = null;
                  window.originalCollapsePosition = null;
                } 
              } else if (window.pendingAnimationTopics) {
                // Fallback to old logic if no collapse data
                slideTopicsUp(window.pendingAnimationTopics);
                
                // Clear the pending animation
                window.pendingAnimationTopics = null;
                window.pendingAnimationTimestamp = null;
                window.originalTopicPosition = null;
                window.clickedParentContainer = null;
              }
            }
          });
        }
      }
    });
  });
  
  observer.observe(document.body, {
    childList: true,
    subtree: true
  });
  
})();
