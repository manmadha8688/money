    const todayDate = new Date();
    const yyyy = todayDate.getFullYear();
    const mm = String(todayDate.getMonth() + 1).padStart(2, '0');
    const dd = String(todayDate.getDate()).padStart(2, '0');
    const today = `${yyyy}-${mm}-${dd}`;
    document.getElementById("apply_date").value = today;

    const takenDateInput = document.getElementById("taken_date");
    const returnDateInput = document.getElementById("return_date");
    takenDateInput.setAttribute("min", today);
    returnDateInput.setAttribute("min", today);

    takenDateInput.addEventListener("change", function () {
      returnDateInput.setAttribute("min", takenDateInput.value);
    });

    const loanItemInput = document.getElementById("loan_item");
    /* const photoLabel = document.getElementById("photo-label");

    loanItemInput.addEventListener("input", function () {
      const item = loanItemInput.value.trim();
      photoLabel.innerText = item ? `Upload ${item} Photos (Optional):` : "Upload Photos (Optional):";
    });

    
    

     const input = document.getElementById("photos");
    const previewContainer = document.getElementById("preview-container");
    let selectedFiles = [];

    input.addEventListener("change", (e) => {
      selectedFiles = selectedFiles.concat(Array.from(e.target.files));
      updatePreview();
      updateInputFiles();
    });
*/
    function updatePreview() {
      previewContainer.innerHTML = "";
      selectedFiles.forEach((file, index) => {
        const reader = new FileReader();
        reader.onload = function (e) {
          const wrapper = document.createElement("div");
          wrapper.style.position = "relative";

          const img = document.createElement("img");
          img.src = e.target.result;
          img.style.width = "100px";
          img.style.height = "100px";
          img.style.objectFit = "cover";
          img.style.borderRadius = "8px";
          img.style.boxShadow = "0 0 4px rgba(0,0,0,0.2)";

          const closeBtn = document.createElement("span");
          closeBtn.innerHTML = "&times;";
          closeBtn.style.position = "absolute";
          closeBtn.style.top = "-6px";
          closeBtn.style.right = "-6px";
          closeBtn.style.background = "red";
          closeBtn.style.color = "white";
          closeBtn.style.borderRadius = "50%";
          closeBtn.style.cursor = "pointer";
          closeBtn.style.fontSize = "16px";
          closeBtn.style.width = "20px";
          closeBtn.style.height = "20px";
          closeBtn.style.display = "flex";
          closeBtn.style.alignItems = "center";
          closeBtn.style.justifyContent = "center";

          closeBtn.onclick = () => {
            selectedFiles.splice(index, 1);
            updatePreview();
            updateInputFiles();
          };

          wrapper.appendChild(img);
          wrapper.appendChild(closeBtn);
          previewContainer.appendChild(wrapper);
        };
        reader.readAsDataURL(file);
      });
    }

    function updateInputFiles() {
      const dataTransfer = new DataTransfer();
      selectedFiles.forEach((file) => dataTransfer.items.add(file));
      input.files = dataTransfer.files;
    }
      const paymentPlanSelect = document.getElementById("payment_plan");
      const returnDateLabel = document.querySelector("label[for='return_date']");
    
      paymentPlanSelect.addEventListener("change", function () {
        const plan = this.value;
        takenDateInput.value = "";
        
    
        returnDateInput.value = ""; // Clear previous value
      });
    
      takenDateInput.addEventListener("change", function () {
        const plan = paymentPlanSelect.value;
        if (plan === "monthly") {
          setDueDateMonthly();
        } else if (plan === "weekly") {
          setDueDateByDays(98);
        } else {
          setDueDateByDays(100); // Daily one-time with 100 days gap
        }
      });
      
      function setDueDateByDays(days) {
        const start = new Date(takenDateInput.value);
        if (isNaN(start)) return;
      
        const due = new Date(start);
        due.setDate(due.getDate() + days); // Automatically excludes the taken date
        returnDateInput.value = formatDate(due);
      }
      
      function setDueDateMonthly() {
        const start = new Date(takenDateInput.value);
        if (isNaN(start)) return;
      
        const due = new Date(start);
        due.setMonth(due.getMonth() + 1); // Moves to same date next month
        returnDateInput.value = formatDate(due);
      }
      
      function formatDate(date) {
        const yyyy = date.getFullYear();
        const mm = String(date.getMonth() + 1).padStart(2, '0');
        const dd = String(date.getDate()).padStart(2, '0');
        return `${yyyy}-${mm}-${dd}`;
      }
      
      document.addEventListener('DOMContentLoaded', () => {
        const fieldInfo = {
          borrower_name: "Enter your full name.",
          phone: "Provide a valid 10-digit mobile number of yours.",
          email: "Enter your Email for updates.",
          loan_item: "What valuable item are you giving as security for the loan?",
  amount: "Enter the total amount of money you need.",
  taken_date: "The date when you received or will receive the loan.",
  payment_plan: `Choose how you plan to repay the loan:<br><br>

• <strong>100 Days Plan:</strong> Repay the full amount day by day for 100 days.<br><br>

• <strong>Weekly:</strong> Make one payment per week over 100 days (about 14 weeks).<br><br>

• <strong>Monthly:</strong> Pay once a month. Interest is calculated only for one month, whether you repay Interets or Total amount.
 `,
  
  return_date: "The date by which you plan to repay the full loan or Interest.",
  referral: "Optional – Mention the person who referred you, if any.",
  photos: "Upload related documents or images (e.g., ID proof, item photos).",
  notes: "Reason for borrowing the money or any additional information."
        };
      
        Object.entries(fieldInfo).forEach(([id, text]) => {
          const input = document.getElementById(id);
          if (input) {
            const icon = document.getElementById(`${id}-icon`);
            const infoBox = document.createElement("div");
            infoBox.className = "info-box";
            infoBox.innerHTML = text;
      
            icon.addEventListener("mouseenter", () => {
              infoBox.style.display = "block";
            });
      
            icon.addEventListener("mouseleave", () => {
              infoBox.style.display = "none";
            });
      
            icon.appendChild(infoBox);
          }
        });
      });