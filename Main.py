squaredWeight = None
def performCollection(cityLevel, filename):
    import os
    if cityLevel:
        outputDir = 'GoogleTrendsCity/'
        if not os.path.exists(outputDir):
            os.mkdir(outputDir)
    else:
        outputDir = 'GoogleTrendsCountry/'
        if not os.path.exists(outputDir):
            os.mkdir(outputDir)
    
    import pickle
    infile = open(filename,'rb')
    kw_list = pickle.load(infile)
    infile.close()
    
    import time
    from pytrends.request import TrendReq
    pytrends = TrendReq()
    count = 0
    for keyword in kw_list:
        count += 1
        if not '/' in keyword:
            filename = outputDir+ keyword + '.pickle'
            from os import path
            if not path.exists(filename):
                pytrends.build_payload([keyword])
                
                if cityLevel:
                    df = pytrends.interest_by_region(resolution='CITY', inc_low_vol=True, inc_geo_code=False)
                else:
                    df = pytrends.interest_by_region(resolution='COUNTRY', inc_low_vol=True, inc_geo_code=False)
                
                import pickle
                outfile = open(filename,'wb')
                pickle.dump(df,outfile)
                outfile.close()
                #time.sleep(3)
        print(count)

def formCityList(filename):
    filenameToWriteTo = "allCities.pickle"
    from os import path
    if not path.exists(filenameToWriteTo):
        outputDir = 'GoogleTrendsCity/'
        
        import pickle
        infile = open(filename,'rb')
        kw_list = pickle.load(infile)
        infile.close()
        
        count = 0
        allCities = {}
        for keyword in kw_list:
            print(count)
            if count != 897:
                filename = outputDir+ keyword + '.pickle'
                from os import path
                if path.exists(filename):
                    import pickle
                    infile = open(filename,'rb')
                    df = pickle.load(infile)
                    infile.close()
                    
                    if len(df) != 0:
                        cities = list(df['geoName'])
                        latLong = list(df['coordinates'])
                        for i in range(0, len(cities), 1):
                            cityName = cities[i]
                            if not cityName.lower() in allCities:
                                allCities[cityName.lower()] = latLong[i]
            count += 1
            
        import pickle
        outfile = open(filenameToWriteTo,'wb')
        pickle.dump(allCities, outfile)
        outfile.close()

def averageAndStdDevAcrossAssociationsMadeByGoogle(cityLevel, filename):
    import os
    if cityLevel:
        outputDir = 'GoogleTrendsCity/'
        if not os.path.exists(outputDir):
            os.mkdir(outputDir)
    else:
        outputDir = 'GoogleTrendsCountry/'
        if not os.path.exists(outputDir):
            os.mkdir(outputDir)
            
    import os
    import pickle
    infile = open(filename,'rb')
    kw_list = pickle.load(infile)
    infile.close()
    print(len(kw_list))
    count = 0
    valuesReturned = []
    zeroValueCount = 0
    for keyword in kw_list:
        if keyword != 'con':
            filename = outputDir+ keyword + '.pickle'
            from os import path
            if path.exists(filename):
                import pickle
                infile = open(filename,'rb')
                df = pickle.load(infile)
                infile.close()
                try:
                    valuesReturned.append(len(df))
                except:
                    zeroValueCount += 1
                count += 1

    import numpy as np
    print(np.average(valuesReturned))
    print(np.std(valuesReturned))
    print(zeroValueCount)
    print(count)

