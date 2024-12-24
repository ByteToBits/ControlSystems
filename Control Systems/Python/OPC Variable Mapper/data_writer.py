

def writeDataToCSV(outputPath, dataFile, contentList): 

    for fileName, globalVariables in dataFile.items():
        if fileName and globalVariables: 
            stringFileName = fileName.replace('SCADA_', "")
            outputDataFile = f'{outputPath}\\{stringFileName}.csv'
        with open(outputDataFile, "w", newline="") as file:
            file.writelines(contentList) 

    # print(f"CSV written to Destination: {outputDataDirectory}")
    print(f"Success: Data Written to CSV Files")
    print("Destination: " + fileName + ".csv")



