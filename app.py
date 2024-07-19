"""
Fashion Trends Spotting App

This Streamlit app analyzes fashion trends based on Instagram posts from popular brands in the Middle East.
It involves logging into Instagram, selecting a brand, scraping post data, selecting a fashion item from the post image, performing sentiment analysis on comments,
and determining the trendiness of the post.

Modules:
    - instaloader: For scraping Instagram post data.
    - pandas: For handling data in DataFrame format.
    - requests: For making HTTP requests.
    - re: For text processing using regular expressions.
    - PIL: For image processing.
    - groq: For sentiment analysis using the Groq API.
    - time: For measuring time taken for operations.
    - streamlit: For building the web application.
    - cv2: For computer vision tasks.
    - json: For handling JSON data.
    - numpy: For numerical operations.
    - torch: For machine learning and tensor operations.
    - matplotlib.pyplot: For plotting graphs.
    - os: For interacting with the operating system.
    - ast: For parsing Python literals.
    - io.BytesIO: For handling binary data in memory.
    - IPython.display: For displaying images and other media in IPython environments.
    - instaloader.Post: Specific components from Instaloader for post handling.
    - instaloader.exceptions: Exception handling for Instaloader.
    - sklearn.metrics.pairwise.cosine_similarity: For calculating similarity scores.
    - transformers.BertModel, transformers.BertTokenizer, transformers.pipeline: For natural language processing tasks with BERT models.
    - torchvision.transforms, torchvision.models: For computer vision tasks with PyTorch models.
    - ast.literal_eval: For safely evaluating strings containing Python literals.
    - sentence_transformers.SentenceTransformer: For generating embeddings from text for semantic similarity.
"""

#Import libraries
import cv2
import instaloader
import json
import numpy as np
import pandas as pd
import re
import time
import requests
import torch
import requests
import matplotlib.pyplot as plt
import os, ast
from io import BytesIO
from instaloader import Post
from instaloader.exceptions import BadResponseException, ConnectionException, LoginRequiredException, TooManyRequestsException
from IPython.display import display, clear_output
from groq import Groq
from PIL import Image, ImageDraw
from transformers import BertModel, BertTokenizer, pipeline
from sklearn.metrics.pairwise import cosine_similarity
from torchvision import transforms, models
from ast import literal_eval
from torchvision import transforms, models
from sentence_transformers import SentenceTransformer
import streamlit as st


# Constants
KEY = "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"
BACKGROUND_IMAGE_URL = "https://img.freepik.com/premium-photo/abstract-blurred-background-interior-clothing-store-shopping-mall_44943-543.jpg"
FASHION_BRANDS = {
    "HM": {
        "Platform": "Instagram",
        "URL": "https://www.instagram.com/hm/",
        "Region": "Middle East",
        "Stats": {
            "Followers": "38.4m",
            "Avg. likes": "19500", #19.5k
            "Avg. comments": "179.6"
        }
    },
    "Stradivarius": {
        "Platform": "Instagram",
        "URL": "https://www.instagram.com/stradivarius/",
        "Region": "Middle East",
        "Stats": {
            "Followers": "8.3m",
            "Uploads": "4k",
            "Avg. likes": "4400", #4.4k
            "Avg. comments": "19"
        }
    },
    "MANGO": {
        "Platform": "Instagram",
        "URL": "https://www.instagram.com/mango/",
        "Region": "Middle East",
        "Stats": {
            "Followers": "15.5m",
            "Avg. likes": "2100", #2.1k
            "Avg. comments": "49.8"
        }
    },
    "BERSHKA": {
        "Platform": "Instagram",
        "URL": "https://www.instagram.com/bershka/",
        "Region": "Middle East",
        "Stats": {
            "Followers": "10.9m",
            "Avg. likes": "12200", #12.2k
            "Avg. comments": "95.9"
        }
    },
    "PullandBear": {
        "Platform": "Instagram",
        "URL": "https://www.instagram.com/pullandbear/",
        "Region": "Middle East",
        "Stats": {
            "Followers": "7.8m",
            "Uploads": "5.9k",
            "Avg. likes": "7200", #7.2k
            "Avg. comments": "15.6"
        }
    },
    "Max Fashion Mena": {
        "Platform": "Instagram",
        "URL": "https://www.instagram.com/maxfashionmena/",
        "Region": "Middle East",
        "Stats": {
            "Followers": "2.7m",
            "Uploads": "8.2k",
            "Avg. likes": "248.5",
            "Avg. comments": "167.3"
        }
    },
    "Shein Arabia": {
        "Platform": "Instagram",
        "URL": "https://www.instagram.com/shein_ar/",
        "Region": "Middle East",
        "Stats": {
            "Followers": "5.5m",
            "Uploads": "10.1k",
            "Avg. likes": "536.8",
            "Avg. comments": "149.8"
        }
    },
    "Malameh Fashion": {
        "Platform": "Instagram",
        "URL": "https://www.instagram.com/mlameh_fashion_official/",
        "Region": "KSA",
        "Stats": {
            "Followers": "1.5m",
            "Uploads": "6.5k",
            "Avg. likes": "436.1",
            "Avg. comments": "25.9",
            "Avg. activity": "63.96%"
        }
    },
    "DeFacto": {
        "Platform": "Instagram",
        "URL": "https://www.instagram.com/defacto/",
        "Region": "Middle East",
        "Stats": {
            "Followers": "3.4m",
            "Uploads": "10.8k",
            "Avg. likes": "13700", #13.7k
            "Avg. comments": "915.1",
            "Avg. activity": "150.46%"
        }
    }
}


