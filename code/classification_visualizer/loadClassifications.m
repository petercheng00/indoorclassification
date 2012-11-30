function planes = loadClassifications( planes, sortedAtlasFile, imageDir, classificationDirs)
%for each entry in sortedatlasfile
%get camera matrices
%grab associated classifications
%get its plane
%assign to plane


safid = fopen(sortedAtlasFile);

firstLine = fgets(safid);
while ischar(firstLine)
    newPlaneImg = plane_img();
    
    index = strfind(firstLine, '_');
    index = index(end);
    maskFile = firstLine(1:index);
    maskFile = strcat(imageDir, '/', maskFile);
    maskFile = strcat(strrep(maskFile, '\', '/'), 'Mask.bmp');
    newPlaneImg.mask = maskFile;
    
    index = strfind(firstLine, ' ');
    index = index(1);
    imageFile = firstLine(1:index);
    imagePath = strcat(imageDir, '/', firstLine(1:index));
    imagePath = strrep(imagePath, '\', '/');
    newPlaneImg.img = imagePath;
    
    index = strfind(firstLine, ' ');
    index = index(end);
    planeInd = str2double(firstLine(index+1:end));
    
    transLine = fgets(safid);
    transLine = transLine(3:(end-4));
    newPlaneImg.t = transLine;
    
    rotLine = fgets(safid);
    rotLine = rotLine(3:(end-4));
    newPlaneImg.r = quat2rot(rotLine);
    
    %this is hardcoded
    fgets(safid);
    fgets(safid);
    fgets(safid);
    newPlaneImg.K = [612 0 1224; 0 612 1024; 0 0 1];
    
    %now grab related classification matrices
    for classInd = 1:size(classificationDirs, 1)
        classFile = strcat(classificationDirs(classInd,:), '/', imageFile);
        classFile = strrep(classFile, '\', '/');
        classFile = strrep(classFile, '.jpg', '.lt');
        newPlaneImg.classifications{classInd} = classFile;
    end
    
    planes(planeInd+1).images = [planes(planeInd+1).images, newPlaneImg];
    
    firstLine = fgets(safid);
end

fclose(safid);
end

