# =====================================================================
#  TP07 - Inteligencia Artificial
#  Agente que interpreta comandos en lenguaje natural
#
#  ESTE ES EL ARCHIVO DONDE ESCRIBIS TU PROGRAMA.
#
#  Antes de ejecutarlo:
#    1. Abri INICIAR_SIMULADOR (elegi G1 o Go2)
#    2. Espera a que aparezca la ventana con el robot
#    3. Recien ahi ejecuta este archivo
#
#  Integrantes: Martina Morena Castro, Martina Ornella Toffoletto,
#               Agustin Buset y Elias Gantus
# =====================================================================

import math
import re
import unicodedata

from robot import Robot

from ejecutor import Ejecutor
from evaluar import evaluar

ALUMNO = "Martina Morena Castro, Martina Ornella Toffoletto, Agustin Buset y Elias Gantus"

# El ejecutor recibe una intención por vez. El validador conserva el texto entero.
_SEPARADOR_ORDENES = re.compile(r";|\by\s+(?:despues|luego)\b")
_PREFIJO_ORDEN = re.compile(r"^(?:(?:por favor|robot)[,\s]+)+")
_PATRON_PARADA = re.compile(
    r"^(?:deten(?:te|ete|er)|para(?:te)?(?!\s+(?:adelante|atras)\b)|"
    r"frena|stop|quiet[oa]|no\s+(?:avances|sigas|te\s+muevas))\b"
)
_PATRON_SALUDO = re.compile(
    r"^(?:salud[ao]|(?:hace|haz|da)\s+un\s+saludo)\b|^hola[.!?]*$"
)
_INICIO_MOVIMIENTO = {
    "GIRAR": re.compile(
        r"^(?:gira(?:te)?|rota|voltea|(?:da(?:le|te)?\s+)?(?:una|media)\s+vuelta)\b"
    ),
    "MOVER": re.compile(
        r"^(?:avanza|avanzar|muevete|movete|camina|retroced[ea]|anda|"
        r"(?:dale\s+para\s+)?(?:adelante|atras))\b"
    ),
}


def _normalizar(texto):
    texto = unicodedata.normalize("NFD", texto.casefold().replace("−", "-"))
    return "".join(caracter for caracter in texto if not unicodedata.combining(caracter))


def _primera_orden(texto_normalizado):
    orden = _SEPARADOR_ORDENES.split(texto_normalizado, maxsplit=1)[0].strip()
    return _PREFIJO_ORDEN.sub("", orden.lstrip("¡¿ "))


class ClasificadorIntencion:
    """Identifica la intención en la primera orden, sin extraer medidas."""

    TIPOS = ("MOVER", "GIRAR", "DETENERSE", "SALUDO",
             "CONSULTAR_ESTADO", "DESCONOCIDO")

    _PATRONES = {
        "DETENERSE": _PATRON_PARADA,
        **_INICIO_MOVIMIENTO,
        "SALUDO": _PATRON_SALUDO,
        "CONSULTAR_ESTADO": r"\b(?:bateria|estado)\b|^como estas[.!?]*$",
    }

    def __init__(self, modelo=None):
        self.modelo = modelo

    def clasificar(self, texto):
        orden = _primera_orden(_normalizar(texto))
        if self.modelo is not None:
            return str(self.modelo.predict([orden])[0])

        for tipo, patron in self._PATRONES.items():
            if re.search(patron, orden):
                return tipo
        return "DESCONOCIDO"


