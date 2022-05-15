from datetime import date, datetime
from distutils import extension
import os
from pathlib import Path
import shutil
from tkinter import VERTICAL


def find(name, path):
    for root, dirs, files in os.walk(path):
        if name in files:
            return os.path.join(root, name)


def chdirToScriptLocation():
    abspath = os.path.abspath(os.sys.argv[0])
    dname = os.path.dirname(abspath)
    os.chdir(dname)


def getListOfBinaryFilesFromReleaseBuildDirectory(pluginName):
    chdirToScriptLocation()
    os.chdir("../cmake-build-release/Plugins/" + pluginName + "/" + pluginName + "_artefacts/Release/")

    fileExtensionsToGet = {"*.component", "*.vst3", "*.aaxplugin", "*vst", "*.dll"}
    filePaths = []

    for ext in fileExtensionsToGet:
        for path in Path(os.getcwd()).rglob(ext):
            filePaths.append(path)
            print("Found file: " + str(path))

    return filePaths


def signMacBinaries(pluginName):
    print("===========================================================================")
    print("Begin signing LX480 binaries...")

    filesToSign = getListOfBinaryFilesFromReleaseBuildDirectory(pluginName)

    for file in filesToSign:
        print("Signing file: " + str(file))
        signingCommand = 'codesign --force --sign "Apple Development: Jamie Pond (QU2A8WQL89)" ' + '"' + str(file) + '"'
        os.system(signingCommand)


def copyBinariesToInstallerInputFolder(pluginName):
    print("===========================================================================")
    print("Begin copying plugins to installer input folder...")
    filesToCopy = getListOfBinaryFilesFromReleaseBuildDirectory(pluginName)

    installerInputFolder = "/Users/jamiepond/PluginDevelopment/CoalescentSounds/CoalescentSoundsPlugins/Installers/MacOS/" + pluginName + "/Binaries To Release/"
    print("Installer input folder: " + installerInputFolder)

    for file in filesToCopy:
        dest = os.path.join(installerInputFolder, str(file.name))
        print(dest)
        if os.path.isdir(dest):
            #print("Removing: " + os.path.dirname(dest))
            shutil.rmtree(dest)
        #print("Copying: " + os.path.dirname(file))
        shutil.copytree(file, dest)



def createMacInstaller(pluginName):
    print("===========================================================================")
    print("Begin creating Mac installer...")
    chdirToScriptLocation()
    os.chdir("../Installers")

    pkgBuildPath = find(pluginName + ".pkgproj", os.getcwd())
    packagesCommand = "/usr/local/bin/packagesbuild --project " + "'" + str(pkgBuildPath) + "'"
    print(packagesCommand)
    os.system(packagesCommand)


def signMacInstaller(pluginName):
    print("===========================================================================")
    print("Begin signing pluginName installer...")
    chdirToScriptLocation()
    os.chdir("../Installers/MacOS/"+pluginName+"/build/")
    signInstallerCommand = "productsign --sign '3rd Party Mac Developer Installer: Jamie Pond (DN5WMFL5W5)' '"+pluginName+".pkg' '"+pluginName+"_signed.pkg'"
    os.system(signInstallerCommand)


def copySignedInstallerToGDrive(pluginName):
    print("===========================================================================")
    print("Copy installer to GDrive...")
    chdirToScriptLocation()
    os.chdir("../Installers/MacOS/"+pluginName+"/build/")

    packagePath = os.path.join(os.getcwd(), pluginName+"_signed.pkg")
    print(str(packagePath))

    now = str(date.today())

    googleDrivePath = "/Users/jamiepond/.CMVolumes/GDrive/Shared Folder/Beta Binaries/"+pluginName+"/"

    googleDrivePathToday = os.path.join(googleDrivePath, now)
    googleDrivePathLEVEL = os.path.join(googleDrivePathToday, pluginName+".pkg")
    print(googleDrivePathLEVEL)

    if not os.path.exists(googleDrivePathToday):
        os.mkdir(googleDrivePathToday)

    if os.path.isfile(googleDrivePathLEVEL):
        os.remove(googleDrivePathLEVEL)

    shutil.copy(packagePath, googleDrivePathLEVEL)


if __name__ == "__main__":
    pluginName = "LEVEL"
    signMacBinaries(pluginName)
    copyBinariesToInstallerInputFolder(pluginName)
    createMacInstaller(pluginName)
    signMacInstaller(pluginName)
    copySignedInstallerToGDrive(pluginName)
