function loadedPlanes = loadPlanes( model_file, outputDir)

    model = dlmread(model_file, ' ');
    numPlanes = model(1);
    linenum = 2;
    
    loadedPlanes = [];
    
    for pnum = 1:numPlanes
        newPlane = plane();
          
        numcorners = model(linenum,1);
        inputnormal = model(linenum+1,1:3);
        inputnormal = inputnormal/norm(inputnormal);
        %plane_offset = model(linenum+1,4);
        vertices = model(linenum+2:linenum+numcorners+1,1:3);

        %turns out model file normals are UNTRUSTWORTHY
        %however they still have normals facing the right side of the plane
        %offset is garbage though
        side1 = vertices(end,:) - vertices(1,:);
        s = 1;
        side2 = vertices(s,:) - vertices(s+1,:);
        normal = cross(side1,side2);
        while (sum(normal) == 0)
            s = s + 1;
            side1 = vertices(s-1,:) - vertices(s,:);
            side2 = vertices(s,:) - vertices(s+1,:);
            normal = cross(side1,side2);
        end
        normal = normal/norm(normal);
        if dot(normal, inputnormal) < 0
            normal = -1 * normal;
        end
        if abs(normal(3) - 1) < 0.001
            normal(3) = 1;
        end
        if abs(normal(3) + 1) < 0.001
            normal(3) = -1;
        end
        plane_offset = -1 * dot(vertices(1,:),normal);
        [bbCorners,relCoords] = calculate_bounding_box(vertices,normal);


           
        planeCorners = bbCorners' .* 1000;

        % Visualize the plane in 3D space
        center = [mean(vertices(:,1)), mean(vertices(:,2)), mean(vertices(:,3))];
        normalEnd = [center(1,1) + 10*normal(1), center(1,2) + 10*normal(2), center(1,3) + 10*normal(3) ];
        plot3(0,0,0,'kx')
        patch(bbCorners(:,1),bbCorners(:,2),bbCorners(:,3),'c');
        hold on;
        patch(vertices(:,1)+0.1*normal(1),vertices(:,2)+0.1*normal(2),vertices(:,3)+0.1*normal(3),'k');
        line([center(1), normalEnd(1)], [center(2), normalEnd(2)], [center(3), normalEnd(3)], 'linewidth', 5)
        axis('equal')
        hold off;
        drawnow

        % We want plane corners arranged like this
        % 2   3 
        % 1   4
        % Normal should be pointing out the screen at you


        newPlane.vertices = vertices' .* 1000 ;
        newPlane.bbCorners = planeCorners;
        newPlane.relCoords = relCoords;
        newPlane.base = planeCorners(:,2);
        newPlane.down = planeCorners(:,1) - newPlane.base;
        newPlane.side = planeCorners(:,3) - newPlane.base;
        newPlane.normal = normal';
        newPlane.d = plane_offset * 1000;

        newPlane.outputDir = strcat(outputDir, '/', num2str(pnum));
        newPlane.outputImgFile = 'img.jpg';
        
        % Ratio is the number of pixels per centemeter or something. I'm not entirely sure. Just make
        % it larger if you want higher-resolution planes
        newPlane.ratio = 0.10;
        % Width and height of the plane in pixels
        newPlane.width = round(newPlane.ratio*norm(newPlane.side));
        newPlane.height = round(newPlane.ratio*norm(newPlane.down));

        pnum = pnum + 1; 
        linenum = linenum + numcorners + 2;
        loadedPlanes = [loadedPlanes newPlane];
    end
end

