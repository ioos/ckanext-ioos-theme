/* Displays error message if the recaptcha
 * checkbox is not checked and blocks form submission
 */
var form = document.getElementById('user-register-form');
form.addEventListener("submit", function(event){
    if (grecaptcha.getResponse() === '') {                            
      event.preventDefault();
      alert('Please check the recaptcha');
    }
  }
, false);