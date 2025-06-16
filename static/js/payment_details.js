function togglePaymentDetails() {
      const type = document.getElementById("payment_type").value;
      const cashFields = document.getElementById("cashFields");
      const onlineFields = document.getElementById("onlinePlatformFields");
    
      cashFields.classList.add("hidden");
      onlineFields.classList.add("hidden");
    
      if (type === "cash") {
        cashFields.classList.remove("hidden");
      } else if (type === "online") {
        onlineFields.classList.remove("hidden");
      }
    
      // Reset inner fields
    }
    
    function toggleOnlineMethodFields() {
      const method = document.getElementById("online_method").value;
      const upiFields = document.getElementById("upiFields");
      const bankFields = document.getElementById("bankFields");

      upiFields.classList.add("hidden");
      bankFields.classList.add("hidden");

      if (method === "bank") {
        bankFields.classList.remove("hidden");
      } else if (["phonepay", "googlepay", "paytm"].includes(method)) {
        upiFields.classList.remove("hidden");
      }
    }

    function confirmSubmit(button) {
      const paymentType = document.getElementById("payment_type").value;
    
      if (!paymentType) {
        alert("Please select a payment method.");
        return false;
      }
    
      if (paymentType === "cash") {
        const cashFrom = document.getElementById("cash_from").value.trim();
        if (!cashFrom) {
          alert("Please enter from whom cash was taken.");
          document.getElementById("cash_from").focus();
          return false;
        }
      }
    
      else if (paymentType === "online") {
        const platform = document.getElementById("online_method").value;
    
        if (!platform) {
          alert("Please select an online payment platform.");
          document.getElementById("online_method").focus();
          return false;
        }
    
        if (["phonepay", "googlepay", "paytm"].includes(platform)) {
          const upi = document.querySelector("input[name='upi_number']").value.trim();
          const name = document.querySelector("input[name='account_holder_name']").value.trim();
        
          const upiRegex = /^[\w.-]+@[\w.-]+$/; // Valid UPI ID
          const phoneRegex = /^[6-9]\d{9}$/;    // Valid 10-digit Indian number
          const nameRegex = /^[a-zA-Z\s]{3,50}$/; // Only letters and spaces, 3-50 chars
        
          if (!upi || !name) {
            if (!upi) {
              alert("Please enter both UPI ID or phone number.");
            
              document.querySelector("input[name='upi_number']").focus();
            } else {
              alert("Please enter account holder name.");
            
              document.querySelector("input[name='account_holder_name']").focus();
            }
            return false;
          }
        
          if (!upiRegex.test(upi) && !phoneRegex.test(upi)) {
            alert("Please enter a valid UPI ID (e.g., name@bank) or a valid 10-digit phone number.");
            document.querySelector("input[name='upi_number']").focus();
            return false;
          }
        
          if (!nameRegex.test(name)) {
            alert("Please enter a valid account holder name (only letters and spaces, 3-50 characters).");
            document.querySelector("input[name='account_holder_name']").focus();
            return false;
          }
        }
        
        if (platform === "bank") {
          const acc = document.querySelector("input[name='account_number']").value.trim();
          const ifsc = document.querySelector("input[name='ifsc']").value.trim().toUpperCase();
          const bank = document.querySelector("input[name='bank_name']").value.trim();
          const name = document.querySelector("input[name='bank_account_holder_name']").value.trim();
        
          const bankNameRegex = /^[A-Za-z\s]{2,100}$/;
          const accountNumberRegex = /^\d{9,18}$/;
          const ifscRegex = /^[A-Z]{4}0[A-Z0-9]{6}$/;
          const nameRegex = /^[A-Za-z\s]{3,100}$/;
        
          if (!acc) {
            alert("Please enter account number.");
            document.querySelector("input[name='account_number']").focus();
            return false;
          } else if (!accountNumberRegex.test(acc)) {
            alert("Please enter a valid account number (9 to 18 digits).");
            document.querySelector("input[name='account_number']").focus();
            return false;
          }
        
          if (!ifsc) {
            alert("Please enter IFSC code.");
            document.querySelector("input[name='ifsc']").focus();
            return false;
          } else if (!ifscRegex.test(ifsc)) {
            alert("Please enter a valid IFSC code (e.g., HDFC0123456).");
            document.querySelector("input[name='ifsc']").focus();
            return false;
          }
        
          if (!bank) {
            alert("Please enter bank name.");
            document.querySelector("input[name='bank_name']").focus();
            return false;
          } else if (!bankNameRegex.test(bank)) {
            alert("Please enter a valid bank name (only letters and spaces).");
            document.querySelector("input[name='bank_name']").focus();
            return false;
          }
        
          if (!name) {
            alert("Please enter account holder name.");
            document.querySelector("input[name='bank_account_holder_name']").focus();
            return false;
          } else if (!nameRegex.test(name)) {
            alert("Please enter a valid account holder name (only letters and spaces).");
            document.querySelector("input[name='bank_account_holder_name']").focus();
            return false;
          }
        
          
        }
        
    
        
      }
      return true;
    }