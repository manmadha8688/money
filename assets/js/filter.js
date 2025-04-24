document.addEventListener('DOMContentLoaded', function () {
  const fromDate = document.getElementById('from_date');
  const toDate = document.getElementById('to_date');

  // When 'from_date' changes, update min of 'to_date'
  fromDate.addEventListener('change', function () {
      if (fromDate.value) {
          toDate.min = fromDate.value;
      } else {
          toDate.removeAttribute('min');
      }
  });

  // When 'to_date' changes, update max of 'from_date'
  toDate.addEventListener('change', function () {
      if (toDate.value) {
          fromDate.max = toDate.value;
      } else {
          fromDate.removeAttribute('max');
      }
  });

  // Trigger initial sync if dates already pre-filled (e.g., from GET request)
  if (fromDate.value) {
      toDate.min = fromDate.value;
  }

  if (toDate.value) {
      fromDate.max = toDate.value;
  }
});

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