# Helper functions
# Function to log in to Instagram
def login_instagram(username, password):
    """
    Authenticates and logs in to Instagram using the provided username and password.

    Parameters:
    - username (str): The Instagram username.
    - password (str): The Instagram password.

    Returns:
    - instaloader.Instaloader: The authenticated Instaloader instance if login is successful.
    - None: If an error occurs during the login process.
    """
    L = instaloader.Instaloader()
    try:
        L.login(username, password)
        return L
    except Exception as e:
        st.error(f"Error during login: {e}")
        return None
 

# Function to scrape a post from Instagram    
def scrape_instagram_post(L, post_link):
    """
    Scrapes data from an Instagram post and returns it as a DataFrame.

    Parameters:
    - L (instaloader.Instaloader): The authenticated Instaloader instance.
    - post_link (str): The URL of the Instagram post to scrape.

    Returns:
    - pd.DataFrame: A DataFrame containing the scraped post data, including post ID, shortcode, date, caption, likes, image URL, video URL, hashtags, mentions, and comments.
    - None: If an error occurs during the scraping process.
    """
    try:
        start_time = time.time()

        # Extract shortcode from the post link
        shortcode = post_link.split("/")[-2]

        # Load the post using the shortcode
        post = Post.from_shortcode(L.context, shortcode)

        # Initialize dictionary to hold the post data
        data = {
            "post_id": post.mediaid,
            "post_shortcode": post.shortcode,
            "post_date": post.date,
            "post_caption": post.caption,
            "post_likes": post.likes,
            "image_url": post.url if not post.is_video else None,
            "post_is_video": post.is_video,
            "post_hashtags": post.caption_hashtags,
            "post_mentions": post.caption_mentions,
            "video_url": post.video_url if post.is_video else None,
            "comments": []
        }

        # Get the total number of comments and likes  
        total_comments = post.comments
        post_likes = post.likes
        st.write(f"The post has {total_comments} comments and {post_likes} likes.")

        # Initialize progress bar
        st.write("Scraping Post comments...")
        scraping_progress_bar = st.progress(0)

        # Iterate over comments
        for i, comment in enumerate(post.get_comments(), start=1):
            if i % 5 == 0:
                scraping_progress_bar.progress(i / total_comments)  # Update progress bar
            data["comments"].append(str(comment.text))

        # Convert the data to a DataFrame
        df = pd.DataFrame([data])

        end_time = time.time()
        time_taken = end_time - start_time
        st.write(f"Time taken to scrape the post: {time_taken:.2f} seconds")

        return df

    except (BadResponseException, ConnectionException, TooManyRequestsException) as e:
        st.error(f"Error fetching post data: {e}")
        return None


# Function to clean a text
def clean_text(text):
    """
    Cleans a given text by removing URLs, hashtags, and mentions, and replacing newlines and tabs with spaces.

    This function performs the following text cleaning operations:
    - Removes any URLs (starting with http, https, or www).
    - Removes any hashtags (words starting with #).
    - Removes any mentions (words starting with @).
    - Replaces newline characters (\n) and tab characters (\t) with spaces.

    Parameters:
    - text (str): The text to be cleaned. If the input is not a string, an empty string is returned.

    Returns:
    - str: The cleaned text.
    """
    if not isinstance(text, str):
        return ""
    text = re.sub(r'http\S+|www\S+|https\S+', '', text, flags=re.MULTILINE)
    text = re.sub(r'#\w+', '', text)
    text = re.sub(r'@\w+', '', text)
    text = text.replace('\n', ' ').replace('\t', ' ')
    return text

# Initialize the sentence transformer model
model = SentenceTransformer('distilbert-base-nli-mean-tokens')

