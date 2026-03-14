const courseSelect = document.getElementById("courseSelect");
const subjectsDiv = document.getElementById("subjects");

courseSelect.addEventListener("change", function () {

let course = this.value;

let subjects = [];

if(course === "mca"){

subjects = [
"Advanced Java",
"Cloud Computing",
"Machine Learning",
"Software Engineering"
];

}

else if(course === "bca"){

subjects = [
"C Programming",
"Data Structures",
"Operating System",
"Computer Networks"
];

}

subjectsDiv.innerHTML = "";

subjects.forEach(function(sub){

let card = document.createElement("div");

card.classList.add("subject-card");

card.innerText = sub;

subjectsDiv.appendChild(card);

});

});



function logout(){

window.location.href = "index.html";

}