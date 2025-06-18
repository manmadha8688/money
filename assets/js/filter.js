
function handleEnter(event, fieldId) {
    if (event.key === 'Enter') {
      const allFields = ['borrower', 'token', 'status','number','from_date', 'to_date'];
 
      allFields.forEach((fid) => {
        if (fieldId === 'token') {
          // If current field is "token", clear all except itself
          if (fid !== 'token') document.getElementById(fid).value = '';
          
        } 
        else if (fieldId === 'number') {
          // If current field is "token", clear all except itself
          if (fid !== 'number') document.getElementById(fid).value = '';
          
        } 
        
        else {
          // If current field is NOT "token", clear only the token field
          if (fid === 'token') document.getElementById(fid).value = '';
        }
      });

      event.target.form.submit();
    }
  }

  // Attach listeners
  document.getElementById('borrower').addEventListener('keydown', function(e) {
    handleEnter(e, 'borrower');
  });

  document.getElementById('token').addEventListener('keydown', function(e) {
    handleEnter(e, 'token');
  });

  const statusInput = document.getElementById('status');

  if (statusInput) {
  statusInput.addEventListener('keydown', function (e) {
    handleEnter(e, 'status');
  });
 }
 const numberInput = document.getElementById('mobile_number');

 if (numberInput) {
  numberInput.addEventListener('keydown', function (e) {
    handleEnter(e, 'number');
  });
 }


 