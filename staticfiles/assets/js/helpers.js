/**
 * Oculta tots els popovers actius del formulari.
 * 
 * Aquesta funció recorre tots els elements del DOM que tenen l'atribut
 * `data-bs-toggle="popover"` i, si tenen una instància activa de `bootstrap.Popover`,
 * la tanca programàticament.
 * 
 * S'utilitza per evitar que quedin boletes d'informació obertes quan l'usuari
 * canvia de pas del formulari.
 */

function hideAllPopovers() {
    $('[data-bs-toggle="popover"]').each(function () {
      const popover = bootstrap.Popover.getInstance(this);
      if (popover) {
        popover.hide();
      }
    });
  }

/**
 * Actualitza l’estat i la visibilitat dels botons de navegació del formulari
 * segons el pas actual en què es troba l’usuari.
 *
 * @param {number} currentStep - Índex del pas actual del formulari (comença en 0)
 */

function update_buttons(currentStep) {
    // Obté l’índex de l’últim pas (nombre total de passos - 1)
    let lastStep = $(".form-step").length - 1;

    // Alineació dels botons dins del contenidor:
    // - Només a la dreta si estem al pas inicial
    // - Separats entre si (entre esquerra i dreta) si estem a un pas posterior
    $("#buttons").toggleClass("justify-content-end", currentStep === 0) 
     .toggleClass("justify-content-between", currentStep > 0);


    // Mostra o amaga el botó 'Anterior' depenent de si estem al primer pas
    $(".prev-step").toggleClass("d-none", currentStep === 0);
    // Mostra o amaga el botó 'Següent' depenent de si estem a l'últim pas
    $(".next-step").toggleClass("d-none", currentStep === lastStep);

    // Mostra el botó 'Finalitzar' només quan estem a l’últim pas del formulari
    if (currentStep === lastStep) {
        $("#end-form").removeClass("d-none");
    } else {
        $("#end-form").addClass("d-none");
    }
}

/**
 * Obté tots els valors dels camps d'una secció concreta d'un formulari en format d'acordió.
 * 
 * Aquesta funció busca inputs dins del bloc `.accordion-collapse` amb l’ID `collapse<SECTION_ID>`,
 * i retorna un objecte amb els valors identificats per `name` o `id`, segons el cas.
 * 
 * @param {string|number} sectionId - L'identificador numèric o string de la secció (sense el prefix 'collapse').
 * @returns {Object} Un objecte clau-valor amb totes les respostes de la secció.
 */
function get_accordion_values(sectionId) {
    // Localitza la secció de l'acordió corresponent
    const section = document.querySelector(`#collapse${sectionId}`);
    if (!section) return {};  // Si no existeix, retorna un objecte buit

    // Selecciona tots els inputs i selects dins de la secció
    const inputs = section.querySelectorAll("input, select");
    let values = {};

    // Itera sobre cada input/select trobat
    inputs.forEach(input => {
        // Cas 1: Botons de selecció única (Sí/No)
        if (input.type === "radio") {
            if (input.checked) {
                 // Codifiquem "on" per Sí i "off" per No (a partir del seu ID)
                if (input.id.startsWith("true-")){
                    values[input.name] = 'on';
                }
                else{
                    values[input.name] = 'off';
                }
            }
          
         // Cas 2: Checkbox (múltiples opcions)
        } else if (input.type === "checkbox") {
            values[input.name] = input.checked;

        // Cas 3: Select amb múltiples opcions
        } else if (input.tagName === "SELECT" && input.multiple) {
            values[input.id] = Array.from(input.selectedOptions).map(option => option.value);
        // Cas 4: Camps de text, números, selects normals...
        } else {
            values[input.name || input.id] = input.value;
        }
    });

    return values;
}

/**
 * Recull totes les respostes dels formularis agrupats dins d'una targeta (card) amb acordions.
 * 
 * Aquesta funció cerca totes les seccions (accordions) dins d’una targeta concreta identificada per `cardId`,
 * i per a cadascuna crida `get_accordion_values` per obtenir els valors dels inputs d’aquella secció.
 * 
 * Els IDs de cada acordió es pressuposen amb el format `accordion<SectionId>`, i s’utilitza el `SectionId`
 * com a clau principal de l’objecte final retornat.
 * 
 * @param {string} cardId - L'ID HTML del contenidor de la targeta (sense `#`, però s’aplica amb jQuery).
 * @returns {Object} Objecte amb les dades de cada secció, estructurat com: 
 *                   { section1: {...}, section2: {...}, ... }
 */
function collect_all_card_responses(cardId) {
    let $card = $(`#${cardId}`); // Selecciona la targeta principal per ID
    let $accordions = $card.find(".accordion"); // Troba tots els elements acordió dins d’aquesta targeta
    let values = {}; // Objecte on s’acumularan totes les respostes

    if ($card.length) {
        $accordions.each(function () {
            let id = $(this).attr("id");
            // Només processa els elements amb ID que comencin per 'accordion'
            if (id && id.startsWith("accordion")) {
                let cleanId = id.slice(9); // Elimina el prefix 'accordion' → extreu el nom real de la secció
                values[cleanId] = get_accordion_values(cleanId); // Obté les respostes d’aquella secció
            }
        });
    }
    return values;
}


