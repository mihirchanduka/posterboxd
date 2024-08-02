import requests
import concurrent.futures
from datetime import date
import configparser

TOKEN_URL = 'https://api.letterboxd.com/api/v0/auth/token'

def get_access_token(config_file):
    print("Reading configuration file for client credentials...")
    config = configparser.ConfigParser()
    config.read(config_file)
    CLIENT_ID = config.get('Letterboxd API Token', 'CLIENT_ID')
    CLIENT_SECRET = config.get('Letterboxd API Token', 'CLIENT_SECRET')
    print("Configuration read successfully.")

    data = {
        'grant_type': 'client_credentials',
        'client_id': CLIENT_ID,
        'client_secret': CLIENT_SECRET
    }
    headers = {
        'Content-Type': 'application/x-www-form-urlencoded'
    }
    print("Requesting access token...")
    response = requests.post(TOKEN_URL, data=data, headers=headers)
    response_data = response.json()
    if 'access_token' in response_data:
        print("Access token received.")
        return response_data['access_token']
    else:
        error_message = f"Error obtaining access token: {response_data}"
        print(error_message)
        raise Exception(error_message)

def get_user_id(access_token, username):
    print(f"Fetching user ID for username: {username}...")
    headers = {
        'Authorization': f'Bearer {access_token}'
    }
    params = {
        "input": username,
        "include": "MemberSearchItem"
    }
    response = requests.get("https://api.letterboxd.com/api/v0/search", params=params, headers=headers)
    if response.status_code == 200:
        user_id = response.json()["items"][0]['member']["id"]
        print(f"User ID for {username} is {user_id}.")
        return user_id
    else:
        error_message = f"Failed to fetch user ID: {response.status_code} - {response.text}"
        print(error_message)
        raise Exception(error_message)

def get_display_name(access_token, user_id):
    print(f"Fetching display name for user ID: {user_id}...")
    headers = {
        'Authorization': f'Bearer {access_token}'
    }
    response = requests.get(f"https://api.letterboxd.com/api/v0/member/{user_id}", headers=headers)
    if response.status_code == 200:
        display_name = response.json()["displayName"]
        print(f"Display name for user ID {user_id} is {display_name}.")
        return display_name
    else:
        error_message = f"Failed to fetch display name: {response.status_code} - {response.text}"
        print(error_message)
        raise Exception(error_message)

def get_profile_picture(access_token, user_id):
    print(f"Fetching profile picture for user ID: {user_id}...")
    headers = {
        'Authorization': f'Bearer {access_token}'
    }
    response = requests.get(f"https://api.letterboxd.com/api/v0/member/{user_id}", headers=headers)
    if response.status_code == 200:
        avatars = response.json()["avatar"]['sizes']
        profile_picture = next(size['url'] for size in avatars if size['height'] == 1000)
        print(f"Profile picture URL for user ID {user_id}: {profile_picture}")
        return profile_picture
    else:
        error_message = f"Failed to fetch profile picture: {response.status_code} - {response.text}"
        print(error_message)
        raise Exception(error_message)

def get_favorite_posters(access_token, user_id):
    print(f"Fetching favorite posters for user ID: {user_id}...")
    headers = {
        'Authorization': f'Bearer {access_token}'
    }
    response = requests.get(f"https://api.letterboxd.com/api/v0/member/{user_id}", headers=headers)
    if response.status_code == 200:
        data = response.json()
        favorite_posters = []
        if 'favoriteFilms' in data:
            for film in data['favoriteFilms']:
                if 'poster' in film and 'sizes' in film['poster']:
                    largest_poster = next((size['url'] for size in film['poster']['sizes'] if size['height'] == 3000), None)
                    favorite_posters.append(largest_poster)
        print(f"Retrieved {len(favorite_posters)} favorite posters.")
        return favorite_posters
    else:
        error_message = f"Failed to fetch favorite posters: {response.status_code} - {response.text}"
        print(error_message)
        raise Exception(error_message)

def get_diary_entries_this_year(access_token, user_id):
    print(f"Fetching diary entries for this year for user ID: {user_id}...")
    headers = {
        'Authorization': f'Bearer {access_token}'
    }
    response = requests.get(f"https://api.letterboxd.com/api/v0/member/{user_id}/statistics", headers=headers)
    if response.status_code == 200:
        data = response.json()['counts']['diaryEntriesThisYear']
        formatted_data = f"{data:,}"
        print(f"Diary entries this year: {formatted_data}")
        return formatted_data
    else:
        error_message = f"Failed to fetch diary entries: {response.status_code} - {response.text}"
        print(error_message)
        raise Exception(error_message)

