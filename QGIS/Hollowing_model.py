"""
Model exported as python.
Name : Trial
Group : 
With QGIS : 33410
"""

from qgis.core import QgsProcessing
from qgis.core import QgsProcessingAlgorithm
from qgis.core import QgsProcessingMultiStepFeedback
from qgis.core import QgsProcessingParameterVectorLayer
from qgis.core import QgsProcessingParameterNumber
from qgis.core import QgsProcessingParameterFeatureSink
from qgis.core import QgsProcessingParameterFolderDestination
from qgis.core import QgsProcessingParameterString
from qgis.core import QgsExpression
from qgis.core import QgsVectorLayer
from qgis.core import QgsProject
from qgis.core import QgsCoordinateReferenceSystem
import processing
import os
from datetime import datetime

class Trial(QgsProcessingAlgorithm):

    def initAlgorithm(self, config=None):
        # Layer showing the drowned surface, drawn over the orthophoto
        self.addParameter(QgsProcessingParameterVectorLayer('capa_ahoyado', 'Capa ahoyado', types=[QgsProcessing.TypeVectorPolygon], defaultValue=None))
        # The layer must have the corrects attributes. Check "IMP-WI-021-HOW TO-Create a post-planting layer".
        self.addParameter(QgsProcessingParameterVectorLayer('net_plots', 'Net plots', types=[QgsProcessing.TypeVectorPolygon], defaultValue=None))
        self.addParameter(QgsProcessingParameterNumber('delete_holes_size', '"Delete holes" size', type=QgsProcessingParameterNumber.Integer, minValue=0, maxValue=50000, defaultValue=3000))
        self.addParameter(QgsProcessingParameterFolderDestination('output_folder', 'Output folder', defaultValue=None))
        self.addParameter(QgsProcessingParameterString('planting_site_name','Planting site name', defaultValue=''))
        self.addParameter(QgsProcessingParameterString('name_initials','Name initials', defaultValue=''))

    def processAlgorithm(self, parameters, context, model_feedback):
        # Use a multi-step feedback, so that individual child algorithm progress reports are adjusted for the
        # overall progress through the model
        feedback = QgsProcessingMultiStepFeedback(21, model_feedback)
        results = {}
        outputs = {}

        # Check if the layers´ CRS is a projected one. If not, the process should not start

        def check_projected_crs(layer,feedback):
            crs=layer.crs()
            if crs.isGeographic():
                feedback.reportError(f'La capa "{layer.name()}"  está en un CRS geográfico. Por favor, reproyecta la capa a un CRS proyectado y reinicia el geoproceso.')
                return True
            return False
        
        crs_ahoyado = self.parameterAsVectorLayer(parameters, 'capa_ahoyado', context)
        crs_net_plots = self.parameterAsVectorLayer(parameters, 'net_plots', context)

        if check_projected_crs(crs_ahoyado, feedback) or check_projected_crs(crs_net_plots, feedback):
            return {}

        feedback.setCurrentStep(1)
        if feedback.isCanceled():
            return {}

        # Check if some of the attrbiutes are correct. 

        def check_attributes(layer,required_attributes,optional_attributes,optional_attributes2,feedback):
            layer_fields=[field.name() for field in layer.fields()]
            missing_attributes=[attr for attr in required_attributes if attr not in layer_fields]
            has_optional = any(attr in layer_fields for attr in optional_attributes)
            has_optional2 = any(attr in layer_fields for attr in optional_attributes2)
            if missing_attributes or (not has_optional and not has_optional2):
                if missing_attributes:
                    feedback.reportError(
                        f'The layer "{layer.name()}" is missing the following required attributes: {", ".join(missing_attributes)}')
                if not has_optional:
                    feedback.reportError(
                        f'The layer "{layer.name()}" must contain at least one of the following optional attributes: {", ".join(optional_attributes)}')
                if not has_optional2:
                    feedback.reportError(
                        f'The layer "{layer.name()}" must contain at least one of the following optional attributes: {", ".join(optional_attributes2)}')
                return True
            return False

        required_attributes=['stand_id','region']
        optional_attributes=['stand_type_id','st_type_id']
        optional_attributes2=['stand_type_name','stand_type']
        if check_attributes(crs_net_plots,required_attributes,optional_attributes,optional_attributes2,feedback):
            return{}

        # Creamos función - Reproject to WGS 84
        
        def reproject_to_wgs84(input_layer, context, feedback, step):
            alg_params = {
                'INPUT': input_layer,
                'TARGET_CRS': 'EPSG:4326',  # WGS 84
                'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
            }
            feedback.setCurrentStep(step)
            if feedback.isCanceled():
                return None
            return processing.run('native:reprojectlayer', alg_params, context=context, feedback=feedback, is_child_algorithm=True)['OUTPUT']

        # Get today´s date in MMDDYYYY format
        today_date=datetime.now().strftime('%m%d%Y')

        # Get the planting site name
        planting_site_name=parameters['planting_site_name']

        # Get the initials
        initials=parameters['name_initials']

        # Define output file names
        geojson_post_planting_area = f"Post_planting_area_{planting_site_name}_{today_date}_{initials}.geojson"
        geojson_post_planting_simplified_area = f"Post_planting_simplified_area_{planting_site_name}_{today_date}_{initials}.geojson"
        kml_post_planting_area = f"Post_planting_area_{planting_site_name}_{today_date}_{initials}.kml"
        kml_post_planting_simplified_area = f"Post_planting_simplified_area_{planting_site_name}_{today_date}_{initials}.kml"

        # Define output paths
        output_folder = parameters['output_folder']
        kml_folder = os.path.join(output_folder, 'kml')
        os.makedirs(kml_folder, exist_ok=True)

        geojson_post_planting_area_path = os.path.join(output_folder, geojson_post_planting_area)
        geojson_post_planting_simplified_area_path = os.path.join(output_folder, geojson_post_planting_simplified_area)
        kml_post_planting_area_path = os.path.join(kml_folder, kml_post_planting_area)
        kml_post_planting_simplified_area_path = os.path.join(kml_folder, kml_post_planting_simplified_area)

        # Capa ahoyado - Retain fields
        alg_params = {
            'FIELDS': [''],
            'INPUT': parameters['capa_ahoyado'],
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['RetainFields'] = processing.run('native:retainfields', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(2)
        if feedback.isCanceled():
            return {}

        # Capa ahoyado - Remove duplicate vertices
        alg_params = {
            'INPUT': outputs['RetainFields']['OUTPUT'],
            'TOLERANCE': 1e-06,
            'USE_Z_VALUE': False,
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['Ahoyado_RemoveDuplicateVertices'] = processing.run('native:removeduplicatevertices', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(3)
        if feedback.isCanceled():
            return {}

        # Net plots - Remove duplicate vertices 
        alg_params = {
            'INPUT': parameters['net_plots'],
            'TOLERANCE': 1e-06,
            'USE_Z_VALUE': False,
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['NetPlots_RemoveDuplicateVertices'] = processing.run('native:removeduplicatevertices', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(4)
        if feedback.isCanceled():
            return {}

        # Net plots - Fix geometries Linework
        alg_params = {
            'INPUT': outputs['NetPlots_RemoveDuplicateVertices']['OUTPUT'],
            'METHOD': 0,  # Linework
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['NetPlots_FixGeometries0'] = processing.run('native:fixgeometries', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(5)
        if feedback.isCanceled():
            return {}

        # Net plots - Fix geometries Structure
        alg_params = {
            'INPUT': outputs['NetPlots_FixGeometries0']['OUTPUT'],
            'METHOD': 1,  # Linework
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['NetPlots_FixGeometries1'] = processing.run('native:fixgeometries', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(6)
        if feedback.isCanceled():
            return {}

        # Capa ahoyado - Fix geometries Linework
        alg_params = {
            'INPUT': outputs['Ahoyado_RemoveDuplicateVertices']['OUTPUT'],
            'METHOD': 0,  # Structure
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['Ahoyado_FixGeometries0'] = processing.run('native:fixgeometries', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(7)
        if feedback.isCanceled():
            return {}

        # Capa ahoyado - Fix geometries Structure
        alg_params = {
            'INPUT': outputs['Ahoyado_FixGeometries0']['OUTPUT'],
            'METHOD': 1,  # Structure
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['Ahoyado_FixGeometries1'] = processing.run('native:fixgeometries', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(8)
        if feedback.isCanceled():
            return {}

        # Capa ahoyado - Create spatial index
        alg_params = {
            'INPUT': outputs['Ahoyado_FixGeometries1']['OUTPUT']
        }
        outputs['Ahoyado_CreateSpatialIndex'] = processing.run('native:createspatialindex', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(9)
        if feedback.isCanceled():
            return {}

        # Net Plots - Create spatial index
        alg_params = {
            'INPUT': outputs['NetPlots_FixGeometries1']['OUTPUT']
        }
        outputs['NetPlots_CreateSpatialIndex'] = processing.run('native:createspatialindex', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(10)
        if feedback.isCanceled():
            return {}

        # Net plots - Buffer
        alg_params = {
            'DISSOLVE': False,
            'DISTANCE': -0.5,
            'END_CAP_STYLE': 0,  # Round
            'INPUT': outputs['NetPlots_CreateSpatialIndex']['OUTPUT'],
            'JOIN_STYLE': 0,  # Round
            'MITER_LIMIT': 2,
            'SEGMENTS': 5,
            'SEPARATE_DISJOINT': False,
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['Buffer'] = processing.run('native:buffer', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(11)
        if feedback.isCanceled():
            return {}

        # Buffered - Create spatial index
        alg_params = {
            'INPUT': outputs['Buffer']['OUTPUT']
        }
        outputs['Buffered_CreateSpatialIndex'] = processing.run('native:createspatialindex', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(12)
        if feedback.isCanceled():
            return {}

        # Join attributes by location
        alg_params = {
            'DISCARD_NONMATCHING': False,
            'INPUT': outputs['Ahoyado_CreateSpatialIndex']['OUTPUT'],
            'JOIN': outputs['Buffered_CreateSpatialIndex']['OUTPUT'], 
            'JOIN_FIELDS': [''],
            'METHOD': 2,  # Take attributes of the feature with largest overlap only (one-to-one)
            'PREDICATE': [0],  # intersect
            'PREFIX': '',
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['JoinAttributesByLocation'] = processing.run('native:joinattributesbylocation', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(13)
        if feedback.isCanceled():
            return {}

        # Simplify vertices
        alg_params = {
            'INPUT': outputs['JoinAttributesByLocation']['OUTPUT'],
            'METHOD': 0,  # Distance (Douglas-Peucker)
            'TOLERANCE': 0.1,
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['Simplify'] = processing.run('native:simplifygeometries', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(14)
        if feedback.isCanceled():
            return {}

        # Drop field(s)
        alg_params = {
            'COLUMN': QgsExpression("'area_net;area_gross'").evaluate(),
            'INPUT': outputs['Simplify']['OUTPUT'],
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['DropFields'] = processing.run('native:deletecolumn', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(15)
        if feedback.isCanceled():
            return {}
        
        # Net area - Save Geojson

        reprojected_geojson_area = reproject_to_wgs84(outputs['DropFields']['OUTPUT'], context, feedback, step=16)
        alg_params = {
            'FIELD_LENGTH': 10,
            'FIELD_NAME': 'area_net',
            'FIELD_PRECISION': 3,
            'FIELD_TYPE': 0,  # Decimal (double)
            'FORMULA': '$area/10000',
            'INPUT': reprojected_geojson_area,
            'OUTPUT': geojson_post_planting_area_path
        }
        outputs['FieldCalculator'] = processing.run('native:fieldcalculator', alg_params, context=context, feedback=feedback, is_child_algorithm=True)
        results['PostPlantingArea'] = outputs['FieldCalculator']['OUTPUT']

        feedback.setCurrentStep(17)
        if feedback.isCanceled():
            return {}

        # Net area - Save KML
        alg_params = {
            'ACTION_ON_EXISTING_FILE': 0,  # Create or overwrite file
            'DATASOURCE_OPTIONS': '',
            'INPUT': outputs['FieldCalculator']['OUTPUT'],
            'LAYER_NAME': '',
            'LAYER_OPTIONS': '',
            'OUTPUT': kml_post_planting_area_path
        }
        outputs['SaveVectorFeaturesToFile'] = processing.run('native:savefeatures', alg_params, context=context, feedback=feedback, is_child_algorithm=True)
        results['PostPlantingAreaKml'] = kml_post_planting_area_path

        feedback.setCurrentStep(18)
        if feedback.isCanceled():
            return {}

        # Net area - Delete holes
        alg_params = {
            'INPUT': outputs['DropFields']['OUTPUT'],
            'MIN_AREA': parameters['delete_holes_size'],
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['DeleteHoles'] = processing.run('native:deleteholes', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(19)
        if feedback.isCanceled():
            return {}

        # Simplified area - Save Geojson
        reprojected_geojson_simplified = reproject_to_wgs84(outputs['DeleteHoles']['OUTPUT'], context, feedback, step=20)
        alg_params = {
            'FIELD_LENGTH': 10,
            'FIELD_NAME': 'area_gross',
            'FIELD_PRECISION': 3,
            'FIELD_TYPE': 0,  # Decimal (double)
            'FORMULA': '$area/10000',
            'INPUT': reprojected_geojson_simplified,
            'OUTPUT': geojson_post_planting_simplified_area_path
        }
        outputs['FieldCalculator'] = processing.run('native:fieldcalculator', alg_params, context=context, feedback=feedback, is_child_algorithm=True)
        results['PostPlantingSimplifiedArea'] = geojson_post_planting_simplified_area_path

        feedback.setCurrentStep(21)
        if feedback.isCanceled():
            return {}

        # Simplified area - Save KML
        alg_params = {
            'ACTION_ON_EXISTING_FILE': 0,  # Create or overwrite file
            'DATASOURCE_OPTIONS': '',
            'INPUT': outputs['FieldCalculator']['OUTPUT'],
            'LAYER_NAME': '',
            'LAYER_OPTIONS': '',
            'OUTPUT': kml_post_planting_simplified_area_path
        }
        outputs['SaveVectorFeaturesToFile'] = processing.run('native:savefeatures', alg_params, context=context, feedback=feedback, is_child_algorithm=True)
        results['PostPlantingSimplifiedAreaKml'] = kml_post_planting_simplified_area_path

        feedback.setCurrentStep(22)
        if feedback.isCanceled():
            return {}

        #Check for duplicates. Esto se puede poner justo después de la Join by Location
        geojson_check=QgsVectorLayer(geojson_post_planting_area_path,f'Post_planting_area_{planting_site_name}_{today_date}_{initials}',"ogr")
        if not geojson_check.isValid():
            print(f"Failed to load layer: {geojson_post_planting_area_path}")
            return{}
        if 'stand_id' not in [field.name() for field in geojson_check.fields()]:
            feedback.reportError("El campo 'stand_id' no existe en la capa. Verifica los atributos de la capa generada.")
            return {}
        stand_ids=[feature['stand_id'] for feature in geojson_check.getFeatures()]
        if len(set(stand_ids))!=len(stand_ids):
            # QMessageBox().information(None, 'Aviso', 'Hay entidades repetidas en el Geojson.')
            feedback.reportError("Hay entidades repetidas en el Geojson. Por favor, comprueba que los polígonos de la capa de ahoyado están bien agrupados y que las geometrías de las capas son correctas.\
                                 En caso de no encontrar solución, contactar con Santi o Jorge")
        else:
            QgsProject.instance().addMapLayer(geojson_check)
            feedback.pushInfo("Procesamiento completado con éxito. Las cuatro capas se han guardado en la carpeta correspondiente")
            return results

    def name(self):
        return 'Trial'

    def displayName(self):
        return 'Trial'

    def group(self):
        return ''

    def groupId(self):
        return ''

    def createInstance(self):
        return Trial()
