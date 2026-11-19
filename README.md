# TP07 · Agente de comandos para Unitree G1

Trabajo práctico de Inteligencia Artificial de la UADE. El agente interpreta órdenes en castellano, extrae sus parámetros, valida la seguridad y ejecuta las acciones permitidas en el simulador.

**Integrantes** · Martina Morena Castro, Martina Ornella Toffoletto, Agustin Buset y Elias Gantus.

## Entregables

- [Código de entrega](mi_desarrollo/tp07_castro_toffoletto_buset_gantus.py)
- [Reporte de accuracy y comparación con scikit-learn](entrega_tp07/reporte_accuracy_tp07.pdf)
- [Análisis de fallos](entrega_tp07/analisis_de_fallos_tp07.pdf)
- [Informe técnico](entrega_tp07/informe_tecnico_tp07.pdf)
- [ZIP de entrega](entrega_tp07/TP07_Castro_Toffoletto_Buset_Gantus.zip)

## Ejecutar las pruebas

Desde la carpeta del repositorio, ejecutá el modo basado en reglas con Python 3.10 o superior.

```powershell
python mi_desarrollo/tp07_castro_toffoletto_buset_gantus.py --sin-robot
```

Para reproducir la comparación con Naive Bayes, instalá la versión usada en el informe y ejecutá el comparador.

```powershell
python -m pip install scikit-learn==1.7.2
python mi_desarrollo/comparar_clasificadores.py
```

Para probar el G1 simulado, seguí [INSTALACION.md](INSTALACION.md). El entorno del laboratorio proviene de [UadeRobotLab](https://github.com/tsamaan/UadeRobotLab).
