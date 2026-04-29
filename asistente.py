import random
from typing import TypedDict, List, Optional
from langgraph.graph import StateGraph, END
from datasets import load_dataset

# ============================================
# CARGAR DATASET REAL DE HUGGING FACE
# ============================================
print("⏳ Cargando dataset de Hugging Face...")

dataset = load_dataset(
    "openfoodfacts/product-database",
    split="food",
    streaming=True
)

productos_raw = []
count = 0
for item in dataset:
    if count >= 500:
        break
    lang = item.get("lang", "")
    if lang in ["es", "en", "fr"]:
        productos_raw.append(item)
        count += 1

print(f"✅ Dataset cargado: {len(productos_raw)} productos")

# ============================================
# CONSTRUIR CATÁLOGO CON CAMPOS OBLIGATORIOS
# ============================================
def construir_catalogo(productos_raw):
    catalogo = []
    for p in productos_raw:
        nutriments = p.get("nutriments", {})
        if not isinstance(nutriments, dict):
            nutriments = {}

        producto = {
            "code": str(p.get("code", "")),
            "brands": str(p.get("brands", "")),
            "brands_tags": p.get("brands_tags", []) if isinstance(p.get("brands_tags"), list) else [],
            "categories": str(p.get("categories", "")),
            "categories_tags": p.get("categories_tags", []) if isinstance(p.get("categories_tags"), list) else [],
            "ingredients_text": str(p.get("ingredients_text", "")),
            "traces": str(p.get("traces", "")),
            "traces_tags": p.get("traces_tags", []) if isinstance(p.get("traces_tags"), list) else [],
            "lang": str(p.get("lang", "")),
            "languages_tags": p.get("languages_tags", []) if isinstance(p.get("languages_tags"), list) else [],
            "nutriments": {
                "salt_value": nutriments.get("salt_value", ""),
                "salt_unit": nutriments.get("salt_unit", "g"),
                "fat_value": nutriments.get("fat_value", ""),
                "fat_unit": nutriments.get("fat_unit", "g"),
                "energy_value": nutriments.get("energy_value", ""),
                "energy_unit": nutriments.get("energy_unit", "kcal"),
                "proteins_value": nutriments.get("proteins_value", ""),
                "proteins_unit": nutriments.get("proteins_unit", "g"),
                "carbohydrates_value": nutriments.get("carbohydrates_value", ""),
                "carbohydrates_unit": nutriments.get("carbohydrates_unit", "g"),
            },
            "price": round(random.uniform(0.50, 50.00), 2)
        }
        catalogo.append(producto)
    return catalogo

catalogo = construir_catalogo(productos_raw)
print(f"✅ Catálogo construido: {len(catalogo)} productos con columna Price ($0.50 - $50.00)")

# ============================================
# PALABRAS RELACIONADAS
# ============================================
palabras_relacionadas = {
    "desayuno": ["cereal", "bread", "milk", "dairy", "oat"],
    "vegetariano": ["vegetable", "fruit", "cereal", "vegetal"],
    "almuerzo": ["meat", "fish", "vegetable", "chicken"],
    "leche": ["milk", "dairy"],
    "pan": ["bread"],
    "huevo": ["egg"],
    "avena": ["oat", "cereal"],
    "mantequilla": ["butter", "dairy"]
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
    """
    Recibe una búsqueda en texto libre del cliente
    y retorna los productos relevantes del catálogo.
    """
    query = query.lower()
    resultados = []

    for producto in catalogo:
        nombre = str(producto.get("brands", "")).lower()
        categoria = str(producto.get("categories", "")).lower()
        ingredientes = str(producto.get("ingredients_text", "")).lower()

        if query in nombre or query in categoria or query in ingredientes:
            if producto not in resultados:
                resultados.append(producto)

    for palabra, relacionadas in palabras_relacionadas.items():
        if palabra in query:
            for termino in relacionadas:
                for producto in catalogo:
                    nombre = str(producto.get("brands", "")).lower()
                    categoria = str(producto.get("categories", "")).lower()
                    if termino in nombre or termino in categoria:
                        if producto not in resultados:
                            resultados.append(producto)

    return resultados[:10]

def build_cart(product_codes: list, catalogo: list, budget: float = None) -> dict:
    """
    Arma un carrito con los productos indicados.
    Retorna un dict con items y total.
    """
    items = []
    total = 0

    for code in product_codes:
        for producto in catalogo:
            if producto["code"] == code:
                items.append({
                    "code": producto["code"],
                    "brands": producto["brands"],
                    "categories": producto["categories"],
                    "price": producto["price"]
                })
                total = round(total + producto["price"], 2)

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
# 2.3 MINI FLUJO SIMPLE
# ============================================
def mini_flujo(mensaje: str) -> str:
    """
    Función simple que recibe el mensaje del cliente,
    llama a search_products y retorna texto de respuesta.
    El punto 2.3 se implementó con esta función simple y
    adicionalmente se desarrolló un agente completo con
    LangGraph que extiende esta lógica con clasificación
    de intención, manejo de presupuesto y routing inteligente.
    """
    productos = search_products(mensaje, catalogo)
    if len(productos) == 0:
        return "Lo siento, no encontré productos relacionados. ¿Puedo ayudarte con algo más?"
    respuesta = "Encontré estos productos para ti:\n"
    for p in productos[:5]:
        marca = p['brands'] if p['brands'] else "Sin marca"
        categoria = p['categories'][:50] if p['categories'] else "Sin categoría"
        respuesta += f"- {marca} ({categoria}) a ${p['price']}\n"
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
        productos = [p for p in productos if p["price"] <= estado["presupuesto"]]
    return {"productos": productos}

def nodo_responder(estado: EstadoAgente) -> EstadoAgente:
    print("💬 Generando respuesta...")
    intencion = estado["intencion"]
    if intencion == "saludo":
        respuesta = "¡Hola! Soy el asistente de compras de Tipti 🛒 ¿En qué puedo ayudarte hoy?"
    elif intencion == "fuera_scope":
        respuesta = "Entiendo tu consulta, pero no tengo acceso a esa información. Te recomiendo contactar a nuestro equipo de soporte 😊"
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
            for p in productos[:5]:
                marca = p['brands'] if p['brands'] else "Sin marca"
                categoria = p['categories'][:50] if p['categories'] else "Sin categoría"
                respuesta += f"- {marca} ({categoria}) a ${p['price']}\n"
            respuesta += "¿Te agrego alguno al carrito? 😊"
    return {"respuesta": respuesta}

# ============================================
# CONSTRUIR AGENTE CON ROUTING
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

print("\n" + "=" * 50)
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
if len(catalogo) >= 3:
    codes = [catalogo[0]["code"], catalogo[1]["code"], catalogo[2]["code"]]
    carrito = build_cart(codes, catalogo, budget=10.0)
    print("Carrito:")
    for item in carrito["items"]:
        marca = item['brands'] if item['brands'] else "Sin marca"
        print(f"- {marca} - ${item['price']}")
    print(f"Total: ${carrito['total']}")
    print(carrito["alerta"])