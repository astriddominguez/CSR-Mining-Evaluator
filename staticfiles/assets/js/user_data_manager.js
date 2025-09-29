/**
 * Obté el valor del token CSRF des de les cookies del navegador.
 * 
 * Aquest token és necessari per fer peticions POST, PUT o DELETE segures en aplicacions Django,
 * ja que protegeix contra atacs de tipus Cross-Site Request Forgery.
 * 
 * @returns {string|null} El valor del CSRF token si es troba, o `null` en cas contrari.
 */

function getCSRFToken() {
    let cookieValue = null;
    if (document.cookie && document.cookie !== "") {
        const cookies = document.cookie.split(";"); // recorre totes les cookies del navegador
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.startsWith("csrftoken=")) { // cookie que ens interessa: CSRF
                cookieValue = cookie.substring("csrftoken=".length, cookie.length); // obtenim el valor assignat. Ex: csrftoken=3472349823 -> 3472349823. Equivalent a cookie[len("csrftoken="):] en python
                break;
            }
        }
    }
    return cookieValue;
}

/**
 * Obté el token CSRF del servidor mitjançant una petició `fetch`
 * i l’emmagatzema com a cookie accessible des de JavaScript.
 * 
 * Aquesta funció assumeix que el backend (Django) exposa una ruta com
 * `/get-csrf-token/` que retorna una resposta JSON amb el camp `csrftoken`.
 * 
 * El token rebut es guarda com a cookie amb `path=/` per tal que sigui accessible
 * des de qualsevol ruta del domini actual.
 */
function fetchAndSetCsrfToken() {
    fetch("/get-csrf-token/")
      .then(response => response.json())
      .then(data => {
        document.cookie = `csrftoken=${data.csrftoken}; path=/;`;
      });
  }
  
/**
 * Genera un hash SHA-256 en format hexadecimal a partir d’un identificador de fingerprint.
 * 
 * Aquesta funció s’utilitza per encriptar l’ID de fingerprint d’un usuari de forma segura 
 * abans de guardar-lo o utilitzar-lo com identificador únic en el sistema.
 * 
 * Es fa servir la llibreria `jsSHA` per a generar el hash sincrònicament.
 * 
 * @param {string} fingerprintId - L’identificador de fingerprint generat pel client.
 * @returns {string} Hash SHA-256 codificat en hexadecimal.
 */

function hashFingerprintSync(fingerprintId) {
    const shaObj = new jsSHA("SHA-256", "TEXT");
    shaObj.update(fingerprintId);
    return shaObj.getHash("HEX");
}

/**
 * Envia al servidor el fingerprint de l’usuari per guardar-lo a la base de dades.
 * 
 * Aquesta funció fa una petició POST a l’endpoint `/save-fingerprint/` amb el
 * `fingerprintId` en format JSON, incloent el token CSRF per seguretat.
 * 
 * El servidor ha de gestionar aquesta petició i retornar una resposta JSON.
 * 
 * @param {string} fingerprintId - L’identificador únic generat per fingerprinting del client.
 * @returns {Promise<Object>} Resposta JSON del servidor.
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
        return data;
    })
    .catch(error => {
        console.error("Error al guardar Fingerprint:", error);
    });
}

/**
 * Envia les respostes de la secció “Overview” (pas 0 del formulari) al servidor per actualitzar-les.
 * 
 * Aquesta funció fa una petició POST a l’endpoint `/update-overview/` amb les respostes recollides
 * del formulari. El token CSRF s’inclou per complir amb les proteccions de seguretat de Django.
 * 
 * @param {Object} answers - Objecte amb les respostes del pas 0 (projecte, empresa, fase, ubicació...).
 * @returns {Promise<Object>} Resposta JSON del servidor.
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
        return data;
    })
    .catch(error => {
        console.error("Error actualizant l'Overview:", error);
    });
}

/**
 * Envia al servidor les respostes de la dimensió socioeconòmica del formulari.
 * 
 * Aquesta funció fa una petició POST a l’endpoint `/update-socioeconomic-dimension/` amb
 * totes les dades introduïdes per l’usuari en la secció “Dimensió Socioeconòmica”.
 * 
 * El token CSRF es passa a l'encapçalament per garantir la seguretat contra atacs CSRF.
 * 
 * @param {Object} answers - Objecte amb totes les respostes de la dimensió socioeconòmica.
 *                           Inclou el `fingerprint` i totes les preguntes agrupades per secció.
 * @returns {Promise<Object>} Resposta JSON del servidor.
 */
function update_socioeconomic_dimension(answers) {
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
        return data;
    })
    .catch(error => {
        console.error("Error actualizant les dades de la dimensió socioeconòmica:", error);
    });
}

/**
 * Envia al servidor les respostes de la dimensió ambiental del formulari.
 * 
 * Aquesta funció fa una petició POST a l’endpoint `/update-environment-dimension/` amb
 * totes les dades proporcionades per l’usuari en la secció “Dimensió Ambiental”.
 * 
 * Inclou el token CSRF com a mesura de seguretat i espera una resposta JSON del backend.
 * 
 * @param {Object} answers - Objecte amb totes les respostes de la dimensió ambiental,
 *                           incloent el `fingerprint` i les preguntes agrupades per secció.
 * @returns {Promise<Object>} Resposta JSON del servidor.
 */

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
        return data;
    })
    .catch(error => {
        console.error("Error actualizant les dades de la dimensió ambiental:", error);
    });
}



/**
 * Comprova si el `fingerprintId` ja està registrat al sistema i, si és així,
 * retorna les dades del formulari associades.
 * 
 * Aquesta funció envia una petició POST a `/check-fingerprint/` amb l’ID hash del fingerprint
 * i espera que el servidor respongui amb un objecte que indiqui si el fingerprint existeix
 * i, si escau, les dades de formulari prèviament desades.
 * 
 * @param {string} fingerprintId - Identificador únic de l’usuari, hash SHA-256 del fingerprint original.
 * @returns {Promise<Object|null>} Objecte amb les claus:
 *    - `registered` (boolean): si el fingerprint ja estava registrat,
 *    - `form` (objecte): dades del formulari si existeixen.
 *    En cas d’error, retorna `null`.
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
