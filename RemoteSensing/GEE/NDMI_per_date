// Region of interest
var ROI = ee.FeatureCollection("projects/keen-ascent-439714-i6/assets/Pinof_24-25_PPA");

// Descargamos las imágenes sentinel
var s2 = ee.ImageCollection('COPERNICUS/S2_SR_HARMONIZED')
    .filterBounds(ROI)
    .filterDate('2019-01-01', '2019-06-01');

// Paleta de colores NDMI
var NDMIpalette = [
  'FFFFFF', // White for very low NDI
  'A7D080', // Light green
  '70C25F', // Medium green
  '38A700', // Darker green
  '006400'  // Dark green for high NDMI
];

// Cargamos Cloud Score+
var csPlus = ee.ImageCollection('GOOGLE/CLOUD_SCORE_PLUS/V1/S2_HARMONIZED');

// Cargamos los umbrales numéricos
var QA_BAND = 'cs_cdf';
var INVALID_SCL_VALUES = [3, 8, 9, 10];
var CLEAR_THRESHOLD = 0.60;

// Calculamos el NDMI y lo añadimos
function calculateNDMI(img) {
    var ndmi = img.normalizedDifference(['B8', 'B11']).rename('NDMI');
    return img.addBands(ndmi)}
var s2_ndmi= s2.map(calculateNDMI)

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
var s2_ndmiWithMasks = s2_ndmi.linkCollection(csPlus, [QA_BAND]).map(generateMasks);
print(s2_ndmiWithMasks)

// Add `date` and `datatake_id` properties
var s2_ndmiWithDate = s2_ndmiWithMasks.map(function(image) {
    var date = ee.Date(image.get('system:time_start')).format('YYYY-MM-dd');
    return image.set({
        'date': date,
    });
});

print('s2_ndmiWithDate:', s2_ndmiWithDate);

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
        s2_ndmiWithDate.aggregate_array('date').distinct().map(function(date) {
            // Filter images for the current date
            var imagesForDate = s2_ndmiWithDate.filter(ee.Filter.eq('date', date));
            
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

// Add the masked and clipped NDMI
var uniqueDates = combinedMasks.aggregate_array('system:time_start').distinct();
Map.centerObject(ROI, 10); // Center the map on the ROI
uniqueDates.evaluate(function(dates) {
    dates.forEach(function(timestamp) {
        var daily_NDMI_Clipped = Masked_combinedMasks.filter(ee.Filter.eq('system:time_start', timestamp)).first();
        Map.addLayer(daily_NDMI_Clipped.clip(ROI).select('NDMI'),
        NDMIpalette, 'Masked NDMI' + ee.Date(timestamp).format('YYYY-MM-dd').getInfo());
    });
});

// Calculate average NDMI for image
var ndmiPerDate = Masked_combinedMasks.map(function(image) {
    var meanNDMI = image.select('NDMI')
        .reduceRegion({
            reducer: ee.Reducer.mean(), // Mean NDMI for all pixels in the ROI
            geometry: ROI,
            scale: 10, // Sentinel-2 resolution
            maxPixels: 1e9
        }).get('NDMI'); // Extract NDMI value
    var pixelCount=image.select('NDMI')
      .reduceRegion({
            reducer: ee.Reducer.count(),
            geometry: ROI,
            scale: 10,
            maxPixels: 1e9
        }).get('NDMI'); // Pixel count for the NDMI band
    return ee.Feature(null, {
        'date': ee.Date(image.get('system:time_start')).format('YYYY-MM-dd'),
        'meanNDMI': meanNDMI,
        'pixelCount': pixelCount
    });
});

// Convert NDMI results to a feature collection
var ndmiPerDateCollection = ee.FeatureCollection(ndmiPerDate);

// Export results as CSV
Export.table.toDrive({
    collection: ndmiPerDateCollection,
    description: 'NDMI_Per_Date2018',
    folder: 'NDMI_EarthEngine_Exports',
    fileFormat: 'CSV'
});
