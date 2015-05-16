#!/usr/bin/python

# Do not remove
GOOGLE_LOGIN = GOOGLE_PASSWORD = AUTH_TOKEN = None

import sys
from pprint import pprint
from config import *
from googleplay import GooglePlayAPI
from helpers import sizeof_fmt, print_header_line, print_result_line
#import subprocess, time
import json

# as written this file must be stored in the googleplay-api-master directory and needs internet access to work
# this file assumes you have edited config.py with valid phone credentials. I used a device ID app to get an ANDROID_ID

def retrieveCategoryPackageNames(request):

    nb_res = None
    offset = None
    api = GooglePlayAPI(ANDROID_ID)
    api.login(GOOGLE_LOGIN, GOOGLE_PASSWORD, AUTH_TOKEN)


    packageNamesList = []
    #print_header_line()

    # continue requesting until receive ALL apps by category. use to make histogram.
    while True:
        try:
            message = api.search(request, nb_res, offset)
        except:
            break

        if message.doc:
            doc = message.doc[0]

            for c in doc.child:
                packageNamesList.append(c.docid)
            offset = len(packageNamesList)
        else:
            break

    dic = {}
    final_results = {}

    # Only one app returned TODO update this
    if (len(packageNamesList) == 1):
        response = api.details(packageNamesList[0])
        print "\n".join(i.encode('utf8') for i in response.docV2.details.appDetails.permission)

    # More than one app
    else:
        response = api.bulkDetails(packageNamesList)

        for entry in response.entry:
            hasCustom = False
            if (entry.ListFields()):
                iconUrl = ""
                for x in entry.doc.image:
                    if x.imageType == 4:
                        iconUrl = x.imageUrl
                final_results[entry.doc.docid] = {'package': entry.doc.docid, 'title':entry.doc.title, 
                                          'creator':entry.doc.creator, 
                                          'price':{'amount':entry.doc.offer[0].formattedAmount, 'currency':entry.doc.offer[0].currencyCode}, 
                                          'icon':iconUrl,
                                          'permissions':[perm for perm in entry.doc.details.appDetails.permission],
                                          'rating':{'stars':entry.doc.aggregateRating.starRating, 'count':entry.doc.aggregateRating.ratingsCount},
                                          'shareUrl': entry.doc.shareUrl 
                                          }
                for permission in entry.doc.details.appDetails.permission:
                    # apps can have custom permissions that don't start with android.permission.PERM_NAME_HERE
                    # are they safe? Will warn users about custom permissions.
                    perm = permission.split(".")
                    if (permission != "com.android.browser.permission.WRITE_HISTORY_BOOKMARKS" and permission != "com.android.browser.permission.WRITE_HISTORY_BOOKMARKS" and (len(perm) !=3 or perm[0] != "android" or perm[1] != "permission")):
                        hasCustom = True
                        continue # don't want to count custom permissions in the histogram dictionary since they will all of them will be unusual
                    #perm = perm[-2] + "." + perm[-1]
                    if permission in dic:
                        dic[permission] += 1;
                    else:
                        dic[permission] = 1;
                final_results[entry.doc.docid]['custom'] = hasCustom
    #print dic

    DANGEROUS_PERMS = ["android.permission.ACCESS_COARSE_LOCATION",
                       "android.permission.ACCESS_FINE_LOCATION",
                       "android.permission.ACCESS_MOCK_LOCATION",
                       "android.permission.AUTHENTICATE_ACCOUNTS",
                       "android.permission.BLUETOOTH",
                       "android.permission.BLUETOOTH_ADMIN",
                       "android.permission.CALL_PHONE",
                       "android.permission.CAMERA",
                       "android.permission.CHANGE_CONFIGURATION",
                       "android.permission.CHANGE_NETWORK_STATE",
                       "android.permission.CHANGE_WIFI_MULTICAST_STATE",
                       "android.permission.CHANGE_WIFI_STATE",
                       "android.permission.CLEAR_APP_CACHE",
                       "android.permission.DUMP",
                       "android.permission.GET_TASKS",
                       "android.permission.INTERNET",
                       "android.permission.MANAGE_ACCOUNTS",
                       "android.permission.MODIFY_AUDIO_SETTINGS",
                       "android.permission.MODIFY_PHONE_STATE",
                       "android.permission.MOUNT_FORMAT_FILESYSTEMS",
                       "android.permission.MOUNT_UNMOUNT_FILESYSTEMS",
                       "android.permission.PERSISTENT_ACTIVITY",
                       "android.permission.PROCESS_OUTGOING_CALLS",
                       "android.permission.READ_CALENDAR",
                       "android.permission.READ_CONTACTS",
                       "android.permission.READ_LOGS",
                       "android.permission.READ_OWNER_DATA",
                       "android.permission.READ_PHONE_STATE",
                       "android.permission.READ_SMS",
                       "android.permission.READ_USER_DICTIONARY",
                       "android.permission.RECEIVE_MMS",
                       "android.permission.RECEIVE_SMS",
                       "android.permission.RECEIVE_WAP_PUSH",
                       "android.permission.RECORD_AUDIO",
                       "android.permission.REORDER_TASKS",
                       "android.permission.SEND_SMS",
                       "android.permission.SET_ALWAYS_FINISH",
                       "android.permission.SET_ANIMATION_SCALE",
                       "android.permission.SET_DEBUG_APP",
                       "android.permission.SET_PROCESS_LIMIT",
                       "android.permission.SET_TIME_ZONE",
                       "android.permission.SIGNAL_PERSISTENT_PROCESSES",
                       "android.permission.SUBSCRIBED_FEEDS_WRITE",
                       "android.permission.SYSTEM_ALERT_WINDOW",
                       "android.permission.USE_CREDENTIALS",
                       "android.permission.WAKE_LOCK",
                       "android.permission.WRITE_APN_SETTINGS",
                       "android.permission.WRITE_CALENDAR",
                       "android.permission.WRITE_CONTACTS",
                       "android.permission.WRITE_EXTERNAL_STORAGE",
                       "android.permission.WRITE_OWNER_DATA",
                       "android.permission.WRITE_SETTINGS",
                       "android.permission.WRITE_SMS",
                       "android.permission.WRITE_SYNC_SETTINGS",
                       "com.android.browser.permission.READ_HISTORY_BOOKMARKS",
                       "com.android.browser.permission.WRITE_HISTORY_BOOKMARKS"]
    #go through final_results and add field for unusual permissions
    for docid in final_results: 
        final_results[docid]['unusual'] = False
        final_results[docid]['dangerous'] = False
        for permission in final_results[docid]['permissions']:
            perm = permission.split(".")
            if (permission != "com.android.browser.permission.WRITE_HISTORY_BOOKMARKS" and permission != "com.android.browser.permission.WRITE_HISTORY_BOOKMARKS" and (len(perm) !=3 or perm[0] != "android" or perm[1] != "permission")):
                continue
            elif dic[permission] < 0.05*offset:
                final_results[docid]['unusual'] = True
                if 'unusual_perms' in final_results[docid]:
                    final_results[docid]['unusual_perms'].append(permission)
                else:
                    final_results[docid]['unusual_perms'] = [permission]
                if permission in DANGEROUS_PERMS:
                    final_results[docid]['dangerous'] = True
                    if 'dangerous_permissions' in final_results[docid]:
                        final_results[docid]['dangerous_permissions'].append(permission)
                    else:
                        final_results[docid]['dangerous_permissions'] = [permission]

    final = json.dumps({"app": final_results.values()})
    print final
    return None


def main():
    if len(sys.argv) > 1:
        request = " ".join(sys.argv[1:])
    else:
        request = sys.argv[1]
    pkgNamesList = retrieveCategoryPackageNames(request)


main()
