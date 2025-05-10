// Form validation functionality
document.addEventListener('DOMContentLoaded', function() {
    // Get form elements if they exist
    const loginForm = document.querySelector('form[action="/auth/login"]');
    const signupForm = document.querySelector('form[action="/auth/signup"]');
    
    // Handle login form validation
    if (loginForm) {
      loginForm.addEventListener('submit', function(event) {
        const username = document.getElementById('username').value.trim();
        const password = document.getElementById('password').value;
        
        if (username === '' || password === '') {
          event.preventDefault();
          showError('Please fill in all fields');
        }
      });
    }

    // Handle signup form validation
    if (signupForm) {
      signupForm.addEventListener('submit', function(event) {
        const username = document.getElementById('username').value.trim();
        const email = document.getElementById('email').value.trim();
        const fullName = document.getElementById('full_name').value.trim();
        const password = document.getElementById('password').value;
        const confirmPassword = document.getElementById('confirm_password').value;
        
        if (username === '' || email === '' || fullName === '' || password === '' || confirmPassword === '') {
          event.preventDefault();
          showError('Please fill in all fields');
          return;
        }
        
        if (password.length < 8) {
          event.preventDefault();
          showError('Password must be at least 8 characters long');
          return;
        }
        
        if (password !== confirmPassword) {
          event.preventDefault();
          showError('Passwords do not match');
          return;
        }
        
        if (!isValidEmail(email)) {
          event.preventDefault();
          showError('Please enter a valid email address');
          return;
        }
      });
      
      // Add real-time password matching validation
      const passwordInput = document.getElementById('password');
      const confirmPasswordInput = document.getElementById('confirm_password');
      const passwordMatchMessage = document.getElementById('password_match_message');
      
      function checkPasswordsMatch() {
        if (confirmPasswordInput.value === '') {
          passwordMatchMessage.style.color = 'var(--text-tertiary)';
          passwordMatchMessage.textContent = 'Both passwords must match';
        } else if (passwordInput.value === confirmPasswordInput.value) {
          passwordMatchMessage.style.color = 'var(--success)';
          passwordMatchMessage.textContent = 'Passwords match';
        } else {
          passwordMatchMessage.style.color = 'var(--error)';
          passwordMatchMessage.textContent = 'Passwords do not match';
        }
      }
      
      if (passwordInput && confirmPasswordInput) {
        passwordInput.addEventListener('input', checkPasswordsMatch);
        confirmPasswordInput.addEventListener('input', checkPasswordsMatch);
      }
    }
    
    // Handle signup form validation
    // if (signupForm) {
    //   signupForm.addEventListener('submit', function(event) {
    //     const username = document.getElementById('username').value.trim();
    //     const email = document.getElementById('email').value.trim();
    //     const fullName = document.getElementById('full_name').value.trim();
    //     const password = document.getElementById('password').value;
        
    //     if (username === '' || email === '' || fullName === '' || password === '') {
    //       event.preventDefault();
    //       showError('Please fill in all fields');
    //       return;
    //     }
        
    //     if (password.length < 8) {
    //       event.preventDefault();
    //       showError('Password must be at least 8 characters long');
    //       return;
    //     }
        
    //     if (!isValidEmail(email)) {
    //       event.preventDefault();
    //       showError('Please enter a valid email address');
    //       return;
    //     }
    //   });
    // }
    
    // Helper functions
    function showError(message) {
      // Check if error message already exists
      let errorDiv = document.querySelector('.error-message');
      
      if (!errorDiv) {
        // Create error message div
        errorDiv = document.createElement('div');
        errorDiv.className = 'error-message';
        
        // Insert at the top of the form
        const authHeader = document.querySelector('.auth-header');
        authHeader.insertAdjacentElement('afterend', errorDiv);
      }
      
      errorDiv.textContent = message;
      
      // Scroll to error
      errorDiv.scrollIntoView({ behavior: 'smooth', block: 'center' });
    }
    
    function isValidEmail(email) {
      const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
      return emailRegex.test(email);
    }
    
    // Add input event listeners for real-time validation
    if (signupForm) {
      const passwordInput = document.getElementById('password');
      if (passwordInput) {
        passwordInput.addEventListener('input', function() {
          const password = this.value;
          const smallText = this.nextElementSibling;
          
          if (password.length < 8 && password.length > 0) {
            smallText.style.color = 'var(--error)';
          } else {
            smallText.style.color = 'var(--text-tertiary)';
          }
        });
      }
    }
    
    // Add password visibility toggle
    const passwordInputs = document.querySelectorAll('input[type="password"]');
    passwordInputs.forEach(input => {
      // Create toggle button
      const toggleButton = document.createElement('button');
      toggleButton.type = 'button';
      toggleButton.className = 'password-toggle';
      toggleButton.innerHTML = '👁️';
      toggleButton.style.position = 'absolute';
      toggleButton.style.right = '10px';
      toggleButton.style.top = '50%';
      toggleButton.style.transform = 'translateY(-50%)';
      toggleButton.style.background = 'none';
      toggleButton.style.border = 'none';
      toggleButton.style.color = 'var(--text-tertiary)';
      toggleButton.style.cursor = 'pointer';
      
      // Create a wrapper for the input to position the button
      const wrapper = document.createElement('div');
      wrapper.style.position = 'relative';
      
      // Insert the wrapper before the input
      input.parentNode.insertBefore(wrapper, input);
      
      // Move the input into the wrapper
      wrapper.appendChild(input);
      
      // Add the button to the wrapper
      wrapper.appendChild(toggleButton);
      
      // Toggle password visibility
      toggleButton.addEventListener('click', function() {
        const type = input.getAttribute('type') === 'password' ? 'text' : 'password';
        input.setAttribute('type', type);
        toggleButton.innerHTML = type === 'password' ? '👁️' : '🔒';
      });
    });
  
    // Handle animation effects
    const authCard = document.querySelector('.auth-card');
    if (authCard) {
      authCard.style.opacity = '0';
      authCard.style.transform = 'translateY(20px)';
      authCard.style.transition = 'opacity 0.5s ease, transform 0.5s ease';
      
      // Trigger animation
      setTimeout(() => {
        authCard.style.opacity = '1';
        authCard.style.transform = 'translateY(0)';
      }, 100);
    }
  });