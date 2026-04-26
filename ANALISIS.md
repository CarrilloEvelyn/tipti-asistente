# 📊 Análisis y Evaluación — Asistente de Compras Tipti

> Análisis abordado desde **Ingeniería Industrial aplicada al ecommerce**, con tres ejes: optimización de procesos, calidad de servicio y experiencia del cliente.

---

## 🗣️ Parte 1 — Análisis de Conversaciones

### C1 — Validaciones del carrito

Antes de confirmar la adición al carrito, el asistente debe ejecutar una cadena de validaciones en tiempo real:

| # | Validación | Descripción |
|---|-----------|-------------|
| 1 | **Stock con reserva inteligente** | Descontar unidades en *soft reserve* (carritos activos no pagados últimos 30 min) para prevenir sobreventas |
| 2 | **Integridad de precio con timestamp** | Confirmar precio vigente en PIM — los precios cambian dinámicamente por promociones o algoritmos de pricing |
| 3 | **Especificación de variante obligatoria** | No asumir marca/volumen/gramaje — asumir genera devoluciones y afecta el NPS |
| 4 | **Vigencia y trazabilidad del lote** | Validar fecha de vencimiento, especialmente en perecederos |
| 5 | **Límite de compra por cliente** | Verificar política de cantidad máxima para evitar acaparamiento |

---

### C2 — Alternativas sin stock

La decisión de ofrecer alternativas fue acertada — un cliente sin opciones es un cliente perdido.

Sin embargo, la lógica de sustitución presenta una falla de criterio. El sistema debe seguir una **jerarquía de sustitución estricta:**

| Nivel | Criterio | Ejemplo |
|-------|---------|---------|
| 1 | Sustitución exacta | Tomates cherry 500g si no hay 250g |
| 2 | Equivalente funcional | Tomate pera, tomate normal |
| 3 | Misma subcategoría | Pepino, lechuga |
| 4 | Categoría general | Otro vegetal fresco |

> ⚠️ La **espinaca** apenas califica en Nivel 3. La **manzana** no supera ningún nivel — es fruta, no sustituto de tomate.

En producción esto se resuelve con un **motor de similitud semántica** entrenado con el catálogo.

---

### C3 — Fuera de scope

El asistente rechazó correctamente. Los 3 tipos de pregunta adicionales que debe declinar:

| # | Tipo | Ejemplo | Razón |
|---|------|---------|-------|
| 1 | Devoluciones y reembolsos | *"¿Puedo devolver este producto?"* | Corresponde a Customer Success con acceso a Zendesk/Salesforce |
| 2 | Datos de terceros | *"¿Puedo ver el pedido de otra persona?"* | Viola GDPR/LGPD — riesgo legal directo |
| 3 | Consultas médicas | *"¿Puedo comer esto si soy diabético?"* | Riesgo legal — jamás emitir recomendaciones médicas |

---

### C4 — Gestión de presupuesto

El asistente debe seguir este protocolo:

| Paso | Acción |
|------|--------|
| 1 | **Solicitar especificación** — preguntar presentación antes de calcular |
| 2 | **Calcular impacto real** — margen disponible = $8 - $6.15 = **$1.85** |
| 3 | **Informar con desglose exacto** — *"Agregar 6 huevos llevaría tu total a $8.65"* |
| 4 | **Proponer opciones** — reducir cantidad, sustituir producto más económico, optimizar carrito |
| 5 | **Respetar autonomía del cliente** — informar y proponer, nunca decidir |

> 💡 Principio de **cart optimization en tiempo real** — impacta en reducción de abandono, aumento de ticket promedio y mejora del NPS.

---

## ⚙️ Parte 1.2 — Diseño del comportamiento

### e. Reglas básicas

| # | Regla | Descripción |
|---|-------|-------------|
| 1 | **Identidad y contexto de sesión** | Presentarse siempre y mantener contexto de toda la conversación |
| 2 | **Catálogo como única fuente de verdad** | Cero tolerancia a productos inexistentes — validación automática obligatoria |
| 3 | **Comunicación empática y adaptativa** | Tono positivo, sin tecnicismos, adaptado al perfil del cliente |
| 4 | **Gestión de errores con redirección** | Nunca dejar al cliente sin salida — redirigir al canal correcto |
| 5 | **Cierre con valor medible** | Resumen del carrito + invitación abierta al finalizar |

---

### f. Métricas de producción

| Métrica | Qué mide | Valor aceptable |
|---------|---------|----------------|
| **Task Success Rate (TSR)** | Sesiones donde el usuario completó su objetivo sin fricción | ≥ 80% |
| **Assisted Revenue per Session (ARPS)** | Ingreso promedio generado por sesión asistida | $3 – $8 por sesión |
| **Customer Effort Score (CES)** | Qué tan fácil fue completar la tarea (escala 1-5) | ≥ 4.3 / 5 |

---

### g. Fallo crítico — 20% productos inexistentes

**Causa raíz:** Alucinación de modelo — el LLM responde de memoria sin consultar el catálogo real. Ausencia de capa **RAG (Retrieval Augmented Generation)**.

**Plan de resolución:**

| Plazo | Acción |
|-------|--------|
| 🔴 Inmediato | Capa de validación obligatoria antes de enviar cualquier recomendación |
| 🟡 Corto plazo | Reforzar prompt + implementar RAG |
| 🟢 Mediano plazo | Monitoreo automático con alertas si precisión baja del 98% |
| 🔵 Largo plazo | Ciclo **PDCA** de mejora continua aplicado al asistente |

---

## 🧪 Parte 3 — Evaluación del asistente

### 3.1 Casos de prueba

| # | Tipo | Mensaje del cliente | Respuesta esperada | Cómo verificarías |
|---|------|--------------------|--------------------|-------------------|
| 1 | Happy path | ¿Tienen avena? | Menciona 'Avena instantánea 500g' con precio | Nombre y precio coincidan con catálogo |
| 2 | Sin stock | Quiero tomates cherry | No menciona el producto, ofrece alternativa vegetal | Producto requerido no aparece en respuesta |
| 3 | Pregunta ambigua | Quiero algo rico para el desayuno | Pide clarificación o sugiere categorías reales | No asume ni inventa productos |
| 4 | Presentaciones distintas | ¿Tienen leche? | Muestra todas las presentaciones disponibles | Todas las variantes existen en catálogo |
| 5 | Presupuesto muy bajo | Quiero desayuno con $1 | Informa honestamente que no alcanza | No inventa productos baratos inexistentes |
| 6 | Otro idioma | I want to buy some milk please | Responde en inglés con productos disponibles | Detectó idioma y productos existen |

---

### 3.2 Criterio de aprobación

**¿Cuándo está listo?** → Mínimo **90% de casos aprobados** antes de producción.

**Respuesta correcta para "¿Tienen salmón?":**

| ✅ Correcto | ❌ Incorrecto |
|------------|--------------|
| Busca en catálogo real antes de responder | Recomienda salmón con precio inventado |
| Si existe: nombre exacto + precio vigente | Dice que no hay sin haber buscado |
| Si no existe: informa honestamente | Sugiere alternativas que tampoco existen |
| Ofrece alternativas reales de la misma categoría | No ofrece alternativa cuando sí las hay |

---

*Desarrollado por **Evelyn Carrillo** — Prueba técnica AI Developer*
*Análisis desde perspectiva de Ingeniería Industrial aplicada a eCommerce*