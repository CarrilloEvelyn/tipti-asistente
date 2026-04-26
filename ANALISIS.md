# 📊 Análisis y Evaluación — Asistente de Compras Tipti

> Análisis abordado desde **Ingeniería Industrial aplicada al ecommerce**, con tres ejes: optimización de procesos, calidad de servicio y experiencia del cliente. El criterio no fue solo si el asistente respondió bien, sino si cada interacción preserva la credibilidad del sistema y la confianza del usuario — porque en alto volumen, cada conversación es una venta, una retención o un abandono. Las mejoras propuestas apuntan a convertir al asistente en un **asesor de compra inteligente** que anticipa, optimiza y siempre devuelve la decisión final al cliente.

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

El asistente no puede calcular el impacto exacto porque el cliente no especificó cantidad ni presentación. Debe seguir este protocolo:

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
| 1 | Happy path | ¿Tienen avena? | Sí, menciona 'Avena instantánea 500g' con su precio | Verificar que nombre y precio coincidan con el catálogo |
| 2 | Sin stock | Quiero tomates cherry (o algún producto que no exista) | No menciona que el producto requerido no existe, ofrece alternativa de frutas o verduras disponibles | Verificar que el producto requerido no aparezca en la respuesta |
| 3 | Pregunta ambigua | Quiero algo rico para el desayuno | El asistente pide clarificación o sugiere categorías: lácteos, cereales, panadería | Verificar que no asuma ni invente — debe preguntar o mostrar categorías reales del catálogo |
| 4 | Presentaciones distintas | ¿Tienen leche? | Muestra todas las presentaciones disponibles: entera, descremada, 1L, 2L con sus precios | Verificar que todas las variantes mostradas existan en el catálogo y ninguna esté agotada |
| 5 | Presupuesto muy bajo | Quiero armar un desayuno con $1 | Informa honestamente que con $1 no alcanza para un desayuno completo y sugiere el producto más económico disponible | Verificar que no invente productos baratos inexistentes y que el precio sugerido sea real |
| 6 | Mensaje en otro idioma | I want to buy some milk please | Responde en inglés con los productos disponibles de leche y sus precios | Verificar que detectó el idioma, respondió en inglés y los productos existen en el catálogo |

---

### 3.2 Criterio de aprobación

**a. ¿Cuándo el asistente está listo?**

La empresa quiere lanzar el asistente cuando "funcione bien". El asistente debe aprobar mínimo el **90% de los casos de prueba** antes de salir a producción. El 10% restante puede corresponder a casos edge o ambiguos que se resuelven en iteraciones posteriores. En ecommerce de alto volumen, lanzar con menos del 90% representa un riesgo operativo y reputacional inaceptable — cada conversación fallida es un cliente potencialmente perdido.

**b. ¿Cómo defines respuesta correcta vs incorrecta?**

Para la pregunta *"¿Tienen salmón?"* una respuesta es:

| ✅ Correcta si... | ❌ Incorrecta si... |
|------------------|-------------------|
| Busca en el catálogo real antes de responder | Recomienda salmón con precio inventado sin verificar |
| Si existe: muestra nombre exacto + precio vigente | Dice que no hay sin haber buscado realmente |
| Si no existe: informa honestamente sin inventar | Sugiere alternativas que tampoco existen en el catálogo |
| Ofrece alternativas reales de la misma categoría | No ofrece alternativa cuando sí hay productos similares |

---

*Desarrollado por **Evelyn Carrillo** — Prueba técnica AI Developer*
*Análisis desde perspectiva de Ingeniería Industrial aplicada a eCommerce*