class ExtractorParametros:
    """Extrae medidas y direcciones sin decidir si son seguras."""

    _NUMEROS_EN_PALABRAS = {"cero": 0, "un": 1, "uno": 1, "una": 1,
                           "dos": 2, "tres": 3, "cuatro": 4, "cinco": 5}
    _NUMERO = (
        r"(?<![\w.,+\-])(?P<numero>"
        r"[+-]?(?:[0-9]+(?:[.,][0-9]+)?|[.,][0-9]+)(?:e[+-]?[0-9]+)?|"
        r"(?:" + "|".join(_NUMEROS_EN_PALABRAS) + r")(?=\s))"
    )
    _UNIDADES = {
        "velocidad_ms": r"m\s*/\s*s\b|metros?\s+por\s+segundos?\b",
        "velocidad_giro": r"rad\s*/\s*s\b|radianes?\s+por\s+segundos?\b",
        "distancia_m": r"(?:m|metros?)\b(?!\s*(?:/|por\b))",
        "angulo_deg": r"grados?\b|°",
    }
    _MEDIDAS = re.compile(r"(?:\b(?:a|de)\s+)?" + _NUMERO + r"\s*(?:" + "|".join(
        f"(?P<{campo}>{unidad})" for campo, unidad in _UNIDADES.items()
    ) + ")")
    _DIRECCIONES = {
        "atras": r"\b(?:(?:para|hacia)\s+)?atras\b",
        "adelante": r"\b(?:(?:para|hacia)\s+)?adelante\b",
        "derecha": r"\b(?:(?:a|hacia|para)\s+la\s+)?derecha\b",
        "izquierda": r"\b(?:(?:a|hacia|para)\s+la\s+)?izquierda\b",
    }
    _DISTANCIAS = {"un poco": 0.5, "bastante": 2.0}
    _ANGULOS = {"media vuelta": 180, "una vuelta": 360}
    _DESPACIO = re.compile(r"\b(?:despacio|lent[oa](?:mente)?)\b")
    _RAPIDO = re.compile(r"\b(?:(?:muy|mas|demasiado)\s+)?(?:rapido|veloz)\b")

    def __init__(self, perfil=None):
        self.perfil = perfil if perfil is not None else _perfil_por_defecto()

    def extraer(self, texto, tipo):
        if tipo not in _INICIO_MOVIMIENTO:
            return {}

        orden = _primera_orden(_normalizar(texto))
        parametros = {}
        for medida in self._MEDIDAS.finditer(orden):
            campo = medida.lastgroup
            if campo in parametros:
                return {"ambiguedad": "Hay más de un valor para la misma medida."}
            numero = medida.group("numero")
            if numero in self._NUMEROS_EN_PALABRAS:
                parametros[campo] = self._NUMEROS_EN_PALABRAS[numero]
            else:
                parametros[campo] = float(numero.replace(",", "."))

        resto = _INICIO_MOVIMIENTO[tipo].sub("", self._MEDIDAS.sub("", orden), count=1)
        direcciones = {direccion for direccion, patron in self._DIRECCIONES.items()
                       if re.search(patron, orden)}
        if re.match(r"retroced[ea]\b", orden):
            direcciones.add("atras")
        if len(direcciones) > 1:
            return {"ambiguedad": "Indicá una sola dirección."}
        if direcciones:
            parametros["direccion"] = direcciones.pop()
        for patron in self._DIRECCIONES.values():
            resto = re.sub(patron, "", resto)

        if tipo == "MOVER":
            campo_medida, aproximaciones = "distancia_m", self._DISTANCIAS
            campo_velocidad, velocidad_max = "velocidad_ms", self.perfil.velocidad_max
        else:
            campo_medida, aproximaciones = "angulo_deg", self._ANGULOS
            campo_velocidad, velocidad_max = "velocidad_giro", self.perfil.velocidad_angular_max

        for expresion, valor in aproximaciones.items():
            patron = rf"\b{expresion}\b"
            if re.search(patron, orden):
                if parametros.setdefault(campo_medida, valor) != valor:
                    return {"ambiguedad": "Hay medidas contradictorias."}
                resto = re.sub(patron, "", resto)

        despacio = self._DESPACIO.search(orden)
        rapido = self._RAPIDO.search(orden)
        if despacio and rapido:
            return {"ambiguedad": "Indicá una sola velocidad."}
        if despacio or rapido:
            parametros.setdefault(campo_velocidad, velocidad_max / 2 if despacio else velocidad_max)
            resto = self._RAPIDO.sub("", self._DESPACIO.sub("", resto))

        resto = re.sub(r"\bpor favor\b", "", resto)
        if resto.strip(" \t\r\n.,!?¡¿"):
            return {"ambiguedad": "No pude interpretar parte del movimiento. Revisá las medidas y la dirección."}

        return parametros


