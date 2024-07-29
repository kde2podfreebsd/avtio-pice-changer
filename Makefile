main:
	docker compose build --no-cache
	docker compose up

build:
	docker build -t app src/.  

run:
	docker run -p 5173:5173 app

clean_repo:
	find . -name __pycache__ -type d -print0|xargs -0 rm -r --
	rm -rf .idea/

fix_git_cache:
	git rm -rf --cached .
	git add .

docker_clean:
	sudo docker stop $$(sudo docker ps -a -q) || true
	sudo docker rm $$(sudo docker ps -a -q) || true
