from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import pandas as pd
import time

# 1. Setup the automated browser (Run visible so you can watch the browser work)
options = webdriver.ChromeOptions()
# options.add_argument('--headless') # Removed to show live execution
options.add_argument('--disable-gpu')
options.add_argument('user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')
options.add_experimental_option("excludeSwitches", ["enable-automation"])
options.add_experimental_option('useAutomationExtension', False)
options.add_argument("--disable-blink-features=AutomationControlled")

# Start the browser
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
# Override webdriver property on every page load
driver.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {
    "source": "Object.defineProperty(navigator, 'webdriver', {get: () => undefined})"
})

# 2. Add the route URLs you want to scrape
route_urls = [
    # FROM CHENNAI
    "https://www.redbus.in/bus-tickets/chennai-to-coimbatore",
    "https://www.redbus.in/bus-tickets/chennai-to-madurai",
    "https://www.redbus.in/bus-tickets/chennai-to-tiruchirapalli",
    "https://www.redbus.in/bus-tickets/chennai-to-salem",
    "https://www.redbus.in/bus-tickets/chennai-to-tirunelveli",
    "https://www.redbus.in/bus-tickets/chennai-to-nagercoil",
    "https://www.redbus.in/bus-tickets/chennai-to-erode",
    "https://www.redbus.in/bus-tickets/chennai-to-tirupur",
    "https://www.redbus.in/bus-tickets/chennai-to-vellore",
    "https://www.redbus.in/bus-tickets/chennai-to-hosur",
    "https://www.redbus.in/bus-tickets/chennai-to-thanjavur",
    "https://www.redbus.in/bus-tickets/chennai-to-tuticorin",
    "https://www.redbus.in/bus-tickets/chennai-to-kumbakonam",
    "https://www.redbus.in/bus-tickets/chennai-to-karur",
    "https://www.redbus.in/bus-tickets/chennai-to-dindigul",
    "https://www.redbus.in/bus-tickets/chennai-to-ooty",
    "https://www.redbus.in/bus-tickets/chennai-to-kanyakumari",
    "https://www.redbus.in/bus-tickets/chennai-to-rameswaram",
    "https://www.redbus.in/bus-tickets/chennai-to-cuddalore",
    "https://www.redbus.in/bus-tickets/chennai-to-pudukottai",
    "https://www.redbus.in/bus-tickets/chennai-to-karaikudi",
    "https://www.redbus.in/bus-tickets/chennai-to-sivakasi",
    "https://www.redbus.in/bus-tickets/chennai-to-virudhnagar",
    "https://www.redbus.in/bus-tickets/chennai-to-theni",
    "https://www.redbus.in/bus-tickets/chennai-to-pollachi",
    "https://www.redbus.in/bus-tickets/chennai-to-dharmapuri",
    "https://www.redbus.in/bus-tickets/chennai-to-krishnagiri",
    "https://www.redbus.in/bus-tickets/chennai-to-namakkal",
    "https://www.redbus.in/bus-tickets/chennai-to-chidambaram",
    "https://www.redbus.in/bus-tickets/chennai-to-nagapattinam",
    "https://www.redbus.in/bus-tickets/chennai-to-velankanni",
    "https://www.redbus.in/bus-tickets/chennai-to-mayiladuthurai",
    "https://www.redbus.in/bus-tickets/chennai-to-thiruvarur",
    "https://www.redbus.in/bus-tickets/chennai-to-perambalur",
    "https://www.redbus.in/bus-tickets/chennai-to-villupuram",
    "https://www.redbus.in/bus-tickets/chennai-to-tiruvannamalai",
    "https://www.redbus.in/bus-tickets/chennai-to-kanchipuram",
    "https://www.redbus.in/bus-tickets/chennai-to-marthandam",
    "https://www.redbus.in/bus-tickets/chennai-to-kovilpatti",
    "https://www.redbus.in/bus-tickets/chennai-to-ramanathapuram",
    "https://www.redbus.in/bus-tickets/chennai-to-mannargudi",
    "https://www.redbus.in/bus-tickets/chennai-to-sirkazhi",
    "https://www.redbus.in/bus-tickets/chennai-to-tenkasi",
    "https://www.redbus.in/bus-tickets/chennai-to-rajapalayam",
    "https://www.redbus.in/bus-tickets/chennai-to-bodi",
    "https://www.redbus.in/bus-tickets/chennai-to-periyakulam",

    # FROM COIMBATORE
    "https://www.redbus.in/bus-tickets/coimbatore-to-chennai",
    "https://www.redbus.in/bus-tickets/coimbatore-to-madurai",
    "https://www.redbus.in/bus-tickets/coimbatore-to-tiruchirapalli",
    "https://www.redbus.in/bus-tickets/coimbatore-to-salem",
    "https://www.redbus.in/bus-tickets/coimbatore-to-tirunelveli",
    "https://www.redbus.in/bus-tickets/coimbatore-to-nagercoil",
    "https://www.redbus.in/bus-tickets/coimbatore-to-erode",
    "https://www.redbus.in/bus-tickets/coimbatore-to-hosur",
    "https://www.redbus.in/bus-tickets/coimbatore-to-thanjavur",
    "https://www.redbus.in/bus-tickets/coimbatore-to-tuticorin",
    "https://www.redbus.in/bus-tickets/coimbatore-to-kumbakonam",
    "https://www.redbus.in/bus-tickets/coimbatore-to-karur",
    "https://www.redbus.in/bus-tickets/coimbatore-to-dindigul",
    "https://www.redbus.in/bus-tickets/coimbatore-to-rameswaram",
    "https://www.redbus.in/bus-tickets/coimbatore-to-pudukottai",
    "https://www.redbus.in/bus-tickets/coimbatore-to-karaikudi",
    "https://www.redbus.in/bus-tickets/coimbatore-to-sivakasi",
    "https://www.redbus.in/bus-tickets/coimbatore-to-virudhnagar",
    "https://www.redbus.in/bus-tickets/coimbatore-to-theni",
    "https://www.redbus.in/bus-tickets/coimbatore-to-namakkal",
    "https://www.redbus.in/bus-tickets/coimbatore-to-chidambaram",
    "https://www.redbus.in/bus-tickets/coimbatore-to-nagapattinam",
    "https://www.redbus.in/bus-tickets/coimbatore-to-velankanni",
    "https://www.redbus.in/bus-tickets/coimbatore-to-mayiladuthurai",
    "https://www.redbus.in/bus-tickets/coimbatore-to-thiruvarur",
    "https://www.redbus.in/bus-tickets/coimbatore-to-kovilpatti",
    "https://www.redbus.in/bus-tickets/coimbatore-to-ramanathapuram",
    "https://www.redbus.in/bus-tickets/coimbatore-to-mannargudi",
    "https://www.redbus.in/bus-tickets/coimbatore-to-tenkasi",
    "https://www.redbus.in/bus-tickets/coimbatore-to-rajapalayam",
    "https://www.redbus.in/bus-tickets/coimbatore-to-dharmapuri",
    "https://www.redbus.in/bus-tickets/coimbatore-to-krishnagiri",
    "https://www.redbus.in/bus-tickets/coimbatore-to-vellore",
    "https://www.redbus.in/bus-tickets/coimbatore-to-tiruvannamalai",
    "https://www.redbus.in/bus-tickets/coimbatore-to-villupuram",

    # FROM MADURAI
    "https://www.redbus.in/bus-tickets/madurai-to-chennai",
    "https://www.redbus.in/bus-tickets/madurai-to-coimbatore",
    "https://www.redbus.in/bus-tickets/madurai-to-tiruchirapalli",
    "https://www.redbus.in/bus-tickets/madurai-to-salem",
    "https://www.redbus.in/bus-tickets/madurai-to-tirunelveli",
    "https://www.redbus.in/bus-tickets/madurai-to-nagercoil",
    "https://www.redbus.in/bus-tickets/madurai-to-erode",
    "https://www.redbus.in/bus-tickets/madurai-to-tirupur",
    "https://www.redbus.in/bus-tickets/madurai-to-hosur",
    "https://www.redbus.in/bus-tickets/madurai-to-thanjavur",
    "https://www.redbus.in/bus-tickets/madurai-to-tuticorin",
    "https://www.redbus.in/bus-tickets/madurai-to-kumbakonam",
    "https://www.redbus.in/bus-tickets/madurai-to-karur",
    "https://www.redbus.in/bus-tickets/madurai-to-vellore",
    "https://www.redbus.in/bus-tickets/madurai-to-tiruvannamalai",
    "https://www.redbus.in/bus-tickets/madurai-to-villupuram",
    "https://www.redbus.in/bus-tickets/madurai-to-karaikudi",
    "https://www.redbus.in/bus-tickets/madurai-to-nagapattinam",
    "https://www.redbus.in/bus-tickets/madurai-to-velankanni",
    "https://www.redbus.in/bus-tickets/madurai-to-mayiladuthurai",
    "https://www.redbus.in/bus-tickets/madurai-to-chidambaram",
    "https://www.redbus.in/bus-tickets/madurai-to-dharmapuri",
    "https://www.redbus.in/bus-tickets/madurai-to-krishnagiri",
    "https://www.redbus.in/bus-tickets/madurai-to-namakkal",

    # FROM TIRUCHIRAPALLI
    "https://www.redbus.in/bus-tickets/tiruchirapalli-to-chennai",
    "https://www.redbus.in/bus-tickets/tiruchirapalli-to-coimbatore",
    "https://www.redbus.in/bus-tickets/tiruchirapalli-to-madurai",
    "https://www.redbus.in/bus-tickets/tiruchirapalli-to-salem",
    "https://www.redbus.in/bus-tickets/tiruchirapalli-to-tirunelveli",
    "https://www.redbus.in/bus-tickets/tiruchirapalli-to-nagercoil",
    "https://www.redbus.in/bus-tickets/tiruchirapalli-to-erode",
    "https://www.redbus.in/bus-tickets/tiruchirapalli-to-tirupur",
    "https://www.redbus.in/bus-tickets/tiruchirapalli-to-hosur",
    "https://www.redbus.in/bus-tickets/tiruchirapalli-to-thanjavur",
    "https://www.redbus.in/bus-tickets/tiruchirapalli-to-tuticorin",
    "https://www.redbus.in/bus-tickets/tiruchirapalli-to-kumbakonam",
    "https://www.redbus.in/bus-tickets/tiruchirapalli-to-karur",
    "https://www.redbus.in/bus-tickets/tiruchirapalli-to-dindigul",
    "https://www.redbus.in/bus-tickets/tiruchirapalli-to-vellore",
    "https://www.redbus.in/bus-tickets/tiruchirapalli-to-tiruvannamalai",
    "https://www.redbus.in/bus-tickets/tiruchirapalli-to-villupuram",
    "https://www.redbus.in/bus-tickets/tiruchirapalli-to-karaikudi",
    "https://www.redbus.in/bus-tickets/tiruchirapalli-to-ramanathapuram",
    "https://www.redbus.in/bus-tickets/tiruchirapalli-to-nagapattinam",
    "https://www.redbus.in/bus-tickets/tiruchirapalli-to-velankanni",

    # FROM SALEM
    "https://www.redbus.in/bus-tickets/salem-to-chennai",
    "https://www.redbus.in/bus-tickets/salem-to-coimbatore",
    "https://www.redbus.in/bus-tickets/salem-to-madurai",
    "https://www.redbus.in/bus-tickets/salem-to-tiruchirapalli",
    "https://www.redbus.in/bus-tickets/salem-to-tirunelveli",
    "https://www.redbus.in/bus-tickets/salem-to-nagercoil",
    "https://www.redbus.in/bus-tickets/salem-to-erode",
    "https://www.redbus.in/bus-tickets/salem-to-tirupur",
    "https://www.redbus.in/bus-tickets/salem-to-hosur",
    "https://www.redbus.in/bus-tickets/salem-to-thanjavur",
    "https://www.redbus.in/bus-tickets/salem-to-tuticorin",
    "https://www.redbus.in/bus-tickets/salem-to-kumbakonam",
    "https://www.redbus.in/bus-tickets/salem-to-karur",
    "https://www.redbus.in/bus-tickets/salem-to-dindigul",
    "https://www.redbus.in/bus-tickets/salem-to-vellore",
    "https://www.redbus.in/bus-tickets/salem-to-tiruvannamalai",
    "https://www.redbus.in/bus-tickets/salem-to-villupuram",
    "https://www.redbus.in/bus-tickets/salem-to-dharmapuri",
    "https://www.redbus.in/bus-tickets/salem-to-krishnagiri",
    "https://www.redbus.in/bus-tickets/salem-to-namakkal",

    # FROM TIRUNELVELI
    "https://www.redbus.in/bus-tickets/tirunelveli-to-chennai",
    "https://www.redbus.in/bus-tickets/tirunelveli-to-coimbatore",
    "https://www.redbus.in/bus-tickets/tirunelveli-to-madurai",
    "https://www.redbus.in/bus-tickets/tirunelveli-to-tiruchirapalli",
    "https://www.redbus.in/bus-tickets/tirunelveli-to-salem",
    "https://www.redbus.in/bus-tickets/tirunelveli-to-erode",
    "https://www.redbus.in/bus-tickets/tirunelveli-to-tirupur",
    "https://www.redbus.in/bus-tickets/tirunelveli-to-hosur",
    "https://www.redbus.in/bus-tickets/tirunelveli-to-thanjavur",
    "https://www.redbus.in/bus-tickets/tirunelveli-to-kumbakonam",
    "https://www.redbus.in/bus-tickets/tirunelveli-to-karur",
    "https://www.redbus.in/bus-tickets/tirunelveli-to-dindigul",
    "https://www.redbus.in/bus-tickets/tirunelveli-to-vellore",
    "https://www.redbus.in/bus-tickets/tirunelveli-to-tiruvannamalai",
    "https://www.redbus.in/bus-tickets/tirunelveli-to-villupuram",

    # FROM NAGERCOIL
    "https://www.redbus.in/bus-tickets/nagercoil-to-chennai",
    "https://www.redbus.in/bus-tickets/nagercoil-to-coimbatore",
    "https://www.redbus.in/bus-tickets/nagercoil-to-madurai",
    "https://www.redbus.in/bus-tickets/nagercoil-to-tiruchirapalli",
    "https://www.redbus.in/bus-tickets/nagercoil-to-salem",
    "https://www.redbus.in/bus-tickets/nagercoil-to-erode",
    "https://www.redbus.in/bus-tickets/nagercoil-to-tirupur",
    "https://www.redbus.in/bus-tickets/nagercoil-to-hosur",
    "https://www.redbus.in/bus-tickets/nagercoil-to-thanjavur",
    "https://www.redbus.in/bus-tickets/nagercoil-to-kumbakonam",
    "https://www.redbus.in/bus-tickets/nagercoil-to-karur",
    "https://www.redbus.in/bus-tickets/nagercoil-to-dindigul",
    "https://www.redbus.in/bus-tickets/nagercoil-to-vellore",
    "https://www.redbus.in/bus-tickets/nagercoil-to-villupuram",

    # FROM ERODE
    "https://www.redbus.in/bus-tickets/erode-to-chennai",
    "https://www.redbus.in/bus-tickets/erode-to-coimbatore",
    "https://www.redbus.in/bus-tickets/erode-to-madurai",
    "https://www.redbus.in/bus-tickets/erode-to-tiruchirapalli",
    "https://www.redbus.in/bus-tickets/erode-to-salem",
    "https://www.redbus.in/bus-tickets/erode-to-tirunelveli",
    "https://www.redbus.in/bus-tickets/erode-to-nagercoil",
    "https://www.redbus.in/bus-tickets/erode-to-hosur",
    "https://www.redbus.in/bus-tickets/erode-to-thanjavur",
    "https://www.redbus.in/bus-tickets/erode-to-tuticorin",
    "https://www.redbus.in/bus-tickets/erode-to-kumbakonam",
    "https://www.redbus.in/bus-tickets/erode-to-vellore",
    "https://www.redbus.in/bus-tickets/erode-to-tiruvannamalai",
    "https://www.redbus.in/bus-tickets/erode-to-villupuram",

    # FROM TIRUPUR
    "https://www.redbus.in/bus-tickets/tirupur-to-chennai",
    "https://www.redbus.in/bus-tickets/tirupur-to-madurai",
    "https://www.redbus.in/bus-tickets/tirupur-to-tiruchirapalli",
    "https://www.redbus.in/bus-tickets/tirupur-to-salem",
    "https://www.redbus.in/bus-tickets/tirupur-to-tirunelveli",
    "https://www.redbus.in/bus-tickets/tirupur-to-nagercoil",
    "https://www.redbus.in/bus-tickets/tirupur-to-hosur",
    "https://www.redbus.in/bus-tickets/tirupur-to-thanjavur",
    "https://www.redbus.in/bus-tickets/tirupur-to-tuticorin",
    "https://www.redbus.in/bus-tickets/tirupur-to-kumbakonam",
    "https://www.redbus.in/bus-tickets/tirupur-to-vellore",
    "https://www.redbus.in/bus-tickets/tirupur-to-villupuram",

    # FROM HOSUR
    "https://www.redbus.in/bus-tickets/hosur-to-chennai",
    "https://www.redbus.in/bus-tickets/hosur-to-coimbatore",
    "https://www.redbus.in/bus-tickets/hosur-to-madurai",
    "https://www.redbus.in/bus-tickets/hosur-to-tiruchirapalli",
    "https://www.redbus.in/bus-tickets/hosur-to-salem",
    "https://www.redbus.in/bus-tickets/hosur-to-tirunelveli",
    "https://www.redbus.in/bus-tickets/hosur-to-nagercoil",
    "https://www.redbus.in/bus-tickets/hosur-to-erode",
    "https://www.redbus.in/bus-tickets/hosur-to-tirupur",
    "https://www.redbus.in/bus-tickets/hosur-to-thanjavur",
    "https://www.redbus.in/bus-tickets/hosur-to-tuticorin",
    "https://www.redbus.in/bus-tickets/hosur-to-kumbakonam",
    "https://www.redbus.in/bus-tickets/hosur-to-karur",
    "https://www.redbus.in/bus-tickets/hosur-to-dindigul",
    "https://www.redbus.in/bus-tickets/hosur-to-pudukottai",
    "https://www.redbus.in/bus-tickets/hosur-to-karaikudi",
    "https://www.redbus.in/bus-tickets/hosur-to-sivakasi",
    "https://www.redbus.in/bus-tickets/hosur-to-virudhnagar",
    "https://www.redbus.in/bus-tickets/hosur-to-theni",

    # FROM THANJAVUR
    "https://www.redbus.in/bus-tickets/thanjavur-to-chennai",
    "https://www.redbus.in/bus-tickets/thanjavur-to-coimbatore",
    "https://www.redbus.in/bus-tickets/thanjavur-to-madurai",
    "https://www.redbus.in/bus-tickets/thanjavur-to-salem",
    "https://www.redbus.in/bus-tickets/thanjavur-to-tirunelveli",
    "https://www.redbus.in/bus-tickets/thanjavur-to-nagercoil",
    "https://www.redbus.in/bus-tickets/thanjavur-to-erode",
    "https://www.redbus.in/bus-tickets/thanjavur-to-tirupur",
    "https://www.redbus.in/bus-tickets/thanjavur-to-hosur",

    # FROM TUTICORIN
    "https://www.redbus.in/bus-tickets/tuticorin-to-chennai",
    "https://www.redbus.in/bus-tickets/tuticorin-to-coimbatore",
    "https://www.redbus.in/bus-tickets/tuticorin-to-madurai",
    "https://www.redbus.in/bus-tickets/tuticorin-to-tiruchirapalli",
    "https://www.redbus.in/bus-tickets/tuticorin-to-salem",
    "https://www.redbus.in/bus-tickets/tuticorin-to-erode",
    "https://www.redbus.in/bus-tickets/tuticorin-to-tirupur",
    "https://www.redbus.in/bus-tickets/tuticorin-to-hosur",

    # FROM KUMBAKONAM
    "https://www.redbus.in/bus-tickets/kumbakonam-to-chennai",
    "https://www.redbus.in/bus-tickets/kumbakonam-to-coimbatore",
    "https://www.redbus.in/bus-tickets/kumbakonam-to-madurai",
    "https://www.redbus.in/bus-tickets/kumbakonam-to-salem",
    "https://www.redbus.in/bus-tickets/kumbakonam-to-tirunelveli",
    "https://www.redbus.in/bus-tickets/kumbakonam-to-nagercoil",
    "https://www.redbus.in/bus-tickets/kumbakonam-to-erode",
    "https://www.redbus.in/bus-tickets/kumbakonam-to-tirupur",
    "https://www.redbus.in/bus-tickets/kumbakonam-to-hosur",

    # FROM KARUR
    "https://www.redbus.in/bus-tickets/karur-to-chennai",
    "https://www.redbus.in/bus-tickets/karur-to-coimbatore",
    "https://www.redbus.in/bus-tickets/karur-to-madurai",
    "https://www.redbus.in/bus-tickets/karur-to-salem",
    "https://www.redbus.in/bus-tickets/karur-to-tirunelveli",
    "https://www.redbus.in/bus-tickets/karur-to-nagercoil",
    "https://www.redbus.in/bus-tickets/karur-to-hosur",

    # FROM DINDIGUL
    "https://www.redbus.in/bus-tickets/dindigul-to-chennai",
    "https://www.redbus.in/bus-tickets/dindigul-to-coimbatore",
    "https://www.redbus.in/bus-tickets/dindigul-to-salem",
    "https://www.redbus.in/bus-tickets/dindigul-to-tirunelveli",
    "https://www.redbus.in/bus-tickets/dindigul-to-nagercoil",
    "https://www.redbus.in/bus-tickets/dindigul-to-hosur",

    # FROM VELLORE
    "https://www.redbus.in/bus-tickets/vellore-to-coimbatore",
    "https://www.redbus.in/bus-tickets/vellore-to-madurai",
    "https://www.redbus.in/bus-tickets/vellore-to-tiruchirapalli",
    "https://www.redbus.in/bus-tickets/vellore-to-salem",
    "https://www.redbus.in/bus-tickets/vellore-to-tirunelveli",
    "https://www.redbus.in/bus-tickets/vellore-to-nagercoil",
    "https://www.redbus.in/bus-tickets/vellore-to-erode",
    "https://www.redbus.in/bus-tickets/vellore-to-tirupur",

    # FROM TIRUVANNAMALAI
    "https://www.redbus.in/bus-tickets/tiruvannamalai-to-chennai",
    "https://www.redbus.in/bus-tickets/tiruvannamalai-to-coimbatore",
    "https://www.redbus.in/bus-tickets/tiruvannamalai-to-madurai",
    "https://www.redbus.in/bus-tickets/tiruvannamalai-to-tiruchirapalli",
    "https://www.redbus.in/bus-tickets/tiruvannamalai-to-salem",
    "https://www.redbus.in/bus-tickets/tiruvannamalai-to-tirunelveli",
    "https://www.redbus.in/bus-tickets/tiruvannamalai-to-erode",

    # FROM VILLUPURAM
    "https://www.redbus.in/bus-tickets/villupuram-to-coimbatore",
    "https://www.redbus.in/bus-tickets/villupuram-to-madurai",
    "https://www.redbus.in/bus-tickets/villupuram-to-tiruchirapalli",
    "https://www.redbus.in/bus-tickets/villupuram-to-salem",
    "https://www.redbus.in/bus-tickets/villupuram-to-tirunelveli",
    "https://www.redbus.in/bus-tickets/villupuram-to-nagercoil",

    # FROM PUDUKOTTAI
    "https://www.redbus.in/bus-tickets/pudukottai-to-chennai",
    "https://www.redbus.in/bus-tickets/pudukottai-to-coimbatore",
    "https://www.redbus.in/bus-tickets/pudukottai-to-salem",
    "https://www.redbus.in/bus-tickets/pudukottai-to-hosur",

    # FROM KARAIKUDI
    "https://www.redbus.in/bus-tickets/karaikudi-to-chennai",
    "https://www.redbus.in/bus-tickets/karaikudi-to-coimbatore",
    "https://www.redbus.in/bus-tickets/karaikudi-to-salem",
    "https://www.redbus.in/bus-tickets/karaikudi-to-hosur",

    # FROM SIVAKASI
    "https://www.redbus.in/bus-tickets/sivakasi-to-chennai",
    "https://www.redbus.in/bus-tickets/sivakasi-to-coimbatore",
    "https://www.redbus.in/bus-tickets/sivakasi-to-salem",
    "https://www.redbus.in/bus-tickets/sivakasi-to-hosur",

    # FROM VIRUDHNAGAR
    "https://www.redbus.in/bus-tickets/virudhnagar-to-chennai",
    "https://www.redbus.in/bus-tickets/virudhnagar-to-coimbatore",
    "https://www.redbus.in/bus-tickets/virudhnagar-to-salem",
    "https://www.redbus.in/bus-tickets/virudhnagar-to-hosur",

    # FROM THENI
    "https://www.redbus.in/bus-tickets/theni-to-chennai",
    "https://www.redbus.in/bus-tickets/theni-to-coimbatore",
    "https://www.redbus.in/bus-tickets/theni-to-salem",
    "https://www.redbus.in/bus-tickets/theni-to-hosur",

    # FROM POLLACHI
    "https://www.redbus.in/bus-tickets/pollachi-to-chennai",
    "https://www.redbus.in/bus-tickets/pollachi-to-madurai",
    "https://www.redbus.in/bus-tickets/pollachi-to-tiruchirapalli",
    "https://www.redbus.in/bus-tickets/pollachi-to-hosur",

    # FROM DHARMAPURI
    "https://www.redbus.in/bus-tickets/dharmapuri-to-chennai",
    "https://www.redbus.in/bus-tickets/dharmapuri-to-coimbatore",
    "https://www.redbus.in/bus-tickets/dharmapuri-to-madurai",
    "https://www.redbus.in/bus-tickets/dharmapuri-to-tirunelveli",

    # FROM KRISHNAGIRI
    "https://www.redbus.in/bus-tickets/krishnagiri-to-chennai",
    "https://www.redbus.in/bus-tickets/krishnagiri-to-coimbatore",
    "https://www.redbus.in/bus-tickets/krishnagiri-to-madurai",
    "https://www.redbus.in/bus-tickets/krishnagiri-to-tirunelveli",

    # FROM NAMAKKAL
    "https://www.redbus.in/bus-tickets/namakkal-to-chennai",
    "https://www.redbus.in/bus-tickets/namakkal-to-coimbatore",
    "https://www.redbus.in/bus-tickets/namakkal-to-madurai",

    # FROM CHIDAMBARAM
    "https://www.redbus.in/bus-tickets/chidambaram-to-chennai",
    "https://www.redbus.in/bus-tickets/chidambaram-to-coimbatore",
    "https://www.redbus.in/bus-tickets/chidambaram-to-madurai",

    # FROM NAGAPATTINAM
    "https://www.redbus.in/bus-tickets/nagapattinam-to-chennai",
    "https://www.redbus.in/bus-tickets/nagapattinam-to-coimbatore",
    "https://www.redbus.in/bus-tickets/nagapattinam-to-madurai",

    # FROM VELANKANNI
    "https://www.redbus.in/bus-tickets/velankanni-to-chennai",
    "https://www.redbus.in/bus-tickets/velankanni-to-coimbatore",
    "https://www.redbus.in/bus-tickets/velankanni-to-madurai",

    # FROM MAYILADUTHURAI
    "https://www.redbus.in/bus-tickets/mayiladuthurai-to-chennai",
    "https://www.redbus.in/bus-tickets/mayiladuthurai-to-coimbatore",
    "https://www.redbus.in/bus-tickets/mayiladuthurai-to-madurai",

    # FROM THIRUVARUR
    "https://www.redbus.in/bus-tickets/thiruvarur-to-chennai",
    "https://www.redbus.in/bus-tickets/thiruvarur-to-coimbatore",

    # FROM KOVILPATTI
    "https://www.redbus.in/bus-tickets/kovilpatti-to-chennai",
    "https://www.redbus.in/bus-tickets/kovilpatti-to-coimbatore",

    # FROM RAMANATHAPURAM
    "https://www.redbus.in/bus-tickets/ramanathapuram-to-chennai",
    "https://www.redbus.in/bus-tickets/ramanathapuram-to-coimbatore",

    # FROM MANNARGUDI
    "https://www.redbus.in/bus-tickets/mannargudi-to-chennai",
    "https://www.redbus.in/bus-tickets/mannargudi-to-coimbatore",

    # FROM TENKASI
    "https://www.redbus.in/bus-tickets/tenkasi-to-chennai",
    "https://www.redbus.in/bus-tickets/tenkasi-to-coimbatore",

    # FROM RAJAPALAYAM
    "https://www.redbus.in/bus-tickets/rajapalayam-to-chennai",
    "https://www.redbus.in/bus-tickets/rajapalayam-to-coimbatore"
]



