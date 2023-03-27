# Develop with separate containers running
1. Build your container in "developer mode":
~~~bash
sudo ./scripts/devel-compose up --build
~~~
2. Switch into **webapp** container:
~~~bash
sudo podman exec -it vmaas-webapp bash
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

3. Switch to **webapp_utils** container:
~~~bash
sudo podman exec -it vmaas-webapp-utils bash
~~~
Now run:

```./entrypoint.sh```

4. Switch into **reposcan** container:
~~~bash
sudo podman exec -it vmaas-reposcan bash
~~~
Now run:

```./entrypoint.sh```

5. Switch to **database** container to gain access to db:
~~~bash
sudo podman exec -it vmaas-database bash
~~~
Now you can run database terminal with:

```psql -d vmaas```

6. Safe EXIT
~~~bash
sudo podman-compose down
~~~
Otherwise pod and containers remain up and running.
