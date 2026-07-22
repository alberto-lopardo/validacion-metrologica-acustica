📏 Validación Metrológica Automática de Campaña Acústica
Trazabilidad de Calibración · Detección de Deriva · Carta de Control I-MR · ISO 17025
Python
NumPy
Pandas
Matplotlib
Norma

![image alt](https://github.com/alberto-lopardo/validacion-metrologica-acustica/blob/main/validacion_metrologica_fig2.png?raw=true)

⚠️ Aviso: 
Proyecto de portafolio con datos 100% sintéticos (simulando
exportaciones de sonómetros). No guarda relación con proyectos reales,
clientes, metodologías propietarias ni datos confidenciales de empleadores
actuales o anteriores. Las normativas citadas son de conocimiento público
y su aplicación es meramente ilustrativa.

📋 Descripción:
Sistema automatizado de validación metrológica para campañas de monitoreo
acústico, conforme a los requisitos de trazabilidad de ISO 17025:2017
e IEC 61672-1:2013.

El pipeline ingesta los registros de calibración pre/post medición que genera
un sonómetro de Clase 1, evalúa tres criterios de aceptación independientes,
clasifica automáticamente cada medición como válida o inválida, y produce un
dashboard metrológico y una carta de control estadístico de proceso (I-MR)
para el seguimiento de la estabilidad del equipamiento a lo largo de la campaña.

🎯 Objetivos Técnicos
Simular el flujo de datos crudos de un sonómetro Clase 1 (15 mediciones, 3 días)
Aplicar tres criterios de validación metrológica independientes por medición
Detectar y catalogar mediciones con deriva excesiva de calibración
Calcular estadísticos de proceso: μ, σ, rango móvil MR̄
Generar una carta de control I-MR (Shewhart) con límites de control 3σ
Producir un reporte tabular estructurado listo para archivo de trazabilidad
📊 Visualizaciones Generadas
Figura	Contenido
validacion_metrologica_fig1.png	Dashboard 6 paneles: deriva, calibraciones pre/post, timeline, histograma, tabla resumen, niveles acústicos
validacion_metrologica_fig2.png	Carta de control I-MR completa (gráfico I + gráfico MR) con límites de control y normativo
✅ Criterios de Validación Implementados
Criterio A — Deriva de calibración pre/post
  |Cal_post − Cal_pre| ≤ 0.5 dB
  Ref: IEC 61672-1 Clase 1, tolerancia de estabilidad

Criterio B — Error absoluto calibración pre-medición
  |Cal_pre − 94.0 dB| ≤ 0.5 dB
  Ref: valor nominal del pistófono de referencia

Criterio C — Error absoluto calibración post-medición
  |Cal_post − 94.0 dB| ≤ 0.5 dB
  Ref: verificación de integridad al cierre de la medición
Una medición se clasifica como INVÁLIDA si falla uno o más criterios,
y debe ser descartada y repetida con equipo verificado.

📈 Carta de Control I-MR (Shewhart)
El gráfico I-MR aplica control estadístico de proceso (SPC) a la deriva
de calibración, herramienta estándar en laboratorios acreditados bajo ISO 17025:

Estimación de σ por rango móvil:
  σ̂ = MR̄ / d₂     (d₂ = 1.128 para n = 2)

Límites de control (3σ):
  LCS = μ + 3σ̂
  LCI = μ − 3σ̂

Límite de acción normativo (independiente):
  ±0.5 dB  (IEC 61672-1 Clase 1)
La separación entre los límites de control estadísticos (3σ) y el límite
normativo permite identificar si el equipo presenta deriva sistemática
antes de superar el umbral de rechazo.

⚙️ Tecnologías
Librería	Uso
NumPy	Generación de datos sintéticos, estadísticos de proceso
Pandas	Estructura de campaña, aplicación de validación por fila, exportación
Matplotlib	Dashboard 6 paneles + carta de control I-MR
🚀 Instalación y Uso
# Clonar el repositorio
git clone https://github.com/alberto-lopardo/validacion-metrologica-acustica.git
cd validacion-metrologica-acustica

# Instalar dependencias
pip install numpy pandas matplotlib

# Ejecutar
python validacion_metrologica.py
El script imprime el reporte completo en consola (detalle por medición +
resumen estadístico + lista de anomalías) y guarda las dos figuras en el
directorio de trabajo. Para exportar el dataset validado a CSV, descomentar
la última línea del script.

📤 Estructura del Reporte de Consola
ID      Fecha/Hora         Punto  ΔCal (dB)   Leq (dBA)  Estado    Fallas
M001    04/11/2024 08:00   P01     +0.197 dB    62.9 dBA  ✅ VÁLIDA  —
M004    04/11/2024 14:00   P04     +0.810 dB    57.6 dBA  ❌ INVÁLIDA Deriva +0.810 dB > ±0.5 dB
...
Resultado: 12/15 válidas (80.0 %)
Deriva: μ = −0.019 dB  |  σ = 0.397 dB  |  máx. abs. = 0.930 dB
📐 Normativa de Referencia
ISO 17025:2017 — Requisitos generales para la competencia de laboratorios de ensayo y calibración
IEC 61672-1:2013 — Sonómetros: especificaciones (tolerancias Clase 1)
ISO 1996-2:2017 — Determinación de niveles de ruido ambiental (requisitos de trazabilidad)
👤 Autor
Alberto Lopardo — Especialista en Acústica y Análisis de Señales
LinkedIn

Proyecto de portafolio — datos 100% sintéticos — sin relación con mediciones reales.
