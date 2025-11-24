import cloudscraper

scraper = cloudscraper.create_scraper()
try:
    response = scraper.get("https://jobregister.aas.org")
    print(response.status_code)
    print(response.text[:500])
except Exception as e:
    print(e)
