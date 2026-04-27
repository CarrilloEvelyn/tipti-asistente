import random
from typing import TypedDict, List, Optional
from langgraph.graph import StateGraph, END

# ============================================
# CATALOGO DE PRODUCTOS
# ============================================
catalogo = [
    {"id": "P001", "nombre": "Leche entera 1L", "categoria": "Lacteos", "precio": round(random.uniform(0.50, 5.00), 2)},
    {"id": "P002", "nombre": "Pan integral 500g", "categoria": "Panaderia", "precio": round(random.uniform(0.50, 5.00), 2)},
    {"id": "P003", "nombre": "Huevos 12 unidades", "categoria": "Lacteos", "precio": round(random.uniform(1.00, 5.00), 2)},
    {"id": "P004", "nombre": "Avena instantanea 500g", "categoria": "Cereales", "precio": round(random.uniform(0.50, 4.00), 2)},
    {"id": "P005", "nombre": "Mantequilla 200g", "categoria": "Lacteos", "precio": round(random.uniform(1.00, 4.00), 2)}
]

# ============================================
# PALABRAS RELACIONADAS
# ============================================
palabras_relacionadas = {
    "desayuno": ["lacteos", "cereales", "panaderia"],
    "vegetariano": ["lacteos", "cereales", "panaderia"],
    "almuerzo": ["lacteos", "cereales"],
    "leche": ["leche"],
    "pan": ["pan"],
    "huevo": ["huevo"],
    "avena": ["avena"],
    "mantequilla": ["mantequilla"]
}

# ============================================
# ESTADO DEL AGENTE
# ============================================
class EstadoAgente(TypedDict):
    mensaje: str
    intencion: str
    productos: List[dict]
    presupuesto: Optional[float]
    respuesta: str

# ============================================
# FUNCIONES PRINCIPALES
# ============================================
def search_products(query: str, catalogo: list) -> list:
    query = query.lower()
    resultados = []
    for producto in catalogo:
        if query in producto["nombre"].lower() or query in producto["categoria"].lower():
            if producto not in resultados:
                resultados.append(producto)
    for palabra, relacionadas in palabras_relacionadas.items():
        if palabra in query:
            for termino in relacionadas:
                for producto in catalogo:
                    if termino in producto["nombre"].lower() or termino in producto["categoria"].lower():
                        if producto not in resultados:
                            resultados.append(producto)
    return resultados

def build_cart(product_ids: list, catalogo: list, budget: float = None) -> dict:
    items = []
    total = 0
    for pid in product_ids:
        for producto in catalogo:
            if producto["id"] == pid:
                items.append({
                    "id": producto["id"],
                    "nombre": producto["nombre"],
                    "precio": producto["precio"]
                })
                total = round(total + producto["precio"], 2)
    resultado = {"items": items, "total": total}
    if budget is not None:
        if total > budget:
            resultado["alerta"] = f"⚠️ Presupuesto superado! Total ${total} supera el límite de ${budget}"
        else:
            resultado["alerta"] = f"✅ Dentro del presupuesto! Te sobran ${round(budget - total, 2)}"
    return resultado

def extraer_presupuesto(mensaje: str) -> Optional[float]:
    if "$" in mensaje:
        try:
            parte = mensaje.split("$")[-1]
            numero = ""
            for c in parte:
                if c.isdigit() or c == ".":
                    numero += c
                else:
                    break
            if numero:
                return float(numero)
        except:
            pass
    return None

# ============================================
# 2.3 MINI FLUJO SIMPLE (requerimiento base)
# ============================================
def mini_flujo(mensaje: str) -> str:
    """
    Función simple que recibe el mensaje del cliente,
    llama a search_products y retorna texto de respuesta.
    """
    productos = search_products(mensaje, catalogo)
    if len(productos) == 0:
        return "Lo siento, no encontré productos relacionados. ¿Puedo ayudarte con algo más?"
    respuesta = "Encontré estos productos para ti:\n"
    for p in productos:
        respuesta += f"- {p['nombre']} a ${p['precio']}\n"
    return respuesta

# ============================================
# NODOS DEL AGENTE LANGGRAPH
# ============================================
def nodo_clasificar(estado: EstadoAgente) -> EstadoAgente:
    print("🧠 Clasificando intención...")
    mensaje = estado["mensaje"].lower()
    saludos = ["hola", "buenos", "buenas", "hey", "hi", "buen dia"]
    fuera_scope = ["pedido", "envio", "devolucion", "reembolso", "cuando llega"]
    if any(s in mensaje for s in saludos):
        intencion = "saludo"
    elif any(f in mensaje for f in fuera_scope):
        intencion = "fuera_scope"
    elif "$" in mensaje or "presupuesto" in mensaje:
        intencion = "presupuesto"
    else:
        intencion = "compra"
    presupuesto = extraer_presupuesto(estado["mensaje"])
    return {"intencion": intencion, "presupuesto": presupuesto}

