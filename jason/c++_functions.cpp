bool readMADFile(string file, vector<NavigationMeasurement*>& navToFill, vector<ZeroVelocityState>& zuptsToFill)
{
	//open the input file stream; MAD files are binary files
	ifstream mad_file;
	mad_file.open(file.c_str(), ios::in | ios::binary);
	if(!mad_file.is_open()){
		cout << "ERROR opening MAD file: " << file.c_str() << endl;
		return false;
	}

	//MAD file first specifies the zero velocity updates, i.e. times at which the operator was stopped for
	//readucing IMU error.
	//First read in the number of zupts during the data acquisition
	int numZUPTs;
	mad_file.read((char*)&numZUPTs, sizeof(int));

	for(int jj = 0; jj!=numZUPTs; ++jj)
	{
		//read in the start and end time of each zupt
		double startTime, endTime;
		mad_file.read((char*)&startTime, sizeof(double));
		mad_file.read((char*)&endTime, sizeof(double));

		//Note: because the applanix isn't good with the start time: we subtact 3 seconds
		startTime = startTime - 3.0;

		//Store the start and end time of the zupt as a ZeroVelocityState object and add it to the list of ZeroVelocityStates held by the model
		ZeroVelocityState zeroVelState(startTime, endTime);
		zuptsToFill.push_back(zeroVelState);
	}

	//Read in the number of navigation measurements specified by the mad file
	//Each navigation measurement consists of a timestamp, a position, and an orientation.
	int numIMUMeas;
	mad_file.read((char*)&numIMUMeas, sizeof(int));

	//To get the rotations right, we have to apply the following intermediate rotation to each measurement.
	//See John Kua's documentation \\coeus\HOME\jkua\indoormapping\docs\backpackConfig for more details on this intermediate roation.
	mat3 tempIntermediateRot = mat3(vec3(0,1,0), vec3(1,0,0), vec3(0,0,-1));
	MattQuaternion intermediateRot = quatFromRotationMatrix(tempIntermediateRot);  //store the intermediate rotation as a quaternion rather than rotation matrix

	for(int jj = 0; jj!=numIMUMeas; ++jj)
	{

		//Each measurement is a time, position, and orientation.
		//Read in the measurement timestamp, (x,y,z) specifying position, and (roll, pitch, yaw) specifying orientation.
		double time = 0;
		double x,y,z,roll,pitch,yaw;

		mad_file.read((char*)&time, sizeof(double));
		mad_file.read((char*)&x, sizeof(double));
		mad_file.read((char*)&y, sizeof(double));
		mad_file.read((char*)&z, sizeof(double));
		mad_file.read((char*)&roll, sizeof(double));
		mad_file.read((char*)&pitch, sizeof(double));
		mad_file.read((char*)&yaw, sizeof(double));

		//Store everything as a NavigationMeasurement, which will be eventually added to the list of NavigationMeasurements stored by the model.
		NavigationMeasurement* ar = new NavigationMeasurement();

		//once the intermediate roation is applied, quaternion q1 now truly represetns the IMU to world transformation at the current timestamp.
		MattQuaternion q1 = intermediateRot*quatFromYPR(yaw, pitch, roll);
		ar->nav.rotation = q1;  //associate q1 with the NavigationMeasurement ar

		//the position already represents the IMU to world transformation at the current timestamp in meters
		vec3 translation = vec3(x,y,z);
		ar->nav.translation = 1000*translation; // first convert to MM and then associate translation with the NavigationMeasurement ar.

		ar->time = time ; //associate the timestamp with the NavigationMeasurement ar

		navToFill.push_back(ar); //store the NavigationMeasurement ar as part of the list of NavigationMeasurements stored by the model

	}
	mad_file.close();
	return true;
}


inline vec3 ImageInfo::worldToCameraCoords(vec3 p)
{
	return _K * (_rotMat.transpose() * (p - _transVec));
}

inline vec3 ImageInfo::cameraToWorldCoords(vec3 camPt)
{
	return (_rotMat * _K.inverse() * camPt) + _transVec;
}


vec2d Plane::worldToPlaneCoords(vec3 p)
{
	vec3 closestPoint_world = p - ((p - base) * _normal) * _normal;
	vec3 corner_vec = closestPoint_world - base;
	double vert = (corner_vec * (downVec/downVec.length())) / downVec.length();
	double horiz = (corner_vec * (rightVec/rightVec.length())) / rightVec.length();
	return vec2d(horiz * width, vert*height);
}



vec3 Plane::planeToWorldCoords(int row, int col)
{
	return (base + ((double)col/width * rightVec) + ((double)row/height * downVec));
}

vec3 Plane::imageToCameraCoords(Image* im, vec2i p)
{
	double scale = ((-1 * getD()) - im->getTransVec() * getNormal()) / ((im->getRotMat() * im->getK().inverse() * vec3(p.x, p.y, 1)) * getNormal());
	return scale * vec3(p.x, p.y, 1);
}
