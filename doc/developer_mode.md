# Develop with separate containers running
1. Build your container in "developer mode":
~~~bash
./scripts/devel-compose build --no-cache
./scripts/devel-compose up
~~~
2. Switch into **webapp** container:
~~~bash
docker-compose exec vmaas_webapp bash
~~~
Now your local git directory is mounted under `/git` in the container so any change
you make you can immediatelly test.

```python3 ./app.py```

Note that by default container does NOT run the application 
(so you can run your own modificationtion)
so if you want to run "original" (unmodified) application use

```/app/entrypoint.sh```

Now you have bash inside vmaas_webapp container, run: 

```./entrypoint.sh```

3. Switch into **websocket** container:
~~~bash
docker-compose exec vmaas_websocket bash
~~~
Now run:

```python3 websocket.py```

4. Switch into **reposcan** container:
~~~bash
docker-compose exec vmaas_reposcan bash
~~~
Now run:

```./entrypoint.sh```

5. Switch to **database** container to gain access to db:
~~~bash
docker-compose exec vmaas_database bash
~~~
Now you can run database terminal with:

```psql -d vmaas```