def nodo_buscar(estado: EstadoAgente) -> EstadoAgente:
    print("🔍 Buscando productos...")
    productos = search_products(estado["mensaje"], catalogo)
    if estado.get("presupuesto"):
        productos = [p for p in productos if p["precio"] <= estado["presupuesto"]]
    return {"productos": productos}

def nodo_responder(estado: EstadoAgente) -> EstadoAgente:
    print("💬 Generando respuesta...")
    intencion = estado["intencion"]
    if intencion == "saludo":
        respuesta = "¡Hola! Soy el asistente de compras de Tipti 🛒 ¿En qué puedo ayudarte hoy?"
    elif intencion == "fuera_scope":
        respuesta = "Entiendo tu consulta, pero no tengo acceso a esa información. Te recomiendo contactar a nuestro equipo de soporte para ayudarte mejor 😊"
    elif intencion in ["compra", "presupuesto"]:
        productos = estado["productos"]
        presupuesto = estado.get("presupuesto")
        if len(productos) == 0:
            respuesta = "Lo siento, no encontré productos relacionados. ¿Puedo ayudarte con algo más? 😊"
        else:
            if presupuesto:
                respuesta = f"¡Perfecto! Con tu presupuesto de ${presupuesto}, encontré estas opciones:\n"
            else:
                respuesta = "¡Hola! Encontré estos productos para ti:\n"
            for p in productos:
                respuesta += f"- {p['nombre']} a ${p['precio']}\n"
            respuesta += "¿Te agrego alguno al carrito? 😊"
    return {"respuesta": respuesta}

# ============================================
# CONSTRUIR EL AGENTE CON ROUTING
# ============================================
def crear_agente():
    grafo = StateGraph(EstadoAgente)
    grafo.add_node("clasificar", nodo_clasificar)
    grafo.add_node("buscar", nodo_buscar)
    grafo.add_node("responder", nodo_responder)
    grafo.set_entry_point("clasificar")
    def routing(estado):
        if estado["intencion"] in ["saludo", "fuera_scope"]:
            return "responder"
        return "buscar"
    grafo.add_conditional_edges("clasificar", routing)
    grafo.add_edge("buscar", "responder")
    grafo.add_edge("responder", END)
    return grafo.compile()

# ============================================
# PRUEBAS
# ============================================
agente = crear_agente()
estado_inicial = {"mensaje": "", "intencion": "", "productos": [], "presupuesto": None, "respuesta": ""}

print("=" * 50)
print("PRUEBA 2.3 — Mini flujo simple")
print("=" * 50)
mensaje_prueba = "Quiero algo vegetariano para el almuerzo, tengo $15"
print(f"Cliente: {mensaje_prueba}")
print(f"Asistente: {mini_flujo(mensaje_prueba)}")

print("=" * 50)
print("PRUEBA 1 — Saludo")
print("=" * 50)
r = agente.invoke({**estado_inicial, "mensaje": "Hola!"})
print(f"Cliente: Hola!")
print(f"Asistente: {r['respuesta']}")

print("=" * 50)
print("PRUEBA 2 — Búsqueda con presupuesto")
print("=" * 50)
r = agente.invoke({**estado_inicial, "mensaje": "Quiero algo vegetariano para el almuerzo, tengo $15"})
print(f"Cliente: Quiero algo vegetariano para el almuerzo, tengo $15")
print(f"Asistente: {r['respuesta']}")

print("=" * 50)
print("PRUEBA 3 — Fuera de scope")
print("=" * 50)
r = agente.invoke({**estado_inicial, "mensaje": "¿Cuándo llega mi pedido?"})
print(f"Cliente: ¿Cuándo llega mi pedido?")
print(f"Asistente: {r['respuesta']}")

print("=" * 50)
print("PRUEBA 4 — Carrito con presupuesto")
print("=" * 50)
carrito = build_cart(["P001", "P002", "P003"], catalogo, budget=10.0)
print("Carrito:")
for item in carrito["items"]:
    print(f"- {item['nombre']} - ${item['precio']}")
print(f"Total: ${carrito['total']}")
print(carrito["alerta"])
