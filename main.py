import sys
sys.path.append('src')
import letterboxd_api as letterboxd

import generate_poster as poster



def main():
    username = input("what is your Letterboxd username?: ")

    access_token = letterboxd.get_access_token("config.ini")
    user_id = letterboxd.get_user_id(access_token, username)
    display_name = letterboxd.get_display_name(access_token, user_id)
    profile_picture_url = letterboxd.get_profile_picture(access_token, user_id)
    watches = letterboxd.get_watches(access_token, user_id)
    watches_this_year = letterboxd.get_diary_entries_this_year(access_token, user_id)
    total_watch_time = letterboxd.get_total_watch_time(access_token, letterboxd.get_list_of_watches(access_token, user_id))
    total_watch_time_this_year = letterboxd.get_total_watch_time(access_token, letterboxd.get_list_of_watches_this_year(access_token, user_id))
    favorite_posters = letterboxd.get_favorite_posters(access_token, user_id)
    histogram = letterboxd.get_histogram(access_token, user_id)
    poster.draw_poster(username, user_id, display_name, profile_picture_url, watches, watches_this_year, total_watch_time, total_watch_time_this_year, favorite_posters, histogram)
    


if __name__ == "__main__":
    main()