# Function to load and resize image from URL
def load_and_resize_image(image_url, max_pixels=178956970):
    """
    Loads an image from a URL and resizes it if its total pixel count exceeds a specified limit.

    Parameters:
    - image_url (str): The URL of the image to load.
    - max_pixels (int): The maximum number of pixels allowed in the image. Default is 178,956,970 pixels.

    Returns:
    - PIL.Image: The loaded and resized image.
    - None: If an error occurs during loading or resizing.
    """
    try:
        response = requests.get(image_url, stream=True)
        img = Image.open(response.raw)
        width, height = img.size
        if width * height > max_pixels:
            ratio = (max_pixels / (width * height)) ** 0.5
            new_width = int(width * ratio)
            new_height = int(height * ratio)
            img = img.resize((new_width, new_height))
        return img
    except Exception as e:
        st.error(f"Error loading or resizing image: {e}")
        return None


# Function to extract image features using a pre-trained model (e.g., VGG16)
def extract_image_features(img):
    """
    Extracts image features using the VGG16 pre-trained model after preprocessing the image.

    Args:
    - img (PIL Image): Image to extract features from.

    Returns:
    - np.ndarray: Numpy array of flattened image features.
    """
    preprocess = transforms.Compose([
        transforms.Resize(256),
        transforms.CenterCrop(224),
        transforms.ToTensor(),
        transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]),
    ])
    img_tensor = preprocess(img).unsqueeze(0)
    model_vgg = models.vgg16(pretrained=True)
    model_vgg.eval()

    # Extract features from the second last layer (before classification layer)
    feature_extractor = torch.nn.Sequential(*list(model_vgg.children())[:-1])

    with torch.no_grad():
        features = feature_extractor(img_tensor)

    return features.view(features.size(0), -1).numpy().flatten()


# Function to draw bounding boxes on an image with labels
def draw_boxes(image, detections):
    """
    Draws bounding boxes with labels on an image.

    Parameters:
    - image (PIL.Image): The image on which to draw the bounding boxes.
    - detections (list): A list of detections, where each detection is a dictionary with 'label' and 'box' keys.
        - 'label' (str): The label for the detection.
        - 'box' (dict): The bounding box coordinates with 'xmin', 'ymin', 'xmax', and 'ymax' keys.

    Returns:
    - PIL.Image: The image with the bounding boxes and labels drawn on it.
    """
    draw = ImageDraw.Draw(image)
    for detection in detections:
        label = detection['label']
        box = detection['box']
        xmin, ymin, xmax, ymax = box['xmin'], box['ymin'], box['xmax'], box['ymax']
        draw.rectangle([xmin, ymin, xmax, ymax], outline='red', width=3)
        draw.text((xmin, ymin), label, fill='white', align='center', font_size=25)
    return image


# Function to process a row of data
def process_row(row):
    """
    Processes a single row of data to perform image-based fashion item detection, comment analysis, 
    and similarity calculation to determine the most relevant fashion item in the image based on comments 
    and captions.

    Args:
        row (pd.Series): A pandas Series object representing a single row of data. 
                         Expected to contain 'image_url', 'clean_comments', and 'post_caption' fields.

    Returns:
        pd.Series: The updated row with additional fields 'most_similar_item' and 'selected_item_features'. 
                   Returns None if no relevant items are found or if an error occurs during processing.
    """
    try:
        # Load and resize post image from URL
        image_url = row['image_url']
        image = load_and_resize_image(image_url)

        # Perform object detection on the image
        object_detection = pipeline("object-detection", model="valentinafeve/yolos-fashionpedia")
        detections = object_detection(image_url)

        # Visualize object detection results on the original image
        image_with_boxes = draw_boxes(image.copy(), detections)
        plt.figure(figsize=(5, 3))
        plt.imshow(image_with_boxes)
        plt.axis('off')
        plt.title('Object Detection Results')
        st.pyplot(plt)
        
        # Extract labels to crop (adjust as per your requirements)
        labels_to_crop = ['dress', 'shirt', 'pants', 'jacket', 'skirt', 'top, t-shirt, sweatshirt']

        # Extract cropped images and their labels
        cropped_images = []
        for detection in detections:
            label = detection['label']
            if label in labels_to_crop:
                box = detection['box']
                xmin, ymin, xmax, ymax = box['xmin'], box['ymin'], box['xmax'], box['ymax']
                cropped_img = image.crop((xmin, ymin, xmax, ymax))
                cropped_images.append((cropped_img, label))

        if not cropped_images:
            return None

        # Convert clean_comments from string to list of comments
        clean_comments = row['clean_comments'].strip("[]").replace("'", "").split(", ")

        # Calculate embeddings for comments and post caption using Sentence Transformers
        comment_embeddings = model.encode(clean_comments, show_progress_bar=True)
        caption_embedding = model.encode([row['post_caption']], show_progress_bar=True)[0]

        similarities_total = {label: 0.0 for _, label in cropped_images}

        # Calculate cosine similarity between each label and each comment
        for img, label in cropped_images:
            item_embedding = model.encode([label])[0]
            for comment_embedding in comment_embeddings:
                similarity = cosine_similarity(np.array(comment_embedding).reshape(1, -1), np.array(item_embedding).reshape(1, -1))[0][0]
                similarities_total[label] += similarity

        # Calculate cosine similarity between each label and the caption
        for img, label in cropped_images:
            item_embedding = model.encode([label])[0]
            similarity = cosine_similarity(np.array(caption_embedding).reshape(1, -1), np.array(item_embedding).reshape(1, -1))[0][0]
            similarities_total[label] += similarity

        # Find the most similar fashion item based on total similarity
        most_similar_item = max(similarities_total, key=similarities_total.get)

        # Find the cropped image and extract its feature vector
        selected_image = None
        selected_image_features = None
        for cropped_img, label in cropped_images:
            if label == most_similar_item:
                selected_image = cropped_img
                selected_image_features = extract_image_features(selected_image)
                break

        # Display the selected cropped image
        if selected_image:
            plt.figure(figsize=(2, 2))
            plt.imshow(selected_image)
            plt.axis('off')
            plt.title(f'Selected Item: {most_similar_item}')
            st.pyplot(plt)

        # Update the row with the most similar item label and its feature vector
        row['most_similar_item'] = most_similar_item
        row['selected_item_features'] = selected_image_features.tolist() if selected_image_features is not None else None

        return row

    except Exception as e:
        st.error(f"Error processing row: {e}")
        return None
     