def get_watches(access_token, user_id):
    print(f"Fetching total watches for user ID: {user_id}...")
    headers = {
        'Authorization': f'Bearer {access_token}'
    }
    response = requests.get(f"https://api.letterboxd.com/api/v0/member/{user_id}/statistics", headers=headers)
    if response.status_code == 200:
        data = response.json()['counts']['watches']
        formatted_data = f"{data:,}"
        print(f"Total watches: {formatted_data}")
        return formatted_data
    else:
        error_message = f"Failed to fetch total watches: {response.status_code} - {response.text}"
        print(error_message)
        raise Exception(error_message)

def get_list_of_watches(access_token, user_id):
    print("Starting to fetch the list of watched films...")
    cursor = 'start=0'
    all_ratings = []

    headers = {
        'Authorization': f'Bearer {access_token}'
    }
    params = {
        "perPage": 100,
        "member": user_id,
        "memberRelationship": "Watched",
        "sort": "MemberRatingHighToLow",
        "cursor": cursor
    }

    while True:
        print(f"Fetching page with cursor: {cursor}")
        response = requests.get("https://api.letterboxd.com/api/v0/films/", params=params, headers=headers)
        if response.status_code == 200:
            results = response.json()
            print(f"Retrieved {len(results['items'])} items from current page.")
            
            for item in results['items']:
                entry = {'film': item.get('id')}
                all_ratings.append(entry)
            
            if 'next' in results:
                cursor = results['next']
                params['cursor'] = cursor
                print("Moving to the next page...")
            else:
                print("No more pages to fetch.")
                break
        else:
            print(f"Error fetching data: {response.status_code} - {response.text}")
            break

    print(f"Completed fetching watched films. Total films retrieved: {len(all_ratings)}")
    return all_ratings

def get_list_of_watches_this_year(access_token, user_id):
    print(f"Starting to fetch the list of films watched this year for user ID: {user_id}...")
    cursor = 'start=0'
    all_ratings = []

    headers = {
        'Authorization': f'Bearer {access_token}'
    }
    params = {
        "perPage": 100,
        "member": user_id,
        "cursor": cursor,
        "year": date.today().year
    }
    
    while True:
        print(f"Fetching page with cursor: {cursor}")
        response = requests.get("https://api.letterboxd.com/api/v0/log-entries/", params=params, headers=headers)
        if response.status_code == 200:
            results = response.json()
            print(f"Retrieved {len(results['items'])} items from current page.")

            for item in results['items']:
                entry = {'film': item['film']['id']}
                all_ratings.append(entry)
            
            if 'next' in results:
                cursor = results['next']
                params['cursor'] = cursor
                print("Moving to the next page...")
            else:
                print("No more pages to fetch.")
                break
        else:
            print(f"Error fetching data: {response.status_code} - {response.text}")
            break

    print(f"Completed fetching films watched this year. Total films retrieved: {len(all_ratings)}")
    return all_ratings

def get_film_runtime(film, headers):
    print(f"Fetching runtime for film ID: {film['film']}...")
    response = requests.get(f"https://api.letterboxd.com/api/v0/film/{film['film']}", headers=headers)
    if response.status_code == 200:
        results = response.json()
        print(f"Runtime for film ID {film['film']}: {results['runTime']} minutes")
        return results["runTime"]
    else:
        error_message = f"Failed to fetch film runtime: {response.status_code} - {response.text}"
        print(error_message)
        raise Exception(error_message)

def get_total_watch_time(access_token, film_list):
    print("Calculating total watch time for the film list...")
    headers = {
        'Authorization': f'Bearer {access_token}'
    }

    total_run_time = 0
    with concurrent.futures.ThreadPoolExecutor(max_workers=20) as executor:
        futures = [executor.submit(get_film_runtime, film, headers) for film in film_list]
        for future in concurrent.futures.as_completed(futures):
            try:
                total_run_time += future.result()
            except Exception as e:
                print(f"Error calculating runtime: {e}")
    total_run_time_in_hours = round(total_run_time / 60)
    formatted_data = f"{total_run_time_in_hours:,}"
    print(f"Total watch time: {total_run_time_in_hours} hours")
    return formatted_data

def get_histogram(access_token, user_id):
    print(f"Fetching ratings histogram for user ID: {user_id}...")
    headers = {
        'Authorization': f'Bearer {access_token}'
    }
    response = requests.get(f"https://api.letterboxd.com/api/v0/member/{user_id}/statistics", headers=headers)
    if response.status_code == 200:
        ratings_histogram = response.json()['ratingsHistogram']
        print("Ratings histogram fetched successfully.")
        simplified_histogram = []
        for rating_data in ratings_histogram:
            simplified_histogram.append({
                "rating": rating_data["rating"],
                "count": rating_data["count"]
            })
        print(f"Processed ratings histogram: {simplified_histogram}")
        return simplified_histogram
    else:
        error_message = f"Failed to fetch ratings histogram: {response.status_code} - {response.text}"
        print(error_message)
        raise Exception(error_message)
