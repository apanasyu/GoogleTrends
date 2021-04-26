# GoogleTrends
Project as part of PhD studies at Syracuse University. Method utilizes Google Trends to associated a token with a set of cities or countries (depending on resolution used). Google gives each city/country a weight, from 0 to 100, based on how popular the token was (based on how many search queries, originating from that location, contained the token). Our project applied this resource over Twitter data in order to associate a token with North/South America, Europe/Africa, or Asia/Oceania.

This project inspired by Zola et. al. [1]. Authors attempt to estimate worldwide Twitter user locations without relying on geolocation target labels (no geotagged tweets or user location profiles and no access to geographic dictionaries). Their dataset consisted of 744,830 tweets written by 3,298 users from 54 countries. The location of each user was manually verified. Their approach focuses on nouns (like sites, events, people), which are expected to have a spatial context that is helpful for user location estimation. Each noun was associated with a geographic region based on Google Trends (Google Trends identifies nouns that are trending in various cities). For each user, clustering is used to identify the most probable centroid from coordinates associated with each city. Because no geoinformation is used, the problem is more complex; their approach correctly predicts the ground truth locations of 15%, 23%, 39%, 58%, 70%, 82% of the users for tolerance distances of 250, 500, 1000, 2000, 4000, and 10000 km.

The authors utilize following approach:
- (i) Part of Speech Tagging used to identify a set of nouns for each user.
- (ii) Pytrends Python module is used to associate noun with a list of cities. Google gives each city a weight, from 0 to 100, based on how popular the noun was (based on how many search queries, originating from that city, contained that noun). Cities with 0 score are given a 1 score so that a non-zero value is present for each city. 
- (iii) Google geocoder Python module (used to get lat, long of each city)
- (iv) Scikit-learn Python library (used to get the centroid) the best method is based on K-means and Density-Based Spatial Clustering of Applications with Noise (DBSCAN)
- (v) Centroid compared to known location of user. Median, Mean, and ACC@x (is user within x kilometers of predicted centroid) are recorded across all users.

Our project also utilizes Pytrends. Pytrend is an unofficial library supporting Google Trends. In method interest_by_region() in pytrends/request.py we change the code so that the dataframe is returned immediately after collecting json response from Google. We find that Google, at the 'City’ resolution, does return coordinates for each city, it is just that Pytrends did not accurately capture this information. In this way it is not necessary to geocode each city name (as the geocoding has potential to introduce additional error) and steps (ii) and (iii) can be combined.

There are other differences in that we are focussed on all tokens (not just nouns) and we already have three predefined regions that the world is broken up into (so the accuracy will be judged based on how well a region is predicted as was done in previous section). Google Trends ranking is used to predict a region for a token using:
- (i) For each token, we record the set of cities A that came from the Americas (longitude $\leq$ -25), set of cities B that came from Europe/Africa (-25 $<$ longitude $\leq$ 65), and set of cities C that came from Asia/Oceania (longitude $>$ 65).
- (ii) For each set of cities in A, B, C the cumulative score across the cities in each set are recorded. The cumulative score is based on the ranking returned by Google Trends (Google gives each city a weight based on how popular the token was in city, from 0 to 100).
- (iii) A token is assigned to a region which captured the biggest cumulative score (so no complex clustering required).

Because for our problem the regions are large we can also compare Google Trends performance at the 'Country’ resolution vs. only 'City’. Each country given the average latitude and longitude of its cities based on CSV file [2].

The library dependencies are: geopy, pytrends (Python ver. 3.9 used). This project was coded using Windows 10 operating system (not sure if this affects pickled files).

The code for recording Google Trends:

    kw_list = ['pizza', 'moscow']
    for keyword in kw_list:
      pytrends.build_payload([keyword])
    if city:
        df = pytrends.interest_by_region(resolution='CITY', inc_low_vol=True, inc_geo_code=False)
    else:
        df = pytrends.interest_by_region(resolution='COUNTRY', inc_low_vol=True, inc_geo_code=False)

