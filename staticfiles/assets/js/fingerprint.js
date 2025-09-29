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

function hashFingerprintSync(fingerprintId) {
    const shaObj = new jsSHA("SHA-256", "TEXT");
    shaObj.update(fingerprintId);
    return shaObj.getHash("HEX");
}


/*
=======================
Registra el Fingerprint
======================= 
*/

function save_fingerprint(fingerprintId) {
    return fetch("/save-fingerprint/", {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
            "X-CSRFToken": getCSRFToken()
        },
        body: JSON.stringify({ fingerprint_id: fingerprintId }),
        credentials: "include"
    })
    .then(response => response.json())
    .then(data => {
        console.log("Fingerprint guardado:", data);
        return data;
    })
    .catch(error => {
        console.error("Error al guardar Fingerprint:", error);
    });
}

/*
=================================================
Actualitza les dades del primer pas del formulari
=================================================
*/

function update_overview(answers) {
    return fetch("/update-overview/", {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
            "X-CSRFToken": getCSRFToken()
        },
        body: JSON.stringify(answers),
        credentials: "include"
    })
    .then(response => response.json())
    .then(data => {
        console.log("Django Response:", data);
        return data;
    })
    .catch(error => {
        console.error("Error actualizant l'Overview:", error);
    });
}

function update_socioeconomic_dimension(answers) {
    console.log("Respostesss");
    console.log(answers);
    return fetch("/update-socioeconomic-dimension/", {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
            "X-CSRFToken": getCSRFToken()
        },
        body: JSON.stringify(answers),
        credentials: "include"
    })
    .then(response => response.json())
    .then(data => {
        console.log("Django Response:", data);
        return data;
    })
    .catch(error => {
        console.error("Error actualizant les dades de la dimensió socioeconòmica:", error);
    });
}

function update_environment_dimension(answers) {
    return fetch("/update-environment-dimension/", {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
            "X-CSRFToken": getCSRFToken()
        },
        body: JSON.stringify(answers),
        credentials: "include"
    })
    .then(response => response.json())
    .then(data => {
        console.log("Django Response:", data);
        return data;
    })
    .catch(error => {
        console.error("Error actualizant les dades de la dimensió ambiental:", error);
    });
}



/*
=============================================================================
Revisa si el fingerprint es troba registrat i retorna les dades del formulari
============================================================================= 
*/

function check_fingerprint(fingerprintId) {
    return fetch("/check-fingerprint/", {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
            "X-CSRFToken": getCSRFToken()
        },
        body: JSON.stringify({ fingerprint_id: fingerprintId }),
        credentials: "include"
    })
    .then(response => response.json())
    .catch(error => {
        console.error("Error verificando Fingerprint:", error);
        return null;
    });
}
