     
     
function showAlert(message = "Success!", type = "green") {
  const alertBox = document.getElementById('custom-alert');
  const messageSpan = document.getElementById('custom-alert-message');

  // Reset classes
  alertBox.classList.remove("red", "yellow");

  // Add color variant
  if (type === "red") alertBox.classList.add("red");
  if (type === "yellow") alertBox.classList.add("yellow");

  messageSpan.innerText = message;
  alertBox.style.display = 'block';

  setTimeout(() => {
    alertBox.classList.add('fadeOut');
    setTimeout(() => {
      alertBox.style.display = 'none';
      alertBox.classList.remove('fadeOut');
    }, 500);
  }, 5000);
}

// Example triggers based on URL
const urlParams = new URLSearchParams(window.location.search);

if (urlParams.get('accept') === 'true') {
  const loanId = urlParams.get('loan_id');
  const amount = urlParams.get('amount');
  showAlert(`Loan #${loanId} for ₹${amount} has been accepted!`, "green");

}
if (urlParams.get('reject') === 'true') {
    const loanId = urlParams.get('loan_id');
  const amount = urlParams.get('amount');
  showAlert(`Loan #${loanId} for ₹${amount} has been Rejected!`, "green");
}
if (urlParams.get('paymentdone') === 'true') {
    const loanId = urlParams.get('loan_id');
  const amount = urlParams.get('amount');
  showAlert(`Loan #${loanId} amount ₹${amount} has been sent successfully!`, "green");
}
if (urlParams.get('paymentexists') === 'true') {
    
  showAlert("Payment already done by borrower. Please check in Payments and confirm!..",'yellow');
  
}
if (urlParams.get('paidpayment') === 'true') {
    const loanId = urlParams.get('loan_id');
  const amount = urlParams.get('amount');
  showAlert(`You've successfully paid ₹${amount} for Loan #${loanId}.`,'green');
}
if (urlParams.get('paid') === 'true') {
    const loanId = urlParams.get('loan_id');
  const amount = urlParams.get('amount');
  showAlert(`Loan #${loanId}: ₹${amount} confirmed successfully!`,'green');
}
if (urlParams.get('paid') === 'false') {
    const loanId = urlParams.get('loan_id');
  const amount = urlParams.get('amount');
  showAlert(`Loan #${loanId}: ₹${amount} deleted successfully!`,'red');
}