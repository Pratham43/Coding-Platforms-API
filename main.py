import requests
from bs4 import BeautifulSoup
from fastapi import FastAPI, HTTPException

app = FastAPI()


@app.get("/codechef/{username}")
async def get_codechef_user(username: str):
    res = requests.get(f"https://www.codechef.com/users/{username}")
    if res.status_code != 200:
        raise HTTPException(status_code=404, detail="User Not Found")

    soup = BeautifulSoup(res.text, 'html.parser')
    rating = get_rating(soup)
    problems_solved = get_problems_solved(soup)

    return {
        "username": username,
        "rating": rating,
        "problemsSolved": problems_solved
    }


@app.get("/codeforces/{username}")
async def get_codeforces_user(username: str):
    url = f"https://codeforces.com/api/user.info?handles={username}"
    res = requests.get(url)
    if res.status_code != 200:
        raise HTTPException(status_code=404, detail="User Not Found")

    data = res.json()
    if "result" not in data or len(data["result"]) == 0:
        raise HTTPException(status_code=404, detail="User Not Found")

    rating = data["result"][0].get("rating")
    problems_solved = get_codeforces_problems_solved(username)

    return {
        "username": username,
        "rating": rating,
        "problemsSolved": problems_solved
    }


def get_rating(soup):
    rating_div = soup.find_all("div", class_="rating-number")
    if len(rating_div) == 0:
        raise HTTPException(status_code=404, detail="User Not Found")
    return rating_div[0].text


def get_problems_solved(soup):
    sections = soup.find("section", class_="rating-data-section problems-solved")
    if sections is None:
        raise HTTPException(status_code=404, detail="User Not Found")
    problem_solved_sections = sections.h5.text
    problems_solved = problem_solved_sections.split("(")[1].split(")")[0]
    return problems_solved


def get_codeforces_problems_solved(username):
    forces_res = requests.get(f"https://codeforces.com/profile/{username}")
    if forces_res.status_code != 200:
        raise HTTPException(status_code=404, detail="User Not Found")
    forces_soup = BeautifulSoup(forces_res.text, 'html.parser')
    problems_div = forces_soup.find_all("div", class_="_UserActivityFrame_counterValue")
    if len(problems_div) == 0:
        raise HTTPException(status_code=404, detail="User Not Found")
    return problems_div[0].text.split()[0]
