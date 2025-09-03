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

// Function to calculate NDMI
function calculateNDMI(img) {
    var ndmi = img.normalizedDifference(['B8', 'B11']).rename('NDMI');
    return img.addBands(ndmi)}

// Apply NDMI calculation to both seasons
var s2_ndmi_season1 = s2_season1.map(calculateNDMI);
var s2_ndmi_season2 = s2_season2.map(calculateNDMI);

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
var s2_ndmiWithMasks_season1 = s2_ndmi_season1.linkCollection(csPlus, [QA_BAND]).map(generateMasks);
var s2_ndmiWithMasks_season2 = s2_ndmi_season2.linkCollection(csPlus, [QA_BAND]).map(generateMasks);

// Function to apply cloud and shadow masks to NDMI images
function applyMasks(img) {
    var cloudMask = img.select('CloudScoreMask').and(img.select('SCLMask'));
    return img.updateMask(cloudMask); // Apply combined cloud mask
}

// Apply cloud masks to NDMI images for both seasons
var maskedNDMICollection_season1 = s2_ndmiWithMasks_season1.map(applyMasks);
var maskedNDMICollection_season2 = s2_ndmiWithMasks_season2.map(applyMasks);

// Compute seasonal mean NDMI for both seasons
var seasonalMeanNDMI_season1 = maskedNDMICollection_season1.select('NDMI').mean().rename('Mean_NDMI_Season1');
var seasonalMeanNDMI_season2 = maskedNDMICollection_season2.select('NDMI').mean().rename('Mean_NDMI_Season2');

// Clip images to the region of interest
var finalNDMI_season1 = seasonalMeanNDMI_season1.clip(ROI);
var finalNDMI_season2 = seasonalMeanNDMI_season2.clip(ROI);

// Display the seasonal NDMI maps
Map.centerObject(ROI, 10);
Map.addLayer(finalNDMI_season1, {min: -1, max: 1, palette: ['FFFFFF', 'A7D080', '70C25F', '38A700', '006400']}, 'Seasonal Mean NDMI 2024 (Dry)');
Map.addLayer(finalNDMI_season2, {min: -1, max: 1, palette: ['FFFFFF', 'A7D080', '70C25F', '38A700', '006400']}, 'Seasonal Mean NDMI 2023-2024 (Wet)');

// Export NDMI for Season 1 (2024-06-01 to 2024-09-29)
Export.image.toDrive({
    image: finalNDMI_season1,
    description: 'Seasonal_Mean_NDMI_2024_Dry',
    folder: 'EarthEngine_Exports',
    scale: 10, // Sentinel-2 resolution
    region: ROI,
    fileFormat: 'GeoTIFF',
    maxPixels: 1e13
});

// Export NDMI for Season 2 (2023-09-30 to 2024-05-31)
Export.image.toDrive({
    image: finalNDMI_season2,
    description: 'Seasonal_Mean_NDMI_2023-2024_Wet',
    folder: 'EarthEngine_Exports',
    scale: 10, // Sentinel-2 resolution
    region: ROI,
    fileFormat: 'GeoTIFF',
    maxPixels: 1e13
});
