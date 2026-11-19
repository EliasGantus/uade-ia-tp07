# TP07 – Agente de comandos para el Unitree G1

**UADE – 3.4.096 Inteligencia Artificial**
Docente: Parkinson, Christian

## Integrantes

- Buset, Agustín
- Castro, Martina Morena
- Gantus, Elías
- Toffoletto, Martina Ornella

## El problema

Un agente inteligente recibe una orden en castellano ("avanzá 2 metros", "girá 90 grados a la derecha", "salta desde la mesa") y decide qué hacer: ejecutarla en el robot Unitree G1 simulado o rechazarla con un motivo. Tiene que clasificar la intención, extraer los parámetros, validar la seguridad y ejecutar (ver `consigna/`).

## Requisitos

- Python 3.10 o superior.
- Modo sin robot: no hace falta instalar nada, solo se usa la biblioteca estándar.
- Extensión con Naive Bayes: `pip install scikit-learn==1.7.2`.
- Simulador del robot: `pip install mujoco`. En Windows, si `import mujoco` falla, instalar el [Visual C++ Redistributable](https://aka.ms/vs/17/release/vc_redist.x64.exe). Sin placa de video compatible con OpenGL, el simulador funciona igual en modo consola.

El entorno del simulador (carpeta `entorno/`) viene de [UadeRobotLab](https://github.com/tsamaan/UadeRobotLab) e incluye los modelos del G1.

## Cómo correrlo

Desde la carpeta del proyecto:

```bash
# Agente con reglas, sin simulador: evalúa los 25 casos de la cátedra
python mi_desarrollo/tp07_castro_toffoletto_buset_gantus.py --sin-robot

# Agente con Naive Bayes
python mi_desarrollo/tp07_castro_toffoletto_buset_gantus.py --sin-robot --clasificador ml

# Comparación de reglas contra Naive Bayes (25 casos de la cátedra y 30 adicionales)
cd mi_desarrollo && python comparar_clasificadores.py
```

### Con el robot simulado

```bash
# 1. Abrir el simulador y elegir el robot (G1)
./mi_desarrollo/scripts/INICIAR_SIMULADOR.sh          # Linux / macOS
mi_desarrollo\scripts\INICIAR_SIMULADOR.bat           # Windows

# 2. En otra terminal, ejecutar el agente: evalúa los casos y luego acepta órdenes escritas
./mi_desarrollo/scripts/EJECUTAR_MI_CODIGO.sh         # Linux / macOS
mi_desarrollo\scripts\EJECUTAR_MI_CODIGO.bat          # Windows
```

Para comprobar que el entorno está listo: `cd entorno && python -m sim --solo-revisar`.

### Ejemplo de salida

```
  ACCURACY: 25/25 = 100.0 %   APRUEBA (>= 70 %)
  PELIGROSOS BLOQUEADOS: 3/3   BIEN
```

## Estructura del proyecto

| Archivo | Contenido |
|---|---|
| `mi_desarrollo/tp07_castro_toffoletto_buset_gantus.py` | **Lo implementado:** clasificador, extractor, validador y agente (`mi_tp07.py` es la misma copia) |
| `mi_desarrollo/entrenar.py`, `comparar_clasificadores.py` | Extensión: Naive Bayes y comparación con las reglas |
| `mi_desarrollo/dataset.csv`, `casos_prueba.json`, `casos_adicionales.json` | 80 frases de entrenamiento, 25 casos de la cátedra y 30 casos adicionales |
| `mi_desarrollo/ejecutor.py`, `evaluar.py`, `robot.py` | Provistos por la cátedra |
| `entrega_tp07/` | Lo que se entrega: reporte de accuracy, análisis de fallos, informe técnico y ZIP |
| `mi_desarrollo/scripts/` | Scripts para abrir el simulador y ejecutar el agente |
| `mi_desarrollo/docs/` | `INSTALACION.md` (instalación completa del simulador) y `LEEME.md` (guía de la carpeta de trabajo) |
| `entorno/` | Simulador del robot, provisto por la cátedra |
| `consigna/` | Enunciado del TP (PDF) |

## Resumen de la solución

| Etapa | Decisión |
|---|---|
| 1. Clasificador de intención | Reglas con expresiones regulares (MOVER, GIRAR, DETENERSE, SALUDO, CONSULTAR_ESTADO, DESCONOCIDO). Como extensión, Naive Bayes entrenado con 80 frases |
| 2. Extractor de parámetros | Distancia, ángulo, velocidad y dirección con expresiones regulares. "un poco" vale 0,5 m y "bastante" 2 m |
| 3. Validador de seguridad | Clase independiente que revisa el texto original: bloquea acciones peligrosas y valores fuera de los límites (5 m, 180° y la velocidad del perfil del simulador) |
| 4. Ejecutor | Convierte distancia o ángulo en velocidad y tiempo, y lo envía al robot. Una parada explícita tiene prioridad sobre el resto |

## Resultados

| Prueba | Reglas | Naive Bayes |
|---|---|---|
| 25 casos de la cátedra | 100,0 % | 84,0 % |
| 30 casos adicionales | 76,7 % | 86,7 % |

Con las reglas se bloquean los 3 casos peligrosos de la cátedra (3/3). El detalle está en `entrega_tp07/`: `reporte_accuracy_tp07.pdf`, `analisis_de_fallos_tp07.pdf` e `informe_tecnico_tp07.pdf`.
