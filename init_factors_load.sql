DO $$
DECLARE directory TEXT := 'D:\Shared Documents\Work\Clients\Si Chen\open-climate-investing\data';

BEGIN
	EXECUTE '
		COPY ff_factor FROM ''' || directory || '\ff_factors.csv'' WITH (FORMAT CSV, HEADER);
		COPY carbon_risk_factor FROM ''' || directory || '\carbon_risk_factor.csv'' WITH (FORMAT CSV, HEADER);
		COPY risk_free FROM ''' || directory || '\risk_free.csv'' WITH (FORMAT CSV, HEADER)';
END $$;