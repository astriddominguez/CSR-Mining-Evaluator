/*
========== 
CSRF Token
========== 
*/

function getCSRFToken() {
    let cookieValue = null;
    if (document.cookie && document.cookie !== "") {
        const cookies = document.cookie.split(";");
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            console.log(cookie);
            if (cookie.startsWith("csrftoken=")) {
                cookieValue = cookie.substring("csrftoken=".length, cookie.length);
                break;
            }
        }
    }
    return cookieValue;
}

/*
=======================
Registra el Fingerprint
======================= 
*/

function save_fingerprint(fingerprintId) { 
    console.log("holaaaaaaa");
    console.log(getCSRFToken());
    return $.ajax({
        url: "/save-fingerprint/",
        type: "POST",
        contentType: "application/json",
        headers: { "X-CSRFToken": getCSRFToken() },
        data: JSON.stringify({ fingerprint_id: fingerprintId })
    })
    .done(data => console.log("Fingerprint guardado:", data))
    .fail(error => console.error("Error al guardar Fingerprint:", error));
}

/*
=================================================
Actualitza les dades del primer pas del formulari
=================================================
*/

console.log("✅ fingerprint.js cargado correctamente");

function update_overview(fingerprintId, answers) { 
    console.log("Actualizando overview");
    return $.ajax({
        url: "/update-overview/",
        type: "POST",
        contentType: "application/json",
        headers: { "X-CSRFToken": getCSRFToken() },
        data: JSON.stringify({
            fingerprint: fingerprintId,
            project_name: answers['project_name'],
            company_name: answers['company_name'], 
            longitude: answers['longitude'],
            latitude: answers['latitude'],
            phase: answers['phase']
        })
    })
    .done(data => console.log("Django Response:", data))
    .fail(error => console.error("Error actualizando initial step:", error));
}

/*
===============================
Retorna les dades del formulari
===============================
*/

function get_form_data(fingerprintId) { 
    return $.ajax({
        url: "/get-filled-form-data/",
        type: "POST",
        contentType: "application/json",
        headers: { "X-CSRFToken": getCSRFToken() },
        data: JSON.stringify({ fingerprint: fingerprintId })
    })
    .fail(error => console.error("Error obteniendo datos del formulario:", error));
}

/*
===========================================
Revisa si el fingerprint es troba registrat
=========================================== 
*/

function check_fingerprint(fingerprintId) {
    return $.ajax({
        url: "/check-fingerprint/",
        type: "POST",
        contentType: "application/json",
        headers: { "X-CSRFToken": getCSRFToken() },
        data: JSON.stringify({ fingerprint_id: fingerprintId })
    })
    .fail(error => {
        console.error("Error verificando Fingerprint:", error);
        return null;
    });
}
