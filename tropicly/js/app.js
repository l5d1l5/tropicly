// Map obj
var map;
var marker = null;

// html obj
var nextButton;
var openButton;

// samples
var samples = [[10, 10], [20, 20]];
var finished = [];


function moveToLocation(event) {
    if(marker != null){
        marker.setMap(null)
    }

    var current = samples.pop();

    var center = new google.maps.LatLng(current[0], current[1]);
    marker = new google.maps.Marker({position: center, map: map});

    map.panTo(center);
}

function openFile(event) {
    console.log(event.target.files[0]);
    Papa.parse(event.target.files[0], {
        complete: function (results) {
            console.log(results);
        }
    });
}

function init() {
    var mapOptions = {
        center: {lat: 0, lng: 0},
        zoom: 11,
        mapTypeId: google.maps.MapTypeId.SATELLITE
    };
    map = new google.maps.Map(document.getElementById("map"), mapOptions);

    nextButton = document.getElementById('next');
    openButton = document.getElementById('files');

    nextButton.addEventListener('click', moveToLocation);
    openButton.addEventListener('change', openFile)
}
