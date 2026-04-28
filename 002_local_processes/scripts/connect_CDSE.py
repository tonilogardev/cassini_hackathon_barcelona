import os
import requests
import json
from datetime import datetime
from dotenv import load_dotenv

# Cargar variables de entorno desde el fichero .env si existe
load_dotenv()

class CDSEConnector:
    """
    Conector para la API de Copernicus Data Space Ecosystem (CDSE).
    Permite la autenticación y la búsqueda/descarga de productos satelitales.
    """
    def __init__(self, username=None, password=None):
        # Utiliza variables de entorno si no se pasan parámetros directamente
        self.username = username or os.environ.get('CDSE_USERNAME')
        self.password = password or os.environ.get('CDSE_PASSWORD')
        
        self.token_url = "https://identity.dataspace.copernicus.eu/auth/realms/CDSE/protocol/openid-connect/token"
        self.catalogue_url = "https://catalogue.dataspace.copernicus.eu/odata/v1/Products"
        self.access_token = None

    def authenticate(self):
        """
        Obtiene el token de acceso OAuth2 utilizando las credenciales.
        """
        if not self.username or not self.password:
            raise ValueError("Faltan credenciales. Por favor configura CDSE_USERNAME y CDSE_PASSWORD en tus variables de entorno.")
        
        payload = {
            "client_id": "cdse-public",
            "username": self.username,
            "password": self.password,
            "grant_type": "password"
        }

        print("Autenticando en Copernicus Data Space Ecosystem...")
        response = requests.post(self.token_url, data=payload)
        
        if response.status_code == 200:
            self.access_token = response.json().get("access_token")
            print("¡Autenticación exitosa!")
        else:
            raise Exception(f"Fallo en la autenticación: {response.status_code} - {response.text}")

    def get_session(self):
        """
        Devuelve una sesión de requests pre-configurada con el token de autorización.
        """
        if not self.access_token:
            self.authenticate()
        
        session = requests.Session()
        session.headers.update({
            "Authorization": f"Bearer {self.access_token}"
        })
        return session

    def search_products(self, collection="SENTINEL-2", cloud_cover=None, start_date=None, end_date=None, top=10):
        """
        Busca productos en el catálogo OData de CDSE usando varios filtros.
        
        :param collection: Nombre de la colección (ej. 'SENTINEL-2')
        :param cloud_cover: Cobertura nubosa máxima en porcentaje (ej. 10)
        :param start_date: Fecha de inicio en formato 'YYYY-MM-DD'
        :param end_date: Fecha de fin en formato 'YYYY-MM-DD'
        :param top: Número máximo de resultados a devolver
        """
        if not self.access_token:
            self.authenticate()
            
        session = self.get_session()
        
        # Construir los filtros de OData
        filters = [f"Collection/Name eq '{collection}'"]
        
        if cloud_cover is not None:
            # Atributos específicos pueden variar dependiendo de la colección
            filters.append(f"Attributes/OData.CSC.DoubleAttribute/any(att:att/Name eq 'cloudCover' and att/OData.CSC.DoubleAttribute/Value le {cloud_cover})")
            
        if start_date and end_date:
            filters.append(f"ContentDate/Start ge {start_date}T00:00:00.000Z and ContentDate/Start le {end_date}T23:59:59.999Z")

        filter_query = " and ".join(filters)
        query = f"?$filter={filter_query}&$top={top}&$orderby=ContentDate/Start desc"
        url = f"{self.catalogue_url}{query}"
        
        print(f"Buscando productos: {collection}...")
        response = session.get(url)
        
        if response.status_code == 200:
            data = response.json()
            return data.get("value", [])
        else:
            print(f"Error buscando productos: {response.status_code} - {response.text}")
            return None
            
    def download_product(self, product_id, output_dir="downloads"):
        """
        Descarga un producto específico dado su ID.
        """
        if not self.access_token:
            self.authenticate()
            
        session = self.get_session()
        url = f"{self.catalogue_url}({product_id})/$value"
        
        os.makedirs(output_dir, exist_ok=True)
        
        # Primero necesitamos obtener los metadatos para saber el nombre del archivo
        metadata_url = f"{self.catalogue_url}({product_id})"
        metadata_response = session.get(metadata_url)
        if metadata_response.status_code != 200:
            raise Exception(f"No se pudieron obtener los metadatos del producto: {metadata_response.text}")
            
        product_name = metadata_response.json().get("Name", str(product_id))
        output_path = os.path.join(output_dir, f"{product_name}.zip")
        
        print(f"Descargando producto {product_name}...")
        
        # Descarga el archivo en chunks
        with session.get(url, stream=True) as r:
            r.raise_for_status()
            with open(output_path, 'wb') as f:
                for chunk in r.iter_content(chunk_size=8192):
                    f.write(chunk)
                    
        print(f"¡Descarga completada! Guardado en {output_path}")
        return output_path

if __name__ == "__main__":
    # === EJEMPLO DE USO ===
    print("Iniciando prueba de conexión a CDSE...")
    try:
        # Asegúrate de tener CDSE_USERNAME y CDSE_PASSWORD exportados en tu terminal o `.env`
        # export CDSE_USERNAME="tu_correo@ejemplo.com"
        # export CDSE_PASSWORD="tu_password"
        connector = CDSEConnector()
        
        # Prueba de búsqueda rápida de las últimas 3 imágenes de Sentinel-2 sin nubes
        products = connector.search_products(
            collection="SENTINEL-2", 
            cloud_cover=10, 
            top=3
        )
        
        if products:
            print(f"\nSe encontraron {len(products)} productos:")
            for p in products:
                print(f"- {p.get('Name')} (ID: {p.get('Id')})")
                
            # Para probar la descarga, descomenta la siguiente línea (aviso: son archivos pesados ~1GB)
            # connector.download_product(products[0]['Id'])
        else:
            print("No se encontraron productos o faltan credenciales.")
            
    except Exception as e:
        print(f"Error durante la prueba: {e}")