# Function to allow user to select a model for sentiment analysis  
def select_model():
    """
    Allows the user to select a model for sentiment analysis from a predefined list using a Streamlit selectbox.

    Returns:
    - str: The model identifier for the selected model.
    """
    model_options = {
        "Gemma 7b": 'gemma-7b-it',
        "Mixtral 8x7b": 'mixtral-8x7b-32768',
        "LLaMA3 70b": 'llama3-70b-8192',
        "LLaMA3 8b": 'llama3-8b-8192'
    }
    selected_model = st.selectbox("Select the model to use for sentiment analysis", list(model_options.keys()), index=None)
    return model_options[selected_model] if selected_model else None


# Function to analyze sentiments in batches using the Groq API
def analyze_sentiments_batch(client, comments, model="mixtral-8x7b-32768", temperature=0.7, batch_size=50):
    """
    Analyzes sentiments of a list of comments in batches using the specified model via the Groq API.

    Args:
        client: The client object to interact with the Groq API.
        comments (list): A list of comments to analyze.
        model (str): The name of the model to use for sentiment analysis. Default is "mixtral-8x7b-32768".
        temperature (float): The temperature parameter for the model to control the randomness of the output. Default is 0.7.
        batch_size (int): The number of comments to process in each batch. Default is 50.

    Returns:
        list: A list of sentiments corresponding to each comment. The sentiments can be 'positive', 'neutral', or 'negative'.
              Returns None if an error occurs during processing.
    """
    def analyze_single_batch(batch_comments):
        # Create the prompt with the batch of comments
        prompt = "Analyze the sentiment of the following comments on fashion posts in the context of fashion. Reply with 'positive', 'neutral', or 'negative' for each comment.\n\n"
        for i, comment in enumerate(batch_comments, 1):
            prompt += f"{i}. {comment}\n"

        # Send the prompt to the Groq API
        try:
            response = client.chat.completions.create(
                model=model,
                messages=[
                    {"role": "system", "content": "You are a helpful assistant."},
                    {"role": "user", "content": prompt}
                ],
                temperature=temperature
            )
        except Exception as e:
            st.error(f"Error in request: {e}")
            return None

        # Extract the response content
        response_content = response.choices[0].message.content

        # Parse the sentiments from the response
        sentiments = []
        for line in response_content.split("\n"):
            if line.strip():
                if 'positive' in line.lower():
                    sentiments.append('positive')
                elif 'neutral' in line.lower():
                    sentiments.append('neutral')
                elif 'negative' in line.lower():
                    sentiments.append('negative')
                else:
                    sentiments.append('unknown')

        return sentiments

    # Initialize progress bar
    st.write("Analyzing Sentiments...")
    sentiments_progress_bar = st.progress(0)

    # Split the comments into batches
    batched_sentiments = []
    total_batches = (len(comments) + batch_size - 1) // batch_size  # Calculate total batches needed

    for i in range(0, len(comments), batch_size):
        batch_comments = comments[i:i+batch_size]
        batch_sentiments = analyze_single_batch(batch_comments)

        # Handle errors in batch processing
        if batch_sentiments is None:
            st.error("An error occurred during sentiment analysis.")
            return None

        batched_sentiments.extend(batch_sentiments)

        # Update progress bar
        progress_value = min((i + batch_size) / len(comments), 1.0)  # Ensure progress is within [0.0, 1.0]
        sentiments_progress_bar.progress(progress_value)

    return batched_sentiments


