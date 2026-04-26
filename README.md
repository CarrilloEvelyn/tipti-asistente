# 🛒 Asistente de Compras Inteligente — Tipti

Asistente conversacional de compras construido con Python y LangGraph con routing inteligente de intenciones.

## 🧠 Tecnologías utilizadas
- Python 3.14
- LangGraph — para el flujo del agente con routing
- Hugging Face — como fuente del catálogo de productos

## 🏗️ Arquitectura del Agente

Cliente escribe mensaje
        ↓
  [Nodo: Clasificar intención]
        ↓
  ¿Saludo o fuera de scope? → [Nodo: Responder]
  ¿Compra o presupuesto?   → [Nodo: Buscar] → [Nodo: Responder]

## 📦 Funciones principales

### search_products
Busca productos en el catálogo según texto libre del cliente con palabras relacionadas inteligentes.

### build_cart
Arma un carrito con productos por ID, calcula el total y avisa si se supera el presupuesto.

### mini_flujo — Punto 2.3
Función simple que recibe el mensaje del cliente, llama a search_products y retorna un texto de respuesta con los productos encontrados o un mensaje si no hay resultados.

> El punto 2.3 se implementó con la función simple mini_flujo() y adicionalmente se desarrolló un agente completo con LangGraph que extiende esta lógica con clasificación de intención, manejo de presupuesto y routing inteligente.

### Agente LangGraph con Routing
- 🧠 Nodo 1 — Clasifica la intención: saludo, compra, presupuesto, fuera de scope
- 🔍 Nodo 2 — Busca productos y filtra por presupuesto si aplica
- 💬 Nodo 3 — Genera respuesta personalizada según contexto

## 🚀 ¿Cómo ejecutarlo?

1. Clona el repositorio
2. Instala las dependencias:
python -m pip install -r requirements.txt
3. Ejecuta el asistente:
python asistente.py

## 📊 Catálogo
Basado en el dataset de Hugging Face openfoodfacts/product-database
Precios generados con valores aleatorios entre $0.50 y $50.00 USD.

## 👩‍💻 Autor
**Evelyn Carrillo**
Desarrollado como prueba técnica AI Developer.
Análisis y lógica de negocio: criterio propio de Ingeniería Industrial aplicada a eCommerce.
Implementación asistida con Claude (Anthropic) como herramienta de desarrollo.