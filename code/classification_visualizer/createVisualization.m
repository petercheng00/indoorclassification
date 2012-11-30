function createVisualization(planes, planeNum);

p = planes(planeNum);

p.outputImg = zeros(p.height, p.width, 3);

plane_pts = getPlanePtsOnPlane(p);
world_pts = getWorldPtsFromPlanePts(p, plane_pts);

for imgInd = 1:size(p.images,2)
    i = p.images(imgInd);
    
    cameraPts = getCameraPtsFromWorldPts(i, world_pts);
    validPts = logical(getValidPts(i, cameraPts));
    imagePts = getImagePtsFromCameraPts(cameraPts);
    imagePts_linear = linearizePts(i, imagePts);
    imagePts_linear = imagePts_linear(validPts);
    
    
    
    testImg = zeros(p.height, p.width, 1);
    validPts = reshape(validPts, size(testImg(:,:,1)));
    
    keyboard
    
    for cInd = 1:size(i.classifications,1)
        %clData = load(i.classifications{cInd}, '-mat');
        clData = load('Z:\ClassImgOutputs\light\CoryHall\20121119-1\leftCameraPostProcessed\left\Camera_110732781_Image001794.lt', '-mat');
        clData = clData.tmpImg;
        testImg(validPts) = clData(imagePts_linear);
    end
    keyboard
        
    
    %%%Image Method
    %imageData = imread(i.img);
    %for chan = 1:3
    %    tmp_img = imageData(:,:,chan);
    %    tmp_dest = testImg(:,:,chan);
    %    tmp_dest(validPts) = tmp_img(imagePts_linear);
    %    testImg(:,:,chan) = tmp_dest;
    %end
    
    keyboard

end

end

function im_pts_linear = linearizePts(i, im_pts)
   [h w c] = size(imread(i.img));
   im_pts_linear = uint32(im_pts(2,:) +  h*(im_pts(1,:)-1));
end


function does_contain_point = getValidPts(i, camera_pts)
   im_pts = getImagePtsFromCameraPts(camera_pts);
   does_contain_point = logical(camera_pts(3,:) > 0.001);
   [h w c] = size(imread(i.img));
   does_contain_point = does_contain_point .* (im_pts(1,:) >= 1);
   does_contain_point = does_contain_point .* (im_pts(1,:) <= w);
   does_contain_point = does_contain_point .* (im_pts(2,:) >= 1);
   does_contain_point = does_contain_point .* (im_pts(2,:) <= h);
   im_pts_linear = linearizePts(i, im_pts);
   
   maskData = imread(i.mask) > 0;
   isinmask = maskData(im_pts_linear(logical(does_contain_point)));
   does_contain_point(logical(does_contain_point)) = isinmask;
   does_contain_point = logical(does_contain_point);

end

function im_pts = getImagePtsFromCameraPts(camera_pts)
   im_pts(1,:) = round(camera_pts(1,:) ./ camera_pts(3,:));
   im_pts(2,:) = round(camera_pts(2,:) ./ camera_pts(3,:));
end

function camera_pts = getCameraPtsFromWorldPts(i, world_pts)
   npoints = size(world_pts,2);
   camera_pts = i.r'*(world_pts - repmat(i.t', [1, npoints]));
   camera_pts = i.K*camera_pts;
end

function world_pts = getWorldPtsFromPlanePts(p, planePts)
    npoints = size(planePts,2);
    world_pts = repmat(p.base, [1,npoints]);
    world_pts = world_pts + ...
        repmat(planePts(1,:) / p.height, [3,1]) .* ...
        repmat(p.down, [1,npoints]);
    world_pts = world_pts + ...
        repmat(planePts(2,:) / p.width, [3,1]) .* ...
        repmat(p.side, [1,npoints]);
end

function plane_pts = getPlanePtsOnPlane(p)
    [jj ii] = meshgrid(1:p.width, 1:p.height);
    npoints = numel(ii);
    ivec = reshape(ii, [1,npoints]);
    jvec = reshape(jj, [1,npoints]);
    plane_pts = [ivec ; jvec];
end


