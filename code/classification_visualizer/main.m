addpath util

%%%INPUT PARAMETERS%%%

modelFile = 'F:\projects\plane_mapping\plane_mapping_matlab_full\models\nov222011_set1_leftRight_kims_v2_heightsFixed_floorSplit\input_files\nov222011_set1_leftRight_kims_v2_heightsFixed_floorSplit.model';
planesToUse = 22;
sortedAtlasFile = 'F:\projects\plane_mapping\plane_mapping_matlab_full\models\nov222011_set1_leftRight_kims_v2_heightsFixed_floorSplit\input_files\sortedAtlasImages.txt';
imagesDir = 'E:\projects\indoormapping\data\20111122-1\images';
lightClassificationDir = 'temp\classification\dir\1';
windowClassificationDir = 'temp\classification\dir\2';
classificationDirs = [lightClassificationDir; windowClassificationDir];

%%%OUTPUT PARAMETERS%%%
outputDir = 'F:\projects\indoorclassification\data\output\visualized';
outputMapFile = 'tempMap.map';
outputRPInputFile = 'tempRPInput.rpinput';

disp('loading planes');
planes = loadPlanes(modelFile, outputDir);

disp('loading images and classifications');
planes = loadClassifications(planes, sortedAtlasFile, imagesDir, classificationDirs);

disp('preparing output dirs');
setupOutputDirs(outputDir, outputRPInputFile, outputMapFile, modelFile, planes);

disp('ready to begin actual stuff');
for planeInd = 1:size(planesToUse,2)
    planeNum = planesToUse(planeInd);
    disp(['processing plane ', num2str(planeNum)]);
    createVisualization(planes, planeNum);
end