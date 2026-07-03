import re, spacy, requests
from bs4 import BeautifulSoup


class Scrapper:

    def __init__(self, spacy_model:str ='es_core_news_lg'):
        try:
            self.nlp = spacy.load(spacy_model)
        except OSError:
            print(f"Error: Falta el modelo de spaCy '{spacy_model}'. Instalar antes de continuar.")
            exit()

    # ------Funciones principales--------

    def escanear_web(self, url_o_html:str, es_url:bool=True):
        """
        Función orquestadora del proceso principal leyendo contenedores lógicos.
        """

        if es_url:
            headers = {"User-Agent": "Mozilla/5.0"}
            try:
                response = requests.get(url_o_html, headers=headers)
                response.raise_for_status()
                html_crudo = response.text
            except Exception as e:
                return {"error": str(e)}
        else:
            html_crudo = url_o_html


        soup = BeautifulSoup(html_crudo, 'html.parser')

        scripts_tags = soup.find_all('script')
        texto_de_scripts = " ".join([s.get_text() for s in scripts_tags if s.get_text()])

        fuga_por_scripts = self._extraer_info_scripts(texto_de_scripts)
        
        # Limpieza de scripts y estilos para evitar ruido
        for script in soup(["script", "style", "noscript"]):
            script.extract()
            
        personas_encontradas = []
        
        # Memorias para evitar duplicar procesamientos y datos obtenidos
        emails_ya_vistos = set()
        nombres_ya_vistos = set()
        usuarios_ya_vistos = set()
        
        # Sumamos palabras que usa este HTML específico para etiquetar datos
        palabras_basura = [
            "Usuario", "Correo", "Ubicación", "Teléfono", "Tel", "Celular", "Mail", "Publicado", 
            "Argentina", "Contacto", "Nombre", "Fecha", "registro", "Aviso", "Importante", 
            "Seguridad", "Estimado", "React", "WhatsApp", "Contenido", "Cargo", "Email"
        ]     

        roles_clave = [
            "Administrador", "Base de Datos", "Moderadora", "CEO", "Soporte", "Director", 
            "Desarrollador", "Diseñador", "Tester", "Líder", "Coordinador"
        ]

        # Iteración sobre los contenedores lógicos más comunes en maquetación
        for bloque in soup.find_all(['article', 'section', 'div', 'li']):
            
            texto_bloque = bloque.get_text(separator=' ', strip=True)
            
            if len(texto_bloque) < 10:
                continue
                
            # Analizamos todo el texto del bloque para extraer datos
            emails, telefonos, usuarios, fechas = self._extraer_datos_por_patron(texto_bloque)
            nombres_crudos, lugares = self._extraer_entidades_nlp(texto_bloque)

            roles_encontrados = []
            for rol in roles_clave:
                if re.search(rf'\b{rol}\b', texto_bloque, flags=re.IGNORECASE):
                    roles_encontrados.append(rol)
            
            # Limpieza de nombres
            nombres_limpios = []
            for nombre in nombres_crudos:
                nombre_temp = nombre
                for basura in palabras_basura:
                    # Borramos la basura usando regex para ignorar mayúsculas/minúsculas
                    nombre_temp = re.sub(rf'\b{basura}\b', '', nombre_temp, flags=re.IGNORECASE)
                
                nombre_temp = nombre_temp.strip()
                
                # Solo aceptamos el nombre si le quedó Nombre + Apellido
                if len(nombre_temp.split()) > 1:
                    nombres_limpios.append(nombre_temp)
            

            lista_negra_lugares = {
                "ubicación", "ubicacion", "telefono", "teléfono", "tel", "mail", "correo", 
                "usuario", "fecha", "registro", "contacto", "administrador", "moderadora", 
                "empresa", "whatsapp", "react", "código", "rol", "contenido", "corporativo"
            }

            lugares_limpios = []
            for lugar in lugares:
                lugar_temp = lugar
                
                # Eliminación de palabras basura
                for basura in palabras_basura:
                    lugar_temp = re.sub(rf'\b{basura}\b', '', lugar_temp, flags=re.IGNORECASE)
                
                # Limpieza de caracteres especiales
                lugar_clean = re.sub(r'^[,\s:\-]+|[,\s:\-]+$', '', lugar_temp).strip()
                
                if lugar_clean.lower() not in lista_negra_lugares and len(lugar_clean) > 3:
                    lugares_limpios.append(lugar_clean)

            # 3. FILTRO DE DENSIDAD
            # Lo ignoramos y dejamos que el bucle siga iterando hacia sus hijos más pequeños.
            if len(set(nombres_limpios)) >= 2 or len(emails) >= 3:
                continue
                
            nuevos_emails = [e for e in emails if e not in emails_ya_vistos]
            nuevos_nombres = [n for n in nombres_limpios if n not in nombres_ya_vistos]
            nuevos_usuarios = [u for u in usuarios if u not in usuarios_ya_vistos]
            
            if nuevos_emails or nuevos_nombres or nuevos_usuarios:
                nombre_final = nuevos_nombres[0] if nuevos_nombres else (nombres_limpios[0] if nombres_limpios else "Desconocido")
                
                perfil = {
                    "nombre": nombre_final,
                    "usuarios": nuevos_usuarios, 
                    "emails": nuevos_emails,
                    "telefonos": telefonos,
                    "ubicaciones": lugares_limpios,
                    "fechas": fechas,
                    "roles": list(set(roles_encontrados))  
                }
                personas_encontradas.append(perfil)
                
                # Actualizamos la memoria
                emails_ya_vistos.update(emails)
                nombres_ya_vistos.update(nombres_limpios)
                usuarios_ya_vistos.update(usuarios)

        return {
            "estado": "completado",
            "total_personas_encontradas": len(personas_encontradas),
            "personas": personas_encontradas,
            "tecnologias_detectadas": fuga_por_scripts
            }


    # -----Funciones auxiliares--------

    def _extraer_datos_por_patron(self, texto:str):
        """
        Utilizando expresiones regulares y patrones regex se intentará
        extraer emails, teléfonos, usuarios y fechas del texto.
        """
        # Regex para emails y teléfonos (los que ya tenías)
        patron_email = r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'
        emails = re.findall(patron_email, texto)
        
        patron_telefono = r'(?:\+?\d{1,3}[\s-]?)?\(?\d{2,4}\)?[\s-]?\d{3,4}[\s-]?\d{3,4}'
        telefonos = re.findall(patron_telefono, texto)
        telefonos = [tel.strip() for tel in telefonos if len(tel.replace(" ", "").replace("-", "")) >= 8]
        
        # NUEVO: Regex para nombres de usuario (atrapa @usuario, @nombre.apellido, @dev_99)
        patron_usuario = r'(?<![\w.-])@[\w.]+'
        usuarios = re.findall(patron_usuario, texto)
        
        # NUEVO: Regex para fechas (atrapa tanto "2023-08-15" como "2026-06-30 09:18:42 UTC-3")
        patron_fecha = r'\d{4}-\d{2}-\d{2}(?:\s+\d{2}:\d{2}:\d{2}\s*UTC[-+]\d+)?'
        fechas = re.findall(patron_fecha, texto)
        
        return list(set(emails)), list(set(telefonos)), list(set(usuarios)), list(set(fechas))

    def _extraer_entidades_nlp(self, texto:str):
        """
        Detecta nombres y lugares en el texto utilizando spaCy.
        """
        doc = self.nlp(texto)
        nombres = []
        direcciones_lugares = []
        
        for entidad in doc.ents:
            if entidad.label_ == "PER":
                nombres.append(entidad.text)
            elif entidad.label_ in ["LOC"]:
                texto_entidad = entidad.text
                
                es_email_o_web = "@" in texto_entidad or re.search(r'\.[a-zA-Z]{2,4}\b', texto_entidad)
                
                if not es_email_o_web:
                    direcciones_lugares.append(texto_entidad)
                
        return list(set(nombres)), list(set(direcciones_lugares))

    def _extraer_info_scripts(self, texto:str):

        info_tecnologias = {
            "frameworks": [],
            "arquitectura_bd_api": [],
            "posibles_fugas_config": {}
        }

        if texto:

            # Frameworks o librerías
            framework_patterns = {
                "React.js": r"reactRoot|__react|react-dom",
                "Next.js": r"__NEXT_DATA__|next/script",
                "Vue.js": r"__VUE__|vue-router",
                "Angular": r"ng-version|ng-bootstrap",
                "jQuery": r"jQuery|libs/jquery"
            }
            for framework, pattern in framework_patterns.items():
                if re.search(pattern, texto):
                    info_tecnologias["frameworks"].append(framework)

            # Bases de datos, ORMs o APIs
            db_api_patterns = {
                "GraphQL / Apollo": r"query\s*\{|mutation\s*\{|__typename",
                "Firebase / Firestore": r"firebaseConfig|firestore|initializeWithApp",
                "MongoDB / Mongoose": r"mongodb:\/\/|ObjectId\(",
                "PostgreSQL / MySQL / SQL": r"SELECT\s+.*\s+FROM|postgres:\/\/|mysql:\/\/",
                "Supabase": r"supabaseUrl|supabaseKey"
            }
            for tecnologia, pattern in db_api_patterns.items():
                if re.search(pattern, texto, flags=re.IGNORECASE):
                    info_tecnologias["arquitectura_bd_api"].append(tecnologia)


            # API_KEYS, TOKENS o variables de entorno
            config_patterns = {
                "Variables de Entorno expuestas": r"process\.env\.[A-Z0-9_]+",
                "API Key / Tokens en código": r"(?:api_key|apikey|secret_key|token|auth_domain)\s*[:=]\s*['\"][A-Za-z0-9_\-]{16,}['\"]",
                "Endpoint de Base de Datos expuesto": r"(?:db_url|database_url|connection_string)\s*[:=]"
            }
            riesgos = []
            for riesgo, pattern in config_patterns.items():
                if re.search(pattern, texto, flags=re.IGNORECASE):
                    riesgos.append(riesgo)
            
            info_tecnologias["posibles_fugas_config"]['riesgos_identificados'] = riesgos

            patron_env = r"(process\.env\.[A-Z0-9_]+)"
            envs = re.findall(patron_env, texto)
            if envs:
                info_tecnologias["posibles_fugas_config"]["variables_entorno_expuestas"] = list(set(envs))

            patron_keys = r"(?:api_key|apikey|secret_key|token|auth_domain)\s*[:=]\s*['\"]([A-Za-z0-9_\-]{16,})['\"]"
            keys = re.findall(patron_keys, texto, flags=re.IGNORECASE)
            if keys:
                info_tecnologias["posibles_fugas_config"]["tokens_api_keys_encontrados"] = list(set(keys))

            # Captura strings de asignación a bases de datos o strings de conexión crudos
            patron_db_urls = r"(?:db_url|database_url|connection_string)\s*[:=]\s*['\"]([^'\"]+)['\"]"
            db_urls = re.findall(patron_db_urls, texto, flags=re.IGNORECASE)
            if db_urls:
                info_tecnologias["posibles_fugas_config"]["endpoints_bd_encontrados"] = list(set(db_urls))

            return info_tecnologias




