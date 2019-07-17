from database import CursorFromConnectionPool

class Lead:
    def __init__(self, search_title, linkedin_url, lead_name, lead_company, domain, id=None):
        self.id = id
        self.search_title = search_title
	    self.linkedin_url = linkedin_url
        self.lead_name = lead_name
        self.lead_company = lead_company
        self.domain = domain   
	
    def __repr__(self):
        return "<Lead(search_title='{}',linkedin_url='{}', lead_name='{}', lead_company={}, domain={})>"\
                .format(self.search_title,self.linkedin_url, self.lead_name, self.lead_company, self.domain)

    def save_to_db(self):
        with CursorFromConnectionPool() as cursor:
            cursor.execute('INSERT INTO leads(search_title, linkedin_url, lead_name, lead_company, domain) VALUES (%s, %s, %s, %s, %s)', (self.search_title, self.linkedin_url, self.lead_name, self.lead_company, self.domain))