# Function to count occurrences of a specific sentiment type in a list
def count_sentiments(sentiments, sentiment_type):
    """
    Counts the occurrences of a specific sentiment type in a list of sentiments.

    Args:
        sentiments (list): A list of sentiment strings.
        sentiment_type (str): The type of sentiment to count ('positive', 'neutral', 'negative').

    Returns:
        int: The count of the specified sentiment type in the list.
    """
    if not isinstance(sentiments, list):
        return 0

    return sum(1 for sentiment in sentiments if sentiment.lower() == sentiment_type.lower())


# Function to separate sentiment counts into positive, negative, and neutral
def separate_sentiments(df):
    """
    Separates and counts positive, negative, and neutral sentiments in a DataFrame column.

    Args:
        df (pd.DataFrame): The DataFrame containing a column named 'sentiments', which holds lists of sentiment strings.

    Returns:
        pd.DataFrame: The updated DataFrame with additional columns 'positive_count', 'negative_count', 'neutral_count',
                      and 'total_sentiments' representing the count of each sentiment type and the total number of sentiments.
    """
    df["positive_count"] = df["sentiments"].apply(lambda x: count_sentiments(eval(x), "positive") if isinstance(x, str) else 0)
    df["negative_count"] = df["sentiments"].apply(lambda x: count_sentiments(eval(x), "negative") if isinstance(x, str) else 0)
    df["neutral_count"] = df["sentiments"].apply(lambda x: count_sentiments(eval(x), "neutral") if isinstance(x, str) else 0)
    df["total_sentiments"] = df["sentiments"].apply(lambda x: len(eval(x)) if isinstance(x, str) else 0)
    return df


# Function to calculate sentiment scores for posts
def calculate_sentiment_scores(df, negativity_factor=1):
    """
    Calculates sentiment scores for posts based on counts of positive, negative, and neutral sentiments.

    Args:
        df (pd.DataFrame): The DataFrame containing sentiment counts and total sentiments.
        negativity_factor (float): A factor to weigh negative sentiments more heavily. Default is 1.

    Returns:
        pd.DataFrame: The updated DataFrame with an additional column 'sentiment_score' representing the sentiment score
                      for each post.
    """
    df = separate_sentiments(df)

    if df["total_sentiments"].iloc[0] == 0:
        df["sentiment_score"] = 0
        return df
    df["sentiment_score"] = (df["positive_count"] - negativity_factor * df["negative_count"]) / df["total_sentiments"]
    return df


# Function to normalize likes and comments based on averages
def normalize_likes_comments(df, avg_likes, avg_comments):
    """
    Normalizes likes and comment counts based on average likes and comments.

    Parameters:
    - df (pandas.DataFrame): The DataFrame containing 'post_likes' and 'comment_count' columns.
    - avg_likes (float): The average number of likes.
    - avg_comments (float): The average number of comments.

    Returns:
    - pandas.DataFrame: The updated DataFrame with normalized likes and comments added as new columns.

    """
    if avg_likes == 0 or avg_comments == 0:
        return df

    df["likes_normalized"] = df["post_likes"] / avg_likes
    df["comments_normalized"] = df["comment_count"] / avg_comments
    return df


# Function to determine if a post is trendy based on thresholds
def trendy_decision(df, likes_th=0.8, comments_th=0.2, sentiment_th=0.1):
    """
    Determines if a post is trendy based on normalized likes, comments, and sentiment scores.

    Parameters:
    - df (pandas.DataFrame): The DataFrame containing 'likes_normalized', 'comments_normalized', and 'sentiment_score' columns.
    - likes_th (float): The threshold for normalized likes. Default is 0.8.
    - comments_th (float): The threshold for normalized comments. Default is 0.2.
    - sentiment_th (float): The threshold for sentiment score. Default is 0.1.

    Returns:
    - pandas.DataFrame: The updated DataFrame with a new column 'is_trendy' indicating whether each post is trendy.

    """
    df['is_trendy'] = ((df['likes_normalized'] >= likes_th) &
                       (df['sentiment_score'] >= sentiment_th) &
                       (df['comments_normalized'] >= comments_th)).astype(int)
    return df



