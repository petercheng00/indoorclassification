addpath util

%%%INPUT PARAMETERS%%%

modelFile = 'F:\projects\indoorclassification\data\input\cory3rdfloor\model\revit\cory3rdfloorv4.model"';

%in here, Z corresponds to \\amol\CS280FinalProject
%Y corresponds to \\behshahr\indoormapping



%first plane is plane 1
planesToUse = 1:48;
sortedAtlasFile = 'F:\projects\indoorclassification\data\input\cory3rdfloor\model\revit\output\imagesFile.txt';
imagesDir = 'Y:\data\CoryHall\20121119-1\images';
lightClassificationDir = 'Z:\ClassImgOutputs\light\CoryHall\20121119-1';
windowClassificationDir = 'Z:\ClassImgOutputs\window';
classificationDirs = {lightClassificationDir, windowClassificationDir};

%%%OUTPUT PARAMETERS%%%
outputDir = 'F:\projects\indoorclassification\data\output\visualized\cory';
outputMapFile = 'coryMap.map';
outputRPInputFile = 'coryRPInput.rpinput';

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