The collection is performed using a predefined list of keywords in file:

    performCollection(True, 'Input/3183.pickle') #Google Trends at city level
    performCollection(False, 'Input/3183.pickle') #Google Trends at country level

The json results are stored in a pickled file as a pandas dataframe (see full code listing). Working with the pickled file we can retrieve the top ranked result, top 3 results, results with weight > 90, and all results which are in dataframes df1, df2, df3, and df4 (respectively).

    for keyword in kw_list:
        filename = outputDir+ keyword + '.pickle'
        from os import path
        if path.exists(filename):
            import pickle
            infile = open(filename,'rb')
            df = pickle.load(infile)
            infile.close()

            if len(df) != 0:
                weights = list(df['value'])
                weightsValues = []
                for value in weights:
                    weightsValues.append(value[0])
                df['weights'] = weightsValues
                valuesReturned.append(len(df))

                df1 = df.nlargest(1, 'weights')
                df2 = df.nlargest(3, 'weights')
                df3 = df.loc[df['weights'] > 90]
                df4 = df

Finally these are used to assign a region:
- (i) For each token, we record the set of cities A that came from the Americas (longitude <= -25), set of cities B that came from Europe/Africa (-25 < longitude <= 65), and set of cities C that came from Asia/Oceania (longitude > 65).
- (ii) For each set of cities in A, B, C the cumulative score across the cities in each set are recorded. The cumulative score is based on the ranking returned by Google Trends (Google gives each city a weight based on how popular the token was in city, from 0 to 100).
- (iii) A token is assigned to a region which captured the biggest cumulative score.
The labels are evaluated using coordinates from message traffic. The file in Folder Input: combineDBsCoordinateGroundTruthDiv3.csv was generated using code from apanasyu/TwitterMining. The following code is used:

    filename = 'Input/3183.pickle'
    outputFilename = '3183.csv'
    assignRegion(True, filename, str(True)+outputFilename) #city-level
    assignRegion(False, filename, str(False)+outputFilename) #country-level

This results in a file 'True3183.csv' and 'False3183.csv' in folder AssignRegion. For each keyword for which Google Trends contained data a label is computed and compared against label in message traffic dataset. Here is the performance over at the city and country resolution:

![image](https://user-images.githubusercontent.com/80060152/116119716-b9eecf80-a68c-11eb-8559-629ed4da30b2.png)

# GoogleTrends not the same as Geocoding

    formCityList('Input/3183.pickle') #forms list of cities from Google Trend Associations, stores into "allCities.pickle"
    performCollection(True, "allCities.pickle") #Google Trends at city level
    compareQueryCityLocationVsTopTrendingCityLocation()
        
Google Trends at city resolution associates tokens with city locations. For each city, the city name and its coordinates are stored in file "allCities.pickle". Next we send each city name to Google Trends and utilize the top city result. For example 'chicago' is sent and the top city result from Google Trends is returned. Because the coordinates for both city query and the top city via Google trend are known, they can be used to compute distance in miles between the two. The results of comparison for each city stored in: topCityAnalysis.csv. Here is an excerpt from this file:

![image](https://user-images.githubusercontent.com/80060152/116116271-f6203100-a688-11eb-8fd7-56ea4353bcbd.png)

Over 4789 cities on average the top city result from Google Trends is 362 miles away +/- 1335 miles. So Google Trends not same as geocoding, it merely returns the city where the keyword is currently trending which may not coincide with the actual city location. For more information see thesis which is or will soon be uploaded to github.

[1] Zola, Paola, Costantino Ragno, and Paulo Cortez. "A Google Trends spatial clustering approach for a worldwide Twitter user geolocation." Information Processing & Management 57.6 (2020): 102312.

[2] https://gist.github.com/tadast/8827699#file-countries_codes_and_coordinates-csv