# Streamlit app configuration
st.set_page_config(
    page_title="Fashion Trends Spotting",
    page_icon=":dress:",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Apply background image
page_bg_img = f"""
<style>
[data-testid="stAppViewContainer"] > .main {{
background-image: url("{BACKGROUND_IMAGE_URL}");
background-size: cover;
background-position: top;
background-attachment: scroll;
}}

[data-testid="stHeader"] {{
background: rgba(0, 0, 0, 0);
}}
</style>
"""
st.markdown(page_bg_img, unsafe_allow_html=True)

# Streamlit app
if 'step' not in st.session_state:
    st.session_state.step = 0

def go_to_home():
    """
    Resets the current step to the home step (step 0) in the Streamlit session state.

    This function sets the 'step' key in the Streamlit session state to 0, navigating the user to the home step.
    """
    st.session_state.step = 0

def go_to_next_step():
    """
    Advances the current step by 1 in the Streamlit session state.

    This function increments the 'step' key in the Streamlit session state by 1, navigating the user to the next step.
    """
    st.session_state.step += 1

def go_to_previous_step():
    """
    Decreases the current step by 1 in the Streamlit session state.

    This function decrements the 'step' key in the Streamlit session state by 1, navigating the user to the previous step.
    """
    st.session_state.step -= 1

def reset_session_state():
    """
    Resets all keys in the Streamlit session state and sets the current step to the home step (step 0).

    This function deletes all keys in the Streamlit session state and sets the 'step' key to 0, effectively resetting the session state.
    """
    for key in st.session_state.keys():
        del st.session_state[key]
    st.session_state.step = 0

def add_home_button():
    """
    Adds a "Home" button to the Streamlit app that navigates the user to the home step when clicked.

    This function creates a layout with two columns, placing the "Home" button in the first column. When the button is clicked, it triggers the go_to_home function.
    """
    col1, col2 = st.columns([1, 9])
    with col1:
        st.button("Home", on_click=go_to_home)


# Landing page
if st.session_state.step == 0:
    st.title("Welcome to the Fashion Trends Spotting App")
    st.write("This app helps you analyze fashion trends based on Instagram posts from popular brands in the Middle East.")
    st.button("Start", on_click=go_to_next_step)

# Step 1: Login to Instagram
elif st.session_state.step == 1:
    add_home_button()
    st.title("Step 1: Login to Instagram")
    username = st.text_input("Enter your Instagram username", value="")
    password = st.text_input("Enter your Instagram password", type="password", value="")
    if st.button("Login"):
        if not username or not password:
            st.error("Please provide both username and password.")
        else:
            L = login_instagram(username, password)
            if L:
                st.success("Logged in successfully.")
                st.session_state.L = L

    # Button placement
    col1, _, col3 = st.columns([1, 8, 1])
    with col1:
        st.button("Previous", on_click=go_to_home)
    with col3:
        st.button("Next", on_click=go_to_next_step)

# Step 2: Select Brand
elif st.session_state.step == 2:
    add_home_button()
    st.title("Step 2: Select Brand")
    selected_brand = st.selectbox("Select a fashion brand", list(FASHION_BRANDS.keys()), index=None)
    if selected_brand:
        st.session_state.selected_brand = selected_brand  # Store selected brand in session state
        brand_info = FASHION_BRANDS[selected_brand]

        # Display brand information and stats in a boxed format with background color
        st.markdown(f"""
            <div style='background-color: #f0f0f0; padding: 20px; border-radius: 10px; box-shadow: 0 0 10px rgba(0, 0, 0, 0.1);'>
                <h2>{selected_brand}</h2>
                <p><strong>Platform:</strong> {brand_info['Platform']}</p>
                <p><strong>URL:</strong> <a href='{brand_info['URL']}' target='_blank'>{brand_info['URL']}</a></p>
                <p><strong>Region:</strong> {brand_info['Region']}</p>
                <h3>Stats:</h3>
                <ul>
                    {"".join([f"<li><strong>{stat}:</strong> {value}</li>" for stat, value in brand_info['Stats'].items()])}
                </ul>
            </div>
        """, unsafe_allow_html=True)

    # Button placement
    col1, _, col3 = st.columns([1, 8, 1])
    with col1:
        st.button("Previous", on_click=go_to_previous_step)
    with col3:
        st.button("Next", on_click=go_to_next_step)

# Step 3: Enter Post Link
elif st.session_state.step == 3:
    add_home_button()
    st.title("Step 3: Enter Post Link")
    post_link = st.text_input("Enter the Instagram post link", value="")
    if st.button("Fetch Post"):
        if not post_link:
            st.error("Please provide a post link.")
        else:
            df = scrape_instagram_post(st.session_state.L, post_link)
            if df is not None:
                st.session_state.df = df

                # Display fetched post details in a structured manner
                st.markdown("### Fetched Post Details")
                col1, col2 = st.columns([1, 2])
                with col1:
                    if df['post_is_video'].iloc[0]:
                        video_url = df['video_url'].iloc[0]
                        if video_url:
                            # Embed video in an HTML video tag
                            st.markdown(f"""
                                <video width="100%" height="auto" controls>
                                    <source src="{video_url}" type="video/mp4">
                                    Your browser does not support the video tag.
                                </video>
                            """, unsafe_allow_html=True)
                        else:
                            st.error("Video URL not available.")
                    else:
                        image_url = df['image_url'].iloc[0]
                        if image_url:
                            # Fetch the image content
                            response = requests.get(image_url)
                            image = Image.open(BytesIO(response.content))
                            st.image(image, caption='Instagram Post Image', use_column_width=True)
                        else:
                            st.error("Image URL not available.")
                with col2:
                    st.write(f"*Post ID:* {df['post_id'].iloc[0]}")
                    st.write(f"*Post Shortcode:* {df['post_shortcode'].iloc[0]}")
                    st.write(f"*Post Date:* {df['post_date'].iloc[0]}")
                    st.write(f"*Caption:* {df['post_caption'].iloc[0]}")
                    st.write(f"*Likes:* {df['post_likes'].iloc[0]}")
                    st.write(f"*Is Video:* {'Yes' if df['post_is_video'].iloc[0] else 'No'}")
                    st.write(f"*Hashtags:* {' '.join(df['post_hashtags'].iloc[0])}")
                    st.write(f"*Mentions:* {' '.join(df['post_mentions'].iloc[0])}")

                # Display the DataFrame
                #st.markdown("### Scraped Post Data")
                #st.write(df)

    # Button placement
    col1, _, col3 = st.columns([1, 8, 1])
    with col1:
        st.button("Previous", on_click=go_to_previous_step)
    with col3:
        st.button("Next", on_click=go_to_next_step)

# Step 4: Clean Comments
elif st.session_state.step == 4:
    add_home_button()
    st.title("Step 4: Clean Comments")
    if "df" in st.session_state and not st.session_state.df.empty:
        df = st.session_state.df

        comments = df["comments"].iloc[0]
        clean_comments = [clean_text(comment) for comment in comments]

        # Convert the clean_comments list to a string for storage
        df.at[0, "clean_comments"] = str(clean_comments)
        df["comment_count"] = df["clean_comments"].apply(lambda x: len(eval(x)) if isinstance(x, str) else 0)
        st.session_state.df = df

        # Display cleaned comments in a collapsible box with scrollable content
        with st.expander("View Cleaned Comments", expanded=True):
            comments_content = "<br>".join(clean_comments)
            st.markdown(f"""
                <div style='background-color: #f0f0f0; padding: 10px; border-radius: 5px;'>
                    <div style='max-height: 300px; overflow-y: auto;'>
                        {comments_content}
                    </div>
                </div>
            """, unsafe_allow_html=True)

    # Button placement
    col1, _, col3 = st.columns([1, 8, 1])
    with col1:
        st.button("Previous", on_click=go_to_previous_step)
    with col3:
        st.button("Next", on_click=go_to_next_step)


# Step 5: Select a fashion item from the image
elif st.session_state.step == 5:
    add_home_button()
    st.title("Step 5: Select a Fashion Item From The Image")
    if "df" in st.session_state and not st.session_state.df.empty:
        df = st.session_state.df

        # Process the first row of the DataFrame
        row = df.iloc[0]
        processed_row = process_row(row)
        
        if processed_row is not None:
            # Ensure the keys in processed_row match the DataFrame columns
            for key in processed_row.keys():
                if key not in df.columns:
                    df[key] = None  # Add the new key as a column with None values
            
            # Update the first row with the processed data
            for key, value in processed_row.items():
                df.at[0, key] = value

            st.session_state.df = df
            most_similar_item = processed_row["most_similar_item"]
            st.write(f"The most similar fashion item based on the image and comments is: **{most_similar_item}**")

            # Display the selected item features if available
            #if "selected_item_features" in processed_row and processed_row["selected_item_features"]:
                #st.write("Selected Item Features:", processed_row["selected_item_features"])
        else:
            st.error("No fashion items detected in the image or an error occurred during processing.")

    # Button placement
    col1, _, col3 = st.columns([1, 8, 1])
    with col1:
        st.button("Previous", on_click=go_to_previous_step)
    with col3:
        st.button("Next", on_click=go_to_next_step)


elif st.session_state.step == 6:
    add_home_button()
    st.title("Step 6: Perform Sentiment Analysis")
    if "df" in st.session_state and not st.session_state.df.empty:
        st.write("Post Data:", st.session_state.df[["post_caption", "post_likes", "post_hashtags", "post_mentions"]])
        model = select_model()
        if model:
            comments = st.session_state.df["clean_comments"].iloc[0]

            # Convert clean_comments back to a list
            if isinstance(comments, str):
                clean_comments = eval(comments)
            else:
                st.error("Comments are not in the expected format.")
                clean_comments = []

            if st.button("Analyze Sentiments"):
                client = Groq(api_key=KEY)

                sentiments = analyze_sentiments_batch(client, clean_comments, model)
                if sentiments:
                    # Ensure the lengths match by trimming excess sentiments if needed
                    if len(clean_comments) > len(sentiments):
                        st.warning("Mismatch in number of comments and sentiments. Some comments may not have been analyzed.")
                        sentiments.extend(['unknown'] * (len(clean_comments) - len(sentiments)))

                    st.session_state.df["sentiments"] = str(sentiments)

                    # Calculate sentiment scores based on batched sentiments
                    st.session_state.df = calculate_sentiment_scores(st.session_state.df)

                    # Optionally display sentiment scores if needed
                    # st.write("Sentiment Scores:", st.session_state.df[["positive_count", "negative_count", "neutral_count", "sentiment_score"]])
                else:
                    # Ensure sentiments column exists even if there are no comments
                    st.session_state.df["sentiments"] = str([])
                    st.session_state.df = calculate_sentiment_scores(st.session_state.df)

    # Button placement and navigation
    col1, _, col3 = st.columns([1, 8, 1])
    with col1:
        st.button("Previous", on_click=go_to_previous_step)
    with col3:
        st.button("Next", on_click=go_to_next_step)


# Step 7: Sentiment Analysis Results
elif st.session_state.step == 7:
    add_home_button()
    st.title("Step 7: Sentiment Analysis Results")
    if "df" in st.session_state and not st.session_state.df.empty:
        df = st.session_state.df
        df = calculate_sentiment_scores(df)
        st.write("Sentiment Scores:", df[["positive_count", "negative_count", "neutral_count", "sentiment_score"]])
        avg_likes = float(FASHION_BRANDS[st.session_state.selected_brand]["Stats"].get("Avg. likes", 0))
        avg_comments = float(FASHION_BRANDS[st.session_state.selected_brand]["Stats"].get("Avg. comments", 0))
        df = normalize_likes_comments(df, avg_likes, avg_comments)
        st.write("Normalized Likes and Comments:", df[["likes_normalized", "comments_normalized"]])
        df = trendy_decision(df)
        st.session_state.result_df = df

    # Button placement
    col1, _, col3 = st.columns([1, 8, 1])
    with col1:
        st.button("Previous", on_click=go_to_previous_step)
    with col3:
        st.button("Next", on_click=go_to_next_step)

# Step 8: Final Decision on Trendiness
elif st.session_state.step == 8:
    add_home_button()
    st.title("Step 8: Trendy Decision")

    # Add sliders for likes_th, comments_th, and sentiment_th
    likes_th = st.slider("Likes Threshold", min_value=0.0, max_value=1.0, value=0.8, step=0.01)
    comments_th = st.slider("Comments Threshold", min_value=0.0, max_value=1.0, value=0.2, step=0.01)
    sentiment_th = st.slider("Sentiment Threshold", min_value=-1.0, max_value=1.0, value=0.1, step=0.01)

    # Add Predict button
    if st.button("Predict"):
        if "result_df" in st.session_state and not st.session_state.result_df.empty:
            df = st.session_state.result_df

            # Use the values from the sliders in the trendy_decision function
            df = trendy_decision(df, likes_th=likes_th, comments_th=comments_th, sentiment_th=sentiment_th)
            is_trendy = df["is_trendy"].iloc[0]

            # Display trendy decision in a boxed format with background color
            if is_trendy:
                st.markdown("""
                    <div style='background-color: #c8e6c9; padding: 10px; border-radius: 5px;'>
                        <p style='color: green;'>The analyzed post is trendy!</p>
                    </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown("""
                    <div style='background-color: #ffcdd2; padding: 10px; border-radius: 5px;'>
                        <p style='color: red;'>The analyzed post is not trendy.</p>
                    </div>
                """, unsafe_allow_html=True)

    # Button placement
    col1, _, col3 = st.columns([1, 8, 1])
    with col1:
        st.button("Previous", on_click=go_to_previous_step)
    with col3:
        st.button("Finish", on_click=reset_session_state)
