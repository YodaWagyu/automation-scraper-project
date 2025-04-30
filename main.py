from bigc_scraper import run_scraper

def main(request):
    run_scraper()
    return 'Scraper ran successfully', 200
