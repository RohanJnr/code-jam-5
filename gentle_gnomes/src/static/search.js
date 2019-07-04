const inputName = document.getElementById('name');
const inputLocation = document.getElementById('location');
const form = document.getElementById('search-form');
const map = document.getElementById('map');

const restrictions = {'country': ['us']};
autocomplete = new google.maps.places.Autocomplete(inputName);
autocomplete.setFields(['geometry']);
autocomplete.setComponentRestrictions(restrictions);

const acService = new google.maps.places.AutocompleteService();
const placesService = new google.maps.places.PlacesService(map);
const sessionToken = new google.maps.places.AutocompleteSessionToken();

function setLocation(location) {
    inputLocation.setAttribute('value', JSON.stringify(location));
}

function getTopLocation(predictions, status) {
    if (status !== google.maps.places.PlacesServiceStatus.OK) {
        console.error('Could not get predictions: status is ' + status);
        return;
    }

    const request = {
        fields: ['geometry.location'],
        placeId: predictions[0].place_id,
        sessionToken: sessionToken
    };

    placesService.getDetails(request, (result, status) => {
        if (status !== google.maps.places.PlacesServiceStatus.OK) {
            console.error('Could not get details: status is ' + status);
            return;
        }

        setLocation(result.geometry.location);
    });
}

form.addEventListener('submit', () => {
    const place = autocomplete.getPlace();

    if (place === undefined) {
        const request = {
            componentRestrictions: restrictions,
            input: inputName.value,
            sessionToken: sessionToken
        };

        acService.getPlacePredictions(request, getTopLocation);
    } else {
        setLocation(place.geometry.location);
    }
});