def assignRegion(cityLevel, filename, outputFile):
    import os
    outputDirAssignRegion = 'AssignRegion/'
    if not os.path.exists(outputDirAssignRegion):
        os.mkdir(outputDirAssignRegion)
    outputDirAssignRegion = 'AssignRegionWeightSquared/'
    if not os.path.exists(outputDirAssignRegion):
        os.mkdir(outputDirAssignRegion)
    outputDirAssignRegion = 'AssignRegion/'
    if squaredWeight:
        outputDirAssignRegion = 'AssignRegionWeightSquared/'
    
    isoToLat, isoToLong = getCountryInfo()
    print(isoToLat)
    print(isoToLong)
    import os
    if cityLevel:
        outputDir = 'GoogleTrendsCity/'
        if not os.path.exists(outputDir):
            os.mkdir(outputDir)
    else:
        outputDir = 'GoogleTrendsCountry/'
        if not os.path.exists(outputDir):
            os.mkdir(outputDir)
            
    import pickle
    infile = open(filename,'rb')
    kw_list = pickle.load(infile)
    infile.close()
    
    noData = 0
    noWeightsOver0 = 0
    rows = [['keyword', 'using top 1', 'using top 3', 'using weight > 50', 'all']]
    keywordToRegion1 = {}
    keywordToRegion2 = {}
    keywordToRegion3 = {}
    keywordToRegion4 = {}
    for keyword in kw_list:
        if keyword != 'con':
            filename = outputDir+ keyword + '.pickle'
            from os import path
            if path.exists(filename):
                import pickle
                infile = open(filename,'rb')
                df = pickle.load(infile)
                infile.close()

                dataReturnedByTrends = False
                try:
                    weights = list(df['value'])
                    weightsValues = []
                    for value in weights:
                        weightsValues.append(value[0])
                    df['weights'] = weightsValues
                    df = df.loc[df['weights'] > 0]
                    dataReturnedByTrends = True
                except:
                    noData += 1
                
                if dataReturnedByTrends:
                    if len(df) > 0:
                        df1 = df.nlargest(1, 'weights')
                        df2 = df.nlargest(3, 'weights')
                        df3 = df.loc[df['weights'] > 50]
                        df4 = df
                        
                        label1 = predictRegion(cityLevel, df1, isoToLong)
                        if label1 != None:
                            keywordToRegion1[keyword] = label1
                        label2 = predictRegion(cityLevel, df2, isoToLong)
                        if label2 != None:
                            keywordToRegion2[keyword] = label2
                        label3 = predictRegion(cityLevel, df3, isoToLong)
                        if label3 != None:
                            keywordToRegion3[keyword] = label3
                        label4 = predictRegion(cityLevel, df4, isoToLong)
                        if label4 != None:
                            keywordToRegion4[keyword] = label4
                        if label1 != None or label2 != None or label3 != None or label4 != None:
                            rows.append([keyword, label1, label2, label3, label4])
                    else:
                        noWeightsOver0 += 1
    print(str(noData) + " out of " + str(len(kw_list)) + " tokens had no data.")
    print(str(noWeightsOver0) + " out of " + str(len(kw_list)) + " tokens had no weights.")
    
    writeRowsToCSV(rows, outputDirAssignRegion+outputFile)
    
    rows = [['Resriction', 'Predictions', 'NA_SA', 'AF_EUR', 'AS_OC', 'Total Accuracy', 'Total Predictions']]
    rows.append(['using top 1']+evaluatePredictions(keywordToRegion1))
    rows.append(['using top 3']+evaluatePredictions(keywordToRegion2))
    rows.append(['using weight > 50']+evaluatePredictions(keywordToRegion3))
    rows.append(['all']+evaluatePredictions(keywordToRegion4))
    
    writeRowsToCSV(rows, outputDirAssignRegion+"Performance"+outputFile)
    
def predictRegion(cityLevel, df, isoToLong):
    import numpy as np
    if cityLevel:
        geoNameToCoordinates = dict(zip(list(df["geoName"]), list(df['coordinates'])))
        geoNameToWeight = dict(zip(list(df["geoName"]), list(df['weights'])))
        
        label = None
        l1 = 0
        l2 = 0
        l3 = 0
        for geoName in geoNameToCoordinates:
            coordinate = geoNameToCoordinates[geoName]
            weight = geoNameToWeight[geoName]
            if squaredWeight:
                weight = weight*weight
            long = coordinate['lng']
            if long <= -25:
                l1 += weight
            elif long <= 65:
                l2 += weight
            else:
                l3 += weight
        Americas = l1
        Africa_Europe = l2
        Asia_Australia = l3
        total = l1+l2+l3
        if total > 0:
            ratioAmericas = float(Americas)/float(total)
            ratioAfrica_Europe = float(Africa_Europe)/float(total)
            ratioAsia_Australia = float(Asia_Australia)/float(total)
            ratioMax = np.max([ratioAmericas, ratioAfrica_Europe, ratioAsia_Australia])
            label = None
            if ratioAmericas == ratioMax:
                label = "Americas"
            elif ratioAfrica_Europe == ratioMax:
                label = "Africa_Europe"
            else:
                label = "Asia_Australia"
        else:
            label = None
    else:
        countryISOCodeToWeight = dict(zip(list(df["geoCode"]), list(df['weights'])))

        label = None
        l1 = 0
        l2 = 0
        l3 = 0
        for countryISOCode in countryISOCodeToWeight:
            weight = countryISOCodeToWeight[countryISOCode]
            long = isoToLong[countryISOCode]
            if long <= -25:
                l1 += weight
            elif long <= 65:
                l2 += weight
            else:
                l3 += weight
        Americas = l1
        Africa_Europe = l2
        Asia_Australia = l3
        total = l1+l2+l3
        if total > 0:
            ratioAmericas = float(Americas)/float(total)
            ratioAfrica_Europe = float(Africa_Europe)/float(total)
            ratioAsia_Australia = float(Asia_Australia)/float(total)
            ratioMax = np.max([ratioAmericas, ratioAfrica_Europe, ratioAsia_Australia])
            label = None
            if ratioAmericas == ratioMax:
                label = "Americas"
            elif ratioAfrica_Europe == ratioMax:
                label = "Africa_Europe"
            else:
                label = "Asia_Australia"
        else:
            label = None
    return label