class ValidadorSeguridad:
    """Revisa el texto original y las medidas antes de invocar al ejecutor."""

    DIST_MAX_M = 5.0
    VEL_MAX_MS = 0.5
    ANG_MAX_DEG = 180
    # El ejecutor prepara todos los tramos antes de mover. Acotamos ese trabajo.
    MAX_TRAMOS = 100

    _ACCION_PELIGROSA = re.compile(
        r"\b(?:salt(?:a|ar|e|es|o)|brinc(?:a|ar|e|es)|cae(?:r|te)?|fuerza|romp(?:e|er|as)|"
        r"empuj(?:a|ar|e|es)|golpe(?:a|ar|e|es)|corr(?:e|er|as)|sprint|"
        r"tir(?:a|ar)|pate(?:a|ar))\b"
    )
    _SALUDOS_ALTERNATIVOS = re.compile(
        r"^(?:levanta\s+(?:la|una)\s+mano\s+para\s+saludar|"
        r"da(?:le)?\s+la\s+bienvenida)\b|^hola\s+robot[.!?]*$"
    )

    def __init__(self, perfil):
        self.perfil = perfil

    def validar(self, texto, tipo, parametros):
        original = _normalizar(texto)
        peligro = self._ACCION_PELIGROSA.search(original)
        if peligro:
            return False, f"La acción '{peligro.group()}' está bloqueada por seguridad."

        orden = _primera_orden(original)
        for tipo_movimiento, patron in _INICIO_MOVIMIENTO.items():
            if patron.match(orden) and tipo != tipo_movimiento:
                return False, "La intención inferida no coincide con el movimiento escrito."
        if tipo == "SALUDO":
            directo = _PATRON_SALUDO.match(orden) or self._SALUDOS_ALTERNATIVOS.match(orden)
            condicionado = re.search(r"\b(?:no|nunca|si|cuando|hasta|antes|despues|luego)\b", orden)
            if not directo or condicionado:
                return False, "Indicá un saludo directo para poder ejecutarlo."
        if tipo not in _INICIO_MOVIMIENTO:
            return True, ""

        if "ambiguedad" in parametros:
            return False, parametros["ambiguedad"]

        if re.search(r"\b(?:muy|mas|demasiado)\s+(?:rapido|veloz)\b", orden):
            return False, "Reformulá el movimiento con una velocidad dentro del límite del TP."

        if tipo == "MOVER":
            direcciones = ("adelante", "atras")
            limites = (
                ("distancia_m", "distancia", self.DIST_MAX_M, "m"),
                ("velocidad_ms", "velocidad", min(self.VEL_MAX_MS, self.perfil.velocidad_max), "m/s"),
            )
        else:
            direcciones = ("izquierda", "derecha")
            limites = (
                ("angulo_deg", "ángulo", self.ANG_MAX_DEG, "grados"),
                ("velocidad_giro", "velocidad de giro", self.perfil.velocidad_angular_max, "rad/s"),
            )

        if parametros.get("direccion", direcciones[0]) not in direcciones:
            return False, "Esa dirección no corresponde al movimiento pedido."
        campos_validos = {"direccion"} | {campo for campo, _, _, _ in limites}
        if parametros.keys() - campos_validos:
            return False, "Hay medidas que no corresponden al movimiento pedido."

        for campo, nombre, tope, unidad in limites:
            if campo in parametros:
                valor = parametros[campo]
                if not isinstance(valor, (int, float)) or not 0 < valor <= tope:
                    return False, f"El valor de {nombre} debe ser mayor que 0 y hasta {tope:g} {unidad}."

        if tipo == "MOVER":
            distancia = parametros.get("distancia_m", 0.5)
            velocidad = parametros.get("velocidad_ms", self.perfil.velocidad_max)
        else:
            distancia = math.radians(parametros.get("angulo_deg", 90))
            velocidad = parametros.get("velocidad_giro", self.perfil.velocidad_angular_max)

        if distancia > self.MAX_TRAMOS * self.perfil.duracion_max * velocidad:
            return False, "El movimiento requeriría demasiados tramos a esa velocidad."
        return True, ""


