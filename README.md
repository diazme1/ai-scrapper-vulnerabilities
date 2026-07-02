# 🛡️ AI Scrapper Vulnerabilities API

Esta plataforma es un motor de análisis inteligente diseñado para la **detección automatizada de exposición de datos sensibles**. A través de técnicas de web scraping y clasificación basada en riesgos, identifica perfiles y vulnerabilidades en sitios web o documentos HTML.

## 🚀 Arquitectura del Sistema
El flujo de trabajo se divide en dos etapas críticas:

1. 🔍 Motor de Análisis: Procesa la entrada (URL o HTML), utiliza patrones Regex avanzados y estructura la información semántica del DOM en objetos JSON.
2. ⚖️ RiskClassifier: Aplica una matriz de scoring sobre los datos extraídos para categorizar la exposición en niveles: Bajo, Medio, Alto o Crítico.

## Diagrama
![alt text](docs/diagrama_ai_scrapper_vulnerabilities.png)

---

## 🛠️ Setup e Instalación

Para poner en marcha el entorno de desarrollo, sigue estos pasos:

### 1. Clonar y preparar entorno
# Instalar dependencias
pip install -r requirements.txt

### 2. Ejecutar la API
Levanta el servidor utilizando Uvicorn para desarrollo con recarga automática:
uvicorn src.api.main:app --reload

### 3. Acceso a Documentación
Una vez ejecutado, accede a la documentación interactiva (Swagger UI) para probar tus endpoints:
http://localhost:8000/docs

---

## 🔌 Endpoints de la API

La API expone los siguientes puntos de entrada para el análisis:

- POST /escanear-web: Analiza un sitio web en vivo a partir de una URL (entrada: url: str).
- POST /escanear-html: Analiza el contenido de un archivo HTML subido (entrada: file: UploadFile).

---

## 📊 Niveles de Riesgo Detectados

El sistema clasifica automáticamente los hallazgos según el nivel de exposición:

- ✅ Riesgo Bajo: Exposición limitada de datos públicos.
- ⚠️ Riesgo Medio: Presencia de datos sensibles con impacto moderado.
- 🚫 Riesgo Alto: Exposición significativa de información personal.
- 💀 Riesgo Crítico: Fuga masiva de datos (correos, teléfonos, ubicaciones).

---

## ⚠️ Vulnerabilidades Críticas bajo Vigilancia

El RiskClassifier está configurado para identificar activamente:

- 📧 Exposición de correos: Riesgo de phishing y suplantación.
- ☎️ Fuga de números telefónicos: Facilita el acoso e ingeniería social.
- 📍 Direcciones y Geolocalización: Riesgo de robo o amenazas físicas.
- 🧠 Patrones de comportamiento: Identificación de perfiles para seguimiento dirigido.

---

> ⚖️ Consideraciones Éticas: Este sistema está destinado exclusivamente a fines autorizados, de seguridad y auditoría, respetando siempre la privacidad y las leyes de protección de datos vigentes.