def getCountryInfo():
    #file with average lat, long for each country
    #country info from: https://gist.github.com/tadast/8827699#file-countries_codes_and_coordinates-csv
    import pandas as pd
    filePath = 'countries_codes_and_coordinates.csv'
    df=pd.read_csv(filePath, encoding='utf-8') 
    print(df.columns)
    temp = list(df["Alpha-2 code"])
    countryList = []
    for isoCode in temp:
        countryList.append(str(isoCode).strip().replace('"', ''))
    latitudeList = []
    temp = list(df['Latitude (average)'])
    for s in temp:
        latitudeList.append(float(s.strip().replace('"', '')))
    longitudeList = []
    temp = list(df['Longitude (average)'])
    for s in temp:
        longitudeList.append(float(s.strip().replace('"', '')))
        
    isoToLat = dict(zip(countryList, latitudeList))
    isoToLong = dict(zip(countryList, longitudeList))
    
    isoToLat['CW'] = 12.1696
    isoToLong['CW'] = -68.9900
    isoToLat['XK'] = 42.6026
    isoToLong['XK'] = 20.9030
    isoToLat['SX'] = 18.0425
    isoToLong['SX'] = -63.0548
    isoToLat['MF'] = 18.0826
    isoToLong['MF'] = -63.0523
    isoToLat['AX'] = 60.1785
    isoToLong['AX'] = 19.9156
    isoToLat['BL'] = 17.9000
    isoToLong['BL'] = -62.8333
    isoToLat['BQ'] = 12.1684
    isoToLong['BQ'] = -68.3082
    
    return isoToLat, isoToLong

def writeRowsToCSV(rows, fileToWriteToCSV):
    import csv
    if len(rows) > 0:
        with open(fileToWriteToCSV, "w", encoding='utf-8') as fp:
            a = csv.writer(fp, delimiter=',')
            a.writerows(rows)
            fp.close()
            print("Written " + str(len(rows)) + " rows to: " + fileToWriteToCSV)

def evaluatePredictions(tokenToPrediction):
    import pandas as pd
    filePath = "Input/combineDBsCoordinateGroundTruthDiv3.csv"
    df=pd.read_csv(filePath, encoding='utf-8') 
    
    tokenToLabel = dict(zip(list(df["id"]), list(df['label'])))

    l1 = 0
    l2 = 0
    l3 = 0
    for token in tokenToPrediction:
        prediction = tokenToPrediction[token]
        if prediction == 'Americas':
            l1 += 1
        elif prediction == 'Africa_Europe':
            l2 += 1
        else:
            l3 += 1
    
    print(str(l1) + ", " + str(l2) + ", " + str(l3) + " Americas vs. Africa_Europe vs. Asia_Australia")

    correct = {'Americas':0,'Africa_Europe':0,'Asia_Australia':0}
    wrong = {'Americas':0,'Africa_Europe':0,'Asia_Australia':0}
    for token in tokenToPrediction:
        label = tokenToLabel[token]
        prediction = tokenToPrediction[token]
        if label == prediction:
            if label == 'Americas':
                correct['Americas'] += 1
            elif label == 'Africa_Europe':
                correct['Africa_Europe'] += 1
            elif label == 'Asia_Australia':
                correct['Asia_Australia'] += 1
            else:
                print("unknown label")
                import sys
                sys.exit()
        else:
            if label == 'Americas':
                wrong['Americas'] += 1
            elif label == 'Africa_Europe':
                wrong['Africa_Europe'] += 1
            elif label == 'Asia_Australia':
                wrong['Asia_Australia'] += 1
            else:
                print("unknown label")
                import sys
                sys.exit()
    
    import numpy as np
    accuracy = float(np.sum(list(correct.values())))/float(np.sum(list(correct.values()))+np.sum(list(wrong.values())))
    row = []
    predictions = []
    for key in ['Americas', 'Africa_Europe', 'Asia_Australia']:
        predictions.append(float(correct[key]+wrong[key]))
    precision = []
    for key in ['Americas', 'Africa_Europe', 'Asia_Australia']:
        precision.append(round(float(correct[key])/float(correct[key]+wrong[key])*100,2))

    row = [str(predictions)]+precision
    row += [round(accuracy*100, 2), float(np.sum(list(correct.values()))+np.sum(list(wrong.values())))]
    
    return row
 