class AgenteRobot:
    """Encadena las etapas y registra las órdenes aceptadas."""

    def __init__(self, robot=None, *, clasificador=None):
        self.robot = robot
        perfil = robot.perfil if robot is not None else _perfil_por_defecto()
        self.clasificador = clasificador if clasificador is not None else ClasificadorIntencion()
        self.extractor = ExtractorParametros(perfil)
        self.validador = ValidadorSeguridad(perfil)
        self.ejecutor = Ejecutor(robot) if robot is not None else None
        self.historial = []

    def procesar(self, texto):
        """Devuelve la decisión y, con simulador conectado, ejecuta las órdenes válidas."""
        ordenes = _SEPARADOR_ORDENES.split(_normalizar(texto))
        # Una parada explícita tiene prioridad sobre la predicción estadística.
        parada = next((orden for orden in ordenes if _PATRON_PARADA.match(_primera_orden(orden))), None)
        if parada is not None:
            tipo = "DETENERSE"
            texto_validado = parada
            siguientes = ()
        else:
            tipo = self.clasificador.clasificar(texto)
            texto_validado = texto
            siguientes = ordenes[1:]

        parametros = self.extractor.extraer(texto_validado, tipo)
        valido, mensaje = self.validador.validar(texto_validado, tipo, parametros)
        if valido and tipo != "DESCONOCIDO":
            for orden in siguientes:
                tipo_siguiente = self.clasificador.clasificar(orden)
                if tipo_siguiente == "DESCONOCIDO":
                    valido, mensaje = False, "No pude interpretar una de las órdenes de la secuencia."
                    break
                parametros_siguientes = self.extractor.extraer(orden, tipo_siguiente)
                valido, mensaje = self.validador.validar(orden, tipo_siguiente, parametros_siguientes)
                if not valido:
                    break

        ejecutar = valido and tipo != "DESCONOCIDO"
        if ejecutar:
            if self.ejecutor is None:
                mensaje = "Orden aceptada para ejecución."
            else:
                mensaje = self.ejecutor.ejecutar(tipo, parametros)
                if mensaje.startswith("RECHAZADO POR EL ROBOT:"):
                    ejecutar = valido = False
            if ejecutar and len(ordenes) > 1:
                if parada is not None:
                    mensaje += " La parada tuvo prioridad sobre el resto de la secuencia."
                else:
                    mensaje += " Se tomó solo la primera orden."
        elif valido:
            mensaje = "No entendí la orden. Probá con avanzar, girar, parar, saludar o consultar el estado."

        resultado = {
            "tipo": tipo,
            "parametros": parametros,
            "ejecutar": ejecutar,
            "bloqueado": not valido,
            "confianza": 0.9 if tipo != "DESCONOCIDO" else 0.0,
            "texto_original": texto,
            "mensaje": mensaje,
        }
        if ejecutar:
            self.historial.append(resultado)
        return resultado


def _perfil_por_defecto():
    """Permite evaluar el agente sin abrir el simulador."""
    import sys
    from pathlib import Path
    entorno = Path(__file__).resolve().parent.parent / "entorno"
    if str(entorno) not in sys.path:
        sys.path.insert(0, str(entorno))
    from sim.safety import perfil
    return perfil("tp07")


# =====================================================================
#  PROGRAMA PRINCIPAL - no hace falta que lo toques
# =====================================================================
def main():
    import argparse

    parser = argparse.ArgumentParser(description="Agente para el Unitree G1 simulado.")
    parser.add_argument("--sin-robot", action="store_true", help="evalúa sin abrir el simulador")
    parser.add_argument("--clasificador", choices=("reglas", "ml"), default="reglas")
    args = parser.parse_args()

    modelo = None
    if args.clasificador == "ml":
        from entrenar import entrenar_desde_csv, hay_sklearn

        if not hay_sklearn():
            parser.error("Instalá la dependencia con python -m pip install scikit-learn==1.7.2.")
        modelo = entrenar_desde_csv()

    robot = None
    if not args.sin_robot:
        robot = Robot()
        robot.conectar()

    try:
        print(f"\n  Integrantes: {ALUMNO}\n  Clasificador: {args.clasificador}")
        agente = AgenteRobot(robot, clasificador=ClasificadorIntencion(modelo))
        evaluar(agente)

        if robot is not None:
            print("\n  Escribi ordenes para el robot. Enter vacio para salir.")
            while True:
                try:
                    texto = input("\n  > ").strip()
                except (EOFError, KeyboardInterrupt):
                    break
                if not texto:
                    break
                r = agente.procesar(texto)
                print(f"    {r['tipo']}  {r.get('mensaje', '')}")
    finally:
        if robot is not None:
            robot.detenerse()
            robot.desconectar()


if __name__ == "__main__":
    main()
