def create_html_sentence_with_summary(sentence, summary):
    """
    Crea una estructura en format HTML que mostra una frase introductòria i, a sota, un resum. 
    Aquesta funció s'utilitza habitualment per generar el contingut de targetes visuals.

    :param sentence (str): Frase introductòria que es mostrarà a la part superior.
    :param summary (str): Resum explicatiu que es mostrarà a continuació.
    :return (str): Cadena HTML amb el contingut formatat.
    """
    summary_template = f"""
    <p class="text-muted fs-5 mb-2">
        <span style="font-size: 0.8em; color: white; text-shadow: 0 0 1px #aaa;">⚪️</span> {sentence}
    </p>
    <p class="text-muted fs-5 mb-3">
        {summary}
    </p>
    """
    return summary_template


def get_html_summary(summary):
    """
    Construeix un paràgraf HTML amb estil per mostrar un resum explicatiu.

    :param summary (str): Text del resum a mostrar.
    :return (str): Cadena HTML amb el paràgraf del resum formatat.
    """
    summary_template = f"""
    <p class="text-muted fs-5 mb-3">
           {summary}
    </p>    
    """
    return summary_template


def get_html_sentence(sentence):
    """
    Construeix un paràgraf HTML amb una frase introductòria precedida d’un icona decoratiu.

    :param sentence (str): Text de la frase introductòria.
    :return (str): Cadena HTML amb la frase formatada i estilada.
    """
    sentence_template = f"""
    <p class="text-muted fs-5 mb-2">
            <span style="font-size: 0.8em; color: white; text-shadow: 0 0 1px #aaa;">⚪️</span> {sentence}
    </p>    
    """
    return sentence_template

def get_html_list(data):
    """
    Construeix una llista HTML (<ul>) on cada element conté un títol en negreta i una descripció.

    :param data (list): Llista de tuples amb parelles (títol, informació).
    :return (str): Cadena HTML amb la llista generada.
    """
    list_items = ""
    for title, info in data:
        list_items += f"<li><strong>{title}:</strong> {info}</li>\n"
    
    list_template = f"""     
        <ul class="fs-5 mb-3">
            {list_items}
        </ul>
    """
    return list_template

def get_html_warning(data):
    """
    Construeix un paràgraf HTML destacat amb un símbol d’advertència.

    :param data (str): Missatge d’advertència.
    :return (str): Cadena HTML amb l’advertència estilada.
    """
    warning = f""" 
    <p class="fs-5 mb-3">⚠️ {data}</p>
    """
    return warning

    

def get_html_table(headers, data):
    """
    Genera una taula HTML a partir de capçaleres i dades.

    :param headers (list): Llista amb els noms de les columnes.
    :param data (list of lists): Cada subllista representa una fila. 
                                 El primer element pot ser opcionalment la classe CSS de la fila.
    :return (str): Taula HTML com a string.
    """
    # Capçalera
    head = "".join(f"<th class='fw-bold'>{h}</th>" for h in headers)
    table_head = f"<thead><tr>{head}</tr></thead>"

    # Files
    rows = ""
    for row in data:
        # Si la fila comença amb una classe (com "table-danger"), la utilitzem
        if isinstance(row[0], str) and row[0].startswith("table-"):
            css_class = row[0]
            values = row[1:]
        else:
            css_class = ""
            values = row

        row_html = "".join(f"<td class='fw-bold'>{v}</td>" for v in values)
        rows += f"<tr class='{css_class}'>{row_html}</tr>\n"

    table_body = f"<tbody>{rows}</tbody>"

    return f"""
    <div class="table-responsive mb-3">
        <table class="table table-bordered table-hover table-sm align-middle text-center">
            {table_head}
            {table_body}
        </table>
    </div>
    """


