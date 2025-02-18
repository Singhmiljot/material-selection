from flask import Flask, request, jsonify, render_template
import logging
import json
import os
import google.generativeai as genai



app = Flask(__name__, 
            template_folder='templates', 
            static_folder='static')

# Ensure static files are served with proper caching headers
@app.after_request
def add_header(response):
    response.cache_control.max_age = 300
    return response

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Load material data from a JSON file
with open('data/materials.json', 'r') as f:
    materials = json.load(f)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/material-details', methods=['POST'])
def material_details():
    data = request.json
    material_name = data['name']
    
    try:
        try:
            # Initialize Google Generative AI with direct API key
            genai.configure(
                api_key='AIzaSyB4mLmJ_1WsMvouTvUXE9heG8qNJYM4qrc',
                transport='rest'  # Use REST instead of gRPC to avoid timeout issues
            )


            
            # Create prompt for material information
            prompt = f"""Provide detailed technical information about {material_name} material in strict JSON format with the following fields:
            - name: Material name
            - strength: Tensile strength in MPa
            - weight: Density in g/cm³
            - cost: Relative cost (Low/Medium/High)
            - max_temperature: Maximum operating temperature in °C
            - thermalResistance: Thermal conductivity in W/m·K
            - mechanicalProperties: Key mechanical properties
            - applications: Common applications
            - advantages: Main advantages
            - limitations: Key limitations
            
            Return ONLY a valid JSON object with double quotes, no additional text or explanations. The response must be parseable by json.loads(). Example format:
            {{
              "name": "material_name",
              "strength": 0,
              "weight": 0,
              "cost": "Low",
              "max_temperature": 0,
              "thermalResistance": "N/A",
              "mechanicalProperties": "N/A",
              "applications": "N/A",
              "advantages": "N/A",
              "limitations": "N/A"
            }}"""

            
            # Get response from Google Generative AI with error handling
            model = genai.GenerativeModel('gemini-pro')
            try:
                response = model.generate_content(prompt)

            except Exception as api_error:
                logger.error(f"API request failed: {str(api_error)}")
                raise ValueError("Failed to get response from API")

            
            # Parse the response
            if response.text:
                try:
                    # Try to parse as JSON first
                    material_info = json.loads(response.text)
                except json.JSONDecodeError:
                    # If not JSON, create a structured response
                    material_info = {
                        'name': material_name,
                        'strength': 0,
                        'weight': 0,
                        'cost': 0,
                        'max_temperature': 0,
                        'thermalResistance': 'N/A',
                        'mechanicalProperties': response.text,
                        'applications': 'N/A',
                        'advantages': 'N/A',
                        'limitations': 'N/A'
                    }
            else:
                raise ValueError("Empty response from API")

                
        except json.JSONDecodeError:
            logger.error("Failed to parse API response as JSON")
            raise ValueError("Invalid JSON response from API")
        except Exception as e:
            logger.error(f"API request failed: {str(e)}")
            raise




        logger.debug(f"Scraped material info: {material_info}")

        # Add to local dataset for future reference
        materials.append(material_info)
        with open('data/materials.json', 'w') as f:
            json.dump(materials, f)
            
        return jsonify(material_info)

    except Exception as e:
        logger.error(f"Failed to retrieve material information: {str(e)}")
        # Return cached data if available
        cached_material = next((m for m in materials if m['name'].lower() == material_name.lower()), None)
        if cached_material:
            logger.info("Returning cached material data")
            return jsonify(cached_material)
        return jsonify({
            'error': 'Failed to retrieve material information',
            'details': str(e),
            'suggestion': 'Please check your internet connection and try again later.'
        }), 503



if __name__ == '__main__':
    app.run(debug=True)
