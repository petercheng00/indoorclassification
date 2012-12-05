function createVisualization(planes, planeNum);

p = planes(planeNum);

p.outputImg = zeros(p.height, p.width, 3);
numVotes = zeros(p.height, p.width);
plane_pts = getPlanePtsOnPlane(p);
world_pts = getWorldPtsFromPlanePts(p, plane_pts);

%masks = zeros(p.height, p.width, 0);
%maskInd = 1;

for imgInd = 1:size(p.images,2)

    disp(['plane ', num2str(planeNum), ', img ', num2str(imgInd), ' of ', num2str(size(p.images,2))]);
    i = p.images(imgInd);
    if (exist(i.img, 'file') ~= 2)
        continue;
    end
    camDir = i.r * [0;0;1];
    angleQuality = camDir' * p.normal;
    if (angleQuality > -0.75 && angleQuality < 0.75)
        continue;
    end
    cameraPts = getCameraPtsFromWorldPts(i, world_pts);
    validPts = logical(getValidPts(i, cameraPts));
    imagePts = getImagePtsFromCameraPts(cameraPts);
    imagePts_linear = linearizePts(i, imagePts);
    imagePts_linear = imagePts_linear(validPts);
    
    %imageData = imread(i.img);
    validPts = reshape(validPts, size(p.outputImg(:,:,1)));
        
    for cInd = 1:size(i.classifications,2)
        if (exist(i.classifications{cInd}, 'file') == 2)
            clData = load(i.classifications{cInd}, '-mat');
            if (cInd == 1)
                clData = clData.tmpImg;
            else
                clData = clData.imgClass;
            end
            
            %update counts
            numVotes(validPts) = numVotes(validPts) + 1;
            
            newVotes = clData(imagePts_linear)';
            
            %convert from 1, 0, to 1, -1
            if sum(sum(newVotes)) == 0
                continue;
            end
            
            
            %newVotes = newVotes * (numel(newVotes)/sum(sum(newVotes)));
            newVotes = newVotes * 5;
            newVotes = newVotes - 1;
            currClassMask = zeros(p.height, p.width);
            currClassMask(validPts) = newVotes;
            
            p.outputImg(:,:,1) = p.outputImg(:,:,1) + currClassMask;
            
            %masks(:,:,maskInd) = currClassMask;
            %maskInd = maskInd + 1;
            
        end
    end
    
    %%Image Method
    %
    %keyboard
    %for chan = 1:3
    %    tmp_img = imageData(:,:,chan);
    %    tmp_dest = p.outputImg(:,:,chan);
    %    tmp_dest(validPts) = tmp_img(imagePts_linear)';
    %    p.outputImg(:,:,chan) = tmp_dest;
    %end
end

%save('allMasks', 'masks', '-v7.3');

p.outputImg(:,:,1) = max(p.outputImg(:,:,1),0);
p.outputImg(:,:,1) = p.outputImg(:,:,1) ./ numVotes;

maxVal = max(max(p.outputImg(:,:,1)));
p.outputImg = p.outputImg / maxVal;
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


