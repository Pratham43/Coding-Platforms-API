import requests
from bs4 import BeautifulSoup
from flask import Flask, jsonify
from flask_restful import Api, Resource, abort 

app = Flask(__name__)
api = Api(app)

class CodechefUser(Resource):
    def get(self, username):
        res = requests.get(f"https://www.codechef.com/users/{username}")
        if res.status_code != 200:
            abort(404, message="User Not Found")

        soup = BeautifulSoup(res.text, 'html.parser')
        rating = self.get_rating(soup)
        problems_solved = self.get_problems_solved(soup)

        return jsonify({
            "username": username,
            "rating": rating,
            "problemsSolved": problems_solved
        })

    def get_rating(self, soup):
        rating_div = soup.find_all(["div"], class_="rating-number")
        if len(rating_div) == 0:
            abort(404, message="User Not Found")
        return rating_div[0].text

    def get_problems_solved(self, soup):
        sections = soup.find(["section"], class_="rating-data-section problems-solved")
        if sections is None:
            abort(404, message="User Not Found")
        problem_solved_sections = sections.h5.text
        probs_solved = problem_solved_sections.split("(")
        probs_solved = probs_solved[1].split(")")[0]
        return probs_solved

class CodeforcesUser(Resource):
    def get(self, username):
        url = f"https://codeforces.com/api/user.info?handles={username}"
        res = requests.get(url)
        if res.status_code != 200:
            abort(404, message="User Not Found")

        data = res.json()
        if "result" not in data or len(data["result"]) == 0:
            abort(404, message="User Not Found")

        rating = data["result"][0].get("rating")
        codeForcesProblemsSolved = self.get_problems_solved(username)
        return jsonify({
            "username": username,
            "rating": rating,
            "problemsSolved": codeForcesProblemsSolved
        })
    
    def get_problems_solved(self,username):
        forces_res = requests.get(f"https://codeforces.com/profile/{username}")
        if forces_res.status_code != 200:
            abort(404, message="User Not Found")
        forces_soup = BeautifulSoup(forces_res.text, 'html.parser')
        problems_div = forces_soup.find_all(["div"], class_="_UserActivityFrame_counterValue")
        if len(problems_div) == 0:
            abort(404, message="User Not Found")
        return problems_div[0].text.split()[0]


api.add_resource(CodechefUser, '/codechef/<username>')
api.add_resource(CodeforcesUser, '/codeforces/<username>')

if __name__ == "__main__":
    app.run(debug=True)