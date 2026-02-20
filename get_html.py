from streamlit.testing.v1 import AppTest
from bs4 import BeautifulSoup

at = AppTest.from_file('app.py').run()
soup = BeautifulSoup(at.main[0].value if at.main else "", "html.parser")
print("OK")
