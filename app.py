from flask import Flask, render_template, request
from selenium import webdriver
from selenium.webdriver.common.by import By
import os
import time
import csv
import matplotlib.pyplot as plt

app = Flask(__name__)


def update_cars(car_link=None):
    if not os.path.exists('cars.csv') or (time.time() - os.path.getmtime('cars.csv')) > 1200 or car_link is not None:
        browser = webdriver.Chrome(f"{os.getcwd()}/chromedriver.exe")
        next_page = True
        link = car_link
        car_list = []
        while next_page:
            browser.get(link)
            time.sleep(2)
            cars = browser.find_elements(by=By.CSS_SELECTOR, value=".searchResultsItem")
            for c in cars:
                if c.get_attribute("data-id") is not None:
                    infos = c.find_elements(by=By.CSS_SELECTOR, value='.searchResultsAttributeValue')
                    price = c.find_elements(by=By.CSS_SELECTOR, value='.searchResultsPriceValue')
                    location = c.find_elements(by=By.CSS_SELECTOR, value='.searchResultsLocationValue')
                    curr_car_link = c.find_elements(by=By.CSS_SELECTOR,
                                                    value='.searchResultsLargeThumbnail:nth-child(1)')
                    try:
                        car_list.append({'year': int(infos[0].text),
                                         'km': int(infos[1].text.replace('.', '')),
                                         'color': infos[2].text,
                                         'price': int(price[0].text.replace('.', '').replace('TL', '')),
                                         'location': location[0].text.replace('\n', ' '),
                                         'linkItem': curr_car_link[0].find_element(by=By.TAG_NAME,
                                                                                   value='a').get_attribute(
                                             'href')
                                         })
                    except:
                        continue
                else:
                    continue

            time.sleep(1)
            next_link = browser.find_elements(by=By.CSS_SELECTOR, value=".prevNextBut")
            next_page = False if len(next_link) == 0 else True
            for n in next_link:
                if n.get_attribute('title') == 'Sonraki':
                    link = n.get_attribute('href')
                    next_page = True
                else:
                    next_page = False

        browser.close()

        with open('cars.csv', 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow([car_link])
            writer.writerow(['year', 'km', 'color', 'price', 'location'])
            for car in car_list:
                writer.writerow([car['year'], car['km'], car['color'], car['price'], car['location'], car['linkItem']])
    else:
        car_list = []
        with open('cars.csv', 'r') as f:
            reader = csv.reader(f)
            for row in reader:
                try:
                    if row[:5] == 'https':
                        continue
                    else:
                        car_list.append({'year': int(row[0]),
                                         'km': int(row[1]),
                                         'color': row[2],
                                         'price': int(row[3]),
                                         'location': row[4],
                                         'linkItem': row[5]
                                         })
                except:
                    continue
    return car_list


def get_link_csv():
    with open('cars.csv', 'r') as f:
        lines = f.read()
        first = lines.split('\n', 1)[0]
        return first


@app.route('/image.jpg')
def image():
    car_list = update_cars()
    plt.figure(figsize=(10, 8))
    plt.xlabel('KM')
    plt.ylabel('Price [TL]')
    title = ' '.join(get_link_csv()[27:].split('-')).title()
    plt.title(title)
    plt.scatter(list(map(lambda x: x['km'], car_list)), list(map(lambda x: x['price'], car_list)))
    plt.savefig('image.jpg')
    return open('image.jpg', 'rb').read()


@app.route('/', methods=['GET', 'POST'])
def index():
    show_output = False
    car_link = request.form.get('car_link')
    print()
    if car_link is not None:
        if car_link == get_link_csv():
            car_list = update_cars()
        else:
            car_list = update_cars(car_link)
        show_output = True
    else:
        car_list = []
    return render_template("index.html",
                           title="Flask Project",
                           cars=sorted(car_list, key=lambda x: x['price']),
                           show_output=show_output
                           )


if __name__ == '__main__':
    app.run()