target_dates = [
    ("17-Jun-2026", "Weekday"),
    ("19-Jun-2026", "Weekend"),
    ("20-Jun-2026", "Weekend"),
    ("21-Jun-2026", "Weekend")
]

import os

# Resume from existing CSV if present
scraped_keys = set()
master_data = []
if os.path.exists("tn_bus_data.csv"):
    try:
        df_existing = pd.read_csv("tn_bus_data.csv")
        if 'Departure Time' in df_existing.columns and 'Date' in df_existing.columns:
            for _, row in df_existing.iterrows():
                if pd.notna(row['Origin']) and pd.notna(row['Destination']) and pd.notna(row['Date']):
                    route_key = f"{str(row['Origin']).strip().lower()}-to-{str(row['Destination']).strip().lower()}"
                    scraped_keys.add(f"{route_key}@{str(row['Date']).strip()}")
            master_data = df_existing.to_dict('records')
            print(f"Loaded {len(master_data)} existing records. Skipping {len(scraped_keys)} already scraped combinations.", flush=True)
        else:
            print("Existing CSV is in the old format (missing Departure/Arrival columns). Archiving to start fresh.", flush=True)
            try:
                os.rename("tn_bus_data.csv", "tn_bus_data_old.csv")
            except Exception as rename_err:
                print(f"Could not rename: {rename_err}", flush=True)
    except Exception as e:
        print(f"Error reading existing CSV: {e}. Starting fresh.", flush=True)

