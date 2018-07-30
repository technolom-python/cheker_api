#!/usr/bin/python3
# -*- coding: utf-8 -*-
import requests
import json
import os
from collections import defaultdict


def get_server_name_from_user():
    print("Choose server: ")
    print("Default - Production - press Enter")
    print("Stage - 1 + Enter")
    server_name_in = input()
    if server_name_in == "0" or not server_name_in or "prod":
        server_name_in = ""
        print("Prod server")
        return server_name_in
    elif server_name_in == "1" or "stage":
        server_name_in = "stage."
        print("Stage server")
        return server_name_in
    else:
        print("Not found")
        return get_server_name_from_user()

server_name = get_server_name_from_user()

list_child = defaultdict(list)
all_in_list = defaultdict(list)
is_in_list = defaultdict(list)
not_in_list = defaultdict(list)
device_names = defaultdict(list)
all_recipe_name_with_id = defaultdict(list)

folder_with_report_file = 'api_test_reports'
language_file = "language.json"
devices_file = "devices.json"
recipe_mode_file = "recipe_mode.json"
programs_file = "program.json "
recipe_need_verification_file = "recipes_to_check.json"
file_report = "report.txt"

url_api = 'https://content.{}readyforsky.com/'.format(server_name)

user_login_url = "{0}headless/login".format(url_api)
url_commit = "{0}api/commit/last".format(url_api)
url_recipe_mode = "{0}api/recipe_mode/catalog/0/".format(url_api)
url_all_program = "{0}api/program/full_catalog/".format(url_api)
url_languages = "{0}api/language/catalog/".format(url_api)
user_headers_for_login = {'Accept': 'application/json', 'Content-Type': 'application/json'}
user_headers_for_content = {"Accept": 'application/json', "Authorization": "Bearer"}


def get_token(url, data, headers):
    try:
        response = requests.post(url=url, data=data, headers=headers)
        status = response.status_code
        if status == 200:
            response_content = json.loads(response.content.decode('utf-8'))
            token = response_content['access_token']
            return token
        else:
            return 'Check login and password', {'status_code': status}
    except requests.exceptions.ReadTimeout:
        print('Oops. Read timeout occured')
    except requests.exceptions.ConnectTimeout:
        print('Oops. Connection timeout occured!')
    except requests.exceptions.HTTPError:
        print('Oops. HTTP Error occured')
    except requests.exceptions.ConnectionError:
        print('Oops. ConnectionError occured')


def checking_language(list_locale):
    all_locale = []
    for name in list_locale:
        if name["locale"] not in all_locale:
            all_locale.append(name["locale"])
    print('Choose language:{0}'.format(str(all_locale)))
    print('(default - ru - press Enter): ')
    input_language = input()
    if not input_language:
        language = 'ru'
        print("Default language: {0}".format(language))
        print("The program is running")
        return language
    else:
        if input_language in all_locale:
            print("The program is running")
            return input_language
    print("language not found")
    return checking_language(list_of_languages)


def create_and_change_directory(folder_name):
    x = os.getcwd()
    t = os.path.join(x, folder_name)
    try:
        os.mkdir(t)
    except OSError:
        os.chdir(t)
    else:
        os.chdir(t)


def get_data_from_api(url, headers):
    try:
        api_data = requests.get(url=url, headers=headers)
        status = api_data.status_code
        if status == 200:
            print("---")
            api_content = json.loads(api_data.content.decode('utf-8'))
            return api_content
        else:
            print("Server status: ", status)
    except requests.exceptions.HTTPError:
        print('Oops. HTTP Error occured')


def get_programs_with_child(all_programs):
    for program in all_programs:
        if 'child' in program:
            for child in program['child']:
                list_child[child["parent_id"]].append(child["id"])
    return list_child


def get_list_need_verification(list_devices_from_file, list_programs_with_child, list_recipe_mode_from_file):
    for device in list_devices_from_file:
        for recipe in device['recipeDescriptions']:
            for program in device['programs']:
                if program in list_programs_with_child:
                    for child in list_programs_with_child[program]:
                        if child not in device["programs"]:
                            device["programs"].append(child)
                for mode in list_recipe_mode_from_file:
                    if {mode['recipeDescription']: mode['program']} == {recipe: program}:
                        is_in_list[recipe].append({program: device['name']})
                all_in_list[recipe].append({program: device['name']})
    list_needs_verification = (all_in_list.keys() - is_in_list.keys())
    return list_needs_verification


