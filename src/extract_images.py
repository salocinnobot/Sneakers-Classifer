## Driver
from ssl import Options
from webbrowser import Chrome

## Image Manipulation
import urllib
from PIL import Image
import matplotlib.pyplot as plt
import io

## Saving image
import requests
import time
import shutil
import os

## Image Url Test
import urllib

## Selenium
import selenium
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

## Saving Image
def save_image(url, path): 
    try:
        response = requests.get(url, stream = True)
            # delay to avoid corrupted previews
        time.sleep(1)
        with open(path, 'wb+') as out_file:
            shutil.copyfileobj(response.raw, out_file)
    except Exception as e:
        print(e)

## Tests if our images can be saved as JPEG
def test_image(url):
    try: 
        image = Image.open(urllib.request.urlopen(url)).resize((256,256))
        image_bytes = io.BytesIO()
        image.save(image_bytes, format='JPEG')
    except Exception as e: 
        raise(e)


## Converts our images from url to image, resizes them, and saves them as binary then returns a list of images in binary
def load_images(image_urls):

    images = []

    ## Open the image, resize, and convert to bytes
    for iu in image_urls:
        try: 
            image = Image.open(urllib.request.urlopen(iu)).resize((256,256))
            image_bytes = io.BytesIO()
            image.save(image_bytes, format='JPEG')
            images.append(image_bytes.getvalue())
        except Exception as e:
            print(e)
    return images

## Driver
def select_driver(driver_path):
    
    service = Service(driver_path)

    ## Add any chrome options, such as headless (supress open window) using "chrome_options.add_argument("--headless")
    chrome_options = webdriver.ChromeOptions()
    
    return webdriver.Chrome(service=service, options=chrome_options)

## Extracting Images
def extract(query, max_num_links, driver, sleep): 

    ## Scroll to the end of the page, used for loading the next page
    def scroll_to_end(driver):
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(sleep)


    search_url = 'https://www.google.com/search?safe=off&site=&tbm=isch&source=hp&q={q}&oq={q}&gs_l=img'
    driver.get(search_url.format(q = query))

    urls = set()
    image_count = 0
    results_start = 0

    while len(urls) < max_num_links: 
        ##scroll_to_end(driver)

        ## Our thumbnail results are all of the images in our results
        thumbnail_results = driver.find_elements(By.CSS_SELECTOR, 'img.Q4LuWd')
        num_results = len(thumbnail_results)
        print(num_results)


        print(2)
        print(f"Found: {num_results} search results. Extracting links from {results_start}:{num_results}")

        while len(urls) != max_num_links:
            for object in thumbnail_results[results_start:num_results]:
                try: 
                    WebDriverWait(driver, 5).until(EC.element_to_be_clickable(object)).click()
                except Exception as e:
                    print(e)
                    continue;

                ## Our image object is the extractable image
                image_object = driver.find_elements(By.CSS_SELECTOR, 'img.n3VNCb')
                for image in image_object: 
                    if len(urls) != max_num_links:
                        ## The image link
                        if (image.get_attribute('src') and 'http' in image.get_attribute('src')):
                            url = image.get_attribute('src')
                            try:
                                urllib.request.urlopen(url)
                                test_image(url)
                            except: 
                                print("Error Here, going to the next image")
                                continue;
                            urls.add(url)
                            print(f'Amount of images {len(urls)} | url: {url}')
                    else: 
                        break;

                if len(urls) == max_num_links:
                    break
                
            
        else:

            if len(urls) == max_num_links:
                print(f"Completed: Found {max_num_links} images")
            else: 
                print("Found:", len(urls), "image links, looking for more ...")
                time.sleep(30)
                load_more_button = driver.find_element(By.CSS_SELECTOR, ".mye4qd")
                if load_more_button:
                    driver.execute_script("document.querySelector('.mye4qd').click();")

    return list(urls)
