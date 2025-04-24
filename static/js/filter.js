
function handleEnter(event, fieldId) {
    if (event.key === 'Enter') {
      const allFields = ['borrower', 'token', 'status', 'from_date', 'to_date'];
 
      allFields.forEach((fid) => {
        if (fieldId === 'token') {
          // If current field is "token", clear all except itself
          if (fid !== 'token') document.getElementById(fid).value = '';
        } else {
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

  document.getElementById('status').addEventListener('keydown', function(e) {
    handleEnter(e, 'status');
  });

  document.getElementById('from_date').addEventListener('keydown', function(e) {
    handleEnter(e, 'from_date');
  });

  document.getElementById('to_date').addEventListener('keydown', function(e) {
    handleEnter(e, 'to_date');
  });

