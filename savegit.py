# -*- coding: utf-8 -*-
#!/usr/bin/env python

from argparse import ArgumentParser, Namespace
from collections import defaultdict
from datetime import datetime
import time
import logging
import os
import requests
from requests.exceptions import ConnectTimeout
import zipfile
import shutil


class GitHub:
    """
    GitHub interaction class
    """
    def __init__(self, args: Namespace) -> None:
        # class object initialization
        self.args = args

        self.save_path = self.args.path if self.args.path else "./"
        self.save_path = self.save_path[:-1] if self.save_path[-1] == "/" else self.save_path

        self.url = "https://api.github.com/"
        self.headers = {
            "Accept": "application/vnd.github+json",
            "Authorization": f"Bearer {self.args.token}"
        }

        if not self.args.quiet: print("\n\n🚀🚀🚀🚀\n\n")
    
    def backup(self) -> None:
        # get all user information
        user_request = requests.get(
            url=self.url+"user",
            headers=self.headers
        ).json()
        username = user_request["login"]
        print(f"GitHub user: {username}")

        # get information about repositories + all branches in the repository
        repositories_request = requests.get(
            url=self.url+"search/repositories?q=user:"+username,
            headers=self.headers
        ).json()
        repositories = defaultdict(list)
        for rep_name in repositories_request["items"]:
            branches_request = requests.get(
                url=self.url+f"repos/{username}/{rep_name['name']}/branches",
                headers=self.headers
            ).json()
            for branch in branches_request:
                repositories[rep_name['name']].append(branch["name"])
        print(f"Total number of repositories: {len(repositories)}")

        # all information about the user's gists
        gists_request = requests.get(
            url=self.url+f"users/{username}/gists",
            headers=self.headers
        ).json()
        gists = {url["html_url"].split("/")[-1]: list(url["files"].items())[0][0] for url in gists_request}
        print(f"Total number of gists: {len(gists)}\n")

        # create directories for backup
        main_path = f"{self.save_path}/GitHub-{username}-{str(datetime.now()).replace(' ', 'T')}"
        os.mkdir(main_path)
        os.mkdir(main_path+"/repositories/")
        os.mkdir(main_path+"/gists/")

        def download_content(url: str, message: str):
            for _ in range(5):
                try:
                    print(message)
                    return requests.get(url=url, headers=self.headers)
                except ConnectTimeout:
                    print("Connection refused by the server. Reconnect after 10 seconds.")
                    time.sleep(10)
                    continue

        # download repositories
        print(f"Downloading all user's repositories...")
        for index, rep_name in enumerate(repositories):
            for branch in repositories[rep_name]:
                req = slef.download_content(
                    url=self.url+f"repos/{username}/{rep_name}/zipball/{branch}",
                    message=f"{index+1}/{len(repositories)} - Repository download - \"{rep_name}/{branch}\""
                )
                if req.status_code == 200:
                    if not os.path.isdir(f'{main_path}/repositories/{rep_name}/'): 
                        os.mkdir(f"{main_path}/repositories/{rep_name}/")
                    with open(f'{main_path}/repositories/{rep_name}/{branch.replace("/", "-")}.zip', 'wb') as files_path:
                        files_path.write(req.content)
                else:
                    print(f"Failed to reach the repository: {rep_name}. Status: {req.status_code}")

        # download gists
        print(f"Downloading all user's gists...")
        for index, gist_id in enumerate(gists):
            req = slef.download_content(
                    url=self.url+f"gists/{gist_id}",
                    message=f"{index+1}/{len(gists)} - Gist download - \"{gists[gist_id]}\""
                )
            if req.status_code == 200:
                with open(main_path+"/gists/"+gists[gist_id], "w") as files_path:
                    files_path.write(req.json()["files"][gists[gist_id]]["content"])
            else:
                print(f"Failed to reach the gist: {gists['gists_id']}. Status: {req.status_code}")

        # archiving backups
        zf = zipfile.ZipFile(f"{main_path}.zip", "w")
        for dirname, subdirs, files in os.walk(main_path):
            zf.write(dirname)
            for filename in files:
                zf.write(os.path.join(dirname, filename))
        zf.close()
        shutil.rmtree(main_path)

        print(f"✅ Backup completed successfully. The result is saved in  {main_path}.zip")


if __name__ == "__main__":
    # script logging configuration
    logging.basicConfig(
        format='%(name)s - %(levelname)s - %(message)s',
        level=logging.INFO
    )

    # geting options from command line
    parser = ArgumentParser(description='Add description letter')
    optional = parser.add_argument_group('optional arguments')
    optional.add_argument("-p", "--path", 
                          dest="path",
                          help="directory where backups are saved", 
                          metavar="PATH")
    optional.add_argument("-q", "--quiet",
                          default=False,
                          action="store_true", 
                          dest="quiet",
                          help="don't logging to stdout")
    required = parser.add_argument_group('required arguments')
    required.add_argument("-t", "--token",
                          dest="token",
                          help="api token of your github", 
                          metavar="TOKEN", 
                          required=True)
    args = parser.parse_args()

    # making a GitHub Backup
    gh = GitHub(args=args)
    gh.backup()
