function setupOutputDirs(outputDir, outputRPInputFile, outputMapFile, modelFile, planes);

outputDir = strrep(outputDir, '\', '/');

warning off
mkdir(outputDir);
warning on

rpInputfid = fopen(strcat(outputDir, '/', outputRPInputFile), 'W');
fprintf(rpInputfid, strcat(strrep(modelFile,'\','/'), '\r\n'));
fprintf(rpInputfid, strcat(outputDir, '/', outputMapFile, '\r\n'));
fprintf(rpInputfid, 'noSave');
fclose(rpInputfid);

mapfid = fopen(strcat(outputDir, '/', outputMapFile), 'W');
fprintf(mapfid, [num2str(size(planes,2)), '\n']);
for planeInd = 1:size(planes,2)
    fprintf(mapfid, [num2str(size(planes(planeInd).vertices,2)), '\n']);
    fprintf(mapfid, strcat(strrep(planes(planeInd).outputDir,'\','/'), '/', planes(planeInd).outputImgFile, '\n'));
    for vertInd = 1:size(planes(planeInd).vertices,2)
        fprintf(mapfid, [num2str(planes(planeInd).relCoords(vertInd, 1), 4), ' ', num2str(planes(planeInd).relCoords(vertInd,2),4), '\n']);
    end
end

fclose(mapfid);

