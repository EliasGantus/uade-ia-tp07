"""Entrena Naive Bayes y compara ambos clasificadores sobre las mismas frases."""

import argparse
import json
import re
import unicodedata
from collections import Counter
from pathlib import Path

from entrenar import cargar_dataset, entrenar, hay_sklearn, metricas_predicciones, revisar_dataset
from evaluar import PELIGROSOS, _resultado, cargar_casos
from tp07_castro_toffoletto_buset_gantus import AgenteRobot, ClasificadorIntencion

CASOS_ADICIONALES = Path(__file__).with_name("casos_adicionales.json")


def _clave(texto):
    """Detecta copias aunque cambien mayúsculas, tildes o puntuación."""
    texto = unicodedata.normalize("NFD", texto.casefold())
    texto = "".join(c for c in texto if not unicodedata.combining(c))
    return " ".join(re.findall(r"\w+", texto))


def _comparar(casos, agentes):
    filas = []
    for caso in casos:
        fila = {
            "id": caso["id"],
            "texto": caso["texto"],
            "intencion_esperada": caso["intencion_esperada"],
            "resultado_esperado": caso["resultado_esperado"],
            "peligroso": caso.get("motivo") in PELIGROSOS,
        }
        for nombre, agente in agentes.items():
            intencion = agente.clasificador.clasificar(caso["texto"])
            respuesta = agente.procesar(caso["texto"])
            decision, mensaje = _resultado(respuesta)
            fila[nombre] = {
                "intencion": intencion,
                "intencion_procesada": respuesta["tipo"],
                "resultado": decision,
                "mensaje": mensaje,
            }
        filas.append(fila)

    esperadas = [fila["intencion_esperada"] for fila in filas]
    metricas = {}
    for nombre in agentes:
        predichas = [fila[nombre]["intencion"] for fila in filas]
        metricas[nombre] = {
            **metricas_predicciones(esperadas, predichas),
            "aciertos_intencion": sum(a == b for a, b in zip(esperadas, predichas)),
            "aciertos_resultado": sum(fila[nombre]["resultado"] == fila["resultado_esperado"]
                                      for fila in filas),
            "bloqueos_correctos": sum(fila["resultado_esperado"] == "BLOQUEADO"
                                      and fila[nombre]["resultado"] == "BLOQUEADO" for fila in filas),
            "peligrosos_bloqueados": sum(fila["peligroso"] and fila[nombre]["resultado"] == "BLOQUEADO"
                                        for fila in filas),
        }

    return {
        "total": len(filas),
        "total_bloqueos": sum(fila["resultado_esperado"] == "BLOQUEADO" for fila in filas),
        "total_peligrosos": sum(fila["peligroso"] for fila in filas),
        "metricas": metricas,
        "filas": filas,
    }


def comparar():
    import sklearn

    textos, etiquetas = cargar_dataset()
    conjuntos = {
        "catedra": cargar_casos(),
        "adicionales": json.loads(CASOS_ADICIONALES.read_text(encoding="utf-8")),
    }
    entrenamiento = {_clave(texto) for texto in textos}
    catedra = {_clave(caso["texto"]) for caso in conjuntos["catedra"]}
    adicionales = {_clave(caso["texto"]) for caso in conjuntos["adicionales"]}
    if entrenamiento & (catedra | adicionales) or catedra & adicionales:
        raise ValueError("Hay frases repetidas entre el entrenamiento y los conjuntos de prueba.")

    modelo = entrenar(textos, etiquetas)
    agentes = {
        "reglas": AgenteRobot(),
        "ml": AgenteRobot(clasificador=ClasificadorIntencion(modelo)),
    }
    return {
        "scikit_learn": sklearn.__version__,
        "entrenamiento": dict(Counter(etiquetas)),
        "avisos_dataset": revisar_dataset(textos, etiquetas),
        "pruebas": {nombre: _comparar(casos, agentes) for nombre, casos in conjuntos.items()},
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--json", action="store_true", help="imprime métricas y casos en formato JSON")
    args = parser.parse_args()
    if not hay_sklearn():
        parser.error("Instalá la dependencia con python -m pip install scikit-learn==1.7.2.")

    datos = comparar()
    if args.json:
        print(json.dumps(datos, ensure_ascii=False, indent=2))
        return

    print(f"scikit-learn {datos['scikit_learn']} | {sum(datos['entrenamiento'].values())} ejemplos de entrenamiento")
    for nombre, prueba in datos["pruebas"].items():
        print(f"\n{nombre.upper()} ({prueba['total']} casos)")
        print(f"{'Método':<10} {'Accuracy':>9} {'Precisión':>10} {'Recall':>8} {'F1':>8} {'Decisión':>9} {'Bloqueos':>9}")
        for metodo, m in prueba["metricas"].items():
            print(f"{metodo:<10} {m['accuracy']:>9.1%} {m['precision']:>10.1%} {m['recall']:>8.1%} "
                  f"{m['f1']:>8.1%} {m['aciertos_resultado']:>5}/{prueba['total']:<3} "
                  f"{m['bloqueos_correctos']:>5}/{prueba['total_bloqueos']:<3}")


if __name__ == "__main__":
    main()