route_city_params = {}

# 3. Loop through the Dates and URLs
for date_str, date_type in target_dates:
    for url in route_urls:
        route_key = url.split('/')[-1].strip().lower()
        combo_key = f"{route_key}@{date_str}"
        if combo_key in scraped_keys:
            continue

        # Step 1: Resolve city IDs for the route if not already cached
        if route_key not in route_city_params:
            print(f"Resolving city search parameters for: {url}...", flush=True)
            try:
                driver.get(url)
                # Wait for page to redirect and load valid city parameters in URL (not 'undefined')
                WebDriverWait(driver, 15).until(
                    lambda d: "fromCityId" in d.current_url and 
                              "fromCityId=undefined" not in d.current_url and 
                              "toCityId=undefined" not in d.current_url
                )
                from urllib.parse import urlparse, parse_qs
                parsed = urlparse(driver.current_url)
                queries = parse_qs(parsed.query)
                from_id = queries.get('fromCityId', [''])[0]
                from_name = queries.get('fromCityName', [''])[0]
                to_id = queries.get('toCityId', [''])[0]
                to_name = queries.get('toCityName', [''])[0]
                if from_id and to_id and from_id != 'undefined' and to_id != 'undefined':
                    route_city_params[route_key] = f"fromCityId={from_id}&fromCityName={from_name}&toCityId={to_id}&toCityName={to_name}"
            except Exception as e:
                print(f"Could not resolve city parameters for {url}: {e}. Falling back to simple query string.", flush=True)
        
        # Step 2: Construct the target URL with query params + target date
        city_query = route_city_params.get(route_key)
        if city_query:
            url_with_date = f"{url}?{city_query}&onward={date_str}"
        else:
            url_with_date = f"{url}?onward={date_str}"

        print(f"Scraping: {url_with_date} ({date_type})...", flush=True)
        
        # Try to load the page, restarting Chrome if the session crashed
        try:
            driver.get(url_with_date)
        except Exception as e:
            print(f"Chrome connection lost ({e}). Attempting to restart browser...", flush=True)
            try:
                driver.quit()
            except:
                pass
            try:
                driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
                driver.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {
                    "source": "Object.defineProperty(navigator, 'webdriver', {get: () => undefined})"
                })
                driver.get(url_with_date)
            except Exception as startup_err:
                print(f"Failed to restart browser: {startup_err}. Retrying in 10 seconds...", flush=True)
                time.sleep(10)
                continue
        
        try:
            # Wait up to 15 seconds for the bus results list to load on the page
            WebDriverWait(driver, 15).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "li[class*='tupleWrapper']"))
            )
            
            # Give the page a moment to render dynamic JS elements
            time.sleep(3) 
            
            # Scroll down to load all buses lazily
            last_height = driver.execute_script("return document.body.scrollHeight")
            for _ in range(15): # Max 15 scrolls to prevent infinite loops
                driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                time.sleep(2)
                new_height = driver.execute_script("return document.body.scrollHeight")
                if new_height == last_height:
                    break
                last_height = new_height
                
            # Grab all the bus cards on the page
            bus_cards = driver.find_elements(By.CSS_SELECTOR, "li[class*='tupleWrapper']")
            
            import re
            import math
            import random
            
            scraped_any = False
            page_night_buses = []
            page_day_buses = []
            
            for card in bus_cards:
                try:
                    # Extract the aria-label attribute which contains the combined details
                    aria_label = card.get_attribute("aria-label")
                    if not aria_label:
                        continue
                    
                    # Split the first comma to get the operator
                    parts_comma = aria_label.split(',', 1)
                    operator = parts_comma[0].strip() if len(parts_comma) > 0 else "Unknown"
                    
                    # Split the first period from the rest to get the bus type
                    rest = parts_comma[1] if len(parts_comma) > 1 else ""
                    parts_period = rest.split('.', 1)
                    bus_type = parts_period[0].strip() if len(parts_period) > 0 else "Unknown"
                    
                    # Extract Departure Time (e.g. "Departs 21:35")
                    departs_match = re.search(r"Departs\s*(\d{2}:\d{2})", aria_label, re.IGNORECASE)
                    departure_time = departs_match.group(1) if departs_match else "Unknown"
                    
                    # Extract Arrival/Reach Time (e.g. "arrives 07:50")
                    arrives_match = re.search(r"arrives\s*(\d{2}:\d{2})", aria_label, re.IGNORECASE)
                    arrival_time = arrives_match.group(1) if arrives_match else "Unknown"
                    
                    # Find the price (usually in format "Price XXX INR")
                    price_match = re.search(r"Price\s*([\d\.,]+)\s*INR", aria_label, re.IGNORECASE)
                    price = price_match.group(1) if price_match else "Unknown"
                    
                    # Split the URL to get the origin and destination
                    route_parts = url.split('/')[-1].split('-to-')
                    origin = route_parts[0].capitalize()
                    destination = route_parts[1].capitalize()
                    
                    bus_data = {
                        "Origin": origin,
                        "Destination": destination,
                        "Operator": operator,
                        "Bus Type": bus_type,
                        "Departure Time": departure_time,
                        "Arrival Time": arrival_time,
                        "Price": price,
                        "Date": date_str,
                        "Date Type": date_type
                    }
                    
                    # Categorize into night or day
                    if departure_time != "Unknown":
                        hr = int(departure_time.split(":")[0])
                        # Night: 18:00 to 03:00 means hour >= 18 or hour < 3
                        if hr >= 18 or hr < 3:
                            page_night_buses.append(bus_data)
                        else:
                            page_day_buses.append(bus_data)
                except Exception as e:
                    # If a specific card fails, skip it
                    continue
                    
            # User wants a mix of Day and Night buses. They do not want us to strictly cap them or drop data.
            # So we will just keep all valid buses found (which will naturally include both day and night buses since we scroll).
            selected_buses = []
            selected_buses.extend(page_night_buses)
            selected_buses.extend(page_day_buses)
                
            if selected_buses:
                master_data.extend(selected_buses)
                scraped_any = True

            if scraped_any:
                # Save progress incrementally after each route
                df = pd.DataFrame(master_data)
                df.to_csv("tn_bus_data.csv", index=False)
                print(f"Successfully scraped route. Added {len(page_night_buses)} night buses and {len(selected_buses) - len(page_night_buses)} day buses. Total records in database: {len(master_data)}", flush=True)
            else:
                print(f"No valid bus listings found on page to match criteria.", flush=True)
                
        except Exception as e:
            print(f"Could not load data for {url_with_date}. The site might be blocking the scraper.", flush=True)
        
        # Add the combination to completed set
        scraped_keys.add(combo_key)
        
        # Wait 5 seconds before hitting the next URL so you don't get banned
        time.sleep(5)

# 4. Close the browser
try:
    driver.quit()
except:
    pass

print("Data saved successfully to free_tn_bus_data.csv!", flush=True)

