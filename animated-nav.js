// Simple Navigation Animations - Focus on sliding topics below downwards
(function() {
  // console.log('🎯 Simple navigation animations loaded');
  
  // Function to find all navigation topics that are visually below a given element
  function getTopicsBelow(clickedElement) {
    // Look for the actual navigation content container
    const navContainer = document.querySelector('#sidebar-content') || 
                         document.querySelector('#navigation-items') ||
                         document.querySelector('aside, [class*="sidebar-content"], [id*="sidebar"]') || 
                         document.querySelector('[role="navigation"]') ||
                         document.body;
    
    // console.log('✅ Found sidebar container:', navContainer);
    
    // Get the Y position of the clicked element's parent container
    const clickedRect = clickedElement.getBoundingClientRect();
    const clickedBottom = clickedRect.bottom;
    
    // console.log('🔍 Clicked element bottom Y:', clickedBottom);
    
    // Find all navigation items - be more inclusive to catch all navigation elements
    // Look for the main navigation containers that could be animated
    const allTopics = navContainer.querySelectorAll('div[class*="group"], div[class*="cursor-pointer"], a[href], button, [class*="flex items-center"]');
    
    const topicsBelow = [];
    const processedTexts = new Set(); // Track processed text content to avoid duplicates
    
    // console.log('🔍 All potential navigation containers found:', allTopics.length);
    
    Array.from(allTopics).forEach((topic, index) => {
      const topicRect = topic.getBoundingClientRect();
      const text = topic.textContent?.trim();
      
      // Skip if we've already processed an element with this text content
      if (processedTexts.has(text)) {
        // console.log(`🔍 Topic ${index}: "${text}" at Y: ${topicRect.top} - SKIPPED (duplicate)`);
        return;
      }
      
      // console.log(`🔍 Topic ${index}: "${text}" at Y: ${topicRect.top}`);
      
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
            // console.log(`✅ Added topic below: "${text}"`);
          }
        }
      }
    });
    
    // console.log('📍 Found topics below clicked element:', topicsBelow);
    return topicsBelow;
  }
  
  // Function to slide topics down by a specific amount
  function slideTopicsDown(topics, slideDistance) {
    // console.log(`🎬 Sliding ${topics.length} topics down by ${slideDistance}px`);
    
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
    // console.log(`🎬 Sliding ${topics.length} topics back up`);
    
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
    // console.log('🖱️ EARLY Click detected on:', e.target);
    
    // Look for the actual clickable navigation element
    const clickedElement = e.target.closest('.flex-1, button, [role="button"]') || e.target;
    const navContainer = e.target.closest('nav, aside, [role="navigation"], [class*="sidebar"], #navigation-items');
    
    // console.log('🔍 EARLY Clicked element:', clickedElement);
    // console.log('🔍 EARLY Nav container:', navContainer);
    
    // Check if this is a navigation item that can expand
    // Look for the group container or any parent that might contain expandable content
    const parentContainer = e.target.closest('div[class*="group"], li, [class*="cursor-pointer"]') || 
                           e.target.closest('div[class*="flex items-center"]');
    
    // Check for existing children or if this looks like an expandable item
    const hasChildren = parentContainer?.querySelector('ul, ol') || 
                       (parentContainer && (
                         parentContainer.textContent.includes('Models') || 
                         parentContainer.textContent.includes('Experiments') ||
                         parentContainer.textContent.includes('Guides')
                       ));
    
    // console.log('🔍 EARLY Parent container:', parentContainer);
    // console.log('🔍 EARLY Has children or will have children:', hasChildren);
    
    // Only proceed if this looks like a navigation click
    if (clickedElement && (navContainer || parentContainer)) {
      // console.log('🎯 EARLY Navigation click detected:', clickedElement);
      
      // Get topics below this element BEFORE Mintlify changes anything
      // Use the parent container for positioning reference if available
      const referenceElement = parentContainer || clickedElement;
      const topicsBelow = getTopicsBelow(referenceElement);
      
      if (topicsBelow.length > 0) {
        // console.log('📍 EARLY Will animate these topics:', topicsBelow);
        
        // Check if there's already a UL (meaning we're about to collapse)
        // Look more thoroughly for existing content
        const existingContent = parentContainer?.querySelector('ul') || 
                               parentContainer?.querySelector('ol') ||
                               parentContainer?.parentElement?.querySelector('ul');
        
        // Also check if any of the topics below are actually children that were just expanded
        const hasExpandedChildren = topicsBelow.some(topic => {
          return parentContainer?.contains(topic) || 
                 topic.textContent?.includes('Overview') || 
                 topic.textContent?.includes('Experiments');
        });
        
        // console.log('🔍 EARLY Existing content check:', !!existingContent);
        // console.log('🔍 EARLY Has expanded children:', hasExpandedChildren);
        // console.log('🔍 EARLY Topics below include children:', topicsBelow.map(t => t.textContent?.trim()));
        
        if ((existingContent && existingContent.offsetHeight > 0) || hasExpandedChildren) {
          // console.log('🔄 EARLY Found existing content or expanded children, this is a collapse action');
          
          // Filter out the child topics - we only want to animate topics that are truly below
          const realTopicsBelow = topicsBelow.filter(topic => {
            const text = topic.textContent?.trim();
            return !parentContainer?.contains(topic) && 
                   !text?.includes('Overview') && 
                   !text?.includes('Experiments');
          });
          
          // console.log('🔍 EARLY Real topics below (excluding children):', realTopicsBelow.map(t => t.textContent?.trim()));
          
          if (realTopicsBelow.length > 0) {
            // Store the current position of topics below before collapse
            const firstTopicBelow = realTopicsBelow[0];
            const currentPosition = firstTopicBelow.getBoundingClientRect().top;
            
            // Measure the height that will be removed
            const contentHeight = existingContent?.offsetHeight || 68; // fallback height
            // console.log('📏 Content to be removed height:', contentHeight);
            
            // Store collapse animation data for the mutation observer
            window.pendingCollapseTopics = realTopicsBelow;
            window.pendingCollapseHeight = contentHeight;
            window.pendingCollapseTimestamp = Date.now();
            window.originalCollapsePosition = currentPosition; // Store original position
            
            // STEP 1: Start fading out the content if we found it
            if (existingContent) {
              // console.log('🌅 Fading out existing content');
              existingContent.style.transition = 'opacity 0.15s ease-out';
              existingContent.style.opacity = '0';
            }
          } else {
            // console.log('⚠️ No real topics below to animate for collapse');
          }
          
        } else {
          // console.log('➕ EARLY No existing UL, this is an expand action');
          
          // Store the current position of the first topic below
          const firstTopicBelow = topicsBelow[0];
          const currentPosition = firstTopicBelow.getBoundingClientRect().top;
          
          // Store topics and their original position for comparison
          window.pendingAnimationTopics = topicsBelow;
          window.pendingAnimationTimestamp = Date.now();
          window.originalTopicPosition = currentPosition;
          window.clickedParentContainer = parentContainer;
          
          // console.log('🎯 EARLY Stored topics and original position:', currentPosition);
          // console.log('🎯 EARLY Topics to animate:', topicsBelow.map(t => t.textContent?.trim()));
        }
              } else {
        // console.log('⚠️ No topics found below clicked element');
        // Debug: Let's see what we're working with
        // console.log('🔍 DEBUG: Reference element rect:', referenceElement.getBoundingClientRect());
        // console.log('🔍 DEBUG: All navigation elements in container:', navContainer?.querySelectorAll('div[class*="group"], div[class*="cursor-pointer"], a[href], button').length);
      }
    } else {
      // console.log('❌ Not recognized as navigation click');
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
              // console.log('🎬 New UL detected, measuring content...');
              
              // Check if we have pending animation topics from a recent click
              if (window.pendingAnimationTopics && window.pendingAnimationTimestamp && window.originalTopicPosition) {
                const timeSinceClick = Date.now() - window.pendingAnimationTimestamp;
                
                if (timeSinceClick < 500) { // Within 500ms of the click
                  // console.log('📏 Measuring content dimensions...');
                  
                  // Store references locally to prevent them from being cleared during async operations
                  const topicsToAnimate = window.pendingAnimationTopics;
                  const originalPos = window.originalTopicPosition;
                  
                  // STEP 1: Hide the new content immediately to prevent visual jump
                  node.style.visibility = 'hidden';
                  node.style.opacity = '0';
                  
                  // STEP 2: Measure how much the topics below have been pushed down
                  const firstTopicBelow = topicsToAnimate[0];
                  const currentTopicPosition = firstTopicBelow.getBoundingClientRect().top;
                  const naturalDisplacement = currentTopicPosition - originalPos;
                  
                  // console.log('📍 Position analysis:');
                  // console.log('  - Original position:', originalPos);
                  // console.log('  - Current position (after DOM insertion):', currentTopicPosition);
                  // console.log('  - Natural displacement:', naturalDisplacement);
                  
                                      if (naturalDisplacement > 0) {
                      // STEP 3: Immediately move topics back to their original position (without animation)
                      // console.log('⚡ Moving topics back to original position instantly');
                    topicsToAnimate.forEach(topic => {
                      topic.style.transition = 'none';
                      topic.style.transform = `translateY(-${naturalDisplacement}px)`;
                      topic.style.willChange = 'transform';
                    });
                    
                    // Force a reflow to ensure the instant positioning takes effect
                    firstTopicBelow.offsetHeight;
                    
                                          // STEP 4: Now animate them down to their final position
                      setTimeout(() => {
                        // console.log('🎬 Animating topics to final position:', naturalDisplacement);
                      topicsToAnimate.forEach(topic => {
                        topic.style.transition = 'transform 0.3s cubic-bezier(0.25, 0.46, 0.45, 0.94)';
                        topic.style.transform = 'translateY(0)';
                      });
                      
                                              // STEP 5: Show the content after animation starts
                        setTimeout(() => {
                          // console.log('✨ Revealing new content');
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
                      // console.log('⚠️ No natural displacement detected, showing content immediately');
                    node.style.visibility = 'visible';
                    node.style.opacity = '1';
                  }
                  
                  // Clear the pending animation variables
                  window.pendingAnimationTopics = null;
                  window.pendingAnimationTimestamp = null;
                  window.originalTopicPosition = null;
                  window.clickedParentContainer = null;
                } else {
                  // console.log('⏰ UL detected but too late after click (', timeSinceClick, 'ms)');
                }
              } else {
                // console.log('❓ UL detected but no pending animation topics');
              }
            }
          });
        }
        
        // Handle UL removals (collapse)
        if (mutation.removedNodes.length > 0) {
          mutation.removedNodes.forEach(node => {
            if (node.nodeType === 1 && node.tagName === 'UL') {
              // console.log('🗑️ UL removed, content collapsed');
              
              // Check if we have pending collapse animation data
              if (window.pendingCollapseTopics && window.pendingCollapseHeight && window.pendingCollapseTimestamp) {
                const timeSinceClick = Date.now() - window.pendingCollapseTimestamp;
                
                if (timeSinceClick < 1000) { // Within 1 second of the click
                  // console.log('🎬 Performing collapse slide animation');
                  const topicsToSlide = window.pendingCollapseTopics;
                  const slideHeight = window.pendingCollapseHeight;
                  const originalPosition = window.originalCollapsePosition;
                  
                  // STEP 1: Measure how much topics have moved up due to DOM removal
                  const firstTopic = topicsToSlide[0];
                  const currentPosition = firstTopic.getBoundingClientRect().top;
                  const naturalUpMovement = originalPosition - currentPosition;
                  
                  // console.log('📍 Collapse position analysis:');
                  // console.log('  - Original position before collapse:', originalPosition);
                  // console.log('  - Current position after DOM removal:', currentPosition);
                  // console.log('  - Natural up movement:', naturalUpMovement);
                  
                                      if (naturalUpMovement > 0 && naturalUpMovement < 200 && currentPosition > 0) {
                      // STEP 2: Move topics back down to their original position instantly
                      // console.log('⚡ Moving topics back to original position to prevent snap');
                    topicsToSlide.forEach(topic => {
                      topic.style.transition = 'none';
                      topic.style.transform = `translateY(${naturalUpMovement}px)`;
                      topic.style.willChange = 'transform';
                    });
                    
                    // Force a reflow
                    firstTopic.offsetHeight;
                    
                                          // STEP 3: Now animate them up to their final position
                      setTimeout(() => {
                        // console.log('🎬 Animating topics to final position');
                      topicsToSlide.forEach(topic => {
                        topic.style.transition = 'transform 0.3s cubic-bezier(0.25, 0.46, 0.45, 0.94)';
                        topic.style.transform = 'translateY(0)';
                      });
                      
                                              // STEP 4: Clean up after animation
                        setTimeout(() => {
                          // console.log('🧹 Cleaning up collapse animation');
                        topicsToSlide.forEach(topic => {
                          topic.style.transform = '';
                          topic.style.transition = '';
                          topic.style.willChange = '';
                        });
                      }, 350);
                      
                                          }, 16); // One frame delay to ensure positioning is applied
                      
                    } else {
                      // console.log('⚠️ Using fallback simple slide animation');
                    // Fallback: For complex nested cases where position measurement fails,
                    // we need to prevent the snap-up issue without relying on position data
                                          
                      // console.log('🎬 Applying anti-snap fallback animation');
                    
                    // The key insight: if elements snapped up due to DOM removal,
                    // we need to push them back down first, then animate up
                    // Use the stored slide height as an approximation
                    
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
                        // console.log('🎬 Animating from pushed-down position to final position');
                      topicsToSlide.forEach(topic => {
                        topic.style.transition = 'transform 0.3s cubic-bezier(0.25, 0.46, 0.45, 0.94)';
                        topic.style.transform = 'translateY(0)';
                      });
                      
                                              // Clean up after animation
                        setTimeout(() => {
                          // console.log('🧹 Cleaning up fallback collapse animation');
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
                } else {
                  // console.log('⏰ UL removed but too late after click (', timeSinceClick, 'ms)');
                }
              } else if (window.pendingAnimationTopics) {
                // Fallback to old logic if no collapse data
                // console.log('📏 Sliding topics back up (fallback)');
                slideTopicsUp(window.pendingAnimationTopics);
                
                // Clear the pending animation
                window.pendingAnimationTopics = null;
                window.pendingAnimationTimestamp = null;
                window.originalTopicPosition = null;
                window.clickedParentContainer = null;
              } else {
                // console.log('❓ UL removed but no pending animation data');
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