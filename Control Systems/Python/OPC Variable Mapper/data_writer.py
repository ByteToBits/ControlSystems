

# Process 7: Write Data to CSV (Section to be Refactored)
def writeData(dataFile, contentList): 
    try: 
        for fileName, globalVariables in dataFile.items():
          if fileName and globalVariables: 
            stringFileName = fileName.replace('SCADA_', "")
            outputDataDirectory = f'{outputDataDirectory}\\{stringFileName}.csv'
            with open(outputDataDirectory, "w", newline="") as file:
                file.writelines(contentList)     
        # print(f"CSV written to Destination: {outputDataDirectory}")
        print(f"Success: Data Written to CSV Files")
        print("Destination: " + fileName + ".csv")
    except Exception as e: 
        print("Error: Writing Data to Destination - ", e)
        print("Destination: " + fileName)