def get_devices_with_problems(all_descriptions_in_list, descriptions_need_verification):
    for all_descriptions in all_descriptions_in_list.keys():
            if all_descriptions in descriptions_need_verification:
                for name_device in all_descriptions_in_list[all_descriptions]:
                    name_dev = list(name_device.values())
                    if name_dev[0] not in device_names[all_descriptions]:
                        device_names[all_descriptions].append(name_dev[0])
    return device_names


def get_recipe_name_with_id(recipes, recipe_descriptions):
    for recipe in recipes:
        for desc in recipe_descriptions:
            if desc in recipe["descriptions"]:
                recipe_name_with_id = "Recipe name: {0}, Recipe Id:{1}".format(str(recipe["name"]), str(recipe["id"]))
                all_recipe_name_with_id[desc].append(recipe_name_with_id)
    return all_recipe_name_with_id


def get_report(list_device_names, list_recipe_name_with_id):
    full_report = []
    for name in list_device_names:
        for recipe_name in list_recipe_name_with_id:
            if name == recipe_name:
                    recipe_and_device = *list_recipe_name_with_id[recipe_name], str(list_device_names[name])
                    if recipe_and_device not in full_report:
                        full_report.append(recipe_and_device)
    return full_report

create_and_change_directory(folder_with_report_file)
token_api = get_token(user_login_url, LOGIN_DATA, user_headers_for_login)
user_headers_for_content["Authorization"] = user_headers_for_content["Authorization"] + " " + token_api

with open(language_file, "w", encoding='utf=8') as data_file:
    languages = get_data_from_api(url_languages, user_headers_for_content)
    json.dump(languages, data_file, ensure_ascii=False)
    data_file.close()

with open(language_file, "r", encoding='utf=8') as data_file:
    list_of_languages = json.load(data_file)
    data_file.close()

choosen_language = checking_language(list_of_languages)

url_all_devices = "{0}api/v2/device/catalog/{1}/0/deleted:=:0/protocolType:=:1".format(url_api, choosen_language)

with open(devices_file, 'w', encoding="Utf-8") as data_file:
    all_devices = get_data_from_api(url_all_devices, user_headers_for_content)
    json.dump(all_devices, data_file, ensure_ascii=False)
    data_file.close()

with open(devices_file, 'r', encoding="Utf-8") as data_file:
    devices_from_file = json.load(data_file)
    data_file.close()

with open(recipe_mode_file, 'w', encoding="Utf-8") as data_file:
    recipe_mode = get_data_from_api(url_recipe_mode, user_headers_for_content)
    json.dump(recipe_mode, data_file, ensure_ascii=False)
    data_file.close()

with open(recipe_mode_file, 'r', encoding="Utf-8") as data_file:
    recipe_mode_from_file = json.load(data_file)
    data_file.close()

with open(programs_file, 'w', encoding="Utf-8") as data_file:
    all_program = get_data_from_api(url_all_program, user_headers_for_content)
    json.dump(all_program, data_file, ensure_ascii=False)
    data_file.close()

with open(programs_file, 'r', encoding="Utf-8") as data_file:
    programs_from_file = json.load(data_file)
    data_file.close()


all_program_with_child = get_programs_with_child(programs_from_file)
need_verification = get_list_need_verification(devices_from_file, all_program_with_child, recipe_mode_from_file)

url_recipe = (str(need_verification))[1:-1]

url_recipe_for_check = "{0}api/recipe/catalog/{1}/0/descriptions:IN:{2}".format(url_api, choosen_language, url_recipe)

with open(recipe_need_verification_file, 'w', encoding="Utf-8") as data_file:
    recipe_for_check = get_data_from_api(url_recipe_for_check, user_headers_for_content)
    json.dump(recipe_for_check, data_file, ensure_ascii=False)
    data_file.close()

with open(recipe_need_verification_file, 'r', encoding="Utf-8") as data_file:
    recipe_from_file = json.load(data_file)
    data_file.close()

get_devices_with_problems(all_in_list, need_verification)
get_recipe_name_with_id(recipe_from_file, need_verification)

report = get_report(device_names, all_recipe_name_with_id)

create_and_change_directory(choosen_language)

last_commit_info = get_data_from_api(url_commit, user_headers_for_content)
last_commit_id = last_commit_info['id']

print("Need to check: {0} recipe(s)".format(str(len(report))))
file_report = "Commit_{0}_{1}_{2}".format(str(last_commit_id), choosen_language, file_report)
print("The report is saved in a file: {0}".format(file_report))
print("Path to file: {0}".format(os.getcwd()))

with open(file_report, 'w', encoding="Utf-8") as data_file:
    data_file.write(str(report) + '\n')
    [print(line)for line in report]
    data_file.close()

print('Successfully')