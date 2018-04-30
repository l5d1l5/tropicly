// Map obj
var map;
var marker = null;

// samples
var samples = [];
var current = -1;
var name;

// html obj
var labelInput;
var validationInput;
var remainInput;
var totalInput;


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
    labelInput.value = sample.label;

    marker = new google.maps.Marker({position: center, map: map});
    map.panTo(center);
}

function updateProgress() {
    remainInput.value = current + 1;
    totalInput.value = samples.length;
}

function updateSample(event) {
    if(current === -1 || current === samples.length) {
        return;
    }
    samples[current].validation = validationInput.value;
    console.log(samples[current]);
}

function keybinds(event) {
    switch(event.keyCode) {
        case 68:
            nextSample();
            break;
        case 65:
            previousSample();
            break;
    }
}

function download() {
    var csv = Papa.unparse(samples, {
        delimiter: ',',
        header: true,
        newline: '\n'
    });
    var a = document.getElementById('a');
    var file = new Blob([csv], {type: 'text/plain'});
    a.href = URL.createObjectURL(file);
    a.download = name;
}

function loadSamples(results, file) {
    samples = results.data;
    name = file.name;
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
    labelInput = document.getElementById('label');
    validationInput = document.getElementById('valid');
    remainInput = document.getElementById('remain');
    totalInput = document.getElementById('total');

    var nextButton = document.getElementById('next');
    var downloadButton = document.getElementById('download');
    var previousButton = document.getElementById('prev');
    var openButton = document.getElementById('files');

    nextButton.addEventListener('click', nextSample);
    downloadButton.addEventListener('click', download);
    previousButton.addEventListener('click', previousSample);
    openButton.addEventListener('change', openFile);
    validationInput.addEventListener('change', updateSample);

    document.addEventListener('keydown', keybinds);
}
