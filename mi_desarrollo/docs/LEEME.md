# Tu carpeta de trabajo — TP07

| Archivo | Para qué |
|---|---|
| `tp07_castro_toffoletto_buset_gantus.py` | El agente: clasificador, extractor, validador y ejecutor. **Es lo que se entrega.** |
| `mi_tp07.py` | Acceso con el nombre de la plantilla: ejecuta el archivo de entrega (lo usan los scripts `EJECUTAR_MI_CODIGO`). |
| `casos_prueba.json` | Los 25 casos de la cátedra. Dados hechos. |
| `evaluar.py` | Dado hecho. Calcula tu accuracy y la tabla de fallos. |
| `ejecutor.py` | Dado hecho. Convierte a velocidad y tiempo, y manda al robot. |
| `robot.py` | No lo toques. |
| `dataset.csv` | 80 frases anotadas para entrenar Naive Bayes. |
| `entrenar.py` | Entrena el modelo y calcula métricas de clasificación. |
| `casos_adicionales.json` | 30 frases reservadas para medir generalización. |
| `comparar_clasificadores.py` | Compara las reglas y Naive Bayes. |

## Cómo lo ejecutás

**Con robot** (para ver al G1 hacerte caso):

1. Abrí `INICIAR_SIMULADOR` y elegí el robot.
2. Doble clic en `EJECUTAR_MI_CODIGO`, o `python3 mi_desarrollo/mi_tp07.py`.

**Sin robot** (para trabajar el clasificador tranquilo):

```
python3 mi_desarrollo/mi_tp07.py --sin-robot
```

Corre los 25 casos y te da la accuracy, sin abrir nada.

## Modo interactivo

Con el robot conectado, después de la evaluación podés escribirle órdenes:

```
  > avanzá 2 metros
  > girá 90 grados a la derecha
  > salta desde la mesa
```

Es la mejor forma de encontrar los casos que tu agente no cubre.

## Extensión con Naive Bayes

Desde esta carpeta, instalá la versión usada para el informe y ejecutá la
comparación sin abrir el simulador. En Windows podés usar `py -3` en lugar
de `python`.

```text
python -m pip install scikit-learn==1.7.2
python comparar_clasificadores.py
```

El script entrena con las 80 frases de `dataset.csv` y evalúa los dos enfoques
sobre los 25 casos de la cátedra y los 30 casos adicionales. El argumento
`--json` exporta el detalle de cada predicción.

El archivo de entrega usa reglas por defecto. Para probar el modelo entrenado
sobre los 25 casos de la cátedra, activalo desde la línea de comandos.

```text
python tp07_castro_toffoletto_buset_gantus.py --sin-robot --clasificador ml
```

En ambos modos se usan el mismo extractor, validador y ejecutor. El modo de
reglas funciona con la biblioteca estándar de Python.