/**
 * Introdueix valors en un `<select>` amb múltiples opcions seleccionables (Select2).
 * 
 * Aquesta funció és útil per reinserir valors al formulari quan es carreguen dades prèviament desades.
 * Accepta tant cadenes separades per comes (`"opció1, opció2"`) com arrays en format JSON (`["opció1", "opció2"]`).
 * 
 * @param {string} value - Cadena amb valors (separats per comes o en format JSON).
 * @param {string} id - ID del `<select multiple>` on s’han d’inserir les opcions (com a string CSS: `#id`).
 */

function insert_in_multiple_selector(value, id){
    let parsedList;
    // Cas 1: Si es rep una cadena separada per comes (ex: "a, b, c")
    // Es divideix en un array netejant espais
    if (typeof value === 'string' && !value.trim().startsWith('[')) {
        parsedList = value.split(',').map(e => e.trim());
    // Cas 2: Si es rep un array en format JSON però amb cometes simples (no vàlid)
    // Es corregeix substituint cometes simples per dobles
    } else {
        let fixedValue = value.replace(/'/g, '"');
        parsedList = JSON.parse(fixedValue);
    }
    // Assigna els valors i dispara l’event 'change' perquè Select2 els mostri com seleccionats
    $(id).val(parsedList).trigger('change');
}

/**
 * Valida que el valor introduït en un input numèric estigui dins del rang permès.
 * 
 * Aquesta funció comprova si el valor d’un camp està dins dels límits especificats
 * per les propietats `min` i `max` de l’element `<input>`. 
 * Si no ho està, mostra un missatge d’alerta i marca l’input com a invàlid.
 * 
 * @param {HTMLElement} input - L'element `<input>` que es vol validar.
 */

function validateLimit(input) {
    // Valida les entrades per a que tingui valors vàlids
    const $input = $(input);
    const alert_div = $('#' + input.id + '-alert'); // contenidor que mostra el missatge d'alerta (previament amagat)
    const min = parseFloat(input.min); // valor mínim
    const max = parseFloat(input.max); // valor màxim
    const valor = parseFloat(input.value); // valor entrat per l'usuari

    // Comprova si el valor està fora dels límits especificats
    if (valor > max || valor < min) { // valor fora de rang
      $input.addClass('is-invalid'); // clase is-invalid que permet mostrar el missatge d'alerta sota el camp
      if (Number.isNaN(max)) { // quan no s'especifica màxim
        alert_div.text("El valor ha de ser mínim " + min + ".");
      } else { // el valor ha d'estar dins un interval vàlid
        alert_div.text("El valor ha d'estar entre " + min + " i " + max + "."); // insereix el text dins el contenidor del missatge
      }
    }
    // Si tot és correcte, esborra el missatge d'error i la classe d'error
    else {
      $input.removeClass('is-invalid');
      alert_div.empty();
    }

  }

   /**
   * Aplica la lògica de dependències entre preguntes del formulari.
   * 
   * Algunes preguntes només s’han de mostrar si l’usuari ha respost "Sí" a una pregunta anterior.
   * Aquesta relació es defineix mitjançant l’atribut `data-depends-on` en l’element dependent.
   * 
   * Requisits:
   * - Les preguntes que decideixen han de ser de tipus Sí/No (amb inputs `#true-<id>` i `#false-<id>`).
   * - L’ID del control "pare" ha d'estar referenciat a `data-depends-on` (ex: `data-depends-on="question-foo"`).
   * 
   * Exemple d’estructura:
   *   <div id="dependent-question" data-depends-on="question-foo">...</div>
   *   <input id="true-foo" type="radio" name="foo" value="true">
   *   <input id="false-foo" type="radio" name="foo" value="false">
   */

   function apply_dependencies() {
    // Recorre tots els elements que tenen dependències declarades 
    $('[data-depends-on]').each(function() {
      const $dependent = $(this); // L’element dependent (que mostra o amaga)
      const dependsOn = $dependent.data('depends-on');  // El camp del qual depèn, ex: 'question-foo'
      
      // Elimina el prefix 'question-' si existeix per obtenir l'ID base de la pregunta condicional
      const mainDependsOn = dependsOn.replace("question-", "");

      // Inputs de control que decideixen la visibilitat
      const $trueInput = $('#true-' + mainDependsOn); // Radio "Sí"
      const $falseInput = $('#false-' + mainDependsOn); // Radio "No"

      // Funció que mostra o amaga l’element dependent segons el valor seleccionat
      const toggle = function() {
        const trueChecked = $trueInput.is(':checked');
        const falseChecked = $falseInput.is(':checked');

        if (falseChecked) { 
          $dependent.hide();  // Si l'usuari ha triat "No", s’amaga
        } else if (trueChecked) { 
          $dependent.fadeIn(800); // Si ha triat "Sí" o cap opció, es mostra amb una animació suau
        } else {
          // Cas excepcional: no s’ha seleccionat ni "Sí" ni "No".
          // Això no hauria de passar en condicions normals, però per seguretat,
          // es prioritza mostrar la pregunta dependent.
          $dependent.fadeIn(800);
        }
      };

      // Assigna l'esdeveniment `change` i `input` als botons de Sí i No (si existeixen).
      // Això permet mostrar o amagar dinàmicament la pregunta dependent en temps real,
      // segons el valor seleccionat per l’usuari.
      if ($trueInput.length) {
        $trueInput.on('change input', toggle);
      }
      if ($falseInput.length) {
        $falseInput.on('change input', toggle);
      }

      // Executa la funció de control `toggle()` un cop en carregar la pàgina,
      toggle();
    });

  }