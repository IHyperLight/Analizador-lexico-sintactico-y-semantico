from flask import Flask, render_template, redirect, flash, url_for, request, session
import sqlite3
import os
from analysis import run_lexical_analyzer, run_syntax_analyzer, run_semantic_analyzer

app = Flask(__name__)

# Configuración simple para desarrollo y producción
app.secret_key = os.environ.get("SECRET_KEY", "llave_secreta_demo_analizador_sql_2025")

# Base de datos SQLite persistente
DB_PATH = os.path.join(os.path.dirname(__file__), "analizador.db")


def create_db_connection():
    """Crea conexión a SQLite - No requiere configuración externa"""
    try:
        connection = sqlite3.connect(DB_PATH)
        return connection
    except sqlite3.Error as error:
        print(f"Error de conexión a SQLite: {error}")
        return None


def execute_query(connection, query):
    """Ejecuta query en SQLite - Adaptado para sintaxis compatible"""
    try:
        # Detectar comandos que SQLite no soporta pero que simulamos
        query_upper = query.strip().upper()

        # CREATE DATABASE y USE DATABASE solo se simulan, no se ejecutan
        if query_upper.startswith("CREATE DATABASE") or query_upper.startswith("USE "):
            print(f"Simulated command: {query}")
            result = "Éxito, sentencias ejecutadas correctamente"
            return result

        # Ejecutar otros comandos normalmente
        cursor = connection.cursor()
        cursor.execute(query)
        connection.commit()
        print("Query executed successfully")
        result = "Éxito, sentencias ejecutadas correctamente"
        return result
    except sqlite3.Error as e:
        print(f"Error executing query: {e}")
        session["semant_result"] = str(e)
        result = f"Error SQLite: {str(e)}"
        return result


def logic(connection, step):
    analyzers = [
        ("lex", run_lexical_analyzer),
        ("sintact", run_syntax_analyzer),
        ("semant", run_semantic_analyzer),
    ]
    return_result = []
    flag = False

    results = {}
    for analyzer_type, analyzer_func in analyzers:
        result, error = (
            analyzer_func(connection, step)
            if analyzer_type == "semant"
            else analyzer_func(step)
        )

        if error:
            for a, _ in analyzers:
                if flag:
                    results[f"{a}_result"] = ""
                if analyzer_type == a:
                    results[f"{analyzer_type}_result"] = result
                    flag = True
            session.update(results)
            return_result.append(
                f"Hubo un error {analyzer_type}ico, revisa las salidas de los analizadores."
            )
            return return_result

        results[f"{analyzer_type}_result"] = result

    session.update(results)
    return_result.append(execute_query(connection, step))
    return return_result


def flow(connection, *steps):
    results = []

    for step in steps:
        if step:
            result = logic(connection, step)
            results.append(result)
        else:
            continue
    print(results)
    return results


@app.route("/", methods=["GET", "POST"])
def front():
    analyzers = ["lex", "sintact", "semant"]
    results = {}
    s = []

    connection = create_db_connection()

    if not connection:
        flash("Error de conexión a la base de datos.", "notify")
        return render_template(
            "front.html",
            value_1="",
            value_2="",
            value_3="Error de conexión a la base de datos",
        )

    if request.method == "POST":
        # En POST, obtener valores de la sesión
        lex_result = session.get("lex_result", "")
        sintact_result = session.get("sintact_result", "")
        semant_result = session.get("semant_result", "")
        steps = [
            request.form.get("step_1", ""),
            request.form.get("step_2", ""),
            request.form.get("step_3", ""),
            request.form.get("step_4", ""),
            request.form.get("step_5", ""),
        ]

        button_areas = [
            (
                "btn_1",
                "area_1",
                run_lexical_analyzer,
                "Análisis léxico ejecutado",
                "lex_result",
                None,
            ),
            (
                "btn_2",
                "area_2",
                run_syntax_analyzer,
                "Análisis sintáctico ejecutado",
                "sintact_result",
                None,
            ),
            (
                "btn_3",
                "area_3",
                run_semantic_analyzer,
                "Análisis semántico ejecutado",
                "semant_result",
                "connection",
            ),
        ]

        for (
            button,
            area,
            analyzer_func,
            message,
            result_key,
            additional_param,
        ) in button_areas:
            if request.form.get(button):
                x = request.form.get(area)
                if x:
                    if additional_param:
                        a, b = analyzer_func(connection, x)
                    else:
                        a, b = analyzer_func(x)
                    results = {
                        "lex_result": "",
                        "sintact_result": "",
                        "semant_result": "",
                    }
                    results[result_key] = a
                    session.update(results)
                flash(message, "notify")
                return redirect(url_for("front"))

        if steps[0]:
            result = logic(connection, steps[0])
            if steps[1]:
                result = flow(connection, *steps[1:])
            print(result)
            flash(result[-1], "notify")
        elif steps[1]:
            result = flow(connection, *steps[1:])
            flash(result[-1], "notify")
        elif steps[2]:
            result = flow(connection, *steps[2:])
            flash(result[-1], "notify")
        elif steps[3]:
            result = flow(connection, *steps[3:])
            flash(result[-1], "notify")
        elif steps[4]:
            result = logic(connection, steps[4])
            flash(result[-1], "notify")
        else:
            for n in analyzers:
                results[f"{n}_result"] = ""
            session.update(results)
            flash("Error, revisa los campos faltantes o introducidos.", "notify")

        connection.close()
        return redirect(url_for("front"))
    
    # En GET (recarga de página), limpiar la sesión y mostrar campos vacíos
    session.pop("lex_result", None)
    session.pop("sintact_result", None)
    session.pop("semant_result", None)
    
    connection.close()
    return render_template(
        "front.html", value_1="", value_2="", value_3=""
    )


def main():
    port = int(os.environ.get("PORT", 5000))
    debug = os.environ.get("FLASK_ENV") != "production"
    app.run(debug=debug, port=port, host="0.0.0.0")


if __name__ == "__main__":
    main()
