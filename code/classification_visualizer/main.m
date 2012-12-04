addpath util

%%%INPUT PARAMETERS%%%

modelFile = 'F:\projects\indoorclassification\data\input\lbnl\model\revit\lbnlv2.model';

%first plane is plane 1
planesToUse = 1:57;
sortedAtlasFile = 'F:\projects\indoorclassification\data\input\lbnl\output\imagesFile.txt';
imagesDir = 'Y:\data\LBNL\20120312-1\images';
lightClassificationDir = 'Z:\ClassImgOutputs\light\LBNL\20120312-1';
windowClassificationDir = 'Z:\ClassImgOutputs\window';
classificationDirs = {lightClassificationDir, windowClassificationDir};

%%%OUTPUT PARAMETERS%%%
outputDir = 'F:\projects\indoorclassification\data\output\visualized\lbnl';
outputMapFile = 'lbnlMap.map';
outputRPInputFile = 'lbnlRPInput.rpinput';

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
    mkdir(planes(planeNum).outputDir);
    imgFileOut = strcat(planes(planeNum).outputDir, '/', planes(planeNum).outputImgFile);
    imgFileOut = strrep(imgFileOut, '\', '/');
    imwrite(planes(planeNum).outputImg, imgFileOut);
end