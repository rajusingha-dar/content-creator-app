// app/static/js/auth.js
document.addEventListener('DOMContentLoaded', function() {
  // Login form handling
  const loginForm = document.getElementById('login-form');
  const loginError = document.getElementById('login-error');
  
  if (loginForm) {
      // Remove the event.preventDefault() and let the form submit normally
      // Just validate fields before submission
      loginForm.addEventListener('submit', function(event) {
          const username = document.getElementById('username').value.trim();
          const password = document.getElementById('password').value;
          
          // Clear previous error messages
          if (loginError) {
              loginError.classList.add('d-none');
          }
          
          // Validate required fields
          if (!username || !password) {
              event.preventDefault(); // Stop form submission only if validation fails
              
              if (loginError) {
                  loginError.textContent = 'Please enter both username and password';
                  loginError.classList.remove('d-none');
              }
              return false;
          }
          
          // Let the form submit normally via standard form submission
          return true;
      });
  }
  
  // Signup form handling
  const signupForm = document.getElementById('signup-form');
  const passwordMatchMessage = document.getElementById('password_match_message');
  
  if (signupForm) {
      // Password match validation
      const passwordInput = document.getElementById('password');
      const confirmPasswordInput = document.getElementById('confirm_password');
      
      if (passwordInput && confirmPasswordInput && passwordMatchMessage) {
          // Check passwords match on input
          confirmPasswordInput.addEventListener('input', function() {
              if (passwordInput.value === confirmPasswordInput.value) {
                  passwordMatchMessage.style.color = '#4299e1';
                  passwordMatchMessage.textContent = 'Passwords match!';
              } else {
                  passwordMatchMessage.style.color = '#fc8181';
                  passwordMatchMessage.textContent = 'Passwords do not match';
              }
          });
          
          // Also check when password field changes
          passwordInput.addEventListener('input', function() {
              if (confirmPasswordInput.value) {
                  if (passwordInput.value === confirmPasswordInput.value) {
                      passwordMatchMessage.style.color = '#4299e1';
                      passwordMatchMessage.textContent = 'Passwords match!';
                  } else {
                      passwordMatchMessage.style.color = '#fc8181';
                      passwordMatchMessage.textContent = 'Passwords do not match';
                  }
              }
          });
      }
      
      // Form submission validation
      signupForm.addEventListener('submit', function(event) {
          const username = document.getElementById('username').value.trim();
          const email = document.getElementById('email').value.trim();
          const fullName = document.getElementById('full_name').value.trim();
          const password = document.getElementById('password').value;
          const confirmPassword = document.getElementById('confirm_password').value;
          const signupError = document.getElementById('signup-error');
          
          // Validate all fields are filled
          if (!username || !email || !fullName || !password || !confirmPassword) {
              event.preventDefault();
              if (signupError) {
                  signupError.textContent = 'Please fill in all fields';
                  signupError.classList.remove('d-none');
              }
              return false;
          }
          
          // Validate password length
          if (password.length < 8) {
              event.preventDefault();
              if (signupError) {
                  signupError.textContent = 'Password must be at least 8 characters long';
                  signupError.classList.remove('d-none');
              }
              return false;
          }
          
          // Validate passwords match
          if (password !== confirmPassword) {
              event.preventDefault();
              if (signupError) {
                  signupError.textContent = 'Passwords do not match';
                  signupError.classList.remove('d-none');
              }
              return false;
          }
          
          // Let the form submit normally
          return true;
      });
  }
});

// Toggle password visibility for password field
function togglePassword() {
  const passwordInput = document.getElementById('password');
  const passwordToggle = document.querySelector('.password-toggle i');
  
  if (passwordInput && passwordToggle) {
      if (passwordInput.type === 'password') {
          passwordInput.type = 'text';
          passwordToggle.classList.remove('fa-eye');
          passwordToggle.classList.add('fa-eye-slash');
      } else {
          passwordInput.type = 'password';
          passwordToggle.classList.remove('fa-eye-slash');
          passwordToggle.classList.add('fa-eye');
      }
  }
}

// Toggle password visibility for confirm password field
function toggleConfirmPassword() {
  const confirmPasswordInput = document.getElementById('confirm_password');
  const confirmPasswordToggle = document.querySelector('.confirm-password-toggle i');
  
  if (confirmPasswordInput && confirmPasswordToggle) {
      if (confirmPasswordInput.type === 'password') {
          confirmPasswordInput.type = 'text';
          confirmPasswordToggle.classList.remove('fa-eye');
          confirmPasswordToggle.classList.add('fa-eye-slash');
      } else {
          confirmPasswordInput.type = 'password';
          confirmPasswordToggle.classList.remove('fa-eye-slash');
          confirmPasswordToggle.classList.add('fa-eye');
      }
  }
}