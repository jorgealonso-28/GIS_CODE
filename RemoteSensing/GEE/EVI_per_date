// Region of interest
var ROI = ee.FeatureCollection("projects/keen-ascent-439714-i6/assets/Pinof_24-25_PPA");

// Descargamos las imágenes sentinel
var s2 = ee.ImageCollection('COPERNICUS/S2_SR_HARMONIZED')
    .filterBounds(ROI)
    .filterDate('2019-01-01', '2019-06-01');

// Paleta de colores EVI
var EVIpalette = [
  'FFFFFF', // White for very low EVI
  'A7D080', // Light green
  '70C25F', // Medium green
  '38A700', // Darker green
  '006400'  // Dark green for high EVI
];

// Cargamos Cloud Score+
var csPlus = ee.ImageCollection('GOOGLE/CLOUD_SCORE_PLUS/V1/S2_HARMONIZED');

// Cargamos los umbrales numéricos
var QA_BAND = 'cs_cdf';
var INVALID_SCL_VALUES = [3, 8, 9, 10];
var CLEAR_THRESHOLD = 0.60;

// Calculamos el EVI y lo añadimos
function calculateEVI(img) {
    // Scale bands to reflectance (divide by 10,000)
    var nir = img.select('B8').divide(10000);
    var red = img.select('B4').divide(10000);
    var blue = img.select('B2').divide(10000);

    // Calculate EVI using scaled values
    var evi = img.expression(
        'G * ((NIR - RED) / (NIR + C1 * RED - C2 * BLUE + L))', {
            'NIR': nir,   // Scaled Near-Infrared
            'RED': red,   // Scaled Red
            'BLUE': blue, // Scaled Blue
            'G': 2.5,     // Gain factor
            'C1': 6,      // Coefficient for RED
            'C2': 7.5,    // Coefficient for BLUE
            'L': 1        // Canopy background adjustment
        }
    ).rename('EVI'); // Rename the band to 'EVI'
    return img.addBands(evi);
}
var s2_evi= s2.map(calculateEVI)

// Creamos bandas con las nubes QA_BAND y SCL
function generateMasks(img) {
    // Cloud Score+ Mask
    var cloudScore = img.select(QA_BAND); // Get the cloud score band
    var CMmask = cloudScore.gte(CLEAR_THRESHOLD); // Mask pixels based on cloud probability
    
    // SCL Cloud Mask
    var scl = img.select('SCL'); // Get the SCL band
    var SCLmask = scl.neq(INVALID_SCL_VALUES[0])
                  .and(scl.neq(INVALID_SCL_VALUES[1]))
                  .and(scl.neq(INVALID_SCL_VALUES[2]))
                  .and(scl.neq(INVALID_SCL_VALUES[3])); // Keep valid pixels

    // Return both masks as bands
    return img.addBands(CMmask.rename('CloudScoreMask'))
              .addBands(SCLmask.rename('SCLMask'))
              .set('system:time_start', img.get('system:time_start'));
}

// Apply the mask generation function
var s2_eviWithMasks = s2_evi.linkCollection(csPlus, [QA_BAND]).map(generateMasks);
print(s2_eviWithMasks)

// Add `date` and `datatake_id` properties
var s2_eviWithDate = s2_eviWithMasks.map(function(image) {
    var date = ee.Date(image.get('system:time_start')).format('YYYY-MM-dd');
    return image.set({
        'date': date,
    });
});

print('s2_eviWithDate:', s2_eviWithDate);

// Function to combine CloudScoreMask and SCLMask for all images of a date
function combineMasksForDate(images) {
    // Combine CloudScoreMask and SCLMask
    var combinedMask = images.select('CloudScoreMask').max()
                             .and(images.select('SCLMask').max())
                             .rename('CombinedCloudScoreMask');

    // Apply the combined mask to each image and add it as a band
    var maskedImages = images.map(function(image) {
        return image.addBands(combinedMask); // Add the combined mask to the image
    });

    // Return the list of masked images
    return maskedImages.toList(maskedImages.size());
}

// Group images by date and combine masks
var combinedMasks = ee.ImageCollection(
    ee.List(
        s2_eviWithDate.aggregate_array('date').distinct().map(function(date) {
            // Filter images for the current date
            var imagesForDate = s2_eviWithDate.filter(ee.Filter.eq('date', date));
            
            // Combine masks for the date and return an ImageCollection
            return combineMasksForDate(imagesForDate);
        })
    ).flatten() // Flatten the list of lists into a single list of images
);
print('Combined Masks (ImageCollection):', combinedMasks);

function calculateMask(images){
    var Clouds_score = images.select('CombinedCloudScoreMask');
    var Clouds_mask = Clouds_score.gte(1);
    return images.updateMask(Clouds_mask);
}

var Masked_combinedMasks=combinedMasks.map(calculateMask)

print('Masked ombined Masks (ImageCollection):', Masked_combinedMasks);

Map.centerObject(ROI, 10);
Map.addLayer(ROI, {color: 'red'}, 'ROI Region');

// Add the masked and clipped EVI
var uniqueDates = combinedMasks.aggregate_array('system:time_start').distinct();
Map.centerObject(ROI, 10); // Center the map on the ROI
uniqueDates.evaluate(function(dates) {
    dates.forEach(function(timestamp) {
        var daily_EVI_Clipped = Masked_combinedMasks.filter(ee.Filter.eq('system:time_start', timestamp)).first();
        Map.addLayer(daily_EVI_Clipped.clip(ROI).select('EVI'),
        EVIpalette, 'Masked EVI' + ee.Date(timestamp).format('YYYY-MM-dd').getInfo());
    });
});

// Calculate average EVI for image
var eviPerDate = Masked_combinedMasks.map(function(image) {
    var meanEVI = image.select('EVI')
        .reduceRegion({
            reducer: ee.Reducer.mean(), // Mean EVI for all pixels in the ROI
            geometry: ROI,
            scale: 10, // Sentinel-2 resolution
            maxPixels: 1e9
        }).get('EVI'); // Extract EVI value
    var pixelCount=image.select('EVI')
      .reduceRegion({
            reducer: ee.Reducer.count(),
            geometry: ROI,
            scale: 10,
            maxPixels: 1e9
        }).get('EVI'); // Pixel count for the EVI band
    return ee.Feature(null, {
        'date': ee.Date(image.get('system:time_start')).format('YYYY-MM-dd'),
        'meanEVI': meanEVI,
        'pixelCount': pixelCount
    });
});

// Convert EVI results to a feature collection
var eviPerDateCollection = ee.FeatureCollection(eviPerDate);

// Export results as CSV
Export.table.toDrive({
    collection: eviPerDateCollection,
    description: 'EVI_Per_Date2018',
    folder: 'EVI_EarthEngine_Exports',
    fileFormat: 'CSV'
});
