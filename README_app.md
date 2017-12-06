# Leverage Population Health Data

Please refer to the documentation in the *Final Delivery* directory for
instructions on how to run the entire project, including sample EHR server
(CDS Hooks Sandbox), FHIR server, and referral web app. In particular,
the *Special Instructions* and *Manual* have installation and usage info.

You should only use the following instructions when running just the
referral web app as a standalone application.

### How to run the referral web app

1. git clone this repo
2. cd to the current directroy
3. Set your BASE_URL where the app will run.
	```
	export BASE_URL=http://example.com
	```

3. **OPTION 1:** Run in Docker (Recommended):<br>
	a. Build Docker image: 
	```
	sudo docker build -t lphd_webapp:latest .
	```
	b. Run the webapp on port 5000 mapping it to port 5000 of the container:
	```
	sudo docker run -d -p 5000:5000 lphd_webapp
	```

4. **OPTION 2:** Run natively (Faster to run everytime, better for developing):<br>
	a. Install dependencies (this is a one time setup)
	```
	pip install -r requirements.txt
	```
	b. Run the app  (this should start your service):
	```
	python app.py
	```
	
5. Query the service using a URL Like: 
	```
	$BASE_URL:5000/patient?user_id=075786e8-383c-4eee-abb6-264b3b967482&conditions=high_blood_pressure
	```
