const attendanceSelect = document.getElementById("attendanceSelect");
    const marksSelect = document.getElementById("marksSelect");
    const assignmentSelect = document.getElementById("assignmentSelect");

    const attendanceUpload = document.getElementById("attendanceUpload");
    const marksUpload = document.getElementById("marksUpload");
    const assignmentUpload = document.getElementById("assignmentUpload");

   
    attendanceSelect.addEventListener("change", function() {
        if (this.value === "BCA" || this.value === "MCA") {
            attendanceUpload.style.display = "block";
        } else {
            attendanceUpload.style.display = "none";
        }
    });

   
    marksSelect.addEventListener("change", function() {
        if (this.value === "BCA" || this.value === "MCA") {
            marksUpload.style.display = "block";
        } else {
            marksUpload.style.display = "none";
        }
    });

    
    assignmentSelect.addEventListener("change", function() {
        if (this.value === "BCA" || this.value === "MCA") {
            assignmentUpload.style.display = "block";
        } else {
            assignmentUpload.style.display = "none";
        }
    });

    
    function goHome() {
        window.location.href = "index.html"; 
    }