from bigc_scraper_od import run_scraper

def main(request):
    run_scraper()
    return 'Scraper ran successfully', 200
