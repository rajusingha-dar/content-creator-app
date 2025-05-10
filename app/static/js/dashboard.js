// Dashboard functionality
document.addEventListener('DOMContentLoaded', function() {
    // Animate dashboard elements on load
    animateDashboardElements();
    
    // Add event listeners to action buttons
    setupActionButtons();
  });
  
  // Animate dashboard elements with a staggered effect
  function animateDashboardElements() {
    const elements = [
      '.dashboard-header',
      '.stat-card',
      '.action-button',
      '.dashboard-recent'
    ];
    
    let delay = 100;
    
    elements.forEach(selector => {
      const items = document.querySelectorAll(selector);
      
      items.forEach(item => {
        item.style.opacity = '0';
        item.style.transform = 'translateY(20px)';
        item.style.transition = 'opacity 0.5s ease, transform 0.5s ease';
        
        setTimeout(() => {
          item.style.opacity = '1';
          item.style.transform = 'translateY(0)';
        }, delay);
        
        delay += 100;
      });
    });
  }
  
  // Setup action buttons
  function setupActionButtons() {
    const actionButtons = document.querySelectorAll('.action-button');
    
    actionButtons.forEach(button => {
      button.addEventListener('click', function() {
        // Add a ripple effect
        createRipple(this);
        
        // Get button type from class
        const buttonType = this.classList[1];
        
        // Handle different button actions
        switch(buttonType) {
          case 'ideation':
            showNotImplemented('Content ideation is coming soon!');
            break;
          case 'create-content':
            showNotImplemented('Content creation is coming soon!');
            break;
          case 'schedule':
            showNotImplemented('Post scheduling is coming soon!');
            break;
          case 'analytics':
            showNotImplemented('Analytics dashboard is coming soon!');
            break;
        }
      });
    });
  }
  
  // Create a ripple effect on button click
  function createRipple(button) {
    const ripple = document.createElement('span');
    ripple.classList.add('ripple');
    
    const diameter = Math.max(button.clientWidth, button.clientHeight);
    const radius = diameter / 2;
    
    ripple.style.width = ripple.style.height = `${diameter}px`;
    ripple.style.left = '50%';
    ripple.style.top = '50%';
    ripple.style.transform = 'translate(-50%, -50%)';
    
    // Add styles for the ripple
    ripple.style.position = 'absolute';
    ripple.style.borderRadius = '50%';
    ripple.style.backgroundColor = 'rgba(255, 255, 255, 0.2)';
    ripple.style.pointerEvents = 'none';
    ripple.style.animation = 'ripple 0.6s linear';
    
    // Add the ripple to the button
    button.style.position = 'relative';
    button.style.overflow = 'hidden';
    button.appendChild(ripple);
    
    // Remove the ripple after animation completes
    setTimeout(() => {
      ripple.remove();
    }, 600);
  }
  
  // Show "not implemented" notification
  function showNotImplemented(message) {
    // Create notification element if it doesn't exist
    let notification = document.querySelector('.dashboard-notification');
    
    if (!notification) {
      notification = document.createElement('div');
      notification.className = 'dashboard-notification';
      document.body.appendChild(notification);
      
      // Add styles inline (could also be in CSS)
      notification.style.position = 'fixed';
      notification.style.bottom = '20px';
      notification.style.right = '20px';
      notification.style.padding = '16px 24px';
      notification.style.backgroundColor = 'var(--bg-elevation)';
      notification.style.color = 'var(--text-primary)';
      notification.style.borderRadius = 'var(--radius-md)';
      notification.style.boxShadow = 'var(--shadow-lg)';
      notification.style.zIndex = '1000';
      notification.style.opacity = '0';
      notification.style.transform = 'translateY(20px)';
      notification.style.transition = 'opacity 0.3s ease, transform 0.3s ease';
    }
    
    // Update notification content
    notification.textContent = message;
    
    // Show notification
    setTimeout(() => {
      notification.style.opacity = '1';
      notification.style.transform = 'translateY(0)';
    }, 10);
    
    // Hide notification after 3 seconds
    setTimeout(() => {
      notification.style.opacity = '0';
      notification.style.transform = 'translateY(20px)';
    }, 3000);
  }
  
  // Add CSS animation for ripple effect
  const styleSheet = document.createElement('style');
  styleSheet.type = 'text/css';
  styleSheet.innerText = `
    @keyframes ripple {
      0% {
        transform: translate(-50%, -50%) scale(0);
        opacity: 1;
      }
      100% {
        transform: translate(-50%, -50%) scale(2);
        opacity: 0;
      }
    }
  `;
  document.head.appendChild(styleSheet);