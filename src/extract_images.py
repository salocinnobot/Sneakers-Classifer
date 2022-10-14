## Driver
from ssl import Options
from urllib.request import urlopen
from webbrowser import Chrome

## Image Manipulation
import urllib3
from PIL import Image
import matplotlib.pyplot as plt
import io

## Saving image
import requests
import time
import shutil
import os

## Image Url Test
import urllib3
from urllib3.util import Retry
from urllib3.request import RequestMethods

## Selenium
import selenium
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

## Creates directory if it does not exits
def check_dir(path, folder, create: bool):
    root = path
    if folder not in os.listdir(root) and create:
        os.mkdir(os.path.join(root, folder))
    return 

## Saving image to our url path
def save_image(binary, path): 
    try:
        with open(path, 'wb+') as file:
            file.write(binary)
    except Exception as e:
        raise(e)

## Tests to see if our url is valid, and return the url
def test_url(url): 
    try:
        timeout = urllib3.Timeout(total = 10)
        retries = urllib3.Retry(total = 3, backoff_factor=0.1)
        http = urllib3.PoolManager(retries = retries, timeout = timeout)
        response = http.urlopen(method = 'GET', url = url)
    except Exception as e:
        raise(e)
    return url

## Tests if our images can be saved as JPEG, and returns the image binary
def test_image(url):
    try: 
        timeout = urllib3.Timeout(total = 10)
        retries = urllib3.Retry(total = 3, backoff_factor=0.1)
        http = urllib3.PoolManager(retries = retries, timeout = timeout)
        image = http.urlopen(method = 'GET', url = url).data
        image = Image.open(io.BytesIO(image)).resize((256,256))
        image_bytes = io.BytesIO()
        image.save(image_bytes, format='JPEG')
    except Exception as e: 
        raise(e)
    return image_bytes.getvalue()

## Converts our images from url to image, resizes them, and saves them as binary then returns a list of images in binary
def load_images(image_urls):

    images = []

    ## Open the image, resize, and convert to bytes
    for iu in image_urls:
        try: 
            timeout = urllib3.Timeout(total = 10)
            retries = urllib3.Retry(total = 3, backoff_factor=0.1)
            http = urllib3.PoolManager(retries = retries, timeout = timeout)
            image = http.urlopen(method = 'GET', url = iu).data
            image = Image.open(io.BytesIO(image)).resize((256,256))
            image_bytes = io.BytesIO()
            image.save(image_bytes, format='JPEG')
            images.append(image_bytes.getvalue())
        except Exception as e:
            raise(e)
    return images

## Driver for Selenium
def select_driver(driver_path):
    
    service = Service(driver_path)

    ## Add any chrome options, such as headless (supress open window) using "chrome_options.add_argument("--headless")
    chrome_options = webdriver.ChromeOptions()
    
    return webdriver.Chrome(service=service, options=chrome_options)

## Checking category
def category(resell_link, driver, sleep): 
    
    try: 
        driver.get(resell_link)
        results = driver.get(By.XPATH, '/html/body/div[2]/div/main/div/script[1]')
        print(results)

    except Exception as e:
        raise(e)




## Extracting Images
def extract(query, max_num_links, path, driver, sleep): 

    url_paths = set()
    url_map = dict()
    url_avg_size = 0

    ## Scroll to the end of the page, used for loading the next page
    def scroll_to_end(driver):
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(sleep)


    search_url = 'https://www.google.com/search?safe=off&site=&tbm=isch&source=hp&q={q}&oq={q}&gs_l=img'
    driver.get(search_url.format(q = query))

    results_start = 0

    while len(url_paths) < max_num_links: 
        ##scroll_to_end(driver)

        ## Our thumbnail results are all of the images in our results
        thumbnail_results = driver.find_elements(By.CSS_SELECTOR, 'img.Q4LuWd')
        num_results = len(thumbnail_results)
        print(f"Found: {num_results} search results. Extracting links from {results_start}:{num_results}")

        while len(url_paths) != max_num_links:
            for object in thumbnail_results[results_start:num_results]:
                try: 
                    WebDriverWait(driver, 5).until(EC.element_to_be_clickable(object)).click()
                except Exception as e:
                    print(e)
                    continue;

                ## Our image object is the extractable image
                image_object = driver.find_elements(By.CSS_SELECTOR, 'img.n3VNCb')
                for image in image_object: 
                    if len(url_paths) != max_num_links:
                        ## The image link
                        if (image.get_attribute('src') and 'http' in image.get_attribute('src')):
                            url = image.get_attribute('src')
                            try:
                                url_check = test_url(url)
                                url not in url_map
                            except Exception as e: 
                                print(f"{e.args} | Error Here, going to the next image")
                                continue;
                            try: 
                                binary_check = test_image(url)
                            except Exception as e:
                                 print(f"{e.args} | Error Here, going to the next image")
                                 continue;
    
                            ## Add the url to the map
                            url_map[url] = str(len(url_paths)+1)

                            ## Check that the index is not in our directory, and create the path 
                            check_dir(path, url_map[url], False)
                            url_path = os.path.join(path, url_map[url])

                            ## Save the image to the path
                            save_image(binary_check, url_path)

                            url_avg_size = ((url_avg_size)*(len(url_paths)/(len(url_paths)+1))) + ((os.stat(url_path).st_size)/(len(url_paths)+1))
                            print(f'Average image size for folder {url_avg_size}')

                            url_paths.add(url_path)

                            print(f'Amount of images {len(url_paths)} | url: {url} | url path: {url_path}')
                    else: 
                        break;

                if len(url_paths) == max_num_links:
                    break
                
            
        else:

            if len(url_paths) == max_num_links:
                print(f"Completed: Found {max_num_links} images")
            else: 
                print("Found:", len(url_paths), "image links, looking for more ...")
                time.sleep(30)
                load_more_button = driver.find_element(By.CSS_SELECTOR, ".mye4qd")
                if load_more_button:
                    driver.execute_script("document.querySelector('.mye4qd').click();")

    return (url_avg_size, url_map, url_paths)
