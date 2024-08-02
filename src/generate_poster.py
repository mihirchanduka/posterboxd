import numpy as np
from sklearn.cluster import KMeans
from PIL import Image, ImageDraw, ImageFont, ImageOps, ImageFilter
import requests

def convert_to_jpg(image):
    rgb_image = image.convert('RGB')
    return rgb_image 
def get_most_prominent_color(image):
    image = image.convert("RGB")
    image = image.resize((100, 100))
    image = np.array(image).reshape((-1, 3))
    kmeans = KMeans(n_clusters=1)
    kmeans.fit(image)
    return tuple(map(int, kmeans.cluster_centers_[0]))

def create_initial_gradient(width, height, colors):
    gradient = Image.new('RGB', (width, height))
    draw = ImageDraw.Draw(gradient)
    for i, color in enumerate(colors):
        if i == 0:
            draw.rectangle([0, 0, width//2, height//2], fill=color)
        elif i == 1:
            draw.rectangle([width//2, 0, width, height//2], fill=color)
        elif i == 2:
            draw.rectangle([0, height//2, width//2, height], fill=color)
        elif i == 3:
            draw.rectangle([width//2, height//2, width, height], fill=color)
    
    draw.rectangle([0, 4*1400, width, height], fill=(20, 24, 28))
    return gradient

def add_rounded_corners(image, radius):
    big_size = (image.size[0] * 4, image.size[1] * 4)
    mask = Image.new('L', big_size, 0)
    draw = ImageDraw.Draw(mask)
    draw.rounded_rectangle((0, 0) + big_size, radius=radius * 4, fill=255)
    mask = mask.resize(image.size, Image.Resampling.LANCZOS)
    rounded_image = image.copy()
    rounded_image.putalpha(mask)
    return rounded_image

def make_circle(image):
    size = image.size
    mask = Image.new('L', size, 0)
    draw = ImageDraw.Draw(mask)
    draw.ellipse((0, 0) + size, fill=255)
    circle_image = image.copy()
    circle_image.putalpha(mask)
    return circle_image

def draw_rectangle(image, x, y, width, height, color):
    draw = ImageDraw.Draw(image)
    draw.rectangle([x, y, x + width, y + height], fill=color)

def draw_histogram_rectangles(image, anchor_rect_x, anchor_rect_y, anchor_rect_width, anchor_rect_height, rating_data, gap=8):
    draw = ImageDraw.Draw(image)
    num_rectangles = len(rating_data)
    rect_width = (anchor_rect_width - (num_rectangles - 1) * gap) // num_rectangles
    max_count = max(item['count'] for item in rating_data) 

    scaling_factor = (100 * 4) / max_count 

    for i, item in enumerate(rating_data):
        x = anchor_rect_x + i * (rect_width + gap)
        height = item['count'] * scaling_factor
        y = anchor_rect_y - height
        draw.rectangle([x, y, x + rect_width, anchor_rect_y], fill=(68, 85, 102, 255))


def draw_poster(username, user_id, display_name, profile_picture_url, watches, watches_this_year, total_watch_time, total_watch_time_this_year, favorite_posters, histogram):
    width, height = 1080 * 4, 1920 * 4
    background_color = (255, 255, 255)
    poster = Image.new("RGB", (width, height), background_color)
    draw = ImageDraw.Draw(poster)

    try:
        font = ImageFont.truetype("fonts/GraphikSemibold.otf", 60 * 4)
    except IOError:
        font = ImageFont.load_default()


    response = requests.get(profile_picture_url, stream=True)
    profile_picture = Image.open(response.raw).resize((200 * 4, 200 * 4))
    profile_picture = convert_to_jpg(profile_picture)


    profile_picture_position = (27 * 4, 1580 * 4)

    if not favorite_posters:
        favorite_posters = ["images/blankfavorite.png", "images/blankfavorite.png", "images/blankfavorite.png", "images/blankfavorite.png"]

    dominant_colors = []
    for source in favorite_posters:
        if source.startswith('http'):
            response = requests.get(source, stream=True)
            fav_poster = Image.open(response.raw).resize((500 * 4, 750 * 4))
        else:
            fav_poster = Image.open(source).resize((500 * 4, 750 * 4))
        dominant_colors.append(get_most_prominent_color(fav_poster))

    initial_gradient = create_initial_gradient(width, height, dominant_colors)
    blurred_gradient = initial_gradient.filter(ImageFilter.GaussianBlur(radius=200 * 4))
    poster.paste(blurred_gradient, (0, 0))

    grid_positions = [(27 * 4, 27 * 4), (553 * 4, 27 * 4), (27 * 4, 803 * 4), (553 * 4, 803 * 4)]
    grid_size = (500 * 4, 750 * 4)

    for i, source in enumerate(favorite_posters):
        if source.startswith('http'):
            response = requests.get(source, stream=True)
            fav_poster = Image.open(response.raw).resize(grid_size)
        else:
            fav_poster = Image.open(source).resize(grid_size)
        fav_poster_rounded = add_rounded_corners(fav_poster, 5 * 4)
        poster.paste(fav_poster_rounded, grid_positions[i], fav_poster_rounded)

    profile_picture_circle = make_circle(profile_picture)
    poster.paste(profile_picture_circle, profile_picture_position, profile_picture_circle)

    profile_center_x = profile_picture_position[0] + profile_picture.size[0] // 2
    max_length = 12

    if len(display_name) > max_length:
        display_name = display_name[:max_length - 3] + "..."

    text_bbox = draw.textbbox((0, 0), display_name, font=font)
    text_x_position = profile_center_x + profile_picture.size[0] // 2 + 40
    text_y_position = profile_picture_position[1] + profile_picture.size[1] // 2 - text_bbox[3] // 2

    draw.text((text_x_position, text_y_position), display_name, font=font, fill=(216, 224, 232, 255))

    rect_x, rect_y = 405 * 4, 1780 * 4
    rect_width, rect_height = 1 * 4, 100 * 4
    rect_color = (68,85,102,255)
    draw_rectangle(poster, rect_x, rect_y, rect_width, rect_height, rect_color)

    watches_text = str(watches)
    watches_font = ImageFont.truetype("fonts/TiemposTextSemibold.ttf", int(40 * 4 * 1.1))
    watches_text_bbox = draw.textbbox((0, 0), watches_text, font=watches_font)
    watches_text_x_position = rect_x - 45 * 4 - (watches_text_bbox[2] - watches_text_bbox[0])
    watches_text_y_position = rect_y + rect_height // 2 - watches_text_bbox[3] // 2 - 20 * 4
    draw.text((watches_text_x_position, watches_text_y_position), watches_text, font=watches_font, fill=(216, 224, 232, 255))

    films_text = "FILMS"
    films_font = ImageFont.truetype("fonts/GraphikRegular.otf", int(40 * 2))
    films_text_bbox = draw.textbbox((0, 0), films_text, font=films_font)
    films_text_x_position = watches_text_x_position + ((watches_text_bbox[2] - watches_text_bbox[0]) - (films_text_bbox[2] - films_text_bbox[0])) // 2
    films_text_y_position = rect_y + rect_height // 2 - films_text_bbox[3] // 2 + 20 * 4
    draw.text((films_text_x_position, films_text_y_position), films_text, font=films_font, fill=(100, 119, 135, 255))

    watches_this_year_text = str(watches_this_year)
    watches_this_year_font = ImageFont.truetype("fonts/TiemposTextSemibold.ttf", int(40 * 4 * 1.1))
    watches_this_year_text_bbox = draw.textbbox((0, 0), watches_this_year_text, font=watches_this_year_font)
    watches_this_year_text_x_position = rect_x + 45 * 4 + rect_width
    watches_this_year_text_y_position = rect_y + rect_height // 2 - watches_this_year_text_bbox[3] // 2 - 20 * 4
    draw.text((watches_this_year_text_x_position, watches_this_year_text_y_position), watches_this_year_text, font=watches_this_year_font, fill=(216, 224, 232, 255))

    this_year_text = "THIS YEAR"
    this_year_font = ImageFont.truetype("fonts/GraphikRegular.otf", int(40 * 2))
    this_year_text_bbox = draw.textbbox((0, 0), this_year_text, font=this_year_font)
    this_year_text_x_position = watches_this_year_text_x_position + ((watches_this_year_text_bbox[2] - watches_this_year_text_bbox[0]) - (this_year_text_bbox[2] - this_year_text_bbox[0])) // 2
    this_year_text_y_position = rect_y + rect_height // 2 - this_year_text_bbox[3] // 2 + 20 * 4
    draw.text((this_year_text_x_position, this_year_text_y_position), this_year_text, font=this_year_font, fill=(100, 119, 135, 255))

    new_rect_x = watches_this_year_text_x_position + (watches_this_year_text_bbox[2] - watches_this_year_text_bbox[0]) + 45 * 4
    new_rect_y = rect_y
    new_rect_width = 1 * 4
    new_rect_height = 100 * 4
    draw_rectangle(poster, new_rect_x, new_rect_y, new_rect_width, new_rect_height, rect_color)

    total_watch_time_text = str(total_watch_time)
    total_watch_time_font = ImageFont.truetype("fonts/TiemposTextSemibold.ttf", int(40 * 4 * 1.1))
    total_watch_time_text_bbox = draw.textbbox((0, 0), total_watch_time_text, font=total_watch_time_font)
    total_watch_time_text_x_position = new_rect_x + 45 * 4 + new_rect_width
    total_watch_time_text_y_position = rect_y + rect_height // 2 - total_watch_time_text_bbox[3] // 2 - 20 * 4
    draw.text((total_watch_time_text_x_position, total_watch_time_text_y_position), total_watch_time_text, font=total_watch_time_font, fill=(216, 224, 232, 255))

    hours_text = "HOURS"
    hours_font = ImageFont.truetype("fonts/GraphikRegular.otf", int(40 * 2))
    hours_text_bbox = draw.textbbox((0, 0), hours_text, font=hours_font)
    hours_text_x_position = total_watch_time_text_x_position + ((total_watch_time_text_bbox[2] - total_watch_time_text_bbox[0]) - (hours_text_bbox[2] - hours_text_bbox[0])) // 2
    hours_text_y_position = rect_y + rect_height // 2 - hours_text_bbox[3] // 2 + 20 * 4
    draw.text((hours_text_x_position, hours_text_y_position), hours_text, font=hours_font, fill=(100, 119, 135, 255))

    hours_text = "WATCHED"
    hours_font = ImageFont.truetype("fonts/GraphikRegular.otf", int(40 * 2))
    hours_text_bbox = draw.textbbox((0, 0), hours_text, font=hours_font)
    hours_text_x_position = total_watch_time_text_x_position + ((total_watch_time_text_bbox[2] - total_watch_time_text_bbox[0]) - (hours_text_bbox[2] - hours_text_bbox[0])) // 2
    hours_text_y_position = rect_y + rect_height // 2 - hours_text_bbox[3] // 2 + 45 * 4
    draw.text((hours_text_x_position, hours_text_y_position), hours_text, font=hours_font, fill=(100, 119, 135, 255))

    final_rect_x = total_watch_time_text_x_position + (total_watch_time_text_bbox[2] - total_watch_time_text_bbox[0]) + 45 * 4
    final_rect_y = rect_y
    final_rect_width = 1 * 4
    final_rect_height = 100 * 4
    draw_rectangle(poster, final_rect_x, final_rect_y, final_rect_width, final_rect_height, rect_color)

    total_watch_time_this_year_text = str(total_watch_time_this_year)
    total_watch_time_this_year_font = ImageFont.truetype("fonts/TiemposTextSemibold.ttf", int(40 * 4 * 1.1))
    total_watch_time_this_year_text_bbox = draw.textbbox((0, 0), total_watch_time_this_year_text, font=total_watch_time_this_year_font)
    total_watch_time_this_year_text_x_position = final_rect_x + 45 * 4 + final_rect_width
    total_watch_time_this_year_text_y_position = rect_y + rect_height // 2 - total_watch_time_this_year_text_bbox[3] // 2 - 20 * 4
    draw.text((total_watch_time_this_year_text_x_position, total_watch_time_this_year_text_y_position), total_watch_time_this_year_text, font=total_watch_time_this_year_font, fill=(216, 224, 232, 255))

    hours_this_year_text = "HOURS"
    hours_this_year_font = ImageFont.truetype("fonts/GraphikRegular.otf", int(40 * 2))
    hours_this_year_text_bbox = draw.textbbox((0, 0), hours_this_year_text, font=hours_this_year_font)
    hours_this_year_text_x_position = total_watch_time_this_year_text_x_position + ((total_watch_time_this_year_text_bbox[2] - total_watch_time_this_year_text_bbox[0]) - (hours_this_year_text_bbox[2] - hours_this_year_text_bbox[0])) // 2
    hours_this_year_text_y_position = rect_y + rect_height // 2 - hours_this_year_text_bbox[3] // 2 + 20 * 4
    draw.text((hours_this_year_text_x_position, hours_this_year_text_y_position), hours_this_year_text, font=hours_this_year_font, fill=(100, 119, 135, 255))

    hours_this_year_text = "THIS YEAR"
    hours_this_year_font = ImageFont.truetype("fonts/GraphikRegular.otf", int(40 * 2))
    hours_this_year_text_bbox = draw.textbbox((0, 0), hours_this_year_text, font=hours_this_year_font)
    hours_this_year_text_x_position = total_watch_time_this_year_text_x_position + ((total_watch_time_this_year_text_bbox[2] - total_watch_time_this_year_text_bbox[0]) - (hours_this_year_text_bbox[2] - hours_this_year_text_bbox[0])) // 2
    hours_this_year_text_y_position = rect_y + rect_height // 2 - hours_this_year_text_bbox[3] // 2 + 45 * 4
    draw.text((hours_this_year_text_x_position, hours_this_year_text_y_position), hours_this_year_text, font=hours_this_year_font, fill=(100, 119, 135, 255))




    histrect_x, histrect_y = 606 * 4, 1730 * 4
    histrect_width, histrect_height = 405 * 4, 1 * 4
    histrect_color = (68, 85, 102, 255)

    draw_histogram_rectangles(poster, histrect_x, histrect_y, histrect_width, histrect_height, histogram)

    one_star = Image.open("images/onestar.png").resize((23 * 4, 23 * 4))
    one_star_position = (606 * 4, 1736 * 4)
    poster.paste(one_star, one_star_position, one_star)

    one_star = Image.open("images/fivestar.png").resize((126 * 4, 23 * 4))
    one_star_position = (885 * 4, 1736 * 4)
    poster.paste(one_star, one_star_position, one_star)

    filename = f"poster_{username}.png"
    poster.save(filename)