def compareQueryCityLocationVsTopTrendingCityLocation():
    rows = [['query city', 'query city geo', 'top Google Trends city', 'top city geo', 'distance between two']]
    distanceBetweenGoogleQueryCityAndTopCityFromGoogleTrends = []
    noWeightsOver0 = 0
    noData = 0
    filename = "allCities.pickle"
    import pickle
    infile = open(filename,'rb')
    cityToLatLong = pickle.load(infile)
    infile.close()
    
    count = 0
    for cityName in cityToLatLong:
        if not '/' in cityName:
            queryCityCoordinates = (cityToLatLong[cityName]['lat'], cityToLatLong[cityName]['lng'])
            queryCityName = cityName
            outputDir = 'GoogleTrendsCity/'
            filename = outputDir+ cityName + '.pickle'
            from os import path
            if path.exists(filename):
                count += 1
                import pickle
                infile = open(filename,'rb')
                df = pickle.load(infile)
                infile.close()
                
                try:
                    weights = list(df['value'])
                    weightsValues = []
                    for value in weights:
                        weightsValues.append(value[0])
                    df['weights'] = weightsValues
                    df = df.loc[df['weights'] > 0]
                    
                    if len(df) > 0:
                        df1 = df.nlargest(1, 'weights')
                        
                        topGoogleTrendCityCoordinates = list(df1['coordinates'])[0]
                        topGoogleTrendCityName = list(df1['geoName'])[0]
                        topGoogleTrendCityCoordinates = (topGoogleTrendCityCoordinates['lat'], topGoogleTrendCityCoordinates['lng']) 

                        from geopy.distance import geodesic
                        from geopy.distance import great_circle
                        
                        distanceBetweenTheTwo = geodesic(queryCityCoordinates, topGoogleTrendCityCoordinates).miles
                        distanceBetweenGoogleQueryCityAndTopCityFromGoogleTrends.append(distanceBetweenTheTwo)
                        rows.append([queryCityName, str(queryCityCoordinates), topGoogleTrendCityName, str(topGoogleTrendCityCoordinates), distanceBetweenTheTwo])
                    else:
                        noWeightsOver0 += 1
                except:
                    noData += 1
    print(str(noData) + " out of " + str(count) + " tokens had no data.")
    print(str(noWeightsOver0) + " out of " + str(count) + " tokens had no weights.")
    
    import numpy as np
    print(np.average(distanceBetweenGoogleQueryCityAndTopCityFromGoogleTrends))
    print(np.std(distanceBetweenGoogleQueryCityAndTopCityFromGoogleTrends))
    
    writeRowsToCSV(rows, 'topCityAnalysis.csv')

if __name__ == '__main__':
    pass
    
    step1 = False
    if step1:
        performCollection(True, 'Input/459.pickle') #Google Trends at city level
        performCollection(True, 'Input/3183.pickle') #Google Trends at city level
        performCollection(False, 'Input/459.pickle') #Google Trends at country level
        performCollection(False, 'Input/3183.pickle') #Google Trends at country level
    
    '''Google Trends does not always return the same number of cities
    the following code examines average/standard deviation for the number of cities returned'''
    if False:
        averageAndStdDevAcrossAssociationsMadeByGoogle(True, 'Input/459.pickle')
        averageAndStdDevAcrossAssociationsMadeByGoogle(True, 'Input/3183.pickle')
        averageAndStdDevAcrossAssociationsMadeByGoogle(False, 'Input/459.pickle')
        averageAndStdDevAcrossAssociationsMadeByGoogle(False, 'Input/3183.pickle')
        
    step2 = True
    if step2:
        squaredWeight = True #This parameter raises the weight associated by Google via weight=weight*weight
        filename = 'Input/459.pickle'
        outputFilename = '459.csv'
        assignRegion(True, filename, str(True)+outputFilename)
        assignRegion(False, filename, str(False)+outputFilename)
        filename = 'Input/3183.pickle'
        outputFilename = '3183.csv'
        assignRegion(True, filename, str(True)+outputFilename)
        assignRegion(False, filename, str(False)+outputFilename)
    
    '''Google Trends at city resolution associates tokens with city locations
    For each city, the city name and its coordinates are stored in file "allCities.pickle"
    Next we send each city name to Google Trends and utilize the top city result
    For example 'chicago' is sent and the top city result from Google Trends is returned
    The coordinates for both city query and the Google trend city are known
    These coordinates are used to compute distance in miles.
    Over 4789 cities on average the top city result from Google Trends is 362 miles away +/- 1335 miles.
    So Google Trends not same as geocoding, but for query such as Moscow Google is able to capture that
    this query is not likely to be utilized by Russian speakers in Moscow since those would like utilize
    Cyrilis version.
    The results of comparison for each city stored in: topCityAnalysis.csv'''
    step3 = False
    if step3:
        formCityList('Input/3183.pickle') #forms list of cities from Google Trend Associations, stores into "allCities.pickle"
        performCollection(True, "allCities.pickle") #Google Trends at city level
        compareQueryCityLocationVsTopTrendingCityLocation()
        
    