const locations = {
  arekere: { lat: 12.890631905939655, lng: 77.59808109273573, zoom: 18.5 },
  jp_nagar: { lat: 12.906434245038183, lng: 77.5804062705511, zoom: 19 },
};

// Function to get location parameter from URL
function getLocationFromURL() {
  const urlParams = new URLSearchParams(window.location.search);
  const location = urlParams.get("location");
  return locations[location] || locations["arekere"]; // Default to 'arekere' if not specified
}

const current = getLocationFromURL();

function initMap() {
  const map = new google.maps.Map(document.getElementById("map"), {
    zoom: current.zoom,
    center: { lat: current.lat, lng: current.lng },
    disableDefaultUI: true,
    draggable: false,
    fullscreenControl: true,
    styles: [
      {
        featureType: "poi",
        stylers: [{ visibility: "off" }],
      },
      {
        featureType: "street poi",
        stylers: [{ visibility: "off" }],
      },
    ],
  });
  const trafficLayer = new google.maps.TrafficLayer();
  trafficLayer.setMap(map);
}

window.initMap = initMap;
