from scraping_common import *
import time
import datetime
from collections import OrderedDict

def login(driver, main_url, user, password):
    """Enters user and password in main URL.
    """
    driver.get(main_url)

    wait = WebDriverWait(driver, 20)
    try:
        # loader = wait.until(EC.visibility_of_element_located\
        #     ((By.ID, 'app-loader')))
        # while loader:
        loader = wait.until_not(EC.visibility_of_element_located\
            ((By.ID, 'app-loader')))
       
        driver.find_element_by_xpath('//a[contains(@class, "account-login-link")]').click()
        
        login_button = driver.find_element_by_xpath(
            '//a[contains(@href, "/Authenticate/SignIn")]')
    except NoSuchElementException:
        print('No located')

    except Exception:
        print('Already logged in.')
        return
    
    login_button.click()
    # driver.execute_script("arguments[0].click();", login_button)

    # username_field = wait.until(
    #     EC.presence_of_element_located((By.ID, 'username'))
    # )
    username_field = driver.find_element_by_id('username')
    username_field.send_keys(user)

    pass_field = driver.find_element_by_id('password')
    pass_field.send_keys(password)

    driver.find_element_by_id('submitButton').click()

    driver.implicitly_wait(10)


def extract_links(driver):
    wait = WebDriverWait(driver, 10)

    urls = wait.until(EC.presence_of_all_elements_located\
        ((By.XPATH, '//li[contains(@class, "list-item linked")]//a')))
    names = [a.text for a in urls]
    urls = [url.get_attribute('href') for url in urls]
    
    results = {url:name for url, name in zip(urls, names)}

    return results


def extract_vehicle_data(driver, year, url, make, model, submodel):
    """Extracts vehicle data and returns it in format.
    """
    driver.get(url)
    time.sleep(10)
    data = OrderedDict()

    data['date_of_data'] = datetime.date.today()
    data['year'] = year
    data['make'] = make
    data['model'] = model
    data['submodel'] = submodel
    
    try:
        data['undertitle'] = driver.find_element_by_xpath(
            '//div[contains(@class, "vehicle-specs")]').text.encode('utf-8')
    except NoSuchElementException:
        print('Error scraping undertitle at {}'.format(url))
    
    try:
        data['avg_value'] = driver.find_element_by_xpath(
            '//span[contains(@class, "amount")]').text.encode('utf-8')
    except NoSuchElementException:
        print('Error scraping average value at {}'.format(url))

    try:
        data['model_overview'] = driver.find_element_by_xpath(
            '//div[contains(@class, "summary")]').text.encode('utf-8')
    except NoSuchElementException:
        pass
    finally:
        data['model_overview'] = driver.find_element_by_xpath(
            '//div[contains(@class, "summary")]').text.encode('utf-8')

    return data 
    

if __name__ == "__main__":
    driver = get_chromedriver(user_agent=get_user_agent(), images=False, 
        fast_load=False)
    
    main_url = 'https://www.hagerty.com/apps/valuationtools/search/auto'

    logged = False
    while not logged:
        try:
            login(driver, main_url, 'pauledoux@hotmail.com', 'Ni$$anSkyline')
            logged = True
        except Exception as e:
            print(str(e))
            pass

    make_urls = extract_links(driver)
    vehicles_data = list()

    current_make = None
    current_model = None
    current_submodel = None
    current_year = None

    try:
        for make_url, make_name in make_urls.items():
            done = False
            while not done:
                try:
                    driver.get(make_url)
                    done = True
                except Exception as e:
                    print('Retrying {} '.format(make_url))

            current_make = make_name
            try:
                models_urls = extract_links(driver)
            except Exception:
                break
            for model_url, model_name in models_urls.items():
                done = False
                while not done:
                    try:
                        driver.get(model_url)
                        done = True
                    except Exception as e:
                        print('Retrying {} '.format(make_url))

                current_model = model_name
                try:
                    submodel_urls = extract_links(driver)
                except Exception:
                    break
                for submodel_url, submodel_name in submodel_urls.items():
                    done = False
                    while not done:
                        try:
                            driver.get(submodel_url)
                            done = True
                        except Exception as e:
                            print('Retrying {} '.format(make_url))

                    current_submodel = submodel_name
                    try:
                        years_urls = extract_links(driver)
                    except Exception:
                        break
                    for year_url, year_name in years_urls.items():
                        done = False
                        while not done:
                            try:
                                driver.get(year_url)
                                done = True
                            except Exception as e:
                                print('Retrying {} '.format(make_url))

                        current_year = year_name
                        try:
                            vehicle_urls = extract_links(driver)
                        except Exception:
                            break
                        for vehicle_url, vehicle_name in vehicle_urls.items():
                            scraped = False
                            repeated_times = 0
                            while not scraped and repeated_times <= 10:
                                try:
                                    vehicle_data = extract_vehicle_data(driver=driver, 
                                        url=vehicle_url,
                                        make=current_make, 
                                        model=current_model, 
                                        submodel=current_submodel, 
                                        year=current_year)
                                    vehicles_data.append(vehicle_data)
                                    scraped = True
                                except KeyboardInterrupt:
                                    dict_to_csv(vehicles_data, ['date_of_data', 'year', 'make', 'model',
                                    'submodel', 'undertitle', 'avg_value', 'model_overview'])
                                    scraped = True
                                    break
                                except Exception:
                                    repeated_times += 1
                                    pass
                                finally:
                                    print('{} Scraped.'.format(driver.current_url))
    except KeyboardInterrupt:
        dict_to_csv(vehicles_data, ['date_of_data', 'year', 'make', 'model',
        'submodel', 'undertitle', 'avg_value', 'model_overview'])
    except Exception as e:
        print('Error: \n{}'.format(e))
    finally:
        dict_to_csv(vehicles_data, ['date_of_data', 'year', 'make', 'model',
        'submodel', 'undertitle', 'avg_value', 'model_overview'])
                        


