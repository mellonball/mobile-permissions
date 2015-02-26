import subprocess, time

# as written this file must be stored in the googleplay-api-master directory and needs internet access to work
# this file assumes you have edited config.py with valid phone credentials. I used a device ID to get my ANDROID_ID


# retrieveCategoryPackageNames(searchCategory)
# takes in a string category name (like "weather" or "flashlight")
# returns list of all package names (listPackageNames) as strings for apps in that category
def retrieveCategoryPackageNames(searchCategory):
  # TODO can search ever return ALL apps besides specified number (which takes 100 as max), or 20 (which is how many are returned if number is not specified)?
  p = subprocess.Popen("python search.py '%s'" % searchCategory, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
  searchResult = p.stdout
  searchResult = searchResult.readlines()
  searchResultList = list(searchResult[1:])

  packageNamesList = []

  for line in searchResultList:
    #the second element in list returned is the package name
    line = line.split(";")
    packageNamesList.append(line[1])

  # print "\n\n Length of packageNamesList: ", len(packageNamesList)

  return packageNamesList
  

# retrievePermissionFrequency(searchCategory, listPackageNames)
# takes list of package names for apps and a category, 
# returns a dictionary of all permissions used by apps in the searchCategory and in what frequency they are seen.
def retrievePermissionFrequency(searchCategory, listPackageNames):
  dic = {}

  for pkg in listPackageNames:
    p = subprocess.Popen("python permissions.py %s" % pkg, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
    result = p.stdout
    result = result.readlines()
  
    for perm in result:
      if perm in dic:
        dic[perm] += 1;
      else:
        dic[perm] = 1;

  return dic


# test calls to functions -------------
def main():
  pkgNamesList = retrieveCategoryPackageNames("weather")
  print "\n\nPrinting Package Names list: \n\n", pkgNamesList

  dic = retrievePermissionFrequency("weather", pkgNamesList)
  print "\n\nPrinting Dictionary: \n\n", dic

main()
