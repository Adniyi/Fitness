const dateFormat = document.getElementById('date');
const formSent = document.getElementById('formSent');
const CaloriesBured = document.getElementById('calories_burned');
const Duration = document.getElementById('duration');
const WorkoutOption = document.getElementById('workout-option');

const WorkoutTable = document.querySelector('.workout-table')



formSent.addEventListener('click',function(e){
    e.preventDefault()
    const formatDate = dateFormat.value;
    if (formatDate) {
        const date = new Date(formatDate);
        const option = {day:'2-digit', month:'short', year:'numeric'};
        const format = date.toLocaleDateString('en-GB', option);
        console.log(format);
        console.log(CaloriesBured.value);
        console.log(Duration.value);
        console.log(WorkoutOption.value);
        console.log("It worked");
        const dataSent = {
            calories: CaloriesBured.value,
            duration : Duration.value,
            formatSent: format,
            workoutoption : WorkoutOption.value
        };
        fetch(`/tracker`,{
            method:'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(dataSent)
        })
        .then(res => res.json())
    }
    
    // dateFormat.value = "";
    // CaloriesBured.value = "";
    // Duration.value = "";
    // WorkoutOption.value = "";
    location.reload(true)

    
});



fetch(`/tracker_data`,{
    method:'GET',
})
.then(res=>res.json())
.then(data => {
    if(data){
        data.forEach(element => {
            createWork(element);
        });
    }   
    
})


const createWork = (data) =>{
    let res =  data;
    WorkoutTable.innerHTML += `
    <div class="workout-table-sub">
        <p>Calories Burned: <span>${res.calories_burned}cals</span></p>
        <p>Duration: <span>${res.duration}mins </span></p>
        <p>Date: <span>${res.date}</span></p>
        <p>Type: <span>${res.type_of_workout}</span></p>
    </div>
    `;
}

