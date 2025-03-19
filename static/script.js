document.addEventListener('DOMContentLoaded', function () {
  console.log('Website loaded!');

  // Get the translation form and result container
  const translationForm = document.querySelector('#translation-form');
  const translationResult = document.querySelector('#translation-result');
  const translatedText = document.querySelector('#translated-text');
  const loadingSpinner = document.querySelector('#loading-spinner');
  const errorMessage = document.querySelector('#error-message');

  // Add event listener to the translation form
  if (translationForm) {
      translationForm.addEventListener('submit', function (event) {
          event.preventDefault(); // Prevent the form from submitting normally

          // Get the input values
          const text = document.querySelector('#text').value.trim();
          const language = document.querySelector('#language').value;

          // Validate the input
          if (!text) {
              alert('Please enter some text to translate.');
              return;
          }

          // Show loading spinner and hide other elements
          loadingSpinner.style.display = 'block';
          translationResult.style.display = 'none';
          errorMessage.style.display = 'none';

          // Send the translation request to the server
          fetch('/translate', {
              method: 'POST',
              headers: {
                  'Content-Type': 'application/x-www-form-urlencoded',
              },
              body: `text=${encodeURIComponent(text)}&language=${encodeURIComponent(language)}`,
          })
              .then(response => response.json())
              .then(data => {
                  // Hide loading spinner
                  loadingSpinner.style.display = 'none';

                  if (data.translation) {
                      // Display the translated text
                      translatedText.textContent = data.translation;
                      translationResult.style.display = 'block';
                  } else if (data.message) {
                      // Display a message (e.g., "Please login to continue")
                      errorMessage.textContent = data.message;
                      errorMessage.style.display = 'block';
                  } else {
                      // Handle errors
                      errorMessage.textContent = 'Translation failed. Please try again.';
                      errorMessage.style.display = 'block';
                  }
              })
              .catch(error => {
                  console.error('Error:', error);
                  loadingSpinner.style.display = 'none';
                  errorMessage.textContent = 'An error occurred. Please try again.';
                  errorMessage.style.display = 'block';
              });
      });
  }
});