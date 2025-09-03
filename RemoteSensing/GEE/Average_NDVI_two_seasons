// Region of Interest (ROI)
var ROI = ee.FeatureCollection("projects/keen-ascent-439714-i6/assets/Pinof_24-25_PPA");

// Load Sentinel-2 Images for Both Seasons
var s2_season1 = ee.ImageCollection('COPERNICUS/S2_SR_HARMONIZED')
    .filterBounds(ROI)
    .filterDate('2024-06-01', '2024-09-30'); // 2024 Dry Season

var s2_season2 = ee.ImageCollection('COPERNICUS/S2_SR_HARMONIZED')
    .filterBounds(ROI)
    .filterDate('2023-10-01', '2024-05-31'); // 2023-2024 Wet Season

// Load Cloud Score+
var csPlus = ee.ImageCollection('GOOGLE/CLOUD_SCORE_PLUS/V1/S2_HARMONIZED');

// Define thresholds for cloud and shadow masking
var QA_BAND = 'cs_cdf';
var INVALID_SCL_VALUES = [3, 8, 9, 10]; // Cloud shadow, cirrus, and snow
var CLEAR_THRESHOLD = 0.60;

// Function to calculate NDVI
function calculateNDVI(img) {
    var ndvi = img.normalizedDifference(['B8', 'B4']).rename('NDVI');
    return img.addBands(ndvi);
}

// Apply NDVI calculation to both seasons
var s2_ndvi_season1 = s2_season1.map(calculateNDVI);
var s2_ndvi_season2 = s2_season2.map(calculateNDVI);

// Function to generate cloud and shadow masks
function generateMasks(img) {
    // Cloud Score+ Mask
    var cloudScore = img.select(QA_BAND);
    var CMmask = cloudScore.gte(CLEAR_THRESHOLD); // Mask high cloud probability pixels
    
    // SCL Cloud Mask
    var scl = img.select('SCL');
    var SCLmask = scl.neq(INVALID_SCL_VALUES[0])
                     .and(scl.neq(INVALID_SCL_VALUES[1]))
                     .and(scl.neq(INVALID_SCL_VALUES[2]))
                     .and(scl.neq(INVALID_SCL_VALUES[3])); // Keep valid pixels

    // Return both masks as bands
    return img.addBands(CMmask.rename('CloudScoreMask'))
              .addBands(SCLmask.rename('SCLMask'))
              .set('system:time_start', img.get('system:time_start'));
}

// Apply cloud masking function to both seasons
var s2_ndviWithMasks_season1 = s2_ndvi_season1.linkCollection(csPlus, [QA_BAND]).map(generateMasks);
var s2_ndviWithMasks_season2 = s2_ndvi_season2.linkCollection(csPlus, [QA_BAND]).map(generateMasks);

// Function to apply cloud and shadow masks to NDVI images
function applyMasks(img) {
    var cloudMask = img.select('CloudScoreMask').and(img.select('SCLMask'));
    return img.updateMask(cloudMask); // Apply combined cloud mask
}

// Apply cloud masks to NDVI images for both seasons
var maskedNDVICollection_season1 = s2_ndviWithMasks_season1.map(applyMasks);
var maskedNDVICollection_season2 = s2_ndviWithMasks_season2.map(applyMasks);

// Compute seasonal mean NDVI for both seasons
var seasonalMeanNDVI_season1 = maskedNDVICollection_season1.select('NDVI').mean().rename('Mean_NDVI_Season1');
var seasonalMeanNDVI_season2 = maskedNDVICollection_season2.select('NDVI').mean().rename('Mean_NDVI_Season2');

// Clip images to the region of interest
var finalNDVI_season1 = seasonalMeanNDVI_season1.clip(ROI);
var finalNDVI_season2 = seasonalMeanNDVI_season2.clip(ROI);

// Display the seasonal NDVI maps
Map.centerObject(ROI, 10);
Map.addLayer(finalNDVI_season1, {min: -1, max: 1, palette: ['FFFFFF', 'A7D080', '70C25F', '38A700', '006400']}, 'Seasonal Mean NDVI 2024 (Dry)');
Map.addLayer(finalNDVI_season2, {min: -1, max: 1, palette: ['FFFFFF', 'A7D080', '70C25F', '38A700', '006400']}, 'Seasonal Mean NDVI 2023-2024 (Wet)');

// Export NDVI for Season 1 (2024-06-01 to 2024-09-29)
Export.image.toDrive({
    image: finalNDVI_season1,
    description: 'Seasonal_Mean_NDVI_2024_Dry',
    folder: 'EarthEngine_Exports',
    scale: 10, // Sentinel-2 resolution
    region: ROI,
    fileFormat: 'GeoTIFF',
    maxPixels: 1e13
});

// Export NDVI for Season 2 (2023-09-30 to 2024-05-31)
Export.image.toDrive({
    image: finalNDVI_season2,
    description: 'Seasonal_Mean_NDVI_2023-2024_Wet',
    folder: 'EarthEngine_Exports',
    scale: 10, // Sentinel-2 resolution
    region: ROI,
    fileFormat: 'GeoTIFF',
    maxPixels: 1e13
});
