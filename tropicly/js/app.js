// Map obj
var map;
var marker = null;

// samples
var samples = [];
var current = -1;


function nextSample() {
    if(current === samples.length - 1) {
        return;
    }

    if(marker != null) {
        marker.setMap(null);
    }

    current++;
    setSample()
}

function previousSample() {
    if(current <= 0) {
        return;
    }

    if(marker != null) {
        marker.setMap(null);
    }

    current--;
    setSample();
}

function setSample() {
    console.log(samples[current]);

    var sample = samples[current];
    var center = new google.maps.LatLng(sample.y, sample.x);

    updateProgress();
    userInfo(sample.label);

    marker = new google.maps.Marker({position: center, map: map});
    map.panTo(center);
}

function updateProgress() {

}

function userInfo(label) {

}

function loadSamples(results, file) {
    samples = results.data;
    current = -1;
}

function openFile(event) {
    Papa.parse(event.target.files[0], {
        header: true,
        dynamicTyping: true,
        skipEmptyLines: true,
        complete: loadSamples
    });
}

function init() {
    map = new google.maps.Map(document.getElementById("map"), {
        center: {lat: 0, lng: 0},
        zoom: 11,
        mapTypeId: google.maps.MapTypeId.SATELLITE
    });

    var nextButton = document.getElementById('next');
    var previousButton = document.getElementById('prev');
    var openButton = document.getElementById('files');

    nextButton.addEventListener('click', nextSample);
    previousButton.addEventListener('click', previousSample);
    openButton.addEventListener('change', openFile)
}
