import os
from PIL import Image
from PIL.ExifTags import TAGS
from PIL.ExifTags import GPSTAGS
import tkinter
from PIL import ImageTk

currentDir = os.getcwd()
dataPaths = list()
data = list()


class Explorer:

    def __init__(self):
        self.allList = list()  # list of all scanned items or item paths
        self.dirList = list()  # list of all folders or folder paths
        self.fileList = list()  # list of all files or files paths

    def clearData(self):
        self.allList = list()
        self.dirList = list()
        self.fileList = list()

    def scanPaths(self, inputDir, depth=""):
        # a list of all folder and file names in inputDirectory
        surfaceItems = os.listdir(inputDir)

        # for the list of all items, join the path to the directory & separate
        # to file or directory list as a useable path.
        for i in range(0, len(surfaceItems)):
            # make a full path and add to self.allList
            fullPath = os.path.join(inputDir, surfaceItems[i])
            self.allList.append(fullPath)

            if depth == "deep":
                # if there is a directory within another directory, recurse
                if os.path.isdir(fullPath):
                    self.scanPaths(fullPath, "deep")

    def splitItems(self):
        # separate items into separate lists of folders and files
        if len(self.dirList) == 0 or len(self.fileList) == 0:
            for i in range(0, len(self.allList)):
                if os.path.isdir(self.allList[i]):
                    self.dirList.append(self.allList[i])

                elif os.path.isfile(self.allList[i]):
                    self.fileList.append(self.allList[i])

    def itemNameOnly(self, dataList):
        # remove path names and only have base names
        if dataList == "allList":
            for i in range(0, len(self.allList)):
                self.allList[i] = os.path.basename(self.allList[i])

        if dataList == "allList" or "dirList":
            for i in range(0, len(self.dirList)):
                self.dirList[i] = os.path.basename(self.dirList[i])

        if dataList == "allList" or "fileList":
            for i in range(0, len(self.fileList)):
                self.fileList[i] = os.path.basename(self.fileList[i])

    def countItemType(self):
        # show count number for documents and files
        self.dirCount = int()
        self.fileCount = int()

        for i in self.allList:
            if os.path.isdir(i):
                self.dirCount += 1

            elif os.path.isfile(i):
                self.fileCount += 1

    def returnData(self, rType="print", rData="all", path=""):
        # with rType on rData:
        #   with "return", "print" or "length" (number of rData)
        #   on "all", "files" or "folers"
        #   path set to none, but if "yes", will print full path names
        # kind of information needed

        if rType == "return":
            if rData == "all":
                return self.allList

            elif rData == "files" or "folders":
                self.splitItems()

                if rData == "folders":
                    return self.dirList

                elif rData == "files":
                    return self.fileList

        elif rType == "print":
            self.splitItems()

            if rData == "all":
                if path == "noPath":
                    self.itemNameOnly("allList")
                print("===== Folders =====")
                print(*self.dirList, sep="\n")
                print("\n===== Files =====")
                print(*self.fileList, sep="\n")

            elif rData == "folders":
                if path == "noPath":
                    self.itemNameOnly("dirList")
                print("===== Folders =====")
                print(*self.dirList, sep="\n")

            elif rData == "files":
                if path == "noPath":
                    self.itemNameOnly("fileList")
                print("===== Files =====")
                print(*self.fileList, sep="\n")

        elif rType == "length":
            self.countItemType()
            if rData == "all":
                print(str(self.dirCount) + " folders")
                print(str(self.fileCount) + " files")

            elif rData == "folders":
                print(str(self.dirCount) + " folders")

            elif rData == "files":
                print(str(self.fileCount) + " files")


class ExifTool:
    noExifData = list()  # list of files with no exif data - Not saved as txt
    noSpecificData = list()  # list of files with no specific exif data
    gpsKeyError = list()

    def __init__(self):
        self.exifDataGPSCoords = tuple()

    def returnExif(self, file):
        image = Image.open(file)
        image.verify()  # quick check if the image is corrupted
        rawData = image.getexif()  # get the exif data
        image.close()  # do I need this?  Seems to work without it

        if not rawData:
            # if no exif data, note which file, notify user and end function
            ExifTool.noExifData.append(file)
            # print("No EXIF data for " + file)
            return
        else:
            return rawData  # nothing saved, straight output

    def labelledExif(self, file):
        rawData = self.returnExif(file)  # run the exifReturn function

        # if no exif data, end function.  User has already been notified.
        if not rawData:
            return

        # exifDataLabelled = dict()  # clear whatever was there before
        exifDataLabelled = dict()
        for (key, val) in rawData.items():
            exifDataLabelled[TAGS.get(key)] = val

        if "MakerNote" in exifDataLabelled:
            # optional because this appears to be unnecessary and cluttered
            del exifDataLabelled["MakerNote"]  # faster than if != "MakerNote"

        return exifDataLabelled

    def GPSExif(self, file):
        rawData = self.returnExif(file)  # run the exifReturn function

        # if no exif data, end function.  User has already been notified.
        if not rawData:
            return

        exifDataGeoTagged = dict()
        for (idx, tag) in TAGS.items():
            if tag == "GPSInfo":
                if idx not in rawData:
                    exifTool.noSpecificData.append(file)
                    # print("No GPS data for " + file)
                    return
                else:
                    for (key, val) in GPSTAGS.items():
                        if key in rawData[idx]:
                            exifDataGeoTagged[val] = rawData[idx][key]

        return exifDataGeoTagged

    def convertDecimal(self, dms, ref):
        if not dms and not ref:
            return
        else:
            # converts GPS location from lat/long dms to a single decimal
            degrees = dms[0][0] / dms[0][1]
            minutes = dms[1][0] / dms[1][1] / 60.0
            seconds = dms[2][0] / dms[2][1] / 3600.0

            if ref in ['S', 'W']:
                degrees = -degrees
                minutes = -minutes
                seconds = -seconds

            return round(degrees + minutes + seconds, 5)

    def GPSCoords(self, file):
        gpsData = self.GPSExif(file)
        if not gpsData:
            return
        else:
            try:
                lat = self.convertDecimal(gpsData['GPSLatitude'],
                                          gpsData['GPSLatitudeRef'])
                lon = self.convertDecimal(gpsData['GPSLongitude'],
                                          gpsData['GPSLongitudeRef'])

                return (lat, lon)
            except KeyError:
                return "KeyError"


