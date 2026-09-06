document.addEventListener("DOMContentLoaded", function () {
    const latitude = document.getElementById("id_latitude");
    const longitude = document.getElementById("id_longitude");

    // Run only on the project add/edit form.
    if (!latitude || !longitude) return;

    const container = document.createElement("div");
    container.style.margin = "20px 0";

    const instruction = document.createElement("p");
    instruction.textContent =
        "اضغط على الخريطة لتحديد الموقع، أو اسحب العلامة لتعديله.";

    const mapElement = document.createElement("div");
    mapElement.id = "project-location-map";
    mapElement.style.height = "360px";
    mapElement.style.width = "100%";
    mapElement.style.maxWidth = "900px";
    mapElement.style.borderRadius = "12px";

    container.append(instruction, mapElement);

    const locationRow = longitude.closest(".form-row");
    if (!locationRow) return;
    locationRow.insertAdjacentElement("afterend", container);

    if (!window.L) {
        instruction.textContent =
            "تعذر تحميل الخريطة. يمكنك إدخال الإحداثيات يدويًا.";
        mapElement.hidden = true;
        return;
    }

    function readCoordinates() {
        const latText = latitude.value.trim();
        const lngText = longitude.value.trim();

        if (!latText || !lngText) return null;

        const lat = Number(latText);
        const lng = Number(lngText);

        if (
            !Number.isFinite(lat) ||
            !Number.isFinite(lng) ||
            lat < -90 || lat > 90 ||
            lng < -180 || lng > 180
        ) {
            return null;
        }

        return [lat, lng];
    }

    const initialCoordinates = readCoordinates();
    const map = L.map(mapElement).setView(
        initialCoordinates || [25.2854, 51.5310],
        initialCoordinates ? 16 : 11
    );

    L.tileLayer("https://tile.openstreetmap.org/{z}/{x}/{y}.png", {
        maxZoom: 19,
        attribution:
            '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>'
    }).addTo(map);

    let marker = null;

    function updateFields(latlng) {
        latitude.value = latlng.lat.toFixed(6);
        longitude.value = latlng.lng.toFixed(6);
    }

    function placeMarker(coordinates) {
        if (marker) {
            marker.setLatLng(coordinates);
            return;
        }

        marker = L.marker(coordinates, {
            draggable: true
        }).addTo(map);

        marker.on("dragend", function () {
            updateFields(marker.getLatLng());
        });
    }

    if (initialCoordinates) {
        placeMarker(initialCoordinates);
    }

    map.on("click", function (event) {
        placeMarker(event.latlng);
        updateFields(event.latlng);
    });

    function syncFromFields() {
        const coordinates = readCoordinates();

        if (!coordinates) {
            if (marker) {
                map.removeLayer(marker);
                marker = null;
            }
            return;
        }

        placeMarker(coordinates);
        map.setView(coordinates, 16);
    }

    latitude.addEventListener("change", syncFromFields);
    longitude.addEventListener("change", syncFromFields);

    requestAnimationFrame(function () {
        map.invalidateSize();
    });
});