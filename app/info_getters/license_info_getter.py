from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait, TimeoutException
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException

from logger import logger

class LicenseInfoGetter:

    @classmethod
    def get_info_about_license(cls, vat_number : int | str) -> dict:
        cls.vat_number = str(vat_number)
        options = webdriver.ChromeOptions()
        options.add_argument('--headless')
        with webdriver.Chrome(options=options) as driver:
            cls.driver = driver
            link = cls.__get_link_with_license_page()
            return cls.__parse_html(link)
        
    @classmethod
    def __get_link_with_license_page(cls):
        try:
            cls.driver.get('https://license.gov.by/')
            cls.driver.find_element(By.XPATH, '//*[@id="header"]/div[1]/div[3]/div/div/div/ul/li/div/span[1]/input').send_keys(str(cls.vat_number))
            elements = WebDriverWait(cls.driver, 2).until(
                    EC.presence_of_all_elements_located((By.CLASS_NAME, "active")))
            link = elements[-1].get_attribute('href')
            return link
        except Exception as e:
            logger.exception(f"Link can't be given: {e}")
            raise e
    
    @classmethod
    def __parse_html(cls, link : str) -> dict:
        try:
            cls.driver.get(link)
            parser = LicenseHTMLParserCommands(cls.driver)
            parser.wait_until_located(By.XPATH, "//*[text()='Наименование органа, предоставившего лицензию:']")

            chunk_1 = {
                'agency' : parser.get_agency_info(),
                'activity_type' : parser.get_activity_type(),
                'license_status' : parser.get_license_status(),
                'license_number' : parser.get_license_number(),
                'license_from' : parser.get_license_from(),
                'full_activity_info' : parser.get_full_activity_info(),
                'short_activity_info' : parser.get_short_activity_info(),
            }

            chunk_2 = {'license_actions' : []}
            if parser.find_info_about_license_actions():
                chunk_2 = {
                    'license_actions' : parser.get_license_actions(),
                }
            
            data = chunk_1 | chunk_2
        except TimeoutException:
            raise e
        except Exception as e:
            logger.exception(f'Exception during parsing html: {e}', exc_info=True)
            raise e
        finally:
            return data
        
class LicenseHTMLParserCommands():
    def __init__(self, driver : webdriver.Chrome) -> None:
        self.driver = driver

    def wait_until_located(self, by, value, time=1):
        try:
            WebDriverWait(self.driver, time).until(EC.presence_of_element_located((by, value)))
        except TimeoutException:
            exc_msg = "The waiting time for the license information page to be detected has been exceeded."
            logger.exception(exc_msg, exc_info=True)
            raise TimeoutException(exc_msg)

    def find_info_about_license_actions(self) -> bool:
        try:
            self.driver.find_element(By.XPATH, "//*[text()='Информация об изменениях или дополнениях лицензии']").click()
            self.wait_until_located(By.XPATH, "//*[text()='Дата выполнения действия с лицензией']")
            logger.debug(f'Information found')
            return True
        except TimeoutException:
            logger.warning("Information about license_actions wasn't detected.")
            return False
        except Exception as e:
            logger.exception(f'Exception during a proccess looking for license_actions: {e}', exc_info=True)
            return False

    def get_agency_info(self) -> str:
        try:
            result = self.driver.find_element(By.XPATH, "//*[text()='Наименование органа, предоставившего лицензию:']")\
                                .find_element(By.TAG_NAME, 'strong').get_attribute('innerHTML')
        except Exception as e:
            logger.exception(f'Exception during the retreiving of agency_info: {e}', exc_info=True)
            result = ''
        finally:
            logger.debug(f'Given value: {result}')
            return result
    
    def get_activity_type(self) -> str:
        try:
            result = self.driver.find_element(By.XPATH, "//*[text()='Вид деятельности:']")\
                                .find_element(By.TAG_NAME, 'strong').get_attribute('innerHTML')
        except Exception as e:
            logger.exception(f'Exception during the retreiving of activity_type: {e}', exc_info=True)
            result = ''
        finally:
            logger.debug(f'Given value: {result}')
            return result
    
    def get_license_status(self) -> str:
        try:
            result = self.driver.find_element(By.XPATH, "//*[text()='Статус лицензии:']")\
                                .find_element(By.TAG_NAME, 'span').get_attribute('innerHTML')
        except Exception as e:
            logger.exception(f'Exception during the retreiving of license_status: {e}', exc_info=True)
            result = ''
        finally:
            logger.debug(f'Given value: {result}')
            return result
    
    def get_license_number(self) -> str:
        try:
            result = self.driver.find_element(By.XPATH, "//*[text()='Номер лицензии: ']")\
                                .find_element(By.TAG_NAME, 'strong').get_attribute('innerHTML')
        except Exception as e:
            logger.exception(f'Exception during the retreiving of license_number: {e}', exc_info=True)
            result = ''
        finally:
            logger.debug(f'Given value: {result}')
            return result
    
    def get_license_from(self) -> str:
        try:
            result = self.driver.find_element(By.XPATH, "//*[text()='Дата принятия решения о предоставлении лицензии:']")\
                                .find_element(By.TAG_NAME, 'strong').get_attribute('innerHTML')
        except Exception as e:
            logger.exception(f'Exception during the retreiving of license_from: {e}', exc_info=True)
            result = ''
        finally:
            logger.debug(f'Given value: {result}')
            return result
    
    def get_full_activity_info(self) -> list:
        try:
            result = [elem.get_attribute('innerHTML') for elem in self.driver.find_element(By.ID, "ql-editor")\
                          .find_elements(By.TAG_NAME, 'p')]
        except Exception as e:
            logger.warning("Information about full_activity_info wasn't detected.")
            result = []
        finally:
            logger.debug(f'Given value: {result}')
            return result
    
    def get_short_activity_info(self) -> list:
        return self.__query_table(0, 'short_activity_info')
    
    def get_license_actions(self) -> list:
        return self.__query_table(-1, 'license_actions')
        
    def __query_table(self, index : int, type : str):
        try:
            result = []
            table_rows = self.driver.find_elements(By.TAG_NAME, 'table')[index].find_elements(By.TAG_NAME, 'tr')[1:]
            p_tags_list = [elem.find_elements(By.TAG_NAME, 'p') for elem in table_rows]
            for p_tags in p_tags_list:
                result.append([])
                for tag in p_tags:
                    if 'span' in tag.get_attribute('innerHTML'):
                        result[-1].append(tag.find_element(By.TAG_NAME, 'span').get_attribute('innerHTML'))
                    else:
                        result[-1].append(tag.get_attribute('innerHTML'))
        except Exception as e: 
            logger.exception(f'Exception during the retreiving of {type}: {e}', exc_info=True)
            result = []
        finally:
            logger.debug(f'Given value: {result}')
            return result