def display():
    global data

    cWidth = 1152
    cHeight = 800

    root = tkinter.Tk()
    root.title("Photo GPS Extract, Save, Display and Drive Explorer")
    display = tkinter.Canvas(root, width=cWidth, height=cHeight)
    display.pack()

    importImg = Image.open("Kagawa.png")
    KagawaMap = ImageTk.PhotoImage(importImg)
    importImg.close()
    display.create_image(0, 0, anchor=tkinter.NW, image=KagawaMap)

    ox = 133.412  # GPS coordinates of origin x point (longitude) - eyeballed
    oy = 34.587  # GPS coordinates of origin y point (latitude) - eyeballed
    scaleX = 1069.2408  # image width / ((originX + refPointX) / 2)
    scaleY = -1300.6015  # image height / ((originY + refPointY) / 2)

    images = []  # to hold the newly created image

    def create_rectangle(x1, y1, x2, y2, **kwargs):
        if 'alpha' in kwargs:
            # take alpha and fill, remove words and take numbers.
            alpha = int(kwargs.pop('alpha') * 255)
            fill = kwargs.pop('fill')
            # tkinter return tuple of RGB and add alpha as tuple element
            fill = root.winfo_rgb(fill) + (alpha,)
            # PIL new image called RGBA at width, height, with RGBA input
            image = Image.new('RGBA', (x2-x1, y2-y1), fill)
            # add new image to images list to display
            images.append(ImageTk.PhotoImage(image))
            # display last image in list before displaying new image
            display.create_image(x1, y1, image=images[-1], anchor='nw')
        display.create_rectangle(x1, y1, x2, y2, outline="", **kwargs)

    for i in range(0, len(data)):
        inputX = data[i][1]
        inputY = data[i][0]

        xPos = (inputX - ox) * scaleX
        yPos = (inputY - oy) * scaleY

        dotX1 = int(xPos - 2)
        dotX2 = int(xPos + 2)
        dotY1 = int(yPos - 2)
        dotY2 = int(yPos + 2)

        create_rectangle(dotX1, dotY1, dotX2, dotY2, fill="red", alpha=.05)

    display.quit()

    display.mainloop()


scanner = Explorer()
exifTool = ExifTool()


def runProgram():
    global currentDir
    global dataPaths
    global data

    while True:
        print("\nCurrently in " + currentDir, end="\n\n")
        print("\nall, folders, files, count, GPSData, display (after GPSData)," +
              " print data,\n<folder name>, back, exit")
        userInput = input()

        if userInput == "exit":
            print("Laters.")
            break

        elif userInput == "back":
            currentDir = os.path.dirname(currentDir)
            scanner.clearData()
            scanner.scanPaths(currentDir)
            scanner.returnData("print", "folders", "noPath")
            if len(scanner.dirList) == 0:
                print("No folders.")

        elif userInput == "count":
            scanner.clearData()
            scanner.scanPaths(currentDir, "deep")
            scanner.returnData("length", "all")

        elif userInput == "all":
            scanner.clearData()
            scanner.scanPaths(currentDir)
            scanner.returnData("print", "all", "noPath")

        elif userInput == "folders":
            scanner.clearData()
            scanner.scanPaths(currentDir)
            scanner.returnData("print", "folders", "noPath")
            if len(scanner.dirList) == 0:
                print("No folders.")

        elif userInput == "files":
            scanner.clearData()
            scanner.scanPaths(currentDir)
            scanner.returnData("print", "files", "noPath")

        elif userInput == "GPSData":
            scanner.clearData()
            scanner.scanPaths(currentDir, "deep")
            data = list()
            dataPaths = list()
            dataPaths = scanner.returnData("return", "files")

            f1 = open("dataPaths.txt", "a+")
            f2 = open("data.txt", "a+")
            f3 = open("gpsKeyError.txt", "a+")
            f4 = open("noSpecificData.txt", "a+")

            for i in dataPaths:
                if i.endswith(".JPG") or i.endswith(".jpeg"):
                    extractedGPSData = exifTool.GPSCoords(i)

                    if extractedGPSData:
                        if extractedGPSData == "KeyError":
                            exifTool.gpsKeyError.append(i)
                            f3.write(str(i) + "\n")

                        else:
                            data.append(extractedGPSData)
                            f1.write(str(i) + "\n")
                            f2.write(str(extractedGPSData) + "\n")

            f1.close()
            f2.close()
            f3.close()

            for i in exifTool.noSpecificData:
                f4.write(str(i) + "\n")

            f4.close()

        elif userInput == "print data":
            for i in data:
                print(i)

        elif userInput == "display":
            display()

        else:
            if userInput in os.listdir(currentDir):
                if os.path.isdir(os.path.join(currentDir, userInput)):
                    currentDir = os.path.join(currentDir, userInput)
                    scanner.clearData()
                    scanner.scanPaths(currentDir)
                    scanner.returnData("print", "folders", "noPath")
                    if len(scanner.dirList) == 0:
                        print("No folders.")

            else:
                print("No such folder")
                continue


runProgram()
