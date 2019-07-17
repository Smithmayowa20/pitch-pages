from selenium import webdriver
import time
from selenium.webdriver.common.keys import Keys
from parsel import Selector
from urllib.parse import urlparse, parse_qsl, unquote_plus
import pickle
import os.path
import re
from PIL import Image
import json

class Pitch_Page:
    def __init__(self, email, password, title, html_page):
        self.email = email
        self.password = password
		self.title = title
        self.html_page = html_page
        self.leads_list = []
        self.filtered_leads_list = []
        self.pattern = re.compile('([^\s\w]|_)+')
		driverProfile = webdriver.ChromeOptions()
        driverProfile.add_experimental_option('prefs', {'intl.accept_languages': 'en,en_US'})
        self.driver = webdriver.Chrome(executable_path=r"C:\Users\Smith\chromedriver.exe", options=driverProfile)

		
    def login(self):
        self.driver.maximize_window()
        self.driver.get('https://www.linkedin.com')
        username = self.driver.find_element_by_class_name('login-email')
        username.send_keys(self.email)
        time.sleep(0.5)
        password = self.driver.find_element_by_class_name('login-password')
        password.send_keys(password)
        time.sleep(0.5)
        sign_in_button = self.driver.find_element_by_xpath('//*[@type="submit"]')
        sign_in_button.click()
        time.sleep(1)

	def get_leads_search_result(self):
        base_url = "https://www.linkedin.com"
        filter_string = "/sales/search/company?keywords="
        search_link = "https://www.linkedin.com/sales/search/people?companySize=B%2CC&doFetchHeroCard=false&geoIncluded=us%3A0&industryIncluded=6&keywords=b2b&logHistory=true&logId=3106532216&page={page}&searchSessionId=EtZzWLk5S0OjpEawLj12Lg%3D%3D&seniorityIncluded=10%2C9&titleIncluded={title}%3A35%2CCo-Founder%3A103&titleTimeScope=CURRENT"

        for i in range(1,41):
            self.driver.get(search_link.format(page=i,title=self.title))
            time.sleep(5)
            self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(5)
            sel = Selector(text=self.driver.page_source)
            leads_search_list = sel.xpath('//li[contains(@class, "pv5 ph2 search-results__result-item")]')
            leads_search_list.getall()
            for lead in leads_search_list:
                lead_list = []
                company_link = lead.xpath('.//a[contains(@class, "Sans-14px-black-75%-bold ember-view")]//@href').extract_first()
                company_link = company_link.strip()
                if filter_string in company_link:
                    continue
                lead_list.append(base_url + company_link)
                lead_name = lead.xpath('.//a[@class="ember-view"]/text()').extract_first()
                lead_name = lead_name.strip()
                lead_list.append(lead_name)
                company_name = lead.xpath('.//a[contains(@class, "Sans-14px-black-75%-bold ember-view")]/span/text()').extract_first()
                company_name = company_name.strip()
                lead_list.append(company_name)
                self.leads_list.append(lead_list)
		
	def get_leads_company_info(self):
        for lead in self.leads_list:
            try: 
                self.driver.get(lead[0])
                time.sleep(1)
                sel = Selector(text=self.driver.page_source)
                domain = sel.xpath('//a[contains(@class, "website ember-view")]//@href').extract_first()
                domain = domain.strip()
                lead.append(domain)
                self.driver.get(domain)
                time.sleep(1)
                self.driver.save_screenshot("{}.png".format(lead[2]))
            except:
                pass
        
    def quit_driver(self):
        self.driver.quit()
        
    def filter_leads_list(self):
        for lead in leads_list:
            if (lead[2].strip() and (os.path.exists('{}.png'.format(lead[2])))):
                lead[1] = lead[1].replace('- we are hiring','')
                lead[1] = lead[1].replace('CRM      LEED Green Associate','')
                lead[1] = lead[1].replace('- Founder and CTO','')
                lead[1] = lead[1].replace(', MBA, Ph.D, AI and Data Science Certified','')
                lead[1] = lead[1].replace(', OMCP','')
                lead[1] = lead[1].replace(', CTS','')
                lead[1] = lead[1].replace(', Ph.D.','')
                lead[1] = lead[1].replace(', CSM','')
                lead[1] = lead[1].replace(', VCP, CDCP', '')
                lead[1] = lead[1].replace(', M.S., MBA', '')
                lead[1] = lead[1].replace(', MBA', '')
                lead[1] = pattern.sub('', lead[1])
                lead[1] = lead[1].title()
                lead[2] = lead[2].replace(', LLC','')
                lead[2] = pattern.sub('', lead[2])
                lead[2] = lead[2].title()

            self.filtered_leads_list.append(lead)

	
    def create_pitch_pages(self):
        for lead in self.filtered_leads_list:
            name = lead[1].split()[0]
            company = lead[2]
            html_page = html_page.replace('{{Name}}',name)
            html_page = html_page.replace('{{Company}}',company)
            try:
                with open('{}.html'.format(company),'w') as file:
                    file.write(html_page)
            except:
                pass
    
    def save_to_database(self, database, user, password, host):	
	    from models import Lead
        from database import Database
        Database.initialise(database=database, user=user, password=password, host=host)
        for index in self.filter_leads_list:
            lead = Lead(self.title, index[0], index[1], index[2], index[3])
            lead.save_to_db()

    
    def execute_pitch_page_creation(self, database, user, password, host):
        self.login()
        self.get_leads_search_result()
        self.get_leads_company_info()
        self.filter_leads_list()
		self.save_to_database(database, user, password, host)
		self.create_pitch_pages()
        self.quit_driver()


hardcoded_html_page = ''''''#Insert html page string here		
@click.command()
@click.option('--linkedin_email', help='Email for your linkedin sales navigator account')
@click.option('--linkedin_password', help='Password for your linkedin sales navigator account')
@click.option('--title', default='Founder', help='Title of leads being searched for')
@click.option('--db_name', help='Postgresql database name')
@click.option('--db_user', help='postgresql database username')
@click.option('--db_password', help='postgresql database password')
@click.option('--host', default=5432, help='postgresql database host')
def create_execute_pitch_page(linkedin_email,linkedin_password,title,db_name,db_user,db_password,host):
    pitch_page = Pitch_Page(linkedin_email,linkedin_password,title,hardcoded_html_page)
    pitch_page.execute_pitch_page_creation(db_name,db_user,db_password,host)
    

if __name__ == '__main__':
    create_execute_pitch_page()
    