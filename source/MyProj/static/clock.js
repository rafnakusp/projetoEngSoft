
var tempo = document.getElementById('relogio');
var ddd = document.getElementById('data');

function time() {
    var d = new Date();
    var seconds = d.getSeconds();
    var minutes = d.getMinutes();
    var hours = d.getHours();
    var day = d.getDate();
    var month = d.getMonth();
    var year = d.getFullYear();
    tempo.textContent = 
      ("0" + hours).substr(-2) + ":" + ("0" + minutes).substr(-2) + ":" + ("0" + seconds).substr(-2);
    ddd.textContent = day + "/" + (month+1) + "/" + year;
    console.log(day);
}

setInterval(time, 1000);